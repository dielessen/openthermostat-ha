"""Learn again (1.4.4, docs/engineering/RELEASE-1.4.4-PLAN.nl.md 2.3 and chapter 4; the firmware is FW-RELEARN).

After a change to the heating circuit (other radiators, floor heating added) the owner can let the E32 start learning
again on purpose, for one room or for the house:

- a room: how fast it warms up and cools down, its house model, its morning check (ArrivalLearner) and its free heat;
- the house: the weather compensation (CurveLearner), the boiler's highest water and rhythm (BoilerResponse), its
  lowest water (BoilerMinimumFlow) and the self-tuning steps (AutoTuner).

The week programs, the settings and the counters and day records stay. The E32 clears and stores at once (a restart
does not bring it back) and says what it cleared: ``POST /control/learned/reset`` with ``{"room": "<id>"}`` or
``{"house": true}``, answer ``{"cleared": [...], "room" | "house", "stored": bool}``, ``400 unknown_room`` or
``invalid_request``; E32 1.4.3 has no such route (405), so everything here waits for the plan's feature. ``stored``
false (the E32 could not write the record at once) goes to the log, not to the person.

Home Assistant offers it in three places, all asking the same question first where a person taps it:

- a button per room "Learn again" (``<prefix>_e32_room_<room>_relearn``, on the room's device, diagnostic, enabled)
  and one for the house "Learn again: house" (``<prefix>_hub_relearn``, on the E32), created once the E32's room plan
  names the feature ``relearn`` (ENTITY-LIFETIME: kept from then on; firmware without the feature never gets them);
  a button entity has no question of its own (Home Assistant's more-info presses at once): it is the action for
  automations and scripts, the cards and the panel ask;
- the settings panel's action ``relearn`` (``{room}`` on the room's screen, block Learning; ``{house: true}`` under
  Heating and boiler);
- the Learning view's room card: its text button presses the room's button entity after the same question.

Every request goes through the stored E32 connection (RoomPlanLink.async_call: one sign-in, a write waits for a free
E32 web session, controller_link.SessionGate).
"""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError

import logging

from .const import DOMAIN
from .heating_link import HubEntity, RoomEntity, add_options, heating_hub, label, track_entities

_LOGGER = logging.getLogger(__name__)

RELEARN_FEATURE = "relearn"
ENTITY_KEY = "relearn"
# What the E32 says it cleared (plan chapter 4); other words are passed on as they come.
ROOM_PARTS = ("warmup", "cooling", "arrival", "model", "free_heat")
HOUSE_PARTS = ("curve", "boiler", "minimum", "tuner", "steady")


def supported(hub):
    """True once the E32's room plan (GET /config/heating) names the feature ``relearn`` (E32 1.4.4)."""
    from .e32_house import plan_features
    return RELEARN_FEATURE in plan_features(hub)


def _link(hass, entry):
    """(the entry's hub, its room-plan link) as the platforms set them up; never creates one."""
    state = hass.data.get(DOMAIN, {}).get(getattr(entry, "entry_id", None))
    hub = state.get("heating_hub") if isinstance(state, dict) else None
    return hub, getattr(hub, "plan", None)


def _document(room=None, house=False):
    return {"house": True} if house else {"room": room}


async def async_relearn(hass, entry, room=None, house=False):
    """Clear what the E32 learned for ``room`` (its id) or the house; returns the parts it cleared. Raises
    ControllerLinkError (HeatingPlanRejected for a refusal with the E32's word) or LookupError without a link."""
    hub, link = _link(hass, entry)
    if link is None:
        raise LookupError("no_controller_connection")
    answer = await link.async_call(lambda client: client.async_learned_reset(_document(room, house)), write=True)
    if type(answer) is dict and answer.get("stored") is False:
        _LOGGER.warning("The E32 cleared what it learned for %s but could not write the record at once; it writes it "
                        "later, and a restart before that brings the old record back", "the house" if house else room)
    cleared = answer.get("cleared") if type(answer) is dict else None
    return [part for part in cleared if type(part) is str] if type(cleared) is list else []


def _failure_key(err):
    """(the button's exception key, placeholders) of a failed reset."""
    from .controller_link import HeatingPlanRejected
    from .e32_system import failure
    if isinstance(err, HeatingPlanRejected):
        if err.error == "unknown_room":
            return "e32_relearn_unknown_room", None
        return "e32_relearn_failed", {"error": err.error}
    key, placeholders = failure(err)
    if key == "e32_settings_update_required":
        return "e32_relearn_update_required", None
    return {"e32_password_changed": ("room_plan_password", None),
            "e32_settings_no_free_session": ("e32_no_free_session", None),
            "e32_settings_password_default": ("e32_password_change_required", None)}.get(
        key, ("e32_relearn_failed", {"error": placeholders.get("error", key)}))


async def _press(hass, entry, room=None, house=False):
    from .controller_link import ControllerLinkError
    try:
        return await async_relearn(hass, entry, room, house)
    except LookupError:
        from .room_plan import link_error
        raise link_error("no_controller_connection") from None
    except ControllerLinkError as err:
        key, placeholders = _failure_key(err)
        raise HomeAssistantError(translation_domain=DOMAIN, translation_key=key,
                                 translation_placeholders=placeholders) from None


class RoomRelearnButton(RoomEntity, ButtonEntity):
    """"Learn again" of one room: the E32 clears what it learned for this room (its week program stays)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry, hub, room):
        self._entry = entry
        self._attach_room(hub, room, ENTITY_KEY)  # translation key room_relearn, unique id <prefix>_e32_room_<id>_relearn

    async def async_press(self):
        await _press(self.hass, self._entry, room=self.room_id)


class HouseRelearnButton(HubEntity, ButtonEntity):
    """"Learn again: house": the E32 clears what it learned about the whole house (the week programs stay)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_translation_key = "hub_relearn"

    def __init__(self, entry, hub):
        self._entry = entry
        self._attach(hub, "hub_relearn")

    @property
    def available(self):
        return self.hub.fresh

    async def async_press(self):
        await _press(self.hass, self._entry, house=True)


def wanted(entry):
    def wanted_buttons(hub):
        """Once the plan names ``relearn``: the house's button and one per room (kept after that: track_entities
        never removes what it made; a room that leaves the plan goes with its device)."""
        if not supported(hub):
            return
        yield ("relearn_house",), lambda: HouseRelearnButton(entry, hub)
        for room_id, room in hub.known_rooms.items():
            yield ("relearn", room_id), lambda room=room: RoomRelearnButton(entry, hub, room)
    return wanted_buttons


async def async_setup_buttons(hass, entry, async_add_entities):
    """Product entries with an E32 room plan: the Learn again buttons, as soon as the E32 offers it."""
    from .product import is_product
    if not is_product(entry):
        return
    hub = heating_hub(hass, entry)
    if hub is None:
        return
    entry.async_on_unload(track_entities(hub, async_add_entities, add_options(hass, entry), wanted(entry)))


# -- the settings panel's action (CONTRACT: action ``relearn`` with {room} or {house: true}) ----------------------------


async def relearn_action(hass, entry, item, values):
    """settings/action ``relearn``: ``{room}`` (or the item, the room's screen) or ``{house: true}``. Answers
    ``{"cleared": [...], "room": id}`` or ``{"cleared": [...], "house": true}``. Refusals: ``relearn_update_required``
    (firmware without it), ``e32_room_missing``, ``e32_password_changed``, ``relearn_no_free_session``,
    ``relearn_failed`` ({error})."""
    from .controller_link import ControllerLinkError, HeatingPlanRejected
    from .e32_system import failure
    from .settings import SettingsError
    house = values.get("house") is True
    room = None if house else (values.get("room") if type(values.get("room")) is str else item)
    hub, link = _link(hass, entry)
    if hub is None or link is None:
        raise SettingsError("unavailable")
    if not supported(hub):
        raise SettingsError("relearn_update_required")
    if not house:
        plan = getattr(link, "plan", None)
        rooms = {r.get("id") for r in (plan.get("rooms") or []) if type(r) is dict} if type(plan) is dict else set()
        if type(room) is not str or not room or room not in rooms:
            raise SettingsError("e32_room_missing", room=str(room))
    try:
        cleared = await async_relearn(hass, entry, room, house)
    except HeatingPlanRejected as err:
        if err.error == "unknown_room":
            raise SettingsError("e32_room_missing", room=str(room)) from None
        raise SettingsError("relearn_failed", error=err.error) from None
    except ControllerLinkError as err:
        key, placeholders = failure(err)
        if key == "e32_settings_update_required":
            raise SettingsError("relearn_update_required") from None
        if key == "e32_password_changed":
            raise SettingsError("e32_password_changed") from None
        if key == "e32_settings_no_free_session":
            raise SettingsError("relearn_no_free_session") from None
        raise SettingsError("relearn_failed", error=placeholders.get("error", key)) from None
    return {"cleared": cleared, **({"house": True} if house else {"room": room})}


def room_name(hub, room_id):
    room = (getattr(hub, "rooms", None) or {}).get(room_id)
    return label(room) if room else room_id


def _register():
    from .settings import register_section
    register_section("rooms", actions={"relearn": relearn_action})
    register_section("heating", actions={"relearn": relearn_action})


_register()
