"""Last restart of the E32 and why (1.1.1, P1 HA-2): the sensor "Last restart" on the E32 device.

E32 1.1.1 publishes the retained ``fw/state/boot`` once per MQTT session (at most 300 B, F-FW2 FW-1)::

    {"schema": 1, "boot": "1a2b3c4d", "reset_reason": 3, "reset": "sw",
     "previous": null | {"uptime_s", "heap_min", "stack": {...}, "restart"?, "phase"?, ...},
     "coredump": null | {"task", "pc", "cause"}}

``boot`` is a random id per boot: a new value is a new boot. ``previous`` is null after a power cut (the RTC
memory is lost) and on the first boot after installing 1.1.1; ``restart`` is there only when the E32's
supervisor restarted it; ``coredump`` only after a crash.

The sensor is a timestamp: when the E32 started (the time of the report minus the heartbeat's uptime), so its
history has one row per restart. ``reason`` says why in plain words (translated states): power (power on or a
brown-out), restart (an install or a restart request), automatic (the supervisor restarted it; ``restart`` names
why), crash (a panic or a watchdog), unknown. The previous boot's uptime and lowest free memory, the restart
cause and the crash summary are attributes; the same object is in the diagnostics download.

Firmware without the topic never creates the entity (nothing to go stale). Diagnostic.

1.4 (FW-LOG): the sensor "E32 errors" (below) lives here too: the error lines of the E32's system log since it
started, from the heartbeat's ``errors``.
"""
from __future__ import annotations

from datetime import timedelta
import json
import re

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import CONF_TOPIC_PREFIX, DOMAIN

TOPIC = "fw/state/boot"
MAX_BYTES = 512
RESETS = ("unknown", "poweron", "ext", "sw", "panic", "int_wdt", "task_wdt", "wdt", "deepsleep", "brownout", "sdio")
REASONS = ["power", "restart", "automatic", "crash", "unknown"]
RESTARTS = ("loop_stall", "wifi_lost", "broker_lost", "network_dead", "update_stuck", "bluetooth_settings",
            "bluetooth_silent", "settings_restore", "control_fault", "setup_reenter")
_WORD = re.compile(r"[A-Za-z0-9_./-]{1,48}")
STATE_KEY = "last_restart"


def _count(value, high=2**32 - 1):
    return value if type(value) is int and 0 <= value <= high else None


def _word(value):
    return value if type(value) is str and _WORD.fullmatch(value) else None


def decode(payload):
    """The validated boot report, or None (older firmware, a cleared topic or an invalid message: ignored)."""
    if not isinstance(payload, (str, bytes)) or not payload or len(payload) > MAX_BYTES:
        return None
    try:
        value = json.loads(payload)
    except (ValueError, TypeError, UnicodeError):
        return None
    if type(value) is not dict or value.get("schema") != 1:
        return None
    boot = value.get("boot")
    if type(boot) is not str or not re.fullmatch(r"[0-9a-f]{1,16}", boot):
        return None
    reset = value.get("reset") if value.get("reset") in RESETS else "unknown"
    report = {"boot": boot, "reset": reset, "reset_reason": _count(value.get("reset_reason"), 255),
              "previous": None, "coredump": None}
    previous = value.get("previous")
    if type(previous) is dict:
        stack = previous.get("stack") if type(previous.get("stack")) is dict else {}
        report["previous"] = {
            "uptime_s": _count(previous.get("uptime_s")), "heap_min": _count(previous.get("heap_min")),
            "restart": previous.get("restart") if previous.get("restart") in RESTARTS else None,
            "phase": _word(previous.get("phase")), "slow_phase": _word(previous.get("slow_phase")),
            "slow_ms": _count(previous.get("slow_ms")), "request": _word(previous.get("request")),
            "stack": {k: _count(stack.get(k)) for k in ("loop", "sup", "ems", "ble") if _count(stack.get(k)) is not None}}
    dump = value.get("coredump")
    if type(dump) is dict:
        report["coredump"] = {"task": _word(dump.get("task")), "pc": _word(dump.get("pc")),
                              "cause": _count(dump.get("cause"), 255)}
    return report


def reason(report):
    """The plain-language reason of a boot report (REASONS)."""
    reset = report.get("reset")
    if reset in ("poweron", "brownout"):
        return "power"
    if reset in ("panic", "int_wdt", "task_wdt", "wdt") or report.get("coredump"):
        return "crash"
    if reset == "sw":
        return "automatic" if (report.get("previous") or {}).get("restart") else "restart"
    return "unknown"


class LastRestartSensor(SensorEntity):
    """When the E32 started and why (a diagnostic of the E32 device)."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "last_restart"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    # The crash and the previous boot's details only while shown; the state and the reason are history.
    _unrecorded_attributes = frozenset({"previous_stack", "previous_phase", "previous_slow_phase",
                                        "previous_slow_ms", "previous_request", "crash_task", "crash_pc"})

    def __init__(self, prefix, hub):
        self._hub = hub
        self.report = None
        self.started = None
        self._since = None
        self._attr_unique_id = f"{prefix}_hub_last_restart"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, prefix)})

    @property
    def available(self):
        return self.report is not None

    @property
    def native_value(self):
        return self.started

    @property
    def extra_state_attributes(self):
        report = self.report
        if report is None:
            return None
        previous, dump = report.get("previous") or {}, report.get("coredump") or {}
        uptime = previous.get("uptime_s")
        return {"reason": reason(report), "reset": report.get("reset"), "boot": report.get("boot"),
                "previous_uptime_h": round(uptime / 3600, 1) if uptime is not None else None,
                "previous_lowest_free_memory_kb": round(previous["heap_min"] / 1000) if previous.get("heap_min") else None,
                "automatic_restart": previous.get("restart"), "previous_stack": previous.get("stack") or None,
                "previous_phase": previous.get("phase"), "previous_slow_phase": previous.get("slow_phase"),
                "previous_slow_ms": previous.get("slow_ms"), "previous_request": previous.get("request"),
                "crash_task": dump.get("task"), "crash_pc": dump.get("pc"), "crash_cause": dump.get("cause")}

    @callback
    def receive(self, report):
        """A boot report: a new boot (another ``boot``) gets its start time from the next heartbeat's uptime."""
        if self.report is None or report["boot"] != self.report["boot"]:
            self.started = None
            self._since = self._hub.clock() if hasattr(self._hub, "clock") else None
        self.report = report
        self.heartbeat()

    @callback
    def heartbeat(self):
        """The first heartbeat after the report says how long the E32 has been running."""
        if self.report is not None and self.started is None:
            received = getattr(self._hub, "heartbeat_received", None)
            if received is not None and (self._since is None or received > self._since):
                self.started = started_at(self._hub)
        if self.hass is not None and self.entity_id is not None:
            self.async_write_ha_state()


def started_at(hub, now=None):
    """When the E32 started: now minus the heartbeat's uptime (whole minutes), else now."""
    now = now or dt_util.utcnow()
    beat = getattr(hub, "heartbeat", None)
    uptime = beat.get("uptime_s") if type(beat) is dict else None
    started = now - timedelta(seconds=uptime) if type(uptime) is int and 0 <= uptime < 10 * 365 * 86400 else now
    return started.replace(second=0, microsecond=0)


async def async_setup_sensor(hass, entry, async_add_entities):
    """Product entries: the sensor appears with the first valid fw/state/boot (E32 1.1.1 and newer)."""
    from homeassistant.components import mqtt
    from .heating_link import add_options, heating_hub, topic_base
    prefix = entry.data[CONF_TOPIC_PREFIX]
    hub = heating_hub(hass, entry)
    state = hass.data[DOMAIN][entry.entry_id]
    holder = {}

    @callback
    def received(message):
        report = decode(message.payload)
        if report is None:
            return
        state[STATE_KEY] = report
        sensor = holder.get("sensor")
        if sensor is None:
            sensor = holder["sensor"] = LastRestartSensor(prefix, hub)
            sensor.receive(report)
            async_add_entities([sensor], **add_options(hass, entry))
        else:
            sensor.receive(report)

    @callback
    def hub_changed():
        if (sensor := holder.get("sensor")) is not None and sensor.started is None:
            sensor.heartbeat()

    entry.async_on_unload(hub.add_listener(hub_changed))
    await mqtt.async_wait_for_mqtt_client(hass)
    entry.async_on_unload(await mqtt.async_subscribe(hass, topic_base(hass, entry) + TOPIC, received))


def diagnostics(hass, entry):
    """The last boot report for the diagnostics download, or None."""
    return hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get(STATE_KEY)


# -- E32 errors (1.4, FW-LOG) ------------------------------------------------------------------------------------------
#
# E32 1.4 counts the error lines of its system log since it started and keeps the last one; every fw/heartbeat
# (60 s) carries them as ``"errors"``: ``[count]`` without an error since the start, else
# ``[count, uptime_s of the last, "<source>: <message>"]`` (the line at most 120 characters, redacted like the log).
# The sensor "E32 errors" shows the count (it starts at 0 again after a restart) with the last line and its time as
# attributes. A figure, not a fault: no Repairs item (the owner's rule: Repairs only for what needs action).
# Firmware before 1.4 sends no "errors" and never gets the entity.

ERRORS_STATE_KEY = "e32_errors"
MAX_ERROR_TEXT = 160


def decode_errors(beat):
    """The heartbeat's error lines (E32 1.4): {"count", "at_s", "text"}, or None (older firmware or invalid)."""
    value = beat.get("errors") if type(beat) is dict else None
    if type(value) is not list or len(value) not in (1, 3):
        return None
    count = _count(value[0])
    if count is None:
        return None
    if len(value) == 1:
        return {"count": count, "at_s": None, "text": None}
    at, text = _count(value[1]), value[2]
    if (count == 0 or at is None or type(text) is not str or not 0 < len(text) <= MAX_ERROR_TEXT
            or not text.isprintable()):
        return None
    return {"count": count, "at_s": at, "text": text}


def error_time(beat, errors, now=None):
    """When the last error line was logged: now minus how long before this heartbeat (whole seconds), or None."""
    if errors is None or errors["at_s"] is None:
        return None
    now = now or dt_util.utcnow()
    uptime = beat.get("uptime_s") if type(beat) is dict else None
    ago = uptime - errors["at_s"] if type(uptime) is int and uptime >= errors["at_s"] else 0
    return (now - timedelta(seconds=ago)).replace(microsecond=0)


class E32ErrorsSensor(SensorEntity):
    """The error lines in the E32's system log since it started, and the last one (a diagnostic of the E32 device)."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "e32_errors"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    # A count that starts again at every restart: its statistics give the error lines per hour or day.
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, prefix, hub):
        self._hub = hub
        self.errors = None
        self.last_error_at = None
        self._shown = None
        self._attr_unique_id = f"{prefix}_hub_e32_errors"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, prefix)})

    @property
    def available(self):
        return self.errors is not None and getattr(self._hub, "alive", True)

    @property
    def native_value(self):
        return self.errors["count"] if self.errors is not None else None

    @property
    def extra_state_attributes(self):
        if self.errors is None:
            return None
        return {"last_error": self.errors["text"],
                "last_error_at": self.last_error_at.isoformat() if self.last_error_at is not None else None}

    @callback
    def receive(self, beat, errors, now=None, gone=False):
        """A heartbeat's errors (None: keep the last ones; gone: a live heartbeat without them, after a firmware
        downgrade: unavailable). The time of the last line is worked out once per new line, so it stays put;
        the state is written only when something shown changed (also availability)."""
        if gone:
            self.errors = self.last_error_at = None
        elif errors is not None and errors != self.errors:
            self.last_error_at = error_time(beat, errors, now)
            self.errors = errors
        shown = (self.available, self.errors, self.last_error_at)
        if shown == self._shown:
            return
        self._shown = shown
        if self.hass is not None and self.entity_id is not None:
            self.async_write_ha_state()


async def async_setup_errors_sensor(hass, entry, async_add_entities):
    """Product entries: "E32 errors" appears with the first heartbeat that carries them (E32 1.4 and newer)."""
    from .heating_link import add_options, heating_hub
    prefix = entry.data[CONF_TOPIC_PREFIX]
    hub = heating_hub(hass, entry)
    state = hass.data[DOMAIN][entry.entry_id]
    holder = {"beat": None}

    @callback
    def hub_changed():
        beat = getattr(hub, "heartbeat", None)
        errors, gone = None, False
        if beat is not holder["beat"]:
            holder["beat"] = beat
            errors = decode_errors(beat)
            gone = errors is None and beat is not None
        sensor = holder.get("sensor")
        if gone:
            state.pop(ERRORS_STATE_KEY, None)
        if errors is not None:
            state[ERRORS_STATE_KEY] = errors
            if sensor is None:
                if getattr(hub, "closed", False):
                    return
                sensor = holder["sensor"] = E32ErrorsSensor(prefix, hub)
                sensor.receive(beat, errors)
                async_add_entities([sensor], **add_options(hass, entry))
                return
        if sensor is not None:
            sensor.receive(beat, errors, gone=gone)  # new errors, none any more, or only whether the E32 is heard

    entry.async_on_unload(hub.add_listener(hub_changed))
    hub_changed()
