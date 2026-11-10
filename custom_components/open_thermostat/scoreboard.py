"""Yesterday's scoreboard (E32 rc.4): is the thermostat getting better at its job?

The E32 keeps score per local day and sends it in ``fw/telemetry/summary`` as ``scoreboard``:
``{"yesterday": {...} | null, "today": {...} | null}``, each day with ``day`` (YYYY-MM-DD),
``heating_h``, ``heating_starts_per_h``, ``short_cycle_h``, ``heating_kwh``, ``degree_days`` and
``rooms``: ``[{"id", "on_time_min", "overshoot_c"}]``. Every number may be null (not measured);
firmware before rc.4 sends no scoreboard at all.

Per room, on the room's device: "Warm on time yesterday (minutes late)" (minutes after the program's
switch time that the room was warm; negative: early) and "Above target yesterday" (how far it got
above its target, °C). Per house, on the product device: burner starts per heating hour, hours of
short cycling, heating energy and heating energy per degree-day (kWh/°C·d), each named "yesterday".
Each shows yesterday's figure; state class measurement, so the Recorder keeps the history of every
day. Today's figure so far is an attribute (not recorded: it changes all day). An entity appears
only once the E32 reported a value for yesterday (1.0.0rc7; before: yesterday or today, which left
it "unknown" all through the first day), so firmware or a house without a figure never gets an
"unknown" entity. All are diagnostic: the Learning view shows them, the device page keeps them aside.

Once it existed it stays (1.4.1): at every later setup it is created again while its registry record
is there (heating_link.entity_was_there), also on a day without that figure (a room not measured, a
mild day without gas per degree-day, an E32 that lost the day in a restart, firmware that stopped
sending the scoreboard). Before 1.4.1 such a day left the record without an entity: "Unavailable",
"no longer provided" on the room's device. Without a figure the state is unknown, ``day`` the day the
E32 scored (None without one) and ``reason`` "not_measured"; the last figure is not kept, so no day
shows another day's figure and the history and statistics have no value for that day (the dashboard
and the Yesterday card leave an unknown figure out, a room's unknown warm on time reads "no warm-up").

1.4.2 (review R142 F8, F11): a "yesterday" that is not the day before the scoreboard's own today (the E32's day
jumped by more than one, after a day without a trusted clock) is not yesterday: every figure is unknown with
``reason`` "other_day" and creates no entity. The E32's own today is the reference, not Home Assistant's date: the
two may run in different time zones, and a stale summary is unavailable anyway. Heating energy per degree-day
needs a day the E32 observed for at least MIN_OBSERVED_H hours (``observed_h``, E32 1.4.2): a day it was partly off
would read as a frugal one; below that it is unknown with ``reason`` "partial_day". Firmware without ``observed_h``
keeps the figure as before.

1.4.2 (F16, the owner's bathroom): a room on Heat along only or Off works towards no target, so it never gets a
figure. Its figures stay, in the same form as a day without a figure, with the reason why: ``reason`` "heat_along"
or "off" (the room's state now) instead of "not_measured". The dashboard's Yesterday in figures then says "not
measured" with that reason in grey for the room, never "Unknown"; the entity keeps its history.
"""
from datetime import date

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory, UnitOfEnergy, UnitOfTemperature, UnitOfTime

from .heating_link import HubEntity, RoomEntity, number

# Room figure: (scoreboard key, lowest and highest plausible value).
ROOM_FIGURES = {"warm_on_time": ("on_time_min", -1440, 1440), "overshoot": ("overshoot_c", -10, 10)}
# House figure: (scoreboard key, lowest and highest plausible value); gas per degree-day is worked out.
HOUSE_FIGURES = {"burner_starts_per_heating_hour": ("heating_starts_per_h", 0, 60),
                 "short_cycling_hours": ("short_cycle_h", 0, 24),
                 "heating_gas_yesterday": ("heating_kwh", 0, 1000),
                 "gas_per_degree_day": None}
# Below one degree-day (a mild day) gas per degree-day says little and jumps: not shown.
MIN_DEGREE_DAYS = 1.0
# Heating energy per degree-day (rc.4-rc.6 said kWh; the statistics follow, native_entity_cleanup).
PER_DEGREE_DAY_UNIT = "kWh/°C·d"
# The attribute ``reason`` while yesterday has no figure (state unknown, 1.4.1); 1.4.2: the scoreboard's yesterday is
# another day (F11), or gas per degree-day on a day the E32 observed less than MIN_OBSERVED_H hours (F8).
NOT_MEASURED = "not_measured"
OTHER_DAY = "other_day"
PARTIAL_DAY = "partial_day"
# The firmware's own Insights refuse a day with less than 20 h of outdoor data (Scoreboard.h).
MIN_OBSERVED_H = 20.0
# 1.4.2 (F16): the reason of a room's figure while the room works towards no target: its state now.
ROOM_REASONS = {"follow": "heat_along", "inactive": "off"}


def room_reason(room):
    """Why a room's figure has no value: "heat_along" (Heat along only), "off" (Off), else "not_measured"."""
    return ROOM_REASONS.get(room.get("state") if type(room) is dict else None, NOT_MEASURED)


def scoreboard(summary):
    """The summary's scoreboard, or None on firmware without it."""
    board = summary.get("scoreboard") if type(summary) is dict else None
    return board if type(board) is dict else None


def scoreboard_day(board, which):
    """One day of the scoreboard ("yesterday" or "today"), or None."""
    day = board.get(which) if type(board) is dict else None
    return day if type(day) is dict else None


def day_name(day):
    """The local day a scoreboard day is about (YYYY-MM-DD), or None."""
    value = day.get("day") if type(day) is dict else None
    return value if type(value) is str and len(value) == 10 else None


def other_day(board):
    """True when the scoreboard's yesterday is not the day before its today (F11): an older day kept as yesterday."""
    names = [day_name(scoreboard_day(board, which)) for which in ("yesterday", "today")]
    if None in names:
        return False
    try:
        yesterday, today = (date.fromisoformat(name) for name in names)
    except ValueError:
        return False
    return (today - yesterday).days != 1


def yesterday(board):
    """The scoreboard's yesterday when it is the day before its today, else None."""
    return None if other_day(board) else scoreboard_day(board, "yesterday")


def partial_day(day):
    """True for a day the E32 observed less than MIN_OBSERVED_H hours (``observed_h``, E32 1.4.2; F8)."""
    hours = number(day.get("observed_h"), 0, 48) if type(day) is dict else None
    return hours is not None and hours < MIN_OBSERVED_H


def room_figure(day, room_id, key):
    """One room's figure of a scoreboard day, or None (not measured, or no such room)."""
    rooms = day.get("rooms") if type(day) is dict else None
    room = next((r for r in rooms if type(r) is dict and r.get("id") == room_id), None) if type(rooms) is list else None
    field, low, high = ROOM_FIGURES[key]
    return number(room.get(field), low, high) if room is not None else None


def house_figure(day, key):
    """One house figure of a scoreboard day, or None (not measured)."""
    if type(day) is not dict:
        return None
    if key == "gas_per_degree_day":
        if partial_day(day):
            return None
        kwh, degree_days = number(day.get("heating_kwh"), 0, 1000), number(day.get("degree_days"), 0, 100)
        return round(kwh / degree_days, 2) if kwh is not None and degree_days and degree_days >= MIN_DEGREE_DAYS else None
    field, low, high = HOUSE_FIGURES[key]
    return number(day.get(field), low, high)


class _Scoreboard:
    """Mixin: the hub's scoreboard while the E32 reports; available while the E32 is online, with or without a figure."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    # Today's figure changes all day: shown, not kept in the history (yesterday's figure is the state).
    _unrecorded_attributes = frozenset({"today"})

    @property
    def board(self):
        return scoreboard(self.hub.summary) if self.hub.fresh else None


class ScoreboardRoomSensor(_Scoreboard, RoomEntity, SensorEntity):
    """Yesterday's "warm on time" or "overshoot" of one room."""

    def __init__(self, hub, room, key):
        self.key = key
        self._attach_room(hub, room, key)
        if key == "overshoot":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE_DELTA
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_suggested_display_precision = 1
        else:  # minutes late; negative: early (plain minutes: a duration cannot be negative)
            self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
            self._attr_suggested_display_precision = 0

    @property
    def available(self):
        return self.hub.fresh and self.room is not None

    @property
    def native_value(self):
        return room_figure(yesterday(self.board), self.room_id, self.key)

    @property
    def extra_state_attributes(self):
        if not self.available:
            return None
        board = self.board
        result = {"room_id": self.room_id, "day": day_name(scoreboard_day(board, "yesterday")),
                  "today": room_figure(scoreboard_day(board, "today"), self.room_id, self.key)}
        return _with_reason(result, self.native_value, OTHER_DAY if other_day(board) else room_reason(self.room))


class ScoreboardHouseSensor(_Scoreboard, HubEntity, SensorEntity):
    """Yesterday's burner starts per heating hour, short cycling, gas for heating or gas per degree-day."""

    def __init__(self, hub, key):
        self.key = key
        self._attach(hub, f"hub_{key}")
        self._attr_translation_key = key
        if key == "short_cycling_hours":
            self._attr_device_class = SensorDeviceClass.DURATION
            self._attr_native_unit_of_measurement = UnitOfTime.HOURS
            self._attr_suggested_display_precision = 1
        elif key == "heating_gas_yesterday":
            # A day's figure, not a meter: no energy device class (the Energy dashboard has the gas meter).
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
            self._attr_suggested_display_precision = 1
        elif key == "gas_per_degree_day":
            self._attr_native_unit_of_measurement = PER_DEGREE_DAY_UNIT
            self._attr_suggested_display_precision = 2
        else:
            self._attr_suggested_display_precision = 1

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        if self.key == "gas_per_degree_day":  # its statistics were labelled kWh before rc7: the same numbers
            from .native_entity_cleanup import async_tidy_statistics
            self.hass.async_create_background_task(
                async_tidy_statistics(self.hass, self.entity_id, unit=PER_DEGREE_DAY_UNIT),
                "open_thermostat statistics unit")

    @property
    def available(self):
        return self.hub.fresh

    @property
    def native_value(self):
        return house_figure(yesterday(self.board), self.key)

    @property
    def extra_state_attributes(self):
        if not self.available:
            return None
        board = self.board
        shown, older = yesterday(board), other_day(board)
        result = {"day": day_name(scoreboard_day(board, "yesterday")),
                  "today": house_figure(scoreboard_day(board, "today"), self.key)}
        if self.key == "burner_starts_per_heating_hour":
            result["heating_hours"] = number((shown or {}).get("heating_h"), 0, 24)
        elif self.key == "gas_per_degree_day":
            result["heating_kwh"] = house_figure(shown, "heating_gas_yesterday")
            result["degree_days"] = number((shown or {}).get("degree_days"), 0, 100)
            if (hours := number((shown or {}).get("observed_h"), 0, 48)) is not None:
                result["observed_hours"] = hours
        reason = (OTHER_DAY if older else PARTIAL_DAY if self.key == "gas_per_degree_day" and partial_day(shown)
                  else NOT_MEASURED)
        return _with_reason(result, self.native_value, reason)


def _with_reason(attributes, value, reason=NOT_MEASURED):
    """The attributes, with ``reason`` ("not_measured"; "other_day" for an older day kept as yesterday; for gas per
    degree-day also "partial_day"; for a room also "heat_along" or "off") while yesterday has no figure (the state
    unknown)."""
    return attributes if value is not None else {**attributes, "reason": reason}


def wanted_scoreboard(hub):
    """(key, factory) of every scoreboard figure the E32 reported a value for yesterday (the state), and of every
    one that existed before (its registry record is there, heating_link.entity_was_there), with or without a value.

    Today's figure alone never creates one: it would read "unknown" until midnight (today is an attribute). A
    house figure that existed is created at once at setup (unavailable until the E32 reports), a room's once the
    E32 reports the room.
    """
    from .heating_link import entity_was_there
    day = yesterday(scoreboard(hub.summary) if hub.fresh else None)  # never a figure of another day (F11)
    for key in HOUSE_FIGURES:
        if house_figure(day, key) is not None or entity_was_there(hub, f"hub_{key}"):
            yield ("scoreboard", key), lambda key=key: ScoreboardHouseSensor(hub, key)
    for room_id, room in hub.known_rooms.items():  # 1.4.2 (HC-03): also while the E32 is offline
        for key in ROOM_FIGURES:
            if room_figure(day, room_id, key) is not None or entity_was_there(hub, f"e32_room_{room_id}_{key}"):
                yield ("room", room_id, key), lambda room=room, key=key: ScoreboardRoomSensor(hub, room, key)
