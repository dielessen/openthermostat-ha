"""Boiler settings (track W, W2): the boiler's own Classic settings, changed by the E32 on the owner's word.

The E32 V2 (firmware with track W, ``src/EMS/ClassicBoilerSettingsService.h``, docs/RESTAPI.md) keeps the one
write path: ``GET /boiler/settings`` (the table, the values, the open change, the last result),
``POST /boiler/settings/write`` (one value), ``/confirm`` (keep it, put it back, or acknowledge a revert that
could not be confirmed) and ``/persistent`` (the owner's switch, off by default). It also sends the retained
``fw/telemetry/boiler_settings`` (verified and unsupported settings, the open change, the last result).

Home Assistant only asks and shows:

- the telemetry is the feature detection: firmware without it never sends it, so Configure offers no
  "Boiler settings", there is no sensor and nothing is logged;
- "Boiler settings writes" (diagnostic sensor): off, ready, watching or failed, with the last result;
- an everyday setting the E32 verified on this boiler (reviewed evidence in the firmware, none today) gets a
  number, select or switch on the E32 device, also reachable in Configure → Heating and boiler → Boiler settings;
  installer settings never get one (they stay under Advanced in Configure);
- a revert that could not be confirmed raises the Repair "Check the boiler: a setting could not be put back"
  (acknowledged there), and a watched change that the E32 put back is a persistent notification.

Home Assistant signs in only for a request (RoomPlanLink.async_call, like every other E32 write): the write
(with its readback, a few seconds) and a keep or put-back. Since W1b a watch does not depend on any web session
and blocks no other E32 write: it runs to the end of its 15-minute window, where the E32 puts the value back by
itself. Home Assistant keeps the watcher's token (``attended_token``, shown only to the session that asked) in
the entry's Watch, so a keep or put-back from a later sign-in is accepted. Times are ages and remaining seconds
(``age_s``, ``watch_remaining_s``), never E32 uptime.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
import logging

from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er, issue_registry as ir
from homeassistant.util import dt as dt_util

from .const import CONF_TOPIC_PREFIX, DOMAIN

_LOGGER = logging.getLogger(__name__)

TOPIC = "fw/telemetry/boiler_settings"
KEY = "e32_boiler_settings"            # hass.data[DOMAIN][entry_id]: the entry's BoilerSettingsState
WATCH_KEY = "e32_boiler_settings_watch"  # ... and the Watch of a change Home Assistant asked for
FAILED_ISSUE = "e32_boiler_setting_failed"
MAX_TELEMETRY_BYTES = 2048

# How often a running change is read while the E32 reads and writes the boiler (seconds), and how long that
# may take: the old value, the write and the readback are a few seconds on the bus (a step is due within 5 s).
POLL_S = 1.0
STEP_TIMEOUT_S = 45.0
# One E32 result that arrives again (the E32 resends its telemetry on a real change and hourly) is the same
# result while its finish time, worked out from age_s, moves less than this.
SAME_RESULT_S = 120
# A boiler value from the boiler fields is shown again this often on the setting entities.
REFRESH_S = 30


@dataclass(frozen=True)
class Row:
    """One setting of src/EMS/BoilerSettingsTable.h (pinned by test_e32_boiler_settings)."""

    field: str        # the boiler_fields name of its current value
    kind: str         # switch, number or select
    unit: str         # bool, degC, K, %, min, code
    minimum: int
    maximum: int
    user_minimum: int
    user_maximum: int
    level: str        # user or installer (Advanced, at your own risk)


ROWS = {
    "heatingactivated": Row("heating_enabled", "switch", "bool", 0, 1, 0, 1, "user"),
    "heatingtemp": Row("configured_heating_temperature", "number", "degC", 30, 90, 30, 90, "user"),
    "burnmaxpower": Row("maximum_burner_power", "number", "%", 0, 100, 0, 100, "installer"),
    "boilhystoff": Row("heating_hysteresis_off", "number", "K", 2, 15, 2, 15, "installer"),
    "boilhyston": Row("heating_hysteresis_on", "number", "K", -15, -2, -15, -2, "installer"),
    "burnminperiod": Row("minimum_burner_period", "number", "min", 0, 60, 0, 60, "installer"),
    "pumpdelay": Row("pump_run_on", "number", "min", 0, 60, 0, 60, "installer"),
    "pumpmodmax": Row("pump_modulation_maximum", "number", "%", 0, 100, 0, 100, "installer"),
    "pumpmodmin": Row("pump_modulation_minimum", "number", "%", 0, 100, 0, 100, "installer"),
    "pumpmode": Row("configured_pump_mode", "select", "code", 0, 4, 0, 4, "installer"),
    "dhw.activated": Row("dhw_enabled", "switch", "bool", 0, 1, 0, 1, "user"),
    "dhw.seltemp": Row("selected_dhw_temperature", "number", "degC", 30, 80, 50, 60, "user"),
    "dhw.hyston": Row("dhw_hysteresis_on", "number", "K", -20, -2, -20, -2, "installer"),
    "dhw.chargeoptimization": Row("dhw_charge_optimisation_enabled", "switch", "bool", 0, 1, 0, 1, "installer"),
    "dhw.flowtempoffset": Row("dhw_flow_temperature_offset", "number", "K", 25, 40, 25, 40, "installer"),
    "dhw.circpump": Row("dhw_circulation_enabled", "switch", "bool", 0, 1, 0, 1, "installer"),
    "dhw.circmode": Row("configured_dhw_circulation_mode", "select", "code", 1, 7, 1, 7, "installer"),
    "dhw.disinfectiontemp": Row("dhw_disinfection_temperature", "number", "degC", 60, 80, 60, 80, "installer"),
    "dhw.comfort": Row("configured_dhw_comfort_mode", "select", "code", 0, 2, 0, 2, "user"),
}
# Switching these off really switches heating or hot water off on the boiler: the flow asks first.
SWITCHES_OFF_WARNED = {"heatingactivated": "off_heating", "dhw.activated": "off_dhw"}
# dhw.comfort: the index the E32 uses for each choice (BoilerSettingsTable.h: hot 0x00, eco 0xD8, intelligent 0xEC).
COMFORT = ("hot", "eco", "intelligent")
# The boiler fields' wire bytes of dhw.comfort, for the value shown on its select.
COMFORT_WIRE = {0x00: 0, 0xD8: 1, 0xEC: 2}
VERIFICATIONS = ("verified", "unverified", "unsupported")
REVERTED = frozenset({"reverted_mismatch", "reverted_unconfirmed", "reverted_window_end", "reverted_cancelled",
                      "restored_after_restart"})
STATES = ("off", "ready", "watching", "failed")
UNITS = {"degC": "°C", "K": "K", "%": "%", "min": "min"}


def key_of(setting):
    """A setting id as a key for texts and unique ids: dhw.seltemp → dhw_seltemp."""
    return setting.replace(".", "_")


def _int(value):
    return type(value) is int


def decode_document(value):
    """The GET /boiler/settings document (schema 2), checked; None when it is not one.

    Returns {"persistent", "available", "reason", "phase", "unresolved", "writes_today", "daily_cap",
    "watch_window_s", "transaction", "last", "settings": {id: row}} with only the settings Home Assistant knows.
    """
    if type(value) is not dict or value.get("schema") != 2 or type(value.get("settings")) is not list:
        return None
    settings = {}
    for item in value["settings"]:
        if type(item) is not dict or item.get("id") not in ROWS:
            continue
        row = ROWS[item["id"]]
        shown = item.get("value")
        verification = item.get("verification")
        settings[item["id"]] = {
            "value": shown if _int(shown) and row.minimum - 100 <= shown <= row.maximum + 100 else None,
            "verification": verification if verification in VERIFICATIONS else "unverified",
            "minimum": item["minimum"] if _int(item.get("minimum")) else row.minimum,
            "maximum": item["maximum"] if _int(item.get("maximum")) else row.maximum,
            "user_minimum": item["user_minimum"] if _int(item.get("user_minimum")) else row.user_minimum,
            "user_maximum": item["user_maximum"] if _int(item.get("user_maximum")) else row.user_maximum,
            "level": item["level"] if item.get("level") in ("user", "installer") else row.level,
            "last_result": item["last_result"] if type(item.get("last_result")) is str else None,
        }
    transaction = value.get("transaction")
    if type(transaction) is not dict or transaction.get("id") not in ROWS:
        transaction = None
    last = value.get("last")
    if type(last) is not dict or last.get("id") not in ROWS or type(last.get("result")) is not str:
        last = None
    return {"persistent": value.get("persistent_writes") is True, "available": value.get("available") is True,
            "compiled": value.get("compiled") is not False,
            "reason": value.get("reason") if type(value.get("reason")) is str else "",
            "phase": value.get("phase") if type(value.get("phase")) is str else "idle",
            "unresolved": value.get("unresolved") is True,
            "writes_today": value.get("writes_today") if _int(value.get("writes_today")) else 0,
            "daily_cap": value.get("daily_cap") if _int(value.get("daily_cap")) else 12,
            "watch_window_s": value.get("watch_window_s") if _int(value.get("watch_window_s")) else 900,
            "transaction": transaction, "last": last, "settings": settings}


def decode_telemetry(payload):
    """fw/telemetry/boiler_settings (schema 1), checked; None when it is not one."""
    if not isinstance(payload, (str, bytes)) or not payload or len(payload) > MAX_TELEMETRY_BYTES:
        return None
    try:
        value = json.loads(payload)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        return None
    if type(value) is not dict or value.get("schema") != 1:
        return None
    verified = value.get("verified")
    unsupported = value.get("unsupported")
    transaction = value.get("transaction")
    last = value.get("last")
    if type(transaction) is not dict or transaction.get("id") not in ROWS:
        transaction = None
    if type(last) is not dict or last.get("id") not in ROWS or type(last.get("result")) is not str:
        last = None
    return {"persistent": value.get("persistent_writes") is True,
            "phase": value.get("phase") if type(value.get("phase")) is str else "idle",
            "unresolved": value.get("unresolved") is True,
            "writes_today": value.get("writes_today") if _int(value.get("writes_today")) else 0,
            "verified": tuple(s for s in (verified if type(verified) is list else ()) if s in ROWS),
            "unsupported": tuple(s for s in (unsupported if type(unsupported) is list else ()) if s in ROWS),
            "transaction": transaction, "last": last}


def entity_settings(telemetry):
    """The settings that get an entity: verified on this boiler and everyday (user level), never installer ones."""
    if telemetry is None:
        return set()
    return {s for s in telemetry["verified"] if ROWS[s].level == "user"}


def writes_state(telemetry):
    """The sensor's state: failed (a revert not confirmed), watching (a change runs), off or ready."""
    if telemetry is None:
        return None
    if telemetry["unresolved"]:
        return "failed"
    if telemetry["transaction"] is not None or telemetry["phase"] != "idle":
        return "watching"
    return "ready" if telemetry["persistent"] else "off"


# -- words ---------------------------------------------------------------------------------------------------

def setting_name(texts, setting):
    return texts.get("name_" + key_of(setting), setting)


def value_text(texts, setting, value):
    """A value in words with its unit: 60 °C, On, Eco: saves gas, 3 × 3 minutes an hour."""
    if value is None or not _int(value):
        return texts.get("value_unknown", "-")
    row = ROWS[setting]
    if row.kind == "switch":
        return texts.get("value_on" if value else "value_off", str(value))
    if setting == "dhw.comfort":
        return texts.get("choice_" + COMFORT[value], str(value)) if 0 <= value < len(COMFORT) else str(value)
    if setting == "pumpmode":
        return texts.get("pump_0", "0") if value == 0 else texts.get("pump_fixed", "{n}").format(n=value)
    if setting == "dhw.circmode":
        return texts.get("circ_7", "7") if value == 7 else texts.get("circ_n", "{n}").format(n=value)
    return f"{value} {UNITS.get(row.unit, '')}".strip()


def choices(texts, setting, low, high):
    """The select options of a select or switch setting between low and high: [{"value", "label"}]."""
    return [{"value": str(v), "label": value_text(texts, setting, v)} for v in range(low, high + 1)]


def range_text(texts, setting, low, high):
    row = ROWS[setting]
    if row.kind != "number":
        return texts.get("range_choices", "")
    return texts.get("range", "{low} – {high}").format(low=value_text(texts, setting, low),
                                                        high=value_text(texts, setting, high))


def verification_text(texts, verification):
    return texts.get("verification_" + verification, verification)


def result_text(texts, result):
    if result is None:
        return ""
    return texts.get("result_" + ("reverted" if result.startswith("reverted_") else result), result)


# -- one request on one E32 sign-in --------------------------------------------------------------------------

class SettingsCall:
    """The boiler settings requests on one signed-in client (inside RoomPlanLink.async_call)."""

    def __init__(self, client):
        self.client = client
        self.document = None
        self.token = None

    def _keep(self, document):
        doc = decode_document(document)
        if doc is not None:
            self.document = doc
            transaction = (document.get("transaction") if type(document) is dict else None) or {}
            token = transaction.get("attended_token")
            if type(token) is str and transaction.get("owned_by_requester") is True:
                self.token = token
        return doc

    async def async_read(self):
        from .controller_link import ControllerLinkError
        doc = self._keep(await self.client.async_boiler_settings())
        if doc is None:
            raise ControllerLinkError("controller_response_invalid")
        return doc

    async def async_post(self, path, document):
        """(HTTP status, error name, settings) of one POST; a refusal raises BoilerSettingsRejected."""
        from .controller_link import BoilerSettingsRejected
        try:
            status, answer = await self.client.async_boiler_settings_post(path, document)
        except BoilerSettingsRejected as err:
            if err.settings is not None:
                self._keep(err.settings)
            raise
        settings = answer.get("settings") if type(answer) is dict else None
        doc = self._keep(settings) if settings is not None else None
        error = answer.get("error") if type(answer) is dict and type(answer.get("error")) is str else ""
        return status, error, doc

    async def async_until(self, done, timeout=STEP_TIMEOUT_S):
        """Read until done(doc) (or the timeout); returns the last document."""
        loop = asyncio.get_running_loop()
        end = loop.time() + timeout
        doc = self.document
        while doc is None or not done(doc):
            if loop.time() >= end:
                break
            await asyncio.sleep(POLL_S)
            doc = await self.async_read()
        return doc


@dataclass
class Watch:
    """A change Home Assistant asked for that the E32 now watches: the token keeps or puts it back."""

    setting: str
    value: object
    before: object
    token: str
    until: object  # when the E32 puts it back by itself (Home Assistant's clock, from watch_remaining_s)


def watch_of(hass, entry, doc=None):
    """The entry's Watch while the E32 still watches that change (doc: the E32's latest view), else None."""
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    watch = data.get(WATCH_KEY)
    if watch is None:
        return None
    if doc is not None:
        transaction = doc.get("transaction")
        if transaction is None or transaction.get("id") != watch.setting:
            data.pop(WATCH_KEY, None)  # kept, put back or ended at its window
            return None
    return watch


def remember_watch(hass, entry, doc, token):
    """After a write: the Watch of the change the E32 now watches (None when it is not watched)."""
    from datetime import timedelta
    transaction = doc.get("transaction")
    if not token or transaction is None:
        return None
    remaining = transaction.get("watch_remaining_s")
    remaining = remaining if _int(remaining) and remaining >= 0 else doc.get("watch_window_s", 900)
    watch = Watch(transaction["id"], transaction.get("value"), transaction.get("before"), token,
                  dt_util.now() + timedelta(seconds=remaining))
    hass.data[DOMAIN][entry.entry_id][WATCH_KEY] = watch
    return watch


def settled_for(setting):
    """No change of this setting runs any more (the E32 finished it)."""
    def settled(doc):
        transaction = doc.get("transaction")
        return transaction is None or transaction.get("id") != setting or doc.get("phase") == "idle"
    return settled


def watching_for(setting):
    """The change is read back and waits for the watcher (or finished without a watch)."""
    settled = settled_for(setting)
    return lambda doc: settled(doc) or doc.get("phase") == "watching"


def result_of(doc, setting):
    """The E32's result for this setting when it finished, else None."""
    last = doc.get("last") if doc else None
    return last if last is not None and last.get("id") == setting and settled_for(setting)(doc) else None


# -- the telemetry: sensor, entities, Repair and notification ------------------------------------------------

class BoilerSettingsState:
    """What the E32 last sent on fw/telemetry/boiler_settings, and who follows it."""

    def __init__(self, hass, entry, texts):
        self.hass, self.entry, self.texts = hass, entry, texts
        self.prefix = entry.data[CONF_TOPIC_PREFIX]
        self.telemetry = None
        self.last_seen = None    # (what the last result says, when it finished) of the result already seen
        self.last_when = None    # when the E32 finished that result (now - its age_s)
        self._listeners = []
        self._platforms = {}     # kind -> (async_add_entities, options)
        self._entities = {}      # setting -> entity
        self.sensor_added = False
        self.add_sensor = None
        self.value_source = None  # setting -> value; None: the boiler fields
        self.clock = dt_util.utcnow

    @property
    def offered(self):
        return self.telemetry is not None

    def add_listener(self, listener):
        self._listeners.append(listener)

        @callback
        def remove():
            if listener in self._listeners:
                self._listeners.remove(listener)
        return remove

    @callback
    def notify(self):
        for listener in list(self._listeners):
            listener()

    @callback
    def receive(self, payload):
        telemetry = decode_telemetry(payload)
        if telemetry is None:
            return
        first = self.telemetry is None
        self.telemetry = telemetry
        last = telemetry["last"]
        if last is None:
            self.last_seen = self.last_when = None
        elif self._new_result(last) and not first:
            self._put_back_notification(last)  # the first message after a start only sets the baseline
        transaction = telemetry["transaction"]
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {})
        watch = data.get(WATCH_KEY)
        if watch is not None and (transaction is None or transaction["id"] != watch.setting):
            data.pop(WATCH_KEY, None)  # the watch ended (kept, put back, or at its window)
        self.sync_failure(telemetry["unresolved"], last)
        self._sensor()
        self.sync_entities()
        self.notify()

    def _new_result(self, last):
        """Whether this is another result than the one seen before (the E32 resends the same one hourly)."""
        from datetime import timedelta
        age = last.get("age_s")
        finished = self.clock() - timedelta(seconds=age) if _int(age) and age >= 0 else None
        what = tuple(last.get(k) for k in ("id", "result", "mode", "detail", "before", "requested", "readback"))
        if self.last_seen is not None:
            seen, at = self.last_seen
            if seen == what and (finished is None or at is None
                                 or abs((finished - at).total_seconds()) < SAME_RESULT_S):
                return False
        self.last_seen, self.last_when = (what, finished), finished
        return True

    def set_sensor_adder(self, add):
        """The sensor platform's way to add "Boiler settings writes": at once when the E32 already sent them."""
        self.add_sensor = add
        self._sensor()

    @callback
    def _sensor(self):
        if not self.sensor_added and self.add_sensor is not None and self.telemetry is not None:
            self.sensor_added = True
            self.add_sensor()

    # The notification: a change the E32 put back by itself (not one the watcher put back).
    def _put_back_notification(self, last):
        if last["result"] not in REVERTED:
            return
        from homeassistant.components import persistent_notification
        texts, setting = self.texts, last["id"]
        why = texts.get("why_" + last["result"], texts.get("why_reverted_mismatch", ""))
        message = texts.get("notify_message", "{setting} {before} {why}").format(
            setting=setting_name(texts, setting), before=value_text(texts, setting, last.get("before")), why=why)
        persistent_notification.async_create(self.hass, message, title=texts.get("notify_title", "OpenThermostat"),
                                             notification_id=f"{DOMAIN}_boiler_setting_put_back_{self.entry.entry_id}")

    @callback
    def sync_failure(self, unresolved, last):
        """The Repair while a revert is not confirmed (the E32 writes no setting until it is acknowledged)."""
        issue = f"{FAILED_ISSUE}_{self.entry.entry_id}"
        if not unresolved:
            ir.async_delete_issue(self.hass, DOMAIN, issue)
            return
        texts = self.texts
        setting = last["id"] if last is not None else None
        name = setting_name(texts, setting) if setting else texts.get("a_setting", "-")
        before = value_text(texts, setting, last.get("before")) if setting else texts.get("value_unknown", "-")
        cause = failure_cause(texts, last)
        ir.async_create_issue(self.hass, DOMAIN, issue, is_fixable=True, is_persistent=False,
                              severity=ir.IssueSeverity.ERROR, translation_key=FAILED_ISSUE,
                              translation_placeholders={"setting": name, "before": before, "cause": cause},
                              data={"entry_id": self.entry.entry_id})

    # -- entities for verified settings ----------------------------------------------------------------------

    def add_platform(self, kind, async_add_entities, options):
        self._platforms[kind] = (async_add_entities, options)
        self.sync_entities()

    def unique_id(self, setting):
        return f"{self.prefix}_boiler_setting_{key_of(setting)}"

    @callback
    def sync_entities(self):
        """An entity for each everyday setting verified on this boiler; the entity of one that no longer is goes.

        Installer settings never get an entity, verified or not (owner, 6 Nov 2026): they stay in Configure →
        Heating and boiler → Boiler settings → Advanced, at your own risk.
        """
        verified = entity_settings(self.telemetry)
        for setting in sorted(verified - set(self._entities)):
            kind = ROWS[setting].kind
            if kind not in self._platforms:
                continue
            add, options = self._platforms[kind]
            from .e32_boiler_settings_entities import ENTITY_CLASSES
            entity = self._entities[setting] = ENTITY_CLASSES[kind](self, setting)
            add([entity], **options)
        registry = er.async_get(self.hass)
        wanted = {self.unique_id(s) for s in verified}
        for record in er.async_entries_for_config_entry(registry, self.entry.entry_id):
            if record.unique_id.startswith(f"{self.prefix}_boiler_setting_") and record.unique_id not in wanted:
                registry.async_remove(record.entity_id)
        for setting in [s for s in self._entities if s not in verified]:
            del self._entities[setting]

    def value(self, setting):
        """The setting's value now (the boiler fields the E32 reads), or None."""
        if self.value_source is not None:
            return self.value_source(setting)
        return boiler_value(self.hass, self.entry, setting)

    async def async_write(self, setting, value):
        """A verified setting from its entity: written at once and read back; raises HomeAssistantError."""
        from homeassistant.exceptions import HomeAssistantError
        reason = await async_write_verified(self.hass, self.entry, setting, value)
        if reason is not None:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="boiler_setting_refused",
                                     translation_placeholders={"setting": setting_name(self.texts, setting),
                                                               "reason": reason})
        self.notify()


def failure_cause(texts, last):
    """Why the E32 could not confirm a put-back, in words (from the result's detail and readback)."""
    setting = last["id"] if last is not None else None
    name = setting_name(texts, setting) if setting else texts.get("a_setting", "-")
    before = value_text(texts, setting, last.get("before")) if setting else texts.get("value_unknown", "-")
    readback = last.get("readback") if last is not None else None
    detail = (last or {}).get("detail") or ""
    shown = value_text(texts, setting, readback) if setting and _int(readback) else None
    if detail == "revert_not_sent":
        return texts.get("cause_not_sent", "").format(setting=name)
    if detail == "no_answer":
        return texts.get("cause_restart_no_answer", "").format(setting=name)
    if detail == "unexpected_value" and shown is not None:
        return texts.get("cause_restart_value", "").format(setting=name, readback=shown)
    if shown is not None:
        cause = texts.get("cause_readback", "").format(setting=name, before=before, readback=shown)
    else:
        cause = texts.get("cause_no_answer", "").format(setting=name)
    if detail and detail not in ("revert_not_read_back", "unexpected_value"):
        cause += " " + texts.get("cause_detail", "({detail})").format(detail=detail)
    return cause


def boiler_value(hass, entry, setting):
    """The value of a setting in the boiler fields (as the E32 table counts it), or None."""
    from .boiler_fields import INDEX_BY_NAME, spec
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    client = getattr(state.get("v1_connection"), "client", None) or state.get("boiler_source")
    cache = getattr(client, "boiler_fields", None)
    index = INDEX_BY_NAME.get(ROWS[setting].field)
    if cache is None or index is None:
        return None
    try:
        reading = cache.reading(index, client.clock())
    except Exception:  # noqa: BLE001 - a value that cannot be read is no value
        return None
    if not reading or not reading.get("usable") or not _int(reading.get("raw")):
        return None
    raw, divisor = reading["raw"], spec(index)[2]
    if setting == "dhw.comfort":
        return COMFORT_WIRE.get(raw)
    if ROWS[setting].kind == "switch":
        return 1 if raw else 0
    return round(raw / divisor) if divisor != 1 else raw


async def async_write_verified(hass, entry, setting, value):
    """Write a verified setting (no watch) and wait for the readback; None on success, else the reason in words."""
    from .controller_link import (BOILER_SETTINGS_CONFIRM, BOILER_SETTINGS_WRITE, BoilerSettingsRejected,
                                  ControllerLinkError)
    from .e32_system import link_for
    state = hass.data[DOMAIN][entry.entry_id].get(KEY)
    texts = state.texts if state is not None else {}
    link = link_for(hass, entry)
    if link is None:
        return texts.get("reason_unreachable", "{error}").format(error="no_connection")

    async def write(client):
        call = SettingsCall(client)
        _, error, _ = await call.async_post(BOILER_SETTINGS_WRITE, {
            "id": setting, "value": int(value)})  # an everyday setting in its everyday range: never advanced
        if error == "attendance_required":
            # No longer verified on this boiler: stop the armed probe, nothing is written.
            if call.token:
                await call.async_post(BOILER_SETTINGS_CONFIRM, {"attended_token": call.token, "keep": False})
            return texts.get("reason_not_verified", "not verified")
        last = result_of(await call.async_until(settled_for(setting)), setting)
        if last is None:
            return texts.get("reason_pending", "pending")
        if last["result"] in ("written", "unchanged"):
            return None
        return result_text(texts, last["result"])

    try:
        return await link.async_call(write, write=True)
    except BoilerSettingsRejected as err:
        return texts.get("refusal_" + err.error, texts.get("refusal_other", "{error}").format(error=err.error))
    except ControllerLinkError as err:
        return texts.get("reason_unreachable", "{error}").format(error=str(err))


def boiler_settings_state(hass, entry):
    return hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get(KEY)


def offered(hass, entry):
    """Configure → Heating and boiler offers Boiler settings: an E32 that sends them, with a stored connection."""
    from .e32_system import link_for
    state = boiler_settings_state(hass, entry)
    return state is not None and state.offered and link_for(hass, entry) is not None


async def async_setup(hass, entry):
    """Follow fw/telemetry/boiler_settings of this E32 (product entries); returns the state."""
    from homeassistant.components import mqtt
    from homeassistant.helpers.event import async_track_time_interval
    from datetime import timedelta
    from .heating_link import topic_base
    from .options_navigation import async_flow_texts
    data = hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    state = data.get(KEY)
    if state is not None:
        return state  # the first platform set it up (the platforms start together)
    state = data[KEY] = BoilerSettingsState(hass, entry, {})
    state.texts.update(await async_flow_texts(hass, "boiler_settings_text"))

    @callback
    def received(message):
        state.receive(message.payload)

    @callback
    def unload():
        ir.async_delete_issue(hass, DOMAIN, f"{FAILED_ISSUE}_{entry.entry_id}")
        data.pop(WATCH_KEY, None)  # the watch itself goes on on the E32, to its window
        if data.get(KEY) is state:
            data.pop(KEY, None)

    entry.async_on_unload(unload)
    if not await mqtt.async_wait_for_mqtt_client(hass):
        return state  # no MQTT: nothing arrives, nothing is offered (and nothing to log)
    entry.async_on_unload(await mqtt.async_subscribe(hass, topic_base(hass, entry) + TOPIC, received))

    @callback
    def refresh(_now):
        state.notify()  # the setting entities show the boiler fields' latest value

    entry.async_on_unload(async_track_time_interval(hass, refresh, timedelta(seconds=REFRESH_S)))
    return state
