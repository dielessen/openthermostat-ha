"""Configure → Notifications: who gets a message on which phone, about which rooms and about the house.

- People and phones: per person the phone or app (a ``notify`` service) that gets the messages; the app on
  the person's own phone is suggested. Without a phone, a message shows in Home Assistant instead. And the
  tick "Also messages about the house" (off by default): only the people with it get the house messages.
- The house: one switch and the house messages in two groups, Problems (notifications.HOUSE_PROBLEMS) and
  Maintenance (notifications.HOUSE_MAINTENANCE). With the switch on and nobody ticked, the step says so and the
  messages show in Home Assistant.
- Rooms: pick a room, then one switch "Notify about this room" and its messages (notifications.ROOM_KINDS).
  The room's own recipients get them (1.4.2: chosen on the room's screen on the Settings tab, apart from its
  persons for presence); the step says who in one sentence (settings_notifications.recipients_line).

Nothing is on by default. Saving stores the settings without a reload (notifications.save_notifications).

The checks and changes of the three forms are module functions (changed_person, changed_house, changed_room,
phone_choices, notify_rooms), shared with the settings panel's section Notifications (settings_notifications.py, 1.4);
room_change and room_recipients also with the panel's room screen (settings_rooms.py, 1.4.1).
"""
from __future__ import annotations

import probatio as vol
from homeassistant.helpers import selector

from .const import DOMAIN
from .notifications import (HOUSE_MAINTENANCE, HOUSE_PROBLEMS, ROOM_KINDS, house_people, notification_options,
                            phone_services, save_notifications, suggested_phone, with_house, with_house_person,
                            with_phone, with_room)
from .e32_room_flow import FlowError
from .options_navigation import async_flow_texts

NO_PHONE = "none"


def _kinds_selector(key, kinds=ROOM_KINDS):
    return selector.SelectSelector({"options": list(kinds), "multiple": True, "mode": "list", "translation_key": key})


# -- shared with the settings panel (settings_notifications.py, 1.4): one check and one change for both ---------------


def notify_rooms(hass, entry):
    """[(room id, name)] of the E32's rooms, by the name the dashboard shows, sorted by name."""
    hub = (hass.data.get(DOMAIN, {}).get(entry.entry_id) or {}).get("heating_hub")
    if hub is None:
        return []
    from .insight import room_names
    names = room_names(hub, hass, entry.entry_id)
    return sorted(((room_id, names.get(room_id) or room_id) for room_id in hub.rooms), key=lambda r: r[1].lower())


def person_name(hass, person):
    state = hass.states.get(person)
    return state.name if state is not None else person


def phone_label(service, services, texts):
    if not service:
        return texts["no_phone"]
    return services.get(service) or texts["phone_gone"].format(service=f"notify.{service}")


def phone_choices(settings, services, person, texts):
    """{value: label} of a person's phone: No phone, every phone or app, and a chosen one that is gone (it stays
    visible, so saving the form unchanged keeps it)."""
    current = settings["phones"].get(person)
    choices = {NO_PHONE: texts["no_phone"], **services}
    if current and current not in choices:
        choices[current] = phone_label(current, services, texts)
    return choices


def changed_person(settings, person, chosen, house, choices):
    """The settings with this person's phone (a key of choices; NO_PHONE: none) and the tick "Also messages about the
    house"; FlowError notification_phone_invalid on "phone", or notification_invalid for a tick that is no bool."""
    if chosen not in choices:
        raise FlowError("notification_phone_invalid", "phone")
    if type(house) is not bool:
        raise FlowError("notification_invalid")
    return with_house_person(with_phone(settings, person, None if chosen == NO_PHONE else chosen), person, house)


def changed_house(settings, on, problems, maintenance):
    """The settings with the house switch and its messages (problems and maintenance); FlowError
    notification_invalid, or notification_kinds_needed on "kinds" when it is switched on without a message."""
    if (type(on) is not bool or type(problems) is not list or type(maintenance) is not list
            or any(k not in HOUSE_PROBLEMS for k in problems) or any(k not in HOUSE_MAINTENANCE for k in maintenance)):
        raise FlowError("notification_invalid")
    if on and not problems and not maintenance:
        raise FlowError("notification_kinds_needed", "kinds")
    return with_house(settings, on, [*problems, *maintenance])


def shown_room(settings, room_id):
    """A room's switch and messages as the form shows them (every message chosen until the room was set once)."""
    return settings["rooms"].get(room_id) or {"on": False, "kinds": list(ROOM_KINDS)}


def changed_room(settings, room_id, on, kinds):
    """The settings with one room's switch and messages; FlowError notification_invalid, or
    notification_kinds_needed on "kinds" when it is switched on without a message."""
    if type(on) is not bool or type(kinds) is not list or any(k not in ROOM_KINDS for k in kinds):
        raise FlowError("notification_invalid")
    if on and not kinds:
        raise FlowError("notification_kinds_needed", "kinds")
    return with_room(settings, room_id, on, kinds)


def room_change(settings, room_id, on, kinds):
    """The settings after one room's switch and messages, or None when the room stays as shown (the forms' and the
    settings panel's "unchanged": nothing is stored). Raises FlowError as changed_room."""
    changed = changed_room(settings, room_id, on, kinds)
    return None if changed["rooms"][room_id] == shown_room(settings, room_id) else changed


def room_recipients(hass, entry, room_id):
    """The names of the people chosen for this room's messages whom Home Assistant still knows (1.4.2: the room's
    own recipients); empty: everyone with a phone, nobody, or nobody left (settings_notifications.recipients_line
    says which, in a sentence)."""
    from .notifications import person_found, room_choice
    return [person_name(hass, p) for p in room_choice(notification_options(entry), room_id) or ()
            if person_found(hass, p)]


class NotificationOptionsSteps:
    """Mixin of the product options flow."""

    def _notify_rooms(self):
        return notify_rooms(self.hass, self.config_entry)

    def _person_name(self, person):
        return person_name(self.hass, person)

    def _phone_label(self, service, services, texts):
        return phone_label(service, services, texts)

    async def async_step_notifications(self, user_input=None):
        """The menu, with what is switched on now and who gets what."""
        texts = await async_flow_texts(self.hass, "notification_text")
        settings = notification_options(self.config_entry)
        services = phone_services(self.hass)
        people = [f"- {self._person_name(p)}: {self._phone_label(settings['phones'].get(p), services, texts)}"
                  + (texts["with_house"] if p in settings["house_people"] else "")
                  for p in house_people(self.hass, self.config_entry)]
        rooms = [name for room_id, name in self._notify_rooms() if settings["rooms"].get(room_id, {}).get("on")]
        on = [*([texts["house"]] if settings["house"]["on"] else []), *rooms]
        return self.async_show_menu(step_id="notifications", menu_options=["notify_people", "notify_house", "notify_rooms"],
                                    description_placeholders={
                                        "on": ", ".join(on) if on else texts["nothing_on"],
                                        "people": "\n".join(people) if people else texts["no_people"]})

    async def async_step_notify_people(self, user_input=None):
        """Pick the person whose phone to choose."""
        people = house_people(self.hass, self.config_entry)
        if not people:
            return self.async_abort(reason="notifications_no_people")
        texts = await async_flow_texts(self.hass, "notification_text")
        settings, services = notification_options(self.config_entry), phone_services(self.hass)
        errors = {}
        if user_input is not None:
            if user_input.get("person") in people:
                self._notify_person = user_input["person"]
                return await self.async_step_notify_person()
            errors["person"] = "notification_person_invalid"
        options = [{"value": p, "label": f"{self._person_name(p)}: "
                                         f"{self._phone_label(settings['phones'].get(p), services, texts)}"
                                         + (texts["with_house"] if p in settings["house_people"] else "")}
                   for p in people]
        return self.async_show_form(step_id="notify_people", errors=errors, data_schema=vol.Schema({
            vol.Required("person", default=people[0]): selector.SelectSelector({"options": options, "mode": "list"})}))

    async def async_step_notify_person(self, user_input=None):
        """The phone or app of one person (a notify service), or none, and the tick "Also messages about the house"."""
        person = getattr(self, "_notify_person", None)
        if person is None:
            return await self.async_step_notify_people()
        texts = await async_flow_texts(self.hass, "notification_text")
        settings, services = notification_options(self.config_entry), phone_services(self.hass)
        current = settings["phones"].get(person)
        choices = phone_choices(settings, services, person, texts)  # a phone that is gone stays visible
        ticked = person in settings["house_people"]
        errors = {}
        if user_input is not None:
            try:
                changed = changed_person(settings, person, user_input.get("phone"), user_input.get("house", ticked),
                                         choices)
            except FlowError as err:
                errors[err.field] = err.key
            else:
                if changed == settings:
                    return self.async_abort(reason="notifications_unchanged")
                save_notifications(self.hass, self.config_entry, changed)
                return self.async_abort(reason="notifications_saved")
        default = current or suggested_phone(self.hass, person, services) or NO_PHONE
        return self.async_show_form(step_id="notify_person", errors=errors, data_schema=vol.Schema({
            vol.Required("phone", default=default): selector.SelectSelector({
                "options": [{"value": k, "label": v} for k, v in choices.items()], "mode": "dropdown"}),
            vol.Required("house", default=ticked): selector.BooleanSelector()}),
            description_placeholders={"person": self._person_name(person)})

    async def async_step_notify_house(self, user_input=None):
        """One switch and the house messages: Problems and Maintenance; says who gets them."""
        texts = await async_flow_texts(self.hass, "notification_text")
        settings = notification_options(self.config_entry)
        house = settings["house"]
        errors = {}
        if user_input is not None:
            try:
                changed = changed_house(settings, user_input.get("on"), user_input.get("kinds") or [],
                                        user_input.get("maintenance") or [])
            except FlowError as err:
                errors[err.field] = err.key
            else:
                if changed["house"] == house:
                    return self.async_abort(reason="notifications_unchanged")
                save_notifications(self.hass, self.config_entry, changed)
                return self.async_abort(reason="notifications_saved")
        receivers = [self._person_name(p) for p in settings["house_people"]]
        who = texts["house_people"].format(people=", ".join(receivers)) if receivers else texts["house_nobody"]
        schema = vol.Schema({
            vol.Required("on", default=house["on"]): selector.BooleanSelector(),
            vol.Required("kinds", default=[k for k in house["kinds"] if k in HOUSE_PROBLEMS]):
                _kinds_selector("notification_house_kind", HOUSE_PROBLEMS),
            vol.Required("maintenance", default=[k for k in house["kinds"] if k in HOUSE_MAINTENANCE]):
                _kinds_selector("notification_house_kind", HOUSE_MAINTENANCE)})
        if user_input is not None:
            schema = self.add_suggested_values_to_schema(schema, user_input)
        return self.async_show_form(step_id="notify_house", data_schema=schema, errors=errors,
                                    description_placeholders={"who": who})

    async def async_step_notify_rooms(self, user_input=None):
        """Pick the room first, so the form below always belongs to the room it names."""
        rooms = self._notify_rooms()
        if not rooms:
            return self.async_abort(reason="notifications_no_rooms")
        texts = await async_flow_texts(self.hass, "notification_text")
        settings = notification_options(self.config_entry)
        errors = {}
        if user_input is not None:
            if user_input.get("room") in dict(rooms):
                self._notify_room = user_input["room"]
                return await self.async_step_notify_room()
            errors["room"] = "room_invalid"
        options = [{"value": room_id, "label": f"{name}: {texts['on'] if settings['rooms'].get(room_id, {}).get('on') else texts['off']}"}
                   for room_id, name in rooms]
        return self.async_show_form(step_id="notify_rooms", errors=errors, data_schema=vol.Schema({
            vol.Required("room", default=rooms[0][0]): selector.SelectSelector({"options": options, "mode": "list"})}))

    async def async_step_notify_room(self, user_input=None):
        rooms = dict(self._notify_rooms())
        room_id = getattr(self, "_notify_room", None)
        if room_id not in rooms:
            return await self.async_step_notify_rooms()
        texts = await async_flow_texts(self.hass, "notification_text")
        settings = notification_options(self.config_entry)
        room = shown_room(settings, room_id)
        errors = {}
        if user_input is not None:
            try:  # shared with the settings panel's room screen (settings_rooms.py)
                changed = room_change(settings, room_id, user_input.get("on"), user_input.get("kinds") or [])
            except FlowError as err:
                errors[err.field] = err.key
            else:
                if changed is None:
                    return self.async_abort(reason="notifications_unchanged")
                save_notifications(self.hass, self.config_entry, changed)
                return self.async_abort(reason="notifications_saved")
        from .heating_advice import language
        from .settings_notifications import recipients_line
        who = recipients_line(self.hass, self.config_entry, settings, room_id, rooms[room_id])
        schema = vol.Schema({vol.Required("on", default=room["on"]): selector.BooleanSelector(),
                             vol.Required("kinds", default=room["kinds"]): _kinds_selector("notification_room_kind")})
        if user_input is not None:
            schema = self.add_suggested_values_to_schema(schema, user_input)
        return self.async_show_form(step_id="notify_room", data_schema=schema, errors=errors,
                                    description_placeholders={"room": rooms[room_id],
                                                              "who": who.get(language(self.hass), who["en"])})
