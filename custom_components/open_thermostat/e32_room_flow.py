"""E32 rooms: the Home Assistant editor of the E32 room plan.

The rooms live in the E32 room plan (GET/POST /config/heating) and keep
running on the E32 without Home Assistant. This options flow step lists them
and adds, edits or removes one room at a time through RoomPlanLink: the whole
plan with the revision it was read at; on 409 the plan is read again and the
same edit applied once. An edit changes only the fields the form changed, so a
concurrent change on the E32's own page to another field or room survives.

Each source records who reads it: "ha" (a Home Assistant climate or °C
temperature sensor that HA forwards to the E32) or "ble" (a Bluetooth sensor
paired on the E32, read by the E32 itself).

The form also holds the room's window and door contacts: any Home Assistant
binary sensor of the class window, door, opening or garage door. They are not
part of the E32 plan but of this entry's comfort settings (e32_comfort.py),
which forward the room's combined state to the E32 (RoomOverrides.h): open
for longer than the delay pauses the room at frost protection.

Its Persons section holds the room's persons (comfort settings, like the
contacts) and, for an E32 that names "plan.room_away.v1", the room's own away
temperature (room_away.py): a plan field, used while all of the room's persons
are away and someone else is home; empty is the house value.

The form's last section holds the room's radiator valves (rc.3, one room in one
place): just their climate entities. valve_routes.py decides per valve whether
the E32 drives it over Zigbee2MQTT ("works without Home Assistant") or Home
Assistant does; the E32's valve record (e32_valves.ValveLink) is written after
the plan, so a new room exists before its valves. "Choose the models myself"
opens one more step with a model per Zigbee2MQTT valve. Firmware without valve
records shows no section and leaves them alone.

E32 1.1 (Shelly): the same section lists the BLU Gateway's valves the E32 reads
(``GET /status/shelly``, on the same sign-in as the valve record): which belong
to this room, which of them are floor loop valves on the manifold, and which
radiator is kept open as the water's path. A room takes up to 8 valves, at most
4 that are not on the gateway. Firmware without Shelly shows none of this.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
import re

import probatio as vol
from homeassistant.const import UnitOfTemperature
from homeassistant.data_entry_flow import section
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .const import CONF_TOPIC_PREFIX, DOMAIN
from .e32_comfort import (DELAY_LIMITS, ComfortError, comfort_options, contact_delay_text, contact_selector,
                          own_contact_delay, persons_selector, room_contact_delay, room_contacts, room_door_delay,
                          room_doors, room_persons, save_comfort, validate_contacts, validate_kinds,
                          validate_room_persons, with_room_contacts, with_room_persons)
from .heating_link import TEMPERATURE_UNITS, celsius, heating_hub, label, number
from .native_form import retained_input_schema
from .room_plan import LATEST_UNTIL, LINK_ERRORS, follows, has_room_plan, plan_room, until_datetime
from . import room_away

MAX_ROOMS = 8
# The room form's title while adding a room (its name once it has one), EN/NL/PL.
NEW_ROOM_TITLE = {"en": "new room", "nl": "nieuwe ruimte", "pl": "nowe pomieszczenie"}
MAX_SOURCES = 4
MAX_VALVE_MODELS = 4  # the Advanced step: one model per Zigbee2MQTT valve of a room (e32_valves.MAX_VALVES_PER_ROOM)
MAX_POINTS = 6
NAME_BYTES = 40
ROOM_ID_LENGTH = 32
LIMITS_CENTI_C = (500, 3000)
ENTITY_ID = re.compile(r"[a-z0-9_]+\.[a-z0-9_]+")
SOURCE_DOMAINS = ("climate", "sensor")
from .e32_setting_device import default_program, proposed_device, setting_hint  # noqa: E402
SETPOINT_DOMAINS = ("climate", "input_number", "number")
CELSIUS = UnitOfTemperature.CELSIUS
# The plan's flow limits as the E32 accepts them (RoomPlan.h): whole °C, minimum
# 20–79 and maximum 21–80, minimum below maximum. Up to 80 °C for radiator homes;
# firmware before that refuses more than 60 °C (invalid_flow_limits, shown as
# e32_rejected_flow_limits).
FLOW_MINIMUM_C = (20, 79)
FLOW_MAXIMUM_C = (21, 80)
# Floor heating without a mixing valve: a higher maximum earns a warning first.
FLOOR_FLOW_WARNING_C = 50
FAHRENHEIT = UnitOfTemperature.FAHRENHEIT
# Plan error names of the E32 (RoomPlan.h) -> a clear message instead of the code.
REJECTIONS = {"invalid_sources": "e32_rejected_sources", "invalid_room_name": "e32_name_invalid",
              "duplicate_room": "e32_rejected_duplicate_room", "duplicate_source": "e32_rejected_duplicate_source",
              "invalid_setpoint_entity": "e32_rejected_setpoint", "invalid_room_limits": "e32_limits_invalid",
              "invalid_flow_limits": "e32_rejected_flow_limits", "invalid_schedule": "e32_rejected_schedule",
              "invalid_schedule_limits": "e32_rejected_schedule", "invalid_room_away": "e32_away_invalid",
              # E32 1.4: the room's reset times
              "invalid_reset": "e32_rejected_resets", "invalid_reset_limits": "e32_rejected_resets",
              "too_many_resets": "e32_resets_too_many"}
# The one sentence about the boiler's own maximum in the flow-limits form.
BOILER_MAXIMUM_TEXT = {
    "en": "Boiler maximum: {maximum} (set on the boiler); the E32 never asks for more. A lower limit here is "
          "useful for floor heating.",
    "nl": "Maximum van de ketel: {maximum} (ingesteld op de ketel); de E32 vraagt nooit meer. Een lagere grens "
          "hier is nuttig bij vloerverwarming.",
    "pl": "Maksimum kotła: {maximum} (ustawione na kotle); E32 nigdy nie żąda więcej. Niższy limit jest tu "
          "przydatny przy ogrzewaniu podłogowym."}
FLOW_LIMIT_FIELDS = {"minimum_flow_temperature": "minimum_flow_c", "maximum_flow_temperature": "maximum_flow_c"}
# Plan item 1 (E32 with "minimum_flow_automatic" in its plan): the lowest water temperature automatic (the
# default; the E32 keeps 30 °C as the hard lower bound and its learned floors decide above it) or set by you.
MINIMUM_AUTOMATIC_KEY = "minimum_flow_automatic"
MINIMUM_AUTOMATIC_FIELD = "minimum_flow_automatic"
# E32 1.4 (#8): a room's own Smart warm-up ("house" | "on" | "off"; absent: as the house), only for an E32 that names it.
SMART_WARM_UP_FEATURE, SMART_WARM_UP_FIELD = "plan.room_smart_warm_up.v1", "smart_warm_up"
STANDARD_MINIMUM_FLOW_C = 30  # RoomPlan::defaultMinimumFlowC
# The form's line about the lowest water temperature in effect (fw/telemetry/flow "minimum_flow"), EN/NL/PL;
# the same words as the E32's House page.
MINIMUM_NOW_TEXT = {
    "en": {"standard": "Lowest water temperature now: {value} (standard).",
           "own": "Lowest water temperature now: {value} (set by you).",
           "learned": "Lowest water temperature now: {value} (learned)."},
    "nl": {"standard": "Laagste watertemperatuur nu: {value} (standaard).",
           "own": "Laagste watertemperatuur nu: {value} (door jou ingesteld).",
           "learned": "Laagste watertemperatuur nu: {value} (geleerd)."},
    "pl": {"standard": "Najniższa temperatura wody teraz: {value} (standardowa).",
           "own": "Najniższa temperatura wody teraz: {value} (ustawiona przez ciebie).",
           "learned": "Najniższa temperatura wody teraz: {value} (wyuczona)."}}


def minimum_flow_now(summary):
    """(°C, "standard" | "own" | "learned", automatic) of the lowest water temperature the E32 applies now
    (fw/telemetry/flow "minimum_flow", plan item 1), or None from firmware without it."""
    flow = summary.get("flow") if type(summary) is dict else None
    minimum = flow.get("minimum_flow") if type(flow) is dict else None
    if type(minimum) is not dict:
        return None
    value, automatic, source = minimum.get("c"), minimum.get("automatic"), minimum.get("source")
    if type(value) not in (int, float) or type(value) is bool or type(automatic) is not bool:
        return None
    if source in ("boiler", "steady"):
        return value, "learned", automatic
    return value, "standard" if automatic else "own", automatic

DAYS = {"en": ("mon", "tue", "wed", "thu", "fri", "sat", "sun"),
        "nl": ("ma", "di", "wo", "do", "vr", "za", "zo")}
DAY_NAMES = {name: index for names in (
    *DAYS.values(),
    ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"),
    ("maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"),
) for index, name in enumerate(names)}
POINT = re.compile(r"(\d{1,2})[:.](\d{2})\s+(\d{1,2}(?:[.,]\d{1,2})?)")
DAY_PREFIX = re.compile(r"([a-z][a-z ,\-]*?)\s*:\s*(.*)")

# Reset times (E32 1.4, docs/engineering/TERUGZETMOMENT-ONTWERP.nl.md): on a time, on chosen days, any manual change
# of the room ends and the room takes one value, a temperature or a state; the E32 never works towards it. The plan
# keeps them per room as "resets": [{"days": [0..6], "time": "HH:MM", "temperature_c": 14.0} or {..., "state":
# "follow"}], at most four, never two on the same day and minute. Firmware before 1.4 has no such key and ignores it.
MAX_RESETS = 4
RESET_STATES = ("active", "follow", "inactive")
# A state's word in the form, EN and NL (Polish uses the English words, as it does the day names).
STATE_WORDS = {"en": {"active": "on", "follow": "heat along", "inactive": "off"},
               "nl": {"active": "aan", "follow": "meeverwarmen", "inactive": "uit"}}
STATE_NAMES = {**{word: state for words in STATE_WORDS.values() for state, word in words.items()},
               "heat along only": "follow", "alleen meeverwarmen": "follow"}
EVERY_DAY = {"en": "daily", "nl": "dag"}
EVERY_DAY_NAMES = frozenset({"daily", "every day", "dag", "elke dag", "dagelijks"})
RESET_LINE = re.compile(r"(?:([a-z][a-z ,\-]*?)\s*:?\s+)?(\d{1,2})[:.](\d{2})\s+(.+)")
RESET_TEMPERATURE = re.compile(r"(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:°\s*[cf]?)?")
# The form's one sentence while the E32 has no reset times (firmware before 1.4), after the program's help, EN/NL/PL.
RESETS_LATER_TEXT = {
    "en": " With E32 firmware 1.4 or newer you can also set reset times here.",
    "nl": " Met E32-firmware 1.4 of nieuwer kun je hier ook terugzetmomenten instellen.",
    "pl": " Z oprogramowaniem E32 w wersji 1.4 lub nowszej możesz tu też ustawić godziny powrotu."}
# After a save, the room list says what the room's week program and reset times now are (issue #7), EN/NL/PL.
SAVED_PROGRAM_TEXT = {
    "en": {"none": "Week program: none; the room keeps {temperature} without a week program.",
           "program": "Week program:", "resets": "Reset times:"},
    "nl": {"none": "Weekprogramma: geen; de ruimte houdt {temperature} zonder weekprogramma.",
           "program": "Weekprogramma:", "resets": "Terugzetmomenten:"},
    "pl": {"none": "Program tygodniowy: brak; pomieszczenie utrzymuje {temperature} bez programu tygodniowego.",
           "program": "Program tygodniowy:", "resets": "Godziny powrotu:"}}

# HA error translation keys of RoomPlanLink -> this flow's error/abort keys.
FAILURES = {"room_plan_changed": "e32_plan_changed", "room_plan_too_large": "e32_plan_too_large",
            "room_plan_storage_full": "e32_storage_full",
            "room_plan_rejected": "e32_rejected", "room_plan_unconfirmed": "e32_unconfirmed",
            "room_plan_unreachable": "e32_unreachable", "room_plan_invalid": "e32_plan_invalid",
            "room_plan_room_missing": "e32_room_missing", "room_plan_password": "e32_password_changed",
            # room_plan.LINK_ERRORS: the form says the plan could not be reached or read, with the code
            **dict.fromkeys(LINK_ERRORS.values(), "e32_unreachable")}
ABORTS = {"e32_unconfirmed", "e32_plan_invalid", "e32_room_missing", "e32_password_changed"}


class FlowError(Exception):
    """A form error key (and the field it belongs to)."""

    def __init__(self, key, field="base", **placeholders):
        super().__init__(key)
        self.key, self.field, self.placeholders = key, field, placeholders


def unique_room_id(name, taken):
    """A room id from the name ([a-z0-9_], at most 32), unique in the plan."""
    base = re.sub(r"[^a-z0-9_]", "", slugify(name, separator="_"))[:ROOM_ID_LENGTH].strip("_")
    if not base or base == "unknown" and "unknown" not in name.lower():  # slugify's empty result
        base = "room"
    candidate, count = base, 1
    while candidate in taken:
        count += 1
        suffix = f"_{count}"
        candidate = base[:ROOM_ID_LENGTH - len(suffix)] + suffix
    return candidate


def valid_name(value):
    name = (value or "").strip()
    if not name or len(name.encode()) > NAME_BYTES or any(ord(c) < 32 for c in name):
        raise FlowError("e32_name_invalid", "name")
    return name


def centi(value, unit=CELSIUS):
    """A temperature in the user's unit (°C or °F) as the plan's centi-°C (°F: to 0.1 °C)."""
    try:
        number = Decimal(str(value).replace(",", "."))
        if not number.is_finite():
            raise InvalidOperation
        if unit == FAHRENHEIT:
            return int(((number - 32) * 50 / 9).to_integral_value(ROUND_HALF_UP)) * 10
        return int((number * 100).to_integral_value(ROUND_HALF_UP))
    except (InvalidOperation, ValueError):
        raise FlowError("e32_program_invalid", "program") from None


def shown(centi_c, unit=CELSIUS):
    """The plan's centi-°C in the user's unit (°F with one decimal)."""
    if unit == FAHRENHEIT:
        return float((Decimal(centi_c) * 9 / 500 + 32).quantize(Decimal("0.1"), ROUND_HALF_UP))
    return centi_c / 100


def flow_shown(celsius_value, unit=CELSIUS):
    """A whole-°C flow temperature in the user's unit (whole °F)."""
    return round(celsius_value * 9 / 5 + 32) if unit == FAHRENHEIT else celsius_value


def flow_celsius(value, unit=CELSIUS):
    """A whole flow temperature in the user's unit as whole °C (None when not whole)."""
    if not float(value).is_integer():
        return None
    return round((value - 32) * 5 / 9) if unit == FAHRENHEIT else int(value)


def _days(text):
    days = []
    for token in (t.strip() for t in text.split(",")):
        ends = [part.strip() for part in token.split("-")]
        if len(ends) > 2 or any(end not in DAY_NAMES for end in ends):
            raise FlowError("e32_program_invalid", "program")
        first, last = DAY_NAMES[ends[0]], DAY_NAMES[ends[-1]]
        days += [(first + step) % 7 for step in range((last - first) % 7 + 1)]
    return days


def parse_program(text, minimum, maximum, unit=CELSIUS):
    """The 7-day schedule from the program text, or None for no program.

    One line per group of days: "mon-fri: 06:30 20.5; 22:30 18" (Dutch
    "ma-vr: 06:30 20,5; 22:30 18"; a comma between points works too); a line
    without days applies to every day. Days not named have no switch point
    (the previous point holds, as on the E32). Temperatures are in the user's
    unit (°C or °F). An error names the line it could not read.
    """
    week = [None] * 7
    for number, original in enumerate((text or "").splitlines(), 1):
        try:
            _parse_line(original, week, minimum, maximum, unit)
        except FlowError as err:
            err.placeholders.setdefault("line", str(number))
            err.placeholders.setdefault("text", original.strip()[:60])
            raise
    if all(day is None for day in week):
        return None
    return [day or [] for day in week]


def _parse_line(original, week, minimum, maximum, unit):
    """One program line into week (days -> points); raises FlowError."""
    line = original.lower().replace("–", "-").strip()
    if not line:
        return
    prefix = DAY_PREFIX.fullmatch(line)
    days, body = (_days(prefix[1]), prefix[2]) if prefix else (range(7), line)
    points, position = {}, 0
    for match in POINT.finditer(body):
        if body[position:match.start()].strip(" ,;\t"):
            raise FlowError("e32_program_invalid", "program")
        position = match.end()
        hour, minute = int(match[1]), int(match[2])
        if hour > 23 or minute > 59 or hour * 60 + minute in points:
            raise FlowError("e32_program_invalid", "program")
        value = centi(match[3], unit)
        if not minimum <= value <= maximum:
            raise FlowError("e32_program_outside_limits", "program")
        points[hour * 60 + minute] = value
    if not points or body[position:].strip(" ,;\t"):
        raise FlowError("e32_program_invalid", "program")
    if len(points) > MAX_POINTS:
        raise FlowError("e32_program_too_many", "program")
    for day in days:
        if week[day] is not None:
            raise FlowError("e32_program_invalid", "program")
        week[day] = [[minute, points[minute]] for minute in sorted(points)]


def _day_ranges(days, names):
    runs = []
    for day in days:
        if runs and runs[-1][1] == day - 1:
            runs[-1][1] = day
        else:
            runs.append([day, day])
    return ",".join(names[a] if a == b else f"{names[a]}-{names[b]}" for a, b in runs)


def format_program(schedule, language="en", unit=CELSIUS):
    """The program text for a stored schedule (identical days grouped; Dutch with decimal commas)."""
    if type(schedule) is not list or len(schedule) != 7 or not any(schedule):
        return ""
    dutch = language == "nl"
    names = DAYS["nl" if dutch else "en"]
    groups = {}

    def degrees(c):
        text = f"{shown(c, unit):g}"
        return text.replace(".", ",") if dutch else text
    for day, points in enumerate(schedule):
        if points:
            key = "; ".join(f"{m // 60:02d}:{m % 60:02d} {degrees(c)}" for m, c in points)
            groups.setdefault(key, []).append(day)
    return "\n".join(key if len(days) == 7 else f"{_day_ranges(days, names)}: {key}"
                     for key, days in groups.items())


RESETS_FEATURE = "plan.room_resets.v1"


def resets_supported(plan):
    """True when the E32 that answered this plan has reset times: it names plan.room_resets.v1 (also with no room
    yet), or, as a fallback, a room carries "resets" (1.4 sends the key with every room)."""
    if type(plan) is not dict:
        return False
    features, rooms = plan.get("features"), plan.get("rooms")
    if type(features) is list and RESETS_FEATURE in features:
        return True
    return type(rooms) is list and any(type(room) is dict and type(room.get("resets")) is list for room in rooms)


def parse_resets(text, minimum, maximum, unit=CELSIUS):
    """The room's reset times from the form's text ([] for none); an error names the line it could not read.

    One per line: days, time and value, "mon-fri 22:00 14" or "daily 09:00 heat along" (Dutch "ma-vr 22:00 14",
    "dag 09:00 meeverwarmen"). The days as in the week program; "daily" (or no days) is every day. The value is a
    temperature in the user's unit (whole or half °C; °F to the nearest half °C) within the room's limits, or a
    state: on, heat along, off (aan, meeverwarmen, uit). At most four; never two on the same day and minute.
    """
    resets, moments = [], set()
    for number, original in enumerate((text or "").splitlines(), 1):
        line = " ".join(original.lower().replace("–", "-").split())
        if not line:
            continue
        try:
            reset = _parse_reset(line, minimum, maximum, unit)
            if any((day, reset["time"]) in moments for day in reset["days"]):
                raise FlowError("e32_resets_same_moment", "resets")
        except FlowError as err:
            err.placeholders.setdefault("line", str(number))
            err.placeholders.setdefault("text", original.strip()[:60])
            raise
        moments.update((day, reset["time"]) for day in reset["days"])
        resets.append(reset)
    if len(resets) > MAX_RESETS:
        raise FlowError("e32_resets_too_many", "resets")
    return resets


def _parse_reset(line, minimum, maximum, unit):
    """One reset time line (lower case, single spaces) in the plan's form; raises FlowError."""
    match = RESET_LINE.fullmatch(line)
    if match is None or int(match[2]) > 23 or int(match[3]) > 59:
        raise FlowError("e32_resets_invalid", "resets")
    if match[1] is None or match[1].strip() in EVERY_DAY_NAMES:
        days = list(range(7))
    else:
        try:
            days = sorted(set(_days(match[1])))
        except FlowError:
            raise FlowError("e32_resets_invalid", "resets") from None
    reset = {"days": days, "time": f"{int(match[2]):02d}:{match[3]}"}
    value = match[4].strip()
    if value in STATE_NAMES:
        reset["state"] = STATE_NAMES[value]
        return reset
    temperature = RESET_TEMPERATURE.fullmatch(value)
    if temperature is None:
        raise FlowError("e32_resets_invalid", "resets")
    try:
        centi_c = centi(temperature[1], unit)
    except FlowError:
        raise FlowError("e32_resets_invalid", "resets") from None
    if unit == FAHRENHEIT:  # the E32 keeps half degrees, as the thermostat sets them
        centi_c = int((Decimal(centi_c) / 50).to_integral_value(ROUND_HALF_UP)) * 50
    elif centi_c % 50:
        raise FlowError("e32_resets_invalid", "resets")
    if not minimum <= centi_c <= maximum:
        raise FlowError("e32_resets_outside_limits", "resets")
    reset["temperature_c"] = centi_c / 100
    return reset


def reset_value(reset, language="en", unit=CELSIUS):
    """A reset time's value in words: its temperature in the user's unit (Dutch: decimal comma) or its state word."""
    words = STATE_WORDS["nl" if language == "nl" else "en"]
    if reset.get("state") in RESET_STATES:
        return words[reset["state"]]
    temperature = reset.get("temperature_c")
    if type(temperature) not in (int, float):
        return None
    text = f"{shown(round(temperature * 100), unit):g}"
    return text.replace(".", ",") if language == "nl" else text


def format_resets(resets, language="en", unit=CELSIUS):
    """The form's text for the room's stored reset times: one per line, in the stored order."""
    if type(resets) is not list:
        return ""
    dutch = language == "nl"
    names = DAYS["nl" if dutch else "en"]
    lines = []
    for reset in resets:
        if type(reset) is not dict or type(reset.get("time")) is not str:
            continue
        days = sorted({day for day in reset.get("days") or [] if type(day) is int and 0 <= day <= 6})
        value = reset_value(reset, language, unit)
        if not days or value is None:
            continue
        when = EVERY_DAY["nl" if dutch else "en"] if len(days) == 7 else _day_ranges(days, names)
        lines.append(f"{when} {reset['time']} {value}")
    return "\n".join(lines)


def source_problem(hass, entity_id, setpoint=False):
    """An error key when the E32 cannot use this HA entity as a source (or setpoint), else None."""
    if len(entity_id) > 80 or not ENTITY_ID.fullmatch(entity_id):
        return "e32_source_invalid_id"
    domain = entity_id.split(".", 1)[0]
    if domain not in (SETPOINT_DOMAINS if setpoint else SOURCE_DOMAINS):
        return "e32_source_wrong_domain"
    state = hass.states.get(entity_id)
    if state is None:
        return "e32_source_not_found"
    if domain == "climate":
        # Climate attributes are in the HA unit system (°C or °F); they are
        # converted to °C before they are forwarded to the E32.
        if not setpoint and celsius(state.attributes.get("current_temperature"),
                                    hass.config.units.temperature_unit, -40, 85) is None:
            return "e32_source_no_temperature"
        return None
    unit = state.attributes.get("unit_of_measurement")
    # °F and K sources are converted to °C on the way to the E32; other units are refused.
    if domain == "sensor" and unit not in TEMPERATURE_UNITS or domain != "sensor" and unit not in (None, "", *TEMPERATURE_UNITS):
        return "e32_source_not_celsius"
    return None


class E32RoomFlow:
    """Options flow steps for the E32 room plan (mixed into ProductOptionsFlow)."""

    def _e32_link(self):
        entry = self.config_entry
        if not has_room_plan(entry) or entry.entry_id not in self.hass.data.get(DOMAIN, {}):
            return None
        return heating_hub(self.hass, entry).plan

    def _e32_failure(self, err):
        key = FAILURES.get(getattr(err, "translation_key", None), "e32_rejected")
        placeholders = dict(getattr(err, "translation_placeholders", None) or {})
        placeholders.setdefault("error", getattr(err, "translation_key", None) or "unknown")
        if key == "e32_rejected":
            key = REJECTIONS.get(placeholders["error"], key)
        return key, placeholders

    def _unit(self):
        """The Home Assistant temperature unit (°C or °F); the E32 plan itself is always °C."""
        unit = getattr(getattr(getattr(self.hass, "config", None), "units", None), "temperature_unit", CELSIUS)
        return FAHRENHEIT if unit == FAHRENHEIT else CELSIUS

    def _e32_abort_failure(self, err):
        key, placeholders = self._e32_failure(err)
        if key not in ABORTS | {"e32_unreachable"}:
            key = "e32_unreachable"
        return self.async_abort(reason=key, description_placeholders=placeholders)

    async def async_step_e32_rooms(self, user_input=None, done=None, name=None, valves="", program=""):
        """The room list and what to do next; done ("saved"/"removed") says what just happened.

        valves: after a save, the saved room's radiator valves and their route, one per line; program: its week
        program and reset times as saved (issue #7: also when it has none).
        """
        link = self._e32_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        if done is not None and link.plan is not None:
            plan = link.plan  # just stored and confirmed by the E32
        else:
            try:
                plan = await link.async_read()
            except HomeAssistantError as err:
                return self._e32_abort_failure(err)
        self._e32_plan = plan
        # The flow limits are for all rooms together: Configure → Heating and boiler (product_flow.py).
        options = (["e32_room_add"] if len(plan["rooms"]) < MAX_ROOMS else []) + (
            ["e32_room_pick"] if plan["rooms"] else [])
        from .options_navigation import async_flow_texts
        texts = await async_flow_texts(self.hass, "e32_room_list_text")
        placeholders = {"rooms": self._e32_room_list(plan, texts), "revision": str(plan["revision"])}
        if done is not None:
            placeholders["name"] = name or ""
            placeholders["valves"] = valves or ""
            placeholders["program"] = program or ""
        return self.async_show_menu(step_id="e32_rooms" if done is None else f"e32_rooms_{done}",
                                    menu_options=options, description_placeholders=placeholders)

    async def async_step_e32_rooms_saved(self, user_input=None):
        """The room list right after a save (its own text: what was saved)."""
        return await self.async_step_e32_rooms()

    async def async_step_e32_rooms_removed(self, user_input=None):
        """The room list right after a removal."""
        return await self.async_step_e32_rooms()

    def _e32_source_label(self, source):
        if source.get("type") == "ble":
            sensor = heating_hub(self.hass, self.config_entry).ble.get(source.get("id"))
            name = label(sensor) if sensor else source.get("id")
            return f"Bluetooth {name}" if name == source.get("id") else f"Bluetooth {name} ({source.get('id')})"
        # A Home Assistant source by the name the user knows it by; its entity ID without one.
        state = self.hass.states.get(str(source.get("id")))
        name = state.attributes.get("friendly_name") if state is not None else None
        return name if type(name) is str and name.strip() else str(source.get("id"))

    def _e32_room_list(self, plan, texts):
        """One line per room; ``texts``: selector.e32_room_list_text in the user's language (async_flow_texts)."""
        lines = []
        for room in plan["rooms"]:
            # E32 1.3: a room on Heat along only says so (an older text table: English, async_flow_texts).
            inactive = ("" if room.get("state") == "active" else f" ({texts['follow']})" if room.get("state") == "follow"
                        else f" ({texts['inactive']})")
            sources = ", ".join(self._e32_source_label(s) for s in room.get("sources", []))
            contacts = len(room_contacts(self.config_entry, room["id"]))
            window = "; " + texts["contacts"].replace("{count}", str(contacts)) if contacts else ""
            lines.append(f"- {room.get('name', room['id'])}{inactive}: {sources}{window}")
        return "\n".join(lines) or texts["none"]

    async def async_step_e32_room_add(self, user_input=None):
        self._e32_room_id = None
        return await self.async_step_e32_room()

    async def async_step_e32_room_pick(self, user_input=None):
        rooms = self._e32_plan["rooms"]
        if user_input is not None:
            if user_input.get("room") not in {r["id"] for r in rooms}:
                return self.async_abort(reason="e32_room_missing", description_placeholders={
                    "room": str(user_input.get("room"))})
            self._e32_room_id = user_input["room"]
            if user_input.get("action") == "remove":
                return await self.async_step_e32_room_remove()
            # rc.3: the radiator valves are a section of the room form itself (one room, one place).
            return await self.async_step_e32_room()
        return self.async_show_form(step_id="e32_room_pick", data_schema=vol.Schema({
            vol.Required("room", default=rooms[0]["id"]): selector.SelectSelector({"options": [
                {"value": r["id"], "label": r.get("name", r["id"])} for r in rooms]}),
            vol.Required("action", default="edit"): selector.SelectSelector({
                "options": ["edit", "remove"], "translation_key": "e32_room_action"}),
        }))

    def _boiler_maximum(self):
        """The boiler's own maximum heating temperature (°C) when it reports one, else None.

        On some boilers a knob (read-only, the boiler reports its position), on
        others a menu setting; it is the real ceiling either way.
        """
        state = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id, {})
        client = getattr(state.get("v1_connection"), "client", None)
        if client is None:
            return None
        from .heating_advice import boiler_maximum
        return boiler_maximum(client)

    async def async_step_e32_flow_limits(self, user_input=None):
        """The plan's minimum/maximum flow temperature (whole °C, 20–79 / 21–80, minimum below maximum).
        Smart warm-up and Weather compensation have their own steps (options_house_heating.py).

        Shown and entered in the Home Assistant unit. A maximum above 50 °C with
        floor heating, or above the boiler's own maximum, is saved only after a
        second confirming save (a warning, not a block: the boiler caps anyway).
        The options are written first (their own record on the E32), then the limits.
        """
        plan = self._e32_plan  # read when the form opened: what it shows
        unit = self._unit()
        current = {key: plan.get(key) for key in FLOW_LIMIT_FIELDS.values()}
        tick = type(plan.get(MINIMUM_AUTOMATIC_KEY)) is bool  # plan item 1: an E32 that has the choice
        if tick:
            current[MINIMUM_AUTOMATIC_KEY] = plan[MINIMUM_AUTOMATIC_KEY]
        boiler = self._boiler_maximum()
        errors, placeholders = {}, {"error": "", "boiler": "", **self._flow_ranges(unit), "minimum_now": ""}
        from .heating_advice import language
        if boiler is not None:
            placeholders["boiler"] = BOILER_MAXIMUM_TEXT[language(self.hass)].format(
                maximum=f"{flow_shown(boiler, unit):g} {unit}")
        now = minimum_flow_now(getattr(getattr(self._e32_link(), "hub", None), "summary", None)) if tick else None
        if now is not None:
            placeholders["minimum_now"] = MINIMUM_NOW_TEXT[language(self.hass)][now[1]].format(
                value=f"{flow_shown(round(now[0]), unit):g} {unit}")
        if user_input is not None:
            # Plan item 1b: only what the user changed in this form goes to the E32 (against what it showed),
            # so a limit changed on the E32's own page while the form was open stays. 1.4: the same check as the
            # settings panel (e32_flow.limit_edits, limit_warnings).
            from .e32_flow import limit_edits, limit_warnings
            try:
                edits, low, high = limit_edits(plan, user_input.get(MINIMUM_AUTOMATIC_FIELD),
                                               user_input.get("minimum_flow_temperature"),
                                               user_input.get("maximum_flow_temperature"), unit)
            except FlowError as err:
                errors["base"] = err.key
            else:
                if not edits:
                    return self.async_abort(reason="e32_room_unchanged")
                warnings = limit_warnings(plan, high, boiler)
                if warnings and getattr(self, "_e32_flow_warned", None) != (low, high):
                    self._e32_flow_warned = (low, high)  # the same values once more: save
                    errors.update(warnings)
                else:
                    return await self._e32_save_flow_limits(edits, errors, placeholders, current)
        return self._e32_flow_form(current, unit, user_input, errors, placeholders)

    @staticmethod
    def _flow_ranges(unit):
        def span(bounds):
            return f"{flow_shown(bounds[0], unit)}–{flow_shown(bounds[1], unit)} {unit}"
        return {"minimum_range": span(FLOW_MINIMUM_C), "maximum_range": span(FLOW_MAXIMUM_C),
                "floor_maximum": f"{flow_shown(FLOOR_FLOW_WARNING_C, unit)} {unit}"}

    async def _e32_save_flow_limits(self, edits, errors, placeholders, current):
        """Writes only ``edits`` (the fields the user changed) on top of the plan the E32 holds now (1.4: the same write
        as the settings panel, e32_flow.async_save_limits)."""
        from .e32_flow import async_save_limits
        link = self._e32_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        try:
            stored = await async_save_limits(link, edits)
        except HomeAssistantError as err:
            key, extra = self._e32_failure(err)
            if key in ABORTS:
                return self.async_abort(reason=key, description_placeholders={"room": "", **extra})
            errors["base"] = key
            placeholders.update(extra)
            return self._e32_flow_form({**current, **edits}, self._unit(), None, errors, placeholders)
        unit = self._unit()
        stored = stored if type(stored) is dict else {**current, **edits}
        low, high = stored.get("minimum_flow_c"), stored.get("maximum_flow_c")
        return self.async_abort(reason="e32_flow_limits_saved", description_placeholders={
            "minimum": f"{flow_shown(low, unit)}", "maximum": f"{flow_shown(high, unit)}", "unit": unit})

    def _e32_flow_form(self, current, unit, user_input, errors, placeholders):
        default = {"minimum_flow_temperature": current["minimum_flow_c"], "maximum_flow_temperature":
                   current["maximum_flow_c"]}
        for field, fallback in (("minimum_flow_temperature", 30), ("maximum_flow_temperature", 60)):
            if type(default[field]) not in (int, float) or type(default[field]) is bool:
                default[field] = fallback
        fields = {}
        if type(current.get(MINIMUM_AUTOMATIC_KEY)) is bool:  # plan item 1: the tick first, the value under it
            fields[vol.Required(MINIMUM_AUTOMATIC_FIELD, default=current[MINIMUM_AUTOMATIC_KEY])] = \
                selector.BooleanSelector()
        for field, (low, high) in (("minimum_flow_temperature", FLOW_MINIMUM_C),
                                   ("maximum_flow_temperature", FLOW_MAXIMUM_C)):
            fields[vol.Required(field, default=flow_shown(default[field], unit))] = selector.NumberSelector({
                "min": flow_shown(low, unit), "max": flow_shown(high, unit), "step": 1, "mode": "box",
                "unit_of_measurement": unit})
        return self.async_show_form(step_id="e32_flow_limits", data_schema=retained_input_schema(
            self, vol.Schema(fields), user_input), errors=errors, description_placeholders=placeholders)

    async def async_step_e32_room_remove(self, user_input=None):
        room_id = self._e32_room_id
        room = plan_room(self._e32_plan, room_id)
        if room is None:
            return self.async_abort(reason="e32_room_missing", description_placeholders={"room": room_id})
        errors, placeholders = {}, {"name": room.get("name", room_id), "error": ""}
        if user_input is not None:
            if not user_input.get("confirm_remove", False):
                return self.async_abort(reason="cancelled")
            link = self._e32_link()
            if link is None:
                return self.async_abort(reason="e32_rooms_unavailable")
            try:
                await remove_room(self.hass, self.config_entry, link, room_id)  # shared with the settings panel
            except HomeAssistantError as err:
                key, extra = self._e32_failure(err)
                if key in ABORTS:
                    return self.async_abort(reason=key, description_placeholders={**placeholders, **extra})
                errors["base"] = key
                placeholders.update(extra)
            else:  # the E32 confirmed a plan without it (or the plan just read no longer had it)
                return await self.async_step_e32_rooms(done="removed", name=placeholders["name"])
        return self.async_show_form(step_id="e32_room_remove", data_schema=vol.Schema({
            vol.Required("confirm_remove", default=False): bool}),
            errors=errors, description_placeholders=placeholders)

    # -- radiator valves: a section of the room form (rc.3) ------------------------------------

    async def _e32_read_valves(self):
        """(the E32's valve record, its BLU Gateway valves or None), or (None, None) (read_valves)."""
        return await read_valves(self.hass, self.config_entry)

    def _e32_valve_context(self, config, room_id, room, gateway=None):
        return valve_context(self.hass, self.config_entry, config, room_id, room, gateway)

    def _e32_gateway_option(self, ctx, name):
        """One BLU Gateway valve in the picker: its name on the gateway and which gateway, its battery."""
        from .e32_valves import shown_name
        from .valve_routes import language_of
        valve = ctx.gateway_labels.get(name) or {}
        stored = next((r for r in ctx.gateway_stored if r.name == name), None)
        text = valve.get("label") or (stored.friendly if stored else None) or shown_name(name, language_of(self))
        details = [d for d in (valve.get("gateway"), f"{valve['battery']:g} %" if "battery" in valve else None) if d]
        return {"value": name, "label": f"{text} ({', '.join(details)})" if details else text}

    def _e32_valve_fields(self, ctx):
        """The valves section: just the climate entities; the route per valve is decided by valve_routes."""
        from .valve_routes import MODEL_NAMES
        chosen = [r.entity_id for r in ctx.stored if r.entity_id]
        kept = [r for r in ctx.stored if r.entity_id is None]
        climate = {"filter": [{"domain": "climate"}], "multiple": True}
        if ctx.excluded:
            climate["exclude_entities"] = ctx.excluded
        fields = {vol.Optional("valves", description={"suggested_value": chosen or None}): selector.EntitySelector(climate)}
        if kept:  # stored Zigbee2MQTT valves Home Assistant does not know: kept unless deselected here
            fields[vol.Optional("kept", description={"suggested_value": [r.name for r in kept]})] = selector.SelectSelector({
                "options": [{"value": r.name, "label": f"{r.name} ({MODEL_NAMES.get(r.model, r.model)})"} for r in kept],
                "multiple": True})
        if ctx.gateway_options:  # E32 1.1: the BLU Gateway's valves, their role and keep open
            options = [self._e32_gateway_option(ctx, name) for name in ctx.gateway_options]
            for field, chosen in (("gateway_valves", [r.name for r in ctx.gateway_stored]),
                                  ("loop_valves", [r.name for r in ctx.gateway_stored if r.role == "loop"]),
                                  ("keep_open", [r.name for r in ctx.gateway_stored if r.keep_open])):
                fields[vol.Optional(field, description={"suggested_value": chosen or None})] = selector.SelectSelector(
                    {"options": options, "multiple": True})
        fields[vol.Optional("control", default=ctx.control)] = bool
        fields[vol.Optional("choose_models", default=False)] = bool
        return fields

    def _e32_submitted_valves(self, user_input, ctx, models=None):
        """(routes, control) of the valves section, or None when the form has none (submitted_valves)."""
        return submitted_valves(user_input.get("valves"), ctx, models)

    def _e32_model_candidates(self, user_input, ctx):
        """[(entity, friendly name, detected model, device text)] of the chosen Zigbee2MQTT valves."""
        return model_candidates((user_input or {}).get("valves"), ctx)

    @staticmethod
    def _e32_valve_pins(ctx, models):
        """The "Through Home Assistant" choices after this save (valve_pins)."""
        return valve_pins(ctx, models)

    def _e32_wants_models(self, user_input, ctx):
        """Advanced ticked with a Zigbee2MQTT valve chosen (then its models are chosen first)."""
        part = user_input.get("valves")
        return type(part) is dict and bool(part.get("choose_models")) and bool(self._e32_model_candidates(user_input, ctx))

    def _e32_valve_routes(self, routes):
        """Each valve's route in plain words (the valves field's description)."""
        from .valve_routes import language_of, route_lines
        return route_lines(self.hass, routes, language_of(self))

    def _e32_saved_valves(self, valves):
        """After a save: the room's valves and their route, for the room list ("" without a valves section)."""
        from .valve_routes import ROUTE_HEADING, language_of
        if not valves or not valves[0]:
            return ""
        return f"\n\n{ROUTE_HEADING[language_of(self)]}\n{self._e32_valve_routes(valves[0])}"

    async def async_step_e32_room_valve_models(self, user_input=None):
        """Advanced: per Zigbee2MQTT valve its model (the E32 drives it) or Home Assistant (always works).

        Shown only when "Choose the models myself" was ticked; then the room is saved as submitted.
        """
        from .e32_valves import HA_MODEL, ZIGBEE_MODELS
        pending = getattr(self, "_e32_pending", None)
        state = getattr(self, "_e32_valve_state", None)
        if pending is None or state is None or state[1] is None or state[0] != getattr(self, "_e32_room_id", None):
            return self.async_abort(reason="e32_room_missing", description_placeholders={"room": ""})
        ctx = state[1]
        candidates = self._e32_model_candidates(pending, ctx)
        stored = {r.entity_id: r for r in ctx.stored if r.entity_id}
        errors = {}
        if user_input is not None:
            models = {}
            for k, (entity_id, *_rest) in enumerate(candidates, 1):
                model = user_input.get(f"model_{k}")
                if model not in (HA_MODEL, *ZIGBEE_MODELS):
                    errors[f"model_{k}"] = "e32_valve_model_missing"
                models[entity_id] = model
            if not errors:
                self._e32_valve_models = models
                return await self.async_step_e32_room(pending, models_chosen=True)
        from .valve_routes import model_choice_text
        fields, placeholders = {}, {"name": "", "error": "", **{f"valve_{k}": "" for k in range(1, MAX_VALVE_MODELS + 1)}}
        room = plan_room(self._e32_plan, ctx.room_id) if ctx.room_id else None
        placeholders["name"] = (room or {}).get("name") or str(pending.get("name") or "")
        for k, (entity_id, friendly, detected, text) in enumerate(candidates, 1):
            current = self._e32_valve_models.get(entity_id)
            if current is None:
                current = stored[entity_id].model if entity_id in stored else (detected or HA_MODEL)
            fields[vol.Required(f"model_{k}", default=current)] = selector.SelectSelector(
                {"options": [HA_MODEL, *ZIGBEE_MODELS], "translation_key": "e32_valve_model"})
            placeholders[f"valve_{k}"] = model_choice_text(self.hass, entity_id, friendly, text)
        return self.async_show_form(step_id="e32_room_valve_models", data_schema=vol.Schema(fields),
                                    errors=errors, description_placeholders=placeholders)

    def _e32_forget_room(self, room_id):
        """The room is gone from the E32 plan: remove its device and entities (this entry's only)."""
        forget_room(self.hass, self.config_entry, room_id)

    def _e32_own_entities(self):
        """This entry's E32 entities (room and Bluetooth values): never an HA source.

        The E32 already has them; its Bluetooth sensors are chosen as such.
        """
        prefix = self.config_entry.data.get(CONF_TOPIC_PREFIX, "") + "_e32_"
        return [item.entity_id for item in er.async_entries_for_config_entry(
            er.async_get(self.hass), self.config_entry.entry_id) if item.unique_id.startswith(prefix)]

    def _e32_ble_options(self, room):
        sensors = heating_hub(self.hass, self.config_entry).ble
        options = []
        for sensor_id, sensor in sensors.items():
            text = label(sensor)
            text = sensor_id if text == sensor_id else f"{text} ({sensor_id})"
            temperature = number(sensor.get("temperature"), -40, 85)
            options.append({"value": sensor_id, "label": text if temperature is None else f"{text} {temperature:g} °C"})
        for source in (room or {}).get("sources", []):
            if source.get("type") == "ble" and source.get("id") not in sensors:
                options.append({"value": source["id"], "label": source["id"]})
        return options

    def _e32_defaults(self, room):
        room = room or {}
        sources = room.get("sources", [])
        unit = self._unit()
        # Issue #7: a room shows the program it has (empty: none). Only a new room starts from the standard
        # program "Workdays and weekend", shown in the field, so it is a choice the user sees and can clear.
        schedule = room.get("schedule") if room.get("id") else default_program(
            room.get("minimum_centi_c", 500), room.get("maximum_centi_c", 3000))
        return {
            "name": room.get("name", ""), "state": room.get("state", "active"),
            "emitter": room.get("emitter", "radiator"),
            # "Off until": local time of the room's end of inactivity (None: no end set).
            "inactive_until": None if (until := until_datetime(room)) is None else dt_util.as_local(until).strftime(
                "%Y-%m-%d %H:%M:%S"),
            "ha_sources": [s["id"] for s in sources if s.get("type") == "ha"],
            "ble_sources": [s["id"] for s in sources if s.get("type") == "ble"],
            # Windows: every contact that is no door (also all contacts chosen before 1.0.1); doors their own.
            "contacts": [e for e in room_contacts(self.config_entry, room["id"])
                         if e not in room_doors(self.config_entry, room["id"])] if room.get("id") else [],
            "door_contacts": room_doors(self.config_entry, room["id"]) if room.get("id") else [],
            "persons": room_persons(self.config_entry, room["id"]) if room.get("id") else [],
            # The room's own away temperature (plan.room_away.v1); None: the house value.
            "away_temperature": None if room_away.room_away(room) is None else shown(room_away.room_away(room), unit),
            # The room's own pause delays in minutes: windows (beta.23; default 2 min), doors (1.0.1; default 5 min).
            "contact_delay": room_contact_delay(comfort_options(self.config_entry), room.get("id") or "") / 60,
            "door_delay": room_door_delay(comfort_options(self.config_entry), room.get("id") or "") / 60,
            "bluetooth_first": bool(sources) and sources[0].get("type") == "ble",
            # The setting device as stored, never pre-selected: Home Assistant writes its
            # target at every switch point, so the user picks it (a climate source is only hinted).
            "setpoint_entity": room.get("setpoint_entity") or None,
            "fallback_temperature": shown(room.get("fallback_centi_c", 2000), unit),
            "minimum_temperature": shown(room.get("minimum_centi_c", 500), unit),
            "maximum_temperature": shown(room.get("maximum_centi_c", 2500), unit),
            "program": format_program(schedule, self.hass.config.language, unit),
            # E32 1.4: the room's reset times, one per line ("" without any, or on older firmware).
            "resets": format_resets(room.get("resets"), self.hass.config.language, unit),
        }

    def _e32_centi(self, value, field, defaults, room):
        """A submitted temperature as centi-°C; the value as shown keeps the stored one exactly."""
        stored = room.get({"fallback_temperature": "fallback_centi_c", "minimum_temperature": "minimum_centi_c",
                           "maximum_temperature": "maximum_centi_c"}[field])
        try:
            same = type(stored) is int and float(value) == float(defaults[field])
        except (TypeError, ValueError):
            same = False
        return stored if same else centi(value, self._unit())

    def _e32_room_values(self, user_input, room, ble_options):
        """The submitted room as plan fields; raises FlowError for the first problem."""
        room = room or {}
        defaults = self._e32_defaults(room)
        name = valid_name(user_input.get("name"))
        state, emitter = user_input.get("state"), user_input.get("emitter")
        if state not in self._e32_states(room) or emitter not in ("floor", "radiator"):
            raise FlowError("e32_rejected", error="invalid_room")
        known = {(s.get("type"), s.get("id")) for s in room.get("sources", [])}
        ha, ble = [], []
        for entity_id in user_input.get("ha_sources") or []:
            if entity_id not in ha:
                if ("ha", entity_id) not in known and (problem := source_problem(self.hass, entity_id)):
                    raise FlowError(problem, "ha_sources", source=entity_id)
                ha.append(entity_id)
        offered = {option["value"] for option in ble_options}
        for sensor_id in user_input.get("ble_sources") or []:
            if sensor_id not in offered and sensor_id not in ble:
                raise FlowError("e32_rejected", "ble_sources", error="invalid_sources")
            if sensor_id not in ble:
                ble.append(sensor_id)
        if not 1 <= len(ha) + len(ble) <= MAX_SOURCES:
            raise FlowError("e32_sources_count")
        first = user_input.get("bluetooth_first", defaults["bluetooth_first"])
        if (ha, ble, first) == (defaults["ha_sources"], defaults["ble_sources"], defaults["bluetooth_first"]):
            sources = deepcopy(room.get("sources", []))  # untouched: keep the stored order exactly
        else:
            ha_sources = [{"type": "ha", "id": e} for e in ha]
            ble_sources = [{"type": "ble", "id": b} for b in ble]
            sources = ble_sources + ha_sources if first else ha_sources + ble_sources
        setpoint = user_input.get("setpoint_entity") or ""
        if setpoint and setpoint != room.get("setpoint_entity") and (
                problem := source_problem(self.hass, setpoint, setpoint=True)):
            raise FlowError(problem, "setpoint_entity", source=setpoint)
        limits = user_input.get("limits") or {}
        try:
            low = self._e32_centi(limits.get("minimum_temperature", defaults["minimum_temperature"]),
                                  "minimum_temperature", defaults, room)
            high = self._e32_centi(limits.get("maximum_temperature", defaults["maximum_temperature"]),
                                   "maximum_temperature", defaults, room)
            fallback = self._e32_centi(user_input.get("fallback_temperature", defaults["fallback_temperature"]),
                                       "fallback_temperature", defaults, room)
        except FlowError:
            raise FlowError("e32_limits_invalid", "fallback_temperature", **self._limit_range()) from None
        if not LIMITS_CENTI_C[0] <= low <= high <= LIMITS_CENTI_C[1] or not low <= fallback <= high:
            raise FlowError("e32_limits_invalid", "fallback_temperature", **self._limit_range())
        text = user_input.get("program") or ""
        stored = room.get("schedule")
        if stored and text.strip() == defaults["program"].strip() and all(
                low <= point[1] <= high for day in stored for point in day):
            schedule = deepcopy(stored)  # the program as shown: kept exactly (no °F rounding)
        else:
            schedule = parse_program(text, low, high, self._unit())
        # Issue #7: an empty field is no program; the room keeps its temperature without a week program (None:
        # an edit drops the stored program, a new room is added without one).
        values = {"name": name, "state": state, "emitter": emitter, "sources": sources,
                  "setpoint_entity": setpoint, "fallback_centi_c": fallback,
                  "minimum_centi_c": low, "maximum_centi_c": high, "schedule": schedule or None,
                  "inactive_until": self._e32_inactive_until(user_input, state, room)}
        if self._e32_away_supported():  # an older E32 ignores the field: not offered, not sent
            values[room_away.FIELD] = self._e32_room_away(user_input, room, defaults)
        if SMART_WARM_UP_FEATURE in ((getattr(self, "_e32_plan", None) or {}).get("features") or []):
            # E32 1.4 (#8): Smart warm-up for this room; "house" (the default) is a room without the key (None: removed).
            choice = user_input.get(SMART_WARM_UP_FIELD)
            values[SMART_WARM_UP_FIELD] = choice if choice in ("on", "off") else None
        if self._e32_resets_supported():  # E32 1.4: always sent (also []); never to older firmware
            values["resets"] = self._e32_resets(user_input, room, defaults, low, high)
        return values

    def _e32_resets_supported(self):
        return resets_supported(getattr(self, "_e32_plan", None))

    def _e32_resets(self, user_input, room, defaults, low, high):
        """The submitted reset times in the plan's form; the text as shown keeps the stored ones exactly.

        The settings panel sends them as a list (settings_rooms.py): each one checked by the same rules."""
        if type(user_input.get("resets")) is list:
            return valid_resets(user_input["resets"], low, high, self._unit(), room.get("resets"))
        text = user_input.get("resets") or ""
        stored = room.get("resets")

        def within(reset):
            temperature = reset.get("temperature_c") if type(reset) is dict else None
            return type(temperature) not in (int, float) or low <= round(temperature * 100) <= high
        if type(stored) is list and text.strip() == defaults["resets"].strip() and all(map(within, stored)):
            return deepcopy(stored)  # as shown: kept exactly (no °F rounding)
        return parse_resets(text, low, high, self._unit())

    def _e32_language(self):
        """The user's language when the flow context carries it, Home Assistant's own otherwise: en, nl or pl."""
        language = ((getattr(self, "context", None) or {}).get("language") or self.hass.config.language or "en")[:2]
        return language if language in ("en", "nl", "pl") else "en"

    def _e32_saved_program(self, values):
        """After a save: the room's week program and reset times as saved, for the room list (issue #7)."""
        language, unit = self._e32_language(), self._unit()
        words, written = SAVED_PROGRAM_TEXT[language], "nl" if language == "nl" else "en"
        program = format_program(values.get("schedule"), written, unit)
        if program:
            lines = [words["program"], *(f"- {line}" for line in program.splitlines())]
        else:
            temperature = f"{shown(values['fallback_centi_c'], unit):g}"
            temperature = temperature.replace(".", ",") if language == "nl" else temperature
            lines = [words["none"].format(temperature=f"{temperature} {unit}")]
        resets = format_resets(values.get("resets"), written, unit)
        if resets:
            lines += ["", words["resets"], *(f"- {line}" for line in resets.splitlines())]
        return "\n\n" + "\n".join(lines)

    def _e32_inactive_until(self, user_input, state, room):
        """The submitted "Off until" as epoch seconds; 0 (no end) when blank or the room heats."""
        text = user_input.get("inactive_until")
        if state != "inactive" or text is None or not str(text).strip():
            return 0
        parsed = dt_util.parse_datetime(str(text).strip().replace("T", " ", 1))
        if parsed is None:
            raise FlowError("e32_inactive_until_invalid", "inactive_until")
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
        until = int(parsed.timestamp())
        if until == room.get("inactive_until") and until <= LATEST_UNTIL:
            return until  # as shown: kept, even when it has just passed
        if until <= dt_util.utcnow().timestamp() or until > LATEST_UNTIL:
            raise FlowError("e32_inactive_until_invalid", "inactive_until")
        return until

    def _e32_away_supported(self):
        return room_away.supported(getattr(self, "_e32_plan", None))

    def _e32_states(self, room):
        """The room states the form offers: E32 1.3's "follow" (Heat along only) only for an E32 that names it
        (plan.room_follow.v1; older firmware refuses the state), or for a room already on it."""
        if follows(getattr(self, "_e32_plan", None)) or (room or {}).get("state") == "follow":
            return ["active", "follow", "inactive"]
        return ["active", "inactive"]

    def _e32_room_away(self, user_input, room, defaults):
        """The submitted own away temperature (the form's "persons" section) as centi-°C; None: the house value."""
        value = (user_input.get("persons") or {}).get("away_temperature")
        if value is None or type(value) is str and not value.strip():
            return None
        stored = room_away.room_away(room)
        try:
            if stored is not None and float(value) == float(defaults["away_temperature"]):
                return stored  # as shown: kept exactly (no °F rounding)
        except (TypeError, ValueError):
            pass
        try:
            centi_c = centi(value, self._unit())
        except FlowError:
            raise FlowError("e32_away_invalid", "persons", **self._away_range()) from None
        if not room_away.LIMITS_CENTI_C[0] <= centi_c <= room_away.LIMITS_CENTI_C[1]:
            raise FlowError("e32_away_invalid", "persons", **self._away_range())
        return centi_c

    def _away_range(self):
        unit = self._unit()
        low, high = room_away.LIMITS_CENTI_C
        return {"away_range": f"{shown(low, unit):g}–{shown(high, unit):g} {unit}"}

    def _e32_house_away(self):
        """The house away temperature as the form shows it ("15 °C"), from the E32's status."""
        from .e32_house import house_away
        unit = self._unit()
        away = house_away(heating_hub(self.hass, self.config_entry)) or {}
        value = number(away.get("target_c"), 5, 25)
        value = 15.0 if value is None else value
        return f"{shown(round(value * 100), unit):g} {unit}"

    def _limit_range(self):
        unit = self._unit()
        low, high = LIMITS_CENTI_C
        return {"range": f"{shown(low, unit):g}–{shown(high, unit):g} {unit}"}

    async def async_step_e32_room(self, user_input=None, models_chosen=False):
        room_id = getattr(self, "_e32_room_id", None)
        room = plan_room(self._e32_plan, room_id) if room_id else None
        if room_id and room is None:
            return self.async_abort(reason="e32_room_missing", description_placeholders={"room": room_id})
        ble_options = self._e32_ble_options(room)
        errors = {}
        placeholders = {"source": "", "error": "", "line": "", "text": "", **self._limit_range(), **self._away_range(),
                        "delay": contact_delay_text(comfort_options(self.config_entry), room_id),
                        "door_delay": contact_delay_text(comfort_options(self.config_entry), room_id, door=True),
                        "house_away": self._e32_house_away()}
        link = self._e32_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        valve_state = getattr(self, "_e32_valve_state", None)
        if user_input is None or valve_state is None or valve_state[0] != room_id:
            # Read when the form opens: the valves section shows what the E32 stores now.
            config, gateway = await self._e32_read_valves()
            valve_state = self._e32_valve_state = (
                room_id, self._e32_valve_context(config, room_id, room, gateway) if config else None)
            self._e32_valve_models = {}
        valve_ctx = valve_state[1]
        placeholders["valve_routes"] = self._e32_valve_routes(
            [*valve_ctx.stored, *valve_ctx.gateway_stored] if valve_ctx else [])
        placeholders["resets_note"] = "" if self._e32_resets_supported() else RESETS_LATER_TEXT[self._e32_language()]
        if user_input is not None:
            try:
                values = self._e32_room_values(user_input, room, ble_options)
                # The contacts, persons and valves of the room: checked as the panel checks them (room_parts).
                parts = room_parts(self.hass, self.config_entry, room, user_input, valve_ctx, self._e32_valve_models)
                valves = parts.valves
                if valves is not None:
                    placeholders["valve_routes"] = self._e32_valve_routes(valves[0])
                if not models_chosen and self._e32_wants_models(user_input, valve_ctx):
                    self._e32_pending = user_input  # Advanced: the models first, then this same save
                    return await self.async_step_e32_room_valve_models()
                if room is not None and not room_edits(room, values) and parts.unchanged(self.config_entry, room_id):
                    return self.async_abort(reason="e32_room_unchanged")
                # Shared with the settings panel (settings_rooms.py): the plan (only the changed fields, on top of the
                # plan the E32 holds now; a new room gets its id there), then the valves, the contacts and the persons.
                await save_room(self.hass, self.config_entry, link, room, values, parts)
            except FlowError as err:
                if getattr(err, "saved", None) is not None:
                    # The room is stored, its valves refused: the same form now edits it, so saving again only retries
                    # the valves.
                    self._e32_room_id = err.saved
                    if getattr(link, "plan", None) is not None:
                        self._e32_plan = link.plan
                if err.key in ABORTS:
                    return self.async_abort(reason=err.key, description_placeholders={"room": room_id or ""})
                errors[err.field] = err.key
                placeholders.update(err.placeholders)
            except HomeAssistantError as err:
                key, extra = self._e32_failure(err)
                if key in ABORTS:
                    return self.async_abort(reason=key, description_placeholders={"room": room_id or "", **extra})
                errors["base"] = key
                placeholders.update(extra)
            else:
                return await self.async_step_e32_rooms(done="saved", name=values["name"],
                                                       valves=self._e32_saved_valves(valves),
                                                       program=self._e32_saved_program(values))
        if getattr(self, "_e32_room_id", None) != room_id:  # a new room stored, its valves refused: edit it now
            room = plan_room(self._e32_plan, self._e32_room_id)
        placeholders["setting_hint"] = self._e32_setting_hint(room, user_input)
        # The title says which room (or that it is a new one).
        placeholders["room_name"] = room.get("name", room_id) if room else NEW_ROOM_TITLE[self._e32_language()]
        return self.async_show_form(step_id="e32_room", data_schema=retained_input_schema(
            self, self._e32_room_schema(room, ble_options, valve_ctx), user_input),
            errors=errors, description_placeholders=placeholders)

    def _e32_setting_hint(self, room, user_input):
        """A climate source that could set this room, as a question; never a pre-selection."""
        if user_input is not None:  # the form shown again: the sources as just submitted
            room = {"setpoint_entity": user_input.get("setpoint_entity") or "",
                    "sources": [{"type": "ha", "id": e} for e in user_input.get("ha_sources") or []]}
        # The user's language when the flow context carries it; Home Assistant's own otherwise
        # (a flow is not told the browser's language). The texts: EN, NL and PL.
        language = (getattr(self, "context", None) or {}).get("language") or self.hass.config.language
        return setting_hint(proposed_device(room), language)

    def _e32_room_schema(self, room, ble_options, valve_ctx=None):
        d = self._e32_defaults(room)
        own = self._e32_own_entities()
        unit = self._unit()
        low, high = (shown(limit, unit) for limit in LIMITS_CENTI_C)
        temperature = selector.NumberSelector({"min": low, "max": high, "step": 0.5 if unit == CELSIUS else 0.1,
                                               "mode": "box", "unit_of_measurement": unit})
        sources = {"filter": [{"domain": "climate"}, {"domain": "sensor", "device_class": "temperature"}],
                   "multiple": True, "reorder": True}
        delay_minutes = selector.NumberSelector({"min": DELAY_LIMITS[0] / 60, "max": DELAY_LIMITS[1] / 60, "step": 0.5,
                                                 "mode": "box", "unit_of_measurement": "min"})
        persons = {vol.Optional("persons", description={"suggested_value": d["persons"] or None}): persons_selector()}
        if self._e32_away_supported():
            away_low, away_high = (shown(limit, unit) for limit in room_away.LIMITS_CENTI_C)
            persons[vol.Optional("away_temperature", description={"suggested_value": d["away_temperature"]})] = (
                selector.NumberSelector({"min": away_low, "max": away_high, "step": 0.5 if unit == CELSIUS else 0.1,
                                         "mode": "box", "unit_of_measurement": unit}))
        if own:
            sources["exclude_entities"] = own
        fields = {
            vol.Required("name", default=d["name"]): str,
            vol.Required("state", default=d["state"]): selector.SelectSelector({
                "options": self._e32_states(room), "translation_key": "e32_room_state"}),
            vol.Optional("inactive_until", description={"suggested_value": d["inactive_until"]}):
                selector.DateTimeSelector(),
            vol.Required("emitter", default=d["emitter"]): selector.SelectSelector({
                "options": ["radiator", "floor"], "translation_key": "e32_room_emitter"}),
            vol.Optional("ha_sources", description={"suggested_value": d["ha_sources"]}):
                selector.EntitySelector(sources),
        }
        if ble_options:
            fields[vol.Optional("ble_sources", description={"suggested_value": d["ble_sources"]})] = \
                selector.SelectSelector({"options": ble_options, "multiple": True})
            fields[vol.Optional("bluetooth_first", default=d["bluetooth_first"])] = bool
        fields.update({
            vol.Optional("setpoint_entity", description={"suggested_value": d["setpoint_entity"]}):
                selector.EntitySelector({"filter": [{"domain": domain} for domain in SETPOINT_DOMAINS]}),
            vol.Required("fallback_temperature", default=d["fallback_temperature"]): temperature,
            vol.Optional("program", description={"suggested_value": d["program"] or None}):
                selector.TextSelector({"multiline": True}),
        })
        if self._e32_resets_supported():  # E32 1.4: the room's reset times, right under its week program
            fields[vol.Optional("resets", description={"suggested_value": d["resets"] or None})] = \
                selector.TextSelector({"multiline": True})
        fields.update({
            # Open: easy to find in the room itself, not only under Comfort.
            # Windows and doors (1.0.1): each kind with its own delay; a door usually waits longer.
            vol.Optional("window"): section(vol.Schema({
                vol.Optional("contacts", description={"suggested_value": d["contacts"] or None}): contact_selector(),
                vol.Optional("contact_delay", default=d["contact_delay"]): delay_minutes,
                vol.Optional("door_contacts", description={"suggested_value": d["door_contacts"] or None}):
                    contact_selector(),
                vol.Optional("door_delay", default=d["door_delay"]): delay_minutes,
            }), {"collapsed": False}),
            # Persons per room (beta.23): empty = the room follows the house's presence. With
            # plan.room_away.v1 also the room's own away temperature (empty = the house value).
            vol.Optional("persons"): section(vol.Schema(persons), {
                "collapsed": not d["persons"] and d["away_temperature"] is None}),
            vol.Optional("limits"): section(vol.Schema({
                vol.Required("minimum_temperature", default=d["minimum_temperature"]): temperature,
                vol.Required("maximum_temperature", default=d["maximum_temperature"]): temperature,
            }), {"collapsed": True}),
        })
        if SMART_WARM_UP_FEATURE in ((getattr(self, "_e32_plan", None) or {}).get("features") or []):
            # E32 1.4 (#8): Smart warm-up for this room: as the house (the default), on or off.
            stored = (room or {}).get(SMART_WARM_UP_FIELD)
            fields[vol.Required(SMART_WARM_UP_FIELD, default=stored if stored in ("on", "off") else "house")] =                 selector.SelectSelector({"options": ["house", "on", "off"], "translation_key": "e32_smart_warm_up"})
        if valve_ctx is not None:  # rc.3: the room's radiator valves, in the room itself (open when it has some)
            fields[vol.Optional("valves")] = section(vol.Schema(self._e32_valve_fields(valve_ctx)),
                                                     {"collapsed": not (valve_ctx.stored or valve_ctx.gateway_stored)})
        return vol.Schema(fields)

    @staticmethod
    def _e32_edit(room_id, edits):
        def change(plan):
            candidate = deepcopy(plan)
            room = plan_room(candidate, room_id)
            if room is None:
                raise FlowError("e32_room_missing")
            for key, value in edits.items():
                if value is None:
                    room.pop(key, None)  # schedule cleared: fallback only
                else:
                    room[key] = deepcopy(value)
            if "state" in edits and "inactive_until" not in edits:
                room["inactive_until"] = 0
            return candidate
        return change, lambda stored: plan_room(stored, room_id) is not None

    @staticmethod
    def _e32_add(values, created=None):
        created = [] if created is None else created

        def change(plan):
            candidate = deepcopy(plan)
            if len(candidate["rooms"]) >= MAX_ROOMS:
                raise FlowError("e32_room_limit")
            room_id = unique_room_id(values["name"], {r["id"] for r in candidate["rooms"]})
            room = {"id": room_id, "name": values["name"], "state": values["state"], "inactive_until": 0,
                    **{k: deepcopy(v) for k, v in values.items()
                       if k not in ("name", "state") and v is not None}}
            candidate["rooms"].append(room)
            created[:] = [room_id]
            return candidate
        return change, lambda stored: bool(created) and plan_room(stored, created[0]) is not None


# -- the room rules without the form (1.4): shared by this flow and the settings panel (settings_rooms.py) ----------

def room_edits(room, values):
    """The plan fields of ``values`` that differ from the stored room: an edit sends only these."""
    return {k: v for k, v in values.items() if room.get(k, 0 if k == "inactive_until" else None) != v}


async def write_room(link, room, values):
    """Store one room in the E32 plan (RoomPlanLink.async_change_plan: the read revision, one re-read on 409) and
    return its id. An edit (``room``: the room as shown) sends only the fields that differ from it, on top of the
    plan the E32 holds now, so a change made meanwhile on the E32 page to another field or room stays; nothing is
    sent when nothing differs. A new room (``room`` None) gets its id from its name. Raises FlowError
    (e32_room_missing, e32_room_limit) or the link's HomeAssistantError."""
    if room is not None:
        edits = room_edits(room, values)
        if edits:
            await link.async_change_plan(*E32RoomFlow._e32_edit(room["id"], edits))
        return room["id"]
    created = []
    await link.async_change_plan(*E32RoomFlow._e32_add(values, created))
    return created[0]


def forget_room(hass, entry, room_id):
    """The room is gone from the E32 plan: its device and entities go (this entry's only), and its window and door
    contacts and its persons with them."""
    from .native_entity_cleanup import remove_room_devices
    remove_room_devices(hass, entry, heating_hub(hass, entry).prefix, [room_id])
    if room_contacts(entry, room_id) or room_persons(entry, room_id):
        settings = with_room_persons(comfort_options(entry), room_id, [])
        save_comfort(hass, entry, with_room_contacts(settings, room_id, []))


async def remove_room(hass, entry, link, room_id):
    """Remove a room from the E32 plan, then forget it in Home Assistant. A room the plan no longer has counts as
    removed. Raises the link's HomeAssistantError (nothing removed)."""
    def change(plan):
        if plan_room(plan, room_id) is None:
            raise FlowError("e32_room_missing")
        candidate = deepcopy(plan)
        candidate["rooms"] = [r for r in candidate["rooms"] if r["id"] != room_id]
        return candidate
    try:
        await link.async_change_plan(change, lambda stored: plan_room(stored, room_id) is None)
    except FlowError:  # the plan just read no longer has it
        pass
    forget_room(hass, entry, room_id)


# -- the room's contacts, persons and radiator valves (1.4.1): shared by the room form and the settings panel ----------
# (settings_rooms.py). They are not part of the E32 plan: the contacts and persons are this entry's comfort settings
# (e32_comfort.py), the valves the E32's valve record (e32_valves.ValveLink). The form and the panel check them with
# room_parts and write them with save_room, after the plan, so a new room exists before its valves.

def submitted_contacts(hass, entry, room, user_input):
    """The window and door contacts of the form's "window" section: (all of them, the doors); a contact the room
    has may be unavailable now. Raises FlowError (its code on the whole form, as the form shows it)."""
    window = user_input.get("window") or {}
    known = room_contacts(entry, room["id"]) if room else []
    try:
        return validate_kinds(validate_contacts(hass, list(window.get("contacts") or []), known),
                              validate_contacts(hass, list(window.get("door_contacts") or []), known))
    except ComfortError as err:
        raise FlowError(err.code) from None


def submitted_persons(hass, entry, room, user_input):
    """The persons of the form's "persons" section; a person the room has may be unavailable now. Raises FlowError."""
    known = room_persons(entry, room["id"]) if room else []
    try:
        return validate_room_persons(hass, list((user_input.get("persons") or {}).get("persons") or []), known)
    except ComfortError as err:
        raise FlowError(err.code, "persons") from None


def submitted_delay(user_input, field="contact_delay"):
    """The pause delay of the "window" section (field door_delay: the doors') in seconds (minutes in the form), or
    None when the form has none. Raises FlowError contact_delay_invalid."""
    minutes = (user_input.get("window") or {}).get(field)
    if minutes is None:
        return None
    seconds = round(float(minutes) * 60)
    if not DELAY_LIMITS[0] <= seconds <= DELAY_LIMITS[1]:
        raise FlowError("contact_delay_invalid", "window")
    return seconds


def same_delay(settings, room_id, delay, door=False):
    """The delay is what the room stores already (its own delay, or none for the house default)."""
    return own_contact_delay(settings, delay, door) == settings.get(
        "door_delays" if door else "contact_delays", {}).get(room_id)


def same_delays(settings, room_id, delay, door_delay):
    return ((delay is None or same_delay(settings, room_id, delay))
            and (door_delay is None or same_delay(settings, room_id, door_delay, True)))


async def read_valves(hass, entry):
    """(the E32's valve record, its BLU Gateway valves or None), or (None, None): firmware without valves (or not
    readable now) leaves them alone."""
    from .e32_valves import valve_link
    link = valve_link(hass, entry)
    if link is None:
        return None, None
    try:
        return await link.async_read_with_gateway()
    except HomeAssistantError:
        return None, None


def valve_context(hass, entry, config, room_id, room, gateway=None):
    """What the valves of one room need: the record, this room's stored valves as routes, the exclusions, and the BLU
    Gateway valves to choose from (E32 1.1; None without Shelly)."""
    from types import SimpleNamespace
    from .e32_valves import GATEWAY_MODEL, HA_MODEL
    from .valve_routes import RouteFinder, gateway_route, through_ha_choices
    current = next((r for r in config["rooms"] if room_id and r["room"] == room_id), {"control": False, "valves": []})
    finder = RouteFinder(hass, config["base_topic"])
    pins = through_ha_choices(entry)
    classic = [v for v in current["valves"] if v["model"] != GATEWAY_MODEL]
    # a Home Assistant valve the E32 can drive now: shown and saved so
    stored = finder.stored(classic, pins)
    others = [v for r in config["rooms"] if r["room"] != room_id for v in r["valves"]]
    # Never a valve of this room: OpenThermostat's own thermostats, the room's thermostat sources
    # and the valves of the other rooms (Home Assistant ones by entity, Zigbee2MQTT ones by name).
    own = [e.entity_id for e in er.async_get(hass).entities.values() if e.platform == DOMAIN and e.domain == "climate"]
    sources = [s["id"] for s in (room or {}).get("sources", [])
               if s.get("type") == "ha" and str(s.get("id", "")).startswith("climate.")]
    taken = [v["name"] if v["model"] == HA_MODEL else finder.index().get(v["name"])
             for v in others if v["model"] != GATEWAY_MODEL]
    mine = {r.entity_id for r in stored if r.entity_id}
    excluded = [e for e in dict.fromkeys(own + sources + taken) if e and e not in mine]
    # The BLU Gateway valves: this room's stored ones (also when the gateway no longer lists them, so they
    # can be kept or let go) and the gateway's valves no other room has.
    labels = {v["name"]: v for v in gateway or []}
    others_named = {v["name"] for v in others}
    gateway_stored = [gateway_route(v["name"], (labels.get(v["name"]) or {}).get("label"), v.get("role"),
                                    v.get("keep_open")) for v in current["valves"] if v["model"] == GATEWAY_MODEL]
    options = [r.name for r in gateway_stored] + [v["name"] for v in gateway or []
                                                  if v["name"] not in others_named
                                                  and v["name"] not in {r.name for r in gateway_stored}]
    # The order on the E32: each stored record's place (a route that moved to the E32 keeps its record's place).
    places = [k for k, v in enumerate(current["valves"]) if v["model"] != GATEWAY_MODEL]
    position = {route.name: places[k] for k, route in enumerate(stored)}
    position.update({v["name"]: k for k, v in enumerate(current["valves"]) if v["model"] == GATEWAY_MODEL})
    return SimpleNamespace(config=config, room_id=room_id, finder=finder, stored=stored, control=current["control"],
                           records=[dict(v) for v in current["valves"]], pins=pins, others=others, excluded=excluded,
                           gateway=gateway, gateway_stored=gateway_stored, gateway_options=options,
                           gateway_labels=labels, position=position)


def submitted_valves(part, ctx, models=None):
    """(routes, control) of the form's valves section ``part``, or None when there is none; raises FlowError.

    A valve stored before keeps its route and model; a new one gets the route its device allows; models: the
    Advanced choice per entity (HA_MODEL: through Home Assistant).
    """
    from .e32_valves import (MAX_CLASSIC_VALVES_PER_ROOM, MAX_VALVES, MAX_VALVES_PER_ROOM,
                             MAX_VALVES_WITHOUT_GATEWAY, valid_entity)
    from .valve_routes import gateway_route
    if ctx is None or type(part) is not dict:
        return None
    stored = {r.entity_id: r for r in ctx.stored if r.entity_id}
    kept = {r.name: r for r in ctx.stored if r.entity_id is None}
    routes = []
    for entity_id in dict.fromkeys(part.get("valves") or []):
        if models and entity_id in models:
            route = ctx.finder.route(entity_id, models[entity_id])
        else:
            route = stored.get(entity_id) or ctx.finder.route(entity_id)
        if not route.direct and (not valid_entity(entity_id) or entity_id in ctx.excluded):
            raise FlowError("e32_valve_entity_invalid", "valves")
        routes.append(route)
    routes += [kept[name] for name in dict.fromkeys(part.get("kept") or []) if name in kept]
    classic = len(routes)
    offered = set(getattr(ctx, "gateway_options", None) or [])
    chosen = [name for name in dict.fromkeys(part.get("gateway_valves") or []) if name in offered]
    loops = {name for name in part.get("loop_valves") or [] if name in chosen}
    keep = {name for name in part.get("keep_open") or [] if name in chosen}
    if loops & keep:
        raise FlowError("e32_valve_keep_open_loop", "valves")
    labels = {r.name: r.friendly for r in getattr(ctx, "gateway_stored", [])}
    labels.update({name: v.get("label") for name, v in (getattr(ctx, "gateway_labels", None) or {}).items()
                   if v.get("label")})
    routes += [gateway_route(name, labels.get(name), "loop" if name in loops else None, name in keep)
               for name in chosen]
    # The stored valves keep their order on the E32; new ones follow in the order chosen.
    position = getattr(ctx, "position", None) or {r.name: k for k, r in enumerate(ctx.stored)}
    routes = [r for _k, r in sorted(enumerate(routes), key=lambda item: (
        position.get(item[1].name, len(ctx.records) + len(ctx.stored)), item[0]))]
    names, taken = set(), {v["name"] for v in ctx.others}
    for route in routes:
        if route.name in names or route.name in taken:
            raise FlowError("e32_valve_duplicate", "valves")
        names.add(route.name)
    if len(routes) > MAX_VALVES_PER_ROOM or classic > MAX_CLASSIC_VALVES_PER_ROOM:
        raise FlowError("e32_valve_room_limit")
    # 24 on an E32 with the BLU Gateway (it lists its gateway valves, E32 1.1), 16 before.
    total = MAX_VALVES if getattr(ctx, "gateway", None) is not None else MAX_VALVES_WITHOUT_GATEWAY
    if len(ctx.others) + len(routes) > total:
        raise FlowError("e32_valve_limit")
    return routes, bool(part.get("control", ctx.control)) and bool(routes)


def model_candidates(part, ctx):
    """[(entity, friendly name, detected model, device text)] of the chosen Zigbee2MQTT valves: those whose model
    can be chosen (the step e32_room_valve_models), at most MAX_VALVE_MODELS."""
    if ctx is None or type(part) is not dict:
        return []
    found = []
    for entity_id in dict.fromkeys(part.get("valves") or []):
        details = ctx.finder.z2m_details(entity_id)
        if details is not None:
            found.append((entity_id, *details))
    return found[:MAX_VALVE_MODELS]


def valve_pins(ctx, models):
    """The "Through Home Assistant" choices after this save: the models chosen decide for their valves."""
    from .e32_valves import HA_MODEL
    pins = set(ctx.pins)
    for entity_id, model in (models or {}).items():
        if model == HA_MODEL and ctx.finder.route(entity_id).direct:
            pins.add(entity_id)  # would go to the E32 by itself: the explicit choice sticks
        else:
            pins.discard(entity_id)
    return pins


async def save_valves(hass, entry, room_id, routes, control, ctx=None, pins=None):
    """Store the room's valves on the E32 (after its plan; nothing is sent when they are as stored) and the "Through
    Home Assistant" choices. Raises FlowError e32_valves_rejected (``error``: the E32's word)."""
    from .e32_valves import valve_link
    from .valve_routes import save_through_ha
    link = valve_link(hass, entry)
    try:
        if link is None:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="valves_unreachable",
                                     translation_placeholders={"error": "no_connection"})
        if ctx is None or [r.record() for r in routes] != ctx.records or control != ctx.control:
            await link.async_change(room_id, control=control, valves=[r.record() for r in routes])
    except HomeAssistantError as err:
        error = (getattr(err, "translation_placeholders", None) or {}).get("error") or \
            getattr(err, "translation_key", None) or "unknown"
        raise FlowError("e32_valves_rejected", error=error) from None
    if pins is not None:
        save_through_ha(hass, entry, pins)


@dataclass
class RoomParts:
    """What the room form holds besides the plan, checked: the window and door contacts with the room's pause
    delays (seconds; None: the form has none), the persons, and the valves ((routes, control); None: the form has no
    valves section) with their context and the "Through Home Assistant" choices after the save."""
    contacts: list
    doors: list
    delay: int | None
    door_delay: int | None
    persons: list
    valves: tuple | None = None
    valve_ctx: object = None
    pins: set | None = None

    @property
    def valves_changed(self):
        return self.valves is not None and ([r.record() for r in self.valves[0]] != self.valve_ctx.records
                                            or self.valves[1] != self.valve_ctx.control or self.pins != self.valve_ctx.pins)

    def unchanged(self, entry, room_id):
        """Nothing of this differs from what the room stores."""
        return (not self.valves_changed and self.contacts == room_contacts(entry, room_id)
                and self.doors == room_doors(entry, room_id)
                and same_delays(comfort_options(entry), room_id, self.delay, self.door_delay)
                and self.persons == room_persons(entry, room_id))


def room_parts(hass, entry, room, user_input, valve_ctx=None, models=None):
    """The room form's contacts, persons and valves (its sections "window", "persons" and "valves") checked, in the
    form's order; ``models``: the models chosen per valve (the step e32_room_valve_models). Raises FlowError."""
    contacts, doors = submitted_contacts(hass, entry, room, user_input)
    persons = submitted_persons(hass, entry, room, user_input)
    delay = submitted_delay(user_input)
    door_delay = submitted_delay(user_input, "door_delay")
    valves = submitted_valves(user_input.get("valves"), valve_ctx, models)
    pins = valve_pins(valve_ctx, models) if valves is not None else None
    return RoomParts(contacts, doors, delay, door_delay, persons, valves, valve_ctx, pins)


async def save_room(hass, entry, link, room, values, parts):
    """Store a room as the form stores it and return its id: the plan (write_room), then its valves, its contacts
    with their delays (only with contacts) and its persons, each only when it differs from what is stored. A refused
    valve record raises FlowError e32_valves_rejected with ``saved`` (the room is stored: a new room has its id)."""
    saved = await write_room(link, room, values)
    if parts.valves_changed:  # after the plan: a new room exists on the E32 before its valves
        try:
            await save_valves(hass, entry, saved, *parts.valves, parts.valve_ctx, parts.pins)
        except FlowError as err:
            err.saved = saved
            raise
    settings = comfort_options(entry)
    if (parts.contacts != room_contacts(entry, saved) or parts.doors != room_doors(entry, saved)
            or (parts.contacts and not same_delays(settings, saved, parts.delay, parts.door_delay))):
        save_comfort(hass, entry, with_room_contacts(settings, saved, parts.contacts, parts.delay, parts.doors,
                                                     parts.door_delay))
    if parts.persons != room_persons(entry, saved):
        save_comfort(hass, entry, with_room_persons(comfort_options(entry), saved, parts.persons))
    return saved


def valid_resets(items, minimum, maximum, unit=CELSIUS, stored=None):
    """The settings panel's reset times (a list of {"days", "time", and "temperature" in the user's unit or
    "state"}) in the plan's form, checked by the rules of parse_resets: whole minutes, at least one day, a
    temperature in whole or half °C (°F to the nearest half °C) within the room's limits, or a state; at most four,
    never two on the same day and minute. One shown as stored keeps the stored one exactly (no °F rounding). An
    error is on the field "resets" with the reset time's place ``line`` (1..)."""
    if type(items) is not list:
        raise FlowError("e32_resets_invalid", "resets", line="1", text="")
    if len(items) > MAX_RESETS:
        raise FlowError("e32_resets_too_many", "resets")
    as_stored = {}
    for reset in stored if type(stored) is list else []:
        if type(reset) is dict:
            as_stored[_reset_key(shown_reset(reset, unit))] = reset
    resets, moments = [], set()
    for number, item in enumerate(items, 1):
        try:
            kept = as_stored.get(_reset_key(item))
            reset = deepcopy(kept) if kept is not None else _valid_reset(item, minimum, maximum, unit)
            temperature = reset.get("temperature_c")
            if type(temperature) in (int, float) and not minimum <= round(temperature * 100) <= maximum:
                raise FlowError("e32_resets_outside_limits", "resets")
            if any((day, reset["time"]) in moments for day in reset["days"]):
                raise FlowError("e32_resets_same_moment", "resets")
        except FlowError as err:
            err.placeholders.setdefault("line", str(number))
            err.placeholders.setdefault("text", "")
            raise
        moments.update((day, reset["time"]) for day in reset["days"])
        resets.append(reset)
    return resets


def shown_reset(reset, unit=CELSIUS):
    """A stored reset time as the settings panel shows it: its days, time and state, or its temperature in the
    user's unit."""
    out = {"days": sorted({d for d in reset.get("days") or [] if type(d) is int and 0 <= d <= 6}),
           "time": reset.get("time")}
    if reset.get("state") in RESET_STATES:
        out["state"] = reset["state"]
    elif type(reset.get("temperature_c")) in (int, float):
        out["temperature"] = shown(round(reset["temperature_c"] * 100), unit)
    return out


def _reset_key(item):
    """What makes two reset times the same as shown: days, time and value (None for anything else)."""
    if type(item) is not dict:
        return None
    days = item.get("days")
    days = tuple(sorted(days)) if type(days) is list and all(type(d) is int for d in days) else None
    value = item.get("temperature")
    value = float(value) if type(value) in (int, float) and type(value) is not bool else None
    return days, item.get("time"), item.get("state"), value


def _valid_reset(item, minimum, maximum, unit):
    """One reset time of the settings panel in the plan's form; raises FlowError."""
    if type(item) is not dict:
        raise FlowError("e32_resets_invalid", "resets")
    days, time_text = item.get("days"), item.get("time")
    match = re.fullmatch(r"(\d{2}):(\d{2})", time_text) if type(time_text) is str else None
    if (type(days) is not list or not days or len(set(days)) != len(days)
            or any(type(d) is not int or not 0 <= d <= 6 for d in days)
            or match is None or int(match[1]) > 23 or int(match[2]) > 59):
        raise FlowError("e32_resets_invalid", "resets")
    reset = {"days": sorted(days), "time": time_text}
    state, temperature = item.get("state"), item.get("temperature")
    if state is not None:
        if state not in RESET_STATES or temperature is not None:
            raise FlowError("e32_resets_invalid", "resets")
        reset["state"] = state
        return reset
    if type(temperature) not in (int, float) or type(temperature) is bool:
        raise FlowError("e32_resets_invalid", "resets")
    try:
        centi_c = centi(temperature, unit)
    except FlowError:
        raise FlowError("e32_resets_invalid", "resets") from None
    if unit == FAHRENHEIT:  # the E32 keeps half degrees, as the thermostat sets them
        centi_c = int((Decimal(centi_c) / 50).to_integral_value(ROUND_HALF_UP)) * 50
    elif centi_c % 50:
        raise FlowError("e32_resets_invalid", "resets")
    if not minimum <= centi_c <= maximum:
        raise FlowError("e32_resets_outside_limits", "resets")
    reset["temperature_c"] = centi_c / 100
    return reset


class RoomEditor(E32RoomFlow):
    """The room rules of the form, without the form: the settings panel (settings_rooms.py) validates and writes a
    room with the very methods the options step uses, for one installation and the plan Home Assistant read."""

    def __init__(self, hass, entry, plan, language=None):
        self.hass, self.config_entry, self._e32_plan = hass, entry, plan
        self.context = {"language": language} if language else {}

    def room_input(self, room):
        """What the room form would send for this room left as shown (``room`` None: a new room); the panel lays
        its own fields over it, so everything it does not show stays exactly as stored."""
        d = self._e32_defaults(room)
        user_input = {key: d[key] for key in ("name", "state", "emitter", "ha_sources", "ble_sources",
                                              "bluetooth_first", "setpoint_entity", "fallback_temperature",
                                              "program", "inactive_until")}
        user_input["limits"] = {"minimum_temperature": d["minimum_temperature"],
                                "maximum_temperature": d["maximum_temperature"]}
        user_input["persons"] = {"persons": d["persons"], "away_temperature": d["away_temperature"]}
        # 1.4.1: the window and door contacts with the room's pause delays (minutes, as the form shows them).
        user_input["window"] = {"contacts": d["contacts"], "door_contacts": d["door_contacts"],
                                "contact_delay": d["contact_delay"], "door_delay": d["door_delay"]}
        if self._e32_resets_supported():
            user_input["resets"] = [shown_reset(r, self._unit()) for r in (room or {}).get("resets") or []
                                    if type(r) is dict]
        stored = (room or {}).get(SMART_WARM_UP_FIELD)
        user_input[SMART_WARM_UP_FIELD] = stored if stored in ("on", "off") else "house"
        return user_input


def validate_room(hass, entry, plan, room, user_input, language=None):
    """The room as plan fields, checked as the room form checks it (E32RoomFlow._e32_room_values: the name, the
    state, the sources, the setting device, the temperatures, the program, the reset times, Off until); raises
    FlowError for the first problem. ``room``: the stored room (None: a new one); ``user_input``: the form's fields."""
    editor = RoomEditor(hass, entry, plan, language)
    return editor._e32_room_values(user_input, room, editor._e32_ble_options(room))
