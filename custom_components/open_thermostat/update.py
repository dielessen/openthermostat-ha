"""Update platform: E32 firmware through Home Assistant (firmware_update.py)."""
from .firmware_update import async_setup_firmware_update

# Home Assistant may run this platform's actions in parallel (R4-15): every E32 sign-in of the integration,
# the firmware entity's version read and install included, passes one gate (controller_link.SessionGate: at
# most two E32 web sessions at once, 1.4.2). A limit of 1 here would hold every other write behind a wait for
# a free E32 web session (R4-02).
PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    from .product import is_product
    options = {}
    if is_product(entry):
        from .installation_group import ensure_installation_group
        options["config_subentry_id"] = ensure_installation_group(hass, entry)
    await async_setup_firmware_update(hass, entry, async_add_entities, **options)
