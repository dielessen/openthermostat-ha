"""Button platform: back up the E32 settings now (e32_backup.py), restart the E32 (e32_system.py), let the E32
plan the heating (heating_plan.py, only while it is ready for that confirmation) and, 1.4.4, Learn again per room and
for the house (e32_learned.py, once the E32 offers it)."""
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
    from .e32_backup_entities import async_setup_buttons
    await async_setup_buttons(hass, entry, async_add_entities)
    from .e32_system import async_setup_buttons as async_setup_restart_button
    await async_setup_restart_button(hass, entry, async_add_entities)
    from .heating_plan import async_setup_buttons as async_setup_plan_button  # only while the E32 is ready to plan
    await async_setup_plan_button(hass, entry, async_add_entities)
    from .e32_learned import async_setup_buttons as async_setup_relearn_buttons  # 1.4.4: only on firmware with relearn
    await async_setup_relearn_buttons(hass, entry, async_add_entities)
