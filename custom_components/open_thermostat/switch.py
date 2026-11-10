"""Switches of an E32 product entry: the flow options (weather curve, learned flow and optimum start)
and the valve control of each room with radiator valves (e32_valves.py)."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN

# Home Assistant may run this platform's actions in parallel (R4-15): every E32 sign-in of the integration
# passes one gate (controller_link.SessionGate: at most two E32 web sessions at once, 1.4.2); the entry's
# RoomPlanLink signs in once at a time and lets a newer write supersede one that waits for a free E32 web
# session (R4-02). A limit of 1 here would hold every other write behind such a wait.
PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    if "v1_runtime" not in hass.data.get(DOMAIN, {}).get(entry.entry_id, {}):
        return
    from .e32_flow import async_setup_switches
    await async_setup_switches(hass, entry, async_add_entities)
    from .e32_valves import async_setup_switches as async_setup_valve_switches
    await async_setup_valve_switches(hass, entry, async_add_entities)
    from .e32_boiler_settings_entities import async_setup_platform
    await async_setup_platform(hass, entry, async_add_entities, "switch")  # boiler settings verified here
