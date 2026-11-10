"""The season hint of an E32 (1.4.1, docs/engineering/ZOMERSTAND-ONTWERP.nl.md §3): a question, never a switch.

The E32 computes it from the outdoor day means (five days in a row at 17 °C or more while not in summer:
``summer_on``; three days at 12 °C or less while in summer: ``summer_off``) and reports it in the house's away status
(``fw/state/heating`` "away", the object that carries the house ``mode``): ``season_hint`` null or
``{"kind": "summer_on" | "summer_off", "since_day": "YYYY-MM-DD"}``. The E32 never switches by itself, and Home
Assistant never sets the mode by itself either: it only decides whether to show the hint.

- Shown while the E32 reports it and it fits the mode (``summer_on`` outside summer, ``summer_off`` in summer), for at
  most SHOWN_DAYS days from its ``since_day``, and not dismissed for that ``since_day``.
- Dismissed (the entry's options ``season_hint_dismissed``: that ``since_day``; no E32 write) once the user answers it
  in Home Assistant: switches summer on (``summer_on``) or off (``summer_off``) in any way (the select, Configure, the
  settings panel: e32_house.HouseState.async_command calls ``acted``), or answers the notification (Switch on, Switch
  off, Not now: ``async_answer``). A later hint with another ``since_day`` is shown again.
- Shown as the house message ``season`` (notifications.py): with the two answers as actions on a Home Assistant app
  (``notify.mobile_app_*``), the sentence alone on other services and in Home Assistant; and as the house mode
  select's attribute ``season_hint`` for the cards. No Repairs issue: Repairs are only for faults (owner, 9 Nov).
"""
from __future__ import annotations

from datetime import date
import logging
import re

from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

HINT_KINDS = ("summer_on", "summer_off")
DISMISSED = "season_hint_dismissed"  # entry options: the since_day of the hint the user answered
SHOWN_DAYS = 7  # the design: the hint goes after the choice or after seven days
ACTION_EVENT = "mobile_app_notification_action"
CHOICES = ("on", "off", "no")  # switch summer on, switch it off, not now
_ACTION = re.compile(r"open_thermostat_season_(on|off|no)_([0-9A-Za-z]+)_(\d{4}-\d{2}-\d{2})")
# The answers on a phone (the house message's actions), in the Home Assistant language.
ACTION_TITLES = {
    "en": {"on": "Switch summer mode on", "off": "Switch summer mode off", "no": "Not now"},
    "nl": {"on": "Zomerstand aanzetten", "off": "Zomerstand uitzetten", "no": "Niet nu"},
    "pl": {"on": "Włącz tryb letni", "off": "Wyłącz tryb letni", "no": "Nie teraz"},
}


def _day(text):
    try:
        return date.fromisoformat(text) if type(text) is str and len(text) == 10 else None
    except ValueError:
        return None


def season_hint(away):
    """{"kind", "since_day"} of the hint the E32 reports in the house's away status, or None."""
    hint = away.get("season_hint") if type(away) is dict else None
    if type(hint) is not dict or hint.get("kind") not in HINT_KINDS or _day(hint.get("since_day")) is None:
        return None
    return {"kind": hint["kind"], "since_day": hint["since_day"]}


def summer_exercise(away):
    """Unix seconds of the last weekly exercise of the valves and pumps in summer (``summer_exercise_utc``), or None."""
    value = away.get("summer_exercise_utc") if type(away) is dict else None
    return value if type(value) is int and value > 0 else None


def dismissed_day(entry):
    value = (getattr(entry, "options", None) or {}).get(DISMISSED)
    return value if type(value) is str else None


def shown_hint(entry, away, today):
    """The hint as Home Assistant shows it now ({"kind", "since_day"}), or None: not reported, not fitting the mode
    (the E32's next status catches up with a mode just changed), older than SHOWN_DAYS days, or dismissed."""
    hint = season_hint(away)
    if hint is None or (hint["kind"] == "summer_off") != (away.get("mode") == "summer"):
        return None
    if (today - _day(hint["since_day"])).days >= SHOWN_DAYS or dismissed_day(entry) == hint["since_day"]:
        return None
    return hint


def _today():
    from homeassistant.util import dt as dt_util
    return dt_util.now().date()


@callback
def dismiss(hass, entry, since_day):
    """Store the dismissal of the hint of ``since_day`` without a reload (the comfort settings' no-reload marker);
    the house mode select and the notifier see it at once."""
    from .energy_input import ENERGY_ONLY_UPDATE
    options = {**entry.options, DISMISSED: since_day}
    if options == dict(entry.options):
        return False
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if state is not None:
        state[ENERGY_ONLY_UPDATE] = dict(options)
    if not hass.config_entries.async_update_entry(entry, options=options) and state is not None:
        state.pop(ENERGY_ONLY_UPDATE, None)  # no listener runs: never leave the marker behind
    if type(state) is dict:
        if (hub := state.get("heating_hub")) is not None:
            hub.notify()
        if (notifier := state.get("notifier")) is not None:
            notifier.evaluate()
    return True


@callback
def acted(hass, entry, away, mode):
    """A house mode was set in Home Assistant: the hint shown before it is answered when the mode is what it asked."""
    hint = shown_hint(entry, away, _today())
    if hint is not None and (mode == "summer") == (hint["kind"] == "summer_on"):
        dismiss(hass, entry, hint["since_day"])


def action_id(entry_id, choice, since_day):
    return f"open_thermostat_season_{choice}_{entry_id}_{since_day}"


def notification_data(entry_id, values, lang):
    """The ``data`` of the house message ``season`` on a Home Assistant app: its two actions and one tag (a newer hint
    replaces the older one on the phone)."""
    titles = ACTION_TITLES.get(lang, ACTION_TITLES["en"])
    since = values.get("since_day")
    answer = "on" if values.get("hint") == "summer_on" else "off"
    return {"tag": f"open_thermostat_season_{entry_id}",
            "actions": [{"action": action_id(entry_id, choice, since), "title": titles[choice]}
                        for choice in (answer, "no")]}


def parse_action(action):
    """(choice, entry id, since_day) of one of our actions, or None."""
    found = _ACTION.fullmatch(action) if type(action) is str else None
    return found.groups() if found and _day(found.group(3)) is not None else None


async def async_answer(hass, entry, choice, since_day):
    """The user's answer to the hint of ``since_day``: ``on`` switches summer on, ``off`` switches it off (the mode set
    before it comes back), ``no`` only dismisses. Shared by the notification's actions and (golf B) the panel.

    Returns False when that hint is no longer shown (answered elsewhere, gone, another day): nothing is sent. A refusal
    of the E32 raises its HomeAssistantError and the hint stays.
    """
    from .e32_house import house_state, leave_summer
    if choice not in CHOICES:
        return False
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    hub = state.get("heating_hub") if type(state) is dict else None
    if hub is None or getattr(hub, "plan", None) is None:
        return False
    house = house_state(hass, entry, hub)
    away = house.away
    hint = shown_hint(entry, away, _today()) if away is not None else None
    if hint is None or hint["since_day"] != since_day or (choice != "no" and choice != (
            "on" if hint["kind"] == "summer_on" else "off")):
        return False
    if choice == "on":
        await house.async_command("summer")
    elif choice == "off":
        await house.async_command(*leave_summer(away))  # the mode before it; a running holiday continues
    dismiss(hass, entry, since_day)
    return True


def listen(hass, entry):
    """Answers from a phone (the house message's actions): the event ``mobile_app_notification_action``."""

    @callback
    def handle(event):
        parsed = parse_action((event.data or {}).get("action"))
        if parsed is None or parsed[1] != entry.entry_id:
            return
        choice, _entry_id, since_day = parsed

        async def answer():
            try:
                await async_answer(hass, entry, choice, since_day)
            except HomeAssistantError as err:
                _LOGGER.warning("OpenThermostat: the answer to the season hint was not sent to the E32: %s", err)
        hass.async_create_task(answer(), f"{DOMAIN} season hint answer")
    return hass.bus.async_listen(ACTION_EVENT, handle)
