"""The settings panel's section Notifications (settings.py registers it; the screens are
frontend/openthermostat-settings-notifications.js).

1.4 built one screen with Configure → Notifications' three forms together. 1.4.1 (design
docs/engineering/HA-INSTELPANEEL-FASE2.nl.md 3.5) splits it into two questions, each on its own calm screen: "who gets
messages" (the people, then one person) and "which messages" (the house, and the rooms with a summary each). Home
Assistant keeps these settings (the entry's options); nothing is read from the E32, and no model holds a live value.

The items of ``settings/get {section: "notifications", item}``:

- ``None`` (the overview): ``status`` for the one status line at the top ("Messages go to Mark (Pixel 8) · house
  messages to nobody."; ``status.line`` is that line in EN/NL/PL), ``people_count``, ``house_on``, ``rooms_on``
  (names). It has no save.
- ``people``: ``{people: [{person, name, phone, phone_label, phone_kind, house_too, suggested}]}``.
- ``person/<person>``: ``{person, name, phone, phone_label, phone_kind, phones, suggested, house_too}``; save keys
  ``phone`` (a notify service, or null for none) and ``house_too``.
- ``house``: ``{on, problems, maintenance, kinds: {problems: [{kind, cause_key}], maintenance: [...]}}``; save keys
  ``on``, ``problems``, ``maintenance``.
- ``rooms``: ``{rooms: [{room, name, on, kinds, people, summary}]}``; no save (a room's notifications are on its own
  screen, ``#room/<id>``).

A phone is shown language-neutral: ``phone_label`` is the phone's name for a Home Assistant app ("Pixel 8"; the panel
adds "(Home Assistant app)" in the viewer's language), else ``notify.<service>``; ``phone_kind`` is ``"app"``,
``"service"`` (another notify service), ``"gone"`` (chosen, but Home Assistant no longer has it) or null (no phone).

A save checks and changes with the forms' own functions (notifications_flow.changed_person for a person,
changed_house for the house): a part shown unchanged is not touched, so each item stores exactly what the matching
Configure form stores for the same input. Errors carry the item's field (``phone``, ``house_too``, ``problems``) and
the forms' codes (``notification_phone_invalid``, ``notification_invalid``, ``notification_kinds_needed``,
``notification_person_invalid``). The one screen of 1.4 (its flat model and flat save) is gone since 1.4.1.

The words the backend writes itself, EN/NL/PL (docs/UX-GLOSSARY.md, block "1.4.1 NOTIFY-BACKEND"): CAUSES, one line
per message kind saying what causes it (the panel shows it under the kind; ``cause_key`` names it), SHORT, the
kinds' short words of a room's summary ("On: window open, too cold"), and STATUS, the parts of the status line.

add_season: the one-time migration of 1.4.1 that adds the house message ``season`` (the summer-mode question) to an
installation whose house messages were on before 1.4.1 (notifications.async_setup_notifications runs it).
"""
from __future__ import annotations

from homeassistant.core import callback

from .settings import SettingsError, register_section

# The overview's line (the words of Configure → Notifications: "On now: the house, Woonkamer").
WORDS = {"en": {"on": "On: {what}", "off": "Off", "house": "the house"},
         "nl": {"on": "Aan: {what}", "off": "Uit", "house": "het huis"},
         "pl": {"on": "Włączone: {what}", "off": "Wyłączone", "house": "dom"}}

LANGUAGES = ("en", "nl", "pl")

# One line per message kind: what causes it (cause_key = "cause_<kind>"). Every kind of notifications.ROOM_KINDS and
# HOUSE_KINDS has one, and no other (test_settings_notifications.py fails otherwise). "season" is the summer-mode
# hint of 1.4.1.
CAUSES = {
    "en": {
        "window": "A window or door is open while the room heats.",
        "cold": "The room stays more than 1 °C below its target temperature for over an hour.",
        "sensor": "The room's temperature sensor has not reported for 30 minutes.",
        "battery": "A thermometer or radiator valve of the room reports a battery below 20 %.",
        "boiler_fault": "The boiler reports a fault.",
        "e32_offline": "The E32 has not reported for 10 minutes; a second message when it is back.",
        "awaiting_confirmation": "The E32 waits for your confirmation before it controls the boiler.",
        "frost": "A room cooled below 8 °C, so the E32 heats against frost.",
        "pressure_low": "The water pressure of the heating is too low.",
        "maintenance": "The boiler asks for maintenance (an H code).",
        "update": "A new version of the E32 firmware or of this integration is available.",
        "backup": "The daily backup of the E32 settings has failed for more than 3 days.",
        "plan_ready": "The E32 is ready to plan the heating and asks for your confirmation once.",
        "season": "Five days above 17 °C outside, or three cold days while summer mode is on.",
    },
    "nl": {
        "window": "Er staat een raam of deur open terwijl de ruimte verwarmt.",
        "cold": "De ruimte blijft langer dan een uur meer dan 1 °C onder de gewenste temperatuur.",
        "sensor": "De temperatuursensor van de ruimte meldt zich al 30 minuten niet.",
        "battery": "Een thermometer of radiatorkraan van de ruimte meldt een batterij onder 20 %.",
        "boiler_fault": "De ketel meldt een storing.",
        "e32_offline": "De E32 meldt zich al 10 minuten niet; een tweede bericht als hij er weer is.",
        "awaiting_confirmation": "De E32 wacht op je bevestiging voordat hij de ketel regelt.",
        "frost": "Een ruimte is afgekoeld tot onder 8 °C, dus de E32 verwarmt tegen vorst.",
        "pressure_low": "De waterdruk van de verwarming is te laag.",
        "maintenance": "De ketel vraagt om onderhoud (een H-code).",
        "update": "Er is een nieuwe versie van de E32-firmware of van deze integratie.",
        "backup": "De dagelijkse back-up van de E32-instellingen mislukt al meer dan 3 dagen.",
        "plan_ready": "De E32 is klaar om de verwarming te plannen en vraagt één keer je bevestiging.",
        "season": "Vijf dagen boven 17 °C buiten, of drie koude dagen terwijl de zomerstand aan staat.",
    },
    "pl": {
        "window": "Okno lub drzwi są otwarte, gdy pomieszczenie jest ogrzewane.",
        "cold": "Pomieszczenie przez ponad godzinę jest ponad 1 °C poniżej temperatury docelowej.",
        "sensor": "Czujnik temperatury pomieszczenia nie odzywa się od 30 minut.",
        "battery": "Termometr lub zawór grzejnikowy pomieszczenia zgłasza baterię poniżej 20 %.",
        "boiler_fault": "Kocioł zgłasza usterkę.",
        "e32_offline": "E32 nie odzywa się od 10 minut; druga wiadomość, gdy znów jest dostępny.",
        "awaiting_confirmation": "E32 czeka na Twoje potwierdzenie, zanim zacznie sterować kotłem.",
        "frost": "Pomieszczenie wychłodziło się poniżej 8 °C, więc E32 grzeje, chroniąc przed mrozem.",
        "pressure_low": "Ciśnienie wody w instalacji grzewczej jest za niskie.",
        "maintenance": "Kocioł wymaga konserwacji (kod H).",
        "update": "Dostępna jest nowa wersja oprogramowania E32 lub tej integracji.",
        "backup": "Codzienna kopia ustawień E32 nie udaje się od ponad 3 dni.",
        "plan_ready": "E32 jest gotowy do planowania ogrzewania i raz prosi o Twoje potwierdzenie.",
        "season": "Pięć dni powyżej 17 °C na zewnątrz albo trzy chłodne dni, gdy tryb letni jest włączony.",
    },
}
# A kind that may have a sentence before notifications.py has the kind (a package that adds one merges later).
PENDING_KINDS = frozenset()

# A room's summary on the "which messages" screen: "On: window open, too cold" / "Off" (the kinds in their order).
SHORT = {
    "en": {"on": "On: {kinds}", "off": "Off", "window": "window open", "cold": "too cold", "sensor": "sensor silent",
           "battery": "battery low"},
    "nl": {"on": "Aan: {kinds}", "off": "Uit", "window": "raam open", "cold": "te koud", "sensor": "sensor stil",
           "battery": "batterij bijna leeg"},
    "pl": {"on": "Włączone: {kinds}", "off": "Wyłączone", "window": "otwarte okno", "cold": "za zimno",
           "sensor": "czujnik milczy", "battery": "słaba bateria"},
}

# The parts of the status line, joined with " · " and ended with a full stop:
# "Messages go to Mark (Pixel 8) · Anna without a phone · house messages to nobody."; somebody with the tick "Also
# messages about the house" but no phone is named with "no_phone" ("house messages to Anna (no phone: in Home
# Assistant)": they show in Home Assistant).
STATUS = {
    "en": {"to": "Messages go to {people}", "to_nobody": "No phone chosen yet, so messages show in Home Assistant",
           "without": "{people} without a phone", "gone": "{people}: phone not found",
           "house": "house messages to {people}", "house_nobody": "house messages to nobody",
           "house_off": "house messages off", "no_people": "No people in Home Assistant yet",
           "no_phone": "{name} (no phone: in Home Assistant)"},
    "nl": {"to": "Berichten gaan naar {people}",
           "to_nobody": "Nog geen telefoon gekozen, dus berichten verschijnen in Home Assistant",
           "without": "{people} zonder telefoon", "gone": "{people}: telefoon niet gevonden",
           "house": "huisberichten naar {people}", "house_nobody": "huisberichten naar niemand",
           "house_off": "huisberichten uit", "no_people": "Nog geen personen in Home Assistant",
           "no_phone": "{name} (geen telefoon: in Home Assistant)"},
    "pl": {"to": "Wiadomości trafiają do: {people}",
           "to_nobody": "Nie wybrano jeszcze telefonu, więc wiadomości pojawiają się w Home Assistant",
           "without": "{people}: bez telefonu", "gone": "{people}: nie znaleziono telefonu",
           "house": "wiadomości o domu: {people}", "house_nobody": "wiadomości o domu: do nikogo",
           "house_off": "wiadomości o domu: wyłączone", "no_people": "Brak osób w Home Assistant",
           "no_phone": "{name} (brak telefonu: w Home Assistant)"},
}

ITEMS = ("people", "house", "rooms")
PERSON = "person/"


def cause_key(kind):
    return f"cause_{kind}"


def kind_rows(kinds):
    """[{kind, cause_key}] of message kinds in their order (the panel shows CAUSES[lang][kind] under each)."""
    return [{"kind": kind, "cause_key": cause_key(kind)} for kind in kinds]


def phone_shown(service, apps):
    """(phone_label, phone_kind) of a chosen notify service: the phone's name and "app" for a Home Assistant app,
    ``notify.<service>`` and "service" for another one, ``notify.<service>`` and "gone" for one Home Assistant no
    longer has, (None, None) for none. ``apps`` is notifications.phone_apps."""
    if not service:
        return None, None
    if service in apps:
        return (apps[service], "app") if apps[service] else (f"notify.{service}", "service")
    return f"notify.{service}", "gone"


def room_summary(on, kinds):
    """{en, nl, pl} of a room's line: "On: window open, too cold" or "Off"."""
    from .notifications import ROOM_KINDS
    out = {}
    for lang in LANGUAGES:
        words = SHORT[lang]
        out[lang] = (words["on"].format(kinds=", ".join(words[k] for k in ROOM_KINDS if k in kinds))
                     if on else words["off"])
    return out


def _phone_row(service, apps):
    label, kind = phone_shown(service, apps)
    return {"service": service, "label": label, "kind": kind}


def _people(hass, entry, settings, apps):
    """[{person, name, phone, phone_label, phone_kind, house_too, suggested}] of everyone a phone can be chosen for."""
    from .notifications import house_people, suggested_phone
    from .notifications_flow import person_name
    services = dict.fromkeys(apps, "")
    people = []
    for person in house_people(hass, entry):
        phone = settings["phones"].get(person)
        label, kind = phone_shown(phone, apps)
        suggested = None if phone else suggested_phone(hass, person, services)
        people.append({"person": person, "name": person_name(hass, person), "phone": phone, "phone_label": label,
                       "phone_kind": kind, "house_too": person in settings["house_people"],
                       "suggested": _phone_row(suggested, apps) if suggested else None})
    return people


def _rooms_on(hass, entry, settings):
    """The names of the rooms switched on, by the name the dashboard shows (sorted as the form lists them); a room
    the E32 no longer reports by its id, after them."""
    from .notifications_flow import notify_rooms
    rooms = [room_id for room_id, room in settings["rooms"].items() if room["on"]]
    known = notify_rooms(hass, entry)
    return ([name for room_id, name in known if room_id in rooms]
            + sorted(set(rooms) - {room_id for room_id, _ in known}))


def status_line(status, house_on, people_count):
    """{en, nl, pl} of the status line from the status data."""
    reached = [row for row in status["recipients"] if row["phone_kind"] != "gone"]
    gone = [row["name"] for row in status["recipients"] if row["phone_kind"] == "gone"]
    out = {}
    for lang in LANGUAGES:
        words = STATUS[lang]
        if not people_count:
            out[lang] = words["no_people"] + "."
            continue
        parts = [words["to"].format(people=", ".join(f"{r['name']} ({r['phone_label']})" for r in reached))
                 if reached else words["to_nobody"]]
        if gone:
            parts.append(words["gone"].format(people=", ".join(gone)))
        if status["without_phone"] and reached:
            parts.append(words["without"].format(people=", ".join(status["without_phone"])))
        if not house_on:
            parts.append(words["house_off"])
        elif status["house_recipients"]:
            without = set(status["without_phone"])
            parts.append(words["house"].format(people=", ".join(
                words["no_phone"].format(name=name) if name in without else name
                for name in status["house_recipients"])))
        else:
            parts.append(words["house_nobody"])
        out[lang] = " · ".join(parts) + "."
    return out


def _overview(hass, entry, settings, people):
    status = {"recipients": [{"person": p["person"], "name": p["name"], "phone": p["phone"],
                              "phone_label": p["phone_label"], "phone_kind": p["phone_kind"]}
                             for p in people if p["phone"]],
              "without_phone": [p["name"] for p in people if not p["phone"]],
              "house_recipients": [p["name"] for p in people if p["house_too"]]}
    house_on = settings["house"]["on"]
    status["line"] = status_line(status, house_on, len(people))
    return {"status": status, "people_count": len(people), "house_on": house_on,
            "rooms_on": _rooms_on(hass, entry, settings)}


def _person_id(hass, entry, item):
    """The person of an item ``person/<person>``; SettingsError notification_person_invalid when no phone can be
    chosen for it (as the form's person picker)."""
    from .notifications import house_people
    person = item[len(PERSON):]
    if person not in house_people(hass, entry):
        raise SettingsError("notification_person_invalid")
    return person


def read_notifications(hass, entry, item=None):
    from .notifications import HOUSE_MAINTENANCE, HOUSE_PROBLEMS, notification_options, phone_apps, room_people
    from .notifications_flow import notify_rooms, person_name, shown_room
    if item is not None and item not in ITEMS and not (type(item) is str and item.startswith(PERSON)):
        raise SettingsError("unknown_section")
    settings, apps = notification_options(entry), phone_apps(hass)
    if item is None:
        return _overview(hass, entry, settings, _people(hass, entry, settings, apps))
    if item == "people":
        return {"people": _people(hass, entry, settings, apps)}
    if item == "house":
        house = settings["house"]
        return {"on": house["on"], "problems": [k for k in house["kinds"] if k in HOUSE_PROBLEMS],
                "maintenance": [k for k in house["kinds"] if k in HOUSE_MAINTENANCE],
                "kinds": {"problems": kind_rows(HOUSE_PROBLEMS), "maintenance": kind_rows(HOUSE_MAINTENANCE)}}
    if item == "rooms":
        rooms = []
        for room_id, name in notify_rooms(hass, entry):
            shown = shown_room(settings, room_id)
            rooms.append({"room": room_id, "name": name, "on": shown["on"], "kinds": list(shown["kinds"]),
                          "people": [person_name(hass, p) for p in room_people(entry, room_id)],
                          "summary": room_summary(shown["on"], shown["kinds"])})
        return {"rooms": rooms}
    person = _person_id(hass, entry, item)
    row = next(p for p in _people(hass, entry, settings, apps) if p["person"] == person)
    phones = [_phone_row(service, apps) for service in apps]
    if row["phone"] and row["phone"] not in apps:
        phones.append(_phone_row(row["phone"], apps))  # a chosen phone that is gone stays a choice (as the form)
    if row["suggested"]:  # the suggestion on top, as the screen shows it
        phones.sort(key=lambda p: p["service"] != row["suggested"]["service"])
    return {**row, "phones": phones}


def _changed_person(hass, entry, person, values):
    """The settings after a person's screen (``phone``: a notify service, None or "none" for none; ``house_too``;
    what is left out stays as shown), checked as the form notify_person checks them; SettingsError with the screen's
    field."""
    from .e32_room_flow import FlowError
    from .notifications import notification_options, phone_apps
    from .notifications_flow import NO_PHONE, changed_person, phone_choices
    settings = notification_options(entry)
    chosen = values.get("phone", settings["phones"].get(person) or NO_PHONE)
    house = values.get("house_too", person in settings["house_people"])
    texts = {"no_phone": "", "phone_gone": "{service}"}  # labels are the panel's; only the choices' keys count here
    choices = phone_choices(settings, dict.fromkeys(phone_apps(hass), ""), person, texts)
    try:
        return changed_person(settings, person, NO_PHONE if chosen is None else chosen, house, choices)
    except FlowError as err:
        raise SettingsError(err.key, "phone" if err.field == "phone" else "house_too") from None


def _changed_house(entry, values):
    """The settings after the house's screen (``on``, ``problems``, ``maintenance``; what is left out stays as
    shown), checked as the form notify_house checks them; unchanged: the settings as they are."""
    from .e32_room_flow import FlowError
    from .notifications import HOUSE_MAINTENANCE, HOUSE_PROBLEMS, notification_options
    from .notifications_flow import changed_house
    settings = notification_options(entry)
    house = settings["house"]
    shown = (house["on"], [k for k in house["kinds"] if k in HOUSE_PROBLEMS],
             [k for k in house["kinds"] if k in HOUSE_MAINTENANCE])
    wanted = (values.get("on", shown[0]), values.get("problems", shown[1]), values.get("maintenance", shown[2]))
    if wanted == shown:
        return settings
    try:
        return changed_house(settings, *wanted)
    except FlowError as err:
        raise SettingsError(err.key, "problems" if err.field == "kinds" else "base") from None


SAVE_KEYS = {"house": {"on", "problems", "maintenance"}, "person": {"phone", "house_too"}}


def save_notifications_section(hass, entry, item, values):
    """A save of the house's screen or of one person's; the overview, the people and the rooms have none
    (unknown_section). Only the item's keys; nothing is written when nothing changed."""
    from .notifications import notification_options, save_notifications
    if item == "house":
        kind, person = "house", None
    elif type(item) is str and item.startswith(PERSON):
        kind, person = "person", _person_id(hass, entry, item)
    else:
        raise SettingsError("unknown_section")
    if type(values) is not dict or set(values) - SAVE_KEYS[kind]:
        raise SettingsError("notification_invalid")
    settings = _changed_house(entry, values) if kind == "house" else _changed_person(hass, entry, person, values)
    if settings != notification_options(entry):
        save_notifications(hass, entry, settings)  # the forms' own write: no reload, the notifier checks at once
    return read_notifications(hass, entry, item)


@callback
def add_season(hass, entry):
    """1.4.1, once: house messages that were switched on before 1.4.1 get the new message ``season`` (the
    summer-mode question) added to their chosen kinds, as a new installation gets it by default. Only such an entry is
    written (anything else keeps its options exactly); notifications.save_notifications marks every list chosen from
    1.4.1 on (SEASON_ADDED), so an owner's later choice is never changed. Stored without a reload; True when it
    wrote."""
    from .const import DOMAIN
    from .energy_input import ENERGY_ONLY_UPDATE
    from .notifications import CONF_NOTIFICATIONS, SEASON_ADDED
    options = dict(getattr(entry, "options", None) or {})
    raw = options.get(CONF_NOTIFICATIONS)
    house = raw.get("house") if type(raw) is dict else None
    kinds = house.get("kinds") if type(house) is dict else None
    if (options.get(SEASON_ADDED) is True or house is None or house.get("on") is not True or type(kinds) is not list
            or "season" in kinds):
        return False
    new = {**options, SEASON_ADDED: True, CONF_NOTIFICATIONS: {**raw, "house": {**house, "kinds": [*kinds, "season"]}}}
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if type(state) is dict:
        state[ENERGY_ONLY_UPDATE] = dict(new)  # the comfort settings' no-reload marker
    if not hass.config_entries.async_update_entry(entry, options=new) and type(state) is dict:
        state.pop(ENERGY_ONLY_UPDATE, None)  # no listener runs: never leave the marker behind
    return True


def summary_notifications(hass, entry, hub, lang):
    """"Off" until something is on; then what is on, as Configure says it ("On: the house, Woonkamer")."""
    from .notifications import notification_options
    words, settings = WORDS[lang], notification_options(entry)
    on = ([words["house"]] if settings["house"]["on"] else []) + _rooms_on(hass, entry, settings)
    return [words["on"].format(what=", ".join(on)) if on else words["off"]]


register_section("notifications", read_notifications, save_notifications_section, summary=summary_notifications)
