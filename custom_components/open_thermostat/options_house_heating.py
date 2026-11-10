"""Configure steps for what the house mode, Smart warm-up and Weather compensation entities also set.

Everything the E32 device offers as a control is also here, in Configure
(options_navigation.py gives each step its Back item):

- House -> House mode and holiday: the house mode (Automatic, At home, Away,
  Holiday and, on an E32 with house.mode.summer.v1 (1.4.1), Summer) and the holiday end, with the very command of the select and the
  datetime entity (e32_house.HouseState.async_command); "Stop holiday". On an
  E32 that plans holidays (rc.4, house.holidays.v1) it is a menu: the house
  mode, plan a holiday, change or remove one, and the temperature on holiday
  (the number entity's command); the whole list is read and written in one E32
  web session (e32_house.async_change_holidays);
- Heating and boiler -> Smart warm-up and -> Weather compensation (with the water
  temperature in hard frost under Advanced): the same E32 link as the switches
  and the select (e32_flow.FlowSettingsLink.async_change). Beside Smart warm-up the
  comfort style (1.1.1 stage B: comfort first, balanced, save most), only for firmware
  that has it, as a plain choice with one sentence per option.
"""
from datetime import timedelta

import probatio as vol
from homeassistant.data_entry_flow import section
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .e32_comfort import AWAY_LIMITS, MAX_AWAY_DAYS
from .e32_flow import (COMFORT_STYLE_KEY, COMFORT_STYLES, DESIGN_FLOW_AUTOMATIC, DESIGN_FLOW_KEY, DESIGN_FLOW_LIMITS,
                       flow_link)
from .e32_house import (async_comfort_state, holiday_periods, holiday_temperature, holiday_until, house_mode,
                        offered_modes, supports_holidays)
from .heating_link import number
from .native_form import remember_shown, shown_value

DESIGN_CHOICES = [DESIGN_FLOW_AUTOMATIC, *(str(c) for c in range(DESIGN_FLOW_LIMITS[0], DESIGN_FLOW_LIMITS[1] + 1))]
# The E32's refusals of a holiday list (RoomOverrides::command) and of a change made elsewhere -> the form's error.
HOLIDAY_ERRORS = {"holiday_in_past": "house_holiday_past", "holiday_too_far": "house_holiday_too_far",
                  "too_many_holidays": "house_holiday_too_many", "house_holiday_too_many": "house_holiday_too_many",
                  "invalid_holidays": "house_holiday_order", "comfort_no_clock": "house_holiday_no_clock",
                  "house_holiday_changed": "house_holiday_changed"}


class HolidayInputError(Exception):
    def __init__(self, field, code):
        super().__init__(code)
        self.field, self.code = field, code


def holiday_input(start, end, now=None):
    """(from, until) in unix seconds of the form's two moments (local time when without a zone).

    The end lies in the future and at most a year ahead and after the start; the start may lie in the
    past (a holiday that runs already). Raises HolidayInputError(field, error key).
    """
    now = now or dt_util.utcnow()
    moments = []
    for field, value in (("holiday_from", start), ("holiday_to", end)):
        moment = dt_util.parse_datetime(str(value or ""))
        if moment is None:
            raise HolidayInputError(field, "house_holiday_dates_needed")
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=dt_util.get_default_time_zone())
        moments.append(moment)
    if moments[1] <= moments[0]:
        raise HolidayInputError("holiday_to", "house_holiday_order")
    if moments[1] <= now:
        raise HolidayInputError("holiday_to", "house_holiday_past")
    if moments[1] > now + timedelta(days=MAX_AWAY_DAYS):
        raise HolidayInputError("holiday_to", "house_holiday_too_far")
    return max(0, int(moments[0].timestamp())), int(moments[1].timestamp())


def holiday_line(period, language="en"):
    """One holiday in plain words, local time: "19 Dec 2030 10:00 – 3 Jan 2031 18:00" (numeric dates in Dutch)."""
    def moment(utc):
        local = dt_util.as_local(dt_util.utc_from_timestamp(utc))
        if language == "en":
            return f"{local.day} {local.strftime('%b %Y %H:%M')}"
        return local.strftime("%d-%m-%Y %H:%M")
    return f"{moment(period[0])} – {moment(period[1])}"


def _without(periods, period):
    """The list without one holiday; it must still be there (else it was changed elsewhere)."""
    if period not in periods:
        raise HomeAssistantError(translation_domain=DOMAIN, translation_key="house_holiday_changed")
    return [p for p in periods if p != period]


# -- the house mode and the holidays without the form (1.4): shared by these steps and the settings panel
# (settings_house.py). Each raises HolidayInputError(field, error key); a refusal of the E32 carries its word as
# ``error`` (the form's {error}).

def house_modes(away):
    """The house modes this E32 offers (the house mode select's options): At home only with house.mode.v1, Summer only
    with house.mode.summer.v1 (``away`` as e32_house.HouseState.away shows it)."""
    return offered_modes(away)


def house_mode_input(mode, until_text, modes):
    """(mode, until) of a chosen house mode; Holiday needs the moment it ends (unix seconds: in the future, at most
    a year ahead), the other modes (Summer too: on until you switch it off) have none."""
    if mode not in modes:
        raise HolidayInputError("house_mode", "house_mode_invalid")
    if mode != "holiday":
        return mode, None
    value = dt_util.parse_datetime(str(until_text or ""))
    if value is None:
        raise HolidayInputError("holiday_until", "house_holiday_date_needed")
    try:
        return mode, holiday_until(value)
    except HomeAssistantError:
        raise HolidayInputError("holiday_until", "house_holiday_date_invalid") from None


def _refused(code, err):
    failure = HolidayInputError("base", code)
    key = getattr(err, "translation_key", None)
    failure.error = (getattr(err, "translation_placeholders", None) or {}).get("error") or key or "unknown"
    return failure


async def async_set_house_mode(house, mode, until):
    """Send the house mode (and a holiday's end) with the very command of the house mode select."""
    try:
        if until is not None:
            house.pending_until = until
        await house.async_command(mode, until)
    except HomeAssistantError as err:
        key = getattr(err, "translation_key", None)
        raise _refused("house_mode_update_required" if key == "house_mode_update_required"
                       else "house_mode_not_saved", err) from None


def holidays_change(shown, wanted):
    """The change of the planned holidays from the periods shown to the ones wanted: each removed one must still be
    on the E32 (else house_holiday_changed: changed elsewhere), the added ones join the list as the E32 holds it."""
    removed = [period for period in shown if period not in wanted]
    added = [period for period in wanted if period not in shown]

    def change(periods):
        for period in removed:
            periods = _without(periods, period)
        return [*periods, *added]
    return change


async def async_change_planned_holidays(house, change):
    """Send one change of the planned holidays (read and written in one E32 web session)."""
    try:
        await house.async_holidays(change)
    except HomeAssistantError as err:
        key = getattr(err, "translation_key", None)
        code = (getattr(err, "translation_placeholders", None) or {}).get("error") or key or "unknown"
        failure = HolidayInputError("base", HOLIDAY_ERRORS.get(code, "house_holiday_not_saved"))
        failure.error = code
        raise failure from None


async def async_set_holiday_temperature(house, value):
    """Send the temperature on holiday (5–25 °C) with the very command of its number entity."""
    temperature = number(value, *AWAY_LIMITS)
    if temperature is None:
        raise HolidayInputError("holiday_temperature", "house_holiday_temperature_invalid")
    try:
        await house.async_holiday_temperature(temperature)
    except HomeAssistantError as err:
        raise _refused("house_holiday_not_saved", err) from None


class HouseHeatingSteps:
    """Mixin of the product options flow."""

    # -- house mode and holiday -------------------------------------------------------

    async def async_step_house_mode(self, user_input=None):
        house = self._presence_house()
        if house is None:
            return self.async_abort(reason="house_mode_unavailable")
        if user_input is None and supports_holidays(house.away):
            return await self.async_step_house_holidays()
        return await self._house_mode_form("house_mode", house, user_input)

    async def async_step_house_mode_set(self, user_input=None):
        """The house mode itself, inside the holidays menu (the same form as before rc.4)."""
        house = self._presence_house()
        if house is None:
            return self.async_abort(reason="house_mode_unavailable")
        return await self._house_mode_form("house_mode_set", house, user_input)

    async def _house_mode_form(self, step_id, house, user_input):
        away = house.away
        current = house_mode(away)
        modes = house_modes(away)
        errors, placeholders = {}, {"error": ""}
        if user_input is not None:
            try:  # shared with the settings panel (settings_house.py)
                mode, until = house_mode_input(user_input.get("house_mode"), user_input.get("holiday_until"), modes)
                # Plan item 1b: unchanged against what the form showed (the E32 may have changed it since).
                was_mode, was_until = shown_value(self, step_id, (current, away.get("until")))
                if mode == was_mode and (mode != "holiday" or until == was_until):
                    return self.async_abort(reason="e32_room_unchanged")
                await async_set_house_mode(house, mode, until)
            except HolidayInputError as err:
                errors[err.field] = err.code
                if hasattr(err, "error"):
                    placeholders["error"] = err.error
            else:
                return self.async_abort(reason="house_mode_saved")
        until = away.get("until") if current == "holiday" else None
        marker = vol.Optional("holiday_until")
        if type(until) is int and until > 0:
            marker = vol.Optional("holiday_until", description={"suggested_value": dt_util.as_local(
                dt_util.utc_from_timestamp(until)).strftime("%Y-%m-%d %H:%M:%S")})
        schema = vol.Schema({
            vol.Required("house_mode", default=current): selector.SelectSelector({
                "options": modes, "translation_key": "house_mode_choice", "mode": "list"}),
            marker: selector.DateTimeSelector(),
        })
        if user_input is not None:
            schema = self.add_suggested_values_to_schema(schema, user_input)
        else:
            remember_shown(self, step_id, (current, away.get("until")))
        return self.async_show_form(step_id=step_id, data_schema=schema, errors=errors,
                                    description_placeholders=placeholders)

    async def async_step_house_holiday_stop(self, user_input=None):
        house = self._presence_house()
        if house is None:
            return self.async_abort(reason="house_mode_unavailable")
        try:
            if supports_holidays(house.away):
                # rc.4: the running holiday ends now; the house returns to the mode it had before it.
                now = int(dt_util.utcnow().timestamp())
                await house.async_holidays(lambda periods: [p for p in periods if not p[0] <= now < p[1]])
            else:
                await house.async_command("auto", None)
        except HomeAssistantError:
            return self.async_abort(reason="house_mode_unavailable")
        return self.async_abort(reason="house_mode_saved")

    # -- planned holidays (E32 rc.4, house.holidays.v1) -------------------------------

    def _holiday_house(self):
        house = self._presence_house()
        return house if house is not None and supports_holidays(house.away) else None

    def _holiday_language(self):
        language = str(getattr(self.hass.config, "language", "en") or "en").split("-")[0]
        return language if language in ("en", "nl") else "en"

    async def _holiday_periods(self, house):
        """Every planned holiday as the E32 holds it now (the status names only the next two)."""
        return holiday_periods((await async_comfort_state(house.hub.plan))["holidays"])

    async def _holidays_change(self, house, change, errors, placeholders):
        """Sends one change of the list; the menu again ("Saved.") or None with the form's error set."""
        try:
            await async_change_planned_holidays(house, change)  # shared with the settings panel
        except HolidayInputError as err:
            errors[err.field] = err.code
            placeholders["error"] = err.error
            return None
        return self.async_abort(reason="house_mode_saved")

    async def async_step_house_holidays(self, user_input=None):
        """House mode and holiday: the house mode, plan a holiday, change or remove one, the temperature on holiday."""
        house = self._holiday_house()
        if house is None:
            return self.async_abort(reason="house_mode_unavailable")
        try:
            periods = await self._holiday_periods(house)
        except HomeAssistantError:
            return self.async_abort(reason="house_mode_unavailable")
        language = self._holiday_language()
        none = {"en": "No holidays planned.", "nl": "Geen vakanties gepland."}[language]
        lines = "\n".join(f"- {holiday_line(p, language)}" for p in periods) or none
        options = ["house_mode_set", "house_holiday_add", *(["house_holiday_change"] if periods else []), "house_holiday_temperature"]
        return self.async_show_menu(step_id="house_holidays", menu_options=options, description_placeholders={"holidays": lines})

    async def async_step_house_holiday_add(self, user_input=None):
        house = self._holiday_house()
        if house is None:
            return self.async_abort(reason="house_mode_unavailable")
        errors, placeholders = {}, {"error": ""}
        if user_input is not None:
            try:
                period = holiday_input(user_input.get("holiday_from"), user_input.get("holiday_to"))
            except HolidayInputError as err:
                errors[err.field] = err.code
            else:
                if (result := await self._holidays_change(house, holidays_change([], [period]), errors,
                                                          placeholders)) is not None:
                    return result
        schema = vol.Schema({vol.Required("holiday_from"): selector.DateTimeSelector(),
                             vol.Required("holiday_to"): selector.DateTimeSelector()})
        if user_input is not None:
            schema = self.add_suggested_values_to_schema(schema, user_input)
        return self.async_show_form(step_id="house_holiday_add", data_schema=schema, errors=errors,
                                    description_placeholders=placeholders)

    async def async_step_house_holiday_change(self, user_input=None):
        """Which holiday to change or remove (then house_holiday_edit)."""
        house = self._holiday_house()
        if house is None:
            return self.async_abort(reason="house_mode_unavailable")
        try:
            periods = await self._holiday_periods(house)
        except HomeAssistantError:
            return self.async_abort(reason="house_mode_unavailable")
        if not periods:
            return self.async_abort(reason="house_holidays_none")
        language, errors = self._holiday_language(), {}
        choices = {f"{f}-{u}": (f, u) for f, u in periods}
        if user_input is not None:
            if user_input.get("holiday") in choices:
                self._holiday = choices[user_input["holiday"]]
                return await self.async_step_house_holiday_edit()
            errors["holiday"] = "house_holiday_changed"
        options = [{"value": key, "label": holiday_line(p, language)} for key, p in choices.items()]
        schema = vol.Schema({vol.Required("holiday", default=options[0]["value"]): selector.SelectSelector(
            {"options": options, "mode": "list"})})
        return self.async_show_form(step_id="house_holiday_change", data_schema=schema, errors=errors)

    async def async_step_house_holiday_edit(self, user_input=None):
        house = self._holiday_house()
        original = getattr(self, "_holiday", None)
        if house is None or original is None:
            return self.async_abort(reason="house_mode_unavailable")
        errors = {}
        placeholders = {"error": "", "holiday": holiday_line(original, self._holiday_language())}
        if user_input is not None:
            change = None
            if user_input.get("remove") is True:
                change = holidays_change([original], [])
            else:
                try:
                    period = holiday_input(user_input.get("holiday_from"), user_input.get("holiday_to"))
                except HolidayInputError as err:
                    errors[err.field] = err.code
                else:
                    if period == original:
                        return self.async_abort(reason="e32_room_unchanged")
                    change = holidays_change([original], [period])
            if change is not None and (result := await self._holidays_change(house, change, errors, placeholders)) is not None:
                return result

        def local(utc):
            return dt_util.as_local(dt_util.utc_from_timestamp(utc)).strftime("%Y-%m-%d %H:%M:%S")
        schema = vol.Schema({
            vol.Required("holiday_from", default=local(original[0])): selector.DateTimeSelector(),
            vol.Required("holiday_to", default=local(original[1])): selector.DateTimeSelector(),
            vol.Optional("remove", default=False): selector.BooleanSelector(),
        })
        if user_input is not None:
            schema = self.add_suggested_values_to_schema(schema, user_input)
        return self.async_show_form(step_id="house_holiday_edit", data_schema=schema, errors=errors,
                                    description_placeholders=placeholders)

    async def async_step_house_holiday_temperature(self, user_input=None):
        """The temperature on holiday, with the very command of its number entity."""
        house = self._holiday_house()
        if house is None:
            return self.async_abort(reason="house_mode_unavailable")
        current = holiday_temperature(house.away)
        errors, placeholders = {}, {"error": ""}
        if user_input is not None:
            value = number(user_input.get("holiday_temperature"), *AWAY_LIMITS)
            was = shown_value(self, "house_holiday_temperature", current)  # plan item 1b
            if value is None:
                errors["holiday_temperature"] = "house_holiday_temperature_invalid"
            elif was is not None and float(value) == float(was):
                return self.async_abort(reason="e32_room_unchanged")
            else:
                try:
                    await async_set_holiday_temperature(house, value)  # shared with the settings panel
                except HolidayInputError as err:
                    errors[err.field] = err.code
                    placeholders["error"] = getattr(err, "error", "")
                else:
                    return self.async_abort(reason="house_mode_saved")
        if user_input is None:
            remember_shown(self, "house_holiday_temperature", current)
        schema = vol.Schema({vol.Required("holiday_temperature", default=current if current is not None else 15.0):
                             selector.NumberSelector({"min": AWAY_LIMITS[0], "max": AWAY_LIMITS[1], "step": 0.5, "mode": "box",
                                                      "unit_of_measurement": "°C"})})
        return self.async_show_form(step_id="house_holiday_temperature", data_schema=schema, errors=errors,
                                    description_placeholders=placeholders)

    # -- Smart warm-up and Weather compensation ---------------------------------------

    async def _heating_options(self):
        """(link, the options the E32 stored); (None, an abort result) when they cannot be read."""
        link = flow_link(self.hass, self.config_entry)
        if link is None:
            return None, self.async_abort(reason="e32_rooms_unavailable")
        try:
            return link, await link.async_read_now()
        except HomeAssistantError as err:
            return None, self._e32_abort_failure(err)

    @staticmethod
    def _comfort_field(stored):
        """{the comfort style field} for firmware that has it (1.1.1 stage B), else {}."""
        if stored.get(COMFORT_STYLE_KEY) not in COMFORT_STYLES:
            return {}
        return {vol.Required("comfort_style", default=stored[COMFORT_STYLE_KEY]): selector.SelectSelector({
            "options": list(COMFORT_STYLES), "translation_key": "comfort_style_choice", "mode": "list"})}

    @staticmethod
    def _comfort_change(stored, user_input, changes, shown=None):
        """Adds the comfort style to ``changes`` when the user changed it; False for a value the E32 would refuse.

        ``shown``: the options the form showed (plan item 1b): a style left as shown is not sent, so a style
        chosen on the E32's own page meanwhile stays.
        """
        if stored.get(COMFORT_STYLE_KEY) not in COMFORT_STYLES or "comfort_style" not in user_input:
            return True
        style = user_input.get("comfort_style")
        if style not in COMFORT_STYLES:
            return False
        was = (shown or stored).get(COMFORT_STYLE_KEY, stored[COMFORT_STYLE_KEY])
        if style != was and style != stored[COMFORT_STYLE_KEY]:
            changes[COMFORT_STYLE_KEY] = style
        return True

    @staticmethod
    def _option_change(changes, key, value, shown, stored):
        """Plan item 1b: ``value`` goes to the E32 only when the user changed it against what the form showed
        (and it is not what the E32 has now): Home Assistant never puts its copy back over an E32 edit."""
        if value != shown.get(key, stored[key]) and value != stored[key]:
            changes[key] = value

    async def _heating_save(self, link, changes):
        """None when the E32 stored every change (one field at a time), else the form's error key (1.4: the same
        write as the settings panel, e32_flow.async_save_options)."""
        from .e32_flow import async_save_options
        return await async_save_options(link, changes)

    async def async_step_heating_flow(self, user_input=None):
        """Smart warm-up and weather compensation in one form (1.1.1, V12-31): the two switches, the water
        temperature in hard frost under Advanced. The old rows heating_warm_up and heating_weather stay as steps
        (aliases), so a link to either still works."""
        link, stored = await self._heating_options()
        if link is None:
            return stored
        design = stored[DESIGN_FLOW_KEY]
        shown = DESIGN_FLOW_AUTOMATIC if design == 0 else str(design)
        errors = {}
        if user_input is not None:
            was = shown_value(self, "heating_options", stored)
            warm_up, on = user_input.get("smart_warm_up"), user_input.get("weather_compensation")
            choice = (user_input.get("advanced") or {}).get("hard_frost_water_temperature", shown)
            # 1.4: the same check as the settings panel (e32_flow.option_changes); the comfort style first, as before.
            from .e32_flow import option_changes
            try:
                if type(warm_up) is not bool or type(on) is not bool or choice not in DESIGN_CHOICES:
                    raise ValueError("e32_flow_options_failed")
                style = {COMFORT_STYLE_KEY: user_input.get("comfort_style")} if "comfort_style" in user_input else {}
                changes = option_changes(stored, was, {**style, "apply_learned": warm_up, "weather_curve": on,
                                                       DESIGN_FLOW_KEY: 0 if choice == DESIGN_FLOW_AUTOMATIC else int(choice)})
            except ValueError:
                errors["base"] = "e32_flow_options_failed"
            else:
                if not changes:
                    return self.async_abort(reason="e32_room_unchanged")
                if (error := await self._heating_save(link, changes)) is None:
                    return self.async_abort(reason="e32_flow_options_saved")
                errors["base"] = error
        remember_shown(self, "heating_options", dict(stored))
        schema = vol.Schema({
            vol.Required("smart_warm_up", default=stored["apply_learned"]): selector.BooleanSelector(),
            **self._comfort_field(stored),
            vol.Required("weather_compensation", default=stored["weather_curve"]): selector.BooleanSelector(),
            vol.Optional("advanced"): section(vol.Schema({
                vol.Required("hard_frost_water_temperature", default=shown): selector.SelectSelector({
                    "options": DESIGN_CHOICES, "translation_key": "flow_design_choice", "mode": "dropdown"}),
            }), {"collapsed": True}),
        })
        return self.async_show_form(step_id="heating_flow", data_schema=schema, errors=errors)

    async def async_step_heating_warm_up(self, user_input=None):
        link, stored = await self._heating_options()
        if link is None:
            return stored
        errors = {}
        if user_input is not None:
            was = shown_value(self, "heating_options", stored)
            value, changes = user_input.get("smart_warm_up"), {}
            if type(value) is not bool or not self._comfort_change(stored, user_input, changes, was):
                errors["base"] = "e32_flow_options_failed"
            else:
                first = {}
                self._option_change(first, "apply_learned", value, was, stored)
                changes = {**first, **changes}
                if not changes:
                    return self.async_abort(reason="e32_room_unchanged")
                if (error := await self._heating_save(link, changes)) is None:
                    return self.async_abort(reason="e32_flow_options_saved")
                errors["base"] = error
        remember_shown(self, "heating_options", dict(stored))
        schema = vol.Schema({vol.Required("smart_warm_up", default=stored["apply_learned"]): selector.BooleanSelector(),
                             **self._comfort_field(stored)})
        return self.async_show_form(step_id="heating_warm_up", data_schema=schema, errors=errors)

    async def async_step_heating_weather(self, user_input=None):
        link, stored = await self._heating_options()
        if link is None:
            return stored
        design = stored[DESIGN_FLOW_KEY]
        shown = DESIGN_FLOW_AUTOMATIC if design == 0 else str(design)
        errors = {}
        if user_input is not None:
            was = shown_value(self, "heating_options", stored)
            changes = {}
            on = user_input.get("weather_compensation")
            choice = (user_input.get("advanced") or {}).get("hard_frost_water_temperature", shown)
            if type(on) is not bool or choice not in DESIGN_CHOICES:
                errors["base"] = "e32_flow_options_failed"
            else:
                self._option_change(changes, "weather_curve", on, was, stored)
                wanted = 0 if choice == DESIGN_FLOW_AUTOMATIC else int(choice)
                self._option_change(changes, DESIGN_FLOW_KEY, wanted, was, stored)
                if not changes:
                    return self.async_abort(reason="e32_room_unchanged")
                if (error := await self._heating_save(link, changes)) is None:
                    return self.async_abort(reason="e32_flow_options_saved")
                errors["base"] = error
        remember_shown(self, "heating_options", dict(stored))
        schema = vol.Schema({
            vol.Required("weather_compensation", default=stored["weather_curve"]): selector.BooleanSelector(),
            vol.Optional("advanced"): section(vol.Schema({
                vol.Required("hard_frost_water_temperature", default=shown): selector.SelectSelector({
                    "options": DESIGN_CHOICES, "translation_key": "flow_design_choice", "mode": "dropdown"}),
            }), {"collapsed": True}),
        })
        return self.async_show_form(step_id="heating_weather", data_schema=schema, errors=errors)
