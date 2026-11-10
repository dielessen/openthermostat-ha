"""Configure → Heating and boiler → Boiler settings (track W, W2), and the Repair after a revert that failed.

The menu (only when the E32 sends fw/telemetry/boiler_settings and its connection is stored):

- "Allow the E32 to change boiler settings" with the risk in plain words and a tick box (off by default:
  ``POST /boiler/settings/persistent {"enabled": true, "risk_accepted": true}``), or "Stop the E32 changing
  boiler settings";
- the everyday (user-level) settings with their value now, their range and whether they are verified on this
  boiler, in the menu text; "Change a setting" picks one of them;
- "Advanced (installer settings)": every setting and the boiler's whole range, at your own risk (a tick box);
- while a change is watched: "The change you are watching".

A change: ``POST /boiler/settings/write``. A setting verified on this boiler is written at once and read back
("Saved"). Any other one answers ``attendance_required``: the flow resends at once with the token (the E32 wants
it within 60 s) and, once the boiler read the new value back, asks: "Watch your boiler for up to 15 minutes.
Keep the new value, or put it back?" (``POST /boiler/settings/confirm`` with the token Home Assistant kept, on
a new sign-in). "Done" leaves the watch running: the E32 puts the value back by itself after 15 minutes (a
notification says so). Home Assistant holds no E32 session during the watch (W1b), and the other E32 writes keep
working. Switching heating or hot water off is asked first: it really switches it off on the boiler.
"""
from __future__ import annotations

from homeassistant.components.repairs import RepairsFlow
from homeassistant.config_entries import OptionsFlow
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .e32_boiler_settings import (
    FAILED_ISSUE, REVERTED, ROWS, SWITCHES_OFF_WARNED, SettingsCall, boiler_settings_state, choices,
    decode_document, range_text, remember_watch, result_of, settled_for, setting_name, value_text,
    verification_text, watch_of, watching_for)

TEXTS = "boiler_settings_text"

# The E32's refusal names (docs/RESTAPI.md) → the form error in plain words. Since E32 1.1.1 (K15) a setting can be
# changed while the E32 drives the boiler; 409 active_heat_owns_boiler now only means a planned restart or a
# firmware upload is coming (its own text: try again in a minute).
REFUSALS = {
    "value_out_of_range": "boiler_setting_out_of_range", "unknown_setting": "boiler_setting_out_of_range",
    "invalid_request": "boiler_setting_out_of_range", "above_system_maximum": "boiler_setting_above_maximum",
    "advanced_required": "boiler_setting_advanced", "persistent_writes_off": "boiler_setting_writes_off",
    "settings_writes_unavailable": "boiler_setting_unavailable", "risk_not_accepted": "boiler_settings_confirm",
    "boiler_not_available": "boiler_setting_not_now", "active_heat_owns_boiler": "boiler_setting_restarting",
    "boiler_identity_unknown": "boiler_setting_not_now", "settings_transport_fault": "boiler_setting_not_now",
    "unsupported_on_this_boiler": "boiler_setting_unsupported", "check_boiler_first": "boiler_setting_check_boiler",
    "too_soon_for_this_setting": "boiler_setting_too_soon", "daily_limit_reached": "boiler_setting_daily_limit",
    "settings_busy": "boiler_setting_busy", "settings_write_active": "boiler_setting_busy",
    "attended_token_invalid": "boiler_setting_busy", "different_operator": "boiler_setting_busy",
    "nothing_to_confirm": "boiler_setting_busy", "store_failed": "boiler_setting_store_failed",
}
# The E32's result of a finished change → the line shown on top of the Boiler settings menu (or, failed, the end).
RESULTS = {
    "written": "boiler_setting_saved", "kept": "boiler_setting_kept", "unchanged": "boiler_setting_unchanged",
    "reverted_by_user": "boiler_setting_put_back", "not_taken": "boiler_setting_not_taken",
    "rejected": "boiler_setting_rejected", "boiler_restored": "boiler_setting_restored",
    "not_started": "boiler_setting_not_started", "attendance_expired": "boiler_setting_not_started",
    "failed": "boiler_setting_failed", **{result: "boiler_setting_reverted" for result in REVERTED},
}
# Reasons shown as the menu again with their line (options_navigation SAVED_REASONS): every result but failed.
MENU_RESULTS = frozenset(set(RESULTS.values()) - {"boiler_setting_failed", "boiler_setting_unchanged"}) | {
    "boiler_settings_allowed", "boiler_settings_stopped", "boiler_setting_pending"}
UNCHANGED_RESULTS = frozenset({"boiler_setting_unchanged"})


def refusal(error):
    return REFUSALS.get(error, "boiler_setting_refused")


# -- one back end for Configure and the settings panel (1.4.1, settings_heating item "boiler") --------------------
#
# The steps below and the panel's actions call these functions, so the same input sends the same E32 requests and
# stores the same thing. They raise ControllerLinkError (BoilerSettingsRejected for a named refusal of the E32).

# The state of boiler settings in one word (the menu's "Changing boiler settings: ..." line, texts "state_<key>").
STATES = ("unavailable", "blocked", "busy", "off", "not_now", "on")


async def async_read_document(link):
    """The settings document, read on one short sign-in."""
    from .controller_link import ControllerLinkError
    from .e32_system import async_e32_call
    doc = decode_document(await async_e32_call(link, lambda c: c.async_boiler_settings(), write=False))
    if doc is None:
        raise ControllerLinkError("controller_response_invalid")
    return doc


def state_of(doc):
    """unavailable (not on this E32), blocked (a put-back to check), busy (a change runs), off, not_now or on."""
    if not doc["compiled"]:
        return "unavailable"
    if doc["unresolved"]:
        return "blocked"
    if doc["transaction"] is not None:
        return "busy"
    if not doc["persistent"]:
        return "off"
    if doc["reason"] not in ("ready", ""):
        return "not_now"
    return "on"


def candidates(doc, advanced):
    """The settings that can be chosen: not unsupported by this boiler, the installer ones only under Advanced."""
    settings = (doc or {}).get("settings", {})
    return [s for s, row in ROWS.items() if s in settings and settings[s]["verification"] != "unsupported"
            and (advanced or row.level == "user")]


def value_range(item, advanced):
    """(lowest, highest) a value may be: the everyday range, or under Advanced the boiler's whole range."""
    return (item["minimum"], item["maximum"]) if advanced else (item["user_minimum"], item["user_maximum"])


def value_outcome(setting, item, advanced, raw):
    """(value, what next) of a new value: out_of_range, unchanged, switch_off (ask first) or write."""
    low, high = value_range(item, advanced)
    value = _whole(raw)
    if value is None or not low <= value <= high:
        return value, "out_of_range"
    if value == item["value"]:
        return value, "unchanged"
    if setting in SWITCHES_OFF_WARNED and value == 0:
        return value, "switch_off"
    return value, "write"


async def async_switch(link, enabled):
    """The owner's switch: allowed (with the risk accepted) or stopped."""
    from .controller_link import BOILER_SETTINGS_PERSISTENT
    from .e32_system import async_e32_call
    body = {"enabled": True, "risk_accepted": True} if enabled else {"enabled": False}
    await async_e32_call(link, lambda c: c.async_boiler_settings_post(BOILER_SETTINGS_PERSISTENT, body), write=True)


async def async_write(link, setting, value, advanced):
    """Write one value: (the E32's document after it, the watcher's token or None); (None, None) when the E32 asked
    for a watch without giving the token (another change runs)."""
    from .controller_link import BOILER_SETTINGS_WRITE
    from .e32_system import async_e32_call
    body = {"id": setting, "value": value, **({"advanced": True} if advanced else {})}

    async def write(client):
        call = SettingsCall(client)
        _, answer, _ = await call.async_post(BOILER_SETTINGS_WRITE, body)
        if answer != "attendance_required":
            return await call.async_until(settled_for(setting)), None
        if not call.token:
            return None, None
        # The E32 wants the same request with its token within 60 s, on the same sign-in: this form watches.
        await call.async_post(BOILER_SETTINGS_WRITE, {**body, "attended_token": call.token})
        return await call.async_until(watching_for(setting)), call.token

    return await async_e32_call(link, write, write=True)  # signs out after the readback


def after_write(hass, entry, doc, token, setting):
    """(busy | watch | pending | done, the E32's result when done) after async_write; keeps the watch's token."""
    if doc is None:
        return "busy", None
    if not settled_for(setting)(doc):
        # Watched, or still busy: the E32 goes on by itself; Home Assistant keeps only the token.
        remember_watch(hass, entry, doc, token)
        if doc["phase"] == "watching" and token:
            return "watch", None
        return "pending", None
    return "done", result_of(doc, setting)


async def async_confirm(link, watch, keep):
    """Keep or put back the watched change: one new sign-in with the token; the E32's document after it."""
    from .controller_link import BOILER_SETTINGS_CONFIRM, BoilerSettingsRejected
    from .e32_system import async_e32_call
    setting = watch.setting

    async def confirm(client):
        call = SettingsCall(client)
        try:
            await call.async_post(BOILER_SETTINGS_CONFIRM, {"attended_token": watch.token, "keep": keep})
        except BoilerSettingsRejected:
            await call.async_read()  # it ended meanwhile (the window, a switch-off): say how
        return await call.async_until(settled_for(setting))

    return await async_e32_call(link, confirm, write=True)


def after_confirm(hass, entry, doc, setting):
    """The E32's result after async_confirm, or None while it still works on it; a finished watch is forgotten."""
    if not settled_for(setting)(doc):
        return None
    watch_of(hass, entry, doc)  # the watch is over: forget its token
    return result_of(doc, setting) or doc.get("last")


def result_reason(hass, entry, last):
    """The reason key of the E32's result (RESULTS; none yet: boiler_setting_pending); a failed put-back raises the
    Repair at once (the telemetry follows)."""
    reason = RESULTS.get((last or {}).get("result"), "boiler_setting_pending")
    if reason == "boiler_setting_failed":
        state = boiler_settings_state(hass, entry)
        if state is not None:
            state.sync_failure(True, last)
    return reason


def result_values(last, setting, value):
    """(setting, value, before) a result speaks of: the E32's own when it names one, else what was asked."""
    if last is not None and last.get("id") in ROWS:
        setting = last["id"]
    return setting, (last or {}).get("requested", value), (last or {}).get("before")


async def async_acknowledge(link):
    """The owner checked the boiler after a put-back that failed: the E32 may write again. Already cleared (a
    restart put it back) counts as done."""
    from .controller_link import BOILER_SETTINGS_CONFIRM, BoilerSettingsRejected
    from .e32_system import async_e32_call
    try:
        await async_e32_call(link, lambda c: c.async_boiler_settings_post(
            BOILER_SETTINGS_CONFIRM, {"acknowledge_failure": True}), write=True)
    except BoilerSettingsRejected as err:
        if err.error != "nothing_to_acknowledge":
            raise


class BoilerSettingsSteps:
    """Mixin for the product options flow: Heating and boiler → Boiler settings."""

    _bs_doc = None
    _bs_setting = None
    _bs_value = None
    _bs_advanced = False

    async def _bs_texts(self):
        from .options_navigation import async_flow_texts
        return await async_flow_texts(self.hass, TEXTS)

    def _bs_link(self):
        from .e32_system import link_for
        return link_for(self.hass, self.config_entry)

    def _bs_failure(self, err, errors=None, placeholders=None):
        """A failed E32 request: an abort, or (errors given) the form error; returns the abort or None."""
        from .e32_system import ABORTS, failure
        key, values = failure(err)
        if errors is None or key in ABORTS:
            if key not in ABORTS:
                key = "e32_settings_unreachable"
            return self.async_abort(reason=key, description_placeholders=values)
        errors["base"] = key
        if placeholders is not None:
            placeholders.update(values)
        return None

    async def _bs_read(self):
        """The settings document, read on one short sign-in."""
        return await async_read_document(self._bs_link())

    # -- the menu --------------------------------------------------------------------------------------------

    async def async_step_boiler_settings(self, user_input=None):
        from .controller_link import ControllerLinkError
        if self._bs_link() is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        try:
            doc = self._bs_doc = await self._bs_read()
        except ControllerLinkError as err:
            return self._bs_failure(err)
        texts = await self._bs_texts()
        options = []
        if watch_of(self.hass, self.config_entry, doc) is not None and doc["phase"] == "watching":
            options.append("boiler_settings_watch")
        options.append("boiler_settings_stop" if doc["persistent"] else "boiler_settings_allow")
        if doc["persistent"]:
            options += ["boiler_settings_pick", "boiler_settings_advanced"]
        return self.async_show_menu(step_id="boiler_settings", menu_options=options, description_placeholders={
            "state": self._bs_state(texts, doc), "settings": self._bs_list(texts, doc)})

    @staticmethod
    def _bs_state(texts, doc):
        state = state_of(doc)
        if state == "busy":
            return texts["state_busy"].format(setting=setting_name(texts, doc["transaction"]["id"]))
        if state == "on":
            return texts["state_on"].format(used=doc["writes_today"], cap=doc["daily_cap"])
        return texts["state_" + state]

    @staticmethod
    def _bs_list(texts, doc):
        lines = []
        for setting, row in ROWS.items():
            item = doc["settings"].get(setting)
            if row.level != "user" or item is None:
                continue
            # The same layout in every language: the pieces are translated.
            lines.append(f"- **{setting_name(texts, setting)}**: {value_text(texts, setting, item['value'])} "
                         f"({range_text(texts, setting, item['user_minimum'], item['user_maximum'])}) · "
                         f"{verification_text(texts, item['verification'])}")
        return "\n".join(lines)

    # -- the owner's switch ----------------------------------------------------------------------------------

    async def async_step_boiler_settings_allow(self, user_input=None):
        from homeassistant.helpers import selector
        import probatio as vol
        errors, placeholders = {}, {"cap": str((self._bs_doc or {}).get("daily_cap", 12)), "error": ""}
        if user_input is not None:
            if not user_input.get("confirm"):
                errors["base"] = "boiler_settings_confirm"
            else:
                done = await self._bs_switch(True, errors, placeholders)
                if done is not None:
                    return done
        return self.async_show_form(step_id="boiler_settings_allow", errors=errors,
                                    description_placeholders=placeholders, data_schema=vol.Schema({
                                        vol.Required("confirm", default=False): selector.BooleanSelector()}))

    async def async_step_boiler_settings_stop(self, user_input=None):
        import probatio as vol
        errors, placeholders = {}, {"error": ""}
        if user_input is not None:
            done = await self._bs_switch(False, errors, placeholders)
            if done is not None:
                return done
        return self.async_show_form(step_id="boiler_settings_stop", errors=errors,
                                    description_placeholders=placeholders, data_schema=vol.Schema({}))

    async def _bs_switch(self, enabled, errors, placeholders):
        from .controller_link import BoilerSettingsRejected, ControllerLinkError
        link = self._bs_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        try:
            await async_switch(link, enabled)
        except BoilerSettingsRejected as err:
            errors["base"], placeholders["error"] = refusal(err.error), err.error
            return None
        except ControllerLinkError as err:
            return self._bs_failure(err, errors, placeholders)
        self._bs_doc = None
        # Placeholders make the menu show this step's own line instead of a plain "Saved." (options_navigation).
        return self.async_abort(reason="boiler_settings_allowed" if enabled else "boiler_settings_stopped",
                                description_placeholders={"enabled": "on" if enabled else "off"})

    # -- choosing a setting and its value --------------------------------------------------------------------

    def _bs_candidates(self, advanced):
        return candidates(self._bs_doc, advanced)

    def _bs_options(self, texts, advanced):
        settings = self._bs_doc["settings"]
        return [{"value": s, "label": f"{setting_name(texts, s)}: {value_text(texts, s, settings[s]['value'])} · "
                                      f"{verification_text(texts, settings[s]['verification'])}"}
                for s in self._bs_candidates(advanced)]

    async def async_step_boiler_settings_pick(self, user_input=None):
        return await self._bs_pick("boiler_settings_pick", False, user_input)

    async def async_step_boiler_settings_advanced(self, user_input=None):
        return await self._bs_pick("boiler_settings_advanced", True, user_input)

    async def _bs_pick(self, step_id, advanced, user_input):
        from homeassistant.helpers import selector
        import probatio as vol
        if self._bs_doc is None:
            return await self.async_step_boiler_settings()
        texts = await self._bs_texts()
        errors = {}
        if user_input is not None:
            setting = user_input.get("setting")
            if setting not in self._bs_candidates(advanced):
                errors["setting"] = "boiler_setting_unknown"
            elif advanced and not user_input.get("own_risk"):
                errors["own_risk"] = "boiler_settings_own_risk"
            else:
                self._bs_setting, self._bs_advanced = setting, advanced
                return await self.async_step_boiler_settings_value()
        fields = {vol.Required("setting", default=(user_input or {}).get("setting", vol.UNDEFINED)):
                  selector.SelectSelector(selector.SelectSelectorConfig(
                      options=self._bs_options(texts, advanced), mode=selector.SelectSelectorMode.DROPDOWN))}
        if advanced:
            fields[vol.Required("own_risk", default=False)] = selector.BooleanSelector()
        return self.async_show_form(step_id=step_id, data_schema=vol.Schema(fields), errors=errors)

    async def async_step_boiler_settings_value(self, user_input=None):
        from homeassistant.helpers import selector
        import probatio as vol
        setting = self._bs_setting
        if self._bs_doc is None or setting not in self._bs_doc["settings"]:
            return await self.async_step_boiler_settings()
        texts = await self._bs_texts()
        item, row = self._bs_doc["settings"][setting], ROWS[setting]
        low, high = value_range(item, self._bs_advanced)
        current = item["value"]
        verified = item["verification"] == "verified"
        placeholders = {"setting": setting_name(texts, setting), "current": value_text(texts, setting, current),
                        "range": range_text(texts, setting, low, high),
                        "verification": texts["how_verified" if verified else "how_watched"], "error": ""}
        errors = {}
        if user_input is not None:
            value, outcome = value_outcome(setting, item, self._bs_advanced, user_input.get("value"))
            if outcome == "out_of_range":
                errors["value"] = "boiler_setting_out_of_range"
            elif outcome == "unchanged":
                return self.async_abort(reason="boiler_setting_unchanged", description_placeholders={
                    "setting": placeholders["setting"], "value": value_text(texts, setting, value)})
            else:
                self._bs_value = value
                if outcome == "switch_off":
                    return await self.async_step_boiler_settings_off()
                result = await self._bs_start(errors, placeholders)
                if result is not None:
                    return result
        default = (user_input or {}).get("value", current if current is not None and low <= current <= high else low)
        if row.kind == "number":
            field = selector.NumberSelector(selector.NumberSelectorConfig(
                min=low, max=high, step=1, mode=selector.NumberSelectorMode.BOX,
                unit_of_measurement={"degC": "°C"}.get(row.unit, row.unit)))
        else:
            field = selector.SelectSelector(selector.SelectSelectorConfig(
                options=choices(texts, setting, low, high), mode=selector.SelectSelectorMode.LIST))
            default = str(default)
        return self.async_show_form(step_id="boiler_settings_value", errors=errors,
                                    description_placeholders=placeholders,
                                    data_schema=vol.Schema({vol.Required("value", default=default): field}))

    async def async_step_boiler_settings_off(self, user_input=None):
        """Switching heating or hot water off on the boiler: said plainly before anything is sent."""
        import probatio as vol
        setting = self._bs_setting
        if setting not in SWITCHES_OFF_WARNED or self._bs_value != 0:
            return await self.async_step_boiler_settings()
        texts = await self._bs_texts()
        placeholders = {"what": texts[SWITCHES_OFF_WARNED[setting]], "error": ""}
        errors = {}
        if user_input is not None:
            result = await self._bs_start(errors, placeholders)
            if result is not None:
                return result
        return self.async_show_form(step_id="boiler_settings_off", errors=errors,
                                    description_placeholders=placeholders, data_schema=vol.Schema({}))

    # -- the write, the watch and the result -----------------------------------------------------------------

    async def _bs_start(self, errors, placeholders):
        """Write the chosen value; the watch, the result or (None) a form error."""
        from .controller_link import BoilerSettingsRejected, ControllerLinkError
        link = self._bs_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        setting = self._bs_setting
        try:
            doc, token = await async_write(link, setting, self._bs_value, self._bs_advanced)
        except BoilerSettingsRejected as err:
            errors["base"], placeholders["error"] = refusal(err.error), err.error
            return None
        except ControllerLinkError as err:
            return self._bs_failure(err, errors, placeholders)
        outcome, last = after_write(self.hass, self.config_entry, doc, token, setting)
        if outcome == "busy":
            errors["base"] = "boiler_setting_busy"
            return None
        self._bs_doc = doc
        if outcome == "watch":
            return await self.async_step_boiler_settings_watch()
        return await self._bs_result(last, setting)

    async def async_step_boiler_settings_watch(self, user_input=None):
        watch = watch_of(self.hass, self.config_entry, self._bs_doc)
        if watch is None:
            return await self.async_step_boiler_settings()
        texts = await self._bs_texts()
        setting = watch.setting
        return self.async_show_menu(step_id="boiler_settings_watch", menu_options=[
            "boiler_settings_keep", "boiler_settings_put_back", "boiler_settings_leave"], description_placeholders={
            "setting": setting_name(texts, setting), "value": value_text(texts, setting, watch.value),
            "before": value_text(texts, setting, watch.before),
            "until": dt_util.as_local(watch.until).strftime("%H:%M")})

    async def async_step_boiler_settings_keep(self, user_input=None):
        return await self._bs_confirm(True)

    async def async_step_boiler_settings_put_back(self, user_input=None):
        return await self._bs_confirm(False)

    async def async_step_boiler_settings_leave(self, user_input=None):
        """Done: the watch goes on; the E32 puts the value back by itself at the end of its 15 minutes."""
        return OptionsFlow.async_create_entry(self, title="", data=dict(self.config_entry.options))

    async def _bs_confirm(self, keep):
        """Keep or put back the watched change: one new sign-in with the token, then the E32's result."""
        from .controller_link import ControllerLinkError
        watch = watch_of(self.hass, self.config_entry)
        if watch is None:
            return await self.async_step_boiler_settings()
        setting = watch.setting
        try:
            doc = await async_confirm(self._bs_link(), watch, keep)
        except ControllerLinkError as err:
            return self._bs_failure(err)
        self._bs_doc = doc
        return await self._bs_result(after_confirm(self.hass, self.config_entry, doc, setting), setting)

    async def _bs_result(self, last, setting):
        texts = await self._bs_texts()
        reason = result_reason(self.hass, self.config_entry, last)  # failed: the Repair at once
        setting, value, before = result_values(last, setting, self._bs_value)
        placeholders = {"setting": setting_name(texts, setting), "value": value_text(texts, setting, value),
                        "before": value_text(texts, setting, before)}
        return self.async_abort(reason=reason, description_placeholders=placeholders)


def _whole(value):
    """A whole number from the form (a number box or a select's text), else None."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number) if number == int(number) else None


class BoilerSettingFailedRepairFlow(RepairsFlow):
    """"Check the boiler: a setting could not be put back": the owner checked it; the E32 may write again."""

    def __init__(self, issue_id, data):
        self._issue_id, self._data = issue_id, data if isinstance(data, dict) else {}

    async def async_step_init(self, user_input=None):
        # Home Assistant opens a repair with data={"issue_id": ...} as this step's input: never a submitted form.
        return await self.async_step_boiler_setting_checked()

    async def async_step_boiler_setting_checked(self, user_input=None):
        from .controller_link import BoilerSettingsRejected, ControllerLinkError
        from .e32_system import failure, link_for
        entry = self.hass.config_entries.async_get_entry(self._data.get("entry_id"))
        link = link_for(self.hass, entry) if entry is not None else None
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        issue = ir.async_get(self.hass).async_get_issue(DOMAIN, self._issue_id)
        placeholders = {"setting": "-", "before": "-", "cause": "", **dict(getattr(issue, "translation_placeholders", None)
                                                                         or {}), "error": ""}
        errors = {}
        if user_input is not None:
            try:
                await async_acknowledge(link)  # already cleared (a restart put it back): done
            except BoilerSettingsRejected as err:
                errors["base"], placeholders["error"] = refusal(err.error), err.error
            except ControllerLinkError as err:
                key, values = failure(err)
                errors["base"] = key
                placeholders.update(values)
            if not errors:
                ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
                return self.async_create_entry(data={})
        import probatio as vol
        return self.async_show_form(step_id="boiler_setting_checked", errors=errors,
                                    description_placeholders=placeholders, data_schema=vol.Schema({}))


def issue_matches(issue_id):
    return issue_id.startswith(FAILED_ISSUE + "_")
