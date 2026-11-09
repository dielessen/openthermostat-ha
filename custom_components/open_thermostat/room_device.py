"""What a room's device says it is: "Room on the E32: radiators" or "... floor heating", with the E32's version.

Every E32 room has its own device in Home Assistant (heating_link.RoomEntity). Its model names what the room is,
from the room's emitter: the room plan Home Assistant read last (room_plan.RoomPlanLink), else the emitter the E32
sends with what it learned about the room (``learned/<room id>``, "radiator" or "floor"). Without either (a first
start, firmware that sends neither) the model is "Room on the E32", and a model with an emitter that was written
before is kept. The device's software version is the E32's firmware version (the E32 device's ``sw_version``,
which the update entity sets).

The model never stays stale (1.3):

- every room entity checks its device when the E32 reports (heating_link.RoomEntity._follow_name), so a room
  renamed or switched between radiators and floor heating shows it as soon as Home Assistant knows;
- a plan read checks every room device (room_plan.RoomPlanLink._set);
- a new E32 version updates every room device (firmware_update.E32FirmwareUpdate._sync_device_version);
- a room entity added again (a restart) gives the same model (RoomEntity.device_info).

The model is written in Home Assistant's language (English, Dutch or Polish); a model written in another language
is replaced at the next check. Only this entry's own room devices are changed, and only their model and software
version: a user's own name or area is never touched.
"""
from __future__ import annotations

import logging

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
EMITTERS = ("radiator", "floor")
# The room device's model per language: without a known emitter, and per emitter (the room form's words).
TEXT = {
    "en": {"room": "Room on the E32", "radiator": "Room on the E32: radiators",
           "floor": "Room on the E32: floor heating"},
    "nl": {"room": "Ruimte op de E32", "radiator": "Ruimte op de E32: radiatoren",
           "floor": "Ruimte op de E32: vloerverwarming"},
    "pl": {"room": "Pomieszczenie w E32", "radiator": "Pomieszczenie w E32: grzejniki",
           "floor": "Pomieszczenie w E32: ogrzewanie podłogowe"},
}


def language(hass):
    value = str(getattr(getattr(hass, "config", None), "language", "en") or "en").split("-")[0]
    return value if value in TEXT else "en"


def room_emitter(hub, room_id):
    """"radiator" or "floor" for one room: the plan read last, else what the E32 learned; None when unknown."""
    plan = getattr(getattr(hub, "plan", None), "plan", None)
    rooms = plan.get("rooms") if isinstance(plan, dict) else None
    for room in rooms if isinstance(rooms, list) else []:
        if isinstance(room, dict) and room.get("id") == room_id and room.get("emitter") in EMITTERS:
            return room["emitter"]
    learned = (getattr(hub, "learned", None) or {}).get(room_id)
    emitter = learned.get("emitter") if isinstance(learned, dict) else None
    return emitter if emitter in EMITTERS else None


def _emitter_of_model(model):
    """The emitter a model we wrote names (any language), or None."""
    for texts in TEXT.values():
        for key in EMITTERS:
            if model == texts[key]:
                return key
    return None


def room_model(hass, emitter, current=None):
    """The model for a room with this emitter; with an unknown one, the emitter of ``current`` (a model we wrote)."""
    texts = TEXT[language(hass)]
    if emitter not in EMITTERS:
        emitter = _emitter_of_model(current)
    return texts[emitter] if emitter in EMITTERS else texts["room"]


def e32_version(hass, entry_id, prefix):
    """The E32's firmware version as its device shows it, or None."""
    device = dr.async_get(hass).async_get_device_by_identifier((DOMAIN, prefix), entry_id)
    return device.sw_version if device is not None else None


def device_fields(hass, entry_id, hub, room_id, current=None):
    """{"model": ..., "sw_version": ...} for one room's device (no sw_version while the E32's is unknown)."""
    fields = {"model": room_model(hass, room_emitter(hub, room_id), getattr(current, "model", None))}
    version = e32_version(hass, entry_id, hub.prefix)
    if version:
        fields["sw_version"] = version
    return fields


@callback
def sync_room_device(hass, hub, room_id, device):
    """Bring one room device's model and software version up to date; True when it changed."""
    if device is None:
        return False
    wanted = device_fields(hass, device.config_entry_id, hub, room_id, device)
    changes = {key: value for key, value in wanted.items() if getattr(device, key) != value}
    if changes:
        dr.async_get(hass).async_update_device(device.id, **changes)
    return bool(changes)


@callback
def sync_room_devices(hass, entry, hub):
    """Every room device of this entry; returns the room ids whose device changed. Never raises: a plan read or
    a version update is never held up by a label."""
    if hub is None:
        return []
    changed = []
    try:
        head = f"{hub.prefix}_e32_room_"
        for device in dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id):
            room_ids = [identifier.removeprefix(head) for domain, identifier in device.identifiers
                        if domain == DOMAIN and identifier.startswith(head)]
            if len(room_ids) == 1 and device.config_entry_id == entry.entry_id and sync_room_device(
                    hass, hub, room_ids[0], device):
                changed.append(room_ids[0])
    except Exception:
        _LOGGER.debug("Could not update the E32 room devices", exc_info=True)
    return changed
