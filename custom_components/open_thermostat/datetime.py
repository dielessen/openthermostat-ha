"""Datetime platform: E32 room "inactive until" through the room plan (room_plan.py) and the
house's "Holiday until" (e32_house.py)."""
from .e32_house import async_setup_datetimes as async_setup_house_datetimes
from .room_plan import async_setup_datetimes

# Home Assistant may run this platform's actions in parallel (R4-15): every E32 sign-in of the integration
# passes one gate (controller_link.SessionGate: at most two E32 web sessions at once, 1.4.2); the entry's
# RoomPlanLink signs in once at a time and lets a newer write supersede one that waits for a free E32 web
# session (R4-02). A limit of 1 here would hold every other write behind such a wait.
PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    await async_setup_datetimes(hass, entry, async_add_entities)
    await async_setup_house_datetimes(hass, entry, async_add_entities)
