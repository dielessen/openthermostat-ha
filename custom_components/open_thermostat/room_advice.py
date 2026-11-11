"""Heat along or a fixed temperature: advice per room, and a house model per room (1.4.2, plan 3.14; review
R142-ENERGY-DHW G6). Home Assistant only: no firmware, no NVS, no E32 flash.

The heating advice sensor (heating_advice.py) takes a five-minute sample; ``room_sample`` adds every room's
temperature, state, heat demand and valve opening to it, and ``RoomRecords`` folds each sample into a small record per
room and day, kept ROOM_DAYS_KEPT days in the sensor's restore state:

- ``f``: samples on Heat along only while the boiler heated (heat-along hours), ``fc`` the ones at an outdoor
  temperature of COLD_OUTDOOR_C or colder, ``b`` their room temperatures as a histogram (BIN_PER_C bins per °C), ``ts``
  their sum (the mean), ``os``/``on`` the outdoor temperature's sum and count;
- ``ac``: samples on On at COLD_OUTDOOR_C or colder, ``solo`` samples on On in which this room was the only one
  asking for heat (the reverse case);
- ``c`` and ``h``: the sums of a least-squares fit of the room's first-order model
  ``dT/dt = (T_out - T) / tau + g * h`` over stretches without heat (the boiler not heating for at least
  COOL_SETTLE_S, or the room's valves closed) and with heat (the boiler heating for at least HEAT_SETTLE_S and the
  room getting it). ``tau`` (h) is how fast the room cools towards outside, ``g`` (K/h) how fast its heating warms it.

``advise`` turns the records into the advice of plan 3.14 (the break-even ``T0`` = the 20th percentile of the
achieved temperature while heating along, normalised to the typical outdoor temperature; the extra heat for a target
above it with the house's heat loss shared over the heated rooms by 1/tau; gas through the boiler efficiency and the
gas calibration), ``fit`` gives the model. ``room_live`` is the room model's read value for the settings panel
(``live.advice`` and ``live.model``), ``learning_lines`` the Learning view's line per room, and ``adopt_advice`` the
panel action that writes the advised temperature as the room's fixed temperature with the routine flag (CONTRACT-1.4.2
§1), so the E32's self-tuning does not restart.

Nothing here changes the control: the E32's own warm-up learning stays the control; this model only informs the
advice and the Learning view.
"""
from __future__ import annotations

import math
from datetime import date

SAMPLE_S = 300
GAP_S = 2 * SAMPLE_S + 60          # two samples further apart are not one stretch
ROOM_DAYS_KEPT = 21                # days of room records (14 qualifying days among them)
SAMPLE_H = SAMPLE_S / 3600

# -- the advice (plan 3.14) ------------------------------------------------------------------------------------------
ADVICE_DAYS = 14                   # days needed with ...
DAY_MIN_SAMPLES = 72               # ... at least 6 h of heating along (On: of being on) ...
COLD_OUTDOOR_C = 15.0              # ... at this outdoor temperature or colder
PERCENTILE = 0.2                   # the break-even: 8 of 10 heat-along hours were at least this warm
BIN_PER_C = 4                      # histogram bins of 0.25 °C
ROOM_C = (0.0, 40.0)               # a room temperature outside this is no reading
NORMALISE_MIN_DAYS = 5             # the outdoor normalisation needs this many days ...
NORMALISE_MIN_SPREAD_C = 3.0       # ... spread over this many degrees outside
NORMALISE_SLOPE = (0.0, 1.0)       # K of room per K outside, clamped
SOLO_LITTLE_H = 0.5                # an On room asking alone at most this long a day: Heat along only changes little
FREE_MARGIN_C = 0.25               # a fixed temperature this close above T0 is still free
RETURN_DEFAULT_C = 45.0            # the return temperature for the efficiency without a reading
GAS_KWH_PER_M3 = 9.77              # the E32's default calorific value (heating_advice.GAS_KWH_PER_M3)

# -- the room model ------------------------------------------------------------------------------------------------
COOL_SETTLE_S = 1800               # the radiators cool down first: cooling counts from 30 min after the heat stopped
HEAT_SETTLE_S = 900                # and heating from 15 min after it started
MAX_RATE_K_PER_H = 4.0             # faster changes are a window, a shower or a sensor jump
VALVE_OPEN_PCT = 50
VALVE_CLOSED_PCT = 5
DEMAND_MARGIN_C = 0.2              # a heat-along room this far below its target gets heat
MODEL_MIN_COOL_H = 12              # too little data below these hours
MODEL_MIN_HEAT_H = 6
MODEL_LEARNED_COOL_H = 48          # learned (not rough) from these hours on ...
MODEL_LEARNED_HEAT_H = 24
MODEL_LEARNED_REL_SE = 0.15        # ... with both figures known within 15 %
MODEL_MIN_SPREAD_C = 3.0           # the room must be this much warmer than outside on average to see it cool
TAU_H = (2.0, 2000.0)
SENTENCE_OUTDOOR_C = 5.0           # the plain sentence: at 5 °C outside

STATES = ("active", "follow", "inactive")
BAD_STATUS = ("window_open", "window_pending", "stale", "lost", "fallback")
REASONS = ("too_little_data", "valve_sensor")
QUALITIES = ("learned", "rough", "too_little_data", "valve_sensor")
# A radiator valve by its device's words (besides the models the E32 knows, e32_valves.guess_model).
VALVE_WORDS = ("trv", "radiator valve", "radiator thermostat", "thermostatic radiator", "heizkörperthermostat",
               "radiatorkraan", "thermostaatkraan", "radiatorthermostaat")


def _num(value, low, high):
    if type(value) not in (int, float) or not math.isfinite(value):
        return None
    return float(value) if low <= value <= high else None


# -- samples -------------------------------------------------------------------------------------------------------


def room_sample(hub):
    """{room id: {"s", "d", "T"?, "sp"?, "v"?, "nv"}} of the hub's rooms now: state, heat demand, temperature (left out
    while a window is open or the room has no fresh reading), target, mean valve opening and number of valves."""
    rooms = {}
    valves = getattr(hub, "valves", None) or {}
    for room_id, room in (getattr(hub, "rooms", None) or {}).items():
        state = room.get("state") if room.get("state") in STATES else None
        if state is None:
            continue
        record = {"s": state, "d": room.get("demand") is True}
        temperature = _num(room.get("temperature"), *ROOM_C)
        if temperature is not None and room.get("status") not in BAD_STATUS:
            record["T"] = round(temperature, 2)
        target = _num(room.get("setpoint"), *ROOM_C)
        if target is not None:
            record["sp"] = target
        own = (valves.get(room_id) or {}).get("valves") if type(valves.get(room_id)) is dict else None
        own = own if type(own) is list else []
        record["nv"] = len(own)
        positions = [p for p in (_num(v.get("position_pct"), 0, 100) for v in own if type(v) is dict) if p is not None]
        if positions:
            record["v"] = round(sum(positions) / len(positions), 1)
        rooms[room_id] = record
    return rooms


def boiler_heating(sample):
    """True while the boiler heats the rooms (not hot water), False while it does not, None when unknown: the boiler's
    own flag, else the E32's request."""
    if sample.get("ha") is not None:
        return sample["ha"] is True and sample.get("da") is not True
    request = sample.get("re")
    return None if request is None else request >= 20


def room_input(sample, room, heating):
    """1 when the room gets heat, 0 when it does not, None when that is not clear."""
    if heating is None:
        return None
    if heating is False:
        return 0
    if room["s"] == "inactive":
        return None
    opening = room.get("v")
    if opening is not None:
        return 1 if opening >= VALVE_OPEN_PCT else 0 if opening <= VALVE_CLOSED_PCT else None
    if not room.get("nv"):
        return 1  # no valves: the radiators get the water whenever the boiler heats
    if room.get("d"):
        return 1
    if room["s"] == "follow" and room.get("sp") is not None and room.get("T") is not None \
            and room["T"] < room["sp"] - DEMAND_MARGIN_C:
        return 1
    return None


# -- the records -----------------------------------------------------------------------------------------------------

COOL_SUMS = 5   # n, Sxx, Sxy, Syy, ST
HEAT_SUMS = 7   # n, Sx, Sy, Sxx, Sxy, Syy, ST
COUNTS = ("f", "fc", "on", "ac", "solo")
SUMS = ("ts", "os")


def new_record():
    return {"f": 0, "fc": 0, "b": {}, "ts": 0.0, "os": 0.0, "on": 0, "ac": 0, "solo": 0,
            "c": [0.0] * COOL_SUMS, "h": [0.0] * HEAT_SUMS}


class RoomRecords:
    """Per day and room the records of the module docstring; the phase of each room (heated or not, since when) lives
    in memory only: after a restart the settle times start again."""

    def __init__(self):
        self.days = {}
        self._previous = None
        self._phase = {}

    def add(self, sample, day):
        rooms = sample.get("rm")
        if type(rooms) is not dict:
            self._previous = None
            return
        records = self.days.setdefault(day.isoformat(), {})
        heating = boiler_heating(sample)
        outdoor = sample.get("o")
        asking = [room_id for room_id, room in rooms.items() if room.get("d") and room["s"] != "inactive"]
        previous = self._previous if self._previous is not None and 0 < sample["t"] - self._previous["t"] <= GAP_S else None
        for room_id, room in rooms.items():
            record = records.setdefault(room_id, new_record())
            temperature = room.get("T")
            cold = outdoor is not None and outdoor <= COLD_OUTDOOR_C
            if room["s"] == "follow" and heating is True and temperature is not None:
                record["f"] += 1
                key = str(round(temperature * BIN_PER_C))
                record["b"][key] = record["b"].get(key, 0) + 1
                record["ts"] += temperature
                if outdoor is not None:
                    record["os"] += outdoor
                    record["on"] += 1
                    record["fc"] += cold
            if room["s"] == "active":
                record["ac"] += cold and temperature is not None
                record["solo"] += asking == [room_id]
            self._model(room_id, room, record, sample, previous, heating, outdoor)
        self._previous = sample
        for key in sorted(self.days)[:-ROOM_DAYS_KEPT]:
            del self.days[key]

    def _model(self, room_id, room, record, sample, previous, heating, outdoor):
        now = sample["t"]
        given = room_input(sample, room, heating)
        phase = self._phase.get(room_id)
        if previous is None or phase is None or phase[0] != given:
            self._phase[room_id] = (given, now)
            return
        before = (previous.get("rm") or {}).get(room_id)
        start = phase[1]
        settle = COOL_SETTLE_S if given == 0 else HEAT_SETTLE_S
        if (given is None or before is None or before.get("T") is None or room.get("T") is None
                or previous.get("o") is None or outdoor is None or previous["t"] - start < settle):
            return
        hours = (now - previous["t"]) / 3600
        y = (room["T"] - before["T"]) / hours
        if abs(y) > MAX_RATE_K_PER_H:
            return
        mean_t = (room["T"] + before["T"]) / 2
        x = (outdoor + previous["o"]) / 2 - mean_t
        if given == 0:
            sums = record["c"]
            for k, value in enumerate((1, x * x, x * y, y * y, mean_t)):
                sums[k] += value
        else:
            sums = record["h"]
            for k, value in enumerate((1, x, y, x * x, x * y, y * y, mean_t)):
                sums[k] += value

    # -- restore state ---------------------------------------------------------------------------------------------

    def export(self):
        return {day: {room_id: _rounded(record) for room_id, record in rooms.items()} for day, rooms in self.days.items()}

    def restore(self, data):
        for day, rooms in (data.items() if type(data) is dict else ()):
            try:
                date.fromisoformat(day)
            except (TypeError, ValueError):
                continue
            if type(rooms) is not dict:
                continue
            kept = {room_id: record for room_id, record in ((r, _valid(v)) for r, v in rooms.items())
                    if type(room_id) is str and record is not None}
            if kept:
                self.days[day] = kept
        for key in sorted(self.days)[:-ROOM_DAYS_KEPT]:
            del self.days[key]


def _rounded(record):
    out = {key: record[key] for key in COUNTS}
    out.update({key: round(record[key], 2) for key in SUMS})
    out["b"] = dict(record["b"])
    out["c"] = [round(v, 3) for v in record["c"]]
    out["h"] = [round(v, 3) for v in record["h"]]
    return out


def _valid(value):
    """A restored record, or None when it is not one this version wrote."""
    if type(value) is not dict:
        return None
    try:
        record = {key: int(value[key]) for key in COUNTS if type(value[key]) is int and value[key] >= 0}
        record.update({key: float(value[key]) for key in SUMS if type(value[key]) in (int, float)})
        bins = value["b"]
        sums = {key: value[key] for key in ("c", "h")}
    except (KeyError, TypeError):
        return None
    if (len(record) != len(COUNTS) + len(SUMS) or type(bins) is not dict
            or not all(type(k) is str and k.lstrip("-").isdigit() and type(v) is int and v > 0 for k, v in bins.items())
            or type(sums["c"]) is not list or len(sums["c"]) != COOL_SUMS
            or type(sums["h"]) is not list or len(sums["h"]) != HEAT_SUMS
            or not all(type(v) in (int, float) and math.isfinite(v) for v in sums["c"] + sums["h"])):
        return None
    record["b"] = dict(bins)
    record["c"] = [float(v) for v in sums["c"]]
    record["h"] = [float(v) for v in sums["h"]]
    return record


def _window(days, today):
    """The records of the last ROOM_DAYS_KEPT days up to today, oldest first."""
    result = []
    for key in sorted(days):
        try:
            age = (today - date.fromisoformat(key)).days
        except (TypeError, ValueError):
            continue
        if 0 <= age < ROOM_DAYS_KEPT:
            result.append((key, days[key]))
    return result


# -- the model ---------------------------------------------------------------------------------------------------------


def fit(days, room_id, today):
    """The room's model: {tau_h, warm_rate_k_per_h, quality, hours_used, residual_k_per_h, mean_c}.

    tau from the stretches without heat (least squares through the origin of dT/dt on T_out - T), g from the heated
    stretches with that tau. ``quality``: learned, rough, or too_little_data (also when the fit makes no physical
    sense: a room that warms up without heat, as with strong sun)."""
    cool, heat = [0.0] * COOL_SUMS, [0.0] * HEAT_SUMS
    for _, rooms in _window(days, today):
        record = rooms.get(room_id)
        if record is None:
            continue
        cool = [a + b for a, b in zip(cool, record["c"])]
        heat = [a + b for a, b in zip(heat, record["h"])]
    n_cool, n_heat = cool[0], heat[0]
    cool_h, heat_h = n_cool * SAMPLE_H, n_heat * SAMPLE_H
    result = {"tau_h": None, "warm_rate_k_per_h": None, "quality": "too_little_data",
              "hours_used": round(cool_h + heat_h, 1), "residual_k_per_h": None, "mean_c": None}
    if cool_h < MODEL_MIN_COOL_H or heat_h < MODEL_MIN_HEAT_H:
        return result
    _, sxx, sxy, syy, st_cool = cool
    if sxx <= 0 or math.sqrt(sxx / n_cool) < MODEL_MIN_SPREAD_C:
        return result
    a = sxy / sxx
    if a <= 0 or not TAU_H[0] <= 1 / a <= TAU_H[1]:
        return result
    _, sx, sy, hxx, hxy, hyy, st_heat = heat
    g = (sy - a * sx) / n_heat
    if g <= 0:
        return result
    ssr_cool = max(0.0, syy - a * sxy)
    ssr_heat = max(0.0, hyy + a * a * hxx + n_heat * g * g - 2 * a * hxy - 2 * g * sy + 2 * a * g * sx)
    se_a = math.sqrt(ssr_cool / max(1.0, n_cool - 1) / sxx)
    se_g = math.sqrt(ssr_heat / max(1.0, n_heat - 1) / n_heat)
    learned = (cool_h >= MODEL_LEARNED_COOL_H and heat_h >= MODEL_LEARNED_HEAT_H
               and se_a / a <= MODEL_LEARNED_REL_SE and se_g / g <= MODEL_LEARNED_REL_SE)
    result.update(tau_h=round(1 / a, 1), warm_rate_k_per_h=round(g, 2), quality="learned" if learned else "rough",
                  residual_k_per_h=round(math.sqrt((ssr_cool + ssr_heat) / (n_cool + n_heat)), 2),
                  mean_c=round((st_cool + st_heat) / (n_cool + n_heat), 1))
    return result


# -- the advice --------------------------------------------------------------------------------------------------------


def efficiency(return_c):
    """FlowLearner::efficiency: 97.5 % at a return of 35 °C or cooler, 0.43 % less per K up to 55 °C."""
    return 0.975 - min(max(return_c - 35.0, 0.0), 20.0) * 0.0043


def _qualifying(days, room_id, today, key):
    return [(day, rooms[room_id]) for day, rooms in _window(days, today)
            if room_id in rooms and rooms[room_id][key] >= DAY_MIN_SAMPLES][-ADVICE_DAYS:]


def _median(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2


def normalised(records):
    """([(room °C, samples)], typical outdoor °C or None, slope): the heat-along temperatures of the days, each day
    shifted to the typical outdoor temperature (the median of the days) by a straight-line fit of the day's mean room
    temperature on its mean outdoor temperature (no shift with too few days or too little spread)."""
    pairs = [(rec["ts"] / rec["f"], rec["os"] / rec["on"]) for _, rec in records if rec["f"] and rec["on"]]
    outdoors = [o for _, o in pairs]
    typical = _median(outdoors) if outdoors else None
    slope = 0.0
    if len(pairs) >= NORMALISE_MIN_DAYS and max(outdoors) - min(outdoors) >= NORMALISE_MIN_SPREAD_C:
        mean_o = sum(outdoors) / len(pairs)
        mean_t = sum(t for t, _ in pairs) / len(pairs)
        sxx = sum((o - mean_o) ** 2 for o in outdoors)
        slope = min(max(sum((o - mean_o) * (t - mean_t) for t, o in pairs) / sxx, NORMALISE_SLOPE[0]),
                    NORMALISE_SLOPE[1])
    temperatures = []
    for _, rec in records:
        shift = slope * (typical - rec["os"] / rec["on"]) if typical is not None and rec["on"] else 0.0
        temperatures += [(int(key) / BIN_PER_C + shift, count) for key, count in rec["b"].items()]
    return temperatures, typical, slope


def percentile(temperatures, share):
    total = sum(count for _, count in temperatures)
    seen = 0
    for value, count in sorted(temperatures):
        seen += count
        if seen >= share * total:
            return value
    return None


def degree_hours(temperatures, target):
    """Σ max(0, target − T) over the samples, in K·h."""
    return sum(count * SAMPLE_H * max(0.0, target - value) for value, count in temperatures)


def shares(heated, taus):
    """{room: share of the house's heat loss}: by 1/tau where tau is known (a room that cools faster loses more),
    the mean of the known ones for the others; equal shares when none is known."""
    weights = {room: 1 / taus[room] for room in heated if taus.get(room)}
    fill = sum(weights.values()) / len(weights) if weights else 1.0
    weights = {room: weights.get(room, fill) for room in heated}
    total = sum(weights.values())
    return {room: weight / total for room, weight in weights.items()} if total else {}


def advise(days, room_id, today, ctx):
    """The values of a room's advice (pure), or None for a room that is Off or unknown.

    ctx: state ("active" | "follow" | "inactive"), program (bool), fallback_c, minimum_c, maximum_c, valve_sensor
    (bool), house_learned (bool), ua_kw_per_k, heated (room ids on On or Heat along only), taus ({room: tau_h}),
    efficiency, kwh_per_m3, factor (the gas calibration with a meter, else None)."""
    state = ctx.get("state")
    if state == "follow":
        if ctx.get("valve_sensor"):
            return {"kind": "follow", "reason": "valve_sensor", "rough": True}
        records = _qualifying(days, room_id, today, "fc")
        if len(records) < ADVICE_DAYS:
            return {"kind": "follow", "reason": "too_little_data", "part": "days", "days": len(records), "rough": False}
        if not ctx.get("house_learned") or not ctx.get("ua_kw_per_k"):
            return {"kind": "follow", "reason": "too_little_data", "part": "house", "days": len(records),
                    "rough": False}
        temperatures, typical, slope = normalised(records)
        t0 = percentile(temperatures, PERCENTILE)
        if t0 is None:
            return {"kind": "follow", "reason": "too_little_data", "part": "days", "days": 0, "rough": False}
        heated = list(dict.fromkeys([*ctx.get("heated", []), room_id]))
        taus = ctx.get("taus") or {}
        share = shares(heated, taus)[room_id]
        ua_room = ctx["ua_kw_per_k"] * share
        n_days = len(records)

        def kwh(target):  # extra heat a day for a target above T0
            return ua_room * (degree_hours(temperatures, target) - degree_hours(temperatures, t0)) / n_days

        def m3(energy):
            gas = energy / ctx.get("efficiency", efficiency(RETURN_DEFAULT_C)) / ctx.get("kwh_per_m3", GAS_KWH_PER_M3)
            return gas * ctx["factor"] if ctx.get("factor") else gas
        free = math.floor(t0 * 2) / 2
        low, high = ctx.get("minimum_c"), ctx.get("maximum_c")
        if low is not None:
            free = max(free, low)
        if high is not None:
            free = min(free, high)
        per_kwh = kwh(t0 + 1)
        values = {"kind": "follow", "reason": None, "rough": not taus.get(room_id), "t0": free, "days": n_days,
                  "kwh": round(per_kwh, 2), "m3": round(m3(per_kwh), 2), "typical_c": typical, "slope": slope,
                  "ua": ctx["ua_kw_per_k"], "n": len(heated), "share": share,
                  "efficiency": ctx.get("efficiency", efficiency(RETURN_DEFAULT_C)), "target": None,
                  "program": bool(ctx.get("program")), "now": None, "now_m3": None}
        now = ctx.get("fallback_c")
        if not values["program"] and now is not None:
            values["now"] = now
            if now > free + FREE_MARGIN_C:
                values["now_m3"] = round(m3(kwh(now)), 2)
                values["target"] = free
        return values
    if state == "active":
        records = _qualifying(days, room_id, today, "ac")
        if len(records) < ADVICE_DAYS:
            return {"kind": "active", "reason": "too_little_data", "part": "days", "days": len(records), "rough": False}
        solo = sum(rec["solo"] for _, rec in records) * SAMPLE_H / len(records)
        return {"kind": "active", "reason": None, "rough": False, "solo_h": round(solo, 1), "days": len(records),
                "little": solo <= SOLO_LITTLE_H, "target": None}
    return None


# -- texts (English and Dutch; the room screen and the Learning view) --------------------------------------------------

TEXT = {
    "en": {
        "follow": "{room} heats along up to about {t0} °C for free. Each degree above that costs about {m3} m³ of gas "
                  "a day ({kwh} kWh).",
        "follow+costly": " Heat along up to is now {now} °C: about {now_m3} m³ of gas a day extra.",
        "follow+free": " Heat along up to is now {now} °C: that costs nothing extra.",
        "follow+program": " This room follows its week program: keep its temperatures at or below {t0} °C to heat "
                          "along for free.",
        "follow.days": "Too little data yet. After 14 days with at least 6 hours of heating along at 15 °C or colder "
                       "outside, this says up to which temperature {room} heats along for free. So far {days} of the "
                       "14 days.",
        "follow.house": "Too little data yet: the E32 is still learning how much heat the house loses.",
        "follow.valve_sensor": "No figure: the temperature of {room} comes only from its radiator valve's own sensor, "
                               "which reads too high next to a warm radiator. With a separate thermometer in the room "
                               "this says up to which temperature it heats along for free.",
        "active": "{room} was the only room asking for heat for about {solo} h a day (last {days} days).",
        "active+much": " In those hours the boiler heats for this room alone; on Heat along only it would get heat "
                       "only while another room asks for it.",
        "active+little": " Heat along only would change little: it hardly ever asks for heat on its own.",
        "active.days": "Too little data yet. After 14 days with at least 6 hours at 15 °C or colder outside, this says "
                       "how often {room} asks for heat on its own. So far {days} of the 14 days.",
        "more.follow": "How this is worked out: the free temperature is the temperature {room} reached in 8 of 10 "
                       "hours while it heated along and the boiler heated, over {days} days, corrected to a typical "
                       "outdoor temperature of {typical} °C. The extra gas per degree is the house's heat loss "
                       "({ua} kW per °C, learned by the E32) {share}, times the hours it heated along, divided by the "
                       "boiler's efficiency ({efficiency} %){gas}. Assumptions: the room sizes are unknown, so the "
                       "shares are estimates; part of the heat that goes to the neighbouring rooms comes back, so the "
                       "real cost is lower (this is an upper limit); and it assumes a steady state.",
        "more.share_tau": "shared over the {n} heated rooms by how fast each one cools down (this room: {pct} %)",
        "more.share_equal": "shared equally over the {n} heated rooms (how fast this room cools down is not known "
                            "yet, so the figure is rough)",
        "more.gas_meter": ", corrected with your gas meter",
        "more.no_gas_meter": "",
        "more.valve_sensor": "A radiator valve measures next to the radiator: while it is warm the valve reads more "
                             "than the room is. Advice from that temperature would say a room heats along for free "
                             "when it does not. Add a separate thermometer as the room's first temperature source.",
        "more.days": "The advice needs 14 days with at least 6 hours of heating along at 15 °C or colder outside, and "
                     "the E32's learned heat loss of the house. Counting started when this version was installed.",
        "more.active": "Counted over the last {days} days with at least 6 hours at 15 °C or colder outside: the hours "
                       "in which {room} was the only room asking for heat. On Heat along only a room never makes the "
                       "boiler heat on its own; its valves open while other rooms ask for heat.",
        "model": "At 5 °C outside {room} cools down by about {cool} °C an hour and warms up by about {warm} °C an hour "
                 "with the {emitter}.",
        "model.level": "At 5 °C outside {room} cools down by about {cool} °C an hour; with the {emitter} on it stays "
                       "about level.",
        "model+rough": " Rough: from {hours} hours of data.",
        "model.too_little_data": "Too little data yet to say how fast {room} cools down and warms up ({hours} of "
                                 "the {need} hours).",
        "model.valve_sensor": "No model: the temperature of {room} comes only from its radiator valve's own sensor.",
        "emitter.radiator": "radiators", "emitter.floor": "floor heating", "emitter.other": "heating",
    },
    "nl": {
        "follow": "{room} verwarmt gratis mee tot ongeveer {t0} °C. Elke graad daarboven kost ongeveer {m3} m³ gas "
                  "per dag ({kwh} kWh).",
        "follow+costly": " Meeverwarmen tot staat nu op {now} °C: ongeveer {now_m3} m³ gas per dag extra.",
        "follow+free": " Meeverwarmen tot staat nu op {now} °C: dat kost niets extra.",
        "follow+program": " Deze ruimte volgt haar weekprogramma: houd de temperaturen daarin op of onder {t0} °C om "
                          "gratis mee te verwarmen.",
        "follow.days": "Nog te weinig gegevens. Na 14 dagen met minstens 6 uur meeverwarmen bij 15 °C of kouder buiten "
                       "staat hier tot welke temperatuur {room} gratis meeverwarmt. Tot nu toe {days} van de 14 "
                       "dagen.",
        "follow.house": "Nog te weinig gegevens: de E32 leert nog hoeveel warmte het huis verliest.",
        "follow.valve_sensor": "Geen cijfer: de temperatuur van {room} komt alleen van de eigen voeler van de "
                               "radiatorkraan, en die meet te hoog naast een warme radiator. Met een losse thermometer "
                               "in de ruimte staat hier tot welke temperatuur ze gratis meeverwarmt.",
        "active": "{room} was ongeveer {solo} uur per dag de enige ruimte die warmte vroeg (laatste {days} dagen).",
        "active+much": " In die uren verwarmt de ketel alleen voor deze ruimte; op Alleen meeverwarmen krijgt ze alleen "
                       "warmte als een andere ruimte warmte vraagt.",
        "active+little": " Alleen meeverwarmen zou weinig veranderen: ze vraagt bijna nooit als enige om warmte.",
        "active.days": "Nog te weinig gegevens. Na 14 dagen met minstens 6 uur bij 15 °C of kouder buiten staat hier "
                       "hoe vaak {room} als enige om warmte vraagt. Tot nu toe {days} van de 14 dagen.",
        "more.follow": "Zo is het berekend: de gratis temperatuur is de temperatuur die {room} in 8 van de 10 uur "
                       "haalde terwijl ze meeverwarmde en de ketel verwarmde, over {days} dagen, omgerekend naar een "
                       "gewone buitentemperatuur van {typical} °C. Het extra gas per graad is het warmteverlies van het "
                       "huis ({ua} kW per °C, geleerd door de E32) {share}, maal de uren dat ze meeverwarmde, gedeeld "
                       "door het rendement van de ketel ({efficiency} %){gas}. Aannames: de grootte van de ruimtes is "
                       "onbekend, dus de aandelen zijn schattingen; een deel van de warmte die naar de buurruimtes gaat "
                       "komt terug, dus het echte verbruik is lager (dit is een bovengrens); en het gaat uit van een "
                       "stabiele toestand.",
        "more.share_tau": "verdeeld over de {n} verwarmde ruimtes naar hoe snel elke ruimte afkoelt (deze ruimte: "
                          "{pct} %)",
        "more.share_equal": "gelijk verdeeld over de {n} verwarmde ruimtes (hoe snel deze ruimte afkoelt is nog niet "
                            "bekend, dus het cijfer is ruw)",
        "more.gas_meter": ", gecorrigeerd met je gasmeter",
        "more.no_gas_meter": "",
        "more.valve_sensor": "Een radiatorkraan meet naast de radiator: als die warm is, meet de kraan meer dan het in "
                             "de ruimte is. Een advies uit die temperatuur zou zeggen dat een ruimte gratis meeverwarmt "
                             "terwijl dat niet zo is. Voeg een losse thermometer toe als eerste temperatuurbron van de "
                             "ruimte.",
        "more.days": "Het advies heeft 14 dagen nodig met minstens 6 uur meeverwarmen bij 15 °C of kouder buiten, en "
                     "het door de E32 geleerde warmteverlies van het huis. Het tellen begon bij de installatie van deze "
                     "versie.",
        "more.active": "Geteld over de laatste {days} dagen met minstens 6 uur bij 15 °C of kouder buiten: de uren "
                       "waarin {room} de enige ruimte was die warmte vroeg. Op Alleen meeverwarmen laat een ruimte de "
                       "ketel nooit alleen voor zichzelf verwarmen; haar kranen gaan open als andere ruimtes warmte "
                       "vragen.",
        "model": "Bij 5 °C buiten koelt {room} ongeveer {cool} °C per uur af en warmt met de {emitter} ongeveer {warm} °C "
                 "per uur op.",
        "model.level": "Bij 5 °C buiten koelt {room} ongeveer {cool} °C per uur af; met de {emitter} aan blijft ze "
                       "ongeveer gelijk.",
        "model+rough": " Ruw: uit {hours} uur aan gegevens.",
        "model.too_little_data": "Nog te weinig gegevens om te zeggen hoe snel {room} afkoelt en opwarmt ({hours} van "
                                 "de {need} uur).",
        "model.valve_sensor": "Geen model: de temperatuur van {room} komt alleen van de eigen voeler van de "
                              "radiatorkraan.",
        "emitter.radiator": "radiatoren", "emitter.floor": "vloerverwarming", "emitter.other": "verwarming",
    },
}
LANGUAGES = tuple(TEXT)


def fmt(value, lang, digits=1):
    """A figure for a sentence: at most ``digits`` decimals, a decimal comma in Dutch."""
    if value is None:
        return "?"
    value = round(float(value), digits)
    text = f"{value:.{digits}f}".rstrip("0").rstrip(".") if digits else str(int(round(value)))
    return text.replace(".", ",") if lang == "nl" else text


def advice_text(values, name, lang):
    """(sentence, more) of advise()'s values in a language."""
    t = TEXT[lang]
    kind, reason = values["kind"], values.get("reason")
    if reason == "valve_sensor":
        return t[kind + ".valve_sensor"].format(room=name), t["more.valve_sensor"]
    if reason == "too_little_data":
        part = values.get("part", "days")
        text = t.get(f"{kind}.{part}", t[kind + ".days"])
        more = t["more.days"] if kind == "follow" else t["more.active"].format(room=name, days=values.get("days", 0))
        return text.format(room=name, days=values.get("days", 0)), more
    if kind == "active":
        text = t["active"].format(room=name, solo=fmt(values["solo_h"], lang), days=values["days"])
        text += t["active+little" if values["little"] else "active+much"]
        return text, t["more.active"].format(room=name, days=values["days"])
    figures = {"room": name, "t0": fmt(values["t0"], lang), "m3": fmt(values["m3"], lang, 2),
               "kwh": fmt(values["kwh"], lang, 1)}
    text = t["follow"].format(**figures)
    if values["program"]:
        text += t["follow+program"].format(**figures)
    elif values["now"] is not None:
        key = "follow+costly" if values["now_m3"] is not None else "follow+free"
        text += t[key].format(now=fmt(values["now"], lang), now_m3=fmt(values["now_m3"], lang, 2))
    share = (t["more.share_equal"] if values["rough"] else t["more.share_tau"]).format(
        n=values["n"], pct=fmt(values["share"] * 100, lang, 0))
    more = t["more.follow"].format(
        room=name, days=values["days"], typical=fmt(values["typical_c"], lang), ua=fmt(values["ua"], lang, 2),
        share=share, efficiency=fmt(values["efficiency"] * 100, lang, 0),
        gas=t["more.gas_meter" if values.get("factor") else "more.no_gas_meter"])
    return text, more


def model_rates(model):
    """(cools, warms): the model sentence's figures, °C an hour at 5 °C outside; None while the model has none (too
    little data, only the valve's own sensor). 1.4.3: the Learning view's room card shows the cooling as a figure."""
    if not model or model.get("quality") not in ("learned", "rough") or not model.get("tau_h"):
        return None
    reference = model["mean_c"] if model.get("mean_c") is not None else 20.0
    cool = max(0.0, (reference - SENTENCE_OUTDOOR_C) / model["tau_h"])
    return cool, model["warm_rate_k_per_h"] - cool


def model_text(model, name, emitter, lang):
    t = TEXT[lang]
    quality = model["quality"]
    if quality == "valve_sensor":
        return t["model.valve_sensor"].format(room=name)
    if quality == "too_little_data":
        return t["model.too_little_data"].format(room=name, hours=fmt(model["hours_used"], lang, 0),
                                                 need=MODEL_MIN_COOL_H + MODEL_MIN_HEAT_H)
    cool, warm = model_rates(model)
    word = t["emitter." + (emitter if emitter in ("radiator", "floor") else "other")]
    if warm < 0.1:
        text = t["model.level"].format(room=name, cool=fmt(cool, lang), emitter=word)
    else:
        text = t["model"].format(room=name, cool=fmt(cool, lang), warm=fmt(warm, lang), emitter=word)
    if quality == "rough":
        text += t["model+rough"].format(hours=fmt(model["hours_used"], lang, 0))
    return text


# -- Home Assistant: the inputs, the room model's read value, the Learning view ----------------------------------------


def _valve_device(device):
    from .e32_valves import guess_model
    text = " ".join(str(v or "") for v in (device.manufacturer, device.model, getattr(device, "model_id", None),
                                           device.name)).lower()
    return guess_model(text) is not None or any(word in text for word in VALVE_WORDS)


def valve_sensor_only(hass, room, valve_entities=()):
    """True when every temperature source of the room is a radiator valve's own sensor: a Home Assistant entity that
    is one of the radiator valves, or that sits on a radiator valve's device (a Zigbee2MQTT ``local_temperature``
    sensor of the valve, a valve's climate entity). A Bluetooth thermometer of the E32 is never a valve."""
    sources = [s for s in (room or {}).get("sources") or [] if type(s) is dict]
    if not sources or any(s.get("type") != "ha" or type(s.get("id")) is not str for s in sources):
        return False
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er
    entities, devices = er.async_get(hass), dr.async_get(hass)
    valve_devices = {e.device_id for e in (entities.async_get(v) for v in valve_entities) if e is not None and e.device_id}
    for source in sources:
        if source["id"] in valve_entities:
            continue
        registered = entities.async_get(source["id"])
        device = devices.async_get(registered.device_id) if registered is not None and registered.device_id else None
        if device is None or not (device.id in valve_devices or _valve_device(device)):
            return False
    return True


def _plan_rooms(hub):
    plan = getattr(getattr(hub, "plan", None), "plan", None)
    rooms = plan.get("rooms") if type(plan) is dict else None
    return [room for room in rooms if type(room) is dict and type(room.get("id")) is str] if type(rooms) is list else []


def _has_program(room):
    schedule = room.get("schedule")
    return (type(schedule) is list and any(day for day in schedule)) or bool(room.get("week"))


def _centi(room, key):
    value = room.get(key)
    return value / 100 if type(value) is int else None


def _valve_entities(hub):
    from .e32_valves import HA_MODEL
    return {v["name"] for room in (getattr(hub, "valves", None) or {}).values() if type(room) is dict
            for v in room.get("valves") or [] if type(v) is dict and v.get("model") == HA_MODEL
            and type(v.get("name")) is str}


def house_model(hub):
    """(learned, ua kW/K or None): the E32's house model (fw/telemetry/insight ``house``)."""
    from .insight import insight_status
    house = (insight_status(getattr(hub, "summary", None)) or {}).get("house")
    if type(house) is not dict:
        return False, None
    return house.get("state") == "learned", _num(house.get("ua_kw_per_k"), 0.001, 5)


def gas_context(hass, entry, hub, samples):
    """efficiency (from the median return while heating, else RETURN_DEFAULT_C), kWh per m³, and the gas calibration
    factor once the E32 calibrated against a meter."""
    from .e32_flow import gas_calibration
    from .energy_input import energy_options, kwh_per_m3
    returns = sorted(s["rn"] for s in samples or () if s.get("rn") is not None and s.get("ha") is True
                     and s.get("da") is not True)
    measured = returns[len(returns) // 2] if returns else RETURN_DEFAULT_C
    gas = gas_calibration(hub) or {}
    factor = _num(gas.get("factor"), 0.1, 10) if gas.get("status") == "calibrated" else None
    try:
        per_m3 = kwh_per_m3(energy_options(entry))
    except Exception:  # noqa: BLE001 - an entry without energy options: the default
        per_m3 = GAS_KWH_PER_M3
    return {"efficiency": efficiency(measured), "kwh_per_m3": per_m3 or GAS_KWH_PER_M3, "factor": factor}


class Inputs:
    """Everything the advice of all rooms needs, read once: the plan rooms, the fits, the house model, the gas."""

    def __init__(self, hass, entry, hub, history, today):
        self.hass, self.hub, self.today = hass, hub, today
        self.days = history.rooms.days if history is not None else {}
        self.rooms = {room["id"]: room for room in _plan_rooms(hub)}
        valves = _valve_entities(hub)
        self.valve_sensor = {room_id: valve_sensor_only(hass, room, valves) for room_id, room in self.rooms.items()}
        self.models = {}
        for room_id in self.rooms:
            model = fit(self.days, room_id, today)
            if self.valve_sensor[room_id]:
                model = {**model, "tau_h": None, "warm_rate_k_per_h": None, "quality": "valve_sensor",
                         "residual_k_per_h": None}
            self.models[room_id] = model
        self.learned, self.ua = house_model(hub)
        self.gas = gas_context(hass, entry, hub, history.samples if history is not None else ())
        self.heated = [room_id for room_id, room in self.rooms.items() if room.get("state") in ("active", "follow")]
        self.taus = {room_id: model["tau_h"] for room_id, model in self.models.items() if model.get("tau_h")}

    def name(self, room_id):
        from .heating_link import label
        room = self.rooms.get(room_id) or (getattr(self.hub, "rooms", None) or {}).get(room_id) or {"id": room_id}
        return label({"id": room_id, **room})

    def advice(self, room_id):
        room = self.rooms.get(room_id)
        if room is None:
            return None
        ctx = {"state": room.get("state"), "program": _has_program(room), "fallback_c": _centi(room, "fallback_centi_c"),
               "minimum_c": _centi(room, "minimum_centi_c"), "maximum_c": _centi(room, "maximum_centi_c"),
               "valve_sensor": self.valve_sensor.get(room_id), "house_learned": self.learned, "ua_kw_per_k": self.ua,
               "heated": self.heated, "taus": self.taus, **self.gas}
        values = advise(self.days, room_id, self.today, ctx)
        if values is not None:
            values["factor"] = self.gas.get("factor")
        return values

    def live(self, room_id):
        """``live.advice`` and ``live.model`` of a room's screen (CONTRACT-1.4.2 §2, HA-ADVICE)."""
        name = self.name(room_id)
        emitter = (self.rooms.get(room_id) or {}).get("emitter")
        result = {"advice": None, "model": None}
        values = self.advice(room_id)
        if values is not None:
            texts = {lang: advice_text(values, name, lang) for lang in LANGUAGES}
            result["advice"] = {"text_en": texts["en"][0], "text_nl": texts["nl"][0],
                                "more_en": texts["en"][1], "more_nl": texts["nl"][1],
                                "target_c": values.get("target"), "rough": bool(values.get("rough")),
                                "reason": values.get("reason")}
        model = self.models.get(room_id)
        if model is not None:
            result["model"] = {key: model[key] for key in ("tau_h", "warm_rate_k_per_h", "quality", "hours_used",
                                                          "residual_k_per_h")}
            result["model"].update({f"sentence_{lang}": model_text(model, name, emitter, lang) for lang in LANGUAGES})
        return result


def _sensor(hass, entry):
    from .const import DOMAIN
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    return state.get("heating_advice") if isinstance(state, dict) else None


def room_live(hass, entry, room_id):
    """The room model's read values for PANEL-ROOM: ``{"advice": {...} | None, "model": {...} | None}``, or {} when the
    installation has no heating advice (not a product entry, or not set up yet). Outside the token (``live``)."""
    sensor = _sensor(hass, entry)
    if sensor is None or getattr(sensor, "hub", None) is None:
        return {}
    inputs = Inputs(hass, entry, sensor.hub, sensor.history, sensor.today())
    if room_id not in inputs.rooms:
        return {}
    return inputs.live(room_id)


def learning_lines(hass, entry, hub, history, today, lang):
    """The Learning view's line per room in the plan's order: [{room_id, name, advice, model}] (a room that is Off
    has no advice; a room without either is left out). 1.4.3 (LEARN-TAB, the room card's facts): also
    ``advice_kind`` (the room's state the advice is for: "active" or "follow"), ``advice_reason`` (None once it has a
    figure, else why not: too_little_data, valve_sensor) and ``cool_c_per_h`` (the model sentence's cooling at 5 °C
    outside, or None)."""
    if lang not in TEXT:
        lang = "en"
    inputs = Inputs(hass, entry, hub, history, today)
    lines = []
    for room_id in inputs.rooms:
        live = inputs.live(room_id)
        advice = (live.get("advice") or {}).get("text_" + lang)
        model = (live.get("model") or {}).get("sentence_" + lang)
        if advice or model:
            rates = model_rates(inputs.models.get(room_id))
            lines.append({"room_id": room_id, "name": inputs.name(room_id), "advice": advice, "model": model,
                          "advice_kind": inputs.rooms[room_id].get("state") if advice else None,
                          "advice_reason": (live.get("advice") or {}).get("reason") if advice else None,
                          "cool_c_per_h": round(rates[0], 3) if rates else None})
    return lines


# -- the action "Use 18 °C" ------------------------------------------------------------------------------------------


def routine_fallback(room_id, centi_c):
    """The plan change of the advice button: the room's fixed temperature, sent as a routine write (``"routine":
    true`` at the top of the plan, CONTRACT-1.4.2 §1: the E32 keeps its self-tuning and the warm-up state of every
    room; E32 1.4.1 ignores the key)."""
    from .room_plan import changed_plan, set_fallback

    def change(plan):
        candidate = changed_plan(plan, room_id, set_fallback(centi_c))
        candidate["routine"] = True
        return candidate
    return change


async def adopt_advice(hass, entry, item, values):
    """settings/action {section: "rooms", action: "adopt_advice", item: <room id>, values: {temperature?}}: write the
    advised temperature as the room's fixed temperature ("Heat along up to"), routine. ``temperature`` (°C, what the
    page showed) must still be the advice, else ``advice_changed``; no advice to adopt: ``advice_unavailable``."""
    from .room_plan import plan_room
    from .settings import SettingsError
    room_id = item if type(item) is str and item else values.get("room")
    sensor = _sensor(hass, entry)
    hub = getattr(sensor, "hub", None)
    link = getattr(hub, "plan", None)
    if sensor is None or hub is None or link is None:
        raise SettingsError("unavailable")
    inputs = Inputs(hass, entry, hub, sensor.history, sensor.today())
    if type(room_id) is not str or room_id not in inputs.rooms:
        raise SettingsError("e32_room_missing", room=str(room_id))
    advice = inputs.advice(room_id) or {}
    target = advice.get("target")
    if target is None:
        raise SettingsError("advice_unavailable")
    shown = values.get("temperature")
    if shown is not None and (type(shown) not in (int, float) or abs(shown - target) > 0.01):
        raise SettingsError("advice_changed")
    centi_c = int(round(target * 2)) * 50
    stored = await link.async_change_plan(
        routine_fallback(room_id, centi_c),
        lambda plan: (plan_room(plan, room_id) or {}).get("fallback_centi_c") == centi_c, key=("fallback", room_id))
    return {"room": room_id, "fallback_temperature": target, "routine": True, "stored": stored is not None}


def _register():
    from .settings import register_section
    register_section("rooms", actions={"adopt_advice": adopt_advice})


_register()
