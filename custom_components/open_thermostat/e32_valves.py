"""Radiator valves (TRVs) per E32 room: through Zigbee2MQTT by the E32, others by Home Assistant (E32 beta.24).

The E32 owns the valve record (``GET/POST /config/heating/trv``, ``src/control/TrvConfig.h``):
per room the Zigbee2MQTT friendly names and models of its valves, and whether the
E32 drives them ("valve control", off until switched on). The E32 itself talks to
Zigbee2MQTT on the same broker; Home Assistant only shows and configures:

- per room with valves, on the room's device: "Valve position" (the mean opening
  of the valves that report one, each valve in the attributes), "Valve battery"
  (the lowest, diagnostic), "Valve problem" (a low battery or a valve that stopped
  reporting, diagnostic) and the switch "Valve control" (configuration; its entity
  ID ends in ``_valve_control``);
- Repairs: a low battery (about 20 %), a valve that stopped reporting, and a room
  whose valve control is on while the room has a single temperature source (a
  separate sensor keeps it heating when that one fails);
- the valves of a room are chosen in the room's own form, section Radiator valves
  (Configure → Rooms → Edit or remove a room → Edit room, e32_room_flow.py): just
  their climate entities; valve_routes.py decides per valve whether the E32
  drives it over Zigbee2MQTT or Home Assistant does.

A valve Home Assistant controls (ZHA, Z-Wave, Shelly, a cloud integration) is model
``ha_climate`` with its climate entity id as name: the E32 only lists it, Home
Assistant drives it on the E32's rules and reports its health, battery and opening
in the same entities (ha_valves.py).

E32 1.1 (Shelly): a Shelly BLU TRV behind a BLU Gateway Gen3 that the E32 drives
itself over local HTTP is model ``shelly_blu_trv`` named ``g<n>:<id>`` (gateway
device n of the E32's Shelly record, component blutrv:<id>), with its role
(``radiator``, or ``loop`` for a floor loop valve on the manifold) and, for a
radiator, ``keep_open`` (kept open as the water's path). A room takes up to 8
valves, more than 4 only through the gateway; 24 in all. Its room document adds
``role`` and ``link`` (the route's problem: the gateway does not answer, the
valve is silent, missing or not paired); the signal strength stays on the E32's
own page. Repairs: the gateway does not answer, a valve the gateway does not know.

Everything comes from ``fw/state/trv/<room>`` (HeatingHub.valves): without valves
there is no entity and no issue, and an entity of a room whose valves were removed
is removed again.
"""
from __future__ import annotations

import logging
import re
import time

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er, issue_registry as ir

from .const import DOMAIN
from .heating_link import ROOM_ID, RoomEntity, add_options, heating_hub, label, track_entities

_LOGGER = logging.getLogger(__name__)

KEY = "e32_valves"
# Our model ids (TrvConfig.h trvModels); what each can do is the E32's to know.
ZIGBEE_MODELS = ("bosch_bth_ra", "sonoff_trvzb", "sonoff_trv_zbt", "tuya_tv02", "generic")
HA_MODEL = "ha_climate"  # a climate entity Home Assistant drives (ha_valves.py)
GATEWAY_MODEL = "shelly_blu_trv"  # E32 1.1: a Shelly BLU TRV through the BLU Gateway Gen3 (TrvConfig.h)
MODELS = (*ZIGBEE_MODELS, HA_MODEL, GATEWAY_MODEL)
# Models without a position readback (TrvConfig.h positionKey nullptr): the E32 drives the valve by temperature (it
# sends the target), the valve opens and closes, and it reports no opening (Sonoff confirmed it for the TRV Gen2 /
# TRV-ZBT).
NO_POSITION_MODELS = ("sonoff_trvzb", "sonoff_trv_zbt", "tuya_tv02", "generic")
CLIMATE_ID = re.compile(r"climate\.[a-z0-9_]+")
# "g<gateway device number 1-99>:<blutrv component id 200-299>" (TrvConfig.h parseGatewayValveName).
GATEWAY_NAME = re.compile(r"g([1-9][0-9]?):(2[0-9]{2})")
ROLES = ("radiator", "loop")
MAX_VALVES_PER_ROOM = 8  # E32 1.1; more than MAX_CLASSIC_VALVES_PER_ROOM only through the BLU Gateway
MAX_CLASSIC_VALVES_PER_ROOM = 4
MAX_VALVES = 24
MAX_VALVES_WITHOUT_GATEWAY = 16  # an E32 without the BLU Gateway (before 1.1, or esp32dev)
MAX_NAME = 64
HEALTH = ("ok", "low_battery", "offline", "unknown")
# A BLU Gateway valve's route problem in its room document (TrvControl.h "link").
LINKS = ("gateway", "silent", "missing", "unpaired", "unknown")
ENTITY_KEYS = ("valve_position", "valve_battery", "valve_problem", "valve_control")
# A room with one temperature source is no Repairs item (1.4): the room form's help text says what it means.
ISSUES = ("valve_battery_low", "valve_offline", "valve_gateway_silent", "valve_not_found")
# A switched control shows its new state until the E32's telemetry agrees (at most this long).
PENDING_SECONDS = 30


def guess_model(text):
    """Our model id from a Zigbee2MQTT device's manufacturer/model text, or None (the installer chooses).

    By the model number only: a Bosch room thermostat (BTH-RM) is no BTH-RA valve.
    """
    text = text.lower()
    if "bth-ra" in text:
        return "bosch_bth_ra"
    if "trv-zbt" in text:  # Sonoff TRV Gen2, before the TRVZB match
        return "sonoff_trv_zbt"
    if "trvzb" in text:
        return "sonoff_trvzb"
    return "tuya_tv02" if "tv02" in text else None


def valid_name(name):
    """A Zigbee2MQTT friendly name the E32 takes (TrvConfig::validName)."""
    return (type(name) is str and 0 < len(name) <= MAX_NAME and name == name.strip() and not name.startswith("/")
            and not name.endswith("/") and "//" not in name and name != "bridge" and not name.startswith("bridge/")
            and all(0x20 <= ord(c) <= 0x7E and c not in '#+"\\' for c in name))


def valid_entity(name):
    """A climate entity id the E32 takes as an ha_climate valve (TrvConfig::validClimate)."""
    return type(name) is str and len(name) <= MAX_NAME and CLIMATE_ID.fullmatch(name) is not None


def valid_gateway_name(name):
    """A BLU Gateway valve's name the E32 takes ("g1:200")."""
    return type(name) is str and GATEWAY_NAME.fullmatch(name) is not None


def valid_valve(name, model):
    if model == HA_MODEL:
        return valid_entity(name)
    return valid_gateway_name(name) if model == GATEWAY_MODEL else valid_name(name)


def valve_record(valve):
    """One valve as the E32 stores it: name and model, and for a BLU Gateway valve its role and keep_open."""
    record = {"name": valve["name"], "model": valve["model"]}
    if valve["model"] == GATEWAY_MODEL:
        if valve.get("role") == "loop":
            record["role"] = "loop"
        if valve.get("keep_open") is True:
            record["keep_open"] = True
    return record


def _valid_record(valve):
    if type(valve) is not dict or valve.get("model") not in MODELS or not valid_valve(valve.get("name"), valve.get("model")):
        return False
    role, keep = valve.get("role"), valve.get("keep_open")
    if valve["model"] != GATEWAY_MODEL:
        return role is None and keep is None
    return role in (None, *ROLES) and keep in (None, True, False) and not (keep is True and role == "loop")


def decode_config(value):
    """The stored record of a GET/POST answer ({"schema","base_topic","rooms"}), or None."""
    if type(value) is not dict or value.get("schema") != 1 or type(value.get("base_topic")) is not str:
        return None
    rooms = value.get("rooms")
    if type(rooms) is not list or len(rooms) > 8:
        return None
    result = []
    for room in rooms:
        valves = room.get("valves") if type(room) is dict else None
        if (type(room) is not dict or type(room.get("room")) is not str or type(room.get("control")) is not bool
                or type(valves) is not list or len(valves) > MAX_VALVES_PER_ROOM
                or not all(_valid_record(v) for v in valves)
                or sum(v["model"] != GATEWAY_MODEL for v in valves) > MAX_CLASSIC_VALVES_PER_ROOM):
            return None
        result.append({"room": room["room"], "control": room["control"], "valves": [valve_record(v) for v in valves]})
    return {"schema": 1, "base_topic": value["base_topic"], "rooms": result}


def with_room(config, room_id, control=None, valves=None):
    """The record with one room changed: its control and/or its valves (an empty list removes the room)."""
    rooms = [dict(r) for r in config["rooms"]]
    room = next((r for r in rooms if r["room"] == room_id), None)
    if room is None:
        room = {"room": room_id, "control": False, "valves": []}
        rooms.append(room)
    if valves is not None:
        room["valves"] = [valve_record(v) for v in valves]
    if control is not None:
        room["control"] = control
    if not room["valves"]:
        rooms.remove(room)  # the E32 keeps no control without a valve
    return {"schema": 1, "base_topic": config["base_topic"], "rooms": rooms}


def valve_error(err):
    """A clear Home Assistant error for a refused or failed write."""
    from .controller_link import ControllerLoginRejected, HeatingPlanRejected
    if isinstance(err, ControllerLoginRejected):
        return HomeAssistantError(translation_domain=DOMAIN, translation_key="room_plan_password")
    if str(err) == "controller_no_free_session":
        return HomeAssistantError(translation_domain=DOMAIN, translation_key="e32_no_free_session")
    if isinstance(err, HeatingPlanRejected):
        if err.error == "save_unconfirmed":
            return HomeAssistantError(translation_domain=DOMAIN, translation_key="valves_unconfirmed")
        return ServiceValidationError(translation_domain=DOMAIN, translation_key="valves_rejected",
                                      translation_placeholders={"error": err.error})
    from .room_plan import link_error
    return link_error(str(err)) or HomeAssistantError(translation_domain=DOMAIN, translation_key="valves_unreachable",
                                                      translation_placeholders={"error": str(err)})


class ValveLink:
    """Reads and writes the E32's valve record over the stored controller connection.

    The record is read right before every change, so another writer (the E32
    page) is never overwritten with an old copy.
    """

    def __init__(self, hass, hub, plan):
        self.hass, self.hub, self.plan = hass, hub, plan
        self.config = None

    async def async_read(self):
        from .controller_link import ControllerLinkError
        try:
            value = decode_config(await self.plan.async_call(lambda client: client.async_valves()))
        except ControllerLinkError as err:
            raise valve_error(err) from None
        if value is None:
            raise unreadable()
        self.config = value
        return value

    async def async_change(self, room_id, control=None, valves=None):
        """POST the record with one room changed; the E32 answers with what it stored.

        The read, the change and the POST share one lock hold and one sign-in, so
        two switches changed at once each build on the other's stored record. A
        change waits for a free E32 web session (RoomPlanLink.async_call).
        """
        from .controller_link import ControllerLinkError

        async def change(client):
            current = decode_config(await client.async_valves())
            if current is None:
                raise unreadable()
            self.config = current
            return decode_config(await client.async_valves(with_room(current, room_id, control, valves)))
        try:
            answer = await self.plan.async_call(change, write=True)
        except ControllerLinkError as err:
            raise valve_error(err) from None
        if answer is None:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="valves_unconfirmed")
        self.config = answer
        return answer


    async def async_read_with_gateway(self):
        """(the record, the BLU Gateway valves the E32 lists, or None) on one sign-in, for the room form.

        The valves come from ``GET /status/shelly`` (E32 1.1): firmware without Shelly gives None.
        """
        from .controller_link import ControllerLinkError

        async def read(client):
            value = decode_config(await client.async_valves())
            if value is None:
                return None, None  # no valve record: no gateway valves either
            try:
                status = await client.async_shelly_status()
            except ControllerLinkError:
                status = None  # firmware without Shelly, or its status not readable now: no gateway valves
            return value, status
        try:
            value, status = await self.plan.async_call(read)
        except ControllerLinkError as err:
            raise valve_error(err) from None
        if value is None:
            raise unreadable()
        self.config = value
        return value, gateway_valves(status) if status is not None else None


def gateway_valves(status):
    """[{"name": "g1:200", "label", "gateway", "health", "battery"?}] of the BLU Gateways in /status/shelly.

    Only the valves the E32's Shelly record lists for each gateway (its own page adds them).
    """
    found = []
    devices = status.get("devices") if type(status) is dict else None
    for device in devices if type(devices) is list else []:
        if type(device) is not dict or device.get("kind") != "gateway" or type(device.get("valves")) is not list:
            continue
        gateway = device.get("label") if type(device.get("label")) is str and device["label"].strip() else None
        for valve in device["valves"]:
            name = valve.get("trv") if type(valve) is dict else None
            if not valid_gateway_name(name) or any(v["name"] == name for v in found):
                continue
            label = valve.get("name") if type(valve.get("name")) is str and valve["name"].strip() else None
            item = {"name": name, "label": label, "gateway": gateway, "health": valve.get("health")}
            if type(valve.get("battery")) in (int, float):
                item["battery"] = valve["battery"]
            found.append(item)
    return found


def unreadable():
    from .room_plan import link_error
    return link_error("controller_response_invalid")


def valve_link(hass, entry):
    """The entry's one link; None without a stored controller connection."""
    state = hass.data[DOMAIN][entry.entry_id]
    link = state.get(KEY)
    if link is None:
        hub = heating_hub(hass, entry)
        if hub.plan is None:
            return None
        link = state[KEY] = ValveLink(hass, hub, hub.plan)
    return link


def room_valves(hub, room_id):
    """A room's ``fw/state/trv/<room>`` with Home Assistant's view of its ha_climate valves, or None."""
    room = hub.valves.get(room_id)
    driver = getattr(hub, "ha_valves", None)
    return driver.overlay(room) if room is not None and driver is not None else room


def positions(room):
    return [v["position_pct"] for v in room.get("valves", []) if type(v.get("position_pct")) in (int, float)]


def batteries(room):
    return [v["battery_pct"] for v in room.get("valves", []) if type(v.get("battery_pct")) in (int, float)]


def problems(room):
    """[(valve name, "low_battery" | "offline")] of a room's valves."""
    return [(v["name"], v.get("health")) for v in room.get("valves", []) if v.get("health") in ("low_battery", "offline")]


def link_problems(room):
    """[(valve name, link)] of a room's BLU Gateway valves whose route has a problem (LINKS)."""
    return [(v["name"], v["link"]) for v in room.get("valves", []) if v.get("link") in LINKS]


# A BLU Gateway valve in a sentence: the E32 knows it as g<n>:<id> (the room's own name says where it is).
GATEWAY_VALVE_TEXT = {"en": "valve {id} on BLU Gateway {n}", "nl": "kraan {id} aan BLU Gateway {n}",
                      "pl": "zawór {id} na BLU Gateway {n}"}
# The route's problem in plain words (the Valve problem attributes).
LINK_TEXT = {
    "en": {"gateway": "the BLU Gateway does not answer", "silent": "the valve has not reported to the gateway",
           "missing": "the gateway does not know this valve", "unpaired": "the valve is not paired with the gateway",
           "unknown": "the gateway is not among the E32's Shelly devices"},
    "nl": {"gateway": "de BLU Gateway antwoordt niet", "silent": "de kraan heeft zich niet bij de gateway gemeld",
           "missing": "de gateway kent deze kraan niet", "unpaired": "de kraan is niet gekoppeld aan de gateway",
           "unknown": "de gateway staat niet bij de Shelly-apparaten van de E32"},
    "pl": {"gateway": "BLU Gateway nie odpowiada", "silent": "zawór nie zgłosił się do bramki",
           "missing": "bramka nie zna tego zaworu", "unpaired": "zawór nie jest sparowany z bramką",
           "unknown": "bramki nie ma wśród urządzeń Shelly w E32"},
}


# The Valves open sensor's note for such a valve (1.3: the E32 decides, the valve opens and closes; never "regulates
# itself"). The same sentence as the E32's Rooms page.
POSITION_NOTE = {"en": "Driven by temperature; the position cannot be read",
                 "nl": "Gestuurd op temperatuur; de stand is niet uit te lezen",
                 "pl": "Sterowany temperaturą; nie można odczytać położenia"}
# 1.3 (NEXT-RELEASE 1f): the temperature the E32 gave such valves, and in a mixed room how many there are, as
# sentences the dashboard's valve tile shows (state_content).
SET_TO_TEXT = {"en": ("Set to {t} °C", "Set to {t} °C (frost protection)"),
               "nl": ("Ingesteld op {t} °C", "Ingesteld op {t} °C (vorstbeveiliging)"),
               "pl": ("Ustawiono na {t} °C", "Ustawiono na {t} °C (ochrona przed mrozem)")}
DRIVEN_TEXT = {"en": ("{n} valve driven by temperature", "{n} valves driven by temperature"),
               "nl": ("{n} kraan op temperatuur gestuurd", "{n} kranen op temperatuur gestuurd"),
               "pl": ("{n} zawór sterowany temperaturą", "{n} zawory sterowane temperaturą",
                      "{n} zaworów sterowanych temperaturą")}


def language(hass):
    value = str(getattr(getattr(hass, "config", None), "language", "en") or "en")[:2]
    return value if value in LINK_TEXT else "en"


def shown_name(name, lang="en"):
    """A valve's name for a sentence: a BLU Gateway valve as "valve 200 on BLU Gateway 1"."""
    match = GATEWAY_NAME.fullmatch(name) if type(name) is str else None
    if match is None:
        return name
    return GATEWAY_VALVE_TEXT.get(lang, GATEWAY_VALVE_TEXT["en"]).format(n=match.group(1), id=match.group(2))


def driven(room):
    """The valves of a room document that the E32 drives by temperature and that report no opening."""
    return [v for v in (room or {}).get("valves", [])
            if v.get("model") in NO_POSITION_MODELS and type(v.get("position_pct")) not in (int, float)]


def tile_kind(room):
    """What the dashboard's valve tile shows for a room document: "driven" (no valve reports an opening: the
    temperature the E32 gave them), "mixed" (the average opening and how many are driven by temperature), or None
    (the average opening, as before 1.3)."""
    valves, found = (room or {}).get("valves", []), driven(room)
    if not valves or not found:
        return None
    return "driven" if len(found) == len(valves) else "mixed"


def set_to(room, status_room):
    """(°C, frost protection) the E32 gave the valves driven by temperature, or None while unknown.

    The setpoint the valves report back (the most common one), else the room's target, or 8 °C frost protection
    while the room is off (ha_valves.room_target, TrvControl::step).
    """
    from .ha_valves import FROST_C, room_target
    reported = [v["setpoint_c"] for v in driven(room) if type(v.get("setpoint_c")) in (int, float)]
    if reported:
        value = max(reported, key=reported.count)
    elif type(status_room) is dict:
        value = room_target(status_room)
    else:
        return None
    off = type(status_room) is dict and (status_room.get("status") == "inactive" or status_room.get("state") == "inactive")
    return float(value), off and float(value) == FROST_C


def degrees(value, lang="en"):
    """20.5 → "20.5" (English) or "20,5"; a whole number without decimals."""
    text = f"{value:.0f}" if float(value).is_integer() else f"{value:.1f}"
    return text if lang == "en" else text.replace(".", ",")


def set_to_text(value, frost, lang="en"):
    return SET_TO_TEXT.get(lang, SET_TO_TEXT["en"])[1 if frost else 0].format(t=degrees(value, lang))


def driven_text(count, lang="en"):
    forms = DRIVEN_TEXT.get(lang, DRIVEN_TEXT["en"])
    if lang == "pl":  # 1 zawór, 2-4 zawory (not 12-14), else zaworów
        form = forms[0] if count == 1 else forms[1] if count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14) else forms[2]
    else:
        form = forms[0 if count == 1 else 1]
    return form.format(n=count)


def valve_attributes(room):
    return {"valves": [{key: v.get(key) for key in ("name", "model", "role", "health", "link", "position_pct",
                                                    "battery_pct", "battery_low", "setpoint_c") if v.get(key) is not None}
                       for v in room.get("valves", [])],
            "control": room.get("control"), "degraded": room.get("degraded"), "single_source": room.get("single_source")}


# -- entities -----------------------------------------------------------------------------


class ValveEntity(RoomEntity):
    """One room's radiator valves; available while the E32 reports them."""

    def __init__(self, hub, room, key):
        self._attach_room(hub, room, key)

    @property
    def valves(self):
        return room_valves(self.hub, self.room_id)

    @property
    def available(self):
        return self.hub.fresh and self.room is not None and self.valves is not None


class ValvePositionSensor(ValveEntity, SensorEntity):
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:valve"

    def __init__(self, hub, room):
        super().__init__(hub, room, "valve_position")

    @property
    def native_value(self):
        values = positions(self.valves or {})
        return round(sum(values) / len(values)) if values else None

    @property
    def extra_state_attributes(self):
        attributes = valve_attributes(self.valves or {})
        lang = language(getattr(self, "hass", None))
        own = [shown_name(v["name"], lang) for v in driven(self.valves)]
        if own:  # these valves are not in the average: say why, and what the E32 gave them, in words
            attributes["driven_by_temperature"] = own
            attributes["position_note"] = POSITION_NOTE[lang]
            attributes["driven_text"] = driven_text(len(own), lang)
            given = set_to(self.valves, self.room)
            if given is not None:
                attributes["set_to_c"] = given[0]
                attributes["set_to_text"] = set_to_text(*given, lang)
        return attributes


class ValveBatterySensor(ValveEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub, room):
        super().__init__(hub, room, "valve_battery")

    @property
    def native_value(self):
        values = batteries(self.valves or {})
        return min(values) if values else None


class ValveProblemBinarySensor(ValveEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub, room):
        super().__init__(hub, room, "valve_problem")

    @property
    def is_on(self):
        return bool(problems(self.valves or {}) or link_problems(self.valves or {}))

    @property
    def extra_state_attributes(self):
        found = [{"name": name, "health": health} for name, health in problems(self.valves or {})]
        texts = LINK_TEXT[language(getattr(self, "hass", None))]
        found += [{"name": name, "link": link, "problem": texts[link]} for name, link in link_problems(self.valves or {})]
        return {"problems": found}


class ValveControlSwitch(ValveEntity, SwitchEntity):
    """The room's valve control: on, the E32 drives its valves (while its output is enabled)."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, hub, room, link, clock=time.monotonic):
        super().__init__(hub, room, "valve_control")  # unique id <prefix>_e32_room_<id>_valve_control
        self.link, self._clock, self._pending = link, clock, None

    @property
    def is_on(self):
        reported = (self.valves or {}).get("control")
        if self._pending is not None:
            value, since = self._pending
            if reported is value or self._clock() - since > PENDING_SECONDS:
                self._pending = None
            else:
                return value
        return reported if type(reported) is bool else None

    @property
    def extra_state_attributes(self):
        trv = (self.hub.status or {}).get("trv")
        return {"output": trv.get("output") if type(trv) is dict else None}

    async def _set(self, value):
        await self.link.async_change(self.room_id, control=value)
        self._pending = (value, self._clock())
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs):
        await self._set(True)

    async def async_turn_off(self, **kwargs):
        await self._set(False)


def _valve_rooms(hub):
    for room_id, valves in hub.valves.items():
        room = hub.rooms.get(room_id)
        if room is not None and valves.get("valves"):
            yield room_id, room


def wanted_sensors(hub):
    for room_id, room in _valve_rooms(hub):
        yield ("valve", room_id, "position"), lambda room=room: ValvePositionSensor(hub, room)
        yield ("valve", room_id, "battery"), lambda room=room: ValveBatterySensor(hub, room)


def wanted_binary_sensors(hub):
    for room_id, room in _valve_rooms(hub):
        yield ("valve", room_id, "problem"), lambda room=room: ValveProblemBinarySensor(hub, room)


def wanted_switches(link):
    def wanted(hub):
        for room_id, room in _valve_rooms(hub):
            yield ("valve", room_id, "control"), lambda room=room: ValveControlSwitch(hub, room, link)
    return wanted


# -- issues and removed valves --------------------------------------------------------------


def issue_id(kind, entry, room_id):
    return f"{kind}_{entry.entry_id}_{room_id}"


@callback
def sync_issues(hass, entry, hub, raised):
    """Raise and clear the valve issues of the current telemetry; raised: the ids this entry raised."""
    if not hub.fresh:
        return  # an offline E32 says nothing about its valves; "E32 offline" is its own problem
    wanted = {}
    from .insight import room_names  # the dashboard's names: a room renamed in Home Assistant keeps its name
    names = room_names(hub, hass, entry.entry_id) if hub.valves else {}
    lang = language(hass)
    silent_gateway = []
    for room_id in hub.valves:
        valves = room_valves(hub, room_id)
        room = hub.rooms.get(room_id) or {"id": room_id}
        name = names.get(room_id) or label(room) or room_id
        found = problems(valves)
        low = [n for n, h in found if h == "low_battery"]
        gone = [n for n, h in found if h == "offline"]
        if low:
            wanted[issue_id("valve_battery_low", entry, room_id)] = ("valve_battery_low", ir.IssueSeverity.WARNING,
                                                                     {"room": name, "valves": ", ".join(
                                                                         shown_name(n, lang) for n in low)})
        if gone:
            wanted[issue_id("valve_offline", entry, room_id)] = ("valve_offline", ir.IssueSeverity.WARNING,
                                                                 {"room": name, "valves": ", ".join(
                                                                     shown_name(n, lang) for n in gone)})
        # BLU Gateway valves: a gateway that does not answer (one issue for the house, below), a valve the
        # gateway does not know or that is not paired. A silent valve waits for "offline" (2 hours) above.
        links = link_problems(valves)
        silent_gateway += [f"{name}: {shown_name(n, lang)}" for n, link in links if link == "gateway"]
        lost = [shown_name(n, lang) for n, link in links if link in ("missing", "unpaired", "unknown")]
        if lost:
            wanted[issue_id("valve_not_found", entry, room_id)] = ("valve_not_found", ir.IssueSeverity.WARNING,
                                                                   {"room": name, "valves": ", ".join(lost)})
    if silent_gateway:
        wanted[f"valve_gateway_silent_{entry.entry_id}"] = ("valve_gateway_silent", ir.IssueSeverity.WARNING,
                                                            {"valves": ", ".join(silent_gateway)})
    for issue in [i for i in raised if i not in wanted]:
        ir.async_delete_issue(hass, DOMAIN, issue)
        raised.discard(issue)
    for issue, (key, severity, placeholders) in wanted.items():
        ir.async_create_issue(hass, DOMAIN, issue, is_fixable=False, is_persistent=False, severity=severity,
                              translation_key=key, translation_placeholders=placeholders)
        raised.add(issue)


TRV_ABSENT_CONFIRM_S = 600  # R-C-02: two plan messages without ``trv`` at least this far apart mean "no valves"


def _valves_gone(hub):
    """True once two plan messages at least TRV_ABSENT_CONFIRM_S apart had no ``trv`` (R-C-02).

    Firmware 1.1.0 leaves ``trv`` out of fw/config/plan once the last valve is removed (later firmware sends
    an empty list). It also leaves it out during start-up, so one such plan proves nothing; the firmware
    sends its plan on every change and at least once an hour. Counts only while the heating document has no
    valve block either; a plan that lists ``trv`` or a heating document with one starts again.
    """
    heating = hub.heating if type(hub.heating) is dict else {}
    if "trv" in hub.config or hub.config_received is None or type(heating.get("trv")) is dict:
        hub.trv_missing_since = None
        return False
    if hub.trv_missing_since is None:
        hub.trv_missing_since = hub.config_received
        return False
    return hub.config_received - hub.trv_missing_since >= TRV_ABSENT_CONFIRM_S


@callback
def remove_stale_entities(hass, entry, hub):
    """Remove the valve entities of rooms the E32 no longer lists with valves (fw/config/plan ``trv``).

    Only while the E32 is online and its plan known: an offline E32 never removes anything. One plan
    without a ``trv`` list says nothing about the valves (R4-04: the firmware leaves the key out while its
    status has no valve block, for example during start-up), so it keeps every valve entity; an explicit
    list removes the rooms it leaves out, an empty one all of them. Older firmware never sends an empty
    list: a ``trv`` missing from two plan messages at least 10 minutes apart counts as one (_valves_gone).
    """
    if not hub.fresh or hub.config is None:
        return
    listed = hub.config.get("trv")
    if type(listed) is list:
        hub.trv_missing_since = None
    elif _valves_gone(hub):
        listed = []
    else:
        return
    keep = set(listed)
    head = f"{hub.prefix}_e32_room_"
    registry = er.async_get(hass)
    for record in er.async_entries_for_config_entry(registry, entry.entry_id):
        uid = record.unique_id or ""
        if record.platform != DOMAIN or not uid.startswith(head):
            continue
        rest = uid[len(head):]
        for key in ENTITY_KEYS:
            room_id = rest[:-len(key) - 1] if rest.endswith("_" + key) else None
            if room_id and ROOM_ID.fullmatch(room_id) and room_id not in keep:
                registry.async_remove(record.entity_id)
                break


def watch(hass, entry):
    """Once per entry: keep the issues and the entities in step with the telemetry."""
    state = hass.data[DOMAIN][entry.entry_id]
    if state.get(KEY + "_watch"):
        return
    state[KEY + "_watch"] = True
    hub = heating_hub(hass, entry)
    raised = set()
    from .ha_valves import HaValveDriver
    driver = hub.ha_valves = HaValveDriver(hass, hub)
    stop_driver = driver.start()

    @callback
    def changed():
        sync_issues(hass, entry, hub, raised)
        remove_stale_entities(hass, entry, hub)

    entry.async_on_unload(hub.add_listener(changed))

    @callback
    def unload():
        stop_driver()
        if hub.ha_valves is driver:
            hub.ha_valves = None
        for issue in list(raised):
            ir.async_delete_issue(hass, DOMAIN, issue)
        raised.clear()
        state.pop(KEY + "_watch", None)
    entry.async_on_unload(unload)
    changed()


def _product(entry):
    from .product import is_product
    return is_product(entry)


async def async_setup_sensors(hass, entry, async_add_entities):
    if not _product(entry):
        return
    hub = heating_hub(hass, entry)
    entry.async_on_unload(track_entities(hub, async_add_entities, add_options(hass, entry), wanted_sensors))
    watch(hass, entry)


async def async_setup_binary_sensors(hass, entry, async_add_entities):
    if not _product(entry):
        return
    hub = heating_hub(hass, entry)
    entry.async_on_unload(track_entities(hub, async_add_entities, add_options(hass, entry), wanted_binary_sensors))


async def async_setup_switches(hass, entry, async_add_entities):
    if not _product(entry):
        return
    link = valve_link(hass, entry)
    if link is None:
        return  # no stored controller connection: the control cannot be written
    hub = heating_hub(hass, entry)
    entry.async_on_unload(track_entities(hub, async_add_entities, add_options(hass, entry), wanted_switches(link)))
