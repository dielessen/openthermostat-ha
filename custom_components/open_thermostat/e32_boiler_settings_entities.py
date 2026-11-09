"""The entities of the boiler settings (e32_boiler_settings.py), on the E32 device.

- "Boiler settings writes" (diagnostic sensor): off, ready, watching or failed, from fw/telemetry/boiler_settings;
  it exists once the E32 sends that topic (firmware without boiler settings: no sensor). Its attributes (the
  last setting, its result and when Home Assistant saw it) are not recorded.
- One number, select or switch per everyday setting the E32 verified on this boiler: those are written at once
  and read back, without a watch, within the everyday range. Configure → Heating and boiler → Boiler settings
  changes the same setting (and every other one, while you watch the boiler). Installer settings never get an
  entity: they stay under Advanced in Configure. A setting that is no longer verified loses its entity.
"""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN
from .e32_boiler_settings import ROWS, STATES, UNITS, entity_settings, setting_name, value_text, writes_state

_LOGGER = logging.getLogger(__name__)


class _BoilerSettingsEntity:
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, state, unique_id):
        self._settings = state
        from .ems_devices import boiler_identifier
        self._attr_unique_id = unique_id
        # On the boiler device (1.1.1, V12-26): the boiler's own settings.
        self._attr_device_info = DeviceInfo(identifiers={boiler_identifier(state.prefix)})

    async def async_added_to_hass(self):
        self.async_on_remove(self._settings.add_listener(self.async_write_ha_state))


class BoilerSettingsWritesSensor(_BoilerSettingsEntity, SensorEntity):
    """Whether the E32 may change boiler settings now, and what the last change did."""

    _attr_translation_key = "boiler_settings_writes"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(STATES)
    # Recorded minimally: the state; the details only while shown.
    _unrecorded_attributes = frozenset({"last_setting", "last_result", "when"})

    def __init__(self, state):
        super().__init__(state, f"{state.prefix}_boiler_settings_writes")

    @property
    def available(self):
        return self._settings.telemetry is not None

    @property
    def native_value(self):
        return writes_state(self._settings.telemetry)

    @property
    def extra_state_attributes(self):
        last = (self._settings.telemetry or {}).get("last")
        when = self._settings.last_when
        return {"last_setting": last["id"] if last else None, "last_result": last["result"] if last else None,
                "when": when.isoformat() if when is not None else None}


class _SettingEntity(_BoilerSettingsEntity):
    """One setting verified on this boiler: written at once, read back by the E32."""

    _attr_translation_key = "boiler_setting"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, state, setting):
        super().__init__(state, state.unique_id(setting))
        self.setting, self.row = setting, ROWS[setting]
        self._attr_translation_placeholders = {"setting": setting_name(state.texts, setting)}

    @property
    def available(self):
        telemetry = self._settings.telemetry
        return self.setting in entity_settings(telemetry) and telemetry["persistent"]

    def _value(self):
        return self._settings.value(self.setting)

    @property
    def extra_state_attributes(self):
        return {"setting": self.setting}

    async def _write(self, value):
        await self._settings.async_write(self.setting, value)


class BoilerSettingNumber(_SettingEntity, NumberEntity):
    _attr_mode = NumberMode.BOX
    _attr_native_step = 1

    def __init__(self, state, setting):
        super().__init__(state, setting)
        row = self.row
        self._attr_native_min_value, self._attr_native_max_value = row.user_minimum, row.user_maximum
        self._attr_native_unit_of_measurement = UNITS.get(row.unit)
        if row.unit == "degC":
            self._attr_device_class = NumberDeviceClass.TEMPERATURE

    @property
    def native_value(self):
        return self._value()

    async def async_set_native_value(self, value):
        await self._write(int(round(value)))


class BoilerSettingSelect(_SettingEntity, SelectEntity):
    def _labels(self):
        row = self.row
        return {value_text(self._settings.texts, self.setting, v): v for v in range(row.user_minimum, row.user_maximum + 1)}

    @property
    def options(self):
        return list(self._labels())

    @property
    def current_option(self):
        value = self._value()
        return None if value is None else value_text(self._settings.texts, self.setting, value)

    async def async_select_option(self, option):
        await self._write(self._labels()[option])


class BoilerSettingSwitch(_SettingEntity, SwitchEntity):
    @property
    def is_on(self):
        value = self._value()
        return None if value is None else bool(value)

    async def async_turn_on(self, **kwargs):
        await self._write(1)

    async def async_turn_off(self, **kwargs):
        await self._write(0)


ENTITY_CLASSES = {"number": BoilerSettingNumber, "select": BoilerSettingSelect, "switch": BoilerSettingSwitch}


def _options(hass, entry):
    from .heating_link import add_options
    return add_options(hass, entry)


async def async_setup_sensors(hass, entry, async_add_entities):
    from .e32_boiler_settings import async_setup
    from .product import is_product
    if not is_product(entry):
        return
    state = await async_setup(hass, entry)
    options = _options(hass, entry)
    state.set_sensor_adder(lambda: async_add_entities([BoilerSettingsWritesSensor(state)], **options))


async def async_setup_platform(hass, entry, async_add_entities, kind):
    """number, select or switch: the entities of the settings verified on this boiler, as the E32 reports them."""
    from .e32_boiler_settings import async_setup
    from .product import is_product
    if not is_product(entry):
        return
    try:
        state = await async_setup(hass, entry)
        state.add_platform(kind, async_add_entities, _options(hass, entry))
    except Exception:  # noqa: BLE001 - optional: never let it take the platform's other entities down
        _LOGGER.exception("OpenThermostat: setting up the boiler settings %s entities failed", kind)
