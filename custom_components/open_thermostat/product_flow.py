"""Ordinary installation/room flows; configuration is not actuator authority.

Uses the existing HA subentry map, validators and versioned runtime. Historic
internal protocol names do not create a second user-facing test installation.
"""
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import logging

import probatio as vol
from homeassistant.data_entry_flow import section
from homeassistant.helpers import selector

from .const import CONF_CREATE_DASHBOARD, DOMAIN
from .product import (central_entry, commit_configuration, configuration_snapshot,
                      default_document)
from .product import INSTALLATION
from .room_setup_flow import RadiatorRoomSetupFlow
from .v1_config_flow import ShadowOptionsFlow, validate_room
from .v1_heating_flow import central_schema, draft_from_form
from .v1_heating_graph import actual_runtime_active, selected_reference, validated_graph
from .v1_model import CONF_ENABLED, MODE_SHADOW, integration_mode
from .native_form import retained_input_schema
from .schedule_compiler import WEEKDAYS
from .v1_program import normalize_program
from .controller_setup_flow import ControllerSetupFlow
from .legacy_rooms_flow import LegacyRoomsSteps
from .e32_room_flow import E32RoomFlow

_LOGGER = logging.getLogger(__name__)


def milliseconds(seconds):
    if type(seconds) not in (int, float):
        raise ValueError("invalid_integer_or_bounds")
    try:
        value = Decimal(str(seconds)) * 1000
        if not value.is_finite() or value != value.to_integral_value() or not 1000 <= value <= 86400000:
            raise ValueError("invalid_integer_or_bounds")
        return int(value)
    except InvalidOperation:
        raise ValueError("invalid_integer_or_bounds") from None


def _error(err):
    key = str(err)
    known = {"binding_missing", "loop_binding", "not_temperature", "unsupported_unit",
             "invalid_target_range", "program_source_conflict", "duplicate_room",
             "duplicate_actuator", "output_has_multiple_owners", "input_output_loop",
             "select_radiators", "invalid_name", "weather_requires_outdoor_source",
             "curve_must_not_fall_towards_cold_outdoors", "unused_fallback_must_be_null",
             "minimum_must_be_below_maximum", "invalid_integer_or_bounds",
             "single_central_owner", "setup_changed", "setup_platform_unsupported", "runtime_active",
             "advanced_room_required", "confirm_program_source_change", "emitter_not_available",
             "invalid_program", "program_overlap", "program_limit"}
    return key if key in known else "setup_invalid"



class ProductRoomFlow(RadiatorRoomSetupFlow):
    """One guided native flow for adding and editing ordinary radiator rooms."""

    async def async_step_user(self, user_input=None):
        from .room_plan import has_room_plan, uses_e32_rooms
        if has_room_plan(self._get_entry()):
            # Home Assistant may still show its cached button until a restart.
            return self.async_abort(reason="e32_rooms_elsewhere")
        if uses_e32_rooms(self._get_entry()):
            # A new installation: its rooms go on the E32, after Configure → Connect E32.
            return self.async_abort(reason="e32_connect_first")
        return await RadiatorRoomSetupFlow.async_step_user(self, {"room": "new"})

    async def async_step_reconfigure(self, user_input=None):
        return await self.async_step_edit_room(user_input)

    async def async_step_edit_room(self, user_input=None):
        """Existing rooms have one settings form; creation alone uses the wizard."""
        from .room_editor import read_room, save_room
        from .dashboard import RoomDashboard
        entry = self._get_entry()
        old = self._get_reconfigure_subentry()
        if not hasattr(self, '_edit_model'):
            try:
                self._edit_model = read_room(self.hass, entry.entry_id, old.data['room_id'])
            except (ValueError, KeyError):
                return self.async_abort(reason='setup_changed')
        model = self._edit_model
        values = model['settings']
        errors = {}
        if user_input is not None:
            settings = deepcopy(values)
            try:
                settings.update(name=user_input['name'], emitter=user_input['emitter'],
                    temperature_entity=user_input['temperature_entity'], radiator_entities=user_input['radiator_entities'])
                settings['base_centi_c'] = round(user_input['base_temperature'] * 100)
                advanced = user_input.get('advanced', {})
                for native, key in [('minimum_target_temperature', 'minimum_centi_c'), ('maximum_target_temperature', 'maximum_centi_c')]:
                    if native in advanced:
                        settings[key] = round(advanced[native] * 100)
                if 'maximum_age_seconds' in advanced:
                    settings['maximum_age_ms'] = milliseconds(advanced['maximum_age_seconds'])
                await save_room(self.hass, entry.entry_id, old.data['room_id'], model['token'], settings)
            except (KeyError, ValueError, vol.Invalid) as err:
                errors['base'] = _error(err)
            except Exception:
                _LOGGER.exception('Room edit save could not be confirmed')
                return self.async_abort(reason='setup_save_uncertain')
            else:
                return self.async_abort(reason='room_saved')
        number = selector.NumberSelector({'min': 5, 'max': 35, 'step': .1, 'mode': 'box', 'unit_of_measurement': '°C'})
        fields = {
            vol.Required('name', default=values['name']): str,
            vol.Required('emitter', default='radiator'): selector.SelectSelector({'options': ['radiator', 'floor', 'combined'], 'translation_key': 'product_emitter'}),
            vol.Required('temperature_entity', default=values['temperature_entity']): selector.EntitySelector({'filter': {'domain': 'sensor', 'device_class': 'temperature'}}),
            vol.Required('radiator_entities', default=values['radiator_entities']): selector.EntitySelector({'filter': {'domain': 'climate'}, 'multiple': True}),
            vol.Required('base_temperature', default=values['base_centi_c']/100): number,
            vol.Optional('advanced'): section(vol.Schema({
                vol.Required('minimum_target_temperature', default=values['minimum_centi_c']/100): number,
                vol.Required('maximum_target_temperature', default=values['maximum_centi_c']/100): number,
                vol.Required('maximum_age_seconds', default=values['maximum_age_ms']/1000): selector.NumberSelector({'min': 1, 'max': 86400, 'step': .001, 'mode': 'box', 'unit_of_measurement': 's'}),
            }), {'collapsed': True}),
        }
        dashboard = RoomDashboard(self.hass, entry.data.get('topic_prefix', entry.unique_id), entry.entry_id)
        return self.async_show_form(step_id='edit_room', data_schema=retained_input_schema(self, vol.Schema(fields), user_input),
            errors=errors, description_placeholders={'editor_url': '/' + dashboard.path + '/room-' + old.data['room_id']})

    async def async_step_radiator(self, user_input=None):
        # The parent starts here only after taking its snapshot and preparing IDs.
        if not hasattr(self, "_wizard_values"):
            data = dict(self._old.data) if self._old else {}
            schema = RadiatorRoomSetupFlow._radiator_schema(self)
            defaults = {str(k): k.default() for k in schema.schema
                        if k.default is not vol.UNDEFINED and str(k) != "advanced"}
            defaults.update(name=data.get("name", ""), program_action="save")
            self._wizard_values = defaults
        return await self.async_step_room(user_input)

    async def async_step_room(self, user_input=None):
        if guard := self._guard():
            return guard
        errors = {}
        if user_input is not None:
            if not user_input.get("name", "").strip() or len(user_input["name"]) > 80:
                errors["name"] = "invalid_name"
            elif user_input.get("emitter", "radiator") != "radiator":
                errors["emitter"] = "emitter_not_available"
            else:
                self._wizard_values["name"] = user_input["name"].strip()
                return await self.async_step_devices()
        schema = vol.Schema({
            vol.Required("name", default=self._wizard_values.get("name", "")): str,
            vol.Required("emitter", default="radiator"): selector.SelectSelector({
                "options": ["radiator", "floor", "combined"],
                "translation_key": "product_emitter"}),
        })
        return self.async_show_form(step_id="room", data_schema=retained_input_schema(
            self, schema, user_input), errors=errors)

    async def async_step_devices(self, user_input=None):
        if guard := self._guard():
            return guard
        values = self._wizard_values
        errors = {}
        if user_input is not None:
            values.update(user_input)
            try:
                outputs = values["radiator_entities"]
                if not 1 <= len(outputs) <= 8:
                    raise ValueError("select_radiators")
                self._radiators = [selected_reference(self.hass, x, ("climate",)) for x in outputs]
                self._prepare_graph(validate_room(self.hass, self._get_entry(),
                                                  self._submitted(values), self._old))
            except (KeyError, ValueError, vol.Invalid) as err:
                errors["base"] = _error(err)
            else:
                return await self.async_step_room_temperature()
        schema = vol.Schema({
            vol.Required("temperature_entity", default=values.get("temperature_entity", "")):
                selector.EntitySelector({"filter": {"domain": "sensor", "device_class": "temperature"}}),
            vol.Required("radiator_entities", default=values.get("radiator_entities", [])):
                selector.EntitySelector({"filter": {"domain": "climate"}, "multiple": True}),
        })
        return self.async_show_form(step_id="devices", data_schema=retained_input_schema(
            self, schema, user_input), errors=errors)

    async def async_step_room_temperature(self, user_input=None):
        if guard := self._guard():
            return guard
        values = self._wizard_values
        errors = {}
        if user_input is not None:
            submitted = deepcopy(user_input)
            advanced = submitted.get("advanced")
            try:
                if advanced is not None and "maximum_age_seconds" in advanced:
                    advanced["maximum_age_ms"] = milliseconds(advanced.pop("maximum_age_seconds"))
                values.update(submitted)
                result = await RadiatorRoomSetupFlow.async_step_radiator(self, values)
            except ValueError as err:
                errors["base"] = _error(err)
            else:
                if result.get("step_id") != "radiator":
                    return result
                errors = result.get("errors", {})
        base = RadiatorRoomSetupFlow._radiator_schema(self)
        kept = {key: val for key, val in base.schema.items()
                if str(key) in {"base_temperature", "program_action"}}
        # Retain the native collapsed section, but express report age in seconds.
        advanced_fields = {
            vol.Required("minimum_target_temperature", default=(dict(self._old.data) if self._old else {}).get("minimum_target_centi_c", 500)/100):
                selector.NumberSelector({"min": 5, "max": 35, "step": .1, "unit_of_measurement": "°C", "mode": "box"}),
            vol.Required("maximum_target_temperature", default=(dict(self._old.data) if self._old else {}).get("maximum_target_centi_c", 3500)/100):
                selector.NumberSelector({"min": 5, "max": 35, "step": .1, "unit_of_measurement": "°C", "mode": "box"}),
            vol.Required("maximum_age_seconds", default=(dict(self._old.data) if self._old else {}).get("maximum_age_ms", 120000)/1000):
                selector.NumberSelector({"min": 1, "max": 86400, "step": .001, "unit_of_measurement": "s", "mode": "box"}),
        }
        kept[vol.Optional("advanced")] = section(vol.Schema(advanced_fields), {"collapsed": True})
        defaults = {k: values[k] for k in ("base_temperature", "program_action") if k in values}
        if user_input is None:
            user_input = defaults
        return self.async_show_form(step_id="room_temperature", data_schema=retained_input_schema(
            self, vol.Schema(kept), user_input), errors=errors)

    async def async_step_program(self, user_input=None):
        result = await super().async_step_program(user_input)
        if result.get("type") == "menu":
            result["menu_options"].insert(3, "copy_day")
        return result

    async def async_step_copy_day(self, user_input=None):
        if guard := self._guard():
            return guard
        errors = {}
        if user_input is not None:
            try:
                source, targets = user_input["source_day"], user_input["target_days"]
                if source not in WEEKDAYS or not targets or any(t not in WEEKDAYS or t == source for t in targets):
                    raise ValueError("invalid_program")
                candidate = deepcopy(self._program_week)
                for day in targets:
                    candidate[day] = deepcopy(candidate[source])
                self._program_week = normalize_program(candidate,
                    self._program_room.minimum_target_centi_c, self._program_room.maximum_target_centi_c)
            except (KeyError, ValueError, vol.Invalid):
                errors["base"] = "invalid_program"
            else:
                return await self.async_step_program()
        return self.async_show_form(step_id="copy_day", data_schema=vol.Schema({
            vol.Required("source_day"): selector.SelectSelector({"options": list(WEEKDAYS), "translation_key": "program_days"}),
            vol.Required("target_days"): selector.SelectSelector({"options": list(WEEKDAYS), "multiple": True, "translation_key": "program_days"}),
        }), errors=errors)


from .e32_comfort import ComfortOptionsSteps  # noqa: E402
from .e32_backup_flow import E32RestoreSteps  # noqa: E402
from .e32_care import CareOptionsSteps  # noqa: E402
from .e32_system import SystemOptionsSteps  # noqa: E402
from .e32_boiler_model import BoilerModelSteps  # noqa: E402
from .e32_boiler_settings_flow import BoilerSettingsSteps  # noqa: E402
from .e32_bluetooth import BluetoothOptionsSteps  # noqa: E402
from .e32_devices import DevicesOptionsSteps  # noqa: E402
from .options_house_heating import HouseHeatingSteps  # noqa: E402
from .options_navigation import MenuNavigation  # noqa: E402
from .e32_shelly import CircuitOptionsSteps  # noqa: E402
from .e32_tester import TesterSteps  # noqa: E402
from .notifications_flow import NotificationOptionsSteps  # noqa: E402


class ProductOptionsFlow(MenuNavigation, NotificationOptionsSteps, HouseHeatingSteps, CircuitOptionsSteps, TesterSteps, E32RestoreSteps, CareOptionsSteps, SystemOptionsSteps, BoilerModelSteps, BoilerSettingsSteps, BluetoothOptionsSteps, DevicesOptionsSteps, ComfortOptionsSteps, E32RoomFlow, LegacyRoomsSteps, ControllerSetupFlow, ShadowOptionsFlow,
                         ProductRoomFlow):
    """One central options entrypoint, using the same room editor and native Store.

    With a stored E32 connection the rooms are the E32 room plan: "E32 rooms"
    replaces the older HA room settings in this menu.
    """

    def _get_entry(self):
        return self.config_entry

    def _get_reconfigure_subentry(self):
        return self.config_entry.subentries[self._managed_room]

    def _native_plan_review_available(self):
        connection = self._graph_connection()
        return connection is not None and connection.runtime.native_plan_source is not None

    async def async_step_init(self, user_input=None):
        from .options_navigation import async_flow_texts
        texts = await async_flow_texts(self.hass, "configure_text")
        return self.async_show_menu(step_id="init", menu_options=main_menu(self.config_entry), description_placeholders={
            "intro": texts["settings_page" if settings_page(self.config_entry) else "menu"]})

    async def async_step_open_settings(self, user_input=None):
        """Configure → "Open the settings page" (1.4): the everyday settings live on the dashboard's Settings tab. An
        options flow cannot navigate, so this step names the way there (with a link) and Done closes the dialog with
        the options unchanged."""
        if user_input is not None:
            return await self.async_step_done()
        from .dashboard import RoomDashboard
        entry = self.config_entry
        dashboard = RoomDashboard(self.hass, entry.data.get("topic_prefix", entry.unique_id), entry.entry_id)
        return self.async_show_form(step_id="open_settings", data_schema=vol.Schema({}),
                                    description_placeholders={"path": dashboard.settings_path})

    async def async_step_heating_boiler(self, user_input=None):
        """Configure → Heating and boiler: Smart warm-up, Weather compensation, the water temperature limits,
        Comfort and boiler care (when the E32 can change them), the heating circuits (when the E32 reports one
        with a pump, E32 1.1), the boiler model and the boiler's own settings (when the E32 sends them,
        e32_boiler_settings)."""
        from .e32_boiler_settings import offered as boiler_settings_offered
        from .e32_care import care_offered
        from .e32_shelly import circuits_offered
        from .e32_flow import KEY
        link = (self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id) or {}).get(KEY)
        # Offered once the E32 device page has the two controls (the link exists from the platform setup on).
        # One row for both switches (1.1.1, V12-31); heating_warm_up and heating_weather stay as steps.
        flow = ["heating_flow"] if link is not None and not link.unsupported else []
        care = ["comfort_care"] if care_offered(self.hass, self.config_entry) else []
        settings = ["boiler_settings"] if boiler_settings_offered(self.hass, self.config_entry) else []
        circuits = ["heating_circuits"] if circuits_offered(self.hass, self.config_entry) else []
        return self.async_show_menu(step_id="heating_boiler", menu_options=[
            *flow, "heating_boiler_limits", *circuits, *care, "boiler_model", *settings])

    async def async_step_heating_boiler_limits(self, user_input=None):
        """The E32 plan's water temperature limits (e32_room_flow.py)."""
        from homeassistant.exceptions import HomeAssistantError
        link = self._e32_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        try:
            self._e32_plan = await link.async_read()
        except HomeAssistantError as err:
            return self._e32_abort_failure(err)
        return await self.async_step_e32_flow_limits()

    async def async_step_general(self, user_input=None):
        """Name and dashboard of an installation whose rooms are on the E32.

        The older installation form ("installation") also held water limits and a
        weather curve of the Home Assistant room route; for the E32 room plan those
        are under Heating and boiler and on the E32 device page, so only these two stay.
        """
        # 1.4: the same validation and write as the settings panel's section "Dashboard and name" (settings.py).
        from .settings import SettingsError, commit_general, general_unchanged, general_values
        entry = self.config_entry
        if not hasattr(self, "_general_before"):
            self._general_before = configuration_snapshot(entry)
        errors = {}
        if user_input is not None:
            try:
                name, dashboard = general_values(user_input)
            except SettingsError as err:
                errors[err.field] = err.key
            else:
                if general_unchanged(entry, name, dashboard):
                    return self.async_abort(reason="installation_saved")
                try:
                    commit_general(self.hass, entry, self._general_before, name, dashboard)
                except SettingsError as err:
                    return self.async_abort(reason=err.key)
                return self.async_abort(reason="installation_saved")
        schema = vol.Schema({
            vol.Required("name", default=entry.title): str,
            vol.Optional(CONF_CREATE_DASHBOARD, default=entry.options.get(CONF_CREATE_DASHBOARD, False)): bool,
        })
        return self.async_show_form(step_id="general", data_schema=retained_input_schema(self, schema, user_input),
                                    errors=errors)

    async def async_step_energy(self, user_input=None):
        """Optional gas meter, gas price, outdoor temperature and boiler power (nothing is required)."""
        from .energy_input import EnergyError, currency, energy_schema, save_energy, validate_energy
        errors = {}
        if user_input is not None:
            try:
                values = validate_energy(self.hass, user_input)
            except EnergyError as err:
                errors[err.field] = err.code
            else:
                save_energy(self.hass, self.config_entry, values)
                return self.async_abort(reason="energy_saved")
        # A suggested power (gas meter calibration, a known boiler type, else the default), in the description only.
        from .boiler_power import basis, detected_model, suggestion
        from .const import DOMAIN
        from .e32_flow import gas_calibration
        hub = (self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id) or {}).get("heating_hub")
        model = detected_model(self.hass, self.config_entry)
        kw, source = suggestion({}, gas_calibration(hub) if hub is not None else None, None, model)
        schema = energy_schema(vol, self.config_entry.options, currency(self.hass))
        return self.async_show_form(step_id="energy", data_schema=retained_input_schema(self, schema, user_input),
                                    errors=errors, description_placeholders={
                                        "boiler_kw_suggested": f"{kw:g}",
                                        "boiler_kw_basis": basis(source, self.hass.config.language, model)})

    async def async_step_installation(self, user_input=None):
        entry = self.config_entry
        if integration_mode(entry) != MODE_SHADOW:
            return self.async_abort(reason="product_upgrade_required")
        from .installation_edit import installation_context, active_installation_step
        if hasattr(self, '_central_active_before') or installation_context(self.hass, entry) is not None:
            if hasattr(self, '_central_before'):
                return self.async_abort(reason='setup_changed')
            return await active_installation_step(self, user_input)
        if entry.options.get(CONF_ENABLED, False) or actual_runtime_active(self.hass, entry):
            return self.async_abort(reason="setup_runtime_off")
        from .room_profile_apply import pending_profile_source
        if pending_profile_source(self.hass, entry) is not None:
            return self.async_abort(reason='installation_apply_pending')
        errors = {}
        try:
            current = central_entry(entry)
        except ValueError as err:
            return self.async_abort(reason=_error(err))
        document = deepcopy(dict(current.data)["draft"]) if current else default_document()
        if not hasattr(self, "_central_before"):
            self._central_before = configuration_snapshot(entry)
        if user_input is not None:
            try:
                name = user_input["name"].strip()
                if not name or len(name) > 80:
                    raise ValueError("invalid_name")
                defaults = central_schema(document, self.hass)
                flattened = {str(key): key.default() for key in defaults.schema
                             if key.default is not vol.UNDEFINED and str(key) != "draft_action"}
                if document["central"].get("outdoor_source"):
                    flattened["outdoor_source"] = self._display(document["central"]["outdoor_source"], ("sensor", "weather"))
                if document["central"].get("fixed_fallback_centi_c") is not None:
                    flattened["fixed_fallback_temperature"] = document["central"]["fixed_fallback_centi_c"] / 100
                advanced = dict(user_input.get("advanced", {}))
                if "advanced" in user_input and "fixed_fallback_temperature" not in advanced:
                    flattened.pop("fixed_fallback_temperature", None)
                if "outdoor_maximum_age_seconds" in advanced:
                    advanced["outdoor_maximum_age_ms"] = milliseconds(advanced.pop("outdoor_maximum_age_seconds"))
                flattened.update(advanced)
                flattened["weather_enabled"] = user_input["weather_enabled"]
                if user_input.get("outdoor_source"):
                    flattened["outdoor_source"] = user_input["outdoor_source"]
                else:
                    flattened.pop("outdoor_source", None)
                # Central changes never silently replace room/group declarations.
                candidate = draft_from_form(self.hass, flattened, document)
                for group in candidate["groups"]:
                    if (group["emitter"] == "radiator" and group["supply_limits"] == document["central"]["supply_limits"]):
                        group["supply_limits"] = deepcopy(candidate["central"]["supply_limits"])
                parsed = validated_graph(self.hass, entry, candidate)
                data = {**(dict(current.data) if current else {}),
                    "draft": parsed.storage_document(), "status": parsed.readiness,
                    "draft_digest": parsed.digest, "incomplete_group_ids": list(parsed.incomplete_group_ids)}
                commit_configuration(self.hass, entry, self._central_before,
                    title=name, options={**entry.options, CONF_CREATE_DASHBOARD: user_input.get(CONF_CREATE_DASHBOARD, False)},
                    data={**entry.data, INSTALLATION: data},
                    subentries={k: s for k, s in entry.subentries.items() if s.subentry_type != "heating"})
            except (KeyError, ValueError, vol.Invalid) as err:
                errors["base"] = _error(err)
            except Exception:
                _LOGGER.exception("Installation save could not be confirmed")
                return self.async_abort(reason="setup_save_uncertain")
            else:
                return self.async_abort(reason="installation_saved")
        fields = central_schema(document, self.hass)
        advanced = {}
        for key, value in fields.schema.items():
            if str(key) in {"draft_action", "weather_enabled", "outdoor_source"}:
                continue
            if str(key) == "outdoor_maximum_age_ms":
                key = vol.Required("outdoor_maximum_age_seconds", default=document["central"]["outdoor_maximum_age_ms"]/1000)
                value = selector.NumberSelector({"min": 1, "max": 86400, "step": .001, "mode": "box", "unit_of_measurement": "s"})
            advanced[key] = value
        source = document["central"].get("outdoor_source")
        marker = vol.Optional("outdoor_source", description={"suggested_value": self._display(source, ("sensor", "weather"))}) if source else vol.Optional("outdoor_source")
        schema = vol.Schema({
            vol.Required("name", default=entry.title): str,
            vol.Required("weather_enabled", default=document["central"]["weather_enabled"]): bool,
            marker: selector.EntitySelector({"filter": [
                {"domain": "sensor", "device_class": "temperature"}, {"domain": "weather"}]}),
            vol.Optional(CONF_CREATE_DASHBOARD, default=entry.options.get(CONF_CREATE_DASHBOARD, False)): bool,
            vol.Optional("advanced"): section(vol.Schema(advanced), {"collapsed": True}),
        })
        return self.async_show_form(step_id="installation", data_schema=retained_input_schema(
            self, schema, user_input), errors=errors)

    async def async_step_installation_connected(self, user_input=None):
        from .installation_edit import active_installation_step
        return await active_installation_step(self, user_input)

    async def async_step_room_settings(self, user_input=None):
        rooms = [s for s in self.config_entry.subentries.values() if s.subentry_type == "zone"]
        if not rooms:
            return self.async_abort(reason="no_rooms")
        if user_input is not None:
            if user_input.get("room") not in {s.subentry_id for s in rooms}:
                return self.async_abort(reason="setup_changed")
            self._managed_room = user_input["room"]
            if user_input.get("action") == "remove":
                return await self.async_step_remove_room()
            if user_input.get("action") != "edit":
                return self.async_abort(reason="setup_changed")
            return await ProductRoomFlow.async_step_reconfigure(self)
        return self.async_show_form(step_id="room_settings", data_schema=vol.Schema({
            vol.Required("room", default=rooms[0].subentry_id): selector.SelectSelector({"options": [
                {"value": s.subentry_id, "label": s.title} for s in rooms]}),
            vol.Required("action", default="edit"): selector.SelectSelector({
                "options": ["edit", "remove"], "translation_key": "product_room_action"}),
        }))

    async def async_step_remove_room(self, user_input=None):
        entry = self.config_entry
        if entry.options.get(CONF_ENABLED, False) or actual_runtime_active(self.hass, entry):
            return self.async_abort(reason="setup_runtime_off")
        old = entry.subentries.get(self._managed_room)
        if old is None:
            return self.async_abort(reason="setup_changed")
        if not hasattr(self, "_remove_before"):
            self._remove_before = configuration_snapshot(entry)
        if user_input is not None:
            if not user_input.get("confirm_remove", False):
                return self.async_abort(reason="cancelled")
            try:
                subentries = {k: s for k, s in entry.subentries.items() if k != old.subentry_id}
                current = central_entry(entry)
                if current:
                    document = deepcopy(dict(current.data)["draft"])
                    own_groups = {a["group_id"] for a in document["actuators"] if a["room_id"] == old.data["room_id"]}
                    document["actuators"] = [a for a in document["actuators"] if a["room_id"] != old.data["room_id"]]
                    used = {a["group_id"] for a in document["actuators"]}
                    document["groups"] = [g for g in document["groups"] if g["group_id"] not in own_groups or g["group_id"] in used]
                    # Parse prospective ownership without creating an intermediate entry.
                    from .v1_heating_draft import parse_heating_draft
                    parsed = parse_heating_draft(document, known_room_ids={s.data["room_id"] for s in subentries.values() if s.subentry_type == "zone"})
                    data = {**dict(current.data), "draft": parsed.storage_document(), "status": parsed.readiness,
                            "draft_digest": parsed.digest, "incomplete_group_ids": list(parsed.incomplete_group_ids)}
                # A removed layout invalidates the selected logical device profile.
                from .native_provisioning import SOURCE_OPTION
                options = {k: v for k, v in entry.options.items() if k != SOURCE_OPTION}
                changed = {"options": options, "subentries": subentries}
                if current:
                    changed["data"] = {**entry.data, INSTALLATION: data}
                commit_configuration(self.hass, entry, self._remove_before, **changed)
            except (ValueError, KeyError) as err:
                return self.async_abort(reason=_error(err))
            except Exception:
                _LOGGER.exception("Room removal could not be confirmed")
                return self.async_abort(reason="setup_save_uncertain")
            return self.async_abort(reason="room_removed")
        return self.async_show_form(step_id="remove_room", data_schema=vol.Schema({
            vol.Required("confirm_remove", default=False): bool,
        }), description_placeholders={"name": old.title})

    async def async_step_configuration_status(self, user_input=None):
        if user_input is not None:
            return self.async_abort(reason="configuration_status_closed")
        entry = self.config_entry
        state = self.hass.data.get("open_thermostat", {}).get(entry.entry_id, {})
        connection = state.get("v1_connection")
        client = getattr(connection, "client", None)
        verified = bool(getattr(client, "graph_status", {}).get("readback_verified", False))
        # The texts in the user's language (English, Dutch or Polish: strings.json, R4-24).
        from .options_navigation import async_flow_texts
        words = await async_flow_texts(self.hass, "configuration_status_text")
        connection_text = words["confirmed" if verified else "unconfirmed"]
        enabled = actual_runtime_active(self.hass, entry)
        # Neutral on purpose: in shadow mode the thermostat controls the boiler, after the switch-over the E32 does.
        runtime_text = words["calculations_on" if enabled else "calculations_off"]
        # Inspect saved targets without altering settings or granting physical readiness.
        from .room_editor import read_room
        from .v1_profile_c import MODE_MESSAGES
        checks = []
        for sub in entry.subentries.values():
            if sub.subentry_type != "zone":
                continue
            try:
                review = read_room(self.hass, entry.entry_id, sub.data["room_id"])["actuator_target_review"]
            except (KeyError, ValueError):
                continue
            for actuator in review["actuators"]:
                cap = actuator.get("capability")
                text = actuator["entity_id"] + ": "
                if cap and actuator["status"] != "unknown":
                    text += f"{cap['minimum']:g}–{cap['maximum']:g} {cap['unit']}; "
                    text += f"{words['step']} {cap['step']:g} {cap['unit']}"
                    if any(reason in actuator["issues"] for reason in (
                            "room_limits_exceed_actuator", "saved_targets_need_review")):
                        text += ". " + words["review_limits"]
                else:
                    text += words["capabilities_unavailable"]
                for reason in actuator.get("operating_mode", {}).get("issues", []):
                    if reason in MODE_MESSAGES and reason in words:
                        text += " " + words[reason]
                if review["external_program_present"]:
                    text += " " + words["external_program"]
                checks.append(text)
        actuator_text = "\n\n".join(checks) or words["no_valves"]
        return self.async_show_form(step_id="configuration_status", data_schema=vol.Schema({}),
            description_placeholders={"rooms": str(sum(s.subentry_type == "zone" for s in entry.subentries.values())),
                "connection": connection_text, "runtime": runtime_text, "actuator_checks": actuator_text})

    async def async_step_advanced_settings(self, user_input=None):
        from .options_navigation import async_flow_texts
        texts = await async_flow_texts(self.hass, "configure_text")
        return self.async_show_menu(step_id="advanced_settings", menu_options=await self._advanced_options(),
                                    description_placeholders={"intro": texts["advanced_menu"]})

    async def _advanced_options(self):
        """The rows of Configure → Advanced and diagnostics: on the menu of an installation without the settings page
        (without the OpenThermostat dashboard, before Connect E32, on the old room route). With the settings page
        (1.4.1) Configure has no Advanced row: everything is on the dashboard's Settings tab (the rooms' radiator
        valves, persons and limits on the room screen, the boiler settings under Heating and boiler, the E32 system
        log, its time zone, the tester program, restoring a backup, tidying entity IDs and the old rooms under
        Installation)."""
        from .e32_link import legacy_rooms_pending, legacy_zones
        entry = self.config_entry
        e32 = not old_room_route(entry)
        panel = settings_page(entry)
        options = []
        # Dashboard and name are on the main menu unless the old room route is (1.1.1, Q6). "Check the old rooms"
        # counts and checks the old Home Assistant rooms only: it is shown while such rooms are left (1.3, Q7).
        if not e32:
            options.append("general")
        if not e32 or legacy_zones(entry):
            options.append("configuration_status")
        if e32 and legacy_zones(entry):
            # The water limits of the older room profile, while its rooms are left.
            options.append("installation")
        if self._native_plan_review_available():
            options += ["graph_prepare", "graph_status"]
        if legacy_rooms_pending(entry):
            options.append("legacy_rooms")
        from .e32_backup import backups
        if backups(self.hass, entry) is not None:
            # Restore one of the E32 settings backups Home Assistant keeps (e32_backup_flow).
            options.append("e32_restore")
        from .e32_system import link_for
        if link_for(self.hass, entry) is not None and not panel:
            # The E32's system log and time zone (e32_system), as on its System pages. Its Bluetooth sensors are under
            # E32 devices on the main menu since 1.3.
            options += ["e32_logging", "e32_time_zone"]
            # The tester programme (e32_tester, E5): off by default; share what the E32 heard from the boiler.
            options.append("tester")
        from .entity_id_tidy import async_undo_available
        options.append("entity_ids")
        if await async_undo_available(self.hass, entry):
            options.append("entity_ids_undo")
        return options

    async def async_step_entity_ids(self, user_input=None):
        """Optional tidy of long entity IDs: a preview of every old -> new pair and where it is used,
        then rename on explicit confirmation (entity_id_tidy)."""
        from homeassistant.helpers import selector
        from . import entity_id_tidy as tidy
        plan = getattr(self, "_entity_id_plan", None)
        if plan is None or user_input is None:
            plan = self._entity_id_plan = await tidy.async_plan(self.hass, self.config_entry)
        if not plan.renames:
            return self.async_abort(reason="entity_ids_nothing")
        errors = {}
        scope = (user_input or {}).get("scope", "unused")
        if user_input is not None:
            if not user_input.get("confirm"):
                errors["base"] = "entity_ids_confirm"
            else:
                done, todo = await tidy.async_apply_plan(self.hass, self.config_entry, plan, scope == "unused")
                self._entity_id_plan = None
                return self.async_abort(reason="entity_ids_done", description_placeholders={
                    "count": str(len(done)), "todo": todo})
        schema = vol.Schema({
            vol.Required("scope", default=scope): selector.SelectSelector(selector.SelectSelectorConfig(
                options=["unused", "all"], translation_key="entity_ids_scope",
                mode=selector.SelectSelectorMode.LIST)),
            vol.Required("confirm", default=False): selector.BooleanSelector(),
        })
        return self.async_show_form(step_id="entity_ids", data_schema=schema, errors=errors,
            description_placeholders={"count": str(len(plan.renames)),
                                      "used": str(len(plan.renames) - len(plan.unused)),
                                      "days": str(tidy.UNDO_DAYS),
                                      "preview": tidy.preview_text(plan, False, self.hass.config.language)})

    async def async_step_entity_ids_undo(self, user_input=None):
        from homeassistant.helpers import selector
        from . import entity_id_tidy as tidy
        available = await tidy.async_undo_available(self.hass, self.config_entry)
        if not available:
            return self.async_abort(reason="entity_ids_nothing")
        errors = {}
        if user_input is not None:
            if not user_input.get("confirm"):
                errors["base"] = "entity_ids_confirm"
            else:
                undone = await tidy.async_undo(self.hass, self.config_entry)
                return self.async_abort(reason="entity_ids_undone", description_placeholders={"count": str(len(undone))})
        return self.async_show_form(step_id="entity_ids_undo", errors=errors,
            data_schema=vol.Schema({vol.Required("confirm", default=False): selector.BooleanSelector()}),
            description_placeholders={"count": str(len(available))})


# Configure -> Advanced -> "Is everything connected?" (older Home Assistant rooms only): the lines filled into its
# translated description, in plain words. "Configuration confirmed" is what that description explains.


def main_menu(entry):
    """Configure's top level, in the order a user needs it, without duplicates.

    E32 room plan with the settings page (1.4, settings_page): Open the settings page and E32 connection (1.4.1: two
    rows, HA-INSTELPANEEL-FASE2.nl.md 3.8). Every setting lives on the dashboard's Settings tab (settings.py); the
    steps stay in the flow for the menu without the dashboard and for the Repairs dialogs, which use them.
    E32 room plan without the OpenThermostat dashboard (so without its Settings tab): Rooms, House, Heating and boiler,
    Energy and outdoor temperature, Notifications, E32 connection, E32 devices, Dashboard and name, Advanced and
    diagnostics (1.1.1, the owner's Q6: Dashboard and name on the main menu, its last row before Advanced; 1.3: E32
    devices, the Bluetooth sensors and the Shelly devices as on the E32's page System → Devices). A new installation
    whose E32 is not connected yet starts with E32 connection (rooms and heating need it).
    Older installations on the Home Assistant room route keep their menu.
    """
    from .room_plan import has_room_plan
    if has_room_plan(entry):
        if settings_page(entry):
            return ["open_settings", "controller_connection"]
        return ["e32_rooms", "house", "heating_boiler", "energy", "notifications", "controller_connection",
                "e32_devices", "general", "advanced_settings"]
    if not old_room_route(entry):
        return ["controller_connection", "energy", "general", "advanced_settings"]
    return ["room_settings", "controller_connection", "energy", "installation", "advanced_settings"]


def settings_page(entry):
    """True when the everyday settings live on the dashboard's Settings tab (1.4): an installation on the E32 room plan
    that shows the OpenThermostat dashboard (the tab is part of it). Without the dashboard Configure keeps every
    setting in its own menu, so nothing is out of reach."""
    from .room_plan import has_room_plan
    return has_room_plan(entry) and (getattr(entry, "options", None) or {}).get(CONF_CREATE_DASHBOARD, False) is True


def old_room_route(entry):
    """True while Configure offers the old Home Assistant room route (1.3, Q7): an installation from before beta.19
    that is not connected to an E32 room plan and still has an old Home Assistant room. Without one it gets the menu
    of a new installation (E32 connection first; Connect E32 then links the room plan)."""
    from .e32_link import legacy_zones
    from .room_plan import uses_e32_rooms
    return not uses_e32_rooms(entry) and bool(legacy_zones(entry))


ProductOptionsFlow.wrap_steps()
