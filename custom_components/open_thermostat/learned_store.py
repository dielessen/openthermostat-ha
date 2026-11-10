"""A Repairs item about what the E32 learned and could not keep (1.1.1, R-E-04; 1.4.2: one, after a day).

On 5 November the E32 lost what it learned at a restart, and nothing showed it (R-E-04: the boot's "restored"
and the save's count were RAM log lines only). The E32 (SL-A, ``LearnedStore::addJson``, TELEMETRIEBUDGET.nl.md
section 25) now puts a bounded ``learned_store`` part at the top of its summary (``fw/telemetry/summary``)::

    "learned_store": {"restored_rooms": n, "restored_parts": n, "rooms": n | null, "saved_rooms": n | null,
                      "complete": bool | null, "saves": n, "pending_entries": n, "nvs_free_entries": n | null,
                      "reserve_entries": n | null, "needed_entries": n}

``restored_*`` are the boot's restore; ``rooms``, ``saved_rooms`` and ``complete`` the last save of this boot
(null before the first one); ``saves`` the saves this boot; ``pending_entries`` what the frames left in RAM would
need; ``nvs_free_entries`` the free NVS entries (null when unreadable). Since NVS-RESERVE (1.3) also why a part was
refused: ``reserve_entries``, what the E32 keeps free for its own settings (null when unknown), and
``needed_entries``, what the first part it could not write needs (0 when nothing is pending). Firmware without
``learned_store`` raises nothing here.

- ``learned_not_saved``: the last save stored fewer rooms than the plan has (``saved_rooms < rooms``): "the E32
  could not save what it learned for <n> of its <m> rooms; it keeps it in memory until there is room". With the
  counts (``memory``) a second sentence says why: the free places, those it keeps for its own settings and what
  the learned record needs. Firmware without them gets the text without that sentence
  (``learned_not_saved_no_counts``). A save
  that kept every room but not all the rest (``complete`` false: the house and boiler part) raises
  ``learned_not_saved_part``. Either goes once a later save is complete. 1.4.2 (HC-05, Repairs only for faults):
  raised only once the condition has lasted NOT_SAVED_AFTER_S (a day; its own text says "if this stays for days"):
  a save that leaves something out for a while is normal while the E32 makes room. Counted in this Home Assistant
  run (a restart of Home Assistant starts the day again).
- A restart that lost what the E32 learned (right after an E32 restart, the knowledge figure, "Known about your
  house", the insight's ``knowledge.pct``, is more than LOSS_POINTS below the last figure before it): information
  after the fact, the E32 learns it again. 1.4.2: no Repairs item any more (``learned_lost_at_restart`` is in
  issue_sync.RETIRED); the diagnostics download says it (support_diagnostics.learned_store, ``lost_at_restart``).
"""
from __future__ import annotations

from homeassistant.core import callback

from .const import DOMAIN
from .issue_sync import clear_issues, sync_issues

GROUP = "learned_store"
LOSS_POINTS = 30
NOT_SAVED_AFTER_S = 24 * 3600  # 1.4.2: the Repairs item only once the last saves left something out for a day
STATE_KEY = "learned_store_watch"
COUNTS = ("restored_rooms", "restored_parts", "rooms", "saved_rooms", "saves", "pending_entries", "nvs_free_entries",
          "reserve_entries", "needed_entries")
# The largest believable count: rooms (RoomPlan::maxRooms is 8) and saves (uint16) fit; NVS entries of 4 KB pages too.
COUNT_MAX = 65535


def store_status(summary):
    """The summary's ``learned_store`` with every field checked (an implausible one is None); None without it."""
    part = summary.get("learned_store") if type(summary) is dict else None
    if type(part) is not dict:
        return None

    def count(value):
        return value if type(value) is int and 0 <= value <= COUNT_MAX else None
    status = {key: count(part.get(key)) for key in COUNTS}
    status["complete"] = part.get("complete") if type(part.get("complete")) is bool else None
    return status


def not_saved(status):
    """("rooms", missing, of) when the last save left rooms out, ("part", 0, of) when it kept every room but not
    the rest, else None (no save yet this boot, or a complete one)."""
    if status is None or status["rooms"] is None or status["saved_rooms"] is None:
        return None
    rooms, saved = status["rooms"], status["saved_rooms"]
    if saved < rooms:
        return "rooms", rooms - saved, rooms
    if status["complete"] is False:
        return "part", 0, rooms
    return None


def memory(status):
    """{"free", "reserve", "needed"}: the settings memory's free places, those the E32 keeps for its own settings and
    what the learned record needs (NVS entries), or None when the firmware does not send all three (older firmware)
    or nothing is pending."""
    if status is None:
        return None
    free, reserve, needed = status["nvs_free_entries"], status.get("reserve_entries"), status.get("needed_entries")
    if free is None or reserve is None or not needed:
        return None
    return {"free": free, "reserve": reserve, "needed": needed}


class LearnedStoreWatch:
    """Follows the hub: the last save and the knowledge figure around each E32 restart."""

    def __init__(self, hass, entry, hub):
        self.hass, self.entry, self.hub = hass, entry, hub
        self.boots = getattr(hub, "boots", 0)
        self.before = None      # the knowledge figure before the latest restart
        self.last = None        # the latest knowledge figure of this E32 boot
        self.loss = None        # (before, after) of a restart that lost what it learned (diagnostics only)
        self.after_restart = False
        self.not_saved_since = None  # hub clock time since the saves leave something out

    @callback
    def check(self):
        from .insight import knowledge
        summary = getattr(self.hub, "summary", None)
        boots = getattr(self.hub, "boots", 0)
        if boots != self.boots:
            self.boots = boots
            self.before, self.last, self.after_restart = self.last, None, True
        figure = (knowledge(summary) or {}).get("pct") if summary is not None else None
        if figure is not None:
            if self.after_restart and self.before is not None:
                self.loss = (self.before, figure) if self.before - figure > LOSS_POINTS else None
            self.after_restart = False
            self.last = figure
            if self.loss is not None and self.loss[0] - figure <= LOSS_POINTS:
                self.loss = None  # it learned it again
        wanted = {}
        status = store_status(summary)
        missing = not_saved(status)
        clock = getattr(self.hub, "clock", None)
        now = clock() if callable(clock) else 0
        if missing is None:
            if status is not None:
                self.not_saved_since = None  # a complete save (or none yet this boot): the day starts again
        elif self.not_saved_since is None:
            self.not_saved_since = now
        if missing is not None and now - self.not_saved_since >= NOT_SAVED_AFTER_S:
            if missing[0] == "rooms":
                placeholders = {"name": self.entry.title, "missing": missing[1], "of": missing[2]}
                why = memory(status)
                wanted["not_saved"] = (("learned_not_saved", {**placeholders, **why}) if why is not None
                                       else ("learned_not_saved_no_counts", placeholders))
            else:
                wanted["not_saved"] = ("learned_not_saved_part", {"name": self.entry.title})
        sync_issues(self.hass, self.entry.entry_id, GROUP, wanted)


async def async_setup_learned_store(hass, entry):
    """Product entries: the Repairs item (no entities)."""
    from .heating_link import heating_hub
    hub = heating_hub(hass, entry)
    watch = hass.data[DOMAIN][entry.entry_id][STATE_KEY] = LearnedStoreWatch(hass, entry, hub)
    entry.async_on_unload(hub.add_listener(watch.check))
    entry.async_on_unload(lambda: clear_issues(hass, entry.entry_id, GROUP))
    watch.check()
