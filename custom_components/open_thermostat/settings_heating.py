"""The settings panel's section Heating and boiler (1.4; settings.py registers it, the screens are
frontend/openthermostat-settings-heating.js; design docs/engineering/HA-INSTELPANEEL-ONTWERP.nl.md, chapter 5).

The screens (the panel's item; ``#heating/<item>``):

- ``None``: the list, what is set now from what Home Assistant already holds (the room plan it last read, the
  flow options the E32 last reported, the boiler model of its last profile, the circuits of its telemetry); no E32
  read. Read-only: each row opens its screen, "Boiler settings (preview)" opens Configure.
- ``flow``: Smart warm-up, Weather compensation, the comfort style (firmware that has it) and the water temperature
  in hard frost (−10 °C): ``e32_flow.option_changes`` and ``async_save_options``, as Configure's step heating_flow.
- ``limits``: the water temperature limits with the tick "Lowest water temperature: automatic": ``e32_flow.limit_edits``,
  ``limit_warnings`` and ``async_save_limits`` (the room plan's revision and If-Match, only what changed), as
  Configure's step e32_flow_limits. A warning (floor heating above 50 °C, above the boiler's own maximum) is a
  question in the panel; the save after it says ``confirmed``.
- ``circuits``: per heating circuit with a pump, Pump control by the E32, the highest water temperature to the floor
  and the run-on at most (``e32_shelly.pump_changes``, ``ShellyLink.async_pump_settings``).
- ``care``: Comfort and boiler care, every knob automatic or your value in one save (``e32_care.changes_for``), and
  the two actions "Back to automatic for all" and "Back to start values" (``{"action": "auto_all" | "reset"}``).
  Read from the E32 on every opening (its self-tuning moves the values), as Configure does.
- ``model``: the boiler model (``e32_boiler_model.async_read_model``, ``async_save_model``), with what the E32
  recognised on the bus (boiler_capabilities) beside it.

Every model is plain JSON in the user's unit; what only informs (the lowest water temperature now, the boiler's own
maximum, the recognised boiler) is under ``live``, which the token leaves out (settings.LIVE), so a new reading never
makes a save "changed elsewhere". Errors are the flow's own keys with their placeholders (the panel has a sentence for
each one).
"""
from __future__ import annotations

from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .settings import SettingsError, register_section

ITEMS = (None, "flow", "limits", "circuits", "care", "model")


# -- what Home Assistant holds -------------------------------------------------------------------------------------

def _state(hass, entry):
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    return state if isinstance(state, dict) else {}


def _hub(hass, entry):
    return _state(hass, entry).get("heating_hub")


def _plan_link(hass, entry):
    """The room-plan link of the stored E32 connection (its sign-in and lock); SettingsError connect_e32 without."""
    from .room_plan import has_room_plan
    link = getattr(_hub(hass, entry), "plan", None) if has_room_plan(entry) else None
    if link is None:
        raise SettingsError("connect_e32")
    return link


def _flow_link(hass, entry, create=False):
    """The flow-options link (e32_flow); None while the platforms have not made it (``create``: make it, as
    Configure's forms do)."""
    from .e32_flow import KEY, flow_link
    link = _state(hass, entry).get(KEY)
    if link is None and create:
        _plan_link(hass, entry)
        link = flow_link(hass, entry)
    return link


def _plan_failure(err):
    """A refused or failed room-plan write as the flow's error key and placeholders (E32RoomFlow._e32_failure)."""
    from .e32_room_flow import E32RoomFlow
    key, placeholders = E32RoomFlow._e32_failure(None, err)
    return SettingsError(key, **placeholders)


def _boiler_maximum(hass, entry):
    """The boiler's own maximum heating temperature (°C) when it reports one (E32RoomFlow._boiler_maximum)."""
    client = getattr(_state(hass, entry).get("v1_connection"), "client", None)
    if client is None:
        return None
    from .heating_advice import boiler_maximum
    return boiler_maximum(client)


def _minimum_now(hub, unit):
    """{"value", "kind": standard | own | learned} of the lowest water temperature the E32 applies now, or None."""
    from .e32_room_flow import flow_shown, minimum_flow_now
    now = minimum_flow_now(getattr(hub, "summary", None))
    return None if now is None else {"value": flow_shown(round(now[0]), unit), "kind": now[1]}


def _options(settings):
    """The four options of the flow form as the panel shows them (the flow's field names)."""
    from .e32_flow import COMFORT_STYLE_KEY, COMFORT_STYLES, DESIGN_FLOW_AUTOMATIC, DESIGN_FLOW_KEY
    design = settings[DESIGN_FLOW_KEY]
    model = {"smart_warm_up": settings["apply_learned"], "weather_compensation": settings["weather_curve"],
             "hard_frost_water_temperature": DESIGN_FLOW_AUTOMATIC if design == 0 else str(design)}
    if settings.get(COMFORT_STYLE_KEY) in COMFORT_STYLES:
        model["comfort_style"] = settings[COMFORT_STYLE_KEY]
    return model


# -- the list ------------------------------------------------------------------------------------------------------

def _list(hass, entry):
    from .e32_boiler_settings import offered as boiler_settings_offered
    from .e32_care import care_offered
    from .e32_flow import temperature_unit
    from .e32_room_flow import MINIMUM_AUTOMATIC_KEY, flow_shown
    from .e32_shelly import CIRCUIT_ID, pump_of
    hub, unit = _hub(hass, entry), temperature_unit(hass)
    plan = getattr(getattr(hub, "plan", None), "plan", None)
    limits = None
    if type(plan) is dict:
        low, high = plan.get("minimum_flow_c"), plan.get("maximum_flow_c")
        limits = {"automatic": plan.get(MINIMUM_AUTOMATIC_KEY) if type(plan.get(MINIMUM_AUTOMATIC_KEY)) is bool else None,
                  "minimum": flow_shown(low, unit) if type(low) is int else None,
                  "maximum": flow_shown(high, unit) if type(high) is int else None}
    link = _flow_link(hass, entry)
    settings = getattr(link, "settings", None)
    circuits = [{"id": circuit_id, "kind": circuit.get("kind")} for circuit_id, circuit in (getattr(hub, "circuits", None) or {}).items()
                if CIRCUIT_ID.fullmatch(str(circuit_id)) and pump_of(circuit) is not None]
    model_id = _state(hass, entry).get("ems_boiler_model")
    from .e32_boiler_model import model_name
    return {"unit": unit, "limits": limits,
            "flow_offered": link is not None and not link.unsupported,
            "flow": _options(settings) if type(settings) is dict else None,
            "care_offered": care_offered(hass, entry),
            "care": {"yours": len(settings["tuning_manual"])} if type(settings) is dict and "tuning_manual" in settings else None,
            "circuits": circuits,
            "boiler_model": model_name(model_id, "en") if type(model_id) is str and model_id != "none" else None,
            "boiler_settings": boiler_settings_offered(hass, entry),
            "live": {"minimum_now": _minimum_now(hub, unit) if limits and limits["automatic"] else None}}


# -- Smart warm-up and weather compensation ---------------------------------------------------------------------------

async def _flow_settings(hass, entry):
    """(link, the options as the E32 reported them last); read from the E32 once when Home Assistant has none yet."""
    link = _flow_link(hass, entry, create=True)
    if link is None or link.unsupported:
        raise SettingsError("e32_settings_update_required")
    settings = link.settings if type(link.settings) is dict else await link.async_read_now()
    return link, settings


async def _read_flow(hass, entry):
    _link, settings = await _flow_settings(hass, entry)
    return _options(settings)


async def _save_flow(hass, entry, values):
    from .e32_flow import (COMFORT_STYLE_KEY, DESIGN_CHOICES, DESIGN_FLOW_AUTOMATIC, DESIGN_FLOW_KEY,
                           async_save_options, option_changes)
    link, stored = await _flow_settings(hass, entry)
    choice = values.get("hard_frost_water_temperature")
    if choice not in DESIGN_CHOICES:
        raise SettingsError("e32_flow_options_failed")
    wanted = {**({COMFORT_STYLE_KEY: values["comfort_style"]} if "comfort_style" in values else {}),
              "apply_learned": values.get("smart_warm_up"), "weather_curve": values.get("weather_compensation"),
              DESIGN_FLOW_KEY: 0 if choice == DESIGN_FLOW_AUTOMATIC else int(choice)}
    try:
        # The token check just compared what the panel showed with what the E32 reports now: shown is stored.
        changes = option_changes(stored, stored, wanted)
    except ValueError as err:
        raise SettingsError(str(err)) from None
    if changes and (error := await async_save_options(link, changes)) is not None:
        raise SettingsError(error)
    return None


# -- the water temperature limits ------------------------------------------------------------------------------------

async def _limits_plan(hass, entry):
    link = _plan_link(hass, entry)
    if type(link.plan) is dict:
        return link, link.plan
    try:
        return link, await link.async_read()
    except HomeAssistantError as err:
        raise _plan_failure(err) from None


def _ranges(unit):
    from .e32_room_flow import E32RoomFlow
    return E32RoomFlow._flow_ranges(unit)


async def _read_limits(hass, entry):
    from .e32_flow import temperature_unit
    from .e32_room_flow import FLOW_MAXIMUM_C, FLOW_MINIMUM_C, FLOOR_FLOW_WARNING_C, MINIMUM_AUTOMATIC_KEY, flow_shown
    _link, plan = await _limits_plan(hass, entry)
    unit = temperature_unit(hass)
    low, high = plan.get("minimum_flow_c"), plan.get("maximum_flow_c")
    model = {"minimum_flow_temperature": flow_shown(low if type(low) is int else 30, unit),
             "maximum_flow_temperature": flow_shown(high if type(high) is int else 60, unit), "unit": unit,
             "minimum_range": [flow_shown(v, unit) for v in FLOW_MINIMUM_C],
             "maximum_range": [flow_shown(v, unit) for v in FLOW_MAXIMUM_C],
             "floor_maximum": flow_shown(FLOOR_FLOW_WARNING_C, unit),
             "floor": any(type(room) is dict and room.get("emitter") == "floor" for room in plan.get("rooms", []))}
    tick = type(plan.get(MINIMUM_AUTOMATIC_KEY)) is bool
    if tick:
        model[MINIMUM_AUTOMATIC_KEY] = plan[MINIMUM_AUTOMATIC_KEY]
    boiler = _boiler_maximum(hass, entry)
    model["live"] = {"boiler_maximum": flow_shown(boiler, unit) if boiler is not None else None,
                     "minimum_now": _minimum_now(_hub(hass, entry), unit) if tick else None}
    return model


async def _save_limits(hass, entry, values):
    from .e32_flow import async_save_limits, limit_edits, limit_warnings, temperature_unit
    from .e32_room_flow import MINIMUM_AUTOMATIC_FIELD, FlowError
    link, plan = await _limits_plan(hass, entry)
    unit = temperature_unit(hass)
    try:
        edits, _low, high = limit_edits(plan, values.get(MINIMUM_AUTOMATIC_FIELD), values.get("minimum_flow_temperature"),
                                        values.get("maximum_flow_temperature"), unit)
    except FlowError as err:
        raise SettingsError(err.key, **_ranges(unit)) from None
    if not edits:
        return None
    warnings = limit_warnings(plan, high, _boiler_maximum(hass, entry))
    if warnings and values.get("confirmed") is not True:
        # The panel asks first (its confirm); a save without that answer gets the flow's warning, on its field.
        field = next(iter(warnings))
        raise SettingsError(warnings[field], field, **_ranges(unit))
    try:
        await async_save_limits(link, edits)
    except HomeAssistantError as err:
        raise _plan_failure(err) from None
    return None


# -- the heating circuits --------------------------------------------------------------------------------------------

async def _circuit_record(hass, entry):
    from .e32_shelly import pump_settings, record_circuits, shelly_link
    _plan_link(hass, entry)
    link = shelly_link(hass, entry)
    try:
        record = await link.async_record()
    except HomeAssistantError as err:
        raise SettingsError("heating_circuit_failed", error=_code(err)) from None
    pumps = [(c, pump_settings(record, c["id"])) for c in record_circuits(record)]
    return link, [(c, settings) for c, settings in pumps if settings is not None]


def _code(err):
    return (getattr(err, "translation_placeholders", None) or {}).get("error") or getattr(err, "translation_key", None) \
        or "unknown"


async def _read_circuits(hass, entry):
    _link, pumps = await _circuit_record(hass, entry)
    model = {"circuits": [{"id": c["id"], "kind": c.get("kind")} for c, _ in pumps]}
    for circuit, settings in pumps:
        for key, value in settings.items():
            model[f"{key}:{circuit['id']}"] = value
    return model


async def _save_circuits(hass, entry, values):
    from .e32_shelly import pump_changes
    link, pumps = await _circuit_record(hass, entry)
    writes = []
    for circuit, current in pumps:
        cid = circuit["id"]
        changes, errors, _wanted = pump_changes(
            current, values.get(f"control:{cid}", current["control"]),
            values.get(f"max_supply_c:{cid}", current["max_supply_c"]),
            values.get(f"run_on_max_minutes:{cid}", current["run_on_max_minutes"]))
        if errors:
            field = next(iter(errors))
            raise SettingsError(errors[field], "base" if field == "base" else f"{field}:{cid}", error="invalid_value")
        if changes:
            writes.append((cid, changes))
    for cid, changes in writes:
        try:
            await link.async_pump_settings(cid, changes)
        except HomeAssistantError as err:
            raise SettingsError("heating_circuit_failed", error=_code(err)) from None
    return None


# -- Comfort and boiler care ----------------------------------------------------------------------------------------

def _care_failure(err):
    from .e32_care import _failure
    key, placeholders = _failure(err)
    return SettingsError(key, **placeholders)


async def _care_settings(hass, entry):
    """(link, settings) read from the E32 now (the self-tuning moves the values in effect)."""
    link = _flow_link(hass, entry, create=True)
    if link is None:
        raise SettingsError("connect_e32")
    try:
        settings = await link.async_read_now()
    except HomeAssistantError as err:
        raise _care_failure(err) from None
    if "tuning_manual" not in settings:
        raise SettingsError("care_update_required")
    return link, settings


async def _read_care(hass, entry):
    from .e32_care import KNOBS, shown_value
    _link, settings = await _care_settings(hass, entry)
    tuning, manual = settings["tuning"], settings["tuning_manual"]
    model = {"knobs": []}
    for key, (auto, default, low, high, step, unit, _scale, _decimals) in KNOBS.items():
        model["knobs"].append({"key": key, "automatic_knob": auto, "standard": shown_value(key, default), "min": low,
                               "max": high, "step": step, "unit": unit})
        if auto:
            model[f"auto:{key}"] = key not in manual
        model[f"value:{key}"] = shown_value(key, tuning[key])
    return model


async def _save_care(hass, entry, values):
    from .e32_care import KNOBS, changes_for, range_text, stored_value
    from .learned_overview import language
    link, settings = await _care_settings(hass, entry)
    action = values.get("action")
    if action is not None:
        if action not in ("auto_all", "reset"):
            raise SettingsError("care_rejected", error="invalid_action")
        change = {"tuning_manual": []} if action == "auto_all" else {"tuning": None}
    else:
        tuning, manual, wanted = settings["tuning"], settings["tuning_manual"], {}
        for key, knob in KNOBS.items():
            automatic = knob[0] and values.get(f"auto:{key}", key not in manual) is True
            if automatic:
                if key in manual:
                    wanted[key] = (True, tuning[key])
                continue
            try:
                wanted[key] = (False, stored_value(key, values.get(f"value:{key}")))
            except ValueError as err:
                raise SettingsError(str(err), f"value:{key}", range=range_text(key, language(hass))) from None
        change = changes_for(settings, wanted)
        if change is None:
            return None
    try:
        await link.async_change(change)
    except HomeAssistantError as err:
        raise _care_failure(err) from None
    return None


# -- the boiler model -----------------------------------------------------------------------------------------------

def _recognised(hass, entry):
    """What the E32 recognised on the bus (boiler_capabilities), language-neutral: the panel words it as Configure."""
    from .boiler_capabilities import current, family_name, row, sentence_key
    doc = current(hass, entry.entry_id)
    if not doc:
        return None
    return {"name": row(doc)[1] or family_name(doc), "product": doc.get("product"), "version": doc.get("version"),
            "sentence": sentence_key(doc)}


async def _boiler_model(hass, entry):
    from .controller_link import ControllerLinkError
    from .e32_boiler_model import async_read_model, models, options
    from .e32_system import failure, link_for
    from .ems_devices import products
    link = link_for(hass, entry)
    if link is None:
        raise SettingsError("connect_e32")
    await hass.async_add_executor_job(products)  # read once, never in the event loop
    if not models():
        raise SettingsError("e32_settings_update_required")
    try:
        current = await async_read_model(link)
    except ControllerLinkError as err:
        key, placeholders = failure(err)
        raise SettingsError(key, **placeholders) from None
    return link, current, [c for c in options(current, "en") if c["value"] != "none"]


async def _read_model(hass, entry):
    _link, current, choices = await _boiler_model(hass, entry)
    return {"model": current, "options": choices, "live": {"recognised": _recognised(hass, entry)}}


async def _save_model(hass, entry, values):
    from .controller_link import ControllerLinkError
    from .e32_boiler_model import NONE, async_save_model
    from .e32_system import failure
    link, current, choices = await _boiler_model(hass, entry)
    chosen = values.get("model")
    if chosen != NONE and chosen not in {c["value"] for c in choices}:
        raise SettingsError("boiler_model_invalid", "model")
    if chosen == current:
        return None
    try:
        confirmed = await async_save_model(hass, entry, link, chosen)
    except ControllerLinkError as err:
        key, placeholders = failure(err)
        raise SettingsError(key, **placeholders) from None
    if not confirmed:
        raise SettingsError("e32_settings_unconfirmed")
    return None


# -- the section ----------------------------------------------------------------------------------------------------

READ = {"flow": _read_flow, "limits": _read_limits, "circuits": _read_circuits, "care": _read_care, "model": _read_model}
SAVE = {"flow": _save_flow, "limits": _save_limits, "circuits": _save_circuits, "care": _save_care, "model": _save_model}


async def read_heating(hass, entry, item=None):
    if item is None:
        _plan_link(hass, entry)
        from .ems_devices import products
        await hass.async_add_executor_job(products)  # the boiler catalog names the model: read once, off the loop
        return _list(hass, entry)
    if item not in READ:
        raise SettingsError("unknown_section")
    return {**await READ[item](hass, entry), "screen": item}  # the panel's module draws the screen its model names


async def save_heating(hass, entry, item, values):
    if item not in SAVE:
        raise SettingsError("unknown_section")  # the list itself saves nothing
    await SAVE[item](hass, entry, values)
    return None  # the core reads the screen again: the fresh model


register_section("heating", read_heating, save_heating)
