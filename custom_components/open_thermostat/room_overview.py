"""Per E32 room, in plain words: why it heats or not (OpenThermostat 1.1).

``room_reason`` is a pure function of what the E32 already reports: the room
(``fw/state/room/<id>``: state, status, temperature, setpoint, demand and, while
it deviates from its plan, ``comfort``) and the house (``fw/state/heating``:
mode, request, away, burner activity). Home Assistant adds only the name and
the opening time of an open window or door contact; the E32 decides whether
the room is paused. The E32 overview page (data/html/index.html, roomWhy)
makes the same choice with the same words.

The "Reason" sensor of each room shows the reason as its state (a timeline in
the history) and the sentence variant and its values as attributes; the room
status card (frontend/room-status-card.js) writes the sentence from
strings.json (``entity.sensor.room_reason.state_attributes.line``), so every
viewer reads it in their own language.

HA 1.0.0rc7 (the owner's sketch, "Comfort until 22:30, then Night 18.0 °C"): the
same sensor carries ``program``, the room's week program now and its next step
(program_step), computed in Home Assistant from the plan it holds and the E32's
time zone; the room status card writes it after the sentence.

E32 1.3: a room on "Heat along only" (state ``follow``) says "Heats along" (reason
``follow``); in Smart warm-up's lead the E32 gives the room the coming target
(``setpoint_source`` "warmup", ``warmup_for`` the time on its clock) and the room
says "Warming up for 17:30" (reason ``warm_up``, sentence ``warm_up_for``).

E32 1.4.1: in the house mode Summer a room that is on says "Summer" (reason
``summer``, the room's ``setpoint_source`` "summer" or the house ``mode``
"summer"): the heating stays off, frost protection stays. A room that is off
still says so first.

1.4.2 (design §3.4): a room that is Off until a moment says when and what it
returns to: "Off until 14:00, then on again" / "then heating along again" (the
sentences ``off_until`` / ``off_until_follow`` from the plan's inactive_until and
follow_when_on); the sensor carries ``after`` (what the room returns to when it
is switched on, "active" or "follow", from the plan) and ``room_state`` (the
room's state as the E32 reports it), so the card labels a room on Heat along only
also while a boost or a manual change runs ("Heat along only · Boost until 21:00").

1.4.3 (HA-DASHBOARD-ONTWERP-1.4.3 §3.3, CONTRACT-1.4.3 §2): the sensor carries ``today``, the room's week program
of the local day (Home Assistant's time zone) as at most 8 entries [{"at": "06:30", "c": 21.0, "level", "name"}],
the first the level in force at 00:00, so the Rooms view's room card (frontend/room-card.js) draws today's bar
without reading the plan; absent on a room without a week program.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time as clock_time, timedelta, timezone
import re

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback

from .heating_link import RoomEntity, number

# The room status card's module (served and loaded with the week planner's, week_planner.card_modules).
CARD_URL = "/open_thermostat/room-status-card-1.4.5.js"
# The Overview's house card (E32 rc.5, frontend/house-card.js): what the boiler does now, today in figures, the day
# so far and, in a house with one room switched on, that room. The seventh card module, versioned like the others.
HOUSE_CARD_URL = "/open_thermostat/house-card-1.4.5.js"
HOUSE_CARD_TYPE = "custom:openthermostat-house"
# Yesterday's headline figures on the Learning view, large as on the house card (the same module, house-card.js).
YESTERDAY_CARD_TYPE = "custom:openthermostat-yesterday"
# The reasons, in the order they win: a room that is off or paused says so before
# anything else; a room that wants heat but waits for the boiler says why it waits;
# then the mode that sets its target (away, boost); then what it does.
REASONS = ["off", "summer", "window_open", "window_pending", "no_measurement", "hot_water", "boiler_pause",
           "warm_up", "away_return", "holiday", "away", "room_away", "house_away", "boost", "temporary",
           "follow", "heating", "wants_heat", "warm_enough"]
# The sentence of each variant (strings.json state_attributes.line) and the values it uses.
LINES = {
    # 1.4.2: Off until a moment, then back to On or to Heat along only (design §3.4).
    "off": (), "off_until": ("until",), "off_until_follow": ("until",), "summer": (), "window_open": (), "window_open_contact": ("contact", "since"),
    "window_pending": (), "window_pending_contact": ("contact",), "no_measurement": (),
    # E32 1.0.1 names the kind that pauses the room (comfort.opening) when no open contact can be named.
    "window_open_window": (), "window_open_door": (), "window_pending_window": (), "window_pending_door": (),
    "hot_water": (), "boiler_pause": (), "warm_up": ("time", "target"), "away_return": (), "holiday": ("until", "target"),
    # E32 1.3: Smart warm-up's lead (the room already has the coming target) and a room on Heat along only.
    "warm_up_for": ("time",), "follow": (), "follow_frost": (),
    "away": ("target",), "room_away": ("target",), "house_away": ("target",),
    "boost": (), "boost_until": ("until",), "temporary": ("target",), "temporary_until": ("target", "until"),
    "heating": ("temperature", "target"), "wants_heat": ("temperature", "target"),
    "warm_enough": ("temperature", "target"), "no_heat_needed": (),
}
# burner.activity (E32 beta.23) while the boiler serves hot water instead of the rooms.
HOT_WATER = ("tapping", "keep_warm", "charging", "hot_water")
PRESENCE = ["room_home", "room_away", "house_home", "house_away"]
# The Boiler view's "Now" card (E32 rc.5, frontend/boiler-now-card.js): what the boiler does now in a band of its
# colour with its display code in words, the water to the heating and back, the burner power and its starts as large
# figures. The eighth card module, versioned like the others.
BOILER_NOW_CARD_URL = "/open_thermostat/boiler-now-card-1.4.5.js"
BOILER_NOW_CARD_TYPE = "custom:openthermostat-boiler-now"
# 1.4.1 (CONTRACT-1.4.1 §9): the house banner at the top of every dashboard view (frontend/openthermostat-house-banner.js):
# empty unless the house is in summer mode, then the summer sentence and "Switch summer mode off". The ninth card module.
HOUSE_BANNER_URL = "/open_thermostat/openthermostat-house-banner-1.4.5.js"
HOUSE_BANNER_TYPE = "custom:openthermostat-house-banner"
# 1.4.3 (CONTRACT-1.4.3 §2): the Rooms view's room card (frontend/room-card.js): one card per room with its temperature
# and target, its presets and state, today's program, the last 24 hours and its devices. The tenth card module.
ROOM_CARD_URL = "/open_thermostat/room-card-1.4.5.js"
ROOM_V2_CARD_TYPE = "custom:openthermostat-room"  # (week_planner.ROOM_CARD_TYPE is the older room editor)
# The room card's today bar: at most this many entries (the first is the level in force at midnight).
TODAY_MAX = 8
# A level's name in the attribute ``today`` (the card prefers strings.json program.state; this is for automations and
# the last resort): the planner's three levels in the languages of the integration.
LEVEL_NAMES = {"en": {"comfort": "Comfort", "eco": "Eco", "night": "Night"},
               "nl": {"comfort": "Comfort", "eco": "Eco", "night": "Nacht"}}


@dataclass(frozen=True, slots=True)
class OpenContact:
    """An open window or door contact of the room as Home Assistant sees it."""
    name: str
    since: datetime | None = None


@dataclass(frozen=True, slots=True)
class RoomReason:
    reason: str
    line: str
    values: dict = field(default_factory=dict)


def _dict(value):
    return value if type(value) is dict else {}


def _utc(value):
    return datetime.fromtimestamp(value, timezone.utc) if type(value) is int and value > 0 else None


def opening(room):
    """E32 1.0.1: "window" or "door", the kind of contact that pauses the room (comfort.opening) while its window
    state is open or pending; None otherwise and on firmware that does not name it (1.0.0)."""
    comfort = _dict(room.get("comfort")) if type(room) is dict else {}
    if comfort.get("window") not in ("open", "pending") and comfort.get("mode") != "window_open":
        return None
    return comfort.get("opening") if comfort.get("opening") in ("window", "door") else None


def warmup_rise(room, now, zone):
    """E32 1.3: the moment a room in Smart warm-up's lead warms up for, or None.

    The E32 names it as a time on its own clock (``warmup_for`` "17:30", while ``setpoint_source`` is "warmup"):
    the next such moment in its time zone ``zone``, a minute's grace for the rise itself.
    """
    room = _dict(room)
    text = room.get("warmup_for")
    if (room.get("setpoint_source") != "warmup" or type(text) is not str or not re.fullmatch(r"\d\d:\d\d", text)
            or not isinstance(now, datetime) or now.tzinfo is None or zone is None):
        return None
    hour, minute = int(text[:2]), int(text[3:])
    if hour > 23 or minute > 59:
        return None
    local = now.astimezone(zone)
    at = datetime.combine(local.date(), clock_time(hour, minute), tzinfo=zone)
    if at < local - timedelta(minutes=1):
        at = datetime.combine(local.date() + timedelta(days=1), clock_time(hour, minute), tzinfo=zone)
    return at.astimezone(timezone.utc)


def after_off(plan_room):
    """What a room that is Off returns to when it is switched on (or its "Off until" ends): "follow" (Heat along
    only, E32 1.3's follow_when_on) or "active"; None without a plan room."""
    if type(plan_room) is not dict:
        return None
    from .room_plan import on_state
    return on_state(plan_room)


def room_reason(room, status=None, contact=None, warmup=None, rise=None, plan_room=None, now=None):
    """Why the room heats or not: a RoomReason, or None without a room.

    room: one room of the E32 status; status: the house (mode, request, away,
    burner); contact: the OpenContact HA sees open in this room (only used
    while the E32 itself reports the window open or pending; of the kind the
    E32 names, see RoomReasonSensor._contact); rise: E32 1.3, the moment the
    room warms up for while it has Smart warm-up's coming target (warmup_rise);
    plan_room (1.4.2): the room in the plan, for an Off room's end and what it
    returns to (the E32's room report leaves inactive_until out); now: an aware
    datetime (default: now).
    """
    if type(room) is not dict:
        return None
    status, comfort = _dict(status), _dict(room.get("comfort"))
    temperature = number(room.get("temperature"), -40, 85)
    target = number(room.get("setpoint"), 5, 35)
    mode_target = number(comfort.get("target_c"), 5, 35)
    mode = comfort.get("mode")

    def reason(key, line=None, **values):
        line = line or key
        return RoomReason(key, line, {name: values.get(name) for name in LINES[line]})

    if room.get("state") == "inactive":
        # The E32's frost protection still covers it; Off until a moment says when and what it returns to (1.4.2).
        plan = _dict(plan_room)
        until = _utc(plan.get("inactive_until", room.get("inactive_until")))
        if until is not None and until > (now or datetime.now(timezone.utc)):
            follow = after_off(plan) == "follow" if plan else room.get("follow_when_on") is True
            return reason("off", "off_until_follow" if follow else "off_until", until=until)
        return reason("off")
    if room.get("setpoint_source") == "summer" or _dict(status.get("away")).get("mode") == "summer":
        return reason("summer")  # E32 1.4.1: summer wins over programs, changes, away and open windows
    window, kind = comfort.get("window"), opening(room)
    if window == "open" or mode == "window_open":
        if contact is not None:
            return reason("window_open", "window_open_contact", contact=contact.name, since=contact.since)
        return reason("window_open", f"window_open_{kind}" if kind else None)
    if window == "pending":
        if contact is not None:
            return reason("window_pending", "window_pending_contact", contact=contact.name)
        return reason("window_pending", f"window_pending_{kind}" if kind else None)
    if room.get("status") == "lost" or temperature is None:
        return reason("no_measurement")
    demand = room.get("demand") is True
    active = status.get("mode") == "active"
    if demand and _dict(status.get("burner")).get("activity") in HOT_WATER:
        return reason("hot_water")
    if demand and active and _dict(status.get("request")).get("reason") == "minimum_off":
        return reason("boiler_pause")
    if room.get("setpoint_source") == "warmup" and mode in (None, "program") and isinstance(rise, datetime):
        return reason("warm_up", "warm_up_for", time=rise)
    start = _dict(warmup)
    switch = _dict(start.get("next_switch"))
    if (demand and start.get("start_now") is True and start.get("applies") is True and mode in (None, "program")
            and _utc(switch.get("utc")) and number(switch.get("target_c"), 5, 35) is not None):
        return reason("warm_up", time=_utc(switch["utc"]), target=number(switch["target_c"], 5, 35))
    until = _utc(comfort.get("until"))
    away_target = mode_target if mode_target is not None else number(_dict(status.get("away")).get("target_c"), 5, 25)
    if mode == "away_return":
        return reason("away_return")
    if mode == "away":
        return reason("holiday", until=until, target=away_target) if until else reason("away", target=away_target)
    if mode == "presence_away":
        # The room's own persons when the E32 has a fresh report of them, else everyone of the house.
        # rc.3 names it (away_by); older firmware: its own persons away while the house is not.
        own = comfort.get("away_by") == "room" if comfort.get("away_by") in ("room", "house") else comfort.get("persons") == "away"
        return reason("room_away" if own else "house_away", target=away_target)
    if mode == "boost":
        return reason("boost", "boost_until", until=until) if until else reason("boost")
    if mode in ("timed", "next"):
        held = mode_target if mode_target is not None else target
        return (reason("temporary", "temporary_until", target=held, until=until) if until
                else reason("temporary", target=held))
    if room.get("state") == "follow":  # E32 1.3, Heat along only: its target, never a request of its own
        # ... except below the frost limit (8 °C), where the E32 asks for heat for it (demand).
        return reason("follow", "follow_frost") if demand else reason("follow")
    if demand:
        # In shadow mode the old thermostat still runs the boiler: the room wants heat, the E32 does not heat.
        return reason("heating" if active else "wants_heat", temperature=temperature, target=target)
    if target is None:
        return reason("warm_enough", "no_heat_needed")
    return reason("warm_enough", temperature=temperature, target=target)


def room_presence(room, status=None):
    """Whether someone is home for this room: its own persons (room_*), else the house (house_*), else None."""
    persons = _dict(_dict(room).get("comfort")).get("persons")
    if persons in ("home", "away"):
        return "room_" + persons
    presence = _dict(_dict(status).get("away")).get("presence")
    return "house_" + presence if presence in ("home", "away") else None


# The week planner's levels (room_levels.LEVELS, schedule_levels digits 1..3) and the house's holiday: the names a
# program step can have (strings.json state_attributes.program.state); None is a point with its own temperature.
PROGRAM_LEVELS = ["comfort", "eco", "night", "holiday"]
# Comfort modes in which the week program sets the room's target (the E32's comfort.mode; absent: the program).
FOLLOWS_PROGRAM = (None, "program")


def _marks(plan_room, schedule):
    """Per day the level of each switch point ("comfort", "eco", "night" or None): the marks the planner stored with
    its levels (E32 beta.23, room_levels), else the levels inferred from the program as the planner shows them."""
    from .e32_comfort import program_levels
    from .room_levels import LEVELS, mark_text, room_levels
    levels = room_levels(plan_room)
    text = plan_room.get("schedule_levels") if levels is not None else None
    if levels is None:
        levels = dict(zip(LEVELS, (round(value * 100) for value in program_levels(plan_room, None))))
    days = mark_text(schedule, levels, text).split(".")
    return [[LEVELS[int(digit) - 1] if digit != "0" else None for digit in day] for day in days]


def _schedule(plan_room):
    """The room's week program as 7 days of [(minute, centi °C)], or None (no program, or not well-formed)."""
    schedule = plan_room.get("schedule") if type(plan_room) is dict else None
    if type(schedule) is not list or len(schedule) != 7:
        return None
    week = []
    for day in schedule:
        if type(day) is not list:
            return None
        points = []
        for point in day:
            if (type(point) is not list or len(point) != 2 or any(type(v) is not int for v in point)
                    or not 0 <= point[0] <= 1439 or (points and point[0] <= points[-1][0])):
                return None
            points.append((point[0], point[1]))
        week.append(points)
    return week if any(week) else None


def _holiday_ahead(away, now, before):
    """(start, temperature °C) of the first planned holiday that starts after now and before ``before`` (None: any
    time), or None."""
    from .e32_house import holiday_periods, holiday_temperature, supports_holidays
    if not supports_holidays(away):
        return None
    temperature = holiday_temperature(away)
    if temperature is None:
        return None
    for start, _end in holiday_periods(away.get("holidays")):
        at = datetime.fromtimestamp(start, timezone.utc)
        if now < at and (before is None or at < before):
            return at, temperature
    return None


def _program_now(week, marks, local):
    """(level, centi °C) of the switch point in force at the local time: the last one at or before it today, else the
    last one of an earlier day (a week back at most, the E32's RoomSchedule::at)."""
    weekday, minute = local.weekday(), local.hour * 60 + local.minute
    for back in range(8):
        day = (weekday - back) % 7
        found = [i for i, (at, _) in enumerate(week[day]) if back or at <= minute]
        if found:
            return marks[day][found[-1]], week[day][found[-1]][1]
    return None


def program_target_now(plan_room, now, zone):
    """The temperature (°C) the room's week program gives at ``now`` in the E32's time zone ``zone``, or None (no
    program, not well-formed, or no aware time). For a room that is Off: what it keeps for when it is on."""
    week = _schedule(plan_room)
    if week is None or not isinstance(now, datetime) or now.tzinfo is None:
        return None
    local = now.astimezone(zone)
    marks = [[None] * len(day) for day in week]
    found = _program_now(week, marks, local)
    return found[1] / 100 if found else None


def program_step(plan_room, now, zone, room=None, away=None):
    """The room's week program now and its next step, for the room status card ("Comfort until 22:30, then Night
    18.0 °C"); None while the program does not set the room's target.

    plan_room: the room in the E32's plan (its ``schedule``, 7 days Mon..Sun of [minute, centi °C], a point holding
    until the next one, also across midnight and empty days, and the planner's ``levels`` and ``schedule_levels``);
    now: an aware datetime; zone: the E32's time zone (tzinfo) in which the program's times are wall-clock times;
    room: the room as the E32 reports it (its state, setpoint_source and comfort mode); away: the house's away status
    (its planned holidays, E32 rc.4).

    Returns {"level", "target", "next_at", "next_level", "next_target"}: the level of the switch point in force
    ("comfort", "eco", "night", or None for a point with its own temperature) and its temperature (°C); then the
    first later moment where the level or the temperature changes (ISO, UTC) with the level and temperature from
    then, all three None when nothing changes in the coming week. A planned holiday that starts before that change is
    the next step instead: level "holiday", the program's temperature then, at most the holiday temperature (the E32's
    ceiling on holiday).

    None: no plan room or no program; the room is off; the E32 sets the target from elsewhere (setpoint_source not
    "schedule": no clock yet, or a target from Home Assistant); an override, away, a holiday or an open window holds
    the room (comfort mode other than the program: the room's sentence says what holds it and until when).
    """
    week = _schedule(plan_room)
    if week is None or not isinstance(now, datetime) or now.tzinfo is None:
        return None
    room = _dict(room)
    # E32 1.3: Smart warm-up's lead ("warmup") still runs the program: its coming step is what it warms up for.
    if room.get("state") == "inactive" or room.get("setpoint_source") not in (None, "schedule", "warmup"):
        return None
    if _dict(room.get("comfort")).get("mode") not in FOLLOWS_PROGRAM:
        return None
    marks = _marks(plan_room, [[list(point) for point in day] for day in week])
    local = now.astimezone(zone)
    current = _program_now(week, marks, local)
    minute = local.hour * 60 + local.minute
    following = None
    for ahead in range(8):  # the coming week, up to the same weekday a week on
        day = (local.weekday() + ahead) % 7
        for index, (at, centi) in enumerate(week[day]):
            if ahead * 1440 + at - minute > 0 and (marks[day][index], centi) != current:
                # The wall-clock time in the E32's zone (a time a clock change skips counts as the hour after it).
                wall = datetime.combine(local.date() + timedelta(days=ahead), clock_time(at // 60, at % 60), tzinfo=zone)
                following = (wall.astimezone(timezone.utc), marks[day][index], centi / 100)
                break
        if following:
            break
    holiday = _holiday_ahead(_dict(away), now, following[0] if following else None)
    if holiday is not None:
        at, ceiling = holiday
        then = _program_now(week, marks, at.astimezone(zone))[1] / 100
        following = (at, "holiday", min(then, ceiling))
    level, centi = current
    return {"level": level, "target": centi / 100,
            "next_at": following[0].isoformat() if following else None,
            "next_level": following[1] if following else None,
            "next_target": following[2] if following else None}


def _level_name(level, centi, lang):
    """A level's name in ``today``: the planner's ("Night"/"Nacht"), a point with its own temperature by that
    temperature ("21.5 °C"/"21,5 °C")."""
    if level in LEVELS_KNOWN:
        return LEVEL_NAMES.get(lang, LEVEL_NAMES["en"])[level]
    text = f"{centi / 100:g}"
    return (text.replace(".", ",") if lang == "nl" else text) + " °C"


LEVELS_KNOWN = ("comfort", "eco", "night")


def program_today(plan_room, now, zone, house_zone=None, lang="en"):
    """The room's week program of the local day, for the room card's bar: [{"at", "c", "level", "name"}], or None.

    plan_room: the room in the E32's plan (its 7-day ``schedule`` of [minute, centi °C] and the planner's marks);
    now: an aware datetime; zone: the E32's time zone, in which the program's times are wall-clock times;
    house_zone: Home Assistant's time zone, whose day the bar shows (default: the E32's). The first entry is the level
    in force at 00:00 ("at" "00:00"); then every switch point of the day where the level or the temperature changes,
    by its time in the house's zone ("06:30"); at most TODAY_MAX entries. ``level``: "comfort", "eco", "night", or
    "own" for a point with its own temperature; ``name``: its name in ``lang``. None: no program (or not well-formed)
    or no aware time.
    """
    week = _schedule(plan_room)
    if week is None or not isinstance(now, datetime) or now.tzinfo is None:
        return None
    house = house_zone or zone
    marks = _marks(plan_room, [[list(point) for point in day] for day in week])
    local = now.astimezone(house)
    start = datetime.combine(local.date(), clock_time(0, 0), tzinfo=house)
    end = datetime.combine(local.date() + timedelta(days=1), clock_time(0, 0), tzinfo=house)
    first = _program_now(week, marks, start.astimezone(zone))
    points = [(start, *first)] if first else []
    # The E32's days that overlap the house's day (the same day while both zones agree, as they normally do).
    e32_day = start.astimezone(zone).date()
    for offset in (-1, 0, 1):
        day = e32_day + timedelta(days=offset)
        for index, (at, centi) in enumerate(week[day.weekday()]):
            wall = datetime.combine(day, clock_time(at // 60, at % 60), tzinfo=zone).astimezone(house)
            if start < wall < end:
                points.append((wall, marks[day.weekday()][index], centi))
    points.sort(key=lambda point: point[0])
    today = []
    for wall, level, centi in points:
        if today and (today[-1]["level"], round(today[-1]["c"] * 100)) == (level or "own", centi):
            continue  # the same level and temperature again: no new block
        today.append({"at": wall.strftime("%H:%M"), "c": centi / 100, "level": level or "own",
                      "name": _level_name(level, centi, lang)})
    return today[:TODAY_MAX] or None


def e32_zone(hass, entry):
    """The E32's time zone (its Settings, as last seen in its daily settings backup or the time zone step) when Home
    Assistant knows its rules; else Home Assistant's own (the zone the E32 is set to when it is installed)."""
    from zoneinfo import ZoneInfo

    from homeassistant.util import dt as dt_util

    from .const import DOMAIN
    from .e32_system import TIME_ZONE_STATE, ha_zone, zone_of
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id) if entry is not None else None
    posix = state.get(TIME_ZONE_STATE) if type(state) is dict else None
    name = zone_of(posix, ha_zone(hass)) if type(posix) is str else None
    if name is not None:
        try:
            return ZoneInfo(name)
        except (ValueError, OSError):
            pass
    return dt_util.get_default_time_zone()


def open_contact(hass, entity_ids):
    """The contact of the room that has been open longest (with the others' names), or None."""
    opened = [state for state in (hass.states.get(e) for e in entity_ids) if state is not None and state.state == "on"]
    if not opened:
        return None
    opened.sort(key=lambda state: state.last_changed)
    names = [state.name for state in opened]
    # Two names at most; more open contacts are counted ("Back door, Kitchen window +1").
    name = ", ".join(names[:2]) + (f" +{len(names) - 2}" if len(names) > 2 else "")
    return OpenContact(name, opened[0].last_changed)


def _iso(value):
    return value.isoformat() if isinstance(value, datetime) else value


class RoomReasonSensor(RoomEntity, SensorEntity):
    """Why the room heats or not; the attributes carry the sentence for the room status card."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = REASONS
    _attr_icon = "mdi:comment-question-outline"
    # The card's live values; the history keeps the reason itself (the room's own sensors keep the rest).
    _unrecorded_attributes = frozenset({"values", "temperature", "setpoint", "presence", "window", "opening",
                                        "valve_position", "valve_problem", "program", "comfort_mode", "comfort_until",
                                        "after", "room_state", "today"})

    def __init__(self, hub, room):
        self._attach_room(hub, room, "reason")
        self._tick = None  # the timer that writes the state again at the program's next step

    def _entry(self):
        return getattr(getattr(self, "platform", None), "config_entry", None)

    def _plan_room(self):
        plan = getattr(self.hub, "plan", None)
        return plan.room(self.room_id) if plan is not None else None

    def _program(self, now=None):
        """The week program now and its next step (program_step), or None."""
        plan_room = self._plan_room()
        if plan_room is None or self.hass is None:
            return None
        status = self.hub.status if type(self.hub.status) is dict else {}
        return program_step(plan_room, now or datetime.now(timezone.utc), e32_zone(self.hass, self._entry()), self.room,
                            status.get("away"))

    def _today(self):
        """Today's week program for the room card's bar (program_today), in Home Assistant's day, or None."""
        plan_room = self._plan_room()
        if plan_room is None or self.hass is None:
            return None
        from homeassistant.util import dt as dt_util
        lang = str(getattr(self.hass.config, "language", "en") or "en")[:2]
        return program_today(plan_room, datetime.now(timezone.utc), e32_zone(self.hass, self._entry()),
                             dt_util.get_default_time_zone(), lang)

    @callback
    def async_write_ha_state(self):
        super().async_write_ha_state()
        self._plan_tick()

    @callback
    def _plan_tick(self):
        """Write the state again just after the program's next step, also when the E32 reports nothing new then
        (a step to another level with the same temperature)."""
        if self._tick is not None:
            self._tick()
            self._tick = None
        program = self._program() if self.hub.fresh and self.room else None
        moments = [datetime.fromisoformat(program["next_at"])] if program and program["next_at"] else []
        if self.hub.fresh and self.room and self._plan_room() is not None:
            # 1.4.3: a new day gives a new ``today`` (the room card's bar), also without a step at midnight.
            from homeassistant.util import dt as dt_util
            local = dt_util.now()
            moments.append(datetime.combine(local.date() + timedelta(days=1), clock_time(0, 0), tzinfo=local.tzinfo))
        if not moments:
            return
        from homeassistant.helpers.event import async_track_point_in_utc_time

        @callback
        def due(_now):
            self._tick = None
            if self.hass is not None and self.entity_id:
                self.async_write_ha_state()
        self._tick = async_track_point_in_utc_time(self.hass, due, min(moments) + timedelta(seconds=1))

    async def async_will_remove_from_hass(self):
        if self._tick is not None:
            self._tick()
            self._tick = None
        await super().async_will_remove_from_hass()

    def _contact(self, opening=None):
        """The open contact to name: of the kind the E32 says pauses the room (1.0.1), else any of the room's."""
        entry = self._entry()
        if entry is None or self.hass is None:
            return None
        from .e32_comfort import comfort_options, doors_of, windows_of
        settings = comfort_options(entry)
        ids = {"door": doors_of, "window": windows_of}.get(opening, lambda *_: [])(settings, self.room_id)
        return open_contact(self.hass, ids or settings["contacts"].get(self.room_id, []))

    def _reason(self):
        room = self.room
        if not room or not self.hub.fresh:
            return None
        comfort = _dict(room.get("comfort"))
        warmup = self.hub.warmup.get(self.room_id) if type(getattr(self.hub, "warmup", None)) is dict else None
        start = warmup.get("optimum_start") if type(warmup) is dict else None
        contact = self._contact(comfort.get("opening")) if comfort.get("window") in ("open", "pending") else None
        if room.get("setpoint_source") == "warmup":
            from homeassistant.util import dt as dt_util
            zone = e32_zone(self.hass, self._entry()) if self.hass is not None else dt_util.get_default_time_zone()
            rise = warmup_rise(room, datetime.now(timezone.utc), zone)
        else:
            rise = None
        return room_reason(room, self.hub.status, contact, start, rise, self._plan_room())

    @property
    def native_value(self):
        reason = self._reason()
        return reason.reason if reason else None

    @property
    def extra_state_attributes(self):
        reason = self._reason()
        if reason is None:
            return None
        from .e32_valves import positions, problems, room_valves
        room, valves = self.room, room_valves(self.hub, self.room_id) or {}
        moved = positions(valves)
        # values: the sentence's own (an away line's target is the away temperature, not the setpoint).
        return {"room_id": self.room_id, "line": reason.line,
                "values": {key: _iso(value) for key, value in reason.values.items()},
                "temperature": number(room.get("temperature"), -40, 85), "setpoint": number(room.get("setpoint"), 5, 35),
                "presence": room_presence(room, self.hub.status),
                "window": _dict(room.get("comfort")).get("window"),
                # E32 1.0.1: which kind pauses the room while the window state is open or pending ("window" or
                # "door"); None on 1.0.0, which does not tell them apart (the cards then say "window or door").
                "opening": opening(room),
                "valve_position": round(sum(moved) / len(moved)) if moved else None,
                "valve_problem": bool(problems(valves)) if valves else None,
                # HA 1.0.0rc7: the week program now and its next step (program_step), for the room status card.
                "program": self._program(),
                # The comfort mode itself (away, nobody home, open window) and a holiday's end: the Reason ranks no
                # measurement, hot water and a boiler pause above them, while the E32 still holds the program (Today).
                "comfort_mode": _dict(room.get("comfort")).get("mode"),
                "comfort_until": _iso(_utc(_dict(room.get("comfort")).get("until"))),
                # E32 1.4 (#8): Smart warm-up as this room has it ("on" / "off": its own choice or the house switch);
                # None on older firmware (the card then follows the house switch).
                "smart_warm_up": room.get("smart_warm_up") if room.get("smart_warm_up") in ("on", "off") else None,
                # 1.4.2: what the room returns to when it is switched on ("active", "follow"; from the plan) and its
                # state now, so the card says "Heat along only" also while a boost runs.
                "after": after_off(self._plan_room()),
                "room_state": room.get("state") if room.get("state") in ("active", "follow", "inactive") else None,
                # 1.4.3: today's week program for the room card's bar (absent without a program, CONTRACT-1.4.3 §2).
                **({"today": today} if (today := self._today()) else {})}
