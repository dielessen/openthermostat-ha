"""Optional, integration-managed Lovelace dashboard for thermostat rooms.

The views, built from the entity registry (renamed entity IDs are followed,
disabled and absent entities are left out) with built-in cards, the week
planner and, per room, the room status card (frontend/room-status-card.js):

* Overview (first), as the owner's sketch: the house card across the top
  (custom:openthermostat-house: what the boiler does now in a band of its
  colour, today's hot water, gas and burner starts as large figures, a problem
  with its reason that leads to Repairs, and the one room that is on; the day so
  far; without a heat request and boiler activity there is no card,
  and the rooms that want heat with the boiler request and the problem tile
  stand there instead); under it, side by side on a wide screen and in this
  order on a phone, Rooms (one status card per other room: now, why it heats or
  not, what it does in a word), Today (when each room warms up and how yesterday
  went, what weather compensation asks) and House (the holiday planner and the
  outdoor temperature; home or away and the next holiday only while there is no
  house card, which shows them since 1.4.1). Nothing else;
* Rooms: per room its thermostat, 24-hour graph, sensors, windows and people,
  and what it learned for that room; then the sensors that feed no single room;
* Room settings, only with rooms of the older Home Assistant setup: the first
  such room's editor, and one subview per such room. (The Week program tab of
  1.4 is gone in 1.4.1: a room's week program is on its own screen in the
  Settings tab, #room/<id>, where the planner is built in; the card
  custom:openthermostat-e32-week stays a card anyone can add by hand.)
* Boiler, in this order: Now (one card, custom:openthermostat-boiler-now: what
  the boiler does in a band of its colour with its display code in words, the
  connection with the boiler and whether it serves hot water; the water to the
  heating and back, the burner power and its starts in the last hour as large
  figures, across the whole width on a wide screen), the heating advice (a strip
  across the whole width too), Today and this week
  (today's gas and burner as figures, the one chart of the gas per day and the
  burner hours per day), Hot water (its temperature and target, today's taps and
  keeping warm, what the boiler did in the last 24 hours), What the boiler
  reports (its values in groups), the last 24 hours and the boiler settings. The
  thermostat on the bus and the raw boiler data are on Diagnostics;
* Learning (1.4.3, design docs/engineering/HA-DASHBOARD-ONTWERP-1.4.3.nl.md
  chapter 4): what the E32 knows across the view (the knowledge ring and the
  learning path), a learning card per room side by side
  (custom:openthermostat-learning-room: its facts in figures, what it does not
  know yet says what it still needs), today's plan, house and boiler (the curve
  and what it learned from the boiler, as tiles), yesterday (the four headline
  figures, what stood out, missed comfort, the rest of the scoreboard and the
  daily summary), what it changed by itself and what is worth checking, two
  columns each; who controls the boiler in the trial run and one quiet line
  with Smart warm-up, weather compensation and the comfort style at the bottom;
* Diagnostics: the connection with the E32 in plain words (is it heard, do
  the room values reach it, the MQTT broker, the firmware), the E32 itself, the
  thermostat on the boiler bus, the energy and hot water counters, the raw boiler data and the hot water capability,
  and the older Home Assistant rooms' heat model and history while such rooms are left;
* Settings (last, 1.4; an E32 installation): one panel card, the settings app (custom:openthermostat-settings,
  settings.py): every section with what is set now, and the editor of each section; each room status card's
  "Settings" button opens its room there;
* Comparison (subview, trial run with a thermostat on the bus only).

On top of every view (1.4.1, CONTRACT-1.4.1 §9): the house banner (custom:openthermostat-house-banner,
frontend/openthermostat-house-banner.js), shown only while the house mode is summer: the summer sentence and "Switch
summer mode off". In a sections view it is the view's header card, in a panel view the first card of a vertical stack
with the view's card; Home Assistant hides it (a visibility condition on the house mode select) otherwise, and the
element itself draws nothing then.

Layout (1.4.3, one width for every tab): every view is sections with at most four columns (Home Assistant shows as
many as the screen holds, each 320 to 500 px wide: four on a 1920 px monitor, two at 1280 px with the sidebar open,
one on a phone), so every tab fills the screen as the Overview; a strip across the top spans all four (_span: Home
Assistant clamps a span to the columns it shows). In a section across n columns the cards lie on 12 x n grid
columns: 12 is one view column (the room cards side by side), "full" the whole section (_full).
A section hides as a whole while nothing in it
has a value, so a heading never stands over nothing; a card is as wide as its
section, or one of a tidy pair of half-width cards (tiles, figures, a gauge) that
appear together on one condition (never one half card alone); a note is one
sentence with the rest behind "More"; a card whose text can change is one card
instead of cards that come and go; one icon per concept (ICONS).

Rows, tiles and graphs without a value stay hidden until they have one, so a
boiler that never reports a value shows no "Unknown" for it.

A stored Lovelace config has no per-viewer language, so the few fixed
headings follow the Home Assistant language (English or Dutch) and the
dashboard is rebuilt when that changes. Entity names come from Home
Assistant's own translations.
"""

import asyncio
import json
import logging
import re

from homeassistant.components import frontend
from homeassistant.components.lovelace.const import LOVELACE_DATA
from homeassistant.components.lovelace.dashboard import LovelaceStorage
from homeassistant.const import EVENT_CORE_CONFIG_UPDATE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_call_later
from homeassistant.util import slugify

from .const import DOMAIN
from .e32_flow import CURVE_CARD_TYPE, KNOWLEDGE_CARD_TYPE
from .product import is_product
from .week_planner import ROOM_CARD_TYPE

# Per room (1.1): temperature against target and why it heats or not, from the room's Reason sensor.
ROOM_STATUS_CARD_TYPE = "custom:openthermostat-room-status"

_LOGGER = logging.getLogger(__name__)
# Registry and language changes come in bursts (a start creates every entity one by one): one rebuild
# once they settled this long after the first (R4-11).
REGISTRY_SETTLE_SECONDS = 2

DEVICE_DIAGNOSTIC_METRICS = (
    "connected",
    "memory_free",
    "memory_min_free",
    "memory_max_alloc",
    "rtc_temperature",
    "cpu_temperature",
    "uptime",
)

# The groups of boiler fields (boiler_group) under "What the boiler reports" on the Boiler view, one titled card
# each, in this order. The settings are a section of their own (last on that view); the thermostat on the bus and
# the raw group (unreliable raw values) are on Diagnostics (dashboard-spec §5.6, §5.7, §8).
REPORTED_GROUPS = ("heating", "dhw", "status", "counters")
STATUS_FIELDS = frozenset({"display_code", "service_number", "maintenance_message", "ionisation_current",
                           "plus_flame_current"})
SETTINGS_FIELDS = frozenset({"maximum_burner_power", "pump_run_on", "minimum_burner_period", "pump_modulation_maximum",
                             "pump_modulation_minimum", "pump_start_temperature", "dhw_charge_optimisation_enabled",
                             "dhw_flow_temperature_offset", "dhw_circulation_enabled", "dhw_disinfection_temperature",
                             "reported_dhw_type", "plus_heating_temperature", "plus_maximum_burner_power"})
# The energy and hot water counters (definition v2; only boilers that report them fill these in).
COUNTER_KEYS = ("energy", "energy_heating", "energy_warm_water", "energy_unattributed", "warm_water_usage",
                "warm_water_avg_flow", "burner_observed_time")


def boiler_group(name):
    """The Boiler view group of boiler field ``name``; "raw" for the unreliable raw values (Diagnostics)."""
    from .boiler_fields import INDEX_BY_NAME, quality
    index = INDEX_BY_NAME.get(name)
    from .v1_boiler_fields import LIVE_FLOW
    if name in LIVE_FLOW:
        return "dhw"  # 1.4.5: the hot water flow is made only once it moves, so it is a measured value, not a raw one
    if (index is not None and quality(index) == 1) or name.startswith("raw_"):
        return "raw"
    if name.startswith("thermostat_"):
        return "thermostat"
    if name in STATUS_FIELDS or name.startswith("last_"):
        return "status"
    if name.endswith(("_starts", "_runtime")) or name == "boiler_uptime":
        return "counters"
    if name.startswith("configured_") or "hysteresis" in name or name in SETTINGS_FIELDS:
        return "settings"
    if "dhw" in name or name.startswith(("storage_", "solar_")):
        return "dhw"
    return "heating"

# E32 room entities: unique ID f"{prefix}_e32_room_{room id}_{key}" (longest key first).
ROOM_KEYS = ("valve_position", "valve_battery", "valve_problem", "valve_control", "fallback_setpoint", "inactive_until", "heating_start", "flow_advice", "temperature", "thermostat",
             "learning", "reason", "warm_on_time", "overshoot", "relearn",
             "setpoint", "status", "demand", "state")
# Yesterday's scoreboard of the house (scoreboard.py, E32 rc.4): unique ID f"{prefix}_hub_{key}".
SCOREBOARD_HOUSE = ("burner_starts_per_heating_hour", "short_cycling_hours", "heating_gas_yesterday", "gas_per_degree_day")
# Today's hot water from the E32 (unique ID f"{prefix}_hub_{key}"): keeping warm without a tank, the charges with one.
DHW_TODAY = ("dhw_taps_today", "dhw_keep_warm_today", "dhw_charges_today", "dhw_burner_time_today")
BLE_KEYS = ("temperature", "humidity", "battery")

# Boiler essentials: (key, boiler field, older hub metric).
ESSENTIALS = (
    ("flow", "measured_flow_temperature", "boiler_current_flow_temperature"),
    ("return", "measured_return_temperature", None),
    ("max_ch", "configured_heating_temperature", None),
    ("modulation", "reported_burner_modulation", "boiler_burner_power"),
    ("pressure", "pressure", "boiler_pressure"),
    ("dhw", "measured_dhw_temperature", "boiler_current_hot_water_temperature"),
    ("code", "display_code", "boiler_display_code"),
)

# Weather compensation and learning on the product device (e32_flow.py): unique ID f"{prefix}_flow_{key}";
# "curve" is what weather compensation asks now, which the heating-curve card draws (E32 rc.5).
FLOW_KEYS = ("source", "weather_curve", "curve_design_flow_c", "apply_learned", "curve", "comfort_style")
COMPARISON_PATH = "comparison"
# One icon per concept, the same in every view (dashboard-spec §1): the boiler's values, what the boiler does
# (heating flame, hot water tap, resting boiler), the gas and the burner, and the sections that carry them.
ICONS = {"flow": "mdi:thermometer-chevron-up", "return": "mdi:thermometer-chevron-down",
         "max_ch": "mdi:thermometer-high", "modulation": "mdi:fire", "pressure": "mdi:gauge",
         "dhw": "mdi:water-thermometer", "dhw_target": "mdi:thermometer-water", "code": "mdi:information-outline",
         "dhw_flow": "mdi:faucet",
         "heating": "mdi:fire", "hot_water": "mdi:faucet", "gas": "mdi:meter-gas", "burner_starts": "mdi:counter",
         "burner_time": "mdi:timer-outline", "house": "mdi:home-thermometer", "learning": "mdi:school-outline",
         "boiler": "mdi:water-boiler", "now": "mdi:water-boiler", "week": "mdi:chart-bar",
         "history": "mdi:chart-line", "settings": "mdi:cog-outline", "yesterday": "mdi:scoreboard-outline",
         "thermostat": "mdi:thermostat", "knowledge": "mdi:home-analytics", "curve": "mdi:chart-bell-curve-cumulative",
         "insight": "mdi:information-outline", "free_heat": "mdi:weather-sunny",
         # 1.1.1 stage B: Today's plan (heating_plan.py) and why the E32 plans it so.
         "plan": "mdi:calendar-clock", "why": "mdi:lightbulb-on-outline",
         # rc.5 (P18, the owner's sketch of the Overview): Today with its two lines, and the House card's rows.
         "today": "mdi:calendar-today", "warm_up": "mdi:clock-outline", "weather": "mdi:sun-thermometer",
         "house_mode": "mdi:home-account", "holiday": "mdi:calendar-month-outline",
         # rc.7: Diagnostics' connection lines (fine, waiting, a problem, not known, an update) and Your boiler's lines
         # (the boiler's own highest water temperature, its rest, the lowest water temperature it heats at).
         "connection": "mdi:lan-connect", "valves": "mdi:radiator", "link_ok": "mdi:check-circle-outline", "link_wait": "mdi:clock-alert-outline",
         "link_problem": "mdi:alert-circle-outline", "link_unknown": "mdi:help-circle-outline",
         "link_update": "mdi:arrow-up-circle-outline", "ceiling": "mdi:arrow-collapse-up", "rest": "mdi:timer-sand",
         "lowest": "mdi:arrow-collapse-down"}
# The sketch's coloured icons in a markdown line (_icon), in the colours of Home Assistant's default theme: heating
# (--state-climate-heat-color, deep orange), information (--info-color) and the sun (--amber-color).
ICON_COLOURS = {"heating": "#ff6f22", "insight": "#039be5", "free_heat": "#ffc107", "why": "#039be5",
                # rc.5 (P18): the Overview's Today, blue as in the sketch (information: --info-color).
                "warm_up": "#039be5", "weather": "#039be5",
                # rc.7: --success-color, --warning-color, --error-color, --disabled-color and --info-color; the boiler's
                # lines in the heating colour, what it still learns in the information colour.
                "link_ok": "#4caf50", "link_wait": "#ffa600", "link_problem": "#db4437", "link_unknown": "#9e9e9e",
                "link_update": "#039be5", "ceiling": "#ff6f22", "rest": "#ff6f22", "lowest": "#ff6f22",
                "learning": "#039be5"}
TEXT = {
    "en": {
        "heating": "Heating", "boiler_view": "Boiler", "diagnostics": "Diagnostics", "settings_view": "Settings",
        "room_settings": "Room settings", "now": "Now", "rooms": "Rooms",
        "settings": "{room} settings",
        "boiler_request": "Boiler request", "flow": "Water to heating", "return": "Water back",
        "modulation": "Burner power", "pressure": "Pressure", "dhw": "Hot water", "code": "Display code",
        "max_ch": "Boiler maximum", "status": "Status", "problem": "Heating",
        "starts_hour": "Starts per hour", "short_cycling": "Switching on and off too often",
        "agreement": "Agreement with thermostat",
        "mode": "Mode", "without_ha": "Temperature without a week program",
        "compare": "E32 and thermostat", "e32_request": "Boiler request E32",
        "thermostat_request": "Thermostat request", "compare_heating_time": "Heating time today",
        "compare_starts": "Burner starts today", "heating_per_day": "Heating time per day",
        "boiler": "Boiler", "bluetooth": "Bluetooth sensors", "bluetooth_link": "Link to a room",

        "shadow": "Trial run: the E32 calculates along but does not control the boiler yet; your current "
                  "thermostat or the boiler's own control stays in charge.",
        "active": "The E32 controls the boiler.",
        "next": "Next step: run the boiler test on the E32's Boiler page and confirm the takeover under Rooms → Active "
                "control. Until then the E32 sends nothing to the boiler.",
        "how": "The E32 keeps your rooms running, also without Home Assistant.",
        "overview": "Overview",
        "house": "House",
        "learning_view": "Learning",
        # 1.4.3 (LEARN-TAB): the Learning view's own words (glossary block "1.4.3 LEARN-TAB").
        "per_room": "Per room",
        "care_link": "Comfort and boiler care",
        "settings_heating": "Settings → Heating and boiler", "configure_heating": "Configure → Heating and boiler",
        "row_smart_on": "Smart warm-up on", "row_smart_off": "Smart warm-up off",
        "row_curve_on": "Weather compensation on", "row_curve_off": "Weather compensation off", "row_style": "Comfort style {style}",
        "more": "More",
        # 1.1.1 stage B: the E32's heating plan (heating_plan.py).
        "plan_today": "Today's plan", "plan_why": "Why",
        # 1.4.2 (HA-LIFETIME): the one confirmation under Today's plan (no Repairs item any more), the advice lines
        # that were Repairs items, and a room's figures while it heats along only or is off (F16).
        "plan_confirm": "Let the E32 plan the heating", "plan_confirm_ask": "Let the E32 plan the heating from now on?",
        "worth_checking": "Worth checking",
        "scoreboard_heat_along": "not measured: the room heats along only",
        "scoreboard_room_off": "not measured: the room is off",
        "cycling_ok": "The burner runs calmly.",
        "cycling_info": "The E32 lengthens the burner rest step by step.",
        "burner": "Burner",
        "problem_more": "All reasons",
        "legacy_rooms": "Rooms (older setup)",
        "group_heating": "Heating", "group_dhw": "Hot water", "group_status": "Status and faults",
        "group_counters": "Counters", "group_settings": "Boiler settings",
        "group_thermostat": "Thermostat on the bus", "history_24h": "Last 24 hours",
        "boiler_note": "Values as the boiler reports them; a value the boiler does not send is left out. "
                       "Burner power is a percentage of the boiler's maximum, not kW; \"active\" is what the boiler "
                       "reports, not a separate check.",
        "settings_note": "Settings the boiler reports only when asked are read at start-up and every six hours; the "
                         "time of the last reading is on the sensor.",
        "raw": "Raw boiler data",
        "raw_note": "For troubleshooting: values exactly as the boiler sends them, not checked by the E32.",
        "e32_device": "E32",
        # rc.7: Diagnostics, "Connection with the E32": is the E32 heard, do the room values reach it (the heat request
        # sensor's ha_input, heating_link.HeatingInputWatch), the MQTT broker and the firmware; plain words first.
        "connection": "Connection with the E32",
        "link_heard_yes": "The E32 reports to Home Assistant: yes, last at {at}.",
        "link_heard_no": "The E32 reports to Home Assistant: no, nothing heard since {at}.",
        "link_heard_never": "The E32 reports to Home Assistant: not yet.",
        "link_heard_fix": "Check that the E32 has power and Wi-Fi and that the MQTT broker runs. Meanwhile the E32 keeps "
                          "heating the rooms by itself.",
        "link_input_yes": "Room values reach the E32: yes, last at {at}.",
        "link_input_quiet": "Room values reach the E32: none in the last 15 minutes; the last at {at}.",
        "link_input_no": "Room values reach the E32: no, not since {at}.",
        "link_input_no_plain": "Room values reach the E32: no.",
        "link_input_unknown": "Room values reach the E32: the E32 does not say (older firmware).",
        "link_refused": "The E32 refused the last value at {at}: {why}.",
        "link_refused_earlier": "The E32 last refused a value at {at}: {why}.",
        "link_input_fix": "Until they arrive, the E32 runs the rooms on its own sensors and week programs. Home "
                          "Assistant keeps sending them; if this stays, restart Home Assistant.",
        "link_broker_ok": "MQTT broker: the E32 and Home Assistant both reach it.",
        "link_broker_failed": "MQTT broker: Home Assistant could not send through it at {at}: {error}.",
        "send_timeout": "the broker did not take the value in time",
        "send_unreachable": "Home Assistant could not reach the broker",
        "send_waiting": "too many messages were waiting for the broker",
        "link_firmware": "Firmware: {version}, up to date.",
        "link_firmware_new": "Firmware: {version}; {latest} is available under Settings → Updates.",
        "link_firmware_skipped": "Firmware: {version}; you skipped {latest}.",
        "link_firmware_installing": "Firmware: installing {latest} now.",
        "link_sent": "Home Assistant last sent a value at {at}.",
        "link_error": "Last send error at {at}: {error}.",
        "link_dropped": "Values dropped while the broker did not answer: {n}.",
        "link_unread": "Messages the E32 could not read since it started: {n}, last: {topic}, {reason}.",
        "unread_too_large": "too large", "unread_too_deep": "nested too deeply", "unread_malformed": "broken or cut off",
        "unread_unknown_device": "from no known device", "unread_wrong_type": "not a device state",
        "why_too_large": "the message was too long", "why_invalid_json": "it could not read the message",
        "why_no_entity": "the message named no Home Assistant entity",
        "why_unknown_kind": "it does not know that kind of value; update the E32",
        "why_invalid_value": "the value was outside what it accepts", "why_unknown_room": "it does not know that room",
        "estimates": "Energy and hot water counters",
        "estimates_empty": "This boiler reports no energy or hot water counters yet; boilers that do (EMS+) fill "
                           "them in here. The Boiler tab and the E32's Home page estimate the gas per day from "
                           "the burner power and the boiler's power.",
        "older_rooms": "Rooms (older setup)",
        # 1.4.4 (HA-CARDS-144): every radiator valve on Diagnostics with what it reports and the E32's finding; the words
        # of the room card (frontend/room-card.js) word for word.
        "valves_diag": "Radiator valves", "valve_open": "{n} % open", "valve_set_to": "set to {t} °C",
        "valve_battery": "battery {n} %", "valve_offline": "not reporting", "valve_no_reading": "no reading",
        "valve_too_large": "message too large ({kb} KB)", "valve_too_large_plain": "message too large",
        # 1.4.5 (FW-TRV-DOC-145): the E32 shortened the room's valve document to fit (``trimmed``), a grey note.
        "valves_trimmed": "shortened",
        "valve_put_back": "put back to {t} °C", "valve_put_back_plain": "put back", "valve_own_schedule": "running its own program",
        "valve_own_sensor": "on its own sensor (the E32 is putting it back on the room's sensor)",
        "valve_off_by_user": "switched off by you", "valve_gave_up": "not responding to the E32",
        "valve_gateway": "Valve {id} on BLU Gateway {n}",
        "legacy_boiler_note": "What the boiler reports over its bus (EMS), not proof of an E32 command. Unknown or old values are not zero. "
                              "Burner power is a percentage of the boiler's maximum, not kW.",
        "flow_graph": "Water temperatures: target, to heating and back", "flow_selection": "Target (boiler)",
        "measured_flow": "Water to heating", "measured_return": "Water back",
        "current_flow": "To heating, as the boiler reports it",
        "modulation_graph": "Burner power (%)", "modulation_series": "Burner power (%)",
        "dhw_graph": "Hot water temperatures", "dhw_selected": "Selected",
        "dhw_measured": "Measured", "dhw_target": "Target",
        "states_graph": "Reported heating / hot water / flame / pump", "state_heating": "Reported heating",
        "state_dhw": "Reported hot water", "state_flame": "Reported flame bit", "state_pump": "Reported pump bit",
        "dhw_card": "Hot water capability and quality",
        "dhw_note": "Hot water, view only: the last values the boiler reported (their age is not checked); "
                    "nothing is sent to the boiler.",
        "dhw_profile": "Profile", "dhw_status": "status", "unknown": "Unknown",
        "estimates_note": "Energy and volume are estimates from reported values, not gas or heat meters.",
        "energy_chart": "Estimated energy per day (not a meter)", "volume_chart": "Hot water volume per day",
        "flame_chart": "Observed flame time per day",
        "models_note": "Room heat models are estimates, not measured heat; unknown or stale inputs leave gaps.",
        "room_history": "{room}: target and measured", "room_measured": "Measured", "room_target": "Target",
        "dhw_taps": "Taps today", "dhw_today": "Hot water today",
        "advice": "Advice", "advice_where": "Where", "advice_confidence": "Confidence",
        "advice_note": "Advice only: nothing is changed automatically.",
        "learned_house": "House and boiler",
        "learned_changes": "What it changed by itself",
        "confidence_low": "low", "confidence_medium": "medium", "confidence_high": "high",
        "gas_heating": "Heating", "gas_hot_water": "Hot water", "gas_keep_warm": "Of which keeping hot water warm",
        "gas_tapping": "Tapping", "gas_keeping_warm": "Keeping warm", "gas_hot_water_total": "Hot water (total)",
        "activity_timeline": "What the boiler does (24 hours)", "activity": "Boiler",
        "dhw_use_note": "Tapping is hot water used at a tap; keeping warm is the boiler reheating its store or "
                        "exchanger without a tap, nothing more. The E32 tells them apart with the most direct signal "
                        "your boiler reports. Today's figures follow within five minutes after a hot water period ends.",
        "dhw_use_note_tank": "Tapping is hot water drawn from the tank, counted from the boiler's hot water flow, so the "
                             "litres are approximate; charging the tank is the boiler heating it again. Today's figures "
                             "follow within five minutes after a hot water period ends.",
        "gas_per_day": "Gas per day", "gas_split_per_day": "Hot water: tapping and keeping warm",
        "gas_measured": "Measured with your gas meter, split by what the boiler did.",
        "gas_estimate": "Estimated from the burner power and the boiler's heating power (no gas meter).",
        "gas_note": "Add heating and hot water to the Energy dashboard under Gas consumption; tapping and keeping warm "
                    "are parts of hot water, so leave them out there. A gas meter that reports once an hour can put the "
                    "last hour's gas on the next day.",
        "gas_note_tank": "Add heating and hot water to the Energy dashboard under Gas consumption. With a hot water tank "
                         "all its gas is hot water: a tap and the charge after it often run together. A gas meter that "
                         "reports once an hour can put the last hour's gas on the next day.",
        "yesterday": "Yesterday", "burner_per_day": "Burner hours per day",
        "missed_per_day": "Missed comfort per day (minutes)",
        "missed_series": "Missed comfort",
        "day_burner": "Burner {h} h, {starts}{short}.",
        "day_gas": "Gas: heating {heating}, hot water {hot_water}.",
        "day_room": "{room}: asked for heat {h} h; warm after {ttt} min on average; missed comfort {missed} min.",
        "day_room_no_step": "{room}: asked for heat {h} h; missed comfort {missed} min.",
        "day_room_plain": "{room}: asked for heat {h} h; warm after {ttt} min on average.",
        "day_room_no_step_plain": "{room}: asked for heat {h} h.",
        "day_missed": "Missed comfort: {missed} min, added up over the rooms that were more than 0.3 °C below their target while in use.",
        "day_outdoor": "Outdoor {low} to {high} °C.", "day_outdoor_one": "Outdoor {low} °C.",
        "day_partial": "Partial day: the E32 was not heard all day, so the figures are incomplete.",
        "scoreboard_on_time": "warm on time",
        "scoreboard_late": "warm {d} late",
        "scoreboard_early": "warm {d} early",
        "scoreboard_overshoot": "{c} °C too warm",
        "scoreboard_hours": "Heating time: {h} h",
        "scoreboard_burner": "Burner starts per heating hour: {n}",
        "scoreboard_short": "Short burner runs: {h} h",
        "scoreboard_gas": "Gas for heating (boiler's estimate): {kwh} kWh",
        "scoreboard_degree_days": "Degree-days: {d}",
        "scoreboard_degree_day": "{v} kWh per degree-day",
        "scoreboard_note": "Every day the E32 checks whether each room was warm on time without getting too warm, how often the burner started and how much gas went to heating. It learns from this; every figure keeps its history on its own sensor.",
        "day_none": "The first day appears here tomorrow.",
        "outdoor": "Outdoor",
        "flow_settings": "Weather compensation and learning",
        "flow_source": "Water temperature set by",
        "house_mode": "House mode", "boiler_now": "Boiler",
        # rc.4: the next holiday under House (house.holidays.v1).
        "holiday_next": "Holiday from {from} to {until}", "holiday_now": "On holiday until {until}",
        "holiday_day": "Holiday on {from}",
        "months": "Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec",
        "compare_link": "E32 compared with your thermostat",
        "no_request": "No boiler request",
        "wanting_one": "1 room wants heat", "wanting_many": "{n} rooms want heat", "wanting_none": "No room wants heat",
        "decimal": ".",
        "flow_short": "Water to heating", "return_short": "Water back",
        "e32": "E32", "thermostat": "Thermostat",
        "comparison_view": "Comparison",
        # 1.4 (issue #9): an Off room's measured temperature and its source in one line ("Off · 17.2 °C (Bluetooth
        # sensor)"); a Home Assistant source by its name.


        "readiness": "Ready to take over?",
        "ready_ready": "Ready: follow the switch-over steps.",
        "ready_waiting": "Not yet: the E32 is still collecting data in the trial run.",
        "ready_not_ready": "Not ready: fix the red items first.",
        "ready_no_comparison": "No thermostat on the boiler bus to compare with, so only the E32 and the boiler "
            "are checked.",
        "ready_stable": "Stable: {stable_hours} of {stable_hours_needed} h without a hang or unexpected restart",
        "ready_periods": "Heating periods compared: {periods_compared} of {periods_needed}, with a night setback, "
            "a morning warm-up and a period without demand",
        "ready_timing": "Heat at the same moments: {timing_events} of {timing_events_needed} starts and stops",
        "ready_flow_limit": "Water temperature request never above the limit: highest {flow_max_c} °C, limit {flow_limit_c} °C",
        "ready_cycling": "Not more heating periods than the thermostat: E32 {heating_periods_e32}, "
            "thermostat {heating_periods_thermostat}",
        "ready_sources": "Room sources work, and a backup sensor has taken over",
        "ready_boiler": "Boiler heard on the bus",
        "ready_boiler_limit": "Boiler maximum known: {boiler_limit_c} °C",
        "fix_timing": "The E32 heats at other moments than your thermostat: check the room targets and week program.",
        "fix_flow_limit": "A request went above the hard limit: check the water temperature limits.",
        "fix_cycling": "The E32 would start the burner more often: check the water temperature limits.",
        "fix_sources": "Check the room sensors (battery, range) and give a room a second source.",
        "fix_boiler": "The E32 hears nothing from the boiler: check the bus cable.",
        "fix_boiler_limit": "The boiler has not reported its maximum: check the bus connection.",
        # rc.5 dashboard (dashboard-spec §1): the Boiler view's sections and today's figures, Yesterday once on the
        # Learning view and who controls the boiler.
        "today_week": "Today and this week", "gas_heating_today": "Heating gas",
        "gas_hot_water_today": "Hot water gas", "starts_today": "Burner starts",
        "burner_today": "Burner time", "boiler_values": "What the boiler reports",
        "who_controls": "Who controls the boiler", "yesterday_figures": "Yesterday",
        "dhw_target_short": "Hot water target",
        # 1.4.5 (HA-DHW-FLOW-145): the hot water flow's tile on the Boiler view: the flow while a tap runs, else this.
        "tapping_now": "Tapping now", "no_tapping": "No tapping",
        # E32 rc.5: the Learning view's what the E32 knows and (1.4.3, folded into Yesterday) what stood out (insight.py).
        "knowledge": "What the E32 knows",
        "noticed": "Noticed",
        # E32 1.3: under the chart while the learned steady-burn floor decides the water temperature (owner's wish).
        "curve_floor": "The lowest water temperature decides here: weather compensation would ask for {curve} °C, but your "
                       "boiler burns steadily only from about {floor} °C water, so the E32 asks for {floor} °C.",
        # rc.5 (P18): the Overview's Today (when each room warms up, what weather compensation asks) and House rows.
        "today": "Today", "home_or_away": "Home or away", "holiday": "Holiday", "plan": "Plan",
        "when_today": "Today", "when_tomorrow": "Tomorrow", "when_date": "On {date}",
        "warm_up_at": "{when} {room} warms up from **{start}** to be {target} °C at **{time}**.",
        "warm_up_estimate": "{when} {room} warms up from **{start}** (estimate) to be {target} °C at **{time}**.",
        "warm_up_ready": "{when} {room} is warm enough for {target} °C at **{time}**; if it cools down before then, the "
                         "warm-up starts earlier.",
        "warm_up_now": "{room} is warming up now to be {target} °C at **{time}**.",
        "warm_up_from": "{when} {room} starts warming up at **{start}**.",
        "warm_up_off": "{when} {room} starts heating at **{time}** for {target} °C (Smart warm-up is off).",
        "arrived_late": "{day} it was warm {m} minutes late.", "arrived_late_one": "{day} it was warm 1 minute late.",
        "arrived_early": "{day} it was warm {m} minutes early.",
        "arrived_early_one": "{day} it was warm 1 minute early.", "arrived_on_time": "{day} it was warm on time.",
        # 1.4.3 (design 4.3): Today says only what the E32 asks; the arithmetic of the line is on the Learning tab.
        "weather_outside": "Outdoor {outdoor} °C", "weather_asks": "the E32 asks {flow} °C water",
        "weather_off": "weather compensation is off; it would ask for {flow} °C water",
        "line_learned": "on the line it learned for your house",
        # rc7: the sentences review (R1, R3): Today in every case, Yesterday in figures, the Learning view.
        "cycling_info_shadow": "Your current thermostat lets the burner switch on and off often; the E32 will lengthen the rest once it controls the boiler.",
        "day_starts": "{n} starts",
        "day_starts_one": "1 start",
        "day_short": " ({short} shorter than 10 minutes)",
        "day_burner_none": "The burner did not start.",
        "scoreboard_not_warm": "not warm within 3 h",
        "scoreboard_short_none": "Short burner runs: none",
        "figures_day": "These figures are from {date}: the E32 has no newer full day.",
        "holiday_hint": "To plan a holiday: Configure → House → House mode and holiday.",
        "dur_h_m": "{h} h {m} min",
        "dur_h": "{h} h",
        "warm_up_now_estimate": "{room} is warming up now (estimate) to be {target} °C at **{time}**.",
        "warm_up_late": "{room} is warming up now; {target} °C may come a little after **{time}**.",
        "warm_up_trial": "{when} {room} would warm up from **{start}** to be {target} °C at **{time}** (trial run).",
        "warm_up_trial_now": "{room} would be warming up now to be {target} °C at **{time}** (trial run).",
        "at_tomorrow": "{time} tomorrow",
        "at_date": "{time} on {date}",
        "today_away": "{room} is set to away: no early warm-up.",
        "today_nobody": "Nobody is home for {room}: no early warm-up.",
        "today_holiday": "{room} is on holiday until {date}; it is warm again when you are back.",
        "today_return": "{room} is warming up for your return.",
        "today_window": "{room} is paused: a window or door is open.",
        "today_summer": "{room}: summer mode, the heating stays off.",
        "today_window_window": "{room} is paused: a window is open.",
        "today_window_door": "{room} is paused: a door is open.",
        "day_yesterday": "Yesterday",
        "day_today": "Today",
        "day_on": "On {date}",
        "arrived_late_long": "{day} it was warm {d} late.",
        "arrived_early_long": "{day} it was warm {d} early.",
        "arrived_not_warm": "{day} it did not get warm within 3 hours.",
        "weather_idle": "when a room asks for heat, the E32 asks {flow} °C water",
    },
    "nl": {
        "heating": "Verwarming", "boiler_view": "Ketel", "diagnostics": "Diagnose", "settings_view": "Instellen",
        "room_settings": "Ruimte-instellingen", "now": "Nu", "rooms": "Ruimtes",
        "settings": "Instellingen {room}",
        "boiler_request": "Ketelvraag", "flow": "Water naar verwarming", "return": "Water terug",
        "modulation": "Brandervermogen", "pressure": "Waterdruk", "dhw": "Warm water", "code": "Displaycode",
        "max_ch": "Maximum van de ketel", "status": "Status", "problem": "Verwarming",
        "starts_hour": "Starts per uur", "short_cycling": "Te vaak aan en uit",
        "agreement": "Overeenstemming met thermostaat",
        "mode": "Stand",
        "without_ha": "Temperatuur zonder weekprogramma",
        "compare": "E32 en thermostaat vergeleken", "e32_request": "Ketelvraag E32",
        "thermostat_request": "Vraag thermostaat", "compare_heating_time": "Verwarmingstijd vandaag",
        "compare_starts": "Branderstarts vandaag", "heating_per_day": "Verwarmingstijd per dag",
        "boiler": "Ketel", "bluetooth": "Bluetooth-sensoren", "bluetooth_link": "Aan een ruimte koppelen",

        "shadow": "Proefperiode: de E32 rekent mee maar stuurt de ketel nog niet; je huidige thermostaat of de "
                  "eigen regeling van de ketel blijft de baas.",
        "active": "De E32 regelt de ketel.",
        "next": "Volgende stap: doe de keteltest op de pagina Ketel van de E32 en bevestig de overname onder Ruimtes → "
                "Actieve regeling. Tot dan stuurt de E32 niets naar de ketel.",
        "how": "De E32 houdt je ruimtes op temperatuur, ook zonder Home Assistant.",
        "overview": "Overzicht",
        "house": "Huis",
        "learning_view": "Leren",
        "per_room": "Per ruimte",
        "care_link": "Comfort en zorg voor de ketel",
        "settings_heating": "Instellen → Verwarming en ketel", "configure_heating": "Configureren → Verwarming en ketel",
        "row_smart_on": "Slim opwarmen aan", "row_smart_off": "Slim opwarmen uit",
        "row_curve_on": "Weerafhankelijke regeling aan", "row_curve_off": "Weerafhankelijke regeling uit",
        "row_style": "Comfortstijl {style}",
        "more": "Meer",
        "plan_today": "Plan voor vandaag", "plan_why": "Waarom",
        "plan_confirm": "Laat de E32 de verwarming plannen",
        "plan_confirm_ask": "Mag de E32 de verwarming voortaan plannen?",
        "worth_checking": "Het nakijken waard",
        "scoreboard_heat_along": "niet gemeten: de ruimte verwarmt alleen mee",
        "scoreboard_room_off": "niet gemeten: de ruimte staat uit",
        "cycling_ok": "De brander loopt rustig.",
        "cycling_info": "De E32 verlengt de rusttijd van de brander stap voor stap.",
        "burner": "Brander",
        "problem_more": "Alle redenen",
        "legacy_rooms": "Ruimtes (oudere opzet)",
        "group_heating": "Verwarming", "group_dhw": "Warm water", "group_status": "Status en storingen",
        "group_counters": "Tellers", "group_settings": "Ketelinstellingen",
        "group_thermostat": "Thermostaat op de bus", "history_24h": "Afgelopen 24 uur",
        "boiler_note": "Waarden zoals de ketel ze meldt; een waarde die de ketel niet stuurt, staat er niet. "
                       "Brandervermogen is een percentage van het maximum van de ketel, geen kW; \"actief\" is wat de ketel "
                       "meldt, geen aparte controle.",
        "settings_note": "Instellingen die de ketel alleen op verzoek meldt, leest de E32 bij het opstarten en daarna "
                         "elke zes uur; wanneer ze voor het laatst zijn gelezen staat op de sensor.",
        "raw": "Ruwe keteldata",
        "raw_note": "Voor het zoeken naar fouten: waarden precies zoals de ketel ze stuurt, niet gecontroleerd "
                    "door de E32.",
        "e32_device": "E32",
        "connection": "Verbinding met de E32",
        "link_heard_yes": "De E32 meldt zich bij Home Assistant: ja, het laatst om {at}.",
        "link_heard_no": "De E32 meldt zich bij Home Assistant: nee, niets gehoord sinds {at}.",
        "link_heard_never": "De E32 meldt zich bij Home Assistant: nog niet.",
        "link_heard_fix": "Controleer of de E32 stroom en wifi heeft en of de MQTT-broker draait. Intussen blijft de E32 de "
                          "ruimtes zelf verwarmen.",
        "link_input_yes": "Ruimtewaarden komen aan bij de E32: ja, het laatst om {at}.",
        "link_input_quiet": "Ruimtewaarden komen aan bij de E32: geen in de laatste 15 minuten; de laatste om {at}.",
        "link_input_no": "Ruimtewaarden komen aan bij de E32: nee, niet meer sinds {at}.",
        "link_input_no_plain": "Ruimtewaarden komen aan bij de E32: nee.",
        "link_input_unknown": "Ruimtewaarden komen aan bij de E32: de E32 meldt het niet (oudere firmware).",
        "link_refused": "De E32 weigerde de laatste waarde om {at}: {why}.",
        "link_refused_earlier": "De E32 weigerde het laatst een waarde om {at}: {why}.",
        "link_input_fix": "Tot ze aankomen regelt de E32 de ruimtes met zijn eigen sensoren en weekprogramma's. Home "
                          "Assistant blijft ze sturen; blijft dit zo, herstart dan Home Assistant.",
        "link_broker_ok": "MQTT-broker: de E32 en Home Assistant bereiken hem allebei.",
        "link_broker_failed": "MQTT-broker: Home Assistant kon er om {at} niets via versturen: {error}.",
        "send_timeout": "de broker nam de waarde niet op tijd aan",
        "send_unreachable": "Home Assistant bereikte de broker niet",
        "send_waiting": "er wachtten te veel berichten op de broker",
        "link_firmware": "Firmware: {version}, actueel.",
        "link_firmware_new": "Firmware: {version}; {latest} staat klaar onder Instellingen → Updates.",
        "link_firmware_skipped": "Firmware: {version}; je hebt {latest} overgeslagen.",
        "link_firmware_installing": "Firmware: {latest} wordt nu geïnstalleerd.",
        "link_sent": "Home Assistant stuurde de laatste waarde om {at}.",
        "link_error": "Laatste verzendfout om {at}: {error}.",
        "link_dropped": "Waarden die wegvielen omdat de broker niet antwoordde: {n}.",
        "link_unread": "Berichten die de E32 niet kon lezen sinds hij startte: {n}, laatste: {topic}, {reason}.",
        "unread_too_large": "te groot", "unread_too_deep": "te diep genest", "unread_malformed": "kapot of afgebroken",
        "unread_unknown_device": "van geen bekend apparaat", "unread_wrong_type": "geen apparaatstatus",
        "why_too_large": "het bericht was te lang", "why_invalid_json": "hij kon het bericht niet lezen",
        "why_no_entity": "het bericht noemde geen Home Assistant-entiteit",
        "why_unknown_kind": "hij kent dat soort waarde niet; werk de E32 bij",
        "why_invalid_value": "de waarde lag buiten wat hij aanneemt", "why_unknown_room": "hij kent die ruimte niet",
        "estimates": "Tellers voor energie en warm water",
        "estimates_empty": "Deze ketel meldt nog geen tellers voor energie of warm water; ketels die dat wel doen "
                           "(EMS+) vullen ze hier in. Het tabblad Ketel en de pagina Huis van de E32 schatten het "
                           "gas per dag uit het brandervermogen en het vermogen van de ketel.",
        "older_rooms": "Ruimtes (oudere opzet)",
        "valves_diag": "Radiatorkranen", "valve_open": "{n} % open", "valve_set_to": "staat op {t} °C",
        "valve_battery": "batterij {n} %", "valve_offline": "meldt zich niet", "valve_no_reading": "geen meting",
        "valve_too_large": "bericht te groot ({kb} KB)", "valve_too_large_plain": "bericht te groot",
        "valves_trimmed": "ingekort",
        "valve_put_back": "teruggezet naar {t} °C", "valve_put_back_plain": "teruggezet", "valve_own_schedule": "eigen programma",
        "valve_own_sensor": "op eigen sensor (de E32 zet hem terug op de sensor van de ruimte)",
        "valve_off_by_user": "door jou uitgezet", "valve_gave_up": "geeft niet thuis",
        "valve_gateway": "Kraan {id} aan BLU Gateway {n}",
        "legacy_boiler_note": "Wat de ketel via zijn bus (EMS) meldt, geen bewijs van een E32-opdracht. Onbekende of "
                              "oude waarden zijn geen nul. Brandervermogen is een percentage van het maximum van de ketel, geen kW.",
        "flow_graph": "Watertemperaturen: doel, naar verwarming en terug", "flow_selection": "Doel (ketel)",
        "measured_flow": "Water naar verwarming", "measured_return": "Water terug",
        "current_flow": "Naar verwarming, zoals de ketel meldt",
        "modulation_graph": "Brandervermogen (%)", "modulation_series": "Brandervermogen (%)",
        "dhw_graph": "Warmwatertemperaturen", "dhw_selected": "Ingesteld",
        "dhw_measured": "Gemeten", "dhw_target": "Doel",
        "states_graph": "Gemeld verwarmen / warm water / vlam / pomp", "state_heating": "Gemeld verwarmen",
        "state_dhw": "Gemeld warm water", "state_flame": "Gemelde vlambit", "state_pump": "Gemelde pompbit",
        "dhw_card": "Warmwatermogelijkheden en kwaliteit",
        "dhw_note": "Warm water, alleen bekijken: de laatste waarden die de ketel meldde (hun leeftijd wordt niet gecontroleerd); "
                    "er gaat niets naar de ketel.",
        "dhw_profile": "Profiel", "dhw_status": "status", "unknown": "Onbekend",
        "estimates_note": "Energie en volume zijn schattingen uit gemelde waarden, geen gas- of warmtemeter.",
        "energy_chart": "Geschatte energie per dag (geen meter)", "volume_chart": "Warmwatervolume per dag",
        "flame_chart": "Waargenomen vlamtijd per dag",
        "models_note": "Warmtemodellen per ruimte zijn schattingen, geen gemeten warmte; onbekende of verouderde "
                       "invoer laat gaten.",
        "room_history": "{room}: gewenst en gemeten", "room_measured": "Gemeten", "room_target": "Gewenst",
        "dhw_taps": "Tappen vandaag", "dhw_today": "Warm water vandaag",
        "advice": "Advies", "advice_where": "Waar", "advice_confidence": "Zekerheid",
        "advice_note": "Alleen advies: er wordt niets automatisch veranderd.",
        "learned_house": "Huis en ketel",
        "learned_changes": "Wat hij zelf heeft aangepast",
        "confidence_low": "laag", "confidence_medium": "middel", "confidence_high": "hoog",
        "gas_heating": "Verwarming", "gas_hot_water": "Warm water", "gas_keep_warm": "Waarvan warm water warmhouden",
        "gas_tapping": "Tappen", "gas_keeping_warm": "Warmhouden", "gas_hot_water_total": "Warm water (totaal)",
        "activity_timeline": "Wat de ketel doet (24 uur)", "activity": "Ketel",
        "dhw_use_note": "Tappen is warm water uit een kraan; warmhouden is de ketel die zijn voorraad of "
                        "warmtewisselaar opwarmt zonder dat er getapt wordt, meer niet. De E32 houdt ze uit elkaar met "
                        "het meest directe signaal dat je ketel geeft. De cijfers van vandaag volgen binnen vijf minuten "
                        "na het einde van een warmwaterperiode.",
        "dhw_use_note_tank": "Tappen is warm water uit het vat, geteld aan het warmwaterdebiet van de ketel, dus de "
                             "liters zijn bij benadering; vat opwarmen is de ketel die het vat weer opwarmt. De cijfers "
                             "van vandaag volgen binnen vijf minuten na het einde van een warmwaterperiode.",
        "gas_per_day": "Gas per dag", "gas_split_per_day": "Warm water: tappen en warmhouden",
        "gas_measured": "Gemeten met je gasmeter, verdeeld naar wat de ketel deed.",
        "gas_estimate": "Geschat uit het brandervermogen en het vermogen van de ketel (geen gasmeter).",
        "gas_note": "Voeg verwarmen en warm water toe aan het energiedashboard onder Gasverbruik; tappen en warmhouden "
                    "zijn delen van warm water, laat die daar weg. Een gasmeter die eens per uur meldt, kan het gas van het "
                    "laatste uur op de volgende dag zetten.",
        "gas_note_tank": "Voeg verwarmen en warm water toe aan het energiedashboard onder Gasverbruik. Met een "
                         "warmwatervat is al zijn gas warm water: een tap en de lading erna lopen vaak samen. Een gasmeter "
                         "die eens per uur meldt, kan het gas van het laatste uur op de volgende dag zetten.",
        "yesterday": "Gisteren", "burner_per_day": "Branderuren per dag",
        "missed_per_day": "Gemist comfort per dag (minuten)",
        "missed_series": "Gemist comfort",
        "day_burner": "Brander {h} uur, {starts}{short}.",
        "day_gas": "Gas: verwarmen {heating}, warm water {hot_water}.",
        "day_room": "{room}: vroeg {h} uur warmte; gemiddeld na {ttt} min op temperatuur; gemist comfort {missed} min.",
        "day_room_no_step": "{room}: vroeg {h} uur warmte; gemist comfort {missed} min.",
        "day_room_plain": "{room}: vroeg {h} uur warmte; gemiddeld na {ttt} min op temperatuur.",
        "day_room_no_step_plain": "{room}: vroeg {h} uur warmte.",
        "day_missed": "Gemist comfort: {missed} min, opgeteld over de ruimtes die meer dan 0,3 °C onder hun streeftemperatuur waren terwijl ze in gebruik waren.",
        "day_outdoor": "Buiten {low} tot {high} °C.", "day_outdoor_one": "Buiten {low} °C.",
        "day_partial": "Gedeeltelijke dag: de E32 was niet de hele dag te horen, dus de cijfers zijn onvolledig.",
        "scoreboard_on_time": "op tijd warm",
        "scoreboard_late": "{d} te laat warm",
        "scoreboard_early": "{d} te vroeg warm",
        "scoreboard_overshoot": "{c} °C te warm",
        "scoreboard_hours": "Verwarmingstijd: {h} u",
        "scoreboard_burner": "Branderstarts per stookuur: {n}",
        "scoreboard_short": "Korte brandtijden: {h} u",
        "scoreboard_gas": "Gas voor verwarming (schatting van de ketel): {kwh} kWh",
        "scoreboard_degree_days": "Graaddagen: {d}",
        "scoreboard_degree_day": "{v} kWh per graaddag",
        "scoreboard_note": "Elke dag kijkt de E32 of elke ruimte op tijd warm was zonder te warm te worden, hoe vaak de brander startte en hoeveel gas naar verwarmen ging. Hij leert daarvan; elk getal houdt zijn geschiedenis bij op zijn eigen sensor.",
        "day_none": "Morgen staat hier de eerste dag.",
        "outdoor": "Buiten",
        "flow_settings": "Weerafhankelijke regeling en leren",
        "flow_source": "Watertemperatuur bepaald door",
        "house_mode": "Huismodus", "boiler_now": "Ketel",
        "holiday_next": "Vakantie vanaf {from} tot {until}", "holiday_now": "Op vakantie tot {until}",
        "holiday_day": "Vakantie op {from}",
        "months": "jan,feb,mrt,apr,mei,jun,jul,aug,sep,okt,nov,dec",
        "compare_link": "E32 vergeleken met je thermostaat",
        "no_request": "Geen ketelvraag",
        "wanting_one": "1 ruimte vraagt warmte", "wanting_many": "{n} ruimtes vragen warmte",
        "wanting_none": "Geen ruimte vraagt warmte", "decimal": ",",
        "flow_short": "Water naar verwarming", "return_short": "Water terug",
        "e32": "E32", "thermostat": "Thermostaat",
        "comparison_view": "Vergelijking",


        "readiness": "Klaar om over te nemen?",
        "ready_ready": "Klaar: volg de stappen om over te stappen.",
        "ready_waiting": "Nog niet: de E32 verzamelt nog gegevens in de proefperiode.",
        "ready_not_ready": "Niet klaar: los eerst de rode punten op.",
        "ready_no_comparison": "Geen thermostaat op de ketelbus om mee te vergelijken, dus alleen de E32 en de "
            "ketel worden gecontroleerd.",
        "ready_stable": "Stabiel: {stable_hours} van {stable_hours_needed} uur zonder vastloper of onverwachte herstart",
        "ready_periods": "Verwarmingsperiodes vergeleken: {periods_compared} van {periods_needed}, met een "
            "nachtverlaging, een ochtendopwarming en een periode zonder vraag",
        "ready_timing": "Warmte op dezelfde momenten: {timing_events} van {timing_events_needed} starts en stops",
        "ready_flow_limit": "Gevraagde watertemperatuur nooit boven de grens: hoogste {flow_max_c} °C, grens {flow_limit_c} °C",
        "ready_cycling": "Niet meer verwarmingsperiodes dan de thermostaat: E32 {heating_periods_e32}, "
            "thermostaat {heating_periods_thermostat}",
        "ready_sources": "Ruimtebronnen werken, en een reservesensor heeft het overgenomen",
        "ready_boiler": "Ketel gehoord op de bus",
        "ready_boiler_limit": "Maximum van de ketel bekend: {boiler_limit_c} °C",
        "fix_timing": "De E32 stookt op andere momenten dan je thermostaat: controleer de doeltemperaturen en "
            "het weekprogramma.",
        "fix_flow_limit": "Een vraag kwam boven de harde grens: controleer de grenzen van de watertemperatuur.",
        "fix_cycling": "De E32 zou de brander vaker starten: controleer de grenzen van de watertemperatuur.",
        "fix_sources": "Controleer de ruimtesensoren (batterij, bereik) en geef een ruimte een tweede bron.",
        "fix_boiler": "De E32 hoort niets van de ketel: controleer de buskabel.",
        "fix_boiler_limit": "De ketel heeft zijn maximum niet gemeld: controleer de busverbinding.",
        "today_week": "Vandaag en deze week", "gas_heating_today": "Gas verwarmen",
        "gas_hot_water_today": "Gas warm water", "starts_today": "Branderstarts",
        "burner_today": "Brandertijd", "boiler_values": "Wat de ketel meldt",
        "who_controls": "Wie regelt de ketel", "yesterday_figures": "Gisteren",
        "dhw_target_short": "Doel warm water",
        "tapping_now": "Tapt nu", "no_tapping": "Geen tapwater",
        "knowledge": "Wat de E32 weet",
        "noticed": "Opgevallen",
        "curve_floor": "De laagste watertemperatuur beslist hier: de weerafhankelijke regeling zou {curve} °C vragen, maar je "
                       "ketel brandt pas rustig door vanaf water van ongeveer {floor} °C, dus de E32 vraagt {floor} °C.",
        "today": "Vandaag", "home_or_away": "Thuis of weg", "holiday": "Vakantie", "plan": "Plannen",
        "when_today": "Vandaag", "when_tomorrow": "Morgen", "when_date": "Op {date}",
        "warm_up_at": "{when} begint {room} om **{start}** met opwarmen, zodat het om **{time}** {target} °C is.",
        "warm_up_estimate": "{when} begint {room} om **{start}** (schatting) met opwarmen, zodat het om **{time}** {target} °C is.",
        "warm_up_ready": "{when} is {room} warm genoeg voor {target} °C om **{time}**; koelt de ruimte voor die tijd "
                         "af, dan begint het opwarmen eerder.",
        "warm_up_now": "{room} warmt nu op, zodat het om **{time}** {target} °C is.",
        "warm_up_from": "{when} begint {room} om **{start}** met opwarmen.",
        "warm_up_off": "{when} begint {room} om **{time}** met verwarmen naar {target} °C (Slim opwarmen staat uit).",
        "arrived_late": "{day} was het {m} minuten te laat warm.",
        "arrived_late_one": "{day} was het 1 minuut te laat warm.",
        "arrived_early": "{day} was het {m} minuten te vroeg warm.",
        "arrived_early_one": "{day} was het 1 minuut te vroeg warm.", "arrived_on_time": "{day} was het op tijd warm.",
        "weather_outside": "Buiten {outdoor} °C", "weather_asks": "de E32 vraagt {flow} °C water",
        "weather_off": "de weerafhankelijke regeling staat uit; die zou {flow} °C water vragen",
        "line_learned": "op de lijn die hij voor jouw huis leerde",
        # rc7: the sentences review (R1, R3): Today in every case, Yesterday in figures, the Learning view.
        "cycling_info_shadow": "Je huidige thermostaat laat de brander vaak aan en uit gaan; de E32 verlengt de rusttijd zodra hij de ketel regelt.",
        "day_starts": "{n} starts",
        "day_starts_one": "1 start",
        "day_short": " ({short} korter dan 10 minuten)",
        "day_burner_none": "De brander startte niet.",
        "scoreboard_not_warm": "niet warm binnen 3 uur",
        "scoreboard_short_none": "Korte brandtijden: geen",
        "figures_day": "Deze cijfers zijn van {date}: de E32 heeft geen nieuwere volledige dag.",
        "holiday_hint": "Vakantie plannen: Configureren → Huis → Huismodus en vakantie.",
        "dur_h_m": "{h} u {m} min",
        "dur_h": "{h} u",
        "warm_up_now_estimate": "{room} warmt nu op (schatting), zodat het om **{time}** {target} °C is.",
        "warm_up_late": "{room} warmt nu op; {target} °C wordt misschien pas iets na **{time}** gehaald.",
        "warm_up_trial": "{when} zou {room} om **{start}** met opwarmen beginnen, zodat het om **{time}** {target} °C is (proefperiode).",
        "warm_up_trial_now": "{room} zou nu opwarmen, zodat het om **{time}** {target} °C is (proefperiode).",
        "at_tomorrow": "{time} morgen",
        "at_date": "{time} op {date}",
        "today_away": "{room} staat op afwezig: niet eerder opwarmen.",
        "today_nobody": "Niemand is thuis voor {room}: niet eerder opwarmen.",
        "today_holiday": "{room} is met vakantie tot {date}; bij thuiskomst is het weer warm.",
        "today_return": "{room} warmt op voor je thuiskomst.",
        "today_window": "{room} is gepauzeerd: er staat een raam of deur open.",
        "today_summer": "{room}: zomerstand, de verwarming blijft uit.",
        "today_window_window": "{room} is gepauzeerd: er staat een raam open.",
        "today_window_door": "{room} is gepauzeerd: er staat een deur open.",
        "day_yesterday": "Gisteren",
        "day_today": "Vandaag",
        "day_on": "Op {date}",
        "arrived_late_long": "{day} was het {d} te laat warm.",
        "arrived_early_long": "{day} was het {d} te vroeg warm.",
        "arrived_not_warm": "{day} werd het binnen 3 uur niet warm.",
        "weather_idle": "als een ruimte warmte vraagt, vraagt de E32 {flow} °C water",
    },
}


def dashboard_language(hass):
    """English or Dutch by the Home Assistant language (English otherwise)."""
    language = (hass.config.language or "en").lower().replace("_", "-").split("-")[0]
    return language if language in TEXT else "en"


def view_cards(view):
    """Every card of a view, also inside its sections."""
    cards = list(view.get("cards", []))
    for section in view.get("sections", []):
        cards.extend(section.get("cards", []))
    return cards


def _with_banner(select, views):
    """1.4.1 (CONTRACT-1.4.1 §9): the house banner on top of every view, shown only while the house mode ``select`` is
    summer (Home Assistant's visibility condition; the element itself also draws nothing otherwise). A sections view
    gets it as its header card (no section shifts, nothing between the sections), a panel view as the first card of a
    vertical stack with its own card (a panel shows one card). Without the select (no E32, older firmware): unchanged."""
    if not select:
        return views
    from .room_overview import HOUSE_BANNER_TYPE
    def banner():
        return {"type": HOUSE_BANNER_TYPE, "entity": select,
                "visibility": [{"condition": "state", "entity": select, "state": "summer"}]}
    out = []
    for view in views:
        if view.get("type") == "sections":
            view = {**view, "header": {"layout": "start", "card": banner()}}
        elif view.get("panel") and view.get("cards"):
            view = {**view, "cards": [{"type": "vertical-stack", "cards": [banner(), *view["cards"]]}]}
        out.append(view)
    return out


def _section(*cards):
    return {"type": "grid", "cards": [card for card in cards if card]}


def _section_known(entities, *cards, hidden=None):
    """A section that hides as a whole while none of ``entities`` has a value (dashboard-spec §1).

    ``entities`` are the ones its cards show with: every card in it is visible whenever one of them has a value,
    so its heading never stands over nothing. ``hidden``: {entity id: more states that count as no value}.
    """
    section = _section(*cards)
    entities = [entity for entity in dict.fromkeys(entities) if entity]
    if entities:
        section["visibility"] = _any_known(entities, hidden)
    return section


def _filled(section):
    """The section, or None when it would be its heading alone."""
    return section if section is not None and len(section["cards"]) > 1 else None


# Ready to take over? (takeover_readiness.py): the result attribute of each criterion, in order.
READINESS_ITEMS = ("stable", "periods", "timing", "flow_limit", "cycling", "sources", "boiler", "boiler_limit")


def _readiness_card(t, entity_id):
    """The verdict and one line per criterion the E32 reports (✅ pass, ⏳ wait, ❌ fail with what to do)."""
    quoted = json.dumps(entity_id)

    def attribute(match):
        return "{{ state_attr(" + quoted + ", '" + match.group(1) + "') }}"
    content = ("{% set s = states(" + quoted + ") %}{% set mark = {'pass': '✅', 'wait': '⏳', 'fail': '❌'} %}"
               "**{% if s == 'ready' %}" + t["ready_ready"] + "{% elif s == 'not_ready' %}" + t["ready_not_ready"]
               + "{% else %}" + t["ready_waiting"] + "{% endif %}**\n\n"
               "{% if state_attr(" + quoted + ", 'comparison') == false %}" + t["ready_no_comparison"] + "\n\n{% endif %}")
    for item in READINESS_ITEMS:
        text = t["ready_" + item]
        line = re.sub(r"\{(\w+)\}", attribute, text)
        names = re.findall(r"\{(\w+)\}", text)
        if names:
            # A figure the E32 does not know yet (null) shows the criterion alone, never "None °C".
            known = " and ".join("state_attr(" + quoted + ", '" + name + "') is not none" for name in names)
            line = "{% if " + known + " %}" + line + "{% else %}" + text.split(":")[0] + "{% endif %}"
        fix = t.get("fix_" + item)
        content += ("{% set r = state_attr(" + quoted + ", '" + item + "') %}{% if r in mark %}- {{ mark[r] }} " + line
                    + ("{% if r == 'fail' %}. " + fix + "{% endif %}" if fix else "") + "\n{% endif %}")
    return {"type": "markdown", "content": content, "visibility": _known(entity_id, ("not_applicable",))}


def _heading(text, icon=None, badges=None, style="title", visibility=None):
    card = {"type": "heading", "heading": text, "heading_style": style}
    if icon:
        card["icon"] = icon
    if badges:
        card["badges"] = badges
    if visibility:
        card["visibility"] = visibility
    return card


def _link(text, icon, path, visibility=None):
    """A one-line link row (a heading with a chevron) to another page."""
    card = _heading(text, icon, style="subtitle", visibility=visibility)
    card["tap_action"] = {"action": "navigate", "navigation_path": path}
    return card


def _known(entity_id, also=()):
    """Card visibility: only while the entity has a value (and none of the states ``also``)."""
    return [{"condition": "state", "entity": entity_id, "state_not": ["unavailable", "unknown", *also]}]


# Rows hidden in this state too: the maintenance message while there is none.
HIDDEN_STATES = {"maintenance_message": ("none",)}


def _rows(entity_ids):
    """Entities-card rows named by the entity alone: the card title already says whose they are,
    and the device name in front of every row cut the names short."""
    return [{"entity": entity_id, "name": {"type": "entity"}} for entity_id in entity_ids]


def _known_rows(entity_ids, hidden=None):
    """Rows shown only while their entity has a value (no "Unknown" rows for what a boiler never sends);
    ``hidden``: {entity id: more states that hide the row}."""
    hidden = hidden or {}
    return [{"type": "conditional", "conditions": _known(row["entity"], hidden.get(row["entity"], ())), "row": row}
            for row in _rows(entity_ids)]


def _any_known(entity_ids, hidden=None):
    """Card visibility: while at least one of the entities has a value; ``hidden``: {entity id: more states that
    count as none}, as for its row (_known_rows)."""
    hidden = hidden or {}
    return [{"condition": "or", "conditions": [condition for entity_id in entity_ids
                                               for condition in _known(entity_id, hidden.get(entity_id, ()))]}]


def _none_known(entity_ids):
    """Card visibility: while none of the entities has a value."""
    return [{"condition": "state", "entity": entity_id, "state": ["unavailable", "unknown"]} for entity_id in entity_ids]


def _known_entities_card(entity_ids, hidden=None, title=None):
    """An entities card of rows with a value, hidden while no row shows; no title where its section heading names
    it, ``title`` where one section holds several such cards."""
    card = {"type": "entities", "entities": _known_rows(entity_ids, hidden), "visibility": _any_known(entity_ids, hidden)}
    if title:
        card["title"] = title
    return card


ADVICE_ICONS = {"warning": "mdi:alert-outline", "suggestion": "mdi:lightbulb-on-outline",
                "info": "mdi:information-outline"}


def _advice_section(t, advice):
    """The current heating advice (title, action, where); hidden while there is none."""
    if not advice:
        return None
    quoted = json.dumps(advice)
    confidence = json.dumps({key: t["confidence_" + key] for key in ("low", "medium", "high")})
    icons = json.dumps(ADVICE_ICONS)
    content = ("{% set icons = " + icons + " %}{% set confidence = " + confidence + " %}"
               "{% for item in state_attr(" + quoted + ", 'items') or [] %}"
               "<ha-icon icon=\"{{ icons.get(item.severity, 'mdi:information-outline') }}\"></ha-icon> "
               "**{{ item.title }}**\n\n{{ item.action }}\n\n"
               "*" + t["advice_where"] + ": {{ item.where }} · " + t["advice_confidence"]
               + ": {{ confidence.get(item.confidence, item.confidence) }}*\n\n"
               "{% endfor %}" + t["advice_note"])
    shown = [{"condition": "numeric_state", "entity": advice, "above": 0}]
    section = _section(_heading(t["advice"], "mdi:lightbulb-on-outline", style="title", visibility=shown),
                       {"type": "markdown", "content": content, "visibility": shown})
    section["visibility"] = shown
    return section


LEARNED_PATH = "learned"


def _changes_section(t, learned, link=None, settings=False):
    """What it changed by itself (1.4.3, design 4.2 item 5): the self-tuning's changes, newest first, each with its date
    ("9 Nov: The burner now rests ..."; a trial-run proposal without one), or the learned overview's "Nothing changed
    yet" line, and a link to where the settings are changed (``link``: Settings → Heating and boiler → Comfort and boiler
    care on the E32 room plan, ``settings``; else Configure). Hidden while the learned overview is unavailable."""
    if not learned:
        return None
    quoted = json.dumps(learned)
    # "5 Nov: ...", as every other date on the dashboard (not "05-11", which reads as 11 May in English).
    changes = ("{% for change in state_attr(" + quoted + ", 'changes') or [] %}- {% if change.time %}"
               "{% set c = as_local(as_datetime(change.time)) %}**{{ " + _date(t, "c") + " }}** · {% endif %}"
               "{{ change.text }}\n{% endfor %}")
    shown = [{"condition": "state", "entity": learned, "state_not": "unavailable"}]
    section = _section(_heading(t["learned_changes"], "mdi:history", style="title"),
                       {"type": "markdown", "content": changes},
                       # The screen's own name (the panel's words): a whole path was cut short on a phone.
                       _link(t["care_link"], "mdi:tune-variant", link) if link else None)
    section["visibility"] = shown
    return section


def _learning_rooms_section(t, entry_id, learned, names, rooms):
    """Per room (1.4.3, design 4.2 item 2, CONTRACT-1.4.3 §3): one learning card per room (custom:openthermostat-
    learning-room, frontend/learning-room-card.js), side by side, one view column each (``columns: 12``), the rooms
    that are on first. ``rooms``: [(room id, its entities)]. Hidden as a whole while the learned overview has no value
    (the cards then say nothing), so no heading stands over empty cards after an update or while the E32 is off.
    1.4.4: ``relearn``, the room's Learn again button (e32_learned.py, only on firmware with it): the card's text button
    "Learn again" asks first and presses it."""
    if not learned or not rooms:
        return None
    from .e32_flow import LEARNING_ROOM_CARD_TYPE
    cards = [{"type": LEARNING_ROOM_CARD_TYPE, "entry_id": entry_id, "room_id": room_id, "name": names.get(room_id, room_id),
              "learned": learned, **{key: room[key] for key in ("learning", "warm_on_time", "heating_start", "reason", "state",
                                                                "relearn") if room.get(key)},
              "grid_options": {"columns": 12}} for room_id, room in rooms]
    section = _section(_heading(t["per_room"], ICONS["learning"]), *cards)
    section["visibility"] = _known(learned)
    return _span(section, 4, cards=None)  # the room cards keep one view column each


def _noticed_card(t, learned):
    """What stood out yesterday (the learned overview's ``insights``, insight.py), folded into Yesterday (1.4.3, design
    4.2 item 4) as one highlighted line each with what can cause it muted under it; hidden while nothing stood out."""
    quoted = json.dumps(learned)
    return {"type": "markdown", "visibility": _listed(learned, "insights"), "content": (
        "{% for line in state_attr(" + quoted + ", 'insights') or [] %}<ha-alert alert-type=\"info\" title=\""
        + t["noticed"] + "\">{{ line.text }}{% if line.meaning %}<br><small>{{ line.meaning }}</small>{% endif %}"
        "</ha-alert>\n{% endfor %}")}


def _icon(concept):
    """The icon of a concept (ICONS) in its colour, at the start of a markdown line, as the sketch draws it. A markdown
    card cannot read the theme's CSS variables (its sanitiser keeps <font color> only), so the colours are those of
    Home Assistant's default theme (ICON_COLOURS)."""
    return '<font color="' + ICON_COLOURS[concept] + '"><ha-icon icon="' + ICONS[concept] + '"></ha-icon></font>'


def _listed(entity_id, attribute):
    """Visibility: while the entity's list ``attribute`` has an item (Home Assistant 2026.10 reads an attribute in a
    state condition as text: an empty list is "", a missing attribute or entity "unknown")."""
    return [{"condition": "state", "entity": entity_id, "attribute": attribute,
             "state_not": ["unavailable", "unknown", ""]}]


def _plan_section(t, plan, confirm=None):
    """Today's plan (heating_plan.py, 1.1.1 stage B): how far the E32's planner is in one plain line, why it plans
    what it plans, the next blocks and when the room is expected warm, then the morning check ("This morning: 6
    minutes early.", E32 1.3), from the sensor "Heating plan" (its texts are in Home Assistant's language). Hidden
    while the E32 reports no plan (firmware without the planner).

    confirm: the button "Let the E32 plan the heating" (heating_plan.PlanConfirmButton), which exists only while the
    E32 is ready for that one confirmation; then it stands under the plan, asking first (1.4.2: the invitation is no
    Repairs item any more). The registry change rebuilds the dashboard, so it comes and goes with the button."""
    if not plan:
        return None
    quoted = json.dumps(plan)

    def attr(name):
        return "state_attr(" + quoted + ", '" + name + "')"
    content = ("{% set s = " + attr("plan_state_text") + " %}{% if s %}{{ s }}{% endif %}"
               "{% set r = " + attr("reason") + " %}{% if r %}\n\n" + _icon("why") + " **" + t["plan_why"]
               + ":** {{ r }}{% endif %}"
               "{% set b = " + attr("block_lines") + " or [] %}{% if b %}\n\n{% for line in b %}- {{ line }}\n"
               "{% endfor %}{% endif %}"
               "{% set a = " + attr("arrival_text") + " %}{% set c = " + attr("confidence_text") + " %}"
               "{% if a or c %}\n\n{% if a %}{{ a }}{% endif %}{% if a and c %} {% endif %}{% if c %}*{{ c }}*{% endif %}"
               "{% endif %}"
               "{% set m = " + attr("morning_text") + " %}{% if m %}\n\n{{ m }}{% endif %}")
    shown = [{"condition": "state", "entity": plan, "state_not": "unavailable"}]
    button = _wide(_tile(confirm, t["plan_confirm"], "mdi:calendar-check", tap_action={
        "action": "perform-action", "perform_action": "button.press", "target": {"entity_id": confirm},
        "confirmation": {"text": t["plan_confirm_ask"]}},
        visibility=[{"condition": "state", "entity": confirm, "state_not": "unavailable"}])) if confirm else None
    section = _section(_heading(t["plan_today"], ICONS["plan"], visibility=shown),
                       {"type": "markdown", "content": content, "visibility": shown}, button)
    section["visibility"] = shown
    return section


def _worth_checking_section(t, problem):
    """Worth checking (1.4.2, HC-05): what the E32 noticed that is advice, not a fault, so no Repairs item: a room
    that stays too cold while it asks for heat, a burner that keeps switching on and off after the self-tuning had
    its chance. One line each from the Heating problem sensor's ``advice``; hidden while there is none."""
    if not problem:
        return None
    quoted = json.dumps(problem)
    section = _section(_heading(t["worth_checking"], "mdi:lightbulb-on-outline"), {"type": "markdown", "content": (
        "{% for line in state_attr(" + quoted + ", 'advice') or [] %}" + _icon("insight") + " {{ line }}\n\n"
        "{% endfor %}")})
    section["visibility"] = _listed(problem, "advice")
    return section


def _knowledge_section(t, knowledge):
    """What the E32 knows (insight.py, E32 rc.5), first on the Learning view and across it (1.4.3): the knowledge card,
    a ring beside "The E32 knows your house: 88 %" and the learning path (frontend/heating-curve-card.js). It follows
    its sensor without a rebuild and hides until the E32 reports it (firmware before rc.5 leaves it unknown)."""
    if not knowledge:
        return None
    section = _section_known([knowledge], _heading(t["knowledge"], ICONS["knowledge"]),
                             {"type": KNOWLEDGE_CARD_TYPE, "entity": knowledge, "visibility": _known(knowledge)})
    return _span(section, 4)


def _curve_section(t, curve, request=None, learned=None, boiler=None, smart=None):
    """House and boiler (1.4.3, design 4.2 item 3): water temperature by outdoor temperature (the heating-curve card,
    its title left out under this heading; with the heat request, HA 1.0.1, it says "E32 would ask" in the trial run),
    the note "the lowest water temperature decides here" while the learned steady-burn floor is applied above what
    weather compensation asks (E32 1.3, the learned overview's ``steady_burn``), and what the E32 learned from the
    boiler as tiles (custom:openthermostat-boiler-learned: the Boiler response sensor, the learned overview's floors,
    the curve's outdoor temperature for its band, ``smart`` the Smart warm-up switch). Shown while the curve or the
    boiler's response has a value; each card follows its sensors without a rebuild."""
    if not curve and not boiler:
        return None
    card = None
    if curve:
        card = {"type": CURVE_CARD_TYPE, "entity": curve, "show_name": False, "visibility": _known(curve)}
        if request:
            card["request"] = request
    note = None
    if curve and learned:
        q, lo = json.dumps(curve), json.dumps(learned)
        note = {"type": "markdown", "show_empty": False, "content": (
            "{% set f = state_attr(" + q + ", 'flow_c') %}{% set fl = state_attr(" + lo + ", 'steady_burn_floor_c') %}"
            "{% set sb = state_attr(" + lo + ", 'steady_burn') %}"
            "{% if f is number and fl is number and sb is mapping and sb.applied == true"
            " and (f | round(0) | int) < (fl | round(0) | int) %}" + _icon("lowest") + " {{ "
            + _jinja_text(t["curve_floor"], curve="f | round(0) | int", floor="fl | round(0) | int") + " }}{% endif %}")}
    tiles = None
    if boiler:
        from .e32_flow import BOILER_LEARNED_CARD_TYPE
        tiles = {"type": BOILER_LEARNED_CARD_TYPE, "boiler": boiler, "visibility": _known(boiler),
                 **{key: value for key, value in (("learned", learned), ("curve", curve), ("smart", smart)) if value}}
    return _section_known([curve, boiler], _heading(t["learned_house"], "mdi:home-thermometer-outline"),
                          _full(card), _full(note), _full(tiles))


def _settings_section(t, flow, link=None, settings=False):
    """The quiet settings row at the bottom of the Learning view (1.4.3, design 4.2 item 7): one line with what is set
    ("Smart warm-up on · Weather compensation on · Comfort style Balanced"), under a link to where it is changed
    (``link``: Settings → Heating and boiler on the E32 room plan, ``settings``; else Configure). The switches
    themselves are under Settings; a value Home Assistant does not know is left out of the line. None without them."""
    keys = [key for key in ("apply_learned", "weather_curve", "comfort_style") if flow.get(key)]
    if not keys:
        return None
    parts = []
    for key, on, off in (("apply_learned", "row_smart_on", "row_smart_off"), ("weather_curve", "row_curve_on", "row_curve_off")):
        if flow.get(key):
            q = json.dumps(flow[key])
            parts.append("{% if is_state(" + q + ", 'on') %}{% set row = row + [" + json.dumps(t[on], ensure_ascii=False)
                         + "] %}{% elif is_state(" + q + ", 'off') %}{% set row = row + [" + json.dumps(t[off], ensure_ascii=False)
                         + "] %}{% endif %}")
    if flow.get("comfort_style"):
        q = json.dumps(flow["comfort_style"])
        parts.append("{% if has_value(" + q + ") %}{% set row = row + [" + _jinja_text(
            t["row_style"], style="state_translated(" + q + ")") + "] %}{% endif %}")
    content = "{% set row = [] %}" + "".join(parts) + "{{ row | join(' · ') }}"
    section = _section(
        _link(t["settings_heating" if settings else "configure_heating"], ICONS["settings"], link) if link
        else _heading(t["settings_heating" if settings else "configure_heating"], ICONS["settings"], style="subtitle"),
        {"type": "markdown", "content": content})
    # Hidden while none of them has a value (the E32 off after an update): never a link over an empty line.
    section["visibility"] = _any_known([flow[key] for key in keys])
    return _span(section, 4)


def _at_macro(t):
    """A Jinja macro ``at(moment)``: a moment (ISO text or datetime) as the local time of day, 14:32 or 09:05 (two
    digits, as everywhere in Home Assistant), with the date in front when it is not today ("4 Nov 14:32")."""
    months = json.dumps(t["months"].split(","), ensure_ascii=False)
    return ("{% macro at(v) %}{% set m = as_datetime(v, none) if v is string else v %}{% if m is not none %}"
            "{% set m = as_local(m) %}{% if m.date() != now().date() %}{{ m.day }} {{ " + months
            + "[m.month - 1] }} {% endif %}{{ '%02d' % m.hour }}:{{ '%02d' % m.minute }}{% endif %}{% endmacro %}")


REFUSALS = ("too_large", "invalid_json", "no_entity", "unknown_kind", "invalid_value", "unknown_room")
# 1.4.4 (DEVICE-ROBUST-144): why the E32 could not read a device message (last_restart.DROP_REASONS).
UNREAD_REASONS = ("too_large", "too_deep", "malformed", "unknown_device", "wrong_type")


def _unread_line(t, errors):
    """1.4.4 (DEVICE-ROBUST-144): "Messages the E32 could not read since it started: 3, last: zigbee2mqtt/…, too large (7.1 KB)." from
    the "E32 errors" sensor's attributes (last_restart.dropped_attributes): a figure since the E32 started, shown only
    while it is above 0 and the sensor is available (never a Repairs item). The size is bytes / 1000 with one decimal,
    as the room card and the E32 pages say a valve message's size; under 1000 bytes in B."""
    if not errors:
        return ""
    e = json.dumps(errors)
    reasons = json.dumps({key: t["unread_" + key] for key in UNREAD_REASONS}, ensure_ascii=False)
    size = ("(' (' ~ (u.b ~ ' B' if u.b < 1000 else ('%.1f' % (u.b / 1000)) | replace('.', "
            + json.dumps(t["decimal"]) + ") ~ ' KB') ~ ')'"
            " if u.b is number and u.b > 0 else '')")
    return ("{% set u = namespace(n=state_attr(" + e + ", 'unread_messages'), topic=state_attr(" + e
            + ", 'unread_last_topic'), why=state_attr(" + e + ", 'unread_last_reason'), b=state_attr(" + e
            + ", 'unread_last_bytes')) %}{% set reasons = " + reasons + " %}"
            "{% if states(" + e + ") not in ['unavailable', 'unknown'] and u.n is number and u.n > 0 and u.topic"
            " and u.why in reasons %}" + _icon("link_wait") + " {{ "
            + _jinja_text(t["link_unread"], n="u.n", topic="u.topic", reason="reasons[u.why] ~ " + size)
            + " }}\n\n{% endif %}")


def _connection_section(t, request, update=None, errors=None):
    """Connection with the E32 (rc.7), first on Diagnostics: one plain line per question, the details behind "More".

    - Is the E32 heard? The heat request sensor (heating_link.HeatRequestSensor) is unavailable while the E32 is silent
      (three heartbeats) and is written with every E32 message, so its ``last_reported`` is when it was last heard and,
      while silent, its ``last_changed`` when it went quiet; with what to check.
    - Do the room values reach the E32? Its ``ha_input`` (HeatingInputWatch.attributes): yes with the time the E32 last
      took one, none for 15 minutes, or no since then (the repair heating_input_lost) with the value it refused last
      and why, and the repair's advice.
    - The MQTT broker: the E32 is heard through it; Home Assistant's newest send failed or not (``last_error_at`` after
      ``last_sent``), the kind of failure in words (``last_error_kind``).
    - The firmware: the update entity (firmware_update.py): its version, and an update available, skipped or installing.
    - 1.4.4 (DEVICE-ROBUST-144): device messages the E32 could not read since it started, with the last one
      (``errors``: the "E32 errors" sensor, _unread_line), only while there are any.

    More: when Home Assistant last sent a value, its last send error, the values dropped and a refusal while values
    arrive. None without the heat request sensor (no E32); always shown otherwise (its first line has an answer).
    """
    if not request:
        return None
    q = json.dumps(request)
    why = json.dumps({key: t["why_" + key] for key in REFUSALS}, ensure_ascii=False)
    sends = json.dumps({key: t["send_" + key] for key in ("timeout", "unreachable", "waiting")}, ensure_ascii=False)

    def line(concept, text):
        return _icon(concept) + " " + text + "\n\n"

    def say(key, **values):
        return "{{ " + _jinja_text(t[key], **values) + " }}"
    refused = "why.get(r.reason, r.reason)"
    heard = (
        "{% set st = states." + request + " %}{% set heard = states(" + q + ") not in ['unavailable', 'unknown'] %}"
        "{% if heard %}" + line("link_ok", say("link_heard_yes", at="at(st.last_reported)"))
        + "{% elif st %}" + line("link_problem", say("link_heard_no", at="at(st.last_changed)") + " " + t["link_heard_fix"])
        + "{% else %}" + line("link_problem", t["link_heard_never"] + " " + t["link_heard_fix"]) + "{% endif %}")
    values = (
        "{% set h = state_attr(" + q + ", 'ha_input') if heard else none %}{% if h is mapping %}"
        "{% set r = h.e32_last_rejected if h.e32_last_rejected is mapping and h.e32_last_rejected.at else none %}"
        "{% if h.state == 'ok' and h.e32_last_input %}" + line("link_ok", say("link_input_yes", at="at(h.e32_last_input)"))
        + "{% elif h.state == 'waiting' and h.e32_last_input %}"
        + line("link_wait", say("link_input_quiet", at="at(h.e32_last_input)"))
        + "{% elif h.state == 'not_received' %}" + _icon("link_problem") + " "
        + "{% if h.e32_last_input %}" + say("link_input_no", at="at(h.e32_last_input)") + "{% else %}"
        + t["link_input_no_plain"] + "{% endif %}"
        + "{% if r %} " + say("link_refused", at="at(r.at)", why=refused) + "{% endif %} " + t["link_input_fix"] + "\n\n"
        + "{% else %}" + line("link_unknown", t["link_input_unknown"]) + "{% endif %}"
        # Home Assistant's newest send failed: one that worked in the same minute or later counts as working.
        + "{% if h.last_error_at and (not h.last_sent or h.last_error_at > h.last_sent) %}"
        # The kind of failure in words (the raw error text, in English, is behind "More").
        + line("link_problem", say("link_broker_failed", at="at(h.last_error_at)",
                                   error="sends.get(h.last_error_kind) or h.last_error"))
        + "{% else %}" + line("link_ok", t["link_broker_ok"]) + "{% endif %}{% endif %}")
    firmware = ""
    if update:
        u = json.dumps(update)
        firmware = (
            "{% set v = state_attr(" + u + ", 'installed_version') %}{% if v %}"
            "{% set l = state_attr(" + u + ", 'latest_version') %}"
            "{% if state_attr(" + u + ", 'in_progress') not in [none, false] and l %}"
            + line("link_update", say("link_firmware_installing", latest="l"))
            + "{% elif is_state(" + u + ", 'on') and l %}" + line("link_update", say("link_firmware_new", version="v", latest="l"))
            # Skipped only when Home Assistant recorded the skip: a development build is no older release.
            + "{% elif l and l == state_attr(" + u + ", 'skipped_version') %}"
            + line("link_ok", say("link_firmware_skipped", version="v", latest="l"))
            + "{% else %}" + line("link_ok", say("link_firmware", version="v")) + "{% endif %}{% endif %}")
    more = (
        "{% if h is mapping %}{% set d = namespace(lines=[]) %}"
        "{% if h.last_sent %}{% set d.lines = d.lines + [" + _jinja_text(t["link_sent"], at="at(h.last_sent)") + "] %}"
        "{% endif %}{% if h.last_error and h.last_error_at %}{% set d.lines = d.lines + ["
        + _jinja_text(t["link_error"], at="at(h.last_error_at)", error="h.last_error") + "] %}{% endif %}"
        "{% if h.dropped is number and h.dropped > 0 %}{% set d.lines = d.lines + ["
        + _jinja_text(t["link_dropped"], n="h.dropped") + "] %}{% endif %}"
        "{% if r and h.state != 'not_received' %}{% set d.lines = d.lines + ["
        + _jinja_text(t["link_refused_earlier"], at="at(r.at)", why=refused) + "] %}{% endif %}"
        "{% if d.lines %}<details><summary>" + t["more"] + "</summary>\n\n{% for x in d.lines %}- {{ x }}\n"
        "{% endfor %}\n</details>{% endif %}{% endif %}")
    content = (_at_macro(t) + "{% set why = " + why + " %}{% set sends = " + sends + " %}" + heard + values + firmware
               + _unread_line(t, errors) + more)
    return _section(_heading(t["connection"], ICONS["connection"]), {"type": "markdown", "content": content})


def _per_day(title, entities, entity_id):
    """A bar per day for the last 7 days (the day's change of a running total), shown while ``entity_id`` has a value."""
    return {"type": "statistics-graph", "title": title, "chart_type": "bar", "period": "day", "days_to_show": 7,
            "stat_types": ["change"], "entities": entities, "visibility": _known(entity_id)}


def _energy_section(t, hub, tank=False):
    """Today and this week (dashboard-spec §5.3): today's gas for heating and for hot water and today's burner
    starts and time as figures, then the chart of the gas per day (always heating and hot water in total, 1.4.2), on
    a boiler without a tank a second small chart of hot water's tapping and keeping warm once the E32 tells them
    apart, the burner hours per day and one note on how the gas is counted.

    Before 1.4.2 the one chart drew heating, tapping and keeping warm: the hot water neither of them holds (a tank's
    charges, unsorted episodes) was missing from it (review R142 F3). Tapping and keeping warm are parts of hot
    water, so they never stand beside it in one bar.

    hub: {key: entity id} of the hub sensors; tank: the hot water is a storage tank (heating_link.dhw_tank): no split
    chart, the note says why. Every card shows only with a value, the section hides as a whole without one, and
    there is none without the gas and the daily-summary sensors.
    """
    heating, hot_water = hub.get("heating_gas"), hub.get("hot_water_gas")
    starts, burner = hub.get("daily_burner_starts"), hub.get("daily_burner_time")
    gas = heating or hot_water
    posts = [(entity_id, t[name]) for entity_id, name in ((heating, "gas_heating"), (hot_water, "gas_hot_water_total"))
             if entity_id]
    parts = [(hub.get(key), t[name]) for key, name in (("tapping_gas", "gas_tapping"), ("keep_warm_gas", "gas_keeping_warm"))]
    split = parts if not tank and all(entity_id for entity_id, _ in parts) else None
    note = None
    if gas:
        quoted = json.dumps(gas)
        note = {"type": "markdown", "visibility": _known(gas), "content": (
            "{% if state_attr(" + quoted + ", 'estimate') %}" + t["gas_estimate"] + "{% else %}" + t["gas_measured"]
            + "{% endif %}" + _details(t, t["gas_note_tank" if tank else "gas_note"]))}
    return _filled(_section_known(
        [gas, starts, burner],
        _heading(t["today_week"], ICONS["week"]),
        *_pair(_statistic(heating, t["gas_heating_today"], ICONS["gas"]),
               _statistic(hot_water, t["gas_hot_water_today"], ICONS["gas"]), rows=2),
        *_pair(_statistic(starts, t["starts_today"], ICONS["burner_starts"]),
               _statistic(burner, t["burner_today"], ICONS["burner_time"]), rows=2),
        # The gas chart of the dashboard; the Overview has today's figure, Learning yesterday's line.
        _per_day(t["gas_per_day"], [{"entity": entity_id, "name": name} for entity_id, name in posts], gas)
        if gas else None,
        _per_day(t["gas_split_per_day"], [{"entity": entity_id, "name": name} for entity_id, name in split],
                 split[0][0]) if split else None,
        # The legend names the series as short as its figure above it: the entity's own name ("OpenThermostat E32
        # Burner time (total)") was cut on a phone (demo, HA 1.0.1).
        _per_day(t["burner_per_day"], [{"entity": burner, "name": t["burner_today"]}], burner) if burner else None,
        note))


def _summary_lines(t, summary, gas_unit, scoreboard_gas=None):
    """Yesterday's daily summary (daily_summary.py) as list lines of "Yesterday in figures": the burner, the gas
    (unless ``scoreboard_gas`` has a value: then the scoreboard's line says it, once) and the outdoor range, then
    per room its heat demand, how fast it got warm and its missed comfort; a partial day says so. Before the first
    full day: "tomorrow", unless the scoreboard has a line already (``shown.lines``, _yesterday_figures).
    """
    q = json.dumps(summary)

    def fill(text, **names):
        for name, expr in names.items():
            text = text.replace("{" + name + "}", "{{ " + expr + " }}")
        return text

    def number(expr):
        """The summary's number as it is, in the language's decimal sign ("7,4 uur", as elsewhere on the dashboard)."""
        if t["decimal"] == ".":
            return expr
        return "(((" + expr + ") ~ '') | replace('.', " + json.dumps(t["decimal"]) + "))"
    unit = " " + gas_unit if gas_unit else ""
    gas = "d.gas and d.gas.heating is not none and d.gas.hot_water is not none"
    if scoreboard_gas:
        gas += " and not is_number(states(" + json.dumps(scoreboard_gas) + "))"
    starts = ("(" + json.dumps(t["day_starts_one"], ensure_ascii=False) + " if d.burner_starts == 1 else "
              + _jinja_text(t["day_starts"], n="d.burner_starts") + ")")
    short = "(" + _jinja_text(t["day_short"], short="d.short_runs") + " if d.short_runs else '')"
    return (
        "{% set d = state_attr(" + q + ", 'last_day') %}{% if d %}- "
        + "{% if not d.burner_starts and not d.burner_hours %}" + t["day_burner_none"] + "{% else %}"
        + fill(t["day_burner"], h=number("d.burner_hours"), starts=starts, short=short) + "{% endif %}"
        + "{% if " + gas + " %} "
        + fill(t["day_gas"], heating=number("d.gas.heating") + " ~ '" + unit + "'",
               hot_water=number("d.gas.hot_water") + " ~ '" + unit + "'")
        + "{% endif %}{% if d.outdoor %} "
        # One outdoor temperature all day (a sensor that did not change): not "Outdoor 5 to 5 °C".
        + "{% if d.outdoor.min == d.outdoor.max %}" + fill(t["day_outdoor_one"], low=number("d.outdoor.min"))
        + "{% else %}" + fill(t["day_outdoor"], low=number("d.outdoor.min"), high=number("d.outdoor.max"))
        + "{% endif %}"
        + "{% endif %}\n"
        # The E32's own missed comfort (E32 SL-A, the scoreboard's comfort) counts the house: one line, and the rooms
        # without the older per-room figure; older firmware: per room, as before.
        + "{% if d.missed_comfort_basis == 'e32' %}- " + fill(t["day_missed"], missed="d.missed_comfort_minutes")
        + "\n{% endif %}{% for r in d.rooms %}- {% set warm = r.time_to_target_minutes is not none"
        " and (r.time_to_target_minutes | round | int) > 0 %}{% if r.missed_minutes is none %}{% if warm %}"
        + fill(t["day_room_plain"], room="r.name", h=number("r.heat_hours"), ttt="r.time_to_target_minutes | round | int")
        + "{% else %}" + fill(t["day_room_no_step_plain"], room="r.name", h=number("r.heat_hours"))
        + "{% endif %}{% elif warm %}"
        # Whole minutes ("25 min", not "25.0 min": the summary keeps the median as a float).
        + fill(t["day_room"], room="r.name", h=number("r.heat_hours"), ttt="r.time_to_target_minutes | round | int",
               missed="r.missed_minutes")
        + "{% else %}" + fill(t["day_room_no_step"], room="r.name", h=number("r.heat_hours"), missed="r.missed_minutes")
        + "{% endif %}\n{% endfor %}{% if not d.complete %}\n_" + t["day_partial"] + "_{% endif %}"
        + "{% elif not shown.lines %}" + t["day_none"] + "{% endif %}")


def _figure(t, digits):
    """A Jinja expression: the number in v with digits decimals and the language's decimal sign."""
    return "(('%." + str(digits) + "f' % (v | float)) | replace('.', " + json.dumps(t["decimal"]) + "))"


def _jinja_text(text, **values):
    """A translated text with {name} placeholders as one Jinja string expression: "warm " ~ (m) ~ " min late"."""
    pieces = []
    for k, piece in enumerate(re.split(r"\{(\w+)\}", text)):
        if k % 2:
            pieces.append("(" + values[piece] + ")")
        elif piece:
            pieces.append(json.dumps(piece, ensure_ascii=False))
    return " ~ ".join(pieces) or '""'


# The headline figures of "Yesterday in figures", large on their own card above the lines (frontend/house-card.js,
# custom:openthermostat-yesterday), each from its own scoreboard sensor: (card key, sensor, its attribute or None for
# the state). The first figure is the lead room's warm on time (_yesterday_figures).
YESTERDAY_FIGURES = (("starts", "burner_starts_per_heating_hour", None), ("gas", "heating_gas_yesterday", None),
                     ("degree_days", "gas_per_degree_day", "degree_days"))


def _scoreboard_lines(t, rooms, names, house, large=()):
    """Yesterday's scoreboard (scoreboard.py, E32 rc.4) in plain words, as list lines of "Yesterday in figures":
    each room warm on time and how far it got above its target; the heating time, the burner's starts per heating
    hour and its short runs; the gas for heating, the degree-days and the gas per degree-day.

    rooms: {room id: {"warm_on_time": entity, "overshoot": entity}}; house: {key: entity}. The text follows the
    sensors' states (the heating time and the degree-days their attributes), so a new day needs no rebuild; a
    figure without a value is left out. Every line it writes counts in ``shown.lines`` (_yesterday_figures).
    large: the figures the card above shows large, (house key, attribute) as in YESTERDAY_FIGURES and
    ("warm_on_time", room id); they are not said again here.
    """
    def part(entity, expression, attribute=None):
        """One figure from the entity's state, or from one of its attributes (the heating hours, the degree-days)."""
        value = ("state_attr(" + json.dumps(entity) + ", " + json.dumps(attribute) + ")" if attribute
                 else "states(" + json.dumps(entity) + ")")
        return "{% set v = " + value + " %}{% if is_number(v) %}{% set parts = parts + [" + expression + "] %}{% endif %}"

    def line(prefix):
        return ("{% if parts %}{% set shown.lines = shown.lines + 1 %}- " + prefix + "{{ parts | join(' · ') }}\n"
                "{% endif %}")
    def minutes(x):
        """Whole minutes: "12 min", or "1 h 35 min" from an hour."""
        return "((" + x + " ~ ' min') if " + x + " < 60 else " + _duration(t, x) + ")"
    content = ""
    for room_id, keys in rooms.items():
        content += "{% set parts = [] %}"
        if keys.get("warm_on_time") and ("warm_on_time", room_id) not in large:  # minutes after the switch time
            # 3 hours or more: the E32 counts a room that never got warm as 3 hours late, so "not warm within 3 h".
            content += ("{% set v = states(" + json.dumps(keys["warm_on_time"]) + ") %}{% if is_number(v) %}"
                        "{% set m = v | float | round(0) | int %}{% set parts = parts + [("
                        + json.dumps(t["scoreboard_not_warm"], ensure_ascii=False) + ") if m >= " + str(NOT_WARM_MIN)
                        + " else (" + _jinja_text(t["scoreboard_late"], d=minutes("m")) + ") if m > 0 else ("
                        + _jinja_text(t["scoreboard_early"], d=minutes("(-m)")) + ") if m < 0 else "
                        + json.dumps(t["scoreboard_on_time"], ensure_ascii=False) + "] %}{% endif %}")
        if keys.get("overshoot"):  # the highest temperature above the target: 0 or below is not too warm
            content += ("{% set v = states(" + json.dumps(keys["overshoot"]) + ") %}{% if is_number(v) and v | float > 0.05 %}"
                        "{% set parts = parts + [" + _jinja_text(t["scoreboard_overshoot"], c=_figure(t, 1)) + "] %}"
                        "{% endif %}")
        content += line("**{{ " + json.dumps(names.get(room_id, room_id), ensure_ascii=False) + " }}**: ")
        # 1.4.2 (F16): a room that heats along only or is off gets no figure; it says so in grey, never "Unknown".
        reason = keys.get("warm_on_time") or keys.get("overshoot")
        if reason:
            why = json.dumps({"heat_along": t["scoreboard_heat_along"], "off": t["scoreboard_room_off"]},
                             ensure_ascii=False)
            content += ("{% set r = state_attr(" + json.dumps(reason) + ", 'reason') %}{% set why = " + why + " %}"
                        "{% if not parts and r in why %}{% set shown.lines = shown.lines + 1 %}- **{{ "
                        + json.dumps(names.get(room_id, room_id), ensure_ascii=False) + " }}**: <font color=\""
                        + ICON_COLOURS["link_unknown"] + "\">{{ why[r] }}</font>\n{% endif %}")
    # (sensor, its attribute or None for the state, text, placeholder, decimals): the heating hours and the
    # degree-days ride as attributes on the burner-starts and gas-per-degree-day sensors (scoreboard.py).
    for figures in ((("burner_starts_per_heating_hour", "heating_hours", "scoreboard_hours", "h", 1),
                     ("burner_starts_per_heating_hour", None, "scoreboard_burner", "n", 1),
                     ("short_cycling_hours", None, "scoreboard_short", "h", 1)),
                    (("heating_gas_yesterday", None, "scoreboard_gas", "kwh", 1),
                     ("gas_per_degree_day", "degree_days", "scoreboard_degree_days", "d", 1),
                     ("gas_per_degree_day", None, "scoreboard_degree_day", "v", 2))):
        said = [(key, attribute) for key, attribute, *_ in figures if house.get(key) and (key, attribute) not in large]
        if said:
            content += "{% set parts = [] %}"
            for key, attribute, text, name, digits in figures:
                if (key, attribute) in said:
                    figure = _jinja_text(t[text], **{name: _figure(t, digits)})
                    if key == "short_cycling_hours":  # "Short burner runs: none", not "0.0 h"
                        figure = ("(" + json.dumps(t["scoreboard_short_none"], ensure_ascii=False)
                                  + " if (v | float) < 0.05 else " + figure + ")")
                    content += part(house[key], figure, attribute)
            content += line("")
    # The E32's "yesterday" is its last scored day: after a day without a trusted clock an older one, said once.
    dated = next((entity for keys in rooms.values() for entity in keys.values()), None) or next(iter(house.values()), None)
    if dated:
        months = json.dumps(t["months"].split(","), ensure_ascii=False)
        content = ("{% set yd = state_attr(" + json.dumps(dated) + ", 'day') %}"
                   "{% if yd is string and yd | length == 10 and yd != (now() - timedelta(days=1)).strftime('%Y-%m-%d') %}"
                   "_{{ " + _jinja_text(t["figures_day"], date="(yd[8:10] | int) ~ ' ' ~ " + months + "[(yd[5:7] | int) - 1]")
                   + " }}_\n\n{% endif %}" + content)
    return content


def _yesterday_figures(t, rooms, names, house, summary=None, missed=None, gas_unit=None, lead=None, meter=False,
                       learned=None):
    """Yesterday (dashboard-spec §6; 1.4.3 design 4.2 item 4), once, on the Learning view: the four headline figures
    large, two by two (frontend/house-card.js, custom:openthermostat-yesterday: the lead room warm on time, burner starts
    per heating hour, gas for heating and the degree-days, each from its own scoreboard sensor), under them what stood
    out (the learned overview's ``insights``, ``learned``: one highlighted line each, _noticed_card), the missed comfort
    per day, the rest of the scoreboard (scoreboard.py, E32 rc.4) and the daily summary (daily_summary.py) in lines,
    and one note.

    rooms, house: the scoreboard's sensors (_scoreboard_lines); summary, missed: the daily summary's; lead: the room
    whose warm on time is a headline figure. A figure without its sensor is left out. The cards follow the states,
    so a new day needs no rebuild; the section hides as a whole until one figure has a value, the figures card
    until one of its own has, and the lines while they have nothing to add (one gas figure: the summary's gas line
    only while the scoreboard has none).
    """
    if meter:  # measured with the gas meter: the summary's gas line in the meter's unit, not the boiler's estimate
        house = {key: entity for key, entity in house.items() if key != "heating_gas_yesterday"}
    scoreboard = [entity for keys in rooms.values() for entity in keys.values()] + list(house.values())
    if not scoreboard and not summary:
        return None
    from .room_overview import YESTERDAY_CARD_TYPE
    room = rooms.get(lead, {}).get("warm_on_time")
    figures = {"room": {"entity": room, "name": names.get(lead, lead)} if room else None,
               **{key: house.get(sensor) for key, sensor, _ in YESTERDAY_FIGURES}}
    figures = {key: value for key, value in figures.items() if value}
    large = {(sensor, attribute) for key, sensor, attribute in YESTERDAY_FIGURES if key in figures}
    large |= {("warm_on_time", lead)} if room else set()
    entities = [entity for entity in [room, *(house.get(sensor) for _, sensor, _ in YESTERDAY_FIGURES)] if entity]
    # A figure on the card counts as a line: "tomorrow" only while nothing has a value yet.
    counted = ("{% if " + " or ".join("is_number(states(" + json.dumps(entity) + "))" for entity in entities)
               + " %}{% set shown.lines = shown.lines + 1 %}{% endif %}") if entities else ""
    content = ("{% set shown = namespace(lines=0) %}" + counted + _scoreboard_lines(t, rooms, names, house, large)
               + (_summary_lines(t, summary, gas_unit, house.get("heating_gas_yesterday")) if summary else ""))
    return _section_known(
        [*scoreboard, summary, missed],
        _heading(t["yesterday_figures"], ICONS["yesterday"]),
        _full({"type": YESTERDAY_CARD_TYPE, **figures, "visibility": _any_known(entities)}) if figures else None,
        _full(_noticed_card(t, learned)) if learned else None,
        _full(_per_day(t["missed_per_day"], [{"entity": missed, "name": t["missed_series"]}], missed)) if missed else None,
        _full({"type": "markdown", "show_empty": False, "content": content}),
        _full(_note(t, t["scoreboard_note"])))


def _hot_water_use_cards(t, hub, heating_active=None, tank=False):
    """When hot water is tapped and when it is kept warm, for the Boiler view's hot-water section: the last 24 hours
    of what the boiler does (next to its own "heating" bit) and one note on tapping and keeping warm (with a storage
    tank: on tapping and charging the tank), both while the activity has a value. The note also says that today's
    figures follow within five minutes after a hot-water period (1.4.2). The gas per day is under "Today and this
    week". No cards without the activity (firmware before it)."""
    activity = hub.get("boiler_activity")
    if not activity:
        return []
    rows = [(activity, t["activity"]), (heating_active, t["state_heating"])]
    return [{"type": "history-graph", "title": t["activity_timeline"], "hours_to_show": 24,
             "entities": [{"entity": entity_id, "name": name} for entity_id, name in rows if entity_id],
             "visibility": _known(activity)},
            _note(t, t["dhw_use_note_tank" if tank else "dhw_use_note"], _known(activity))]


def _boiler_now(t, hub, fields, essential, flow_source=None):
    """Now (dashboard-spec §5.1; rc.5 as the owner's sketch), first on the Boiler view: one card
    (frontend/boiler-now-card.js, custom:openthermostat-boiler-now). A band in the colour of what the boiler does
    (heating, hot water or resting; red with what to do while its display code is a fault) with the display code in
    words, the connection with the boiler and whether it serves hot water; under it, large, the water to the heating
    (what is asked of the boiler and the most the E32 asks near the target), the water back (the difference), the
    burner power and its starts in the last hour (calm or not, and today's starts).

    The card reads only the entities it is given and draws what it has (a figure without its entity is left out, one
    without a value says "—"). The section hides as a whole while none of the display code, what the boiler does, the
    water to the heating or back and the burner power or its starts has a value, so its heading never stands over
    nothing. (_boiler_sections lays it across the whole width on a wide screen.)

    flow_source: the "Water temperature set by" sensor (e32_flow.FlowSourceSensor), whose ``ceiling_c`` is the most
    the E32 asks near the target now."""
    from .room_overview import BOILER_NOW_CARD_TYPE
    code, flow, back, modulation = (essential(key) for key in ("code", "flow", "return", "modulation"))
    activity, starts = hub.get("boiler_activity"), hub.get("burner_starts_last_hour")
    doing = activity or fields.get("heating_active")
    shown = [code, doing, flow or back, modulation or starts]
    if not any(shown):
        return None
    # Each only with its entity: the boiler's own heating and hot water bits (an older integration: the hub's), its
    # display code, the water, the burner, the E32's starts count and short-cycling judgement, today's starts (their
    # statistic), the E32's request and the ceiling in effect.
    reads = {"activity": activity, "heating": fields.get("heating_active") or hub.get("boiler_heating_active"),
             "hot_water": fields.get("dhw_active") or hub.get("boiler_hot_water_active"), "code": code, "flow": flow,
             "return": back, "modulation": modulation, "starts": starts, "starts_today": hub.get("daily_burner_starts"),
             "cycling": hub.get("burner_short_cycling"), "request": hub.get("heat_request"), "ceiling": flow_source}
    return _section_known(shown, _heading(t["now"], ICONS["now"]),
                          {"type": BOILER_NOW_CARD_TYPE, "grid_options": {"columns": "full"},
                           **{key: value for key, value in reads.items() if value}})


def _flow_tiles(t, flow):
    """1.4.5 (HA-DHW-FLOW-145): the boiler's hot water flow as one tile across the section: "Tapping now" with the
    flow (6.2 L/min, in the viewer's number format) while it is above 0, "No tapping" (no figure) at 0. Only with the
    flow entity (a boiler whose flow moved once: v1_boiler_fields.LIVE_FLOW, or the EMS+ field) and while it has a
    value; never "Unknown"."""
    if not flow:
        return []
    tapping = _wide(_tile(flow, t["tapping_now"], ICONS["dhw_flow"],
                          visibility=[{"condition": "numeric_state", "entity": flow, "above": 0.05}]))
    idle = _wide(_tile(flow, t["no_tapping"], ICONS["dhw_flow"],
                       visibility=[{"condition": "numeric_state", "entity": flow, "below": 0.05}]))
    idle["hide_state"] = True
    return [tapping, idle]


def _hot_water_section(t, hub, fields, essential, tank=False):
    """Hot water (dashboard-spec §5.4): its temperature next to its target, the flow (1.4.5), today's taps, keeping
    warm (a tank: its charges) and burner time, and what the boiler did in the last 24 hours with one note on tapping
    and keeping warm (a tank: on tapping and charging the tank)."""
    measured = essential("dhw")
    target = fields.get("reported_dhw_target") or fields.get("selected_dhw_temperature")
    flow = fields.get("dhw_flow") or fields.get("plus_dhw_flow")
    today = [hub[key] for key in DHW_TODAY if key in hub]
    return _filled(_section_known(
        [measured, flow, *today, hub.get("boiler_activity")],
        _heading(t["group_dhw"], ICONS["hot_water"]),
        *_pair(_tile(measured, t["dhw"], ICONS["dhw"]), _tile(target, t["dhw_target_short"], ICONS["dhw_target"])),
        *_flow_tiles(t, flow),
        _known_entities_card(today) if today else None,
        *_hot_water_use_cards(t, hub, fields.get("heating_active"), tank)))


def _value_tile(entity_id, name, icon, color=None):
    """A boiler value, shown only while it has one. Without the E32 the "Heating" tile says why,
    instead of a row of "Unavailable" tiles."""
    return _tile(entity_id, name, icon, color=color, visibility=_known(entity_id)) if entity_id else None


def _wanting_card(t, request):
    """Which rooms want heat and the boiler request, as the E32's dashboard shows it (rc.3, owner's wish).

    "1 room wants heat", then each such room with its temperature and target, then the request.
    From the heat request's ``rooms`` attribute, so it follows the E32 without regenerating.
    """
    if not request:
        return None
    quoted = json.dumps(request)

    def number(value):
        return "{{ ('%.1f' % (" + value + " | float)) | replace('.', " + json.dumps(t["decimal"]) + ") }}"

    return {"type": "markdown", "content": (
        "{% set wanting = (state_attr(" + quoted + ", 'rooms') or []) | selectattr('demand', 'eq', true) | list %}"
        "### {% if wanting | length == 1 %}" + t["wanting_one"]
        + "{% elif wanting %}" + t["wanting_many"].replace("{n}", "{{ wanting | length }}")
        + "{% else %}" + t["wanting_none"] + "{% endif %}\n"
        "{% for room in wanting %}- **{{ room.name }}**"
        "{% if room.temperature is number and room.setpoint is number %}: "
        + number("room.temperature") + " → " + number("room.setpoint") + " °C{% endif %}\n{% endfor %}"
        "{% if states(" + quoted + ") | float(0) > 0 %}\n" + t["boiler_request"] + ": "
        + number("states(" + quoted + ")") + " °C{% endif %}")}


def _holiday_card(t, select):
    """The next holiday (E32 rc.4, house.holidays.v1): "Holiday from 20 Dec to 3 Jan", or "On holiday until 3 Jan"
    while it runs. From the house mode select's ``holidays`` attribute, so it follows the E32 without regenerating;
    empty (and hidden) without a planned holiday or on firmware without them. The first holiday only once there is
    one: Home Assistant's markdown card renders strictly, where "first" of an empty list is an error that left an
    empty card standing (and an error in the log every 30 s).
    """
    if not select:
        return None

    def day(name):
        return "{{ " + name + ".day }} {{ months[" + name + ".month - 1] }}"

    return {"type": "markdown", "show_empty": False, "content": (
        "{% set holidays = state_attr(" + json.dumps(select) + ", 'holidays') or [] %}"
        "{% if holidays %}{% set h = holidays[0] %}{% set months = " + json.dumps(t["months"], ensure_ascii=False)
        + ".split(',') %}"
        "{% set f = as_local(as_datetime(h['from'])) %}{% set u = as_local(as_datetime(h['until'])) %}"
        "{% if f <= now() %}" + t["holiday_now"].replace("{until}", day("u"))
        + "{% elif f.date() == u.date() %}" + t["holiday_day"].replace("{from}", day("f"))
        + "{% else %}" + t["holiday_next"].replace("{from}", day("f")).replace("{until}", day("u"))
        + "{% endif %}{% endif %}")}


# -- rc.5 (P18): the Overview as the owner's sketch: Today and the House rows -------------------------------------------


def _clock(moment):
    """A Jinja expression: the local datetime ``moment`` as a time of day, 06:10 (two digits, as the E32 pages, the
    Rooms view and the glossary write it)."""
    return "(('%02d' % " + moment + ".hour) ~ ':' ~ ('%02d' % " + moment + ".minute))"


def _degrees(t, value):
    """A Jinja expression: a temperature as a target is set, 21 or 20.5, with the language's decimal sign."""
    return ("((" + value + " | int) ~ '' if " + value + " == (" + value + " | int) else (('%.1f' % " + value
            + ") | replace('.', " + json.dumps(t["decimal"]) + ")))")


def _date(t, moment):
    """A Jinja expression: the local datetime ``moment`` as "5 Nov" (the language's months)."""
    months = json.dumps(t["months"].split(","), ensure_ascii=False)
    return moment + ".day ~ ' ' ~ " + months + "[" + moment + ".month - 1]"


def _when(t, days, moment):
    """A Jinja expression: "Today", "Tomorrow" or "On 7 Nov" for ``moment``, ``days`` days from today."""
    date = _jinja_text(t["when_date"], date=_date(t, moment))
    return ("(" + json.dumps(t["when_today"], ensure_ascii=False) + " if " + days + " == 0 else "
            + json.dumps(t["when_tomorrow"], ensure_ascii=False) + " if " + days + " == 1 else (" + date + "))")


def _duration(t, minutes):
    """A Jinja expression: whole minutes of an hour or more as "1 h 35 min" or "2 h" (the language's units)."""
    return ("(" + _jinja_text(t["dur_h_m"], h=minutes + " // 60", m=minutes + " % 60") + " if " + minutes
            + " % 60 else " + _jinja_text(t["dur_h"], h=minutes + " // 60") + ")")


# The room's Reason (room_overview.REASONS) while the E32 holds its week program (away, nobody home or an open window:
# RoomOverrides::holdsProgram, no early start) or heats for the end of a holiday: Today says that instead of a warm-up
# the E32 does not do. The E32's own telemetry plan still says "planned" then. 1.4.1: in summer no room warms up.
HELD_REASONS = {"away": "today_away", "room_away": "today_nobody", "house_away": "today_nobody",
                "away_return": "today_return", "window_open": "today_window", "summer": "today_summer"}
# The room's comfort mode behind a Reason that ranks above it (no measurement, hot water, a boiler pause): the E32
# holds the program all the same. Away is a holiday when it has an end.
HELD_COMFORT = {"away": "holiday", "presence_away": "house_away", "window_open": "window_open"}
NOT_WARM_MIN = 180  # ArrivalLearner: a room not warm within 3 hours counts as 3 hours late


def _held_line(t, text, room, reason):
    """Jinja: Today's line for a held room (HELD_REASONS). An open window names its kind when the E32 does (1.0.1, the
    Reason sensor's ``opening``: "Living room is paused: a door is open."); 1.0.0 does not tell them apart."""
    plain = "{{ " + _jinja_text(t[text], room=room) + " }}"
    if text != "today_window":
        return plain
    return ("{% set op = state_attr(" + reason + ", 'opening') %}{% if op in ['window', 'door'] %}"
            "{{ (" + _jinja_text(t["today_window_door"], room=room) + ") if op == 'door' else ("
            + _jinja_text(t["today_window_window"], room=room) + ") }}{% else %}" + plain + "{% endif %}")


def _arrived(t, warm):
    """Jinja: how the room's last judged warm-up turned out, from its "Warm on time" (scoreboard.py: minutes after the
    switch time, negative early). Today's figure once this morning was judged ("Today it was warm 2 minutes late."),
    else yesterday's ("Yesterday ..."; "On 3 Nov ..." while the E32's last scored day is an older one); an hour or
    more in hours and minutes; 3 hours or more is "did not get warm within 3 hours" (the E32 counts that as 3 h)."""
    q = json.dumps(warm)
    yesterday = json.dumps(t["day_yesterday"], ensure_ascii=False)
    months = json.dumps(t["months"].split(","), ensure_ascii=False)
    older = _jinja_text(t["day_on"], date="(yd[8:10] | int) ~ ' ' ~ " + months + "[(yd[5:7] | int) - 1]")
    return ("{% set tm = state_attr(" + q + ", 'today') %}{% if is_number(tm) %}{% set m = tm %}"
            "{% set dd = " + json.dumps(t["day_today"], ensure_ascii=False) + " %}"
            "{% else %}{% set m = states(" + q + ") %}{% set yd = state_attr(" + q + ", 'day') %}"
            "{% set dd = " + yesterday + " if not yd or yd is not string or yd | length != 10"
            " or yd == (now() - timedelta(days=1)).strftime('%Y-%m-%d') else (" + older + ") %}{% endif %}"
            "{% if is_number(m) %}{% set m = m | float | round(0) | int %} "
            "{% if m >= " + str(NOT_WARM_MIN) + " %}{{ " + _jinja_text(t["arrived_not_warm"], day="dd") + " }}"
            "{% elif m >= 60 %}{{ " + _jinja_text(t["arrived_late_long"], day="dd", d=_duration(t, "m")) + " }}"
            "{% elif m > 1 %}{{ " + _jinja_text(t["arrived_late"], day="dd", m="m") + " }}"
            "{% elif m == 1 %}{{ " + _jinja_text(t["arrived_late_one"], day="dd") + " }}"
            "{% elif m <= -60 %}{{ " + _jinja_text(t["arrived_early_long"], day="dd", d=_duration(t, "(-m)")) + " }}"
            "{% elif m < -1 %}{{ " + _jinja_text(t["arrived_early"], day="dd", m="-m") + " }}"
            "{% elif m == -1 %}{{ " + _jinja_text(t["arrived_early_one"], day="dd") + " }}"
            "{% else %}{{ " + _jinja_text(t["arrived_on_time"], day="dd") + " }}{% endif %}{% endif %}")


def _warm_up_line(t, name, start, state=None, warm=None, smart=None, reason=None, request=None):
    """One line of Today for a room that is switched on: when it warms up and for what ("Tomorrow Living room warms
    up from 06:10 to be 20.5 °C at 07:00."), then how its last warm-up turned out ("Yesterday it was warm 4 minutes
    early.", _arrived).

    From the room's "Smart warm-up start" sensor (heating_link.RoomHeatingStartSensor: its state the start the E32
    plans, later by what the free heat gives, its attributes the program step it plans for, switch_at and target_c,
    start_now, reachable, lead_minutes and estimate) and its "Warm on time" (scoreboard.py). With Smart warm-up
    switched off the heating starts at the program time, so the line says that. With no lead (lead_minutes 0) the
    room is warm enough already; the E32 has no cooling model yet and plans from the room's temperature now, so the
    start moves earlier as it cools, and the line says so. A start no morning has judged yet (estimate) says
    "(estimate)", as the Learning tab does; a start that cannot reach the target in time says it may come a little
    later (with free heat the sensor leaves that flag out: it is for the start without it). In the trial run (the
    heat request's mode ``shadow``) and before the takeover is confirmed (its ``control`` awaiting_confirmation) the
    E32 heats nothing early: "would warm up". While the room's Reason (``reason``) is away, nobody home, an open
    window or warming up for the end of a holiday, or its ``comfort_mode`` is one of them behind a Reason that ranks
    higher (hot water, a boiler pause), the E32 does no early start (RoomOverrides::holdsProgram), so the line says
    that instead. A program step on
    another day than the start says its day ("at 00:30 tomorrow"). Nothing while the start is unknown (no step up
    within 24 hours) or the room is off (``state``, its on/off select); _today_section shows the card on the same
    terms.
    """
    q, room = json.dumps(start), json.dumps(name, ensure_ascii=False)
    on = " and not is_state(" + json.dumps(state) + ", 'inactive')" if state else ""
    off = "is_state(" + json.dumps(smart) + ", 'off')" if smart else "false"
    # The trial run, or active control before the takeover is confirmed: the E32 heats nothing early (house card).
    trial = ("(is_state_attr(" + json.dumps(request) + ", 'mode', 'shadow') or is_state_attr(" + json.dumps(request)
             + ", 'control', 'awaiting_confirmation'))") if request else "false"
    step = {"room": room, "time": _clock("w"), "target": _degrees(t, "g")}
    # The step's time with its day when that is not the start's day: "at **00:30 tomorrow**".
    later = {**step, "time": "wt"}
    held = ""
    if reason:
        r = json.dumps(reason)
        # The Reason ranks no measurement, hot water and a boiler pause above away and holiday, while the E32 still
        # holds the program: its comfort_mode says so then (a holiday is away with an end, comfort_until).
        held = ("{% set why = states(" + r + ") %}{% set cm = state_attr(" + r + ", 'comfort_mode') %}"
                "{% if why not in " + json.dumps(["holiday", *HELD_REASONS]) + " and cm in "
                + json.dumps(list(HELD_COMFORT)) + " %}{% set why = " + json.dumps(HELD_COMFORT) + "[cm] %}{% endif %}"
                "{% if why == 'holiday' %}"
                "{% set u = (state_attr(" + r + ", 'values') or {}).get('until') or state_attr(" + r
                + ", 'comfort_until') %}"
                "{% set u = as_datetime(u, none) if u else none %}"
                "{% if u is not none %}{% set u = as_local(u) %}{{ "
                + _jinja_text(t["today_holiday"], room=room, date=_date(t, "u")) + " }}"
                "{% else %}{{ " + _jinja_text(t["today_away"], room=room) + " }}{% endif %}"
                + "".join("{% elif why == " + json.dumps(key) + " %}" + _held_line(t, text, room, r)
                          for key, text in HELD_REASONS.items())
                + "{% elif w is not none and g is number %}")
    # b: the planned start, w: the program step's time and g its temperature (local), d: days from today.
    line = ("{% set s = states(" + q + ") %}"
            "{% set b = as_datetime(s, none) if s not in ['unknown', 'unavailable'] else none %}"
            "{% if b is not none" + on + " %}{% set b = as_local(b) %}{% set at = state_attr(" + q + ", 'switch_at') %}"
            "{% set w = as_datetime(at, none) if at else none %}{% set w = as_local(w) if w is not none else none %}"
            "{% set g = state_attr(" + q + ", 'target_c') %}{% set d = (b.date() - now().date()).days %}"
            "{% if w is not none %}{% set wt = " + _clock("w") + " if w.date() == b.date() else ("
            + _jinja_text(t["at_tomorrow"], time=_clock("w")) + " if (w.date() - now().date()).days == 1 else ("
            + _jinja_text(t["at_date"], time=_clock("w"), date=_date(t, "w")) + ")) %}{% endif %}"
            + _icon("warm_up") + " " + (held or "{% if w is not none and g is number %}")
            # Smart warm-up off: heating starts at the program time (the day of that time).
            + "{% if " + off + " %}{% set d = (w.date() - now().date()).days %}"
            "{{ " + _jinja_text(t["warm_up_off"], when=_when(t, "d", "w"), **step) + " }}"
            # Warm enough already (no lead, or the start is the step's own minute): the E32 knows no cooling yet, so
            # the start moves earlier as the room cools; never "from 9:00 to be 20.5 °C at 9:00".
            "{% elif (state_attr(" + q + ", 'lead_minutes') == 0 or (w - b).total_seconds() < 60)"
            " and state_attr(" + q + ", 'start_now') != true %}"
            "{{ " + _jinja_text(t["warm_up_ready"], when=_when(t, "d", "b"), **step) + " }}"
            # The start has come (or the E32 says it started): warming up now; in the trial run it only would; not
            # reachable in time: the target may come a little later; a start no morning judged yet: "(estimate)".
            "{% elif state_attr(" + q + ", 'start_now') == true or b <= now() %}"
            "{% if " + trial + " %}{{ " + _jinja_text(t["warm_up_trial_now"], **step) + " }}"
            "{% elif state_attr(" + q + ", 'reachable') == false %}{{ " + _jinja_text(t["warm_up_late"], **step) + " }}"
            "{% elif state_attr(" + q + ", 'estimate') == true %}"
            "{{ " + _jinja_text(t["warm_up_now_estimate"], **step) + " }}"
            "{% else %}{{ " + _jinja_text(t["warm_up_now"], **step) + " }}{% endif %}"
            "{% elif " + trial + " %}"
            "{{ " + _jinja_text(t["warm_up_trial"], when=_when(t, "d", "b"), start=_clock("b"), **later) + " }}"
            # E32 rc.4: a start no morning has judged yet (the standard warm-up time), "estimate" as the Learning tab.
            "{% elif state_attr(" + q + ", 'estimate') == true %}"
            "{{ " + _jinja_text(t["warm_up_estimate"], when=_when(t, "d", "b"), start=_clock("b"), **later) + " }}"
            "{% else %}{{ " + _jinja_text(t["warm_up_at"], when=_when(t, "d", "b"), start=_clock("b"), **later) + " }}"
            "{% endif %}"
            # An E32 before rc.2 names no program step: the start alone.
            "{% else %}{{ " + _jinja_text(t["warm_up_from"], when=_when(t, "d", "b"), room=room, start=_clock("b")) + " }}"
            "{% endif %}")
    if warm:  # the last judged warm-up: minutes late, early or on time
        line += _arrived(t, warm)
    return line + "\n\n{% endif %}"


def _weather_line(t, curve, request=None):
    """The line of Today on weather compensation, the first line of the day (1.4.3, design 4.3): "Outdoor 6.7 °C: the
    E32 asks 42 °C water, on the line it learned for your house." From "Water temperature by weather compensation"
    (e32_flow.py): its attributes flow_c (what the E32 asks, °C, with the room correction), outdoor_c (the outdoor
    temperature the E32 uses, °C), state (applied, or advice while weather compensation is switched off) and
    slope_source (learned: the line learned for the house). The short clause about the line only when it is the learned
    one; the arithmetic (what the line gives, what the rooms add, how far the learning is) is the heating curve's on the
    Learning tab. While no room asks for heat (the heat request is 0 °C) nothing is sent: it says what the E32 asks when
    a room asks. There whenever the sensor has a value; without an outdoor temperature it starts with what it asks.
    """
    q = json.dumps(curve)
    # One decimal as the House row, a true minus sign: "Outdoor −3.6 °C".
    outside = _jinja_text(t["weather_outside"], outdoor="('%.1f' % ((o | round(1)) + 0)) | replace('-', '−') | replace('.', "
                          + json.dumps(t["decimal"]) + ")")
    main = ("(" + _jinja_text(t["weather_off"], flow="f") + ") if advice else (" + _jinja_text(t["weather_idle"], flow="f")
            + ") if idle else (" + _jinja_text(t["weather_asks"], flow="f") + ")")
    idle = ("not (states(" + json.dumps(request) + ") | float(0) > 0)") if request else "false"
    return ("{% set f = state_attr(" + q + ", 'flow_c') %}{% if f is number %}{% set f = f | round(0) | int %}"
            "{% set o = state_attr(" + q + ", 'outdoor_c') %}"
            "{% set advice = state_attr(" + q + ", 'state') == 'advice' %}{% set idle = " + idle + " %}"
            "{% set main = " + main + " %}" + _icon("weather") + " "
            # Without an outdoor temperature the sentence starts with what it asks, from a capital.
            "{% if o is number %}{{ " + outside + " }}: {{ main }}{% else %}{{ main[:1] | upper }}{{ main[1:] }}{% endif %}"
            "{% if not advice and state_attr(" + q + ", 'slope_source') == 'learned' %}, {{ " + _jinja_text(t["line_learned"])
            + " }}{% endif %}.{% endif %}")


def _today_section(t, rooms, curve=None, smart=None, request=None):
    """Today (rc.5, the owner's sketch), on the Overview: per room that is switched on, when it warms up and how
    its last warm-up went (_warm_up_line), then what weather compensation asks now (_weather_line), in one card.

    rooms: [(name, "Smart warm-up start" sensor, the room's on/off select or None, "Warm on time" or None, its Reason
    or None)]; curve: "Water temperature by weather compensation" or None; smart: the Smart warm-up switch or None;
    request: the heat request (its mode: the trial run; its value: whether a room asks for heat) or None. The card
    and its section show while one of its lines has its value (the start known and the room on, or the curve known),
    so a heading never stands over nothing; the text follows the sensors without a rebuild. None without any of them.
    """
    shown, content = [], ""
    for name, start, state, warm, *reason in rooms:
        content += _warm_up_line(t, name, start, state, warm, smart, reason[0] if reason else None, request)
        on = [{"condition": "state", "entity": state, "state_not": "inactive"}] if state else []
        shown.append({"condition": "and", "conditions": _known(start) + on})
    if curve:
        content += _weather_line(t, curve, request)
        shown.append({"condition": "and", "conditions": _known(curve)})
    if not shown:
        return None
    visibility = [{"condition": "or", "conditions": shown}]
    section = _section(_heading(t["today"], ICONS["today"]), {"type": "markdown", "content": content,
                                                               "visibility": visibility})
    section["visibility"] = visibility
    return section


def _house_rows(t, select, outdoor, planner, mode=True):
    """House (rc.5, the owner's sketch) in rows: "Home or away" with the house mode (a tap opens it, to switch; only with
    ``mode``: 1.4.1 leaves it out where the house card shows the mode large with its meaning), "Holiday" with "Plan",
    which leads to the holiday planner (``planner``: the Settings tab's House mode and holiday, 1.4; else Configure,
    the integration's page), and "Outside" with the outdoor temperature (a sensor, or a weather entity's own row).
    Each row shows while its entity has a value, the card while one of them does; None without both."""
    rows = []
    if select:
        if mode:
            rows.append({"type": "conditional", "conditions": _known(select), "row": {
                "type": "simple-entity", "entity": select, "name": t["home_or_away"], "icon": ICONS["house_mode"]}})
        rows += [{"type": "conditional", "conditions": _known(select), "row": {
                     "type": "button", "name": t["holiday"], "icon": ICONS["holiday"], "action_name": t["plan"],
                     "tap_action": {"action": "navigate", "navigation_path": planner}}}]
    if outdoor:
        rows.append({"type": "conditional", "conditions": _known(outdoor), "row": {"entity": outdoor, "name": t["outdoor"]}})
    if not rows:
        return None
    return {"type": "entities", "entities": rows, "visibility": _any_known([e for e in (select, outdoor) if e])}


def _shown_while_one_is(section, cards):
    """``section``, hidden while none of ``cards`` shows; None when none can (a markdown card that may render empty
    keeps no section). A card without a visibility of its own always shows: then the section needs none."""
    cards = [card for card in cards if card and not (card["type"] == "markdown" and card.get("show_empty") is False)]
    if not cards:
        return None
    if all(card.get("visibility") for card in cards):
        section["visibility"] = [{"condition": "or", "conditions": [
            {"condition": "and", "conditions": card["visibility"]} for card in cards]}]
    return section


def _split(text):
    """(first sentence, the rest) of a note; the rest is "" for a note of one sentence."""
    parts = re.split(r"(?<=[.!?])\s+(?=\S)", text.strip(), maxsplit=1)
    return parts[0], parts[1] if len(parts) > 1 else ""


def _details(t, rest):
    """The longer part of a note behind "More", so a phone shows one short sentence."""
    return "\n\n<details><summary>" + t["more"] + "</summary>\n\n" + rest + "\n\n</details>" if rest else ""


def _note(t, text, visibility=None):
    """A note of one sentence; whatever follows it sits behind "More"."""
    first, rest = _split(text)
    card = {"type": "markdown", "content": first + _details(t, rest)}
    if visibility:
        card["visibility"] = visibility
    return card


def _tiles(*cards):
    """Tiles that appear together: pairs of half tiles, and an odd one out across the whole width."""
    cards = [card for card in cards if card]
    if len(cards) % 2:
        _wide(cards[-1])
    return cards


def _wide(card):
    """A card across the whole section (12 of 12 grid columns), so its state is not cut short: in a section of one
    view column. In a section across n columns (_span) 12 is one view column of it: a card across such a section is
    _full."""
    if card is not None:
        card["grid_options"] = {"columns": 12}
    return card


def _full(card):
    """A card across the whole section, also one across several view columns (Home Assistant gives a section 12 grid
    columns per view column it spans: 48 across four, so 12 would be a quarter); on a phone the same as _wide."""
    if card is not None:
        card["grid_options"] = {"columns": "full"}
    return card


HALF_CARDS = ("tile", "button", "statistic", "gauge")  # Home Assistant's half-width cards (6 of 12 grid columns)


def _span(section, columns, cards="full"):
    """Lay ``section`` across ``columns`` view columns (1.4.3; Home Assistant clamps the span to the columns it shows,
    so a phone still has one, and gives the section 12 grid columns per view column). The tiles and figures keep their
    six grid columns (in a section across two columns four of them stand in one row). The other cards: ``"full"``
    across the whole section (_full); ``"pairs"`` one view column each (12), two side by side in a section across two
    (charts), an odd one out and a note across the whole section (a note beside a chart stood stretched to its
    height); ``None`` as they are (the room cards: one column each)."""
    if section is None:
        return None
    section["column_span"] = columns
    wide = [card for card in section["cards"] if card["type"] != "heading" and card["type"] not in HALF_CARDS
            and (card.get("grid_options") or {}).get("columns") != 6]
    paired = [card for card in wide if card["type"] != "markdown"] if cards == "pairs" else []
    for card in wide if cards else ():
        number = paired.index(card) if card in paired else None
        alone = number is None or (len(paired) % 2 and number == len(paired) - 1)
        card["grid_options"] = {**(card.get("grid_options") or {}), "columns": "full" if alone else 12}
    return section


def _wide_when_few(sections):
    """1.4.4 (plan 2.4, NEXT-RELEASE 1.4.4 item 4): Home Assistant shows no more columns than a view's sections span
    together, so a view of fewer than four sections stood narrow on a monitor (Diagnostics with two: 2 × 500 px at 1920
    px). Then every section spans two columns (on a phone still one), its wide cards across it (_span), a tile that was
    across its one-column section across the two. A section with half-width tiles side by side keeps one column: across
    two they would need 12 grid columns each, and a phone (12 in all) would then stack them instead of showing them in
    pairs (the Comparison's E32 and thermostat figures, P21). Applied to Diagnostics and Comparison."""
    if not 0 < len(sections) < 4:
        return sections
    for section in sections:
        paired = any(card["type"] in HALF_CARDS and (card.get("grid_options") or {}).get("columns", 6) == 6
                     for card in section["cards"])
        if section.get("column_span", 1) >= 2 or paired:
            continue
        _span(section, 2)
        for card in section["cards"]:  # a tile across its one-column section (_wide) goes across the two
            if card["type"] in HALF_CARDS and (card.get("grid_options") or {}).get("columns") == 12:
                card["grid_options"] = {**card["grid_options"], "columns": "full"}
    return sections


def _valves_section(t, rooms):
    """1.4.4 (plan 2.4 and 9): Diagnostics' list of every radiator valve, per room: what it reports (its opening, or the
    temperature it was given, its battery, "not reporting") and the E32's finding (``held``, 1.4.3), in the room card's
    words; a valve whose state the E32 could not read (``message_too_large``, FW-TRV-STATE) as a red line with its
    size; 1.4.5 (FW-TRV-DOC-145): a room whose valve document the E32 shortened to fit (``trimmed``) has a grey
    note "shortened" beside its name, here only. ``rooms``: [(the room's name, its Valve position sensor)]. Read live from the sensor's ``valves``; a room
    without valves now says nothing; the section hides while no valve sensor is there (the E32 off)."""
    if not rooms:
        return None
    comma = t["decimal"] == ","

    def word(key, **values):
        text = t[key]
        for name, expression in values.items():
            text = text.replace("{" + name + "}", "{{ " + expression + " }}")
        return text
    number = "(('%g' % {0}) | replace('.', ','))" if comma else "('%g' % {0})"
    kb = "(('%.1f' % ({0} / 1000)) | replace('.', ','))" if comma else "('%.1f' % ({0} / 1000))"
    held = {key: word("valve_" + key) for key in ("own_schedule", "own_sensor", "off_by_user", "gave_up")}
    content = ""
    for name, entity in rooms:
        quoted = json.dumps(entity)
        content += (
            "{% set vs = state_attr(" + quoted + ", 'valves') %}{% if vs %}**" + name.replace("*", "") + "**"
            "{% if state_attr(" + quoted + ", 'trimmed') %} <font color=\"" + ICON_COLOURS["link_unknown"] + "\">"
            + t["valves_trimmed"] + "</font>{% endif %}\n\n"
            "{% for v in vs %}{% set g = v.name.split(':') %}"
            "{% if v.name is match('^g[0-9]+:[0-9]+$') %}{% set label = " + json.dumps(t["valve_gateway"])
            + " | replace('{n}', g[0][1:]) | replace('{id}', g[1]) %}"
            "{% elif v.name.startswith('climate.') %}{% set label = state_attr(v.name, 'friendly_name') or v.name %}"
            "{% else %}{% set label = v.name %}{% endif %}"
            "{% if v.health == 'message_too_large' %}\n<ha-alert alert-type=\"error\">{{ label }}: "
            "{% if v.bytes is number %}" + word("valve_too_large", kb=kb.format("v.bytes")) + "{% else %}"
            + t["valve_too_large_plain"] + "{% endif %}"
            "{% if v.set_to_c is number %} · " + word("valve_set_to", t=number.format("v.set_to_c")) + "{% endif %}"
            "</ha-alert>\n\n"
            "{% else %}- {{ label }}: "
            "{% if v.health == 'offline' %}" + t["valve_offline"]
            + "{% elif v.position is number %}" + word("valve_open", n="(v.position | round | int)")
            + "{% elif v.set_to_c is number %}" + word("valve_set_to", t=number.format("v.set_to_c"))
            + "{% else %}" + t["valve_no_reading"] + "{% endif %}"
            "{% if v.battery is number %} · " + word("valve_battery", n="(v.battery | round | int)") + "{% endif %}"
            "{% set to = v.set_to_c if v.set_to_c is number else v.setpoint_c %}"
            "{% if v.held == 'put_back' %} · {% if to is number %}"
            + word("valve_put_back", t=number.format("to")) + "{% else %}" + t["valve_put_back_plain"] + "{% endif %}"
            + "".join("{% elif v.held == '" + key + "' %} · " + text for key, text in held.items())
            + "{% endif %}\n{% endif %}{% endfor %}\n{% endif %}")
    section = _section(_heading(t["valves_diag"], ICONS["valves"]), {"type": "markdown", "content": content})
    # Shown while a valve sensor is there: its state may be unknown (every valve driven by temperature has no opening).
    section["visibility"] = [{"condition": "or", "conditions": [
        {"condition": "state", "entity": entity, "state_not": "unavailable"} for _, entity in rooms]}]
    return section


def _compared(t, what, icon, e32, thermostat):
    """The Comparison subview's pair: a line with what is counted, then the E32's and the thermostat's figure."""
    tiles = [tile for tile in (_tile(e32, t["e32"], icon), _tile(thermostat, t["thermostat"], icon)) if tile]
    return [_heading(what, style="subtitle"), *tiles] if tiles else []


def _pair(first, second, rows=None):
    """Two half-width cards that appear together on one condition, while the first has a value, side by side in one
    row; one alone takes the whole width (dashboard-spec §1). ``rows``: their height in grid rows, set on both so the
    row is even (a figure or a gauge needs two, and so does a tile beside one)."""
    cards = [card for card in (first, second) if card]
    for card in cards:
        card["visibility"] = _known(cards[0]["entity"])
        if len(cards) == 1:
            card["grid_options"] = {"columns": 12, **({"rows": rows} if rows else {})}
        elif rows:
            card["grid_options"] = {"columns": 6, "rows": rows}
    return cards


def _statistic(entity_id, name, icon):
    """Today's figure of a running total (its change since local midnight): today's gas or burner."""
    if not entity_id:
        return None
    return {"type": "statistic", "entity": entity_id, "name": name, "icon": icon,
            "period": {"calendar": {"period": "day"}}, "stat_type": "change"}


def _tile(entity_id, name=None, icon=None, features=None, visibility=None, color=None, tap_action=None,
          state_content=None):
    if entity_id is None:
        return None
    card = {"type": "tile", "entity": entity_id}
    if name:
        card["name"] = name
    if icon:
        card["icon"] = icon
    if color:
        card["color"] = color
    if tap_action:
        card["tap_action"] = tap_action
    if state_content:
        card["state_content"] = state_content
    if features:
        card["features"] = features
    if visibility:
        card["visibility"] = visibility
    return card


class RoomDashboard:
    """Manage a separate dashboard containing the discovered climate entities."""

    def __init__(self, hass: HomeAssistant, prefix: str, entry_id: str) -> None:
        self.hass = hass
        self.prefix = prefix
        self.entry_id = entry_id
        self.path = f"open-thermostat-{slugify(prefix, separator='-')}-{entry_id[:8].lower()}"
        # The settings view (1.4): the room status cards' "Settings" button opens <settings_path>#room/<id>.
        self.settings_path = f"/{self.path}/settings"
        self._rooms: set[str] = set()
        self._store: LovelaceStorage | None = None
        self._unsubscribe = []
        self._refresh_task: asyncio.Task | None = None
        self._dirty = False
        self._hub = None
        self._hub_unsubscribe = None
        self._hub_signature = None
        self._mode = None  # the E32's last reported mode (shadow / active), kept while it is silent
        self._candidate: LovelaceStorage | None = None  # registered, panel not yet (async_start)
        # This entry's entities and devices at the last build: registry events about others never rebuild.
        self._entity_ids: set[str] = set()
        self._device_ids: set[str] = set()
        self._registry_timer = None  # the debounced rebuild after registry or language changes

    async def async_start(self) -> None:
        """Register a Lovelace panel without changing the user's dashboards.

        Optional: a failure is logged and undone, never failing the installation's setup.
        """
        try:
            await self._async_start()
        except Exception:  # noqa: BLE001 - the dashboard is optional
            _LOGGER.exception("The OpenThermostat dashboard could not be started; "
                              "the installation works without it and tries again on its next start")
            candidate, self._candidate = self._candidate, None
            if self._store is not None:
                await self.async_stop()
            elif candidate is not None and self.hass.data[LOVELACE_DATA].dashboards.get(self.path) is candidate:
                self.hass.data[LOVELACE_DATA].dashboards.pop(self.path, None)
        self._candidate = None

    async def _async_start(self) -> None:
        entry = self.hass.config_entries.async_get_entry(self.entry_id)
        if entry and is_product(entry):
            # Normally done once in async_setup; again here (idempotent) so the cards'
            # modules come back after the last installation was removed and a new one added.
            from .week_planner import async_setup_planner
            await async_setup_planner(self.hass)
        dashboards = self.hass.data[LOVELACE_DATA].dashboards
        if self.path in dashboards or frontend.async_panel_exists(self.hass, self.path):
            _LOGGER.warning("Cannot create OpenThermostat dashboard: %s is already used", self.path)
            return

        config = {
            "id": self.path,
            "url_path": self.path,
            "title": "OpenThermostat",
            "icon": "mdi:thermostat",
            "show_in_sidebar": True,
            "require_admin": False,
        }
        store = LovelaceStorage(self.hass, config)
        await store.async_save(self._dashboard_config())
        dashboards[self.path] = self._candidate = store
        try:
            frontend.async_register_built_in_panel(
                self.hass,
                "lovelace",
                frontend_url_path=self.path,
                sidebar_title=config["title"],
                sidebar_icon=config["icon"],
                show_in_sidebar=True,
                require_admin=False,
                config={"mode": "storage"},
            )
        except ValueError:
            dashboards.pop(self.path, None)
            _LOGGER.warning("Cannot register OpenThermostat dashboard at %s", self.path)
            return
        self._store = store
        self._listen()
        self._watch_hub()

    @callback
    def _listen(self) -> None:
        """Rebuild after registry changes of this entry's own entities and devices and after a change of
        language or units; the registry events of every other integration pass by (R4-11)."""
        self._unsubscribe = [
            self.hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, self._registry_updated,
                                       event_filter=self._own_entity_event),
            self.hass.bus.async_listen(dr.EVENT_DEVICE_REGISTRY_UPDATED, self._registry_updated,
                                       event_filter=self._own_device_event),
            self.hass.bus.async_listen(EVENT_CORE_CONFIG_UPDATE, self._registry_updated,
                                       event_filter=self._language_or_units),
        ]

    @callback
    def _own_entity_event(self, data) -> bool:
        """An entity of this entry was created, renamed, enabled or removed."""
        entity_id = data.get("entity_id")
        if entity_id in self._entity_ids or data.get("old_entity_id") in self._entity_ids:
            return True
        item = er.async_get(self.hass).async_get(entity_id) if type(entity_id) is str else None
        return item is not None and item.config_entry_id == self.entry_id

    @callback
    def _own_device_event(self, data) -> bool:
        """A device of this entry was created, renamed or removed."""
        device_id = data.get("device_id")
        if device_id in self._device_ids:
            return True
        device = dr.async_get(self.hass).async_get(device_id) if type(device_id) is str else None
        # A device belongs to one config entry (Core 2026.10, the minimum): DeviceEntry.config_entries is a deprecated
        # shim there; every read of it logs a deprecation warning, and it stops working in Core 2027.10.
        return device is not None and device.config_entry_id == self.entry_id

    @staticmethod
    @callback
    def _language_or_units(data) -> bool:
        """The language or the unit system changed (an update without data: Home Assistant starts)."""
        return not data or "language" in data or "unit_system" in data

    async def async_stop(self) -> None:
        """Remove the panel when the integration is unloaded or disabled."""
        for unsubscribe in self._unsubscribe:
            unsubscribe()
        self._unsubscribe = []
        if self._registry_timer is not None:
            self._registry_timer()
            self._registry_timer = None
        self._unwatch_hub()
        if self._refresh_task is not None:
            self._refresh_task.cancel()
            try:
                await self._refresh_task
            except asyncio.CancelledError:
                pass
            self._refresh_task = None
        if self._store is not None:
            frontend.async_remove_panel(self.hass, self.path)
            self.hass.data[LOVELACE_DATA].dashboards.pop(self.path, None)
            self._store = None

    @callback
    def set_rooms(self, keys: set[str]) -> None:
        """Keep only rooms present in the latest MQTT status."""
        if keys != self._rooms:
            self._rooms = keys.copy()
            self._schedule_refresh()

    @callback
    def _registry_updated(self, event) -> None:
        """Follow entity creation, entity ID and device name changes, and the HA language.

        Once per burst: the rebuild follows REGISTRY_SETTLE_SECONDS after the first event (a start
        creates this entry's entities one by one, R4-11).
        """
        self._watch_hub()
        if self._registry_timer is None and self._store is not None:
            self._registry_timer = async_call_later(self.hass, REGISTRY_SETTLE_SECONDS, self._registry_settled)

    @callback
    def _registry_settled(self, _now=None) -> None:
        self._registry_timer = None
        self._schedule_refresh()

    def _heating_hub(self):
        return self.hass.data.get(DOMAIN, {}).get(self.entry_id, {}).get("heating_hub")

    @callback
    def _watch_hub(self) -> None:
        """Rebuild when the E32 reports other rooms, room names or thermostats (not on every reading)."""
        hub = self._heating_hub()
        if hub is self._hub or self._store is None:
            return
        self._unwatch_hub()
        if hub is not None:
            self._hub = hub
            self._hub_unsubscribe = hub.add_listener(self._hub_changed)

    @callback
    def _unwatch_hub(self) -> None:
        if self._hub is not None:
            self._hub_unsubscribe()
        self._hub = None

    @callback
    def _hub_changed(self) -> None:
        # The boiler profile (which fields this boiler has) decides the boiler tiles: rebuild when it
        # changes; the hub reports often enough to notice it within seconds.
        from .v1_boiler_fields import boiler_cache
        cache = boiler_cache(self.hass, self.entry_id)
        signature = (self._signature(self._hub), getattr(cache, "profile_sequence", None))
        if signature != self._hub_signature:
            self._hub_signature = signature
            self._schedule_refresh()

    @staticmethod
    def _signature(hub):
        if hub is None or not hub.fresh:
            return None
        from .heating_link import dhw_tank, learned_inputs
        plan = hub.plan.plan if hub.plan is not None else None
        # The E32 counts every plan save in its revision: no need to compare the whole plan (R4-11).
        # A room's state too: switched on or off, it moves into or out of the Overview's house card (rc.5).
        return (hub.status.get("mode"),
                tuple((key, room.get("name"), room.get("source"), room.get("state"))
                      for key, room in hub.rooms.items()),
                tuple((key, sensor.get("name")) for key, sensor in hub.ble.items()),
                plan.get("revision") if plan else None,
                # The outdoor temperature the E32 uses (the House row shows the same one, rc7).
                learned_inputs(getattr(hub, "learned_header", None)).get("outdoor"),
                # The rooms with radiator valves (1.4.3: the room card names their sensor; the card reads the rest live).
                tuple(sorted(getattr(hub, "valves", None) or {})),
                # A storage tank or not (1.4.2): the gas split chart and the hot-water words; only "tank or not", never
                # the method, which can change after every E32 start (R142 G3).
                dhw_tank(hub))

    @callback
    def _schedule_refresh(self) -> None:
        if self._store is None:
            return
        self._dirty = True
        if self._refresh_task is None or self._refresh_task.done():
            self._refresh_task = self.hass.async_create_task(
                self._refresh(), f"Refresh OpenThermostat dashboard {self.path}"
            )

    async def _refresh(self) -> None:
        while self._dirty:
            self._dirty = False
            await asyncio.sleep(0)
            config = self._dashboard_config()
            if config != await self._store.async_load(False):
                await self._store.async_save(config)

    # -- registry lookups -------------------------------------------------

    def _entries(self):
        registry = er.async_get(self.hass)
        return [item for item in er.async_entries_for_config_entry(registry, self.entry_id)
                if item.platform == DOMAIN and item.disabled_by is None]

    def _device_name(self, identifier, fallback):
        device = dr.async_get(self.hass).async_get_device_by_identifier(identifier, self.entry_id)
        if device is None:
            return fallback
        return device.name_by_user or device.name or fallback

    def _e32_rooms(self, entries):
        """{room id: {key: entity id}} in the order the E32 reports its rooms.

        While the telemetry is fresh, a room the E32 no longer reports is left
        out (its entities stay, unavailable, until the user deletes its device).
        """
        head = f"{self.prefix}_e32_room_"
        rooms: dict[str, dict[str, str]] = {}
        for item in entries:
            if not item.unique_id.startswith(head):
                continue
            rest = item.unique_id.removeprefix(head)
            for key in ROOM_KEYS:
                if rest.endswith("_" + key):
                    rooms.setdefault(rest[:-len(key) - 1], {})[key] = item.entity_id
                    break
        hub = self._heating_hub()
        order = list(hub.rooms) if hub is not None else []
        if hub is not None and hub.fresh:
            rooms = {room_id: room for room_id, room in rooms.items() if room_id in hub.rooms}
        return dict(sorted(rooms.items(), key=lambda pair: (
            order.index(pair[0]) if pair[0] in order else len(order), pair[0])))

    def _e32_ble(self, entries):
        head = f"{self.prefix}_e32_ble_"
        sensors: dict[str, dict[str, str]] = {}
        for item in entries:
            if item.unique_id.startswith(head):
                sensor_id, _, metric = item.unique_id.removeprefix(head).rpartition("_")
                if sensor_id and metric in BLE_KEYS:
                    sensors.setdefault(sensor_id, {})[metric] = item.entity_id
        hub = self._heating_hub()
        if hub is not None and hub.fresh:
            sensors = {sensor_id: metrics for sensor_id, metrics in sensors.items() if sensor_id in hub.ble}
        return sensors

    def _room_thermostat(self, room_id):
        """The Home Assistant thermostat whose target the E32 room follows, if it exists."""
        hub = self._heating_hub()
        if hub is None:
            return None
        candidates = []
        plan_room = hub.plan.room(room_id) if hub.plan is not None else None
        if plan_room:
            candidates.append(plan_room.get("setpoint_entity"))
            candidates.extend(source.get("id") for source in plan_room.get("sources", [])
                              if type(source) is dict and source.get("type") == "ha")
        status_room = hub.rooms.get(room_id)
        if status_room:
            candidates.append(status_room.get("source"))
        registry = er.async_get(self.hass)
        for entity_id in candidates:
            if (type(entity_id) is str and entity_id.startswith("climate.")
                    and (self.hass.states.get(entity_id) is not None or registry.async_get(entity_id))):
                return entity_id
        return None

    # -- the dashboard ------------------------------------------------------

    @callback
    def _dashboard_config(self) -> dict:
        t = {**TEXT["en"], **TEXT[dashboard_language(self.hass)]}  # a word a language lacks: the English one
        registry = er.async_get(self.hass)
        entries = self._entries()
        self._entity_ids = {item.entity_id for item in entries}
        self._device_ids = {device.id for device in dr.async_entries_for_config_entry(dr.async_get(self.hass),
                                                                                       self.entry_id)}
        hub_entities = {
            item.unique_id.removeprefix(f"{self.prefix}_hub_"): item.entity_id
            for item in entries if item.unique_id.startswith(f"{self.prefix}_hub_")
        }
        # Registry identities follow user renames; model choice never filters fields.
        native_fields = {
            item.unique_id.removeprefix(f"{self.prefix}_boiler_fields_v1_"): item.entity_id
            for item in entries
            if item.domain == "sensor" and item.unique_id.startswith(f"{self.prefix}_boiler_fields_v1_")
        }
        # No tiles for values this boiler does not have (its boiler profile).
        from .v1_boiler_fields import boiler_field_shown
        native_fields = {name: entity_id for name, entity_id in native_fields.items()
                         if boiler_field_shown(self.hass, self.entry_id, name)}
        entry = self.hass.config_entries.async_get_entry(self.entry_id)
        product = entry is not None and is_product(entry)
        from .room_plan import has_room_plan
        e32_rooms = product and has_room_plan(entry)
        # Older HA room records (zone subentries). With an E32 room plan the
        # rooms are set up in the options flow: no settings view or buttons;
        # only each record's own subview stays, for the link in its
        # reconfigure dialog.
        legacy = [sub for sub in entry.subentries.values() if sub.subentry_type == "zone"] if product else []

        def graph(title, keys, lookup, hours=24):
            entities = [{"entity": lookup[key], "name": name} for key, name in keys if key in lookup]
            return ({"type": "history-graph", "title": title, "hours_to_show": hours, "entities": entities}
                    if entities else None)

        def essential(key):
            _, field, metric = next(item for item in ESSENTIALS if item[0] == key)
            if not boiler_field_shown(self.hass, self.entry_id, field):
                return None  # not on this boiler: no older hub tile either
            return native_fields.get(field) or (hub_entities.get(metric) if metric else None)

        parts = self._heating_sections(t, entries, hub_entities, native_fields, essential, registry, e32_rooms, legacy)
        boiler, raw, thermostat = self._boiler_sections(t, hub_entities, native_fields, graph, essential,
                                                        self._flow_entities(entries).get("source"))
        heating_hub = self._heating_hub()
        from .heating_link import label
        valves = [(self._room_name(room_id, heating_hub, label), room["valve_position"])
                  for room_id, room in self._e32_rooms(entries).items() if room.get("valve_position")]
        diagnostics = self._diagnostics_sections(t, registry, hub_entities, raw, thermostat, valves)

        def view(title, path, sections, columns=4, **more):
            # 1.4.3 (HA-DASHBOARD-ONTWERP-1.4.3 2.1): every tab as wide as the screen, as the Overview: at most four
            # columns, Home Assistant shows as many as fit (four on a monitor, one on a phone).
            # Sections side by side, a short one filling the gap under itself (never half-empty rows inside).
            # No view icon: Home Assistant then shows the view's title in the tab bar ("Overzicht · Ruimtes · ..."),
            # as in the approved sketches; with an icon a tab is only that icon.
            return {"title": title, "path": path, "type": "sections", "max_columns": columns,
                    "dense_section_placement": True, "sections": sections, **more}
        back = "/" + self.path + "/heating"
        comparison = parts["comparison"]
        from .settings import CARD_TYPE as SETTINGS_CARD_TYPE, VIEW_PATH as SETTINGS_PATH
        # 1.4.1: the house banner on top of every view (summer mode), _with_banner.
        house_mode = registry.async_get_entity_id("select", DOMAIN, f"{self.prefix}_house_mode")
        return {
            "views": _with_banner(house_mode, [
                # 1. Overview (rc.5, the owner's sketch): the house card across the whole width, under it Rooms
                # (two columns), Today and House side by side on a wide screen, under each other on a phone.
                *([view(t["overview"], "heating", parts["overview"])] if parts["overview"] else []),
                # 2. Rooms: thermostat, the day, sensors, windows, people and what it learned, per room.
                *([view(t["rooms"], "rooms", parts["rooms"])] if parts["rooms"] else []),
                *([{
                    "title": t["room_settings"],
                    "panel": True,
                    "path": "week",
                    "cards": [{"type": ROOM_CARD_TYPE,
                               "entry_id": self.entry_id, "room_id": sub.data["room_id"]}
                              for sub in legacy[:1]],
                }] if product and not e32_rooms and legacy else []),  # 1.4.2 (P19): never an empty tab
                *[{"title": sub.title, "path": "room-" + sub.data["room_id"],
                   "subview": True, "panel": True,
                   "cards": [{"type": ROOM_CARD_TYPE, "entry_id": self.entry_id,
                              "room_id": sub.data["room_id"]}]}
                  for sub in legacy],
                # (1.4.1: no Week program tab any more: each room's week program is on its screen in Settings,
                # #room/<id>; plan HA-INSTELPANEEL-FASE2 3.8.)
                # 4. Boiler: everything about the boiler in one place.
                view(t["boiler_view"], "boiler", boiler),
                # 5. Learning (1.4.3): what the E32 knows and learned, per room in figures; the takeover check.
                # 1.4.3 (CONTRACT-1.4.3 §1): four columns, the strip and the room cards across the view.
                *([view(t["learning_view"], LEARNED_PATH, parts["learning"])] if parts["learning"] else []),
                # 6. Diagnostics.
                # 1.4.4: fewer than four sections each span two columns (_wide_when_few), so it fills a monitor.
                view(t["diagnostics"], "diagnostics", _wide_when_few(diagnostics)),
                # 7. Settings (1.4, HA-INSTELPANEEL-ONTWERP.nl.md): one panel card, the settings app (settings.py).
                *([{"title": t["settings_view"], "path": SETTINGS_PATH, "panel": True,
                    "cards": [{"type": SETTINGS_CARD_TYPE, "entry_id": self.entry_id,
                               "settings_path": self.settings_path}]}] if product else []),
                # Trial run only: reached from the "E32 compared with your thermostat" link and the
                # "Ready to take over?" tile in the learning view.
                *([view(t["comparison_view"], COMPARISON_PATH, _wide_when_few(comparison), subview=True,
                        back_path=back)] if comparison else []),
            ])
        }

    def _trial_run(self):
        """Whether the E32 runs the trial run (shadow mode), from its live status, never the registry.

        The last reported mode counts while the E32 is silent, so an outage does not drop the
        Comparison subview; nothing reported yet is no trial run. A change of mode rebuilds the
        dashboard (_signature), so this follows the E32 by itself.
        """
        heating_hub = self._heating_hub()
        if heating_hub is not None and heating_hub.fresh:
            self._mode = heating_hub.status.get("mode")
        return self._mode == "shadow"

    def _heating_sections(self, t, entries, hub, fields, essential, registry, e32_rooms, legacy):
        """The sections of the views that come from the E32's heating: {overview, rooms, learning, comparison}.

        Overview: the house card (what the boiler does, today, the problem with its reason while there is one), one
        status card per room, Today and House (home or away, holidays, outside). Rooms: one section per room
        (thermostat, its day, sensors, windows and people, what it learned), then the sensors that feed no single
        room. Learning (1.4.3): what the E32 knows, a learning card per room, today's plan, house and boiler,
        yesterday, what it changed by itself, worth checking, who controls the boiler (the trial run) and the quiet
        settings row. The Boiler view is _boiler_sections.

        The comparison with the thermostat on the boiler bus means something only in the trial run
        and only while such a thermostat is heard: the Comparison subview exists only in the trial
        run (the E32's live mode, _trial_run), and its link and comparison cards show only while the
        agreement has a value (it has none without a thermostat). Once the E32 controls the boiler,
        the comparison sensors are removed (native_entity_cleanup.note_heating_status).
        """
        request = hub.get("heat_request")
        # The house mode (beta.23, e32_house.py): automatic, at home, away, holiday, switched right here.
        house_mode = registry.async_get_entity_id("select", DOMAIN, f"{self.prefix}_house_mode")
        e32_room_entities = self._e32_rooms(entries)
        flow = self._flow_entities(entries)
        problem = hub.get("heating_problem")
        trial = self._trial_run()
        sub_path = "/" + self.path + "/" + COMPARISON_PATH
        from .heating_link import label
        heating_hub = self._heating_hub()

        # -- Overview ------------------------------------------------------------------------------
        on = [{"condition": "state", "entity": problem, "state": "on"}] if problem else None
        # rc.5 (P11): the house card (frontend/house-card.js) heads the House section: what the boiler does now (a
        # problem first, with its reason, a tap to Repairs and all reasons inside), today in figures and the day so
        # far, read from Home Assistant alone. It replaces the rooms-that-want-heat card and the problem tile with its
        # reasons, which stay as before only without a heat request and boiler activity (then there is no card). A
        # house with exactly one room switched on shows that room in the card (its Reason sensor) as a summary; as the
        # owner's sketch, every room keeps its status card under Rooms, the rooms that are on first (rc.5, P18).
        # _signature follows the rooms' state, so switching a room on or off rebuilds the dashboard.
        from .room_overview import HOUSE_CARD_TYPE
        activity = hub.get("boiler_activity")
        reported = heating_hub.rooms if heating_hub is not None else {}
        switched_on = [room_id for room_id in e32_room_entities
                       if (reported.get(room_id) or {}).get("state") != "inactive"]
        inline = (switched_on[0] if (request or activity) and len(switched_on) == 1
                  and e32_room_entities[switched_on[0]].get("reason") else None)
        reads = {"request": request, "activity": activity, "heating": fields.get("heating_active"),
                 "flow": essential("flow"), "hot_water": fields.get("dhw_active"), "taps": hub.get("dhw_taps_today"),
                 "gas": [hub[key] for key in ("heating_gas", "hot_water_gas") if key in hub],
                 "starts": hub.get("daily_burner_starts"), "mode": house_mode, "problem": problem,
                 "rooms": [{"entity": e32_room_entities[inline]["reason"],
                            "name": self._room_name(inline, heating_hub, label)}] if inline else None,
                 # HA 1.0.0rc7, the rest of the desktop sketch: the band's burner power and display code ("burner 37 %
                 # · code -H"), the hot water's temperature and the burner starts in the last hour (the Boiler tab's).
                 "modulation": essential("modulation"), "code": essential("code"), "dhw": essential("dhw"),
                 "starts_hour": hub.get("burner_starts_last_hour")}
        # Across the whole view on a wide screen too, as the sketch (the section spans every column).
        house_card = (_full({"type": HOUSE_CARD_TYPE, **{key: value for key, value in reads.items() if value}})
                      if request or activity else None)
        before = () if house_card else (
            # Which rooms want heat and the boiler request: one card whose text follows the E32.
            _wanting_card(t, request),
            # A problem names itself ("Waiting for your confirmation"), and a tap leads to the fix in Repairs.
            _wide(_tile(problem, t["problem"], visibility=on, state_content=["reason"],
                        tap_action={"action": "navigate", "navigation_path": "/config/repairs"})),
            {"type": "markdown", "visibility": on, "content": (
                "<details><summary>" + t["problem_more"] + "</summary>\n\n{% for reason in state_attr("
                + json.dumps(problem) + ", 'reasons') or [] %}- {{ reason }}\n{% endfor %}\n\n</details>")}
            if problem else None)
        # rc.5 (P18, the owner's sketch): the house card alone across the top, without a heading (it says what it is),
        # or, without a card, what it replaces; then Rooms (two columns), Today and House (one each): beside each other
        # on a wide screen (1.4.3: four columns), in that order on a phone. The top spans every column, so its cards
        # are "full" (Home Assistant gives such a section 12 grid columns per view column: 12 would be a part).
        top = _section(house_card, *(_full(card) for card in before))
        top = _span(_shown_while_one_is(top, top["cards"]), 4, cards=None)
        from .e32_comfort import room_contacts, room_persons
        entry = self.hass.config_entries.async_get_entry(self.entry_id)
        ble = self._e32_ble(entries)
        in_room = {}  # Bluetooth sensor -> the one room it feeds (None: several rooms)
        for room_id in e32_room_entities:
            plan_room = self._plan_room(heating_hub, room_id)
            for source in (plan_room or {}).get("sources", []):
                if type(source) is dict and source.get("type") == "ble" and source.get("id") in ble:
                    in_room[source["id"]] = None if source["id"] in in_room else room_id
        names = {room_id: self._room_name(room_id, heating_hub, label) for room_id in e32_room_entities}
        room_cards = []
        # rc.5 (P18, the owner's sketch): every room under Rooms, also the one the house card shows (the card is its
        # summary; the status card its line, its chips and the tap to its history); the rooms that are on first.
        for room_id in [*switched_on, *(room_id for room_id in e32_room_entities if room_id not in switched_on)]:
            room = e32_room_entities[room_id]
            if room.get("reason"):
                # rc.5 (P18): its chips "Smart warm-up on" (the switch) and at home, away or on holiday (the house mode).
                # 1.4: the card's "Settings" button opens this room in the settings view.
                # 1.4.1: its heating type (radiator or floor heating, the room's settings) as the card's icon.
                emitter = (self._plan_room(heating_hub, room_id) or {}).get("emitter")
                room_cards.append({"type": ROOM_STATUS_CARD_TYPE, "entity": room["reason"], "name": names[room_id],
                                   **{key: value for key, value in (("smart", flow.get("apply_learned")),
                                                                    ("mode", house_mode)) if value},
                                   **({"emitter": emitter} if emitter in ("radiator", "floor") else {}),
                                   "room_id": room_id, "settings_path": self.settings_path})
            else:  # a registry without the Reason sensor (older integration): the temperature at least
                room_cards.append(_wide(_tile(room.get("temperature") or room.get("setpoint"), names[room_id],
                                              "mdi:home-thermometer-outline")))
        # Today: when each room that is on warms up next, and what weather compensation asks now.
        today = _today_section(t, [(names[room_id], room["heating_start"], room.get("state"), room.get("warm_on_time"),
                                    room.get("reason"))
                                   for room_id, room in e32_room_entities.items() if room.get("heating_start")],
                               flow.get("curve"), flow.get("apply_learned"), request)
        # House: home or away, the holiday planner and the outdoor temperature: the one the E32 uses (its learner's
        # input, as Today and the curve: rc7), else the one set under Energy and outdoor temperature, else the
        # boiler's own; with the next holiday under it while one is planned (rc.4) and where to plan one.
        # 1.4.1 (DASHBOARD-FINISH): the house card above shows the house mode large with its meaning and the next
        # holiday (or "Until ..." while one runs); with that card the House section repeats neither (no "Home or
        # away" row, no next-holiday line) and keeps what the card does not show: Holiday with Plan, Outside, the hint.
        from .energy_input import CONF_OUTDOOR, energy_options
        outdoor = energy_options(entry).get(CONF_OUTDOOR) if entry is not None else None
        boiler_outdoor = fields.get("outdoor_temperature") or hub.get("outdoor_temperature")
        from .heating_link import learned_inputs
        used = learned_inputs(heating_hub.learned_header).get("outdoor") if heating_hub is not None else None
        if (type(outdoor) is not str or outdoor.split(".")[0] not in ("sensor", "weather")
                or (used == "boiler" and boiler_outdoor)):
            outdoor = boiler_outdoor
        on_card = house_card is not None and bool(house_mode)  # the house card shows the mode and the next holiday
        # 1.4.2 (plan 3.5): "Batteries low" as one line, only while a battery is below the limit; a tap opens the
        # Batteries list (Settings tab), else the entity. Its own name (the entity's translation), so no dashboard text.
        batteries = hub.get("batteries_low")
        batteries_line = _wide(_tile(batteries, icon="mdi:battery-alert-variant-outline", color="red",
                                     visibility=[{"condition": "numeric_state", "entity": batteries, "above": 0}],
                                     tap_action={"action": "navigate", "navigation_path": self._settings_link(
                                         e32_rooms, "devices/batteries")} if e32_rooms else None))
        house = _section(_heading(t["house"], ICONS["house"]),  # one icon per concept (dashboard-spec §1)
                         _house_rows(t, house_mode, outdoor, self._settings_link(e32_rooms, "house/mode"),
                                     mode=not on_card),
                         None if on_card else _holiday_card(t, house_mode),
                         # 1.4.2 (P6): on the E32 room plan the Plan row opens Settings → House → House mode and
                         # holiday itself, so no note repeats where it leads; the older route's Plan row opens the
                         # integration's page, and its note still says where to go from there.
                         _note(t, t["holiday_hint"], _known(house_mode))
                         if house_mode and not e32_rooms else None, batteries_line)
        house = _shown_while_one_is(house, house["cards"][1:])
        # 1.4.3 (owner decision 10.2): the rooms two side by side where the section is wide (two view columns, each
        # card one: 12 of its 24 grid columns), one under the other on a phone; a single room keeps one column.
        for card in room_cards:
            card["grid_options"] = {**card.get("grid_options", {}), "columns": 12}
        rooms_section = _section(_heading(t["rooms"], "mdi:thermostat"), *room_cards) if any(room_cards) else None
        if rooms_section is not None and len(room_cards) > 1:
            _span(rooms_section, 2, cards=None)
        if rooms_section is not None and today and house:
            # Two rows high: where Home Assistant shows three columns (about 1400 to 1750 px), Today and House stand on
            # top of each other beside the rooms instead of House under them; four columns side by side, two (1280 px
            # with the sidebar open) under the rooms, and a phone in order, are the same as without it.
            rooms_section["row_span"] = 2
        overview = [section for section in (top, rooms_section, today, house) if section]

        # -- Rooms ---------------------------------------------------------------------------------
        # 1.4.3 (HA-DASHBOARD-ONTWERP-1.4.3 §3, CONTRACT-1.4.3 §1-2): one section across the view with one room card
        # per room (frontend/room-card.js, a view column each: four beside each other on a monitor, one on a phone),
        # then the Bluetooth sensors that feed no room. What the E32 learns per room is on the Learning view.
        learned_overview = hub.get("learned_overview")
        room_view_cards = [self._room_card(t, room_id, room, heating_hub, names[room_id], ble, in_room, entry,
                                           (room_contacts, room_persons), flow.get("apply_learned"), house_mode,
                                           to_settings=e32_rooms)
                           for room_id, room in e32_room_entities.items()]
        rooms = []
        if any(room_view_cards):
            # Across every column; each room card keeps its one view column (12 grid columns).
            rooms.append(_span(_section(_heading(t["rooms"], "mdi:thermostat"), *room_view_cards), 4, cards=None))
        # Older HA rooms (one climate per MQTT room) and their settings.
        legacy_cards = []
        for key in sorted(self._rooms):
            entity_id = registry.async_get_entity_id("climate", DOMAIN, f"{self.prefix}_room_{key}_climate")
            if entity_id is not None:
                legacy_cards.append({"type": "thermostat", "entity": entity_id, "show_current_as_primary": False})
        if not e32_rooms:
            legacy_cards.extend({"type": "button", "name": t["settings"].format(room=sub.title), "icon": "mdi:cog",
                                 "tap_action": {"action": "navigate",
                                                "navigation_path": "/" + self.path + "/room-" + sub.data["room_id"]}}
                                for sub in legacy)
        if legacy_cards:
            rooms.append(_section(_heading(t["legacy_rooms"], "mdi:thermostat"), *legacy_cards))
        # 1.4.3 (design §3.2, last paragraph): each Bluetooth sensor that feeds no room as a tile with its temperature,
        # after one line "Link to a room"; both open Settings → Devices → Bluetooth sensors.
        to_ble = self._settings_link(e32_rooms, "devices/bluetooth")
        loose = [_tile(metrics.get("temperature") or next(iter(metrics.values())),
                       self._device_name((DOMAIN, f"{self.prefix}_e32_ble_{sensor_id}"), sensor_id), "mdi:bluetooth",
                       tap_action={"action": "navigate", "navigation_path": to_ble})
                 for sensor_id, metrics in sorted(ble.items()) if not in_room.get(sensor_id) and metrics]
        if loose:
            # One view column (a few sensors, each tile across it): never a half-empty row beside the room cards.
            rooms.append(_section(_heading(t["bluetooth"], "mdi:bluetooth"),
                                  _link(t["bluetooth_link"], "mdi:link-variant", to_ble), *(_wide(card) for card in loose)))

        # -- Learning (1.4.3, design HA-DASHBOARD-ONTWERP-1.4.3 chapter 4, CONTRACT-1.4.3 §1) --------------------------
        # Everything the E32 learns on one tab, per room in figures: what the E32 knows (the ring and the learning path,
        # across the view), a learning card per room (side by side, one view column each), today's plan with its one
        # confirmation, house and boiler (the curve and what it learned from the boiler, as tiles), yesterday (the four
        # figures, what stood out, missed comfort), what it changed by itself and what is worth checking, two columns
        # each; who controls the boiler (the trial run) and the quiet settings row across the view.
        heating_gas = hub.get("heating_gas")
        gas_state = self.hass.states.get(heating_gas) if heating_gas and self.hass is not None else None
        lead = next((room_id for room_id in [*switched_on, *e32_room_entities]
                     if e32_room_entities[room_id].get("warm_on_time")), None)
        yesterday = _yesterday_figures(
            t, {room_id: {key: room[key] for key in ("warm_on_time", "overshoot") if room.get(key)}
                for room_id, room in e32_room_entities.items() if room.get("warm_on_time") or room.get("overshoot")},
            names, {key: hub[key] for key in SCOREBOARD_HOUSE if key in hub}, hub.get("daily_summary"),
            hub.get("daily_missed_comfort"), gas_state.attributes.get("unit_of_measurement") if gas_state else None,
            lead, gas_state is not None and gas_state.attributes.get("estimate") is False, learned=learned_overview)
        per_room = _learning_rooms_section(t, self.entry_id, learned_overview, names,
                                           [(room_id, e32_room_entities[room_id]) for room_id in
                                            [*switched_on, *(r for r in e32_room_entities if r not in switched_on)]])
        learning = [section for section in (
            _knowledge_section(t, hub.get("knowledge")), per_room,
            _plan_section(t, hub.get("heating_plan"), registry.async_get_entity_id(
                "button", DOMAIN, f"{self.prefix}_hub_plan_confirm")),
            _curve_section(t, flow.get("curve"), request, learned_overview, hub.get("boiler_response"),
                           flow.get("apply_learned")),
            yesterday,
            _changes_section(t, learned_overview, self._settings_link(e32_rooms, "heating/care"), e32_rooms),
            # 1.4.2 (HC-05): the advice that was a Repairs item (hidden while there is none).
            _worth_checking_section(t, problem)) if section]
        for section in learning:  # CONTRACT-1.4.3 §1: the strip and the rooms across the view, the rest two columns
            if "column_span" not in section:
                _span(section, 2)
        # The comparison entities exist only once the E32 saw a thermostat to compare with; outside
        # the trial run a record left behind leads nowhere.
        agreement = hub.get("shadow_agreement_today") if trial else None
        readiness = hub.get("takeover_readiness")  # E32 1.0: ready to take over? (shadow mode only)
        # The Comparison subview: the readiness check and the comparison, in the trial run only.
        subview = trial and bool(readiness or agreement)
        control = _section(
            _heading(t["who_controls"], ICONS["boiler"]),
            self._explain_card(t, request) if request or e32_room_entities else None,
            # Short cycling is information, not a fault: the E32 deals with it by itself.
            self._cycling_card(t, hub.get("burner_short_cycling"), request),
            # Ready to take over? Leads to the Comparison subview, which opens with the check.
            # The whole width: its state ("Waiting for more data") was cut short on a phone.
            _wide(_tile(readiness, t["readiness"], "mdi:clipboard-check-outline",
                        visibility=_known(readiness, ("not_applicable",)),
                        tap_action={"action": "navigate", "navigation_path": sub_path} if subview else None)),
            # A bare percentage meant nothing here: a link to the comparison, which explains it; only
            # while a thermostat is heard to compare with (the agreement has a value).
            _link(t["compare_link"], "mdi:compare-horizontal", sub_path, _known(agreement)) if agreement else None)
        if len(control["cards"]) > 1 and (trial or request):
            if all(card.get("visibility") for card in control["cards"][1:]):
                # No sentence on who controls it (no heat request and no rooms): shown while one of its cards is.
                control["visibility"] = [{"condition": "or", "conditions": [
                    {"condition": "and", "conditions": card["visibility"]} for card in control["cards"][1:]]}]
            if not trial:
                # 1.4.3 (design 4.2 item 7): only in the trial run, or while the takeover waits for its confirmation
                # (the E32 in active mode, not yet driving: the explain card says what to do).
                control["visibility"] = [{"condition": "state", "entity": request, "attribute": "control",
                                          "state": "awaiting_confirmation"}]
            _span(control, 4)
            learning.append(control)
        # The quiet settings row at the bottom: Smart warm-up, weather compensation and the comfort style in one line,
        # and where to change them (the switches are under Settings → Heating and boiler, not here).
        settings_row = _settings_section(t, flow, self._settings_link(e32_rooms, "heating/flow"), e32_rooms)
        if settings_row:
            learning.append(settings_row)
        # A lone wide tile (Ready to take over?, Let the E32 plan the heating) across its section: its state ("Waiting
        # for more data") was cut short in one column.
        for card in (card for section in learning for card in section["cards"]):
            if card["type"] == "tile" and (card.get("grid_options") or {}).get("columns") == 12:
                card["grid_options"] = {"columns": "full"}

        # -- Comparison subview (trial run only): the readiness check and the E32 next to the thermostat --
        comparison = []
        if readiness and subview:
            hidden = _known(readiness, ("not_applicable",))
            comparison.append(_section(_heading(t["readiness"], "mdi:clipboard-check-outline", visibility=hidden),
                                       _readiness_card(t, readiness)))
        if agreement:
            compared = []
            compare_entities = [{"entity": entity_id, "name": name} for entity_id, name in (
                (request, t["e32_request"]),
                (fields.get("thermostat_requested_flow_temperature"), t["thermostat_request"]),
                (essential("flow"), t["flow"])) if entity_id]
            heating_time = [hub[key] for key in ("shadow_e32_heating_time_today", "shadow_tado_heating_time_today")
                            if key in hub]
            compare = _section(
                _heading(t["compare"], "mdi:compare-horizontal"),
                # The whole width, so the E32 and thermostat tiles below stand side by side in pairs.
                _wide(_tile(agreement, t["agreement"], "mdi:compare-horizontal", color="teal")),
                # Each pair under a line that says what it counts, so a half tile at 390 px needs only "E32" or
                # "Thermostat" ("Heating time thermostat" was cut there in every language).
                *_compared(t, t["compare_heating_time"], "mdi:timer-outline",
                           hub.get("shadow_e32_heating_time_today"), hub.get("shadow_tado_heating_time_today")),
                *_compared(t, t["compare_starts"], "mdi:counter",
                           hub.get("shadow_e32_starts_today"), hub.get("shadow_tado_starts_today")),
                {"type": "history-graph", "hours_to_show": 24, "entities": compare_entities}
                if compare_entities else None,
            )
            if len(compare["cards"]) > 1:
                compared.append(compare)
            names = {"shadow_e32_heating_time_today": t["e32"], "shadow_tado_heating_time_today": t["thermostat"]}
            if heating_time:
                compared.append(_section(
                    _heading(t["heating_per_day"], "mdi:chart-bar"),
                    {"type": "statistics-graph", "entities": [
                        {"entity": hub[key], "name": name} for key, name in names.items() if key in hub],
                     "stat_types": ["max"], "period": "day", "days_to_show": 7, "chart_type": "bar"}))
            # Only while a thermostat is heard to compare with: no "Unavailable" tiles without one.
            for card in (card for section in compared for card in section["cards"]):
                card.setdefault("visibility", _known(agreement))
            comparison.extend(compared)
        return {"overview": overview, "rooms": rooms, "learning": learning, "comparison": comparison if subview else []}

    @staticmethod
    def _explain_card(t, request):
        """One sentence on who controls the boiler (the rest behind "More"), from the heat request's mode."""
        if not request:
            return _note(t, t["how"])
        quoted = json.dumps(request)
        branches = (("{% if mode == 'active' and state_attr(" + quoted + ", 'control') == 'awaiting_confirmation' %}",
                     t["next"]),
                    ("{% elif mode == 'active' %}", t["active"]), ("{% elif mode == 'shadow' %}", t["shadow"]))
        head = ("".join(condition + _split(text)[0] for condition, text in branches)
                + "{% else %}" + t["how"] + "{% endif %}")
        rest = "".join(condition + _split(text)[1] for condition, text in branches) + "{% endif %}"
        return {"type": "markdown", "content": (
            "{% set mode = state_attr(" + quoted + ", 'mode') %}" + head
            + "\n\n<details><summary>" + t["more"] + "</summary>\n\n" + rest + " " + t["how"] + "\n\n</details>")}

    @staticmethod
    def _cycling_card(t, entity_id, request=None):
        """Short cycling as information (the E32 lengthens the burner's rest step by step), never as a fault. In the
        trial run (the heat request's mode ``shadow``) the E32 sends nothing yet: the thermostat in charge cycles it."""
        if not entity_id:
            return None
        quoted = json.dumps(entity_id)
        info = t["cycling_info"]
        if request:
            info = ("{% if is_state_attr(" + json.dumps(request) + ", 'mode', 'shadow') %}" + t["cycling_info_shadow"]
                    + "{% else %}" + info + "{% endif %}")
        return {"type": "markdown", "visibility": _known(entity_id), "content": (
            "{% if is_state(" + quoted + ", 'on') %}<ha-icon icon=\"mdi:sync\"></ha-icon> **" + t["short_cycling"]
            + "**\n\n" + info + "{% else %}<ha-icon icon=\"mdi:check-circle-outline\"></ha-icon> "
            + t["cycling_ok"] + "{% endif %}")}

    @staticmethod
    def _plan_room(heating_hub, room_id):
        plan = getattr(heating_hub, "plan", None) if heating_hub is not None else None
        return plan.room(room_id) if plan is not None else None

    def _room_name(self, room_id, heating_hub, label):
        reported = heating_hub.rooms.get(room_id) if heating_hub is not None else None
        return self._device_name((DOMAIN, f"{self.prefix}_e32_room_{room_id}"),
                                 label(reported) if reported else room_id)

    def _settings_link(self, e32_rooms, route):
        """Where a dashboard link to a setting leads: the Settings tab's own screen (1.4, settings.py; ``route`` after
        the #) for an installation on the E32 room plan, where Configure is short (product_flow.settings_page); else
        Configure itself (the integration's page)."""
        if e32_rooms:
            return f"{self.settings_path}#{route}"
        return "/config/integrations/integration/" + DOMAIN

    def _room_card(self, t, room_id, room, heating_hub, name, ble, in_room, entry, comfort, smart=None, house_mode=None,
                   to_settings=False):
        """One E32 room as its room card (1.4.3, frontend/room-card.js, CONTRACT-1.4.3 §2): the entities the card
        reads, by role. Every key the room does not have is left out (the card then has no tile or block for it).

        The thermostat is the room's own (E32RoomClimate), else the Home Assistant thermostat it follows; the setting
        device is the plan's setpoint entity; the sources are the room's other Home Assistant entities that measure
        it; the sensor is the one Bluetooth sensor that feeds this room alone. An Off room without any working source
        carries ``no_source`` (where to choose one and where to remove the room: Repairs when it has an item for it,
        else the room's screen in the Settings tab), which the card says in one line with two buttons.
        """
        from .device_battery import limit_pct
        from .room_overview import ROOM_V2_CARD_TYPE
        room_contacts, room_persons = comfort
        sensor = next((metrics for sensor_id, metrics in sorted(ble.items()) if in_room.get(sensor_id) == room_id), {})
        plan_room = self._plan_room(heating_hub, room_id) or {}
        climate = room.get("thermostat") or self._room_thermostat(room_id)
        setting = plan_room.get("setpoint_entity")
        setting = setting if type(setting) is str and "." in setting else None
        sources = [source["id"] for source in plan_room.get("sources", [])
                   if type(source) is dict and source.get("type") == "ha" and type(source.get("id")) is str
                   and not source["id"].startswith("climate.") and source["id"] != setting]
        emitter = plan_room.get("emitter")
        card = {"type": ROOM_V2_CARD_TYPE, "entry_id": self.entry_id, "room_id": room_id, "name": name,
                "reason": room.get("reason"), "climate": climate, "temperature": room.get("temperature"),
                "setpoint": room.get("setpoint"), "heating_start": room.get("heating_start"), "state": room.get("state"),
                # On Heat along only the stepper sets the room's temperature without a week program (the number the
                # room screen writes too: room_plan.RoomFallbackSetpoint, a user's choice, never a routine write).
                "fallback": room.get("fallback_setpoint"),
                "valves": room.get("valve_position"), "valve_battery": room.get("valve_battery"),
                "valve_problem": room.get("valve_problem"),
                "sensor": {key: sensor[key] for key in BLE_KEYS if sensor.get(key)} or None,
                "contacts": list(dict.fromkeys(room_contacts(entry, room_id))) if entry is not None else [],
                "persons": list(dict.fromkeys(room_persons(entry, room_id))) if entry is not None else [],
                "sources": list(dict.fromkeys(sources)), "setting_device": setting, "pump": None,
                "emitter": emitter if emitter in ("radiator", "floor") else None,
                "settings_path": self.settings_path if to_settings else None,
                "battery_limit": limit_pct(entry), "smart": smart, "mode": house_mode}
        card = {key: value for key, value in card.items() if value not in (None, [], {})}
        if not any(key in card for key in ("reason", "climate", "temperature")):
            return None  # nothing of the room to show (a registry without its entities)
        reported = heating_hub.rooms.get(room_id) if heating_hub is not None else None
        if (type(reported) is dict and reported.get("state") == "inactive"
                and not self._room_has_working_source(room_id, heating_hub)):
            from homeassistant.helpers import issue_registry as ir
            integration = self._settings_link(to_settings, f"room/{room_id}")  # its sources and Remove room
            repair = ir.async_get(self.hass).async_get_issue(DOMAIN, f"e32_room_choose_source_{self.entry_id}_{room_id}")
            card["no_source"] = {"choose": "/config/repairs" if repair else integration, "remove": integration}
        card["grid_options"] = {"columns": 12}
        return card

    def _room_has_working_source(self, room_id, heating_hub):
        """Any source of the room that measures now: a Bluetooth sensor with a reading, or an HA entity with a state."""
        plan_room = self._plan_room(heating_hub, room_id)
        if not plan_room:
            return True  # plan not read yet: no hint
        for source in plan_room.get("sources", []):
            if type(source) is not dict:
                continue
            if source.get("type") == "ble":
                sensor = heating_hub.ble.get(source.get("id")) or {}
                if isinstance(sensor.get("temperature"), (int, float)):
                    return True
            elif type(source.get("id")) is str:
                state = self.hass.states.get(source["id"])
                if state is not None and state.state not in ("unavailable", "unknown"):
                    return True
        return False

    def _flow_entities(self, entries):
        """The heating curve and learning entities on the product device: {key: entity id}."""
        head = f"{self.prefix}_flow_"
        return {item.unique_id.removeprefix(head): item.entity_id for item in entries
                if item.unique_id.startswith(head) and item.unique_id.removeprefix(head) in FLOW_KEYS
                and item.domain != "number"}  # the design flow is a select (never a 0 °C number)

    def _boiler_sections(self, t, hub, fields, graph, essential, flow_source=None):
        """The Boiler view (dashboard-spec §5) and what of the boiler belongs on Diagnostics: (sections, the raw
        boiler fields, the thermostat on the bus).

        In this order: Now (the boiler at a glance: one card, _boiler_now), the advice, Today and this week (the gas
        and the burner), Hot water, What the boiler reports (its values, one titled card per group), the last 24
        hours (1.4.3: after the values, for the four-column placement) and the boiler settings. Every section hides as a whole while nothing in it has a value, so a boiler
        that never reports a value shows neither an "Unknown" nor a heading over nothing. Raw values the E32 does not
        check and the thermostat on the bus go to Diagnostics. flow_source: the "Water temperature set by" sensor.
        """
        from .boiler_fields import INDEX_BY_NAME, quality
        now, advice = _boiler_now(t, hub, fields, essential, flow_source), _advice_section(t, hub.get("heating_advice"))
        # As the owner's sketch on a wide screen: Now across the whole width (its four figures in one row), the advice
        # as a strip under it, then the other sections side by side (1.4.3: four columns on a monitor, HA-DASHBOARD-
        # ONTWERP-1.4.3 2.1): Today and this week across two (its four small figures in one row, its charts two by
        # two), Hot water one, the last 24 hours two (its graphs two by two: a day of water temperatures reads better
        # wide), what the boiler reports one column two rows high (its lists of values: as wide as a list reads
        # well, in the fourth column beside Hot water and the boiler settings) and the boiler settings one. A phone
        # shows one column in this order. A section across n columns has a grid of 12 x n columns (_span).
        for section in (now, advice):
            _span(section, 4)
        # A storage tank has no tapping/keeping-warm split and its own words (1.4.2); _signature follows it.
        from .heating_link import dhw_tank
        tank = dhw_tank(self._heating_hub())
        sections = [now, advice, _span(_energy_section(t, hub, tank), 2, cards="pairs"),
                    _hot_water_section(t, hub, fields, essential, tank)]
        raw = thermostat = None
        if fields:
            # Native cards only. Reported selected flow is NOT a controller request,
            # and burner modulation percentage is NOT measured kW or power factor.
            def order(name):
                # Table order; activity inferred from the state bits (quality 2) last in its group.
                index = INDEX_BY_NAME.get(name)
                return (index is not None and quality(index) == 2, index if index is not None else len(INDEX_BY_NAME),
                        name)
            groups = {}
            for name in sorted(fields, key=order):
                groups.setdefault(boiler_group(name), []).append(fields[name])
            raw, thermostat = groups.pop("raw", None), groups.pop("thermostat", None)
            hidden = {fields[name]: states for name, states in HIDDEN_STATES.items() if name in fields}
            # The last 24 hours: each graph once one of its series has a value, so a series the boiler does not
            # send never hides the others (an empty series draws no line).
            graphs = [card for card in (
                graph(t["flow_graph"], (("reported_selected_flow_temperature", t["flow_selection"]),
                                        ("measured_flow_temperature", t["measured_flow"]),
                                        ("measured_return_temperature", t["measured_return"])), fields),
                graph(t["modulation_graph"], (("reported_burner_modulation", t["modulation_series"]),), fields),
                graph(t["dhw_graph"], (("selected_dhw_temperature", t["dhw_selected"]),
                                       ("measured_dhw_temperature", t["dhw_measured"]),
                                       ("reported_dhw_target", t["dhw_target"])), fields)) if card]
            for card in graphs:
                card["visibility"] = _any_known([item["entity"] for item in card["entities"]])
            last_day = _span(_filled(_section_known([item["entity"] for card in graphs for item in card["entities"]],
                                                    _heading(t["history_24h"], ICONS["history"]), *graphs)), 2,
                             cards="pairs")
            # What the boiler reports: one titled card per group (rows with a value), the first with the one note
            # on what these values are (dashboard-spec §5.6).
            reported = [key for key in REPORTED_GROUPS if groups.get(key)]
            cards = [_known_entities_card(groups[key], hidden, t["group_" + key]) for key in reported]
            if cards:
                cards.insert(1, _note(t, t["boiler_note"], _any_known(groups[reported[0]], hidden)))
            values = _filled(_section_known(
                [entity for key in reported for entity in groups[key]],
                _heading(t["boiler_values"], ICONS["boiler"]), *cards, hidden=hidden))
            if values is not None:
                values["row_span"] = 2  # beside Hot water and the boiler settings, one column (1.4.3)
            # 1.4.3: the values before the last 24 hours, so Home Assistant's dense placement puts them in the column
            # beside Hot water (four columns) or beside Hot water and the settings (two), never alone under the graphs.
            sections += [values, last_day]
            # The boiler's own settings, read only, last, with when the boiler reports them (only when asked).
            settings = groups.get("settings")
            if settings:
                sections.append(_section_known(settings, _heading(t["group_settings"], ICONS["settings"]),
                                               _known_entities_card(settings, hidden),
                                               _note(t, t["settings_note"], _any_known(settings, hidden)), hidden=hidden))
        else:
            # An older integration without the boiler fields: what the hub reports, as graphs.
            legacy = _section(
                _heading(t["boiler"], ICONS["boiler"]),
                _note(t, t["legacy_boiler_note"]),
                graph(t["flow_graph"], (
                    ("boiler_selected_flow_temperature", t["flow_selection"]),
                    ("boiler_current_flow_temperature", t["current_flow"])), hub),
                graph(t["modulation_graph"], (("boiler_burner_power", t["modulation_series"]),), hub),
                graph(t["states_graph"], (
                    ("boiler_heating_active", t["state_heating"]),
                    ("boiler_hot_water_active", t["state_dhw"]),
                    ("boiler_burner_active", t["state_flame"]),
                    ("boiler_pump_active", t["state_pump"])), hub))
            # A heading and a note alone are no section.
            if any(card["type"] not in ("heading", "markdown") for card in legacy["cards"]):
                sections.append(legacy)
        return [section for section in sections if section], raw, thermostat

    def _diagnostics_sections(self, t, registry, hub, raw, thermostat, valves=()):
        """The Diagnostics view (dashboard-spec §8): the E32, the thermostat on the boiler bus, the radiator valves
        (1.4.4, ``valves``: [(room name, Valve position sensor)]), the energy and hot water counters, the raw boiler data,
        the hot water capability and the older rooms."""
        # rc.7: first, in plain words, whether the E32 and Home Assistant reach each other (the rc.5 outage).
        sections = [section for section in (_connection_section(
            t, hub.get("heat_request"), registry.async_get_entity_id("update", DOMAIN, f"{self.prefix}_e32_firmware"),
            registry.async_get_entity_id("sensor", DOMAIN, f"{self.prefix}_hub_e32_errors")),)
            if section]
        device = [hub[metric] for metric in DEVICE_DIAGNOSTIC_METRICS if metric in hub]
        # Rows (not tiles) under each heading: whole names, also on a phone.
        if device:
            sections.append(_section_known(device, _heading(t["e32_device"], "mdi:chip"), _known_entities_card(device)))
        # The thermostat still on the boiler bus (the trial run): what it asks of the boiler, as the boiler hears it.
        if thermostat:
            sections.append(_section_known(thermostat, _heading(t["group_thermostat"], ICONS["thermostat"]),
                                           _known_entities_card(thermostat)))
        if valves:
            sections.append(_valves_section(t, list(valves)))
        # The energy and hot water counters: only isolated definition-v2 IDs, no legacy counter aggregates or
        # backfill. Each shows once it has a value; until then one line says why there is none.
        counters = [hub[key + "_v2"] for key in COUNTER_KEYS if key + "_v2" in hub]
        if counters:
            charts = []
            for title, keys in (
                (t["energy_chart"], ("energy", "energy_heating", "energy_warm_water", "energy_unattributed")),
                (t["volume_chart"], ("warm_water_usage",)),
                (t["flame_chart"], ("burner_observed_time",)),
            ):
                entities = [hub[key + "_v2"] for key in keys if key + "_v2" in hub]
                if entities:
                    charts.append({"type": "statistics-graph", "title": title, "entities": entities,
                                   "days_to_show": 7, "period": "day", "chart_type": "bar",
                                   "stat_types": ["change"], "visibility": _any_known(entities)})
            sections.append(_section(
                _heading(t["estimates"], "mdi:chart-bar"),
                _known_entities_card(counters),
                _note(t, t["estimates_note"], _any_known(counters)),
                _note(t, t["estimates_empty"], _none_known(counters)),
                *charts))
        if raw:
            sections.append(_section_known(raw, _heading(t["raw"], "mdi:wrench-outline"),
                                           _note(t, t["raw_note"], _any_known(raw)), _known_entities_card(raw)))
        # The read-only hot water capability, on a connection that reports one (today's taps and keeping warm are
        # on the Boiler view).
        dhw_id = hub.get("dhw_capabilities")
        if dhw_id:
            quoted = json.dumps(dhw_id)
            note = (t["dhw_note"] + "\n\n" + t["dhw_profile"] + ": {{ state_attr(" + quoted + ", 'profile') or '"
                    + t["unknown"] + "' }}; " + t["dhw_status"] + ": {{ states(" + quoted + ") }}.\n"
                    "{% set fields = state_attr(" + quoted + ", 'fields') or {} %}"
                    "{% for key, field in fields.items() %}{% if field.supported_read %}"
                    "\n- {{ key | replace('_', ' ') }}: {{ field.value if field.value is not none else '"
                    + t["unknown"] + "' }} {{ field.unit or '' }} ({{ field.quality }}){% endif %}{% endfor %}")
            # Its name once, as the heading: the Boiler view has the everyday "Hot water".
            sections.append(_section(_heading(t["dhw_card"], ICONS["hot_water"]),
                                     {"type": "entities", "entities": _rows([dhw_id])},
                                     {"type": "markdown", "content": note}))
        # Older HA rooms: heat model estimates and target / measured history, by room name.
        devices = dr.async_get(self.hass)
        model_cards = []
        for key in sorted(self._rooms):
            device = devices.async_get_device_by_identifier((DOMAIN, f"{self.prefix}_room_{key}"), self.entry_id)
            name = (device.name_by_user or device.name) if device is not None else key
            heating_entities = []
            for platform, suffix in (
                ("binary_sensor", "radiator_heating"),
                ("sensor", "radiator_heating_time"),
                ("sensor", "radiator_estimated_power"),
                ("sensor", "radiator_estimated_energy"),
                ("number", "radiator_power"),
            ):
                definition_suffix = "" if platform == "number" else "_v2"
                entity_id = registry.async_get_entity_id(
                    platform, DOMAIN, f"{self.prefix}_room_{key}_{suffix}{definition_suffix}")
                if entity_id is not None:
                    heating_entities.append(entity_id)
            if heating_entities:
                model_cards.append({"type": "entities", "title": name, "entities": _rows(heating_entities)})
            history = []
            for metric, label in (("temperature", t["room_measured"]), ("temperature_set", t["room_target"])):
                entity_id = registry.async_get_entity_id("sensor", DOMAIN, f"{self.prefix}_room_{key}_{metric}")
                if entity_id:
                    history.append({"entity": entity_id, "name": label})
            if history:
                model_cards.append({"type": "history-graph", "title": t["room_history"].format(room=name),
                                    "hours_to_show": 24, "entities": history})
        if model_cards:
            sections.append(_section(_heading(t["older_rooms"], "mdi:home-thermometer-outline"),
                                     _note(t, t["models_note"]), *model_cards))
        return sections
