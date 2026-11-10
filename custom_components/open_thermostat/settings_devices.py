"""The settings panel's section Devices (1.4; settings.py registers it, the screens are
frontend/openthermostat-settings-devices.js): the three blocks of the E32's page System → Devices.

- ``None`` (``#devices``): the Bluetooth sensors (rename, forget: collected and saved together, because every save
  restarts the E32 about 30 seconds later; e32_bluetooth.async_save_sensors), the Shelly devices (remove a device,
  remove valves from a BLU Gateway: an action each, ``{"action": "shelly_remove", "device": <id>}`` and
  ``{"action": "valves_remove", "valves": ["<n>:<valve>"]}``; e32_devices.async_change) and, read-only, the devices
  on the boiler bus as Configure → E32 devices names them.
- ``shelly-add``: add a Shelly device by its address. One save: the E32 tests the address (e32_devices.async_probe,
  up to 16 s), then the device goes into the record with what it does ("auto": as the device says, kind_of), an
  optional name and its password. The password goes to the E32 only: it is in no model, no error and no log, and
  Home Assistant keeps nothing of it.
- ``valve-add``: add a valve to a BLU Gateway by its number (200–299), as Configure does.
- ``batteries`` (1.4.2, plan 3.5): every battery of the installation on one list (device_battery.collect: the E32's
  Bluetooth sensors, the valves, window and door contacts, setting devices, Home Assistant temperature sources), low
  first, under ``live.devices`` (a battery that reports a new figure never makes the save "changed elsewhere"), and
  the one battery limit ``limit_pct`` (15, 20, 25 or 30 %) with its save key ``limit_pct``: stored in the entry
  options without a reload; "Batteries low" counts again and the dashboard's badges follow. No sign-in on the E32.

1.4.2 (plan 3.9): every block screen has its own address, read and saved on its own (deep links and the browser's
back button work; the panel no longer keeps a screen in ``history.state``):

- ``bluetooth``: the paired sensors, each with the room it measures for (``live.bluetooth``), the Search state;
- ``pair``: the search (``live.searching``, ``live.discovery``, ``live.discovery_ended_s``); ``pair/<address>``: the
  pairing form of one device the search heard (``heard``), its save pairs it as the action ``pair`` does;
- ``sensor/<address>``: one sensor: its own name (a sensor without one is named after its room, ``automatic``), the
  room it measures for (``measures_for``: one plan write makes it that room's first temperature source and takes it
  out of every other room) and Forget sensor (``forget``);
- ``shelly``, ``device/<id>`` (remove the device, remove valves) and ``bus`` (read-only).

The Search (``ble.discovery.v1``, E32 1.4.2): the E32 names a requested search on its own (``discovery``:
idle/queued/running, ``discovery_ended_s``), so Search is off only while one is queued or running; firmware without
it keeps the 95 s rule (SEARCH_SECONDS).

One sign-in reads the Bluetooth list, the Shelly record and the Shelly devices' state. What only informs (the
readings and battery of a sensor through its Home Assistant entities, the rooms that use it, a device's state, the
boiler bus, what a save just did) is under ``live``, left out of the token (settings.LIVE).

Actions (1.4.1, ``open_thermostat/settings/action``, plan 3.4): what the E32's page System → Devices does besides
saving, each with the requests that page makes and the integration's E32 session (one sign-in per action):

- ``scan`` → ``{"started": true}``: the Bluetooth search (``POST /config/bluetooth/scan``, about 30 s once the E32's
  current scan ends); ``scan_result`` → ``{"sensors": [{address, name, rssi, kind, encryption, known}], "done",
  "paired", "max", "full"}``: what it hears (the ``GET /config/bluetooth`` "nearby_devices", strongest first; ``kind``
  and ``encryption`` the E32 page's guess from the name, None without one; ``known`` already paired). ``done`` once
  the E32 scans no more or SEARCH_SECONDS after the start (with paired sensors the E32 keeps scanning for them).
- ``pair {address, name, profile?, encryption?, bindkey?}`` → ``{"saved": true, "restart": bool, "restart_in_s"?}``:
  the sensor added to the list with the 1.4 save's ETag write (every other row keeps its key), then read back. The
  E32 restarts by itself about 30 s later (``restart`` false: later, after an update or boiler test). The bindkey goes
  to the E32 only: in no answer, error or log.
- ``pill_roles {device?}`` → ``{"device", "probes": [{c, role, health, t_c}], "roles": {"<c>": role}, "choices",
  "in_use": {role: circuit}}``: The Pill's probes (``device`` its id or number; left out: the only Pill);
  ``set_pill_roles {device?, roles: {"<c>": role | null}}`` → ``{"saved": true, "roles"}``: the whole record written
  with that Pill's probes (as "Save probe roles"). Home Assistant's probe sensors follow the E32's fw/state/probes
  (e32_shelly.remove_stale_entities removes a role's sensor once the E32 no longer reports it).
- ``gateway_scan {gateway}`` → ``{"started": true}`` (``POST /config/shelly/scan {"n"}``); ``gateway_scan_result
  {gateway}`` → ``{"state", "done", "valves": [{id, name, known}], "more", "full", "reason"?, "error"?}`` from ``GET
  /status/shelly`` "scan". Adding a found valve is the ``valve-add`` save.
"""
from __future__ import annotations

import re
import time

from .const import DOMAIN
from .settings import SettingsError, register_section

# The longest a Bluetooth search the panel started can take: it waits for the current scan to end (60 s at most with
# paired sensors, BleScanPlan) and then listens 30 s; after that the result counts as done.
SEARCH_SECONDS = 95
# entry_id -> monotonic start of the last Bluetooth search the panel started (RAM only).
_SEARCHES: dict[str, float] = {}
CLOCK = time.monotonic  # the clock of SEARCH_SECONDS (a test moves it)
# 1.4.2: the requested Search on its own (BleScanLifecycle.h; CONTRACT-1.4.2 §1).
DISCOVERY_FEATURE = "ble.discovery.v1"
DISCOVERY_STATES = ("idle", "queued", "running")
# The screens of the section by address (plan 3.9): the blocks, and one sensor, one heard device, one Shelly device.
BLOCKS = ("bluetooth", "pair", "shelly", "bus")
ONE = re.compile(r"(sensor|pair)/([0-9a-f]{12})")
DEVICE = re.compile(r"device/([A-Za-z0-9][A-Za-z0-9_.:-]{0,63})")
# The E32's refusals of the panel's actions that Configure never meets, as the panel's codes.
PANEL_ERRORS = {"duplicate_probe_role": "shelly_probe_role_duplicate", "invalid_probe": "shelly_probe_invalid",
                "invalid_probe_role": "shelly_probe_invalid", "duplicate_probe": "shelly_probe_invalid",
                "invalid_probes": "shelly_probe_invalid", "scan_busy": "scan_busy"}
# The Bluetooth page's refusals (bluetooth.js errors) as the panel's codes, with the field they belong to.
BLE_ERRORS = {"invalid_device_name": ("ble_name_invalid", "name"), "bluetooth_storage_full": ("ble_storage_full", "base"),
              "bluetooth_resources_unavailable": ("e32_settings_busy", "base"),
              "invalid_device_address": ("ble_address_invalid", "address"),
              "duplicate_device_address": ("ble_already_paired", "address"), "invalid_device_count": ("ble_full", "base"),
              "device_settings_too_large": ("ble_full", "base"), "invalid_device_key": ("ble_key_invalid", "bindkey"),
              "unsupported_device_profile": ("ble_profile_invalid", "profile"),
              "invalid_device_encryption": ("ble_encryption_invalid", "encryption"),
              "bluetooth_scan_not_started": ("ble_scan_not_started", "base")}


def _link(hass, entry):
    from .e32_system import link_for
    link = link_for(hass, entry)
    if link is None:
        raise SettingsError("connect_e32")
    return link


def _failure(err):
    """A failed E32 request (or a Shelly refusal) as the flow's error key, its field and placeholders."""
    from .e32_devices import ERRORS, FIELDS, Refused
    from .e32_system import failure
    if isinstance(err, Refused):
        if err.code == "unknown_command":  # firmware before the gateway search
            return SettingsError("e32_settings_update_required", error=err.code)
        key = ERRORS.get(err.code) or PANEL_ERRORS.get(err.code, "shelly_rejected")
        return SettingsError(key, FIELDS.get(key, "base"), error=err.code)
    if str(err) == "controller_update_required":
        return SettingsError("shelly_unsupported")
    key, placeholders = failure(err)
    return SettingsError(key, **placeholders)


async def _read_all(link, bluetooth=True, shelly=True):
    """(bluetooth value or None, Shelly record or None, Shelly status or None) in one sign-in; a part this firmware
    does not have (or the screen does not need) is None."""
    from .controller_link import ControllerLinkError

    async def read(client):
        ble = record = None
        try:
            if bluetooth:
                ble, _tag = await client.async_bluetooth()
        except ControllerLinkError as err:
            if str(err) != "controller_update_required":
                raise
            ble = None
        try:
            if shelly:
                record = await client.async_shelly()
        except ControllerLinkError as err:
            if str(err) != "controller_update_required":
                raise
            record = None
        status = None
        if record is not None:
            try:
                status = await client.async_shelly_status()
            except ControllerLinkError:
                status = None  # the list without its state is still the list
        return ble, record, status
    return await link.async_call(read)


def _hub(hass, entry):
    return (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get("heating_hub")


def _plan_rooms(hub):
    """The rooms of the room plan Home Assistant last read ([] before the first read)."""
    plan = getattr(getattr(hub, "plan", None), "plan", None)
    rooms = plan.get("rooms") if type(plan) is dict else None
    return [room for room in rooms if type(room) is dict and type(room.get("id")) is str] if type(rooms) is list else []


def _measures(room, address):
    """0 when the sensor is the room's first temperature source, 1 when it is a later one, None when not at all."""
    sources = [s for s in room.get("sources") or [] if type(s) is dict]
    for place, source in enumerate(sources):
        if source.get("type") == "ble" and source.get("id") == address:
            return min(place, 1)
    return None


def measures_for(rooms, address):
    """The id of the room a sensor measures for: the room whose first source it is, else the first room that lists it,
    else None."""
    using = sorted((place, k, room["id"]) for k, room in enumerate(rooms)
                   if (place := _measures(room, address)) is not None)
    return using[0][2] if using else None


def _room_name(room):
    name = room.get("name")
    return name.strip() if type(name) is str and name.strip() else room["id"]


def _ble_live(hass, entry, sensors, nearby=None):
    """{address: {"rooms", "room_ids", "measures_for", "temperature", "humidity", "battery", "shown", "automatic",
    "rssi"}}: the rooms that measure with each sensor (the room plan Home Assistant last read), the one it measures for
    (``measures_for``), its Home Assistant entities, whose state the panel shows, the name Home Assistant shows for it
    (``shown``; ``automatic`` when the E32 has no own name for it: it is named after its room) and its signal when the
    last search heard it."""
    from homeassistant.helpers import device_registry as dr, entity_registry as er
    from .heating_link import BLE_METRICS, ble_broadcast_name, ble_device_identifier
    hub = _hub(hass, entry)
    rooms = _plan_rooms(hub)
    registry, devices, prefix = er.async_get(hass), dr.async_get(hass), getattr(hub, "prefix", None)
    heard = {row["address"]: row.get("rssi") for row in nearby or []}
    live = {}
    for sensor in sensors:
        address = sensor["address"]
        using = [room for room in rooms if _measures(room, address) is not None]
        own = (sensor.get("name") or "").strip()
        automatic = ble_broadcast_name({"id": address, "name": own})
        device = (devices.async_get_device_by_identifier(ble_device_identifier(prefix, address), entry.entry_id)
                  if prefix else None)
        shown = own if not automatic else (device.name if device is not None and device.name else own)
        live[address] = {"rooms": [_room_name(room) for room in using], "room_ids": [room["id"] for room in using],
                         "measures_for": measures_for(rooms, address), "shown": shown or address,
                         "automatic": automatic, "rssi": heard.get(address)}
        for metric in BLE_METRICS:
            live[address][metric] = (registry.async_get_entity_id("sensor", DOMAIN, f"{prefix}_e32_ble_{address}_{metric}")
                                     if prefix else None)
    return live


def _ids_stale(hass, entry, address):
    """True when an entity of the sensor still has an ID from an older device name (Tidy entity IDs renames it)."""
    from homeassistant.helpers import device_registry as dr, entity_registry as er
    from homeassistant.util import slugify
    from .heating_link import BLE_METRICS, ble_device_identifier
    prefix = getattr(_hub(hass, entry), "prefix", None)
    if not prefix:
        return False
    device = dr.async_get(hass).async_get_device_by_identifier(ble_device_identifier(prefix, address), entry.entry_id)
    name = (device.name_by_user or device.name) if device is not None else None
    if not name:
        return False
    registry, slug = er.async_get(hass), slugify(name)
    for metric in BLE_METRICS:
        entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{prefix}_e32_ble_{address}_{metric}")
        if entity_id is not None and not entity_id.split(".", 1)[1].startswith(slug):
            return True
    return False


def _discovery(hass, entry, value):
    """The Search as the panel shows it: {"discovery", "discovery_ended_s", "searching"}. With ble.discovery.v1 the
    E32 names a requested search on its own (Search is off only while one is queued or running); firmware without it
    keeps the 95 s rule: searching while the panel's own search is younger than SEARCH_SECONDS."""
    features = getattr(getattr(_hub(hass, entry), "plan", None), "features", None) or ()
    state = value.get("discovery") if type(value) is dict else None
    if DISCOVERY_FEATURE in features and state in DISCOVERY_STATES:
        ended = value.get("discovery_ended_s")
        ended = ended if type(ended) is int and ended >= 0 else None
        return {"discovery": state, "discovery_ended_s": ended, "searching": state in ("queued", "running")}
    started = _SEARCHES.get(entry.entry_id)
    searching = (started is not None and CLOCK() - started < SEARCH_SECONDS and type(value) is dict
                 and value.get("scan_pending") is True)
    return {"discovery": None, "discovery_ended_s": None, "searching": searching}


def _shelly_model(record):
    pumps = {c["pump"].get("device") for c in record["circuits"] if type(c.get("pump")) is dict}
    devices = []
    for device in record["devices"]:
        item = {"n": device["n"], "id": device["id"], "kind": device["kind"], "ip": device["ip"],
                "label": device.get("label") or "", "pump": device["n"] in pumps}
        if device["kind"] == "gateway":
            item["valves"] = [{"id": v["id"], "name": v.get("name") or ""} for v in device.get("valves") or []
                              if type(v) is dict and type(v.get("id")) is int]
        devices.append(item)
    return devices


def _shelly_live(hass, entry, status):
    """{"<n>": device state, "<n>:<valve>": valve state, "room:<n>:<valve>": its room} from /status/shelly and the
    E32's rooms."""
    from .e32_devices import valve_rooms
    live = {}
    for state in (status or {}).get("devices", []):
        if type(state) is not dict or type(state.get("n")) is not int:
            continue
        if type(state.get("health")) is str:
            live[str(state["n"])] = state["health"]
        for valve in state.get("valves") or []:
            if type(valve) is dict and type(valve.get("id")) is int and type(valve.get("health")) is str:
                live[f"{state['n']}:{valve['id']}"] = valve["health"]
    hub = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get("heating_hub")
    for name, room in valve_rooms(hub).items():
        live["room:" + name[1:]] = room  # "g1:200" -> "room:1:200"
    return live


def _bus(hass, entry):
    """The devices the E32 heard on the boiler bus (the boiler and those that said who they are), named as their Home
    Assistant devices (e32_devices.bus_line), or None before the E32 reported them."""
    from homeassistant.helpers import device_registry as dr
    from .const import CONF_TOPIC_PREFIX
    from .ems_devices import ROLES
    devices = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get("ems_devices")
    if devices is None:
        return None
    registry, prefix = dr.async_get(hass), entry.data.get(CONF_TOPIC_PREFIX)
    shown = []
    for device in sorted((d for d in devices if d["address"] == 8 or d["product_id"] is not None), key=lambda d: d["address"]):
        found = registry.async_get_device_by_identifier((DOMAIN, f"{prefix}_ems_{device['address']:02x}"), entry.entry_id)
        shown.append({"name": (found.name_by_user or found.name) if found is not None else None,
                      "address": f"0x{device['address']:02X}", "role": ROLES.get(device["address"], "device")})
    return shown


async def _devices(hass, entry, bluetooth=True, shelly=True):
    """(link, sensors or None, record or None, status, the Bluetooth answer) as the E32 holds them now; a part the
    screen does not need is not read (None)."""
    from .controller_link import ControllerLinkError
    from .e32_bluetooth import decode_sensors
    from .e32_devices import decode_record
    link = _link(hass, entry)
    try:
        ble, record, status = await _read_all(link, bluetooth, shelly)
    except ControllerLinkError as err:
        raise _failure(err) from None
    sensors = decode_sensors(ble) if ble is not None else None
    record = decode_record(record) if record is not None else None
    if ble is not None and sensors is None:
        raise SettingsError("e32_settings_unreachable", error="controller_response_invalid")
    return link, sensors, record, status, ble


def _shelly_part(record):
    from .e32_devices import MAX_DEVICES, MAX_VALVES
    return None if record is None else {"devices": _shelly_model(record), "max_devices": MAX_DEVICES,
                                        "max_valves": MAX_VALVES}


def _nearby(value):
    from .e32_bluetooth import decode_nearby
    return decode_nearby(value) if value is not None else None


async def _read_devices(hass, entry):
    _link_, sensors, record, status, ble = await _devices(hass, entry)
    return {"bluetooth": sensors, "shelly": _shelly_part(record),
            "live": {"bluetooth": _ble_live(hass, entry, sensors or [], _nearby(ble)),
                     "shelly": _shelly_live(hass, entry, status), "bus": _bus(hass, entry),
                     "batteries": _batteries_line(hass, entry)}}


# -- one screen per address (1.4.2, plan 3.9) -------------------------------------------------------------------------

def _address(item):
    """(screen, argument) of an item of this section: ("bluetooth", None), ("sensor", "<address>"), ("device",
    "<id>") …; SettingsError unknown_section for anything else."""
    if item in BLOCKS:
        return item, None
    found = ONE.fullmatch(item) if type(item) is str else None
    if found is not None:
        return found.group(1), found.group(2)
    found = DEVICE.fullmatch(item) if type(item) is str else None
    if found is not None:
        return "device", found.group(1)
    raise SettingsError("unknown_section")


async def _read_item(hass, entry, item):
    """The model of one block screen (plan 3.9): only what that screen shows, so its token moves only with it."""
    from .e32_bluetooth import MAX_SENSORS, guess
    from .e32_devices import MAX_VALVES
    screen, arg = _address(item)
    if screen == "bus":
        _link(hass, entry)
        return {"screen": "bus", "live": {"bus": _bus(hass, entry)}}
    if screen in ("shelly", "device"):
        _link_, _sensors, record, status, _ble = await _devices(hass, entry, bluetooth=False)
        live = {"shelly": _shelly_live(hass, entry, status)}
        if screen == "shelly":
            return {"screen": "shelly", "shelly": _shelly_part(record), "live": live}
        device = next((d for d in _shelly_model(record) if d["id"] == arg), None) if record is not None else None
        return {"screen": "device", "id": arg, "supported": record is not None, "device": device,
                "max_valves": MAX_VALVES, "live": live}
    _link_, sensors, _record, _status, ble = await _devices(hass, entry, shelly=False)
    nearby, search = _nearby(ble), _discovery(hass, entry, ble)
    paired = [s["address"] for s in sensors or []]
    if screen == "bluetooth":
        return {"screen": "bluetooth", "bluetooth": sensors, "max": MAX_SENSORS,
                "live": {"bluetooth": _ble_live(hass, entry, sensors or [], nearby), **search,
                         "battery_limit": _battery_limit(entry)}}
    if screen == "pair" and arg is None:
        return {"screen": "pair", "supported": sensors is not None, "paired": len(paired), "max": MAX_SENSORS,
                "live": search}
    if screen == "pair":
        row = next((r for r in nearby or [] if r["address"] == arg), None)
        kind, encryption = guess(row["name"]) if row is not None else (None, None)
        heard = None if row is None else {"name": row["name"], "rssi": row["rssi"], "kind": kind, "encryption": encryption}
        return {"screen": "pair_form", "address": arg, "supported": sensors is not None, "known": arg in paired,
                "paired": len(paired), "max": MAX_SENSORS, "live": {"heard": heard}}
    sensor = next((s for s in sensors or [] if s["address"] == arg), None)
    if sensor is None:  # forgotten, or never paired: the panel goes back to the list
        return {"screen": "sensor", "address": arg, "missing": True, "live": {}}
    rooms = _plan_rooms(_hub(hass, entry))
    facts = _ble_live(hass, entry, [sensor], nearby)[arg]
    return {"screen": "sensor", "address": arg, "profile": sensor["profile"], "encryption": sensor["encryption"],
            "own_name": sensor["name"], "rooms": [{"id": room["id"], "name": _room_name(room)} for room in rooms],
            "measures_for": facts["measures_for"],
            "live": {**facts, "ids_stale": _ids_stale(hass, entry, arg), "battery_limit": _battery_limit(entry)}}


def _battery_limit(entry):
    """The house's one battery limit (HA-BATTERIES, device_battery): a battery below it is low, here too."""
    from .device_battery import limit_pct
    return limit_pct(entry)


def _saved_how(answer):
    """The done marker of a Bluetooth write (the E32's answer)."""
    return ("ble_unchanged" if answer.get("changed") is False else
            "ble_saved" if answer.get("restart_scheduled") is not False else "ble_saved_restart_later")


async def _write_sensors(link, sensors, names, forget):
    """Rename and forget in one Bluetooth save (async_save_sensors); the E32's answer, or the panel's refusal."""
    from .controller_link import BluetoothRejected, ControllerLinkError
    from .e32_bluetooth import REFUSALS, async_save_sensors
    try:
        answer = await async_save_sensors(link, sensors, names, forget)
    except BluetoothRejected as err:
        raise SettingsError(REFUSALS.get(err.error, "ble_rejected"), error=err.error) from None
    except ControllerLinkError as err:
        if str(err) == "controller_settings_changed":
            raise SettingsError("ble_changed") from None
        raise _failure(err) from None
    if type(answer) is not dict:
        raise SettingsError("e32_settings_unconfirmed")
    return answer


def _moving(address, room_id):
    """The plan change of "Measures for": the sensor first in ``room_id``'s sources (None: in no room) and out of every
    other room's."""
    from copy import deepcopy

    def change(plan):
        candidate = deepcopy(plan)
        for room in candidate.get("rooms") or []:
            if type(room) is not dict:
                continue
            sources = [s for s in room.get("sources") or []
                       if not (type(s) is dict and s.get("type") == "ble" and s.get("id") == address)]
            if room.get("id") == room_id:
                sources = [{"type": "ble", "id": address}, *sources]
            room["sources"] = sources
        return candidate
    return change


async def _assign(hass, entry, address, room_id):
    """Make the sensor ``room_id``'s first temperature source (None: no room's) in one plan write, after the room form's
    own check of every room it changes (E32RoomFlow._e32_room_values). The room's name when the plan changed, "" for
    no room, None when it already was so. Never routine: a room's sources are the user's structural choice."""
    from homeassistant.exceptions import HomeAssistantError
    from .e32_room_flow import MAX_SOURCES, FlowError, RoomEditor
    from .room_plan import plan_room
    link = getattr(_hub(hass, entry), "plan", None)
    if link is None:
        raise SettingsError("unavailable")
    try:
        plan = link.plan if link.plan is not None else await link.async_read()
    except HomeAssistantError as err:
        raise SettingsError("ble_room_not_saved", "measures_for",
                            error=getattr(err, "translation_key", None) or "unknown") from None
    target = plan_room(plan, room_id) if room_id is not None else None
    if room_id is not None and target is None:
        raise SettingsError("ble_room_missing", "measures_for")
    change = _moving(address, room_id)
    candidate = change(plan)
    if candidate == plan:
        return None
    editor = RoomEditor(hass, entry, plan)
    for before in plan.get("rooms") or []:
        after = plan_room(candidate, before.get("id")) if type(before) is dict else None
        if after is None or after.get("sources") == before.get("sources"):
            continue
        user_input = editor.room_input(before)
        sources = after["sources"]
        user_input.update(ha_sources=[s["id"] for s in sources if s.get("type") == "ha"],
                          ble_sources=[s["id"] for s in sources if s.get("type") == "ble"],
                          bluetooth_first=bool(sources) and sources[0].get("type") == "ble")
        try:
            editor._e32_room_values(user_input, before, editor._e32_ble_options(before))
        except FlowError as err:
            name = _room_name(before)
            if err.key == "e32_sources_count":
                raise SettingsError("ble_room_full" if before.get("id") == room_id else "ble_room_only_source",
                                    "measures_for", room=name, max=MAX_SOURCES) from None
            raise SettingsError("ble_room_refused", "measures_for", room=name,
                                error=err.placeholders.get("error") or err.key) from None
    try:
        await link.async_change_plan(change, lambda stored: change(stored) == stored)
    except HomeAssistantError as err:
        raise SettingsError("ble_room_not_saved", "measures_for",
                            error=getattr(err, "translation_key", None) or "unknown") from None
    return _room_name(target) if target is not None else ""


async def _save_sensor(hass, entry, item, address, values):
    """One sensor's screen: Forget sensor (``ble_forget:<address>`` as on the list, or ``forget``), the room it measures for (``measures_for``: a room id, ""
    or None for no room) and its own name (``name``; the automatic name sent as it is becomes its own). The plan
    first, then the name (the E32 restarts about 30 s after a Bluetooth save)."""
    from .e32_bluetooth import valid_name
    link, sensors, _record, _status, _ble = await _devices(hass, entry, shelly=False)
    if sensors is None:
        raise SettingsError("e32_settings_update_required")
    sensor = next((s for s in sensors if s["address"] == address), None)
    if sensor is None:
        raise SettingsError("ble_changed")
    if values.get("forget") is True or values.get(f"ble_forget:{address}") is True:  # the list's key, as in 1.4.1
        answer = await _write_sensors(link, sensors, {}, {address})
        model = await _read_item(hass, entry, item)
        model["live"]["saved"] = {"done": _saved_how(answer)}
        return model
    name = values.get("name", sensor["name"])
    name = name.strip() if type(name) is str else name
    if name != sensor["name"] and not valid_name(name):
        raise SettingsError("ble_name_invalid", "name")
    done = {}
    if "measures_for" in values:
        wanted = values["measures_for"] or None
        if wanted is not None and type(wanted) is not str:
            raise SettingsError("ble_room_missing", "measures_for")
        room = await _assign(hass, entry, address, wanted)
        if room is not None:
            done = {"done": "room_saved", "room": room}
    if name != sensor["name"]:
        done = {**done, "done": _saved_how(await _write_sensors(link, sensors, {address: name}, set()))}
    model = await _read_item(hass, entry, item)
    model["live"]["saved"] = done or {"done": "ble_unchanged"}
    return model


async def _save_pair(hass, entry, item, address, values):
    """``pair/<address>``: pair the device the search heard, as the action ``pair`` does."""
    answer = await _action_pair(hass, entry, item, {**values, "address": address})
    model = await _read_item(hass, entry, item)
    model["live"]["saved"] = {"done": "paired", **answer}
    return model


async def _save_devices(hass, entry, values, item=None):
    from .controller_link import BluetoothRejected, ControllerLinkError
    from .e32_bluetooth import REFUSALS, async_save_sensors, valid_name
    from .e32_devices import Refused, async_change, gateway_valves, removing, removing_valves
    link, sensors, record, _status, _ble = await _devices(hass, entry)
    action = values.get("action")
    if action in ("shelly_remove", "valves_remove"):
        if record is None:
            raise SettingsError("shelly_unsupported")
        try:
            if action == "shelly_remove":
                device = next((d for d in record["devices"] if d["id"] == values.get("device")), None)
                if device is None:
                    raise SettingsError("shelly_rejected", error="unknown_device")
                if device["n"] in {c["pump"].get("device") for c in record["circuits"] if type(c.get("pump")) is dict}:
                    raise SettingsError("shelly_pump_in_use")
                stored = await async_change(link, removing(device["id"]))
                if any(d["id"] == device["id"] for d in stored["devices"]):
                    raise SettingsError("e32_settings_unconfirmed")
                done = {"done": "removed", "name": device.get("label") or "", "kind": device["kind"]}
            else:
                listed = {(n, i) for n, i, _ in gateway_valves(record)}
                chosen = values.get("valves")
                gone = set()
                for value in chosen if type(chosen) is list else []:
                    parts = str(value).split(":")
                    if len(parts) != 2 or not all(p.isdigit() for p in parts) or (int(parts[0]), int(parts[1])) not in listed:
                        raise SettingsError("shelly_valve_invalid")
                    gone.add((int(parts[0]), int(parts[1])))
                if not gone:
                    raise SettingsError("shelly_valve_invalid")
                stored = await async_change(link, removing_valves(gone, {d["n"]: d["id"] for d in record["devices"]}))
                if gone & {(n, i) for n, i, _ in gateway_valves(stored)}:
                    raise SettingsError("e32_settings_unconfirmed")
                done = {"done": "valves_removed", "count": len(gone)}
        except (Refused, ControllerLinkError) as err:
            raise _failure(err) from None
    elif action is not None:
        raise SettingsError("shelly_rejected", error="invalid_action")
    else:
        if sensors is None:
            return None
        names, forget = {}, set()
        for sensor in sensors:
            address = sensor["address"]
            if values.get(f"ble_forget:{address}") is True:
                forget.add(address)
                continue
            name = values.get(f"ble_name:{address}", sensor["name"])
            name = name.strip() if type(name) is str else name
            if name != sensor["name"]:
                if not valid_name(name):
                    raise SettingsError("ble_name_invalid", f"ble_name:{address}")
                names[address] = name
        if not names and not forget:
            return None
        try:
            answer = await async_save_sensors(link, sensors, names, forget)
        except BluetoothRejected as err:
            raise SettingsError(REFUSALS.get(err.error, "ble_rejected"), error=err.error) from None
        except ControllerLinkError as err:
            if str(err) == "controller_settings_changed":
                raise SettingsError("ble_changed") from None
            raise _failure(err) from None
        if type(answer) is not dict:
            raise SettingsError("e32_settings_unconfirmed")
        done = {"done": _saved_how(answer)}
    model = await _read_devices(hass, entry) if item is None else await _read_item(hass, entry, item)
    model["live"]["saved"] = done
    return model


# -- add a Shelly device, add a valve --------------------------------------------------------------------------------

async def _save_shelly_add(hass, entry, values):
    from .controller_link import ControllerLinkError
    from .e32_devices import (KINDS, MAX_DEVICES, Refused, adding, async_change, async_probe, async_read, kind_of,
                              new_device, valid_ip, valid_label, valid_password)
    link = _link(hass, entry)
    ip = str(values.get("ip") or "").strip()
    kind, label = values.get("kind") or "auto", str(values.get("label") or "").strip()
    password = values.get("password") or ""
    if not valid_ip(ip):
        raise SettingsError("shelly_ip_invalid", "ip")
    if kind != "auto" and kind not in KINDS:
        raise SettingsError("shelly_rejected", "kind", error="invalid_kind")
    if label and not valid_label(label):
        raise SettingsError("shelly_label_invalid", "label")
    if not valid_password(password):
        raise SettingsError("shelly_password_invalid", "password")
    try:
        record, _status = await async_read(link)
        if any(d["ip"] == ip for d in record["devices"]):
            raise SettingsError("shelly_ip_duplicate", "ip")
        if len(record["devices"]) >= MAX_DEVICES:
            raise SettingsError("shelly_full")
        info = await async_probe(link, ip)
        kind = kind_of(info) if kind == "auto" else kind
        if info.get("auth_en") is True and not password:
            raise SettingsError("shelly_password_needed", "password")
        device = new_device(info, ip, kind, label, password)
        stored = await async_change(link, adding(device))
    except (Refused, ControllerLinkError) as err:
        raise _failure(err) from None
    if not any(d["id"] == device["id"] for d in stored["devices"]):
        raise SettingsError("e32_settings_unconfirmed")
    return {"screen": "shelly-add", "live": {"saved": {"done": "added", "name": label, "kind": kind}}}


async def _read_valve_add(hass, entry):
    from .controller_link import ControllerLinkError
    from .e32_devices import MAX_VALVES, VALVE_IDS, async_read
    try:
        record, _status = await async_read(_link(hass, entry))
    except ControllerLinkError as err:
        raise _failure(err) from None
    gateways = [{"n": d["n"], "id": d["id"], "label": d.get("label") or "", "ip": d["ip"],
                 "valves": [v["id"] for v in d.get("valves") or [] if type(v) is dict and type(v.get("id")) is int]}
                for d in record["devices"] if d["kind"] == "gateway"]
    return {"screen": "valve-add", "gateways": gateways, "max_valves": MAX_VALVES, "valve_range": list(VALVE_IDS)}


async def _save_valve_add(hass, entry, values):
    from .controller_link import ControllerLinkError
    from .e32_devices import (MAX_VALVES, VALVE_IDS, Refused, adding_valve, async_change, async_read, gateway_valves,
                              valid_label)
    link = _link(hass, entry)
    try:
        record, _status = await async_read(link)
    except ControllerLinkError as err:
        raise _failure(err) from None
    target = next((d for d in record["devices"] if d["kind"] == "gateway" and str(d["n"]) == str(values.get("gateway"))), None)
    if target is None:
        raise SettingsError("shelly_rejected", "gateway", error="unknown_device")
    valve, name = values.get("valve"), str(values.get("name") or "").strip()
    if isinstance(valve, float) and valve.is_integer():
        valve = int(valve)
    used = {v.get("id") for v in target.get("valves") or [] if type(v) is dict}
    if type(valve) is not int or not VALVE_IDS[0] <= valve <= VALVE_IDS[1]:
        raise SettingsError("shelly_valve_invalid", "valve")
    if valve in used:
        raise SettingsError("shelly_valve_duplicate", "valve")
    if len(used) >= MAX_VALVES:
        raise SettingsError("shelly_valves_full")
    if name and not valid_label(name, quotes=True):
        raise SettingsError("shelly_valve_name_invalid", "name")
    try:
        stored = await async_change(link, adding_valve(target["id"], valve, name))
    except (Refused, ControllerLinkError) as err:
        raise _failure(err) from None
    if (target["n"], valve) not in {(n, i) for n, i, _ in gateway_valves(stored)}:
        raise SettingsError("e32_settings_unconfirmed")
    model = await _read_valve_add(hass, entry)
    model["live"] = {"saved": {"done": "valve_added", "valve": valve, "name": name}}
    return model


# -- the batteries (1.4.2, HA-BATTERIES) ---------------------------------------------------------------------------

def _batteries(hass, entry):
    from .device_battery import collect
    from .settings import language
    return collect(hass, entry, lang=language(hass))


def _batteries_line(hass, entry):
    """{"devices", "low"}: the Batteries row of #devices (how many report a battery, how many are low)."""
    rows = _batteries(hass, entry)
    return {"devices": len(rows), "low": sum(1 for row in rows if row["low"])}


def _read_batteries(hass, entry):
    from .device_battery import LIMITS, limit_pct
    return {"screen": "batteries", "limit_pct": limit_pct(entry), "limits": list(LIMITS),
            "live": {"devices": _batteries(hass, entry)}}


def _save_batteries(hass, entry, values):
    from .device_battery import LIMIT_KEY, LIMITS, refresh
    from .energy_input import ENERGY_ONLY_UPDATE
    limit = values.get("limit_pct")
    if isinstance(limit, float) and limit.is_integer():
        limit = int(limit)
    if type(limit) is not int or limit not in LIMITS or set(values) - {"limit_pct"}:
        raise SettingsError("battery_limit_invalid", "limit_pct")
    if (entry.options or {}).get(LIMIT_KEY) != limit:
        options = {**entry.options, LIMIT_KEY: limit}
        state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
        if type(state) is dict:
            state[ENERGY_ONLY_UPDATE] = dict(options)  # the comfort settings' no-reload marker
        if not hass.config_entries.async_update_entry(entry, options=options) and type(state) is dict:
            state.pop(ENERGY_ONLY_UPDATE, None)  # no listener runs: never leave the marker behind
        refresh(hass, entry)
    return _read_batteries(hass, entry)


# -- actions (1.4.1): pair a Bluetooth sensor, The Pill's probe roles, the gateway's valve search -----------------

def _ble_failure(err):
    """A failed Bluetooth request of an action as the panel's code: the E32's refusal on its field, else _failure."""
    from .controller_link import BluetoothRejected
    if isinstance(err, BluetoothRejected):
        key, field = BLE_ERRORS.get(err.error, ("ble_rejected", "base"))
        return SettingsError(key, field, error=err.error)
    if str(err) == "controller_settings_changed":
        return SettingsError("ble_changed")
    return _failure(err)


async def _action_scan(hass, entry, item, values):
    from .controller_link import ControllerLinkError
    from .e32_bluetooth import async_scan
    link = _link(hass, entry)
    try:
        await async_scan(link)
    except ControllerLinkError as err:
        raise _ble_failure(err) from None
    _SEARCHES[entry.entry_id] = CLOCK()
    return {"started": True}


async def _action_scan_result(hass, entry, item, values):
    from .controller_link import ControllerLinkError
    from .e32_bluetooth import MAX_SENSORS, decode_nearby, decode_sensors, guess
    link = _link(hass, entry)
    try:
        value, _tag = await link.async_call(lambda c: c.async_bluetooth(), write=False)
    except ControllerLinkError as err:
        raise _ble_failure(err) from None
    sensors, nearby = decode_sensors(value), decode_nearby(value)
    if sensors is None or nearby is None:
        raise SettingsError("e32_settings_unreachable", error="controller_response_invalid")
    paired = {s["address"] for s in sensors}
    found = []
    for row in nearby:
        kind, encryption = guess(row["name"])
        found.append({**row, "kind": kind, "encryption": encryption, "known": row["address"] in paired})
    started, search = _SEARCHES.get(entry.entry_id), _discovery(hass, entry, value)
    elapsed = CLOCK() - started if started is not None else None
    if search["discovery"] is not None:
        # E32 1.4.2: done once the requested search is idle again and ended after the panel's start (one that ended
        # before it is an older one); SEARCH_SECONDS stays the cap.
        ended = search["discovery_ended_s"]
        done = (search["discovery"] == "idle" and (elapsed is None or ended is not None and ended <= elapsed + 2)
                or elapsed is not None and elapsed >= SEARCH_SECONDS)
    else:
        done = value.get("scan_pending") is not True or elapsed is None or elapsed >= SEARCH_SECONDS
    if done:
        _SEARCHES.pop(entry.entry_id, None)
    return {"sensors": found, "done": done, "paired": len(sensors), "max": MAX_SENSORS,
            "full": value.get("discovery_full") is True, "discovery": search["discovery"],
            "discovery_ended_s": search["discovery_ended_s"]}


async def _action_pair(hass, entry, item, values):
    from .controller_link import ControllerLinkError
    from .e32_bluetooth import (KEY, PROFILE_ENCRYPTIONS, address_of, async_pair, decode_nearby, guess, pairing_row,
                                valid_name)
    link = _link(hass, entry)
    address = address_of(values.get("address"))
    if address is None:
        raise SettingsError("ble_address_invalid", "address")
    name = values.get("name")
    name = name.strip() if type(name) is str else name
    if not valid_name(name):
        raise SettingsError("ble_name_invalid", "name")
    profile, encryption = values.get("profile") or None, values.get("encryption") or None
    if profile is None:
        # As the E32 page: the guess from the name the search heard (one read), else from the name given.
        try:
            value, _tag = await link.async_call(lambda c: c.async_bluetooth(), write=False)
        except ControllerLinkError as err:
            raise _ble_failure(err) from None
        heard = next((r["name"] for r in decode_nearby(value) or [] if r["address"] == address), "")
        profile = guess(heard)[0] or guess(name)[0]
        if profile is None:
            raise SettingsError("ble_profile_needed", "profile")
    if type(profile) is not str or profile not in PROFILE_ENCRYPTIONS:
        raise SettingsError("ble_profile_invalid", "profile")
    bindkey = values.get("bindkey")
    bindkey = bindkey.strip().lower() if type(bindkey) is str and bindkey.strip() else None
    if encryption is None:
        choices = PROFILE_ENCRYPTIONS[profile]
        encryption = (next((e for e in choices if e != "none"), choices[0]) if bindkey
                      else "none" if "none" in choices else choices[0])
    if encryption not in PROFILE_ENCRYPTIONS[profile]:
        raise SettingsError("ble_encryption_invalid", "encryption")
    if encryption == "none":
        if bindkey is not None:
            raise SettingsError("ble_key_not_used", "bindkey")
    elif bindkey is None:
        raise SettingsError("ble_key_needed", "bindkey")
    elif KEY.fullmatch(bindkey) is None:
        raise SettingsError("ble_key_invalid", "bindkey")
    try:
        answer, confirmed = await async_pair(link, pairing_row(address, name, profile, encryption, bindkey))
    except ControllerLinkError as err:
        raise _ble_failure(err) from None
    if type(answer) is not dict or answer.get("changed") is not True or not confirmed:
        raise SettingsError("e32_settings_unconfirmed")
    scheduled = answer.get("restart_scheduled") is not False
    seconds = answer.get("restart_in_s")
    return {"saved": True, "restart": scheduled,
            **({"restart_in_s": seconds} if scheduled and type(seconds) is int else {})}


async def _record(link):
    from .controller_link import ControllerLinkError
    from .e32_devices import async_read
    try:
        return await async_read(link)
    except ControllerLinkError as err:
        if str(err) == "controller_update_required":
            raise SettingsError("shelly_unsupported") from None
        raise _failure(err) from None


def _the_pill(record, wanted):
    from .e32_devices import find_device
    if wanted in (None, ""):
        pills = [d for d in record["devices"] if d["kind"] == "probes"]
        device = pills[0] if len(pills) == 1 else None
    else:
        device = find_device(record, wanted, "probes")
    if device is None:
        raise SettingsError("shelly_rejected", "device", error="unknown_device")
    return device


def _pill_answer(record, status, device):
    from .e32_devices import circuit_roles, pill_probes
    from .heating_link import PROBE_ROLES
    state = next((s for s in (status or {}).get("devices") or [] if type(s) is dict and s.get("n") == device["n"]), None)
    probes = pill_probes(device, state)
    return {"device": {"n": device["n"], "id": device["id"], "label": device.get("label") or ""},
            "probes": probes, "roles": {str(p["c"]): p["role"] for p in probes if p["role"]},
            "choices": list(PROBE_ROLES), "in_use": circuit_roles(record)}


async def _action_pill_roles(hass, entry, item, values):
    record, status = await _record(_link(hass, entry))
    return _pill_answer(record, status, _the_pill(record, values.get("device")))


async def _action_set_pill_roles(hass, entry, item, values):
    from .controller_link import ControllerLinkError
    from .e32_devices import MAX_PROBES, PROBE_IDS, Refused, async_change, circuit_roles, setting_roles
    from .heating_link import PROBE_ROLES
    link = _link(hass, entry)
    record, _status = await _record(link)
    device = _the_pill(record, values.get("device"))
    given = values.get("roles")
    if type(given) is not dict:
        raise SettingsError("shelly_probe_invalid", "roles")
    roles = {}
    for key, role in given.items():
        if not str(key).isdigit() or not PROBE_IDS[0] <= int(key) <= PROBE_IDS[1]:
            raise SettingsError("shelly_probe_invalid", "roles")
        if role in (None, ""):
            continue
        if role not in PROBE_ROLES:
            raise SettingsError("shelly_probe_invalid", f"role:{int(key)}")
        if role in roles.values():
            raise SettingsError("shelly_probe_role_duplicate", f"role:{int(key)}")
        roles[int(key)] = role
    if len(roles) > MAX_PROBES:
        raise SettingsError("shelly_probe_invalid", "roles")
    others = {p.get("role") for d in record["devices"] if d is not device for p in d.get("probes") or []
              if type(p) is dict}
    for c, role in roles.items():
        if role in others:
            raise SettingsError("shelly_probe_role_duplicate", f"role:{c}")
    for role, circuit in circuit_roles(record).items():
        if role not in others and role not in roles.values():
            held = next((p["c"] for p in device.get("probes") or [] if type(p) is dict and p.get("role") == role), None)
            raise SettingsError("shelly_probe_in_use", f"role:{held}" if held is not None else "roles",
                                role=role, circuit=circuit)
    try:
        stored = await async_change(link, setting_roles(device["id"], roles))
    except (Refused, ControllerLinkError) as err:
        raise _failure(err) from None
    after = next((d for d in stored["devices"] if d["id"] == device["id"]), None)
    kept = {p["c"]: p.get("role") for p in (after or {}).get("probes") or [] if type(p) is dict and type(p.get("c")) is int}
    if after is None or kept != roles:
        raise SettingsError("e32_settings_unconfirmed")
    return {"saved": True, "roles": {str(c): role for c, role in sorted(kept.items())}}


def _gateway(record, values):
    from .e32_devices import find_device
    wanted = values.get("gateway")
    device = find_device(record, wanted, "gateway") if wanted not in (None, "") else None
    if device is None:
        raise SettingsError("shelly_rejected", "gateway", error="unknown_device")
    return device


async def _action_gateway_scan(hass, entry, item, values):
    from .controller_link import ControllerLinkError
    from .e32_devices import Refused, async_gateway_scan
    link = _link(hass, entry)
    record, _status = await _record(link)
    device = _gateway(record, values)
    try:
        await async_gateway_scan(link, device["n"])
    except (Refused, ControllerLinkError) as err:
        raise _failure(err) from None
    return {"started": True}


async def _action_gateway_scan_result(hass, entry, item, values):
    from .e32_devices import MAX_VALVES, scan_found
    record, status = await _record(_link(hass, entry))
    device = _gateway(record, values)
    listed = [v for v in device.get("valves") or [] if type(v) is dict]
    return {**scan_found(status, device), "full": len(listed) >= MAX_VALVES}


ACTIONS = {"scan": _action_scan, "scan_result": _action_scan_result, "pair": _action_pair,
           "pill_roles": _action_pill_roles, "set_pill_roles": _action_set_pill_roles,
           "gateway_scan": _action_gateway_scan, "gateway_scan_result": _action_gateway_scan_result}


# -- the section ----------------------------------------------------------------------------------------------------

async def read_devices(hass, entry, item=None):
    if item is None:
        return await _read_devices(hass, entry)
    if item == "shelly-add":
        _link(hass, entry)
        return {"screen": "shelly-add"}  # nothing to read: the form starts empty, the save tests the address
    if item == "valve-add":
        return await _read_valve_add(hass, entry)
    if item == "batteries":
        return _read_batteries(hass, entry)
    return await _read_item(hass, entry, item)


async def save_devices(hass, entry, item, values):
    if item is None:
        return await _save_devices(hass, entry, values)
    if item == "shelly-add":
        return await _save_shelly_add(hass, entry, values)
    if item == "valve-add":
        return await _save_valve_add(hass, entry, values)
    if item == "batteries":
        return _save_batteries(hass, entry, values)
    screen, arg = _address(item)
    if screen == "sensor":
        return await _save_sensor(hass, entry, item, arg, values)
    if screen == "pair" and arg is not None:
        return await _save_pair(hass, entry, item, arg, values)
    # The blocks and a Shelly device: the saves of #devices (remove a device or valves; rename or forget sensors),
    # answered with this screen's model; a screen with nothing to save (bus, pair) reads its model again.
    return await _save_devices(hass, entry, values, item)


# -- the room screen's suggestion (1.4.2, plan 3.9 item 6b) ----------------------------------------------------------

def e32_sensor_suggestion(hass, hub, room):
    """{"entity_id", "address", "name"} when one of the room's Home Assistant temperature sources is the same device
    as a Bluetooth sensor paired on the E32 (its Bluetooth address among the entity's device identifiers or
    connections, as BTHome and Xiaomi BLE give them) that the room does not measure with yet; else None. The room
    screen then suggests the E32's own sensor: it works without Home Assistant."""
    from homeassistant.helpers import device_registry as dr, entity_registry as er
    from .e32_bluetooth import address_of
    from .heating_link import label
    paired = getattr(hub, "ble", None) or {}
    if not paired or type(room) is not dict:
        return None
    sources = [s for s in room.get("sources") or [] if type(s) is dict]
    used = {s.get("id") for s in sources if s.get("type") == "ble"}
    entities, devices = er.async_get(hass), dr.async_get(hass)
    for source in sources:
        entity = entities.async_get(source.get("id") or "") if source.get("type") == "ha" else None
        device = devices.async_get(entity.device_id) if entity is not None and entity.device_id else None
        if device is None or any(domain == DOMAIN for domain, _value in device.identifiers):
            continue
        for _kind, value in [*device.identifiers, *device.connections]:
            address = address_of(value) if type(value) is str else None
            if address in paired and address not in used:
                return {"entity_id": source["id"], "address": address, "name": label(paired[address])}
    return None


register_section("devices", read_devices, save_devices, actions=ACTIONS)
