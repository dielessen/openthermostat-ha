"""Heating circuits and floor probes that the E32 drives itself (E32 1.1, Shelly; SHELLY-PLAN.nl.md §4.13).

The E32 switches the floor pump on its Shelly Plug, reads the floor's supply and return on The Pill and drives
the BLU TRVs through the BLU Gateway, over local HTTP, also while Home Assistant and the MQTT broker are away.
Home Assistant only shows it, from two retained topics (TELEMETRIEBUDGET.nl.md §16, §17), so no value appears
twice:

- ``fw/state/circuit/<id>`` (listed in ``fw/config/plan`` ``circuits``): one device per circuit ("Floor circuit",
  "Radiator circuit") with the pump (running, its reason in words, its power), the supply, the return and their
  difference, the problem in words, and the select "Floor pump mode" (Automatic, On for 1 hour, Off for 1 hour):
  the owner's override, ``POST /config/shelly/circuit`` over the stored E32 connection (Home Assistant never
  talks to the Plug). Whether the E32 switches the pump at all ("Pump control by the E32"), the highest water
  temperature to the floor and how long the pump runs on at most while the water is still warm are settings:
  Configure → Heating and boiler → Heating circuits (the Shelly record, ``GET``/``POST /config/shelly``);
- ``fw/state/probes``: The Pill's probes that no circuit uses, one temperature sensor per role ("Floor supply",
  "Floor loop 2 return") on the E32 device;
- ``fw/telemetry/flow`` ``flow.zone`` (TELEMETRIEBUDGET.nl.md §19, only with circuits): the diagnostic sensor "Heat
  goes to" on the E32 device (the floor only, the radiators, both, nobody asks), with ``path`` (the boiler's heat
  has an open path) and ``limited`` (a too-hot floor holds the request at the lowest water temperature). No new
  polling: the flow document comes every 5 minutes and on a change.

Repairs, each with what to do: the pump's Plug does not answer (another device at its address, its password),
the pump takes no power (is the pump's own switch still in the way?), the floor water too hot, the supply probe
or a probe without a reading. The thresholds are the E32's (3 minutes for the Plug, 2 for no power and too hot,
5 for a probe), so nothing is raised for a short hiccup. Without the topics nothing appears and nothing is
logged; a circuit or probe that leaves the E32 loses its entities (a circuit also its device).
"""
from __future__ import annotations

import json
import logging
import time

import probatio as vol
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory, UnitOfPower, UnitOfTemperature
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import device_registry as dr, entity_registry as er, issue_registry as ir, selector
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .heating_link import CIRCUIT_ID, PROBE_ROLES, HubEntity, add_options, heating_hub, plan_circuits, track_entities

_LOGGER = logging.getLogger(__name__)

KEY = "e32_shelly"
# CircuitControl.h: the pump rule's reasons and the circuit's faults.
PUMP_REASONS = ("idle", "demand", "run_on", "frost", "exercise", "manual_on", "manual_off", "too_hot")
FAULTS = ("unreachable", "wrong_device", "auth_failed", "device_error", "no_power", "probe_missing")
PROBLEMS = ("none", *FAULTS, "too_hot")
# The select: the E32's own rule, or the owner's on/off for MANUAL_MINUTES (the E32 allows 1-1440).
PUMP_MODES = ("automatic", "on", "off")
# ShellyConfig.h: a circuit pump's highest water temperature (max_supply_c, 50 by default; "too hot" is 5 degC above
# it for 2 minutes) and the cap of the run-on while the water is still warm (run_on_max_s, 1800 s; E32 P9), both
# left out of the record at their default. Configure shows the cap in whole minutes.
MAX_SUPPLY_C = (30, 70, 50)
RUN_ON_MAX_MINUTES = (0, 120, 30)
MANUAL_MINUTES = 60
# A changed select shows its new state until the E32's telemetry agrees (at most this long).
PENDING_SECONDS = 30
# Per circuit: (entity key, platform); the unique id is <prefix>_e32_circuit_<id>_<key>.
CIRCUIT_KEYS = ("pump", "pump_reason", "pump_power", "supply", "return", "delta", "problem", "pump_mode")
# P5's decision for the house (FlowPolicy::addZoneJson, Zones::name): who asks for heat.
ZONE_DEMANDS = ("floor_only", "radiators", "mixed", "none")
ZONE_KEY = "heat_goes_to"
# A probe without any fw/state/probes for this long while the E32 reports (it refreshes every 5 minutes) is gone.
PROBES_GONE_SECONDS = 900
# The Repairs of a circuit's fault (and its too-hot reason); the probes without a circuit share one.
FAULT_ISSUES = {"unreachable": "circuit_pump_unreachable", "device_error": "circuit_pump_error",
                "wrong_device": "circuit_pump_wrong_device", "auth_failed": "circuit_pump_password",
                "no_power": "circuit_pump_no_power", "probe_missing": "circuit_probe_missing"}
TOO_HOT_ISSUE = "circuit_too_hot"
PROBE_ISSUE = "probe_no_reading"
ISSUES = (*FAULT_ISSUES.values(), TOO_HOT_ISSUE, PROBE_ISSUE)

# Names in a Repairs sentence (placeholders are not translated): the circuit's device and the probe roles.
CIRCUIT_NAMES = {"en": {"floor": "Floor circuit", "radiators": "Radiator circuit"},
                 "nl": {"floor": "Vloercircuit", "radiators": "Radiatorcircuit"}}
PROBE_NAMES = {
    "en": {"floor_supply": "Floor supply", "floor_return": "Floor return",
           **{f"loop_return_{n}": f"Floor loop {n} return" for n in range(1, 9)},
           **{f"other_{n}": f"Extra probe {n}" for n in range(1, 5)}},
    "nl": {"floor_supply": "Aanvoer vloer", "floor_return": "Retour vloer",
           **{f"loop_return_{n}": f"Retour vloergroep {n}" for n in range(1, 9)},
           **{f"other_{n}": f"Extra sonde {n}" for n in range(1, 5)}},
}


def language(hass):
    value = str(getattr(getattr(hass, "config", None), "language", "en") or "en")[:2]
    return value if value in CIRCUIT_NAMES else "en"


def circuit_device_identifier(prefix, circuit_id):
    """The device of one heating circuit (its own device, linked via the product device)."""
    return DOMAIN, f"{prefix}_e32_circuit_{circuit_id}"


def pump_of(circuit):
    pump = (circuit or {}).get("pump")
    return pump if type(pump) is dict else None


def circuit_keys(circuit):
    """The entity keys a circuit document asks for: the pump's only with a pump, a probe's only with that probe."""
    keys = ["problem"]
    if pump_of(circuit) is not None:
        keys += ["pump", "pump_reason", "pump_power", "pump_mode"]
    supply, ret = "supply_health" in circuit, "return_health" in circuit
    keys += [key for key, wanted in (("supply", supply), ("return", ret), ("delta", supply and ret)) if wanted]
    return keys


def problem(circuit):
    """The circuit's problem: a fault of CircuitControl, the too-hot stop, "none"; None for a code this release
    does not know."""
    fault = circuit.get("fault")
    if fault is not None:
        return fault if fault in FAULTS else None
    return "too_hot" if (pump_of(circuit) or {}).get("reason") == "too_hot" else "none"


def shelly_error(err):
    """A clear Home Assistant error for a refused or failed pump change."""
    from .controller_link import ControllerLoginRejected, HeatingPlanRejected
    if isinstance(err, ControllerLoginRejected):
        return HomeAssistantError(translation_domain=DOMAIN, translation_key="room_plan_password")
    if str(err) == "controller_no_free_session":
        return HomeAssistantError(translation_domain=DOMAIN, translation_key="e32_no_free_session")
    if isinstance(err, HeatingPlanRejected):
        if err.error == "save_unconfirmed":
            return HomeAssistantError(translation_domain=DOMAIN, translation_key="shelly_unconfirmed")
        return ServiceValidationError(translation_domain=DOMAIN, translation_key="shelly_rejected",
                                      translation_placeholders={"error": err.error})
    from .room_plan import link_error
    return link_error(str(err)) or HomeAssistantError(translation_domain=DOMAIN, translation_key="shelly_unreachable",
                                                      translation_placeholders={"error": str(err)})


class ShellyLink:
    """The pump override and the Shelly record over the stored E32 connection (the room plan's sign-in and lock)."""

    def __init__(self, plan):
        self.plan = plan

    async def async_pump(self, circuit_id, mode, minutes=MANUAL_MINUTES):
        """POST the owner's pump override of one circuit: automatic, or on/off for minutes."""
        from .controller_link import ControllerLinkError
        if mode not in PUMP_MODES or not CIRCUIT_ID.fullmatch(str(circuit_id)):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="shelly_rejected",
                                         translation_placeholders={"error": "invalid_pump"})
        command = {"id": circuit_id, "pump": mode, **({} if mode == "automatic" else {"minutes": minutes})}
        try:
            await self.plan.async_call(lambda client: client.async_shelly_circuit(command), write=True,
                                       key=("pump", circuit_id))
        except ControllerLinkError as err:
            raise shelly_error(err) from None

    async def async_record(self):
        """The Shelly record as GET /config/shelly shows it (no secrets)."""
        from .controller_link import ControllerLinkError
        try:
            record = await self.plan.async_call(lambda client: client.async_shelly())
        except ControllerLinkError as err:
            raise shelly_error(err) from None
        if type(record) is not dict or type(record.get("devices")) is not list:
            raise shelly_error(ControllerLinkError("controller_response_invalid"))
        return record

    async def async_pump_control(self, circuit_id, control):
        """Switch "Pump control by the E32" of one circuit: read the record, change that flag, POST it back.

        The read and the write share one sign-in and the lock, so a change on the E32 page in between is not
        lost; the devices go back without "password" (the E32 keeps each stored one). Returns the stored record.
        """
        from .controller_link import ControllerLinkError

        async def change(client):
            record = await client.async_shelly()
            document = with_pump_control(record, circuit_id, control)
            if document is None:
                raise ControllerLinkError("controller_response_invalid")
            return await client.async_shelly(document)
        try:
            stored = await self.plan.async_call(change, write=True, key=("pump_control", circuit_id))
        except ControllerLinkError as err:
            raise shelly_error(err) from None
        if pump_control(stored, circuit_id) is not control:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="shelly_unconfirmed")
        return stored

    async def async_pump_settings(self, circuit_id, settings):
        """Change a circuit pump's settings in one read-modify-write of the record (as async_pump_control).

        ``settings``: any of ``control`` (bool), ``max_supply_c`` (degC) and ``run_on_max_minutes``; the stored record
        must show every one of them afterwards. Returns the stored record.
        """
        from .controller_link import ControllerLinkError

        async def change(client):
            record = await client.async_shelly()
            document = with_pump_settings(record, circuit_id, settings)
            if document is None:
                raise ControllerLinkError("controller_response_invalid")
            return await client.async_shelly(document)
        try:
            stored = await self.plan.async_call(change, write=True, key=("pump_settings", circuit_id))
        except ControllerLinkError as err:
            raise shelly_error(err) from None
        now = pump_settings(stored, circuit_id) or {}
        if any(now.get(key) != value for key, value in settings.items()):
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="shelly_unconfirmed")
        return stored


def record_circuits(record):
    """The circuits of a Shelly record (GET /config/shelly), [] without any."""
    circuits = record.get("circuits") if type(record) is dict else None
    return [c for c in circuits if type(c) is dict and type(c.get("id")) is str] if type(circuits) is list else []


def pump_control(record, circuit_id):
    """The circuit's "Pump control by the E32" in a Shelly record, or None (no such circuit or no pump)."""
    circuit = next((c for c in record_circuits(record) if c["id"] == circuit_id), None)
    pump = (circuit or {}).get("pump")
    return pump.get("control") if type(pump) is dict and type(pump.get("control")) is bool else None


def pump_settings(record, circuit_id):
    """A circuit pump's settings in a Shelly record, or None (no such circuit or no pump).

    {"control": bool, "max_supply_c": degC, "run_on_max_minutes": whole minutes}; an absent field is its default.
    """
    control = pump_control(record, circuit_id)
    if control is None:
        return None
    pump = next(c for c in record_circuits(record) if c["id"] == circuit_id)["pump"]
    max_supply = pump.get("max_supply_c", MAX_SUPPLY_C[2])
    run_on_max = pump.get("run_on_max_s", RUN_ON_MAX_MINUTES[2] * 60)
    return {"control": control,
            "max_supply_c": max_supply if type(max_supply) is int else MAX_SUPPLY_C[2],
            "run_on_max_minutes": round(run_on_max / 60) if type(run_on_max) is int else RUN_ON_MAX_MINUTES[2]}


def with_pump_settings(record, circuit_id, settings):
    """The record to POST with a circuit pump's settings changed; None when it has no such circuit with a pump.

    Only what POST /config/shelly takes: schema, devices (without "password", so the E32 keeps each one) and
    circuits; every other field of a device or circuit goes back unchanged. A value at its default is left out, as
    the E32 stores it.
    """
    if type(record) is not dict or record.get("schema") != 1 or type(record.get("devices")) is not list:
        return None
    circuits = [dict(c) for c in record_circuits(record)]
    circuit = next((c for c in circuits if c["id"] == circuit_id), None)
    if circuit is None or type(circuit.get("pump")) is not dict:
        return None
    pump = dict(circuit["pump"])
    if "control" in settings:
        pump["control"] = bool(settings["control"])
    for key, field, scale, default in (("max_supply_c", "max_supply_c", 1, MAX_SUPPLY_C[2]),
                                       ("run_on_max_minutes", "run_on_max_s", 60, RUN_ON_MAX_MINUTES[2])):
        if key in settings:
            value = int(settings[key])
            if value == default:
                pump.pop(field, None)
            else:
                pump[field] = value * scale
    circuit["pump"] = pump
    devices = [{k: v for k, v in d.items() if k != "password"} for d in record["devices"] if type(d) is dict]
    return {"schema": 1, "devices": devices, "circuits": circuits}


def with_pump_control(record, circuit_id, control):
    """The record to POST with one circuit's pump control changed (with_pump_settings)."""
    return with_pump_settings(record, circuit_id, {"control": control})


def shelly_link(hass, entry):
    """The entry's one link; None without a stored controller connection."""
    state = hass.data[DOMAIN][entry.entry_id]
    link = state.get(KEY)
    if link is None:
        hub = heating_hub(hass, entry)
        if hub.plan is None:
            return None
        link = state[KEY] = ShellyLink(hub.plan)
    return link


# -- entities -----------------------------------------------------------------------------


class CircuitEntity(HubEntity):
    """One heating circuit, on the circuit's own device; available while the E32 reports it."""

    def __init__(self, hub, circuit_id, kind, key):
        self.circuit_id, self.kind = circuit_id, kind
        device = DeviceInfo(identifiers={circuit_device_identifier(hub.prefix, circuit_id)},
                            manufacturer="OpenThermostat", translation_key=f"circuit_{kind}")
        self._attach(hub, f"e32_circuit_{circuit_id}_{key}", device)
        self._attr_translation_key = f"circuit_{kind}_{key}"

    @property
    def circuit(self):
        return self.hub.circuits.get(self.circuit_id)

    @property
    def pump(self):
        return pump_of(self.circuit)

    @property
    def available(self):
        return self.hub.fresh and self.circuit is not None

    def _write_token(self):
        return self.hub.fresh, json.dumps(self.circuit, sort_keys=True)


class PumpEntity(CircuitEntity):
    @property
    def available(self):
        return super().available and self.pump is not None


class CircuitPumpBinarySensor(PumpEntity, BinarySensorEntity):
    """The pump runs: the Plug is on and the pump takes power (not "no power")."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, hub, circuit_id, kind):
        super().__init__(hub, circuit_id, kind, "pump")

    @property
    def is_on(self):
        pump = self.pump or {}
        if pump.get("state") not in ("on", "off"):
            return None
        return pump["state"] == "on" and (self.circuit or {}).get("fault") != "no_power"

    @property
    def extra_state_attributes(self):
        pump = self.pump or {}
        return {key: pump.get(key) for key in ("power_w", "wanted", "control", "acting", "manual") if key in pump}


class CircuitPumpReasonSensor(PumpEntity, SensorEntity):
    """Why the pump is on or off, in words (the state's translation)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(PUMP_REASONS)

    def __init__(self, hub, circuit_id, kind):
        super().__init__(hub, circuit_id, kind, "pump_reason")

    @property
    def native_value(self):
        reason = (self.pump or {}).get("reason")
        return reason if reason in PUMP_REASONS else None

    @property
    def extra_state_attributes(self):
        pump = self.pump or {}
        # wanted: what the E32's rule wants; acting: the E32 switches the pump now (else it only shows it); warm (E32
        # P9): running on because the water to the floor is still warmer than the water back, by delta_c.
        attributes = {key: pump.get(key) for key in ("wanted", "control", "acting", "warm") if key in pump}
        if pump.get("warm") is True and "delta_c" in (self.circuit or {}):
            attributes["delta_c"] = self.circuit["delta_c"]
        return attributes


class CircuitPumpPowerSensor(PumpEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, hub, circuit_id, kind):
        super().__init__(hub, circuit_id, kind, "pump_power")

    @property
    def native_value(self):
        value = (self.pump or {}).get("power_w")
        return value if type(value) in (int, float) else None


class CircuitTemperatureSensor(CircuitEntity, SensorEntity):
    """The circuit's supply or return (The Pill's probe), with its reading's health."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, hub, circuit_id, kind, key):
        super().__init__(hub, circuit_id, kind, key)
        self._probe = key

    @property
    def available(self):
        return super().available and f"{self._probe}_health" in self.circuit

    @property
    def native_value(self):
        value = (self.circuit or {}).get(f"{self._probe}_c")
        return value if type(value) in (int, float) else None

    @property
    def extra_state_attributes(self):
        return {"reading": (self.circuit or {}).get(f"{self._probe}_health")}


class CircuitDeltaSensor(CircuitEntity, SensorEntity):
    """Supply minus return: how much the water cools in the circuit (a difference, never converted to °F)."""

    _attr_native_unit_of_measurement = "°C"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:thermometer-lines"

    def __init__(self, hub, circuit_id, kind):
        super().__init__(hub, circuit_id, kind, "delta")

    @property
    def native_value(self):
        value = (self.circuit or {}).get("delta_c")
        return value if type(value) in (int, float) else None


class CircuitProblemSensor(CircuitEntity, SensorEntity):
    """The circuit's problem in words (the state's translation): "No problem" while all is well."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(PROBLEMS)
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hub, circuit_id, kind):
        super().__init__(hub, circuit_id, kind, "problem")

    @property
    def native_value(self):
        return problem(self.circuit) if self.circuit is not None else None


class CircuitPumpSelect(PumpEntity, SelectEntity):
    """The owner's pump override: the E32's own rule (Automatic), or on or off for an hour.

    The E32 goes back to Automatic by itself after the hour; frost and too-hot water always win.
    """

    _attr_options = list(PUMP_MODES)

    def __init__(self, hub, circuit_id, kind, link, clock=time.monotonic):
        super().__init__(hub, circuit_id, kind, "pump_mode")
        self.link, self._clock, self._pending = link, clock, None

    def _reported(self):
        manual = (self.pump or {}).get("manual")
        return manual if manual in ("on", "off") else "automatic"

    @property
    def current_option(self):
        reported = self._reported()
        if self._pending is not None:
            value, since = self._pending
            if reported == value or self._clock() - since > PENDING_SECONDS:
                self._pending = None
            else:
                return value
        return reported

    def _write_token(self):
        return None  # the pending choice changes with the clock

    async def async_select_option(self, option):
        await self.link.async_pump(self.circuit_id, option)
        self._pending = (option, self._clock())
        self.async_write_ha_state()


class ProbeSensor(HubEntity, SensorEntity):
    """One probe of The Pill that no circuit uses, named by its role, on the E32 device."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, hub, role):
        self.role = role
        self._attach(hub, f"e32_probe_{role}")
        self._attr_translation_key = f"probe_{role}"

    @property
    def probe(self):
        return (self.hub.probes or {}).get(self.role)

    @property
    def available(self):
        return self.hub.fresh and self.probe is not None

    @property
    def native_value(self):
        value = (self.probe or {}).get("t_c")
        return value if type(value) in (int, float) else None

    @property
    def extra_state_attributes(self):
        return {"reading": (self.probe or {}).get("health")}

    def _write_token(self):
        return self.hub.fresh, json.dumps(self.probe, sort_keys=True)


def zone_of(hub):
    """flow.zone of the E32 summary ({"demand", "path", "limited"}, E32 1.1 with circuits), checked, or None."""
    summary = getattr(hub, "summary", None)
    flow = summary.get("flow") if type(summary) is dict else None
    zone = flow.get("zone") if type(flow) is dict else None
    if type(zone) is not dict or zone.get("demand") not in ZONE_DEMANDS:
        return None
    return {"demand": zone["demand"], "path": zone.get("path") if type(zone.get("path")) is bool else None,
            "limited": zone.get("limited") if type(zone.get("limited")) is bool else None}


class HeatGoesToSensor(HubEntity, SensorEntity):
    """Where the boiler's heat goes now (the floor only, the radiators, both, nobody asks), on the E32 device."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(ZONE_DEMANDS)
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = ZONE_KEY

    def __init__(self, hub):
        self._attach(hub, f"e32_{ZONE_KEY}")

    @property
    def zone(self):
        return zone_of(self.hub) if self.hub.fresh else None

    @property
    def available(self):
        return self.hub.fresh and bool(self.hub.circuits)

    @property
    def native_value(self):
        return (self.zone or {}).get("demand")

    @property
    def extra_state_attributes(self):
        zone = self.zone or {}
        return {"path": zone.get("path"), "limited": zone.get("limited")}

    def _write_token(self):
        return self.hub.fresh, json.dumps(self.zone, sort_keys=True)


SENSORS = {"pump_reason": CircuitPumpReasonSensor, "pump_power": CircuitPumpPowerSensor,
           "delta": CircuitDeltaSensor, "problem": CircuitProblemSensor}


def _circuits(hub):
    for circuit_id, circuit in hub.circuits.items():
        yield circuit_id, circuit["kind"], circuit_keys(circuit)


def wanted_sensors(hub):
    for circuit_id, kind, keys in _circuits(hub):
        for key in keys:
            if key in SENSORS:
                yield ("circuit", circuit_id, kind, key), lambda c=circuit_id, k=kind, cls=SENSORS[key]: cls(hub, c, k)
            elif key in ("supply", "return"):
                yield ("circuit", circuit_id, kind, key), lambda c=circuit_id, k=kind, key=key: (
                    CircuitTemperatureSensor(hub, c, k, key))
    for role in hub.probes or {}:
        yield ("probe", role), lambda role=role: ProbeSensor(hub, role)
    if hub.circuits:  # the zone exists only with circuits; one sensor for the house
        yield ("zone",), lambda: HeatGoesToSensor(hub)


def wanted_binary_sensors(hub):
    for circuit_id, kind, keys in _circuits(hub):
        if "pump" in keys:
            yield ("circuit", circuit_id, kind, "pump"), lambda c=circuit_id, k=kind: CircuitPumpBinarySensor(hub, c, k)


def wanted_selects(link):
    def wanted(hub):
        for circuit_id, kind, keys in _circuits(hub):
            if "pump_mode" in keys:
                yield ("circuit", circuit_id, kind, "pump_mode"), lambda c=circuit_id, k=kind: (
                    CircuitPumpSelect(hub, c, k, link))
    return wanted


# -- Repairs and entities that are gone --------------------------------------------------------------


@callback
def sync_issues(hass, entry, hub, raised):
    """Raise and clear the circuit and probe Repairs of the current telemetry; raised: the ids this entry raised."""
    if not hub.fresh:
        return  # an offline E32 says nothing about its circuits; "E32 offline" is its own problem
    lang, wanted = language(hass), {}
    for circuit_id, circuit in hub.circuits.items():
        name = CIRCUIT_NAMES[lang].get(circuit["kind"], circuit_id)
        found = problem(circuit)
        key = TOO_HOT_ISSUE if found == "too_hot" else FAULT_ISSUES.get(found)
        if key is not None:
            severity = ir.IssueSeverity.ERROR if key == TOO_HOT_ISSUE else ir.IssueSeverity.WARNING
            wanted[f"{key}_{entry.entry_id}_{circuit_id}"] = (key, severity, {"circuit": name})
    silent = [PROBE_NAMES[lang][role] for role, probe in (hub.probes or {}).items()
              if probe.get("health") in ("no_reading", "missing")]
    if silent:
        wanted[f"{PROBE_ISSUE}_{entry.entry_id}"] = (PROBE_ISSUE, ir.IssueSeverity.WARNING, {"probes": ", ".join(silent)})
    for issue in [i for i in raised if i not in wanted]:
        ir.async_delete_issue(hass, DOMAIN, issue)
        raised.discard(issue)
    for issue, (key, severity, placeholders) in wanted.items():
        ir.async_create_issue(hass, DOMAIN, issue, is_fixable=False, is_persistent=False, severity=severity,
                              translation_key=key, translation_placeholders=placeholders)
        raised.add(issue)


def _split(rest):
    """(circuit id, key) of the part after <prefix>_e32_circuit_, or None."""
    for key in sorted(CIRCUIT_KEYS, key=len, reverse=True):
        if rest.endswith("_" + key) and CIRCUIT_ID.fullmatch(rest[:-len(key) - 1]):
            return rest[:-len(key) - 1], key
    return None


@callback
def remove_stale_entities(hass, entry, hub, now=None, fresh_since=None):
    """Remove the entities of circuits and probes the E32 no longer has, and a circuit's device with them.

    Only while the E32 reports. A circuit goes once the plan does not list it and its document is gone (the
    E32 clears it, or it expired): a plan sent during the E32's start-up never removes one. A circuit that is
    still there loses the entities it no longer asks for (its pump or a probe taken out). A probe goes once a
    fw/state/probes message in this run leaves it out, or none came for PROBES_GONE_SECONDS while the E32
    reported (its retained topic was cleared while Home Assistant was away).
    """
    if not hub.fresh or hub.config is None:
        return
    listed = set(plan_circuits(hub.config))
    circuits = hub.circuits
    now = hub.clock() if now is None else now
    if hub.probes_received is not None and not hub.probes_expired:
        roles = set(hub.probes or {})
    elif fresh_since is not None and now - fresh_since >= PROBES_GONE_SECONDS and (
            hub.probes_received is None or now - hub.probes_received >= PROBES_GONE_SECONDS):
        roles = set()
    else:
        roles = None  # not known yet: every probe entity stays
    registry, devices = er.async_get(hass), dr.async_get(hass)
    head, probe_head = f"{hub.prefix}_e32_circuit_", f"{hub.prefix}_e32_probe_"
    gone = set()
    for record in list(er.async_entries_for_config_entry(registry, entry.entry_id)):
        uid = record.unique_id or ""
        if record.platform != DOMAIN:
            continue
        if uid == f"{hub.prefix}_e32_{ZONE_KEY}":
            if not circuits and not listed and not hub.circuit_states:  # the last circuit is really gone
                registry.async_remove(record.entity_id)
            continue
        if uid.startswith(head) and (found := _split(uid[len(head):])) is not None:
            circuit_id, key = found
            if circuit_id in circuits:
                if key not in circuit_keys(circuits[circuit_id]):
                    registry.async_remove(record.entity_id)
            elif circuit_id not in listed and circuit_id not in hub.circuit_states:
                registry.async_remove(record.entity_id)
                gone.add(circuit_id)
        elif uid.startswith(probe_head) and roles is not None and uid[len(probe_head):] in PROBE_ROLES:
            if uid[len(probe_head):] not in roles:
                registry.async_remove(record.entity_id)
    for circuit_id in gone:
        device = devices.async_get_device_by_identifier(circuit_device_identifier(hub.prefix, circuit_id), entry.entry_id)
        if device is not None and device.config_entry_id == entry.entry_id and not er.async_entries_for_device(
                registry, device.id, include_disabled_entities=True):
            devices.async_remove_device(device.id)


def watch(hass, entry):
    """Once per entry: keep the Repairs and the entities in step with the telemetry."""
    state = hass.data[DOMAIN][entry.entry_id]
    if state.get(KEY + "_watch"):
        return
    state[KEY + "_watch"] = True
    hub = heating_hub(hass, entry)
    raised = set()
    fresh_since = None

    @callback
    def changed():
        nonlocal fresh_since
        if not hub.fresh:
            fresh_since = None
        elif fresh_since is None:
            fresh_since = hub.clock()
        sync_issues(hass, entry, hub, raised)
        remove_stale_entities(hass, entry, hub, fresh_since=fresh_since)

    entry.async_on_unload(hub.add_listener(changed))

    @callback
    def unload():
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


async def async_setup_selects(hass, entry, async_add_entities):
    if not _product(entry):
        return
    link = shelly_link(hass, entry)
    if link is None:
        return  # no stored controller connection: the override cannot be sent
    hub = heating_hub(hass, entry)
    entry.async_on_unload(track_entities(hub, async_add_entities, add_options(hass, entry), wanted_selects(link)))


# -- Configure → Heating and boiler → Heating circuits ------------------------------------------------


def circuits_offered(hass, entry):
    """Configure offers the heating circuits once the E32 reports one with a pump (and its connection is stored)."""
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}
    hub = state.get("heating_hub")
    return (hub is not None and hub.plan is not None
            and any(pump_of(c) is not None for c in hub.circuits.values()))


def pump_changes(current, control, max_supply_c, run_on_max_minutes):
    """(changes, errors, wanted) of a circuit pump's settings as asked (Configure's form and the settings panel, 1.4).

    ``current``: pump_settings(); the two numbers whole (a whole float counts) within their limits, else the error
    whole_number_invalid on that field; ``control`` a bool, else heating_circuit_failed on the whole form. ``changes``
    holds only what differs from ``current``.
    """
    wanted, errors = {"control": control}, {}
    for key, value, (low, high, _) in (("max_supply_c", max_supply_c, MAX_SUPPLY_C),
                                       ("run_on_max_minutes", run_on_max_minutes, RUN_ON_MAX_MINUTES)):
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        if type(value) is not int or not low <= value <= high:
            errors[key] = "whole_number_invalid"
        wanted[key] = value
    if type(control) is not bool:
        errors["base"] = "heating_circuit_failed"
    changes = {} if errors else {key: value for key, value in wanted.items() if value != current[key]}
    return changes, errors, wanted


class CircuitOptionsSteps:
    """The options flow's heating circuits: per circuit with a pump, "Pump control by the E32", the highest water
    temperature to the floor and the run-on while the water is warm (at most, in minutes)."""

    async def async_step_heating_circuits(self, user_input=None):
        """Read the Shelly record; one circuit with a pump opens its form, two ask which first."""
        link = shelly_link(self.hass, self.config_entry)
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        try:
            record = await link.async_record()
        except HomeAssistantError as err:
            return self._e32_abort_failure(err)
        lang = language(self.hass)
        pumps = [c for c in record_circuits(record) if pump_control(record, c["id"]) is not None]
        if not pumps:
            return self.async_abort(reason="heating_circuits_none")
        self._circuit_record = record
        if user_input is not None and user_input.get("circuit") in {c["id"] for c in pumps}:
            self._circuit_id = user_input["circuit"]
            return await self.async_step_heating_circuit()
        if len(pumps) == 1:
            self._circuit_id = pumps[0]["id"]
            return await self.async_step_heating_circuit()
        options = [{"value": c["id"], "label": CIRCUIT_NAMES[lang].get(c.get("kind"), c["id"])} for c in pumps]
        return self.async_show_form(step_id="heating_circuits", data_schema=vol.Schema({
            vol.Required("circuit", default=pumps[0]["id"]): selector.SelectSelector({"options": options})}))

    async def async_step_heating_circuit(self, user_input=None):
        """One circuit's pump: "Pump control by the E32" (on: the E32 switches the pump while it controls the boiler),
        the highest water temperature to the floor and the run-on while the water is warm, in one save."""
        record, circuit_id = getattr(self, "_circuit_record", None), getattr(self, "_circuit_id", None)
        current = pump_settings(record, circuit_id) if record is not None else None
        if current is None:
            return self.async_abort(reason="heating_circuits_none")
        circuit = next(c for c in record_circuits(record) if c["id"] == circuit_id)
        placeholders = {"circuit": CIRCUIT_NAMES[language(self.hass)].get(circuit.get("kind"), circuit_id), "error": ""}
        errors = {}
        shown = dict(current)
        if user_input is not None:
            changes, errors, wanted = pump_changes(current, user_input.get("pump_control"),  # 1.4: shared with the panel
                                                   user_input.get("max_supply_c", current["max_supply_c"]),
                                                   user_input.get("run_on_max_minutes", current["run_on_max_minutes"]))
            if not errors:
                if not changes:
                    return self.async_abort(reason="e32_room_unchanged")
                try:
                    await shelly_link(self.hass, self.config_entry).async_pump_settings(circuit_id, changes)
                except HomeAssistantError as err:
                    errors["base"] = "heating_circuit_failed"
                    placeholders["error"] = (getattr(err, "translation_placeholders", None) or {}).get("error") or \
                        getattr(err, "translation_key", None) or "unknown"
                else:
                    return self.async_abort(reason="heating_circuit_saved")
            shown.update({key: value for key, value in wanted.items() if key not in errors and value is not None})

        def number(low, high, unit):
            return selector.NumberSelector({"min": low, "max": high, "step": 1, "mode": "box", "unit_of_measurement": unit})
        schema = vol.Schema({
            vol.Required("pump_control", default=shown["control"]): selector.BooleanSelector(),
            vol.Required("max_supply_c", default=shown["max_supply_c"]): number(MAX_SUPPLY_C[0], MAX_SUPPLY_C[1], "°C"),
            vol.Required("run_on_max_minutes", default=shown["run_on_max_minutes"]): number(
                RUN_ON_MAX_MINUTES[0], RUN_ON_MAX_MINUTES[1], "min"),
        })
        return self.async_show_form(step_id="heating_circuit", data_schema=schema, errors=errors,
                                    description_placeholders=placeholders)
