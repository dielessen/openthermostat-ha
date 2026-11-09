"""Boiler recognition (E4): which boiler the E32 recognised on the bus and whether it may control it.

The E32 (after 1.0.1) publishes the retained ``fw/config/boiler_capabilities``
(src/control/BoilerCapabilitiesReport.h, at most 600 B, on change and hourly):

    {"schema": 1, "table": "<8 hex>",
     "identity": {"product": 206 | null, "version": "2.1" | null, "family": "classic|plus|conflict|unknown"},
     "match": {"state": "unknown|read_only|probe_passed|verified|other_boiler", "reason": <code>,
               "confirmed": bool, "row_nvs_id": 1 | null},
     "control": {"route": "none|classic_1a|plus_2e0|plus_2e0_1a", "refresh_s": 60 | null},
     "capabilities": {"control", "flow_request", "stop", "dhw_during_heat"},
     "settings": {"verified": [ids], "tested": [ids], "more": n}}

The row is named from Home Assistant's own copy of the boiler control table (boiler_control_table.py,
generated with the firmware's); a boiler outside the rows, or a row this copy does not know, is named by
EMS-ESP's family name for its product (PRODUCT_NAMES, the Overview's catalogue), else "unknown model". The
match only classifies: nothing here changes how the E32 controls the boiler.

On the product device, once the topic arrived (older firmware: no entity, nothing logged): the sensor
"Boiler recognition" (state: not_recognised, read_only, probe_passed, verified, other_boiler; attributes
the product, version, family, model, route, reason and the state in one sentence). For other_boiler a
Repairs issue "A different boiler is connected", whose fix confirms the boiler on the E32
(POST /boiler/match/acknowledge, with the stored sign-in). The same words appear in Configure ->
Heating and boiler -> Boiler model and in "Your boiler" on the Learning tab (insight.py). EN/NL/PL,
the plan's texts (EMSPLUS-PLAN 3.6) and E2's reason words. Since E7 the sentence follows the family (sentence_key):
a Classic boiler keeps the Classic route, also unlisted or after another boiler; an EMS+ boiler with only its own
passed test waits for review and is not controlled.
"""
from __future__ import annotations

import json
import logging
import re

from homeassistant.components.repairs import RepairsFlow
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback

from .const import CONF_TOPIC_PREFIX, DOMAIN

_LOGGER = logging.getLogger(__name__)
TOPIC = "fw/config/boiler_capabilities"
MAX_BYTES = 1024
STATE_KEY = "boiler_capabilities"  # hass.data[DOMAIN][entry_id]: the last valid document, or absent
ISSUE = "boiler_other_boiler"
# The E32's "unknown" is a Home Assistant state of its own: the sensor says not_recognised.
STATES = ("not_recognised", "read_only", "probe_passed", "verified", "other_boiler")
E32_STATES = ("unknown", "read_only", "probe_passed", "verified", "other_boiler")
REASONS = ("awaiting_identity", "awaiting_family", "family_settling", "family_conflict", "unknown_product",
           "other_family", "version_not_listed", "unverified_profile", "not_supported", "tested_profile",
           "verified_profile", "other_boiler")
FAMILIES = ("unknown", "classic", "plus", "conflict")
ROUTES = ("none", "classic_1a", "plus_2e0", "plus_2e0_1a")
PROOF = ("unverified", "probe_passed", "verified", "not_supported")
CAPABILITIES = ("control", "flow_request", "stop", "dhw_during_heat")
SETTING_ID = re.compile(r"[a-z][a-z.]{0,31}")
VERSION = re.compile(r"[0-9]{1,3}\.[0-9]{1,3}")

TEXT = {
    "en": {
        "state.not_recognised": "Not recognised yet: the E32 is waiting for the boiler to identify itself.",
        "state.read_only": "Reading only: this boiler model has not been tested with OpenThermostat yet. The E32 shows "
                           "its values and what it would ask, but does not control it.",
        "state.probe_passed": "Tested by you: the E32 can control this boiler. Share the result so others can too.",
        "state.verified": "Verified: the E32 can control this boiler.",
        "state.other_boiler": "A different boiler is connected. Control is off until this boiler is confirmed.",
        # E7: the words per family. A Classic boiler keeps the Classic route (its own gate, not the table); an
        # EMS+ boiler with a passed test of its own waits for review (board::emsPlusProbePassedControl is off).
        "state.read_only.classic_unlisted": "Not in the list yet: the E32 controls it the Classic way, as it did before; "
                                            "share a recording so it can be listed.",
        "state.read_only.classic": "Not tested with OpenThermostat yet: the E32 controls it the Classic way, as it did "
                                   "before; share a recording so it can be tested.",
        "state.probe_passed.plus": "Tested by you: the result waits for review; the E32 does not control this boiler yet.",
        "state.other_boiler.classic": "A different boiler is connected. The E32 still controls it the Classic way; "
                                      "confirm the boiler so it is recognised again.",
        "reason.awaiting_identity": "Waiting for the boiler to identify itself",
        "reason.awaiting_family": "No boiler reports yet",
        "reason.family_settling": "Recognising the boiler (10 minutes)",
        "reason.family_conflict": "The boiler speaks two protocols, reading only",
        "reason.unknown_product": "This boiler model is not in the list yet",
        "reason.other_family": "This boiler talks differently than its listed model",
        "reason.version_not_listed": "This boiler software version is not tested yet",
        "reason.unverified_profile": "Not tested with OpenThermostat yet",
        "reason.not_supported": "Cannot be controlled safely (no clean stop)",
        "reason.tested_profile": "Tested on this boiler, not yet reviewed",
        "reason.verified_profile": "Verified for this boiler model",
        "reason.other_boiler": "A different boiler is connected",
        "unknown_model": "Unknown model",
        "product": "product {product}",
        "version": "version {version}",
        "recognised": "Recognised on the bus: {boiler}. {sentence}",
    },
    "nl": {
        "state.not_recognised": "Nog niet herkend: de E32 wacht tot de ketel zich meldt.",
        "state.read_only": "Alleen lezen: dit ketelmodel is nog niet getest met OpenThermostat. De E32 toont de waarden "
                           "en wat hij zou vragen, maar stuurt de ketel niet aan.",
        "state.probe_passed": "Door jou getest: de E32 kan deze ketel aansturen. Deel het resultaat, dan kunnen anderen "
                              "het ook.",
        "state.verified": "Geverifieerd: de E32 kan deze ketel aansturen.",
        "state.other_boiler": "Er hangt een andere ketel aan. Aansturen staat uit tot deze ketel bevestigd is.",
        "state.read_only.classic_unlisted": "Nog niet in de lijst: de E32 stuurt hem aan op de Classic-manier, zoals "
                                            "voorheen; deel een opname zodat hij in de lijst kan.",
        "state.read_only.classic": "Nog niet getest met OpenThermostat: de E32 stuurt hem aan op de Classic-manier, zoals "
                                   "voorheen; deel een opname zodat hij getest kan worden.",
        "state.probe_passed.plus": "Door jou getest: de uitslag wacht op beoordeling; de E32 stuurt deze ketel nog niet aan.",
        "state.other_boiler.classic": "Er hangt een andere ketel aan. De E32 stuurt hem nog aan op de Classic-manier; "
                                      "bevestig de ketel zodat hij opnieuw herkend wordt.",
        "reason.awaiting_identity": "Wacht tot de ketel zich meldt",
        "reason.awaiting_family": "Nog geen berichten van de ketel",
        "reason.family_settling": "Ketel wordt herkend (10 minuten)",
        "reason.family_conflict": "De ketel spreekt twee protocollen, alleen lezen",
        "reason.unknown_product": "Dit ketelmodel staat nog niet in de lijst",
        "reason.other_family": "Deze ketel praat anders dan zijn model in de lijst",
        "reason.version_not_listed": "Deze softwareversie van de ketel is nog niet getest",
        "reason.unverified_profile": "Nog niet getest met OpenThermostat",
        "reason.not_supported": "Niet veilig aan te sturen (geen schone stop)",
        "reason.tested_profile": "Getest op deze ketel, nog niet beoordeeld",
        "reason.verified_profile": "Geverifieerd voor dit ketelmodel",
        "reason.other_boiler": "Er hangt een andere ketel aan",
        "unknown_model": "Onbekend model",
        "product": "product {product}",
        "version": "versie {version}",
        "recognised": "Herkend op de bus: {boiler}. {sentence}",
    },
    "pl": {
        "state.not_recognised": "Jeszcze nie rozpoznany: E32 czeka, aż kocioł się przedstawi.",
        "state.read_only": "Tylko odczyt: ten model kotła nie był jeszcze testowany z OpenThermostat. E32 pokazuje jego "
                           "wartości i to, o co by poprosił, ale nim nie steruje.",
        "state.probe_passed": "Przetestowany przez Ciebie: E32 może sterować tym kotłem. Udostępnij wynik, aby inni też "
                              "mogli.",
        "state.verified": "Zweryfikowany: E32 może sterować tym kotłem.",
        "state.other_boiler": "Podłączono inny kocioł. Sterowanie jest wyłączone do czasu potwierdzenia tego kotła.",
        "state.read_only.classic_unlisted": "Jeszcze nie na liście: E32 steruje nim w sposób Classic, jak dotąd; "
                                            "udostępnij nagranie, aby można go było dodać do listy.",
        "state.read_only.classic": "Jeszcze nie testowany z OpenThermostat: E32 steruje nim w sposób Classic, jak dotąd; "
                                   "udostępnij nagranie, aby można go było przetestować.",
        "state.probe_passed.plus": "Przetestowany przez Ciebie: wynik czeka na ocenę; E32 jeszcze nie steruje tym kotłem.",
        "state.other_boiler.classic": "Podłączono inny kocioł. E32 nadal steruje nim w sposób Classic; potwierdź kocioł, "
                                      "aby został ponownie rozpoznany.",
        "reason.awaiting_identity": "Czekam, aż kocioł się przedstawi",
        "reason.awaiting_family": "Brak jeszcze komunikatów z kotła",
        "reason.family_settling": "Rozpoznawanie kotła (10 minut)",
        "reason.family_conflict": "Kocioł używa dwóch protokołów, tylko odczyt",
        "reason.unknown_product": "Tego modelu kotła nie ma jeszcze na liście",
        "reason.other_family": "Ten kocioł komunikuje się inaczej niż model z listy",
        "reason.version_not_listed": "Ta wersja oprogramowania kotła nie była testowana",
        "reason.unverified_profile": "Jeszcze nie testowany z OpenThermostat",
        "reason.not_supported": "Nie można bezpiecznie sterować (brak czystego zatrzymania)",
        "reason.tested_profile": "Przetestowany na tym kotle, jeszcze nie oceniony",
        "reason.verified_profile": "Zweryfikowany dla tego modelu kotła",
        "reason.other_boiler": "Podłączono inny kocioł",
        "unknown_model": "Nieznany model",
        "product": "produkt {product}",
        "version": "wersja {version}",
        "recognised": "Rozpoznany na magistrali: {boiler}. {sentence}",
    },
}


def _int(value, low, high):
    return type(value) is int and low <= value <= high


def parse(payload):
    """The validated document of a retained payload; None when empty (cleared) or invalid (ignored)."""
    if payload in ("", b"", None):
        return None
    try:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        if not isinstance(payload, str) or len(payload) > MAX_BYTES:
            return None
        value = json.loads(payload)
    except (TypeError, ValueError, UnicodeError, RecursionError):
        return None
    if type(value) is not dict or value.get("schema") != 1:
        return None
    identity, match, control = (value.get(k) for k in ("identity", "match", "control"))
    caps, settings = value.get("capabilities"), value.get("settings")
    if not all(type(part) is dict for part in (identity, match, control, caps, settings)):
        return None
    product, version = identity.get("product"), identity.get("version")
    if product is not None and not _int(product, 0, 255):
        return None
    if version is not None and (type(version) is not str or not VERSION.fullmatch(version)):
        return None
    row = match.get("row_nvs_id")
    if (identity.get("family") not in FAMILIES or match.get("state") not in E32_STATES
            or match.get("reason") not in REASONS or type(match.get("confirmed")) is not bool
            or (row is not None and not _int(row, 1, 255)) or control.get("route") not in ROUTES
            or any(caps.get(k) not in PROOF for k in CAPABILITIES)):
        return None
    refresh = control.get("refresh_s")
    if refresh is not None and not _int(refresh, 1, 255):
        return None
    lists = {}
    for key in ("verified", "tested"):
        items = settings.get(key)
        if type(items) is not list or len(items) > 32 or not all(type(i) is str and SETTING_ID.fullmatch(i) for i in items):
            return None
        lists[key] = list(items)
    table = value.get("table")
    return {"table": table if type(table) is str and re.fullmatch(r"[0-9a-f]{8}", table) else None,
            "product": product, "version": version, "family": identity["family"],
            "state": "not_recognised" if match["state"] == "unknown" else match["state"], "reason": match["reason"],
            "confirmed": match["confirmed"], "row_nvs_id": row, "route": control["route"], "refresh_s": refresh,
            "capabilities": {k: caps[k] for k in CAPABILITIES},
            "settings": {**lists, "more": settings.get("more") if _int(settings.get("more"), 0, 64) else 0}}


def row(doc):
    """(row id, model) of the document's table row in this Home Assistant's copy, or (None, None)."""
    from .boiler_control_table import ROWS
    entry = ROWS.get(doc.get("row_nvs_id")) if doc else None
    return (entry[0], entry[1]) if entry else (None, None)


def family_name(doc):
    """EMS-ESP's family name for the document's product (boiler_control_table.PRODUCT_NAMES), or None."""
    from .boiler_control_table import PRODUCT_NAMES
    return PRODUCT_NAMES.get(doc.get("product")) if doc else None


def table_current(doc):
    """Whether the E32's table is the one this Home Assistant ships (None: the E32 did not say)."""
    from .boiler_control_table import TABLE_VERSION
    return None if not doc or doc.get("table") is None else doc["table"] == TABLE_VERSION


def _lang(lang):
    return lang if lang in TEXT else "en"


def controls(doc):
    """Whether the E32 may control this boiler as the document says (E7): a Classic boiler always keeps the Classic
    route (its own gate and the takeover, not the table), any boiler whose row is verified too. An EMS+ boiler with
    only a passed test of its own is not controlled (board::emsPlusProbePassedControl is off)."""
    return bool(doc) and (doc["state"] == "verified" or doc["family"] == "classic")


def sentence_key(doc):
    """The TEXT key of the state's sentence, per family and route (E7): five states, words that are true for each."""
    state, classic = doc["state"], doc["family"] == "classic"
    if state == "read_only" and classic:
        return "state.read_only.classic_unlisted" if doc["reason"] == "unknown_product" else "state.read_only.classic"
    if state == "probe_passed" and not classic:
        return "state.probe_passed.plus"
    if state == "other_boiler" and classic:
        return "state.other_boiler.classic"
    return "state." + state


def state_sentence(doc, lang):
    """The state in one or two plain sentences (EMSPLUS-PLAN 3.6, true per family since E7), or None without one."""
    return TEXT[_lang(lang)][sentence_key(doc)] if doc else None


def reason_text(doc, lang):
    return TEXT[_lang(lang)]["reason." + doc["reason"]] if doc else None


def boiler_name(doc, lang):
    """"<model> (product 206, version 2.1)": the row's model, else EMS-ESP's family name for the product ("Nefit
    TopLine / Buderus Logamax plus GB162 (product 115, version 3.6)"), else "Unknown model (product 99)" or "Unknown model"."""
    t = TEXT[_lang(lang)]
    _, model = row(doc)
    parts = [t["product"].format(product=doc["product"])] if doc and doc.get("product") is not None else []
    if doc and doc.get("version"):
        parts.append(t["version"].format(version=doc["version"]))
    name = model or family_name(doc) or t["unknown_model"]
    return f"{name} ({', '.join(parts)})" if parts else name


def recognised_line(doc, lang):
    """One line for Configure -> Heating and boiler -> Boiler model, or "" without a document (older firmware)."""
    if not doc:
        return ""
    return TEXT[_lang(lang)]["recognised"].format(boiler=boiler_name(doc, lang), sentence=state_sentence(doc, lang))


def listening_replaced(doc):
    """"Your boiler" (insight.py): the E32 cannot control this boiler, so its "still listening" is this sentence."""
    return bool(doc) and not controls(doc)


def current(hass, entry_id):
    """The entry's last valid document, or None (older firmware, nothing received)."""
    data = getattr(hass, "data", None)
    state = data.get(DOMAIN, {}).get(entry_id) if isinstance(data, dict) and entry_id else None
    return state.get(STATE_KEY) if isinstance(state, dict) else None


def issue_id(entry_id):
    return f"{ISSUE}_{entry_id}"


class BoilerRecognitionSensor(SensorEntity):
    """Which boiler the E32 recognised and whether it may control it (a diagnostic of the boiler device)."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "boiler_recognition"
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(STATES)
    _unrecorded_attributes = frozenset({"sentence", "reason_text", "capabilities", "table_current"})

    def __init__(self, hass, entry_id, prefix, hub):
        from homeassistant.helpers.device_registry import DeviceInfo
        self._entry_id, self._hub = entry_id, hub
        self.added = False  # in Home Assistant now: only then is a state written
        from .ems_devices import boiler_identifier
        self._attr_unique_id = f"{prefix}_boiler_recognition"
        self._attr_device_info = DeviceInfo(identifiers={boiler_identifier(prefix)})  # 1.1.1: on the boiler

    def _doc(self):
        return current(self.hass, self._entry_id)

    @property
    def available(self):
        return bool(getattr(self._hub, "fresh", True))

    @property
    def native_value(self):
        doc = self._doc()
        return doc["state"] if doc else None

    @property
    def extra_state_attributes(self):
        doc = self._doc()
        if doc is None:
            return None
        from .learned_overview import language
        lang = language(self.hass)
        row_id, model = row(doc)
        return {"product": doc["product"], "version": doc["version"], "family": doc["family"],
                "model": model or family_name(doc),
                "profile": row_id, "route": doc["route"], "reason": doc["reason"], "reason_text": reason_text(doc, lang),
                "sentence": state_sentence(doc, lang), "confirmed": doc["confirmed"],
                "capabilities": doc["capabilities"], "settings_verified": doc["settings"]["verified"],
                "settings_tested": doc["settings"]["tested"], "table_current": table_current(doc)}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.added = True
        if self._hub is not None and hasattr(self._hub, "add_listener"):
            self.async_on_remove(self._hub.add_listener(self.async_write_ha_state))

    async def async_will_remove_from_hass(self):
        self.added = False
        await super().async_will_remove_from_hass()


@callback
def sync_issue(hass, entry, doc):
    """Show "A different boiler is connected" while the E32 says other_boiler; clear it otherwise."""
    from homeassistant.helpers import issue_registry as ir
    issue = issue_id(entry.entry_id)
    if not doc or doc["state"] != "other_boiler":
        ir.async_delete_issue(hass, DOMAIN, issue)
        return
    from .learned_overview import language
    ir.async_create_issue(hass, DOMAIN, issue, is_fixable=True, is_persistent=False,
                          severity=ir.IssueSeverity.WARNING, translation_key=ISSUE,
                          translation_placeholders={"name": entry.title,
                                                    "boiler": boiler_name(doc, language(hass))},
                          data={"entry_id": entry.entry_id})


async def async_setup_boiler_capabilities(hass, entry, async_add_entities, options=None):
    """Product entries: follow the retained fw/config/boiler_capabilities; the sensor appears with the first document."""
    from homeassistant.components import mqtt
    from homeassistant.helpers import issue_registry as ir
    from .heating_link import heating_hub, topic_base
    from .product import is_product
    if not is_product(entry):
        return
    state = hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    hub = heating_hub(hass, entry)
    holder = {"sensor": None}

    @callback
    def received(message):
        doc = parse(message.payload)
        if doc is None and message.payload not in ("", b"", None):
            return  # invalid: ignored, the last valid document stays
        if doc is None:
            state.pop(STATE_KEY, None)
        else:
            state[STATE_KEY] = doc
        if doc is not None and holder["sensor"] is None:
            holder["sensor"] = BoilerRecognitionSensor(hass, entry.entry_id, entry.data[CONF_TOPIC_PREFIX], hub)
            async_add_entities([holder["sensor"]], **(options or {}))
        elif holder["sensor"] is not None and holder["sensor"].added:
            holder["sensor"].async_write_ha_state()
        sync_issue(hass, entry, doc)

    await mqtt.async_wait_for_mqtt_client(hass)
    entry.async_on_unload(await mqtt.async_subscribe(hass, topic_base(hass, entry) + TOPIC, received))

    @callback
    def unloaded():
        state.pop(STATE_KEY, None)
        ir.async_delete_issue(hass, DOMAIN, issue_id(entry.entry_id))
    entry.async_on_unload(unloaded)


class OtherBoilerRepairFlow(RepairsFlow):
    """Fix of "A different boiler is connected": confirm on the E32 that this is the boiler now connected."""

    def __init__(self, issue_id, data):
        self._issue_id, self._data = issue_id, data if isinstance(data, dict) else {}

    async def async_step_init(self, user_input=None):
        # Home Assistant opens a repair with data={"issue_id": ...} as this step's input: never a submitted form.
        return await self.async_step_confirm_boiler()

    async def async_step_confirm_boiler(self, user_input=None):
        from homeassistant.helpers import issue_registry as ir
        from .controller_link import ControllerLinkError
        from .e32_system import ABORTS, async_e32_call, failure, link_for
        from .learned_overview import language
        entry = self.hass.config_entries.async_get_entry(self._data.get("entry_id"))
        link = link_for(self.hass, entry) if entry is not None else None
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        doc = current(self.hass, entry.entry_id)
        if not doc or doc["state"] != "other_boiler":
            ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
            return self.async_abort(reason="boiler_confirmed")
        placeholders = {"name": entry.title, "boiler": boiler_name(doc, language(self.hass)), "error": ""}
        if user_input is None:
            return self.async_show_form(step_id="confirm_boiler", description_placeholders=placeholders)
        try:
            answer = await async_e32_call(link, lambda c: c.async_boiler_match_acknowledge(), write=True)
        except ControllerLinkError as err:
            if str(err) == "controller_boiler_confirmed":
                ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
                return self.async_abort(reason="boiler_confirmed")
            key, values = failure(err)
            if key in ABORTS:
                return self.async_abort(reason=key, description_placeholders=values)
            return self.async_show_form(step_id="confirm_boiler", errors={"base": key},
                                        description_placeholders={**placeholders, **values})
        if type(answer) is not dict or answer.get("acknowledged") is not True:
            return self.async_show_form(step_id="confirm_boiler", errors={"base": "e32_settings_unconfirmed"},
                                        description_placeholders=placeholders)
        ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
        return self.async_create_entry(data={})
