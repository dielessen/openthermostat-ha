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

import time

from .const import DOMAIN
from .settings import SettingsError, register_section

# The longest a Bluetooth search the panel started can take: it waits for the current scan to end (60 s at most with
# paired sensors, BleScanPlan) and then listens 30 s; after that the result counts as done.
SEARCH_SECONDS = 95
# entry_id -> monotonic start of the last Bluetooth search the panel started (RAM only).
_SEARCHES: dict[str, float] = {}
CLOCK = time.monotonic  # the clock of SEARCH_SECONDS (a test moves it)
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


async def _read_all(link):
    """(bluetooth value or None, Shelly record or None, Shelly status or None) in one sign-in; a part this firmware
    does not have is None."""
    from .controller_link import ControllerLinkError

    async def read(client):
        try:
            ble, _tag = await client.async_bluetooth()
        except ControllerLinkError as err:
            if str(err) != "controller_update_required":
                raise
            ble = None
        try:
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


def _ble_live(hass, entry, sensors):
    """{address: {"rooms", "temperature", "humidity", "battery"}}: the rooms that measure with each sensor (the room
    plan Home Assistant last read) and its Home Assistant entities, whose state the panel shows."""
    from homeassistant.helpers import entity_registry as er
    from .heating_link import BLE_METRICS
    hub = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get("heating_hub")
    plan = getattr(getattr(hub, "plan", None), "plan", None)
    rooms = plan.get("rooms", []) if type(plan) is dict else []
    registry, prefix = er.async_get(hass), getattr(hub, "prefix", None)
    live = {}
    for sensor in sensors:
        address = sensor["address"]
        live[address] = {"rooms": [room.get("name") or room.get("id") for room in rooms if type(room) is dict and any(
            type(s) is dict and s.get("type") == "ble" and s.get("id") == address for s in room.get("sources", []))]}
        for metric in BLE_METRICS:
            live[address][metric] = (registry.async_get_entity_id("sensor", DOMAIN, f"{prefix}_e32_ble_{address}_{metric}")
                                     if prefix else None)
    return live


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


async def _devices(hass, entry):
    """(link, sensors or None, record or None, status) as the E32 holds them now."""
    from .controller_link import ControllerLinkError
    from .e32_bluetooth import decode_sensors
    from .e32_devices import decode_record
    link = _link(hass, entry)
    try:
        ble, record, status = await _read_all(link)
    except ControllerLinkError as err:
        raise _failure(err) from None
    sensors = decode_sensors(ble) if ble is not None else None
    record = decode_record(record) if record is not None else None
    if ble is not None and sensors is None:
        raise SettingsError("e32_settings_unreachable", error="controller_response_invalid")
    return link, sensors, record, status


async def _read_devices(hass, entry):
    _link_, sensors, record, status = await _devices(hass, entry)
    from .e32_devices import MAX_DEVICES, MAX_VALVES
    return {"bluetooth": sensors,
            "shelly": None if record is None else {"devices": _shelly_model(record), "max_devices": MAX_DEVICES,
                                                   "max_valves": MAX_VALVES},
            "live": {"bluetooth": _ble_live(hass, entry, sensors or []), "shelly": _shelly_live(hass, entry, status),
                     "bus": _bus(hass, entry)}}


async def _save_devices(hass, entry, values):
    from .controller_link import BluetoothRejected, ControllerLinkError
    from .e32_bluetooth import REFUSALS, async_save_sensors, valid_name
    from .e32_devices import Refused, async_change, gateway_valves, removing, removing_valves
    link, sensors, record, _status = await _devices(hass, entry)
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
        done = {"done": "ble_unchanged" if answer.get("changed") is False else
                "ble_saved" if answer.get("restart_scheduled") is not False else "ble_saved_restart_later"}
    model = await _read_devices(hass, entry)
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
    started = _SEARCHES.get(entry.entry_id)
    done = value.get("scan_pending") is not True or started is None or CLOCK() - started >= SEARCH_SECONDS
    if done:
        _SEARCHES.pop(entry.entry_id, None)
    return {"sensors": found, "done": done, "paired": len(sensors), "max": MAX_SENSORS,
            "full": value.get("discovery_full") is True}


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
    raise SettingsError("unknown_section")


async def save_devices(hass, entry, item, values):
    if item is None:
        return await _save_devices(hass, entry, values)
    if item == "shelly-add":
        return await _save_shelly_add(hass, entry, values)
    if item == "valve-add":
        return await _save_valve_add(hass, entry, values)
    raise SettingsError("unknown_section")


register_section("devices", read_devices, save_devices, actions=ACTIONS)
