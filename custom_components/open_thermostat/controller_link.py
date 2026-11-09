"""Ephemeral native E32 settings client for the normal installation flow.

The cookie, CSRF proof and settings ETag live only in this context. This is not
an arbitrary REST proxy, credential store, source qualifier or MQTT writer.
"""
from __future__ import annotations

import asyncio
from copy import deepcopy
from dataclasses import dataclass, field
import ipaddress
import json
import logging
import re
import secrets
import socket
from urllib.parse import urlsplit

import aiohttp
from aiohttp.abc import AbstractResolver
from yarl import URL

_LOGGER = logging.getLogger(__name__)
# How long a sign-out may take (R4-26). An E32 that writes its flash or installs an update answers slowly; a
# sign-out it never confirms keeps one of its 4 web sessions in use until it frees an idle one (2 minutes),
# and a burst of changes can then find them all in use (429 session_capacity). Every request of the client
# itself stops after 10 s (its ClientTimeout); the sign-out ends after the lock is released (RoomPlanLink).
LOGOUT_TIMEOUT_S = 8
# A sign-out the E32 did not confirm is logged as a warning at most this often (then at debug level).
LOGOUT_WARNING_S = 600
_logout_warned = None  # the event-loop time of the last such warning


class ControllerLinkError(ValueError):
    """A bounded public error code, never a response/URL/credential exception."""


class ControllerLoginRejected(ControllerLinkError):
    """The E32 refused the stored password (401 on /auth/login): it was changed on the E32.

    Same public code as before (controller_auth_failed); callers that know the
    entry start Home Assistant's re-authentication with it.
    """

    def __init__(self):
        super().__init__("controller_auth_failed")


class ControllerPasswordChangeRequired(ControllerLinkError):
    """The E32 still uses its factory password and refuses every change until a new one is chosen.

    403 {"error":"password_change_required"} (rc.2). Reads keep working; the
    Repairs issue "Choose a new E32 password" changes it (e32_access).
    """

    def __init__(self):
        super().__init__("controller_password_change_required")


class PasswordChangeRejected(ControllerLinkError):
    """The E32 refused POST /auth/password with a named reason (password_too_short, password_wrong, ...)."""

    def __init__(self, status, error):
        super().__init__(error)
        self.status = status
        self.error = error


class HeatingPlanRejected(ControllerLinkError):
    """The E32 refused a /config/heating write with a named reason (409 = plan_changed)."""

    def __init__(self, status, error):
        super().__init__(error)
        self.status = status
        self.error = error


HEATING_PLAN = "/config/heating"
# Overrides, window pauses and away on top of the plan (E32 beta.19, RoomOverrides.h).
HEATING_COMFORT = "/config/heating/comfort"
# The flow options: weather curve, learned flow and optimum start (E32 beta.19, FlowPolicy.h).
HEATING_FLOW = "/config/heating/flow"
# The owner's handover for active mode: confirm that the old thermostat is
# disconnected, or hand back (beta.23 Repairs: confirm again after an update).
HEATING_HANDOVER = "/config/heating/handover"
# 1.1.1 stage B (SL-B3, D5): the plan mode, POST {"mode": "planning"|"checking"} (one key), the owner's one
# confirmation that the E32 may plan the heating (heating_plan.py); "planning" only while the planner is ready
# (else 409 plan_not_ready). The answer (and a GET) is the plan with its "mode". Firmware without it answers 404.
HEATING_PLAN_MODE = "/config/heating/plan"
# The radiator valves per room, reached through Zigbee2MQTT (E32 beta.24, TrvConfig.h).
HEATING_TRV = "/config/heating/trv"
# The Shelly devices the E32 drives itself (E32 1.1, ShellyConfig.h): GET the record without secrets ("password":
# bool per device), POST the whole record back (a device without "password" keeps its stored one); the circuits'
# pump override POST {"id","pump":"on"|"off"|"automatic","minutes"?}; and the live status with the BLU Gateway's
# valves. Firmware without Shelly answers 404.
SHELLY_CONFIG = "/config/shelly"
SHELLY_CIRCUIT = "/config/shelly/circuit"
SHELLY_STATUS = "/status/shelly"
SHELLY_PATHS = (SHELLY_CONFIG, SHELLY_CIRCUIT, SHELLY_STATUS)
# The E32 system log: syslog forwarding and the kept log levels (diagnostics/LogSettings.h).
# Not part of a settings backup; refusals are plain text (400 invalid, 503 not confirmed or unavailable).
LOGGING = "/config/logging"
# The boiler model shown on the E32 (BoilerDisplay.h): GET/POST {"model": <catalog id>}; refusals are plain text.
BOILER_DISPLAY = "/config/boiler-display"
# The owner confirms the boiler now connected after the E32 found another one (E4, BoilerCapabilitiesReport.h):
# POST {"acknowledge": true}; 409 {"error": "no_other_boiler"} when there is nothing to confirm.
BOILER_MATCH_ACKNOWLEDGE = "/boiler/match/acknowledge"
# The paired Bluetooth sensors (REST.h bluetoothSettings): GET with an ETag of this sign-in, POST the whole
# list with If-Match; a change restarts the E32 about 30 s later. The answer lists the sensors and the
# discovery, so it may be larger than the other settings.
BLUETOOTH = "/config/bluetooth"
BLUETOOTH_RESPONSE_BYTES = 32768
# The boiler's own settings (E32 V2 with track W, ClassicBoilerSettingsService.h): GET the table with the values
# and the open change; POST one write, a keep / put back (confirm) or the owner's switch (persistent). Every answer
# carries the whole GET document (about 7 KB), refusals too: {"accepted", "duplicate", "error", "settings"}.
# Firmware without them answers 404 (e32_boiler_settings.py then offers nothing).
BOILER_SETTINGS = "/boiler/settings"
BOILER_SETTINGS_WRITE = "/boiler/settings/write"
BOILER_SETTINGS_CONFIRM = "/boiler/settings/confirm"
BOILER_SETTINGS_PERSISTENT = "/boiler/settings/persistent"
BOILER_SETTINGS_POSTS = frozenset((BOILER_SETTINGS_WRITE, BOILER_SETTINGS_CONFIRM, BOILER_SETTINGS_PERSISTENT))
BOILER_SETTINGS_RESPONSE_BYTES = 16384
# The tester programme (E5, boiler_share.py): what "Share result" reads (GET, JSON), the bus recording's start and stop
# (POST, no body; 503 without PSRAM for it) and the recording itself (GET /ems/recording?offset=N, text in parts of at
# most 32 KiB with the recording's ETag). Firmware without them answers 404 (controller_update_required).
BOILER_MATCH = "/boiler/match"
PLUS_PROBE = "/boiler/plus-probe"
EMS_DEVICES = "/status/ems/devices"
BOILER_PROFILE = "/status/boiler/profile"
RECORDING_STATUS = "/ems/recording/status"
RECORDING_START = "/ems/recording/start"
RECORDING_STOP = "/ems/recording/stop"
RECORDING = "/ems/recording"
TESTER_READS = frozenset((BOILER_MATCH, PLUS_PROBE, EMS_DEVICES, BOILER_PROFILE, RECORDING_STATUS))
RECORDING_POSTS = frozenset((RECORDING_START, RECORDING_STOP))
TESTER_RESPONSE_BYTES = 32768
RECORDING_PART_BYTES = 32768
RECORDING_MAX_BYTES = 2 * 1024 * 1024  # a full E32 ring (192 KiB) is about 550 KB of text
HEATING_PLAN_BYTES = 8192  # The E32 refuses larger request bodies (413 plan_too_large).
# Backup and restore of the E32 settings (E32 beta.19, ConfigBackupRoute.h): export,
# validate and apply, each one POST. A backup file holds at most 24 KB; a request
# carries one file plus 512 bytes, and an answer is at most a file.
CONFIG_BACKUP = "/config/backup"
CONFIG_BACKUP_REQUEST_BYTES = 24576 + 512
CONFIG_BACKUP_RESPONSE_BYTES = 32768
# The E32 seals or opens the secrets with PBKDF2 (16384 rounds): seconds, not milliseconds.
CONFIG_BACKUP_TIMEOUT = 45
# Since beta.19 the E32 packs large week programs into its 4 KB store and
# answers 413 plan_too_large itself when even that form does not fit; older
# firmware refuses bodies above 4096 bytes with the same 413.
# A plan that fits but finds its flash storage full is refused with 507 storage_full.


class BackupRejected(ControllerLinkError):
    """The E32 refused a /config/backup request with a named reason (boiler_owned, wrong_passphrase, ...)."""

    def __init__(self, status, error):
        super().__init__(error)
        self.status = status
        self.error = error


class BluetoothRejected(ControllerLinkError):
    """The E32 refused a /config/bluetooth change with a named reason (invalid_device_name, ...)."""

    def __init__(self, status, error):
        super().__init__(error)
        self.status = status
        self.error = error


class BoilerSettingsRejected(ControllerLinkError):
    """The E32 refused a boiler settings request with a named reason (persistent_writes_off, settings_busy, ...).

    ``settings`` is the settings document the refusal carried (None when it had none).
    """

    def __init__(self, status, error, settings=None):
        super().__init__(error)
        self.status = status
        self.error = error
        self.settings = settings


async def _settings_refusal(response):
    """(error name, settings document) of a refused boiler settings request; never response text verbatim."""
    body = bytearray()
    try:
        async for chunk in response.content.iter_chunked(2048):
            body.extend(chunk)
            if len(body) > BOILER_SETTINGS_RESPONSE_BYTES:
                return "settings_refused", None
        value = json.loads(bytes(body))
    except (ValueError, UnicodeError, RecursionError, aiohttp.ClientError):
        # The E32's own gates answer in plain text: an update, the boiler test (409).
        return "settings_busy" if response.status == 409 else "settings_refused", None
    error = value.get("error") if type(value) is dict else None
    settings = value.get("settings") if type(value) is dict and type(value.get("settings")) is dict else None
    return (error if type(error) is str and re.fullmatch(r"[a-z0-9_]{1,48}", error) else "settings_refused"), settings


class ControllerProvisioningError(ControllerLinkError):
    """A remote outcome must be read back before a new attempt, never guessed."""

    def __init__(self, code, *, device_may_have_changed):
        super().__init__(code)
        self.device_may_have_changed = device_may_have_changed


# Home-network DNS names: router/mDNS suffixes (FRITZ!Box, RFC 8375 home.arpa,
# localdomain, internal, lan, local, home). Single-label names are accepted too;
# every name must also resolve to a local address (PrivateResolver).
LOCAL_DNS_SUFFIXES = (".fritz.box", ".home.arpa", ".localdomain", ".internal", ".lan", ".local", ".home")


def private_controller_ip(address, *, link_local=False):
    """A local-network IP (private; link-local only for resolved names), never loopback/public."""
    try:
        address = ipaddress.ip_address(address.split("%", 1)[0] if type(address) is str else address)
    except ValueError:
        return False
    if address.is_loopback or address.is_unspecified or address.is_multicast or address.is_reserved:
        return False
    if address.is_link_local:
        return link_local
    return address.is_private


class PrivateResolver(AbstractResolver):
    """The default resolver, keeping only local-network addresses (no public or loopback hosts).

    Checked at connect time, so a home-network name that resolves (or later
    rebinds) to a public or loopback address is never contacted.
    """

    async def resolve(self, host, port=0, family=socket.AF_INET):
        # A resolver per lookup: the connector does not own (or close) a passed-in resolver.
        resolver = aiohttp.DefaultResolver()
        try:
            results = await resolver.resolve(host, port, family)
        finally:
            await resolver.close()
        local = [result for result in results if private_controller_ip(result["host"], link_local=True)]
        if not local:
            raise OSError(f"{host} does not resolve to a local network address")
        return local

    async def close(self):
        return None


def controller_address(value):
    """Explicit local controller only; fixed API paths and no redirects/proxies."""
    if (type(value) is not str or len(value) > 280 or value != value.strip()
            or any(ord(c) < 33 or ord(c) > 126 for c in value)):
        raise ControllerLinkError("controller_address_invalid")
    try:
        url = urlsplit(value)
        host, port = url.hostname, url.port
        if (url.scheme not in ("http", "https") or not host or url.username is not None
                or url.password is not None or url.path not in ("", "/")
                or url.query or url.fragment or port is not None and not 1 <= port <= 65535):
            raise ValueError
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            if (not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]{0,251}[a-zA-Z0-9])?", host)
                    or ".." in host or host.lower() == "localhost" or host.isdecimal()
                    or re.fullmatch(r"0[xX][0-9a-fA-F]+", host)
                    or "." in host and not host.lower().endswith(LOCAL_DNS_SUFFIXES)):
                raise ValueError
        else:
            if not private_controller_ip(address):
                raise ValueError
    except (ValueError, TypeError):
        raise ControllerLinkError("controller_address_invalid") from None
    # Match aiohttp's actual Host header (case/default-port normalization).
    return str(URL(value).origin())


def _object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _nonfinite(_):
    raise ValueError


def _decode(raw):
    try:
        return json.loads(raw, object_pairs_hook=_object_pairs, parse_constant=_nonfinite)
    except (ValueError, UnicodeError, RecursionError):
        raise ControllerLinkError("controller_response_invalid") from None


async def _error_name(response):
    """The E32's {"error":"<name>"}, or a fixed name; never response text verbatim."""
    fallback = {409: "plan_changed", 413: "plan_too_large", 503: "save_unconfirmed",
                507: "storage_full"}.get(response.status, "invalid_plan")
    try:
        value = json.loads(await response.content.read(512))
    except (ValueError, UnicodeError, RecursionError, aiohttp.ClientError):
        return fallback
    error = value.get("error") if type(value) is dict else None
    return error if type(error) is str and re.fullmatch(r"[a-z0-9_]{1,48}", error) else fallback


async def _backup_error(response):
    """The E32's {"error":"<name>"} of a refused backup request (its warnings may make it long)."""
    body = bytearray()
    try:
        async for chunk in response.content.iter_chunked(2048):
            body.extend(chunk)
            if len(body) > 16384:
                return "backup_refused"
        value = json.loads(bytes(body))
    except (ValueError, UnicodeError, RecursionError, aiohttp.ClientError):
        return "backup_refused"
    error = value.get("error") if type(value) is dict else None
    return error if type(error) is str and re.fullmatch(r"[a-z0-9_]{1,48}", error) else "backup_refused"


@dataclass(frozen=True, slots=True)
class InitialControllerLink:
    """A reviewed prospective change, not a stored secret or live admission."""
    source: object = field(repr=False)
    before: object = field(repr=False)
    observed_settings: dict = field(repr=False)
    settings: dict = field(repr=False)
    etag: str = field(repr=False)
    firmware_identity: dict = field(repr=False)
    private_entry_state: str = field(repr=False)
    settings_unchanged: bool
    needs_reboot: bool


def initial_controller_link(hass, entry, *, version, status, updates, settings, etag, rooms):
    """Derive one normal HA installation link from actual authenticated reads.

    Existing NativePlanSource selects logical policy only. Unknown measurement,
    actuator, hydraulic and boiler qualifications remain unknown. No I/O, Store
    change, runtime activation or source replacement happens in this function.
    """
    from .native_provisioning import propose_local_shadow_source, local_device_descriptor, source_from_selection
    from .product import configuration_snapshot, is_product
    from .v1_heating_graph import actual_runtime_active
    from .v1_model import CONF_ENABLED, MODE_SHADOW, integration_mode
    from .v1_wire import identifier
    from .graph_shadow_validation import canonical
    from .native_plan import native_entry_state

    if (not is_product(entry) or integration_mode(entry) != MODE_SHADOW
            or entry.options.get(CONF_ENABLED, False) or actual_runtime_active(hass, entry)):
        raise ControllerLinkError("controller_runtime_off_required")
    if (type(version) is not dict or type(status) is not dict or type(updates) is not dict
            or type(settings) is not dict or type(rooms) is not list):
        raise ControllerLinkError("controller_response_invalid")
    if status.get("controlMode") not in ("legacy", "shadow"):
        raise ControllerLinkError("controller_response_invalid")
    if (type(etag) is not str or re.fullmatch(r'"[0-9a-f]{64}"', etag) is None):
        raise ControllerLinkError("controller_update_required")
    if (type(version.get("version")) is not str
            or re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+-e32v2(?:-(?:alpha|beta|rc)\.[0-9]+)?", version["version"]) is None
            or type(version.get("source")) is not str
            or re.fullmatch(r"[0-9a-f]{40}", version["source"]) is None
            or any(type(version.get(k)) is not str or re.fullmatch(r"[0-9a-f]{64}",version[k]) is None
                   for k in ("sha256", "web_sha256"))):
        raise ControllerLinkError("controller_update_required")
    build = status.get("control_build")
    if (type(build) is not dict or type(build.get("schema")) is not int or build["schema"] != 1
            or build.get("scope") != "compiled_support_only"
            or build.get("authorizes_physical_outputs") is not False
            or type(build.get("source_formats")) is not list
            or "native.source.local.week.v1" not in build["source_formats"]
            or type(build.get("plans")) is not list
            or not any(type(p) is dict and p.get("contract") == "control.plan.week.v1"
                       and type(p.get("maximum_zones")) is int and p["maximum_zones"] == 2
                       and type(p.get("minimum_zones")) is int and p["minimum_zones"] == 1
                       for p in build["plans"])):
        raise ControllerLinkError("controller_update_required")
    if (updates.get("busy") is not False or updates.get("boot_pending") is not False
            or updates.get("reboot_required") is not False or updates.get("reboot_scheduled") is not False):
        raise ControllerLinkError("controller_busy_or_conflict")
    if rooms:
        raise ControllerLinkError("controller_legacy_rooms_present")
    mqtt = settings.get("mqtt")
    if (type(mqtt) is not dict or mqtt.get("enabled") is not True
            or type(mqtt.get("brokerAddress")) is not str or not mqtt["brokerAddress"]
            or type(mqtt.get("brokerPort")) is not int or not 1 <= mqtt["brokerPort"] <= 65535
            or type(mqtt.get("username")) is not str or not mqtt["username"]
            or mqtt.get("password") != ""):
        raise ControllerLinkError("controller_broker_setup_required")
    controller = mqtt.get("native_source_device_id")
    if (type(controller) is not str or re.fullmatch(r"e32_[0-9a-f]{12}", controller) is None
            or type(mqtt.get("native_source_live_apply")) is not bool
            or not identifier(entry.data.get("topic_prefix"))):
        raise ControllerLinkError("controller_update_required")
    source = propose_local_shadow_source(hass, entry, controller, week_reviewed=True)
    selected = source_from_selection(entry)
    if selected is not None and selected != source:
        raise ControllerLinkError("controller_source_conflict")
    descriptor = local_device_descriptor(source)
    current = deepcopy(settings)
    current["mqtt"].pop("native_source_device_id")
    live = current["mqtt"].pop("native_source_live_apply")
    existing = current["mqtt"].get("native_shadow_source")
    # A selected evolution may replace only its exact CURRENT predecessor.
    # An older evolution descriptor retains history, but only its current tail
    # identifies the immediately preceding policy; no historical config is applied.
    previous_descriptor = None
    if source.predecessor is not None:
        previous_descriptor = local_device_descriptor(source.predecessor)
        if existing is None:
            raise ControllerLinkError("controller_source_conflict")
    observed_current = existing
    if type(existing) is list and len(existing) == 3 and existing[0] == "native.source.evolution.v1":
        observed_current = existing[2]
    predecessor_matches = (previous_descriptor is not None
        and canonical(observed_current) == canonical(previous_descriptor))
    if existing is not None and (
            (canonical(existing) != canonical(descriptor) and not predecessor_matches)
            or current["mqtt"].get("adapter_id") != source.policy.adapter_id
            or current["mqtt"].get("base") != entry.data["topic_prefix"]
            or current["mqtt"].get("modern_shadow") is not True):
        raise ControllerLinkError("controller_source_conflict")
    if (current["mqtt"].get("modern_shadow") is True
            and current["mqtt"].get("adapter_id") != source.policy.adapter_id):
        raise ControllerLinkError("controller_source_conflict")
    candidate = deepcopy(current)
    candidate["mqtt"].update(modern_shadow=True, adapter_id=source.policy.adapter_id,
                             base=entry.data["topic_prefix"], native_shadow_source=descriptor)
    # The firmware preserves the same-broker redacted password/weather key.
    # It checks its final secret-preserving serialization against the same quota.
    if len(json.dumps(candidate, ensure_ascii=True, separators=(",", ":")).encode()) >= 2048:
        raise ControllerLinkError("controller_settings_too_large")
    unchanged = canonical(current) == canonical(candidate)
    identity = {key: version[key] for key in ("version", "source", "sha256", "web_sha256")}
    return InitialControllerLink(source, configuration_snapshot(entry), current, candidate, etag, identity,
                                 native_entry_state(entry),
                                 unchanged, not (unchanged and live and status.get("controlMode") == "shadow"))


def _link_guard(hass, entry, before, source=None, private_entry_state=None):
    from .product import configuration_snapshot
    from .v1_heating_graph import actual_runtime_active
    from .v1_model import CONF_ENABLED
    from .native_plan import native_entry_state
    if (hass.config_entries.async_get_entry(entry.entry_id) is not entry
            or configuration_snapshot(entry) != before
            or entry.options.get(CONF_ENABLED, False) or actual_runtime_active(hass, entry)
            or private_entry_state is not None and native_entry_state(entry) != private_entry_state):
        raise ControllerLinkError("setup_changed")
    if source is not None:
        try:
            source.validate_native(hass, entry)
        except ValueError:
            raise ControllerLinkError("setup_changed") from None


async def async_prepare_controller_link(hass, entry, client):
    """Actual bounded reads and existing native schedule compilation; no writes."""
    from .product import configuration_snapshot
    from .native_plan import native_entry_state
    before = configuration_snapshot(entry)
    private_before = native_entry_state(entry)
    _link_guard(hass, entry, before, private_entry_state=private_before)
    observed = {}
    for key, path in (("version", "/status/version"), ("status", "/status"),
                      ("updates", "/updates/status"), ("settings", "/config/device"),
                      ("rooms", "/config/rooms")):
        value = await client.async_read(path)
        _link_guard(hass, entry, before, private_entry_state=private_before)
        if key == "settings":
            observed[key], observed["etag"] = value
        else:
            observed[key] = value
    try:
        plan = initial_controller_link(hass, entry, **observed)
    except ControllerLinkError:
        raise
    except ValueError:
        raise ControllerLinkError("controller_room_configuration_invalid") from None
    # Same compiler/budgets as the real runtime. A saved week alone is not proof
    # its complete 15-day plan fits the actual native contract.
    try:
        await plan.source.async_configuration(hass, entry)
    except ValueError:
        _link_guard(hass, entry, before, plan.source, private_before)
        raise ControllerLinkError("controller_room_configuration_invalid") from None
    _link_guard(hass, entry, before, plan.source, private_before)
    return plan


LINK_BOOT_TIMEOUT = 60
LINK_POLL_INTERVAL = 1


def _saved_link_settings(value, controller):
    if type(value) is not dict or type(value.get("mqtt")) is not dict:
        raise ControllerLinkError("controller_response_invalid")
    result = deepcopy(value)
    mqtt = result["mqtt"]
    identity = mqtt.pop("native_source_device_id", None)
    live = mqtt.pop("native_source_live_apply", None)
    if identity != controller or type(live) is not bool:
        raise ControllerLinkError("controller_changed")
    return result, live


async def async_provision_controller(hass, entry, client, plan, password):
    """Apply this exact initial logical source and verify the running factory.

    Uses existing native device settings/reboot routes. No HA mutation, MQTT
    writer, room-plan apply or physical authorization. A caller must still fence
    and commit HA source selection, then obtain actual MQTT admission/readback.
    """
    from .graph_shadow_validation import canonical
    if type(plan) is not InitialControllerLink:
        raise ControllerLinkError("controller_readback_invalid")
    changed = False
    wrote = False
    rebooted = False
    try:
        _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
        fresh = await async_prepare_controller_link(hass, entry, client)
        _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
        if (fresh.etag != plan.etag or fresh.firmware_identity != plan.firmware_identity
                or fresh.private_entry_state != plan.private_entry_state
                or fresh.source != plan.source
                or canonical(fresh.observed_settings) != canonical(plan.observed_settings)
                or canonical(fresh.settings) != canonical(plan.settings)):
            raise ControllerLinkError("controller_settings_changed")
        if not fresh.settings_unchanged:
            # Set BEFORE the await: a lost response does not prove no flash save.
            changed = True
            try:
                await client.async_save_settings(fresh.settings, fresh.etag)
            except ControllerLinkError as err:
                if str(err) in ("controller_auth_failed", "controller_settings_changed",
                                "controller_busy_or_conflict", "controller_settings_too_large",
                                "controller_readback_invalid", "controller_request_invalid"):
                    changed = False  # Explicit pre-save rejection, not a lost response.
                raise
            wrote = True
            _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
            saved, _ = await client.async_read("/config/device")
            _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
            actual, _ = _saved_link_settings(saved, plan.source.policy.controller_id)
            if canonical(actual) != canonical(plan.settings):
                raise ControllerLinkError("controller_settings_changed")
        if fresh.needs_reboot:
            changed = True
            _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
            try:
                await client.async_reboot()
                rebooted = True
            except ControllerLinkError as err:
                if str(err) != "controller_unreachable":
                    raise
                # A lost reboot response may mean the boot already started.
                # Read only below; never issue a second reboot automatically.
        reauthenticated = False
        try:
            async with asyncio.timeout(LINK_BOOT_TIMEOUT):
                while True:
                    _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
                    try:
                        version = await client.async_read("/status/version")
                        updates = await client.async_read("/updates/status")
                        status = await client.async_read("/status")
                        saved, _ = await client.async_read("/config/device")
                    except ControllerLinkError as err:
                        _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
                        if fresh.needs_reboot and str(err) == "controller_auth_failed" and not reauthenticated:
                            await client.async_login(password)
                            reauthenticated = True
                        elif str(err) != "controller_unreachable":
                            raise
                        await asyncio.sleep(LINK_POLL_INTERVAL)
                        continue
                    _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
                    if any(type(value) is not dict for value in (version, updates, status)):
                        raise ControllerLinkError("controller_response_invalid")
                    if {k: version.get(k) for k in plan.firmware_identity} != plan.firmware_identity:
                        raise ControllerLinkError("controller_changed")
                    actual, live = _saved_link_settings(saved, plan.source.policy.controller_id)
                    if canonical(actual) != canonical(plan.settings):
                        raise ControllerLinkError("controller_settings_changed")
                    if (live is True and status.get("controlMode") == "shadow"
                            and updates.get("busy") is False and updates.get("boot_pending") is False
                            and updates.get("reboot_required") is False and updates.get("reboot_scheduled") is False):
                        break
                    await asyncio.sleep(LINK_POLL_INTERVAL)
        except TimeoutError:
            raise ControllerLinkError("controller_boot_unconfirmed") from None
        _link_guard(hass, entry, plan.before, plan.source, plan.private_entry_state)
        return {"controller_id": plan.source.policy.controller_id,
                "profile_digest": plan.source.policy.profile_digest,
                "device_settings_verified": True, "running_logical_source_verified": True,
                "settings_written": wrote, "reboot_acknowledged": rebooted,
                "mqtt_session_verified": False, "room_plan_applied": False,
                "authorizes_physical_outputs": False}
    except ControllerLinkError as err:
        raise ControllerProvisioningError(str(err), device_may_have_changed=changed) from None


class ControllerClient:
    """One scoped operation using the existing firmware cookie/CSRF contract."""

    _reads = frozenset(("/auth/session", "/status/version", "/status", "/updates/status",
                        "/config/device", "/config/rooms", HEATING_PLAN, HEATING_COMFORT, HEATING_FLOW,
                        HEATING_TRV, "/status/heating", LOGGING, BOILER_DISPLAY, BLUETOOTH, BOILER_SETTINGS,
                        SHELLY_CONFIG, SHELLY_STATUS, *TESTER_READS))
    _writes = frozenset(("/auth/login", "/auth/logout", "/auth/password", "/config/device", "/updates/reboot",
                         HEATING_PLAN, HEATING_COMFORT, HEATING_FLOW, HEATING_HANDOVER, HEATING_PLAN_MODE,
                         HEATING_TRV, CONFIG_BACKUP,
                         LOGGING, BOILER_DISPLAY, BLUETOOTH, *BOILER_SETTINGS_POSTS, SHELLY_CONFIG, SHELLY_CIRCUIT,
                         BOILER_MATCH_ACKNOWLEDGE, *RECORDING_POSTS))

    def __init__(self, address):
        self.address = controller_address(address)
        self._session = None
        self._csrf = None
        # True once /auth/login answered 200: the E32 holds a session for this
        # client, even when the CSRF read after it failed (closed with a logout).
        self._signed_in = False
        self.logout_confirmed = False
        # From /auth/session after a login: True while the E32 still has its
        # factory password, False once changed, None on firmware that does not say.
        self.default_password = None

    async def __aenter__(self):
        if self._session is not None and not self._session.closed:
            raise ControllerLinkError("controller_request_invalid")
        self.logout_confirmed = False
        self._csrf = None
        self._signed_in = False
        self._session = aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=True),  # Native E32 uses LAN IP cookies.
            timeout=aiohttp.ClientTimeout(total=10), trust_env=False,
            connector=aiohttp.TCPConnector(resolver=PrivateResolver()),
        )
        return self

    async def __aexit__(self, *_):
        await self.async_close()

    async def _request(self, method, path, *, form=None, document=None, etag=None):
        if (self._session is None or self._session.closed
                or method == "GET" and path not in self._reads
                or method == "POST" and path not in self._writes
                or method not in ("GET", "POST")):
            raise ControllerLinkError("controller_request_invalid")
        headers = {"Origin": self.address, "Accept": "application/json"}
        if method == "POST" and path == "/config/device" and etag is None:
            raise ControllerLinkError("controller_readback_invalid")
        if method == "POST" and path != "/auth/login":
            if not self._csrf:
                raise ControllerLinkError("controller_auth_failed")
            headers["X-OpenThermostat-CSRF"] = self._csrf
        if etag is not None:
            if type(etag) is not str or re.fullmatch(r'"[0-9a-f]{64}"', etag) is None:
                raise ControllerLinkError("controller_readback_invalid")
            headers["If-Match"] = etag
        data = form
        if form is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if document is not None:
            headers["Content-Type"] = "application/json"
            if type(document) is not dict:
                raise ControllerLinkError("controller_request_invalid")
            try:
                # A backup goes as UTF-8, as the E32 exported it and as e32_backup measured it:
                # \uXXXX escapes would make a valid backup with non-ASCII names too large to send.
                data = json.dumps(document, ensure_ascii=path != CONFIG_BACKUP, allow_nan=False,
                                  separators=(",", ":"))
            except (TypeError, ValueError, RecursionError):
                raise ControllerLinkError("controller_request_invalid") from None
            if path == HEATING_PLAN:
                if len(data.encode()) > HEATING_PLAN_BYTES:
                    raise HeatingPlanRejected(413, "plan_too_large")
            elif path == CONFIG_BACKUP:
                data = data.encode()
                if len(data) > CONFIG_BACKUP_REQUEST_BYTES:
                    raise BackupRejected(413, "backup_too_large")
            elif len(data.encode()) >= 2048:
                raise ControllerLinkError("controller_settings_too_large")
        backup = path == CONFIG_BACKUP
        settings = path == BOILER_SETTINGS or path in BOILER_SETTINGS_POSTS
        limit = (CONFIG_BACKUP_RESPONSE_BYTES if backup else BLUETOOTH_RESPONSE_BYTES if path == BLUETOOTH
                 else BOILER_SETTINGS_RESPONSE_BYTES if settings
                 else TESTER_RESPONSE_BYTES if path in TESTER_READS else 8192)
        extra = {"timeout": aiohttp.ClientTimeout(total=CONFIG_BACKUP_TIMEOUT)} if backup else {}
        try:
            async with self._session.request(method, self.address + path, data=data,
                    headers=headers, allow_redirects=False, **extra) as response:
                if response.status == 401 and method == "POST" and path == "/auth/login":
                    raise ControllerLoginRejected()
                if path == "/auth/password" and response.status in (400, 403, 409, 503):
                    raise PasswordChangeRejected(response.status, await _error_name(response))
                if settings and response.status == 404:
                    raise ControllerLinkError("controller_update_required")  # firmware without boiler settings
                if settings and method == "POST" and response.status in (400, 403, 409, 429, 500):
                    error, document = await _settings_refusal(response)
                    if error == "password_change_required":
                        raise ControllerPasswordChangeRequired()
                    if error in ("csrf_required", "authentication_required"):
                        raise ControllerLinkError("controller_auth_failed")
                    raise BoilerSettingsRejected(response.status, error, document)
                if response.status == 403 and await _error_name(response) == "password_change_required":
                    raise ControllerPasswordChangeRequired()
                if response.status in (401, 403):
                    raise ControllerLinkError("controller_auth_failed")
                if path == HEATING_PLAN_MODE and response.status == 404:
                    raise ControllerLinkError("controller_update_required")  # firmware without the planner
                if path in (HEATING_PLAN, HEATING_COMFORT, HEATING_FLOW, HEATING_HANDOVER, HEATING_PLAN_MODE,
                            HEATING_TRV) and response.status in (400, 409, 413, 503, 507):
                    raise HeatingPlanRejected(response.status, await _error_name(response))
                if path in SHELLY_PATHS and response.status in (400, 404, 409, 503):
                    name = await _error_name(response) if response.status != 404 or method == "POST" else ""
                    if response.status == 404 and not name.startswith("unknown_"):
                        raise ControllerLinkError("controller_update_required")  # firmware without Shelly
                    raise HeatingPlanRejected(response.status, name)
                if backup and response.status in (400, 409, 413, 500, 503):
                    raise BackupRejected(response.status, await _backup_error(response))
                if backup and response.status == 404:
                    raise ControllerLinkError("controller_update_required")  # firmware before beta.19
                if path == BLUETOOTH and response.status in (400, 413, 503, 507):
                    raise BluetoothRejected(response.status, await _error_name(response))
                if path == BOILER_MATCH_ACKNOWLEDGE and response.status in (404, 409):
                    # 404: firmware without the route; 409: no other boiler to confirm (already done), or busy.
                    raise ControllerLinkError("controller_update_required" if response.status == 404
                                              else "controller_boiler_confirmed"
                                              if await _error_name(response) == "no_other_boiler"
                                              else "controller_busy_or_conflict")
                if (path in TESTER_READS or path in RECORDING_POSTS) and response.status == 404:
                    raise ControllerLinkError("controller_update_required")  # firmware without the tester programme
                if path == RECORDING_START and response.status == 503:
                    raise ControllerLinkError("controller_recording_unavailable")  # no PSRAM for the ring
                if path in (BLUETOOTH, BOILER_DISPLAY) and response.status == 404:
                    raise ControllerLinkError("controller_update_required")
                if path in (LOGGING, BOILER_DISPLAY) and response.status in (400, 404, 503):
                    raise ControllerLinkError({400: "controller_settings_invalid", 404: "controller_update_required",
                                               503: "controller_settings_unconfirmed"}[response.status])
                if path in (HEATING_FLOW, HEATING_TRV) and response.status == 404:
                    raise ControllerLinkError("controller_update_required")  # firmware before beta.19 / beta.24
                if response.status == 429:
                    # /auth/login: all E32 web sessions are in use (session_capacity), or
                    # too many failed sign-ins (try_again_later, Retry-After 30 s).
                    raise ControllerLinkError("controller_session_capacity"
                                              if await _error_name(response) == "session_capacity"
                                              else "controller_try_again_later")
                if response.status == 412:
                    raise ControllerLinkError("controller_settings_changed")
                if response.status == 409:
                    raise ControllerLinkError("controller_busy_or_conflict")
                accepted = ({200, 201} if method == "POST" and path in ("/config/device", CONFIG_BACKUP, BLUETOOTH)
                            else {202} if method == "POST" and path == "/updates/reboot"
                            else {204} if method == "POST" and path == "/auth/password"
                            else {200, 202} if method == "POST" and settings
                            else {200})
                if response.status not in accepted:
                    raise ControllerLinkError("controller_response_invalid")
                body = bytearray()
                async for chunk in response.content.iter_chunked(2048):
                    if len(body) + len(chunk) > limit:
                        raise ControllerLinkError("controller_response_too_large")
                    body.extend(chunk)
                return bytes(body), response.headers.get("ETag"), response.status
        except (aiohttp.ClientError, TimeoutError):
            raise ControllerLinkError("controller_unreachable") from None

    async def async_read(self, path):
        raw, tag, _ = await self._request("GET", path)
        value = _decode(raw)
        if path == "/config/device":
            if type(value) is not dict or type(tag) is not str or re.fullmatch(r'"[0-9a-f]{64}"', tag) is None:
                raise ControllerLinkError("controller_update_required")
            return value, tag
        return value

    async def async_login(self, password):
        if type(password) is not str or not 1 <= len(password) <= 128:
            raise ControllerLinkError("controller_auth_failed")
        # Do not retain the supplied password in this object or an HA entry.
        await self._request("POST", "/auth/login", form={"username": "admin", "password": password})
        self._signed_in = True
        session = await self._read_session()
        self._csrf = session["csrf"]
        flag = session.get("default_password")
        self.default_password = flag if type(flag) is bool else None

    async def async_change_password(self, current, new):
        """POST /auth/password of a signed-in client: the E32 keeps this session, signs out all others.

        Refusals raise PasswordChangeRejected (password_too_short, password_too_long,
        password_wrong, password_change_busy, password_storage_failed). Neither
        password is kept in this object or in an error.
        """
        if type(current) is not str or type(new) is not str or not current or not new:
            raise ControllerLinkError("controller_request_invalid")
        await self._request("POST", "/auth/password", document={"current": current, "new": new})

    async def _read_session(self):
        """GET /auth/session of a signed-in client: its CSRF proof (and default_password)."""
        session = await self.async_read("/auth/session")
        if (type(session) is not dict or session.get("authenticated") is not True
                or type(session.get("csrf")) is not str
                or re.fullmatch(r"[0-9a-f]{64}", session["csrf"]) is None):
            raise ControllerLinkError("controller_auth_failed")
        return session

    async def async_read_heating_plan(self):
        """The E32 room plan (GET /config/heating), parsed but not yet validated."""
        return await self.async_read(HEATING_PLAN)

    async def async_save_heating_plan(self, plan):
        """POST the whole plan with the revision it was read at; returns the stored plan.

        A stale revision raises HeatingPlanRejected(409, "plan_changed"); other
        refusals carry the E32's error name (400), save_unconfirmed (503) or
        storage_full (507: the E32's room-plan storage has no room left).
        """
        if type(plan) is not dict:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", HEATING_PLAN, document=plan)
        return _decode(raw)

    async def async_comfort_state(self):
        """GET the E32's comfort state: overrides, away and (rc.4, house.holidays.v1) every planned holiday."""
        return await self.async_read(HEATING_COMFORT)

    async def async_comfort_command(self, command):
        """POST one override or away command; returns the E32's comfort state.

        A refusal raises HeatingPlanRejected with the E32's error name
        (unknown_room, invalid_temperature, no_clock, no_schedule, ...).
        """
        if type(command) is not dict:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", HEATING_COMFORT, document=command)
        return _decode(raw)

    async def async_handover(self, disconnected):
        """POST the owner's handover; returns the E32's active-control status.

        True confirms that the old thermostat is disconnected from the boiler;
        False hands back (the E32 stops at once with one minute of zero). A
        refusal raises HeatingPlanRejected (active_mode_not_released,
        plan_not_active: 409; invalid_request: 400).
        """
        if type(disconnected) is not bool:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", HEATING_HANDOVER, document={"thermostat_disconnected": disconnected})
        return _decode(raw)

    async def async_plan_mode(self, mode):
        """POST the plan mode ("planning": the owner lets the E32 plan the heating; "checking": back to checking);
        returns the E32's answer (its plan with "mode"). A refusal raises HeatingPlanRejected (400 invalid_request,
        409 plan_not_ready, 503 save_unconfirmed); firmware without the planner raises controller_update_required."""
        if mode not in ("checking", "planning"):
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", HEATING_PLAN_MODE, document={"mode": mode})
        return _decode(raw) if raw else {}

    async def async_flow_settings(self, change=None):
        """GET the flow options, or POST a partial change; returns the stored options.

        A refusal raises HeatingPlanRejected (invalid_key, invalid_value: 400;
        save_unconfirmed: 503); firmware without the options raises
        controller_update_required.
        """
        if change is None:
            return await self.async_read(HEATING_FLOW)
        if type(change) is not dict or not change:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", HEATING_FLOW, document=change)
        return _decode(raw)

    async def async_logging(self, document=None):
        """GET the system log settings, or POST all of them; returns what the E32 stored.

        A POST carries all eight fields (syslog_enabled, server, port, syslog_level,
        web_level, mark_interval_s, syslog_esp, syslog_ems). Refusals raise
        controller_settings_invalid (400) or controller_settings_unconfirmed (503);
        firmware without the route raises controller_update_required.
        """
        if document is None:
            return await self.async_read(LOGGING)
        if type(document) is not dict:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", LOGGING, document=document)
        return _decode(raw)

    async def async_boiler_display(self, model=None):
        """GET the boiler model shown on the E32, or POST a new one; returns {"model": ...} as stored."""
        if model is None:
            return await self.async_read(BOILER_DISPLAY)
        if type(model) is not str or not model:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", BOILER_DISPLAY, document={"model": model})
        return _decode(raw)

    async def async_boiler_match_acknowledge(self):
        """POST the owner's "this is the boiler now connected" (E4); returns the E32's answer {"acknowledged", "match"}."""
        raw, _, _ = await self._request("POST", BOILER_MATCH_ACKNOWLEDGE, document={"acknowledge": True})
        return _decode(raw)

    async def async_tester_read(self, path):
        """One of the tester programme's reads (TESTER_READS), parsed; firmware without it: controller_update_required."""
        if path not in TESTER_READS:
            raise ControllerLinkError("controller_request_invalid")
        return await self.async_read(path)

    async def async_recording(self, start):
        """POST /ems/recording/start (True) or /stop (False); returns the recording's status document.

        Without PSRAM for the ring a start raises controller_recording_unavailable; during an update
        controller_busy_or_conflict; firmware without it controller_update_required.
        """
        if type(start) is not bool:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", RECORDING_START if start else RECORDING_STOP, document={})
        return _decode(raw)

    async def async_recording_download(self, total):
        """The stopped recording's emsrec text, ``total`` bytes (its status "bytes"), read part by part.

        Every part must carry the same ETag (the same recording); a recording that changed meanwhile, or ends
        short, raises controller_recording_changed; one that is not stopped controller_recording_not_ready.
        """
        if (self._session is None or self._session.closed or type(total) is not int
                or not 0 < total <= RECORDING_MAX_BYTES):
            raise ControllerLinkError("controller_request_invalid")
        body, tag = bytearray(), None
        headers = {"Origin": self.address, "Accept": "text/plain"}
        try:
            while len(body) < total:
                async with self._session.request("GET", f"{self.address}{RECORDING}?offset={len(body)}", headers=headers,
                                                 allow_redirects=False,
                                                 timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status in (401, 403):
                        raise ControllerLinkError("controller_auth_failed")
                    if response.status == 404:
                        raise ControllerLinkError("controller_update_required")
                    if response.status == 409:
                        raise ControllerLinkError("controller_recording_not_ready")
                    if response.status != 200:
                        raise ControllerLinkError("controller_recording_changed" if response.status == 416
                                                  else "controller_response_invalid")
                    etag = response.headers.get("ETag")
                    if type(etag) is not str or re.fullmatch(r'"[0-9]{1,10}-[0-9]{1,20}"', etag) is None:
                        raise ControllerLinkError("controller_response_invalid")
                    if tag is None:
                        tag = etag
                    elif etag != tag:
                        raise ControllerLinkError("controller_recording_changed")
                    part = bytearray()
                    async for chunk in response.content.iter_chunked(4096):
                        if len(part) + len(chunk) > RECORDING_PART_BYTES or len(body) + len(part) + len(chunk) > total:
                            raise ControllerLinkError("controller_recording_changed")
                        part.extend(chunk)
                if not part:
                    break
                body.extend(part)
        except (aiohttp.ClientError, TimeoutError):
            raise ControllerLinkError("controller_unreachable") from None
        if len(body) != total:
            raise ControllerLinkError("controller_recording_changed")
        return bytes(body)

    async def async_bluetooth(self, document=None, etag=None):
        """GET the paired Bluetooth sensors with this sign-in's ETag, or POST the whole list with it.

        GET returns (value, etag). POST needs the ETag of a GET in the same sign-in; a list
        changed meanwhile raises controller_settings_changed (412), a refusal
        BluetoothRejected with the E32's name. Bindkeys never travel: rows say "keep".
        """
        if document is None:
            raw, tag, _ = await self._request("GET", BLUETOOTH)
            if type(tag) is not str or re.fullmatch(r'"[0-9a-f]{64}"', tag) is None:
                raise ControllerLinkError("controller_update_required")
            return _decode(raw), tag
        if type(document) is not dict or etag is None:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", BLUETOOTH, document=document, etag=etag)
        return _decode(raw)

    async def async_valves(self, document=None):
        """GET the radiator valves, or POST the whole valve record; returns what the E32 stored.

        A refusal raises HeatingPlanRejected with the E32's error name
        (invalid_valve_name, duplicate_valve, unknown_room, ...: 400;
        save_unconfirmed: 503); firmware without valves raises
        controller_update_required.
        """
        if document is None:
            return await self.async_read(HEATING_TRV)
        if type(document) is not dict:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", HEATING_TRV, document=document)
        return _decode(raw)

    async def async_boiler_settings(self):
        """GET /boiler/settings: the settings table, the values, the open change and the last result.

        Firmware without the boiler settings raises controller_update_required.
        """
        return await self.async_read(BOILER_SETTINGS)

    async def async_boiler_settings_post(self, path, document):
        """POST one boiler settings request; returns (HTTP status, answer document).

        202: the E32 started the change; 200: done, or ``attendance_required`` (the token is in the
        answer's settings transaction). A refusal raises BoilerSettingsRejected with the E32's name.
        """
        if path not in BOILER_SETTINGS_POSTS or type(document) is not dict:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, status = await self._request("POST", path, document=document)
        return status, _decode(raw)

    async def async_shelly(self, document=None):
        """GET the Shelly record (no secrets), or POST the whole record; returns what the E32 stored.

        A refusal raises HeatingPlanRejected with the E32's error name (invalid_..., unknown_field: 400;
        save_unconfirmed: 503); firmware without Shelly raises controller_update_required.
        """
        if document is None:
            return await self.async_read(SHELLY_CONFIG)
        if type(document) is not dict:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", SHELLY_CONFIG, document=document)
        return _decode(raw)

    async def async_shelly_status(self):
        """GET /status/shelly: the devices, the circuits and each BLU Gateway's valves (E32 1.1)."""
        return await self.async_read(SHELLY_STATUS)

    async def async_shelly_circuit(self, command):
        """POST the owner's pump override of one circuit; returns the E32's Shelly status.

        A refusal raises HeatingPlanRejected (unknown_circuit, unknown_device: 404; invalid_request,
        invalid_pump, invalid_minutes, circuit_without_pump: 400).
        """
        if type(command) is not dict:
            raise ControllerLinkError("controller_request_invalid")
        raw, _, _ = await self._request("POST", SHELLY_CIRCUIT, document=command)
        return _decode(raw)

    async def async_config_backup(self, request):
        """POST one backup request (export, validate or apply); returns the E32's answer and status.

        The request may hold the backup passphrase: it goes to the E32 only and
        is never part of an error. A refusal raises BackupRejected with the
        E32's error name (boiler_owned, busy, settings_changed: 409;
        wrong_passphrase, not_a_backup, newer_schema, ...: 400; 413; 503; 500).
        """
        if type(request) is not dict or request.get("action") not in ("export", "validate", "apply"):
            raise ControllerLinkError("controller_request_invalid")
        raw, _, status = await self._request("POST", CONFIG_BACKUP, document=request)
        return _decode(raw), status

    async def async_save_settings(self, document, etag):
        if type(document) is not dict:
            raise ControllerLinkError("controller_request_invalid")
        await self._request("POST", "/config/device", document=document, etag=etag)

    async def async_upload_firmware(self, image):
        """One already verified firmware image over the local /ota route.

        Same multipart form as the device's update page, with a fixed length
        (the device web server does not accept chunked bodies) and paced 2 KiB
        blocks: the device erases flash sector by sector while it writes.
        """
        if (self._session is None or self._session.closed or not self._csrf
                or type(image) is not bytes or not 1000000 <= len(image) <= 0x3C0000):
            raise ControllerLinkError("controller_request_invalid")
        boundary = "OTFirmware" + secrets.token_hex(12)
        prefix = (f'--{boundary}\r\nContent-Disposition: form-data; name="type"\r\n\r\nfirmware\r\n'
                  f'--{boundary}\r\nContent-Disposition: form-data; name="size"\r\n\r\n{len(image)}\r\n'
                  f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="firmware.bin"\r\n'
                  'Content-Type: application/octet-stream\r\n\r\n').encode()
        suffix = f"\r\n--{boundary}--\r\n".encode()

        async def body():
            yield prefix
            for start in range(0, len(image), 2048):
                yield image[start:start + 2048]
                await asyncio.sleep(0.01)
            yield suffix

        headers = {"Origin": self.address, "X-OpenThermostat-CSRF": self._csrf,
                   "Content-Type": f"multipart/form-data; boundary={boundary}",
                   "Content-Length": str(len(prefix) + len(image) + len(suffix))}
        try:
            async with self._session.post(self.address + "/ota", data=body(), headers=headers,
                    allow_redirects=False, timeout=aiohttp.ClientTimeout(total=600)) as response:
                if response.status == 403 and await _error_name(response) == "password_change_required":
                    raise ControllerPasswordChangeRequired()
                if response.status in (401, 403):
                    raise ControllerLinkError("controller_auth_failed")
                if response.status == 409:
                    raise ControllerLinkError("controller_busy_or_conflict")
                if response.status != 200:
                    raise ControllerLinkError("controller_response_invalid")
        except (aiohttp.ClientError, TimeoutError):
            raise ControllerLinkError("controller_unreachable") from None

    async def async_reboot(self):
        _, _, status = await self._request("POST", "/updates/reboot")
        if status != 202:
            raise ControllerLinkError("controller_response_invalid")

    async def async_close(self):
        if self._session is None:
            return
        try:
            # Every sign-in ends with a logout: the E32 has only 4 web sessions and
            # refuses new sign-ins (429 session_capacity) while they are all in use.
            if (self._csrf or self._signed_in) and not self._session.closed:
                try:
                    async with asyncio.timeout(LOGOUT_TIMEOUT_S):
                        if not self._csrf:
                            self._csrf = (await self._read_session())["csrf"]
                        await self._request("POST", "/auth/logout")
                    self.logout_confirmed = True
                except (ControllerLinkError, TimeoutError) as err:
                    _logout_unconfirmed(err)
        finally:
            self._csrf = None
            self._signed_in = False
            self._session.cookie_jar.clear()
            await self._session.close()


def _logout_unconfirmed(err):
    """One clear line when the E32 did not confirm a sign-out: its web session stays in use for a while."""
    global _logout_warned
    why = f"no answer within {LOGOUT_TIMEOUT_S} s" if isinstance(err, TimeoutError) else str(err)
    now = asyncio.get_running_loop().time()
    if _logout_warned is None or not 0 <= now - _logout_warned < LOGOUT_WARNING_S:
        _logout_warned = now
        _LOGGER.warning("The E32 did not confirm the sign-out of Home Assistant (%s); that web session stays in use "
                        "until the E32 frees it after 2 minutes", why)
    else:
        _LOGGER.debug("The E32 did not confirm a sign-out again (%s)", why)


# The waits (s) before each new sign-in while every E32 web session is in use
# (429 session_capacity): a full E32 gives the least recently used session to a
# new sign-in once it was idle 2 minutes (WebAuthSession::evictIdleMs), so the
# last attempt (after 155 s) is past that. A full table is no failed sign-in:
# these attempts never count towards the E32's login limit (try_again_later).
SESSION_WAITS = (5, 10, 20, 30, 30, 30, 30)


async def async_login_waiting(client, password, waits=SESSION_WAITS, pause=asyncio.sleep):
    """client.async_login(password), signing in again after each wait while the E32 is full.

    pause(seconds) is awaited between attempts (it may raise to stop waiting).
    Still full after the last wait: ControllerLinkError("controller_no_free_session").
    Every other refusal is raised at once.
    """
    for wait in (*waits, None):
        try:
            return await client.async_login(password)
        except ControllerLinkError as err:
            if str(err) != "controller_session_capacity":
                raise
            if wait is None:
                raise ControllerLinkError("controller_no_free_session") from None
        await pause(wait)
