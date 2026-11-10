"""The settings panel's section Energy and outdoor temperature (1.4; settings.py registers it, the screen is
frontend/openthermostat-settings-energy.js).

One screen with the eight optional fields of Configure → Energy and outdoor temperature, under the form's own field
names: the gas meter, a gas price sensor or a fixed gas price, the calorific value, the outdoor temperature, the
weather forecast, the boiler's heating power and the water meter. The model is what the form shows (the stored
options; the forecast as energy_schema shows it: the outdoor weather entity while none is chosen), the check and the
write are the form's own (energy_input.validate_energy and save_energy), so the panel and Configure store the same for
the same input. Home Assistant keeps these; nothing is read from the E32. The suggested boiler power is under ``live``
(it follows the gas meter's calibration).
"""
from __future__ import annotations

from .const import DOMAIN
from .settings import SettingsError, register_section


def read_energy(hass, entry, item=None):
    from .boiler_power import detected_model, suggestion
    from .e32_flow import gas_calibration
    from .energy_input import FIELDS, currency
    from .weather_forecast import forecast_entity
    options = entry.options
    model = {field: options.get(key) for field, key in FIELDS.items()}
    model["forecast_entity"] = forecast_entity(options)
    model = {field: ("" if value is None else value) for field, value in model.items()}
    model["currency"] = currency(hass)
    hub = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get("heating_hub")
    detected = detected_model(hass, entry)
    kw, source = suggestion({}, gas_calibration(hub) if hub is not None else None, None, detected)
    model["live"] = {"boiler_kw_suggested": kw, "boiler_kw_basis": source, "boiler_model": detected}
    return model


def save_energy(hass, entry, item, values):
    from .energy_input import FIELDS, EnergyError, save_energy as store, validate_energy
    try:
        stored = validate_energy(hass, {field: values.get(field) for field in FIELDS})
    except EnergyError as err:
        raise SettingsError(err.code, err.field) from None
    store(hass, entry, stored)
    return read_energy(hass, entry)


register_section("energy", read_energy, save_energy)
