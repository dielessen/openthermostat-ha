"""The screens of 1.4's section Advanced, since 1.4.1 part of Settings → Installation: settings_installation.py serves
them as ``#installation/<item>`` and its list reuses ``_read_list`` (the section "advanced" itself is retired; the
screens are frontend/openthermostat-settings-installation.js).

Items, each a model with its ``screen``:

- ``None``, the list (memory only, never an E32 read): whether the E32 is connected (``e32``), the tester program
  on or off, the E32's time zone as Home Assistant last saw it (the daily settings backup, e32_system.check_time_zone),
  and whether a room setup status is there to show (``status``).
- ``logging``: the E32 system log (``GET/POST /config/logging``, every field in one POST, the answer is the read-back),
  with Configure's own check (e32_system.logging_document) and the same refusals.
- ``time-zone``: the zone the E32 runs its week programs in (``/config/device``), from the E32 Settings page's list;
  a change is the Configure step's write (e32_system.async_write_zone: the read's ETag, only the time zone changed,
  read back, one restart), refused when the E32 holds another zone than the screen showed (``posix``).
- ``tester``: the tester program's switch (boiler_share.save_tester) and, while it is on, the bus recording's state
  (``live.recording``) with the actions of Configure's tester menu: ``{"action": "start" | "stop" | "share"}``.
- ``status``: read only, the texts of Configure's two status steps "Check the old rooms" (configuration_status) and
  "Status of your room setup" (graph_status), in Home Assistant's language, when the installation has them.

Every E32 request is one sign-in through the room plan's link (e32_system.async_e32_call). A read that fails answers
an error the panel explains (``e32_unreachable``, ``e32_password_changed``, ``connect_e32`` …); a refused write the
Configure step's own key (``e32_settings_*``, ``e32_log_*``, ``tester_*``).
"""
from __future__ import annotations

from functools import lru_cache
import json
import logging
from pathlib import Path
import re

from .settings import LIVE, SettingsError

_LOGGER = logging.getLogger(__name__)

ITEMS = ("logging", "time-zone", "tester", "status")
# The keys the panel explains on a failed read; any other failure to reach the E32 is "e32_unreachable".
READ_KEYS = {"e32_password_changed", "e32_settings_password_default", "e32_settings_update_required",
             "e32_settings_no_free_session", "e32_settings_busy"}


def _link(hass, entry):
    from .e32_system import link_for
    link = link_for(hass, entry)
    if link is None:
        raise SettingsError("connect_e32")
    return link


async def _e32(hass, entry, call, *, write):
    """call(client) in one sign-in; a failure as the panel's error (a read: plain "e32_unreachable" unless the E32 said
    more, a write: Configure's own key with its {error})."""
    from .controller_link import ControllerLinkError
    from .e32_system import async_e32_call, failure
    link = _link(hass, entry)
    try:
        return await async_e32_call(link, call, write=write)
    except ControllerLinkError as err:
        key, values = failure(err)
        if not write and key not in READ_KEYS:
            raise SettingsError("e32_unreachable") from None
        raise SettingsError(key, **values) from None


def _flow(hass, entry):
    """Configure's options flow for this entry, only to ask it what it would show (its menu, its status steps)."""
    from .product_flow import ProductOptionsFlow
    flow = ProductOptionsFlow()
    flow.hass, flow.handler = hass, entry.entry_id
    return flow


def _status_available(hass, entry, flow):
    from .e32_link import legacy_zones
    return bool(legacy_zones(entry)) or flow._native_plan_review_available()


# -- the list ------------------------------------------------------------------------------------------------------

async def _read_list(hass, entry):
    from .boiler_share import tester_on
    from .const import DOMAIN
    from .e32_system import TIME_ZONE_STATE, ha_zone, link_for, zone_of
    flow = _flow(hass, entry)
    posix = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get(TIME_ZONE_STATE)
    zone = (zone_of(posix, ha_zone(hass)) or posix) if type(posix) is str else None
    return {"screen": "list", "e32": link_for(hass, entry) is not None, "tester": tester_on(entry), "time_zone": zone,
            "status": _status_available(hass, entry, flow)}


# -- the system log ------------------------------------------------------------------------------------------------

def _logging_model(current):
    return {"screen": "logging", **current}


async def _read_logging(hass, entry):
    from .e32_system import decode_logging
    current = decode_logging(await _e32(hass, entry, lambda c: c.async_logging(), write=False))
    if current is None:
        raise SettingsError("e32_unreachable")
    return _logging_model(current)


async def _save_logging(hass, entry, values):
    """The panel sends every field it showed (the core has just checked them against the E32 with the token): the
    two message sources only where the E32 has them, as the form."""
    from .e32_system import decode_logging, logging_document
    try:
        document = logging_document(values, "syslog_esp" in values and "syslog_ems" in values)
    except ValueError as err:
        raise SettingsError(err.args[1], err.args[0]) from None
    stored = decode_logging(await _e32(hass, entry, lambda c: c.async_logging(document), write=True))
    if stored is None or any(stored.get(k) != v for k, v in document.items()):
        raise SettingsError("e32_settings_unconfirmed")
    return _logging_model(stored)


# -- the time zone -------------------------------------------------------------------------------------------------

def _zone_model(hass, posix, restarting=False):
    from .e32_system import ZONE_POSIX, ha_zone, zone_of
    current = zone_of(posix, ha_zone(hass))
    return {"screen": "time-zone", "time_zone": current or "", "posix": posix, "zones": sorted(ZONE_POSIX),
            LIVE: {"e32": current or posix or "", "home": getattr(hass.config, "time_zone", None) or "",
                   "home_zone": ha_zone(hass) or "", "restarting": restarting}}


async def _read_zone(hass, entry):
    from .e32_system import check_time_zone
    settings, _tag = await _e32(hass, entry, lambda c: c.async_read("/config/device"), write=False)
    if type(settings) is not dict or type(settings.get("timeZone")) is not str:
        raise SettingsError("e32_settings_update_required")
    check_time_zone(hass, entry, settings["timeZone"])  # as Configure's step: the Repairs notice follows what it read
    return _zone_model(hass, settings["timeZone"])


async def _save_zone(hass, entry, values):
    from .e32_system import POSIX_ALIASES, ZONE_POSIX, async_write_zone, check_time_zone
    chosen = values.get("time_zone")
    if chosen not in ZONE_POSIX:
        raise SettingsError("e32_time_zone_invalid", "time_zone")
    shown = values.get("posix") if type(values.get("posix")) is str else None
    if shown is not None and ZONE_POSIX[chosen] == POSIX_ALIASES.get(shown, shown):
        return _zone_model(hass, shown)
    posix = ZONE_POSIX[chosen]
    # The step's write: the E32's zone must still be the one shown, then only the zone changes, read back, a restart.
    await _e32(hass, entry, lambda c: async_write_zone(c, posix, shown), write=True)
    check_time_zone(hass, entry, posix)
    return _zone_model(hass, posix, restarting=True)  # not read again: the E32 is restarting


# -- the tester program --------------------------------------------------------------------------------------------

async def _read_tester(hass, entry, done=None):
    from .boiler_share import STATE_KEY, async_status, tester_on
    from .const import DOMAIN
    from .controller_link import ControllerLinkError
    from .e32_system import async_e32_call, link_for
    on, status = tester_on(entry), None
    link = link_for(hass, entry)
    if on and link is not None:
        try:
            status = await async_e32_call(link, async_status, write=False)
        except ControllerLinkError:
            status = None  # the line says the E32 could not be reached just now; the switch still works
        monitor = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get(STATE_KEY)
        if monitor is not None:
            monitor.observe(status)
    recording = None
    if type(status) is dict:
        recording = {k: status.get(k) for k in ("state", "seconds", "frames") if k in status}
    return {"screen": "tester", "tester_enabled": on, "e32": link is not None,
            LIVE: {"recording": recording, "done": done}}


async def _save_tester(hass, entry, values):
    from .boiler_share import STATE_KEY, async_share, save_tester, tester_on
    from .const import DOMAIN
    from .controller_link import ControllerLinkError
    action = values.get("action")
    if action is None:
        wanted = values.get("tester_enabled")
        if type(wanted) is not bool:
            raise SettingsError("setup_invalid", "tester_enabled")
        if wanted != tester_on(entry):
            _link(hass, entry)  # as Configure: only with the E32 connected
            save_tester(hass, entry, wanted)
            return await _read_tester(hass, entry, "switched_on" if wanted else "tester_switched_off")
        return await _read_tester(hass, entry)
    if action not in ("start", "stop", "share") or not tester_on(entry):
        raise SettingsError("setup_invalid")
    link = _link(hass, entry)
    if action == "share":
        try:
            await async_share(hass, entry, link)
        except ControllerLinkError as err:
            from .e32_system import failure
            key, placeholders = failure(err)
            raise SettingsError(key, **placeholders) from None
        except OSError:
            raise SettingsError("tester_share_not_written") from None
        return await _read_tester(hass, entry, "tester_shared")
    start = action == "start"
    try:
        status = await _e32(hass, entry, lambda c: c.async_recording(start), write=True)
    except SettingsError as err:
        if err.placeholders.get("error") == "controller_recording_unavailable":
            raise SettingsError("tester_recording_unavailable") from None
        raise
    monitor = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get(STATE_KEY)
    if monitor is not None:
        monitor.observe(status if type(status) is dict else None)
        if start:
            monitor.recording_started()
    return await _read_tester(hass, entry, "tester_recording_started" if start else "tester_recording_stopped")


# -- the room setup status (read only) -----------------------------------------------------------------------------

@lru_cache(maxsize=4)
def _steps(language):
    path = Path(__file__).parent / "translations" / f"{language}.json"
    return json.loads(path.read_text(encoding="utf-8"))["options"]["step"]


class _Kept(dict):
    def __missing__(self, key):  # a placeholder the step did not fill stays out of the text
        return ""


def _plain(text):
    """A step description as plain text: no **bold** marks, no empty lines at the ends."""
    return re.sub(r"\*\*(.*?)\*\*", r"\1", text).strip()


async def _read_status(hass, entry):
    from .heating_advice import language
    flow = _flow(hass, entry)
    lang = language(hass)
    steps = await hass.async_add_executor_job(_steps, lang)
    blocks = []
    results = []
    from .e32_link import legacy_zones
    steps_shown = [*(["configuration_status"] if legacy_zones(entry) else []),
                   *(["graph_status"] if flow._native_plan_review_available() else [])]
    for name in steps_shown:
        try:
            results.append(await getattr(flow, f"async_step_{name}")())
        except Exception:  # noqa: BLE001 - a status that cannot be made leaves its block out, never the page
            _LOGGER.exception("The status %s for the settings panel could not be made", name)
    for result in results:
        step = steps.get(result.get("step_id") or "") if result.get("type") == "form" else None
        if step is None:
            continue
        text = step.get("description", "").format_map(_Kept(result.get("description_placeholders") or {}))
        blocks.append({"title": step.get("title", ""), "text": _plain(text)})
    return {"screen": "status", "blocks": blocks}


# -- the section ---------------------------------------------------------------------------------------------------

async def read_advanced(hass, entry, item=None):
    if item is None:
        return await _read_list(hass, entry)
    if item == "logging":
        return await _read_logging(hass, entry)
    if item == "time-zone":
        return await _read_zone(hass, entry)
    if item == "tester":
        return await _read_tester(hass, entry)
    if item == "status":
        return await _read_status(hass, entry)
    raise SettingsError("unknown_section")


async def save_advanced(hass, entry, item, values):
    if item == "logging":
        return await _save_logging(hass, entry, values)
    if item == "time-zone":
        return await _save_zone(hass, entry, values)
    if item == "tester":
        return await _save_tester(hass, entry, values)
    raise SettingsError("unknown_section")  # the list and the status are read only
