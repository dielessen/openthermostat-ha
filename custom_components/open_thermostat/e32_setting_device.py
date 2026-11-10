"""Every E32 room runs its own week program; an optional setting device adjusts it.

Owner, 30 Oct 2026: "per ruimte een weekplanner ... los daarvan kun je de
temperatuur instellen / overrulen met een thermostaatfunctie: een trv, een tado
thermostaat, alleen een virtuele thermostaat, of een losse sensor waarmee je de
temperatuur kunt instellen", and yes: push the program target to the knob.

- The week program lives on the E32 and runs without Home Assistant. A new
  room starts from "Workdays and weekend" (comfort 20 °C, away 18 °C, night
  16 °C, the week planner's defaults) in the room editor; a room without a
  program keeps its temperature without a week program (1.4, issue #7: a
  deliberate choice, so no Repairs item asks to give it one any more; the
  item ``room_programs`` an older version raised goes at the next start).
- The room's **setting device** is its plan ``setpoint_entity``: a climate
  entity (a radiator valve such as a TV02, a tado, any thermostat) or a
  number / input_number with a target. Without one, our room thermostat and
  the E32 page are the virtual thermostat.
- Home Assistant writes the E32's current target (the program's, or an
  override or away) to the setting device whenever it differs from what the
  device shows: at each switch point, when the plan changes and when the E32,
  Home Assistant or the device comes back. Only the device the user chose for
  the room, only while the room is on, not paused for an open window and the
  E32 runs its program (it has the clock), rounded to the device's step, at
  most once a minute per room. An override or away changes the E32's reported
  ``setpoint`` while ``setpoint_source`` stays "schedule", so both are written.
  Without the clock the E32 takes the device's own target as the room's
  (``setpoint_source`` "ha") or its fixed one ("fallback"): nothing is written
  then, or an override or away would become the device's target and outlive
  its end.
- The room thermostat shows the link (``setting_device_attributes``): the
  device, the last target written and the last knob value taken (each with its
  time), and the last failure in plain words. Three failed writes in a row
  raise a Repairs item; the next write that works (or the device showing the
  E32's target) clears it.
- A target on the device that we did not write (somebody turned the knob or
  used the device's app) becomes an E32 override "until the next switch point"
  (or the configured time without a week program or clock). Our own write is
  recognised by value (within half the device's step) and for 10 s after it.
- Without Home Assistant the E32 keeps running the program; knob changes are
  not seen then. When it comes back the current target is written again. A
  device that comes back itself (unavailable, or loaded after this
  integration) is not a knob turn: the E32's target is written to it. While it
  is unavailable nothing is written (Home Assistant would skip it anyway).
- A device that keeps changing its own target at the same times on several
  days runs its own schedule: a Repairs issue asks to switch it to manual.
- Summer mode (E32 1.4.1): the device shows the room's frost limit (the E32's
  ``setpoint`` with ``setpoint_source`` "summer"), and a knob turn is no
  override (the E32 refuses one in summer): the frost limit is written back
  within a minute (the design's "local control is put back").

Nothing here writes to the boiler; the frost floor, flow limits and the guard
are the E32's and unchanged.
"""
from __future__ import annotations

import logging
import math
import time

from homeassistant.const import UnitOfTemperature
from homeassistant.core import CoreState, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import async_call_later, async_track_state_change_event
from homeassistant.util import dt as dt_util

from .issue_sync import remove_retired_issues
from .const import DOMAIN
from .heating_link import celsius, number

_LOGGER = logging.getLogger(__name__)

DEVICE_DOMAINS = ("climate", "number", "input_number")
MIN_INTERVAL = 60       # s between two writes to one device
ECHO_SECONDS = 10       # our own write settles
PENDING_SECONDS = 60    # a knob change waits this long for the E32 to report it as its target
TARGET_TEMPERATURE, TARGET_TEMPERATURE_RANGE = 1, 2  # ClimateEntityFeature bits (no import of the enum needed)
SCHEDULE_DAYS = 3       # unasked changes at the same quarter on this many days: its own schedule
SCHEDULE_WINDOW_DAYS = 8
# Retired in 1.4 (issue #7): "Give your rooms a week program"; only removed where an older version left it.
OWN_SCHEDULE_ISSUE = "device_own_schedule"
WRITE_FAILED_ISSUE = "setting_device_write_failed"
FAILURES_FOR_REPAIR = 3  # failed writes in a row to one device before Repairs says so
GONE = ("unavailable", "unknown")  # a device state without a target: back from it is no knob turn

# The last failure in plain words (the room thermostat's setting_device_error and the Repairs item's {error}).
ERROR_TEXT = {
    "en": {"write": "Could not set {value}: {detail}",
           "missing": "{device} no longer exists in Home Assistant.",
           "unavailable": "{device} is unavailable; the target follows when it is back.",
           "knob": "Could not take over {value} from the device: {detail}"},
    "nl": {"write": "{value} instellen lukte niet: {detail}",
           "missing": "{device} bestaat niet meer in Home Assistant.",
           "unavailable": "{device} is niet beschikbaar; de gewenste temperatuur volgt zodra het terug is.",
           "knob": "{value} van het apparaat overnemen lukte niet: {detail}"},
    "pl": {"write": "Nie udało się ustawić {value}: {detail}",
           "missing": "{device} nie istnieje już w Home Assistant.",
           "unavailable": "{device} jest niedostępne; temperatura zadana zostanie ustawiona, gdy wróci.",
           "knob": "Nie udało się przejąć {value} z urządzenia: {detail}"},
}

# The week planner's "Workdays and weekend" (week-editor.js TEMPLATES.work, levels comfort/away/night).
COMFORT, AWAY, NIGHT = 2000, 1800, 1600
WORKDAY = [(390, COMFORT), (510, AWAY), (1020, COMFORT), (1350, NIGHT)]
WEEKEND = [(480, COMFORT), (1380, NIGHT)]


def default_program(low=500, high=3000):
    """The template as a plan "schedule" (7 days of [minute, centi_c]) within the room's limits."""
    clamp = lambda v: max(low, min(high, v))  # noqa: E731
    return [[[m, clamp(c)] for m, c in (WORKDAY if day < 5 else WEEKEND)] for day in range(7)]


def has_program(room):
    schedule = (room or {}).get("schedule")
    return (type(schedule) is list and any(day for day in schedule)) or bool((room or {}).get("week"))


def setting_device(room):
    entity_id = (room or {}).get("setpoint_entity")
    return entity_id if type(entity_id) is str and entity_id.split(".")[0] in DEVICE_DOMAINS else None


def proposed_device(room):
    """A climate source of the room (its valve or thermostat) as the setting device, when it has none."""
    if setting_device(room):
        return None
    for source in (room or {}).get("sources") or []:
        if source.get("type") == "ha" and str(source.get("id", "")).startswith("climate."):
            return source["id"]
    return None


def setting_hint(device, language):
    """The room form's hint for a climate source that could be the setting device ("" without one).

    Only a hint: the form never pre-selects it, the user picks it (Home Assistant
    then writes the device's target at every switch point)."""
    if not device:
        return ""
    if str(language or "").startswith("nl"):
        return (f"\n\n**Instelapparaat?** {device} gebruiken als instelapparaat van deze ruimte? Home Assistant "
                "zet dan bij elk schakelpunt van het weekprogramma de gewenste temperatuur erop. "
                "Kies het daarvoor zelf bij Instelapparaat.")
    if str(language or "").startswith("pl"):
        return (f"\n\n**Urządzenie nastawcze?** Użyć {device} jako urządzenia nastawczego tego pomieszczenia? "
                "Home Assistant ustawi wtedy jego temperaturę zadaną w każdym punkcie przełączenia programu "
                "tygodniowego. Aby tak było, wybierz je w polu Urządzenie nastawcze.")
    return (f"\n\n**Setting device?** Use {device} as this room's setting device? Home Assistant will then set "
            "its target temperature at every switch point of the week program. To do so, choose it under "
            "Setting device.")


def _unit(hass, state):
    if state.domain == "climate":
        return hass.config.units.temperature_unit
    return state.attributes.get("unit_of_measurement") or UnitOfTemperature.CELSIUS


def device_target(hass, state):
    """The device's target in °C, or None."""
    if state is None or state.state in ("unavailable", "unknown"):
        return None
    if state.domain == "climate":
        # A thermostat with only a temperature range (TARGET_TEMPERATURE_RANGE, such as the Bosch Room thermostat II
        # through Zigbee2MQTT) carries its heating setpoint in target_temp_low (issue #5).
        value = state.attributes.get("temperature")
        if value is None:
            value = state.attributes.get("target_temp_low")
    else:
        value = state.state
    return celsius(value, _unit(hass, state), 5, 35)


def device_step(state):
    """The device's step in °C (close enough for °F devices too)."""
    key = "target_temp_step" if state.domain == "climate" else "step"
    step = number(state.attributes.get(key), 0.01, 5)
    return step if step is not None else 0.5


async def async_write(hass, state, value_c, context=None):
    """Set the device's target (its own service), rounded to its step and in its unit."""
    unit, step = _unit(hass, state), device_step(state)
    value = value_c
    if unit not in (UnitOfTemperature.CELSIUS, None, ""):
        from homeassistant.util.unit_conversion import TemperatureConverter
        value = TemperatureConverter.convert(value_c, UnitOfTemperature.CELSIUS, unit)
    value = round(round(value / step) * step, 2)
    low, high = number(state.attributes.get("min_temp" if state.domain == "climate" else "min"), -100, 1000), \
        number(state.attributes.get("max_temp" if state.domain == "climate" else "max"), -100, 1000)
    if low is not None:
        value = max(value, low)
    if high is not None:
        value = min(value, high)
    if state.domain == "climate":
        features = number(state.attributes.get("supported_features"), 0, 2 ** 31) or 0
        if "temperature" in state.attributes or int(features) & TARGET_TEMPERATURE:
            data = {"entity_id": state.entity_id, "temperature": value}
        else:
            # Range only (issue #5): the heating setpoint, with the cooling setpoint kept (never below the new low).
            high = number(state.attributes.get("target_temp_high"), -100, 1000)
            data = {"entity_id": state.entity_id, "target_temp_low": value,
                    "target_temp_high": max(high, value) if high is not None else value}
        service = "set_temperature"
    else:
        service, data = "set_value", {"entity_id": state.entity_id, "value": value}
    await hass.services.async_call(state.domain, service, data, blocking=True, context=context)
    return value


def _language(hass):
    value = (getattr(getattr(hass, "config", None), "language", None) or "en").lower().replace("_", "-").split("-")[0]
    return value if value in ERROR_TEXT else "en"


def _degrees(value, lang):
    """20.5 °C (a decimal comma in Dutch and Polish)."""
    text = f"{round(float(value), 1):.1f}".rstrip("0").rstrip(".")
    return (text.replace(".", ",") if lang != "en" else text) + " °C"


def _detail(err):
    """An error in words: its message, else its kind."""
    return str(err).strip() or type(err).__name__


def error_text(error, lang):
    """A recorded failure (kind, device, °C or None, detail) as one plain sentence in ``lang``."""
    if error is None:
        return None
    kind, device, value, detail = error
    return ERROR_TEXT[lang][kind].format(device=device, value=_degrees(value, lang) if value is not None else "",
                                         detail=detail)


def _new_link(device):
    return {"device": device, "written": None, "written_at": None, "knob": None, "knob_at": None,
            "error": None, "failures": 0, "checked": None}


def setting_device_attributes(hass, entry, room_id, plan_room):
    """The room thermostat's diagnostic attributes for its setting device; {} without one.

    ``setting_device`` (entity ID), ``setting_device_written`` (the last target written, °C) and
    ``setting_device_written_at``, ``setting_device_knob`` (the last knob value taken as an override, °C) and
    ``setting_device_knob_at`` (ISO times: the dashboard shows them in the user's locale), and
    ``setting_device_error``: the last failure in plain words, None once a write works again. Kept in memory: after
    a restart the values come back with the next write or knob change.
    """
    device = setting_device(plan_room)
    if device is None:
        return {}
    state = ((hass.data.get(DOMAIN) or {}).get(entry.entry_id) or {}) if hass is not None else {}
    pusher = state.get("setting_device_pusher") if type(state) is dict else None
    link = pusher.links.get(room_id) if pusher is not None else None
    if link is None or link["device"] != device:
        link = _new_link(device)
    return {"setting_device": device,
            "setting_device_written": link["written"], "setting_device_written_at": link["written_at"],
            "setting_device_knob": link["knob"], "setting_device_knob_at": link["knob_at"],
            "setting_device_error": error_text(link["error"], _language(hass))}


def _written_celsius(hass, state, value):
    """A written value (in the device's unit) back in °C, to a tenth."""
    value_c = celsius(value, _unit(hass, state), -100, 1000)
    return round(value_c, 1) if value_c is not None else None


class SettingDevicePusher:
    """One per entry: writes the E32 targets to the setting devices and turns knob changes into overrides."""

    def __init__(self, hass, entry, hub, clock=time.monotonic, now=dt_util.now):
        self.hass, self.entry, self.hub, self.clock, self.now = hass, entry, hub, clock, now
        self.pushed = {}       # room id -> (entity, °C, clock)
        self.pending = {}      # room id -> (°C, clock until)
        self.unasked = {}      # entity -> [(date, quarter)] of changes we did not write
        self.links = {}        # room id -> what the link did last (_new_link; setting_device_attributes shows it)
        self._tracked, self._unsubscribe, self._retry = (), None, None
        self._busy = set()

    # -- the rooms -------------------------------------------------------------------
    def rooms(self):
        """(room id, plan room, status room, device entity) for each room with a program and a setting device."""
        link = self.hub.plan
        plan = link.plan if link is not None else None
        for room in (plan or {}).get("rooms", []):
            device = setting_device(room)
            if device and has_program(room):
                yield room["id"], room, self.hub.rooms.get(room["id"]), device

    @staticmethod
    def desired(status_room):
        """The E32's effective target to show on the device, or None (off, window pause, program not running).

        The E32 reports the target after its adjustments in ``setpoint``: the program's, an override's (next,
        timed, boost) or the away, holiday or return target, while ``setpoint_source`` names the base, "schedule"
        whenever it runs the program. Without the clock the base is the device's own target ("ha") or the fixed
        one ("fallback"): writing an override or away then would make it the device's target, which the E32 takes
        back as its base, so the override or away would outlive its end.

        E32 1.3: also a room on Heat along only ("follow": it keeps its target) and Smart warm-up's lead
        (setpoint source "warmup": the program's coming target, already the room's). E32 1.4: also a reset time's
        temperature as the room's base (setpoint source "reset"; it needs the clock, like the program). E32 1.4.1:
        summer mode's frost limit (setpoint source "summer", 8 °C for a room that is on).
        """
        if not status_room or status_room.get("state") not in ("active", "follow"):
            return None
        comfort = status_room.get("comfort") if type(status_room.get("comfort")) is dict else {}
        if comfort.get("mode") == "window_open" or status_room.get("setpoint_source") not in ("schedule", "warmup", "reset", "summer"):
            return None
        return number(status_room.get("setpoint"), 5, 35)

    def _link(self, room_id, device):
        """The room's link record; a new one (and no Repairs item of the old device) when the device changed."""
        link = self.links.get(room_id)
        if link is None or link["device"] != device:
            if link is not None:
                ir.async_delete_issue(self.hass, DOMAIN, self._failed_issue(room_id))
            link = self.links[room_id] = _new_link(device)
        return link

    # -- pushing ---------------------------------------------------------------------
    @callback
    def evaluate(self, _now=None):
        self._retry = None
        if not self.hub.fresh:
            return
        self._follow_devices()
        self._clear_own_schedule_issues()
        self._forget_gone_links()
        wait = None
        for room_id, room, status, device in self.rooms():
            link = self._link(room_id, device)
            want, state = self.desired(status), self.hass.states.get(device)
            if want is None or room_id in self._busy:
                continue
            if state is None or state.state == "unavailable":
                self._not_there(room_id, room, link, device, state)
                continue
            pending = self.pending.get(room_id)
            if pending is not None:
                if abs(pending[0] - want) < 0.05 or self.clock() > pending[1]:
                    self.pending.pop(room_id, None)
                else:
                    continue  # the knob's value is on its way to the E32
            shown = device_target(self.hass, state)
            if shown is not None and abs(shown - want) <= device_step(state) / 2 + 0.01:
                self._succeeded(room_id, link)  # it shows the E32's target: nothing to repair
                continue
            last = self.pushed.get(room_id)
            if last is not None and self.clock() - last[2] < MIN_INTERVAL:
                wait = min(wait or MIN_INTERVAL, MIN_INTERVAL - (self.clock() - last[2]))
                continue
            self._busy.add(room_id)
            self.hass.async_create_task(self._push(room_id, room, state, want), f"OpenThermostat setting device {device}")
        if wait is not None and self._retry is None:
            self._retry = async_call_later(self.hass, wait + 1, self.evaluate)

    async def _push(self, room_id, room, state, want):
        error = None
        try:
            value = await async_write(self.hass, state, want)
        except Exception as err:  # noqa: BLE001 - any refusal (also a schema error) is a failed write, never a storm
            _LOGGER.warning("Could not set %s to the program target of E32 room %s: %s", state.entity_id, room_id, err)
            value, error = None, err
        finally:
            self._busy.discard(room_id)
        # Rate-limited also after a failure: never a write storm.
        self.pushed[room_id] = (state.entity_id, want, self.clock())
        link = self.links.get(room_id)
        if link is None or link["device"] != state.entity_id:
            return  # the room changed its setting device meanwhile: this write tells nothing about the new one
        if error is not None:
            self._failed(room_id, room, link, state, ("write", self._name(state), want, _detail(error)))
            return
        _LOGGER.debug("E32 room %s: set %s to %s", room_id, state.entity_id, value)
        link["written"], link["written_at"] = _written_celsius(self.hass, state, value), self.now().isoformat()
        self._succeeded(room_id, link)

    # -- what the link did: attributes and the Repairs item ------------------------------------
    @staticmethod
    def _name(state):
        return state.name if state is not None else None

    def _failed_issue(self, room_id):
        return f"{WRITE_FAILED_ISSUE}_{self.entry.entry_id}_{room_id}"

    @callback
    def _succeeded(self, room_id, link):
        if link["failures"] or link["error"] is not None:
            link["failures"], link["error"] = 0, None
            ir.async_delete_issue(self.hass, DOMAIN, self._failed_issue(room_id))

    @callback
    def _failed(self, room_id, room, link, state, error, count=True):
        """One failure: shown on the room thermostat; FAILURES_FOR_REPAIR in a row raise the Repairs item."""
        link["error"] = error
        if not count:
            return
        link["failures"] += 1
        if link["failures"] >= FAILURES_FOR_REPAIR:
            ir.async_create_issue(self.hass, DOMAIN, self._failed_issue(room_id), is_fixable=False, is_persistent=False,
                                  severity=ir.IssueSeverity.WARNING, translation_key=WRITE_FAILED_ISSUE,
                                  translation_placeholders={
                                      "device": self._name(state) or link["device"],
                                      "room": (room or {}).get("name") or room_id,
                                      "error": error_text(error, _language(self.hass))})

    @callback
    def _not_there(self, room_id, room, link, device, state):
        """No write to a device that is gone or unavailable. Gone while Home Assistant runs (not still starting,
        when a device's integration may load after this one) counts as a failed write, once a minute."""
        if state is not None:
            link["error"] = ("unavailable", self._name(state) or device, None, "")
            return
        if self.hass.state is not CoreState.running:
            return
        if link["checked"] is not None and self.clock() - link["checked"] < MIN_INTERVAL:
            return
        link["checked"] = self.clock()
        self._failed(room_id, room, link, None, ("missing", device, None, ""))

    @callback
    def _forget_gone_links(self):
        """The records and Repairs items of rooms that are gone or no longer have a setting device."""
        devices = {room_id: device for room_id, _room, _status, device in self.rooms()}
        for room_id in [r for r, link in self.links.items() if devices.get(r) != link["device"]]:
            del self.links[room_id]
            ir.async_delete_issue(self.hass, DOMAIN, self._failed_issue(room_id))
        head = f"{WRITE_FAILED_ISSUE}_{self.entry.entry_id}_"
        for domain, issue in list(ir.async_get(self.hass).issues):
            if domain == DOMAIN and issue.startswith(head) and devices.get(issue.removeprefix(head)) is None:
                ir.async_delete_issue(self.hass, DOMAIN, issue)

    # -- the knob --------------------------------------------------------------------
    @callback
    def _follow_devices(self):
        devices = tuple(sorted({device for *_rest, device in self.rooms()}))
        if devices == self._tracked:
            return
        self.stop_tracking()
        self._tracked = devices
        if devices:
            self._unsubscribe = async_track_state_change_event(self.hass, list(devices), self.device_changed)

    @callback
    def device_changed(self, event):
        if not self.hub.fresh:
            return
        entity_id, state = event.data["entity_id"], event.data.get("new_state")
        before = event.data.get("old_state")
        if state is not None and state.state != "unavailable" and (before is None or before.state in GONE):
            # Back (unavailable, or loaded after this integration): its target is what it had, not a knob turn.
            self.evaluate()
            return
        value = device_target(self.hass, state)
        old = device_target(self.hass, before)
        if value is None or (old is not None and abs(old - value) < 0.01):
            return  # no new target (another attribute changed)
        for room_id, room, status, device in self.rooms():
            if device != entity_id or status is None or status.get("state") not in ("active", "follow"):
                continue
            tolerance = device_step(state) / 2 + 0.01
            last = self.pushed.get(room_id)
            if last is not None and last[0] == entity_id and (abs(last[1] - value) <= tolerance
                                                              or self.clock() - last[2] < ECHO_SECONDS):
                return  # our own write
            current = number(status.get("setpoint"), 5, 35)
            if current is not None and abs(current - value) <= tolerance:
                return
            if status.get("setpoint_source") == "summer":
                self.evaluate()  # summer mode: no override; the frost limit goes back on the device within a minute
                return
            self.pending[room_id] = (value, self.clock() + PENDING_SECONDS)
            link = self._link(room_id, entity_id)
            link["knob"], link["knob_at"] = round(value * 2) / 2, self.now().isoformat()
            self._note_unasked(room_id, room, entity_id, state)
            self.hass.async_create_task(self._override(room_id, room, value), f"OpenThermostat knob {entity_id}")
            return

    async def _override(self, room_id, room, value):
        """The knob's target until the next switch point (else the configured time)."""
        from .e32_comfort import async_comfort_command, comfort_options, override_command
        from homeassistant.exceptions import ServiceValidationError
        value = round(value * 2) / 2
        try:
            try:
                await async_comfort_command(self.hub.plan, override_command(room_id, "next", value))
            except ServiceValidationError as err:
                if err.translation_key not in ("comfort_no_clock", "comfort_no_schedule"):
                    raise
                minutes = comfort_options(self.entry)["override_minutes"]
                await async_comfort_command(self.hub.plan, override_command(room_id, "timed", value, minutes))
        except HomeAssistantError as err:
            self.pending.pop(room_id, None)
            _LOGGER.warning("E32 room %s: could not take over %s °C from its setting device: %s", room_id, value, err)
            link = self.links.get(room_id)
            if link is not None:
                self._failed(room_id, room, link, None, ("knob", link["device"], value, _detail(err)), count=False)

    # -- the device's own schedule ------------------------------------------------------
    def _recent_unasked(self, entity_id):
        now = self.now()
        return [(d, q) for d, q in self.unasked.get(entity_id, []) if (now.date() - d).days < SCHEDULE_WINDOW_DAYS]

    def _own_schedule(self, entity_id):
        """Unasked changes at about the same quarter on SCHEDULE_DAYS days within the window."""
        seen = self._recent_unasked(entity_id)
        return any(len({d for d, other in seen if abs(other - q) <= 1}) >= SCHEDULE_DAYS for _, q in seen)

    @callback
    def _clear_own_schedule_issues(self):
        """The "own schedule" item goes once the condition is gone: the device stopped changing by
        itself for SCHEDULE_WINDOW_DAYS, it is no longer the room's setting device, or the room is gone."""
        head = f"{OWN_SCHEDULE_ISSUE}_{self.entry.entry_id}_"
        devices = {room_id: device for room_id, _room, _status, device in self.rooms()}
        for domain, issue in list(ir.async_get(self.hass).issues):
            if domain != DOMAIN or not issue.startswith(head):
                continue
            device = devices.get(issue.removeprefix(head))
            if device is None or not self._own_schedule(device):
                ir.async_delete_issue(self.hass, DOMAIN, issue)

    def _note_unasked(self, room_id, room, entity_id, state):
        now = self.now()
        quarter = (now.hour * 60 + now.minute) // 15
        seen = self._recent_unasked(entity_id)
        seen.append((now.date(), quarter))
        self.unasked[entity_id] = seen[-64:]
        days = {d for d, q in seen if abs(q - quarter) <= 1}
        if len(days) >= SCHEDULE_DAYS:
            name = state.name if state is not None else entity_id
            ir.async_create_issue(self.hass, DOMAIN, f"{OWN_SCHEDULE_ISSUE}_{self.entry.entry_id}_{room_id}",
                                  is_fixable=False, is_persistent=False, severity=ir.IssueSeverity.WARNING,
                                  translation_key=OWN_SCHEDULE_ISSUE,
                                  translation_placeholders={"device": name, "room": room.get("name") or room_id})

    # -- lifecycle -------------------------------------------------------------------------
    @callback
    def stop_tracking(self):
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None
        self._tracked = ()

    @callback
    def start(self):
        remove_retired_issues(self.hass, self.entry.entry_id)  # 1.4: the retired item room_programs of older versions
        remove = self.hub.add_listener(self.evaluate)
        self.evaluate()

        @callback
        def stop():
            remove()
            self.stop_tracking()
            if self._retry is not None:
                self._retry()
                self._retry = None
        return stop

