"""The E32's flow temperature options and what they do (E32 beta.19, ``src/control/FlowPolicy.h``).

Controls on the product device (configuration), read and written over the
stored controller connection (``GET/POST /config/heating/flow``, one field per
change), the same login and lock as the room plan:

- switch "Follow outdoor temperature (heating curve)" (``weather_curve``; on by
  default since E32 rc.3): the flow follows the outdoor temperature, the room
  correction on top; a standard curve until the E32 learned the house's own,
  the room control alone without a fresh outdoor temperature;
- switch "Smart warm-up" (``apply_learned``; on by default since E32 rc.3: a
  time in the week program means "warm at that time"): it starts early enough
  for the next program step, with the lowest flow that is still in time; off,
  heating starts at the program time and the E32 only advises. The entity keeps
  its unique ID (and entity ID) of "Use learned flow and optimum start": the
  meaning is the same, only the name and the default changed;
- number "Flow at −10 °C" (``curve_design_flow_c``): 0 is automatic (floor
  heating 40 °C, radiators 55 °C), else 25–80 °C;
- select "Comfort style" (``comfort_style``: ``comfort``, ``balanced`` or ``save``; 1.1.1 stage B, the owner's
  decision D2): comfort first, balanced (the default) or save most, what the E32's heating plan weighs (comfort
  against burner starts and gas). Only for firmware that reports it. The plan mode is no flow option: it has its
  own route, written only by the owner's one confirmation (heating_plan.py).

The options are static: they are read when the E32 is (back) online and come
back with every write. Since 1.1.1 (P1 HA-1) Home Assistant no longer signs in
every five minutes to look whether they changed: the E32's flow telemetry
(``fw/telemetry/flow``, ``flow.settings``) carries them, so a change made on the
E32's own page is read once when the telemetry shows it. Only firmware whose
telemetry lacks them is still read periodically, once an hour (FALLBACK_REFRESH).
A Configure form reads them when it opens. The controls appear once the E32
answered (firmware without the options never shows them).

Sensors from the E32 summary (``fw/telemetry/summary`` with ``flow`` and
``night_gas`` from ``fw/telemetry/flow``, assembled by the HeatingHub), each
only once the E32 reports its part:

- "Flow source": what sets the flow now (room control, heating curve, learned
  flow, optimum start), with yesterday's comparison in the attributes;
- "Heating curve flow" and "Learned flow" (diagnostic): what each would ask
  for now, in use or as advice (1.4.6: "Learned water temperature" is never Unknown: while the E32 reports none it
  keeps the last value it reported, kept over a restart, with ``last_reported`` and a sentence, and before there has
  been one it says "Not learned yet" in words); "Room control flow" and "Heating curve slope"
  (diagnostic, disabled by default);
- "Gas calibration" (diagnostic): no meter / calibrating / calibrated (with its
  confidence) / meter not reporting, and "Boiler power at full burner"
  (diagnostic, disabled by default);
- "Last night's heating gas" (diagnostic): the measured heating gas of the
  last night next to the model's prediction; only once a night was measured
  with a gas meter (without one there is nothing to show).

The boiler request itself (the flow in use) stays the existing "Boiler
request (E32)" sensor.

"Water temperature by weather compensation" also carries what the heating-curve
card (frontend/heating-curve-card.js, E32 rc.5) draws, all in °C whatever the
unit system: the standard slope from the water temperature in hard frost the E32
publishes (``curve.design_flow_c``; worked out as FlowPolicy does for firmware
before rc.5), the room temperature the curve starts from, the outdoor
temperature the E32 uses now, the water temperature limits (the plan's, the
highest also within the boiler's own maximum, as FlowPolicy's cap), the line's
own value now (``curve.base_c``) and what weather compensation asks with the
room correction (``curve.flow_c``), next to the curve's slope and where it comes
from (standard, learned, or worked out from the house) and the steady periods
it learned from so far (``curve.windows``).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import logging
import time

from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory, UnitOfPower, UnitOfTemperature, UnitOfVolume
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .heating_link import HubEntity, add_options, heating_hub, number, track_entities

_LOGGER = logging.getLogger(__name__)

KEY = "e32_flow"
REFRESH = timedelta(minutes=5)  # the check whether a periodic read is due (no sign-in by itself)
# Only for firmware whose flow telemetry does not carry the options (1.1.1, P1 HA-1: was every 5 minutes).
FALLBACK_REFRESH = timedelta(hours=1)
OPTIONS = ("weather_curve", "apply_learned")
DESIGN_FLOW_KEY = "curve_design_flow_c"
DESIGN_FLOW_AUTOMATIC = "automatic"  # the select option for the stored 0
DESIGN_FLOW_LIMITS = (25, 80)  # the E32's own bound (WeatherCurve::min/maxDesignFlowC); 0 is automatic
# 1.1.1 stage B (SL-B3 item 5, FlowSettings "comfort_style"): an optional key, kept only when the firmware sends a
# value it knows (comfort first, balanced, save most).
COMFORT_STYLE_KEY = "comfort_style"
COMFORT_STYLES = ("comfort", "balanced", "save")
COMFORT_STYLE_DEFAULT = "balanced"
OPTIONAL = {COMFORT_STYLE_KEY: COMFORT_STYLES}
SOURCES = ["rule", "curve", "learned", "optimum_start", "plan"]  # "plan": the E32's heating plan (1.1.1 stage B)
GAS_STATUSES = ["no_meter", "collecting", "calibrated", "meter_stale"]
# The Learning view's cards (E32 rc.5), the sixth card module (week_planner.card_modules), versioned with the
# manifest like the other card URLs: "Water temperature by outdoor temperature" and what the E32 knows (a ring).
CURVE_CARD_URL = "/open_thermostat/heating-curve-card-1.4.6.js"
CURVE_CARD_TYPE = "custom:openthermostat-heating-curve"
KNOWLEDGE_CARD_TYPE = "custom:openthermostat-knowledge"
# 1.4.3 (LEARN-TAB, CONTRACT-1.4.3 §3): what the E32 learned from the boiler, as tiles (the same module as the curve).
BOILER_LEARNED_CARD_TYPE = "custom:openthermostat-boiler-learned"
# 1.4.3: the Learning view's card per room (frontend/learning-room-card.js), its own module, versioned like the others.
LEARNING_ROOM_CARD_URL = "/open_thermostat/learning-room-card-1.4.6.js"
LEARNING_ROOM_CARD_TYPE = "custom:openthermostat-learning-room"
# WeatherCurve (src/control/WeatherCurve.h): the standard slope follows the water temperature in hard frost
# (−10 °C outside) for a 20 °C room; automatic is floor heating 40 °C, radiators 55 °C; the slope's limits.
DESIGN_ROOM_C, DESIGN_OUTDOOR_C = 20, -10
DESIGN_FLOW_BY_EMITTER = {"floor": 40, "radiator": 55}
SLOPE_LIMITS = (0.2, 2.5)
FLOW_CEILING_C = 80  # FlowDemand::ceilingC: the highest water temperature the E32 ever asks
# What only the card reads; it changes with the weather: shown, not kept in the history. base_c and flow_c are the
# curve's values in °C (the sensor's state is converted on an imperial system; the card draws in °C).
CURVE_CHART_KEYS = ("design_flow_c", "standard_slope", "room_c", "outdoor_c", "minimum_flow_c", "maximum_flow_c",
                    "base_c", "flow_c")


def decode_settings(value):
    """The options as the E32 stored them, or None when the answer is not well-formed.

    Since 1.0 the answer also has the "Comfort and boiler care" knobs ("tuning", the values
    in effect) and since rc.2 which automatic knobs the owner set ("tuning_manual"); both
    are kept only when well-formed (e32_care.decode_tuning). The options above never
    depend on them.
    """
    if type(value) is not dict:
        return None
    design = value.get(DESIGN_FLOW_KEY)
    if (any(type(value.get(key)) is not bool for key in OPTIONS) or type(design) is not int
            or design != 0 and not DESIGN_FLOW_LIMITS[0] <= design <= DESIGN_FLOW_LIMITS[1]):
        return None
    from .e32_care import decode_tuning
    optional = {key: value[key] for key, known in OPTIONAL.items() if value.get(key) in known}
    return {**{key: value[key] for key in OPTIONS}, DESIGN_FLOW_KEY: design, **optional, **decode_tuning(value)}


def flow_error(err):
    """A clear Home Assistant error for a refused or failed write."""
    from .controller_link import ControllerLoginRejected, HeatingPlanRejected
    if isinstance(err, ControllerLoginRejected):
        return HomeAssistantError(translation_domain=DOMAIN, translation_key="room_plan_password")
    if str(err) == "controller_no_free_session":
        return HomeAssistantError(translation_domain=DOMAIN, translation_key="e32_no_free_session")
    if isinstance(err, HeatingPlanRejected):
        if err.error == "save_unconfirmed":
            return HomeAssistantError(translation_domain=DOMAIN, translation_key="flow_settings_unconfirmed")
        return ServiceValidationError(translation_domain=DOMAIN, translation_key="flow_settings_rejected",
                                      translation_placeholders={"error": err.error})
    from .room_plan import link_error
    return link_error(str(err)) or HomeAssistantError(translation_domain=DOMAIN,
                                                      translation_key="flow_settings_unreachable",
                                                      translation_placeholders={"error": str(err)})


class FlowSettingsLink:
    """The E32's flow options as last read or written; listeners hear every change.

    Has ``add_listener`` and ``_trackers`` like the HeatingHub, so
    ``track_entities`` adds the controls once the options are known.
    """

    def __init__(self, hass, hub, plan):
        self.hass, self.hub, self.plan = hass, hub, plan
        self.settings = None
        self.unsupported = False  # firmware without the options: not asked again until the E32 is back
        self._task = None
        self._was_fresh = False
        self._read_at = None      # monotonic time of the last read (a sign-in)
        self._seen = None         # the options as the telemetry last showed them
        self._listeners = []
        self._trackers = []

    @property
    def available(self):
        return self.hub.fresh and self.settings is not None

    @property
    def closed(self):
        """The entry is unloading (HeatingHub.close): track_entities adds no control from now on."""
        return getattr(self.hub, "closed", False)

    @callback
    def add_listener(self, listener):
        self._listeners.append(listener)

        @callback
        def remove():
            if listener in self._listeners:
                self._listeners.remove(listener)
        return remove

    @callback
    def notify(self):
        for listener in list(self._listeners):
            listener()

    def telemetry_options(self):
        """The options as the E32's flow telemetry shows them ({weather_curve, apply_learned, design}), or None."""
        summary = getattr(self.hub, "summary", None)
        flow = summary.get("flow") if type(summary) is dict else None
        settings = flow.get("settings") if type(flow) is dict else None
        if type(settings) is not dict:
            return None
        values = {key: settings.get(key) for key in (*OPTIONS, DESIGN_FLOW_KEY)}
        if any(type(values[key]) is not bool for key in OPTIONS) or type(values[DESIGN_FLOW_KEY]) not in (int, float):
            return None
        optional = {key: settings[key] for key, known in OPTIONAL.items() if settings.get(key) in known}
        return {**values, DESIGN_FLOW_KEY: int(values[DESIGN_FLOW_KEY]), **optional}

    @callback
    def poll(self, _now=None):
        """The periodic check: a read only for firmware without the options in its telemetry, once an hour."""
        if self.telemetry_options() is not None and self.settings is not None:
            return  # the telemetry tells a change (hub_changed); no sign-in needed
        loop = self.hass.loop.time()
        if self._read_at is not None and loop - self._read_at < FALLBACK_REFRESH.total_seconds():
            return
        self.read()

    @callback
    def read(self):
        """Read the options once (one sign-in) while the E32 is online; never with a refused password."""
        if (not self.hub.fresh or self.unsupported or self.plan.login_rejected
                or (self._task is not None and not self._task.done())):
            return
        self._read_at = self.hass.loop.time()
        self._task = self.hass.async_create_task(self.async_refresh(), "OpenThermostat E32 flow options read")

    @callback
    def hub_changed(self):
        """The E32 is (back) online, perhaps after a firmware update, or its telemetry shows other options: read."""
        fresh = self.hub.fresh
        if fresh and not self._was_fresh:
            self.unsupported = False
            self.read()
        self._was_fresh = fresh
        seen = self.telemetry_options() if fresh else None
        if seen is not None and seen != self._seen:
            known = self.settings is not None and all(self.settings.get(k) == v for k, v in seen.items())
            self._seen = seen
            if not known:
                self.read()  # changed on the E32's own page (or not read yet): one read brings the rest along

    @callback
    def abilities_read(self, _version=None):
        """HA-REREAD (1.4.2): the E32 restarted (perhaps on other firmware) and the room-plan link read its abilities
        again: read the options again too, so what the panel and Configure show (settings_heating._flow_settings
        serves ``settings``) is the new firmware's, and firmware that now has the options is asked again."""
        self.unsupported = False
        self.read()

    async def _call(self, change=None):
        # A change waits for a free E32 web session; a read does not.
        return await self.plan.async_call(lambda client: client.async_flow_settings(change), write=change is not None)

    async def async_read_now(self):
        """Read the options for a Configure form: what the E32 stored, or a clear HomeAssistantError."""
        from .controller_link import ControllerLinkError
        try:
            value = decode_settings(await self._call())
        except ControllerLinkError as err:
            raise flow_error(err) from None
        if value is None:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="flow_settings_unconfirmed")
        self._set(value)
        return value

    async def async_refresh(self):
        from .controller_link import ControllerLinkError
        try:
            value = decode_settings(await self._call())
        except ControllerLinkError as err:
            self.unsupported = str(err) == "controller_update_required"
            _LOGGER.debug("E32 flow options read failed: %s", err)
            return
        if value is not None:
            self._set(value)

    async def async_change(self, change):
        """POST one change; the E32 answers with what it stored (that is the read-back)."""
        from .controller_link import ControllerLinkError
        if self.settings is None:
            from .room_plan import link_error
            raise link_error("not_read")  # the E32 did not answer when its settings were read
        try:
            answer = await self._call(change)
        except ControllerLinkError as err:
            raise flow_error(err) from None
        value = decode_settings(answer)
        if value is None:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="flow_settings_unconfirmed")
        self._set(value)
        return value

    @callback
    def _set(self, value):
        if value != self.settings:
            self.settings = value
            self.notify()

    @callback
    def stop(self):
        if self._task is not None and not self._task.done():
            self._task.cancel()
        self._listeners.clear()


def flow_link(hass, entry):
    """The entry's one link, started by whichever platform asks first; None without a stored connection."""
    state = hass.data[DOMAIN][entry.entry_id]
    link = state.get(KEY)
    if link is None:
        hub = heating_hub(hass, entry)
        if hub.plan is None:
            return None  # no stored controller connection: nothing can be read or written
        link = state[KEY] = FlowSettingsLink(hass, hub, hub.plan)
        entry.async_on_unload(link.stop)
        entry.async_on_unload(hub.add_listener(link.hub_changed))
        entry.async_on_unload(hub.add_firmware_listener(link.abilities_read))
        entry.async_on_unload(async_track_time_interval(hass, link.poll, REFRESH))
        link.add_listener(lambda: remove_stale_controls(hass, entry, link))
        link.hub_changed()
    return link


def smart_warm_up(hass, entry_id):
    """Smart warm-up (``apply_learned``) as last read from the E32, or None while unknown."""
    data = getattr(hass, "data", None)
    link = data.get(DOMAIN, {}).get(entry_id, {}).get(KEY) if isinstance(data, dict) else None
    value = (link.settings or {}).get("apply_learned") if link is not None else None
    return value if type(value) is bool else None



# -- shared by Configure and the settings panel (1.4): one check and one write for both ----------------------------
# Configure's forms (e32_room_flow.async_step_e32_flow_limits, options_house_heating.async_step_heating_flow) and the
# panel's section Heating and boiler (settings_heating.py) call these, so the two never judge a value differently.

DESIGN_CHOICES = (DESIGN_FLOW_AUTOMATIC, *(str(c) for c in range(DESIGN_FLOW_LIMITS[0], DESIGN_FLOW_LIMITS[1] + 1)))


def temperature_unit(hass):
    """The Home Assistant temperature unit (°C or °F) the limits are shown in; the E32 plan itself is always °C."""
    from .e32_room_flow import CELSIUS, FAHRENHEIT
    unit = getattr(getattr(getattr(hass, "config", None), "units", None), "temperature_unit", CELSIUS)
    return FAHRENHEIT if unit == FAHRENHEIT else CELSIUS


def limit_edits(plan, automatic, low, high, unit="°C"):
    """The water temperature limits as asked, checked as the E32 checks them: (edits, lowest °C, highest °C).

    ``plan`` is the room plan the form showed; ``automatic`` the tick "Lowest water temperature: automatic" (only on
    an E32 that has the choice, plan item 1); ``low`` and ``high`` in the user's unit (the lowest is not used while
    automatic). ``edits`` holds only what differs from the plan (plan item 1b), so a limit changed on the E32's own
    page meanwhile stays. Raises FlowError e32_flow_limits_invalid (whole degrees within the E32's ranges) or
    e32_flow_limits_order (the lowest below the highest).
    """
    from .e32_room_flow import (FLOW_LIMIT_FIELDS, FLOW_MAXIMUM_C, FLOW_MINIMUM_C, MINIMUM_AUTOMATIC_KEY,
                                STANDARD_MINIMUM_FLOW_C, FlowError, flow_celsius)
    tick = type(plan.get(MINIMUM_AUTOMATIC_KEY)) is bool
    automatic = tick and automatic is True
    try:
        low_c, high_c = (flow_celsius(float(value), unit) for value in (low, high))
    except (TypeError, ValueError):
        low_c = high_c = None
    if automatic and (low_c is None or not FLOW_MINIMUM_C[0] <= low_c <= FLOW_MINIMUM_C[1]):
        low_c = STANDARD_MINIMUM_FLOW_C  # not used while automatic: whatever the field holds
    shown = {key: plan.get(key) for key in (*FLOW_LIMIT_FIELDS.values(), *((MINIMUM_AUTOMATIC_KEY,) if tick else ()))}
    wanted = {MINIMUM_AUTOMATIC_KEY: automatic} if tick else {}
    if not automatic:
        wanted["minimum_flow_c"] = low_c
    wanted["maximum_flow_c"] = high_c
    if low_c is None or high_c is None or not (FLOW_MINIMUM_C[0] <= low_c <= FLOW_MINIMUM_C[1]
                                               and FLOW_MAXIMUM_C[0] <= high_c <= FLOW_MAXIMUM_C[1]):
        raise FlowError("e32_flow_limits_invalid")
    if (STANDARD_MINIMUM_FLOW_C if automatic else low_c) >= high_c:
        raise FlowError("e32_flow_limits_order")
    return {key: value for key, value in wanted.items() if shown.get(key) != value}, low_c, high_c


def limit_warnings(plan, high_c, boiler_c):
    """{field: error key} of a highest water temperature worth a second thought (a warning, not a block: the boiler
    caps anyway): above 50 °C while a room has floor heating, or above the boiler's own maximum."""
    from .e32_room_flow import FLOOR_FLOW_WARNING_C
    warnings = {}
    if high_c > FLOOR_FLOW_WARNING_C and any(type(room) is dict and room.get("emitter") == "floor"
                                             for room in plan.get("rooms", [])):
        warnings["maximum_flow_temperature"] = "e32_flow_limits_floor_warning"
    if boiler_c is not None and high_c > boiler_c:
        warnings["base"] = "e32_flow_limits_above_boiler"
    return warnings


async def async_save_limits(link, edits):
    """Write only ``edits`` on top of the plan the E32 holds now (RoomPlanLink.async_change_plan: its revision, one
    re-read on a concurrent save); the stored plan, or the link's HomeAssistantError. Automatic: the E32 sets the
    lowest water temperature to its standard itself."""
    from copy import deepcopy

    def change(stored):
        candidate = deepcopy(stored)
        candidate.update(edits)
        return candidate

    def confirm(stored):
        return all(stored.get(key) == value for key, value in edits.items())
    return await link.async_change_plan(change, confirm)


def option_changes(stored, shown, wanted):
    """The flow options to send: each value of ``wanted`` (apply_learned, weather_curve, curve_design_flow_c, and
    comfort_style on firmware that has it) that the user changed against what the form showed (``shown``) and that
    the E32 does not have already (plan item 1b: Home Assistant never puts its copy back over an E32 edit).

    The changes keep the order of ``wanted`` (they are sent one at a time). Raises ValueError("e32_flow_options_failed")
    for a value the E32 would refuse or a key it does not have.
    """
    changes = {}
    for key, value in wanted.items():
        if key not in (*OPTIONS, DESIGN_FLOW_KEY, COMFORT_STYLE_KEY):
            raise ValueError("e32_flow_options_failed")
        if key == COMFORT_STYLE_KEY and stored.get(key) not in COMFORT_STYLES:
            continue  # firmware without the comfort style: nothing to send
        if (key in OPTIONS and type(value) is not bool or key == COMFORT_STYLE_KEY and value not in COMFORT_STYLES
                or key == DESIGN_FLOW_KEY and (type(value) is not int or value != 0
                                               and not DESIGN_FLOW_LIMITS[0] <= value <= DESIGN_FLOW_LIMITS[1])):
            raise ValueError("e32_flow_options_failed")
        if value != shown.get(key, stored.get(key)) and value != stored.get(key):
            changes[key] = value
    return changes


async def async_save_options(link, changes):
    """Send ``changes`` one field at a time, as the E32 device's controls do; None once the E32 stored each as asked,
    else the form's error key e32_flow_options_failed."""
    for key, value in changes.items():
        try:
            stored = await link.async_change({key: value})
        except HomeAssistantError:
            return "e32_flow_options_failed"
        if stored.get(key) != value:
            return "e32_flow_options_failed"
    return None


# -- the controls ----------------------------------------------------------------------


class FlowOptionEntity(HubEntity):
    """One option on the product device; available while the E32 is online and its options are known."""

    _attr_entity_category = EntityCategory.CONFIG

    def _attach_link(self, link, key):
        self.link, self.key = link, key
        self._attach(link.hub, f"flow_{key}")
        self._attr_translation_key = f"flow_{key}"

    @property
    def available(self):
        return self.link.available

    @property
    def stored(self):
        return (self.link.settings or {}).get(self.key)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(self.link.add_listener(self._hub_changed))

    async def _change(self, value):
        await self.link.async_change({self.key: value})
        self.async_write_ha_state()


class FlowOptionSwitch(FlowOptionEntity, SwitchEntity):
    def __init__(self, link, key):
        self._attach_link(link, key)

    @property
    def is_on(self):
        return self.stored if type(self.stored) is bool else None

    async def async_turn_on(self, **kwargs):
        await self._change(True)

    async def async_turn_off(self, **kwargs):
        await self._change(False)


class FlowDesignSelect(FlowOptionEntity, SelectEntity):
    """The heating curve's flow at −10 °C outside: "automatic" (by heating type) or 25–80 °C.

    The E32 stores 0 for automatic (/config/heating/flow curve_design_flow_c); a choice list
    never shows that 0 as a temperature, and it is never converted to °F.
    """

    _attr_options = [DESIGN_FLOW_AUTOMATIC, *(str(c) for c in range(DESIGN_FLOW_LIMITS[0], DESIGN_FLOW_LIMITS[1] + 1))]

    def __init__(self, link):
        self._attach_link(link, DESIGN_FLOW_KEY)  # unique id <prefix>_flow_curve_design_flow_c (select)

    @property
    def current_option(self):
        if type(self.stored) is not int:
            return None
        return DESIGN_FLOW_AUTOMATIC if self.stored == 0 else str(self.stored)

    async def async_select_option(self, option):
        if option not in self._attr_options:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="flow_design_invalid",
                translation_placeholders={"minimum": str(DESIGN_FLOW_LIMITS[0]), "maximum": str(DESIGN_FLOW_LIMITS[1])})
        await self._change(0 if option == DESIGN_FLOW_AUTOMATIC else int(option))


class FlowComfortSelect(FlowOptionEntity, SelectEntity):
    """The comfort style of the E32's heating plan (comfort first / balanced / save most; default balanced)."""

    _attr_options = list(COMFORT_STYLES)
    _attr_icon = "mdi:tune-variant"

    def __init__(self, link):
        self._attach_link(link, COMFORT_STYLE_KEY)  # unique id <prefix>_flow_comfort_style (select)

    @property
    def current_option(self):
        return self.stored if self.stored in COMFORT_STYLES else None

    async def async_select_option(self, option):
        if option not in COMFORT_STYLES:
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="comfort_style_invalid")
        await self._change(option)


@callback
def remove_stale_controls(hass, entry, link):
    """Firmware whose options lack the comfort style (older, or a downgrade): its select goes."""
    if link.settings is None or COMFORT_STYLE_KEY in link.settings or not link.hub.fresh:
        return
    from homeassistant.helpers import entity_registry as er
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id("select", DOMAIN, f"{link.hub.prefix}_flow_{COMFORT_STYLE_KEY}")
    record = registry.async_get(entity_id) if entity_id else None
    if record is not None and record.config_entry_id == entry.entry_id:
        registry.async_remove(entity_id)


def _wanted_switches(link):
    if link.settings is not None:
        for key in OPTIONS:
            yield key, lambda key=key: FlowOptionSwitch(link, key)


def _wanted_selects(link):
    if link.settings is not None:
        yield DESIGN_FLOW_KEY, lambda: FlowDesignSelect(link)
        if COMFORT_STYLE_KEY in link.settings:
            yield COMFORT_STYLE_KEY, lambda: FlowComfortSelect(link)


async def _async_setup_controls(hass, entry, async_add_entities, wanted):
    from .product import is_product
    if not is_product(entry):
        return
    link = flow_link(hass, entry)
    if link is None:
        return
    entry.async_on_unload(track_entities(link, async_add_entities, add_options(hass, entry), wanted))


async def async_setup_switches(hass, entry, async_add_entities):
    await _async_setup_controls(hass, entry, async_add_entities, _wanted_switches)


async def async_setup_selects(hass, entry, async_add_entities):
    await _async_setup_controls(hass, entry, async_add_entities, _wanted_selects)


# -- the sensors -----------------------------------------------------------------------


def summary_part(hub, key):
    """``flow`` or ``night_gas`` of the E32 summary (the hub merges fw/telemetry/flow into it), or None."""
    summary = getattr(hub, "summary", None)
    part = summary.get(key) if type(summary) is dict else None
    return part if type(part) is dict else None


def gas_calibration(hub):
    """The learner's gas calibration (``learned.gas`` of the summary), or None on firmware without it."""
    header = hub.learned_header
    gas = header.get("gas") if type(header) is dict else None
    return gas if type(gas) is dict else None


def _text(item, key):
    value = item.get(key) if type(item) is dict else None
    return value if type(value) is str and len(value) <= 40 else None


def _flow(value):
    return number(value, 0, 90)


def standard_slope(design_flow_c):
    """WeatherCurve::slopeFor: K of water above the room per K the outdoor is below it, or None."""
    if type(design_flow_c) is not int or not DESIGN_FLOW_LIMITS[0] <= design_flow_c <= DESIGN_FLOW_LIMITS[1]:
        return None
    slope = (design_flow_c - DESIGN_ROOM_C) / (DESIGN_ROOM_C - DESIGN_OUTDOOR_C)
    return round(min(SLOPE_LIMITS[1], max(SLOPE_LIMITS[0], slope)), 3)


def design_flow(settings, plan, learned=None):
    """The water temperature in hard frost the E32 uses: the stored one, else 55 °C with any radiator room and
    40 °C for floor heating only (as FlowPolicy decides), or None while neither is known."""
    stored = settings.get(DESIGN_FLOW_KEY) if type(settings) is dict else None
    if type(stored) is int and stored > 0:
        return stored
    rooms = plan.get("rooms") if type(plan) is dict and type(plan.get("rooms")) is list else None
    emitters = [room.get("emitter") for room in (rooms if rooms else (learned or {}).values()) if type(room) is dict]
    for emitter in ("radiator", "floor"):
        if emitter in emitters:
            return DESIGN_FLOW_BY_EMITTER[emitter]
    return None


def curve_room_c(rooms):
    """The room temperature the curve is drawn for: the highest target of the rooms the E32 heats now
    (FlowPolicy takes the highest base over its usable rooms), else 20 °C."""
    targets = [number(room.get("setpoint"), 5, 30) for room in (rooms or {}).values()
               if type(room) is dict and room.get("status") in ("ok", "fallback")]
    targets = [value for value in targets if value is not None]
    return max(targets) if targets else DESIGN_ROOM_C


def _limit(value):
    return value if type(value) is int and 20 <= value <= 90 else None


def _published_design(curve):
    """The water temperature in hard frost the E32 publishes with its curve (rc.5), or None."""
    value = curve.get("design_flow_c") if type(curve) is dict else None
    return value if type(value) is int and DESIGN_FLOW_LIMITS[0] <= value <= DESIGN_FLOW_LIMITS[1] else None


def curve_chart(settings, plan, learned, rooms, outdoor_c, curve=None, boiler_maximum_c=None):
    """What the heating-curve card draws besides the curve's slope: {design_flow_c, standard_slope, room_c,
    outdoor_c, minimum_flow_c, maximum_flow_c, base_c, flow_c}, all in °C; None for what is not known.

    The design flow is the one the E32 publishes (rc.5), else worked out as FlowPolicy does. The highest water
    temperature is FlowPolicy's cap: the plan's maximum, at most 80 °C and the boiler's own maximum.
    """
    design = _published_design(curve) or design_flow(settings, plan, learned)
    plan = plan if type(plan) is dict else {}
    curve = curve if type(curve) is dict else {}
    outdoor, base = number(outdoor_c, -50, 60), number(curve.get("base_c"), 0, 90)
    highest = [value for value in (_limit(plan.get("maximum_flow_c")), _limit(boiler_maximum_c)) if value is not None]
    return {"design_flow_c": design, "standard_slope": standard_slope(design), "room_c": curve_room_c(rooms),
            "outdoor_c": round(outdoor, 1) if outdoor is not None else None,
            "minimum_flow_c": _limit(plan.get("minimum_flow_c")),
            "maximum_flow_c": min(*highest, FLOW_CEILING_C) if highest else None,
            "base_c": round(base, 1) if base is not None else None, "flow_c": _flow(curve.get("flow_c"))}


def curve_outdoor(hass, entry, hub):
    """The outdoor temperature the E32 uses now (learned.inputs.outdoor) as Home Assistant sees it: the boiler's
    own sensor, or the one set under Energy and outdoor temperature; None without one."""
    from .energy_input import CONF_OUTDOOR, energy_options, outdoor_celsius
    from .heating_link import celsius, learned_inputs
    source = learned_inputs(hub.learned_header).get("outdoor")
    if source == "ha":
        entity_id = energy_options(entry).get(CONF_OUTDOOR)
        return outdoor_celsius(hass.states.get(entity_id)) if type(entity_id) is str else None
    if source == "boiler":
        from homeassistant.helpers import entity_registry as er
        entity_id = er.async_get(hass).async_get_entity_id(
            "sensor", DOMAIN, f"{hub.prefix}_boiler_fields_v1_outdoor_temperature")
        state = hass.states.get(entity_id) if entity_id else None
        return celsius(state.state, state.attributes.get("unit_of_measurement"), -50, 60) if state else None
    return None


def _utc(value):
    if type(value) is not int or value <= 0:
        return None
    return datetime.fromtimestamp(value, timezone.utc).isoformat()


class FlowSummarySensor(HubEntity, SensorEntity):
    """One value of the summary on the product device."""

    part = "flow"

    def __init__(self, hub, key):
        self._attach(hub, key)
        self._attr_translation_key = key

    @property
    def data(self):
        if not self.hub.fresh:
            return None
        return gas_calibration(self.hub) if self.part == "gas" else summary_part(self.hub, self.part)

    @property
    def available(self):
        return self.data is not None


class FlowSourceSensor(FlowSummarySensor):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = SOURCES

    def __init__(self, hub):
        super().__init__(hub, "flow_source")

    @property
    def native_value(self):
        source = _text(self.data, "source")
        return source if source in SOURCES else None

    @property
    def extra_state_attributes(self):
        flow = self.data
        if flow is None:
            return None
        curve, learned = flow.get("curve"), flow.get("learned")
        start = flow.get("optimum_start")
        attributes = {"applied_flow_c": _flow(flow.get("applied_flow_c")), "rule_flow_c": _flow(flow.get("rule_flow_c")),
                      "curve_state": _text(curve, "state"), "learned_state": _text(learned, "state"),
                      "optimum_start": start if type(start) is str else _text(start, "state")}
        yesterday = flow.get("yesterday") if type(flow.get("yesterday")) is dict else {}
        for key in ("rule", "applied", "curve", "learned"):
            attributes[f"yesterday_{key}_mean_c"] = _flow(yesterday.get(f"{key}_mean_c"))
        # E32 rc.5: the most the E32 asks near the target now (flow.ceiling_c, in effect only with Smart warm-up on and
        # the E32 driving the boiler; None otherwise), as the Boiler view's Now card says it ("at most 40 °C").
        from .insight import ceiling_in_effect
        attributes["ceiling_c"] = ceiling_in_effect({"flow": flow})
        return attributes


# 1.4.6 (HA-LEARN-TEXTS): "Learned water temperature" is never Unknown. The E32 leaves ``learned.flow_c`` out until it has
# learned one (and after a demotion): the sensor then keeps the last value it reported (``last_reported``, a sentence
# saying so), and says "Not learned yet" in words before the first one. The same unique id and entity id as before.
KEEPS = ("flow_learned",)
LEARNED_TEXT = {
    "en": {"word": "Not learned yet", "none": "The E32 has not learned a water temperature yet.",
           "kept": "The E32 does not report a learned water temperature right now; this is the last one it reported."},
    "nl": {"word": "Nog niet geleerd", "none": "De E32 heeft nog geen watertemperatuur geleerd.",
           "kept": "De E32 meldt nu geen geleerde watertemperatuur; dit is de laatste die hij meldde."},
}


class FlowTemperatureSensor(RestoreEntity, FlowSummarySensor):
    """A flow in °C: the heating curve's, the learned one or the room control's (what each asks for now)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    PATHS = {"flow_curve": ("curve", "flow_c"), "flow_learned": ("learned", "flow_c"), "flow_rule": (None, "rule_flow_c")}
    _unrecorded_attributes = frozenset(CURVE_CHART_KEYS)

    def __init__(self, hub, key):
        super().__init__(hub, key)
        self.block, self.field = self.PATHS[key]
        self._attr_entity_registry_enabled_default = key != "flow_rule"
        self._kept = None  # (°C, unix s) the last learned value reported (KEEPS only)

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if self.key_kept and self._kept is None:
            last = await self.async_get_last_state()
            try:
                value = float(last.state) if last is not None else None
            except (TypeError, ValueError):
                value = None
            if value is not None and 0 <= value <= 90:
                # The moment the state was last changed: never newer than the truth (an unchanged value is older still).
                self._kept = (_flow(value), last.last_updated.timestamp())

    @property
    def key_kept(self):
        return self.block == "learned"

    def _reported(self):
        return _flow((self._block() or {}).get(self.field))

    def _value(self):
        """What the sensor shows: the E32's value; for KEEPS the last one reported while it reports none; else None."""
        value = self._reported()
        if not self.key_kept:
            return value
        if value is not None:
            self._kept = (value, time.time())
            return value
        return self._kept[0] if self._kept is not None else None

    def _words(self):
        """KEEPS: no value now and none ever kept: the state is a few words, not a number."""
        return self.key_kept and self._value() is None

    def _lang(self):
        from .learned_overview import language
        return language(getattr(self, "hass", None))

    @property
    def device_class(self):
        return None if self._words() else SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        return None if self._words() else SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self):
        return None if self._words() else UnitOfTemperature.CELSIUS

    def _chart(self, curve):
        """The heating-curve card's figures (curve_chart) from the E32's curve, options, plan, rooms and outdoor and
        the boiler's own maximum."""
        hass = getattr(self, "hass", None)
        entry = getattr(getattr(self, "platform", None), "config_entry", None)
        state = hass.data.get(DOMAIN, {}).get(entry.entry_id, {}) if hass is not None and entry is not None else {}
        outdoor = curve_outdoor(hass, entry, self.hub) if state else None
        client = getattr(state.get("v1_connection"), "client", None)
        if client is not None:
            from .heating_advice import boiler_maximum
            boiler = boiler_maximum(client)
        else:
            boiler = None
        plan = getattr(self.hub.plan, "plan", None)
        return curve_chart(getattr(state.get(KEY), "settings", None), plan, self.hub.learned, self.hub.rooms, outdoor,
                           curve, boiler)

    def _block(self):
        flow = self.data
        block = flow if self.block is None or flow is None else flow.get(self.block)
        return block if type(block) is dict else None

    @property
    def native_value(self):
        value = self._value()
        if value is None and self.key_kept:
            return LEARNED_TEXT[self._lang()]["word"]
        return value

    @property
    def extra_state_attributes(self):
        block = self._block()
        if (block is None and not self.key_kept) or self.block is None:
            return None
        attributes = {"state": _text(block, "state")}
        if self.key_kept and self._reported() is None:
            text = LEARNED_TEXT[self._lang()]
            if self._kept is None:
                attributes["learned_text"] = text["none"]
            else:
                attributes["last_reported"] = datetime.fromtimestamp(self._kept[1], timezone.utc).isoformat()
                attributes["learned_text"] = text["kept"]
        if self.block == "curve":
            # windows (E32 rc.3): the steady periods seen so far; the E32 uses the learned line from 6 (the Overview's
            # Today says so, dashboard._weather_line).
            windows = block.get("windows")
            attributes.update(slope=number(block.get("slope"), 0, 10), slope_source=_text(block, "slope_source"),
                              windows=windows if type(windows) is int and windows >= 0 else None)
            attributes.update(self._chart(block))  # E32 rc.5: the heating-curve card
        return attributes


class CurveSlopeSensor(FlowSummarySensor):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(self, hub):
        super().__init__(hub, "flow_curve_slope")

    @property
    def native_value(self):
        curve = (self.data or {}).get("curve")
        return number(curve.get("slope"), 0, 10) if type(curve) is dict else None

    @property
    def extra_state_attributes(self):
        curve = (self.data or {}).get("curve")
        return {"slope_source": _text(curve, "slope_source")} if type(curve) is dict else None


class GasCalibrationSensor(FlowSummarySensor):
    part = "gas"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = GAS_STATUSES

    def __init__(self, hub):
        super().__init__(hub, "gas_calibration")

    @property
    def native_value(self):
        status = _text(self.data, "status")
        return status if status in GAS_STATUSES else None

    @property
    def extra_state_attributes(self):
        gas = self.data
        if gas is None:
            return None
        confidence = _text(gas, "confidence")
        return {"confidence": confidence if confidence in ("none", "low", "medium", "high") else None,
                "factor": number(gas.get("factor"), 0, 10), "kw_source": _text(gas, "kw_source")}


class BoilerFullPowerSensor(FlowSummarySensor):
    part = "gas"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_suggested_display_precision = 1

    def __init__(self, hub):
        super().__init__(hub, "boiler_full_power")

    @property
    def native_value(self):
        return number((self.data or {}).get("kw_at_full_modulation"), 0, 200)

    @property
    def extra_state_attributes(self):
        gas = self.data
        return {"kw_source": _text(gas, "kw_source"), "confidence": _text(gas, "confidence")} if gas else None


class NightGasSensor(FlowSummarySensor):
    """The last night's measured heating gas (hot water taken off) next to the model's prediction."""

    part = "night_gas"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.GAS
    _attr_native_unit_of_measurement = UnitOfVolume.CUBIC_METERS
    _attr_suggested_display_precision = 2

    def __init__(self, hub):
        super().__init__(hub, "night_heating_gas")

    @property
    def last(self):
        last = (self.data or {}).get("last")
        return last if type(last) is dict else None

    @property
    def native_value(self):
        last = self.last
        return number(last.get("heating_m3"), 0, 1000) if last and last.get("status") == "measured" else None

    @property
    def extra_state_attributes(self):
        night, last = self.data, self.last
        if night is None:
            return None
        last = last or {}
        return {"status": _text(last, "status"), "hot_water_m3": number(last.get("hot_water_m3"), 0, 1000),
                "predicted_m3": number(last.get("predicted_program_m3"), 0, 1000),
                "recommended": _text(last, "recommended"), "morning": _utc(last.get("switch_utc")),
                "model_ratio": number(night.get("model_ratio"), 0, 100), "nights": night.get("nights")
                if type(night.get("nights")) is int else None}


def wanted_sensors(hub):
    # 1.4.2 (HC-03): each also while the E32's status is not known, when it existed before (kept_while_unknown).
    from .heating_link import kept_while_unknown
    flow = summary_part(hub, "flow") is not None  # firmware with the flow options (E32 beta.19)
    if flow or kept_while_unknown(hub, "flow_source"):
        yield ("flow", "source"), lambda: FlowSourceSensor(hub)
    for key in FlowTemperatureSensor.PATHS:
        if flow or kept_while_unknown(hub, key):
            yield ("flow", key), lambda key=key: FlowTemperatureSensor(hub, key)
    if flow or kept_while_unknown(hub, "flow_curve_slope"):
        yield ("flow", "slope"), lambda: CurveSlopeSensor(hub)
    gas = gas_calibration(hub) is not None
    if gas or kept_while_unknown(hub, "gas_calibration"):
        yield ("gas", "calibration"), lambda: GasCalibrationSensor(hub)
    if gas or kept_while_unknown(hub, "boiler_full_power"):
        yield ("gas", "full_power"), lambda: BoilerFullPowerSensor(hub)
    last = (summary_part(hub, "night_gas") or {}).get("last")
    # Only with a gas meter, from the first measured night; then it stays (unknown after a night without a
    # measurement, 1.4.1: never a record without its entity, heating_link.entity_was_there).
    from .heating_link import entity_was_there
    if (type(last) is dict and last.get("status") == "measured") or entity_was_there(hub, "night_heating_gas"):
        yield ("night_gas",), lambda: NightGasSensor(hub)


async def async_setup_sensors(hass, entry, async_add_entities):
    from .product import is_product
    if not is_product(entry):
        return
    hub = heating_hub(hass, entry)
    entry.async_on_unload(track_entities(hub, async_add_entities, add_options(hass, entry), wanted_sensors))
