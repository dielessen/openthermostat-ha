"""Every battery of the installation on one list, with one limit (1.4.2, plan 3.5; R142-HA-CORE HC-04, Q7).

**The reader** (``battery_of``): for an entity of our model (a radiator valve, a window or door contact, a room's
setting device, a Home Assistant temperature source) it finds the battery on the same Home Assistant device: the
battery sensor (``device_class: battery``, a percentage), else the "battery low" binary sensor, and as the last
resort a ``battery_level``/``battery`` attribute of the entity itself (some climate integrations). It returns
``{"pct", "low", "reported_at", "entity_id", "stale", "unavailable_since"}`` or None when the device has no battery at
all. ``low`` is only the device's own low flag; whether a percentage is low is ``is_low`` with the one limit.
``stale``: the report is 24 hours old or older (the age rule of the v1 room editor's ``device_power._report``).
``ha_valves`` drives its valves' health with it, the notifications (HA-NOTIFY) read it for their battery messages.

**One limit, one comparison**: the devices section's setting ``battery_low_pct`` (15, 20, 25 or 30 %, default 20) in
the entry options; low = ``pct < limit``; back to normal from ``limit + 5`` (RECOVER_STEP, the notifications'
hysteresis). The firmware keeps its own fixed 20 % for the valves it drives over Zigbee2MQTT ("Valve problem",
``TrvControl::lowBatteryPct``); ``ha_valves`` reports the same health for Home Assistant's valves.

**The list** (``collect``): the E32's Bluetooth sensors (also paired ones no room measures with), the valves the E32
drives (their ``battery_pct``), Home Assistant's own valves, window and door contacts, setting devices, Home
Assistant temperature sources; one row per device (a valve that is also a room's source is one row), low first (the
lowest percentage first), then the others lowest first, then the ones without a report. Read from the hub and Home
Assistant's registries only: no sign-in on the E32. No gateway reports a battery today (the Shelly BLU Gateway runs on
USB power); the kind ``gateway`` stays in the contract for one that will.

**The entity** "Batteries low" (``<prefix>_hub_batteries_low``): the number of low batteries, 0 when none, always
there (never unavailable); its attribute ``devices`` (not recorded) lists them.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import CONF_TOPIC_PREFIX, DOMAIN

_LOGGER = logging.getLogger(__name__)

LIMIT_KEY = "battery_low_pct"   # entry options: the devices section's setting
LIMITS = (15, 20, 25, 30)
DEFAULT_LIMIT = 20               # BATTERY_LOW_PCT
RECOVER_STEP = 5                 # back to normal from limit + 5
STALE_S = 24 * 3600              # a report this old or older is stale (device_power.MAX_AGE_MS)
GONE = ("unavailable", "unknown")
KINDS = ("thermometer", "valve", "contact", "setting_device", "temperature_source", "gateway")
SENSOR_KEY = "batteries_low"     # hass.data[DOMAIN][entry_id][SENSOR_KEY]: the entity, evaluate() after a change
HA_VALVE = "ha_climate"          # e32_valves.HA_MODEL / ha_valves.HA_MODEL (no import: ha_valves imports this module)


# -- the limit ---------------------------------------------------------------------------------------------------

def limit_pct(entry):
    """The one battery limit of an installation (%): the devices section's choice, else 20."""
    value = (getattr(entry, "options", None) or {}).get(LIMIT_KEY)
    return value if type(value) is int and value in LIMITS else DEFAULT_LIMIT


def is_low(pct, limit=DEFAULT_LIMIT):
    """One comparison everywhere (HC-04): a percentage below the limit is low; 20 % at a limit of 20 is not."""
    return pct is not None and pct < limit


def recovered(pct, limit=DEFAULT_LIMIT):
    """A battery that was low counts as replaced from limit + 5 on (no message twice around the limit)."""
    return pct is not None and pct >= limit + RECOVER_STEP


# -- the reader --------------------------------------------------------------------------------------------------

def _percent(value):
    if type(value) is bool:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(number) if number == number and 0 <= number <= 100 else None


def _iso(stamp):
    if not isinstance(stamp, datetime) or stamp.utcoffset() is None:
        return None
    return stamp.astimezone(timezone.utc).isoformat(timespec="seconds")


def _reported(state):
    """When the entity last reported (its ``last_reported``, else ``last_updated``)."""
    return getattr(state, "last_reported", None) or getattr(state, "last_updated", None)


def _usable(state):
    """A state that says something now: not gone, not restored by Home Assistant from before a restart."""
    return state is not None and state.state not in GONE and state.attributes.get("restored") in (None, False)


def device_entities(hass, entity_id):
    """The other enabled entities on the entity's Home Assistant device ([] without a device)."""
    registry = er.async_get(hass)
    entry = registry.async_get(entity_id)
    if entry is None or entry.device_id is None:
        return []
    return [e for e in er.async_entries_for_device(registry, entry.device_id)
            if e.entity_id != entity_id and e.disabled_by is None]


def _battery_entities(hass, entity_id):
    """(battery sensors, battery binary sensors) on the entity's device, each sorted by entity id."""
    sensors, flags = [], []
    for entry in device_entities(hass, entity_id):
        if entry.domain not in ("sensor", "binary_sensor"):
            continue
        state = hass.states.get(entry.entity_id)
        kind = entry.device_class or entry.original_device_class or (state.attributes.get("device_class") if state else None)
        if kind == "battery":
            (sensors if entry.domain == "sensor" else flags).append(entry.entity_id)
    return sorted(sensors), sorted(flags)


def battery_entity(hass, entity_id):
    """The entity id of the battery on the entity's device (the % sensor, else the low binary sensor), or None: what a
    panel row shows the battery from, so the frontend never scans the registry itself (R142-HA-PANEL P21)."""
    sensors, flags = _battery_entities(hass, entity_id)
    return (sensors or flags or [None])[0]


def battery_of(hass, entity_id, now=None):
    """The battery on the entity's device: {pct, low, reported_at, entity_id, stale, unavailable_since}, or None when
    the device has none (no battery sensor, no low sensor, no battery attribute)."""
    now = now or dt_util.utcnow()
    sensors, flags = _battery_entities(hass, entity_id)
    pct = low = source = None
    gone = []
    for candidate in sensors:  # the first that reports a percentage
        state = hass.states.get(candidate)
        value = _percent(state.state) if _usable(state) else None
        if value is not None:
            pct, source = value, state
            break
        gone.append(state)
    for candidate in flags:
        state = hass.states.get(candidate)
        if _usable(state) and state.state in ("on", "off"):
            low = state.state == "on"
            source = source or state
            break
        gone.append(state)
    if pct is None:  # some integrations put it on the entity itself
        own = hass.states.get(entity_id)
        value = (_percent(own.attributes.get("battery_level", own.attributes.get("battery")))
                 if _usable(own) else None)
        if value is not None:
            pct, source = value, source or own
            if not sensors and not flags:
                sensors = [entity_id]
    if not sensors and not flags:
        return None
    reported = _reported(source) if source is not None else None
    age = (now - reported).total_seconds() if reported is not None and reported.utcoffset() is not None else None
    since = [s.last_changed for s in gone if s is not None and s.state in GONE]
    return {"pct": pct, "low": low, "reported_at": _iso(reported),
            "entity_id": source.entity_id if source is not None else (sensors or flags)[0],
            "stale": age is not None and age >= STALE_S,
            "unavailable_since": _iso(min(since)) if source is None and since else None}


def device_name(hass, entity_id):
    """The name of the entity's Home Assistant device (as the user renamed it), else the entity's own name."""
    entry = er.async_get(hass).async_get(entity_id)
    device = dr.async_get(hass).async_get(entry.device_id) if entry is not None and entry.device_id else None
    if device is not None and (device.name_by_user or device.name):
        return device.name_by_user or device.name
    state = hass.states.get(entity_id)
    if state is not None and state.name:
        return state.name
    return (entry.name or entry.original_name) if entry is not None and (entry.name or entry.original_name) else entity_id


def _device_id(hass, entity_id):
    entry = er.async_get(hass).async_get(entity_id)
    return entry.device_id if entry is not None and entry.device_id else None


# -- the list ----------------------------------------------------------------------------------------------------

def _e32_parts(hub):
    """(Bluetooth sensors {id: doc}, valve rooms {room id: trv doc}, fresh): the live ones, else the last the E32 left
    retained (the list stays while the E32 is offline; its figures are then the last it reported)."""
    if hub is None:
        return {}, {}, False
    ble, valves = dict(getattr(hub, "ble", None) or {}), dict(getattr(hub, "valves", None) or {})
    config = getattr(hub, "config", None) or {}
    if not ble:
        listed = config.get("ble")
        ble = {i: s for i, s in (getattr(hub, "ble_states", None) or {}).items()
               if type(s) is dict and (listed is None or i in listed)}
    if not valves:
        listed = config.get("trv")
        valves = {i: s for i, s in (getattr(hub, "trv_states", None) or {}).items()
                  if type(s) is dict and (listed is None or i in listed)}
    return ble, valves, bool(getattr(hub, "fresh", False))


def _rooms(hass, entry, hub):
    """[(room id, name, plan room or {})] in the E32's order: the plan Home Assistant last read, else the telemetry."""
    plan = getattr(getattr(hub, "plan", None), "plan", None) if hub is not None else None
    rooms = [r for r in (plan.get("rooms") or []) if type(r) is dict and type(r.get("id")) is str] if type(plan) is dict else []
    if not rooms and hub is not None:
        rooms = [{"id": room_id, "name": room.get("name")} for room_id, room in (hub.rooms or {}).items()]
    names = {}
    if hub is not None:
        from .insight import room_names  # the dashboard's names: a room renamed in Home Assistant keeps its name
        names = room_names(hub, hass, getattr(entry, "entry_id", None))
    return [(r["id"], names.get(r["id"]) or (r.get("name") or "").strip() or r["id"], r) for r in rooms]


def _valve_name(name, lang):
    from .e32_valves import shown_name
    return shown_name(name, lang)


def _row(row_id, name, kind, room, source, pct=None, low=None, reported_at=None, entity_id=None, limit=DEFAULT_LIMIT):
    flagged = low is True or is_low(pct, limit)
    return {"id": row_id, "name": name, "room": room[0] if room else None, "room_name": room[1] if room else None,
            "kind": kind, "pct": pct, "low": True if flagged else (False if pct is not None or low is False else None),
            "reported_at": reported_at, "source": source, "entity_id": entity_id}


def _order(row):
    """Low first (the lowest percentage first, a low flag without a figure after them), then the others lowest first,
    a device that only says "fine" after them, the ones without a report last; by name within."""
    pct = row["pct"]
    return (0 if row["low"] else 1 if row["low"] is False else 2, pct is None, pct if pct is not None else 0,
            str(row["name"]).casefold(), row["id"])


def collect(hass, entry, hub=None, lang="en", limit=None, now=None):
    """Every battery of the installation, as the devices section's item ``batteries`` lists it (CONTRACT-1.4.2 §2)."""
    if hub is None:
        hub = (hass.data.get(DOMAIN, {}).get(getattr(entry, "entry_id", None)) or {}).get("heating_hub")
    limit = limit_pct(entry) if limit is None else limit
    now = now or dt_util.utcnow()
    rows, seen = [], set()  # seen: Home Assistant devices (and entities without one) already on the list
    rooms = _rooms(hass, entry, hub)
    room_of = {room_id: (room_id, name) for room_id, name, _plan in rooms}
    ble, valves, fresh = _e32_parts(hub)

    # The E32's Bluetooth sensors: every paired one, in a room or not.
    from .heating_link import label
    registry = er.async_get(hass)
    prefix = getattr(hub, "prefix", None) or (getattr(entry, "data", None) or {}).get(CONF_TOPIC_PREFIX)
    for sensor_id, sensor in sorted(ble.items()):
        used = [room_of[room_id] for room_id, _name, plan in rooms if any(
            type(s) is dict and s.get("type") == "ble" and s.get("id") == sensor_id for s in plan.get("sources") or [])]
        pct = _percent(sensor.get("battery")) if sensor.get("battery") is not None else None
        age = sensor.get("age_s")
        reported = (_iso(now - timedelta(seconds=age)) if fresh and type(age) is int and age >= 0 and pct is not None
                    else None)
        room = (used[0][0], ", ".join(name for _id, name in used)) if used else None
        rows.append(_row(f"ble:{sensor_id}", label(sensor), "thermometer", room, "e32", pct, None, reported,
                         registry.async_get_entity_id("sensor", DOMAIN, f"{prefix}_e32_ble_{sensor_id}_battery")
                         if prefix else None, limit))

    # The valves of each room: the E32's own (it reports their battery), Home Assistant's (read here).
    ha_valves = []
    for room_id, doc in valves.items():
        room = room_of.get(room_id) or (room_id, room_id)
        for valve in doc.get("valves") or []:
            name = valve.get("name") if type(valve) is dict else None
            if type(name) is not str:
                continue
            if valve.get("model") == HA_VALVE:
                ha_valves.append((name, room))
                continue
            pct = _percent(valve.get("battery_pct")) if valve.get("battery_pct") is not None else None
            low = valve.get("battery_low") if type(valve.get("battery_low")) is bool else None
            rows.append(_row(f"valve:{name}", _valve_name(name, lang), "valve", room, "e32", pct, low, None, None, limit))

    # What Home Assistant knows: its valves, the setting devices, the temperature sources, the contacts.
    from .e32_comfort import room_contacts
    wanted = [(name, "valve", room) for name, room in ha_valves]
    for room_id, name, plan in rooms:
        room = (room_id, name)
        device = plan.get("setpoint_entity")
        if type(device) is str and device.split(".")[0] in ("climate", "number"):
            wanted.append((device, "setting_device", room))
        for source in plan.get("sources") or []:
            if type(source) is dict and source.get("type") == "ha" and type(source.get("id")) is str:
                wanted.append((source["id"], "temperature_source", room))
    for room_id, name, _plan in rooms:
        for contact in room_contacts(entry, room_id) if entry is not None else []:
            if type(contact) is str:
                wanted.append((contact, "contact", (room_id, name)))
    for entity_id, kind, room in wanted:
        item = registry.async_get(entity_id)
        if item is not None and item.platform == DOMAIN:
            continue  # one of ours (an E32 Bluetooth sensor's reading): listed above as the E32's
        key = _device_id(hass, entity_id) or entity_id
        if key in seen:
            continue
        found = battery_of(hass, entity_id, now)
        if found is None:
            continue
        seen.add(key)
        rows.append(_row(f"ha:{key}", device_name(hass, entity_id), kind, room, "home_assistant", found["pct"],
                         found["low"], found["reported_at"], found["entity_id"], limit))
    rows.sort(key=_order)
    return rows


def low_devices(rows):
    """The attribute ``devices`` of "Batteries low": the low ones, as the notifications and the dashboard name them."""
    return [{"name": r["name"], "room": r["room_name"], "kind": r["kind"], "pct": r["pct"]} for r in rows if r["low"]]


def watched_entities(rows, extra=()):
    """The Home Assistant entities whose state changes the list."""
    return sorted({r["entity_id"] for r in rows if r["source"] == "home_assistant" and r["entity_id"]} | set(extra))


# -- the entity --------------------------------------------------------------------------------------------------

class BatteriesLowSensor(SensorEntity):
    """"Batteries low": how many batteries of the installation are below the limit (0 when none), always there."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = SENSOR_KEY
    # The list changes with every battery; the count has the history.
    _unrecorded_attributes = frozenset({"devices", "limit_pct"})

    def __init__(self, entry, hub):
        self.entry, self.hub = entry, hub
        self._attr_unique_id = f"{hub.prefix}_hub_{SENSOR_KEY}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, hub.prefix)})
        self.rows = []
        self._watched = ()
        self._unwatch = None
        self._written = None

    @property
    def available(self):
        return True

    @property
    def native_value(self):
        return sum(1 for r in self.rows if r["low"])

    @property
    def extra_state_attributes(self):
        return {"devices": low_devices(self.rows), "limit_pct": limit_pct(self.entry)}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(self.hub.add_listener(self.evaluate))
        self.async_on_remove(self._stop_watching)
        self.evaluate()

    @callback
    def _stop_watching(self):
        if self._unwatch is not None:
            self._unwatch()
            self._unwatch = None
        self._watched = ()

    @callback
    def _changed(self, _event):
        self.evaluate()

    @callback
    def evaluate(self, *_args):
        """Read the list again; write the state only when the count or the low devices changed."""
        hass = getattr(self, "hass", None)
        if hass is None:
            return
        from .settings import language
        try:
            self.rows = collect(hass, self.entry, self.hub, language(hass))
        except Exception:  # noqa: BLE001 - a count, never an exception into the hub's listeners
            _LOGGER.exception("OpenThermostat: reading the batteries failed")
            return
        # Follow the battery entities and, for a device that has none yet, the entities themselves.
        watched = tuple(watched_entities(self.rows))
        if watched != self._watched:
            self._stop_watching()
            self._watched = watched
            if watched:
                self._unwatch = async_track_state_change_event(hass, list(watched), self._changed)
        token = (self.native_value, repr(self.extra_state_attributes))
        if token != self._written and self.entity_id is not None:
            self._written = token
            self.async_write_ha_state()


async def async_setup_sensor(hass, entry, async_add_entities):
    """Product entries: "Batteries low" on the E32 device, from the start (no firmware gate: never unavailable)."""
    from .heating_link import add_options, heating_hub
    hub = heating_hub(hass, entry)
    sensor = BatteriesLowSensor(entry, hub)
    hass.data[DOMAIN][entry.entry_id][SENSOR_KEY] = sensor

    async def options_updated(_hass, _entry):
        sensor.evaluate()  # a new limit or other contacts: count again at once

    entry.async_on_unload(entry.add_update_listener(options_updated))
    async_add_entities([sensor], **add_options(hass, entry))


def refresh(hass, entry):
    """After a save that changes the list (the limit): the entity counts again and the dashboard follows the limit."""
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}
    sensor = state.get(SENSOR_KEY)
    if sensor is not None:
        sensor.evaluate()
    dashboard = state.get("dashboard")
    if dashboard is not None and callable(getattr(dashboard, "_schedule_refresh", None)):
        dashboard._schedule_refresh()
