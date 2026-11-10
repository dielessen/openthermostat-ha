"""The settings panel's section Heating and boiler (1.4; settings.py registers it, the screens are
frontend/openthermostat-settings-heating.js; design docs/engineering/HA-INSTELPANEEL-ONTWERP.nl.md, chapter 5).

The screens (the panel's item; ``#heating/<item>``):

- ``None``: the list, what is set now from what Home Assistant already holds (the room plan it last read, the
  flow options the E32 last reported, the boiler model of its last profile, the circuits of its telemetry); no E32
  read. Read-only: each row opens its screen. ``live.boiler_settings`` (1.4.1) is the Boiler settings row's line from
  the telemetry Home Assistant holds (off, on, busy or blocked, the changes of today), no E32 read.
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
- ``boiler`` (1.4.1): Boiler settings, the boiler's own settings changed by the E32 on the owner's word, as
  Configure → Heating and boiler → Boiler settings shows them (one read of the E32, the words of Configure in Home
  Assistant's language beside the raw values). Nothing is saved through ``settings/save``: every change is an action
  of ``settings/action`` (``ACTIONS``: boiler_allow, boiler_stop, boiler_advanced, boiler_write, boiler_watch,
  boiler_checked, boiler_put_back), each one the Configure step's own function from e32_boiler_settings_flow, so
  the same input sends the same E32 requests and gets the same refusal keys. The E32's boiler settings routes have
  no If-Match: the E32 guards them itself (one change at a time, the watcher's token, the daily cap).

Every model is plain JSON in the user's unit; what only informs (the lowest water temperature now, the boiler's own
maximum, the recognised boiler) is under ``live``, which the token leaves out (settings.LIVE), so a new reading never
makes a save "changed elsewhere". Errors are the flow's own keys with their placeholders (the panel has a sentence for
each one).
"""
from __future__ import annotations

from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .settings import SettingsError, register_section

ITEMS = (None, "flow", "limits", "circuits", "care", "model", "boiler")


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
            "live": {"minimum_now": _minimum_now(hub, unit) if limits and limits["automatic"] else None,
                     "boiler_settings": _boiler_now(hass, entry)}}


def _boiler_now(hass, entry):
    """The Boiler settings row of the list (1.4.1): {state: off | on | busy | blocked, writes_today, preview} from the
    telemetry the E32 last sent (e32_boiler_settings), None while Configure offers no boiler settings. No E32 read."""
    from .e32_boiler_settings import boiler_settings_state, offered
    telemetry = getattr(boiler_settings_state(hass, entry), "telemetry", None)
    if telemetry is None or not offered(hass, entry):
        return None
    state = ("blocked" if telemetry["unresolved"] else "busy" if telemetry["transaction"] is not None or telemetry["phase"] != "idle"
             else "on" if telemetry["persistent"] else "off")
    return {"state": state, "writes_today": telemetry["writes_today"], "preview": PREVIEW}


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


# -- Boiler settings (1.4.1): the model and the actions, on Configure's own functions (e32_boiler_settings_flow) --------

# The word "preview" stays in the heading until a real boiler confirmed the boiler settings (plan 3.3).
PREVIEW = True
# Advanced (installer settings) stays open this long after its second confirmation (boiler_advanced), and closes
# when changing boiler settings is stopped or Home Assistant restarts. In memory only, per installation.
ADVANCED_KEY = "e32_boiler_settings_advanced"
ADVANCED_OPEN_S = 1800
# What a setting's value is shown in (the E32 table's units; a switch or a choice has none).
_UNITS = {"degC": "°C", "K": "K", "%": "%", "min": "min"}


def _when(moment):
    """A moment as ISO 8601 in UTC (the panel shows it in Home Assistant's locale and time format)."""
    from homeassistant.util import dt as dt_util
    return dt_util.as_utc(moment).replace(microsecond=0).isoformat() if moment is not None else None


def _boiler_link(hass, entry):
    """The E32 link for boiler settings; connect_e32 without a stored connection."""
    from .e32_system import link_for
    link = link_for(hass, entry)
    if link is None:
        raise SettingsError("connect_e32")
    return link


def _boiler_feature(hass, entry):
    """The link, on an E32 that sends boiler settings (Configure offers them only then); else the reason code."""
    from .e32_boiler_settings import offered
    link = _boiler_link(hass, entry)
    if not offered(hass, entry):
        raise SettingsError("e32_settings_update_required")
    return link


def _link_failure(err):
    """A failed or refused E32 request as the flow's error key: a named refusal of the E32 as its form error
    (with the E32's word in ``error``), any other failure as e32_system.failure says."""
    from .controller_link import BoilerSettingsRejected
    from .e32_boiler_settings_flow import refusal
    from .e32_system import failure
    if isinstance(err, BoilerSettingsRejected):
        return SettingsError(refusal(err.error), error=err.error)
    key, placeholders = failure(err)
    return SettingsError(key, **placeholders)


async def _boiler_document(link):
    from .controller_link import ControllerLinkError
    from .e32_boiler_settings_flow import async_read_document
    try:
        return await async_read_document(link)
    except ControllerLinkError as err:
        raise _link_failure(err) from None


async def _boiler_texts(hass):
    """The words Configure shows (Home Assistant's language): strings.json selector.boiler_settings_text."""
    from .e32_boiler_settings_flow import TEXTS
    from .options_navigation import async_flow_texts
    return await async_flow_texts(hass, TEXTS)


def _advanced_unlocked(hass, entry):
    from homeassistant.util import dt as dt_util
    until = _state(hass, entry).get(ADVANCED_KEY)
    return until is not None and dt_util.utcnow() < until


def _advanced_until(hass, entry):
    """When Advanced closes by itself (ISO 8601 UTC), while it is open: the panel says "Advanced open, {n} min left"."""
    return _when(_state(hass, entry).get(ADVANCED_KEY)) if _advanced_unlocked(hass, entry) else None


def _set_advanced(hass, entry, unlocked):
    from datetime import timedelta
    from homeassistant.util import dt as dt_util
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not isinstance(data, dict):
        return
    if unlocked:
        data[ADVANCED_KEY] = dt_util.utcnow() + timedelta(seconds=ADVANCED_OPEN_S)
    else:
        data.pop(ADVANCED_KEY, None)


def _allowed(row, low, high):
    """{min, max, step} of a number, or the list of values of a switch or a choice."""
    return {"min": low, "max": high, "step": 1} if row.kind == "number" else list(range(low, high + 1))


def _watch_model(texts, watch, doc):
    """The change Home Assistant watches (it holds the token): what to look for at the boiler, and until when."""
    from datetime import timedelta
    from .e32_boiler_settings import setting_name, value_text
    window = (doc or {}).get("watch_window_s", 900)
    setting = watch.setting
    return {"setting": setting, "name": setting_name(texts, setting), "value": watch.value,
            "value_text": value_text(texts, setting, watch.value), "before": watch.before,
            "before_text": value_text(texts, setting, watch.before),
            "since": _when(watch.until - timedelta(seconds=window)), "until": _when(watch.until),
            "state": (doc or {}).get("phase", "watching")}


def _said(texts, reason, last, setting, value):
    """The answer's words of a result: the reason key (strings.json options.abort) and its placeholders as
    Configure fills them, with the raw values beside them."""
    from .e32_boiler_settings import setting_name, value_text
    from .e32_boiler_settings_flow import result_values
    setting, value, before = result_values(last, setting, value)
    return {"result": reason, "setting": setting, "value": value, "before": before,
            "placeholders": {"setting": setting_name(texts, setting), "value": value_text(texts, setting, value),
                             "before": value_text(texts, setting, before)}}


def _unsupported(reason):
    return {"supported": False, "reason": reason, "preview": PREVIEW, "allowed": False, "state": None,
            "writes_today": 0, "daily_cap": 12, "settings": [], "advanced_unlocked": False, "advanced_until": None,
            "watch": None}


async def _read_boiler(hass, entry):
    """The boiler settings as Configure's menu shows them (one read of the E32, as the menu does)."""
    from .controller_link import ControllerLinkError
    from .e32_boiler_settings import (ROWS, SWITCHES_OFF_WARNED, choices, offered, setting_name, value_text,
                                      verification_text, watch_of)
    from .e32_boiler_settings_flow import async_read_document, state_of
    from .e32_system import failure
    link = _boiler_link(hass, entry)
    if not offered(hass, entry):
        return _unsupported("e32_settings_update_required")  # firmware without boiler settings: Configure has none
    try:
        doc = await async_read_document(link)
    except ControllerLinkError as err:
        key, placeholders = failure(err)
        if key == "e32_settings_update_required":
            return _unsupported(key)  # older firmware with the retained telemetry still on the broker
        raise SettingsError(key, **placeholders) from None
    if not doc["compiled"]:
        return _unsupported("boiler_setting_unavailable")
    texts = await _boiler_texts(hass)
    watch = watch_of(hass, entry, doc)
    transaction = doc["transaction"]
    settings = []
    for setting, row in ROWS.items():
        item = doc["settings"].get(setting)
        if item is None:
            continue
        pending = None
        if transaction is not None and transaction.get("id") == setting:
            ours = watch is not None and watch.setting == setting
            pending = {"value": transaction.get("value"), "before": transaction.get("before"), "phase": doc["phase"],
                       "since": _watch_model(texts, watch, doc)["since"] if ours else None, "ours": ours}
        low, high = item["user_minimum"], item["user_maximum"]
        settings.append({
            "key": setting, "name": setting_name(texts, setting), "kind": row.kind, "unit": _UNITS.get(row.unit),
            "current": item["value"], "current_text": value_text(texts, setting, item["value"]),
            "allowed": _allowed(row, low, high), "allowed_advanced": _allowed(row, item["minimum"], item["maximum"]),
            "choices": None if row.kind == "number" else [
                {"value": int(c["value"]), "label": c["label"]}
                for c in choices(texts, setting, item["minimum"], item["maximum"])],
            "advanced": row.level == "installer",
            "verification": item["verification"], "verification_text": verification_text(texts, item["verification"]),
            "changeable": item["verification"] != "unsupported",
            "switch_off_question": SWITCHES_OFF_WARNED.get(setting),
            "last_result": item["last_result"], "changed_by_e32": item["last_result"] in ("written", "kept"),
            "pending": pending})
    return {"supported": True, "reason": None, "preview": PREVIEW, "allowed": doc["persistent"],
            "state": state_of(doc), "writes_today": doc["writes_today"], "daily_cap": doc["daily_cap"],
            "settings": settings, "advanced_unlocked": _advanced_unlocked(hass, entry),
            "advanced_until": _advanced_until(hass, entry),
            "watch": _watch_model(texts, watch, doc) if watch is not None else None}


def _flag(values, key):
    value = values.get(key)
    if type(value) is not bool:
        raise SettingsError("boiler_setting_refused", key, error="invalid_request")
    return value


async def _boiler_allow(hass, entry, item, values):
    """= the steps boiler_settings_allow (the tick ``confirm``) and boiler_settings_stop."""
    from .controller_link import ControllerLinkError
    from .e32_boiler_settings_flow import async_switch
    allow = _flag(values, "allow")
    link = _boiler_feature(hass, entry)
    if allow and values.get("confirm") is not True:
        raise SettingsError("boiler_settings_confirm", "confirm")
    try:
        await async_switch(link, allow)
    except ControllerLinkError as err:
        raise _link_failure(err) from None
    if not allow:
        _set_advanced(hass, entry, False)
    return {"allowed": allow, "result": "boiler_settings_allowed" if allow else "boiler_settings_stopped"}


async def _boiler_stop(hass, entry, item, values):
    """= the step boiler_settings_stop (boiler_allow with allow false)."""
    return await _boiler_allow(hass, entry, item, {"allow": False})


async def _boiler_advanced(hass, entry, item, values):
    """The second confirmation of Advanced (installer settings): ``confirm`` true opens it, false closes it; without
    the answer, the step's refusal (boiler_settings_own_risk)."""
    confirm = values.get("confirm")
    _boiler_feature(hass, entry)
    if type(confirm) is not bool:
        raise SettingsError("boiler_settings_own_risk", "own_risk")
    _set_advanced(hass, entry, confirm)
    return {"advanced_unlocked": confirm}


async def _boiler_write(hass, entry, item, values):
    """= the steps boiler_settings_pick / _advanced, _value and _off: {setting, value, advanced?, confirm?}."""
    from .controller_link import ControllerLinkError
    from .e32_boiler_settings import SWITCHES_OFF_WARNED
    from .e32_boiler_settings_flow import after_write, async_write, candidates, result_reason, value_outcome
    link = _boiler_feature(hass, entry)
    setting, advanced = values.get("setting"), values.get("advanced") is True
    if advanced and not _advanced_unlocked(hass, entry):
        raise SettingsError("boiler_settings_own_risk", "own_risk")
    doc = await _boiler_document(link)
    if setting not in candidates(doc, advanced):
        raise SettingsError("boiler_setting_unknown", "setting")
    value, outcome = value_outcome(setting, doc["settings"][setting], advanced, values.get("value"))
    if outcome == "out_of_range":
        raise SettingsError("boiler_setting_out_of_range", "value")
    texts = await _boiler_texts(hass)
    if outcome == "unchanged":
        return {"written": False, "watch": None, **_said(texts, "boiler_setting_unchanged", None, setting, value)}
    if outcome == "switch_off" and values.get("confirm") is not True:
        # Configure's "Really switch it off?": the panel asks first and sends confirm.
        raise SettingsError("boiler_setting_switch_off", "value", what=texts[SWITCHES_OFF_WARNED[setting]],
                            what_key=SWITCHES_OFF_WARNED[setting])
    try:
        doc, token = await async_write(link, setting, value, advanced)
    except ControllerLinkError as err:
        raise _link_failure(err) from None
    outcome, last = after_write(hass, entry, doc, token, setting)
    if outcome == "busy":
        raise SettingsError("boiler_setting_busy")
    if outcome == "watch":
        from .e32_boiler_settings import watch_of
        return {"written": True, "watch": _watch_model(texts, watch_of(hass, entry), doc), "result": None}
    reason = result_reason(hass, entry, last)
    return {"written": reason == "boiler_setting_saved", "watch": None, **_said(texts, reason, last, setting, value)}


async def _ended(hass, entry, link, texts, setting):
    """No watch Home Assistant holds for this setting: read the E32 and say what is going on (nothing is written)."""
    from .e32_boiler_settings import result_of, watch_of
    from .e32_boiler_settings_flow import RESULTS
    doc = await _boiler_document(link)
    watch = watch_of(hass, entry, doc)
    if watch is not None and (setting is None or watch.setting == setting):
        return {"state": "watching" if doc["phase"] == "watching" else "writing", "confirmed": doc["phase"] == "watching",
                "watch": _watch_model(texts, watch, doc), "result": None}
    transaction = doc["transaction"]
    if transaction is not None and (setting is None or transaction.get("id") == setting):
        return {"state": "elsewhere", "confirmed": False, "watch": None, "result": None,
                "setting": transaction.get("id")}
    last = result_of(doc, setting) if setting is not None else doc["last"]
    reason = RESULTS.get(last["result"]) if last is not None else None
    said = _said(texts, reason, last, setting, None) if reason is not None else {"result": None}
    return {"state": "ended", "confirmed": False, "watch": None, **said}


async def _boiler_watch(hass, entry, item, values):
    """= the step boiler_settings_watch: what to look for at the boiler and whether the boiler read it back
    (``state`` watching), or how the change ended. One read of the E32; call it when the dialog opens, never in a
    loop (the E32 has four web sessions)."""
    link = _boiler_feature(hass, entry)
    return await _ended(hass, entry, link, await _boiler_texts(hass), values.get("setting"))


async def _confirm(hass, entry, values, keep):
    """= the steps boiler_settings_keep / _put_back: one sign-in with the kept token, then the E32's result."""
    from .controller_link import ControllerLinkError
    from .e32_boiler_settings import watch_of
    from .e32_boiler_settings_flow import after_confirm, async_confirm, result_reason
    link = _boiler_feature(hass, entry)
    texts, setting = await _boiler_texts(hass), values.get("setting")
    watch = watch_of(hass, entry)
    if watch is None or setting is not None and watch.setting != setting:
        return {"done": False, **await _ended(hass, entry, link, texts, setting)}  # it ended meanwhile: say how
    try:
        doc = await async_confirm(link, watch, keep)
    except ControllerLinkError as err:
        raise _link_failure(err) from None
    last = after_confirm(hass, entry, doc, watch.setting)
    reason = result_reason(hass, entry, last)
    return {"done": True, "state": "ended" if last is not None else "writing", "watch": None,
            **_said(texts, reason, last, watch.setting, watch.value)}


async def _boiler_put_back(hass, entry, item, values):
    return await _confirm(hass, entry, values, False)


async def _boiler_checked(hass, entry, item, values):
    """With ``setting``: the watched change; ``ok`` true keeps it (boiler_settings_keep), false is Done for now
    (boiler_settings_leave: the watch goes on, the E32 puts it back at ``until``). Without ``setting``: the Repair
    after a put-back that failed (boiler_setting_checked); ``ok`` true says the boiler was checked."""
    from homeassistant.helpers import issue_registry as ir
    from .controller_link import ControllerLinkError
    from .e32_boiler_settings import FAILED_ISSUE, watch_of
    from .e32_boiler_settings_flow import async_acknowledge
    ok = _flag(values, "ok")
    link = _boiler_feature(hass, entry)
    if values.get("setting") is not None:
        if ok:
            return await _confirm(hass, entry, values, True)
        watch = watch_of(hass, entry)
        texts = await _boiler_texts(hass)
        if watch is None or watch.setting != values["setting"]:
            return {"done": False, **await _ended(hass, entry, link, texts, values["setting"])}
        return {"done": True, "state": "watching", "watch": _watch_model(texts, watch, None), "result": None}
    if not ok:
        return {"acknowledged": False}
    try:
        await async_acknowledge(link)
    except ControllerLinkError as err:
        raise _link_failure(err) from None
    ir.async_delete_issue(hass, DOMAIN, f"{FAILED_ISSUE}_{entry.entry_id}")
    return {"acknowledged": True}


ACTIONS = {"boiler_allow": _boiler_allow, "boiler_write": _boiler_write, "boiler_watch": _boiler_watch,
           "boiler_checked": _boiler_checked, "boiler_put_back": _boiler_put_back, "boiler_stop": _boiler_stop,
           "boiler_advanced": _boiler_advanced}


# -- the section ----------------------------------------------------------------------------------------------------

READ = {"flow": _read_flow, "limits": _read_limits, "circuits": _read_circuits, "care": _read_care, "model": _read_model,
        "boiler": _read_boiler}
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


register_section("heating", read_heating, save_heating, actions=ACTIONS)
