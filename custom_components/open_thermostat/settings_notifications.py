"""The settings panel's section Notifications (settings.py registers it; the screens are
frontend/openthermostat-settings-notifications.js).

1.4 built one screen with Configure → Notifications' three forms together. 1.4.1 (design
docs/engineering/HA-INSTELPANEEL-FASE2.nl.md 3.5) splits it into two questions, each on its own calm screen: "who gets
messages" (the people, then one person) and "which messages" (the house, and the rooms with a summary each). Home
Assistant keeps these settings (the entry's options); nothing is read from the E32, and no model holds a live value.

The items of ``settings/get {section: "notifications", item}``:

- ``None`` (the overview): ``status`` for the one status line at the top ("Messages go to Mark (Pixel 8) · house
  messages to nobody."; ``status.line`` is that line in EN/NL), ``people_count``, ``house_on``, ``rooms_on``
  (names). It has no save.
- ``people``: ``{people: [{person, name, phone, phone_label, phone_kind, house_too, suggested}]}``.
- ``person/<person>``: ``{person, name, phone, phone_label, phone_kind, phones, suggested, house_too}``; save keys
  ``phone`` (a notify service, or null for none) and ``house_too``.
- ``house``: ``{on, problems, maintenance, kinds: {problems: [{kind, cause_key}], maintenance: [...]}}``; save keys
  ``on``, ``problems``, ``maintenance``.
- ``rooms``: ``{rooms: [{room, name, on, kinds, people, summary, recipients_line}]}``; no save (a room's
  notifications are on its own screen, ``#room/<id>``). ``people``: the names of the room's chosen recipients Home
  Assistant still knows; ``recipients_line``: who gets them in one sentence (recipients_line).
- ``room/<room id>`` (1.4.2, CONTRACT-1.4.2 §2; the room screen's "Who gets them" saves here, settings_rooms.py is not
  touched): ``{room, name, recipients, people, recipients_line}``. ``recipients``: the room's own list of person and
  device tracker ids, or null when it never had one (everyone with a phone); ``people``: ``[{person, name,
  phone_label, phone_kind, found, chosen}]`` of everyone who can be chosen (house_people, sorted by name) and of a
  chosen one Home Assistant no longer knows (``found`` false: "not found", skipped when a message goes out);
  ``recipients_line``: ``{en, nl}``. Save key ``recipients``: a list of those ids (``[]``: nobody, the messages show in
  Home Assistant only), or null for everyone with a phone. Refusals: ``e32_room_missing`` (a room the E32 does not
  report), ``notification_person_invalid`` on ``recipients`` (an id that is not one of the people).

A phone is shown language-neutral: ``phone_label`` is the phone's name for a Home Assistant app ("Pixel 8"; the panel
adds "(Home Assistant app)" in the viewer's language), else ``notify.<service>``; ``phone_kind`` is ``"app"``,
``"service"`` (another notify service), ``"gone"`` (chosen, but Home Assistant no longer has it) or null (no phone).

A save checks and changes with the forms' own functions (notifications_flow.changed_person for a person,
changed_house for the house): a part shown unchanged is not touched, so each item stores exactly what the matching
Configure form stores for the same input. Errors carry the item's field (``phone``, ``house_too``, ``problems``) and
the forms' codes (``notification_phone_invalid``, ``notification_invalid``, ``notification_kinds_needed``,
``notification_person_invalid``). The one screen of 1.4 (its flat model and flat save) is gone since 1.4.1.

The words the backend writes itself, EN/NL (docs/UX-GLOSSARY.md, block "1.4.1 NOTIFY-BACKEND"): CAUSES, one line
per message kind saying what causes it (the panel shows it under the kind; ``cause_key`` names it), SHORT, the
kinds' short words of a room's summary ("On: window open, too cold"), and STATUS, the parts of the status line.

add_season: the one-time migration of 1.4.1 that adds the house message ``season`` (the summer-mode question) to an
installation whose house messages were on before 1.4.1 (notifications.async_setup_notifications runs it).
add_recipients: the one-time migration of 1.4.2 that copies each room's persons into its own recipients.
"""
from __future__ import annotations

from homeassistant.core import callback

from .settings import SettingsError, register_section

# The overview's line (the words of Configure → Notifications: "On now: the house, Woonkamer").
WORDS = {"en": {"on": "On: {what}", "off": "Off", "house": "the house"},
         "nl": {"on": "Aan: {what}", "off": "Uit", "house": "het huis"}}

LANGUAGES = ("en", "nl")

# One line per message kind: what causes it (cause_key = "cause_<kind>"). Every kind of notifications.ROOM_KINDS and
# HOUSE_KINDS has one, and no other (test_settings_notifications.py fails otherwise). "season" is the summer-mode
# hint of 1.4.1.
CAUSES = {
    "en": {
        "window": "A window or door is open while the room heats.",
        "cold": "The room stays more than 1 °C below its target temperature for over an hour.",
        "sensor": "The room's temperature sensor has not reported for 30 minutes, or a device of the room with a "
                  "battery for 24 hours.",
        "battery": "A thermometer, radiator valve, window or door contact or the setting device of the room reports "
                   "a battery below the limit under Devices (20 % unless you change it); once more after 7 days.",
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
        "sensor": "De temperatuursensor van de ruimte meldt zich al 30 minuten niet, of een apparaat van de ruimte "
                  "met een batterij al 24 uur niet.",
        "battery": "Een thermometer, radiatorkraan, raam- of deurcontact of het instelapparaat van de ruimte meldt een "
                   "batterij onder de grens bij Apparaten (20 % tenzij je die verandert); na 7 dagen nog één keer.",
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
}
# A kind that may have a sentence before notifications.py has the kind (a package that adds one merges later).
PENDING_KINDS = frozenset()

# A room's summary on the "which messages" screen: "On: window open, too cold" / "Off" (the kinds in their order).
SHORT = {
    "en": {"on": "On: {kinds}", "off": "Off", "window": "window open", "cold": "too cold", "sensor": "sensor silent",
           "battery": "battery low"},
    "nl": {"on": "Aan: {kinds}", "off": "Uit", "window": "raam open", "cold": "te koud", "sensor": "sensor stil",
           "battery": "batterij bijna leeg"},
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
}

# Who gets a room's messages, in one sentence (1.4.2; the room screen and Notifications → Rooms): recipients_line.
RECIPIENTS = {
    "en": {"to": "Messages about {room} go to {people}.",
           "everyone": "Messages about {room} go to everyone with a phone.",
           "nobody": "Messages about {room} go to nobody; they show in Home Assistant only.",
           "gone": "Not found in Home Assistant: {people}.", "and": " and "},
    "nl": {"to": "Berichten van {room} gaan naar {people}.",
           "everyone": "Berichten van {room} gaan naar iedereen met een telefoon.",
           "nobody": "Berichten van {room} gaan naar niemand; ze verschijnen alleen in Home Assistant.",
           "gone": "Niet gevonden in Home Assistant: {people}.", "and": " en "},
}

ITEMS = ("people", "house", "rooms")
PERSON = "person/"
ROOM = "room/"


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
    """{en, nl} of a room's line: "On: window open, too cold" or "Off"."""
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


def _names(names, lang):
    """"Mark", "Mark and Anna", "Mark, Anna and Lotte" (EN), "… en …" (NL)."""
    words = RECIPIENTS[lang]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + words["and"] + names[-1]


def recipients_line(hass, entry, settings, room_id, room_name):
    """{en, nl}: who gets this room's messages: "Messages about Badkamer go to Mark and Anna." (someone without a phone
    as "Anna (no phone: in Home Assistant)"), "… to everyone with a phone." (never chosen, or everyone chosen is gone),
    "… to nobody; they show in Home Assistant only." (an empty list); a chosen person Home Assistant no longer knows
    is named after it ("Not found in Home Assistant: person.lotte.")."""
    from .notifications import person_found, room_choice
    from .notifications_flow import person_name
    chosen = room_choice(settings, room_id)
    found = [p for p in chosen or () if person_found(hass, p)]
    gone = [p for p in chosen or () if p not in found]
    out = {}
    for lang, words in RECIPIENTS.items():
        if chosen == []:
            line = words["nobody"].format(room=room_name)
        elif not found:
            line = words["everyone"].format(room=room_name)
        else:
            names = [STATUS[lang]["no_phone"].format(name=person_name(hass, p)) if p not in settings["phones"]
                     else person_name(hass, p) for p in found]
            line = words["to"].format(room=room_name, people=_names(names, lang))
        if gone:
            line += " " + words["gone"].format(people=", ".join(gone))
        out[lang] = line
    return out


def _room_id(hass, entry, item):
    """(room id, name) of an item ``room/<room id>``; SettingsError e32_room_missing for a room the E32 does not
    report."""
    from .notifications_flow import notify_rooms
    room_id = item[len(ROOM):]
    name = dict(notify_rooms(hass, entry)).get(room_id)
    if name is None:
        raise SettingsError("e32_room_missing", room=room_id)
    return room_id, name


def _room_model(hass, entry, settings, apps, room_id, name):
    from .notifications import house_people, person_found, room_choice
    from .notifications_flow import person_name
    chosen = room_choice(settings, room_id)
    people = []
    for person in dict.fromkeys([*house_people(hass, entry), *(chosen or ())]):
        label, kind = phone_shown(settings["phones"].get(person), apps)
        people.append({"person": person, "name": person_name(hass, person), "phone_label": label, "phone_kind": kind,
                       "found": person_found(hass, person), "chosen": person in (chosen or ())})
    people.sort(key=lambda p: (p["name"].casefold(), p["person"]))
    return {"room": room_id, "name": name, "recipients": chosen, "people": people,
            "recipients_line": recipients_line(hass, entry, settings, room_id, name)}


def _rooms_on(hass, entry, settings):
    """The names of the rooms switched on, by the name the dashboard shows (sorted as the form lists them); a room
    the E32 no longer reports by its id, after them."""
    from .notifications_flow import notify_rooms
    rooms = [room_id for room_id, room in settings["rooms"].items() if room["on"]]
    known = notify_rooms(hass, entry)
    return ([name for room_id, name in known if room_id in rooms]
            + sorted(set(rooms) - {room_id for room_id, _ in known}))


def status_line(status, house_on, people_count):
    """{en, nl} of the status line from the status data."""
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
    from .notifications import HOUSE_MAINTENANCE, HOUSE_PROBLEMS, notification_options, phone_apps
    from .notifications_flow import notify_rooms, room_recipients, shown_room
    if item is not None and item not in ITEMS and not (type(item) is str and item.startswith((PERSON, ROOM))):
        raise SettingsError("unknown_section")
    settings, apps = notification_options(entry), phone_apps(hass)
    if type(item) is str and item.startswith(ROOM):
        return _room_model(hass, entry, settings, apps, *_room_id(hass, entry, item))
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
                          "people": room_recipients(hass, entry, room_id),
                          "summary": room_summary(shown["on"], shown["kinds"]),
                          "recipients_line": recipients_line(hass, entry, settings, room_id, name)})
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


def _changed_recipients(hass, entry, room_id, values):
    """The settings with a room's own recipients (``recipients``: a list of the people's ids, or None for everyone
    with a phone); SettingsError notification_person_invalid on ``recipients`` for anything else."""
    from .notifications import house_people, notification_options, room_choice, with_recipients
    settings = notification_options(entry)
    if "recipients" not in values:
        return settings
    wanted = values["recipients"]
    allowed = {*house_people(hass, entry), *(room_choice(settings, room_id) or ())}  # a gone one may stay
    if wanted is not None and (type(wanted) is not list or any(type(p) is not str or p not in allowed for p in wanted)):
        raise SettingsError("notification_person_invalid", "recipients")
    if wanted == room_choice(settings, room_id):
        return settings
    return with_recipients(settings, room_id, wanted)


SAVE_KEYS = {"house": {"on", "problems", "maintenance"}, "person": {"phone", "house_too"}, "room": {"recipients"}}


def save_notifications_section(hass, entry, item, values):
    """A save of the house's screen, of one person's, or of a room's recipients (the room screen); the overview, the
    people and the rooms have none (unknown_section). Only the item's keys; nothing is written when nothing
    changed."""
    from .notifications import notification_options, save_notifications
    if item == "house":
        kind, person = "house", None
    elif type(item) is str and item.startswith(PERSON):
        kind, person = "person", _person_id(hass, entry, item)
    elif type(item) is str and item.startswith(ROOM):
        kind, person = "room", _room_id(hass, entry, item)[0]
    else:
        raise SettingsError("unknown_section")
    if type(values) is not dict or set(values) - SAVE_KEYS[kind]:
        raise SettingsError("notification_invalid")
    if kind == "room":
        settings = _changed_recipients(hass, entry, person, values)
    else:
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


@callback
def add_recipients(hass, entry):
    """1.4.2, once: each room whose notifications are on gets its persons (person and device tracker ids,
    notifications.room_people) as its own recipients, so the same people keep getting its messages after the update;
    from then on the two lists are apart. A room without such persons gets no list (everyone with a phone, as before).
    Written only when it copies something, with the marker RECIPIENTS_ADDED (notifications.save_notifications sets it
    on every later save too), without a reload; True when it wrote."""
    from .const import DOMAIN
    from .energy_input import ENERGY_ONLY_UPDATE
    from .notifications import CONF_NOTIFICATIONS, RECIPIENTS_ADDED, room_people
    options = dict(getattr(entry, "options", None) or {})
    raw = options.get(CONF_NOTIFICATIONS)
    rooms = raw.get("rooms") if type(raw) is dict else None
    if options.get(RECIPIENTS_ADDED) is True or type(rooms) is not dict:
        return False
    copied = {}
    for room_id, room in rooms.items():
        if type(room) is dict and room.get("on") is True and "recipients" not in room:
            if people := room_people(entry, room_id):
                copied[room_id] = {**room, "recipients": people}
    if not copied:
        return False
    new = {**options, RECIPIENTS_ADDED: True, CONF_NOTIFICATIONS: {**raw, "rooms": {**rooms, **copied}}}
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
