"""Retire the MQTT discovery entities that pre-v1 E32 firmware left on the broker (beta.23).

Before the v1 link the firmware announced its own Home Assistant entities with
MQTT discovery (homeassistant/<component>/<prefix>/<object>/config, retained):
"opth_*" boiler, metric and device values, per-room values and a status
sensor, on a device "OpenThermostat". A v1 E32 never sends them again (the
legacy MQTT reporter is not started in modern mode), but the retained configs
stay on the broker, so the MQTT integration keeps re-creating some 45
"unavailable" entities next to this integration's own (the owner's HA, 1 Nov
2026: sensor.ib_therm_opth_warm_water_usage and friends).

They belong to the MQTT integration, so this integration never touches their
registry entries. It retires them the way MQTT discovery itself defines: an
empty retained payload on the config topic, after which the MQTT integration
removes the entity (its history stays in the recorder). Only configs this E32's
old firmware wrote (node ID = the prefix, device identifiers exactly [prefix],
unique ID the prefix or prefix_..., state topic under the old prefix/ and not
prefix/v1/), only on a product (v1) entry, once, RETIRE_AFTER_S after setup, and
never for an entity the user changed (name, icon, area, labels, own entity ID,
or disabled or hidden by the user): that one stays as it is.

1.4.5 (docs/engineering/LEGACY-RETIREMENT.md): the old firmware used its own MQTT base as the node ID, and
Connect E32 replaces that base with the prefix. When they differ (a base typed on the E32 page, or the
firmware's "open_thermostat" for an empty one), Connect E32 records the old base on the entry
(LEGACY_BASE) and the same retirement covers it: right after the link, and again at every start, which is
safe because a cleared config is gone (nothing is found the next time). Under the old base the retained
"<base>/status" of the old firmware goes too, unless the user kept one of its entities. Never a base that
another, older-route entry of this integration still uses (the generic boards keep that route).
"""
import json
import logging
import re

from homeassistant.components import mqtt
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_call_later

from .const import CONF_TOPIC_PREFIX, DOMAIN

_LOGGER = logging.getLogger(__name__)
RETIRE_AFTER_S = 600
COMPONENTS = ("sensor", "binary_sensor", "button", "climate", "number", "select", "switch")
# The entry's record of the E32's MQTT base before Connect E32 (only when it differs from the prefix).
LEGACY_BASE = "legacy_mqtt_base"
# What the old firmware used for an empty base (src/MQTT.h, the legacy upstream route).
FIRMWARE_DEFAULT_BASE = "open_thermostat"
NODE_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def pre_link_base(settings, prefix):
    """The E32's MQTT base before Connect E32, if the old firmware could have announced entities under it.

    settings: the device settings as read before the link (GET /config/device). None when the E32 was
    already linked (its base is then the integration's), when the base is the prefix, or when it cannot
    be an MQTT discovery node ID.
    """
    mqtt = settings.get("mqtt") if type(settings) is dict else None
    if type(mqtt) is not dict or mqtt.get("modern_shadow") is True:
        return None
    base = mqtt.get("base")
    if base is None or base == "":
        base = FIRMWARE_DEFAULT_BASE
    if type(base) is not str or NODE_ID.fullmatch(base) is None or base == prefix:
        return None
    return base


def _older_route_uses(hass, entry, node):
    """Another entry of this integration on the older route (the generic boards) still reads this base."""
    from .product import is_product
    return any(other.entry_id != entry.entry_id and not is_product(other)
               and (other.data or {}).get(CONF_TOPIC_PREFIX) == node
               for other in hass.config_entries.async_entries(DOMAIN))


def retired_nodes(hass, entry):
    """The node IDs whose old discovery configs this entry retires: its prefix, and its recorded old base."""
    prefix = entry.data[CONF_TOPIC_PREFIX]
    nodes = [prefix]
    old = entry.data.get(LEGACY_BASE)
    if (type(old) is str and NODE_ID.fullmatch(old) and old != prefix
            and not _older_route_uses(hass, entry, old)):
        nodes.append(old)
    return nodes


def discovery_prefix(hass):
    for entry in hass.config_entries.async_entries("mqtt"):
        prefix = (entry.options or {}).get("discovery_prefix") or (entry.data or {}).get("discovery_prefix")
        if isinstance(prefix, str) and prefix:
            return prefix
    return "homeassistant"


def legacy_config(topic, payload, base, prefix):
    """(component, unique_id, default_entity_id) of an old-firmware config of this E32, else None."""
    parts = topic.split("/")
    if len(parts) != 5 or parts[0] != base or parts[2] != prefix or parts[4] != "config" or parts[1] not in COMPONENTS:
        return None
    try:
        config = json.loads(payload)
    except (TypeError, ValueError):
        return None
    if type(config) is not dict:
        return None
    device = config.get("dev") or config.get("device") or {}
    ids = device.get("ids") or device.get("identifiers") if type(device) is dict else None
    unique_id = config.get("uniq_id") or config.get("unique_id")
    state = config.get("stat_t") or config.get("state_topic")
    if ids != [prefix] or type(unique_id) is not str or not (unique_id == prefix or unique_id.startswith(f"{prefix}_")):
        return None
    if type(state) is not str or not state.startswith(f"{prefix}/") or state.startswith(f"{prefix}/v1/"):
        return None
    default = config.get("default_entity_id")
    return parts[1], unique_id, default if type(default) is str else None


def user_changed(record, default_entity_id):
    """The user made this MQTT entity their own: it is left alone."""
    return (record.name is not None or record.icon is not None or record.area_id is not None or bool(record.labels)
            or record.disabled_by is er.RegistryEntryDisabler.USER or record.hidden_by is er.RegistryEntryHider.USER
            or (default_entity_id is not None and record.entity_id != default_entity_id))


async def async_setup_legacy_discovery_retirement(hass, entry, delay=RETIRE_AFTER_S, nodes=None):
    """Collect this E32's old retained discovery configs; clear the untouched ones once, after a delay.

    nodes: the node IDs to look under (default: retired_nodes); Connect E32 passes only the old base.
    """
    from .product import is_product
    if not is_product(entry):
        return
    prefix = entry.data[CONF_TOPIC_PREFIX]
    nodes = tuple(retired_nodes(hass, entry) if nodes is None else nodes)
    base = discovery_prefix(hass)
    found, status = {}, {}

    @callback
    def received(message):
        if not getattr(message, "retain", False) or not message.payload:
            return
        parts = message.topic.split("/")
        node = parts[2] if len(parts) == 5 else None
        legacy = legacy_config(message.topic, message.payload, base, node) if node in nodes else None
        if legacy is not None:
            found[message.topic] = (*legacy, node)

    @callback
    def status_received(message):
        # The old firmware's availability ("on", its last will "off"), retained; only under an old base.
        if getattr(message, "retain", False) and message.payload in ("on", "off"):
            status[message.topic] = message.payload

    async def retire(_now=None):
        registry = er.async_get(hass)
        cleared, kept, kept_nodes, topics = [], [], set(), 0
        for topic, (component, unique_id, default_entity_id, node) in sorted(found.items()):
            entity_id = registry.async_get_entity_id(component, "mqtt", unique_id)
            record = registry.async_get(entity_id) if entity_id else None
            if record is not None and user_changed(record, default_entity_id):
                kept.append(entity_id)
                kept_nodes.add(node)
                continue
            await mqtt.async_publish(hass, topic, "", 0, True)
            cleared.append(entity_id or unique_id)
        for topic in sorted(status):
            if topic.rsplit("/", 1)[0] not in kept_nodes:  # a kept entity still reads it
                await mqtt.async_publish(hass, topic, "", 0, True)
                topics += 1
        found.clear()
        status.clear()
        if cleared:
            _LOGGER.info("Retired %d MQTT discovery entities the E32 firmware announced before the v1 link "
                         "(their history stays): %s", len(cleared), ", ".join(cleared))
        if kept:
            _LOGGER.info("Kept %d old MQTT discovery entities you changed yourself: %s", len(kept), ", ".join(kept))
        if topics:
            _LOGGER.info("Cleared the old E32 firmware's retained availability under %d old MQTT base(s)", topics)
        result = {"cleared": len(cleared), "kept": len(kept)}
        if topics:
            result["status_topics"] = topics
        hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})["legacy_discovery_retired"] = result

    await mqtt.async_wait_for_mqtt_client(hass)
    for node in nodes:
        entry.async_on_unload(await mqtt.async_subscribe(hass, f"{base}/+/{node}/+/config", received))
        if node != prefix:  # the prefix's own status topic is an input of the older route (heating.py)
            entry.async_on_unload(await mqtt.async_subscribe(hass, f"{node}/status", status_received))
    entry.async_on_unload(async_call_later(hass, delay, retire))
    return retire


async def async_retire_after_link(hass, entry, settings_before):
    """Connect E32 changed the E32's base: retire what its old firmware left under the old one (1.4.5).

    Returns the old base it looks under, or None. Never raises: the link is done whatever happens here.
    """
    try:
        old = pre_link_base(settings_before, entry.data[CONF_TOPIC_PREFIX])
        if old is None or old not in retired_nodes(hass, entry):
            return None
        await async_setup_legacy_discovery_retirement(hass, entry, nodes=(old,))
        return old
    except Exception:  # noqa: BLE001 - a clean-up step; the next start tries again
        _LOGGER.debug("Old MQTT discovery entities: retirement after Connect E32 not started", exc_info=True)
        return None
