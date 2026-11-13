"""What the E32 has learned: everything the E32 learned and tuned, in plain language (E32 rc.2).

One sensor on the product device ("What the E32 learned"). Its state is the newest change
the self-tuning made (or what it is doing), its attributes the whole overview in the Home Assistant
language (English or Dutch), each figure with a line on what it means:

- ``rooms``: per room its learning progress and what was learned (1.1.1 stage B: first how far the E32 is with
  its model of the room, ``model``: collecting, checking its predictions "2 of 3 days good", trusted with its heat
  loss and hours per degree, or checking again after a demotion; also the room's ``model`` sentence for the
  Learning tab's progress list), how fast it warms and cools,
  the lowest water temperature that still warms it in time, Smart warm-up's start for the next
  program step, how the last morning went and what Smart warm-up changes for it (E32 rc.4), the
  night advice, and the heat it gets for free from sun, cooking and people (E32 rc.5)), from
  ``fw/telemetry/learned/<room>``;
- ``house``: the heating curve, the burner (starts and burn time yesterday) and, once learned, the
  lowest water temperature the boiler starts heating at, from the summary; that last figure is
  also the attribute ``boiler_minimum_flow_c`` (absent until learned); and (E32 SL-A, ``boiler.steady``) the
  water temperature from which the boiler burns steadily, also the attributes ``steady_burn_floor_c`` and
  ``boiler_least_output_pct`` (each absent until learned) with ``steady_burn`` (applied, cycling, and up to three
  points of its starts table: water temperature, burner stops per hour asked, hours asked);
- ``changes``: the self-tuning's changes, newest first. The E32 sends its newest four and (SL-A) every change of
  its newest evaluation (``fw/telemetry/tuning`` ``log``, with ``day_changes`` how many that evaluation made);
  this sensor keeps the last twenty over restarts;
- ``latest_changes``: the texts of the newest evaluation's changes, all of them (the dashboard's "Latest change"),
  and ``latest_more``: how many of that evaluation the E32 left out to stay within 1 KB (0: none);
- ``settings``: the knobs in effect by their plain names, "(automatic)" or "(set by you)";
- ``insights``: yesterday against the house's own usual days, each with what can cause it (E32 rc.5,
  insight.py; also a notification each);
- ``free_heat``: the rooms that get heat for free from sun, cooking and people, each with its free-heat line
  of ``rooms`` and the room's name (E32 rc.5), for the dashboard's "Free heat".

Read only: the knobs are changed in Configure → Home → Comfort and boiler care (e32_care.py) or on
the E32 page (Home -> Comfort and boiler care).
"""
import time
from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.restore_state import ExtraStoredData, RestoreEntity

from .const import DOMAIN

LOG_KEPT = 20  # one evaluation can step all ten knobs (E32 SL-A sends the whole newest day): a day and more
STATE_MAX = 255
REFERENCE_OUTDOOR_C, REFERENCE_ROOM_C = 5, 20  # "loses about .. per hour at 5 °C outside"
WARMUPS_TO_LEARN = 6                           # FlowLearner::Params::roomSegments

TEXT = {
    "en": {
        "h_m": "{h} h {m} min", "h": "{h} h", "m": "{m} min", "at_least": "at least {d}", "per_c": "{d} per °C",
        "gain": "{v} °C warmer water per °C too cold", "automatic": "(automatic)", "yours": "(set by you)",
        "standard": "(standard value)", "your_rooms": "A typical room",
        "knob.min_off_s": "Burner rest between starts", "knob.min_on_s": "Burner run time",
        "knob.heat_start_c": "Start heating when the room is this much below its target",
        "knob.heat_stop_c": "Stop heating when the room is this much above its target",
        "knob.flow_per_degree_c": "How strongly the water temperature reacts to a cold room",
        "knob.floor_lead_min_per_c": "Warm-up time for floor heating", "knob.radiator_lead_min_per_c": "Warm-up time for radiators",
        "knob.curve_correction_pct": "Room correction on weather compensation",
        "knob.learned_accept_pct": "Accepted warm-up time with the learned water temperature",
        "knob.night_saving_min_pct": "Smallest night saving worth advising",
        "why.many_starts": "The burner now rests at least {to} before it starts again, because it started {figure} times yesterday. Fewer starts are gentler on the boiler.",
        "why.cold_during_rest": "The burner rest is now {to}, because {subject} cooled {figure} °C below its target while the burner rested. Comfort comes first.",
        "why.short_burns": "Each burner run now lasts at least {to}, because {figure} runs yesterday were very short. Longer runs are gentler on the boiler.",
        "why.boiler_cycling": "The boiler switches on and off by itself ({figure} times yesterday); longer pauses would only delay heat, so this is now {to} again.",
        "why.overshoot": "{subject} got {figure} °C warmer than its target; the E32 now stops heating a little earlier.",
        "why.overshoot_gain": "{subject} still got {figure} °C warmer than its target; the E32 now heats a little more gently.",
        "why.settled": "{room} hardly gets too warm any more ({figure} °C); the E32 stops heating a little later again, so the burner starts less often.",
        "why.hovering": "Heating now starts when a room is {to} below its target, because it started {figure} times yesterday for small dips. Fewer starts are gentler on the boiler.",
        "why.few_starts": "Heating now starts sooner again, at {to} below the target: with only {figure} starts yesterday there is room for more comfort.",
        "why.room_response_up": "{room} warms about 1 °C in {figure}; the E32 now reacts a little more strongly to a cold room.",
        "why.room_response_down": "{room} warms about 1 °C in {figure}; the E32 now reacts a little more gently to a cold room.",
        "why.learned_warmup": "{room} warms about 1 °C in {figure}; the E32 starts from that until it has learned this room's warm-up.",
        "would": "Would change: {text}",
        "state.waiting": "After a restart or a change the E32 first watches a whole day before it adjusts anything.",
        "state.collecting": "Yesterday there was too little heating to learn from; the settings stay as they are.",
        "state.shadow": "Your current thermostat or the boiler's own control is still in charge, so the E32 only shows what it would change.",
        "state.active": "The E32 adjusts its settings itself, at most one small step a day.",
        "state.none": "Nothing changed yet: the start values still fit, or there is not enough to go on.",
        "learned": "Learned", "learning": "Learning: {n} of {m} warm-ups seen",
        "learning_seen": "Learning: {n} warm-ups seen; it still needs warm-ups on other days or at another water temperature",
        "learning_timing": "Warm-up time learned; the coolest water is still being learned",
        "learning_more": "It needs a few more warm-ups, on other days or at other water temperatures.",
        "learning_first": "It learns from every warm-up while the heating runs.",
        "learning_mean": "Until then it uses safe standard times.",
        "warms": "Warms about 1 °C in {d} with water of {flow} °C.",
        "warms_mean": "The E32 plans the start of every warm-up with this.",
        "lowest": "The lowest water temperature that still warms it in time: {flow} °C.",
        "lowest_mean": "Cooler water lets the boiler condense better, so it uses less gas.",
        "cools": "Loses about {rate} °C per hour at {out} °C outside.",
        "cools_mean": "This is how fast it cools when the heating is off, for example at night.",
        "free_heat": "{when} this room warms up by itself, about {rate} °C per hour (sun, cooking or people).",
        "free_heat_applied": "Its next warm-up starts {m} min later, so Smart warm-up does not heat what comes for free.",
        "free_heat_mean": "Smart warm-up takes this into account when it plans a warm-up at that time of day.",
        "daypart.0": "At night", "daypart.1": "Early in the morning", "daypart.2": "In the morning",
        "daypart.3": "In the afternoon", "daypart.4": "In the evening", "daypart.5": "Late in the evening",
        "start_only": "Starts heating at {start} for the next program step.",
        "start_mean": "So the room is warm on time, without heating longer than needed.",
        "warmup_on": "Smart warm-up: starts at {start} so it is {target} °C at {time}.",
        "warmup_now": "Smart warm-up: heating now so it is {target} °C at {time}.",
        "warmup_late": "Smart warm-up: heating now; {target} °C may come a little after {time}.",
        "warmup_ready": "Smart warm-up: warm enough for {target} °C at {time}, no early start needed.",
        "warmup_learning": "Smart warm-up is still learning: for now heating starts at {time} (estimate: from {start} it would be {target} °C on time).",
        "warmup_learning_mean": "Until the room has been learned, it does not start early on an estimate.",
        "warmup_off": "Smart warm-up is off: heating starts at {time}.",
        "warmup_off_mean": "Turn Smart warm-up on to be warm on time.",
        "warmup_room_off": "Smart warm-up is off for this room: heating starts at {time}.",
        "warmup_room_off_mean": "Chosen in the settings of this room (Configure → Rooms).",
        "warmup_estimate": "Smart warm-up: starts at {start} (estimate; it learns from every morning) so it is {target} °C at {time}.",
        "timing_learned": "The warm-up time is learned; the coolest water is still being learned.",
        "timing_learned_mean": "Smart warm-up already plans with it; the coolest water needs a few more warm-ups at other water temperatures.",
        "arrival": "{when} warm at {time} ({how}).",
        "arrival_earlier": "{when} warm at {time} ({how}); next time it starts a little earlier.",
        "arrival_later": "{when} warm at {time} ({how}); next time it starts a little later.",
        "arrival_earlier_min": "{when} warm at {time} ({how}); next time it starts about {n} earlier.",
        "arrival_later_min": "{when} warm at {time} ({how}); next time it starts about {n} later.",
        # E32 1.4.6 (ArrivalLearner::correct): within 10 min nothing changes, beyond it a part of the rest, at most 15 min
        "arrival_earlier_slow": "{when} warm at {time} ({how}); next time it starts a little earlier (at most a quarter of an hour a morning).",
        "arrival_later_slow": "{when} warm at {time} ({how}); next time it starts a little later (at most a quarter of an hour a morning).",
        "arrival_mean": "It checks every morning whether the room was warm on time and adjusts its warm-up time.",
        "arrival_mean_slow": "It checks every morning whether the room was warm on time. When it was more than 10 minutes off, it moves its warm-up time a little, never more than a quarter of an hour a morning.",
        "how_late": "{d} late",
        "how_early": "{d} early",
        "how_on_time": "on time",
        # 1.4.6 (HA-LEARN-TEXTS part B): what the E32's lead guard says about the room's warm-up time (lead_line)
        "lead_collecting": "Still learning its warm-up time. {n} of its last {m} mornings count; it needs 5 that count.",
        "lead_collecting_one": "Still learning its warm-up time. Its last morning counts; it needs 5 that count.",
        "lead_collecting_one_not": "Still learning its warm-up time. Its last morning did not count; it needs 5 that count.",
        "lead_collecting_none": "Still learning its warm-up time. No morning counts yet; it needs 5 that count.",
        "lead_collecting_plain": "Still learning its warm-up time; it needs 5 mornings that count.",
        "lead_checking": "Adjusting its warm-up time. It has 5 mornings that count, but fewer than 4 of them are within a quarter of an hour of the switch time.",
        "lead_learned": "Learned. At least 4 of its last 5 mornings that count were within a quarter of an hour of the switch time.",
        "lead_held": "Not learned for now. The E32 is watching its warm-up time.",
        "lead_held_evidence": "Not learned for now. Too few of its recent mornings counted, so the E32 is watching its warm-up time.",
        "lead_held_step": "Not learned for now. The correction moved a lot in one day, so the E32 is watching it.",
        "lead_held_range": "Not learned for now. The correction is at its limit, so the E32 is watching it.",
        "lead_mornings": "Last mornings, oldest first: {list}.",
        "lead_never": "not warm within 3 hours",
        "lead_not_counted": "{what} (not counted)",
        "lead_mean": "The E32 judges every morning and calls the warm-up time learned only when the recent mornings were close to the switch time. A morning may not count, for example after a restart or with much hot water in use. Home Assistant only shows what the E32 reports.",
        "when_today": "Today",
        "when_yesterday": "Yesterday",
        "when_date": "On {date}",
        "months": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec",
        "saving_eur": "about {m3} m³ gas ({eur}) a night", "saving": "about {m3} m³ gas a night",
        "night_hold": "Keeping it at {night} °C at night is cheaper than letting it cool down: {saving}.",
        "night_program": "Letting it cool down at night, as your program does, is the cheapest.",
        "night_mean": "This is advice: your week program stays as it is.",
        "curve_status_off": "Weather compensation: off, the water temperature follows the rooms only.",
        "curve_status_no_outdoor": "Weather compensation: no outdoor temperature right now, so the water temperature follows the rooms only.",
        "curve_status_learned": "Weather compensation: learned for your house.",
        "curve_status_learning": "Weather compensation: standard for now, learning from your house ({n} of {m} steady periods).",
        "curve_status_learning_plain": "Weather compensation: standard for now, learning from your house.",
        "curve_status_house": "Weather compensation: estimated from your house for now, learning more ({n} of {m} steady periods).",
        "curve_status_house_plain": "Weather compensation: estimated from your house for now, learning more.",
        "curve_status_mean": "The E32 decides by itself when what it learned is good enough to use.",
        "flow_status_collecting": "Coolest water: still learning from each warm-up.",
        "flow_status_ready": "Coolest water: learned for your house.",
        "flow_status_advice": "Coolest water: learned; used when Smart warm-up is on.",
        "flow_status_mean": "Cooler water lets the boiler condense better, so it uses less gas.",
        "curve_learned": "Weather compensation, learned from your house: the water gets about {s} °C warmer for every degree colder outside.",
        "curve_house": "Weather compensation, estimated from your house: the water gets about {s} °C warmer for every degree colder outside.",
        "curve": "Weather compensation: the water gets about {s} °C warmer for every degree colder outside.",
        "curve_on": "Weather compensation sets the water temperature, so the boiler runs as cool as the weather allows.",
        "curve_off": "Weather compensation is not switched on; this is shown as advice.",
        "burner": "Yesterday the burner started {n} times for heating; a burn lasted {d} on average.",
        "burner_starts": "Yesterday the burner started {n} times for heating.",
        "burner_often": "That is often. Fewer, longer burns are gentler on the boiler; the E32 works on that.",
        "burner_mean": "Fewer, longer burns are gentler on the boiler and use gas more efficiently.",
        "boiler_minimum": "Your boiler only starts heating from about {flow} °C water; the E32 asks at least that much.",
        "boiler_minimum_mean": "It learned this when the boiler did not start for cooler water.",
        "steady": "Your boiler burns steadily from about {flow} °C water; the E32 asks at least that much.",
        "steady_off": "Your boiler burns steadily from about {flow} °C water; with Smart warm-up on the E32 asks at least that much.",
        "steady_mean": "Below that it switches itself off and on at its lowest flame. Slightly warmer water means far fewer burner starts and costs at most a little efficiency.",
        "steady_trying": "The E32 is trying {to} °C water for half an hour: if the boiler keeps burning steadily there, it keeps that.",
        "steady_today": "today",
        "steady_yesterday": "yesterday",
        "steady_days": "{n} days ago",
        "steady_last_week": "last week",
        "steady_kept": "The E32 tried {d} °C lower water ({to} °C) {when} and kept it: the boiler burnt steadily there.",
        "steady_cycling": "The E32 tried {d} °C lower water ({to} °C) {when}; the boiler switched itself off and on there, so the E32 went back to {from_c} °C. It tries again in a week.",
        "steady_cool": "The E32 tried {d} °C lower water ({to} °C) {when}; a room cooled down, so the E32 went back to {from_c} °C. It tries again in a week.",
        # Plan item 1: which mode holds for the lowest water temperature (fw/telemetry/flow "minimum_flow").
        "minimum_auto": "Lowest water temperature: automatic, now {flow} °C.",
        "minimum_auto_mean": "The E32 sets it from what it learned about your boiler and house, never below 30 °C.",
        "minimum_own": "Lowest water temperature: set by you, now {flow} °C.",
        "minimum_own_mean": "The E32 never asks for cooler water, also when your boiler could do with less. Automatic: OpenThermostat → Configure → Heating and boiler → Water temperature limits.",
        "house_none": "Nothing yet: this appears after the first heating days.",
        "unavailable": "The E32 has not reported what it learned yet.",
        # rc7: the sentences review (R1, R3). {subject}: the room as the subject of a sentence.
        "your_rooms_subject": "a typical room",
        # 1.1.1 stage B (SL-B2): the room's model in shadow, in the E32 House page's words.
        "model.collecting": "The E32 is collecting readings for a model of {room}.",
        "model.checking": "The E32 is checking its predictions for {room} ({n} of {m} days good).",
        "model.trusted": "The E32 trusts its model of {room}: heat loss {ua} kW per degree, the room needs about {h} hours per degree at 50 °C water.",
        "model.trusted_plain": "The E32 trusts its model of {room}: heat loss {ua} kW per degree.",
        "model.trusted_bare": "The E32 trusts its model of {room}.",
        "model.demoted": "The model of {room} predicted less well; the E32 went back to its last good model and checks it again ({n} of {m} days good).",
        "model_mean": "For now this is only a check: nothing in the heating changes because of it.",
        "model_mean_planning": "The E32 plans the heating with this model.",
        "warmup_now_estimate": "Smart warm-up: heating now (estimate; it learns from every morning) so it is {target} °C at {time}.",
        "warmup_trial": "Smart warm-up in the trial run: it would start at {start} so it is {target} °C at {time}.",
        "warmup_trial_now": "Smart warm-up in the trial run: it would be heating now so it is {target} °C at {time}.",
        "free_heat_later": "So the warm-up starts {m} min later than without the free heat.",
        "arrival_not_warm": "{when} not warm within 3 hours after {time}.",
        "arrival_not_warm_earlier": "{when} not warm within 3 hours after {time}; next time it starts a little earlier.",
        "arrival_not_warm_earlier_min": "{when} not warm within 3 hours after {time}; next time it starts about {n} earlier.",
        "arrival_not_warm_earlier_slow": "{when} not warm within 3 hours after {time}; next time it starts a little earlier (at most a quarter of an hour a morning).",
        "saving_eur_once": "about {m3} m³ gas ({eur})",
        "saving_once": "about {m3} m³ gas",
        "night_hold_until": "Keeping it at {night} °C until {time} is cheaper than letting it cool down: {saving}.",
        "night_program_until": "Letting it cool down until {time}, as your program does, is the cheapest.",
        "burner_one": "Yesterday the burner started once for heating; the burn lasted {d}.",
        "burner_starts_one": "Yesterday the burner started once for heating.",
        "burner_none": "Yesterday the burner did not start for heating.",
        "why.few_starts_one": "Heating now starts sooner again, at {to} below the target: with only 1 start yesterday there is room for more comfort.",
        "would_set": "Would set “{knob}” to {to}, because {because}.",
        "because.many_starts": "the burner started {figure} times yesterday",
        "because.cold_during_rest": "{subject} cooled {figure} °C below its target while the burner rested",
        "because.short_burns": "{figure} burner runs yesterday were very short",
        "because.boiler_cycling": "the boiler switches on and off by itself ({figure} times yesterday)",
        "because.overshoot": "{subject} got {figure} °C warmer than its target",
        "because.overshoot_gain": "{subject} still got {figure} °C warmer than its target",
        "because.settled": "{room} hardly gets too warm any more ({figure} °C)",
        "because.hovering": "the burner started {figure} times yesterday for small dips",
        "because.few_starts": "there were only {figure} starts yesterday",
        "because.few_starts_one": "there was only 1 start yesterday",
        "because.room_response_up": "{room} warms about 1 °C in {figure}",
        "because.room_response_down": "{room} warms about 1 °C in {figure}",
        "because.learned_warmup": "{room} warms about 1 °C in {figure}",
        "learned_warms": "warms about 1 °C in {d} with water of {flow} °C",
        "curve_slope": "The water gets about {s} °C warmer for every degree colder outside.",
        # 1.4.3 (LEARN-TAB): a room's facts (room_facts): what a fact not learned yet still needs, never a number,
        # and the progress word of a room that learns nothing now.
        "wait.warmups": "{n} more warm-ups", "wait.warmup": "1 more warm-up",
        "wait.other_days": "warm-ups on other days or with other water",
        "wait.timing": "warm-up time learned; the water follows",
        "wait.after_warmup": "after the warm-up is learned",
        "wait.other_water": "warm-ups with another water temperature",
        "wait.not_found": "not found yet",
        "wait.cooling": "after a night without heating",
        "wait.free_heat": "not seen yet",
        "room_follow": "Heat along only", "room_off": "Off",
    },
    "nl": {
        "h_m": "{h} u {m} min", "h": "{h} u", "m": "{m} min", "at_least": "minstens {d}", "per_c": "{d} per °C",
        "gain": "{v} °C warmer water per °C te koud", "automatic": "(automatisch)", "yours": "(door jou ingesteld)",
        "standard": "(standaardwaarde)", "your_rooms": "Een gemiddelde ruimte",
        "knob.min_off_s": "Rust van de brander tussen starts", "knob.min_on_s": "Brandtijd",
        "knob.heat_start_c": "Begin met verwarmen als de ruimte zoveel onder de gewenste temperatuur is",
        "knob.heat_stop_c": "Stop met verwarmen als de ruimte zoveel boven de gewenste temperatuur is",
        "knob.flow_per_degree_c": "Hoe sterk de watertemperatuur reageert op een koude ruimte",
        "knob.floor_lead_min_per_c": "Opwarmtijd voor vloerverwarming", "knob.radiator_lead_min_per_c": "Opwarmtijd voor radiatoren",
        "knob.curve_correction_pct": "Ruimtecorrectie op de weerafhankelijke regeling",
        "knob.learned_accept_pct": "Toegestane opwarmtijd met de geleerde watertemperatuur",
        "knob.night_saving_min_pct": "Kleinste nachtbesparing die een advies waard is",
        "why.many_starts": "De brander rust nu minstens {to} voordat hij weer start, omdat hij gisteren {figure} keer startte. Minder starts zijn beter voor de ketel.",
        "why.cold_during_rest": "De rust van de brander is nu {to}, omdat {subject} {figure} °C onder de gewenste temperatuur afkoelde terwijl de brander rustte. Comfort gaat voor.",
        "why.short_burns": "Elke keer branden duurt nu minstens {to}, omdat {figure} keer branden gisteren heel kort was. Langer branden is beter voor de ketel.",
        "why.boiler_cycling": "De ketel schakelt zelf aan en uit ({figure} keer gisteren); langere pauzes zouden de warmte alleen vertragen, dus dit is nu weer {to}.",
        "why.overshoot": "{subject} werd {figure} °C warmer dan gewenst; de E32 stopt nu iets eerder met verwarmen.",
        "why.overshoot_gain": "{subject} werd nog steeds {figure} °C warmer dan gewenst; de E32 verwarmt nu iets rustiger.",
        "why.settled": "{room} wordt bijna niet meer te warm ({figure} °C); de E32 stopt weer iets later met verwarmen, zodat de brander minder vaak start.",
        "why.hovering": "Het verwarmen start nu als een ruimte {to} onder de gewenste temperatuur is, omdat het gisteren {figure} keer startte voor kleine dalingen. Minder starts zijn beter voor de ketel.",
        "why.few_starts": "Het verwarmen start nu weer eerder, bij {to} onder de gewenste temperatuur: met maar {figure} starts gisteren is er ruimte voor meer comfort.",
        "why.room_response_up": "{room} warmt ongeveer 1 °C op in {figure}; de E32 reageert nu iets sterker op een koude ruimte.",
        "why.room_response_down": "{room} warmt ongeveer 1 °C op in {figure}; de E32 reageert nu iets rustiger op een koude ruimte.",
        "why.learned_warmup": "{room} warmt ongeveer 1 °C op in {figure}; daar begint de E32 mee tot hij de opwarming van deze ruimte heeft geleerd.",
        "would": "Zou aanpassen: {text}",
        "state.waiting": "Na een herstart of een wijziging kijkt de E32 eerst een hele dag voordat hij iets aanpast.",
        "state.collecting": "Gisteren werd er te weinig verwarmd om van te leren; de instellingen blijven zoals ze zijn.",
        "state.shadow": "Je huidige thermostaat of de eigen regeling van de ketel is nog de baas, dus de E32 laat alleen zien wat hij zou aanpassen.",
        "state.active": "De E32 past zijn instellingen zelf aan, hooguit één kleine stap per dag.",
        "state.none": "Nog niets aangepast: de beginwaarden passen nog, of er is nog te weinig om op af te gaan.",
        "learned": "Geleerd", "learning": "Aan het leren: {n} van {m} keer opwarmen gezien",
        "learning_seen": "Aan het leren: {n} keer opwarmen gezien; nog nodig: opwarmen op andere dagen of bij een andere watertemperatuur",
        "learning_timing": "Opwarmtijd geleerd; het koelste water leert hij nog",
        "learning_more": "Hij heeft nog een paar keer opwarmen nodig, op andere dagen of bij andere watertemperaturen.",
        "learning_first": "Hij leert van elke keer opwarmen terwijl de verwarming aan staat.",
        "learning_mean": "Tot dan gebruikt hij veilige standaardtijden.",
        "warms": "Warmt ongeveer 1 °C op in {d} met water van {flow} °C.",
        "warms_mean": "Hiermee plant de E32 de start van elke keer opwarmen.",
        "lowest": "De laagste watertemperatuur die nog op tijd opwarmt: {flow} °C.",
        "lowest_mean": "Met koeler water condenseert de ketel beter, dus verbruikt hij minder gas.",
        "cools": "Verliest ongeveer {rate} °C per uur bij {out} °C buiten.",
        "cools_mean": "Zo snel koelt de ruimte af als de verwarming uit is, bijvoorbeeld 's nachts.",
        "free_heat": "{when} warmt deze ruimte vanzelf op, ongeveer {rate} °C per uur (zon, koken of mensen).",
        "free_heat_applied": "De volgende opwarming begint daardoor {m} min later, zodat Slim opwarmen niet verwarmt wat "
                             "gratis komt.",
        "free_heat_mean": "Slim opwarmen houdt hier rekening mee als het op dat moment van de dag opwarmt.",
        "daypart.0": "'s Nachts", "daypart.1": "Vroeg in de ochtend", "daypart.2": "'s Ochtends",
        "daypart.3": "'s Middags", "daypart.4": "'s Avonds", "daypart.5": "Laat op de avond",
        "start_only": "Begint om {start} met verwarmen voor de volgende stap van het programma.",
        "start_mean": "Zo is de ruimte op tijd warm, zonder langer te verwarmen dan nodig.",
        "warmup_on": "Slim opwarmen: begint om {start}, zodat het om {time} {target} °C is.",
        "warmup_now": "Slim opwarmen: verwarmt nu, zodat het om {time} {target} °C is.",
        "warmup_late": "Slim opwarmen: verwarmt nu; {target} °C wordt misschien pas iets na {time} gehaald.",
        "warmup_ready": "Slim opwarmen: warm genoeg voor {target} °C om {time}, eerder beginnen is niet nodig.",
        "warmup_learning": "Slim opwarmen leert nog: voorlopig begint verwarmen om {time} (schatting: vanaf {start} zou het op tijd {target} °C zijn).",
        "warmup_learning_mean": "Zolang de ruimte niet geleerd is, begint hij niet eerder op een schatting.",
        "warmup_off": "Slim opwarmen staat uit: verwarmen begint om {time}.",
        "warmup_off_mean": "Zet Slim opwarmen aan om op tijd warm te zijn.",
        "warmup_room_off": "Slim opwarmen staat uit voor deze ruimte: verwarmen begint om {time}.",
        "warmup_room_off_mean": "Zo gekozen in de instellingen van deze ruimte (Configureren → Ruimtes).",
        "warmup_estimate": "Slim opwarmen: begint om {start} (schatting; hij leert van elke ochtend), zodat het om {time} {target} °C is.",
        "timing_learned": "De opwarmtijd is geleerd; het koelste water leert hij nog.",
        "timing_learned_mean": "Slim opwarmen plant daar al mee; voor het koelste water zijn nog een paar keer opwarmen bij andere watertemperaturen nodig.",
        "arrival": "{when} warm om {time} ({how}).",
        "arrival_earlier": "{when} warm om {time} ({how}); de volgende keer begint het iets eerder.",
        "arrival_later": "{when} warm om {time} ({how}); de volgende keer begint het iets later.",
        "arrival_earlier_min": "{when} warm om {time} ({how}); de volgende keer begint het ongeveer {n} eerder.",
        "arrival_later_min": "{when} warm om {time} ({how}); de volgende keer begint het ongeveer {n} later.",
        "arrival_earlier_slow": "{when} warm om {time} ({how}); de volgende keer begint het iets eerder (hooguit een kwartier per ochtend).",
        "arrival_later_slow": "{when} warm om {time} ({how}); de volgende keer begint het iets later (hooguit een kwartier per ochtend).",
        "arrival_mean": "Hij kijkt elke ochtend of de ruimte op tijd warm was en past zijn opwarmtijd daarop aan.",
        "arrival_mean_slow": "Hij kijkt elke ochtend of de ruimte op tijd warm was. Scheelde het meer dan 10 minuten, dan verschuift hij zijn opwarmtijd een beetje, nooit meer dan een kwartier per ochtend.",
        "how_late": "{d} te laat",
        "how_early": "{d} te vroeg",
        "how_on_time": "op tijd",
        "lead_collecting": "Leert zijn opwarmtijd nog. {n} van zijn laatste {m} ochtenden tellen mee; hij heeft er 5 nodig die meetellen.",
        "lead_collecting_one": "Leert zijn opwarmtijd nog. Zijn laatste ochtend telt mee; hij heeft er 5 nodig die meetellen.",
        "lead_collecting_one_not": "Leert zijn opwarmtijd nog. Zijn laatste ochtend telde niet mee; hij heeft er 5 nodig die meetellen.",
        "lead_collecting_none": "Leert zijn opwarmtijd nog. Nog geen ochtend telt mee; hij heeft er 5 nodig die meetellen.",
        "lead_collecting_plain": "Leert zijn opwarmtijd nog; hij heeft 5 ochtenden nodig die meetellen.",
        "lead_checking": "Past zijn opwarmtijd aan. Hij heeft 5 ochtenden die meetellen, maar minder dan 4 daarvan liggen binnen een kwartier van de schakeltijd.",
        "lead_learned": "Geleerd. Minstens 4 van zijn laatste 5 ochtenden die meetellen lagen binnen een kwartier van de schakeltijd.",
        "lead_held": "Voorlopig niet geleerd. De E32 let op zijn opwarmtijd.",
        "lead_held_evidence": "Voorlopig niet geleerd. Te weinig van zijn recente ochtenden telden mee, dus de E32 let op zijn opwarmtijd.",
        "lead_held_step": "Voorlopig niet geleerd. De bijstelling veranderde in één dag flink, dus de E32 let erop.",
        "lead_held_range": "Voorlopig niet geleerd. De bijstelling zit aan haar grens, dus de E32 let erop.",
        "lead_mornings": "Laatste ochtenden, oudste eerst: {list}.",
        "lead_never": "niet warm binnen 3 uur",
        "lead_not_counted": "{what} (telt niet mee)",
        "lead_mean": "De E32 beoordeelt elke ochtend en noemt de opwarmtijd pas geleerd als de laatste ochtenden dicht bij de schakeltijd lagen. Een ochtend telt soms niet mee, bijvoorbeeld na een herstart of als er veel warm water werd gebruikt. Home Assistant toont alleen wat de E32 meldt.",
        "when_today": "Vandaag",
        "when_yesterday": "Gisteren",
        "when_date": "Op {date}",
        "months": "jan feb mrt apr mei jun jul aug sep okt nov dec",
        "saving_eur": "ongeveer {m3} m³ gas ({eur}) per nacht", "saving": "ongeveer {m3} m³ gas per nacht",
        "night_hold": "'s Nachts op {night} °C houden is goedkoper dan laten afkoelen: {saving}.",
        "night_program": "'s Nachts laten afkoelen, zoals je programma doet, is het goedkoopst.",
        "night_mean": "Dit is een advies: je weekprogramma blijft zoals het is.",
        "curve_status_off": "Weerafhankelijke regeling: uit, de watertemperatuur volgt alleen de ruimtes.",
        "curve_status_no_outdoor": "Weerafhankelijke regeling: nu geen buitentemperatuur, dus de watertemperatuur volgt alleen de ruimtes.",
        "curve_status_learned": "Weerafhankelijke regeling: geleerd voor je huis.",
        "curve_status_learning": "Weerafhankelijke regeling: voorlopig standaard, hij leert van je huis ({n} van {m} rustige periodes).",
        "curve_status_learning_plain": "Weerafhankelijke regeling: voorlopig standaard, hij leert van je huis.",
        "curve_status_house": "Weerafhankelijke regeling: voorlopig geschat uit je huis, hij leert nog bij ({n} van {m} rustige periodes).",
        "curve_status_house_plain": "Weerafhankelijke regeling: voorlopig geschat uit je huis, hij leert nog bij.",
        "curve_status_mean": "De E32 beslist zelf wanneer wat hij leerde goed genoeg is om te gebruiken.",
        "flow_status_collecting": "Koelste water: leert nog van elke keer opwarmen.",
        "flow_status_ready": "Koelste water: geleerd voor je huis.",
        "flow_status_advice": "Koelste water: geleerd; wordt gebruikt als Slim opwarmen aan staat.",
        "flow_status_mean": "Met koeler water condenseert de ketel beter, dus verbruikt hij minder gas.",
        "curve_learned": "Weerafhankelijke regeling, geleerd van je huis: het water wordt ongeveer {s} °C warmer voor elke graad kouder buiten.",
        "curve_house": "Weerafhankelijke regeling, geschat uit je huis: het water wordt ongeveer {s} °C warmer voor elke graad kouder buiten.",
        "curve": "Weerafhankelijke regeling: het water wordt ongeveer {s} °C warmer voor elke graad kouder buiten.",
        "curve_on": "De weerafhankelijke regeling bepaalt de watertemperatuur, zodat de ketel zo koel draait als het weer toelaat.",
        "curve_off": "De weerafhankelijke regeling staat niet aan; dit is een advies.",
        "burner": "Gisteren startte de brander {n} keer voor verwarmen; hij brandde gemiddeld {d}.",
        "burner_starts": "Gisteren startte de brander {n} keer voor verwarmen.",
        "burner_often": "Dat is vaak. Minder en langer branden is beter voor de ketel; de E32 werkt daaraan.",
        "burner_mean": "Minder en langer branden is beter voor de ketel en gebruikt gas zuiniger.",
        "boiler_minimum": "Je ketel begint pas te verwarmen vanaf water van ongeveer {flow} °C; de E32 vraagt minstens zoveel.",
        "boiler_minimum_mean": "Dat leerde hij toen de ketel voor koeler water niet aansloeg.",
        "steady": "Je ketel brandt rustig door vanaf water van ongeveer {flow} °C; de E32 vraagt minstens zoveel.",
        "steady_off": "Je ketel brandt rustig door vanaf water van ongeveer {flow} °C; met Slim opwarmen aan vraagt de E32 minstens zoveel.",
        "steady_mean": "Daaronder slaat hij op zijn kleinste vlam steeds af en weer aan. Iets warmer water geeft veel minder branderstarts en kost hooguit een klein beetje rendement.",
        "steady_trying": "De E32 probeert een half uur water van {to} °C: blijft de ketel daar rustig doorbranden, dan houdt hij dat aan.",
        "steady_today": "vandaag",
        "steady_yesterday": "gisteren",
        "steady_days": "{n} dagen geleden",
        "steady_last_week": "vorige week",
        "steady_kept": "De E32 probeerde {when} {d} °C lager water ({to} °C) en hield dat aan: de ketel brandde daar rustig door.",
        "steady_cycling": "De E32 probeerde {when} {d} °C lager water ({to} °C); de ketel sloeg daar steeds af en weer aan, dus ging de E32 terug naar {from_c} °C. Over een week probeert hij het opnieuw.",
        "steady_cool": "De E32 probeerde {when} {d} °C lager water ({to} °C); een ruimte koelde af, dus ging de E32 terug naar {from_c} °C. Over een week probeert hij het opnieuw.",
        "minimum_auto": "Laagste watertemperatuur: automatisch, nu {flow} °C.",
        "minimum_auto_mean": "De E32 stelt hem in met wat hij over je ketel en huis leerde, nooit onder 30 °C.",
        "minimum_own": "Laagste watertemperatuur: door jou ingesteld, nu {flow} °C.",
        "minimum_own_mean": "De E32 vraagt nooit koeler water, ook als je ketel met minder toe kan. Automatisch: OpenThermostat → Configureren → Verwarming en ketel → Grenzen van de watertemperatuur.",
        "house_none": "Nog niets: dit verschijnt na de eerste dagen met verwarming.",
        "unavailable": "De E32 heeft nog niet gemeld wat hij geleerd heeft.",
        # rc7: the sentences review (R1, R3).
        "your_rooms_subject": "een gemiddelde ruimte",
        # 1.1.1 stage B (SL-B2): the room's model in shadow, in the E32 House page's words.
        "model.collecting": "De E32 verzamelt metingen voor een model van {room}.",
        "model.checking": "De E32 controleert zijn voorspellingen voor {room} ({n} van {m} dagen goed).",
        "model.trusted": "De E32 vertrouwt zijn model van {room}: warmteverlies {ua} kW per graad, de ruimte heeft ongeveer {h} uur per graad nodig bij water van 50 °C.",
        "model.trusted_plain": "De E32 vertrouwt zijn model van {room}: warmteverlies {ua} kW per graad.",
        "model.trusted_bare": "De E32 vertrouwt zijn model van {room}.",
        "model.demoted": "Het model van {room} voorspelde minder goed; de E32 gebruikt weer zijn laatste goede model en controleert het opnieuw ({n} van {m} dagen goed).",
        "model_mean": "Voorlopig is dit alleen een controle: er verandert niets aan de verwarming door.",
        "model_mean_planning": "De E32 plant de verwarming met dit model.",
        "warmup_now_estimate": "Slim opwarmen: verwarmt nu (schatting; hij leert van elke ochtend), zodat het om {time} {target} °C is.",
        "warmup_trial": "Slim opwarmen in de proefperiode: het zou om {start} beginnen, zodat het om {time} {target} °C is.",
        "warmup_trial_now": "Slim opwarmen in de proefperiode: het zou nu verwarmen, zodat het om {time} {target} °C is.",
        "free_heat_later": "Daardoor begint het opwarmen {m} min later dan zonder de gratis warmte.",
        "arrival_not_warm": "{when} niet warm binnen 3 uur na {time}.",
        "arrival_not_warm_earlier": "{when} niet warm binnen 3 uur na {time}; de volgende keer begint het iets eerder.",
        "arrival_not_warm_earlier_min": "{when} niet warm binnen 3 uur na {time}; de volgende keer begint het ongeveer {n} eerder.",
        "arrival_not_warm_earlier_slow": "{when} niet warm binnen 3 uur na {time}; de volgende keer begint het iets eerder (hooguit een kwartier per ochtend).",
        "saving_eur_once": "ongeveer {m3} m³ gas ({eur})",
        "saving_once": "ongeveer {m3} m³ gas",
        "night_hold_until": "Tot {time} op {night} °C houden is goedkoper dan laten afkoelen: {saving}.",
        "night_program_until": "Tot {time} laten afkoelen, zoals je programma doet, is het goedkoopst.",
        "burner_one": "Gisteren startte de brander 1 keer voor verwarmen; hij brandde {d}.",
        "burner_starts_one": "Gisteren startte de brander 1 keer voor verwarmen.",
        "burner_none": "Gisteren startte de brander niet voor verwarmen.",
        "why.few_starts_one": "Het verwarmen start nu weer eerder, bij {to} onder de gewenste temperatuur: met maar 1 start gisteren is er ruimte voor meer comfort.",
        "would_set": "Zou ‘{knob}’ op {to} zetten, omdat {because}.",
        "because.many_starts": "de brander gisteren {figure} keer startte",
        "because.cold_during_rest": "{subject} {figure} °C onder de gewenste temperatuur afkoelde terwijl de brander rustte",
        "because.short_burns": "{figure} keer branden gisteren heel kort was",
        "because.boiler_cycling": "de ketel zelf aan en uit schakelt ({figure} keer gisteren)",
        "because.overshoot": "{subject} {figure} °C warmer werd dan gewenst",
        "because.overshoot_gain": "{subject} nog steeds {figure} °C warmer werd dan gewenst",
        "because.settled": "{room} bijna niet meer te warm wordt ({figure} °C)",
        "because.hovering": "het verwarmen gisteren {figure} keer startte voor kleine dalingen",
        "because.few_starts": "er gisteren maar {figure} starts waren",
        "because.few_starts_one": "er gisteren maar 1 start was",
        "because.room_response_up": "{room} ongeveer 1 °C opwarmt in {figure}",
        "because.room_response_down": "{room} ongeveer 1 °C opwarmt in {figure}",
        "because.learned_warmup": "{room} ongeveer 1 °C opwarmt in {figure}",
        "learned_warms": "warmt ongeveer 1 °C op in {d} met water van {flow} °C",
        "curve_slope": "Het water wordt ongeveer {s} °C warmer voor elke graad kouder buiten.",
        "wait.warmups": "nog {n} opwarmingen", "wait.warmup": "nog 1 opwarming",
        "wait.other_days": "opwarmingen op andere dagen of met ander water",
        "wait.timing": "opwarmtijd geleerd; het water volgt",
        "wait.after_warmup": "zodra het opwarmen geleerd is",
        "wait.other_water": "opwarmingen bij een andere watertemperatuur",
        "wait.not_found": "nog niet gevonden",
        "wait.cooling": "na een nacht zonder verwarming",
        "wait.free_heat": "nog niet gezien",
        "room_follow": "Alleen meeverwarmen", "room_off": "Uit",
    },
}
# The knobs (control/ControlTuning.h): automatic (AutoTuner) or fixed, the built-in value and how a value reads.
KNOBS = (("min_off_s", True, 300, "rest"), ("min_on_s", True, 300, "run"), ("heat_start_c", True, 0.2, "c"),
         ("heat_stop_c", True, 0.2, "c"), ("flow_per_degree_c", True, 10, "gain"), ("floor_lead_min_per_c", True, 120, "lead"),
         ("radiator_lead_min_per_c", True, 45, "lead"), ("curve_correction_pct", False, 50, "pct"),
         ("learned_accept_pct", False, 100, "pct"), ("night_saving_min_pct", False, 2, "pct"))
KNOB = {key: (auto, default, kind) for key, auto, default, kind in KNOBS}
MINUTE_REASONS = ("room_response", "learned_warmup")


def language(hass):
    """English or Dutch by the Home Assistant language (English otherwise)."""
    value = (getattr(getattr(hass, "config", None), "language", None) or "en").lower().replace("_", "-").split("-")[0]
    return value if value in TEXT else "en"


def number(value, lang, digits=1):
    """A short decimal: 0.15, 7.5, 21 (a decimal comma in Dutch)."""
    text = f"{round(float(value), digits):.{digits}f}".rstrip("0").rstrip(".") if digits else str(round(float(value)))
    return text.replace(".", ",") if lang != "en" else text


def _ok(value):
    return type(value) in (int, float) and value == value and abs(value) < 1e12  # times are unix seconds


def duration(minutes, lang):
    """Minutes in words: "7.5 min" (half minutes below an hour), "1 h 30 min", "2 h"."""
    t = TEXT[lang]
    if minutes < 57.5:
        return t["m"].format(m=number(max(0.5, round(minutes * 2) / 2), lang))
    rounded = int(round(minutes / 5) * 5)
    hours, rest = divmod(rounded, 60)
    return t["h_m"].format(h=hours, m=rest) if rest else t["h"].format(h=hours)


def knob_value(key, value, lang):
    """A knob's value in words, as the E32 page shows it."""
    t, kind = TEXT[lang], KNOB[key][2]
    if kind == "rest":
        return duration(value / 60, lang)
    if kind == "run":
        return t["at_least"].format(d=duration(value / 60, lang))
    if kind == "c":
        return number(value, lang, 2) + " °C"
    if kind == "gain":
        return t["gain"].format(v=number(value, lang, 0))
    if kind == "lead":
        return t["per_c"].format(d=duration(value, lang))
    return number(value, lang, 0) + " %"


def change_text(change, names, lang, proposal=False):
    """One change ([knob, from, to, reason, figure, room]) in words, or None when it is not understood.

    proposal: a change the trial run only proposes (``tuning.would``): "Would set “Burner rest between starts” to
    10 min, because the burner started 25 times yesterday.", never the "now rests" of a change made. The
    sentence starts with a capital.
    """
    if type(change) is not list or len(change) != 6:
        return None
    key, old, new, reason, figure, room = change
    if key not in KNOB or not all(_ok(v) for v in (old, new, figure)) or type(reason) is not str or type(room) is not str:
        return None
    t = TEXT[lang]
    if reason == "room_response":
        reason = "room_response_up" if new > old else "room_response_down"
    if reason == "few_starts" and figure == 1:  # "with only 1 start", not "1 starts"
        reason = "few_starts_one"
    template = t.get(("because." if proposal else "why.") + reason)
    if template is None:
        return None
    shown = (duration(figure, lang) if reason.startswith("room_response") or reason == "learned_warmup"
             else str(figure) if float(figure).is_integer() else number(figure, lang, 2))
    name = names.get(room, room) if room else t["your_rooms"]
    subject = name if room else t.get("your_rooms_subject", name)
    values = {"to": knob_value(key, new, lang), "figure": shown, "room": name, "subject": subject}
    text = template.format(**values)
    if proposal:
        text = t["would_set"].format(knob=t["knob." + key], to=values["to"], because=text)
    return text[:1].upper() + text[1:]


def merge_changes(kept, incoming):
    """The newest LOG_KEPT changes ([utc, knob, from, to, reason, figure, room]) of both, newest first."""
    seen, merged = set(), []
    for change in sorted([c for c in list(incoming) + list(kept) if type(c) is list and len(c) == 7 and _ok(c[0])],
                         key=lambda c: -c[0]):
        key = (change[0], change[1])
        if key in seen:
            continue
        seen.add(key)
        merged.append(change)
    return merged[:LOG_KEPT]


def newest_evaluation(log, tuning=None):
    """(the newest evaluation's changes, how many of it are missing) from the kept log, newest first.

    One evaluation steps several knobs at one time (one utc). ``tuning``: the E32's tuning; its ``day_changes``
    (SL-A) says how many that evaluation made when its newest change is the newest kept here.
    """
    if not log:
        return [], 0
    newest = [change for change in log if change[0] == log[0][0]]
    tuning = tuning if type(tuning) is dict else {}
    sent = tuning.get("log") if type(tuning.get("log")) is list else []
    made = tuning.get("day_changes")
    same = bool(sent) and type(sent[0]) is list and len(sent[0]) == 7 and sent[0][0] == log[0][0]
    missing = made - len(newest) if same and type(made) is int and 0 < made <= 64 and made > len(newest) else 0
    return newest, missing


def settings(values, manual, lang):
    """{plain name: "10 min (automatic)"} for the knobs in effect."""
    t, out = TEXT[lang], {}
    for key, auto, default, _ in KNOBS:
        value = values.get(key) if type(values) is dict else None
        if not _ok(value):
            continue
        mine = key in manual if auto else value != default
        out[t["knob." + key]] = knob_value(key, value, lang) + " " + t["yours" if mine else "automatic" if auto else "standard"]
    return out


def _line(text, meaning):
    return {"text": text, "meaning": meaning}


def room_smart_warm_up(room, house):
    """E32 1.4 (#8): (on, room_off) of Smart warm-up as one room has it. ``room``: the room's status (its
    ``smart_warm_up`` "on" / "off" is the value in effect: its own choice or the house switch); ``house``: the house
    switch (``apply_learned``; None: not known). Older firmware names no value: the house switch. room_off: off for this
    room only (the house switch is not off), so the line can say so."""
    value = room.get("smart_warm_up") if type(room) is dict else None
    if value == "on":
        return True, False
    if value == "off":
        return False, house is not False
    return house, False


def smart_warm_up_line(start, on, lang, clock, trial=False, later_min=0, now=None, room_off=False):
    """(text, meaning) for the room's next program step with Smart warm-up (E32 rc.3), or None.

    ``start``: the room's ``optimum_start``; ``on``: the stored option (``apply_learned``; None: not
    known, on by default), E32 1.4 the room's own value in effect (room_smart_warm_up); room_off: off for this room
    only. ``applies``: the E32 uses this start (older firmware: a learned warm-up);
    otherwise it is an estimate and heating starts at the program time. The E32 page says the same
    (``data/html/index.html`` smartWarmupLine), "heating now (estimate; ...)" too.

    trial: the trial run (the heat request's mode ``shadow``): the E32 heats nothing early, so the line says what
    it would do. later_min: the minutes the free heat moves the start later (``free_heat.applied_min``,
    FreeHeat::shorten in FlowPolicy; the telemetry's ``predicted_start_utc`` is the start without it), so the
    line names the start the E32 really uses; now: unix seconds (for "heating now" once the later start passed).
    """
    t = TEXT[lang]
    start = start if type(start) is dict else {}
    switch = start.get("next_switch") if type(start.get("next_switch")) is dict else {}
    if (start.get("reason") != "planned" or not _ok(start.get("predicted_start_utc"))
            or not _ok(switch.get("utc")) or not _ok(switch.get("target_c"))):
        return None
    shift = later_min * 60 if type(later_min) is int and later_min > 0 and on is not False else 0
    begin = start["predicted_start_utc"] + shift
    values = {"start": clock(begin), "time": clock(switch["utc"]), "target": number(switch["target_c"], lang)}
    applies = start["applies"] if type(start.get("applies")) is bool else start.get("confidence") == "learned"
    # With the free heat the E32 starts later: "heating now" only once that later start has come.
    heating = start.get("start_now") is True and (not shift or begin <= (time.time() if now is None else now))
    if on is False:
        key = "warmup_room_off" if room_off else "warmup_off"
        return t[key].format(**values), t[key + "_mean"]
    if not applies:
        return t["warmup_learning"].format(**values), t["warmup_learning_mean"]
    if start.get("lead_minutes") == 0 and start.get("start_now") is not True:
        key = "warmup_ready"
    elif heating:
        key = ("warmup_trial_now" if trial else "warmup_late" if start.get("reachable") is False and not shift
               else "warmup_now_estimate" if start.get("estimate") is True else "warmup_now")
    elif trial:
        key = "warmup_trial"
    else:  # E32 rc.4: a start from the standard warm-up time is applied too, as an estimate
        key = "warmup_estimate" if start.get("estimate") is True else "warmup_on"
    return t[key].format(**values), t["state.shadow" if trial and key != "warmup_ready" else "start_mean"]


def whole_minutes(minutes, lang):
    """Whole minutes in words, exact: "12 min", "1 h 35 min", "2 h" (duration() rounds above an hour)."""
    t = TEXT[lang]
    if minutes < 60:
        return t["m"].format(m=minutes)
    hours, rest = divmod(minutes, 60)
    return t["h_m"].format(h=hours, m=rest) if rest else t["h"].format(h=hours)


NOT_WARM_MIN = 180   # ArrivalLearner::Params::windowS: a room not warm within 3 h counts as 3 h late
LATE_MIN, EARLY_MIN = 10, -15   # ArrivalLearner lateS (600 s) and earlyS (900 s): the factor changes beyond these
FACTOR_LIMITS = (0.5, 2.0)      # ArrivalLearner minFactor and maxFactor (E32 1.4.5 and older)
FACTOR_LIMITS_SLOW = (0.7, 1.5)  # E32 1.4.6 (learnbounds, the lead budget): the factor stays within these
STEP_LIMITS = (0.5, 1.5)        # ArrivalLearner minStep and maxStep (E32 SL-A): one morning moves the lead at most so much
PROPORTIONAL_FROM_MIN = 15      # below this lead (proportionalFromS is 10 min, plus margin) the E32 keeps small steps
SAME_RISE_S = 3600              # the next rise is the judged one's on a later day when it is this close in clock time
# E32 1.4.6 (ArrivalLearner::correct, review B1): an error within 10 min either way changes nothing; beyond it 30 % of the
# rest moves the next start, at most 15 min a morning (and never more than an hour in all from the model's own lead,
# which Home Assistant cannot see: the text says "at most a quarter of an hour").
SLOW_DEAD_ZONE_MIN = 10
SLOW_FROM_VERSION = (1, 4, 6, 0, 0)   # firmware_update.parse_tag of the first E32 with that rule (any 1.4.6 tag)


def slow_correction(version):
    """Which rule the E32 follows for a judged morning, from its firmware version (``hub.firmware_version``, the
    version the room-plan link read): True from E32 1.4.6 (slow correction), False for an older E32 (proportional,
    E32 SL-A), None while the version is not known (then the text claims neither: no figure, the old thresholds)."""
    from .firmware_update import parse_tag
    key = parse_tag(version)
    return None if key is None else key >= SLOW_FROM_VERSION


def factor_limits(slow):
    """The (lowest, highest) factor the E32 allows itself: 0.7..1.5 from E32 1.4.6 (slow True), 0.5..2.0 before. While
    the version is not known (None) the narrower of the two: the text then never claims a move the E32 cannot make."""
    return FACTOR_LIMITS if slow is False else FACTOR_LIMITS_SLOW


def _judged(minutes, factor, slow):
    """(earlier, later): whether the E32 moves the next start after a morning that was ``minutes`` late (negative:
    early), with its rule (slow_correction) and the factor not at its limit (factor_limits)."""
    low, high = factor_limits(slow)
    if slow is True:
        late, early = minutes > SLOW_DEAD_ZONE_MIN, minutes < -SLOW_DEAD_ZONE_MIN
    else:
        late, early = minutes >= LATE_MIN, minutes <= EARLY_MIN
    return (late and (factor is None or factor < high - 1e-3),
            early and (factor is None or factor > low + 1e-3))


def arrival_shift(minutes, start, at, slow=False):
    """About how many minutes the next warm-up starts earlier (late) or later (early) after this morning, or None.

    ``slow`` (slow_correction): from E32 1.4.6 the move does not follow the lead and Home Assistant cannot see the
    hour's budget, so it names no figure (None: "a little", at most a quarter of an hour); unknown (None): no figure.
    The rest of this paragraph is the rule of E32 1.4.5 and older (``slow`` False).

    E32 SL-A (ArrivalLearner::resolve): the lead moves in proportion, to the lead that would have been right (lead +
    error), at most x0.5..x1.5 per morning. The E32 sends the new lead of the next rise (``optimum_start``
    ``lead_minutes``), not the old one; when that rise is the judged one on a later day (and its warm-up has not
    started), the move is the error, capped at a third of the new lead when late (x1.5) and at the new lead when
    early (x0.5). Rounded to 5 minutes; None when
    the numbers do not tell it (another rise next, a short lead, firmware without them): then "a little".
    """
    if slow is not False:
        return None
    start = start if type(start) is dict else {}
    lead, switch = start.get("lead_minutes"), start.get("next_switch")
    rise = switch.get("utc") if type(switch) is dict else None
    # While the next warm-up runs its lead shrinks with the room's warming: no longer the lead it planned.
    if not _ok(lead) or lead < PROPORTIONAL_FROM_MIN or not _ok(rise) or rise <= at or start.get("start_now") is True:
        return None
    apart = (rise - at) % 86400
    if min(apart, 86400 - apart) > SAME_RISE_S or rise - at < 86400 - SAME_RISE_S:
        return None
    late = minutes > 0
    cap = lead * (1 - 1 / STEP_LIMITS[1]) if late else lead * (1 / STEP_LIMITS[0] - 1)
    shown = int(round(min(abs(minutes), cap) / 5) * 5)
    return shown if shown >= 5 else None


def arrival_line(arrival, lang, clock, day=None, today=None, start=None, slow=False):
    """(text, meaning) on how the room's last program step up turned out (E32 rc.4), or None.

    ``arrival`` (the room's plan): ``last_at_utc`` the program's switch time of the last judged morning,
    ``last_error_min`` how many minutes after it the room was warm (negative: before it; the room was
    warm at last_at_utc + last_error_min, ArrivalLearner::resolve), ``factor`` what the E32 now does
    with the warm-up time (above 1: it starts earlier). clock: utc -> "09:12"; day: utc -> the local
    date; today: the local date now ("Yesterday warm at 09:12 (12 min late); next time it starts a little earlier.").
    start: the room's ``optimum_start``: with it the E32's numbers may say how much ("about 10 min earlier",
    arrival_shift).
    slow: the rule of the E32's firmware (slow_correction): True (E32 1.4.6): more than 10 min either way moves the next
    start a little, at most a quarter of an hour a morning; False (older): more than 10 min late, more than 15 min
    early, with the numbers where it tells them; None (version unknown): the older thresholds, no figure.

    What changes next time follows from this morning alone, with the E32's own thresholds (1.4.5: more than 10 min late:
    earlier; more than 15 min early: later; 1.4.6: more than 10 min either way; not beyond its limits), not from the
    factor, which is the product of every morning so far. A room not warm within 3 hours counts as 3 hours late on the E32: "not warm within 3
    hours after 07:00", never a moment it was not warm.
    """
    t = TEXT[lang]
    arrival = arrival if type(arrival) is dict else {}
    at, error, factor = arrival.get("last_at_utc"), arrival.get("last_error_min"), arrival.get("factor")
    if not _ok(at) or at <= 0 or not _ok(error) or not -1440 <= error <= 1440:
        return None
    day = day or (lambda utc: datetime.fromtimestamp(utc, timezone.utc).date())
    today = today or day(time.time())
    on = day(at)
    if on == today:
        when = t["when_today"]
    elif on == today - timedelta(days=1):
        when = t["when_yesterday"]
    else:
        when = t["when_date"].format(date=f"{on.day} {t['months'].split()[on.month - 1]}")
    minutes = round(error)
    factor = factor if _ok(factor) else None
    earlier, later = _judged(minutes, factor, slow)
    shift = arrival_shift(min(minutes, NOT_WARM_MIN), start, at, slow) if earlier or later else None
    n = whole_minutes(shift, lang) if shift is not None else None
    suffix = "_slow" if slow is True else ""
    meaning = t["arrival_mean" + suffix]
    if minutes >= NOT_WARM_MIN:
        key = (("arrival_not_warm_earlier_min" if n else "arrival_not_warm_earlier" + suffix) if earlier
               else "arrival_not_warm")
        return t[key].format(when=when, time=clock(at), n=n), meaning
    how = (t["how_late"].format(d=whole_minutes(minutes, lang)) if minutes > 0
           else t["how_early"].format(d=whole_minutes(-minutes, lang)) if minutes < 0 else t["how_on_time"])
    key = "arrival_earlier" if earlier else "arrival_later" if later else "arrival"
    key += "_min" if n and key != "arrival" else suffix if key != "arrival" else ""
    # The moment the room was warm: the switch time plus the error (the E32's Home page shows the same moment).
    return t[key].format(when=when, time=clock(at + minutes * 60), how=how, n=n), meaning


# -- 1.4.6 (HA-LEARN-TEXTS part B): what the E32's lead guard says about the room's warm-up time ---------------------------
LEAD_STATES = ("collecting", "checking", "learned", "held")   # LearnGuard::State, as the E32 names them
LEAD_REASONS = ("evidence", "step", "range")                   # LearnGuard::Reason of a held lead ("outcome" is not used)
LEAD_NEEDED = 5                                                # learnbounds::learnedMornings: mornings that must count
LEAD_SHOWN = 5                                                 # ArrivalLearner::shownMornings


def lead_guard(arrival):
    """The lead guard of the room's ``plan.arrival`` as the E32 reports it, or None: {"state", "reason" (only when held,
    else None), "mornings" (minutes, + late, 180: not warm within 3 h, oldest first), "clean" (same length: true when
    the morning counts)}. E32 1.4.5 and older send no ``state``: None, and every caller then says what it said before
    (decided by the key's presence). A state or reason the E32 does not name here, or arrays that do not belong
    together, are not guessed at: an unknown state is None, unusable mornings are None (an empty list is the E32's own
    "none judged yet"). Computes nothing."""
    if type(arrival) is not dict or arrival.get("state") not in LEAD_STATES:
        return None
    state, reason = arrival["state"], arrival.get("reason")
    mornings, clean = arrival.get("mornings"), arrival.get("clean")
    usable = (type(mornings) is list and type(clean) is list and len(mornings) == len(clean) <= LEAD_SHOWN
              and all(_ok(m) and -1440 <= m <= 1440 for m in mornings) and all(type(c) is bool for c in clean))
    return {"state": state, "reason": reason if state == "held" and reason in LEAD_REASONS else None,
            "mornings": [round(m) for m in mornings] if usable else None,
            "clean": list(clean) if usable else None}


def lead_counted(guard):
    """(how many of the mornings the E32 lists count, how many it lists) of a lead_guard, for "n of its last m"."""
    clean = guard["clean"] or []
    return sum(clean), len(clean)


def lead_sentence(guard, lang):
    """The lead's state in a sentence: collecting (with how many of the listed mornings count), checking, learned, or
    held with its reason. "Learned" only for the state ``learned``."""
    t = TEXT[lang]
    state = guard["state"]
    if state == "collecting":
        counted, listed = lead_counted(guard)
        if counted >= LEAD_NEEDED or guard["clean"] is None:
            return t["lead_collecting_plain"]
        if listed == 0:
            return t["lead_collecting_none"]
        if listed == 1:
            return t["lead_collecting_one" if counted else "lead_collecting_one_not"]
        return t["lead_collecting"].format(n=counted, m=listed)
    if state == "held":
        return t["lead_held_" + guard["reason"]] if guard["reason"] else t["lead_held"]
    return t["lead_" + state]


def lead_mornings_text(guard, lang):
    """"Last mornings, oldest first: 1 h 5 min early, 3 min late (not counted), not warm within 3 hours." or None."""
    t = TEXT[lang]
    words = []
    for minutes, counts in zip(guard["mornings"] or [], guard["clean"] or []):
        what = (t["lead_never"] if minutes >= NOT_WARM_MIN else t["how_late"].format(d=whole_minutes(minutes, lang)) if minutes > 0
                else t["how_early"].format(d=whole_minutes(-minutes, lang)) if minutes < 0 else t["how_on_time"])
        words.append(what if counts else t["lead_not_counted"].format(what=what))
    return t["lead_mornings"].format(list=", ".join(words)) if words else None


def lead_line(guard, lang):
    """(text, meaning) of the lead's state with the last mornings, or None without a guard (E32 1.4.5 and older)."""
    if guard is None:
        return None
    text = lead_sentence(guard, lang)
    mornings = lead_mornings_text(guard, lang)
    return (text + " " + mornings if mornings else text), TEXT[lang]["lead_mean"]


FREE_HEAT_DAYPARTS = 6        # FreeHeat: six local dayparts of 4 hours from midnight
FREE_HEAT_MIN_COUNT = 5       # FreeHeat::rateKPerH: an expected free rise from 5 windows
FREE_HEAT_MIN_RATE = 0.05     # K/h: below about 0.1 °C an hour it is not worth a line


def free_heat(learned, plan=None):
    """(daypart, rate in °C per hour, minutes Smart warm-up starts later) of the room's strongest free heat, or None.

    ``free_heat`` (E32 rc.5, FreeHeat::addJson) of the learned room, else of its plan: {"rate": [6 x °C per hour
    or null], "n": [6 counts], "applied_min": n}. A daypart counts with 5 windows or more, as on the E32.
    """
    part = learned.get("free_heat") if type(learned) is dict else None
    if type(part) is not dict:
        part = plan.get("free_heat") if type(plan) is dict else None
    if type(part) is not dict:
        return None
    rates, counts = part.get("rate"), part.get("n")
    if (type(rates) is not list or type(counts) is not list or len(rates) != FREE_HEAT_DAYPARTS
            or len(counts) != FREE_HEAT_DAYPARTS):
        return None
    best = None
    for daypart, (rate, count) in enumerate(zip(rates, counts)):
        if (_ok(rate) and FREE_HEAT_MIN_RATE <= rate <= 10 and type(count) is int and count >= FREE_HEAT_MIN_COUNT
                and (best is None or rate > best[1])):
            best = (daypart, rate)
    if best is None:
        return None
    applied = part.get("applied_min")
    return best[0], best[1], applied if type(applied) is int and 0 < applied <= 1440 else 0


def trial_run(status):
    """Whether the E32 heats nothing early: the trial run (mode ``shadow``) or, before the takeover is confirmed,
    active control that waits (``active.state`` ``awaiting_confirmation``), as the house card's driving()."""
    status = status if type(status) is dict else {}
    active = status.get("active") if type(status.get("active")) is dict else {}
    return status.get("mode") == "shadow" or active.get("state") == "awaiting_confirmation"


def free_heat_later(learned, plan=None):
    """The minutes the free heat moves the room's next warm-up later (``free_heat.applied_min`` of the learned room,
    else of its plan; FreeHeat::shorten), 0 without."""
    for item in (learned, plan):
        part = item.get("free_heat") if type(item) is dict else None
        if type(part) is dict:
            applied = part.get("applied_min")
            return applied if type(applied) is int and 0 < applied <= 1440 else 0
    return 0


def free_heat_line(learned, plan, lang, smart=None, after_start=False):
    """(text, meaning) on the heat the room gets for free (sun, cooking, people), or None.

    smart: the Smart warm-up option (False: off, so no warm-up starts later, whatever the E32 counts);
    after_start: the line follows the Smart warm-up line that already names the later start ("So the warm-up starts
    20 min later than without the free heat.").
    """
    found = free_heat(learned, plan)
    if found is None:
        return None
    t, (daypart, rate, applied) = TEXT[lang], found
    text = t["free_heat"].format(when=t[f"daypart.{daypart}"], rate=number(rate, lang, 1))
    if not applied or smart is False:
        return text, t["free_heat_mean"]
    return text, t["free_heat_later" if after_start else "free_heat_applied"].format(m=applied)


def free_heat_lines(rooms, lang, smart=None):
    """[{name, text, meaning}] of the rooms with free heat (free_heat_line), in order; rooms: [(name, learned, plan)]."""
    return [{"name": name, "text": found[0], "meaning": found[1]} for name, learned, plan in rooms
            if (found := free_heat_line(learned, plan, lang, smart)) is not None]


# The comfort modes that hold the week program on the E32: no early warm-up towards its next rise
# (RoomOverrides::holdsProgram, HeatingController::applyFlowPolicy). 1.4.1: also summer mode.
HELD_MODES = ("away", "presence_away", "window_open", "summer")
CURRENCY_SIGNS = {"EUR": "€", "GBP": "£", "USD": "$", "PLN": "zł"}
NIGHT_HOURS = range(3, 12)  # a step up between 03:00 and 12:00 ends a night setback


def money(value, lang, currency=None):
    """An amount with exactly two decimals in Home Assistant's currency: "€0.15", "€ 0,15" (Dutch), "0.15 zł"."""
    amount = f"{float(value):.2f}"
    amount = amount.replace(".", ",") if lang != "en" else amount
    if not currency:
        return amount
    sign = CURRENCY_SIGNS.get(currency, currency)
    if sign not in ("€", "£", "$"):
        return f"{amount} {sign}"
    return f"{sign} {amount}" if lang == "nl" else f"{sign}{amount}"


MODEL_STATES = ("collecting", "checking", "trusted", "demoted")
MODEL_EMITTERS = ("floor", "radiator", "mixed")


def room_model(learned):
    """The room's model (``model`` of fw/telemetry/learned/<id>, 1.1.1 stage B, control/RoomModels.h), checked, or None
    on firmware without it. Each figure is None while the E32 does not know it (it leaves the key out then)."""
    model = learned.get("model") if type(learned) is dict else None
    if type(model) is not dict or model.get("state") not in MODEL_STATES:
        return None

    def figure(key, low, high):
        value = model.get(key)
        return value if _ok(value) and low <= value <= high else None
    good, need = figure("good_days", 0, 365), figure("of", 1, 365)
    emitter = model.get("type") if model.get("type") in MODEL_EMITTERS else None
    return {"state": model["state"], "good_days": int(good) if good is not None else None,
            "of": int(need) if need is not None else None,
            "why": model["why"] if type(model.get("why")) is str and len(model["why"]) <= 24 else None,
            "error_3h_c": figure("err_3h", 0, 20), "error_6h_c": figure("err_6h", 0, 20),
            "emitter": emitter, "emitter_from": model.get("type_from") if model.get("type_from") == "floor_rejected" else None,
            "heat_loss_kw_per_c": figure("ua", 0, 5), "time_constant_h": figure("tau_h", 0, 2000),
            "lag_min": figure("lag_min", 0, 600), "hours_per_degree": figure("h_per_k", 0, 200),
            "resting": model.get("resting") is True}


def model_line(name, learned, lang, planning=False):
    """(text, meaning) on how far the E32 is with its model of the room, or None (firmware without the models)."""
    model = room_model(learned)
    if model is None:
        return None
    t = TEXT[lang]
    state = model["state"]
    meaning = t["model_mean_planning" if planning and state == "trusted" else "model_mean"]
    if state == "trusted":
        if model["heat_loss_kw_per_c"] is None:
            return t["model.trusted_bare"].format(room=name), meaning
        values = {"room": name, "ua": number(model["heat_loss_kw_per_c"], lang, 2)}
        if model["hours_per_degree"] is not None:
            return t["model.trusted"].format(h=number(model["hours_per_degree"], lang, 1), **values), meaning
        return t["model.trusted_plain"].format(**values), meaning
    if state in ("checking", "demoted"):
        n, m = model["good_days"], model["of"]
        if n is None or m is None:
            return t["model.collecting"].format(room=name), meaning
        return t["model." + state].format(room=name, n=n, m=m), meaning
    return t["model.collecting"].format(room=name), meaning


def room_overview(name, learned, plan, lang, clock, smart=None, day=None, today=None, room_id=None, comfort=None,
                  trial=False, currency=None, now=None, planning=False, room_off=False, advice=None, slow=False):
    """{name, room_id, progress, summary, lines: [{text, meaning}], facts} of one room that is on; clock: utc -> "07:10"
    in local time.

    day: utc -> the local date, today: the local date now (for "Yesterday warm at 09:12", arrival_line).
    comfort: the room's ``comfort`` (its mode: away or an open window holds the program, so no Smart warm-up line);
    trial: the trial run; currency: Home Assistant's (the night advice's money); summary: once learned, how fast it
    warms in a few words (the Learning tab's progress list); planning: the E32 plans the heating (heating_plan.py);
    model: the model line's text (None on firmware without the room models).
    advice: the room's heat-along advice (room_advice.learning_lines, the heating advice sensor's ``rooms``) or None.
    slow: which rule the E32 follows for a judged morning (slow_correction of its firmware version; arrival_line).
    facts (1.4.3, CONTRACT-1.4.3 §3): the same figures as the lines, structured for the Learning view's room card,
    each from the input its line uses; a fact not learned yet is in ``waiting`` with what it needs (finish_facts).
    """
    t = TEXT[lang]
    learned = learned if type(learned) is dict else {}
    facts, heat_along = new_facts(learned), advice  # ``advice`` is the E32's learned advice below
    ready = learned.get("readiness") == "ready"
    seen = min(WARMUPS_TO_LEARN, learned["segments"]) if _ok(learned.get("segments")) else 0
    lines = []
    model = model_line(name, learned, lang, planning)
    if model is not None:  # 1.1.1 stage B: what the E32's model of the room says first
        lines.append(_line(*model))
    if not ready and learned.get("readiness_timing") == "ready":  # E32 rc.4: the warm-up time from one water temperature
        lines.append(_line(t["timing_learned"], t["timing_learned_mean"]))
    elif not ready:
        lines.append(_line(t["learning_more" if seen >= WARMUPS_TO_LEARN else "learning_first"], t["learning_mean"]))
    advice = next((a for a in learned.get("advice") or [] if type(a) is dict and a.get("shortfall_c") == 1), None)
    summary = None
    if ready and advice and _ok(advice.get("rule_warmup_h")) and _ok(advice.get("rule_flow_c")):
        values = {"d": duration(advice["rule_warmup_h"] * 60, lang), "flow": number(advice["rule_flow_c"], lang, 0)}
        lines.append(_line(t["warms"].format(**values), t["warms_mean"]))
        summary = t["learned_warms"].format(**values)
        facts["warmup"] = {"hours": round(advice["rule_warmup_h"], 2), "flow_c": round(advice["rule_flow_c"])}
    if ready and advice and _ok(advice.get("flow_c")) and advice.get("reason") in ("learned", "lowest_learned"):
        lines.append(_line(t["lowest"].format(flow=number(advice["flow_c"], lang, 0)), t["lowest_mean"]))
        facts["lowest_flow_c"] = round(advice["flow_c"])
    # A loss that rounds to 0 °C per hour ("loses about 0 °C") says nothing: left out.
    if (rate := cooling_rate(learned)) is not None:
        lines.append(_line(t["cools"].format(rate=number(rate, lang, 2), out=REFERENCE_OUTDOOR_C), t["cools_mean"]))
        facts["cooling"] = {"c_per_h": round(rate, 2), "outdoor_c": REFERENCE_OUTDOOR_C}
    plan = plan if type(plan) is dict else {}
    start = plan.get("optimum_start") if type(plan.get("optimum_start")) is dict else {}
    comfort = comfort if type(comfort) is dict else {}
    held = comfort.get("mode") in HELD_MODES or comfort.get("window") == "open"
    later = free_heat_later(learned, plan)
    warm = None if held else smart_warm_up_line(start, smart, lang, clock, trial, later, now, room_off)
    facts["smart_start"] = smart_start_fact(start, smart, clock, trial, later, now, room_off,
                                            comfort.get("mode") if comfort.get("mode") in HELD_MODES
                                            else "window_open" if held else None)
    if warm is not None:
        lines.append(_line(*warm))
    elif not held and start.get("reason") == "planned" and _ok(start.get("predicted_start_utc")):
        # firmware before rc.2: no next switch
        lines.append(_line(t["start_only"].format(start=clock(start["predicted_start_utc"])), t["start_mean"]))
    # E32 rc.5: sun, cooking and people, after the Smart warm-up line, which names the later start it gives.
    if (free := free_heat_line(learned, plan, lang, False if held else smart, warm is not None)) is not None:
        lines.append(_line(*free))
    if (found := free_heat(learned, plan)) is not None:
        facts["free_heat"] = {"c_per_h": round(found[1], 1), "part": DAYPARTS[found[0]],
                              "later_min": found[2] if found[2] and smart is not False and not held else 0}
    if (arrived := arrival_line(plan.get("arrival"), lang, clock, day, today, start, slow)) is not None:
        lines.append(_line(*arrived))
        facts["arrival"] = arrival_fact(plan.get("arrival"), clock, day, today, start, slow)
    # 1.4.6: what the E32's lead guard says (collecting / checking / learned / held), never from Home Assistant's own count
    facts["lead"] = lead_guard(plan.get("arrival"))
    if (guarded := lead_line(facts["lead"], lang)) is not None:
        lines.append(_line(*guarded))
    night = plan.get("night") if type(plan.get("night")) is dict else {}
    if night.get("reason") == "estimated" and type(night.get("recommended")) is str:
        hold = night["recommended"] not in ("program", "thermostat_like") and _ok(night.get("recommended_night_c"))
        m3 = number(night["saving_m3"] if _ok(night.get("saving_m3")) else 0, lang, 2)
        # The advice is for the setback before the next step up: "at night" only when that step ends a night.
        switch = start.get("next_switch") if type(start.get("next_switch")) is dict else {}
        rise = clock(switch["utc"]) if _ok(switch.get("utc")) else None
        nightly = rise is None or not rise[:2].isdigit() or int(rise[:2]) in NIGHT_HOURS
        once = "" if nightly else "_once"
        saving = (t["saving_eur" + once].format(m3=m3, eur=money(night["saving_eur"], lang, currency))
                  if _ok(night.get("saving_eur")) and night["saving_eur"] > 0 else t["saving" + once].format(m3=m3))
        if hold:
            text = t["night_hold" if nightly else "night_hold_until"].format(
                night=number(night["recommended_night_c"], lang), saving=saving, time=rise)
        else:
            text = t["night_program" if nightly else "night_program_until"].format(time=rise)
        lines.append(_line(text, t["night_mean"]))
        facts["advice"] = {"text": text, "meaning": t["night_mean"], "kind": "night"}
    # "6 of 6" read as finished while the E32 still waits for other days or a second water temperature
    # (FlowLearner readiness: 6 warm-ups in 3 heating periods and 2 water temperatures): then say what is missing.
    if ready:
        progress = t["learned"]
    elif learned.get("readiness_timing") == "ready":
        progress = t["learning_timing"]
    elif seen >= WARMUPS_TO_LEARN:
        progress = t["learning_seen"].format(n=learned["segments"])
    else:
        progress = t["learning"].format(n=seen, m=WARMUPS_TO_LEARN)
    facts["status"] = "ready" if ready else "timing" if learned.get("readiness_timing") == "ready" else "learning"
    if facts["advice"] is None:
        facts["advice"] = advice_fact(heat_along)
    finish_facts(facts, heat_along, lang)
    return {"name": name, "room_id": room_id, "progress": progress, "summary": summary, "lines": lines,
            "model": model[0] if model is not None else None, "facts": facts}


# -- 1.4.3 (LEARN-TAB): a room's facts for the Learning view's room card (CONTRACT-1.4.3 §3) --------------------------
DAYPARTS = ("night", "early_morning", "morning", "afternoon", "evening", "late_evening")  # FreeHeat's six of 4 hours
# room_advice's kind -> what the advice is about: an On room's (what Heat along only would change), a heat-along room's
# (up to which temperature it heats along for free, a fixed temperature).
ADVICE_KINDS = {"active": "follow", "follow": "fixed"}


def cooling_rate(learned):
    """How fast the room cools at 5 °C outside (°C per hour) from the E32's heat-loss rate, or None (unknown, or so
    small that it would read "0 °C per hour")."""
    loss = learned.get("loss_per_h") if type(learned) is dict else None
    if not _ok(loss):
        return None
    rate = loss * (REFERENCE_ROOM_C - REFERENCE_OUTDOOR_C)
    return rate if rate >= 0.01 else None


def new_facts(learned, status=None):
    """A room's facts before anything is filled in: the progress of its warm-ups (FlowLearner) and its model."""
    learned = learned if type(learned) is dict else {}
    segments, periods = learned.get("segments"), learned.get("periods")
    seen = min(WARMUPS_TO_LEARN, segments) if type(segments) is int and segments >= 0 else 0
    model = room_model(learned)
    return {"status": status, "progress": {"seen": seen, "of": WARMUPS_TO_LEARN,
                                           "periods": periods if type(periods) is int and periods >= 0 else None},
            "warmup": None, "cooling": None, "lowest_flow_c": None, "free_heat": None, "smart_start": None,
            "arrival": None, "lead": None, "model": {key: model[key] for key in ("state", "good_days", "of")} if model else None,
            "advice": None, "reach": None, "waiting": {}}


def smart_start_fact(start, on, clock, trial=False, later_min=0, now=None, room_off=False, held=None):
    """Smart warm-up's start for the room's next step up, read as smart_warm_up_line reads it: {"at", "target_c",
    "target_at", "estimate", "held_reason", "now"}, or None without a planned start. held_reason: why it starts no
    earlier than the program: the comfort mode that holds the program or "window_open", "off" (Smart warm-up off),
    "room_off" (off for this room), "learning" (not learned yet: heating starts at the program time, the start is an
    estimate), "not_needed" (warm enough already), "trial" (the trial run: it would start then),
    else None; now: heating for it now; estimate: not learned yet, or from the standard warm-up time."""
    start = start if type(start) is dict else {}
    switch = start.get("next_switch") if type(start.get("next_switch")) is dict else {}
    if (start.get("reason") != "planned" or not _ok(start.get("predicted_start_utc"))
            or not _ok(switch.get("utc")) or not _ok(switch.get("target_c"))):
        return None
    shift = later_min * 60 if type(later_min) is int and later_min > 0 and on is not False else 0
    begin = start["predicted_start_utc"] + shift
    applies = start["applies"] if type(start.get("applies")) is bool else start.get("confidence") == "learned"
    heating = start.get("start_now") is True and (not shift or begin <= (time.time() if now is None else now))
    reason = (held or ("room_off" if on is False and room_off else "off" if on is False else None)
              or ("learning" if not applies else None)
              or ("not_needed" if start.get("lead_minutes") == 0 and start.get("start_now") is not True else None)
              or ("trial" if trial else None))
    return {"at": clock(begin), "target_c": switch["target_c"], "target_at": clock(switch["utc"]),
            "estimate": not applies or start.get("estimate") is True, "held_reason": reason,
            "now": bool(heating) and reason is None}


def arrival_fact(arrival, clock, day=None, today=None, start=None, slow=False):
    """The last judged morning, read as arrival_line reads it: {"at": when the room was warm (the switch time when it
    was not warm within 3 hours), "minutes_late" (negative: early; 180: not warm within 3 hours), "day": "today",
    "yesterday" or the local date (YYYY-MM-DD), "next": "earlier" | "later" | None, "next_min": about how many minutes,
    or None; "next_slow": True only with an E32 1.4.6, which moves the start at most a quarter of an hour a morning}.
    Only called once arrival_line has a line."""
    at, error, factor = arrival.get("last_at_utc"), arrival.get("last_error_min"), arrival.get("factor")
    day = day or (lambda utc: datetime.fromtimestamp(utc, timezone.utc).date())
    today = today or day(time.time())
    on, minutes = day(at), round(error)
    factor = factor if _ok(factor) else None
    earlier, later = _judged(minutes, factor, slow)
    late = min(minutes, NOT_WARM_MIN)
    return {"at": clock(at if late >= NOT_WARM_MIN else at + minutes * 60), "minutes_late": late,
            "day": "today" if on == today else "yesterday" if on == today - timedelta(days=1) else on.isoformat(),
            "next": "earlier" if earlier else "later" if later else None,
            "next_min": arrival_shift(late, start, at, slow) if earlier or later else None,
            # E32 1.4.6: no figure, only the bound ("at most a quarter of an hour a morning")
            **({"next_slow": True} if slow is True and (earlier or later) else {})}


def advice_fact(advice):
    """The room's heat-along advice (room_advice, 1.4.2) once it has a figure: {"text", "meaning": None, "kind"}
    (ADVICE_KINDS), else None; while it still counts days its sentence is in ``waiting`` (finish_facts)."""
    if type(advice) is not dict or not advice.get("advice") or advice.get("advice_reason") is not None:
        return None
    kind = ADVICE_KINDS.get(advice.get("advice_kind"))
    return {"text": advice["advice"], "meaning": None, "kind": kind} if kind else None


def reach_fact(advice):
    """1.4.4 (plan 2.4): how often a room on Heat along only reached its temperature by heating along, from the room's
    heat-along line (room_advice.reach): {"c", "pct" (None while counting), "days", "of": 14}, or None without one
    (a room with a week program, the valve's own sensor, Home Assistant before 1.4.4 wrote the line)."""
    if type(advice) is not dict or not _ok(advice.get("reach_c")) or type(advice.get("reach_days")) is not int:
        return None
    pct = advice.get("reach_pct")
    from .room_advice import ADVICE_DAYS
    return {"c": advice["reach_c"], "pct": pct if type(pct) is int and 0 <= pct <= 100 else None,
            "days": max(0, min(advice["reach_days"], ADVICE_DAYS)), "of": ADVICE_DAYS}


def finish_facts(facts, advice, lang):
    """``waiting``: what each fact not learned yet still needs, in the unit of its learning, never a number for the
    fact itself; the cooling from the room's own model (room_advice) where the E32 has none."""
    t, waiting, status = TEXT[lang], facts["waiting"], facts["status"]
    cool = advice.get("cool_c_per_h") if type(advice) is dict else None
    if facts["cooling"] is None and _ok(cool) and cool >= 0.01:
        facts["cooling"] = {"c_per_h": round(cool, 2), "outdoor_c": REFERENCE_OUTDOOR_C}
    if facts["cooling"] is None:
        waiting["cooling"] = t["wait.cooling"]
    if type(advice) is dict and advice.get("advice") and advice.get("advice_reason") is not None:
        waiting["advice"] = advice["advice"]  # "Too little data yet ... So far 3 of the 14 days."
    if status in ("follow", "off"):
        return
    seen = facts["progress"]["seen"]
    if facts["warmup"] is None:
        waiting["warmup"] = (t["wait.timing"] if status == "timing" else t["wait.other_days"] if seen >= WARMUPS_TO_LEARN
                             else t["wait.warmup"] if WARMUPS_TO_LEARN - seen == 1
                             else t["wait.warmups"].format(n=WARMUPS_TO_LEARN - seen))
    if facts["lowest_flow_c"] is None:
        waiting["lowest_flow_c"] = (t["wait.not_found"] if status == "ready" else t["wait.other_water"]
                                    if status == "timing" else t["wait.after_warmup"])
    if facts["free_heat"] is None:
        waiting["free_heat"] = t["wait.free_heat"]


def idle_room_overview(name, room_id, state, learned, lang, advice=None):
    """A room that learns no warm-up now (Off, or Heat along only: E32 1.3): no lines; its facts with what still holds
    on Heat along only (how fast it cools, the heat-along advice); an Off room only its status."""
    t = TEXT[lang]
    follow = state == "follow"
    facts = new_facts(learned, "follow" if follow else "off")
    if follow:
        if (rate := cooling_rate(learned)) is not None:
            facts["cooling"] = {"c_per_h": round(rate, 2), "outdoor_c": REFERENCE_OUTDOOR_C}
        facts["advice"] = advice_fact(advice)
        facts["reach"] = reach_fact(advice)
        finish_facts(facts, advice, lang)
    return {"name": name, "room_id": room_id, "progress": t["room_follow" if follow else "room_off"],
            "summary": None, "lines": [], "model": None, "facts": facts}


def boiler_minimum_flow(summary):
    """The lowest water temperature the boiler fires at for heating (°C), as the E32 learned it, or None.

    ``learned.boiler_minimum_flow_c`` of the summary (FlowLearner, E32 rc.2): only there once learned
    above the plan's minimum; older firmware never sends it. A value outside 20..90 °C is not shown.
    """
    learned = summary.get("learned") if type(summary) is dict and type(summary.get("learned")) is dict else {}
    value = learned.get("boiler_minimum_flow_c")
    return value if _ok(value) and 20 <= value <= 90 else None


def steady_burn(summary):
    """The boiler's learned steady-burn floor (``boiler.steady`` of fw/telemetry/flow, E32 SL-A, control/SteadyBurn.h),
    checked, or None on firmware without it.

    {"floor_c": the lowest water temperature at which the boiler keeps burning for the rooms' highest target (None
    while not learned), "applied": whether the E32 asks at least that (Smart warm-up on, the E32 driving the boiler),
    "least_pct": the boiler's least output (p10 of its burns), "cycling": self-cycling seen in an E32 request,
    "points": up to three [{"flow_c", "stops_per_hour", "hours_asked"}] of its starts table (the lowest and highest
    band with evidence and the floor's band), E32 1.3: "trying_c": the water temperature of the daily probe one band
    lower while it runs (else None) and "step": the last probe of the last 14 days, {"days_ago", "from_c", "to_c",
    "result": "kept" | "cycling" | "cool"} (else None)}.
    """
    boiler = summary.get("boiler") if type(summary) is dict else None
    steady = boiler.get("steady") if type(boiler) is dict else None
    if type(steady) is not dict:
        return None
    floor, least = steady.get("floor_c"), steady.get("least_pct")
    points = []
    for point in steady.get("points") if type(steady.get("points")) is list else []:
        if (type(point) is list and len(point) == 3 and all(_ok(v) for v in point) and 10 <= point[0] <= 90
                and 0 <= point[1] <= 600 and 0 <= point[2] <= 1e5):
            points.append({"flow_c": point[0], "stops_per_hour": point[1], "hours_asked": point[2]})
    floor = floor if _ok(floor) and 20 <= floor <= 90 else None
    trying, step = steady.get("trying_c"), steady.get("step")
    if (type(step) is list and len(step) == 4 and all(_ok(v) for v in step[:3]) and 0 <= step[0] < 14
            and 20 <= step[2] < step[1] <= 90 and step[3] in ("kept", "cycling", "cool")):
        step = {"days_ago": int(step[0]), "from_c": step[1], "to_c": step[2], "result": step[3]}
    else:
        step = None
    return {"floor_c": floor, "applied": steady.get("applied") is True and floor is not None,
            "least_pct": least if _ok(least) and 0 <= least <= 100 else None,
            "cycling": steady.get("cycling") is True, "points": points[:3],
            "trying_c": trying if _ok(trying) and 20 <= trying <= 90 else None, "step": step}


def steady_probe_line(steady, lang):
    """E32 1.3: the steady-burn floor's daily probe one band lower in the E32 page's words (house.html
    steadyProbe), or None: while it runs, else the last one of the last 14 days ("yesterday", "last week")."""
    t = TEXT.get(lang, TEXT["en"])
    if steady is None or steady["floor_c"] is None:
        return None
    if steady["trying_c"] is not None:
        return t["steady_trying"].format(to=number(steady["trying_c"], lang, 0))
    step = steady["step"]
    if step is None:
        return None
    days = step["days_ago"]
    when = (t["steady_today"] if days == 0 else t["steady_yesterday"] if days == 1
            else t["steady_days"].format(n=days) if days < 7 else t["steady_last_week"])
    return t["steady_" + step["result"]].format(when=when, d=number(step["from_c"] - step["to_c"], lang, 0),
                                                to=number(step["to_c"], lang, 0), from_c=number(step["from_c"], lang, 0))


CURVE_STEPS = 6  # CurveLearner::Params::minWindows: steady 3-hour periods before the learned curve is used


def curve_status(curve, on, lang):
    """(text, meaning) for what the heating curve uses now (E32 rc.3, on by default), or None.

    ``curve``: the summary's ``flow.curve`` (state, slope_source, windows); ``on``: the stored option
    ``weather_curve`` (None: not known, on by default).
    """
    t = TEXT[lang]
    if type(curve) is not dict or curve.get("state") in (None, "no_room"):
        return None
    if on is False:
        return t["curve_status_off"], t["curve_off"]
    if curve.get("state") == "no_outdoor":
        return t["curve_status_no_outdoor"], t["curve_status_mean"]
    if curve.get("slope_source") == "learned":
        return t["curve_status_learned"], t["curve_status_mean"]
    # E32 rc.5: until 6 steady periods, the slope the house model works out (HouseModel), else the standard one.
    key = "curve_status_house" if curve.get("slope_source") == "house" else "curve_status_learning"
    windows = curve.get("windows")
    if type(windows) is int and 0 <= windows < CURVE_STEPS:  # never "6 of 6" while it does not use the learned line
        return t[key].format(n=windows, m=CURVE_STEPS), t["curve_status_mean"]
    return t[key + "_plain"], t["curve_status_mean"]


def learned_flow_status(learned, smart, lang):
    """(text, meaning) for the learned coolest water (the summary's ``flow.learned``), or None."""
    t = TEXT[lang]
    state = learned.get("state") if type(learned) is dict else None
    # "held" (E32 rc.5): the boiler's own ceiling binds; the boiler sentence (insight.py) says so.
    if type(state) is not str or state in ("no_room", "held"):
        return None
    if state == "not_ready":
        return t["flow_status_collecting"], t["flow_status_mean"]
    return t["flow_status_advice" if smart is False else "flow_status_ready"], t["flow_status_mean"]


def house_overview(summary, lang, options=None):
    """[{text, meaning}] for the heating curve, the burner and the boiler's learned minimum flow, from the summary.

    ``options``: the E32's stored flow options when known (weather_curve, apply_learned).
    """
    t, lines = TEXT[lang], []
    summary = summary if type(summary) is dict else {}
    options = options if type(options) is dict else {}
    flow = summary.get("flow") if type(summary.get("flow")) is dict else {}
    curve = flow.get("curve") if type(flow.get("curve")) is dict else None
    status = curve_status(curve, options.get("weather_curve"), lang)
    slope = number(curve["slope"], lang, 2) if curve is not None and _ok(curve.get("slope")) else None
    # Weather compensation once: what it uses now and, while it is on, how steep its line is, in one line
    # ("Weather compensation: learned for your house. The water gets about 0.85 °C warmer ...").
    on = options.get("weather_curve") is not False and curve is not None and curve.get("state") != "no_outdoor"
    if status is not None and slope is not None and on:
        lines.append(_line(status[0] + " " + t["curve_slope"].format(s=slope),
                           t["curve_on" if curve.get("state") == "applied" else "curve_off"]))
    elif status is not None:
        lines.append(_line(*status))
    elif slope is not None:
        source = curve.get("slope_source")
        key = "curve_learned" if source == "learned" else "curve_house" if source == "house" else "curve"
        lines.append(_line(t[key].format(s=slope), t["curve_on" if curve.get("state") == "applied" else "curve_off"]))
    if (learned := learned_flow_status(flow.get("learned"), options.get("apply_learned"), lang)) is not None:
        lines.append(_line(*learned))
    tuning = summary.get("tuning") if type(summary.get("tuning")) is dict else {}
    yesterday = tuning.get("yesterday") if type(tuning.get("yesterday")) is dict else None
    if yesterday and _ok(yesterday.get("starts")):
        starts, hours = yesterday["starts"], yesterday.get("heating_h") if _ok(yesterday.get("heating_h")) else 0
        one = "_one" if starts == 1 else ""  # "started once", not "1 times"; none: "did not start"
        text = (t["burner_none"] if starts == 0
                else t["burner" + one].format(n=starts, d=duration(yesterday["burn_s"] / 60, lang))
                if _ok(yesterday.get("burns")) and yesterday["burns"] > 0 and _ok(yesterday.get("burn_s"))
                else t["burner_starts" + one].format(n=starts))
        lines.append(_line(text, t["burner_often" if hours > 0 and starts > 3 * hours else "burner_mean"]))
    lowest = boiler_minimum_flow(summary)
    if lowest is not None:
        lines.append(_line(t["boiler_minimum"].format(flow=number(lowest, lang, 0)), t["boiler_minimum_mean"]))
    # E32 SL-A: the learned steady-burn floor, in the E32 page's words (house.html, "House and boiler").
    steady = steady_burn(summary)
    if steady is not None and steady["floor_c"] is not None:
        lines.append(_line(t["steady" if steady["applied"] else "steady_off"].format(flow=number(steady["floor_c"], lang, 0)),
                           t["steady_mean"]))
        probe = steady_probe_line(steady, lang)  # E32 1.3: the floor learns downwards
        if probe:
            lines.append(_line(probe, None))
    # Plan item 1: automatic or set by you, with the value in effect (firmware before it: no line).
    from .e32_room_flow import minimum_flow_now
    if (minimum := minimum_flow_now(summary)) is not None:
        key = "minimum_auto" if minimum[2] else "minimum_own"
        lines.append(_line(t[key].format(flow=number(minimum[0], lang, 0)), t[key + "_mean"]))
    return lines or [_line(t["house_none"], None)]


def local_clock(hass):
    """utc -> "07:10" in Home Assistant's time zone."""
    from homeassistant.util import dt as dt_util
    return lambda utc: dt_util.as_local(datetime.fromtimestamp(utc, timezone.utc)).strftime("%H:%M")


def local_day(hass):
    """(utc -> the local date, today's local date) in Home Assistant's time zone."""
    from homeassistant.util import dt as dt_util
    return lambda utc: dt_util.as_local(datetime.fromtimestamp(utc, timezone.utc)).date(), dt_util.now().date()


class LearnedStoredData(ExtraStoredData):
    def __init__(self, data):
        self.data = data

    def as_dict(self):
        return self.data


class LearnedOverviewSensor(RestoreEntity, SensorEntity):
    """What the E32 learned: state = the newest change (or what it does); the overview as attributes."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "learned_overview"
    _attr_icon = "mdi:school-outline"
    # The texts are shown, not kept in the history.
    # steady_burn: its starts table grows every few minutes (the floor and the least output are recorded).
    _unrecorded_attributes = frozenset({"rooms", "house", "changes", "settings", "explanation", "insights", "free_heat",
                                        "steady_burn", "latest_changes", "latest_more"})

    def __init__(self, entry, hub, clock=None):
        self.entry, self.hub = entry, hub
        self._clock = clock
        self._attr_unique_id = f"{hub.prefix}_hub_learned_overview"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, hub.prefix)})
        self.log = []

    def _lang(self):
        return language(getattr(self, "hass", None))

    def _tuning(self):
        summary = self.hub.summary if type(self.hub.summary) is dict else {}
        return summary.get("tuning") if type(summary.get("tuning")) is dict else None

    def _flow_options(self):
        """The E32's flow options as last read (e32_flow.py), or None."""
        from .e32_flow import KEY
        data = getattr(getattr(self, "hass", None), "data", None)
        link = data.get(DOMAIN, {}).get(self.entry.entry_id, {}).get(KEY) if isinstance(data, dict) else None
        return getattr(link, "settings", None)

    def _advice_lines(self):
        """{room id: the heat-along line of the room} as the heating advice sensor last wrote it (its ``rooms``,
        room_advice.learning_lines, in Home Assistant's language), {} without one: read, never worked out again."""
        hass = getattr(self, "hass", None)
        data = getattr(hass, "data", None)
        sensor = data.get(DOMAIN, {}).get(self.entry.entry_id, {}).get("heating_advice") if isinstance(data, dict) else None
        entity_id = getattr(sensor, "entity_id", None)
        states = getattr(hass, "states", None)
        st = states.get(entity_id) if entity_id and states is not None and hasattr(states, "get") else None
        lines = st.attributes.get("rooms") if st is not None else None
        return {line["room_id"]: line for line in lines if type(line) is dict and type(line.get("room_id")) is str} \
            if type(lines) is list else {}

    def _names(self):
        """The rooms by the name the dashboard shows (renamed in Home Assistant or not; insight.room_names)."""
        from .insight import room_names
        return room_names(self.hub, getattr(self, "hass", None), getattr(self.entry, "entry_id", None))

    @callback
    def _hub_changed(self):
        tuning = self._tuning()
        merged = merge_changes(self.log, tuning.get("log") or []) if tuning else self.log
        if merged != self.log:
            self.log = merged
        if getattr(self, "hass", None) is not None and self.entity_id:
            self.async_write_ha_state()

    @property
    def available(self):
        return self.hub.fresh or bool(self.log)

    @property
    def native_value(self):
        lang, tuning = self._lang(), self._tuning()
        names = self._names()
        for change in self.log:
            text = change_text(change[1:], names, lang)
            if text:
                return text[:STATE_MAX]
        state = tuning.get("state") if tuning else None
        return TEXT[lang].get("state." + state, TEXT[lang]["state.none"])[:STATE_MAX] if state else TEXT[lang]["unavailable"][:STATE_MAX]

    @property
    def extra_state_attributes(self):
        lang, tuning = self._lang(), self._tuning() or {}
        t, names = TEXT[lang], self._names()
        clock = self._clock or (local_clock(self.hass) if getattr(self, "hass", None) is not None else (lambda utc: time.strftime("%H:%M", time.gmtime(utc))))
        changes = []
        # The trial run's proposals first, without a time ("Would set ..."): never the dashboard's "Latest change".
        for proposal in tuning.get("would") or []:
            text = change_text(proposal, names, lang, proposal=True)
            if text:
                changes.append({"time": None, "text": text})
        for change in self.log:
            text = change_text(change[1:], names, lang)
            if text:
                changes.append({"time": datetime.fromtimestamp(change[0], timezone.utc).isoformat(timespec="seconds"), "text": text})
        newest, more = newest_evaluation(self.log, tuning)
        latest = [text for text in (change_text(change[1:], names, lang) for change in newest) if text]
        from .e32_flow import smart_warm_up
        smart = smart_warm_up(self.hass, self.entry.entry_id) if getattr(self, "hass", None) is not None else None
        day, today = local_day(self.hass) if getattr(self, "hass", None) is not None and self._clock is None else (None, None)
        # E32 1.3: a room on Heat along only ("follow") learns no warm-up and gets none: no lines, as a room that is off;
        # 1.4.3: both are in ``rooms`` with their facts (idle_room_overview), for the Learning view's room cards.
        active = [(room_id, name) for room_id, name in names.items()
                  if self.hub.rooms[room_id].get("state") not in ("inactive", "follow")]
        advice = self._advice_lines()
        trial = trial_run(self.hub.status)  # the trial run or a takeover not confirmed yet: the E32 heats nothing early
        currency = getattr(getattr(getattr(self, "hass", None), "config", None), "currency", None)
        from .heating_plan import plan_state
        planning = plan_state(self.hub) == "planning"
        # E32 1.4 (#8): each room's own Smart warm-up in effect (room_smart_warm_up), else the house switch.
        on_rooms = dict(active)
        slow = slow_correction(getattr(self.hub, "firmware_version", None))  # 1.4.6: which rule the arrival line explains
        rooms = [room_overview(name, self.hub.learned.get(room_id), self.hub.warmup.get(room_id), lang, clock, on,
                               day, today, room_id, self.hub.rooms[room_id].get("comfort"), trial, currency,
                               planning=planning, room_off=room_off, advice=advice.get(room_id), slow=slow)
                 if room_id in on_rooms else
                 idle_room_overview(name, room_id, self.hub.rooms[room_id].get("state"), self.hub.learned.get(room_id),
                                    lang, advice.get(room_id))
                 for room_id, name in names.items()
                 for on, room_off in (room_smart_warm_up(self.hub.rooms[room_id], smart),)]
        manual = tuning.get("manual") if type(tuning.get("manual")) is list else []
        from .insight import insight_lines  # E32 rc.5: yesterday against the house's own usual days
        attributes = {"explanation": t.get("state." + str(tuning.get("state")), "") if tuning else t["unavailable"],
                      "rooms": rooms, "house": house_overview(self.hub.summary, lang, self._flow_options()),
                      "changes": changes or [{"time": None, "text": t["state.none"]}],
                      "latest_changes": latest, "latest_more": more,
                      "settings": settings(tuning.get("values"), manual, lang),
                      "insights": insight_lines(self.hub.summary, names, lang),
                      "free_heat": free_heat_lines([(name, self.hub.learned.get(room_id), self.hub.warmup.get(room_id))
                                                    for room_id, name in active], lang, smart)}
        lowest = boiler_minimum_flow(self.hub.summary)
        if lowest is not None:  # only once learned
            attributes["boiler_minimum_flow_c"] = lowest
        steady = steady_burn(self.hub.summary)
        if steady is not None:  # E32 SL-A: the steady-burn floor (recorded) and the starts table it comes from
            if steady["floor_c"] is not None:
                attributes["steady_burn_floor_c"] = steady["floor_c"]
            if steady["least_pct"] is not None:
                attributes["boiler_least_output_pct"] = steady["least_pct"]
            attributes["steady_burn"] = {key: steady[key] for key in ("applied", "cycling", "points")}
        return attributes

    @property
    def extra_restore_state_data(self):
        return LearnedStoredData({"log": self.log})

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        stored = await self.async_get_last_extra_data()
        if stored is not None:
            self.log = merge_changes([], (stored.as_dict() or {}).get("log") or [])
        self.async_on_remove(self.hub.add_listener(self._hub_changed))
        self._hub_changed()


async def async_setup_learned_overview(hass, entry, async_add_entities, options, hub):
    """Product entries: the overview sensor on the product device."""
    sensor = LearnedOverviewSensor(entry, hub)
    hass.data[DOMAIN][entry.entry_id]["learned_overview"] = sensor
    async_add_entities([sensor], **options)
