"""The settings panel's section Rooms (1.4, docs/engineering/HA-INSTELPANEEL-ONTWERP.nl.md 4.2 and 4.3).

Three screens, one section ``rooms`` (settings.py registry):

- the list (item None): every room of the E32 plan, in its order, with its state, heating type and the entities
  whose live values the panel shows beside it (the room's thermostat and temperature sensor in ``hass.states``);
- one room (item = its id, also ``#room/<id>`` from the room card): its name, Heating (On / Heat along only /
  Off), heating type, temperature sources, setting device, temperature without a week program, the week program
  (a summary: it is edited in the week planner), reset times, Smart warm-up and "Off until";
- a new room (item ``new-room``, never a room id: those have no hyphen).

The model comes from what Home Assistant already holds: the room plan it last read from the E32 (read once when
there is none yet), the hub, and the entity and device registries. Live values never enter the model (the token
would change with every reading); the panel reads them from ``hass.states`` through the entity IDs it names.

Saving uses the room form's own rules (e32_room_flow: RoomEditor.room_input, validate_room, write_room,
remove_room): the panel's fields are laid over what the form would send for the room as stored, validated by
the same method, and only the fields that differ from the room as shown go to the E32, on top of the plan it
holds then (If-Match and one re-read on 409, RoomPlanLink.async_change_plan). Configure → Rooms and the panel
therefore give the same result for the same input (test_settings_rooms.py). Radiator valves, persons, temperature
limits and window contacts are not in this screen and stay exactly as stored (the window contacts are in the
section House; the rest stays in Configure → Rooms for now).

Values the panel sends (any key left out keeps the stored value): ``name``, ``state``, ``emitter``, ``sources``
([{"type": "ha" | "ble", "id"}], the first fresh one leads), ``setpoint_entity`` ("" for none),
``fallback_temperature`` (the user's unit), ``resets`` ([{"days", "time", "temperature" | "state"}], E32 1.4),
``smart_warm_up`` ("house" | "on" | "off", E32 1.4), ``inactive_until`` ("YYYY-MM-DDTHH:MM" local, "" for none),
``standard_program`` (a new room only: start with "Workdays and weekend"), ``remove`` (true: remove the room).
"""
from __future__ import annotations

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .e32_room_flow import (MAX_ROOMS, MAX_SOURCES, SMART_WARM_UP_FEATURE, SMART_WARM_UP_FIELD, E32RoomFlow, FlowError,
                            RoomEditor, remove_room, resets_supported, shown, shown_reset, write_room)
from .e32_comfort import comfort_options, doors_of, windows_of
from .e32_setting_device import default_program
from .heating_link import ble_device_identifier, label
from .room_plan import plan_room, until_datetime
from .settings import SettingsError, _hub, register_section

NEW = "new-room"
# The room form's fields that the panel shows under another name: the two source lists are the one list "sources".
FIELDS = {"ha_sources": "sources", "ble_sources": "sources", "persons": "base", "program": "base", "window": "base",
          "limits": "base", "valves": "base"}
# Errors of the form that belong to a field of the panel although the form puts them on the whole form.
FIELD_OF = {"e32_sources_count": "sources", "e32_rejected_sources": "sources", "e32_rejected_duplicate_source": "sources",
            "e32_rejected_setpoint": "setpoint_entity", "e32_rejected_resets": "resets",
            "e32_resets_too_many": "resets"}


def _link(hass, entry):
    """(hub, its room plan link), or SettingsError("unavailable") while the installation does not run."""
    hub = _hub(hass, entry)
    if hub is None or getattr(hub, "plan", None) is None:
        raise SettingsError("unavailable")
    return hub, hub.plan


def _failure(err):
    """A failed E32 read or write as the room form's error key, with its placeholders (error, room)."""
    key, placeholders = E32RoomFlow._e32_failure(None, err)
    return SettingsError(key, FIELD_OF.get(key, "base"), **placeholders)


def _refusal(err):
    """A FlowError of the room form on the panel's field."""
    field = FIELDS.get(err.field, err.field)
    return SettingsError(err.key, FIELD_OF.get(err.key, field) if field == "base" else field, **err.placeholders)


async def _plan_now(link):
    """The room plan Home Assistant last read from the E32; read once when it has none yet."""
    if link.plan is not None:
        return link.plan
    try:
        return await link.async_read()
    except HomeAssistantError as err:
        raise _failure(err) from None


def _local(epoch):
    """A moment as the panel's date-and-time field holds it ("2026-12-01T18:00", local time)."""
    return dt_util.as_local(dt_util.utc_from_timestamp(epoch)).strftime("%Y-%m-%dT%H:%M")


def _entities(hass, hub, room_id):
    """The entity IDs of the room's thermostat and temperature (their live values are in hass.states)."""
    registry = er.async_get(hass)
    found = {"climate": registry.async_get_entity_id("climate", DOMAIN, f"{hub.prefix}_e32_room_{room_id}_thermostat"),
             "temperature": registry.async_get_entity_id("sensor", DOMAIN, f"{hub.prefix}_e32_room_{room_id}_temperature")}
    return {key: value for key, value in found.items() if value}


def _ble(hass, entry, hub, plan):
    """The E32's Bluetooth sensors: id, the name Home Assistant shows and the entity of its temperature; sensors
    the plan still names but the E32 no longer reports keep their id as name."""
    devices, registry = dr.async_get(hass), er.async_get(hass)
    sensors = []
    for sensor_id, sensor in sorted((getattr(hub, "ble", None) or {}).items()):
        device = devices.async_get_device_by_identifier(ble_device_identifier(hub.prefix, sensor_id), entry.entry_id)
        entity = registry.async_get_entity_id("sensor", DOMAIN, f"{hub.prefix}_e32_ble_{sensor_id}_temperature")
        name = (device and (device.name_by_user or device.name)) or label(sensor)
        sensors.append({"id": sensor_id, "name": name, **({"entity_id": entity} if entity else {})})
    known = {sensor["id"] for sensor in sensors}
    for room in plan.get("rooms") or []:
        for source in room.get("sources") or []:
            if type(source) is dict and source.get("type") == "ble" and source.get("id") not in known:
                known.add(source["id"])
                sensors.append({"id": str(source["id"]), "name": str(source["id"])})
    return sensors


def _own(hass, editor):
    """This installation's own room and Bluetooth entities that look like a temperature source: never offered as a
    Home Assistant source (the E32 has them already; its Bluetooth sensors are chosen as such)."""
    registry = er.async_get(hass)
    own = []
    for entity_id in editor._e32_own_entities():
        item = registry.async_get(entity_id)
        if entity_id.startswith("climate.") or (entity_id.startswith("sensor.") and item is not None and (
                item.device_class or item.original_device_class) == "temperature"):
            own.append(entity_id)
    return sorted(own)


def program_groups(schedule, unit):
    """The week program as groups of days with the same switch points, in day order: [{"days": [0..6], "points":
    [["06:30", 18.0], ...]}] (temperatures in the user's unit); [] without a program."""
    if type(schedule) is not list or len(schedule) != 7 or not any(schedule):
        return []
    groups = []
    for day, points in enumerate(schedule):
        if not points:
            continue
        shown_points = [[f"{m // 60:02d}:{m % 60:02d}", shown(c, unit)] for m, c in points]
        group = next((g for g in groups if g["points"] == shown_points), None)
        if group is None:
            groups.append({"days": [day], "points": shown_points})
        else:
            group["days"].append(day)
    return groups


def _features(plan):
    features = plan.get("features") if type(plan.get("features")) is list else []
    return {"resets": resets_supported(plan), "smart_warm_up": SMART_WARM_UP_FEATURE in features}


def list_model(hass, entry, hub, plan):
    rooms = []
    for room in plan.get("rooms") or []:
        until = until_datetime(room)
        rooms.append({"id": room["id"], "name": room.get("name") or room["id"], "state": room.get("state", "active"),
                      "emitter": room.get("emitter", "radiator"),
                      "inactive_until": _local(until.timestamp()) if until is not None else "",
                      "entities": _entities(hass, hub, room["id"])})
    return {"rooms": rooms, "can_add": len(rooms) < MAX_ROOMS, "max_rooms": MAX_ROOMS,
            "unit": RoomEditor(hass, entry, plan)._unit(),
            "ble": {sensor["id"]: sensor["name"] for sensor in _ble(hass, entry, hub, plan)}}


def room_model(hass, entry, hub, plan, room):
    """One room's screen (``room`` None: a new room)."""
    editor = RoomEditor(hass, entry, plan)
    unit, d, features = editor._unit(), editor._e32_defaults(room), _features(plan)
    stored = room or {}
    until = until_datetime(stored) if room is not None else None
    model = {
        "id": stored.get("id", ""), "name": d["name"], "state": d["state"], "emitter": d["emitter"],
        "states": editor._e32_states(room),
        "sources": [{"type": s.get("type"), "id": s.get("id")} for s in stored.get("sources") or [] if type(s) is dict],
        "setpoint_entity": d["setpoint_entity"] or "",
        "fallback_temperature": d["fallback_temperature"], "unit": unit,
        "limits": {"minimum": d["minimum_temperature"], "maximum": d["maximum_temperature"]},
        "inactive_until": _local(until.timestamp()) if until is not None else "",
        "features": features, "max_sources": MAX_SOURCES, "max_rooms": MAX_ROOMS,
        "ble": _ble(hass, entry, hub, plan), "own": _own(hass, editor),
    }
    if room is None:  # the standard program "Workdays and weekend", as the form fills it in for a new room (#7)
        model["program"] = program_groups(default_program(500, 3000), unit)
        model["standard_program"] = True
        model["full"] = len(plan.get("rooms") or []) >= MAX_ROOMS
    else:
        model["program"] = program_groups(room.get("schedule"), unit)
        model["entities"] = _entities(hass, hub, room["id"])
        valves = (getattr(hub, "valves", None) or {}).get(room["id"])
        model["valves"] = len(valves.get("valves") or []) if type(valves) is dict else 0
        comfort = comfort_options(entry)  # the window and door contacts are in the section House
        model["contacts"] = {"windows": len(windows_of(comfort, room["id"])), "doors": len(doors_of(comfort, room["id"]))}
    if features["resets"]:
        model["resets"] = [shown_reset(r, unit) for r in stored.get("resets") or [] if type(r) is dict]
    if features["smart_warm_up"]:
        choice = stored.get(SMART_WARM_UP_FIELD)
        model["smart_warm_up"] = choice if choice in ("on", "off") else "house"
    return model


async def read_rooms(hass, entry, item):
    hub, link = _link(hass, entry)
    plan = await _plan_now(link)
    if item is None:
        return list_model(hass, entry, hub, plan)
    if item == NEW:
        return room_model(hass, entry, hub, plan, None)
    room = plan_room(plan, item)
    if room is None:
        raise SettingsError("e32_room_missing", room=item)
    return room_model(hass, entry, hub, plan, room)


def room_input(editor, room, model, values):
    """What the room form would get for this save: the room as stored, with the panel's fields laid over it."""
    user_input = editor.room_input(room)
    for key in ("name", "state", "emitter", "fallback_temperature"):
        if key in values:
            user_input[key] = values[key]
    if "setpoint_entity" in values:
        user_input["setpoint_entity"] = values["setpoint_entity"] or ""
    sources = values.get("sources")
    if sources is not None:
        if type(sources) is not list or any(type(s) is not dict or type(s.get("id")) is not str for s in sources):
            raise SettingsError("e32_rejected", "sources", error="invalid_sources")
        user_input["ha_sources"] = [s["id"] for s in sources if s.get("type") == "ha"]
        user_input["ble_sources"] = [s["id"] for s in sources if s.get("type") == "ble"]
        if len(user_input["ha_sources"]) + len(user_input["ble_sources"]) != len(sources):
            raise SettingsError("e32_rejected", "sources", error="invalid_sources")
        user_input["bluetooth_first"] = bool(sources) and sources[0].get("type") == "ble"
    if model["features"]["resets"] and "resets" in values:
        if type(values["resets"]) is not list:
            raise SettingsError("e32_resets_invalid", "resets", line="1", text="")
        user_input["resets"] = values["resets"]
    if model["features"]["smart_warm_up"] and SMART_WARM_UP_FIELD in values:
        user_input[SMART_WARM_UP_FIELD] = values[SMART_WARM_UP_FIELD]
    # "Off until" as shown keeps the stored moment exactly (the form's own text, with its seconds).
    if "inactive_until" in values and values["inactive_until"] != model["inactive_until"]:
        user_input["inactive_until"] = values["inactive_until"] or None
    # A new room starts with the standard program, as the form fills it in, unless the user chose none (issue #7).
    if room is None and values.get("standard_program", True) is False:
        user_input["program"] = ""
    return user_input


async def save_rooms(hass, entry, item, values):
    hub, link = _link(hass, entry)
    if item is None:
        raise SettingsError("unknown_section")  # the list itself has nothing to save
    plan = await _plan_now(link)
    room = None if item == NEW else plan_room(plan, item)
    if item != NEW and room is None:
        raise SettingsError("e32_room_missing", room=item)
    if room is not None and values.get("remove") is True:
        try:
            await remove_room(hass, entry, link, item)  # the same removal as Configure → Rooms
        except HomeAssistantError as err:
            raise _failure(err) from None
        return {"removed": True, "id": item, "name": room.get("name") or item}
    model = room_model(hass, entry, hub, plan, room)
    if room is None and model["full"]:
        raise SettingsError("e32_room_limit")
    editor = RoomEditor(hass, entry, plan)
    try:
        plan_values = editor._e32_room_values(room_input(editor, room, model, values), room, editor._e32_ble_options(room))
        saved = await write_room(link, room, plan_values)
    except FlowError as err:
        raise _refusal(err) from None
    except HomeAssistantError as err:
        raise _failure(err) from None
    return await read_rooms(hass, entry, saved)


register_section("rooms", read_rooms, save_rooms)
