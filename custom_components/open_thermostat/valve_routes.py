"""Which way a radiator valve is driven: by the E32 itself over Zigbee2MQTT, or through Home Assistant.

The room form only asks for the valves' climate entities. For each one Home
Assistant's own registries decide the route:

- a Zigbee2MQTT valve (an ``mqtt`` climate entity on a device with the
  identifier ``zigbee2mqtt_0x…``) of a model the E32 drives itself
  (``src/control/TrvConfig.h`` trvModels: Bosch BTH-RA, Sonoff TRVZB, Sonoff TRV
  Gen2 / TRV-ZBT, Tuya TV02) on the E32's Zigbee2MQTT base topic: the E32 gets
  its Zigbee2MQTT friendly name and model and drives it over MQTT, also while
  Home Assistant is down ("works without Home Assistant");
- every other valve (ZHA, Z-Wave, Shelly, a cloud integration, a Zigbee2MQTT
  valve of another model or another Zigbee2MQTT instance): model
  ``ha_climate`` with its entity ID, driven by Home Assistant on the E32's
  rules (ha_valves.py, "through Home Assistant").

The friendly name comes from the device's MQTT topics (``<base>/<friendly
name>``, from the MQTT integration's debug info of its entities), not from the
Home Assistant device name: a device renamed in Home Assistant keeps its
Zigbee2MQTT name. Without known topics the device name Zigbee2MQTT gave it
(``name``, never ``name_by_user``) is used.

A valve stored before (the E32 valve record) keeps its model: a Zigbee2MQTT
valve maps back to its entity by its friendly name; one Home Assistant no
longer knows stays as stored and is listed as kept. A valve stored "through
Home Assistant" that is now a Zigbee2MQTT valve the E32 drives itself moves
to the E32 at the next save of its room (shown in the form before that),
unless the installer chose "Through Home Assistant" for it under Advanced:
that choice is kept in the entry options (``valves_through_ha``).

E32 1.1: a Shelly BLU TRV behind a BLU Gateway that the E32 drives itself
(model ``shelly_blu_trv``, name ``g<n>:<id>``) is not a climate entity here: the
room form lists the gateway's valves from the E32 (gateway_route) with their
role (radiator or floor loop valve) and "keep open".
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .e32_valves import GATEWAY_MODEL, HA_MODEL, ZIGBEE_MODELS, guess_model, valid_entity, valid_name, valve_record

# The entities the installer explicitly keeps "Through Home Assistant" (Advanced), in the entry options.
CONF_THROUGH_HA = "valves_through_ha"

Z2M_PREFIX = "zigbee2mqtt_"
Z2M_BRIDGE_PREFIX = "zigbee2mqtt_bridge_"
# Topics of a Zigbee2MQTT device that are not its state topic <base>/<friendly name>.
OTHER_TOPIC_ENDS = ("/availability", "/set", "/get")
# The models the E32 drives itself; "generic" (setpoint only) is chosen by hand only.
AUTOMATIC_MODELS = tuple(m for m in ZIGBEE_MODELS if m != "generic")

ROUTE_TEXT = {
    "en": {"direct": "works without Home Assistant", "ha": "through Home Assistant",
           "kept": "not found in Home Assistant, kept as it was", "none": "No radiator valves yet.",
           "unknown": "model not recognised", "gateway": "Shelly BLU TRV through the BLU Gateway",
           "loop": "floor loop valve", "keep_open": "kept open as the water's path"},
    "nl": {"direct": "werkt zonder Home Assistant", "ha": "via Home Assistant",
           "kept": "niet gevonden in Home Assistant, blijft zoals hij was", "none": "Nog geen radiatorkranen.",
           "unknown": "model niet herkend", "gateway": "Shelly BLU TRV via de BLU Gateway",
           "loop": "kraan van een vloergroep", "keep_open": "blijft open als weg voor het water"},
}
ROUTE_HEADING = {"en": "Radiator valves:", "nl": "Radiatorkranen:"}
MODEL_NAMES = {"bosch_bth_ra": "Bosch BTH-RA", "sonoff_trvzb": "Sonoff TRVZB", "sonoff_trv_zbt": "Sonoff TRV Gen2",
               "tuya_tv02": "Tuya TV02", "generic": "Zigbee2MQTT"}


@dataclass(frozen=True)
class ValveRoute:
    """One valve as the E32 stores it ({name, model}) and what Home Assistant knows about it."""

    name: str                    # the record's name: the friendly name (direct) or the entity ID
    model: str                   # one of ZIGBEE_MODELS (direct) or HA_MODEL
    entity_id: str | None = None  # None: a stored valve Home Assistant does not know (kept)
    friendly: str | None = None  # its Zigbee2MQTT friendly name on the E32's base topic, if it has one
    detected: str | None = None  # the model recognised from Home Assistant's device registry
    role: str | None = None      # a BLU Gateway valve: "loop" on the floor manifold, else a radiator
    keep_open: bool = False      # a BLU Gateway radiator kept open as the water's path

    @property
    def direct(self):
        return self.model != HA_MODEL

    @property
    def gateway(self):
        return self.model == GATEWAY_MODEL

    def record(self):
        return valve_record({"name": self.name, "model": self.model, "role": self.role, "keep_open": self.keep_open})


def gateway_route(name, label=None, role=None, keep_open=False):
    """A BLU Gateway valve (g<n>:<id>) with its label from the E32 (friendly), role and keep_open."""
    loop = role == "loop"
    return ValveRoute(name, GATEWAY_MODEL, None, label, None, "loop" if loop else None, bool(keep_open) and not loop)


def is_z2m_device(device):
    """A device Zigbee2MQTT announced over MQTT discovery (not its bridge)."""
    return device is not None and any(
        domain == "mqtt" and str(ident).startswith(Z2M_PREFIX) and not str(ident).startswith(Z2M_BRIDGE_PREFIX)
        for domain, ident in device.identifiers)


def detect_model(device):
    """Our model id from the device's manufacturer, model and model id, or None (not recognised)."""
    text = " ".join(str(v or "") for v in (device.manufacturer, device.model, getattr(device, "model_id", None)))
    model = guess_model(text)
    return model if model in AUTOMATIC_MODELS else None


def friendly_from_topics(topics, base_topic):
    """The friendly name in <base>/<friendly name> that the topics agree on, or None.

    Availability, command and bridge topics are left out; two different names
    (a device that moved between names while its entities were set up) give None.
    """
    prefix = str(base_topic or "").rstrip("/") + "/"
    counts = Counter()
    for topic in topics:
        if type(topic) is not str or not topic.startswith(prefix) or "+" in topic or "#" in topic:
            continue
        rest = topic[len(prefix):]
        if not rest or rest == "bridge" or rest.startswith("bridge/") or rest.endswith(OTHER_TOPIC_ENDS):
            continue
        counts[rest] += 1
    ranked = counts.most_common(2)
    if not ranked or len(ranked) == 2 and ranked[0][1] == ranked[1][1]:
        return None
    return ranked[0][0] if valid_name(ranked[0][0]) else None


def device_topics(hass, device_id):
    """The MQTT topics of a device's entities (subscriptions and discovery), from the MQTT debug info."""
    try:
        from homeassistant.components.mqtt.debug_info import info_for_device
        info = info_for_device(hass, device_id)
    except Exception:  # noqa: BLE001 - MQTT not set up (yet): no topics, the device name is used
        return []
    topics = []
    for entity in info.get("entities", []):
        topics += [s.get("topic") for s in entity.get("subscriptions", []) if type(s) is dict]
        payload = (entity.get("discovery_data") or {}).get("payload")
        if isinstance(payload, dict):
            topics += [v for k, v in payload.items() if str(k).endswith("_topic") and type(v) is str
                       and not str(k).endswith("command_topic")]
    return [t for t in topics if type(t) is str]


def friendly_name(hass, device, base_topic):
    """The device's Zigbee2MQTT friendly name on the E32's base topic, or None.

    From its topics when Home Assistant knows them (a device on another base
    topic is not reachable for the E32: None); otherwise the name Zigbee2MQTT
    gave the device (never the name the user gave it in Home Assistant).
    """
    topics = device_topics(hass, device.id)
    if topics:
        return friendly_from_topics(topics, base_topic)
    return device.name if valid_name(device.name) and not str(device.name).startswith("Zigbee2MQTT") else None


class RouteFinder:
    """Routes for climate entities and the entities of stored valves, for one form."""

    def __init__(self, hass, base_topic):
        self.hass, self.base_topic = hass, base_topic or "zigbee2mqtt"
        self.entities, self.devices = er.async_get(hass), dr.async_get(hass)
        self._index = None

    def _z2m(self, entity_id):
        """(device, friendly name) of a Zigbee2MQTT climate entity, else (None, None)."""
        entry = self.entities.async_get(entity_id)
        if entry is None or entry.platform != "mqtt" or not entry.device_id:
            return None, None
        device = self.devices.async_get(entry.device_id)
        if not is_z2m_device(device):
            return None, None
        return device, friendly_name(self.hass, device, self.base_topic)

    def route(self, entity_id, model=None):
        """The route of a newly chosen climate entity; model: the installer's choice (Advanced), if any."""
        device, friendly = self._z2m(entity_id)
        detected = detect_model(device) if device is not None else None
        chosen = detected if model is None else model
        if friendly and chosen in ZIGBEE_MODELS:
            return ValveRoute(friendly, chosen, entity_id, friendly, detected)
        return ValveRoute(entity_id, HA_MODEL, entity_id, friendly, detected)

    def z2m_details(self, entity_id):
        """(friendly name, detected model, device model text) for the Advanced step; None when not Zigbee2MQTT."""
        device, friendly = self._z2m(entity_id)
        if device is None or not friendly:
            return None
        text = " ".join(str(v) for v in (device.manufacturer, device.model, getattr(device, "model_id", None)) if v)
        return friendly, detect_model(device), text

    def index(self):
        """{friendly name: climate entity} of the Zigbee2MQTT climate entities on the E32's base topic."""
        if self._index is None:
            found = {}
            for entry in list(self.entities.entities.values()):
                if entry.domain != "climate" or entry.platform != "mqtt":
                    continue
                _device, friendly = self._z2m(entry.entity_id)
                if friendly:
                    found.setdefault(friendly, entry.entity_id)
            self._index = found
        return self._index

    def stored(self, valves, through_ha=()):
        """The stored valves of a room as routes, each with its entity (None: Home Assistant does not know it).

        A Home Assistant valve the E32 can now drive itself gets that route (saved with the room),
        unless it is in through_ha: the installer's explicit choice.
        """
        routes = []
        for valve in valves:
            name, model = valve["name"], valve["model"]
            if model == HA_MODEL:
                entity = name if valid_entity(name) else None
                found = self.route(entity) if entity is not None and entity not in through_ha else None
                routes.append(found if found is not None and found.direct
                              else ValveRoute(name, model, entity, *self._friendly_detected(entity)))
            else:
                entity = self.index().get(name)
                routes.append(ValveRoute(name, model, entity, name, *self._friendly_detected(entity)[1:]))
        return routes

    def _friendly_detected(self, entity_id):
        if entity_id is None:
            return None, None
        device, friendly = self._z2m(entity_id)
        return friendly, detect_model(device) if device is not None else None


def through_ha_choices(entry):
    """The climate entities the installer keeps "Through Home Assistant" (Advanced)."""
    value = (getattr(entry, "options", None) or {}).get(CONF_THROUGH_HA)
    return {e for e in value if valid_entity(e)} if type(value) is list else set()


@callback
def save_through_ha(hass, entry, entities):
    """Store those choices without a reload (the same no-reload marker as the comfort and energy steps)."""
    from .energy_input import ENERGY_ONLY_UPDATE
    options = {**entry.options, CONF_THROUGH_HA: sorted(entities)}
    if not entities:
        options.pop(CONF_THROUGH_HA)
    if options == dict(entry.options):
        return False
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if state is not None:
        state[ENERGY_ONLY_UPDATE] = dict(options)
    if not hass.config_entries.async_update_entry(entry, options=options) and state is not None:
        state.pop(ENERGY_ONLY_UPDATE, None)  # no listener runs: never leave the marker behind
    return True


def kept_pins(pins, records, rooms=None):
    """The "Through Home Assistant" choices that are still a valve of a room (1.4.2, HC-02): a pin is an entity stored
    with model ha_climate in some room's valves (``records``: valve records, {"room"?, "name", "model"}; ``rooms``: only
    the records of these room ids count, None: every record). A removed valve or room leaves no choice behind."""
    present = {v.get("name") for v in records if type(v) is dict and v.get("model") == HA_MODEL
               and (rooms is None or v.get("room") in rooms)}
    return {pin for pin in pins if pin in present}


async def async_prune_through_ha(hass, entry, rooms=None):
    """Forget the pins of valves no room has any more (after a room was removed, and once by migration): one read of
    the E32's valve record; nothing changes when it cannot be read. ``rooms``: the room ids the plan still has (a
    valve record of a removed room does not count). True when the options changed."""
    from homeassistant.exceptions import HomeAssistantError
    from .e32_valves import valve_link
    pins = through_ha_choices(entry)
    link = valve_link(hass, entry) if pins else None
    if link is None:
        return False
    try:
        config, _gateway = await link.async_read_with_gateway()
    except HomeAssistantError:
        return False
    if config is None:
        return False
    records = [{**v, "room": r["room"]} for r in config["rooms"] for v in r["valves"]]
    kept = kept_pins(pins, records, rooms)
    return kept != pins and save_through_ha(hass, entry, kept)


def language_of(flow):
    language = ((getattr(flow, "context", None) or {}).get("language") or flow.hass.config.language or "en")[:2]
    return language if language in ROUTE_TEXT else "en"


def model_choice_text(hass, entity_id, friendly, device_text):
    """The Advanced step's line for one valve: its name, its Zigbee2MQTT name and what its device says it is."""
    state = hass.states.get(entity_id)
    shown = state.attributes.get("friendly_name") if state is not None else None
    shown = shown if type(shown) is str and shown.strip() else entity_id
    parts = [shown] + ([f"Zigbee2MQTT: {friendly}"] if friendly != shown else []) + ([device_text] if device_text else [])
    return " · ".join(parts)


def route_lines(hass, routes, language="en"):
    """Per valve one plain line: its name and its route ("works without Home Assistant")."""
    text = ROUTE_TEXT.get(language, ROUTE_TEXT["en"])
    lines = []
    for route in routes:
        if route.gateway:
            from .e32_valves import shown_name
            extra = [text["loop"]] if route.role == "loop" else [text["keep_open"]] if route.keep_open else []
            shown = route.friendly or shown_name(route.name, language)
            lines.append(f"- {shown}: {text['direct']} ({', '.join([text['gateway'], *extra])})")
            continue
        state = hass.states.get(route.entity_id) if route.entity_id else None
        shown = state.attributes.get("friendly_name") if state is not None else None
        shown = shown if type(shown) is str and shown.strip() else route.name
        if route.entity_id is None:
            lines.append(f"- {shown}: {text['direct'] if route.direct else text['ha']} ({text['kept']})")
        elif route.direct:
            lines.append(f"- {shown}: {text['direct']} ({MODEL_NAMES.get(route.model, route.model)})")
        elif route.friendly and route.detected is None:
            lines.append(f"- {shown}: {text['ha']} ({text['unknown']})")
        else:
            lines.append(f"- {shown}: {text['ha']}")
    return "\n".join(lines) or text["none"]


# -- one role per valve (1.4.2) ---------------------------------------------------------------------------------------

def valve_entities(hass, config, driven_only=False):
    """{room id: [climate entity]} of the radiator valves in the E32's valve record (``decode_config``): a Home
    Assistant valve by its entity ID, a Zigbee2MQTT valve by the entity of its friendly name; a BLU Gateway valve is
    no climate entity here. ``driven_only``: only rooms whose valve control is on (the E32 drives those valves)."""
    finder = RouteFinder(hass, (config or {}).get("base_topic"))
    found = {}
    for room in (config or {}).get("rooms") or []:
        if driven_only and room.get("control") is not True:
            continue
        entities = [_valve_entity(finder, valve) for valve in room.get("valves") or []]
        entities = [entity for entity in entities if entity]
        if entities:
            found[room["room"]] = entities
    return found


def _valve_entity(finder, valve):
    if valve.get("model") == GATEWAY_MODEL:
        return None
    return valve["name"] if valve.get("model") == HA_MODEL else finder.index().get(valve["name"])


def two_roles(room_id, setpoint_entity, routes, control, ctx=None, plan=None):
    """The device that a save would make both a room's setting device and a radiator valve the E32 drives, or None.

    One role per valve (1.4.2, plan 3.1): as the setting device its temperature is the user's wish (the room
    follows, writes its target back, and the valve opens and closes on its own sensor with valve control off); as a
    valve the E32 drives the same temperature is the E32's lever (the target, 8 °C in a pause or Off, the warm-up
    target), no wish. Both at once would read the E32's own writes as knob turns.

    ``room_id``: the room being saved ("" or None: a new one); ``setpoint_entity``: its setting device after the
    save; ``routes`` and ``control``: its radiator valves (ValveRoute) and valve control after the save; ``ctx``:
    the room form's valve context (e32_room_flow.valve_context: the other rooms' valves and their valve control);
    ``plan``: the room plan (the other rooms' setting devices). The room form (Configure) and the settings panel
    refuse such a save with the code ``device_two_roles`` on the field ``setpoint_entity``
    (e32_room_flow.room_parts calls this for both).
    """
    mine = setpoint_entity if type(setpoint_entity) is str and setpoint_entity.startswith("climate.") else None
    driven = {route.entity_id for route in routes or () if control and route.entity_id and not route.gateway}
    if mine is not None and mine in driven:
        return mine
    if mine is not None and ctx is not None:
        for room in (getattr(ctx, "config", None) or {}).get("rooms") or []:
            if room.get("room") == room_id or room.get("control") is not True:
                continue
            if any(_valve_entity(ctx.finder, valve) == mine for valve in room.get("valves") or []):
                return mine
    for other in (plan or {}).get("rooms") or []:
        if type(other) is dict and other.get("id") != room_id and other.get("setpoint_entity") in driven:
            return other["setpoint_entity"]
    return None
