"""Configure → E32 devices (1.3, NEXT-RELEASE 1e): what the E32 talks to itself, as on its page System → Devices.

- **Bluetooth sensors** (``e32_bluetooth.py``): moved here from Advanced and diagnostics, unchanged.
- **Shelly devices**: the devices the E32 knows (``GET /config/shelly``, their state from ``GET /status/shelly``),
  and adding or removing a BLU Gateway, a valve, the Plug and The Pill with the requests the E32's own page makes
  (``data/html/shelly.js``): the address is tested with ``POST /config/shelly/probe {"ip"}`` and then
  ``GET /status/shelly`` until its ``probe`` answers (up to 16 s, "Test connection"); every change posts the whole
  record back, ``POST /config/shelly`` ({"schema": 1, "devices", "circuits" when there are any}), the devices
  without their ``"password": true|false`` (the E32 keeps each stored one) and a new device with its password as
  text. The read, the change and the write share one sign-in, so a change made on the E32 page meanwhile is not
  lost. A device's password goes to the E32 only; Home Assistant neither keeps nor shows it.
- **On the boiler bus**: read-only, a line in the menu's text with the devices the E32 heard (the retained
  ``fw/config/ems_devices``, named as their Home Assistant devices, ems_devices.py).

The rest stays on the E32's page: The Pill's probe roles, the search for valves at the gateway, the pump by hand, a
device's new name, address or password, and renewing the key for instant updates.
"""
from __future__ import annotations

import asyncio
import re

from .const import DOMAIN

KINDS = ("switch", "probes", "gateway")
MAX_DEVICES = 6           # ShellyConfig::maxDevices
MAX_VALVES = 5            # ShellyConfig::maxValves, per gateway
VALVE_IDS = (200, 299)    # blutrv:<id>, ShellyConfig firstValve..lastValve
LABEL_BYTES = 32          # ShellyConfig::maxLabelBytes, also a valve's name (maxValveNameBytes)
PASSWORD_BYTES = 64       # ShellyConfig::maxPasswordBytes, printable ASCII
# "Test connection": the E32 asks the device, then this many reads of /status/shelly this far apart (shelly.js).
PROBE_READS, PROBE_PAUSE = 16, 1.0
IP = re.compile(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})")

# The E32's refusals and the probe's outcomes (shelly.js refusals) as form errors; the rest name the E32's code.
ERRORS = {"invalid_ip": "shelly_ip_invalid", "duplicate_ip": "shelly_ip_duplicate",
          "connect_failed": "shelly_connect_failed", "timeout": "shelly_timeout", "closed": "shelly_timeout",
          "auth_required": "shelly_auth_required", "not_a_shelly": "shelly_not_a_shelly",
          "probe_busy": "shelly_probe_busy", "duplicate_device": "shelly_duplicate_device",
          "invalid_devices": "shelly_full", "record_too_large": "shelly_full",
          "invalid_label": "shelly_label_invalid", "invalid_password": "shelly_password_invalid",
          "unknown_pump_device": "shelly_pump_in_use", "unknown_circuit_probe": "shelly_probe_in_use",
          "invalid_valve": "shelly_valve_invalid", "duplicate_valve": "shelly_valve_duplicate",
          "invalid_valve_name": "shelly_valve_name_invalid", "invalid_valves": "shelly_valves_full"}
# The field a form error belongs to (else the whole form).
FIELDS = {"shelly_ip_invalid": "ip", "shelly_ip_duplicate": "ip", "shelly_label_invalid": "label",
          "shelly_password_invalid": "password", "shelly_valve_invalid": "valve", "shelly_valve_duplicate": "valve",
          "shelly_valve_name_invalid": "name"}

# Words for the lists this module builds itself (menu texts), as on the E32's page (ui-messages-devices.js).
WORDS = {
    "en": {"kinds": {"switch": "Plug", "probes": "The Pill", "gateway": "BLU Gateway"},
           "labels": {"switch": "Floor pump", "probes": "Floor probes", "gateway": "Valve gateway"},
           "health": {"waiting": "waiting for the first answer", "ok": "connected", "unreachable": "not reachable",
                      "wrong_device": "another device answers at this address",
                      "auth_failed": "the password is not accepted", "error": "the device reports an error"},
           "valve_health": {"waiting": "waiting for a report", "ok": "reporting", "silent": "silent for 15 minutes",
                            "offline": "not reporting", "missing": "not found at the gateway",
                            "unpaired": "not paired with the gateway", "gateway": "gateway not reachable"},
           "valve": "Valve {id}", "in_room": "in {room}", "no_devices": "No Shelly devices yet.",
           "bus_unknown": "the E32 has not reported them yet.", "bus_none": "nothing heard yet.",
           "boiler": "Boiler", "thermostat": "Thermostat", "device": "EMS device", "none": "-"},
    "nl": {"kinds": {"switch": "Plug", "probes": "The Pill", "gateway": "BLU Gateway"},
           "labels": {"switch": "Vloerpomp", "probes": "Sondes vloer", "gateway": "Kranengateway"},
           "health": {"waiting": "wacht op het eerste antwoord", "ok": "verbonden", "unreachable": "niet bereikbaar",
                      "wrong_device": "op dit adres antwoordt een ander apparaat",
                      "auth_failed": "het wachtwoord wordt niet geaccepteerd", "error": "het apparaat meldt een fout"},
           "valve_health": {"waiting": "wacht op een melding", "ok": "meldt zich", "silent": "al 15 minuten stil",
                            "offline": "meldt zich niet", "missing": "niet gevonden bij de gateway",
                            "unpaired": "niet gekoppeld aan de gateway", "gateway": "gateway niet bereikbaar"},
           "valve": "Kraan {id}", "in_room": "in {room}", "no_devices": "Nog geen Shelly-apparaten.",
           "bus_unknown": "de E32 heeft ze nog niet gemeld.", "bus_none": "nog niets gehoord.",
           "boiler": "Ketel", "thermostat": "Thermostaat", "device": "EMS-apparaat", "none": "-"},
    "pl": {"kinds": {"switch": "Plug", "probes": "The Pill", "gateway": "BLU Gateway"},
           "labels": {"switch": "Pompa podłogowa", "probes": "Sondy podłogi", "gateway": "Bramka zaworów"},
           "health": {"waiting": "czeka na pierwszą odpowiedź", "ok": "połączono", "unreachable": "nieosiągalne",
                      "wrong_device": "pod tym adresem odpowiada inne urządzenie",
                      "auth_failed": "hasło nie jest akceptowane", "error": "urządzenie zgłasza błąd"},
           "valve_health": {"waiting": "czeka na zgłoszenie", "ok": "zgłasza się", "silent": "cisza od 15 minut",
                            "offline": "nie zgłasza się", "missing": "nie znaleziono w bramce",
                            "unpaired": "nie sparowano z bramką", "gateway": "bramka nieosiągalna"},
           "valve": "Zawór {id}", "in_room": "w pomieszczeniu {room}", "no_devices": "Brak urządzeń Shelly.",
           "bus_unknown": "E32 jeszcze ich nie zgłosił.", "bus_none": "na razie nic nie słychać.",
           "boiler": "Kocioł", "thermostat": "Termostat", "device": "Urządzenie EMS", "none": "-"},
}


def language(hass):
    value = str(getattr(getattr(hass, "config", None), "language", "en") or "en")[:2]
    return value if value in WORDS else "en"


def valid_ip(text):
    match = IP.fullmatch(text) if type(text) is str else None
    return match is not None and all(int(part) <= 255 for part in match.groups())


def valid_label(text, limit=LABEL_BYTES, quotes=False):
    """A name the E32 takes: up to 32 UTF-8 bytes, no control characters, not only spaces (a valve's name: no quotes
    or backslashes either)."""
    return (type(text) is str and text.strip() != "" and len(text.encode()) <= limit
            and not any(ord(c) < 32 or ord(c) == 127 or (quotes and c in '"\\') for c in text))


def valid_password(text):
    return type(text) is str and len(text) <= PASSWORD_BYTES and all(0x20 <= ord(c) <= 0x7E for c in text)


def decode_record(value):
    """The Shelly record of a GET/POST answer ({"devices", "circuits"}), or None."""
    if type(value) is not dict or type(value.get("devices")) is not list:
        return None
    devices = []
    for device in value["devices"]:
        if (type(device) is not dict or device.get("kind") not in KINDS or type(device.get("id")) is not str
                or type(device.get("ip")) is not str or type(device.get("n")) is not int):
            return None
        devices.append(device)
    circuits = value.get("circuits")
    return {"devices": devices, "circuits": [c for c in circuits if type(c) is dict] if type(circuits) is list else []}


def save_document(devices, circuits):
    """POST /config/shelly as the E32's page sends it (shelly.js record()): each device without a stored-password
    flag (a text password is a new one), the circuits only when there are any (left out, they would be removed)."""
    clean = [{k: v for k, v in d.items() if not (k == "password" and type(v) is not str)} for d in devices]
    return {"schema": 1, "devices": clean, **({"circuits": circuits} if circuits else {})}


def kind_of(info):
    """The kind the E32's page proposes from the probe's answer (its "app"): The Pill, a gateway, or a Plug."""
    app = str((info or {}).get("app") or (info or {}).get("model") or "")
    return "probes" if re.search("pill", app, re.I) else "gateway" if re.search("gw|gateway", app, re.I) else "switch"


def gateway_valves(record):
    """[(device n, valve id, valve name)] of every BLU Gateway in the record."""
    return [(d["n"], v["id"], v.get("name") or "") for d in record["devices"] if d["kind"] == "gateway"
            for v in d.get("valves") or [] if type(v) is dict and type(v.get("id")) is int]


def valve_rooms(hub):
    """{"g<n>:<id>": room name} of the gateway valves in the E32's rooms (fw/state/trv; the names of the room plan)."""
    plan = getattr(getattr(hub, "plan", None), "plan", None)
    names = {r.get("id"): r.get("name") for r in (plan.get("rooms") or []) if type(r) is dict} if type(plan) is dict else {}
    found = {}
    for room_id, room in (getattr(hub, "valves", None) or {}).items():
        name = names.get(room_id) or ((getattr(hub, "rooms", None) or {}).get(room_id) or {}).get("name") or room_id
        for valve in (room or {}).get("valves", []):
            if valve.get("model") == "shelly_blu_trv" and type(valve.get("name")) is str:
                found[valve["name"]] = name
    return found


def device_name(device, lang):
    return device.get("label") or WORDS[lang]["kinds"][device["kind"]]


def describe(record, status, rooms, lang):
    """The menu's list: one line per device (its job, address and state), a gateway's valves below it."""
    words = WORDS[lang]
    states = {s.get("n"): s for s in (status or {}).get("devices", []) if type(s) is dict}
    lines = []
    for device in record["devices"]:
        state = states.get(device["n"]) or {}
        health = words["health"].get(state.get("health"), "")
        lines.append(f"- **{device_name(device, lang)}** ({words['kinds'][device['kind']]}, {device['ip']})"
                     + (f": {health}" if health else ""))
        if device["kind"] == "gateway":
            live = {v.get("id"): v for v in state.get("valves", []) if type(v) is dict}
            for n, valve_id, name in gateway_valves({"devices": [device]}):
                text = words["valve"].format(id=valve_id) + (f" · {name}" if name else "")
                where = rooms.get(f"g{n}:{valve_id}")
                facts = [fact for fact in (words["valve_health"].get((live.get(valve_id) or {}).get("health"), ""),
                                           words["in_room"].format(room=where) if where else "") if fact]
                lines.append(f"  - {text}" + (": " + ", ".join(facts) if facts else ""))
    return "\n".join(lines) or words["no_devices"]


def bus_line(hass, entry, lang):
    """The devices the E32 heard on the boiler bus, named as their Home Assistant devices (ems_devices.py)."""
    from homeassistant.helpers import device_registry as dr
    from .const import CONF_TOPIC_PREFIX
    from .ems_devices import ROLES
    words = WORDS[lang]
    devices = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get("ems_devices")
    if devices is None:
        return words["bus_unknown"]
    # As on the E32's page: the boiler and the devices that said who they are; other senders are traffic.
    shown = sorted((d for d in devices if d["address"] == 8 or d["product_id"] is not None), key=lambda d: d["address"])
    if not shown:
        return words["bus_none"]
    registry, prefix = dr.async_get(hass), entry.data.get(CONF_TOPIC_PREFIX)
    names = []
    for device in shown:
        found = registry.async_get_device_by_identifier((DOMAIN, f"{prefix}_ems_{device['address']:02x}"), entry.entry_id)
        name = (found.name_by_user or found.name) if found is not None else None
        names.append(f"{name or words[ROLES.get(device['address'], 'device')]} (0x{device['address']:02X})")
    return ", ".join(names)


class Refused(Exception):
    """The E32 refused a Shelly change or test; ``code`` is its error name."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


class DevicesOptionsSteps:
    """Mixin for the product options flow: Configure → E32 devices and its Shelly steps."""

    def _devices_link(self):
        from .e32_system import link_for
        return link_for(self.hass, self.config_entry)

    async def async_step_e32_devices(self, user_input=None):
        if self._devices_link() is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        return self.async_show_menu(step_id="e32_devices", menu_options=["ble_sensors", "shelly_devices"],
                                    description_placeholders={"bus": bus_line(self.hass, self.config_entry,
                                                                              language(self.hass))})

    # -- reading and writing the record -----------------------------------------------------------------

    def _shelly_abort(self, err):
        """An abort for a failed read: no Shelly in this firmware, or the E32's own reason."""
        from .e32_system import ABORTS, failure
        if str(err) == "controller_update_required":
            return self.async_abort(reason="shelly_unsupported")
        key, placeholders = failure(err)
        return self.async_abort(reason=key if key in ABORTS else "e32_settings_unreachable",
                                description_placeholders=placeholders)

    async def _shelly_change(self, change):
        """Read the record, change it (change(record) → devices, or raise Refused) and POST it, in one sign-in.

        Returns the stored record. Raises Refused (the E32's refusal or change's own) or ControllerLinkError.
        """
        from .controller_link import ControllerLinkError, HeatingPlanRejected

        async def call(client):
            record = decode_record(await client.async_shelly())
            if record is None:
                raise ControllerLinkError("controller_response_invalid")
            try:
                stored = await client.async_shelly(save_document(change(record), record["circuits"]))
            except HeatingPlanRejected as err:
                raise Refused(err.error) from None
            stored = decode_record(stored)
            if stored is None:
                raise ControllerLinkError("controller_settings_unconfirmed")
            return stored
        return await self._devices_link().async_call(call, write=True)

    def _shelly_form_error(self, err, errors, placeholders):
        """A refusal or a failed write as a form error (the field it belongs to), or an abort result."""
        from .e32_system import ABORTS, failure
        if isinstance(err, Refused):
            key = ERRORS.get(err.code, "shelly_rejected")
            errors[FIELDS.get(key, "base")] = key
            placeholders["error"] = err.code
            return None
        if str(err) == "controller_update_required":
            return self.async_abort(reason="shelly_unsupported")
        key, values = failure(err)
        if key in ABORTS:
            return self.async_abort(reason=key, description_placeholders=values)
        errors["base"] = key
        placeholders.update(values)
        return None

    # -- Shelly devices -----------------------------------------------------------------------------

    async def async_step_shelly_devices(self, user_input=None):
        """The devices the E32 knows, and what can be added or removed here."""
        from .controller_link import ControllerLinkError
        from .heating_link import heating_hub
        link = self._devices_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")

        async def read(client):
            record = await client.async_shelly()
            try:
                status = await client.async_shelly_status()
            except ControllerLinkError:
                status = None  # the list without its state is still the list
            return record, status
        try:
            value, status = await link.async_call(read)
        except ControllerLinkError as err:
            return self._shelly_abort(err)
        record = decode_record(value)
        if record is None:
            return self.async_abort(reason="e32_settings_unreachable",
                                    description_placeholders={"error": "controller_response_invalid"})
        self._shelly = record
        lang = language(self.hass)
        rooms = valve_rooms(heating_hub(self.hass, self.config_entry))
        valves = gateway_valves(record)
        gateways = [d for d in record["devices"] if d["kind"] == "gateway"]
        options = (["shelly_add"] if len(record["devices"]) < MAX_DEVICES else []) \
            + (["shelly_valve_add"] if any(len(d.get("valves") or []) < MAX_VALVES for d in gateways) else []) \
            + (["shelly_valve_remove"] if valves else []) + (["shelly_remove"] if record["devices"] else [])
        return self.async_show_menu(step_id="shelly_devices", menu_options=options,
                                    description_placeholders={"devices": describe(record, status, rooms, lang)})

    async def async_step_shelly_add(self, user_input=None):
        """The device's address; "Test connection": the E32 asks the device who it is."""
        from homeassistant.helpers import selector
        import probatio as vol
        from .controller_link import ControllerLinkError, HeatingPlanRejected
        record = getattr(self, "_shelly", None)
        if record is None:
            return await self.async_step_shelly_devices()
        errors, placeholders = {}, {"error": ""}
        ip = str((user_input or {}).get("ip") or "").strip()
        if user_input is not None:
            if not valid_ip(ip):
                errors["ip"] = "shelly_ip_invalid"
            elif any(d["ip"] == ip for d in record["devices"]):
                errors["ip"] = "shelly_ip_duplicate"
            else:
                async def test(client):
                    try:
                        await client.async_shelly_probe(ip)
                    except HeatingPlanRejected as err:
                        raise Refused(err.error) from None
                    for _ in range(PROBE_READS):
                        await asyncio.sleep(PROBE_PAUSE)
                        probe = (await client.async_shelly_status() or {}).get("probe")
                        if type(probe) is not dict or probe.get("ip") != ip or probe.get("state") == "pending":
                            continue
                        info = probe.get("info")
                        if probe.get("state") != "ok" or type(info) is not dict or not info.get("id"):
                            raise Refused(probe.get("error") or "not_a_shelly")
                        return info
                    raise Refused("timeout")
                try:
                    info = await self._devices_link().async_call(test, write=True)
                except (Refused, ControllerLinkError) as err:
                    aborted = self._shelly_form_error(err, errors, placeholders)
                    if aborted is not None:
                        return aborted
                else:
                    self._shelly_found = {"ip": ip, "info": info}
                    return await self.async_step_shelly_add_device()
        return self.async_show_form(step_id="shelly_add", errors=errors, description_placeholders=placeholders,
                                    data_schema=vol.Schema({vol.Required("ip", default=ip): selector.TextSelector()}))

    async def async_step_shelly_add_device(self, user_input=None):
        """What the found device does, its name and its password; then the whole record is saved."""
        from homeassistant.helpers import selector
        import probatio as vol
        from .controller_link import ControllerLinkError
        found = getattr(self, "_shelly_found", None)
        if found is None:
            return await self.async_step_shelly_devices()
        info, lang = found["info"], language(self.hass)
        errors = {}
        placeholders = {"model": str(info.get("app") or info.get("model") or "?"), "version": str(info.get("ver") or "-"),
                        "ip": found["ip"], "error": ""}
        kind = (user_input or {}).get("kind") or kind_of(info)
        label = str((user_input or {}).get("label") or "").strip() if user_input is not None else WORDS[lang]["labels"][kind]
        if user_input is not None:
            password = user_input.get("password") or ""
            if kind not in KINDS:
                errors["kind"] = "shelly_rejected"
            elif label and not valid_label(label):
                errors["label"] = "shelly_label_invalid"
            elif not valid_password(password):
                errors["password"] = "shelly_password_invalid"
            elif info.get("auth_en") is True and not password:
                errors["password"] = "shelly_password_needed"
            else:
                device = {"id": info["id"], "kind": kind, "ip": found["ip"], "host": info["id"],
                          **({"label": label} if label else {}), **({"password": password} if password else {})}

                def add(record):
                    if any(d["id"] == device["id"] for d in record["devices"]):
                        raise Refused("duplicate_device")
                    if any(d["ip"] == device["ip"] for d in record["devices"]):
                        raise Refused("duplicate_ip")
                    return [*record["devices"], device]
                try:
                    stored = await self._shelly_change(add)
                except (Refused, ControllerLinkError) as err:
                    aborted = self._shelly_form_error(err, errors, placeholders)
                    if aborted is not None:
                        return aborted
                else:
                    self._shelly_found = None
                    if not any(d["id"] == device["id"] for d in stored["devices"]):
                        return self.async_abort(reason="e32_settings_unconfirmed")
                    return self.async_abort(reason="shelly_device_added",
                                            description_placeholders={"name": label or WORDS[lang]["kinds"][kind]})
        return self.async_show_form(step_id="shelly_add_device", errors=errors, description_placeholders=placeholders,
                                    data_schema=vol.Schema({
                                        vol.Required("kind", default=kind): selector.SelectSelector(
                                            selector.SelectSelectorConfig(options=list(KINDS), translation_key="shelly_kind",
                                                                          mode=selector.SelectSelectorMode.LIST)),
                                        vol.Optional("label", default=label): selector.TextSelector(),
                                        vol.Optional("password"): selector.TextSelector(
                                            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
                                    }))

    async def async_step_shelly_remove(self, user_input=None):
        """Remove a device: the E32 stops reading and switching it (a circuit's pump plug first leaves its circuit)."""
        from homeassistant.helpers import selector
        import probatio as vol
        from .controller_link import ControllerLinkError
        record = getattr(self, "_shelly", None)
        if record is None or not record["devices"]:
            return await self.async_step_shelly_devices()
        lang = language(self.hass)
        choices = [{"value": str(d["n"]), "label": f"{device_name(d, lang)} ({WORDS[lang]['kinds'][d['kind']]}, {d['ip']})"}
                   for d in record["devices"]]
        errors, placeholders = {}, {"error": ""}
        chosen = str((user_input or {}).get("device") or choices[0]["value"])
        if user_input is not None:
            device = next((d for d in record["devices"] if str(d["n"]) == chosen), None)
            pumps = {c["pump"].get("device") for c in record["circuits"] if type(c.get("pump")) is dict}
            if device is None:
                errors["device"] = "shelly_rejected"
            elif device["n"] in pumps:
                errors["base"] = "shelly_pump_in_use"
            elif not user_input.get("confirm"):
                errors["base"] = "care_confirm"
            else:
                def remove(current):
                    if not any(d["id"] == device["id"] for d in current["devices"]):
                        raise Refused("unknown_device")
                    return [d for d in current["devices"] if d["id"] != device["id"]]
                try:
                    stored = await self._shelly_change(remove)
                except (Refused, ControllerLinkError) as err:
                    aborted = self._shelly_form_error(err, errors, placeholders)
                    if aborted is not None:
                        return aborted
                else:
                    if any(d["id"] == device["id"] for d in stored["devices"]):
                        return self.async_abort(reason="e32_settings_unconfirmed")
                    return self.async_abort(reason="shelly_device_removed",
                                            description_placeholders={"name": device_name(device, lang)})
        return self.async_show_form(step_id="shelly_remove", errors=errors, description_placeholders=placeholders,
                                    data_schema=vol.Schema({
                                        vol.Required("device", default=chosen): selector.SelectSelector(
                                            selector.SelectSelectorConfig(options=choices,
                                                                          mode=selector.SelectSelectorMode.DROPDOWN)),
                                        vol.Required("confirm", default=False): selector.BooleanSelector()}))

    async def async_step_shelly_valve_add(self, user_input=None):
        """Add a valve to a BLU Gateway by its number (paired in the Shelly app first), as "Add valve" on the E32."""
        from homeassistant.helpers import selector
        import probatio as vol
        from .controller_link import ControllerLinkError
        record = getattr(self, "_shelly", None)
        gateways = [d for d in (record or {}).get("devices", []) if d["kind"] == "gateway"
                    and len(d.get("valves") or []) < MAX_VALVES]
        if not gateways:
            return await self.async_step_shelly_devices()
        lang = language(self.hass)
        choices = [{"value": str(d["n"]), "label": f"{device_name(d, lang)} ({d['ip']})"} for d in gateways]
        gateway = str((user_input or {}).get("gateway") or choices[0]["value"])
        target = next((d for d in gateways if str(d["n"]) == gateway), gateways[0])
        used = {v.get("id") for v in target.get("valves") or [] if type(v) is dict}
        first = next(i for i in range(VALVE_IDS[0], VALVE_IDS[1] + 1) if i not in used)
        errors, placeholders = {}, {"error": ""}
        valve, name = (user_input or {}).get("valve", first), str((user_input or {}).get("name") or "").strip()
        if user_input is not None:
            if isinstance(valve, float) and valve.is_integer():
                valve = int(valve)
            if str(target["n"]) != gateway:
                errors["gateway"] = "shelly_rejected"
            elif type(valve) is not int or not VALVE_IDS[0] <= valve <= VALVE_IDS[1]:
                errors["valve"] = "shelly_valve_invalid"
            elif valve in used:
                errors["valve"] = "shelly_valve_duplicate"
            elif name and not valid_label(name, quotes=True):
                errors["name"] = "shelly_valve_name_invalid"
            else:
                entry = {"id": valve, **({"name": name} if name else {})}

                def add(current):
                    device = next((d for d in current["devices"] if d["id"] == target["id"]), None)
                    if device is None:
                        raise Refused("unknown_device")
                    valves = list(device.get("valves") or [])
                    if any(type(v) is dict and v.get("id") == valve for v in valves):
                        raise Refused("duplicate_valve")
                    if len(valves) >= MAX_VALVES:
                        raise Refused("invalid_valves")
                    return [{**d, "valves": [*valves, entry]} if d is device else d for d in current["devices"]]
                try:
                    stored = await self._shelly_change(add)
                except (Refused, ControllerLinkError) as err:
                    aborted = self._shelly_form_error(err, errors, placeholders)
                    if aborted is not None:
                        return aborted
                else:
                    if (target["n"], valve) not in {(n, i) for n, i, _ in gateway_valves(stored)}:
                        return self.async_abort(reason="e32_settings_unconfirmed")
                    return self.async_abort(reason="shelly_valve_added", description_placeholders={
                        "name": WORDS[lang]["valve"].format(id=valve) + (f" · {name}" if name else "")})
        return self.async_show_form(step_id="shelly_valve_add", errors=errors, description_placeholders=placeholders,
                                    data_schema=vol.Schema({
                                        vol.Required("gateway", default=gateway): selector.SelectSelector(
                                            selector.SelectSelectorConfig(options=choices,
                                                                          mode=selector.SelectSelectorMode.DROPDOWN)),
                                        vol.Required("valve", default=valve if type(valve) is int else first):
                                            selector.NumberSelector({"min": VALVE_IDS[0], "max": VALVE_IDS[1], "step": 1,
                                                                     "mode": "box"}),
                                        vol.Optional("name", default=name): selector.TextSelector()}))

    async def async_step_shelly_valve_remove(self, user_input=None):
        """Remove valves from their gateway; a valve chosen for a room stays there until it is removed under Rooms."""
        from homeassistant.helpers import selector
        import probatio as vol
        from .controller_link import ControllerLinkError
        from .heating_link import heating_hub
        record = getattr(self, "_shelly", None)
        valves = gateway_valves(record) if record is not None else []
        if not valves:
            return await self.async_step_shelly_devices()
        lang = language(self.hass)
        names = {d["n"]: device_name(d, lang) for d in record["devices"]}
        rooms = valve_rooms(heating_hub(self.hass, self.config_entry))
        choices = [{"value": f"{n}:{i}", "label": WORDS[lang]["valve"].format(id=i) + (f" · {name}" if name else "")
                    + f" ({names[n]})"} for n, i, name in valves]
        in_rooms = []
        for choice in choices:
            room = rooms.get("g" + choice["value"])
            if room is not None:
                in_rooms.append(f"- {choice['label']}: " + WORDS[lang]["in_room"].format(room=room))
        errors, placeholders = {}, {"error": "", "rooms": "\n".join(in_rooms) or WORDS[lang]["none"]}
        if user_input is not None:
            chosen = [str(v) for v in user_input.get("valves") or []]
            if not chosen or any(v not in {c["value"] for c in choices} for v in chosen):
                errors["valves"] = "shelly_valve_invalid"
            elif not user_input.get("confirm"):
                errors["base"] = "care_confirm"
            else:
                gone = {tuple(int(x) for x in v.split(":")) for v in chosen}
                ids = {d["n"]: d["id"] for d in record["devices"]}

                def remove(current):
                    return [{**d, "valves": [v for v in d.get("valves") or []
                                             if not (type(v) is dict and (d["n"], v.get("id")) in gone)]}
                            if d["kind"] == "gateway" and d["id"] in {ids[n] for n, _ in gone} else d
                            for d in current["devices"]]
                try:
                    stored = await self._shelly_change(remove)
                except (Refused, ControllerLinkError) as err:
                    aborted = self._shelly_form_error(err, errors, placeholders)
                    if aborted is not None:
                        return aborted
                else:
                    if gone & {(n, i) for n, i, _ in gateway_valves(stored)}:
                        return self.async_abort(reason="e32_settings_unconfirmed")
                    return self.async_abort(reason="shelly_valves_removed",
                                            description_placeholders={"count": str(len(gone))})
        return self.async_show_form(step_id="shelly_valve_remove", errors=errors, description_placeholders=placeholders,
                                    data_schema=vol.Schema({
                                        vol.Required("valves"): selector.SelectSelector(selector.SelectSelectorConfig(
                                            options=choices, multiple=True, mode=selector.SelectSelectorMode.LIST)),
                                        vol.Required("confirm", default=False): selector.BooleanSelector()}))
