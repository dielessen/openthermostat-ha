"""A Home Assistant thermostat per E32 room, temporary overrides, window/door pauses and away.

The rooms live in the E32 room plan and the E32 computes their demand, also
without Home Assistant. This module adds, on top of that plan (E32 beta.19,
``src/control/RoomOverrides.h``):

- one ``climate`` entity per E32 room (thermostat card, voice assistants):
  current temperature, target, mode auto / heat / off and the presets comfort,
  eco, sleep (shown as "Night") and boost: the room's week planner levels
  (stored per room since E32 beta.23, see room_levels; inferred for older
  firmware). "Away" is the house mode only, not a room preset. E32 1.3's room state "Heat along only" is a preset
  too (1.4, issue #10: ``heat_along``, offered while the E32 knows the state): choosing it sets the room's state,
  as the room's Heating select does. "Off" makes the room inactive in the room plan.
- 1.4.2 (docs/engineering/GEDRAGSREGELS-TEMPERATUUR-EN-STAND.nl.md §3.1, §3.2): a temperature never changes the
  room's state. Only Off, switching on from Off (Auto, Heat or turn on), the preset Heat along only and the preset
  none from Heat along only (back to On) choose a state. A new temperature (also the presets comfort, eco and night,
  and Heat while nothing holds the room) is one manual change: with a week program until its next switch time,
  without one the room's temperature without a week program (also on a room that is Off, which stays Off; with a
  program an Off room refuses it). An E32 that announces room.manual.v1 decides that itself (one command
  ``override: manual``); for an older one Home Assistant makes the same split (async_manual_change).
- the actions ``set_room_override`` / ``clear_room_override`` (boost, "2 h at
  21 °C", until the next switch time; never on a room that is Off) and ``set_away`` / ``clear_away`` (a
  lower temperature for the whole house, optionally until a date). The E32
  ends every override itself, also after a restart, and returns the room to
  its week program; a dated away ends early enough to be warm again on time.
- the optional window/door contacts per room and the people of the house
  (beta.23: several person entities; "everyone away" only after all of them
  have been away for the away delay, and never while one of them is unknown),
  forwarded to the E32 over ``<base>ha/heating_input`` as one aggregated value
  (the same message E32 beta.21 understands)::

      {"kind": "contact", "room": "living", "open": true, "delay_s": 120}
      {"kind": "presence", "home": false}
      {"kind": "room_presence", "room": "bedroom", "home": false}

  The last one (beta.23, room.presence.v1) only for a room with its own persons
  (Configure → Rooms → the room → Persons), with the same rule as the house: home
  while one of them is home or unknown, away once all have been away for the
  away delay. It is sent only to an E32 that announces it (away.room_presence);
  an older E32 would not consume it anyway.

  on every change and every five minutes. Any open contact of a room counts as
  open; the E32 pauses the room after the delay (its frost limit stays) and
  resumes when all are closed. Unknown states are not sent: the E32 then
  forgets the report after 15 minutes and the room heats normally.

  Windows and doors (1.0.1): each contact of a room is a window (the default,
  also for every contact chosen before) or a door, and a room has a delay for
  each ("Pause after (windows)", default 2 min; "Pause after (doors)", default
  5 min), so a door opened briefly many times a day pauses later. The delays
  stay in the E32, which counts them from the first open report (a restart of
  Home Assistant never restarts them). Firmware that announces door contacts
  (away.door_contacts, contact.door.v1) gets each kind on its own; doors as::

      {"kind": "contact", "room": "hall", "open": true, "delay_s": 300, "contact": "door"}

  and windows exactly as before (no "contact"). Older firmware (1.0.0) keeps one
  state per room, so it gets one report as before: open while any contact is
  open, with the window delay while a window is open and the door delay while
  only doors are open (legacy_contact_payload). There a window opened while a
  door is already open can pause the room sooner than its own delay: the E32
  counts from the door's opening.

The entity reads the room from the E32 telemetry (``fw/state/room/<id>``: the
room's ``temperature``, ``setpoint``, ``state``, ``demand`` and, while it
deviates from its plan, ``comfort``; ``fw/state/heating``: ``away``) through the
entry's HeatingHub. Commands go over the stored controller connection
(``POST /config/heating/comfort``); plan changes through the room-plan writer.
"""
from __future__ import annotations

from contextlib import asynccontextmanager, nullcontext
from datetime import datetime, timedelta, timezone
from functools import partial
import json
import math
import time

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    PRESET_BOOST, PRESET_COMFORT, PRESET_ECO, PRESET_NONE, PRESET_SLEEP, ClimateEntityFeature, HVACAction, HVACMode)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import selector
from homeassistant.helpers.event import async_call_later, async_track_state_change_event, async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .heating_link import RoomEntity, add_options, heating_hub, number, track_entities
from .native_form import remember_shown, shown_value
from .room_levels import room_levels
from .e32_setting_device import (MANUAL_FEATURE, async_routine_room_change, half_up, has_program,  # noqa: F401
                                 manual_unknown, off_until_over)

CONF_COMFORT = "comfort_settings"
DEFAULTS = {"presence_entity": None, "presence_entities": [], "away_delay_min": 15,
            "comfort_c": 20.0, "eco_c": 16.0,  # the week planner's defaults
            "contact_delay_s": 120,
            # Per room (beta.23): {room id: seconds}; a room without its own delay uses contact_delay_s.
            "contact_delays": {},
            # Doors (1.0.1): the house default and per room, as for windows.
            "door_delay_s": 300, "door_delays": {},
            # {room id: [entity ids]}: every contact of the room (windows and doors, as before 1.0.1, so an
            # older version still finds them all, as windows); doors: those of them that are doors.
            "contacts": {}, "doors": {},
            # Persons per room (beta.23): {room id: [person entity ids]}; a room without uses the house.
            "room_persons": {}}
TEMPERATURE_LIMITS = (5.0, 30.0)
AWAY_LIMITS = (5.0, 25.0)
DELAY_LIMITS = (0, 1800)       # the E32's own bound (RoomOverrides::maxContactDelayS)
# 1.4.2: the comfort settings Home Assistant no longer keeps (the house setting "Length of a manual change" went:
# a manual change lasts until the next switch time, or 120 minutes without a clock). drop_retired_options removes
# them from the entry once and sets RETIRED_MARKER (no entry version change; HA 1.4.1 after a downgrade uses 120).
RETIRED_OPTIONS = ("override_minutes",)
RETIRED_MARKER = "comfort_override_minutes_dropped"
# 1.4.2 (CONTRACT-1.4.2 §1): the minutes of a manual change without a clock (the firmware's own value) or of the
# action's timed change without a duration. The E32's one command for a manual change is room.manual.v1
# (MANUAL_FEATURE); the helpers for it are the setting device's (e32_setting_device), one rule for both.
MANUAL_MINUTES = 120
AWAY_DELAY_LIMITS = (0, 240)   # minutes everyone must be away before the house counts as away
MAX_PRESENCE = 16
MAX_CONTACTS = 8
MAX_AWAY_DAYS = 366
REFRESH = timedelta(minutes=5)
# A new target shows while its write runs (also while it waits for a free E32 web
# session), then at most this long until the telemetry reports it.
PENDING_SECONDS = 60
CONTACT_CLASSES = ("window", "door", "opening", "garage_door")
# No "away" preset per room (owner, 31 Oct 2026): away is the house mode (e32_house.py), not one room's choice.
PRESETS = [PRESET_NONE, PRESET_COMFORT, PRESET_ECO, PRESET_SLEEP, PRESET_BOOST]
# 1.4 (issue #10): the room state "Heat along only" (plan state "follow", E32 1.3) as a preset, for cards, voice
# assistants and automations; only for an E32 that knows the state (plan.room_follow.v1) or a room already on it.
PRESET_HEAT_ALONG = "heat_along"
# Preset -> index in program_levels(): the planner's Comfort, Eco and Night.
LEVEL_PRESETS = {PRESET_COMFORT: 0, PRESET_ECO: 1, PRESET_SLEEP: 2}
OVERRIDES = ("boost", "timed", "next")
AWAY_MODES = ("away", "presence_away", "away_return")
# The E32's refusals that have their own message; the rest name the E32's code.
E32_ERRORS = {"no_clock": "comfort_no_clock", "room_inactive": "comfort_room_off",
              "no_schedule": "comfort_no_schedule",
              # E32 1.4.1: a room override in summer (Home Assistant refuses it first; a write that slips through).
              "summer_mode": "summer_mode_on"}
# The same no-reload flag as the energy step (__init__._async_options_updated).
from .energy_input import ENERGY_ONLY_UPDATE  # noqa: E402


# -- options ---------------------------------------------------------------------


def comfort_options(entry):
    """The comfort settings with defaults; unknown or invalid values fall back to the default."""
    raw = (getattr(entry, "options", None) or {}).get(CONF_COMFORT)
    raw = raw if type(raw) is dict else {}
    out = dict(DEFAULTS)
    presence = raw.get("presence_entity")
    if type(presence) is str and "." in presence:
        out["presence_entity"] = presence
    # Several people since beta.23; an older single presence entity becomes a list of one.
    people = raw.get("presence_entities")
    if type(people) is list:
        out["presence_entities"] = [e for e in people if type(e) is str and "." in e][:MAX_PRESENCE]
    elif out["presence_entity"]:
        out["presence_entities"] = [out["presence_entity"]]
    if type(raw.get("away_delay_min")) is int and AWAY_DELAY_LIMITS[0] <= raw["away_delay_min"] <= AWAY_DELAY_LIMITS[1]:
        out["away_delay_min"] = raw["away_delay_min"]
    for key, (low, high) in (("comfort_c", TEMPERATURE_LIMITS), ("eco_c", TEMPERATURE_LIMITS)):
        if number(raw.get(key), low, high) is not None:
            out[key] = float(raw[key])
    for key, (low, high) in (("contact_delay_s", DELAY_LIMITS), ("door_delay_s", DELAY_LIMITS)):
        if type(raw.get(key)) is int and low <= raw[key] <= high:
            out[key] = raw[key]
    for key in ("contact_delays", "door_delays"):
        delays = raw.get(key)
        if type(delays) is dict:
            out[key] = {room: s for room, s in delays.items()
                        if type(room) is str and type(s) is int and DELAY_LIMITS[0] <= s <= DELAY_LIMITS[1]}
    contacts = raw.get("contacts")
    if type(contacts) is dict:
        out["contacts"] = {room: [e for e in ids if type(e) is str and e.startswith("binary_sensor.")][:MAX_CONTACTS]
                           for room, ids in contacts.items() if type(room) is str and type(ids) is list}
    doors = raw.get("doors")
    if type(doors) is dict:  # only contacts of the room itself; anything else stays a window
        out["doors"] = {room: [e for e in out["contacts"].get(room, []) if e in ids]
                        for room, ids in doors.items() if type(room) is str and type(ids) is list}
        out["doors"] = {room: ids for room, ids in out["doors"].items() if ids}
    persons = raw.get("room_persons")
    if type(persons) is dict:
        out["room_persons"] = {
            room: [e for e in ids if type(e) is str and e.split(".")[0] in PRESENCE_DOMAINS][:MAX_PRESENCE]
            for room, ids in persons.items() if type(room) is str and type(ids) is list}
    return out


class ComfortError(ValueError):
    def __init__(self, field, code):
        super().__init__(code)
        self.field, self.code = field, code


def validate_presence(hass, user_input, current):
    """The people of the house and the away delay (Configure → Home → Presence)."""
    out = dict(current)
    people = user_input.get("presence_entities") or []
    if (type(people) is not list or len(people) > MAX_PRESENCE or len(set(people)) != len(people)
            or any(type(e) is not str or e.split(".")[0] not in PRESENCE_DOMAINS for e in people)):
        raise ComfortError("presence_entities", "presence_entity_invalid")
    for entity_id in people:  # a person already chosen may be unavailable now (a phone off); a new one must exist
        if entity_id not in current["presence_entities"] and hass.states.get(entity_id) is None:
            raise ComfortError("presence_entities", "presence_entity_invalid")
    delay = number(user_input.get("away_delay", out["away_delay_min"]), *AWAY_DELAY_LIMITS)
    if delay is None or delay != int(delay):
        raise ComfortError("away_delay", "whole_number_invalid")
    out["presence_entities"] = list(people)
    # HA 0.4.0b13 and older read one entity: the first person (a downgrade then follows that person only).
    out["presence_entity"] = people[0] if people else None
    out["away_delay_min"] = int(delay)
    return out


def validate_settings(hass, user_input, current):
    """The comfort settings from the options form (preset temperatures, the pauses after a window or door)."""
    out = dict(current)
    for field, key, limits in (("comfort_temperature", "comfort_c", TEMPERATURE_LIMITS),
                               ("eco_temperature", "eco_c", TEMPERATURE_LIMITS)):
        value = number(user_input.get(field, out[key]), *limits)
        if value is None:
            raise ComfortError(field, "temperature_invalid")
        out[key] = round(value * 2) / 2
    for field, key, limits in (("contact_delay", "contact_delay_s", DELAY_LIMITS),
                               ("door_delay", "door_delay_s", DELAY_LIMITS)):
        value = number(user_input.get(field, out[key]), *limits)
        if value is None or value != int(value):
            raise ComfortError(field, "whole_number_invalid")
        out[key] = int(value)
    return out


def validate_contacts(hass, selections, known=()):
    """Window/door/opening binary sensors for one room (at most eight).

    Any brand works: Zigbee, Z-Wave, Shelly, Bluetooth or a template, as long as
    Home Assistant gives it the device class window, door, opening or garage door.
    known: the room's sensors so far; they stay accepted while they are
    unavailable (a sensor with an empty battery never blocks saving the room).
    """
    if type(selections) is not list or len(selections) > MAX_CONTACTS or len(set(selections)) != len(selections):
        raise ComfortError("contacts", "contacts_invalid")
    for entity_id in selections:
        if type(entity_id) is not str or not entity_id.startswith("binary_sensor."):
            raise ComfortError("contacts", "not_contact_sensor")
        if entity_id in known:
            continue
        state = hass.states.get(entity_id)
        if state is None or state.attributes.get("device_class") not in CONTACT_CLASSES:
            raise ComfortError("contacts", "not_contact_sensor")
    return list(selections)


def validate_kinds(windows, doors):
    """A room's window and door sensors from the two pickers: each sensor once, at most eight together."""
    if set(windows) & set(doors):
        raise ComfortError("contacts", "contact_window_and_door")
    if len(windows) + len(doors) > MAX_CONTACTS:
        raise ComfortError("contacts", "contacts_invalid")
    return list(windows) + list(doors), list(doors)


def room_contacts(entry, room_id):
    """The window and door sensors of one E32 room (Configure → Rooms or Comfort), windows and doors alike."""
    return list(comfort_options(entry)["contacts"].get(room_id, []))


def room_doors(entry, room_id):
    """The door sensors of one E32 room (1.0.1): a part of room_contacts()."""
    return list(comfort_options(entry)["doors"].get(room_id, []))


def doors_of(settings, room_id):
    return [e for e in settings.get("doors", {}).get(room_id, []) if e in settings["contacts"].get(room_id, [])]


def windows_of(settings, room_id):
    """The room's contacts that are no door: windows, also every contact chosen before 1.0.1."""
    doors = doors_of(settings, room_id)
    return [e for e in settings["contacts"].get(room_id, []) if e not in doors]


def room_contact_delay(settings, room_id):
    """Seconds an open window waits before this room pauses: its own delay, else the default."""
    return settings.get("contact_delays", {}).get(room_id, settings["contact_delay_s"])


def room_door_delay(settings, room_id):
    """Seconds an open door waits before this room pauses (1.0.1): its own delay, else the default."""
    return settings.get("door_delays", {}).get(room_id, settings.get("door_delay_s", DEFAULTS["door_delay_s"]))


def own_contact_delay(settings, delay_s, door=False):
    """What a room stores for a pause delay: None when it is the house default (the room then follows it)."""
    default = settings.get("door_delay_s", DEFAULTS["door_delay_s"]) if door else settings["contact_delay_s"]
    return None if delay_s == default else delay_s


def with_room_contacts(settings, room_id, contacts, delay_s=None, doors=None, door_delay_s=None):
    """The comfort settings with this room's sensors replaced (none: the room has no sensors and no own
    delays); delay_s / door_delay_s: the room's own pause delay for windows / doors (None keeps it; the
    house default drops it, so the room follows a later change of the default); doors: which of the
    contacts are doors (None keeps those that stay)."""
    rooms = {**settings["contacts"], room_id: list(contacts)}
    door_rooms = dict(settings.get("doors", {}))
    kept = [e for e in (door_rooms.get(room_id, []) if doors is None else doors) if e in contacts]
    if kept:
        door_rooms[room_id] = kept
    else:
        door_rooms.pop(room_id, None)
    result = {**settings, "contacts": rooms, "doors": door_rooms}
    for key, value, door in (("contact_delays", delay_s, False), ("door_delays", door_delay_s, True)):
        delays = dict(settings.get(key, {}))
        if value is not None:
            if own_contact_delay(settings, value, door) is None:
                delays.pop(room_id, None)
            else:
                delays[room_id] = value
        if not contacts:
            delays.pop(room_id, None)
        result[key] = delays
    if not contacts:
        rooms.pop(room_id, None)
    return result


def room_persons(entry, room_id):
    """The persons of one room (persons per room, beta.23); empty: the room follows the house."""
    return list(comfort_options(entry)["room_persons"].get(room_id, []))


def with_room_persons(settings, room_id, persons):
    """The settings with this room's persons replaced (an empty list removes the room)."""
    rooms = dict(settings.get("room_persons", {}))
    if persons:
        rooms[room_id] = list(persons)
    else:
        rooms.pop(room_id, None)
    return {**settings, "room_persons": rooms}


def validate_room_persons(hass, selections, known=()):
    """The room's persons from the room form; a person already chosen may be unavailable now."""
    people = selections or []
    if (type(people) is not list or len(people) > MAX_PRESENCE or len(set(people)) != len(people)
            or any(type(e) is not str or e.split(".")[0] not in PRESENCE_DOMAINS for e in people)):
        raise ComfortError("persons", "presence_entity_invalid")
    for entity_id in people:
        if entity_id not in known and hass.states.get(entity_id) is None:
            raise ComfortError("persons", "presence_entity_invalid")
    return list(people)


def persons_selector():
    """People for a room: persons, device trackers, groups and on/off helpers (zones count a house, not a room)."""
    return selector.EntitySelector({"filter": [{"domain": d} for d in PRESENCE_DOMAINS if d != "zone"],
                                    "multiple": True})


def supports_room_presence(hub):
    """E32 beta.23 and newer announce persons per room as away.room_presence (room.presence.v1)."""
    status = getattr(hub, "status", None)
    away = status.get("away") if type(status) is dict else None
    return type(away) is dict and away.get("room_presence") is True


def supports_door_contacts(hub):
    """E32 1.0.1 and newer keep windows and doors apart, each with its own delay (away.door_contacts)."""
    status = getattr(hub, "status", None)
    away = status.get("away") if type(status) is dict else None
    return type(away) is dict and away.get("door_contacts") is True


def contact_delay_text(settings, room_id=None, door=False):
    """The pause delay as the forms show it: "2 min" or "45 s" (a room's own delay with room_id; door: the doors')."""
    if door:
        seconds = room_door_delay(settings, room_id) if room_id else settings.get("door_delay_s", DEFAULTS["door_delay_s"])
    else:
        seconds = room_contact_delay(settings, room_id) if room_id else settings["contact_delay_s"]
    return f"{seconds // 60} min" if seconds >= 60 and seconds % 60 == 0 else f"{seconds} s"


def contact_selector(**extra):
    """The entity picker for window and door sensors of any brand."""
    return selector.EntitySelector({"filter": [{"domain": "binary_sensor", "device_class": list(CONTACT_CLASSES)}],
                                    "multiple": True, **extra})


@callback
def save_comfort(hass, entry, settings, extra=None):
    """Store the comfort settings without a reload and follow them at once (extra: other entry options to set
    with them, as {key: value})."""
    options = {**entry.options, CONF_COMFORT: settings, **(extra or {})}
    if options == dict(entry.options):
        return False
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if state is not None:
        state[ENERGY_ONLY_UPDATE] = dict(options)
    if not hass.config_entries.async_update_entry(entry, options=options) and state is not None:
        state.pop(ENERGY_ONLY_UPDATE, None)  # no listener runs: never leave the marker behind
    if state is not None and (forwarder := state.get("comfort_forwarder")) is not None:
        forwarder.reconfigure()
    return True


@callback
def drop_retired_options(hass, entry):
    """1.4.2: remove the comfort settings Home Assistant no longer keeps (RETIRED_OPTIONS, the length of a manual
    change) from the entry's options, without a reload, and mark the entry (RETIRED_MARKER). Runs at every set-up
    and does nothing once they are gone; an older version that wrote one back after a downgrade loses it again.
    True when the options changed."""
    raw = (getattr(entry, "options", None) or {}).get(CONF_COMFORT)
    if type(raw) is not dict or not set(RETIRED_OPTIONS) & set(raw):
        return False
    kept = {key: value for key, value in raw.items() if key not in RETIRED_OPTIONS}
    return save_comfort(hass, entry, kept, {RETIRED_MARKER: True})


def settings_schema(vol, settings):
    def box(low, high, step, unit):
        return selector.NumberSelector({"min": low, "max": high, "step": step, "mode": "box",
                                        "unit_of_measurement": unit})
    return vol.Schema({
        vol.Required("comfort_temperature", default=settings["comfort_c"]): box(*TEMPERATURE_LIMITS, 0.5, "°C"),
        vol.Required("eco_temperature", default=settings["eco_c"]): box(*TEMPERATURE_LIMITS, 0.5, "°C"),
        # In minutes, as in each room's own "Pause after" (stored in seconds, the E32's unit).
        vol.Required("contact_delay", default=settings["contact_delay_s"] / 60): box(
            DELAY_LIMITS[0] / 60, DELAY_LIMITS[1] / 60, 0.5, "min"),
        # Doors (1.0.1): usually longer, so walking through a door does not pause the room.
        vol.Required("door_delay", default=settings["door_delay_s"] / 60): box(
            DELAY_LIMITS[0] / 60, DELAY_LIMITS[1] / 60, 0.5, "min"),
    })


def presence_schema(vol, settings, away=False):
    """Configure → Home → Presence: the people of the house, how long everyone must be away and the away
    temperature (away: the E32's current one in °C, None when it reports none; False: no E32 field)."""
    people = settings["presence_entities"]
    fields = {
        (vol.Optional("presence_entities", description={"suggested_value": people}) if people
         else vol.Optional("presence_entities")): selector.EntitySelector(
            {"filter": [{"domain": list(PRESENCE_DOMAINS)}], "multiple": True}),
        vol.Required("away_delay", default=settings["away_delay_min"]): selector.NumberSelector(
            {"min": AWAY_DELAY_LIMITS[0], "max": AWAY_DELAY_LIMITS[1], "step": 1, "mode": "box",
             "unit_of_measurement": "min"}),
    }
    if away is not False:  # the same range and step as the number "Temperature when nobody is home"
        fields[vol.Optional("away_temperature", description={"suggested_value": away})] = selector.NumberSelector(
            {"min": AWAY_LIMITS[0], "max": AWAY_LIMITS[1], "step": 0.5, "mode": "box", "unit_of_measurement": "°C"})
    return vol.Schema(fields)


def validate_away_temperature(user_input, current):
    """The away temperature to send (5–25 °C), or None when it is empty or unchanged."""
    value = user_input.get("away_temperature")
    if value is None or value == "":
        return None
    temperature = number(value, *AWAY_LIMITS)
    if temperature is None:
        raise ComfortError("away_temperature", "comfort_away_temperature_invalid")
    return None if current is not None and float(temperature) == float(current) else float(temperature)


# -- the house settings without the form (1.4): shared by the options steps and the settings panel (settings_house.py)

async def async_save_presence(hass, entry, house, user_input, shown_away):
    """Store the people of the house, the away delay and the away temperature (Configure → House → Presence).

    ``house``: the E32's house state (None: no away temperature to send); ``shown_away``: the away temperature the
    form showed, so one changed on the E32 meanwhile stays unless the user changed it too. The temperature goes to
    the E32 first: when the E32 refuses it, nothing is saved. Raises ComfortError (field, code; ``error``: the E32's
    word for a refusal)."""
    settings = validate_presence(hass, user_input, comfort_options(entry))
    temperature = validate_away_temperature(user_input, shown_away) if house is not None else None
    if temperature is not None:
        try:
            await house.async_command(temperature=temperature)
        except HomeAssistantError as err:
            key = getattr(err, "translation_key", None)
            failure = ComfortError("away_temperature", "away_temperature_update_required"
                                   if key == "house_mode_update_required" else "away_temperature_not_saved")
            failure.error = (getattr(err, "translation_placeholders", None) or {}).get("error") or key or "unknown"
            raise failure from None
    save_comfort(hass, entry, settings)


def save_room_defaults(hass, entry, user_input):
    """Store the room defaults (Configure → House → Room defaults): the temperatures of a room without a week
    program and the pause after a window or door opens (minutes in the form, seconds stored). Raises ComfortError."""
    for field in ("contact_delay", "door_delay"):
        minutes = user_input.get(field)
        if type(minutes) in (int, float) and type(minutes) is not bool:  # the form shows minutes
            user_input = {**user_input, field: round(minutes * 60, 6)}
    save_comfort(hass, entry, validate_settings(hass, user_input, comfort_options(entry)))


def save_room_contacts(hass, entry, room_id, windows, doors):
    """Store one room's window and door contacts (Configure → House → Window and door contacts); the room's own
    pause delays stay. A sensor the room had may be unavailable now. Raises ComfortError."""
    current = comfort_options(entry)
    known = current["contacts"].get(room_id, [])
    contacts, door_ids = validate_kinds(validate_contacts(hass, list(windows or []), known),
                                        validate_contacts(hass, list(doors or []), known))
    save_comfort(hass, entry, with_room_contacts(current, room_id, contacts, doors=door_ids))


def contacts_room_schema(vol, rooms, room_id):
    """Step one: the room whose window/door sensors to change."""
    options = [{"value": rid, "label": name} for rid, name in rooms]
    return vol.Schema({
        vol.Required("room", default=room_id or (rooms[0][0] if rooms else "")): selector.SelectSelector(
            {"options": options, "mode": "dropdown"}),
    })


def contacts_schema(vol, contacts, doors=()):
    """Step two: that room's window and door sensors, prefilled with the ones it has."""
    return vol.Schema({
        vol.Optional("contacts", description={"suggested_value": contacts or None}): contact_selector(),
        vol.Optional("door_contacts", description={"suggested_value": list(doors) or None}): contact_selector(),
    })


# -- presence and contacts (forwarded to the E32) ---------------------------------

PRESENCE_DOMAINS = ("person", "group", "zone", "device_tracker", "binary_sensor", "input_boolean")


def presence_home(state):
    """True: someone is home, False: everyone away, None: unknown.

    person / device_tracker / group: "home" is home, any other place away;
    zone (zone.home): the number of people in it; binary_sensor /
    input_boolean: on = someone home.
    """
    if state is None or state.state in ("unknown", "unavailable", ""):
        return None
    domain = state.entity_id.split(".")[0]
    if domain == "zone":
        count = number(state.state, 0, 10000)
        return None if count is None else count > 0
    if domain in ("binary_sensor", "input_boolean"):
        return {"on": True, "off": False}.get(state.state)
    return state.state == "home"


PRESENCE_MEMORY = DOMAIN + "_presence_memory"
PRESENCE_SAVE_DELAY = 10


class PresenceMemory:
    """When each person last left home, kept across Home Assistant restarts.

    A person's last_changed also moves between two away zones (Work ->
    not_home), from unavailable back to not_home and at every Home Assistant
    start; none of those is someone leaving. "left" is the moment a person
    stopped being home (home -> anything else) and stays until they are home
    again. A person never seen home here falls back to last_changed; one who
    was home when Home Assistant stopped counts from their first state after.
    """

    def __init__(self, hass, store=None):
        self.hass, self.store = hass, store
        self.people = {}  # entity_id -> {"home": True} or {"home": False, "left": datetime}

    async def async_load(self):
        stored = await self.store.async_load() if self.store is not None else None
        people = stored.get("people") if type(stored) is dict else None
        for entity_id, known in people.items() if type(people) is dict else ():
            if type(known) is not dict or entity_id in self.people:
                continue
            if known.get("home") is True:
                self.people[entity_id] = {"home": True}
            elif known.get("home") is False and type(known.get("left")) is str:
                left = dt_util.parse_datetime(known["left"])
                if left is not None and left.tzinfo is not None:
                    self.people[entity_id] = {"home": False, "left": left}

    def _data(self):
        return {"people": {e: {"home": True} if k["home"] else {"home": False, "left": k["left"].isoformat()}
                           for e, k in self.people.items()}}

    @callback
    def observe(self, entity_id, state):
        value = presence_home(state)
        known = self.people.get(entity_id)
        if value is True:
            new = {"home": True}
        elif known is not None and not known["home"]:
            return  # already away: another zone, unavailable, a restart
        elif value is False or known is not None:
            # Home (or first seen) until now: unavailable counts from the moment home was last seen.
            new = {"home": False, "left": state.last_changed if state is not None else dt_util.utcnow()}
        else:
            return
        if new != known:
            self.people[entity_id] = new
            if self.store is not None:
                self.store.async_delay_save(self._data, PRESENCE_SAVE_DELAY)

    def left(self, state):
        known = self.people.get(state.entity_id)
        return known["left"] if known is not None and not known["home"] else state.last_changed


def house_presence(hass, people, delay_min, now=None):
    """(home, wait_s) for the people of the house.

    home is True while anyone is home, while anyone's place is unknown or
    unavailable ("bij twijfel blijft het warm") and while the last person left
    less than the away delay ago (PresenceMemory); then wait_s is the seconds
    until the house counts as away. False: everyone has been away for at least
    the delay. None: no people configured.
    """
    if not people:
        return None, None
    states = [hass.states.get(e) for e in people]
    values = [presence_home(state) for state in states]
    if any(value is not False for value in values):
        return True, None
    now = now or dt_util.utcnow()
    memory = hass.data.get(PRESENCE_MEMORY)
    left = max(memory.left(state) if memory is not None else state.last_changed for state in states)
    remaining = (left + timedelta(minutes=delay_min) - now).total_seconds()
    if remaining > 0:
        return True, remaining
    return False, None


def contacts_open(states):
    """True when any contact is open, False when all are closed, None when unknown."""
    values = [None if s is None else {"on": True, "off": False}.get(s.state) for s in states]
    if any(v is True for v in values):
        return True
    if values and all(v is False for v in values):
        return False
    return None


def contact_payloads(hass, settings, room_id, doors=False):
    """The contact reports of one room: (kind, payload or None while unknown) for each kind it has.

    doors: the E32 keeps doors apart (supports_door_contacts): windows as before (no "contact"), doors with
    "contact": "door" and their own delay. Else one report for all of them (legacy_contact_payload).
    """
    windows, door_ids = windows_of(settings, room_id), doors_of(settings, room_id)
    states = {e: hass.states.get(e) for e in windows + door_ids}
    if not doors:
        return [("window", legacy_contact_payload(settings, room_id, [states[e] for e in windows],
                                                  [states[e] for e in door_ids]))]
    out = []
    if windows:
        value = contacts_open([states[e] for e in windows])
        out.append(("window", None if value is None else {
            "kind": "contact", "room": room_id, "open": value, "delay_s": room_contact_delay(settings, room_id)}))
    if door_ids:
        value = contacts_open([states[e] for e in door_ids])
        out.append(("door", None if value is None else {
            "kind": "contact", "room": room_id, "open": value, "delay_s": room_door_delay(settings, room_id),
            "contact": "door"}))
    return out


def legacy_contact_payload(settings, room_id, windows, doors):
    """One report for firmware without door contacts (1.0.0): open while any contact is open (None: unknown,
    as before); the window delay while a window is open, else the door delay while a door is open."""
    value = contacts_open(windows + doors)
    if value is None:
        return None
    delay = (room_door_delay(settings, room_id) if value and contacts_open(windows) is not True
             else room_contact_delay(settings, room_id))
    return {"kind": "contact", "room": room_id, "open": value, "delay_s": delay}


def closed_payload(settings, room_id, kind):
    """The report that one kind of contact of a room is closed (forgotten and stale contacts)."""
    if kind == "door":
        return {"kind": "contact", "room": room_id, "open": False, "delay_s": room_door_delay(settings, room_id),
                "contact": "door"}
    return {"kind": "contact", "room": room_id, "open": False, "delay_s": room_contact_delay(settings, room_id)}


def comfort_payloads(hass, settings, room_ids, only=None, now=None, room_presence=False, doors=False):
    """The typed heating_input payloads (dicts) for the configured contacts and presence.

    room_presence: the E32 understands persons per room (supports_room_presence); doors: it keeps doors
    apart (supports_door_contacts).
    """
    payloads = []
    for room_id, ids in sorted(settings["contacts"].items()):
        if room_id not in room_ids or not ids or (only is not None and only not in ids):
            continue
        payloads.extend(payload for _kind, payload in contact_payloads(hass, settings, room_id, doors) if payload)
    people = settings["presence_entities"]
    if people and only in (None, *people):
        home, _wait = house_presence(hass, people, settings["away_delay_min"], now)
        if home is not None:
            payloads.append({"kind": "presence", "home": home})
    if room_presence:
        for room_id, persons in sorted(settings.get("room_persons", {}).items()):
            if room_id not in room_ids or not persons or (only is not None and only not in persons):
                continue
            home, _wait = house_presence(hass, persons, settings["away_delay_min"], now)
            if home is not None:
                payloads.append({"kind": "room_presence", "room": room_id, "home": home})
    return payloads


def away_waits(hass, settings, room_ids=None):
    """Seconds until the house or a room with its own persons counts as away (the shortest), or None."""
    groups = [settings["presence_entities"]] + [persons for room_id, persons in settings.get("room_persons", {}).items()
                                                if room_ids is None or room_id in room_ids]
    waits = [wait for people in groups if people
             for _home, wait in [house_presence(hass, people, settings["away_delay_min"])] if wait is not None]
    return min(waits) if waits else None


def people_of(settings):
    """Every person of the house and of the rooms."""
    return sorted(set(settings["presence_entities"]).union(*settings.get("room_persons", {}).values()))


class ComfortForwarder:
    """Sends contact and presence states to the E32: on each change, every 5 minutes and when it is back."""

    def __init__(self, hass, entry, hub, send, track_state=async_track_state_change_event):
        self.hass, self.entry, self.hub, self.send, self.track_state = hass, entry, hub, send, track_state
        self._unsubscribe = None
        self._was_fresh = False
        self._away_timer = None  # sends "everyone away" once the away delay has passed
        self._kinds = set()      # (room, kind) of the contacts last configured (forgotten(): closed once)
        self._doors = None       # supports_door_contacts() at the last send (hub_changed: sent again when it changes)
        self._closed = set()     # (room, kind) told closed while the E32 still reports it open (stale(): once)

    @property
    def settings(self):
        return comfort_options(self.entry)

    def entities(self):
        s = self.settings
        ids = [e for room in sorted(s["contacts"]) for e in s["contacts"][room]]
        persons = [e for room in sorted(s["room_persons"]) for e in s["room_persons"][room]]
        return sorted(set(ids + s["presence_entities"] + persons))

    @callback
    def publish(self, only=None):
        settings = self.settings
        memory = self.hass.data.get(PRESENCE_MEMORY)
        if memory is not None:
            for entity_id in people_of(settings):
                memory.observe(entity_id, self.hass.states.get(entity_id))
        if not self.hub.fresh:
            return
        doors = self._doors = supports_door_contacts(self.hub)
        for payload in self.forgotten(settings, doors) + comfort_payloads(
                self.hass, settings, set(self.hub.rooms), only, room_presence=supports_room_presence(self.hub),
                doors=doors):
            self.send(json.dumps(payload, separators=(",", ":")))
        self._schedule_away(settings)

    def forgotten(self, settings, doors):
        """A closed report, once, for a kind of contact a room no longer has (all its windows or doors removed,
        or a sensor moved from window to door): the E32 would otherwise keep an open one for 15 minutes."""
        rooms = set(self.hub.rooms)
        kinds = {(room_id, kind) for room_id in settings["contacts"] if room_id in rooms
                 for kind, _payload in contact_payloads(self.hass, settings, room_id, doors)}
        gone, self._kinds = self._kinds - kinds, kinds
        gone = {(room_id, kind) for room_id, kind in gone if room_id in rooms and (kind == "window" or doors)}
        self._closed |= gone
        return [closed_payload(settings, room_id, kind) for room_id, kind in sorted(gone)]

    def stale(self, settings, doors):
        """A closed report, once, for a kind of contact the E32 reports open (or its delay running) in a room that
        has no contact of that kind in Home Assistant (any more).

        Only Home Assistant reports contacts to the E32, so that state is a leftover: a contact removed or moved
        while Home Assistant was not running, or while the E32 was offline and Home Assistant restarted before it
        was back (forgotten() keeps that in memory only). It needs no stored memory: the E32's own room status says
        it, after any restart. Sent again only once the E32 stopped reporting it or at the 5-minute refresh, so a
        status that still shows it open right after the report sends nothing more.
        """
        wanted = set()
        for room_id, room in self.hub.rooms.items():
            comfort = room.get("comfort") if type(room) is dict else None
            if type(comfort) is not dict or comfort.get("window") not in ("open", "pending"):
                continue
            if not doors:  # one report for all of the room's contacts (1.0.0)
                if not settings["contacts"].get(room_id):
                    wanted.add((room_id, "window"))
                continue
            opening = comfort.get("opening")
            have = {"window": windows_of(settings, room_id), "door": doors_of(settings, room_id)}
            wanted |= {(room_id, kind) for kind in ((opening,) if opening in have else tuple(have)) if not have[kind]}
        self._closed &= wanted
        new, self._closed = wanted - self._closed, self._closed | wanted
        return [closed_payload(settings, room_id, kind) for room_id, kind in sorted(new)]

    @callback
    def _schedule_away(self, settings):
        """Everyone of the house or of a room left: send "away" exactly when the away delay has passed
        (not at the next 5-minute refresh)."""
        if self._away_timer is not None:
            self._away_timer()
            self._away_timer = None
        rooms = set(self.hub.rooms) if supports_room_presence(self.hub) else set()
        wait = away_waits(self.hass, settings if rooms else {**settings, "room_persons": {}}, rooms)
        if wait is not None:
            @callback
            def due(_now):
                self._away_timer = None
                self.publish()
            self._away_timer = async_call_later(self.hass, wait + 1, due)

    @callback
    def refresh(self, _now=None):
        """Every REFRESH: all again (the E32 forgets a report after 15 minutes).

        A @callback, so Home Assistant runs it in the event loop. As a plain lambda (beta.19 to rc.5) it ran
        in a worker thread, where sending raises: the refresh never went out, and from 1.0.0rc5 on every
        refresh also kept a place in the sender until room values were dropped too (P22).
        """
        self._closed.clear()  # a leftover the E32 still reports is told closed again (stale)
        self.publish()
        self._close_stale()

    @callback
    def _close_stale(self):
        if self.hub.fresh:
            for payload in self.stale(self.settings, supports_door_contacts(self.hub)):
                self.send(json.dumps(payload, separators=(",", ":")))

    @callback
    def _changed(self, event):
        self.publish(event.data["entity_id"])

    @callback
    def hub_changed(self):
        """The E32 is (back) online, or it now does or no longer announces door contacts: send everything at once.

        After an update to or from 1.0.1 the first send can still follow the previous status (a quick restart
        is told before the new status arrives): sent again as soon as the announcement changes, so 1.0.0
        never keeps a door report as its only state, and 1.0.1 gets the doors apart without waiting for the
        5-minute refresh.
        """
        fresh = self.hub.fresh
        if fresh and (not self._was_fresh or (self._doors is not None
                                              and supports_door_contacts(self.hub) != self._doors)):
            self.publish()
        self._was_fresh = fresh
        self._close_stale()

    @callback
    def reconfigure(self):
        self.stop()
        entities = self.entities()
        if entities:
            self._unsubscribe = self.track_state(self.hass, entities, self._changed)
        self.publish()

    @callback
    def stop(self):
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None
        if self._away_timer is not None:
            self._away_timer()
            self._away_timer = None


# -- commands ------------------------------------------------------------------------


def comfort_error(err):
    """A clear Home Assistant error for a refused or failed comfort command."""
    from .controller_link import HeatingPlanRejected
    from .room_plan import plan_error
    if isinstance(err, HeatingPlanRejected) and err.error not in ("save_unconfirmed", "storage_full"):
        key = E32_ERRORS.get(err.error)
        if key:
            return ServiceValidationError(translation_domain=DOMAIN, translation_key=key)
        return ServiceValidationError(translation_domain=DOMAIN, translation_key="comfort_rejected",
                                      translation_placeholders={"error": err.error})
    return plan_error(err)


def comfort_key(command):
    """What a newer house command supersedes: the house (mode, away temperature, holiday end), or (rc.4)
    the holiday temperature on its own, so a house mode chosen right after it never drops it."""
    if type(command) is dict and "holiday_temperature" in command and not {"house_mode", "away", "holidays"} & set(command):
        return ("holiday_temperature",)
    return ("house",)


async def async_comfort_command(link, command):
    """POST one command over the room-plan link's stored connection (RoomPlanLink.async_call).

    With every E32 web session in use it waits for one, without holding up
    other requests. A newer command for the same room (or the house mode)
    supersedes it: None, nothing sent; the newest value is the one that goes
    out. House commands go through e32_house.async_house_change, which carries
    the superseded one's fields along (the E32 takes the house mode, away
    temperature and holiday end as one command).
    """
    from .controller_link import ControllerLinkError
    from .room_plan import WriteSuperseded
    room = command.get("room") if type(command) is dict else None
    try:
        answer = await link.async_call(lambda client: client.async_comfort_command(command), write=True,
                                       key=("room", room) if room is not None else comfort_key(command))
    except WriteSuperseded:
        return None
    except ControllerLinkError as err:
        raise comfort_error(err) from None
    if type(answer) is not dict or answer.get("schema") != 1:
        raise HomeAssistantError(translation_domain=DOMAIN, translation_key="room_plan_unconfirmed")
    return answer


def override_command(room_id, kind, temperature=None, minutes=None):
    command = {"room": room_id, "override": kind}
    if temperature is not None:
        command["temperature"] = round(float(temperature), 2)
    if minutes is not None:
        command["minutes"] = int(minutes)
    return command


def away_command(on, temperature=None, until=None, now=None):
    """{"away": ...}; until: a datetime (aware), within a year."""
    command = {"away": bool(on)}
    if on and temperature is not None:
        if number(temperature, *AWAY_LIMITS) is None:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="comfort_away_temperature")
        command["temperature"] = round(float(temperature), 2)
    if on and until is not None:
        now = now or dt_util.utcnow()
        if until.tzinfo is None:
            until = until.replace(tzinfo=dt_util.get_default_time_zone())
        if not now < until <= now + timedelta(days=MAX_AWAY_DAYS):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="comfort_away_until")
        command["until"] = int(until.timestamp())
    return command


# -- a manual change (1.4.2) ---------------------------------------------------------


def off_until_ended(plan_room, status_room, now=None):
    """E32 1.4.1: "Off until" has passed and the E32 runs the room again, but the plan still says Off, so that
    firmware refuses a manual change (room_inactive) until the plan is written (e32_setting_device.off_until_over)."""
    return off_until_over(plan_room if type(plan_room) is dict else None,
                          status_room if type(status_room) is dict else None, now or time.time())


def manual_supported(link):
    """True when the E32 that answered the plan Home Assistant last read knows the command ``override: manual``
    (room.manual.v1). Read at the moment of every change, never kept: after a firmware update or a downgrade the
    plan is read again (HA-REREAD), so the answer follows the firmware that runs now."""
    return MANUAL_FEATURE in (getattr(link, "features", None) or ())


async def async_heal_off_until(link, room_id, status_room):
    """E32 1.4.1: write the end of a passed "Off until" into the plan (routine) before a manual change; nothing for
    an E32 that announces room.manual.v1 (it writes it itself and takes the change). True when it wrote."""
    from .room_plan import on_state, set_state
    plan = link.room(room_id) if link is not None else None
    if manual_supported(link) or not off_until_ended(plan, status_room):
        return False
    await async_routine_room_change(link, room_id, set_state(on_state(plan)))
    return True


def manual_command(room_id, temperature, by="ha"):
    """{"room", "override": "manual", "temperature", "by"} (room.manual.v1): the E32 decides what it becomes."""
    return {"room": room_id, "override": "manual", "temperature": round(float(temperature), 2), "by": by}


def _answer(applied, temperature, until=None, minutes=None):
    return {"applied": applied, "temperature": temperature,
            "until": until if type(until) is int and until > 0 else None,
            "minutes": minutes if type(minutes) is int and minutes > 0 else None}


def _room_until(answer, room_id):
    """The end of the room's change in the E32's answer (its comfort state), else None."""
    rooms = answer.get("rooms") if type(answer) is dict else None
    for room in rooms if type(rooms) is list else []:
        if type(room) is dict and room.get("id") == room_id:
            return room.get("until")
    return None


async def async_manual_change(link, room_id, temperature, *, running=None, status_room=None, by="ha"):
    """One manual change of a room's temperature (design §3.1); the room's state never changes.

    With room.manual.v1 the E32 decides (one command): until the next switch time with a week program, the room's
    temperature without a week program without one (also on a room that is Off), 120 minutes without a clock. For
    an older E32, or one that answers invalid_override (a downgrade not yet read again), Home Assistant makes the
    same split: ``next``; without a clock (or when the E32 says the room has no program) ``timed`` MANUAL_MINUTES;
    without a program a routine plan write of the temperature without a week program, which also ends a running
    override (``running``: the room's override now) and is skipped when the value is already set; a passed "Off
    until" written first (async_heal_off_until; ``status_room``: the room as the E32 reports it). Several requests
    share one E32 sign-in. A room that is Off and has a week program is refused by the E32 (comfort_room_off).

    Returns {"applied": "next" | "timed" | "fixed", "temperature", "until" (unix) | None, "minutes" | None}, or None
    when a newer change of the same room superseded it. Raises ServiceValidationError / HomeAssistantError.
    """
    from .room_plan import set_fallback
    value = half_up(temperature)
    if manual_supported(link):
        try:
            answer = await async_comfort_command(link, manual_command(room_id, value, by))
        except ServiceValidationError as err:
            if not manual_unknown(err):
                raise
        else:
            if answer is None:
                return None
            applied = answer.get("applied") if answer.get("applied") in ("next", "timed", "fixed") else None
            shown = number(answer.get("temperature"), 5, 35)
            return _answer(applied, shown if shown is not None else value, answer.get("until"), answer.get("minutes"))
    plan = link.room(room_id) or {}
    program = has_program(plan)
    heal = off_until_ended(plan, status_room)
    end_override = not program and running in OVERRIDES
    session = getattr(link, "async_session", None) if heal or end_override else None
    async with session() if session is not None else nullcontext():
        if heal:
            await async_heal_off_until(link, room_id, status_room)
        if not program:
            centi = int(round(value * 100))
            if plan.get("fallback_centi_c") != centi:
                stored = await async_routine_room_change(link, room_id, set_fallback(centi), ("fallback", room_id))
                if stored is None:
                    return None  # a newer temperature for this room replaced this one
            if end_override:
                await async_comfort_command(link, override_command(room_id, "none"))
            return _answer("fixed", value)
        try:
            answer = await async_comfort_command(link, override_command(room_id, "next", value))
        except ServiceValidationError as err:
            if err.translation_key not in ("comfort_no_clock", "comfort_no_schedule"):
                raise
        else:
            return None if answer is None else _answer("next", value, _room_until(answer, room_id))
        answer = await async_comfort_command(link, override_command(room_id, "timed", value, MANUAL_MINUTES))
        return None if answer is None else _answer("timed", value, _room_until(answer, room_id), MANUAL_MINUTES)


# -- the climate entity --------------------------------------------------------------


def _program_counts(room):
    """{centi °C: how often} of the switch points of the room's week program ({} without one)."""
    schedule = room.get("schedule")
    count = {}
    for day in schedule if type(schedule) is list else []:
        for point in day if type(day) is list else []:
            if type(point) is list and len(point) == 2 and type(point[1]) is int:
                count[point[1]] = count.get(point[1], 0) + 1
    return count


def levels_from(plan_room):
    """Where program_levels() takes the room's Comfort, Eco and Night from (1.4.4, issue #17): "room" (the levels it
    stores), "program" (inferred from its week program) or "house" (the Room defaults of Settings → House: a room
    without a week program and without stored levels); None while the plan is not read."""
    if type(plan_room) is not dict:
        return None
    if room_levels(plan_room) is not None:
        return "room"
    return "program" if _program_counts(plan_room) else "house"


def program_levels(plan_room, settings):
    """(comfort, eco, night) in °C: the room's week planner levels.

    The levels the room stores (E32 beta.23, room_levels) when it has them;
    otherwise inferred from its week program exactly like the planner does for
    older firmware (week-editor.js infer(): warmest = Comfort, coolest = Night,
    the most used in between = Eco). A room without either starts from the
    former house settings: "comfort_c" as Comfort and "eco_c" as Night (the
    one-time migration; the planner stores the room's own levels on save).
    """
    room = plan_room or {}
    stored = room_levels(room)
    if stored is not None:
        return stored["comfort"] / 100, stored["eco"] / 100, stored["night"] / 100
    lo, hi = room.get("minimum_centi_c"), room.get("maximum_centi_c")
    lo, hi = (lo, hi) if type(lo) is int and type(hi) is int and lo <= hi else (500, 3000)
    clamp = lambda v: max(lo, min(hi, v))  # noqa: E731
    half_up = lambda v: int(v + 0.5)  # noqa: E731  (JavaScript Math.round for these positive values)
    count = _program_counts(room)
    values = sorted(count, reverse=True)
    if not values:
        comfort, night = clamp(round(settings["comfort_c"] * 100)), clamp(round(settings["eco_c"] * 100))
        return comfort / 100, clamp(half_up((comfort + night) / 100) * 50) / 100, night / 100
    comfort = values[0]
    night = values[-1] if len(values) > 1 else clamp(1600)
    middle = sorted(values[1:-1], key=lambda v: -count[v])
    eco = middle[0] if middle else clamp(half_up((comfort + night) / 100) * 50)
    if night == comfort:
        night = clamp(comfort - 300)
    if len({comfort, eco, night}) < 3:
        eco = next((v for v in map(clamp, (comfort - 100, night + 100, comfort + 100)) if v not in (comfort, night)), eco)
    return comfort / 100, eco / 100, night / 100



def _iso(value):
    return datetime.fromtimestamp(value, timezone.utc).isoformat() if type(value) is int and value > 0 else None


class E32RoomClimate(RoomEntity, ClimateEntity):
    """One E32 room as a thermostat. Reads the telemetry; writes overrides, away or the plan.

    In summer (the house mode Summer, E32 1.4.1) every room is off (hvac_mode off, attribute ``reason`` "summer"): a
    temperature, a mode, a preset, an override or away is refused with "Summer mode is on: switch it off first." and
    nothing is sent to the E32.

    1.4.2: a temperature never changes the room's state (async_manual_change); while the room is Off it shows the
    temperature it keeps (its week program now, else its temperature without a week program, from the plan). The
    attributes ``applied`` ("next": until the next switch time, "timed": for a time, "fixed": it became the room's
    temperature without a week program) and ``until`` say what a manual change does.
    """

    _attr_name = None  # the room device's name
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_hvac_modes = [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = (ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
                                | ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF)
    # A translated sentence that changes with every step and message: shown, not kept in the history.
    _unrecorded_attributes = frozenset({"smart_warm_up"})

    def __init__(self, hub, room, entry):
        self._attach_room(hub, room, "thermostat")
        self.entry = entry
        self._pending = None  # (°C, None while its write runs, else monotonic time it was sent)
        self._answer = None   # the E32's answer to the last manual change from here, with "at" (monotonic)

    # -- state ---------------------------------------------------------------------
    @property
    def link(self):
        return self.hub.plan

    @property
    def plan_room(self):
        return self.link.room(self.room_id) if self.link is not None else None

    @property
    def comfort(self):
        room = self.room or {}
        return room.get("comfort") if type(room.get("comfort")) is dict else {}

    @property
    def away(self):
        status = self.hub.status or {}
        return status.get("away") if type(status.get("away")) is dict else {}

    @property
    def available(self):
        return self.hub.fresh and self.room is not None and self.link is not None

    def _summer(self):
        """Whether the house is in summer: the house mode as the house mode select shows it (the E32's answer to a
        command, else its status), else the room's own report (setpoint_source "summer")."""
        from .e32_house import KEY, house_away
        state = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id) if self.hass is not None else None
        house = state.get(KEY) if type(state) is dict else None
        away = house.away if house is not None else house_away(self.hub)
        if type(away) is dict and type(away.get("mode")) is str:
            return away["mode"] == "summer"
        return (self.room or {}).get("setpoint_source") == "summer"

    def _refuse_in_summer(self):
        if self._summer():
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="summer_mode_on")

    @property
    def current_temperature(self):
        return number((self.room or {}).get("temperature"), -40, 85)

    def _stored_target(self):
        """While the room is Off (the E32 reports no target for it): the temperature it keeps, from the plan: its week
        program now, else its temperature without a week program."""
        plan = self.plan_room
        if type(plan) is not dict:
            return None
        if has_program(plan):
            from .room_overview import e32_zone, program_target_now
            zone = e32_zone(self.hass, self.entry) if self.hass is not None else dt_util.get_default_time_zone()
            value = program_target_now(plan, datetime.now(timezone.utc), zone)
            if value is not None:
                return value
        centi = plan.get("fallback_centi_c")
        return number(centi / 100, 5, 35) if type(centi) is int else None

    @property
    def target_temperature(self):
        reported = (self._stored_target() if self._off()
                    else number((self.room or {}).get("setpoint"), 5, 35))
        if self._pending is not None:
            value, sent = self._pending
            if sent is None or ((reported is None or abs(reported - value) >= 0.05)
                                and time.monotonic() - sent < PENDING_SECONDS):
                return value
            self._pending = None
        return reported

    @property
    def min_temp(self):
        from .room_plan import setpoint_range
        return setpoint_range(self.plan_room)[0]

    @property
    def max_temp(self):
        from .room_plan import setpoint_range
        return setpoint_range(self.plan_room)[1]

    @property
    def hvac_mode(self):
        room = self.room
        if room is None:
            return None
        if room.get("state") == "inactive" or self._summer():
            return HVACMode.OFF
        return HVACMode.HEAT if self.comfort.get("override") in OVERRIDES else HVACMode.AUTO

    @property
    def hvac_action(self):
        room = self.room
        if room is None:
            return None
        if room.get("state") == "inactive" or (self._summer() and room.get("demand") is not True):
            return HVACAction.OFF  # in summer the E32 heats a room only against frost
        return HVACAction.HEATING if room.get("demand") is True else HVACAction.IDLE

    @property
    def preset_modes(self):
        from .room_plan import follows
        if follows(getattr(self.link, "plan", None)) or self._state() == "follow":
            return [*PRESETS, PRESET_HEAT_ALONG]
        return PRESETS

    def _state(self):
        """The room's state as its Heating select shows it: the E32's report, unless our plan write is newer."""
        operation = getattr(self.link, "operation", None)
        room = operation(self.room_id) if operation is not None else self.room
        return (room or {}).get("state")

    @property
    def preset_mode(self):
        comfort = self.comfort
        if comfort.get("override") == "boost":  # 1.4.2: also on Heat along only, while it runs
            return PRESET_BOOST
        if self._state() == "follow":  # 1.4: the room state Heat along only, whatever else holds its target
            return PRESET_HEAT_ALONG
        if comfort.get("override") in OVERRIDES:
            target = number(comfort.get("target_c"), 5, 35)
            levels = program_levels(self.plan_room, comfort_options(self.entry))
            centi = round(target * 100) if target is not None else None
            # Equal levels: the first one (Comfort, Eco, Night) names the hold.
            return next((preset for preset, i in LEVEL_PRESETS.items() if centi == round(levels[i] * 100)), PRESET_NONE)
        plan = self.plan_room
        if type(plan) is dict and not has_program(plan) and type(plan.get("fallback_centi_c")) is int:
            # 1.4.4 (#17): without a week program a level becomes the room's temperature without a week program; the
            # level that temperature equals is the room's preset (Comfort, Eco, Night first), else "none" (Program).
            levels = program_levels(plan, comfort_options(self.entry))
            return next((preset for preset, i in LEVEL_PRESETS.items()
                         if plan["fallback_centi_c"] == round(levels[i] * 100)), PRESET_NONE)
        return PRESET_NONE  # away is the house mode (its own select), not a preset of one room

    @property
    def extra_state_attributes(self):
        room = self.room
        if room is None:
            return None
        comfort, away = self.comfort, self.away
        from .e32_setting_device import setting_device_attributes
        from .room_away import away_reason, room_away
        own = room_away(self.plan_room)
        return {"room_id": self.room_id, "comfort_mode": comfort.get("mode", "program"),
                # 1.4.1: why the thermostat is off although the room is on: "summer" (the house mode Summer), else None.
                "reason": "summer" if self._summer() else None,
                "window": comfort.get("window"), "override": comfort.get("override"),
                # 1.4.2: what the last manual change did (next, timed, fixed) and until when.
                **self._applied(comfort),
                "waiting_for_clock": comfort.get("waiting_for_clock") is True,
                "setpoint_source": room.get("setpoint_source"),
                "away": away.get("on") is True, "away_source": away.get("source"),
                "away_until": _iso(away.get("until")),
                # Why this room is cooler (room_persons: only its own persons are out; everyone; house_mode:
                # Away or Holiday), what its own persons are (home/away) and its own away temperature
                # (None: the house value, plan.room_away.v1).
                "away_reason": away_reason(comfort, away), "room_persons": comfort.get("persons"),
                "own_away_temperature": own / 100 if own is not None else None,
                # E32 1.3: in Smart warm-up's lead the target is already the coming one: the moment it warms up
                # for and the program's target then (None outside a lead; setpoint_source "warmup").
                **self._warming_up(room),
                # E32 1.4: the coming reset time (ISO) and what the room then gets: a temperature (°C) or a state
                # (active, follow, inactive); None without one or on older firmware.
                **self._next_reset(room),
                "smart_warm_up": self._smart_warm_up(),
                # 1.4.4 (#17): where Comfort, Eco and Night come from (room, program, house); the room card says
                # "Comfort, Eco and Night use the room defaults" for "house".
                "levels_from": levels_from(self.plan_room),
                # The room's setting device: which one, what was written and taken, the last failure.
                **setting_device_attributes(self.hass, self.entry, self.room_id, self.plan_room)}

    def _applied(self, comfort):
        """{"applied", "until"}: the running change as the E32 reports it ("next" or "timed" with its end); else, for a
        minute after a manual change from here, the E32's answer (until the telemetry reports it), and "fixed" while
        the room without a week program keeps the temperature that change gave it. None otherwise."""
        override, until = comfort.get("override"), _iso(comfort.get("until"))
        if override in ("next", "timed"):
            return {"applied": override, "until": until}
        answer = self._answer
        if answer is None or override == "boost":
            return {"applied": None, "until": until}
        fresh = time.monotonic() - answer["at"] < PENDING_SECONDS
        if answer["applied"] in ("next", "timed") and fresh:
            return {"applied": answer["applied"], "until": until or _iso(answer.get("until"))}
        plan = self.plan_room
        if (answer["applied"] == "fixed" and not has_program(plan)
                and (fresh or (plan or {}).get("fallback_centi_c") == int(round(answer["temperature"] * 100)))):
            return {"applied": "fixed", "until": None}
        return {"applied": None, "until": until}

    @staticmethod
    def _next_reset(room):
        reset = room.get("next_reset")
        at = _iso(reset.get("utc")) if type(reset) is dict else None
        if at is None:
            return {"next_reset": None, "next_reset_value": None}
        from .room_plan import ROOM_STATES
        value = reset.get("state") if reset.get("state") in ROOM_STATES else number(reset.get("temperature_c"), 5, 35)
        return {"next_reset": at, "next_reset_value": value}

    def _warming_up(self, room):
        from homeassistant.util import dt as dt_util

        from .room_overview import e32_zone, warmup_rise
        zone = e32_zone(self.hass, self.entry) if self.hass is not None else dt_util.get_default_time_zone()
        rise = warmup_rise(room, datetime.now(timezone.utc), zone) if room.get("setpoint_source") == "warmup" else None
        return {"warming_up_for": rise.isoformat() if rise else None,
                "scheduled_target": number(room.get("warmup_target_c"), 5, 35) if rise else None}

    def _smart_warm_up(self):
        """What Smart warm-up does for the next program step (E32 rc.3) and how the last step up turned out
        (E32 rc.4: "Yesterday warm at 09:12 (12 min late); next time it starts a little earlier.", or "about 10 min
        earlier" where the E32's numbers tell it, E32 SL-A), in the Home Assistant language, or None. E32 1.4 (#8):
        as this room has it (its own choice or the house switch); off for this room only, the sentence says so."""
        if self.hass is None or (self.room or {}).get("state") == "follow":  # E32 1.3: Heat along only has none
            return None
        from .e32_flow import smart_warm_up
        from .learned_overview import (HELD_MODES, arrival_line, free_heat_later, language, local_clock, local_day,
                                       room_smart_warm_up, slow_correction, smart_warm_up_line, trial_run)
        plan = self.hub.warmup.get(self.room_id) if type(getattr(self.hub, "warmup", None)) is dict else None
        plan = plan if type(plan) is dict else {}
        lang, clock = language(self.hass), local_clock(self.hass)
        # As the learned overview (rc7): nothing while away or a window holds the program, "would" in the trial run,
        # the later start the free heat gives.
        comfort = (self.hub.rooms.get(self.room_id) or {}).get("comfort")
        comfort = comfort if type(comfort) is dict else {}
        held = comfort.get("mode") in HELD_MODES or comfort.get("window") == "open"
        trial = trial_run(self.hub.status)
        later = free_heat_later((getattr(self.hub, "learned", None) or {}).get(self.room_id), plan)
        on, room_off = room_smart_warm_up(self.room, smart_warm_up(self.hass, self.entry.entry_id))
        line = None if held else smart_warm_up_line(plan.get("optimum_start"), on, lang, clock, trial, later,
                                                    room_off=room_off)
        arrived = arrival_line(plan.get("arrival"), lang, clock, *local_day(self.hass), plan.get("optimum_start"),
                               slow_correction(getattr(self.hub, "firmware_version", None)))  # 1.4.6: the E32's rule
        return " ".join(item[0] for item in (line, arrived) if item) or None

    # -- commands ----------------------------------------------------------------
    def _write_state(self):
        if self.hass is not None and self.entity_id:
            self.async_write_ha_state()

    @asynccontextmanager
    async def _target_pending(self, temperature):
        """The new target is shown at once and never silently dropped: a failed write
        shows the E32's own target again (and raises); a newer target replaces it."""
        mine = self._pending = (temperature, None)
        self._write_state()
        try:
            yield
        except BaseException:
            if self._pending is mine:
                self._pending = None
                self._write_state()
            raise
        if self._pending is mine:
            self._pending = (temperature, time.monotonic())

    async def _command(self, command, house=None):
        if self.link is None:
            from .room_plan import link_error
            raise link_error("no_controller_connection")
        if house is not None:  # the house mode, with the house changes still on their way (e32_house)
            from .e32_house import async_house_change, house_away
            answer = await async_house_change(self.link, house_away(self.hub), **house)
        else:
            answer = await async_comfort_command(self.link, command)
        if self.hass is not None and self.entity_id:
            self.async_write_ha_state()
        return answer

    async def _change_plan(self, change, key=None):
        await self.link.async_change_room(self.room_id, change, key)

    def _inactive(self):
        return (self.room or {}).get("state") == "inactive" or (self.plan_room or {}).get("state") == "inactive"

    def _off(self):
        """Off as a choice of the room's state: the E32 reports it Off, or our plan write (newer than the report)
        switched it off; not an "Off until" that has passed while the E32 already runs the room again (E32 1.4.1)."""
        return self._inactive() and not off_until_ended(self.plan_room, self.room)

    def _one_sign_in(self, needed):
        """R4-27, HC-09: the requests of one action share one E32 sign-in (RoomPlanLink.async_session) when it makes
        more than one; a single request signs in as before (a newer one for the same room still supersedes it)."""
        session = getattr(self.link, "async_session", None) if needed else None
        return session() if session is not None else nullcontext()

    def _heal_needed(self):
        """E32 1.4.1: a passed "Off until" still in the plan (async_heal_off_until writes it first)."""
        return not manual_supported(self.link) and off_until_ended(self.plan_room, self.room)

    async def _manual(self, temperature):
        """One manual change (async_manual_change); remembers the E32's answer for the attributes."""
        answer = await async_manual_change(self.link, self.room_id, temperature,
                                           running=self.comfort.get("override"), status_room=self.room)
        if answer is not None:
            self._answer = {**answer, "at": time.monotonic()}
        if self.hass is not None and self.entity_id:
            self.async_write_ha_state()
        return answer

    async def async_set_temperature(self, **kwargs):
        """1.4.2: a temperature never changes the room's state. A mode sent with it (cards send "heat" while
        dragging) is ignored, except Off."""
        self._refuse_in_summer()
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        if kwargs.get("hvac_mode") == HVACMode.OFF:
            return await self.async_set_hvac_mode(HVACMode.OFF)
        value = half_up(temperature)
        async with self._target_pending(value):
            await self._manual(value)

    async def async_set_hvac_mode(self, hvac_mode):
        from .room_plan import on_state, set_state
        self._refuse_in_summer()
        running = self.comfort.get("override") in OVERRIDES
        if hvac_mode == HVACMode.OFF:
            await self._change_plan(set_state("inactive"))
        elif hvac_mode == HVACMode.AUTO:
            # Back to the week program; from Off to the state it had (On, or Heat along only, 1.3).
            off, heal = self._off(), self._heal_needed()
            async with self._one_sign_in((off or heal) and running):
                if off:
                    await self._change_plan(set_state(on_state(self.plan_room)))
                elif heal:
                    await async_heal_off_until(self.link, self.room_id, self.room)
                if running:
                    await self._command(override_command(self.room_id, "none"))
        elif hvac_mode == HVACMode.HEAT:
            # Off: back to the state it had, no temperature. Otherwise the target it has now as a manual change, when
            # nothing holds the room; Heat along only stays Heat along only (1.4.2).
            if self._off():
                await self._change_plan(set_state(on_state(self.plan_room)))
                return
            target = self.target_temperature
            if not running and target is not None:
                async with self._target_pending(half_up(target)):
                    await self._manual(target)
        else:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="room_state_invalid")

    async def async_turn_on(self):
        await self.async_set_hvac_mode(HVACMode.AUTO)

    async def async_turn_off(self):
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_preset_mode(self, preset_mode):
        from .room_plan import set_state
        self._refuse_in_summer()
        if preset_mode == PRESET_HEAT_ALONG and preset_mode in self.preset_modes:
            # The same plan write as the room's Heating select (also from Off); its target stays as it is.
            await self._change_plan(set_state("follow"))
        elif preset_mode == PRESET_BOOST:
            # The room's maximum for an hour; the state stays (on Heat along only: valves open, no heat request).
            # The E32 refuses it on a room that is Off.
            heal = self._heal_needed()
            async with self._one_sign_in(heal):
                if heal:
                    await async_heal_off_until(self.link, self.room_id, self.room)
                await self._command(override_command(self.room_id, "boost"))
        elif preset_mode in LEVEL_PRESETS:
            # The level of the room's week planner as a manual change, like a temperature.
            level = program_levels(self.plan_room, comfort_options(self.entry))[LEVEL_PRESETS[preset_mode]]
            async with self._target_pending(half_up(level)):
                await self._manual(level)
        elif preset_mode == PRESET_NONE:
            # Back to the week program; the house mode (away, holiday) is its own select (e32_house.py). From Heat
            # along only: On (1.4, V7: the thermostat's one way back to On); a room that is off stays off.
            running, follow = self.comfort.get("override") in OVERRIDES, self._state() == "follow"
            async with self._one_sign_in(running and follow):
                if running:
                    await self._command(override_command(self.room_id, "none"))
                if follow:
                    await self._change_plan(set_state("active"))
        else:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="room_state_invalid")

    # -- actions (services.yaml) --------------------------------------------------
    async def async_set_room_override(self, mode, temperature=None, duration_minutes=None):
        """The action "Temporary temperature for a room": only the room's target changes, never its state (1.4.2: the
        E32 refuses it on a room that is Off). until_next needs a week program; timed without a duration: 120 min."""
        self._refuse_in_summer()
        if mode not in ("boost", "timed", "until_next"):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="room_state_invalid")
        if mode != "boost":
            if temperature is None:
                temperature = self.target_temperature
            if temperature is None or not self.min_temp <= float(temperature) <= self.max_temp:
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="room_setpoint_outside_limits",
                    translation_placeholders={"minimum": f"{self.min_temp:g}", "maximum": f"{self.max_temp:g}"})
            if mode == "until_next" and not has_program(self.plan_room):
                raise ServiceValidationError(translation_domain=DOMAIN, translation_key="comfort_no_schedule")
        if mode == "boost":
            command = override_command(self.room_id, "boost", None, duration_minutes)
        elif mode == "until_next":
            command = override_command(self.room_id, "next", temperature)
        else:
            command = override_command(self.room_id, "timed", temperature, duration_minutes or MANUAL_MINUTES)
        heal = self._heal_needed()
        async with self._one_sign_in(heal):
            if heal:
                await async_heal_off_until(self.link, self.room_id, self.room)
            return await self._command(command)

    async def async_clear_room_override(self):
        await self._command(override_command(self.room_id, "none"))

    # set_away / clear_away stay for existing automations (beta.23). They set the HOUSE mode, exactly as
    # the House mode select does: Away (or Holiday with an end date), and Auto again; never one room. In summer
    # (1.4.1) set_away is refused and clear_away does nothing (nothing is away): only switching summer off ends it,
    # and a presence automation logs no error every day.
    async def async_set_away(self, temperature=None, until=None):
        from .e32_house import holiday_until
        self._refuse_in_summer()
        end = holiday_until(until) if until is not None else None
        await self._command(None, {"mode": "holiday" if end else "away", "until": end, "temperature": temperature})

    async def async_clear_away(self):
        if self._summer():
            return  # summer: nothing to clear, nothing sent
        await self._command(None, {"mode": "auto"})


def register_services(platform):
    """The entity actions of the E32 room thermostats (see services.yaml)."""
    import voluptuous as vol
    platform.async_register_entity_service("set_room_override", {
        vol.Required("mode"): vol.In(["boost", "timed", "until_next"]),
        vol.Optional("temperature"): vol.All(vol.Coerce(float), vol.Range(min=5, max=30)),
        vol.Optional("duration_minutes"): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
    }, "async_set_room_override")
    platform.async_register_entity_service("clear_room_override", {}, "async_clear_room_override")
    from homeassistant.helpers import config_validation as cv
    platform.async_register_entity_service("set_away", {
        vol.Optional("temperature"): vol.All(vol.Coerce(float), vol.Range(min=AWAY_LIMITS[0], max=AWAY_LIMITS[1])),
        vol.Optional("until"): cv.datetime,
    }, "async_set_away")
    platform.async_register_entity_service("clear_away", {}, "async_clear_away")


def _wanted(hub, entry):
    # 1.4.2 (HC-03): also the rooms known while the E32 is offline (heating_link.HeatingHub.known_rooms).
    for room_id, room in hub.known_rooms.items():
        yield room_id, lambda room=room: E32RoomClimate(hub, room, entry)


async def async_setup_e32_climates(hass, entry, async_add_entities):
    """Product entries with a stored E32 connection: a thermostat per room and the forwarder."""
    from .product import is_product
    if not is_product(entry):
        return
    drop_retired_options(hass, entry)  # 1.4.2: the length of a manual change is gone (once, without a reload)
    hub = heating_hub(hass, entry)
    if hub.plan is None:
        return  # no stored controller connection: nothing can be written
    entry.async_on_unload(track_entities(hub, async_add_entities, add_options(hass, entry),
                                         lambda hub: _wanted(hub, entry)))
    state = hass.data[DOMAIN][entry.entry_id]
    # The E32 program on each room's setting device; its knob as an override (e32_setting_device.py).
    from .e32_setting_device import SettingDevicePusher
    pusher = state["setting_device_pusher"] = SettingDevicePusher(hass, entry, hub)
    entry.async_on_unload(pusher.start())
    # The entry's one route to the E32's ha/heating_input, shared with the room and energy values: the topic
    # where the E32 reports, a broker failure logged once, never a stuck or leaked send (P22).
    from .heating_link import heating_input_link
    link = heating_input_link(hass, entry, hub)

    if PRESENCE_MEMORY not in hass.data:
        from homeassistant.helpers.storage import Store
        memory = hass.data[PRESENCE_MEMORY] = PresenceMemory(hass, Store(hass, 1, f"{DOMAIN}.presence"))
        await memory.async_load()
    # Not watched: E32 rc.4 does not count contacts and presence in ha.input_age_s (HeatingInputWatch).
    forwarder = state["comfort_forwarder"] = ComfortForwarder(hass, entry, hub, partial(link.send, watched=False))
    entry.async_on_unload(hub.add_listener(forwarder.hub_changed))
    entry.async_on_unload(async_track_time_interval(hass, forwarder.refresh, REFRESH))
    forwarder.reconfigure()
    entry.async_on_unload(forwarder.stop)


# -- options flow (Configure -> Comfort) ---------------------------------------------


class ComfortOptionsSteps:
    """Mixin for the product options flow: the house (presence) and comfort settings, window/door sensors per room."""

    async def async_step_house(self, user_input=None):
        """Configure → House: presence and the away temperature, the house mode and holiday, and the comfort defaults.

        Heating and boiler, energy and the E32 connection have their own place in the main menu; the window contacts
        are set per room in Configure → Rooms.
        """
        from .e32_house import house_mode
        house = self._presence_house()
        options = ["house_presence"]
        if house is not None:
            options.append("house_mode")
            if house_mode(house.away) == "holiday":
                options.append("house_holiday_stop")
        options.append("comfort_settings")
        return self.async_show_menu(step_id="house", menu_options=options)

    def _presence_house(self):
        """The house state of the away temperature (e32_house.HouseState), or None without an E32 that reports it."""
        state = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        hub = state.get("heating_hub") if type(state) is dict else None
        if hub is None or getattr(hub, "plan", None) is None:
            return None
        from .e32_house import house_state
        house = house_state(self.hass, self.config_entry, hub)
        return house if house.away is not None else None

    async def async_step_house_presence(self, user_input=None):
        """The people of the house, how long everyone must be away and the away temperature.

        The away temperature is the E32's own setting (the number "Temperature when nobody is
        home" and the E32's Home page): it is sent with the same house command as that number
        (e32_house.HouseState.async_command), so all three show the same value. The house
        mode itself is a select.
        """
        import voluptuous as vol
        current = comfort_options(self.config_entry)
        house = self._presence_house()
        away = number(house.away.get("target_c"), *AWAY_LIMITS) if house is not None else None
        errors, placeholders = {}, {"error": ""}
        if user_input is not None:
            try:
                # 1.3 (plan item 1b): against the away temperature the form showed, so an E32 edit meanwhile stays.
                # Shared with the settings panel (settings_house.py).
                await async_save_presence(self.hass, self.config_entry, house, user_input,
                                          shown_value(self, "house_presence", away))
            except ComfortError as err:
                errors[err.field] = err.code
                if hasattr(err, "error"):
                    placeholders["error"] = err.error
            else:
                return self.async_abort(reason="presence_saved")
        if user_input is None:
            remember_shown(self, "house_presence", away)
        schema = presence_schema(vol, current, away if house is not None else False)
        if user_input is not None and errors:  # shown again: what was just entered
            schema = self.add_suggested_values_to_schema(schema, user_input)
        return self.async_show_form(step_id="house_presence", data_schema=schema, errors=errors,
                                    description_placeholders=placeholders)

    async def async_step_comfort_settings(self, user_input=None):
        import voluptuous as vol
        current = comfort_options(self.config_entry)
        errors = {}
        if user_input is not None:
            try:
                save_room_defaults(self.hass, self.config_entry, user_input)  # shared with the settings panel
            except ComfortError as err:
                errors[err.field] = err.code
            else:
                return self.async_abort(reason="comfort_saved")
        return self.async_show_form(step_id="comfort_settings", data_schema=settings_schema(vol, current), errors=errors)

    def _comfort_rooms(self):
        hub = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id, {}).get("heating_hub")
        rooms = hub.rooms if hub is not None else {}
        return [(room_id, room.get("name") or room_id) for room_id, room in sorted(rooms.items())]

    def _comfort_contact_summary(self, rooms, settings):
        """Per room the names of its window/door sensors (or "none"), one line each."""
        def name(entity_id):
            state = self.hass.states.get(entity_id)
            return (state.attributes.get("friendly_name") if state is not None else None) or entity_id
        none = "geen" if self.hass.config.language == "nl" else "none"
        return "\n".join(f"- {room}: {', '.join(name(e) for e in settings['contacts'].get(rid, [])) or none}"
                         for rid, room in rooms)

    async def async_step_comfort_contacts(self, user_input=None):
        """Pick the room first, so the sensor list below always belongs to the room it shows."""
        import voluptuous as vol
        rooms = self._comfort_rooms()
        if not rooms:
            return self.async_abort(reason="comfort_no_rooms")
        current = comfort_options(self.config_entry)
        errors = {}
        if user_input is not None:
            if user_input.get("room") in dict(rooms):
                self._comfort_room = user_input["room"]
                return await self.async_step_comfort_contacts_room()
            errors["room"] = "room_invalid"
        return self.async_show_form(
            step_id="comfort_contacts", errors=errors,
            data_schema=contacts_room_schema(vol, rooms, (user_input or {}).get("room")),
            description_placeholders={"rooms": self._comfort_contact_summary(rooms, current)})

    async def async_step_comfort_contacts_room(self, user_input=None):
        import voluptuous as vol
        rooms = dict(self._comfort_rooms())
        room_id = getattr(self, "_comfort_room", None)
        if room_id not in rooms:
            return self.async_abort(reason="comfort_no_rooms")
        current = comfort_options(self.config_entry)
        windows, doors = windows_of(current, room_id), doors_of(current, room_id)
        errors = {}
        if user_input is not None:
            try:  # shared with the settings panel (settings_house.py)
                save_room_contacts(self.hass, self.config_entry, room_id, user_input.get("contacts"),
                                   user_input.get("door_contacts"))
            except ComfortError as err:
                errors[err.field] = err.code
            else:
                return self.async_abort(reason="comfort_saved")
        if errors:
            windows, doors = (user_input or {}).get("contacts", windows), (user_input or {}).get("door_contacts", doors)
        return self.async_show_form(
            step_id="comfort_contacts_room", errors=errors, data_schema=contacts_schema(vol, windows, doors),
            description_placeholders={"room": rooms[room_id], "delay": contact_delay_text(current),
                                      "door_delay": contact_delay_text(current, door=True)})
