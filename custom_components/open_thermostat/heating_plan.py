"""The E32's heating plan in Home Assistant (1.1.1 stage B: SL-B3's planner, the owner's decision D5).

The E32 plans the heating itself; Home Assistant only shows the plan and carries the owner's one confirmation.

What the E32 sends, ``fw/telemetry/plan`` (retained, on change at most once a minute, at most 660 B;
heating_link.HEATING_PLAN_TOPIC; the same object is "heat_plan" in /status/heating), as SL-B3 built it
(HeatPlanner::addJson, its report section 2)::

    {"schema":1,"state":"checking","applied":false,"why":"checking","days":[3,7],"mornings":[2,5],"made":1794099600,
     "blocks":[[90,245,52,"warmup"]],"confidence":"good","err_3h":0.18,
     "reason":{"key":"warmup","room":"woonkamer","start":1794105000,"flow":52,"target":20.5,"time":1794128400,
               "arrival":1794127800,"alt_flow":37,"alt_start":1794094200,"alt_starts":70},
     "last":{"room":"woonkamer","rise":1794042000,"plan":-165,"e32":-175,"arrived":-9,"predicted":-20,
             "week_min":[-27,-1,4,-9]},
     "guards":0,"learn":"refused"}

``state``: collecting / checking (the plan in shadow) / ready (ready for your confirmation) / planning / demoted; the
plan mode is "planning" exactly when the state is (no mode key on MQTT). ``why`` only while not applied: checking,
memory, clock, model, plant, outdoor, stale, guard. ``days`` and ``mornings``: [have, need]. ``blocks``: at most three
not over yet, [start, end] in minutes from ``made``, the water temperature and the purpose (warmup / hold / preheat /
learn). ``confidence`` (high / good / fair) and ``err_3h`` only with a planned room. ``reason``: the explainer's key
(warmup / preheat / learn / hold / coast / none) and its figures, the predicted arrival in ``arrival``. ``last``: the
last judged morning, ``rise`` in unix seconds, the rest minutes from the rise (signed; absent when unknown);
``week_min`` (E32 1.3, the morning check) that room's last judged mornings (at most 7, oldest first) in minutes from
their rise, 180 for a room not warm within 3 hours. Every field is optional; what is not known is left out, never
shown as a raw code.

The sentences are the E32 House page's (house.html stateText / whyText / reasonText and its last morning line), in
English and in its Dutch (ui-messages-house.js), so the page and Home Assistant say the same; Polish is this
module's. While the E32 does not plan, the reason reads "If the E32 planned the heating: ...", as on the page.

What Home Assistant adds, all on the E32 device:

- the sensor "Heating plan": state = the next planned start; attributes: the planner's state and its plain line,
  the next blocks (and one line each), the expected arrival, the confidence, the reason sentence, the last morning
  and the morning check ("This morning: 6 minutes early.", with the last seven mornings in minutes);
- when the E32 reports ``ready``: a Repairs item (an invitation, not a fault) whose one step confirms, and the
  button "Let the E32 plan the heating", which exists only in that state. Both POST ``/config/heating/plan``
  {"mode": "planning"} (controller_link.async_plan_mode, over the stored connection; the E32 answers 409
  plan_not_ready unless it is ready). The E32 never plans by itself; after a demotion it reports ``checking``
  again and the invitation returns once it is ready;
- the notification "The E32 is ready to plan" (notifications.py, the Maintenance group), once per readiness.

No stale entities: the plan sensor is removed when the E32 has been online for PLAN_GRACE_S in this Home
Assistant run without a plan (firmware without the planner, a downgrade), the button whenever the E32 reports
another state.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone

from homeassistant.components.button import ButtonEntity
from homeassistant.components.repairs import RepairsFlow
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er, issue_registry as ir

from .const import DOMAIN
from .heating_link import HubEntity, decode_document

_LOGGER = logging.getLogger(__name__)

MAX_PLAN_BYTES = 1024
MAX_BLOCKS = 3
PLAN_STATES = ("collecting", "checking", "ready", "planning", "demoted")
WHY = ("checking", "memory", "clock", "model", "plant", "outdoor", "stale", "guard")
PURPOSES = ("warmup", "hold", "preheat", "learn")
REASON_KEYS = ("warmup", "preheat", "learn", "hold", "coast")  # "none": nothing planned, no sentence
CONFIDENCES = ("fair", "good", "high")
PLAN_MODES = ("checking", "planning")  # POST /config/heating/plan {"mode"} (SL-B3 item 3)
PLAN_READY_ISSUE = "plan_ready"
PLAN_GRACE_S = 15 * 60  # online this long without a plan: the firmware has no planner (the sensor goes)
CONFIRM_HOLD_S = 10 * 60  # after a confirmation the invitation waits this long for the E32's new state
UTC_LIMITS = (1e9, 4.2e9)
MINUTE_LIMITS = (-1440 * 3, 1440 * 3)

TEXT = {
    "en": {
        # house.html stateText and whyText
        "state.collecting": "The E32 plans the heating itself once it trusts the model of {room} and knows your "
                            "boiler. Until then it heats as it does now.",
        "state.checking": "The E32 is checking its plans against what really happens: {d} of {dd} days, {m} of {mm} "
                          "mornings predicted within 20 minutes. Nothing changes in the heating yet.",
        "state.ready": "The E32's predictions have been good for a week. It can plan the heating now: warm on time, "
                       "with fewer burner starts. You decide.",
        "state.planning": "The E32 plans the heating.",
        "state.demoted": "The plan was not good enough on some days, so the E32 heats as before and checks its plans "
                         "again for a week ({d} of {dd} days). It will ask you again.",
        "state.paused": "The E32 plans the heating, but right now it heats as before: {why}.",
        "why.model": "it is checking its model of the room again", "why.plant": "it is checking the boiler again",
        "why.outdoor": "there is no outdoor temperature", "why.stale": "it has no fresh plan",
        "why.clock": "it has no fresh plan", "why.memory": "it has no fresh plan",
        "why.guard": "a room was colder than planned",
        # house.html reasonText
        "reason.warmup": "Starts at {start} with {flow} °C water so {room} is {target} °C at {time}.",
        "reason.alt": "With {alt_flow} °C water it would have needed to start at about {alt_start} and the boiler "
                      "would have started about {alt_starts} times.",
        "reason.learn": "Tries {flow} °C water this time to learn how fast {room} warms; it starts at {start}, so "
                        "{room} is still {target} °C at {time}.",
        "reason.preheat": "Starts at {start} with {flow} °C water so {room} is {target} °C when you are back at "
                          "{time}.",
        "reason.hold": "Keeps {room} gently warm with {flow} °C water so it is {target} °C at {time}: cheaper than "
                       "letting it cool and warming it again.",
        "reason.coast": "{room} stays warm enough: no warm-up is needed before {time}.",
        "if_planned": "If the E32 planned the heating: {plan}",
        "last_plan": "Last time the plan would have started at {plan}; the E32 started at {e32}.",
        "last_e32": "Last time the E32 started at {e32}.",
        "last_warm": "{room} was warm at {arrived}.", "last_cold": "{room} was not warm within 3 hours.",
        # Home Assistant's own lines
        # The morning check (E32 1.3, "last.arrived" and "week_min"): when the room was warm, in minutes from the rise.
        "morning_today": "This morning: {how}.", "morning_yesterday": "Yesterday morning: {how}.",
        "morning_date": "On {date}: {how}.",
        "morning_early": "{n} early", "morning_late": "{n} late", "morning_on_time": "on time",
        "morning_cold": "not warm within 3 hours",
        "block": "{from}–{until}: {flow} °C water", "tomorrow": "tomorrow {time}",
        "purpose.warmup": "warm-up", "purpose.hold": "keep warm", "purpose.preheat": "warm up for your return",
        "purpose.learn": "learning",
        "arrival": "{room} is expected to be warm at {time}.",
        "confidence": "Confidence: {word}.",
        "confidence.fair": "fair", "confidence.good": "good", "confidence.high": "high",
        "your_home": "your home",
    },
    "nl": {
        "state.collecting": "De E32 plant de verwarming zelf zodra hij het model van {room} vertrouwt en je ketel "
                            "kent. Tot dan verwarmt hij zoals nu.",
        "state.checking": "De E32 controleert zijn plannen tegen wat er echt gebeurt: {d} van {dd} dagen, {m} van "
                          "{mm} ochtenden binnen 20 minuten voorspeld. Er verandert nog niets aan de verwarming.",
        "state.ready": "De voorspellingen van de E32 zijn al een week goed. Hij kan de verwarming nu plannen: op tijd "
                       "warm, met minder branderstarts. Jij beslist.",
        "state.planning": "De E32 plant de verwarming.",
        "state.demoted": "Het plan was op een paar dagen niet goed genoeg, dus de E32 verwarmt weer zoals eerst en "
                         "controleert zijn plannen opnieuw een week ({d} van {dd} dagen). Daarna vraagt hij het je "
                         "opnieuw.",
        "state.paused": "De E32 plant de verwarming, maar verwarmt nu even zoals eerst: {why}.",
        "why.model": "hij controleert het model van de ruimte opnieuw", "why.plant": "hij controleert de ketel opnieuw",
        "why.outdoor": "er is geen buitentemperatuur", "why.stale": "hij heeft geen vers plan",
        "why.clock": "hij heeft geen vers plan", "why.memory": "hij heeft geen vers plan",
        "why.guard": "een ruimte was kouder dan gepland",
        "reason.warmup": "Begint om {start} met water van {flow} °C, zodat {room} om {time} {target} °C is.",
        "reason.alt": "Met water van {alt_flow} °C had hij rond {alt_start} moeten beginnen en was de ketel ongeveer "
                      "{alt_starts} keer gestart.",
        "reason.learn": "Probeert deze keer water van {flow} °C om te leren hoe snel {room} opwarmt; hij begint om "
                        "{start}, dus {room} is toch om {time} {target} °C.",
        "reason.preheat": "Begint om {start} met water van {flow} °C, zodat {room} {target} °C is als je om {time} "
                          "terug bent.",
        "reason.hold": "Houdt {room} rustig warm met water van {flow} °C, zodat het om {time} {target} °C is: "
                       "goedkoper dan laten afkoelen en weer opwarmen.",
        "reason.coast": "{room} blijft warm genoeg: voor {time} hoeft er niet opgewarmd te worden.",
        "if_planned": "Als de E32 de verwarming plande: {plan}",
        "last_plan": "Vorige keer zou het plan om {plan} zijn begonnen; de E32 begon om {e32}.",
        "last_e32": "Vorige keer begon de E32 om {e32}.",
        "last_warm": "{room} was om {arrived} warm.", "last_cold": "{room} was niet binnen 3 uur warm.",
        "morning_today": "Vanochtend: {how}.", "morning_yesterday": "Gisterochtend: {how}.",
        "morning_date": "Op {date}: {how}.",
        "morning_early": "{n} te vroeg warm", "morning_late": "{n} te laat warm", "morning_on_time": "op tijd warm",
        "morning_cold": "niet binnen 3 uur warm",
        "block": "{from}–{until}: water van {flow} °C", "tomorrow": "morgen {time}",
        "purpose.warmup": "opwarmen", "purpose.hold": "warm houden", "purpose.preheat": "opwarmen voor je terugkomst",
        "purpose.learn": "leren",
        "arrival": "{room} is naar verwachting om {time} warm.",
        "confidence": "Zekerheid: {word}.",
        "confidence.fair": "redelijk", "confidence.good": "goed", "confidence.high": "hoog",
        "your_home": "je huis",
    },
    "pl": {
        "state.collecting": "E32 sam zaplanuje ogrzewanie, gdy zaufa modelowi pomieszczenia {room} i pozna Twój "
                            "kocioł. Do tego czasu grzeje jak teraz.",
        "state.checking": "E32 porównuje swoje plany z tym, co dzieje się naprawdę: {d} z {dd} dni, {m} z {mm} "
                          "poranków przewidzianych z dokładnością do 20 minut. W ogrzewaniu jeszcze nic się nie "
                          "zmienia.",
        "state.ready": "Prognozy E32 są dobre od tygodnia. Może teraz planować ogrzewanie: ciepło na czas, przy "
                       "mniejszej liczbie uruchomień palnika. Ty decydujesz.",
        "state.planning": "E32 planuje ogrzewanie.",
        "state.demoted": "W niektóre dni plan nie był wystarczająco dobry, więc E32 grzeje jak wcześniej i przez "
                         "tydzień ponownie sprawdza swoje plany ({d} z {dd} dni). Potem zapyta Cię ponownie.",
        "state.paused": "E32 planuje ogrzewanie, ale teraz chwilowo grzeje jak wcześniej: {why}.",
        "why.model": "ponownie sprawdza model pomieszczenia", "why.plant": "ponownie sprawdza kocioł",
        "why.outdoor": "brak temperatury zewnętrznej", "why.stale": "nie ma aktualnego planu",
        "why.clock": "nie ma aktualnego planu", "why.memory": "nie ma aktualnego planu",
        "why.guard": "w pomieszczeniu było zimniej, niż planowano",
        "reason.warmup": "Zaczyna o {start} z wodą {flow} °C, aby w pomieszczeniu {room} było {target} °C o {time}.",
        "reason.alt": "Z wodą {alt_flow} °C musiałby zacząć około {alt_start}, a kocioł uruchomiłby się około "
                      "{alt_starts} razy.",
        "reason.learn": "Tym razem próbuje wody {flow} °C, aby poznać, jak szybko nagrzewa się pomieszczenie {room}; "
                        "zaczyna o {start}, więc o {time} w pomieszczeniu {room} i tak będzie {target} °C.",
        "reason.preheat": "Zaczyna o {start} z wodą {flow} °C, aby w pomieszczeniu {room} było {target} °C, gdy "
                          "wrócisz o {time}.",
        "reason.hold": "Utrzymuje łagodne ciepło w pomieszczeniu {room} wodą {flow} °C, aby o {time} było {target} °C: "
                       "taniej niż pozwolić mu wystygnąć i znów je nagrzać.",
        "reason.coast": "W pomieszczeniu {room} pozostanie wystarczająco ciepło: przed {time} nie trzeba nagrzewać.",
        "if_planned": "Gdyby E32 planował ogrzewanie: {plan}",
        "last_plan": "Ostatnio plan zacząłby o {plan}; E32 zaczął o {e32}.",
        "last_e32": "Ostatnio E32 zaczął o {e32}.",
        "last_warm": "Pomieszczenie {room} było ciepłe o {arrived}.",
        "last_cold": "Pomieszczenie {room} nie nagrzało się w ciągu 3 godzin.",
        "morning_today": "Dziś rano: {how}.", "morning_yesterday": "Wczoraj rano: {how}.",
        "morning_date": "Dnia {date}: {how}.",
        "morning_early": "ciepło {n} za wcześnie", "morning_late": "ciepło {n} za późno",
        "morning_on_time": "ciepło na czas", "morning_cold": "nie nagrzało się w ciągu 3 godzin",
        "block": "{from}–{until}: woda {flow} °C", "tomorrow": "jutro {time}",
        "purpose.warmup": "nagrzewanie", "purpose.hold": "utrzymanie ciepła", "purpose.preheat": "nagrzewanie na powrót",
        "purpose.learn": "nauka",
        "arrival": "Pomieszczenie {room} powinno być ciepłe o {time}.",
        "confidence": "Pewność: {word}.",
        "confidence.fair": "umiarkowana", "confidence.good": "dobra", "confidence.high": "wysoka",
        "your_home": "Twój dom",
    },
}


# -- what the E32 sends ---------------------------------------------------------------------------------------------


def _number(value, low, high):
    if type(value) is bool or not isinstance(value, (int, float)) or value != value or not low <= value <= high:
        return None
    return int(value) if value == int(value) else value


def _utc(value):
    return _number(value, *UTC_LIMITS)


def _room(value):
    from .heating_link import ROOM_ID
    return value if type(value) is str and ROOM_ID.fullmatch(value) else None


def _pair(value):
    """[have, need] as (have, need), or None."""
    if type(value) is not list or len(value) != 2:
        return None
    have, need = _number(value[0], 0, 365), _number(value[1], 1, 365)
    return (have, need) if have is not None and need is not None else None


def _block(item, made):
    """[start_min, end_min, flow_c, purpose] (minutes from ``made``) -> {"start", "end", "flow_c", "purpose"}."""
    if made is None or type(item) is not list or len(item) != 4:
        return None
    start, end = _number(item[0], 0, 2 * 1440), _number(item[1], 0, 2 * 1440)
    if start is None or end is None or end <= start:
        return None
    return {"start": made + int(start) * 60, "end": made + int(end) * 60, "flow_c": _number(item[2], 10, 90),
            "purpose": item[3] if item[3] in PURPOSES else None}


def _reason(value):
    if type(value) is not dict or value.get("key") not in REASON_KEYS:
        return None
    reason = {"key": value["key"], "room": _room(value.get("room"))}
    for key in ("start", "time", "arrival", "alt_start"):
        reason[key] = _utc(value.get(key))
    for key, low, high in (("flow", 10, 90), ("alt_flow", 10, 90), ("target", 5, 30), ("alt_starts", 0, 9999)):
        reason[key] = _number(value.get(key), low, high)
    return reason


WEEK_MORNINGS = 7  # HeatPlanner::weekMornings


def _week(value):
    """``last.week_min`` (E32 1.3): the room's last judged mornings in whole minutes from the rise, oldest first, or
    None (older firmware, or anything else than a list of at most WEEK_MORNINGS such numbers)."""
    if type(value) is not list or not 0 < len(value) <= WEEK_MORNINGS:
        return None
    week = [_number(x, *MINUTE_LIMITS) for x in value]
    return [int(x) for x in week] if all(x is not None and x == int(x) for x in week) else None


def _last(value):
    if type(value) is not dict or _utc(value.get("rise")) is None:
        return None
    return {"room": _room(value.get("room")), "rise": _utc(value["rise"]),
            **{key: _number(value.get(key), *MINUTE_LIMITS) for key in ("plan", "e32", "arrived", "predicted")},
            "week": _week(value.get("week_min"))}


def decode_heating_plan(payload):
    """``fw/telemetry/plan`` (schema 1), checked, or None without a known state.

    {"state", "applied", "why", "days": (have, need) or None, "mornings": (have, need) or None, "made", "blocks":
    [{"start", "end" (unix s), "flow_c", "purpose"}] (at most MAX_BLOCKS, in time order), "confidence",
    "error_3h_c", "reason": {...} or None, "last": {...} or None, "guards", "learn_refused", "room" (the plan's
    room: the reason's, else the last morning's)}. A value of the wrong type is left out.
    """
    value = decode_document(payload, MAX_PLAN_BYTES)
    if value is None or value.get("state") not in PLAN_STATES:
        return None
    made = _utc(value.get("made"))
    blocks = [b for b in (_block(item, made) for item in (value.get("blocks") if type(value.get("blocks")) is list
                                                         else [])) if b is not None]
    blocks.sort(key=lambda b: b["start"])
    reason, last = _reason(value.get("reason")), _last(value.get("last"))
    return {"state": value["state"], "applied": value.get("applied") is True,
            "why": value.get("why") if value.get("why") in WHY else None,
            "days": _pair(value.get("days")), "mornings": _pair(value.get("mornings")), "made": made,
            "blocks": blocks[:MAX_BLOCKS],
            "confidence": value.get("confidence") if value.get("confidence") in CONFIDENCES else None,
            "error_3h_c": _number(value.get("err_3h"), 0, 20), "reason": reason, "last": last,
            "guards": _number(value.get("guards"), 0, 1000), "learn_refused": value.get("learn") == "refused",
            "room": (reason or {}).get("room") or (last or {}).get("room")}


def plan_state(hub):
    """The plan's state (PLAN_STATES) while the E32 reports a plan, else None."""
    plan = getattr(hub, "heating_plan", None) if getattr(hub, "fresh", False) else None
    return plan["state"] if plan is not None else None


def plan_ready(hub):
    return plan_state(hub) == "ready"


def lead_room(hub):
    """The first room that is on (the House page's "lead" room for the state line), or None. A room on Heat along
    only (E32 1.3, "follow") is no planner input."""
    return next((room_id for room_id, room in getattr(hub, "rooms", {}).items()
                 if room.get("state") not in ("inactive", "follow")), None)


# -- in words ---------------------------------------------------------------------------------------------------


def _clock(utc, local):
    return local(utc).strftime("%H:%M")


def _when(utc, t, local, today):
    """"06:15", or "tomorrow 06:15" for a time on a later local day (the block lines)."""
    moment = local(utc)
    text = moment.strftime("%H:%M")
    return t["tomorrow"].format(time=text) if moment.date() > today else text


def state_line(plan, lang, names, lead=None):
    """The planner's state in one line, as the House page says it, or None."""
    t, state = TEXT[lang], plan.get("state")
    if state not in PLAN_STATES:
        return None
    if state == "planning" and not plan.get("applied") and plan.get("why") in WHY and f"why.{plan['why']}" in t:
        return t["state.paused"].format(why=t[f"why.{plan['why']}"])
    d, dd = plan.get("days") or (0, 0)
    m, mm = plan.get("mornings") or (0, 0)
    room = names.get(lead) or lead or t["your_home"]
    return t["state." + state].format(room=room, d=d, dd=dd or 7, m=m, mm=mm or 5)


def reason_sentence(plan, lang, names, local):
    """The explainer's sentence as the House page renders it, or None (no reason, or a figure it needs is missing).

    While the E32 does not plan: "If the E32 planned the heating: starts at ..."; nothing while it collects.
    """
    from .learned_overview import number
    reason = plan.get("reason")
    if not reason or plan.get("state") == "collecting":
        return None
    t, key = TEXT[lang], reason["key"]
    values = {"room": names.get(reason["room"]) or reason["room"] or "",
              "start": _clock(reason["start"], local) if reason["start"] is not None else None,
              "flow": str(round(reason["flow"])) if reason["flow"] is not None else None,
              "target": number(reason["target"], lang, 1) if reason["target"] is not None else None,
              "time": _clock(reason["time"], local) if reason["time"] is not None else None}
    if values["time"] is None or (key != "coast" and None in values.values()):
        return None
    text = t["reason." + key].format(**values)
    if key == "warmup" and None not in (reason["alt_flow"], reason["alt_start"], reason["alt_starts"]):
        text += " " + t["reason.alt"].format(alt_flow=round(reason["alt_flow"]),
                                            alt_start=_clock(reason["alt_start"], local),
                                            alt_starts=round(reason["alt_starts"]))
    if plan.get("state") != "planning":
        lower = text if key == "coast" else text[:1].lower() + text[1:]
        text = t["if_planned"].format(plan=lower)
    return text


def last_line(last, lang, names, local):
    """The last judged morning as the House page says it ("Last time the plan would have started at 06:15; the E32
    started at 06:05. Woonkamer was warm at 08:51."), or None while the E32's own start is not known."""
    if not last or last.get("e32") is None:
        return None
    t = TEXT[lang]

    def at(minutes):
        return _clock(last["rise"] + minutes * 60, local) if minutes is not None else None
    values = {"room": names.get(last["room"]) or last["room"] or "", "plan": at(last.get("plan")),
              "e32": at(last["e32"]), "arrived": at(last.get("arrived"))}
    start = t["last_plan" if values["plan"] else "last_e32"].format(**values)
    return start + " " + t["last_warm" if values["arrived"] else "last_cold"].format(**values)


NOT_WARM_MIN = 180  # the planner judges a room not warm within 3 hours at its rise + 3 h (HeatPlanner::judge)


def morning_line(last, lang, local, today):
    """The morning check in one line ("This morning: 6 minutes early."), from the last judged morning: when the room
    was warm, in minutes from its program time; None while no warm-up was judged. The day is the rise's local day:
    today, yesterday, or its date."""
    from .insight import minutes
    from .learned_overview import TEXT as LEARNED_TEXT, whole_minutes
    if not last or last.get("e32") is None:
        return None
    t = TEXT[lang]
    arrived = last.get("arrived")
    if arrived is None or arrived >= NOT_WARM_MIN:
        how = t["morning_cold"]
    else:
        n = abs(int(round(arrived)))
        words = minutes(n, lang) if n < 60 else whole_minutes(n, lang)
        how = t["morning_on_time"] if n == 0 else t["morning_late" if arrived > 0 else "morning_early"].format(n=words)
    day = local(last["rise"]).date()
    if day == today:
        return t["morning_today"].format(how=how)
    if day == today - timedelta(days=1):
        return t["morning_yesterday"].format(how=how)
    months = LEARNED_TEXT[lang]["months"].split()
    return t["morning_date"].format(date=f"{day.day} {months[day.month - 1]}", how=how)


def block_line(block, lang, local, today):
    from .learned_overview import number
    t = TEXT[lang]
    values = {"from": _when(block["start"], t, local, today), "until": _when(block["end"], t, local, today),
              "flow": number(block["flow_c"], lang, 0) if block.get("flow_c") is not None else None}
    if values["flow"] is None:
        return None
    text = t["block"].format(**values)
    word = t.get(f"purpose.{block.get('purpose')}")
    return f"{text} ({word})" if word else text


def next_start(plan, now):
    """The next planned start (unix seconds) after ``now``, or None."""
    starts = [b["start"] for b in (plan or {}).get("blocks") or [] if b["start"] > now]
    return min(starts) if starts else None


def plan_view(plan, lang, names, local, today, now, lead=None):
    """The plan sensor's attributes in a language (local: utc -> local datetime; today: the local date)."""
    t = TEXT[lang]

    def iso(utc):
        return datetime.fromtimestamp(utc, timezone.utc).isoformat() if utc is not None else None
    blocks = [b for b in plan.get("blocks") or [] if b["end"] > now]
    reason = plan.get("reason") or {}
    room = plan.get("room")
    arrival = reason.get("arrival")
    arrival_room = names.get(reason.get("room")) or reason.get("room")
    confidence = plan.get("confidence")
    days, mornings = plan.get("days") or (None, None), plan.get("mornings") or (None, None)
    return {
        "plan_state": plan.get("state"), "plan_state_text": state_line(plan, lang, names, lead),
        "plan_mode": "planning" if plan.get("state") == "planning" else "checking", "applied": plan.get("applied"),
        "why": plan.get("why"), "room_id": room, "room": names.get(room) or room if room else None,
        "days_checked": days[0], "days_needed": days[1], "mornings_on_time": mornings[0],
        "mornings_needed": mornings[1],
        "blocks": [{"start": iso(b["start"]), "end": iso(b["end"]), "flow_c": b.get("flow_c"),
                    "purpose": b.get("purpose")} for b in blocks],
        "block_lines": [line for line in (block_line(b, lang, local, today) for b in blocks) if line],
        "arrival": iso(arrival), "arrival_room": arrival_room,
        "arrival_program_time": iso(reason.get("time")), "arrival_target_c": reason.get("target"),
        "arrival_text": t["arrival"].format(room=arrival_room, time=_when(arrival, t, local, today))
        if arrival is not None and arrival_room else None,
        "confidence": confidence, "prediction_error_3h_c": plan.get("error_3h_c"),
        "confidence_text": t["confidence"].format(word=t["confidence." + confidence]) if confidence else None,
        "reason": reason_sentence(plan, lang, names, local),
        "last_text": last_line(plan.get("last"), lang, names, local),
        "morning_text": morning_line(plan.get("last"), lang, local, today),
        "morning_minutes": ((plan.get("last") or {}).get("week") or None),
        "comfort_guards_today": plan.get("guards"),
    }


def _local():
    from homeassistant.util import dt as dt_util
    return (lambda utc: dt_util.as_local(datetime.fromtimestamp(utc, timezone.utc))), dt_util.now().date()


# -- the entities -----------------------------------------------------------------------------------------------


class HeatingPlanSensor(HubEntity, SensorEntity):
    """The E32's heating plan: state = the next planned start; the plan in words as attributes."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_translation_key = "heating_plan"
    _attr_icon = "mdi:calendar-clock"
    # The texts are shown, not kept in the history (the state and the plan's state are).
    _unrecorded_attributes = frozenset({"plan_state_text", "blocks", "block_lines", "arrival_text", "confidence_text",
                                        "reason", "room", "arrival_room", "last_text", "morning_text",
                                        "morning_minutes", "comfort_guards_today"})

    def __init__(self, hub, clock=time.time):
        self._attach(hub, "hub_heating_plan")  # unique id <prefix>_hub_heating_plan: the dashboard's heating_plan
        self._clock = clock

    @property
    def plan(self):
        return self.hub.heating_plan if self.hub.fresh else None

    @property
    def available(self):
        return self.plan is not None

    def _write_token(self):
        """Written when the plan, the next start or a room's name changes, not on every E32 message (R4-08)."""
        plan = self.plan
        return (plan is not None, repr(plan), next_start(plan, self._clock()) if plan is not None else None,
                tuple(sorted(self._names().items())), lead_room(self.hub))

    def _names(self):
        from .insight import room_names
        entry = getattr(getattr(self, "platform", None), "config_entry", None)
        return room_names(self.hub, getattr(self, "hass", None), getattr(entry, "entry_id", None))

    @property
    def native_value(self):
        start = next_start(self.plan, self._clock())
        return datetime.fromtimestamp(start, timezone.utc) if start is not None else None

    @property
    def extra_state_attributes(self):
        plan = self.plan
        if plan is None:
            return None
        from .learned_overview import language
        local, today = _local()
        return plan_view(plan, language(getattr(self, "hass", None)), self._names(), local, today, self._clock(),
                         lead_room(self.hub))


class PlanConfirmButton(HubEntity, ButtonEntity):
    """"Let the E32 plan the heating": exists only while the E32 reports that it is ready for that confirmation."""

    _attr_translation_key = "plan_confirm"
    _attr_icon = "mdi:calendar-check"

    def __init__(self, entry, hub):
        self._attach(hub, "hub_plan_confirm")
        self._entry = entry

    @property
    def available(self):
        return plan_ready(self.hub)

    async def async_press(self):
        await async_confirm_planning(self.hass, self._entry, self.hub)


async def async_confirm_planning(hass, entry, hub):
    """POST the plan mode ``planning`` to the E32 (the owner's one confirmation) over the stored connection, which
    waits for a free E32 web session; a clear HomeAssistantError when it fails."""
    from .controller_link import ControllerLinkError, HeatingPlanRejected
    link = getattr(hub, "plan", None)
    if link is None:
        raise HomeAssistantError(translation_domain=DOMAIN, translation_key="plan_confirm_unavailable")
    try:
        answer = await link.async_call(lambda client: client.async_plan_mode("planning"), write=True)
    except HeatingPlanRejected as err:
        raise HomeAssistantError(translation_domain=DOMAIN, translation_key="plan_confirm_refused",
                                 translation_placeholders={"error": err.error}) from None
    except ControllerLinkError as err:
        from .room_plan import link_error
        raise link_error(str(err)) or HomeAssistantError(
            translation_domain=DOMAIN, translation_key="plan_confirm_unavailable") from None
    mode = answer.get("mode") if type(answer) is dict else None
    if mode not in (None, "planning"):
        raise HomeAssistantError(translation_domain=DOMAIN, translation_key="plan_confirm_unconfirmed")
    hub.plan_confirmed_at = hub.clock()
    ir.async_delete_issue(hass, DOMAIN, issue_id(entry))
    return answer


# -- the invitation (Repairs) -----------------------------------------------------------------------------------


def issue_id(entry):
    return f"{PLAN_READY_ISSUE}_{entry.entry_id}"


def _room_name(hass, entry, hub):
    from .insight import room_names
    from .learned_overview import language
    plan = hub.heating_plan or {}
    names = room_names(hub, hass, entry.entry_id)
    room = plan.get("room") or lead_room(hub)
    return names.get(room) or room or TEXT[language(hass)]["your_home"]


@callback
def update_issue(hass, entry, hub):
    """The invitation while the E32 is ready for the confirmation; gone in any other state (kept while silent)."""
    if not hub.fresh:
        return
    key = issue_id(entry)
    registry = ir.async_get(hass)
    confirmed = getattr(hub, "plan_confirmed_at", None)
    held = confirmed is not None and 0 <= hub.clock() - confirmed < CONFIRM_HOLD_S
    if not plan_ready(hub) or held:
        if registry.async_get_issue(DOMAIN, key) is not None:
            ir.async_delete_issue(hass, DOMAIN, key)
        if not plan_ready(hub):
            hub.plan_confirmed_at = None
        return
    room = _room_name(hass, entry, hub)
    existing = registry.async_get_issue(DOMAIN, key)
    if existing is None or (existing.translation_placeholders or {}).get("room") != room:
        ir.async_create_issue(hass, DOMAIN, key, is_fixable=True, is_persistent=False,
                              severity=ir.IssueSeverity.WARNING, translation_key=PLAN_READY_ISSUE,
                              translation_placeholders={"room": room}, data={"entry_id": entry.entry_id})


class PlanReadyRepairFlow(RepairsFlow):
    """One step: confirm that the E32 may plan the heating from now on."""

    def __init__(self, issue, data):
        self._issue, self._data = issue, data

    async def async_step_init(self, user_input=None):
        # Home Assistant opens a repair with data={"issue_id": ...} as this step's input: never a submitted form.
        return await self.async_step_plan_ready()

    async def async_step_plan_ready(self, user_input=None):
        entry = self.hass.config_entries.async_get_entry(self._data.get("entry_id"))
        hub = self.hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("heating_hub") if entry else None
        if hub is None or hub.plan is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        room = _room_name(self.hass, entry, hub)
        if hub.fresh and not plan_ready(hub):
            ir.async_delete_issue(self.hass, DOMAIN, self._issue)
            return self.async_abort(reason="plan_confirm_done")
        if user_input is None:
            return self.async_show_form(step_id="plan_ready", description_placeholders={"room": room})
        try:
            await async_confirm_planning(self.hass, entry, hub)
        except HomeAssistantError as err:
            _LOGGER.debug("OpenThermostat: the E32 did not take the plan confirmation: %s", err)
            return self.async_show_form(step_id="plan_ready", description_placeholders={"room": room},
                                        errors={"base": "plan_confirm_failed"})
        return self.async_create_entry(data={})


# -- set-up and tidying -----------------------------------------------------------------------------------------


def _remove(hass, entry, domain, unique_id):
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(domain, DOMAIN, unique_id)
    if entity_id is not None:
        record = registry.async_get(entity_id)
        if record is not None and record.config_entry_id == entry.entry_id:
            registry.async_remove(entity_id)


@callback
def remove_stale(hass, entry, hub, fresh_since):
    """The button outside the ready state; the plan sensor once the E32 was online PLAN_GRACE_S without a plan."""
    if not hub.fresh:
        return
    if not plan_ready(hub):
        _remove(hass, entry, "button", f"{hub.prefix}_hub_plan_confirm")
    if (hub.heating_plan is None and not getattr(hub, "heating_plan_seen", False) and fresh_since is not None
            and hub.clock() - fresh_since >= PLAN_GRACE_S):
        _remove(hass, entry, "sensor", f"{hub.prefix}_hub_heating_plan")


def wanted_sensors(hub):
    if hub.heating_plan is not None:
        yield ("heating_plan",), lambda: HeatingPlanSensor(hub)


def watch(hass, entry, hub):
    """Once per entry: the invitation and the tidying follow the hub. Returns the unsubscribe."""
    fresh_since = None

    @callback
    def changed():
        nonlocal fresh_since
        if hub.fresh and fresh_since is None:
            fresh_since = hub.clock()
        elif not hub.fresh:
            fresh_since = None
        update_issue(hass, entry, hub)
        remove_stale(hass, entry, hub, fresh_since)

    remove = hub.add_listener(changed)
    changed()

    @callback
    def stop():
        remove()
    return stop


async def async_setup_buttons(hass, entry, async_add_entities):
    """Product entries: the confirmation button, only while the E32 is ready for it."""
    from .heating_link import add_options, heating_hub, track_entities
    from .product import is_product
    if not is_product(entry):
        return
    hub = heating_hub(hass, entry)

    def wanted(hub):
        if plan_ready(hub):
            yield ("plan_confirm",), lambda: PlanConfirmButton(entry, hub)
    entry.async_on_unload(track_entities(hub, async_add_entities, add_options(hass, entry), wanted))
