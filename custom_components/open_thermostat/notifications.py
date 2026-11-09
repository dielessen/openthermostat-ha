"""Notifications per room and for the house, on the phones of the people of the house (1.1.1).

Configure → Notifications. Nothing is on until the owner switches a room (or the house) on. A room's
messages go to the people of that room (Configure → Rooms → the room → Persons); a room without its own
people uses everyone who has a phone chosen.

Room messages:

* ``window``: a window or door open while the room heats: the E32 paused the room after the room's own
  delay (``comfort.window`` ``open``, ``comfort.opening`` window or door), and the room was colder than its
  target before the pause. Once per opening, no "closed again" message. Only for people at home.
* ``cold``: the room stays cold: more than COLD_MARGIN_C below its target for over an hour while the E32
  asks heat for it; a rise of its target (the switch point of its week program) starts the hour again, so it
  is also "still too cold an hour after the program time". Once per episode, only for people at home.
* ``sensor``: the room's temperature sensor has not reported for 30 minutes (the E32's ``stale`` / ``lost``,
  the heating problem sensor's ``room_without_measurement``). Home or not.
* ``battery``: the room's Bluetooth thermometer or one of its radiator valves reports a battery below
  BATTERY_LOW_PCT (the E32 reports a percentage, ``fw/state/ble/<id>`` ``battery`` and the valves'
  ``battery_pct``; the same limit as the dashboard's red badge; a valve keeps its own Repairs item too). Home or not.

House messages (Configure → Notifications → The house), only for the people with the tick "Also messages
about the house" (Configure → Notifications → People and phones, off by default). When the house is switched on
and nobody has the tick, a house message shows in Home Assistant instead, as for someone without a phone.
Two groups: the problems


* ``boiler_fault``: the boiler's display code is a fault (display_codes.FAULTS: the severity of its row in
  the boiler's table; the unconfirmed 0P is never one), for FAULT_SECONDS;
* ``e32_offline``: the E32 has not reported for 10 minutes, and ``e32_back`` when it reports again;
* ``awaiting_confirmation``: the E32 waits for the owner's confirmation before it controls the boiler;
* ``frost``: the E32 heats against frost (its active-control command ``frost_minimum`` or
  ``frost_unconfirmed``), for FROST_SECONDS;
* ``pressure_low``: the heating advice's low water pressure;

and the maintenance:

* ``maintenance``: the boiler's own maintenance message (the boiler field ``maintenance_message``, "H01".."H99";
  "none" is none), for MAINTENANCE_SECONDS, once per code;
* ``update``: a new version is available: the E32 Firmware update entity (``update:``) or the integration's own
  update entity (``update_ha:``, the Marketplace's entity of OpenThermostat) turns on; once per version, never
  again for the same version (kept over restarts);
* ``backup``: the daily backup of the E32 settings keeps failing (the Repairs item ``e32_backup_failing`` is
  raised); once per episode, over when a backup succeeds again;
* ``plan_ready`` (1.1.1 stage B): the E32 is ready to plan the heating and waits for the owner's one
  confirmation (heating_plan.py, its Repairs item); once per readiness: after a demotion the E32 checks again,
  and it is a new message when it is ready again.

The heating problem sensor's tracker (heating_problem.ProblemTracker) decides the E32 silence, the waiting
confirmation, the low pressure and the silent sensor, with its own hold times, so a hiccup never notifies;
this module runs its own tracker of that class, so a disabled "Heating problem" entity changes nothing here.

Delivery: ``notify.<service>`` per person (the "Phone or app" chosen in Configure), a short title and one
plain sentence in the Home Assistant language (English, Dutch or Polish, the catalogue below). One message
per episode; the same message for the same room at most once per COOLDOWN_SECONDS; room messages wait while
it is QUIET_HOURS and go out in the morning if the cause is still there (house messages always). A message
for people at home waits until one of them is home. Every message also fires the event
``open_thermostat_notification`` with the same data, for automations. When someone it is for has no phone
chosen, it shows as a persistent notification in Home Assistant instead (once per episode; it goes away
when the cause is gone). No entities: nothing to go stale on an upgrade.
"""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import callback

from .const import DOMAIN
from .heating_problem import ACTIVE_WARNING_SECONDS

_LOGGER = logging.getLogger(__name__)

CONF_NOTIFICATIONS = "notifications"
EVENT = "open_thermostat_notification"
ROOM_KINDS = ("window", "cold", "sensor", "battery")
HOUSE_PROBLEMS = ("boiler_fault", "e32_offline", "awaiting_confirmation", "frost", "pressure_low")
HOUSE_MAINTENANCE = ("maintenance", "update", "backup", "plan_ready")
HOUSE_KINDS = HOUSE_PROBLEMS + HOUSE_MAINTENANCE
# Message kinds that follow the tick of another kind (its key's first part -> the tick).
FOLLOWS = {"e32_back": "e32_offline", "update_ha": "update"}
# Only for the people of the room who are home now; the others go to them home or not.
HOME_ONLY = frozenset({"window", "cold"})
# The heating problems (heating_problem.ProblemTracker) that are a message here: problem id -> kind.
PROBLEM_KINDS = {"e32_offline": "e32_offline", "awaiting_confirmation": "awaiting_confirmation",
                 "pressure_low": "pressure_low", "room_without_measurement": "sensor"}
COLD_MARGIN_C = 1.0
COLD_SECONDS = 3600
BATTERY_LOW_PCT = 20      # below this: low (the dashboard's red battery badge)
BATTERY_OK_PCT = 25       # back to normal from this (a battery around 20 % never notifies twice)
BATTERY_SECONDS = 30 * 60
FROST_SECONDS = 10 * 60
MAINTENANCE_SECONDS = 10 * 60
FAULT_SECONDS = ACTIVE_WARNING_SECONDS  # the heating problem sensor's hold for a warning of the boiler route
FROST_COMMANDS = ("frost_minimum", "frost_unconfirmed")
COOLDOWN_SECONDS = 2 * 3600
QUIET_HOURS = (23, 7)     # local time, room messages only
CHECK_INTERVAL = timedelta(seconds=60)
# The people a message can go to: persons and device trackers (groups and on/off helpers say "someone").
PERSON_DOMAINS = ("person", "device_tracker")
# Notify services that are not one phone or app.
NOT_A_PHONE = ("send_message", "persistent_notification")
STORE_VERSION = 1

TITLE = {
    "en": {
        "window": "Window open in {room}",
        "door": "Door open in {room}",
        "cold": "{room} stays cold",
        "battery": "Battery low in {room}",
        "boiler_fault": "Boiler fault {code}",
        "e32_back": "E32 back",
        "awaiting_confirmation": "The E32 waits for your confirmation",
        "frost": "Frost protection on",
        "maintenance": "Boiler maintenance {code}",
        "update": "New E32 firmware {version}",
        "update_ha": "New OpenThermostat version {version}",
        "backup": "No recent backup of the E32 settings",
        "plan_ready": "The E32 is ready to plan",
    },
    "nl": {
        "window": "Raam open in {room}",
        "door": "Deur open in {room}",
        "cold": "{room} blijft koud",
        "battery": "Batterij bijna leeg in {room}",
        "boiler_fault": "Ketelstoring {code}",
        "e32_back": "E32 weer bereikbaar",
        "awaiting_confirmation": "De E32 wacht op je bevestiging",
        "frost": "Vorstbeveiliging aan",
        "maintenance": "Onderhoud ketel {code}",
        "update": "Nieuwe E32-firmware {version}",
        "update_ha": "Nieuwe versie van OpenThermostat {version}",
        "backup": "Geen recente back-up van de E32-instellingen",
        "plan_ready": "De E32 is klaar om te plannen",
    },
    "pl": {
        "window": "{room}: otwarte okno",
        "door": "{room}: otwarte drzwi",
        "cold": "{room}: zbyt zimno",
        "battery": "{room}: słaba bateria",
        "boiler_fault": "Usterka kotła {code}",
        "e32_back": "E32 znów dostępny",
        "awaiting_confirmation": "E32 czeka na Twoje potwierdzenie",
        "frost": "Ochrona przed mrozem włączona",
        "maintenance": "Konserwacja kotła {code}",
        "update": "Nowe oprogramowanie E32 {version}",
        "update_ha": "Nowa wersja OpenThermostat {version}",
        "backup": "Brak aktualnej kopii ustawień E32",
        "plan_ready": "E32 jest gotowy do planowania",
    },
}
TEXT = {
    "en": {
        "window": "A window in {room} is open, so the heating there is paused. It starts again once the window "
                  "is closed.",
        "door": "A door in {room} is open, so the heating there is paused. It starts again once the door is "
                "closed.",
        "cold": "{room} is at {temperature} °C while you want {target} °C, and has been too cold for over an hour. "
                "Check that the radiators or the floor get warm.",
        "battery": "The battery of the thermometer in {room} is at {battery} %. Replace it soon, so the E32 keeps "
                   "measuring this room.",
        "battery_valve": "The battery of a radiator valve in {room} is at {battery} %. Replace it soon, so the "
                         "valve keeps working.",
        "boiler_fault": "The boiler reports a fault, code {code}: {meaning}",
        "e32_back": "The E32 is reachable again and sends its values to Home Assistant.",
        "frost": "A room has cooled below 8 °C, so the E32 heats a little against frost. Check for an open window "
                 "and that the heating works.",
        "maintenance": "Your boiler asks for maintenance ({code}). Make an appointment with your installer.",
        "update": "A new version of the E32 firmware is available ({version}). Install it from Settings > Updates "
                  "when it suits you; the E32 confirms the takeover again afterwards.",
        "update_ha": "A new version of the OpenThermostat integration is available ({version}). Install it from "
                     "Settings > Updates when it suits you.",
        "backup": "Home Assistant could not back up the E32 settings for more than 3 days (last backup: {last}). "
                  "Check that the E32 is on and its web page opens, and that its password in Home Assistant is "
                  "still right; then press Back up E32 settings now on the E32 device.",
        "plan_ready": "The E32's predictions for {room} have been good for a week. Open Settings > Repairs to let it "
                      "plan the heating, or leave it as it is.",
    },
    "nl": {
        "window": "In {room} staat een raam open, dus de verwarming daar is gepauzeerd. Die gaat weer aan zodra "
                  "het raam dicht is.",
        "door": "In {room} staat een deur open, dus de verwarming daar is gepauzeerd. Die gaat weer aan zodra de "
                "deur dicht is.",
        "cold": "In {room} is het {temperature} °C, terwijl je {target} °C wilt, en dat al meer dan een uur. Kijk "
                "of de radiatoren of de vloer warm worden.",
        "battery": "De batterij van de thermometer in {room} staat op {battery} %. Vervang hem binnenkort, dan "
                   "blijft de E32 deze ruimte meten.",
        "battery_valve": "De batterij van een radiatorkraan in {room} staat op {battery} %. Vervang hem binnenkort, "
                         "dan blijft de kraan werken.",
        "boiler_fault": "De ketel meldt een storing, code {code}: {meaning}",
        "e32_back": "De E32 is weer bereikbaar en stuurt zijn waarden weer naar Home Assistant.",
        "frost": "Een ruimte is afgekoeld tot onder 8 °C, dus de E32 verwarmt een beetje tegen vorst. Kijk of er "
                 "een raam openstaat en of de verwarming werkt.",
        "maintenance": "Je ketel vraagt om onderhoud ({code}). Maak een afspraak met je installateur.",
        "update": "Er is een nieuwe versie van de E32-firmware ({version}). Installeer hem via Instellingen > "
                  "Updates als het je uitkomt; de E32 vraagt daarna opnieuw om je bevestiging van de overname.",
        "update_ha": "Er is een nieuwe versie van de OpenThermostat-integratie ({version}). Installeer hem via "
                     "Instellingen > Updates als het je uitkomt.",
        "backup": "Home Assistant kon al meer dan 3 dagen geen back-up van de E32-instellingen maken (laatste "
                  "back-up: {last}). Controleer of de E32 aan staat en zijn webpagina opent, en of zijn wachtwoord "
                  "in Home Assistant nog klopt; druk daarna op Nu een back-up van de E32 maken op het E32-apparaat.",
        "plan_ready": "De voorspellingen van de E32 voor {room} zijn al een week goed. Open Instellingen > Reparaties "
                      "om hem de verwarming te laten plannen, of laat het zoals het is.",
    },
    "pl": {
        "window": "{room}: otwarte jest okno, więc ogrzewanie w tym pomieszczeniu jest wstrzymane. Włączy się "
                  "ponownie po zamknięciu okna.",
        "door": "{room}: otwarte są drzwi, więc ogrzewanie w tym pomieszczeniu jest wstrzymane. Włączy się "
                "ponownie po zamknięciu drzwi.",
        "cold": "{room}: jest {temperature} °C, a chcesz {target} °C, i od ponad godziny jest za zimno. Sprawdź, "
                "czy grzejniki lub podłoga się nagrzewają.",
        "battery": "{room}: bateria termometru ma {battery} %. Wymień ją wkrótce, aby E32 nadal mierzył "
                   "temperaturę w tym pomieszczeniu.",
        "battery_valve": "{room}: bateria zaworu grzejnikowego ma {battery} %. Wymień ją wkrótce, aby zawór "
                         "nadal działał.",
        "boiler_fault": "Kocioł zgłasza usterkę, kod {code}: {meaning}",
        "e32_back": "E32 znów jest dostępny i wysyła swoje wartości do Home Assistant.",
        "frost": "W jednym z pomieszczeń temperatura spadła poniżej 8 °C, więc E32 lekko grzeje, chroniąc dom "
                 "przed mrozem. Sprawdź, czy nie jest otwarte okno i czy ogrzewanie działa.",
        "maintenance": "Twój kocioł wymaga konserwacji ({code}). Umów się z instalatorem.",
        "update": "Dostępna jest nowa wersja oprogramowania E32 ({version}). Zainstaluj ją w Ustawienia > "
                  "Aktualizacje, gdy Ci to odpowiada; potem E32 ponownie poprosi o potwierdzenie przejęcia.",
        "update_ha": "Dostępna jest nowa wersja integracji OpenThermostat ({version}). Zainstaluj ją w Ustawienia > "
                     "Aktualizacje, gdy Ci to odpowiada.",
        "backup": "Home Assistant od ponad 3 dni nie może utworzyć kopii ustawień E32 (ostatnia kopia: {last}). "
                  "Sprawdź, czy E32 jest włączony i jego strona się otwiera oraz czy jego hasło w Home Assistant "
                  "jest nadal poprawne; potem naciśnij Utwórz teraz kopię ustawień E32 na urządzeniu E32.",
        "plan_ready": "Prognozy E32 dla pomieszczenia {room} są dobre od tygodnia. Otwórz Ustawienia > Naprawy, aby "
                      "pozwolić mu planować ogrzewanie, albo zostaw to tak, jak jest.",
    },
}
# The title of a persistent notification (no phone chosen): the product name first, as the insight notes do.
PERSISTENT_TITLE = "OpenThermostat: {title}"


# -- the settings ------------------------------------------------------------------------------------------------


def notification_options(entry):
    """{"phones": {person: notify service}, "house_people": [person], "house": {"on", "kinds"},
    "rooms": {room id: {"on", "kinds"}}}.

    Unknown or invalid values fall back to the default: nothing on, every kind chosen once it is switched on,
    nobody with the tick "Also messages about the house".
    """
    raw = (getattr(entry, "options", None) or {}).get(CONF_NOTIFICATIONS)
    raw = raw if type(raw) is dict else {}
    phones = raw.get("phones") if type(raw.get("phones")) is dict else {}
    out = {"phones": {person: service for person, service in phones.items()
                      if type(person) is str and person.split(".")[0] in PERSON_DOMAINS
                      and type(service) is str and service and "." not in service},
           "house_people": [], "house": _switch(raw.get("house"), HOUSE_KINDS), "rooms": {}}
    ticked = raw.get("house_people") if type(raw.get("house_people")) is list else []
    out["house_people"] = sorted({p for p in ticked if type(p) is str and p.split(".")[0] in PERSON_DOMAINS})
    rooms = raw.get("rooms") if type(raw.get("rooms")) is dict else {}
    for room_id, value in rooms.items():
        if type(room_id) is str and room_id:
            out["rooms"][room_id] = _switch(value, ROOM_KINDS)
    return out


def _switch(value, kinds):
    value = value if type(value) is dict else {}
    chosen = value.get("kinds")
    chosen = [k for k in kinds if k in chosen] if type(chosen) is list else list(kinds)
    return {"on": value.get("on") is True, "kinds": chosen}


def anything_on(settings):
    return settings["house"]["on"] or any(room["on"] for room in settings["rooms"].values())


def enabled(settings, kind, room_id):
    """Whether a message of this kind for this room ("" for the house) is switched on."""
    if room_id:
        room = settings["rooms"].get(room_id)
        return room is not None and room["on"] and kind in room["kinds"]
    house = settings["house"]
    return house["on"] and FOLLOWS.get(kind, kind) in house["kinds"]


def with_room(settings, room_id, on, kinds):
    rooms = dict(settings["rooms"])
    rooms[room_id] = {"on": bool(on), "kinds": [k for k in ROOM_KINDS if k in kinds]}
    return {**settings, "rooms": rooms}


def with_house(settings, on, kinds):
    return {**settings, "house": {"on": bool(on), "kinds": [k for k in HOUSE_KINDS if k in kinds]}}


def with_house_person(settings, person, on):
    """The tick "Also messages about the house" of one person."""
    people = set(settings.get("house_people") or [])
    (people.add if on else people.discard)(person)
    return {**settings, "house_people": sorted(people)}


def with_phone(settings, person, service):
    phones = dict(settings["phones"])
    if service:
        phones[person] = service
    else:
        phones.pop(person, None)
    return {**settings, "phones": phones}


@callback
def save_notifications(hass, entry, settings):
    """Store the settings without a reload; the notifier reads them on its next check."""
    from .energy_input import ENERGY_ONLY_UPDATE
    options = {**entry.options, CONF_NOTIFICATIONS: settings}
    if options == dict(entry.options):
        return False
    state = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if state is not None:
        state[ENERGY_ONLY_UPDATE] = dict(options)  # the same no-reload marker as the comfort settings
    if not hass.config_entries.async_update_entry(entry, options=options) and state is not None:
        state.pop(ENERGY_ONLY_UPDATE, None)
    if state is not None and (notifier := state.get("notifier")) is not None:
        notifier.evaluate()
    return True


# -- the people ----------------------------------------------------------------------------------------------------


def room_people(entry, room_id):
    """The persons of a room (Configure → Rooms → the room → Persons) who can get a message."""
    from .e32_comfort import room_persons
    return [p for p in room_persons(entry, room_id) if p.split(".")[0] in PERSON_DOMAINS]


def house_people(hass, entry):
    """Everyone a phone can be chosen for: every person in Home Assistant and the people of the house and rooms."""
    from .e32_comfort import comfort_options, people_of
    people = {p for p in people_of(comfort_options(entry)) if p.split(".")[0] in PERSON_DOMAINS}
    people.update(state.entity_id for state in hass.states.async_all("person"))
    people.update(notification_options(entry)["phones"])
    return sorted(people)


def recipients(kind, room_id, people, phones, home):
    """(people, notify services, persistent) of one message, or None to wait (nobody of the room is home).

    ``people``: for a room its own persons (empty: everyone with a phone); for the house the persons with the
    tick "Also messages about the house" (empty: nobody, so it shows in Home Assistant only);
    ``phones``: {person: service}; ``home(person)``: True while that person is home. ``persistent``: someone it
    is for has no phone, or nobody is known at all; the message then also shows in Home Assistant.
    """
    chosen = list(people) if not room_id or people else list(phones)
    if kind in HOME_ONLY and chosen:
        chosen = [p for p in chosen if home(p)]
        if not chosen:
            return None
    services = list(dict.fromkeys(phones[p] for p in chosen if p in phones))
    return chosen, services, not chosen or any(p not in phones for p in chosen)


def quiet(local):
    """Between 23:00 and 07:00 local time: room messages wait."""
    start, end = QUIET_HOURS
    return local.hour >= start or local.hour < end


# -- what holds now ------------------------------------------------------------------------------------------------


def _number(value, low=-40, high=85):
    from .heating_link import number
    return number(value, low, high)


def frost_protection(hub):
    """Whether the E32 heats against frost now (its active-control command, ActiveHeatGuard)."""
    active = getattr(hub, "active", None)
    if type(active) is not dict:
        status = getattr(hub, "status", None)
        active = status.get("active") if type(status) is dict else None
    command = active.get("command") if type(active) is dict else None
    return (type(command) is dict and command.get("why") in FROST_COMMANDS
            and (_number(command.get("flow_c"), 1, 90) or 0) > 0)


def boiler_fault(state):
    """{code, meaning, advice} while the display code sensor's state is a fault (display_codes.FAULTS), else None."""
    from .display_codes import FAULTS
    if state is None or state.state in ("unknown", "unavailable", ""):
        return None
    attributes = state.attributes
    if attributes.get("severity") not in FAULTS:
        return None
    return {"code": state.state, "meaning": attributes.get("meaning") or "", "advice": attributes.get("advice") or ""}


def room_valve_batteries(hub, room_id):
    """The batteries (%) the radiator valves of a room report (e32_valves; empty without valves)."""
    from .e32_valves import batteries, room_valves
    room = room_valves(hub, room_id) if getattr(hub, "valves", None) else None
    return batteries(room) if type(room) is dict else []


def maintenance_code(state):
    """The boiler's maintenance code ("H01".."H99") while its maintenance message sensor shows one, else None."""
    if state is None or type(state.state) is not str:
        return None
    code = state.state.strip().upper()
    return code if len(code) == 3 and code[0] == "H" and code[1:].isdigit() and code != "H00" else None


def new_version(state):
    """The newer version an update entity offers while it is on (a new version available), else None."""
    if state is None or state.state != "on":
        return None
    version = state.attributes.get("latest_version")
    return version if type(version) is str and version.strip() else None


def integration_update(state):
    """Whether an update entity of another integration (the Marketplace) is the one of OpenThermostat itself."""
    title = state.attributes.get("title") or state.attributes.get("friendly_name") or ""
    return type(title) is str and "openthermostat" in title.lower().replace(" ", "")


def room_ble_sensors(hub, room_id):
    """The Bluetooth sensors of a room: the BLE sources of its E32 plan, else the one it measures with now."""
    plan = getattr(hub, "plan", None)
    room = plan.room(room_id) if plan is not None and getattr(plan, "plan", None) is not None else None
    if room is not None:
        return [s["id"] for s in room.get("sources") or [] if s.get("type") == "ble" and s.get("id")]
    source = (hub.rooms.get(room_id) or {}).get("source")
    return [source] if type(source) is str and source in hub.ble else []


class NotificationRules:
    """Which messages are due: when each cause started and which messages went out. Pure, so the tests can
    drive it with fake clocks (``now``: monotonic seconds as the hub's clock; ``wall``: unix seconds;
    ``local``: the local time of day)."""

    def __init__(self, sent=None, open_keys=(), episodes=None, announced=None):
        self.since = {}         # key -> since its cause holds (frost, fault, battery, maintenance)
        self.cold = {}          # room id -> (target, since it is too cold for that target)
        self.before = {}        # room id -> its target before a pause (did it want heat?)
        self.low = set()        # room ids whose thermometer or valve battery is low
        self.battery = {}       # room id -> (its lowest battery reported (%), "thermometer" | "valve")
        self.sent = dict(sent or {})   # key -> unix time of its last message
        self.open = set(open_keys)     # keys whose message went out and whose cause still holds
        self.last = {key: {} for key in self.open}  # what held at the last check
        self.fresh = True       # the E32's values were current at the last check
        # key -> the episode of its open message (the maintenance code): another one is a new message.
        self.episodes = {k: v for k, v in (episodes or {}).items() if k in self.open}
        # key -> the version whose "new version" message went out: never again for that version.
        self.announced = dict(announced or {})

    def found(self, hub, problems, fault, now, house=None):
        """{key: values} of every cause that holds long enough now; key "kind:room id" ("kind:" for the house).

        ``house``: what Home Assistant itself knows of the house's maintenance: ``maintenance`` (the boiler's
        maintenance code or None), ``updates`` ({key: version} of the update entities that are on) and
        ``backup`` (the placeholders of the backup Repairs item, or None).

        While the E32 is silent nothing new is known: what held before still holds (so a short outage never
        ends an episode and sends it again afterwards), and the E32's silence itself is added.
        """
        silent = {f"{PROBLEM_KINDS[key]}:": {"problem": (key, values)} for key, values in problems
                  if key == "e32_offline"}
        silent.update(self._house(house or {}, now))
        self.fresh = hub.fresh
        if not hub.fresh:
            return {**{k: v for k, v in self.last.items() if k.split(":", 1)[0] not in ("update", "update_ha",
                                                                                       "backup")}, **silent}
        found = dict(silent)
        for key, values in problems:
            kind = PROBLEM_KINDS.get(key)
            if kind is None or kind == "e32_offline":
                continue
            room_id = values.get("room_id", "") if kind == "sensor" else ""
            found[f"{kind}:{room_id}"] = {"problem": (key, values), **({"room_id": room_id} if room_id else {})}
        found.update(self._rooms(hub, now))
        if self._held("frost:", frost_protection(hub), now, FROST_SECONDS):
            found["frost:"] = {}
        if self._held("boiler_fault:", fault is not None, now, FAULT_SECONDS):
            found["boiler_fault:"] = dict(fault)
        from .heating_plan import plan_ready
        if plan_ready(hub):  # once per readiness: the episode ends when the E32 plans, or checks again
            found["plan_ready:"] = {"plan_room": (hub.heating_plan or {}).get("room") or ""}
        return found

    def _house(self, house, now):
        """The maintenance causes Home Assistant itself knows (they hold also while the E32 is silent)."""
        found = {}
        code = house.get("maintenance")
        for key in [k for k in self.since if k.startswith("maintenance:") and k != f"maintenance:{code}"]:
            del self.since[key]  # another code (or none): its hold starts again
        if type(code) is str and code and self._held(f"maintenance:{code}", True, now, MAINTENANCE_SECONDS):
            found["maintenance:"] = {"code": code, "episode": code}
        for key, version in (house.get("updates") or {}).items():
            if type(version) is str and version and self.announced.get(key) != version:
                found[key] = {"version": version, "episode": version}
        if type(house.get("backup")) is dict:
            found["backup:"] = dict(house["backup"])
        return found

    def _held(self, key, on, now, seconds):
        if not on:
            self.since.pop(key, None)
            return False
        return now - self.since.setdefault(key, now) >= seconds

    def _rooms(self, hub, now):
        from .heating_problem import ROOM_MEASURED
        found, cold = {}, {}
        for room_id, room in hub.rooms.items():
            comfort = room.get("comfort") if type(room.get("comfort")) is dict else {}
            window = comfort.get("window")
            temperature, target = _number(room.get("temperature")), _number(room.get("setpoint"))
            if window != "open" and target is not None:
                self.before[room_id] = target
            key = f"window:{room_id}"
            if room.get("state") == "active" and window == "open":
                before = self.before.get(room_id)
                # Only while the room heats: colder than its target before the pause (unknown: yes).
                if key in self.last or temperature is None or before is None or temperature < before:
                    found[key] = {"room_id": room_id, "opening": "door" if comfort.get("opening") == "door"
                                  else "window"}
            if (room.get("status") in ROOM_MEASURED and room.get("demand") is True and window not in ("open", "pending")
                    and temperature is not None and target is not None and temperature < target - COLD_MARGIN_C):
                previous = self.cold.get(room_id)
                since = now if previous is None or target > previous[0] else previous[1]
                cold[room_id] = (target, since)
                if now - since >= COLD_SECONDS:
                    found[f"cold:{room_id}"] = {"room_id": room_id, "temperature": temperature, "target": target}
            self._battery(hub, room_id)
            if self._held(f"battery:{room_id}", room_id in self.low, now, BATTERY_SECONDS):
                battery, device = self.battery.get(room_id, (None, "thermometer"))
                found[f"battery:{room_id}"] = {"room_id": room_id, "battery": battery, "device": device}
        self.cold = cold
        return found

    def _battery(self, hub, room_id):
        """Follows the lowest battery of the room's Bluetooth sensors and radiator valves that report one (%),
        and whether it is low."""
        values = [(b, "thermometer") for b in (_number((hub.ble.get(s) or {}).get("battery"), 0, 100)
                                               for s in room_ble_sensors(hub, room_id)) if b is not None]
        values += [(b, "valve") for b in (_number(v, 0, 100) for v in room_valve_batteries(hub, room_id))
                   if b is not None]
        if not values:
            return  # nothing reported (a sensor without a battery value, or silent): as it was
        self.battery[room_id] = min(values, key=lambda item: item[0])
        battery = self.battery[room_id][0]
        if battery < BATTERY_LOW_PCT or (room_id in self.low and battery < BATTERY_OK_PCT):
            self.low.add(room_id)
        else:
            self.low.discard(room_id)

    def due(self, found, settings, wall, local):
        """([(key, values)] to send now, [keys] whose cause is gone).

        A cause that is gone ends its episode; the E32's silence ending is the "E32 back" message. A cause
        whose message is switched off, falls in the quiet hours (rooms) or was sent less than
        COOLDOWN_SECONDS ago waits: it goes out later if it still holds then. While the E32 is silent only
        its silence goes out: the rest is what held before, not news.
        """
        messages, ended = [], sorted(self.open - set(found))
        for key in ended:
            self.open.discard(key)
            if key == "e32_offline:" and enabled(settings, "e32_back", ""):
                messages.append(("e32_back:", {}))
        for key, values in sorted(found.items()):
            kind, room_id = key.split(":", 1)
            if key in self.open and values.get("episode") not in (None, self.episodes.get(key)):
                self.open.discard(key)  # another maintenance code or version: a new message
                self.sent.pop(key, None)
            if key in self.open or not enabled(settings, kind, room_id) or (room_id and quiet(local)):
                continue
            if not self.fresh and kind not in ("e32_offline", *HOUSE_MAINTENANCE, "update_ha"):
                continue
            last = self.sent.get(key)
            if last is not None and 0 <= wall - last < COOLDOWN_SECONDS:
                continue
            messages.append((key, values))
        self.last = found
        self.sent = {key: at for key, at in self.sent.items() if 0 <= wall - at < COOLDOWN_SECONDS or key in self.open}
        return messages, ended

    def done(self, key, wall, values=None):
        """The message of ``key`` went out: once per episode, and its cooldown starts."""
        self.sent[key] = wall
        if key != "e32_back:":
            self.open.add(key)
        episode = (values or {}).get("episode")
        if episode is not None:
            self.episodes[key] = episode
            if key.split(":", 1)[0] in ("update", "update_ha"):
                self.announced[key] = episode

    def reset(self):
        """Nothing is switched on: forget the episodes (the cooldowns and the announced versions stay)."""
        self.open.clear()
        self.episodes.clear()
        self.last = {}


# -- the texts ------------------------------------------------------------------------------------------------------


def _figure(value, lang):
    from .heating_advice import fmt
    return fmt(round(float(value), 1), lang) if type(value) in (int, float) else "?"


def message(key, values, lang, names):
    """(title, sentence) of one message in a language; ``names``: {room id: name} as the dashboard shows it."""
    from .heating_problem import SHORT, render
    kind, room_id = key.split(":", 1)
    lang = lang if lang in TEXT else "en"
    room = names.get(room_id) or room_id
    if kind == "plan_ready":  # a house message about the plan's room
        from .heating_plan import TEXT as PLAN_TEXT
        plan_room = values.get("plan_room") or ""
        room = names.get(plan_room) or plan_room or PLAN_TEXT[lang]["your_home"]
    problem = values.get("problem")
    if problem is not None:
        problem_key, problem_values = problem
        problem_values = {**problem_values, **({"room": room} if room_id else {})}
        body = render([(problem_key, problem_values)], lang)[0]
        title = TITLE[lang].get(kind) or SHORT[lang][problem_key]
        return title.format(room=room), body
    if kind == "window":
        kind = values.get("opening", "window")
    fields = {"room": room, "temperature": _figure(values.get("temperature"), lang),
              "target": _figure(values.get("target"), lang), "battery": _figure(values.get("battery"), lang),
              "code": values.get("code", ""), "meaning": (values.get("meaning") or "").strip(),
              "version": values.get("version", ""), "last": values.get("last") or "?"}
    text = "battery_valve" if kind == "battery" and values.get("device") == "valve" else kind
    body = TEXT[lang][text].format(**fields)
    if kind == "boiler_fault":
        body = body if body.endswith((".", "!", "?")) else body.rstrip(":").rstrip() + "."
        if (advice := (values.get("advice") or "").strip()):
            body += " " + advice
    return TITLE[lang][kind].format(**fields), body


# -- the notifier -------------------------------------------------------------------------------------------------


def notification_id(entry_id, key):
    kind, room_id = key.split(":", 1)
    return f"{DOMAIN}_notification_{kind}{'_' + room_id if room_id else ''}_{entry_id}"


class Notifier:
    """Follows the hub and sends the messages that are due (on every E32 message and every minute)."""

    def __init__(self, hass, entry, hub, store=None, stored=None, wall=None, local=None):
        from .heating_problem import ProblemTracker
        from .room_plan import has_room_plan
        from homeassistant.util import dt as dt_util
        self.hass, self.entry, self.hub, self.store = hass, entry, hub, store
        self.wall = wall or (lambda: dt_util.utcnow().timestamp())
        self.local = local or dt_util.now
        self.tracker = ProblemTracker(hub.clock(), expect_telemetry=has_room_plan(entry))
        stored = stored if type(stored) is dict else {}
        sent = stored.get("sent") if type(stored.get("sent")) is dict else {}
        opened = stored.get("open") if type(stored.get("open")) is list else []

        def texts(name):
            value = stored.get(name)
            return {k: v for k, v in value.items() if type(k) is str and type(v) is str} if type(value) is dict else {}
        self.rules = NotificationRules({k: v for k, v in sent.items() if type(k) is str and type(v) in (int, float)},
                                       [k for k in opened if type(k) is str and ":" in k],
                                       texts("episodes"), texts("announced"))
        self._saved = self._snapshot()

    def _snapshot(self):
        return {"sent": dict(self.rules.sent), "open": sorted(self.rules.open),
                "episodes": dict(self.rules.episodes), "announced": dict(self.rules.announced)}

    def _advice_items(self):
        advice = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id, {}).get("heating_advice")
        return getattr(advice, "items", ()) or ()

    def _fault(self):
        from homeassistant.helpers import entity_registry as er
        entity_id = er.async_get(self.hass).async_get_entity_id(
            "sensor", DOMAIN, f"{self.hub.prefix}_boiler_fields_v1_display_code")
        return boiler_fault(self.hass.states.get(entity_id)) if entity_id else None

    def _house(self):
        """What Home Assistant knows of the house's maintenance (NotificationRules.found ``house``)."""
        return {"maintenance": self._maintenance(), "updates": self._updates(), "backup": self._backup()}

    def _maintenance(self):
        from homeassistant.helpers import entity_registry as er
        entity_id = er.async_get(self.hass).async_get_entity_id(
            "sensor", DOMAIN, f"{self.hub.prefix}_boiler_fields_v1_maintenance_message")
        return maintenance_code(self.hass.states.get(entity_id)) if entity_id else None

    def _updates(self):
        from homeassistant.helpers import entity_registry as er
        registry = er.async_get(self.hass)
        found = {}
        firmware = registry.async_get_entity_id("update", DOMAIN, f"{self.hub.prefix}_e32_firmware")
        if (version := new_version(self.hass.states.get(firmware) if firmware else None)) is not None:
            found["update:"] = version
        for state in self.hass.states.async_all("update"):
            record = registry.async_get(state.entity_id)
            if record is not None and record.platform != DOMAIN and integration_update(state):
                if (version := new_version(state)) is not None:
                    found["update_ha:"] = version
                    break
        return found

    def _backup(self):
        from homeassistant.helpers import issue_registry as ir
        from .e32_backup import ISSUE
        issue = ir.async_get(self.hass).async_get_issue(DOMAIN, f"{ISSUE}_{self.entry.entry_id}")
        if issue is None:
            return None
        return {"last": (issue.translation_placeholders or {}).get("last") or "?"}

    def _home(self, person):
        from .e32_comfort import presence_home
        return presence_home(self.hass.states.get(person)) is True

    @callback
    def evaluate(self, _now=None):
        settings = notification_options(self.entry)
        if not anything_on(settings):
            self.rules.reset()
            self._save()
            return
        from .heating_advice import language
        from .insight import room_names
        now = self.hub.clock()
        self.tracker.observe(self.hub, now)
        names = room_names(self.hub, self.hass, self.entry.entry_id)
        problems = self.tracker.problems(self.hub, now, self._advice_items(), None, names)
        found = self.rules.found(self.hub, problems, self._fault(), now, self._house())
        wall = self.wall()
        messages, ended = self.rules.due(found, settings, wall, self.local())
        lang = language(self.hass)
        for key in ended:
            from homeassistant.components import persistent_notification
            persistent_notification.async_dismiss(self.hass, notification_id(self.entry.entry_id, key))
        for key, values in messages:
            kind, room_id = key.split(":", 1)
            chosen = recipients(kind, room_id, room_people(self.entry, room_id) if room_id else settings["house_people"],
                                settings["phones"], self._home)
            if chosen is None:
                continue  # nobody of this room is home: it waits
            people, services, persistent = chosen
            title, text = message(key, values, lang, names)
            self.rules.done(key, wall, values)
            self._send(key, names.get(room_id) or room_id, title, text, people, services, persistent)
        self._save()

    @callback
    def _send(self, key, room, title, text, people, services, persistent):
        kind, room_id = key.split(":", 1)
        self.hass.bus.async_fire(EVENT, {
            "entry_id": self.entry.entry_id, "kind": kind, "room_id": room_id or None, "room": room or None,
            "title": title, "message": text, "people": list(people)})
        if key == "e32_back:":
            from homeassistant.components import persistent_notification
            persistent_notification.async_dismiss(self.hass, notification_id(self.entry.entry_id, "e32_offline:"))
            persistent = False
        self.hass.async_create_task(self._deliver(key, title, text, services, persistent),
                                    f"{DOMAIN} notification {kind}")

    async def _deliver(self, key, title, text, services, persistent):
        for service in services:
            try:
                await self.hass.services.async_call("notify", service, {"title": title, "message": text},
                                                    blocking=True)
            except Exception as err:  # noqa: BLE001 - a phone that is gone never stops the others
                _LOGGER.warning("OpenThermostat: the notification to notify.%s failed: %s", service, err)
                persistent = True
        if persistent:
            from homeassistant.components import persistent_notification
            persistent_notification.async_create(self.hass, text, title=PERSISTENT_TITLE.format(title=title),
                                                 notification_id=notification_id(self.entry.entry_id, key))

    @callback
    def _save(self):
        snapshot = self._snapshot()
        if snapshot != self._saved and self.store is not None:
            self._saved = snapshot
            self.store.async_delay_save(lambda: snapshot, 1)


def _store(hass, entry_id):
    from homeassistant.helpers.storage import Store
    return Store(hass, STORE_VERSION, f"{DOMAIN}.notifications_{entry_id}")


async def async_setup_notifications(hass, entry, hub):
    """Product entries: the notifier, which reads its settings (Configure → Notifications) on every check."""
    from homeassistant.helpers.event import async_track_time_interval
    store = _store(hass, entry.entry_id)
    notifier = Notifier(hass, entry, hub, store, await store.async_load())
    hass.data[DOMAIN][entry.entry_id]["notifier"] = notifier
    entry.async_on_unload(hub.add_listener(notifier.evaluate))
    entry.async_on_unload(async_track_time_interval(hass, notifier.evaluate, CHECK_INTERVAL))
    notifier.evaluate()
    return notifier


async def async_remove_notifications(hass, entry_id):
    """A removed installation: what its messages kept (the cooldowns, the open episodes) is forgotten."""
    await _store(hass, entry_id).async_remove()


# -- the phones (Configure → Notifications → People and phones) ---------------------------------------------------


PHONE_APP = {"en": "{name} (Home Assistant app)", "nl": "{name} (Home Assistant-app)",
             "pl": "{name} (aplikacja Home Assistant)"}


def phone_services(hass):
    """{service: label} of the notify services that reach one phone or app, the app's devices by their name."""
    from homeassistant.util import slugify
    from .heating_advice import language
    apps = {}
    for app in hass.config_entries.async_entries("mobile_app"):
        name = app.data.get("device_name")
        if type(name) is str and name:
            apps[f"mobile_app_{slugify(name)}"] = name
    words = PHONE_APP[language(hass)]
    return {service: words.format(name=apps[service]) if service in apps else f"notify.{service}"
            for service in sorted(hass.services.async_services_for_domain("notify")) if service not in NOT_A_PHONE}


def suggested_phone(hass, person, services):
    """The app on the person's own phone (a mobile app device tracker of that person), or None."""
    from homeassistant.helpers import device_registry as dr
    from homeassistant.helpers import entity_registry as er
    from homeassistant.util import slugify
    state = hass.states.get(person)
    trackers = state.attributes.get("device_trackers") if state is not None else None
    for tracker in trackers if type(trackers) is list else []:
        item = er.async_get(hass).async_get(tracker) if type(tracker) is str else None
        device = dr.async_get(hass).async_get(item.device_id) if item is not None and item.device_id else None
        if item is None or item.platform != "mobile_app" or device is None:
            continue
        # The app names its notify service after the phone's own name (not a name given in Home Assistant).
        service = f"mobile_app_{slugify(device.name or '')}"
        if service in services:
            return service
    return None
