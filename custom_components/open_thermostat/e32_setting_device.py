"""Every E32 room runs on the E32; an optional setting device sets it, both ways (1.4.2).

Owner, 30 Oct 2026: "per ruimte een weekplanner ... los daarvan kun je de
temperatuur instellen / overrulen met een thermostaatfunctie: een trv, een tado
thermostaat, alleen een virtuele thermostaat, of een losse sensor waarmee je de
temperatuur kunt instellen", and yes: push the program target to the knob.
Owner, 10 Nov 2026: "een temperatuur verandert nooit de stand", the setting
device works both ways also without a week program, and "die TRV's gaan juist
open en dicht met het instellen van de temperatuur": one role per valve.

- The week program lives on the E32 and runs without Home Assistant. A new
  room starts from "Workdays and weekend" (comfort 20 °C, away 18 °C, night
  16 °C, the week planner's defaults) in the room editor; a room without a
  program keeps its temperature without a week program (1.4, issue #7: a
  deliberate choice, so no Repairs item asks to give it one any more).
- The room's **setting device** is its plan ``setpoint_entity``: a climate
  entity (a radiator valve such as a TV02, a tado, any thermostat) or a
  number / input_number with a target. Without one, our room thermostat and
  the E32 page are the virtual thermostat.
- **To the device**: Home Assistant keeps it at the room's temperature, with or
  without a week program, while the room is On or on Heat along only and not
  paused for an open window: the E32's effective target (``setpoint``) whenever
  ``setpoint_source`` is the program ("schedule", Smart warm-up's "warmup"), a
  reset time ("reset") or summer mode ("summer", the frost limit); without a
  program also the temperature without a week program ("fallback"), with an
  away or holiday ceiling and a reset temperature on top. A room with a program
  but without the clock gets nothing: its "fallback" is not the program's
  target. Rounded to the device's step, at most once a minute per room.
- **Home Assistant no longer sends the device's target to the E32**
  (heating_link.target_kept): the target is the room's, written to the device,
  so a ceiling or a reset temperature on the device never becomes the room's
  base. E32 1.4.1 keeps a target it had for up to 15 minutes (source "ha");
  meanwhile a room without a program gets its temperature without a week
  program on the device.
- **From the device**: a target we did not write (somebody turned the knob or
  used the device's app) is a manual change, taken ~5 s after the last step
  (KNOB_SETTLE_S: one change for a knob turned through ten values), on a half
  degree rounded half up. With ``room.manual.v1`` (E32 1.4.2) one command
  ``override: "manual"``: the firmware makes it "until the next switch time"
  with a program and the new temperature without a week program without one.
  Older firmware (or one that answers ``invalid_override``) gets the same
  split from Home Assistant: ``next`` (``timed`` 120 minutes without the
  clock), or the plan's ``fallback_centi_c`` written as a routine write. The
  room's state never changes. A room that is Off: with a program the turn is
  ignored, without one its temperature without a week program is set and the
  room stays Off. In summer mode the frost limit goes back on the device.
- **Echo**: a device value within half its step of the room's current target,
  of the frost limit (8 °C) or of the value we wrote last (also any value in
  the 10 s after a write) is never a manual change. Strictly within: a turn of
  one step on a 1 °C device from 20.5 °C is a change (review HC-13).
- **A stale report** (1.4.6, review B5): cloud-polled devices such as a tado
  report their old target once more after a write (12 Nov 2026: 19 °C again two
  minutes after our 20.5 °C, which ended the morning's warm-up as a "manual
  change"). Per room Home Assistant remembers the device's target as it was
  just before our write (read from its state at the write). That value, within
  half the device's step, within STALE_SECONDS (10 minutes) after the write, is
  no manual change and no pending knob: the room's target is written again
  (after MIN_INTERVAL) and the link records it (``setting_device_stale``, with
  its time). The person at the knob still wins: the same old value a second
  time in that window is a manual change, and any other value is one at once.
  A device that keeps changing by itself is the own-schedule safety net's
  business below; a stale report is not counted for it (no one turned or
  scheduled it) and does not hide it.
- **One role per valve** (valve_routes.two_roles): a device is a room's setting
  device or a radiator valve the E32 drives, not both. The room form and the
  settings panel refuse the combination (``device_two_roles``); an installation
  that had it gets valve control of that room switched off once at the update
  (option ``valve_two_roles_v1``), a log line and the Repairs item
  ``valve_two_roles`` until the room is saved.
- **Its own schedule**: a climate device that reports its own schedule
  (``hvac_mode`` auto, or a preset such as "schedule") is set to manual once
  when it becomes a room's setting device, never from "off". As a safety net
  the same happens when it goes back to its schedule or keeps changing by
  itself at the same quarter on three days within eight, at most once an hour
  and three times in all; the pattern also raises ``device_own_schedule``.
- The room thermostat shows the link (``setting_device_attributes``): the
  device, the last target written and the last knob value taken (each with its
  time), when it was set to manual, and the last failure in plain words. Three
  failed writes in a row raise a Repairs item; the next write that works (or
  the device showing the room's target) clears it.
- Without Home Assistant the E32 keeps running; knob changes are not seen
  then. When it comes back the current target is written again. A device that
  comes back itself (unavailable, or loaded after this integration) is not a
  knob turn: the room's target is written to it. While it is unavailable
  nothing is written (Home Assistant would skip it anyway).

Nothing here writes to the boiler; the frost floor, flow limits and the guard
are the E32's and unchanged.
"""
from __future__ import annotations

from contextlib import nullcontext
import logging
import math
import time

from homeassistant.const import UnitOfTemperature
from homeassistant.core import CoreState, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util import dt as dt_util

from .issue_sync import remove_retired_issues
from .const import DOMAIN
from .heating_link import celsius, number

_LOGGER = logging.getLogger(__name__)

DEVICE_DOMAINS = ("climate", "number", "input_number")
MIN_INTERVAL = 60       # s between two writes to one device
ECHO_SECONDS = 10       # our own write settles
STALE_SECONDS = 600     # a cloud device may report its value from before our write once more within this long
PENDING_SECONDS = 60    # a knob change waits this long for the E32 to report it as its target
KNOB_SETTLE_S = 5       # a knob turned through several values: one manual change this long after the last step
NO_CLOCK_MINUTES = 120  # a manual change with a program but without the clock (the firmware's own fixed value)
FROST_C = 8.0           # the frost limit the E32 writes to the valves it drives (pause, Off, summer)
MANUAL_FEATURE = "room.manual.v1"  # E32 1.4.2: the command override "manual" (CONTRACT-1.4.2 §1)
TARGET_TEMPERATURE, TARGET_TEMPERATURE_RANGE = 1, 2  # ClimateEntityFeature bits (no import of the enum needed)
SCHEDULE_DAYS = 3       # unasked changes at the same quarter on this many days: its own schedule
SCHEDULE_WINDOW_DAYS = 8
# Raised (as a safety net, 1.4.2) when a setting device keeps changing its target by itself at the same quarter on
# SCHEDULE_DAYS days: it runs its own schedule, with or without a week program on the E32. Never from "off".
OWN_SCHEDULE_ISSUE = "device_own_schedule"
SCHEDULE_PRESETS = ("schedule", "auto", "program", "programme")  # a preset that means "its own schedule"
MANUAL_PRESETS = ("manual",)  # the preset that means "manual" on such a device
MANUAL_RETRY_S = 3600   # setting a device to manual again: at most once an hour ...
MANUAL_TRIES = 3        # ... and this often in all for one room's device (then the Repairs item says it)
WRITE_FAILED_ISSUE = "setting_device_write_failed"
FAILURES_FOR_REPAIR = 3  # failed writes in a row to one device before Repairs says so
GONE = ("unavailable", "unknown")  # a device state without a target: back from it is no knob turn
# One role per valve (1.4.2): a room whose valve control was switched off at the update because one of its valves was
# also a setting device. One item per room, removed when the room is saved (e32_room_flow.save_room) or goes.
TWO_ROLES_ISSUE = "valve_two_roles"
TWO_ROLES_DONE = "valve_two_roles_v1"  # entry option: the one-time check of the update ran
TWO_ROLES_RETRY_S = 600  # a check that could not read the valves tries again after this long (three times)

# The last failure in plain words (the room thermostat's setting_device_error and the Repairs item's {error}).
ERROR_TEXT = {
    "en": {"write": "Could not set {value}: {detail}",
           "missing": "{device} no longer exists in Home Assistant.",
           "unavailable": "{device} is unavailable; the target follows when it is back.",
           "knob": "Could not take over {value} from the device: {detail}"},
    "nl": {"write": "{value} instellen lukte niet: {detail}",
           "missing": "{device} bestaat niet meer in Home Assistant.",
           "unavailable": "{device} is niet beschikbaar; de gewenste temperatuur volgt zodra het terug is.",
           "knob": "{value} van het apparaat overnemen lukte niet: {detail}"},
}

# The week planner's "Workdays and weekend" (week-editor.js TEMPLATES.work, levels comfort/away/night).
COMFORT, AWAY, NIGHT = 2000, 1800, 1600
WORKDAY = [(390, COMFORT), (510, AWAY), (1020, COMFORT), (1350, NIGHT)]
WEEKEND = [(480, COMFORT), (1380, NIGHT)]


def default_program(low=500, high=3000):
    """The template as a plan "schedule" (7 days of [minute, centi_c]) within the room's limits."""
    clamp = lambda v: max(low, min(high, v))  # noqa: E731
    return [[[m, clamp(c)] for m, c in (WORKDAY if day < 5 else WEEKEND)] for day in range(7)]


def has_program(room):
    schedule = (room or {}).get("schedule")
    return (type(schedule) is list and any(day for day in schedule)) or bool((room or {}).get("week"))


def setting_device(room):
    entity_id = (room or {}).get("setpoint_entity")
    return entity_id if type(entity_id) is str and entity_id.split(".")[0] in DEVICE_DOMAINS else None


def proposed_device(room):
    """A climate source of the room (its valve or thermostat) as the setting device, when it has none."""
    if setting_device(room):
        return None
    for source in (room or {}).get("sources") or []:
        if source.get("type") == "ha" and str(source.get("id", "")).startswith("climate."):
            return source["id"]
    return None


def setting_hint(device, language):
    """The room form's hint for a climate source that could be the setting device ("" without one).

    Only a hint: the form never pre-selects it, the user picks it. One sentence that is true with and without a
    week program (1.4.2: the device works both ways in both cases)."""
    if not device:
        return ""
    if str(language or "").startswith("nl"):
        return (f"\n\n**Instelapparaat?** {device} gebruiken als instelapparaat van deze ruimte? Home Assistant "
                "houdt het op de temperatuur van de ruimte; eraan draaien verandert de ruimte (met een weekprogramma "
                "tot de volgende schakeltijd, zonder weekprogramma voorgoed). Kies het daarvoor zelf bij "
                "Instelapparaat.")
    return (f"\n\n**Setting device?** Use {device} as this room's setting device? Home Assistant keeps it at the "
            "room's temperature; turning it changes the room (until the next switch time with a week program, for "
            "good without one). To do so, choose it under Setting device.")


def half_up(value):
    """°C on a half degree, halves rounded up (20.25 → 20.5, 20.75 → 21.0), as the E32 pages round (review HC-12)."""
    return math.floor(float(value) * 2 + 0.5) / 2


def _unit(hass, state):
    if state.domain == "climate":
        return hass.config.units.temperature_unit
    return state.attributes.get("unit_of_measurement") or UnitOfTemperature.CELSIUS


def device_target(hass, state):
    """The device's target in °C, or None."""
    if state is None or state.state in ("unavailable", "unknown"):
        return None
    if state.domain == "climate":
        # A thermostat with only a temperature range (TARGET_TEMPERATURE_RANGE, such as the Bosch Room thermostat II
        # through Zigbee2MQTT) carries its heating setpoint in target_temp_low (issue #5).
        value = state.attributes.get("temperature")
        if value is None:
            value = state.attributes.get("target_temp_low")
    else:
        value = state.state
    return celsius(value, _unit(hass, state), 5, 35)


def device_step(state):
    """The device's step in °C (close enough for °F devices too)."""
    key = "target_temp_step" if state.domain == "climate" else "step"
    step = number(state.attributes.get(key), 0.01, 5)
    return step if step is not None else 0.5


def near(state, value, target):
    """True when ``value`` (°C, from the device) is strictly within half the device's step of ``target``.

    Strictly: a device with 1 °C steps that shows 21 for a room target of 20.5 was turned one step (review HC-13); a
    device with fine steps still gets 0.05 °C for the conversion of its own unit."""
    return target is not None and abs(value - target) < max(device_step(state) / 2, 0.05)


def device_value(hass, state, value_c):
    """What async_write sets for ``value_c``: in the device's unit, rounded to its step, within its limits."""
    unit, step = _unit(hass, state), device_step(state)
    value = value_c
    if unit not in (UnitOfTemperature.CELSIUS, None, ""):
        from homeassistant.util.unit_conversion import TemperatureConverter
        value = TemperatureConverter.convert(value_c, UnitOfTemperature.CELSIUS, unit)
    value = round(round(value / step) * step, 2)
    low, high = number(state.attributes.get("min_temp" if state.domain == "climate" else "min"), -100, 1000), \
        number(state.attributes.get("max_temp" if state.domain == "climate" else "max"), -100, 1000)
    if low is not None:
        value = max(value, low)
    if high is not None:
        value = min(value, high)
    return value


async def async_write(hass, state, value_c, context=None):
    """Set the device's target (its own service), rounded to its step and in its unit."""
    value = device_value(hass, state, value_c)
    if state.domain == "climate":
        features = number(state.attributes.get("supported_features"), 0, 2 ** 31) or 0
        if "temperature" in state.attributes or int(features) & TARGET_TEMPERATURE:
            data = {"entity_id": state.entity_id, "temperature": value}
        else:
            # Range only (issue #5): the heating setpoint, with the cooling setpoint kept (never below the new low).
            high = number(state.attributes.get("target_temp_high"), -100, 1000)
            data = {"entity_id": state.entity_id, "target_temp_low": value,
                    "target_temp_high": max(high, value) if high is not None else value}
        service = "set_temperature"
    else:
        service, data = "set_value", {"entity_id": state.entity_id, "value": value}
    await hass.services.async_call(state.domain, service, data, blocking=True, context=context)
    return value


# -- its own schedule, radiator valves and the hint (1.4.2) ------------------------------------------------------

def schedule_mode(state):
    """(service, data) that sets a climate device running its own schedule to manual, or None.

    Its own schedule: ``hvac_mode`` "auto" on a device that also offers "heat" (a tado's smart schedule, a Sonoff
    TRVZB through Zigbee2MQTT), or a preset such as "schedule" or "auto" on a device that offers "manual" (a Tuya
    TV02). Never a device that is "off" (the user's own choice), unavailable or not a climate entity.
    """
    if state is None or state.domain != "climate" or state.state in ("off", *GONE):
        return None
    modes = state.attributes.get("hvac_modes") or ()
    if state.state == "auto" and "heat" in modes:
        return "set_hvac_mode", {"entity_id": state.entity_id, "hvac_mode": "heat"}
    preset, presets = state.attributes.get("preset_mode"), state.attributes.get("preset_modes") or ()
    if type(preset) is str and preset.lower() in SCHEDULE_PRESETS:
        manual = next((p for p in presets if type(p) is str and p.lower() in MANUAL_PRESETS), None)
        if manual is not None:
            return "set_preset_mode", {"entity_id": state.entity_id, "preset_mode": manual}
    return None


async def async_set_manual(hass, state, context=None):
    """Set a climate device that runs its own schedule to manual (schedule_mode); the service used, or None.

    For a room's setting device (here) and a radiator valve when it is chosen (HA-DEVICES may call it)."""
    mode = schedule_mode(state)
    if mode is None:
        return None
    service, data = mode
    await hass.services.async_call("climate", service, data, blocking=True, context=context)
    return service


VALVE_WORDS = ("trv", "radiator", "valve")  # a climate device whose make or model says it is a radiator valve


def is_radiator_valve(hass, entity_id, valves=()):
    """True for a climate entity that is a radiator valve: one the E32 lists as a valve (``valves``: their entities),
    a model we know (e32_valves.guess_model) or a device whose make or model says so."""
    if type(entity_id) is not str or not entity_id.startswith("climate."):
        return False
    if entity_id in valves:
        return True
    from homeassistant.helpers import device_registry as dr, entity_registry as er
    from .e32_valves import guess_model
    found = er.async_get(hass).async_get(entity_id)
    device = dr.async_get(hass).async_get(found.device_id) if found is not None and found.device_id else None
    if device is None:
        return False
    text = " ".join(str(v or "") for v in (device.manufacturer, device.model, getattr(device, "model_id", None)))
    return guess_model(text) is not None or any(word in text.lower() for word in VALVE_WORDS)


def setting_device_hint(hass, state, setpoint_entity, valves=()):
    """The room screen's hint key (CONTRACT-1.4.2 §2 ``setting_device_hint``): "valve_on_active" when a radiator
    valve's climate entity is the setting device of a room that is On, else None.

    On On such a valve regulates on its own sensor and often closes before the room is warm; the panel suggests
    valve control with a separate thermometer. ``state``: the room's state ("active", "follow", "inactive") as the
    screen shows it; ``valves``: the climate entities of the radiator valves the E32 lists (any room)."""
    if state != "active" or not is_radiator_valve(hass, setpoint_entity, valves):
        return None
    return "valve_on_active"


# -- the room's manual change (1.4.2) ----------------------------------------------------------------------------

def routine(change):
    """A plan change(plan) sent with the routine flag (CONTRACT-1.4.2 §1, top-level ``"routine": true``): E32 1.4.2
    then keeps the self-tuning's day and every room's warm-up and learning; E32 1.4.1 ignores the flag."""
    def plan_change(plan):
        changed = change(plan)
        changed["routine"] = True
        return changed
    return plan_change


async def async_routine_room_change(link, room_id, change, key=None):
    """One room's plan field written with the routine flag (RoomPlanLink.async_change_room, routine)."""
    from .room_plan import changed_plan, plan_room
    return await link.async_change_plan(routine(lambda plan: changed_plan(plan, room_id, change)),
                                        lambda stored: plan_room(stored, room_id) is not None, key)


def manual_unknown(err):
    """True when the E32 does not know the command "manual" (E32 1.4.1 answers ``invalid_override``)."""
    placeholders = getattr(err, "translation_placeholders", None) or {}
    return placeholders.get("error") == "invalid_override" or "invalid_override" in str(
        getattr(err, "translation_key", None) or "")


def off_until_over(plan_room, status_room, now_utc):
    """True when the room's "Off until" ended while the plan still says Off (E32 1.4.1 writes no plan then and refuses
    a manual change with ``room_inactive``): the status already reports the room on."""
    until = (plan_room or {}).get("inactive_until")
    return ((plan_room or {}).get("state") == "inactive" and type(until) is int and 0 < until <= now_utc
            and (status_room or {}).get("state") in ("active", "follow"))


def _session(link):
    session = getattr(link, "async_session", None)
    return session() if session is not None else nullcontext()


def _language(hass):
    value = (getattr(getattr(hass, "config", None), "language", None) or "en").lower().replace("_", "-").split("-")[0]
    return value if value in ERROR_TEXT else "en"


def _degrees(value, lang):
    """20.5 °C (a decimal comma in Dutch)."""
    text = f"{round(float(value), 1):.1f}".rstrip("0").rstrip(".")
    return (text.replace(".", ",") if lang != "en" else text) + " °C"


def _detail(err):
    """An error in words: its message, else its kind."""
    return str(err).strip() or type(err).__name__


def error_text(error, lang):
    """A recorded failure (kind, device, °C or None, detail) as one plain sentence in ``lang``."""
    if error is None:
        return None
    kind, device, value, detail = error
    text = ERROR_TEXT.get(lang, ERROR_TEXT["en"]).get(kind) or ERROR_TEXT["en"][kind]
    return text.format(device=device, value=_degrees(value, lang) if value is not None else "", detail=detail)


def _reports_own_schedule(hass, device):
    """True while the setting device reports its own schedule now (schedule_mode); False otherwise, also without hass."""
    state = hass.states.get(device) if hass is not None else None
    return schedule_mode(state) is not None


def _new_link(device):
    return {"device": device, "written": None, "written_at": None, "knob": None, "knob_at": None,
            "error": None, "failures": 0, "checked": None, "stale": None, "stale_at": None,
            "manual_at": None, "manual_tries": 0, "manual_clock": None, "manual_checked": False}


def setting_device_attributes(hass, entry, room_id, plan_room):
    """The room thermostat's diagnostic attributes for its setting device; {} without one.

    ``setting_device`` (entity ID), ``setting_device_written`` (the last target written, °C) and
    ``setting_device_written_at``, ``setting_device_knob`` (the last knob value taken as a manual change, °C) and
    ``setting_device_knob_at``, ``setting_device_stale`` (the last stale report the device made after a write, °C, which
    was not taken as a manual change) and ``setting_device_stale_at``, ``setting_device_set_to_manual`` (when Home Assistant last set it from its own
    schedule to manual; ISO times: the dashboard shows them in the user's locale), ``setting_device_own_schedule``
    (1.4.6: True while the device reports its own schedule right now) and ``setting_device_error``: the
    last failure in plain words, None once a write works again. Kept in memory: after a restart the values come back
    with the next write or knob change.
    """
    device = setting_device(plan_room)
    if device is None:
        return {}
    state = ((hass.data.get(DOMAIN) or {}).get(entry.entry_id) or {}) if hass is not None else {}
    pusher = state.get("setting_device_pusher") if type(state) is dict else None
    link = pusher.links.get(room_id) if pusher is not None else None
    if link is None or link["device"] != device:
        link = _new_link(device)
    return {"setting_device": device,
            "setting_device_written": link["written"], "setting_device_written_at": link["written_at"],
            "setting_device_knob": link["knob"], "setting_device_knob_at": link["knob_at"],
            "setting_device_stale": link.get("stale"), "setting_device_stale_at": link.get("stale_at"),
            "setting_device_set_to_manual": link.get("manual_at"),
            # 1.4.6 (HA-OWN-PROGRAM, issue #15): the device reports its own program right now (hvac_mode auto or a
            # schedule preset); live from its state, so it is said at once and goes when the device is manual again.
            "setting_device_own_schedule": _reports_own_schedule(hass, device),
            "setting_device_error": error_text(link["error"], _language(hass))}


def _written_celsius(hass, state, value):
    """A written value (in the device's unit) back in °C, to a tenth."""
    value_c = celsius(value, _unit(hass, state), -100, 1000)
    return round(value_c, 1) if value_c is not None else None


# -- one role per valve: the update's one-time check (1.4.2) --------------------------------------------------------

def two_roles_issue(entry, room_id):
    return f"{TWO_ROLES_ISSUE}_{entry.entry_id}_{room_id}"


@callback
def clear_two_roles_issue(hass, entry, room_id):
    """The room was saved (its setting device and valves chosen again): its ``valve_two_roles`` item goes."""
    ir.async_delete_issue(hass, DOMAIN, two_roles_issue(entry, room_id))


@callback
def _mark_two_roles_done(hass, entry):
    """Store the option that the one-time check ran, without a reload (the energy step's no-reload marker)."""
    from .energy_input import ENERGY_ONLY_UPDATE
    options = {**entry.options, TWO_ROLES_DONE: True}
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if state is not None:
        state[ENERGY_ONLY_UPDATE] = dict(options)
    if not hass.config_entries.async_update_entry(entry, options=options) and state is not None:
        state.pop(ENERGY_ONLY_UPDATE, None)  # no listener runs: never leave the marker behind


class SettingDevicePusher:
    """One per entry: keeps each setting device at its room's target and turns its knob into a manual change."""

    def __init__(self, hass, entry, hub, clock=time.monotonic, now=dt_util.now, call_later=async_call_later,
                 migrate=True):
        self.hass, self.entry, self.hub, self.clock, self.now = hass, entry, hub, clock, now
        self.call_later = call_later  # (hass, seconds, callback) -> cancel: the knob's settle time
        self.pushed = {}       # room id -> (entity, °C wanted, clock) of the last write
        self.wrote = {}        # room id -> what that write set on the device, in °C (the echo of it)
        # room id -> [entity, °C the device showed just before our write, clock of that write, stale reports seen]
        self.before = {}
        self.pending = {}      # room id -> (°C, clock until): a manual change on its way to the E32
        self.knobs = {}        # room id -> (entity, °C, cancel): a knob still being turned (KNOB_SETTLE_S)
        self.unasked = {}      # entity -> [(date, quarter)] of changes we did not write
        self.links = {}        # room id -> what the link did last (_new_link; setting_device_attributes shows it)
        self._tracked, self._unsubscribe, self._retry = (), None, None
        self._busy = set()
        # One role per valve, the update's one-time check: None to do, "running", "done" (or not wanted here).
        self._two_roles = None if migrate else "done"
        self._two_roles_tries, self._two_roles_at = 0, None

    # -- the rooms -------------------------------------------------------------------
    def rooms(self):
        """(room id, plan room, status room, device entity) for each room with a setting device, with or without a
        week program (1.4.2)."""
        link = self.hub.plan
        plan = link.plan if link is not None else None
        for room in (plan or {}).get("rooms", []):
            device = setting_device(room)
            if device:
                yield room["id"], room, self.hub.rooms.get(room["id"]), device

    def setting_devices(self):
        """The plan's setting devices, whose target Home Assistant keeps to itself (heating_link.target_kept); None
        while the plan is not read."""
        link = self.hub.plan
        if link is None or type(link.plan) is not dict:
            return None
        return frozenset(device for *_rest, device in self.rooms())

    @staticmethod
    def desired(status_room, plan_room=None):
        """The room's effective target to show on the device, or None (off, window pause, nothing to show).

        The E32 reports the target after its adjustments in ``setpoint``: the program's, a manual change's (next,
        timed, boost) or the away, holiday or return target, while ``setpoint_source`` names the base: "schedule"
        whenever it runs the program, "warmup" for Smart warm-up's lead (the program's coming target), "reset" for
        a reset time's temperature, "summer" for summer mode's frost limit (8 °C for a room that is on). Also on
        Heat along only ("follow": it keeps its target).

        1.4.2: a room without a week program (``plan_room`` says so) shows its temperature without a week program
        ("fallback", with an away ceiling on top), also on the device: Home Assistant no longer sends the device's
        target to the E32 (heating_link.target_kept), so nothing written here comes back as the room's base. E32
        1.4.1 keeps a target it had for up to 15 minutes ("ha"): meanwhile the plan's own temperature without a
        week program goes to the device. A room with a program but without the clock gets nothing: its "fallback" or
        "ha" is not the program's target, and an override or away written then would outlive its end.
        """
        if not status_room or status_room.get("state") not in ("active", "follow"):
            return None
        comfort = status_room.get("comfort") if type(status_room.get("comfort")) is dict else {}
        source = status_room.get("setpoint_source")
        if comfort.get("mode") == "window_open":
            return None
        if source in ("schedule", "warmup", "reset", "summer"):
            return number(status_room.get("setpoint"), 5, 35)
        if plan_room is None or has_program(plan_room):
            return None
        if source == "fallback":
            return number(status_room.get("setpoint"), 5, 35)
        fixed = plan_room.get("fallback_centi_c")
        return number(fixed / 100, 5, 35) if source == "ha" and type(fixed) is int else None

    @staticmethod
    def _current(status, room):
        """The room's target now (°C) to compare a device value with: the E32's ``setpoint``; for a room that is Off
        without a program (no setpoint) its temperature without a week program."""
        value = number((status or {}).get("setpoint"), 5, 35)
        fixed = (room or {}).get("fallback_centi_c")
        if value is None and (status or {}).get("state") == "inactive" and not has_program(room) and type(fixed) is int:
            value = fixed / 100
        return value

    def _link(self, room_id, device):
        """The room's link record; a new one (and no Repairs item of the old device) when the device changed."""
        link = self.links.get(room_id)
        if link is None or link["device"] != device:
            if link is not None:
                ir.async_delete_issue(self.hass, DOMAIN, self._failed_issue(room_id))
            link = self.links[room_id] = _new_link(device)
        return link

    # -- pushing ---------------------------------------------------------------------
    @callback
    def evaluate(self, _now=None):
        self._retry = None
        if not self.hub.fresh:
            return
        self._follow_devices()
        self._clear_own_schedule_issues()
        self._forget_gone_links()
        self._check_two_roles()
        wait = None
        for room_id, room, status, device in self.rooms():
            link = self._link(room_id, device)
            state = self.hass.states.get(device)
            if not link["manual_checked"] and state is not None and state.state not in GONE:
                link["manual_checked"] = True
                self._own_program(room_id, room, link, state)  # once, when it becomes the room's setting device
            want = self.desired(status, room)
            if want is None or room_id in self._busy or room_id in self.knobs:
                continue
            if state is None or state.state == "unavailable":
                self._not_there(room_id, room, link, device, state)
                continue
            pending = self.pending.get(room_id)
            if pending is not None:
                if abs(pending[0] - want) < 0.05 or self.clock() > pending[1]:
                    self.pending.pop(room_id, None)
                else:
                    continue  # the knob's value is on its way to the E32
            shown = device_target(self.hass, state)
            if shown is not None and abs(shown - want) <= device_step(state) / 2 + 0.01:
                self._succeeded(room_id, link)  # it shows the room's target: nothing to repair
                continue
            last = self.pushed.get(room_id)
            if last is not None and self.clock() - last[2] < MIN_INTERVAL:
                wait = min(wait or MIN_INTERVAL, MIN_INTERVAL - (self.clock() - last[2]))
                continue
            self._busy.add(room_id)
            self.hass.async_create_task(self._push(room_id, room, state, want), f"OpenThermostat setting device {device}")
        if wait is not None and self._retry is None:
            self._retry = async_call_later(self.hass, wait + 1, self.evaluate)

    async def _push(self, room_id, room, state, want):
        error = None
        # Known before the write: the device may report the new value before the service call returns.
        self.pushed[room_id] = (state.entity_id, want, self.clock())
        self._remember_before(room_id, state)
        self.wrote[room_id] = celsius(device_value(self.hass, state, want), _unit(self.hass, state), -100, 1000)
        try:
            value = await async_write(self.hass, state, want)
        except Exception as err:  # noqa: BLE001 - any refusal (also a schema error) is a failed write, never a storm
            _LOGGER.warning("Could not set %s to the target of E32 room %s: %s", state.entity_id, room_id, err)
            value, error = None, err
        finally:
            self._busy.discard(room_id)
        # Rate-limited also after a failure: never a write storm.
        self.pushed[room_id] = (state.entity_id, want, self.clock())
        if error is not None:
            self.wrote[room_id] = None
            self.before.pop(room_id, None)
        link = self.links.get(room_id)
        if link is None or link["device"] != state.entity_id:
            return  # the room changed its setting device meanwhile: this write tells nothing about the new one
        if error is not None:
            self._failed(room_id, room, link, state, ("write", self._name(state), want, _detail(error)))
            return
        _LOGGER.debug("E32 room %s: set %s to %s", room_id, state.entity_id, value)
        link["written"], link["written_at"] = _written_celsius(self.hass, state, value), self.now().isoformat()
        self._succeeded(room_id, link)

    def _remember_before(self, room_id, state):
        """The device's target just before this write (its state now), for the stale report. A rewrite after a stale
        report keeps the first record: the old value shown again after the second write is the person at the knob."""
        previous = device_target(self.hass, state)
        record = self.before.get(room_id)
        if (record is not None and record[0] == state.entity_id and record[3] and previous is not None
                and self.clock() - record[2] < STALE_SECONDS and near(state, previous, record[1])):
            return
        if previous is None:
            self.before.pop(room_id, None)
        else:
            self.before[room_id] = [state.entity_id, previous, self.clock(), 0]

    def _stale(self, room_id, state, value, link):
        """True (once per write) when ``value`` is the device's target from before our last write, reported late."""
        record = self.before.get(room_id)
        if (record is None or record[0] != state.entity_id or record[3] or self.clock() - record[2] >= STALE_SECONDS
                or not near(state, value, record[1])):
            return False
        record[3] += 1
        link["stale"], link["stale_at"] = round(value, 1), self.now().isoformat()
        self.evaluate()  # the room's target goes back on the device after MIN_INTERVAL
        return True

    # -- what the link did: attributes and the Repairs item ------------------------------------
    @staticmethod
    def _name(state):
        return state.name if state is not None else None

    def _failed_issue(self, room_id):
        return f"{WRITE_FAILED_ISSUE}_{self.entry.entry_id}_{room_id}"

    @callback
    def _succeeded(self, room_id, link):
        if link["failures"] or link["error"] is not None:
            link["failures"], link["error"] = 0, None
            ir.async_delete_issue(self.hass, DOMAIN, self._failed_issue(room_id))

    @callback
    def _failed(self, room_id, room, link, state, error, count=True):
        """One failure: shown on the room thermostat; FAILURES_FOR_REPAIR in a row raise the Repairs item."""
        link["error"] = error
        if not count:
            return
        link["failures"] += 1
        if link["failures"] >= FAILURES_FOR_REPAIR:
            ir.async_create_issue(self.hass, DOMAIN, self._failed_issue(room_id), is_fixable=False, is_persistent=False,
                                  severity=ir.IssueSeverity.WARNING, translation_key=WRITE_FAILED_ISSUE,
                                  translation_placeholders={
                                      "device": self._name(state) or link["device"],
                                      "room": (room or {}).get("name") or room_id,
                                      "error": error_text(error, _language(self.hass))})

    @callback
    def _not_there(self, room_id, room, link, device, state):
        """No write to a device that is gone or unavailable. Gone while Home Assistant runs (not still starting,
        when a device's integration may load after this one) counts as a failed write, once a minute."""
        if state is not None:
            link["error"] = ("unavailable", self._name(state) or device, None, "")
            return
        if self.hass.state is not CoreState.running:
            return
        if link["checked"] is not None and self.clock() - link["checked"] < MIN_INTERVAL:
            return
        link["checked"] = self.clock()
        self._failed(room_id, room, link, None, ("missing", device, None, ""))

    @callback
    def _forget_gone_links(self):
        """The records and Repairs items of rooms that are gone or no longer have a setting device."""
        devices = {room_id: device for room_id, _room, _status, device in self.rooms()}
        for room_id in [r for r, link in self.links.items() if devices.get(r) != link["device"]]:
            del self.links[room_id]
            ir.async_delete_issue(self.hass, DOMAIN, self._failed_issue(room_id))
        for room_id in [r for r, knob in self.knobs.items() if devices.get(r) != knob[0]]:
            self.knobs.pop(room_id)[2]()
            self.pending.pop(room_id, None)
        head = f"{WRITE_FAILED_ISSUE}_{self.entry.entry_id}_"
        rooms = {room.get("id") for room in (getattr(self.hub.plan, "plan", None) or {}).get("rooms", [])
                 if type(room) is dict}
        two_roles = f"{TWO_ROLES_ISSUE}_{self.entry.entry_id}_"
        for domain, issue in list(ir.async_get(self.hass).issues):
            if domain != DOMAIN:
                continue
            if issue.startswith(head) and devices.get(issue.removeprefix(head)) is None:
                ir.async_delete_issue(self.hass, DOMAIN, issue)
            elif issue.startswith(two_roles) and issue.removeprefix(two_roles) not in rooms:
                ir.async_delete_issue(self.hass, DOMAIN, issue)  # the room is gone

    # -- the knob --------------------------------------------------------------------
    @callback
    def _follow_devices(self):
        devices = tuple(sorted({device for *_rest, device in self.rooms()}))
        if devices == self._tracked:
            return
        self.stop_tracking()
        self._tracked = devices
        if devices:
            self._unsubscribe = async_track_state_change_event(self.hass, list(devices), self.device_changed)

    @callback
    def device_changed(self, event):
        if not self.hub.fresh:
            return
        entity_id, state = event.data["entity_id"], event.data.get("new_state")
        before = event.data.get("old_state")
        if state is not None and state.state != "unavailable" and (before is None or before.state in GONE):
            # Back (unavailable, or loaded after this integration): its target is what it had, not a knob turn.
            self.evaluate()
            return
        for room_id, room, status, device in self.rooms():
            if device != entity_id:
                continue
            link = self._link(room_id, device)
            if schedule_mode(state) is not None and schedule_mode(before) is None:
                self._own_program(room_id, room, link, state)  # back on its own schedule: manual again (safety net)
            if (schedule_mode(state) is None) != (schedule_mode(before) is None):
                # HA-OWN-PROGRAM (1.4.6): the room thermostat's "setting_device_own_schedule" follows the device's
                # report at once, not with the next write. After this callback, so a knob turn is registered first.
                self.hass.loop.call_soon(self.hub.notify)
            value = device_target(self.hass, state)
            old = device_target(self.hass, before)
            if value is None or (old is not None and abs(old - value) < 0.01):
                return  # no new target (another attribute changed)
            self._turned(room_id, room, status, state, value, link)
            return

    def _echo(self, room_id, room, status, state, value, link):
        """A device value that is no manual change: what we wrote last (or anything within ECHO_SECONDS of a write or
        of setting it to manual), the room's target now, or the frost limit, each within half the device's step."""
        last = self.pushed.get(room_id)
        if last is not None and last[0] == state.entity_id and (
                self.clock() - last[2] < ECHO_SECONDS or near(state, value, self.wrote.get(room_id))):
            return True
        if link["manual_clock"] is not None and self.clock() - link["manual_clock"] < ECHO_SECONDS:
            return True
        if near(state, value, self._current(status, room)) or near(state, value, FROST_C):
            return True
        return self._stale(room_id, state, value, link)

    @callback
    def _turned(self, room_id, room, status, state, value, link):
        """A new target on the device: once the knob rests (KNOB_SETTLE_S) it becomes the room's manual change."""
        if status is None:
            return
        if status.get("state") not in ("active", "follow") and (status.get("state") != "inactive" or has_program(room)):
            return  # Off with a week program: a turn is ignored (V1); without one it sets the fixed temperature
        if room_id not in self.knobs and self._echo(room_id, room, status, state, value, link):
            return  # (while the knob still turns every value is a step of it, also one back to the room's target)
        if status.get("setpoint_source") == "summer":
            self.evaluate()  # summer mode: no manual change; the frost limit goes back on the device within a minute
            return
        # Until the E32 reports it, the room's old target is not written back over the knob.
        self.pending[room_id] = (half_up(value), self.clock() + KNOB_SETTLE_S + PENDING_SECONDS)
        previous = self.knobs.get(room_id)
        if previous is not None:
            previous[2]()

        @callback
        def rested(_now=None):
            self._settled(room_id)
        self.knobs[room_id] = (state.entity_id, value, self.call_later(self.hass, KNOB_SETTLE_S, rested))

    @callback
    def _settled(self, room_id):
        """The knob rests: its last value (on a half degree) becomes the room's manual change, unless it went back to
        the room's target."""
        knob = self.knobs.pop(room_id, None)
        if knob is None:
            return
        entity_id, value = knob[0], half_up(knob[1])
        found = next(((room, status) for r, room, status, device in self.rooms() if r == room_id and device == entity_id),
                     None)
        if found is None or found[1] is None or not self.hub.fresh:
            self.pending.pop(room_id, None)
            return
        room, status = found
        current = self._current(status, room)
        if current is not None and abs(current - value) < 0.01:
            self.pending.pop(room_id, None)
            self.evaluate()  # turned back to the room's target (or within its half degree): the device shows it again
            return
        self.pending[room_id] = (value, self.clock() + PENDING_SECONDS)
        link = self._link(room_id, entity_id)
        link["knob"], link["knob_at"] = value, self.now().isoformat()
        state = self.hass.states.get(entity_id)
        self._note_unasked(room_id, room, entity_id, state)
        self.hass.async_create_task(self._override(room_id, room, value), f"OpenThermostat knob {entity_id}")

    async def _override(self, room_id, room, value):
        """The knob's value as the room's manual change (1.4.2: with or without a program; the state stays)."""
        try:
            answer = await self._manual(room_id, value)
        except HomeAssistantError as err:
            self.pending.pop(room_id, None)
            _LOGGER.warning("E32 room %s: could not take over %s °C from its setting device: %s", room_id, value, err)
            link = self.links.get(room_id)
            if link is not None:
                self._failed(room_id, room, link, None, ("knob", link["device"], value, _detail(err)), count=False)
            return
        applied = answer.get("applied") if type(answer) is dict else None
        _LOGGER.debug("E32 room %s: %s °C from its setting device taken over%s", room_id, value,
                      f" ({applied})" if applied else "")

    async def _manual(self, room_id, value):
        """E32 1.4.2 (``room.manual.v1``): one command "manual", the firmware decides; older firmware (or one that
        answers ``invalid_override`` after a downgrade) gets the split from Home Assistant (_split)."""
        from .e32_comfort import async_comfort_command
        from .room_plan import plan_room
        link = self.hub.plan
        if MANUAL_FEATURE in (getattr(link, "features", None) or ()):
            try:
                return await async_comfort_command(link, {"room": room_id, "override": "manual", "temperature": value,
                                                          "by": "device"})
            except ServiceValidationError as err:
                if not manual_unknown(err):
                    raise
                _LOGGER.info("E32 room %s: the E32 does not know the manual command (older firmware); Home Assistant "
                             "makes the change itself", room_id)
        return await self._split(link, room_id, plan_room(link.plan, room_id) or {}, self.hub.rooms.get(room_id) or {},
                                 value)

    @staticmethod
    async def _split(link, room_id, plan_room, status, value):
        """Before E32 1.4.2: with a program ``next`` (``timed`` NO_CLOCK_MINUTES without the clock), without one the
        plan's temperature without a week program, written as a routine write, and a running override ends. An
        "Off until" that ended is written in the plan first (E32 1.4.1 refuses the change otherwise); one sign-in."""
        from .e32_comfort import async_comfort_command
        from .room_plan import on_state, set_fallback, set_state
        async with _session(link):
            if off_until_over(plan_room, status, int(dt_util.utcnow().timestamp())):
                await async_routine_room_change(link, room_id, set_state(on_state(plan_room)))
            if has_program(plan_room):
                try:
                    return await async_comfort_command(link, {"room": room_id, "override": "next", "temperature": value})
                except ServiceValidationError as err:
                    if err.translation_key not in ("comfort_no_clock", "comfort_no_schedule"):
                        raise
                return await async_comfort_command(link, {"room": room_id, "override": "timed", "temperature": value,
                                                          "minutes": NO_CLOCK_MINUTES})
            stored = await async_routine_room_change(link, room_id, set_fallback(int(round(value * 100))),
                                                     ("fallback", room_id))
            comfort = status.get("comfort") if type(status.get("comfort")) is dict else {}
            if comfort.get("override") in ("boost", "timed", "next"):
                await async_comfort_command(link, {"room": room_id, "override": "none"})
            return stored

    # -- the device's own schedule ------------------------------------------------------
    @callback
    def _own_program(self, room_id, room, link, state):
        """Set a device that runs its own schedule to manual: at most once an hour and MANUAL_TRIES times per room's
        device, never from "off" (schedule_mode)."""
        if schedule_mode(state) is None or link["manual_tries"] >= MANUAL_TRIES:
            return
        if link["manual_clock"] is not None and self.clock() - link["manual_clock"] < MANUAL_RETRY_S:
            return
        link["manual_tries"] += 1
        link["manual_clock"] = self.clock()
        self.hass.async_create_task(self._set_manual(room_id, room, link, state),
                                    f"OpenThermostat setting device {state.entity_id} to manual")

    async def _set_manual(self, room_id, room, link, state):
        try:
            service = await async_set_manual(self.hass, state)
        except Exception as err:  # noqa: BLE001 - a refusal is logged; the pattern's Repairs item stays the net
            _LOGGER.warning("E32 room %s: could not set %s from its own schedule to manual: %s",
                            (room or {}).get("name") or room_id, state.entity_id, err)
            return
        if service is None:
            return
        link["manual_at"] = self.now().isoformat()
        _LOGGER.info("E32 room %s: %s followed its own schedule; Home Assistant set it to manual so the room decides",
                     (room or {}).get("name") or room_id, state.entity_id)

    def _recent_unasked(self, entity_id):
        now = self.now()
        return [(d, q) for d, q in self.unasked.get(entity_id, []) if (now.date() - d).days < SCHEDULE_WINDOW_DAYS]

    def _own_schedule(self, entity_id):
        """Unasked changes at about the same quarter on SCHEDULE_DAYS days within the window."""
        seen = self._recent_unasked(entity_id)
        return any(len({d for d, other in seen if abs(other - q) <= 1}) >= SCHEDULE_DAYS for _, q in seen)

    @callback
    def _clear_own_schedule_issues(self):
        """The "own schedule" item goes once the condition is gone: the device stopped changing by
        itself for SCHEDULE_WINDOW_DAYS, it is no longer the room's setting device, or the room is gone."""
        head = f"{OWN_SCHEDULE_ISSUE}_{self.entry.entry_id}_"
        devices = {room_id: device for room_id, _room, _status, device in self.rooms()}
        for domain, issue in list(ir.async_get(self.hass).issues):
            if domain != DOMAIN or not issue.startswith(head):
                continue
            device = devices.get(issue.removeprefix(head))
            if device is None or not self._own_schedule(device):
                ir.async_delete_issue(self.hass, DOMAIN, issue)

    def _note_unasked(self, room_id, room, entity_id, state):
        now = self.now()
        quarter = (now.hour * 60 + now.minute) // 15
        seen = self._recent_unasked(entity_id)
        seen.append((now.date(), quarter))
        self.unasked[entity_id] = seen[-64:]
        days = {d for d, q in seen if abs(q - quarter) <= 1}
        if len(days) >= SCHEDULE_DAYS:
            name = state.name if state is not None else entity_id
            ir.async_create_issue(self.hass, DOMAIN, f"{OWN_SCHEDULE_ISSUE}_{self.entry.entry_id}_{room_id}",
                                  is_fixable=False, is_persistent=False, severity=ir.IssueSeverity.WARNING,
                                  translation_key=OWN_SCHEDULE_ISSUE,
                                  translation_placeholders={"device": name, "room": room.get("name") or room_id})
            link = self.links.get(room_id)
            if link is not None and state is not None:
                self._own_program(room_id, room, link, state)  # the safety net: manual again if it shows its schedule

    # -- one role per valve: the update's one-time check ------------------------------------
    @callback
    def _check_two_roles(self):
        """Once per installation (option TWO_ROLES_DONE), when the plan is read: a radiator valve the E32 drives
        that is also a room's setting device gets its room's valve control switched off (_two_roles_fix)."""
        if self._two_roles is not None:
            return
        if (getattr(self.entry, "options", None) or {}).get(TWO_ROLES_DONE) is True:
            self._two_roles = "done"
            return
        plan = getattr(self.hub.plan, "plan", None)
        if type(plan) is not dict:
            return
        if self._two_roles_at is not None and self.clock() - self._two_roles_at < TWO_ROLES_RETRY_S:
            return
        self._two_roles = "running"
        self.hass.async_create_task(self._migrate_two_roles(plan), "OpenThermostat one role per valve")

    async def _migrate_two_roles(self, plan):
        try:
            await self._two_roles_fix(plan)
        except Exception as err:  # noqa: BLE001 - the valve record not readable now: later, at most three times
            self._two_roles_tries += 1
            self._two_roles_at = self.clock()
            self._two_roles = "done" if self._two_roles_tries >= 3 else None
            _LOGGER.debug("OpenThermostat: checking the setting devices against the radiator valves failed: %s", err)
            return
        _mark_two_roles_done(self.hass, self.entry)
        self._two_roles = "done"

    async def _two_roles_fix(self, plan):
        """Valve control off for every room whose driven valve is also a room's setting device; returns those rooms."""
        from .e32_valves import ValveLink
        from .room_plan import plan_room
        from .valve_routes import valve_entities
        devices = {}
        for room in plan.get("rooms") or []:
            device = setting_device(room)
            if device is not None and device.startswith("climate."):
                devices.setdefault(device, room)
        if not devices:
            return []  # no climate setting device: nothing can have both roles
        link = ValveLink(self.hass, self.hub, self.hub.plan)  # the record read right before its change
        config = await link.async_read()
        fixed = []
        for room_id, entities in valve_entities(self.hass, config, driven_only=True).items():
            both = [entity for entity in entities if entity in devices]
            if not both:
                continue
            await link.async_change(room_id, control=False)
            state = self.hass.states.get(both[0])
            device = state.name if state is not None else both[0]
            valves_room = (plan_room(plan, room_id) or {}).get("name") or room_id
            setting_room = devices[both[0]].get("name") or devices[both[0]].get("id")
            _LOGGER.warning("OpenThermostat: %s was the setting device of %s and a radiator valve the E32 drives in %s; "
                            "valve control of %s is now off (a device has one role). Choose on the room's screen.",
                            both[0], setting_room, valves_room, valves_room)
            ir.async_create_issue(self.hass, DOMAIN, two_roles_issue(self.entry, room_id), is_fixable=False,
                                  is_persistent=True, severity=ir.IssueSeverity.WARNING,
                                  translation_key=TWO_ROLES_ISSUE,
                                  translation_placeholders={"device": device, "room": valves_room,
                                                            "setting_room": setting_room})
            fixed.append(room_id)
        return fixed

    # -- lifecycle -------------------------------------------------------------------------
    @callback
    def stop_tracking(self):
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None
        self._tracked = ()

    @callback
    def start(self):
        # Retired in 1.4 (issue #7): the item room_programs ("Give your rooms a week program") of older versions.
        remove_retired_issues(self.hass, self.entry.entry_id)
        remove = self.hub.add_listener(self.evaluate)
        self.evaluate()

        @callback
        def stop():
            remove()
            self.stop_tracking()
            if self._retry is not None:
                self._retry()
                self._retry = None
            for knob in self.knobs.values():
                knob[2]()
            self.knobs.clear()
        return stop
