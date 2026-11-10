"""Notifications per room and for the house, on the phones of the people of the house (1.1.1).

Configure → Notifications. Nothing is on until the owner switches a room (or the house) on. A room's
messages go to its own recipients (1.4.2: ``notifications.rooms[<room id>].recipients``, chosen on the room's screen
in the settings panel, apart from the persons used for presence): a list is exactly those people, an empty list is
nobody (the message shows in Home Assistant only), and a room that never had a list sends to everyone who has a phone
chosen. Recipients that Home Assistant no longer knows are skipped and never make a message wait; when none of the
chosen people is left, the room falls back to everyone with a phone. The one-time migration add_recipients copies
each room's persons into its list (settings_notifications.add_recipients), so nothing changes at the update.

Room messages:

* ``window``: a window or door open while the room heats: the E32 paused the room after the room's own
  delay (``comfort.window`` ``open``, ``comfort.opening`` window or door), and the room was colder than its
  target before the pause. Once per opening, no "closed again" message. Only for people at home.
* ``cold``: the room stays cold: more than COLD_MARGIN_C below its target for over an hour while the E32
  asks heat for it; a rise of its target (the switch point of its week program) starts the hour again, so it
  is also "still too cold an hour after the program time". Once per episode, only for people at home.
* ``sensor``: the room's temperature sensor has not reported for 30 minutes (the E32's ``stale`` / ``lost``,
  the heating problem sensor's ``room_without_measurement``); and (1.4.2) a device of the room with a battery that
  usually reports and has been silent or unavailable for device_battery.STALE_S (24 h): "probably empty", one
  message per device (key ``sensor:<room id>|<device id>``, values ``device`` (its name) and ``kind``). Home or not.
* ``battery`` (1.4.2: every kind): a device of the room reports a battery below the one limit of device_battery
  (``limit_pct``: the Devices setting ``battery_low_pct``, default 20; ``is_low``: ``pct < limit``; ``recovered``:
  back to normal from ``limit + 5``): a thermometer, a radiator valve, a window or door contact, the setting device, a
  Home Assistant temperature source or a gateway (``kind``, device_battery.KINDS). One message per device (key
  ``battery:<room id>|<device id>``, the row ids of device_battery.collect; values ``device`` (its name), ``kind``,
  ``battery``), and once more after BATTERY_REPEAT_S while it stays low. The devices come from battery_rows. Home or
  not.

House messages (Configure → Notifications → The house), only for the people with the tick "Also messages
about the house" (Configure → Notifications → People and phones, off by default). When the house is switched on
and nobody has the tick, a house message shows in Home Assistant instead, as for someone without a phone.
Two groups: the problems


* ``boiler_fault``: the boiler's display code is a fault (display_codes.FAULTS: the severity of its row in
  the boiler's table; the unconfirmed 0P is never one), for FAULT_SECONDS;
* ``e32_offline``: the E32 has not reported for 10 minutes, and ``e32_back`` when it reports again;
* ``awaiting_confirmation``: the E32 waits for the owner's confirmation before it controls the boiler;
* ``frost``: the E32 heats against frost (its active-control command ``frost_minimum`` or
  ``frost_unconfirmed``), for FROST_SECONDS;
* ``pressure_low``: the heating advice's low water pressure;

and the maintenance:

* ``maintenance``: the boiler's own maintenance message (the boiler field ``maintenance_message``, "H01".."H99";
  "none" is none), for MAINTENANCE_SECONDS, once per code;
* ``update``: a new version is available: the E32 Firmware update entity (``update:``) or the integration's own
  update entity (``update_ha:``, the Marketplace's entity of OpenThermostat) turns on; once per version, never
  again for the same version (kept over restarts);
* ``backup``: the daily backup of the E32 settings keeps failing (the Repairs item ``e32_backup_failing`` is
  raised); once per episode, over when a backup succeeds again;
* ``plan_ready`` (1.1.1 stage B): the E32 is ready to plan the heating and waits for the owner's one
  confirmation (heating_plan.py, its Repairs item); once per readiness: after a demotion the E32 checks again,
  and it is a new message when it is ready again;
* ``season`` (1.4.1): the E32's season hint (season_hint.py): "Five days above 17 °C outside on average. Switch
  summer mode on?" or "It is getting colder. Switch summer mode off?"; once per hint (its ``since_day``), never
  again for the same one, gone once answered or after seven days. On a Home Assistant app with the answers as
  actions (Switch summer mode on / off, Not now); elsewhere the sentence alone. Never a Repairs item. In the
  Maintenance group; an installation whose house messages were on before 1.4.1 gets it ticked once
  (settings_notifications.add_season).

The heating problem sensor's tracker (heating_problem.ProblemTracker) decides the E32 silence, the waiting
confirmation, the low pressure and the silent sensor, with its own hold times, so a hiccup never notifies;
this module runs its own tracker of that class, so a disabled "Heating problem" entity changes nothing here.

Delivery: ``notify.<service>`` per person (the "Phone or app" chosen in Configure), a short title and one
plain sentence in the Home Assistant language (English or Dutch, the catalogue below). One message
per episode; the same message for the same room at most once per COOLDOWN_SECONDS; room messages wait while
it is QUIET_HOURS and go out in the morning if the cause is still there (house messages always). A message
for people at home waits until one of them is home. Every message also fires the event
``open_thermostat_notification`` with the same data, for automations. When someone it is for has no phone
chosen, it shows as a persistent notification in Home Assistant instead (once per episode; it goes away
when the cause is gone). No entities: nothing to go stale on an upgrade.
"""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import callback

from .const import DOMAIN
from .device_battery import DEFAULT_LIMIT, KINDS as BATTERY_KINDS, STALE_S, is_low, recovered
from .heating_problem import ACTIVE_WARNING_SECONDS

_LOGGER = logging.getLogger(__name__)

CONF_NOTIFICATIONS = "notifications"
# Entry options: the house message "season" (1.4.1) was offered or added once (settings_notifications.add_season).
SEASON_ADDED = "notifications_season_added"
EVENT = "open_thermostat_notification"
BATTERY_READ_SECONDS = 60  # the notifier reads the batteries at most this often (they hold 30 minutes anyway)
# Entry options (1.4.2): the rooms' recipients were copied once from their persons (settings_notifications.add_recipients).
RECIPIENTS_ADDED = "notifications_recipients_v1"
ROOM_KINDS = ("window", "cold", "sensor", "battery")
HOUSE_PROBLEMS = ("boiler_fault", "e32_offline", "awaiting_confirmation", "frost", "pressure_low")
HOUSE_MAINTENANCE = ("maintenance", "update", "backup", "plan_ready", "season")
HOUSE_KINDS = HOUSE_PROBLEMS + HOUSE_MAINTENANCE
# Message kinds that follow the tick of another kind (its key's first part -> the tick).
FOLLOWS = {"e32_back": "e32_offline", "update_ha": "update"}
# Only for the people of the room who are home now; the others go to them home or not.
HOME_ONLY = frozenset({"window", "cold"})
# The heating problems (heating_problem.ProblemTracker) that are a message here: problem id -> kind.
PROBLEM_KINDS = {"e32_offline": "e32_offline", "awaiting_confirmation": "awaiting_confirmation",
                 "pressure_low": "pressure_low", "room_without_measurement": "sensor"}
COLD_MARGIN_C = 1.0
COLD_SECONDS = 3600
# The battery limit, its one comparison, the kinds and the 24-hour silence are device_battery's (HA-BATTERIES, HC-04).
BATTERY_SECONDS = 30 * 60
BATTERY_REPEAT_S = 7 * 24 * 3600  # once more while it stays low
FROST_SECONDS = 10 * 60
MAINTENANCE_SECONDS = 10 * 60
FAULT_SECONDS = ACTIVE_WARNING_SECONDS  # the heating problem sensor's hold for a warning of the boiler route
FROST_COMMANDS = ("frost_minimum", "frost_unconfirmed")
COOLDOWN_SECONDS = 2 * 3600
QUIET_HOURS = (23, 7)     # local time, room messages only
CHECK_INTERVAL = timedelta(seconds=60)
# The people a message can go to: persons and device trackers (groups and on/off helpers say "someone").
PERSON_DOMAINS = ("person", "device_tracker")
# Notify services that are not one phone or app.
NOT_A_PHONE = ("send_message", "persistent_notification")
STORE_VERSION = 1

TITLE = {
    "en": {
        "window": "Window open in {room}",
        "door": "Door open in {room}",
        "cold": "{room} stays cold",
        "battery": "Battery low in {room}",
        "silent": "{device} stopped reporting",
        "boiler_fault": "Boiler fault {code}",
        "e32_back": "E32 back",
        "awaiting_confirmation": "The E32 waits for your confirmation",
        "frost": "Frost protection on",
        "maintenance": "Boiler maintenance {code}",
        "update": "New E32 firmware {version}",
        "update_ha": "New OpenThermostat version {version}",
        "backup": "No recent backup of the E32 settings",
        "plan_ready": "The E32 is ready to plan",
        "season": "Summer mode",
    },
    "nl": {
        "window": "Raam open in {room}",
        "door": "Deur open in {room}",
        "cold": "{room} blijft koud",
        "battery": "Batterij bijna leeg in {room}",
        "silent": "{device} meldt niets meer",
        "boiler_fault": "Ketelstoring {code}",
        "e32_back": "E32 weer bereikbaar",
        "awaiting_confirmation": "De E32 wacht op je bevestiging",
        "frost": "Vorstbeveiliging aan",
        "maintenance": "Onderhoud ketel {code}",
        "update": "Nieuwe E32-firmware {version}",
        "update_ha": "Nieuwe versie van OpenThermostat {version}",
        "backup": "Geen recente back-up van de E32-instellingen",
        "plan_ready": "De E32 is klaar om te plannen",
        "season": "Zomerstand",
    },
}
TEXT = {
    "en": {
        "window": "A window in {room} is open, so the heating there is paused. It starts again once the window "
                  "is closed.",
        "door": "A door in {room} is open, so the heating there is paused. It starts again once the door is "
                "closed.",
        "cold": "{room} is at {temperature} °C while you want {target} °C, and has been too cold for over an hour. "
                "Check that the radiators or the floor get warm.",
        # 1.4.2: one sentence per kind of device ({level}: LEVEL, the percentage or "low").
        "battery_thermometer": "The battery of the thermometer {device} in {room} {level}. Replace it soon, so the "
                               "E32 keeps measuring this room.",
        "battery_valve": "The battery of the radiator valve {device} in {room} {level}. Replace it soon, so the valve "
                         "keeps working.",
        "battery_contact": "The battery of the window or door contact {device} in {room} {level}. Replace it soon, so "
                           "the heating keeps pausing while a window or door is open.",
        "battery_setting_device": "The battery of the setting device {device} in {room} {level}. Replace it soon, so "
                                  "you can keep setting the room's temperature with it.",
        "battery_temperature_source": "The battery of the thermometer {device} in {room} {level}. Replace it soon, so "
                                      "the room keeps its temperature measurement.",
        "battery_gateway": "The battery of the gateway {device} in {room} {level}. Replace it soon, so the devices "
                           "behind it keep working.",
        # A device with a battery that usually reports and has been silent for a day (kind sensor).
        "silent_thermometer": "The thermometer {device} in {room} has not reported for 24 hours, so its battery is "
                              "probably empty.",
        "silent_valve": "The radiator valve {device} in {room} has not reported for 24 hours, so its battery is "
                        "probably empty.",
        "silent_contact": "The window or door contact {device} in {room} has not reported for 24 hours, so its "
                          "battery is probably empty.",
        "silent_setting_device": "The setting device {device} in {room} has not reported for 24 hours, so its battery "
                                 "is probably empty.",
        "silent_temperature_source": "The thermometer {device} in {room} has not reported for 24 hours, so its "
                                     "battery is probably empty.",
        "silent_gateway": "The gateway {device} in {room} has not reported for 24 hours, so its battery is probably "
                          "empty.",
        "boiler_fault": "The boiler reports a fault, code {code}: {meaning}",
        "e32_back": "The E32 is reachable again and sends its values to Home Assistant.",
        "frost": "A room has cooled below 8 °C, so the E32 heats a little against frost. Check for an open window "
                 "and that the heating works.",
        "maintenance": "Your boiler asks for maintenance ({code}). Make an appointment with your installer.",
        "update": "A new version of the E32 firmware is available ({version}). Install it from Settings > Updates "
                  "when it suits you; the E32 confirms the takeover again afterwards.",
        "update_ha": "A new version of the OpenThermostat integration is available ({version}). Install it from "
                     "Settings > Updates when it suits you.",
        "backup": "Home Assistant could not back up the E32 settings for more than 3 days (last backup: {last}). "
                  "Check that the E32 is on and its web page opens, and that its password in Home Assistant is "
                  "still right; then press Back up E32 settings now on the E32 device.",
        "plan_ready": "The E32's predictions for {room} have been good for a week. To let it plan the heating, press "
                      "Let the E32 plan the heating under Today's plan on the OpenThermostat dashboard (Learning and "
                      "settings), or leave it as it is.",
        "season_on": "Five days above 17 °C outside on average. Switch summer mode on?",
        "season_off": "It is getting colder. Switch summer mode off?",
    },
    "nl": {
        "window": "In {room} staat een raam open, dus de verwarming daar is gepauzeerd. Die gaat weer aan zodra "
                  "het raam dicht is.",
        "door": "In {room} staat een deur open, dus de verwarming daar is gepauzeerd. Die gaat weer aan zodra de "
                "deur dicht is.",
        "cold": "In {room} is het {temperature} °C, terwijl je {target} °C wilt, en dat al meer dan een uur. Kijk "
                "of de radiatoren of de vloer warm worden.",
        "battery_thermometer": "De batterij van de thermometer {device} in {room} {level}. Vervang hem binnenkort, "
                               "dan blijft de E32 deze ruimte meten.",
        "battery_valve": "De batterij van de radiatorkraan {device} in {room} {level}. Vervang hem binnenkort, dan "
                         "blijft de kraan werken.",
        "battery_contact": "De batterij van het raam- of deurcontact {device} in {room} {level}. Vervang hem "
                           "binnenkort, dan blijft de verwarming pauzeren als er een raam of deur openstaat.",
        "battery_setting_device": "De batterij van het instelapparaat {device} in {room} {level}. Vervang hem "
                                  "binnenkort, dan kun je de temperatuur van de ruimte ermee blijven instellen.",
        "battery_temperature_source": "De batterij van de thermometer {device} in {room} {level}. Vervang hem "
                                      "binnenkort, dan blijft de ruimte haar temperatuur meten.",
        "battery_gateway": "De batterij van de gateway {device} in {room} {level}. Vervang hem binnenkort, dan blijven "
                           "de apparaten erachter werken.",
        "silent_thermometer": "De thermometer {device} in {room} meldt al 24 uur niets, dus de batterij is "
                              "waarschijnlijk leeg.",
        "silent_valve": "De radiatorkraan {device} in {room} meldt al 24 uur niets, dus de batterij is waarschijnlijk "
                        "leeg.",
        "silent_contact": "Het raam- of deurcontact {device} in {room} meldt al 24 uur niets, dus de batterij is "
                          "waarschijnlijk leeg.",
        "silent_setting_device": "Het instelapparaat {device} in {room} meldt al 24 uur niets, dus de batterij is "
                                 "waarschijnlijk leeg.",
        "silent_temperature_source": "De thermometer {device} in {room} meldt al 24 uur niets, dus de batterij is "
                                     "waarschijnlijk leeg.",
        "silent_gateway": "De gateway {device} in {room} meldt al 24 uur niets, dus de batterij is waarschijnlijk "
                          "leeg.",
        "boiler_fault": "De ketel meldt een storing, code {code}: {meaning}",
        "e32_back": "De E32 is weer bereikbaar en stuurt zijn waarden weer naar Home Assistant.",
        "frost": "Een ruimte is afgekoeld tot onder 8 °C, dus de E32 verwarmt een beetje tegen vorst. Kijk of er "
                 "een raam openstaat en of de verwarming werkt.",
        "maintenance": "Je ketel vraagt om onderhoud ({code}). Maak een afspraak met je installateur.",
        "update": "Er is een nieuwe versie van de E32-firmware ({version}). Installeer hem via Instellingen > "
                  "Updates als het je uitkomt; de E32 vraagt daarna opnieuw om je bevestiging van de overname.",
        "update_ha": "Er is een nieuwe versie van de OpenThermostat-integratie ({version}). Installeer hem via "
                     "Instellingen > Updates als het je uitkomt.",
        "backup": "Home Assistant kon al meer dan 3 dagen geen back-up van de E32-instellingen maken (laatste "
                  "back-up: {last}). Controleer of de E32 aan staat en zijn webpagina opent, en of zijn wachtwoord "
                  "in Home Assistant nog klopt; druk daarna op Nu een back-up van de E32 maken op het E32-apparaat.",
        "plan_ready": "De voorspellingen van de E32 voor {room} zijn al een week goed. Wil je dat hij de verwarming "
                      "plant, druk dan op Laat de E32 de verwarming plannen bij Plan voor vandaag op het "
                      "OpenThermostat-dashboard (Leren en instellingen), of laat het zoals het is.",
        "season_on": "Al vijf dagen gemiddeld boven 17 °C buiten. Zomerstand aanzetten?",
        "season_off": "Het wordt kouder. Zomerstand uitzetten?",
    },
}
# The battery's level in a battery sentence: its percentage, or "low" for a device that only says low or not.
LEVEL = {"en": {"pct": "is at {battery} %", "low": "is low"},
         "nl": {"pct": "staat op {battery} %", "low": "is bijna leeg"}}
# The title of a persistent notification (no phone chosen): the product name first, as the insight notes do.
PERSISTENT_TITLE = "OpenThermostat: {title}"


# -- the settings ------------------------------------------------------------------------------------------------


def notification_options(entry):
    """{"phones": {person: notify service}, "house_people": [person], "house": {"on", "kinds"},
    "rooms": {room id: {"on", "kinds", "recipients"?}}}.

    Unknown or invalid values fall back to the default: nothing on, every kind chosen once it is switched on,
    nobody with the tick "Also messages about the house". A room's ``recipients`` (1.4.2) is kept only when it is a
    list (of person and device tracker ids, each once, in the chosen order); absent: never chosen (everyone with a
    phone).
    """
    raw = (getattr(entry, "options", None) or {}).get(CONF_NOTIFICATIONS)
    raw = raw if type(raw) is dict else {}
    phones = raw.get("phones") if type(raw.get("phones")) is dict else {}
    out = {"phones": {person: service for person, service in phones.items()
                      if type(person) is str and person.split(".")[0] in PERSON_DOMAINS
                      and type(service) is str and service and "." not in service},
           "house_people": [], "house": _switch(raw.get("house"), HOUSE_KINDS), "rooms": {}}
    ticked = raw.get("house_people") if type(raw.get("house_people")) is list else []
    out["house_people"] = sorted({p for p in ticked if type(p) is str and p.split(".")[0] in PERSON_DOMAINS})
    rooms = raw.get("rooms") if type(raw.get("rooms")) is dict else {}
    for room_id, value in rooms.items():
        if type(room_id) is str and room_id:
            out["rooms"][room_id] = _switch(value, ROOM_KINDS)
            chosen = value.get("recipients") if type(value) is dict else None
            if type(chosen) is list:
                out["rooms"][room_id]["recipients"] = _people_ids(chosen)
    return out


def _people_ids(values):
    """The person and device tracker ids of a list, each once, in their order."""
    return list(dict.fromkeys(p for p in values if type(p) is str and p.split(".")[0] in PERSON_DOMAINS
                              and "." in p))


def _switch(value, kinds):
    value = value if type(value) is dict else {}
    chosen = value.get("kinds")
    chosen = [k for k in kinds if k in chosen] if type(chosen) is list else list(kinds)
    return {"on": value.get("on") is True, "kinds": chosen}


def anything_on(settings):
    return settings["house"]["on"] or any(room["on"] for room in settings["rooms"].values())


def enabled(settings, kind, room_id):
    """Whether a message of this kind for this room ("" for the house) is switched on."""
    if room_id:
        room = settings["rooms"].get(room_id)
        return room is not None and room["on"] and kind in room["kinds"]
    house = settings["house"]
    return house["on"] and FOLLOWS.get(kind, kind) in house["kinds"]


def with_room(settings, room_id, on, kinds):
    rooms = dict(settings["rooms"])
    before = rooms.get(room_id) or {}
    rooms[room_id] = {"on": bool(on), "kinds": [k for k in ROOM_KINDS if k in kinds],
                      **({"recipients": list(before["recipients"])} if "recipients" in before else {})}
    return {**settings, "rooms": rooms}


def with_recipients(settings, room_id, people):
    """The settings with a room's own recipients (a list; None: never chosen, so everyone with a phone)."""
    rooms = dict(settings["rooms"])
    room = dict(rooms.get(room_id) or {"on": False, "kinds": list(ROOM_KINDS)})
    if people is None:
        room.pop("recipients", None)
    else:
        room["recipients"] = _people_ids(people)
    rooms[room_id] = room
    return {**settings, "rooms": rooms}


def room_choice(settings, room_id):
    """A room's own recipients (a list, maybe empty), or None when it never had a list (everyone with a phone)."""
    room = settings["rooms"].get(room_id) or {}
    return list(room["recipients"]) if type(room.get("recipients")) is list else None


def with_house(settings, on, kinds):
    return {**settings, "house": {"on": bool(on), "kinds": [k for k in HOUSE_KINDS if k in kinds]}}


def with_house_person(settings, person, on):
    """The tick "Also messages about the house" of one person."""
    people = set(settings.get("house_people") or [])
    (people.add if on else people.discard)(person)
    return {**settings, "house_people": sorted(people)}


def with_phone(settings, person, service):
    phones = dict(settings["phones"])
    if service:
        phones[person] = service
    else:
        phones.pop(person, None)
    return {**settings, "phones": phones}


@callback
def save_notifications(hass, entry, settings):
    """Store the settings without a reload; the notifier reads them on its next check. A list chosen from 1.4.1 on
    offers the message ``season``, so it carries the marker SEASON_ADDED: the one-time migration never touches it;
    from 1.4.2 on a room's recipients are its own (RECIPIENTS_ADDED: their one-time copy never runs again)."""
    from .energy_input import ENERGY_ONLY_UPDATE
    if (entry.options or {}).get(CONF_NOTIFICATIONS) == settings:
        return False
    options = {**entry.options, CONF_NOTIFICATIONS: settings, SEASON_ADDED: True, RECIPIENTS_ADDED: True}
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if state is not None:
        state[ENERGY_ONLY_UPDATE] = dict(options)  # the same no-reload marker as the comfort settings
    if not hass.config_entries.async_update_entry(entry, options=options) and state is not None:
        state.pop(ENERGY_ONLY_UPDATE, None)
    if state is not None and (notifier := state.get("notifier")) is not None:
        notifier.evaluate()
    return True


# -- the people ----------------------------------------------------------------------------------------------------


def room_people(entry, room_id):
    """The persons of a room (Configure → Rooms → the room → Persons, its presence) who can get a message: what the
    one-time copy of 1.4.2 puts in the room's own recipients (settings_notifications.add_recipients)."""
    from .e32_comfort import room_persons
    return [p for p in room_persons(entry, room_id) if p.split(".")[0] in PERSON_DOMAINS]


def house_people(hass, entry):
    """Everyone a phone can be chosen for: every person in Home Assistant, the people of the house and rooms, and
    the rooms' recipients Home Assistant still knows."""
    from .e32_comfort import comfort_options, people_of
    settings = notification_options(entry)
    people = {p for p in people_of(comfort_options(entry)) if p.split(".")[0] in PERSON_DOMAINS}
    people.update(state.entity_id for state in hass.states.async_all("person"))
    people.update(settings["phones"])
    for room in settings["rooms"].values():
        people.update(p for p in room.get("recipients") or () if person_found(hass, p))
    return sorted(people)


def person_found(hass, person):
    """Whether Home Assistant still knows a person or device tracker (its state, or its registry record while it
    starts): a removed one is skipped as a recipient (HC-15)."""
    if hass.states.get(person) is not None:
        return True
    from homeassistant.helpers import entity_registry as er
    return er.async_get(hass).async_get(person) is not None


def recipients(kind, room_id, people, phones, home, found=None):
    """(people, notify services, persistent) of one message, or None to wait (nobody of the room is home).

    ``people``: for a room its own recipients (a list: exactly those, empty: nobody, so it shows in Home Assistant
    only; None: never chosen, everyone with a phone); for the house the persons with the tick "Also messages about the
    house" (empty: nobody, so it shows in Home Assistant only); ``phones``: {person: service}; ``home(person)``: True
    while that person is home; ``found(person)``: False for a person Home Assistant no longer knows, who is skipped
    for a room (HC-15: never a message that waits for good; when nobody chosen is left, everyone with a phone gets it).
    ``persistent``: someone it is for has no phone, or nobody is known at all; the message then also shows in Home
    Assistant.
    """
    if not room_id:
        chosen = list(people or ())
    else:
        found = found or (lambda person: True)
        chosen = [p for p in (phones if people is None else people) if found(p)]
        if people and not chosen:  # everyone chosen is gone
            chosen = [p for p in phones if found(p)]
    if kind in HOME_ONLY and chosen:
        chosen = [p for p in chosen if home(p)]
        if not chosen:
            return None
    services = list(dict.fromkeys(phones[p] for p in chosen if p in phones))
    return chosen, services, not chosen or any(p not in phones for p in chosen)


def quiet(local):
    """Between 23:00 and 07:00 local time: room messages wait."""
    start, end = QUIET_HOURS
    return local.hour >= start or local.hour < end


# -- what holds now ------------------------------------------------------------------------------------------------


def _number(value, low=-40, high=85):
    from .heating_link import number
    return number(value, low, high)


def frost_protection(hub):
    """Whether the E32 heats against frost now (its active-control command, ActiveHeatGuard)."""
    active = getattr(hub, "active", None)
    if type(active) is not dict:
        status = getattr(hub, "status", None)
        active = status.get("active") if type(status) is dict else None
    command = active.get("command") if type(active) is dict else None
    return (type(command) is dict and command.get("why") in FROST_COMMANDS
            and (_number(command.get("flow_c"), 1, 90) or 0) > 0)


def boiler_fault(state):
    """{code, meaning, advice} while the display code sensor's state is a fault (display_codes.FAULTS), else None."""
    from .display_codes import FAULTS
    if state is None or state.state in ("unknown", "unavailable", ""):
        return None
    attributes = state.attributes
    if attributes.get("severity") not in FAULTS:
        return None
    return {"code": state.state, "meaning": attributes.get("meaning") or "", "advice": attributes.get("advice") or ""}


def maintenance_code(state):
    """The boiler's maintenance code ("H01".."H99") while its maintenance message sensor shows one, else None."""
    if state is None or type(state.state) is not str:
        return None
    code = state.state.strip().upper()
    return code if len(code) == 3 and code[0] == "H" and code[1:].isdigit() and code != "H00" else None


def new_version(state):
    """The newer version an update entity offers while it is on (a new version available), else None."""
    if state is None or state.state != "on":
        return None
    version = state.attributes.get("latest_version")
    return version if type(version) is str and version.strip() else None


def integration_update(state):
    """Whether an update entity of another integration (the Marketplace) is the one of OpenThermostat itself."""
    title = state.attributes.get("title") or state.attributes.get("friendly_name") or ""
    return type(title) is str and "openthermostat" in title.lower().replace(" ", "")


# -- the batteries (1.4.2) ---------------------------------------------------------------------------------------------


def battery_rows(hass, entry, hub, limit=None):
    """Every battery of the installation: device_battery.collect's rows ({id, name, room, room_name, kind, pct, low,
    reported_at, source, entity_id}; ``low`` with the limit applied). A Home Assistant device whose battery entity is
    unavailable has no ``reported_at``; its ``unavailable_since`` (device_battery.battery_of) is added as
    ``silent_since``, so "unavailable for 24 hours" is a silence too."""
    from .device_battery import battery_of, collect
    rows = collect(hass, entry, hub, limit=limit)
    for row in rows:
        if row.get("source") == "home_assistant" and row.get("reported_at") is None and row.get("entity_id"):
            found = battery_of(hass, row["entity_id"])
            if found and found.get("unavailable_since"):
                row["silent_since"] = found["unavailable_since"]
    return rows


def _when(value):
    """Unix seconds of an ISO time (``reported_at``), or None."""
    from homeassistant.util import dt as dt_util
    moment = dt_util.parse_datetime(value) if type(value) is str else None
    return moment.timestamp() if moment is not None and moment.tzinfo is not None else None


def key_parts(key):
    """(kind, room id, device id or "") of a message key "kind:room id" or "kind:room id|device id"."""
    kind, rest = key.split(":", 1)
    room_id, _, device = rest.partition("|")
    return kind, room_id, device


class NotificationRules:
    """Which messages are due: when each cause started and which messages went out. Pure, so the tests can
    drive it with fake clocks (``now``: monotonic seconds as the hub's clock; ``wall``: unix seconds;
    ``local``: the local time of day)."""

    def __init__(self, sent=None, open_keys=(), episodes=None, announced=None):
        self.since = {}         # key -> since its cause holds (frost, fault, battery, maintenance)
        self.cold = {}          # room id -> (target, since it is too cold for that target)
        self.before = {}        # room id -> its target before a pause (did it want heat?)
        self.low = set()        # battery keys whose device's battery is low (device_battery.is_low / recovered)
        self.sent = dict(sent or {})   # key -> unix time of its last message
        self.open = set(open_keys)     # keys whose message went out and whose cause still holds
        self.last = {key: {} for key in self.open}  # what held at the last check
        self.fresh = True       # the E32's values were current at the last check
        # key -> the episode of its open message (the maintenance code): another one is a new message.
        self.episodes = {k: v for k, v in (episodes or {}).items() if k in self.open}
        # key -> the version whose "new version" message went out: never again for that version.
        self.announced = dict(announced or {})

    def found(self, hub, problems, fault, now, house=None, batteries=None, limit=DEFAULT_LIMIT, wall=None):
        """{key: values} of every cause that holds long enough now; key "kind:room id" ("kind:" for the house,
        "kind:room id|device id" for one device of a room).

        ``house``: what Home Assistant itself knows of the house's maintenance: ``maintenance`` (the boiler's
        maintenance code or None), ``updates`` ({key: version} of the update entities that are on) and
        ``backup`` (the placeholders of the backup Repairs item, or None). ``batteries``: battery_rows (None: no
        battery known), judged against ``limit``; ``wall``: unix seconds now, for a device's silence.

        While the E32 is silent nothing new is known: what held before still holds (so a short outage never
        ends an episode and sends it again afterwards), and the E32's silence itself is added.
        """
        silent = {f"{PROBLEM_KINDS[key]}:": {"problem": (key, values)} for key, values in problems
                  if key == "e32_offline"}
        silent.update(self._house(house or {}, now))
        self.fresh = hub.fresh
        if not hub.fresh:
            return {**{k: v for k, v in self.last.items() if k.split(":", 1)[0] not in ("update", "update_ha",
                                                                                       "backup")}, **silent}
        found = dict(silent)
        for key, values in problems:
            kind = PROBLEM_KINDS.get(key)
            if kind is None or kind == "e32_offline":
                continue
            room_id = values.get("room_id", "") if kind == "sensor" else ""
            found[f"{kind}:{room_id}"] = {"problem": (key, values), **({"room_id": room_id} if room_id else {})}
        found.update(self._rooms(hub, now))
        found.update(self._batteries(hub, batteries or (), now, limit, wall, found))
        if self._held("frost:", frost_protection(hub), now, FROST_SECONDS):
            found["frost:"] = {}
        if self._held("boiler_fault:", fault is not None, now, FAULT_SECONDS):
            found["boiler_fault:"] = dict(fault)
        from .heating_plan import plan_ready
        if plan_ready(hub):  # once per readiness: the episode ends when the E32 plans, or checks again
            found["plan_ready:"] = {"plan_room": (hub.heating_plan or {}).get("room") or ""}
        return found

    def _house(self, house, now):
        """The maintenance causes Home Assistant itself knows (they hold also while the E32 is silent)."""
        found = {}
        code = house.get("maintenance")
        for key in [k for k in self.since if k.startswith("maintenance:") and k != f"maintenance:{code}"]:
            del self.since[key]  # another code (or none): its hold starts again
        if type(code) is str and code and self._held(f"maintenance:{code}", True, now, MAINTENANCE_SECONDS):
            found["maintenance:"] = {"code": code, "episode": code}
        for key, version in (house.get("updates") or {}).items():
            if type(version) is str and version and self.announced.get(key) != version:
                found[key] = {"version": version, "episode": version}
        if type(house.get("backup")) is dict:
            found["backup:"] = dict(house["backup"])
        hint = house.get("season")
        if type(hint) is dict:
            # Once per hint (its since_day): open while it holds, never again once its message went out and ended.
            episode = f"{hint['kind']}:{hint['since_day']}"
            if "season:" in self.open or self.announced.get("season:") != episode:
                found["season:"] = {"hint": hint["kind"], "since_day": hint["since_day"], "episode": episode}
        return found

    def _held(self, key, on, now, seconds):
        if not on:
            self.since.pop(key, None)
            return False
        return now - self.since.setdefault(key, now) >= seconds

    def _rooms(self, hub, now):
        from .heating_problem import ROOM_MEASURED
        found, cold = {}, {}
        for room_id, room in hub.rooms.items():
            comfort = room.get("comfort") if type(room.get("comfort")) is dict else {}
            window = comfort.get("window")
            temperature, target = _number(room.get("temperature")), _number(room.get("setpoint"))
            if window != "open" and target is not None:
                self.before[room_id] = target
            key = f"window:{room_id}"
            if room.get("state") == "active" and window == "open":
                before = self.before.get(room_id)
                # Only while the room heats: colder than its target before the pause (unknown: yes).
                if key in self.last or temperature is None or before is None or temperature < before:
                    found[key] = {"room_id": room_id, "opening": "door" if comfort.get("opening") == "door"
                                  else "window"}
            if (room.get("status") in ROOM_MEASURED and room.get("demand") is True and window not in ("open", "pending")
                    and temperature is not None and target is not None and temperature < target - COLD_MARGIN_C):
                previous = self.cold.get(room_id)
                since = now if previous is None or target > previous[0] else previous[1]
                cold[room_id] = (target, since)
                if now - since >= COLD_SECONDS:
                    found[f"cold:{room_id}"] = {"room_id": room_id, "temperature": temperature, "target": target}
        self.cold = cold
        return found

    def _batteries(self, hub, rows, now, limit, wall, found):
        """One battery message per device of a room whose battery is low for BATTERY_SECONDS (its row's ``low``, or
        is_low with the limit; once low, until ``recovered``: limit + 5), and one "silent" message (kind sensor) per
        device that usually reports and has not for STALE_S (``reported_at``, or ``silent_since`` while unavailable).
        A thermometer whose room has no measurement is the room's sensor message already. A device without a room is
        never a room message."""
        out, seen = {}, set()
        for row in rows if type(rows) in (list, tuple) else ():
            room_id, device_id = row.get("room"), row.get("id")
            if type(room_id) is not str or room_id not in hub.rooms or type(device_id) is not str or not device_id:
                continue
            kind = row.get("kind") if row.get("kind") in BATTERY_KINDS else "thermometer"
            name = row.get("name") if type(row.get("name")) is str and row.get("name").strip() else device_id
            key = f"battery:{room_id}|{device_id}"
            seen.add(key)
            pct = _number(row.get("pct"), 0, 100)
            if pct is not None:
                low = row.get("low") is True or is_low(pct, limit) or (key in self.low and not recovered(pct, limit))
            elif type(row.get("low")) is bool:
                low = row["low"]
            else:
                low = key in self.low  # nothing reported now (silent): as it was
            (self.low.add if low else self.low.discard)(key)
            # Its episode still open (kept over a restart): no new hold, so a restart never sends it again.
            if self._held(key, low, now, BATTERY_SECONDS) or (low and key in self.open):
                out[key] = {"room_id": room_id, "device": name, "kind": kind, "battery": pct}
            reported = _when(row.get("reported_at")) or _when(row.get("silent_since"))
            silent = (wall is not None and reported is not None and wall - reported >= STALE_S
                      and not (kind in ("thermometer", "temperature_source") and f"sensor:{room_id}" in found))
            if silent:
                out[f"sensor:{room_id}|{device_id}"] = {"room_id": room_id, "device": name, "kind": kind}
        for key in [k for k in self.low if k not in seen]:  # a device that is gone
            self.low.discard(key)
            self.since.pop(key, None)
        return out

    def due(self, found, settings, wall, local):
        """([(key, values)] to send now, [keys] whose cause is gone).

        A cause that is gone ends its episode; the E32's silence ending is the "E32 back" message. A cause
        whose message is switched off, falls in the quiet hours (rooms) or was sent less than
        COOLDOWN_SECONDS ago waits: it goes out later if it still holds then. While the E32 is silent only
        its silence goes out: the rest is what held before, not news.
        """
        messages, ended = [], sorted(self.open - set(found))
        for key in ended:
            self.open.discard(key)
            if key == "e32_offline:" and enabled(settings, "e32_back", ""):
                messages.append(("e32_back:", {}))
        for key, values in sorted(found.items()):
            kind, room_id, _device = key_parts(key)
            if key in self.open and values.get("episode") not in (None, self.episodes.get(key)):
                self.open.discard(key)  # another maintenance code or version: a new message
                self.sent.pop(key, None)
            if key in self.open and kind == "battery" and wall - self.sent.get(key, wall) >= BATTERY_REPEAT_S:
                self.open.discard(key)  # still low a week later: once more
            if key in self.open or not enabled(settings, kind, room_id) or (room_id and quiet(local)):
                continue
            if not self.fresh and kind not in ("e32_offline", *HOUSE_MAINTENANCE, "update_ha"):
                continue
            last = self.sent.get(key)
            if last is not None and 0 <= wall - last < COOLDOWN_SECONDS:
                continue
            messages.append((key, values))
        self.last = found
        self.sent = {key: at for key, at in self.sent.items() if 0 <= wall - at < COOLDOWN_SECONDS or key in self.open}
        return messages, ended

    def done(self, key, wall, values=None):
        """The message of ``key`` went out: once per episode, and its cooldown starts."""
        self.sent[key] = wall
        if key != "e32_back:":
            self.open.add(key)
        episode = (values or {}).get("episode")
        if episode is not None:
            self.episodes[key] = episode
            if key.split(":", 1)[0] in ("update", "update_ha", "season"):
                self.announced[key] = episode

    def reset(self):
        """Nothing is switched on: forget the episodes (the cooldowns and the announced versions stay)."""
        self.open.clear()
        self.episodes.clear()
        self.last = {}


# -- the texts ------------------------------------------------------------------------------------------------------


def _figure(value, lang):
    from .heating_advice import fmt
    return fmt(round(float(value), 1), lang) if type(value) in (int, float) else "?"


def message(key, values, lang, names):
    """(title, sentence) of one message in a language; ``names``: {room id: name} as the dashboard shows it."""
    from .heating_problem import SHORT, render
    kind, room_id, _device = key_parts(key)
    lang = lang if lang in TEXT else "en"
    room = names.get(room_id) or room_id
    if kind == "plan_ready":  # a house message about the plan's room
        from .heating_plan import TEXT as PLAN_TEXT
        plan_room = values.get("plan_room") or ""
        room = names.get(plan_room) or plan_room or PLAN_TEXT[lang]["your_home"]
    problem = values.get("problem")
    if problem is not None:
        problem_key, problem_values = problem
        problem_values = {**problem_values, **({"room": room} if room_id else {})}
        body = render([(problem_key, problem_values)], lang)[0]
        title = TITLE[lang].get(kind) or SHORT[lang][problem_key]
        return title.format(room=room), body
    if kind == "window":
        kind = values.get("opening", "window")
    fields = {"room": room, "temperature": _figure(values.get("temperature"), lang),
              "target": _figure(values.get("target"), lang), "battery": _figure(values.get("battery"), lang),
              "code": values.get("code", ""), "meaning": (values.get("meaning") or "").strip(),
              "version": values.get("version", ""), "last": values.get("last") or "?",
              "device": values.get("device") or ""}
    text = kind
    if kind in ("battery", "sensor"):  # one device: its kind's sentence (a silent device is kind sensor)
        device_kind = values.get("kind") if values.get("kind") in BATTERY_KINDS else "thermometer"
        text = f"{'battery' if kind == 'battery' else 'silent'}_{device_kind}"
        level = LEVEL[lang]["pct" if type(values.get("battery")) in (int, float) else "low"]
        fields["level"] = level.format(battery=fields["battery"])
        if kind == "sensor":
            kind = "silent"
    if kind == "season":
        text = "season_off" if values.get("hint") == "summer_off" else "season_on"
    body = TEXT[lang][text].format(**fields)
    if kind == "boiler_fault":
        body = body if body.endswith((".", "!", "?")) else body.rstrip(":").rstrip() + "."
        if (advice := (values.get("advice") or "").strip()):
            body += " " + advice
    return TITLE[lang][kind].format(**fields), body


# -- the notifier -------------------------------------------------------------------------------------------------


def notification_id(entry_id, key):
    kind, room_id = key.split(":", 1)
    room_id = room_id.replace("|", "_")  # one device of a room: kind_room_device
    return f"{DOMAIN}_notification_{kind}{'_' + room_id if room_id else ''}_{entry_id}"


class Notifier:
    """Follows the hub and sends the messages that are due (on every E32 message and every minute)."""

    def __init__(self, hass, entry, hub, store=None, stored=None, wall=None, local=None):
        from .heating_problem import ProblemTracker
        from .room_plan import has_room_plan
        from homeassistant.util import dt as dt_util
        self.hass, self.entry, self.hub, self.store = hass, entry, hub, store
        self.wall = wall or (lambda: dt_util.utcnow().timestamp())
        self.local = local or dt_util.now
        self.tracker = ProblemTracker(hub.clock(), expect_telemetry=has_room_plan(entry))
        stored = stored if type(stored) is dict else {}
        sent = stored.get("sent") if type(stored.get("sent")) is dict else {}
        opened = stored.get("open") if type(stored.get("open")) is list else []

        def texts(name):
            value = stored.get(name)
            return {k: v for k, v in value.items() if type(k) is str and type(v) is str} if type(value) is dict else {}
        self._batteries = (None, [])  # (when read: wall seconds, battery_rows)
        self.rules = NotificationRules({k: v for k, v in sent.items() if type(k) is str and type(v) in (int, float)},
                                       [k for k in opened if type(k) is str and ":" in k],
                                       texts("episodes"), texts("announced"))
        self._saved = self._snapshot()

    def _snapshot(self):
        return {"sent": dict(self.rules.sent), "open": sorted(self.rules.open),
                "episodes": dict(self.rules.episodes), "announced": dict(self.rules.announced)}

    def _battery_rows(self, wall, limit):
        """battery_rows, read again at most every BATTERY_READ_SECONDS (an E32 message comes far more often)."""
        read, rows = self._batteries
        if read is None or not 0 <= wall - read < BATTERY_READ_SECONDS:
            self._batteries = (wall, battery_rows(self.hass, self.entry, self.hub, limit))
        return self._batteries[1]

    def _advice_items(self):
        advice = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {}).get("heating_advice")
        return getattr(advice, "items", ()) or ()

    def _fault(self):
        from homeassistant.helpers import entity_registry as er
        entity_id = er.async_get(self.hass).async_get_entity_id(
            "sensor", DOMAIN, f"{self.hub.prefix}_boiler_fields_v1_display_code")
        return boiler_fault(self.hass.states.get(entity_id)) if entity_id else None

    def _house(self):
        """What Home Assistant knows of the house's maintenance (NotificationRules.found ``house``)."""
        return {"maintenance": self._maintenance(), "updates": self._updates(), "backup": self._backup(),
                "season": self._season()}

    def _season(self):
        """The E32's season hint while Home Assistant shows it (season_hint.shown_hint), or None."""
        from .e32_house import house_away
        from .season_hint import shown_hint
        away = house_away(self.hub)
        return shown_hint(self.entry, away, self.local().date()) if away is not None else None

    def _maintenance(self):
        from homeassistant.helpers import entity_registry as er
        entity_id = er.async_get(self.hass).async_get_entity_id(
            "sensor", DOMAIN, f"{self.hub.prefix}_boiler_fields_v1_maintenance_message")
        return maintenance_code(self.hass.states.get(entity_id)) if entity_id else None

    def _updates(self):
        from homeassistant.helpers import entity_registry as er
        registry = er.async_get(self.hass)
        found = {}
        firmware = registry.async_get_entity_id("update", DOMAIN, f"{self.hub.prefix}_e32_firmware")
        if (version := new_version(self.hass.states.get(firmware) if firmware else None)) is not None:
            found["update:"] = version
        for state in self.hass.states.async_all("update"):
            record = registry.async_get(state.entity_id)
            if record is not None and record.platform != DOMAIN and integration_update(state):
                if (version := new_version(state)) is not None:
                    found["update_ha:"] = version
                    break
        return found

    def _backup(self):
        from homeassistant.helpers import issue_registry as ir
        from .e32_backup import ISSUE
        issue = ir.async_get(self.hass).async_get_issue(DOMAIN, f"{ISSUE}_{self.entry.entry_id}")
        if issue is None:
            return None
        return {"last": (issue.translation_placeholders or {}).get("last") or "?"}

    def _home(self, person):
        from .e32_comfort import presence_home
        return presence_home(self.hass.states.get(person)) is True

    @callback
    def evaluate(self, _now=None):
        settings = notification_options(self.entry)
        if not anything_on(settings):
            self.rules.reset()
            self._save()
            return
        from .heating_advice import language
        from .insight import room_names
        now = self.hub.clock()
        self.tracker.observe(self.hub, now)
        names = room_names(self.hub, self.hass, self.entry.entry_id)
        problems = self.tracker.problems(self.hub, now, self._advice_items(), None, names)
        wall = self.wall()
        from .device_battery import limit_pct
        limit = limit_pct(self.entry)
        found = self.rules.found(self.hub, problems, self._fault(), now, self._house(), self._battery_rows(wall, limit),
                                 limit, wall)
        messages, ended = self.rules.due(found, settings, wall, self.local())
        lang = language(self.hass)
        for key in ended:
            from homeassistant.components import persistent_notification
            persistent_notification.async_dismiss(self.hass, notification_id(self.entry.entry_id, key))
        for key, values in messages:
            kind, room_id, _device = key_parts(key)
            chosen = recipients(kind, room_id, room_choice(settings, room_id) if room_id else settings["house_people"],
                                settings["phones"], self._home, lambda person: person_found(self.hass, person))
            if chosen is None:
                continue  # nobody of this room is home: it waits
            people, services, persistent = chosen
            title, text = message(key, values, lang, names)
            self.rules.done(key, wall, values)
            data = None
            if kind == "season":  # the answers as actions on a Home Assistant app (season_hint.listen)
                from .season_hint import notification_data
                data = notification_data(self.entry.entry_id, values, lang)
            self._send(key, names.get(room_id) or room_id, title, text, people, services, persistent, data,
                       values.get("device"))
        self._save()

    @callback
    def _send(self, key, room, title, text, people, services, persistent, data=None, device=None):
        kind, room_id, _device = key_parts(key)
        self.hass.bus.async_fire(EVENT, {
            "entry_id": self.entry.entry_id, "kind": kind, "room_id": room_id or None, "room": room or None,
            "title": title, "message": text, "people": list(people), **({"device": device} if device else {})})
        if key == "e32_back:":
            from homeassistant.components import persistent_notification
            persistent_notification.async_dismiss(self.hass, notification_id(self.entry.entry_id, "e32_offline:"))
            persistent = False
        self.hass.async_create_task(self._deliver(key, title, text, services, persistent, data),
                                    f"{DOMAIN} notification {kind}")

    async def _deliver(self, key, title, text, services, persistent, data=None):
        for service in services:
            payload = {"title": title, "message": text}
            if data and service.startswith("mobile_app_"):  # only the Home Assistant app shows actions
                payload["data"] = data
            try:
                await self.hass.services.async_call("notify", service, payload, blocking=True)
            except Exception as err:  # noqa: BLE001 - a phone that is gone never stops the others
                _LOGGER.warning("OpenThermostat: the notification to notify.%s failed: %s", service, err)
                persistent = True
        if persistent:
            from homeassistant.components import persistent_notification
            persistent_notification.async_create(self.hass, text, title=PERSISTENT_TITLE.format(title=title),
                                                 notification_id=notification_id(self.entry.entry_id, key))

    @callback
    def _save(self):
        snapshot = self._snapshot()
        if snapshot != self._saved and self.store is not None:
            self._saved = snapshot
            self.store.async_delay_save(lambda: snapshot, 1)


def _store(hass, entry_id):
    from homeassistant.helpers.storage import Store
    return Store(hass, STORE_VERSION, f"{DOMAIN}.notifications_{entry_id}")


async def async_setup_notifications(hass, entry, hub):
    """Product entries: the notifier, which reads its settings (Configure → Notifications) on every check."""
    from homeassistant.helpers.event import async_track_time_interval
    from .settings_notifications import add_recipients, add_season
    add_season(hass, entry)  # 1.4.1, once: house messages that are on also get the summer-mode question
    add_recipients(hass, entry)  # 1.4.2, once: each room's persons become its own recipients
    store = _store(hass, entry.entry_id)
    notifier = Notifier(hass, entry, hub, store, await store.async_load())
    hass.data[DOMAIN][entry.entry_id]["notifier"] = notifier
    entry.async_on_unload(hub.add_listener(notifier.evaluate))
    entry.async_on_unload(async_track_time_interval(hass, notifier.evaluate, CHECK_INTERVAL))
    from .season_hint import listen
    entry.async_on_unload(listen(hass, entry))  # the answers to the season hint from a phone
    notifier.evaluate()
    return notifier


async def async_remove_notifications(hass, entry_id):
    """A removed installation: what its messages kept (the cooldowns, the open episodes) is forgotten."""
    await _store(hass, entry_id).async_remove()


# -- the phones (Configure → Notifications → People and phones) ---------------------------------------------------


PHONE_APP = {"en": "{name} (Home Assistant app)", "nl": "{name} (Home Assistant-app)"}


def phone_apps(hass):
    """{service: the phone's name, or None} of the notify services that reach one phone or app, sorted: a Home
    Assistant app by the name of its phone, any other service (Telegram, e-mail …) without one."""
    from homeassistant.util import slugify
    apps = {}
    for app in hass.config_entries.async_entries("mobile_app"):
        name = app.data.get("device_name")
        if type(name) is str and name:
            apps[f"mobile_app_{slugify(name)}"] = name
    return {service: apps.get(service)
            for service in sorted(hass.services.async_services_for_domain("notify")) if service not in NOT_A_PHONE}


def phone_services(hass, lang=None):
    """{service: label} of the notify services that reach one phone or app, the app's devices by their name (in
    Home Assistant's language, or ``lang``)."""
    from .heating_advice import language
    words = PHONE_APP[lang if lang in PHONE_APP else language(hass)]
    return {service: words.format(name=name) if name else f"notify.{service}"
            for service, name in phone_apps(hass).items()}


def suggested_phone(hass, person, services):
    """The app on the person's own phone (a mobile app device tracker of that person), or None."""
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er
    from homeassistant.util import slugify
    state = hass.states.get(person)
    trackers = state.attributes.get("device_trackers") if state is not None else None
    for tracker in trackers if type(trackers) is list else []:
        item = er.async_get(hass).async_get(tracker) if type(tracker) is str else None
        device = dr.async_get(hass).async_get(item.device_id) if item is not None and item.device_id else None
        if item is None or item.platform != "mobile_app" or device is None:
            continue
        # The app names its notify service after the phone's own name (not a name given in Home Assistant).
        service = f"mobile_app_{slugify(device.name or '')}"
        if service in services:
            return service
    return None
