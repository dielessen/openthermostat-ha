"""The settings panel's section House (1.4, docs/engineering/HA-INSTELPANEEL-ONTWERP.nl.md chapter 5).

One section ``house`` with sub-screens (the item):

- None: the four parts with what is set now;
- ``presence``: who lives here, away after, the temperature when nobody is home (Configure → House → Presence);
- ``defaults``: the room defaults (comfort and night without a week program, the pauses after a window or door
  opens, the length of a manual change; Configure → House → Room defaults);
- ``mode``: the house mode now and, on an E32 that plans holidays (house.holidays.v1), the planned holidays and the
  temperature on holiday (Configure → House → House mode and holiday);
- ``contacts``: the rooms with their window and door contacts, and ``contacts/<room id>``: one room's two lists
  (Configure → House → Window and door contacts).

The models come from the config entry and what the hub holds; only the screen ``mode`` reads the E32 (every
planned holiday: its status names the next two), as the options step does. Each save uses the options steps' own
functions (e32_comfort: async_save_presence, save_room_defaults, save_room_contacts; options_house_heating:
house_mode_input, async_set_house_mode, holidays_change, async_change_planned_holidays,
async_set_holiday_temperature) and sends only what differs from the screen as shown: the token proves that is
what is stored, and a value the user left alone is never sent back over a change made elsewhere.
"""
from __future__ import annotations

from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .e32_comfort import (AWAY_LIMITS, ComfortError, async_save_presence, comfort_options, contact_delay_text,
                          doors_of, save_room_contacts, save_room_defaults, windows_of)
from .e32_house import (async_comfort_state, holiday_periods, holiday_temperature, house_mode, house_state,
                        supports_holidays)
from .heating_link import number
from .options_house_heating import (HolidayInputError, async_change_planned_holidays, async_set_holiday_temperature,
                                    async_set_house_mode, holiday_input, holidays_change, house_mode_input,
                                    house_modes)
from .settings import SettingsError, _hub, register_section

PARTS = ("presence", "defaults", "mode", "contacts")
DEFAULT_FIELDS = ("comfort_temperature", "eco_temperature", "contact_delay", "door_delay", "override_minutes")


def _house(hass, entry):
    """The E32's house state (e32_house.HouseState) while it reports the house's away status, else None."""
    hub = _hub(hass, entry)
    if hub is None or getattr(hub, "plan", None) is None:
        return None
    house = house_state(hass, entry, hub)
    return house if house.away is not None else None


def _local(epoch):
    """A moment as the panel's date-and-time field holds it ("2026-12-19T10:00", local time)."""
    return dt_util.as_local(dt_util.utc_from_timestamp(epoch)).strftime("%Y-%m-%dT%H:%M")


def _rooms(hass, entry):
    """[(room id, name)] of the E32 rooms, in the order of the room plan Home Assistant last read."""
    hub = _hub(hass, entry)
    plan = getattr(getattr(hub, "plan", None), "plan", None)
    if type(plan) is dict and type(plan.get("rooms")) is list:
        return [(room["id"], room.get("name") or room["id"]) for room in plan["rooms"]]
    rooms = getattr(hub, "rooms", None) or {}
    return [(room_id, room.get("name") or room_id) for room_id, room in sorted(rooms.items())]


def _comfort_error(err):
    extra = {"error": err.error} if hasattr(err, "error") else {}
    return SettingsError(err.code, err.field, **extra)


def _holiday_error(err, field):
    extra = {"error": err.error} if hasattr(err, "error") else {}
    return SettingsError(err.code, field if err.field == "base" or field == "holidays" else err.field, **extra)


# -- the models ---------------------------------------------------------------------------------------------------

def presence_model(hass, entry, house):
    current = comfort_options(entry)
    away = number(house.away.get("target_c"), *AWAY_LIMITS) if house is not None else None
    return {"presence_entities": list(current["presence_entities"]), "away_delay": current["away_delay_min"],
            "away_temperature": away, "has_away": house is not None}


def defaults_model(entry):
    current = comfort_options(entry)
    return {"comfort_temperature": current["comfort_c"], "eco_temperature": current["eco_c"],
            "contact_delay": current["contact_delay_s"] / 60, "door_delay": current["door_delay_s"] / 60,
            "override_minutes": current["override_minutes"]}


async def _mode_state(house):
    """(the screen's model, the planned holidays as the E32 holds them now [(from, until)])."""
    away = house.away
    mode = house_mode(away)
    until = away.get("until") if mode == "holiday" else None
    model = {"house_mode": mode, "modes": house_modes(away),
             "holiday_until": _local(until) if type(until) is int and until > 0 else "",
             "planning": supports_holidays(away)}
    periods = []
    if model["planning"]:
        try:
            periods = holiday_periods((await async_comfort_state(house.hub.plan))["holidays"])
        except HomeAssistantError:
            raise SettingsError("house_mode_unavailable") from None
        model["holidays"] = [{"from": _local(start), "until": _local(end)} for start, end in periods]
        model["holiday_temperature"] = holiday_temperature(away)
    return model, periods


def contacts_model(hass, entry):
    current = comfort_options(entry)
    return {"rooms": [{"id": room_id, "name": name, "windows": len(windows_of(current, room_id)),
                       "doors": len(doors_of(current, room_id))} for room_id, name in _rooms(hass, entry)]}


def room_contacts_model(hass, entry, room_id):
    rooms = dict(_rooms(hass, entry))
    if room_id not in rooms:
        raise SettingsError("comfort_no_rooms")
    current = comfort_options(entry)
    return {"room": room_id, "name": rooms[room_id], "contacts": windows_of(current, room_id),
            "door_contacts": doors_of(current, room_id), "delay": contact_delay_text(current, room_id),
            "door_delay": contact_delay_text(current, room_id, door=True)}


def overview_model(hass, entry, house):
    """The four parts with what is set now (memory only: the next two holidays from the E32's status)."""
    contacts = contacts_model(hass, entry)["rooms"]
    mode = None
    if house is not None:
        away = house.away
        mode = {"house_mode": house_mode(away), "planning": supports_holidays(away),
                "holidays": [{"from": _local(start), "until": _local(end)}
                             for start, end in holiday_periods(away.get("holidays"))][:2]}
    return {"presence": presence_model(hass, entry, house), "defaults": defaults_model(entry), "mode": mode,
            "contacts": {"rooms": sum(1 for room in contacts if room["windows"] or room["doors"]),
                         "sensors": sum(room["windows"] + room["doors"] for room in contacts),
                         "any_room": bool(contacts)}}


def _part(item):
    """(part, room id) of the item: "presence" → ("presence", None), "contacts/woonkamer" → ("contacts", "woonkamer")."""
    part, _, room_id = (item or "").partition("/")
    if part not in PARTS or (room_id and part != "contacts"):
        raise SettingsError("unknown_section")
    return part, room_id or None


async def read_house(hass, entry, item):
    house = _house(hass, entry)
    if item is None:
        return overview_model(hass, entry, house)
    part, room_id = _part(item)
    if part == "presence":
        return presence_model(hass, entry, house)
    if part == "defaults":
        return defaults_model(entry)
    if part == "contacts":
        return room_contacts_model(hass, entry, room_id) if room_id else contacts_model(hass, entry)
    if house is None:  # the E32 reports no house status yet (or its firmware has none): the screen says so
        return {"house_mode": None, "unavailable": True}
    return (await _mode_state(house))[0]


# -- saving -------------------------------------------------------------------------------------------------------

async def _save_mode(house, values):
    model, periods = await _mode_state(house)
    if model["planning"] and "holidays" in values:
        items = values["holidays"]
        if type(items) is not list:
            raise SettingsError("house_holiday_line_dates_needed", "holidays", line="1")
        wanted = []
        for number_, item in enumerate(items, 1):
            if item in model["holidays"]:  # as shown: the E32's own moments, to the second
                wanted.append(periods[model["holidays"].index(item)])
                continue
            try:
                wanted.append(holiday_input((item or {}).get("from"), (item or {}).get("until")))
            except HolidayInputError as err:  # its own sentence, naming which holiday of the list
                raise SettingsError(err.code.replace("house_holiday_", "house_holiday_line_"), "holidays",
                                    line=str(number_)) from None
        if sorted(wanted) != sorted(periods):
            try:
                await async_change_planned_holidays(house, holidays_change(periods, wanted))
            except HolidayInputError as err:
                raise _holiday_error(err, "holidays") from None
    if model["planning"] and "holiday_temperature" in values and values["holiday_temperature"] != model["holiday_temperature"]:
        try:
            await async_set_holiday_temperature(house, values["holiday_temperature"])
        except HolidayInputError as err:
            raise _holiday_error(err, "holiday_temperature") from None
    mode = values.get("house_mode", model["house_mode"])
    until_text = values.get("holiday_until", model["holiday_until"])
    if mode != model["house_mode"] or (mode == "holiday" and until_text != model["holiday_until"]):
        try:
            await async_set_house_mode(house, *house_mode_input(mode, until_text, model["modes"]))
        except HolidayInputError as err:
            raise _holiday_error(err, "base") from None


async def save_house(hass, entry, item, values):
    if item is None:
        raise SettingsError("unknown_section")  # the overview itself has nothing to save
    part, room_id = _part(item)
    house = _house(hass, entry)
    try:
        if part == "presence":
            model = presence_model(hass, entry, house)
            await async_save_presence(hass, entry, house, {key: values.get(key, model[key]) for key in (
                "presence_entities", "away_delay", "away_temperature")}, model["away_temperature"])
        elif part == "defaults":
            model = defaults_model(entry)
            save_room_defaults(hass, entry, {key: values.get(key, model[key]) for key in DEFAULT_FIELDS})
        elif part == "contacts":
            if room_id is None:
                raise SettingsError("unknown_section")
            model = room_contacts_model(hass, entry, room_id)
            save_room_contacts(hass, entry, room_id, values.get("contacts", model["contacts"]),
                               values.get("door_contacts", model["door_contacts"]))
        else:
            if house is None:
                raise SettingsError("house_mode_unavailable")
            await _save_mode(house, values)
    except ComfortError as err:
        raise _comfort_error(err) from None
    return await read_house(hass, entry, item)


register_section("house", read_house, save_house)
