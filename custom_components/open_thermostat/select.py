"""Select platform: E32 room state (active / inactive) through the room plan (room_plan.py),
the heating curve's flow at −10 °C (e32_flow.py), the house mode (e32_house.py) and (E32 1.1) each
heating circuit's pump mode (e32_shelly.py)."""
from .const import DOMAIN
from .room_plan import async_setup_selects

# Home Assistant may run this platform's actions in parallel (R4-15): every E32 request goes through the
# entry's RoomPlanLink, which signs in once at a time and lets a newer write supersede one that waits for
# a free E32 web session (R4-02). A limit of 1 here would hold every other write behind such a wait.
PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    await async_setup_selects(hass, entry, async_add_entities)
    from .e32_house import async_setup_selects as async_setup_house_selects
    await async_setup_house_selects(hass, entry, async_add_entities)
    if "v1_runtime" in hass.data.get(DOMAIN, {}).get(entry.entry_id, {}):
        from .e32_flow import async_setup_selects as async_setup_flow_selects
        await async_setup_flow_selects(hass, entry, async_add_entities)
        from .e32_boiler_settings_entities import async_setup_platform
        await async_setup_platform(hass, entry, async_add_entities, "select")  # boiler settings verified here
        from .e32_shelly import async_setup_selects as async_setup_circuit_selects
        await async_setup_circuit_selects(hass, entry, async_add_entities)
