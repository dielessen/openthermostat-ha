"""The settings panel's section Notifications (1.4; settings.py registers it, the screen is
frontend/openthermostat-settings-notifications.js).

One screen with Configure → Notifications' three forms together: People (per person the phone or app that gets the
messages, and the tick "Also messages about the house"), The house (the switch, its problems and its maintenance) and
Rooms (per room the switch and its messages). Home Assistant keeps these (the entry's options); nothing is read from
the E32.

The model:

- ``people``: ``[{id, name, phone, house, suggested}]``, everyone a phone can be chosen for
  (notifications.house_people); ``phone`` is the chosen notify service or ``"none"``, ``suggested`` the app on the
  person's own phone (the form's default while none is chosen) or null.
- ``phones``: ``[{service, app}]``, the notify services that reach one phone or app; ``app`` is the phone's name for a
  Home Assistant app (the panel words it "<name> (Home Assistant app)" in the viewer's language), else null.
- ``house``: ``{on, problems, maintenance}``; ``rooms``: ``[{id, name, on, kinds, people}]`` in the order of the
  form (by name), ``people`` the names of the room's own persons (empty: everyone with a phone).
- ``kinds``: the message kinds in their order (``room``, ``problems``, ``maintenance``).

Save takes the screen's values (``phone:<person>``, ``house:<person>``, ``house_on``, ``house_problems``,
``house_maintenance``, ``room:<room>``, ``kinds:<room>``; a value left out keeps what is shown) and changes the
settings with the forms' own checks (notifications_flow.changed_person, changed_house, changed_room): a room or the
house that is shown unchanged is not touched, so the panel stores exactly what the three forms store for the same
input. Errors carry the panel's field (``phone:<person>``, ``house_problems``, ``kinds:<room>``).
"""
from __future__ import annotations

from .settings import SettingsError, register_section

# The overview's line (the words of Configure → Notifications: "On now: the house, Woonkamer").
WORDS = {"en": {"on": "On: {what}", "off": "Off", "house": "the house"},
         "nl": {"on": "Aan: {what}", "off": "Uit", "house": "het huis"},
         "pl": {"on": "Włączone: {what}", "off": "Wyłączone", "house": "dom"}}


def read_notifications(hass, entry, item=None):
    from .notifications import (HOUSE_MAINTENANCE, HOUSE_PROBLEMS, ROOM_KINDS, house_people, notification_options,
                                phone_apps, room_people, suggested_phone)
    from .notifications_flow import NO_PHONE, notify_rooms, person_name, shown_room
    if item is not None:
        raise SettingsError("unknown_section")
    settings, apps = notification_options(entry), phone_apps(hass)
    services = dict.fromkeys(apps, "")
    people = [{"id": person, "name": person_name(hass, person),
               "phone": settings["phones"].get(person) or NO_PHONE, "house": person in settings["house_people"],
               "suggested": None if settings["phones"].get(person) else suggested_phone(hass, person, services)}
              for person in house_people(hass, entry)]
    house = settings["house"]
    rooms = []
    for room_id, name in notify_rooms(hass, entry):
        shown = shown_room(settings, room_id)
        rooms.append({"id": room_id, "name": name, "on": shown["on"], "kinds": list(shown["kinds"]),
                      "people": [person_name(hass, p) for p in room_people(entry, room_id)]})
    return {"people": people, "phones": [{"service": s, "app": a} for s, a in apps.items()],
            "house": {"on": house["on"], "problems": [k for k in house["kinds"] if k in HOUSE_PROBLEMS],
                      "maintenance": [k for k in house["kinds"] if k in HOUSE_MAINTENANCE]},
            "rooms": rooms,
            "kinds": {"room": list(ROOM_KINDS), "problems": list(HOUSE_PROBLEMS), "maintenance": list(HOUSE_MAINTENANCE)}}


def _known(model):
    keys = {"house_on", "house_problems", "house_maintenance"}
    for person in model["people"]:
        keys |= {f"phone:{person['id']}", f"house:{person['id']}"}
    for room in model["rooms"]:
        keys |= {f"room:{room['id']}", f"kinds:{room['id']}"}
    return keys


def changed_settings(hass, entry, values):
    """The notification settings after the panel's values, checked as the three forms check them (FlowError with the
    panel's field)."""
    from .e32_room_flow import FlowError
    from .notifications import notification_options, phone_apps
    from .notifications_flow import changed_house, changed_person, changed_room, phone_choices, shown_room
    model = read_notifications(hass, entry)
    if type(values) is not dict or set(values) - _known(model):
        raise SettingsError("notification_invalid")
    settings = notification_options(entry)
    services = dict.fromkeys(phone_apps(hass), "")
    texts = {"no_phone": "", "phone_gone": "{service}"}  # labels are the panel's; only the choices' keys count here
    for person in model["people"]:
        pid = person["id"]
        chosen, house = values.get(f"phone:{pid}", person["phone"]), values.get(f"house:{pid}", person["house"])
        try:
            settings = changed_person(settings, pid, chosen, house, phone_choices(settings, services, pid, texts))
        except FlowError as err:
            raise SettingsError(err.key, f"phone:{pid}" if err.field == "phone" else f"house:{pid}") from None
    shown = model["house"]
    on = values.get("house_on", shown["on"])
    problems = values.get("house_problems", shown["problems"])
    maintenance = values.get("house_maintenance", shown["maintenance"])
    if (on, problems, maintenance) != (shown["on"], shown["problems"], shown["maintenance"]):
        try:
            settings = changed_house(settings, on, problems, maintenance)
        except FlowError as err:
            raise SettingsError(err.key, "house_problems" if err.field == "kinds" else "base") from None
    for room in model["rooms"]:
        rid = room["id"]
        on, kinds = values.get(f"room:{rid}", room["on"]), values.get(f"kinds:{rid}", room["kinds"])
        if {"on": on, "kinds": kinds} == shown_room(settings, rid):
            continue
        try:
            settings = changed_room(settings, rid, on, kinds)
        except FlowError as err:
            raise SettingsError(err.key, f"kinds:{rid}" if err.field == "kinds" else f"room:{rid}") from None
    return settings


def save_notifications_section(hass, entry, item, values):
    from .notifications import notification_options, save_notifications
    if item is not None:
        raise SettingsError("unknown_section")
    settings = changed_settings(hass, entry, values)
    if settings != notification_options(entry):
        save_notifications(hass, entry, settings)  # the forms' own write: no reload, the notifier checks at once
    return read_notifications(hass, entry)


def summary_notifications(hass, entry, hub, lang):
    """"Off" until something is on; then what is on, as Configure says it ("On: the house, Woonkamer")."""
    from .notifications import notification_options
    from .notifications_flow import notify_rooms
    words, settings = WORDS[lang], notification_options(entry)
    rooms = [room_id for room_id, room in settings["rooms"].items() if room["on"]]
    known = notify_rooms(hass, entry)  # by name, as the form lists them; a room the E32 does not report: its id
    on = ([words["house"]] if settings["house"]["on"] else []) + [name for room_id, name in known if room_id in rooms]
    on += sorted(set(rooms) - {room_id for room_id, _ in known})
    return [words["on"].format(what=", ".join(on)) if on else words["off"]]


register_section("notifications", read_notifications, save_notifications_section, summary=summary_notifications)
