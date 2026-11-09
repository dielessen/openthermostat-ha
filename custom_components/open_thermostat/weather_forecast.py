"""The hourly outdoor forecast for the E32's heating plan (1.1.1 stage B, M3; owner's decisions D4 and D11).

Optional, Configure → Energy and outdoor temperature → "Weather forecast": a weather entity the owner chooses.
Not chosen: the outdoor temperature entity when that is a weather entity (``weather.*``); "Leave empty" on the
form switches it off (stored as FORECAST_OFF while the outdoor entity is a weather entity, else simply absent).

Every hour (and when the E32 is back or restarted, which keeps a forecast for 2 h only) Home Assistant calls
``weather.get_forecasts`` (type hourly) for it and sends the next 24 hourly outdoor temperatures to the E32
over ``<base>ha/heating_input``, as SL-B2 specified (src/control/HeatingInput.h)::

    {"kind":"forecast","hour":1794186000,"values":[72,70,66,61,58,55,53,52,54,60,68,77,84,88,90,89,85,79,74,70,67,65,63,61]}

``hour``: unix seconds of the first value, a whole hour (the next full hour when sent, or the forecast's first
whole hour when it starts later); ``values``: 1..24 whole tenths of °C (−500..600), one per hour from ``hour``,
read off the forecast linearly between its points (a provider whose points are not on the whole UTC hour, such
as a half-hour time zone, still gives the whole hours). The widest message is about 170 B (the E32 takes 256).

When anything fails (no entity, no hourly forecast, a service error, a gap, a value out of range) nothing is
sent: the E32 falls back by itself to persistence and its own learned daily profile of the outdoor
temperature. Only to firmware that reads it: the E32 shows its room models (``model`` in a learned room's
message since this boot) or its heating plan (``fw/telemetry/plan``); older firmware would refuse the kind
(``unknown_kind``) and show that as the last refused value.
"""
from __future__ import annotations

import json
import logging
import math
import time

from homeassistant.core import callback
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

CONF_FORECAST = "energy_forecast_entity"
FORECAST_OFF = "off"  # the stored value of "no forecast" while the outdoor entity is a weather entity
FORECAST_HOURS = 24
VALUE_LIMITS = (-500, 600)  # tenths of °C (HeatingInput.h)
FORECAST_EVERY_S = 3600
RETRY_S = 300  # after a failure: at the next five-minute refresh, not more often
MAX_GAP_S = 3 * 3600  # points further apart than this are no hourly forecast: the values stop there
SERVICE_TIMEOUT_S = 30
WEATHER_FEATURE_FORECAST_HOURLY = 2  # homeassistant.components.weather.WeatherEntityFeature.FORECAST_HOURLY


def forecast_entity(options):
    """The weather entity whose forecast goes to the E32, or None (off).

    The chosen one; none chosen: the outdoor temperature entity when it is a weather entity; FORECAST_OFF: off.
    """
    from .energy_input import CONF_OUTDOOR
    options = options if isinstance(options, dict) else {}
    chosen = options.get(CONF_FORECAST)
    if chosen == FORECAST_OFF:
        return None
    if type(chosen) is str and chosen.startswith("weather."):
        return chosen
    outdoor = options.get(CONF_OUTDOOR)
    return outdoor if type(outdoor) is str and outdoor.startswith("weather.") else None


def offers_hourly(state):
    """Whether a weather entity can give an hourly forecast (True while its features are not known)."""
    features = state.attributes.get("supported_features") if state is not None else None
    return type(features) is not int or bool(features & WEATHER_FEATURE_FORECAST_HOURLY)


def _celsius(value, unit):
    if type(value) is bool or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    if unit == "°F":
        return (value - 32) * 5 / 9
    if unit == "K":
        return value - 273.15
    return float(value) if unit in (None, "°C") else None


def forecast_points(forecast, unit="°C"):
    """[(unix seconds, °C)] of a ``get_forecasts`` list, in time order; unusable entries are left out."""
    points = {}
    for item in forecast if isinstance(forecast, list) else []:
        if not isinstance(item, dict):
            continue
        moment = item.get("datetime")
        when = dt_util.parse_datetime(moment) if type(moment) is str else None
        celsius = _celsius(item.get("temperature"), unit)
        if when is None or celsius is None:
            continue
        if when.tzinfo is None:
            when = when.replace(tzinfo=dt_util.get_default_time_zone())
        points[int(when.timestamp())] = celsius
    return sorted(points.items())


def forecast_payload(forecast, unit, now):
    """The heating_input message (a dict) for a forecast list at ``now`` (unix seconds), or None.

    One value per whole UTC hour from the next full hour (or the first whole hour the forecast covers), linear
    between the forecast's points, until 24 values, the forecast's end or a gap; None when nothing is left or
    one value lies outside what the E32 accepts (the E32 refuses the whole message then).
    """
    points = forecast_points(forecast, unit)
    if not points:
        return None
    hour = -(-int(now) // 3600) * 3600
    if hour < points[0][0]:
        hour = -(-points[0][0] // 3600) * 3600
    values, k = [], 0
    for step in range(FORECAST_HOURS):
        moment = hour + step * 3600
        while k + 1 < len(points) and points[k + 1][0] <= moment:
            k += 1
        t0, v0 = points[k]
        if moment == t0:
            value = v0
        elif k + 1 < len(points) and t0 < moment < points[k + 1][0] and points[k + 1][0] - t0 <= MAX_GAP_S:
            t1, v1 = points[k + 1]
            value = v0 + (v1 - v0) * (moment - t0) / (t1 - t0)
        else:
            break
        tenths = int(round(value * 10))
        if not VALUE_LIMITS[0] <= tenths <= VALUE_LIMITS[1]:
            return None
        values.append(tenths)
    if not values:
        return None
    return {"kind": "forecast", "hour": hour, "values": values}


def encode(payload):
    return json.dumps(payload, separators=(",", ":"))


def firmware_reads_forecast(hub):
    """Whether this E32 takes the forecast: it showed its room models since its last start, or its heating plan."""
    return bool(getattr(hub, "models_seen", False)) or getattr(hub, "heating_plan", None) is not None


class ForecastForwarder:
    """Sends the forecast hourly. ``check`` runs with the room inputs' five-minute refresh; ``reconfigure`` after
    the energy options change. ``call`` (tests): an async function (entity_id) -> the service response."""

    def __init__(self, hass, entry, send, hub, clock=time.monotonic, wall=None, call=None):
        self.hass, self.entry, self.send, self.hub, self.clock = hass, entry, send, hub, clock
        self.wall = wall or (lambda: dt_util.utcnow().timestamp())
        self._call = call
        self.sent_at = None      # monotonic: the last forecast sent
        self.tried_at = None     # monotonic: the last attempt (sent or failed)
        self.boots = None        # the hub's E32 restarts when it was last sent
        self.last = None         # the last message sent (a dict)
        self.error = None        # why the last attempt sent nothing
        self._task = None
        self._entity = None

    @property
    def entity(self):
        return forecast_entity(getattr(self.entry, "options", None) or {})

    def _due(self, now):
        """Another entity, never sent, the E32 restarted (it lost the forecast) or an hour since the last one;
        never twice within RETRY_S (a failure waits for the next five-minute refresh)."""
        if self._entity != self.entity:
            return True
        if self.tried_at is not None and 0 <= now - self.tried_at < RETRY_S:
            return False
        if self.sent_at is None or self.boots != getattr(self.hub, "boots", 0):
            return True
        return now - self.sent_at >= FORECAST_EVERY_S - 60

    @callback
    def check(self, _now=None):
        """Send when due: never yet, an hour since the last one, after an E32 restart or another entity."""
        if self.entity is None or not getattr(self.hub, "fresh", False) or not firmware_reads_forecast(self.hub):
            return
        if self._task is not None and not self._task.done():
            return
        if not self._due(self.clock()):
            return
        self._task = self.hass.async_create_task(self.async_publish(), "OpenThermostat weather forecast")

    @callback
    def reconfigure(self):
        """Another entity (or none) was chosen: send at once with the new one."""
        if self.entity != self._entity:
            self.sent_at = self.tried_at = None
        self.check()

    async def _response(self, entity_id):
        if self._call is not None:
            return await self._call(entity_id)
        return await self.hass.services.async_call(
            "weather", "get_forecasts", {"entity_id": entity_id, "type": "hourly"}, blocking=True,
            return_response=True)

    async def async_publish(self):
        entity_id = self.entity
        self._entity, self.tried_at = entity_id, self.clock()
        if entity_id is None:
            return None
        state = self.hass.states.get(entity_id)
        payload = None
        try:
            if state is None or state.state in ("unavailable", "unknown"):
                raise LookupError("the weather entity is not available")
            if not offers_hourly(state):
                raise LookupError("the weather entity gives no hourly forecast")
            response = await self._response(entity_id)
            forecast = ((response or {}).get(entity_id) or {}).get("forecast") if isinstance(response, dict) else None
            payload = forecast_payload(forecast, state.attributes.get("temperature_unit", "°C"), self.wall())
            if payload is None:
                raise LookupError("the forecast has no usable hourly values")
        except Exception as err:  # noqa: BLE001 - no forecast is fine: the E32 falls back by itself
            self.error = str(err) or type(err).__name__
            _LOGGER.debug("OpenThermostat: no weather forecast for the E32 from %s: %s", entity_id, self.error)
            return None
        self.error, self.last = None, payload
        self.sent_at, self.boots = self.clock(), getattr(self.hub, "boots", 0)
        self.send(encode(payload))
        return payload

    def diagnostics(self):
        now = self.clock()
        return {"entity": self.entity, "last_hour": (self.last or {}).get("hour"),
                "values": len((self.last or {}).get("values") or []),
                "sent_age_s": round(now - self.sent_at, 1) if self.sent_at is not None else None,
                "error": self.error}

    @callback
    def stop(self):
        if self._task is not None and not self._task.done():
            self._task.cancel()
