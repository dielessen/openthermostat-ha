"""E32 firmware updates through Home Assistant, like ESPHome.

Home Assistant checks GitHub for the newest E32 release, downloads
firmware.bin, verifies its SHA-256 (GitHub's asset digest), size and embedded
version marker, and uploads it to the E32 over the local network (/ota, the
same route as the device's update page). The E32 itself makes no HTTPS
connection. Credentials are the ones stored by the controller connection step.

Tags: pre-releases such as ``v0.1.0-e32v2-beta.18`` (alpha < beta < rc) and
stable releases such as ``v1.0.0-e32v2``; a stable release is newer than its
release candidates. An installation is never offered a less mature channel than
the one it runs (like the firmware's own catalog): 1.0.0 is not offered 1.1.0-beta.1.

The entity keeps a record of its last install (attribute ``last_install``:
release, SHA-256, size, start, end, duration, result and the identity the E32
reports after its restart; never an address or a password). It is the Home
Assistant side of an update acceptance (docs/modern-thermostat/HA-UPDATE-ACCEPTANCE.en.md).

1.4.2 (HA-REREAD, plan 3.2): after a confirmed install the entity asks the room-plan link to read the E32's
abilities again (``_abilities_read_again`` → ``RoomPlanLink.request_refresh``), and it observes every such read
(``HeatingHub.add_firmware_listener``): an E32 that restarted on other firmware (installed from its own page, by
another Home Assistant, a downgrade) shows its version at once, not at the next six-hourly read (review HC-16).

1.4.2 (HA-SESSIONS, plan 3.16, review HC-10): every sign-in of this entity (the version read, the upload and the
confirmation every 5 s after it) passes the integration's session gate (controller_link.SessionGate: at most two
E32 web sessions of Home Assistant at once), so a browser on the E32's own pages keeps its sessions during an
update. Since a restart's version reaches the entity through that observer, the scheduled check signs in to the
E32 for its version only once a day (VERSION_READ_INTERVAL); GitHub is still asked every six hours. The read at
start-up and the retries after a failed read always go to the E32.
"""
from __future__ import annotations

import asyncio
from datetime import timedelta
import hashlib
import logging
import re
import time

import aiohttp
from homeassistant.components.update import UpdateDeviceClass, UpdateEntity, UpdateEntityFeature
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_call_later, async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import CONF_TOPIC_PREFIX, DOMAIN
from .controller_link import (ControllerClient, ControllerLinkError, ControllerLoginRejected, SESSION_WAITS,
                              async_login_waiting)
from .controller_setup_flow import CONTROLLER_ADDRESS, CONTROLLER_PASSWORD

_LOGGER = logging.getLogger(__name__)
REPOSITORY = "dielessen/open_thermostat"
CHECK_INTERVAL = timedelta(hours=6)
# The scheduled check reads the version from the E32 only when no read (its own, or the room-plan link's after an
# E32 restart) confirmed it for this long; the half hour keeps a six-hourly tick from just missing the day.
VERSION_READ_INTERVAL = timedelta(hours=24)
VERSION_READ_SLACK = timedelta(minutes=30)
# After a failed read of the installed version (E32 restarting, unreachable, all
# its web sessions in use, ...): try again after 1, 5 and 15 minutes, then the
# normal interval. A known version is kept meanwhile.
RETRY_DELAYS = (60, 300, 900)
_NUMBER = r"(0|[1-9]\d{0,8})"
TAG = re.compile(rf"v{_NUMBER}\.{_NUMBER}\.{_NUMBER}-e32v2(?:-(alpha|beta|rc)\.{_NUMBER})?")
MAX_IMAGE = 0x3C0000
CHANNELS = {"alpha": 0, "beta": 1, "rc": 2, None: 3}
STABLE = CHANNELS[None]
# last_install["result"]: how the last install started from Home Assistant ended.
RESULTS = ("installed", "download_failed", "verification_failed", "upload_failed", "not_confirmed")
INSTALL_RECORD = ("tag", "from_version", "sha256", "size", "started_at", "finished_at", "duration_s",
                  "result", "uploads", "reported")
_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
# Where a failed install stopped (last_install "result") -> the error Home Assistant shows, in the user's
# language (exceptions.<key>), instead of "Unknown error".
INSTALL_ERRORS = {"download_failed": "firmware_download_failed", "verification_failed": "firmware_verification_failed",
                  "upload_failed": "firmware_upload_failed", "not_confirmed": "firmware_not_confirmed"}


class _InstallFailed(Exception):
    """The install stopped where last_install's result says."""


def install_error(result, error=None):
    """The translated Home Assistant error for an install that stopped at ``result``."""
    return HomeAssistantError(translation_domain=DOMAIN, translation_key=INSTALL_ERRORS[result],
                              translation_placeholders={"error": error or "-"} if result == "upload_failed" else None)


def parse_tag(tag):
    """(major, minor, patch, channel rank, number) or None for a foreign tag.

    Channel rank: alpha 0, beta 1, rc 2, stable 3 (number 0).
    """
    match = TAG.fullmatch(tag) if isinstance(tag, str) else None
    if not match:
        return None
    major, minor, patch, channel, number = match.groups()
    return int(major), int(minor), int(patch), CHANNELS[channel], int(number or 0)


def is_stable(tag):
    key = parse_tag(tag)
    return key is not None and key[3] == STABLE


def utc_text(moment):
    return dt_util.as_utc(moment).strftime("%Y-%m-%dT%H:%M:%SZ")


def reported_identity(version):
    """The identity the E32 reports in /status/version (nothing else it sends)."""
    if not isinstance(version, dict) or parse_tag(version.get("version")) is None:
        return None
    identity = {"version": version["version"]}
    for key, field, length in (("source_commit", "source", 40), ("web_sha256", "web_sha256", 64),
                               ("elf_sha256", "sha256", 64)):
        value = version.get(field)
        valid = isinstance(value, str) and re.fullmatch(f"[0-9a-f]{{{length}}}", value) is not None
        identity[key] = value if valid else None
    return identity


def valid_install_record(record):
    """A last_install record exactly as this module writes it (a restored one is checked again)."""
    if not isinstance(record, dict) or set(record) != set(INSTALL_RECORD):
        return False
    reported = record["reported"]
    return (parse_tag(record["tag"]) is not None
            and (record["from_version"] is None or isinstance(record["from_version"], str)
                 and len(record["from_version"]) <= 64)
            and isinstance(record["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) is not None
            and type(record["size"]) is int and 0 < record["size"] <= MAX_IMAGE
            and all(isinstance(record[key], str) and _UTC.fullmatch(record[key]) is not None
                    for key in ("started_at", "finished_at"))
            and type(record["duration_s"]) in (int, float) and 0 <= record["duration_s"] <= 3600
            and record["result"] in RESULTS and type(record["uploads"]) is int and record["uploads"] in (0, 1)
            and (reported is None or isinstance(reported, dict) and reported == reported_identity(
                {"version": reported.get("version"), "source": reported.get("source_commit"),
                 "web_sha256": reported.get("web_sha256"), "sha256": reported.get("elf_sha256")})))


def select_release(releases, minimum_channel=0):
    """The newest published E32 release with a firmware.bin and a SHA-256 digest.

    Releases of a less mature channel than minimum_channel (a rank) are skipped.
    """
    best = None
    for release in releases if isinstance(releases, list) else []:
        if not isinstance(release, dict) or release.get("draft"):
            continue
        key = parse_tag(release.get("tag_name"))
        asset = next((a for a in release.get("assets") or [] if isinstance(a, dict)
                      and a.get("name") == "firmware.bin"
                      and re.fullmatch(r"sha256:[0-9a-f]{64}", a.get("digest") or "")), None)
        if key is None or key[3] < minimum_channel or asset is None or not isinstance(asset.get("size"), int):
            continue
        if not 1000000 <= asset["size"] <= MAX_IMAGE:
            continue
        candidate = {"key": key, "tag": release["tag_name"], "size": asset["size"],
                     "sha256": asset["digest"][7:], "url": asset.get("browser_download_url"),
                     "page": release.get("html_url"), "notes": release.get("body") or ""}
        if best is None or key > best["key"]:
            best = candidate
    return best


def verify_image(image, release):
    """Only the exact firmware.bin of that release may be uploaded."""
    return (isinstance(image, bytes) and len(image) == release["size"]
            and hashlib.sha256(image).hexdigest() == release["sha256"]
            and f"OT_E32V2_OTA_V1:{release['tag']}:".encode() in image)


class E32FirmwareUpdate(UpdateEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "e32_firmware"  # "Firmware" (EN/NL)
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.RELEASE_NOTES

    def __init__(self, hass, entry):
        self.hass, self._entry = hass, entry
        prefix = entry.data[CONF_TOPIC_PREFIX]
        self._attr_unique_id = f"{prefix}_e32_firmware"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, prefix)})
        self._release = None
        self._last_install = None
        self._channel = 0  # the channel rank of the last installed version read from the E32
        self._lock = asyncio.Lock()
        self._failures = 0  # failed reads in a row (RETRY_DELAYS)
        self._retry = None  # the scheduled retry (async_call_later), or None
        self._confirmed_at = None  # time.monotonic() of the last version read from the E32 (own or the link's)

    @property
    def available(self):
        """Unavailable only while no installed version was ever known (never "unknown" for a
        known E32 that is briefly unreachable: its last known version stays)."""
        return self._attr_installed_version is not None

    def _set_installed(self, version):
        """A version the E32 reported (or that a restart restored); its channel follows.

        A version the release tags do not know (a local or development build) shows as installed, with no
        update offered (version_is_newer), instead of an entity that stays unavailable for good.
        """
        key = parse_tag(version)
        if key is None:
            if type(version) is not str or not version.strip() or len(version) > 64:
                return False
        else:
            self._channel = key[3]
        self._attr_installed_version = version
        if self._attr_latest_version is None:
            self._attr_latest_version = version
        self._sync_device_version()
        return True

    def _sync_device_version(self):
        """The E32 device shows its firmware version as its software version (beta.23)."""
        if getattr(self, "hass", None) is None or self.registry_entry is None or not self._attr_installed_version:
            return
        from homeassistant.helpers import device_registry as dr
        registry = dr.async_get(self.hass)
        device = registry.async_get(self.registry_entry.device_id) if self.registry_entry.device_id else None
        if device is not None and device.sw_version != self._attr_installed_version:
            registry.async_update_device(device.id, sw_version=self._attr_installed_version)
            # The room devices show the E32's version too (room_device, 1.3).
            from .room_device import sync_room_devices
            entry = getattr(self, "_entry", None)
            hub = self.hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("heating_hub") if entry is not None else None
            if hub is not None:
                sync_room_devices(self.hass, entry, hub)

    def version_is_newer(self, latest_version, installed_version):
        latest, installed = parse_tag(latest_version), parse_tag(installed_version)
        # An unknown installed version (a development build) is never replaced by an offer.
        return latest is not None and installed is not None and latest > installed

    @property
    def last_install(self):
        return self._last_install

    @property
    def extra_state_attributes(self):
        return {"last_install": self._last_install} if self._last_install else None

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        record = last.attributes.get("last_install") if last is not None else None
        if self._last_install is None and isinstance(record, dict):
            record = {key: dict(value) if isinstance(value, dict) else value for key, value in record.items()}
            if valid_install_record(record):
                self._last_install = record
        # The last known versions survive a Home Assistant restart: the state before it,
        # else what the last install confirmed. The E32's MQTT topics carry no version.
        if self._attr_installed_version is None:
            restored = last.attributes.get("installed_version") if last is not None else None
            if not self._set_installed(restored) and self._last_install is not None:
                reported = self._last_install.get("reported")
                self._set_installed(reported.get("version") if isinstance(reported, dict) else None) or (
                    self._last_install["result"] == "installed" and self._set_installed(self._last_install["tag"]))
            latest = last.attributes.get("latest_version") if last is not None else None
            if parse_tag(latest) is not None and self._attr_installed_version is not None:
                self._attr_latest_version = latest
        self.async_on_remove(self._cancel_retry)
        hub = self._hub()
        if hub is not None and hasattr(hub, "add_firmware_listener"):
            self.async_on_remove(hub.add_firmware_listener(self._firmware_read))
        self._sync_device_version()

    def _hub(self):
        """The entry's heating hub (heating_link.heating_hub: made here when this platform asks first), or None."""
        entry = getattr(self, "_entry", None)
        entry_id = getattr(entry, "entry_id", None)
        data = getattr(self.hass, "data", None) if getattr(self, "hass", None) is not None else None
        if entry_id is None or not isinstance(data, dict) or not isinstance(data.get(DOMAIN, {}).get(entry_id), dict):
            return None
        from .heating_link import heating_hub
        return heating_hub(self.hass, entry)

    def _firmware_read(self, version):
        """HA-REREAD observer: the room-plan link read the E32's abilities again after a restart; the version it
        found is the installed one now (the E32 device and the room devices follow, _sync_device_version)."""
        if version is None or not self._set_installed(version):
            return
        self._confirmed_at = time.monotonic()
        self._failures = 0
        self._cancel_retry()
        if self.hass is not None and self.entity_id:
            self.async_write_ha_state()

    def _abilities_read_again(self, version):
        """HA-REREAD hook (plan 3.2), after a confirmed install: Home Assistant reads the E32's abilities again (the
        plan's features, its version and time zone) without a reload. Never in the way of the install's result."""
        try:
            link = getattr(self._hub(), "plan", None)
            if link is not None and hasattr(link, "request_refresh"):
                link.request_refresh(version)
        except Exception:  # noqa: BLE001 - the install itself succeeded
            _LOGGER.debug("OpenThermostat: could not ask for the E32's abilities after the install", exc_info=True)

    def _cancel_retry(self):
        if self._retry is not None:
            self._retry()
            self._retry = None

    def _schedule_retry(self):
        """The next read soon after a failure (1, 5, 15 min), then only the normal interval."""
        self._cancel_retry()
        if self._failures > len(RETRY_DELAYS) or self.hass is None:
            return
        delay = RETRY_DELAYS[self._failures - 1]

        async def retry(_now):
            self._retry = None
            await self.async_refresh()
        self._retry = async_call_later(self.hass, delay, retry)

    async def async_release_notes(self):
        return self._release["notes"] if self._release else None

    def _client(self):
        return ControllerClient(self._entry.data[CONTROLLER_ADDRESS])

    async def _sign_in(self, client, waits=()):
        """Sign in with the stored password, never with one the E32 refused before (one latch for every
        part of the entry, e32_access, R4-05); waits: the pauses for a free E32 web session."""
        from .e32_access import mark_rejected, password_rejected, report_password
        password = self._entry.data[CONTROLLER_PASSWORD]
        if password_rejected(self.hass, self._entry, password):
            raise ControllerLoginRejected()  # wait for the new password; Repairs asks for it
        try:
            if waits:
                await async_login_waiting(client, password, waits)
            else:
                await client.async_login(password)
        except ControllerLoginRejected:
            mark_rejected(self.hass, self._entry, password)
            raise
        report_password(self.hass, self._entry, getattr(client, "default_password", None))

    def _version_known(self):
        """The version was read from the E32 (here or by the room-plan link) less than a day ago, and the last read
        did not fail: the scheduled check need not sign in for it (HA-SESSIONS)."""
        return (self._confirmed_at is not None and not self._failures and self._attr_installed_version is not None
                and time.monotonic() - self._confirmed_at
                < (VERSION_READ_INTERVAL - VERSION_READ_SLACK).total_seconds())

    async def _read_version(self):
        """The installed version from the E32. Only a successful read changes it: an unreachable or busy E32
        (restarting, all web sessions in use) or a refused password keeps the last known one (and its channel).
        A refused password is a Repairs item."""
        try:
            async with self._client() as client:
                await self._sign_in(client)
                version = await client.async_read("/status/version")
            if not self._set_installed(version.get("version") if isinstance(version, dict) else None):
                raise ControllerLinkError("controller_response_invalid")
            self._confirmed_at = time.monotonic()
            self._failures = 0
            self._cancel_retry()
        except ControllerLoginRejected:
            pass  # Repairs asks for the new password; no retries until then
        except (ControllerLinkError, TimeoutError) as err:
            self._failures += 1
            _LOGGER.debug("E32 firmware version not read (%s); attempt %d", err, self._failures)
            self._schedule_retry()

    async def async_refresh(self, _now=None):
        """Read the installed version from the E32 and the newest release from GitHub.

        ``_now``: the six-hourly schedule (async_track_time_interval). It skips the E32 while its version is known
        from the last day (_version_known); the start-up read and the retries (no ``_now``) always read it.
        """
        if self._lock.locked():
            return
        if _now is None or not self._version_known():
            await self._read_version()
        try:
            session = async_get_clientsession(self.hass)
            async with asyncio.timeout(30):
                async with session.get(f"https://api.github.com/repos/{REPOSITORY}/releases?per_page=20",
                                       headers={"Accept": "application/vnd.github+json"}) as response:
                    releases = await response.json() if response.status == 200 else None
            self._release = select_release(releases, self._channel)
        except (aiohttp.ClientError, TimeoutError, ValueError):
            pass  # GitHub unreachable: keep the last known release
        self._attr_latest_version = self._release["tag"] if self._release else self._attr_installed_version
        self._attr_release_url = self._release["page"] if self._release else None
        if self.hass is not None and self.entity_id:
            self.async_write_ha_state()

    async def async_install(self, version, backup, **kwargs):
        async with self._lock:
            release = self._release
            if release is None or (version is not None and version != release["tag"]):
                raise HomeAssistantError(translation_domain=DOMAIN, translation_key="firmware_release_unknown")
            self._attr_in_progress = True
            self.async_write_ha_state()
            started, clock, before = dt_util.utcnow(), time.monotonic(), self._attr_installed_version
            outcome = {"result": "download_failed", "uploads": 0, "reported": None}
            try:
                session = async_get_clientsession(self.hass)
                async with asyncio.timeout(300):
                    async with session.get(release["url"]) as response:
                        if response.status != 200:
                            raise _InstallFailed("download failed (HTTP %s)" % response.status)
                        chunks, total = [], 0
                        async for chunk in response.content.iter_chunked(65536):
                            total += len(chunk)
                            if total > MAX_IMAGE:
                                outcome["result"] = "verification_failed"
                                raise _InstallFailed("firmware larger than the update slot")
                            chunks.append(chunk)
                        image = b"".join(chunks)
                outcome["result"] = "verification_failed"
                if not verify_image(image, release):
                    raise _InstallFailed("SHA-256, size or version marker does not match the release")
                outcome["result"] = "upload_failed"
                async with self._client() as client:
                    # The owner pressed Install: wait for a free E32 web session (all 4 in use).
                    await self._sign_in(client, SESSION_WAITS)
                    await client.async_upload_firmware(image)
                outcome["uploads"], outcome["result"] = 1, "not_confirmed"
                # The E32 restarts itself; confirm the new version is running.
                for _ in range(36):
                    await asyncio.sleep(5)
                    try:
                        async with self._client() as client:
                            await self._sign_in(client)  # a refused password ends the wait (never tried twice)
                            running = await client.async_read("/status/version")
                        outcome["reported"] = reported_identity(running) or outcome["reported"]
                        if isinstance(running, dict) and running.get("version") == release["tag"]:
                            self._attr_installed_version = release["tag"]
                            self._confirmed_at = time.monotonic()
                            self._sync_device_version()
                            outcome["result"] = "installed"
                            self._abilities_read_again(release["tag"])
                            return
                    except ControllerLoginRejected:
                        raise  # never a second failed sign-in: Repairs asks for the new password
                    except ControllerLinkError:
                        continue
                raise _InstallFailed("the E32 did not report the new version within 3 minutes")
            except _InstallFailed as err:
                _LOGGER.warning("OpenThermostat: the E32 firmware %s was not installed: %s", release["tag"], err)
                raise install_error(outcome["result"]) from None
            except ControllerLinkError as err:
                _LOGGER.warning("OpenThermostat: the E32 firmware %s was not installed: E32 %s", release["tag"], err)
                raise install_error(outcome["result"], str(err) or type(err).__name__) from None
            except (aiohttp.ClientError, TimeoutError) as err:
                _LOGGER.warning("OpenThermostat: the E32 firmware %s was not installed: %s", release["tag"],
                                type(err).__name__)
                raise install_error(outcome["result"]) from None
            finally:
                self._last_install = {
                    "tag": release["tag"], "from_version": before if isinstance(before, str) else None,
                    "sha256": release["sha256"], "size": release["size"], "started_at": utc_text(started),
                    "finished_at": utc_text(dt_util.utcnow()),
                    "duration_s": round(time.monotonic() - clock, 1), **outcome}
                self._attr_in_progress = False
                self.async_write_ha_state()


async def async_setup_firmware_update(hass, entry, async_add_entities, **add_options):
    """Only with a stored controller connection (address and admin password)."""
    if not entry.data.get(CONTROLLER_ADDRESS) or not entry.data.get(CONTROLLER_PASSWORD):
        return
    entity = E32FirmwareUpdate(hass, entry)
    async_add_entities([entity], **add_options)
    entry.async_on_unload(async_track_time_interval(hass, entity.async_refresh, CHECK_INTERVAL))
    hass.async_create_task(entity.async_refresh())
