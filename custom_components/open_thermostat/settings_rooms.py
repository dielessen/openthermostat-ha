"""The settings panel's section Rooms (1.4; 1.4.1: everything of a room on its screen, docs/engineering/
HA-INSTELPANEEL-FASE2.nl.md 3.1 and 5, the model in the 1.4.1 contract §1).

Three screens, one section ``rooms`` (settings.py registry):

- the list (item None): every room of the E32 plan, in its order, with its state, heating type and the entities
  whose live values the panel shows beside it (the room's thermostat and temperature sensor in ``hass.states``);
- one room (item = its id, also ``#room/<id>`` from the room card): its name, Heating (On / Heat along only /
  Off), heating type, temperature sources, setting device, temperature without a week program, the week program
  (a summary: the planner edits it), reset times, Smart warm-up, "Off until", and since 1.4.1 its window and door
  contacts with their pause delays, its radiator valves with their models, its persons with its own away
  temperature, its temperature limits and its notifications;
- a new room (item ``new-room``, never a room id: those have no hyphen).

The model comes from what Home Assistant already holds: the room plan it last read from the E32 (read once when
there is none yet), the comfort and notification settings of the entry, the hub, the entity and device registries
and the names in ``hass.states``. The radiator valves are the E32's own record (``GET /config/heating/trv``): read
when a room's screen is read, at most once per VALVES_FRESH_S, so one save (its token check, the save, the fresh
model) signs in once. Live values never enter the model (the token would change with every reading): battery,
last report and measured values are in ``hass.states`` through the entity IDs the model names.

Saving uses the room form's own rules (e32_room_flow): the panel's fields are laid over what the form would send
for the room as stored (RoomEditor.room_input), validated by the same methods (E32RoomFlow._e32_room_values for the
plan, room_parts for the contacts, persons and valves) and written by the same function (save_room: the plan with
only the fields that differ, on top of the plan the E32 holds then; then the valves, the contacts and the persons,
each only when it differs). The room's notifications use the form's notifications_flow.room_change. Configure →
Rooms (and Configure → Notifications → a room) and the panel therefore give the same result for the same input
(test_settings_rooms.py).

Values the panel sends (any key left out keeps the stored value; each top key whole): ``name``, ``state``,
``emitter``, ``sources`` ([{"type": "ha" | "ble", "id"}], the first fresh one leads), ``setpoint_entity`` ("" for
none), ``fallback_temperature`` (the user's unit), ``resets`` ([{"days", "time", "temperature" | "state"}], E32
1.4), ``smart_warm_up`` ("house" | "on" | "off", E32 1.4), ``inactive_until`` ("YYYY-MM-DDTHH:MM" local, "" for
none), ``standard_program`` (a new room only), ``remove`` (true: remove the room), and since 1.4.1 ``contacts``
({windows, doors, window_delay_s, door_delay_s}; a delay null: the house value), ``radiator_valves`` ({list:
[{entity_id, model} | {id, role?, keep_open?}], control}), ``persons`` ({entity_ids, away_temperature}; null: the
house away temperature), ``minimum_temperature``, ``maximum_temperature`` (the user's unit) and ``notifications``
({on, kinds}). An error names the panel's field: the top key it belongs to.
"""
from __future__ import annotations

from collections import namedtuple
import time

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from . import room_away
from .const import DOMAIN
from .e32_comfort import CONTACT_CLASSES, comfort_options, doors_of, windows_of
from .e32_room_flow import (LIMITS_CENTI_C, MAX_ROOMS, MAX_SOURCES, SMART_WARM_UP_FEATURE, SMART_WARM_UP_FIELD,
                            E32RoomFlow, FlowError, RoomEditor, model_candidates, remove_room, resets_supported,
                            room_parts, save_room, shown, shown_reset, valve_context)
from .e32_setting_device import default_program
from .heating_link import ble_device_identifier, label, number
from .room_plan import plan_room, until_datetime
from .settings import SettingsError, _hub, language, register_section

NEW = "new-room"
# The room form's fields (and sections) under the panel's name: the two source lists are the one list "sources",
# the sections are the contract's top keys.
FIELDS = {"ha_sources": "sources", "ble_sources": "sources", "window": "contacts", "persons": "persons",
          "valves": "radiator_valves", "kinds": "notifications"}
# Errors of the form that belong to a field of the panel although the form puts them on the whole form.
FIELD_OF = {"e32_sources_count": "sources", "e32_rejected_sources": "sources", "e32_rejected_duplicate_source": "sources",
            "e32_rejected_setpoint": "setpoint_entity", "e32_rejected_resets": "resets",
            "e32_resets_too_many": "resets",
            # 1.4.1: the contacts, the radiator valves and the notifications of the room
            "contacts_invalid": "contacts", "not_contact_sensor": "contacts", "contact_window_and_door": "contacts",
            "contact_delay_invalid": "contacts", "e32_valve_room_limit": "radiator_valves",
            "e32_valve_limit": "radiator_valves", "e32_valves_rejected": "radiator_valves",
            "e32_valve_model_missing": "radiator_valves", "notification_invalid": "notifications",
            "notification_kinds_needed": "notifications"}
LIMIT_KEYS = (("minimum_temperature", "minimum"), ("maximum_temperature", "maximum"))
# The radiator valve record is read at most this often for the room screens (each read is one E32 sign-in).
VALVES_FRESH_S = 30
VALVE_CACHE = "settings_room_valves"
UPDATE_REQUIRED = "controller_room_plan_update_required"

# What a room's screen is made of: its model, and what a save needs besides it (the valve context, the reason the
# valves are not in the model).
RoomState = namedtuple("RoomState", "model valve_ctx valve_error")


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


def _limits_field(values, model):
    """The limit field an e32_limits_invalid (or a program or reset time outside new limits) belongs to: a limit
    the panel changed that is out of range or past the other, else the temperature without a week program when it
    was changed, else the changed limit."""
    limits = model["limits"]
    changed = [key for key, shown_key in LIMIT_KEYS if key in values and values[key] != limits[shown_key]]

    def value(key, shown_key):
        found = values.get(key, limits[shown_key])
        return float(found) if type(found) in (int, float) and type(found) is not bool else None
    low, high = (value(key, shown_key) for key, shown_key in LIMIT_KEYS)
    for key, found in zip((key for key, _ in LIMIT_KEYS), (low, high)):
        if key in changed and (found is None or not limits["lowest"] <= found <= limits["highest"]):
            return key
    if changed and low is not None and high is not None and low > high:
        return changed[-1]
    if not changed or ("fallback_temperature" in values and values["fallback_temperature"] != model["fallback_temperature"]):
        return "fallback_temperature"
    return changed[0]


def _refusal(err, values, model):
    """A FlowError of the room form on the panel's field (the contract's top keys)."""
    field = FIELDS.get(err.field, err.field)
    limits_changed = any(key in values and values[key] != model["limits"][shown_key] for key, shown_key in LIMIT_KEYS)
    if err.key == "e32_limits_invalid" or (field in ("program", "resets") and field not in values and limits_changed):
        field = _limits_field(values, model)
    elif field in ("base", "program"):
        field = FIELD_OF.get(err.key, "base")
    return SettingsError(err.key, field, **err.placeholders)


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
    return {"resets": resets_supported(plan), "smart_warm_up": SMART_WARM_UP_FEATURE in features,
            "room_away": room_away.supported(plan)}


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


# -- the parts of a room that are not in the E32 plan (1.4.1) --------------------------------------------------------

def _name(hass, entity_id, fallback=None):
    """The name Home Assistant shows for an entity, else the fallback or the entity ID."""
    state = hass.states.get(entity_id) if entity_id else None
    return state.name if state is not None else (fallback or entity_id)


def _ordered(items):
    return [{"entity_id": entity_id, "name": name} for _rank, _key, entity_id, name in sorted(items)]


def _own_entity(registry, entity_id):
    item = registry.async_get(entity_id)
    return item is not None and item.platform == DOMAIN


def contact_choices(hass, chosen=()):
    """The binary sensors a room may take as window or door contact (the form's picker: the device classes window,
    door, opening and garage door, in that order, each by name), then the room's own ones of another class or
    without a state (they stay); never an OpenThermostat entity."""
    registry, found, seen = er.async_get(hass), [], set()
    for state in hass.states.async_all("binary_sensor"):
        kind = state.attributes.get("device_class")
        if (kind not in CONTACT_CLASSES and state.entity_id not in chosen) or _own_entity(registry, state.entity_id):
            continue
        rank = CONTACT_CLASSES.index(kind) if kind in CONTACT_CLASSES else len(CONTACT_CLASSES)
        found.append((rank, state.name.casefold(), state.entity_id, state.name))
        seen.add(state.entity_id)
    found += [(len(CONTACT_CLASSES), entity_id, entity_id, entity_id) for entity_id in chosen if entity_id not in seen]
    return _ordered(found)


def person_choices(hass, chosen=()):
    """The people Home Assistant knows (its persons, by name), then the room's own choices of another kind (a
    group, a device tracker, a switch: the form takes those too)."""
    found = [(0, state.name.casefold(), state.entity_id, state.name) for state in hass.states.async_all("person")]
    known = {item[2] for item in found}
    found += [(1, _name(hass, entity_id).casefold(), entity_id, _name(hass, entity_id))
              for entity_id in chosen if entity_id not in known]
    return _ordered(found)


def contacts_model(hass, entry, room_id):
    """The room's window and door contacts as stored, its own pause delays (None: the house value) and the house's."""
    settings = comfort_options(entry)
    windows = windows_of(settings, room_id) if room_id else []
    doors = doors_of(settings, room_id) if room_id else []
    return {"windows": windows, "doors": doors,
            "window_delay_s": settings["contact_delays"].get(room_id) if room_id else None,
            "door_delay_s": settings["door_delays"].get(room_id) if room_id else None,
            "house": {"window_delay_s": settings["contact_delay_s"], "door_delay_s": settings["door_delay_s"]},
            "choices": contact_choices(hass, windows + doors)}


def persons_model(hass, entry, hub, room, unit, features):
    """The room's persons (empty: the room follows the house), its own away temperature (None: the house value, or
    an E32 without plan.room_away.v1) and the house away temperature the E32 reports (None while it reports none)."""
    from .e32_house import house_away
    room_id = (room or {}).get("id")
    ids = list(comfort_options(entry)["room_persons"].get(room_id, [])) if room_id else []
    own = room_away.room_away(room) if room and features["room_away"] else None
    house = number((house_away(hub) or {}).get("target_c"), 5, 25)
    low, high = room_away.LIMITS_CENTI_C
    return {"entity_ids": ids, "away_temperature": None if own is None else shown(own, unit),
            "house_away_temperature": None if house is None else shown(round(house * 100), unit),
            "away_range": {"minimum": shown(low, unit), "maximum": shown(high, unit)},
            "choices": person_choices(hass, ids)}


def notifications_model(hass, entry, room_id):
    """The room's notifications as Configure → Notifications → the room shows them, and who gets them (the names
    of the room's own persons; empty: everyone with a phone)."""
    from .notifications import ROOM_KINDS, notification_options
    from .notifications_flow import room_recipients, shown_room
    current = shown_room(notification_options(entry), room_id) if room_id else {"on": False, "kinds": list(ROOM_KINDS)}
    return {"on": current["on"], "kinds": list(current["kinds"]), "kind_choices": list(ROOM_KINDS),
            "recipients": room_recipients(hass, entry, room_id) if room_id else []}


async def _valve_record(hass, entry):
    """("ok", the E32's valve record, its BLU Gateway valves or None), ("update_required", None, None) on firmware
    without one, or ("unreadable", None, the reason); a read is kept VALVES_FRESH_S (not a failed one)."""
    from .e32_valves import valve_link
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    cached = state.get(VALVE_CACHE) if isinstance(state, dict) else None
    if cached is not None and time.monotonic() - cached[0] < VALVES_FRESH_S:
        return cached[1]
    link = valve_link(hass, entry)
    if link is None:
        return "unreadable", None, "no_connection"
    try:
        config, gateway = await link.async_read_with_gateway()
    except HomeAssistantError as err:
        key = getattr(err, "translation_key", None)
        if key != "e32_update_required":
            return "unreadable", None, (getattr(err, "translation_placeholders", None) or {}).get("error") or key or "unknown"
        result = ("update_required", None, None)
    else:
        result = ("ok", config, gateway)
    if isinstance(state, dict):
        state[VALVE_CACHE] = (time.monotonic(), result)
    return result


def _forget_valve_record(hass, entry):
    """After a valve write: the next screen reads the record again."""
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if isinstance(state, dict):
        state.pop(VALVE_CACHE, None)


def _driven(model):
    """How the E32 drives a valve of this model: by its position, by temperature (no position readback), or Home
    Assistant drives it."""
    from .e32_valves import HA_MODEL, NO_POSITION_MODELS
    if model == HA_MODEL:
        return "home_assistant"
    return "temperature" if model in NO_POSITION_MODELS else "position"


def _valve(hass, ctx, route, lang):
    from .e32_valves import shown_name
    if route.gateway:
        kind, name = "gateway", route.friendly or shown_name(route.name, lang)
    else:
        kind = "kept" if route.entity_id is None else "zigbee2mqtt" if route.direct else "home_assistant"
        name = _name(hass, route.entity_id, route.friendly or route.name)
    return {"entity_id": route.entity_id, "id": route.name, "name": name, "model": route.model, "kind": kind,
            "choose_model": route.entity_id is not None and ctx.finder.z2m_details(route.entity_id) is not None,
            "driven": _driven(route.model), "role": ("loop" if route.role == "loop" else "radiator") if route.gateway else None,
            "keep_open": bool(route.keep_open)}


async def radiator_valves_model(hass, entry, ctx):
    """The room's radiator valves as the E32 stores them (its order), the valve control (on: the valves follow the
    room), the models a Zigbee2MQTT valve can get (the step e32_room_valve_models, its order and words), the climate
    entities the form's picker offers, the BLU Gateway valves it offers, and the limits."""
    from .e32_valves import HA_MODEL, MAX_CLASSIC_VALVES_PER_ROOM, MAX_VALVES_PER_ROOM, ZIGBEE_MODELS, shown_name
    from .options_navigation import async_flow_texts
    lang, registry = language(hass), er.async_get(hass)
    routes = sorted([*ctx.stored, *ctx.gateway_stored], key=lambda r: ctx.position.get(r.name, len(ctx.records)))
    words = await async_flow_texts(hass, "e32_valve_model")
    excluded = set(ctx.excluded)
    choices = _ordered([(0, state.name.casefold(), state.entity_id, state.name) for state in hass.states.async_all("climate")
                        if state.entity_id not in excluded and not _own_entity(registry, state.entity_id)])
    stored = {r.name: r for r in ctx.gateway_stored}
    gateway = [{"id": name, "name": (ctx.gateway_labels.get(name) or {}).get("label")
                or (stored[name].friendly if name in stored else None) or shown_name(name, lang)}
               for name in ctx.gateway_options]
    return {"list": [_valve(hass, ctx, route, lang) for route in routes], "control": bool(ctx.control),
            "models": [{"key": key, "name": words.get(key, key)} for key in (HA_MODEL, *ZIGBEE_MODELS)],
            "choices": choices, "gateway_choices": gateway, "max": MAX_CLASSIC_VALVES_PER_ROOM,
            "max_with_gateway": MAX_VALVES_PER_ROOM}


# -- one room --------------------------------------------------------------------------------------------------------

async def room_state(hass, entry, hub, plan, room):
    """One room's screen (``room`` None: a new room), with the valve context a save needs."""
    editor = RoomEditor(hass, entry, plan)
    unit, d, features = editor._unit(), editor._e32_defaults(room), _features(plan)
    stored = room or {}
    room_id = stored.get("id", "")
    until = until_datetime(stored) if room is not None else None
    low, high = LIMITS_CENTI_C
    model = {
        "id": room_id, "name": d["name"], "state": d["state"], "emitter": d["emitter"],
        "states": editor._e32_states(room),
        "sources": [{"type": s.get("type"), "id": s.get("id")} for s in stored.get("sources") or [] if type(s) is dict],
        "setpoint_entity": d["setpoint_entity"] or "",
        "fallback_temperature": d["fallback_temperature"], "unit": unit,
        "limits": {"minimum": d["minimum_temperature"], "maximum": d["maximum_temperature"],
                   "lowest": shown(low, unit), "highest": shown(high, unit)},
        "inactive_until": _local(until.timestamp()) if until is not None else "",
        "features": features, "max_sources": MAX_SOURCES, "max_rooms": MAX_ROOMS,
        "ble": _ble(hass, entry, hub, plan), "own": _own(hass, editor),
        "contacts": contacts_model(hass, entry, room_id),
        "persons": persons_model(hass, entry, hub, room, unit, features),
        "notifications": notifications_model(hass, entry, room_id),
    }
    if room is None:  # the standard program "Workdays and weekend", as the form fills it in for a new room (#7)
        model["program"] = program_groups(default_program(500, 3000), unit)
        model["standard_program"] = True
        model["full"] = len(plan.get("rooms") or []) >= MAX_ROOMS
    else:
        model["program"] = program_groups(room.get("schedule"), unit)
        model["entities"] = _entities(hass, hub, room["id"])
    if features["resets"]:
        model["resets"] = [shown_reset(r, unit) for r in stored.get("resets") or [] if type(r) is dict]
    if features["smart_warm_up"]:
        choice = stored.get(SMART_WARM_UP_FIELD)
        model["smart_warm_up"] = choice if choice in ("on", "off") else "house"
    status, config, extra = await _valve_record(hass, entry)
    ctx = valve_context(hass, entry, config, room_id, room, extra) if status == "ok" else None
    features["radiator_valves"] = status != "update_required"
    model["radiator_valves"] = await radiator_valves_model(hass, entry, ctx) if ctx is not None else None
    return RoomState(model, ctx, extra if status == "unreadable" else None)


async def read_rooms(hass, entry, item):
    hub, link = _link(hass, entry)
    plan = await _plan_now(link)
    if item is None:
        return list_model(hass, entry, hub, plan)
    if item == NEW:
        return (await room_state(hass, entry, hub, plan, None)).model
    room = plan_room(plan, item)
    if room is None:
        raise SettingsError("e32_room_missing", room=item)
    return (await room_state(hass, entry, hub, plan, room)).model


# -- saving ----------------------------------------------------------------------------------------------------------

def _contacts_input(user_input, model, sent):
    """The form's "window" section with the panel's contacts laid over it (the delays in seconds; null: the house
    value, which the room then follows)."""
    shown_contacts = model["contacts"]
    if type(sent) is not dict:
        raise SettingsError("contacts_invalid", "contacts")
    windows, doors = sent.get("windows", shown_contacts["windows"]), sent.get("doors", shown_contacts["doors"])
    if type(windows) is not list or type(doors) is not list:
        raise SettingsError("contacts_invalid", "contacts")
    window = {**user_input["window"], "contacts": windows, "door_contacts": doors}
    for key, field in (("window_delay_s", "contact_delay"), ("door_delay_s", "door_delay")):
        if key not in sent:
            continue
        seconds = shown_contacts["house"][key] if sent[key] is None else sent[key]
        if type(seconds) is not int:
            raise SettingsError("contact_delay_invalid", "contacts")
        window[field] = seconds / 60  # the form's minutes
    user_input["window"] = window


def _persons_input(user_input, model, sent):
    shown_persons = model["persons"]
    if type(sent) is not dict or type(sent.get("entity_ids", [])) is not list:
        raise SettingsError("presence_entity_invalid", "persons")
    away = sent.get("away_temperature", shown_persons["away_temperature"])
    if away is not None and not model["features"]["room_away"]:
        raise SettingsError(UPDATE_REQUIRED, "persons")
    user_input["persons"] = {"persons": sent.get("entity_ids", shown_persons["entity_ids"]), "away_temperature": away}


def _valves_input(user_input, state, sent):
    """The form's "valves" section from the panel's list, and the models the panel changed ({entity: model}, as the
    step e32_room_valve_models gives them); refused on firmware without valves or while the record is unreadable."""
    from .e32_valves import HA_MODEL, ZIGBEE_MODELS
    ctx = state.valve_ctx
    if ctx is None:
        if state.valve_error is not None:
            raise SettingsError("e32_unreachable", "radiator_valves", error=state.valve_error)
        raise SettingsError(UPDATE_REQUIRED, "radiator_valves")
    invalid = SettingsError("e32_rejected", "radiator_valves", error="invalid_valves")
    shown_list = state.model["radiator_valves"]["list"]
    items = sent.get("list", shown_list) if type(sent) is dict else None
    control = sent.get("control", ctx.control) if type(sent) is dict else None
    if type(items) is not list or type(control) is not bool:
        raise invalid
    kept = {r.name for r in ctx.stored if r.entity_id is None}
    part = {"valves": [], "kept": [], "gateway_valves": [], "loop_valves": [], "keep_open": [], "control": control}
    wanted = {}
    for item in items:
        if type(item) is not dict:
            raise invalid
        entity, name = item.get("entity_id"), item.get("id")
        if entity is not None:
            if type(entity) is not str:
                raise invalid
            part["valves"].append(entity)
            if item.get("model") is not None:
                wanted[entity] = item["model"]
        elif name in kept:
            part["kept"].append(name)
        elif name in ctx.gateway_options:
            if item.get("role") not in (None, "radiator", "loop") or item.get("keep_open") not in (None, True, False):
                raise invalid
            part["gateway_valves"].append(name)
            if item.get("role") == "loop":
                part["loop_valves"].append(name)
            if item.get("keep_open") is True:
                part["keep_open"].append(name)
        else:
            raise SettingsError("e32_valve_entity_invalid", "radiator_valves")
    # A model as shown is no choice (the valve keeps its route); a changed one is the Advanced step's choice.
    stored = {r.entity_id: r for r in ctx.stored if r.entity_id}
    candidates = {found[0] for found in model_candidates(part, ctx)}
    models = {}
    for entity, chosen in wanted.items():
        if chosen == (stored.get(entity) or ctx.finder.route(entity)).model:
            continue
        if entity not in candidates or chosen not in (HA_MODEL, *ZIGBEE_MODELS):
            raise SettingsError("e32_valve_model_missing", "radiator_valves")
        models[entity] = chosen
    user_input["valves"] = part
    return models


def room_input(editor, room, state, values):
    """What the room form would get for this save: the room as stored, with the panel's fields laid over it; and
    the models of the radiator valves the panel changed."""
    model = state.model
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
    # 1.4.1: the parts of the room that were only in Configure.
    user_input["limits"] = {**user_input["limits"], **{key: values[key] for key, _ in LIMIT_KEYS if key in values}}
    if "contacts" in values:
        _contacts_input(user_input, model, values["contacts"])
    if "persons" in values:
        _persons_input(user_input, model, values["persons"])
    models = _valves_input(user_input, state, values["radiator_valves"]) if "radiator_valves" in values else None
    return user_input, models


def _notifications_input(model, values):
    """(on, kinds) of the room's notifications as the panel sends them, or None when it sends none."""
    if "notifications" not in values:
        return None
    sent, current = values["notifications"], model["notifications"]
    if type(sent) is not dict:
        raise SettingsError("notification_invalid", "notifications")
    return sent.get("on", current["on"]), sent.get("kinds", current["kinds"])


async def save_rooms(hass, entry, item, values):
    from .notifications import notification_options, save_notifications
    from .notifications_flow import room_change
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
    state = await room_state(hass, entry, hub, plan, room)
    model = state.model
    if room is None and model["full"]:
        raise SettingsError("e32_room_limit")
    editor = RoomEditor(hass, entry, plan)
    user_input, models = room_input(editor, room, state, values)
    notify = _notifications_input(model, values)
    try:
        plan_values = editor._e32_room_values(user_input, room, editor._e32_ble_options(room))
        parts = room_parts(hass, entry, room, user_input, state.valve_ctx, models)
        if notify is not None:  # checked before anything is written
            room_change(notification_options(entry), item, *notify)
        saved = await save_room(hass, entry, link, room, plan_values, parts)
    except FlowError as err:
        if getattr(err, "saved", None) is not None:  # the room is stored, its valves refused
            _forget_valve_record(hass, entry)
            err.placeholders.setdefault("room", err.saved)  # a new room: the panel opens it, as the form does
        raise _refusal(err, values, model) from None
    except HomeAssistantError as err:
        raise _failure(err) from None
    if parts.valves_changed:
        _forget_valve_record(hass, entry)
    if notify is not None and (changed := room_change(notification_options(entry), saved, *notify)) is not None:
        save_notifications(hass, entry, changed)  # the form's own write: no reload
    return await read_rooms(hass, entry, saved)


register_section("rooms", read_rooms, save_rooms)
