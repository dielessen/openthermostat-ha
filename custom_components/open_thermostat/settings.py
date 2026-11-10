"""The settings panel of the OpenThermostat dashboard (tab "Settings" / "Instellen" / "Ustawienia", 1.4).

The panel (frontend/openthermostat-settings.js) is one web component on one dashboard view; this module is its
backend: a small registry of sections and three websocket commands. The design is
docs/engineering/HA-INSTELPANEEL-ONTWERP.nl.md; chapter 10 ("Bouwen op het fundament") says how a section package
builds on it.

Sections, in the order of the overview: rooms, house, heating, devices, notifications, energy, general,
advanced. Each has a summary (the lines under its name on the overview, plain text in the viewer's language,
built from the config entry and what Home Assistant already holds in memory; never a call to the E32) and
optionally an editor: ``read(hass, entry, item)`` returns the model of one screen, ``save(hass, entry, item,
values)`` validates and writes it and returns the fresh model. A section without an editor opens in the panel as
its summary with a link to Configure.

- ``open_thermostat/settings/overview`` (``entry_id``, optional ``language``): any signed-in user. Per section
  its ``title_key``, ``summary`` lines, ``available`` (false with ``reason``), ``editable``; and ``admin``.
- ``open_thermostat/settings/get`` (``entry_id``, ``section``, optional ``item``): any signed-in user (the panel
  shows a non-administrator a read-only page). ``{"model", "token"}``: the token is the SHA-256 of the model's
  canonical JSON.
- ``open_thermostat/settings/save`` (``entry_id``, ``section``, ``item``, ``token``, ``values``): administrators
  only. The token must still match the model as it is now; otherwise error ``changed_elsewhere`` with the fresh
  model and token in the error's data. Answers ``{"model", "token"}`` after the write. A model's top-level ``live``
  (what a screen only shows beside its fields, such as a reading now) is left out of the token: a new reading never
  makes a save "changed elsewhere".

Errors are ``connection.send_error(id, code, message)``: the code from SettingsError (or the duck-typed
``FlowError`` of the options flow: ``key``, ``field``, ``placeholders``), or ``not_admin``, ``unknown_section``,
``unavailable``, ``e32_unreachable``, ``save_uncertain``. The error's data (the field, the
placeholders and, for ``changed_elsewhere``, the fresh model and token) travels in Home Assistant's
``translation_placeholders`` slot of the error, which the frontend receives as it is.

No answer ever carries a password, a passphrase or the E32's connection data: ``_scrub`` removes every key that
contains "password", "passphrase" or "secret" and the controller_* connection keys from every model, at any depth,
whatever a section returns (a section that needs "a password is stored" names that flag otherwise).
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import inspect
import json
import logging
from typing import Any, Callable

import probatio as vol
from homeassistant.components import websocket_api
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_CREATE_DASHBOARD, CONF_TOPIC_PREFIX, DOMAIN

_LOGGER = logging.getLogger(__name__)

# The panel's module, served and loaded with the dashboard cards (week_planner.card_modules); the release script
# moves the version in the name (tools/dev/prepare_release.py, "frontend URLs").
URL = "/open_thermostat/openthermostat-settings-1.4.0.js"
CARD_TYPE = "custom:openthermostat-settings"
# A section package's own module (frontend/openthermostat-settings-<section>.js, it calls the kit's defineSection), served
# and loaded with the panel: one (URL, file) line per package, the URL versioned as the panel's.
SECTION_MODULES: tuple[tuple[str, str], ...] = (
    # ("/open_thermostat/openthermostat-settings-<section>-<HA version>.js", "openthermostat-settings-<section>.js"),
    ("/open_thermostat/openthermostat-settings-rooms-1.4.0.js", "openthermostat-settings-rooms.js"),
    ("/open_thermostat/openthermostat-settings-house-1.4.0.js", "openthermostat-settings-house.js"),
    ("/open_thermostat/openthermostat-settings-heating-1.4.0.js", "openthermostat-settings-heating.js"),
    ("/open_thermostat/openthermostat-settings-devices-1.4.0.js", "openthermostat-settings-devices.js"),
    ("/open_thermostat/openthermostat-settings-energy-1.4.0.js", "openthermostat-settings-energy.js"),
    ("/open_thermostat/openthermostat-settings-notifications-1.4.0.js", "openthermostat-settings-notifications.js"),
    ("/open_thermostat/openthermostat-settings-advanced-1.4.0.js", "openthermostat-settings-advanced.js"),
)
VIEW_PATH = "settings"  # the dashboard view: /<dashboard>/settings#<route>
CONFIGURE_PATH = "/config/integrations/integration/" + DOMAIN
NAME_MAX = 80  # the installation name, as the options step "general" allows it
LANGUAGES = ("en", "nl", "pl")
# Keys that never leave Home Assistant in a panel answer (a section that returns one has a bug; the core drops it).
SECRET_PARTS = ("password", "passphrase", "secret")
SECRET_KEYS = frozenset({"controller_address", "controller_password", "controller_url"})
LIVE = "live"  # a model's values shown beside the fields, not edited: not part of the token


class SettingsError(Exception):
    """A panel error: the code the frontend explains, the field it belongs to ("base": the whole screen) and the
    placeholders of its sentence. The same shape as the options flow's FlowError (key, field, placeholders), so a
    section can raise either."""

    def __init__(self, key, field="base", **placeholders):
        super().__init__(key)
        self.key, self.field, self.placeholders = key, field, placeholders

    @property
    def code(self):
        return self.key


def as_settings_error(err):
    """A SettingsError for any error of FlowError's shape (key, field, placeholders), else None."""
    if isinstance(err, SettingsError):
        return err
    key = getattr(err, "key", None)
    if type(key) is str and key and isinstance(getattr(err, "placeholders", None), dict):
        field = getattr(err, "field", "base")
        return SettingsError(key, field if type(field) is str else "base", **err.placeholders)
    return None


@dataclass(slots=True)
class Section:
    """One section of the panel. ``summary(hass, entry, hub, lang) -> [str]``; ``available(hass, entry, hub) ->
    None | reason key``; ``read``/``save`` as the module docstring says (sync or async)."""
    name: str
    order: int
    summary: Callable | None = None
    available: Callable | None = None
    read: Callable | None = None
    save: Callable | None = None


SECTIONS: dict[str, Section] = {}


def register_section(name, read=None, save=None, *, summary=None, available=None, order=None):
    """Add a section or complete one: what is given replaces, what is left out stays (a section package registers
    its editor, ``register_section("rooms", read_rooms, save_rooms)``, and keeps the core's summary and place)."""
    if type(name) is not str or not name.isidentifier():
        raise ValueError(f"invalid section name {name!r}")
    section = SECTIONS.get(name)
    if save is not None and read is None and (section is None or section.read is None):
        raise ValueError(f"section {name}: save needs read (the token is made from what read returns)")
    section = section or Section(name, len(SECTIONS) if order is None else order)
    for key, value in (("read", read), ("save", save), ("summary", summary), ("available", available)):
        if value is not None:
            setattr(section, key, value)
    if order is not None:
        section.order = order
    SECTIONS[name] = section
    return section


def _load_sections():
    """The modules that add a section's editor; each calls register_section when it is imported. One import
    line per section package, so packages built side by side do not touch each other's lines."""
    from . import settings_rooms  # noqa: F401  (Rooms: the list, a room, add and remove)
    from . import settings_house  # noqa: F401  (House: presence, room defaults, house mode and holidays, contacts)
    from . import settings_heating  # noqa: F401
    from . import settings_devices  # noqa: F401
    from . import settings_energy  # noqa: F401
    from . import settings_notifications  # noqa: F401  (Notifications: people and phones, the house, the rooms)
    from . import settings_advanced  # noqa: F401  (Advanced: system log, time zone, tester program, room setup status)


# -- the token ------------------------------------------------------------------------------------------------

def canonical(model):
    """The model as canonical JSON: sorted keys, no spaces, UTF-8 (the same bytes for the same model)."""
    return json.dumps(model, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def token(model):
    """SHA-256 hex of the model's canonical JSON, without its ``live`` part (LIVE)."""
    if isinstance(model, dict) and LIVE in model:
        model = {key: value for key, value in model.items() if key != LIVE}
    return hashlib.sha256(canonical(model).encode("utf-8")).hexdigest()


def _scrub(value):
    """The value without passwords, passphrases, secrets and the E32's connection keys, at any depth."""
    if isinstance(value, dict):
        return {key: _scrub(item) for key, item in value.items()
                if not (type(key) is str and (key.lower() in SECRET_KEYS
                                              or any(part in key.lower() for part in SECRET_PARTS)))}
    if isinstance(value, (list, tuple)):
        return [_scrub(item) for item in value]
    return value


async def _call(function, *args):
    result = function(*args)
    return await result if inspect.isawaitable(result) else result


async def read_model(hass, entry, section, item=None):
    """{"model", "token"} of a section's screen (SettingsError on a refusal)."""
    model = _scrub(await _call(section.read, hass, entry, item))
    if type(model) is not dict:
        raise SettingsError("save_uncertain")
    return {"model": model, "token": token(model)}


# -- language and plain figures ---------------------------------------------------------------------------------

def language(hass, wanted=None):
    """en, nl or pl: the viewer's language when the panel names one, else Home Assistant's, else English."""
    for value in (wanted, getattr(getattr(hass, "config", None), "language", None)):
        if type(value) is str and value[:2].lower() in LANGUAGES:
            return value[:2].lower()
    return "en"


def figure(value, lang, digits=None):
    """A number as the page writes it: 20.5 / 20,5; whole numbers without decimals unless ``digits`` asks."""
    if digits is None:
        text = f"{round(float(value), 1):g}"
    else:
        text = f"{float(value):.{digits}f}"
    return text.replace(".", ",") if lang in ("nl", "pl") else text


def degrees(value, lang):
    return f"{figure(value, lang)} °C"


def _number(value):
    return value if type(value) in (int, float) and value == value else None


# -- what Home Assistant already holds -----------------------------------------------------------------------------

def _entry(hass, entry_id):
    """The E32 installation, or SettingsError("unavailable")."""
    from .product import is_product
    entry = hass.config_entries.async_get_entry(entry_id)
    if entry is None or entry.domain != DOMAIN or not is_product(entry):
        raise SettingsError("unavailable")
    return entry


def _hub(hass, entry):
    """The entry's heating hub while the installation runs (never created here), else None."""
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    return state.get("heating_hub") if isinstance(state, dict) else None


def _plan(hub):
    """The room plan Home Assistant last read from the E32 (RoomPlanLink.plan), or None."""
    plan = getattr(getattr(hub, "plan", None), "plan", None)
    return plan if type(plan) is dict else None


def _connected(hass, entry, hub):
    """Rooms, House, Heating and Devices need the E32 connection (Configure → E32 connection)."""
    from .room_plan import has_room_plan
    return None if has_room_plan(entry) else "connect_e32"


# The words of the summaries (EN, NL, PL). The house modes are the select's words (strings.json
# entity.select.house_mode, checked by test_settings_panel.py); the room states are the shared words of 1.4.
TEXT = {
    "en": {"no_data": "No data from the E32 yet", "no_rooms": "No rooms yet", "more": "and {n} more",
           "follow": "heat along only", "off": "off", "auto": "Automatic", "home": "At home", "away": "Away",
           "holiday": "Holiday", "away_after": "away after {n} min, then {t}", "away_at": "away: {t}",
           "limits_own": "Water temperature: {low}–{high} °C",
           "limits_auto": "Water temperature: at most {high} °C, lowest automatic",
           "limits_auto_now": "Water temperature: at most {high} °C, lowest automatic (now {now} °C)",
           "boiler": "Boiler", "ble_one": "1 Bluetooth sensor", "ble": "{n} Bluetooth sensors",
           "shelly_one": "1 Shelly valve", "shelly": "{n} Shelly valves",
           "circuit_one": "1 heating circuit", "circuit": "{n} heating circuits",
           "no_devices": "No Bluetooth sensors or Shelly devices", "on": "On", "notifications_off": "Off",
           "gas_meter": "Gas meter", "gas_price": "Gas price", "outdoor": "outdoor: {name}", "boiler_kw": "{kw} kW",
           "water_meter": "Water meter", "forecast": "Weather forecast", "energy_none": "Nothing set yet",
           "advanced": "System log, time zone and tester program"},
    "nl": {"no_data": "Nog geen gegevens van de E32", "no_rooms": "Nog geen ruimtes", "more": "en nog {n}",
           "follow": "alleen meeverwarmen", "off": "uit", "auto": "Automatisch", "home": "Thuis", "away": "Afwezig",
           "holiday": "Vakantie", "away_after": "afwezig na {n} min, dan {t}", "away_at": "afwezig: {t}",
           "limits_own": "Watertemperatuur: {low}–{high} °C",
           "limits_auto": "Watertemperatuur: hoogstens {high} °C, laagste automatisch",
           "limits_auto_now": "Watertemperatuur: hoogstens {high} °C, laagste automatisch (nu {now} °C)",
           "boiler": "Ketel", "ble_one": "1 Bluetooth-sensor", "ble": "{n} Bluetooth-sensoren",
           "shelly_one": "1 Shelly-kraan", "shelly": "{n} Shelly-kranen",
           "circuit_one": "1 verwarmingscircuit", "circuit": "{n} verwarmingscircuits",
           "no_devices": "Geen Bluetooth-sensoren of Shelly-apparaten", "on": "Aan", "notifications_off": "Uit",
           "gas_meter": "Gasmeter", "gas_price": "Gasprijs", "outdoor": "buiten: {name}", "boiler_kw": "{kw} kW",
           "water_meter": "Watermeter", "forecast": "Weersverwachting", "energy_none": "Nog niets ingesteld",
           "advanced": "Systeemlog, tijdzone en testerprogramma"},
    "pl": {"no_data": "Brak jeszcze danych z E32", "no_rooms": "Brak jeszcze pomieszczeń", "more": "i jeszcze {n}",
           "follow": "grzeje tylko razem z innymi", "off": "wyłączone", "auto": "Automatyczny", "home": "W domu",
           "away": "Nieobecność", "holiday": "Urlop", "away_after": "nieobecność po {n} min, potem {t}",
           "away_at": "nieobecność: {t}",
           "limits_own": "Temperatura wody: {low}–{high} °C",
           "limits_auto": "Temperatura wody: najwyżej {high} °C, najniższa automatycznie",
           "limits_auto_now": "Temperatura wody: najwyżej {high} °C, najniższa automatycznie (teraz {now} °C)",
           "boiler": "Kocioł", "ble_one": "1 czujnik Bluetooth", "ble": "Czujniki Bluetooth: {n}",
           "shelly_one": "1 zawór Shelly", "shelly": "Zawory Shelly: {n}",
           "circuit_one": "1 obieg grzewczy", "circuit": "Obiegi grzewcze: {n}",
           "no_devices": "Brak czujników Bluetooth i urządzeń Shelly", "on": "Włączone",
           "notifications_off": "Wyłączone", "gas_meter": "Licznik gazu", "gas_price": "Cena gazu",
           "outdoor": "na zewnątrz: {name}", "boiler_kw": "{kw} kW", "water_meter": "Licznik wody",
           "forecast": "Prognoza pogody", "energy_none": "Jeszcze nic nie ustawiono",
           "advanced": "Dziennik systemowy, strefa czasowa i program testerów"},
}
ROOMS_SHOWN = 6  # the overview names this many rooms, then "and 2 more"


def _room_name(hass, entry, room):
    """The room's name as Home Assistant shows its device (a rename by the user counts), else the E32's."""
    from homeassistant.helpers import device_registry as dr
    from .heating_link import label
    prefix = entry.data.get(CONF_TOPIC_PREFIX)
    device = dr.async_get(hass).async_get_device_by_identifier((DOMAIN, f"{prefix}_e32_room_{room['id']}"),
                                                                entry.entry_id) if prefix else None
    return (device and (device.name_by_user or device.name)) or label(room)


def summary_rooms(hass, entry, hub, lang):
    """"Living room 20.5 °C · Basement 16 °C (heat along only) · Bathroom (off)": each room the E32 reports, in its
    order, with its target from the E32's status and its state."""
    t = TEXT[lang]
    if hub is None or not hub.fresh:
        return [t["no_data"]]
    rooms = list(hub.rooms.values())
    if not rooms:
        return [t["no_rooms"]]
    parts = []
    for room in rooms[:ROOMS_SHOWN]:
        name, target = _room_name(hass, entry, room), _number(room.get("setpoint"))
        if room.get("state") == "inactive":
            parts.append(f"{name} ({t['off']})")
            continue
        text = f"{name} {degrees(target, lang)}" if target is not None else name
        parts.append(f"{text} ({t['follow']})" if room.get("state") == "follow" else text)
    if len(rooms) > ROOMS_SHOWN:
        parts.append(t["more"].format(n=len(rooms) - ROOMS_SHOWN))
    return [" · ".join(parts)]


def summary_house(hass, entry, hub, lang):
    """"Automatic · away after 15 min, then 16 °C": the house mode, and the away temperature (with the wait when
    people are chosen for presence)."""
    from .e32_comfort import comfort_options
    from .e32_house import house_away, house_mode
    t = TEXT[lang]
    if hub is None or not hub.fresh:
        return [t["no_data"]]
    away = house_away(hub)
    parts = [t[house_mode(away)]]
    target = _number(away.get("target_c")) if away else None
    if target is not None:
        settings = comfort_options(entry)
        people = settings.get("presence_entities") or ([settings["presence_entity"]] if settings.get("presence_entity") else [])
        delay = _number(settings.get("away_delay_min"))
        parts.append(t["away_after"].format(n=round(delay), t=degrees(target, lang)) if people and delay is not None
                     else t["away_at"].format(t=degrees(target, lang)))
    return [" · ".join(parts)]


def _boiler_name(hass, entry, lang):
    """The boiler device's name (named after the chosen model, or by the user), else "Boiler"."""
    from homeassistant.helpers import device_registry as dr
    from .ems_devices import boiler_identifier
    prefix = entry.data.get(CONF_TOPIC_PREFIX)
    device = dr.async_get(hass).async_get_device_by_identifier(boiler_identifier(prefix), entry.entry_id) if prefix else None
    return (device and (device.name_by_user or device.name)) or TEXT[lang]["boiler"]


def summary_heating(hass, entry, hub, lang):
    """The boiler's name, then the water temperature limits of the room plan as Home Assistant last read it, with
    the lowest one automatic and its value now (fw/telemetry/flow) on an E32 that has the choice."""
    from .e32_room_flow import MINIMUM_AUTOMATIC_KEY, minimum_flow_now
    t = TEXT[lang]
    lines = [_boiler_name(hass, entry, lang)]
    plan = _plan(hub)
    low, high = (_number(plan.get(key)) for key in ("minimum_flow_c", "maximum_flow_c")) if plan else (None, None)
    if high is not None:
        if plan.get(MINIMUM_AUTOMATIC_KEY) is True:
            now = minimum_flow_now(getattr(hub, "summary", None))
            lines.append(t["limits_auto_now"].format(high=figure(high, lang), now=figure(round(now[0]), lang))
                         if now is not None else t["limits_auto"].format(high=figure(high, lang)))
        elif low is not None:
            lines.append(t["limits_own"].format(low=figure(low, lang), high=figure(high, lang)))
    return lines


def summary_devices(hass, entry, hub, lang):
    """"2 Bluetooth sensors · 3 Shelly valves · 1 heating circuit": what the E32 reports it talks to itself."""
    from .e32_valves import GATEWAY_MODEL
    t = TEXT[lang]
    if hub is None or not hub.fresh:
        return [t["no_data"]]
    valves = sum(1 for room in hub.valves.values() if isinstance(room, dict)
                 for valve in room.get("valves", []) if isinstance(valve, dict) and valve.get("model") == GATEWAY_MODEL)
    parts = []
    for count, key in ((len(hub.ble), "ble"), (valves, "shelly"), (len(hub.circuits), "circuit")):
        if count:
            parts.append(t[key + "_one"] if count == 1 else t[key].format(n=count))
    return [" · ".join(parts) if parts else t["no_devices"]]


def summary_notifications(hass, entry, hub, lang):
    from .notifications import anything_on, notification_options
    return [TEXT[lang]["on" if anything_on(notification_options(entry)) else "notifications_off"]]


def summary_energy(hass, entry, hub, lang):
    """"Gas meter · Gas price · outdoor: KNMI · 22 kW": which optional inputs are set (Configure → Energy)."""
    from .energy_input import (CONF_BOILER_KW, CONF_FORECAST, CONF_GAS_METER, CONF_GAS_PRICE, CONF_GAS_PRICE_ENTITY,
                               CONF_OUTDOOR, CONF_WATER_METER, energy_options)
    t, options, parts = TEXT[lang], energy_options(entry), []
    if options.get(CONF_GAS_METER):
        parts.append(t["gas_meter"])
    if options.get(CONF_GAS_PRICE_ENTITY) or options.get(CONF_GAS_PRICE) is not None:
        parts.append(t["gas_price"])
    if (outdoor := options.get(CONF_OUTDOOR)) and type(outdoor) is str:
        state = hass.states.get(outdoor)
        name = state.attributes.get("friendly_name") if state is not None else None
        parts.append(t["outdoor"].format(name=name if type(name) is str and name else outdoor))
    if _number(options.get(CONF_BOILER_KW)) is not None:
        parts.append(t["boiler_kw"].format(kw=figure(options[CONF_BOILER_KW], lang)))
    if options.get(CONF_WATER_METER):
        parts.append(t["water_meter"])
    if options.get(CONF_FORECAST):
        parts.append(t["forecast"])
    return [" · ".join(parts) if parts else t["energy_none"]]


def summary_general(hass, entry, hub, lang):
    return [entry.title]


def summary_advanced(hass, entry, hub, lang):
    return [TEXT[lang]["advanced"]]


# -- the example section: Dashboard and name (the options step "general" uses the same two functions) -------------

def general_values(values):
    """(name, dashboard) of Dashboard and name, validated as the options step "general" always did: a name of 1 to
    80 characters (surrounding spaces dropped), invalid_name on the field "name"; the tick a bool, else setup_invalid."""
    name = str(values.get("name", "")).strip()
    dashboard = values.get(CONF_CREATE_DASHBOARD, False)
    if not name or len(name) > NAME_MAX:
        raise SettingsError("invalid_name", "name")
    if type(dashboard) is not bool:
        raise SettingsError("setup_invalid")
    return name, dashboard


def general_unchanged(entry, name, dashboard):
    return name == entry.title and dashboard == entry.options.get(CONF_CREATE_DASHBOARD, False)


def commit_general(hass, entry, before, name, dashboard):
    """Store the name and the tick in one guarded configuration write (product.commit_configuration); a refusal is
    SettingsError setup_changed or setup_platform_unsupported, anything else it raises setup_save_uncertain."""
    from .product import commit_configuration
    try:
        commit_configuration(hass, entry, before, title=name, options={**entry.options, CONF_CREATE_DASHBOARD: dashboard})
    except ValueError as err:
        code = str(err)
        raise SettingsError(code if code in {"setup_changed", "setup_platform_unsupported"}
                            else "setup_save_uncertain") from None


def read_general(hass, entry, item=None):
    return {"name": entry.title, CONF_CREATE_DASHBOARD: entry.options.get(CONF_CREATE_DASHBOARD, False) is True}


def save_general(hass, entry, item, values):
    from .product import configuration_snapshot
    name, dashboard = general_values(values)
    if not general_unchanged(entry, name, dashboard):
        commit_general(hass, entry, configuration_snapshot(entry), name, dashboard)
    return read_general(hass, entry)


for _order, (_name, _summary, _available) in enumerate((
        ("rooms", summary_rooms, _connected), ("house", summary_house, _connected),
        ("heating", summary_heating, _connected), ("devices", summary_devices, _connected),
        ("notifications", summary_notifications, None), ("energy", summary_energy, None),
        ("general", summary_general, None), ("advanced", summary_advanced, None))):
    register_section(_name, summary=_summary, available=_available, order=_order)
register_section("general", read_general, save_general)
_load_sections()


# -- the overview -------------------------------------------------------------------------------------------------

_FAILED: set[str] = set()  # sections whose summary failed once in this run (logged once, not on every overview)


def overview(hass, entry, lang, admin):
    """The overview answer: per section its summary lines, whether it is available and has an editor."""
    hub = _hub(hass, entry)
    sections = []
    for section in sorted(SECTIONS.values(), key=lambda s: s.order):
        try:
            reason = section.available(hass, entry, hub) if section.available else None
            lines = [line for line in (section.summary(hass, entry, hub, lang) if section.summary else [])
                     if type(line) is str and line]
        except Exception:  # noqa: BLE001 - one section's summary never breaks the overview
            if section.name not in _FAILED:
                _FAILED.add(section.name)
                _LOGGER.exception("The summary of the settings section %s could not be made", section.name)
            reason, lines = None, []
        sections.append({"name": section.name, "title_key": section.name, "summary": lines,
                         "available": reason is None, "reason": reason,
                         "editable": section.read is not None and section.save is not None})
    return {"admin": admin, "language": lang, "module_url": URL, "configure_path": CONFIGURE_PATH,
            "sections": sections}


# -- the websocket commands ----------------------------------------------------------------------------------------

def _send_error(connection, msg_id, err, data=None):
    """The error with its code; its field, placeholders and any extra data in the error's data slot."""
    payload = {"field": err.field, "placeholders": {k: str(v) for k, v in err.placeholders.items()}, **(data or {})}
    connection.send_error(msg_id, err.key, f"Settings: {err.key}", translation_key=err.key,
                          translation_domain=DOMAIN, translation_placeholders=payload)


def _section(name):
    section = SECTIONS.get(name)
    if section is None:
        raise SettingsError("unknown_section")
    return section


def _failure(err):
    """A Home Assistant error of a write to the E32 as the panel's code: the E32's own key when it names one."""
    key = getattr(err, "translation_key", None)
    return SettingsError(key if type(key) is str and key else "e32_unreachable")


@websocket_api.websocket_command({vol.Required("type"): "open_thermostat/settings/overview",
                                  vol.Required("entry_id"): str, vol.Optional("language"): str})
@callback
def ws_overview(hass, connection, msg):
    try:
        entry = _entry(hass, msg["entry_id"])
    except SettingsError as err:
        _send_error(connection, msg["id"], err)
        return
    admin = bool(getattr(connection.user, "is_admin", False))
    connection.send_result(msg["id"], overview(hass, entry, language(hass, msg.get("language")), admin))


@websocket_api.websocket_command({vol.Required("type"): "open_thermostat/settings/get",
                                  vol.Required("entry_id"): str, vol.Required("section"): str,
                                  vol.Optional("item"): vol.Any(None, str)})
@websocket_api.async_response
async def ws_get(hass, connection, msg):
    try:
        entry = _entry(hass, msg["entry_id"])
        section = _section(msg["section"])
        if section.read is None:
            raise SettingsError("unknown_section")
        result = await read_model(hass, entry, section, msg.get("item"))
    except HomeAssistantError as err:
        _send_error(connection, msg["id"], _failure(err))
    except Exception as err:  # noqa: BLE001 - a section's refusal (SettingsError or FlowError)
        if (known := as_settings_error(err)) is None:
            raise
        _send_error(connection, msg["id"], known)
    else:
        connection.send_result(msg["id"], result)


@websocket_api.websocket_command({vol.Required("type"): "open_thermostat/settings/save",
                                  vol.Required("entry_id"): str, vol.Required("section"): str,
                                  vol.Optional("item"): vol.Any(None, str),
                                  vol.Required("token"): vol.Match(r"^[a-f0-9]{64}$"), vol.Required("values"): dict})
@websocket_api.async_response
async def ws_save(hass, connection, msg):
    # Administrators only, at the backend (the panel's read-only page is a courtesy, not the rule).
    if not getattr(connection.user, "is_admin", False):
        _send_error(connection, msg["id"], SettingsError("not_admin"))
        return
    try:
        entry = _entry(hass, msg["entry_id"])
        section = _section(msg["section"])
        if section.save is None or section.read is None:
            raise SettingsError("unknown_section")
        item = msg.get("item")
        current = await read_model(hass, entry, section, item)
        if current["token"] != msg["token"]:
            _send_error(connection, msg["id"], SettingsError("changed_elsewhere"), current)
            return
        saved = await _call(section.save, hass, entry, item, msg["values"])
        model = _scrub(saved) if type(saved) is dict else (await read_model(hass, entry, section, item))["model"]
    except HomeAssistantError as err:
        _send_error(connection, msg["id"], _failure(err))
    except Exception as err:  # noqa: BLE001 - a refusal has a code; anything else is logged and said plainly
        if (known := as_settings_error(err)) is not None:
            _send_error(connection, msg["id"], known)
            return
        _LOGGER.exception("The settings section %s could not be saved", msg.get("section"))
        _send_error(connection, msg["id"], SettingsError("save_uncertain"))
    else:
        connection.send_result(msg["id"], {"model": model, "token": token(model)})


COMMANDS = (ws_overview, ws_get, ws_save)
