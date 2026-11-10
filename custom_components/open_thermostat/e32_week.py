"""The visual week planner for E32 rooms (dashboard card openthermostat-e32-week).

Reads the E32 room plan and writes one room's week program through the same
RoomPlanLink as the "E32 rooms" options flow: the whole plan with the revision
it was read at, one re-read on 409. The program is the plan's own semantic
form (7 days Mon..Sun of [minute, centi °C], a point holds until the next
one); the E32 packs it for storage itself. A save only replaces the room's
"schedule" when it still equals the program the planner loaded, so a change
made meanwhile on the E32 page or in the options flow is never overwritten.

With E32 beta.23 ("plan.levels.v1") the planner's levels (Comfort, Eco,
Night) and the level of each switch point are stored with the room
(room_levels); for older firmware the card infers them as before.

E32 1.4: each room's reset times ("resets") go to the card. 1.4.1: the planner edits them too (markers on the
day bars, a card and a list) together with the room's own Smart warm-up ("smart_warm_up": house / on / off), and
one save writes the program, the reset times and the Smart warm-up choice of the room as one plan change. The
reset times are checked by the room form's own rules (e32_room_flow.valid_resets). A save without "resets" (a
1.4 card) leaves them alone: the E32 treats a missing key as "keep" and a present one (also []) as "replace";
an E32 without reset times (before 1.4) never gets the key, nor one without the room's Smart warm-up its key.
``expected`` is the program the card loaded (1.4) or {"schedule", "resets", "smart_warm_up"} as it loaded them
(1.4.1): a save only goes through while each of them is still as loaded.
"""
from __future__ import annotations

from copy import deepcopy

import probatio as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .heating_link import heating_hub
from .e32_comfort import comfort_options, program_levels
from .e32_room_flow import (CELSIUS, SMART_WARM_UP_FEATURE, SMART_WARM_UP_FIELD, FlowError, resets_supported,
                            valid_resets)
from .room_levels import room_levels, supported, valid_levels
from .room_plan import has_room_plan, plan_room

MAX_POINTS = 6
CARD_URL = "/open_thermostat/e32-week-card-1.4.2.js"
EDITOR_URL = "/open_thermostat/week-editor-1.4.2.js"
# RoomPlanLink failures -> the short codes the card explains in plain words.
FAILURES = {"room_plan_changed": "plan_changed", "room_plan_too_large": "plan_too_large",
            "room_plan_storage_full": "storage_full", "room_plan_unconfirmed": "save_unconfirmed",
            "room_plan_room_missing": "room_missing", "room_plan_password": "password_changed",
            "room_plan_rejected": "rejected", "room_plan_invalid": "unreachable", "room_plan_unreachable": "unreachable",
            # The E32's web sign-ins (room_plan.SIGN_IN_ERRORS): busy for a while, the card retries.
            "e32_session_capacity": "session_capacity", "e32_try_again_later": "try_again_later",
            "e32_no_free_session": "session_capacity"}
# The room form's reset time errors (e32_room_flow.valid_resets) -> the card's codes.
RESET_FAILURES = {"e32_resets_invalid": "invalid_resets", "e32_resets_too_many": "too_many_resets",
                  "e32_resets_outside_limits": "resets_outside_limits", "e32_resets_same_moment": "resets_same_moment"}
SMART_WARM_UP_CHOICES = ("house", "on", "off")


class WeekError(Exception):
    """A planner error code (sent to the card as the websocket error code)."""


def valid_schedule(schedule, low, high):
    """The 7-day program as the E32 accepts it (RoomSchedule::parse), or None for no program."""
    if schedule is None:
        return None
    if type(schedule) is not list or len(schedule) != 7:
        raise WeekError("invalid_schedule")
    week = []
    for day in schedule:
        if type(day) is not list or len(day) > MAX_POINTS:
            raise WeekError("invalid_schedule")
        points = []
        for point in day:
            if (type(point) is not list or len(point) != 2 or any(type(v) is not int for v in point)
                    or not 0 <= point[0] <= 1439 or (points and point[0] <= points[-1][0])):
                raise WeekError("invalid_schedule")
            if not low <= point[1] <= high:
                raise WeekError("invalid_schedule_limits")
            points.append([point[0], point[1]])
        week.append(points)
    return week if any(week) else None


def _program(room):
    schedule = room.get("schedule")
    return deepcopy(schedule) if type(schedule) is list and any(schedule) else None


def _resets(room):
    """The room's reset times for the card to show ([] without any or from firmware before 1.4)."""
    resets = room.get("resets")
    return [deepcopy(reset) for reset in resets if type(reset) is dict] if type(resets) is list else []


def _smart_supported(plan):
    features = plan.get("features")
    return type(features) is list and SMART_WARM_UP_FEATURE in features


def _smart(room):
    """The room's own Smart warm-up as the card shows it: "on", "off" or "house" (no key: as the house)."""
    value = room.get(SMART_WARM_UP_FIELD)
    return value if value in ("on", "off") else "house"


def checked_resets(items, room):
    """The card's reset times (the plan's form: days, time, temperature_c or state) by the room form's rules, in
    the plan's form; WeekError with the card's code. A reset time as stored is kept exactly."""
    if type(items) is not list:
        raise WeekError("invalid_resets")
    shown = []
    for item in items:
        if type(item) is not dict:
            shown.append(item)
            continue
        one = {"days": item.get("days"), "time": item.get("time")}
        if "state" in item:
            one["state"] = item["state"]
        if "temperature_c" in item or "state" not in item:
            one["temperature"] = item.get("temperature_c")
        shown.append(one)
    try:
        return valid_resets(shown, room.get("minimum_centi_c", 500), room.get("maximum_centi_c", 3000), CELSIUS,
                            room.get("resets"))
    except FlowError as err:
        raise WeekError(RESET_FAILURES.get(err.key, "invalid_resets")) from None


def _link(hass, entry_id):
    """The entry's RoomPlanLink, or WeekError: unavailable (no such E32 installation),
    disabled (turned off by the user), setup_error (the installation could not start: a clear
    message, no retry) or not_ready (still starting: the card waits and retries)."""
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN or not has_room_plan(entry):
        raise WeekError("unavailable")
    if entry.disabled_by is not None:
        raise WeekError("disabled")
    if entry.state in (ConfigEntryState.SETUP_ERROR, ConfigEntryState.MIGRATION_ERROR):
        raise WeekError("setup_error")
    if entry_id not in hass.data.get(DOMAIN, {}):
        raise WeekError("not_ready")
    link = heating_hub(hass, entry).plan
    if link is None:
        raise WeekError("not_ready")
    return link


def _code(err):
    return FAILURES.get(getattr(err, "translation_key", None), "rejected")


def _levels(room, settings):
    """The room's levels for the planner: stored ones, or (no program yet) the former house settings as a
    start; None lets the planner infer them from the program as before."""
    stored = room_levels(room)
    if stored is not None or _program(room) is not None or settings is None:
        return stored
    return dict(zip(("comfort", "eco", "night"), (round(v * 100) for v in program_levels(room, settings))))


def week_rooms(plan, settings=None):
    """What the card shows: per room its name, limits, fallback, program, levels, reset times and (an E32 that has
    it) its own Smart warm-up; ``features`` says what the card may edit besides the program."""
    smart = _smart_supported(plan)
    return {"revision": plan["revision"], "levels_supported": supported(plan),
            "features": {"resets": resets_supported(plan), "smart_warm_up": smart}, "rooms": [{
                "id": room["id"], "name": room.get("name") or room["id"],
                "minimum_centi_c": room.get("minimum_centi_c", 500), "maximum_centi_c": room.get("maximum_centi_c", 3000),
                "fallback_centi_c": room.get("fallback_centi_c", 2000), "setpoint_entity": room.get("setpoint_entity") or "",
                "schedule": _program(room), "levels": _levels(room, settings),
                "schedule_levels": room.get("schedule_levels") if room_levels(room) else None,
                "resets": _resets(room), **({SMART_WARM_UP_FIELD: _smart(room)} if smart else {})}
                for room in plan["rooms"]]}


def _settings(hass, entry_id):
    entry = hass.config_entries.async_get_entry(entry_id)
    return comfort_options(entry) if entry is not None else None


def _current(link):
    """The plan HA already read, while the E32 reports exactly its revision and is heard (so it is current):
    no sign-in on the E32 for every opened card. None: read it from the E32."""
    plan, hub = link.plan, link.hub
    if plan is None or link.revision is None or link.revision != hub.revision or not hub.alive:
        return None
    return plan


async def read_week(hass, entry_id, fresh=False):
    """The week programs; the plan HA holds while it is current, else (and with ``fresh``) read from the E32.

    A save always reads the E32's plan again and only replaces a program that still equals the one shown."""
    link = _link(hass, entry_id)
    settings = _settings(hass, entry_id)
    if not fresh and (plan := _current(link)) is not None:
        return week_rooms(plan, settings)
    try:
        return week_rooms(await link.async_read(), settings)
    except HomeAssistantError as err:
        raise WeekError(_code(err)) from None


async def save_week(hass, entry_id, room_id, schedule, expected, levels=None, schedule_levels=None, resets=None,
                    smart_warm_up=None):
    """Replace one room's program (and, for an E32 with "plan.levels.v1", its levels and the level of each
    point), and with ``resets`` / ``smart_warm_up`` (1.4.1) its reset times and its own Smart warm-up, as one plan
    change. WeekError("week_changed") when anything ``expected`` names changed since it was loaded."""
    link = _link(hass, entry_id)
    wanted = []
    guard = expected if type(expected) is dict else {"schedule": expected}

    def change(plan):
        candidate = deepcopy(plan)
        room = plan_room(candidate, room_id)
        if room is None:
            raise WeekError("room_missing")
        with_resets, with_smart = resets_supported(plan), _smart_supported(plan)
        if (_program(room) != guard.get("schedule")
                or with_resets and "resets" in guard and _resets(room) != guard["resets"]
                or with_smart and SMART_WARM_UP_FIELD in guard and _smart(room) != guard[SMART_WARM_UP_FIELD]):
            raise WeekError("week_changed")
        week = valid_schedule(schedule, room.get("minimum_centi_c", 500), room.get("maximum_centi_c", 3000))
        if week is None:
            room.pop("schedule", None)  # no program: the room keeps its fallback temperature
        else:
            room["schedule"] = week
        chosen = valid_levels(levels, room.get("minimum_centi_c", 500), room.get("maximum_centi_c", 3000))
        if supported(plan) and chosen is not None:
            # room_levels.normalize (on every save) makes the marks fit the program, or derives them.
            room["levels"] = chosen
            room["schedule_levels"] = schedule_levels if type(schedule_levels) is str else None
        # 1.4.1: the room's reset times as the planner shows them (also when unchanged: what was shown is what is
        # meant); every other room's are not sent, so the E32 keeps them. Never to an E32 without reset times.
        own = checked_resets(resets, room) if with_resets and resets is not None else None
        for other in candidate["rooms"]:
            other.pop("resets", None)
        if own is not None:
            room["resets"] = own
        smart = smart_warm_up if with_smart and smart_warm_up in SMART_WARM_UP_CHOICES else None
        if smart == "house":
            room.pop(SMART_WARM_UP_FIELD, None)  # no key: as the house
        elif smart is not None:
            room[SMART_WARM_UP_FIELD] = smart
        wanted[:] = [week, own, smart]
        return candidate

    def confirm(stored):
        room = plan_room(stored, room_id)
        week, own, smart = wanted
        return (room is not None and _program(room) == week and (own is None or _resets(room) == own)
                and (smart is None or _smart(room) == smart))
    try:
        stored = await link.async_change_plan(change, confirm)
    except HomeAssistantError as err:
        raise WeekError(_code(err)) from None
    return week_rooms(stored, _settings(hass, entry_id))


@websocket_api.websocket_command({vol.Required("type"): "open_thermostat/e32_week/get",
                                  vol.Required("entry_id"): str, vol.Optional("fresh", default=False): bool})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_week_get(hass, connection, msg):
    try:
        result = await read_week(hass, msg["entry_id"], msg.get("fresh", False))
    except WeekError as err:
        connection.send_error(msg["id"], str(err), "The week programs could not be read")
    else:
        # The module this backend serves: a page still running an older card asks for a reload.
        # rc.3: Smart warm-up as last read, so the planner's hint says what a time in the program means.
        from .e32_flow import smart_warm_up
        smart = smart_warm_up(hass, msg["entry_id"])
        connection.send_result(msg["id"], {**result, "card_url": CARD_URL, **({"smart_warm_up": smart} if smart is not None else {})})


@websocket_api.websocket_command({vol.Required("type"): "open_thermostat/e32_week/save",
                                  vol.Required("entry_id"): str, vol.Required("room_id"): str,
                                  vol.Required("schedule"): vol.Any(None, list),
                                  vol.Required("expected"): vol.Any(None, list, dict),
                                  vol.Optional("levels"): vol.Any(None, dict),
                                  vol.Optional("schedule_levels"): vol.Any(None, str),
                                  vol.Optional("resets"): list,
                                  vol.Optional("smart_warm_up"): vol.In(SMART_WARM_UP_CHOICES)})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_week_save(hass, connection, msg):
    try:
        result = await save_week(hass, msg["entry_id"], msg["room_id"], msg["schedule"], msg["expected"],
                                 msg.get("levels"), msg.get("schedule_levels"), msg.get("resets"),
                                 msg.get("smart_warm_up"))
    except WeekError as err:
        connection.send_error(msg["id"], str(err), "The week program was not saved")
    else:
        connection.send_result(msg["id"], result)
