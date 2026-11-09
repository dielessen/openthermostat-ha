"""Update platform: E32 firmware through Home Assistant (firmware_update.py)."""
from .firmware_update import async_setup_firmware_update

# Home Assistant may run this platform's actions in parallel (R4-15): every E32 request goes through the
# entry's RoomPlanLink, which signs in once at a time and lets a newer write supersede one that waits for
# a free E32 web session (R4-02). A limit of 1 here would hold every other write behind such a wait.
PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    from .product import is_product
    options = {}
    if is_product(entry):
        from .installation_group import ensure_installation_group
        options["config_subentry_id"] = ensure_installation_group(hass, entry)
    await async_setup_firmware_update(hass, entry, async_add_entities, **options)
