/* The Learning view's room card (OpenThermostat 1.4.3, custom:openthermostat-learning-room; design
   docs/engineering/HA-DASHBOARD-ONTWERP-1.4.3.nl.md 4.2 item 2 and 4.4, CONTRACT-1.4.3 §3).

   One card per room: its name and a label (Learned in green, Learning with how many warm-ups it has seen in amber,
   Heats along, Off), then four facts as tiles, a large number with one short line under it: how fast it warms up and
   with which water, how fast it cools at 5 °C outside, the coolest water that still warms it in time, and the heat it
   gets for free (sun, cooking, people). A fact the E32 has not learned yet is a dotted tile that says what it still
   needs ("2 more warm-ups", "after a night without heating"), never a number. Under the tiles, rows: Smart warm-up's
   start (with "(estimate)" while it is one), "Warm on time, last 7 mornings" as seven dots from the history of the
   room's "Warm on time yesterday" sensor (green on time, amber late or early, an empty ring for a morning without a
   check) with the last morning in words, the room model as a progress bar, and the room's advice with the word
   "Advice" and "Advice only: your week program stays as it is." A room on Heat along only shows its cooling and the
   heat-along advice; a room that is Off one muted sentence.

   Only Home Assistant is read: the learned overview sensor's ``rooms`` entry of this room (its ``facts``, built in
   learned_overview.py from the same inputs as its sentences) and, at most every 5 minutes and when it changes, the last
   8 days of the "Warm on time" sensor (history/history_during_period, as the house card reads its day strip). Nothing
   is polled; nothing talks to the E32. Words: the card's own EN/NL table (the viewer's language); the advice sentences
   come from the sensor in Home Assistant's language. Design tokens of CONTRACT-1.4.1 §8 on the host, "learned" in
   --ot-ok; dark from hass.themes.darkMode, else the browser's scheme; times through Home Assistant's locale (the
   cards' shared clock); Material Design Icons inline. */
const OWN = {
 en: {learned: 'Learned', learning: 'Learning', learning_of: 'Learning · {n} of {m} warm-ups', learning_water: 'Learning · the coolest water',
  heats_along: 'Heats along', off: 'Off',
  warmup_pre: '1 °C in', warmup_caption: 'warming up with water of {flow} °C', warmup_label: 'warming up',
  per_hour: 'per hour', cooling_caption: 'cooling at {out} °C outside', cooling_label: 'cooling',
  lowest_caption: 'coolest water that warms in time', lowest_label: 'coolest water',
  free_caption: 'free heat {part} (sun, cooking, people)', free_label: 'free heat',
  reach_caption: 'reaches {t} °C ({days} days)', reach_title: 'reaches {t} °C {pct} % of the time ({days} days)', reach_label: 'reaches {t} °C',
  reach_counting: 'still counting: day {n} of {m}', reach_counting_plain: 'still counting',
  parts: {night: 'at night', early_morning: 'early in the morning', morning: 'in the morning', afternoon: 'in the afternoon',
   evening: 'in the evening', late_evening: 'late in the evening'},
  wait_warmups: '{n} more warm-ups', wait_warmup: '1 more warm-up', wait_other_days: 'warm-ups on other days',
  wait_timing: 'learned; the water follows', wait_after: 'after the warm-up is learned', wait_other_water: 'warm-ups with other water',
  wait_not_found: 'not found yet', wait_cooling: 'after a night without heating', wait_free: 'not seen yet',
  starts: 'Smart warm-up starts at {at}, so it is {t} °C at {time}', estimate: '(estimate)', learns: 'It learns from every morning.',
  now: 'Smart warm-up is heating now, so it is {t} °C at {time}', still: 'Smart warm-up is still learning: heating starts at {time} for now',
  still_more: 'Estimate: from {at} it would be {t} °C on time.', held: 'No early start: {why}',
  why: {window_open: 'window open', away: 'away', presence_away: 'nobody home', summer: 'summer mode'},
  off_house: 'Smart warm-up is off: heating starts at {time}', off_room: 'Smart warm-up is off for this room: heating starts at {time}',
  not_needed: 'Warm enough for {t} °C at {time}; no early start needed', trial: 'In the trial run it would start at {at}, so it is {t} °C at {time}',
  mornings: 'Warm on time, last 7 mornings', on_time: 'on time', late: '{d} late', early: '{d} early', no_check: 'no check',
  not_warm: 'not warm within 3 h', when_today: 'Today', when_yesterday: 'Yesterday', when_date: 'On {date}',
  arrival: '{when} warm at {at} ({how}).', arrival_never: '{when} not warm within 3 hours after {at}.',
  next_earlier: 'Next time it starts a little earlier.', next_later: 'Next time it starts a little later.',
  next_earlier_min: 'Next time it starts about {n} earlier.', next_later_min: 'Next time it starts about {n} later.',
  model: 'Room model', model_collecting: 'collecting readings', model_checking: 'predictions {n} of {m} days good',
  model_trusted: 'trusted: its predictions hold', model_demoted: 'checking again: {n} of {m} days good',
  advice: 'Advice', advice_only: 'Advice only: your week program stays as it is.',
  off_line: 'Off: the E32 learns nothing here while the room is off.',
  none: 'The E32 has not reported what it learned for this room yet.', min: '{n} min', h: '{h} h', h_m: '{h} h {m} min',
  relearn: 'Learn again', relearn_question: 'Clear what the E32 learned for {name}?', relearn_more: 'It learns again by itself; the week program stays.',
  cancel: 'Cancel', relearn_done: 'Cleared: the E32 starts learning {name} again.', failed: 'That did not work: {reason}'},
 nl: {learned: 'Geleerd', learning: 'Leert nog', learning_of: 'Leert nog · {n} van {m} opwarmingen', learning_water: 'Leert nog · het koelste water',
  heats_along: 'Verwarmt mee', off: 'Uit',
  warmup_pre: '1 °C in', warmup_caption: 'opwarmen met water van {flow} °C', warmup_label: 'opwarmen',
  per_hour: 'per uur', cooling_caption: 'afkoelen bij {out} °C buiten', cooling_label: 'afkoelen',
  lowest_caption: 'koelste water dat op tijd warmt', lowest_label: 'koelste water',
  free_caption: 'gratis warmte {part} (zon, koken, mensen)', free_label: 'gratis warmte',
  reach_caption: 'haalt {t} °C ({days} dagen)', reach_title: 'haalt {t} °C in {pct} % van de tijd ({days} dagen)', reach_label: 'haalt {t} °C',
  reach_counting: 'nog aan het tellen: dag {n} van {m}', reach_counting_plain: 'nog aan het tellen',
  parts: {night: '’s nachts', early_morning: 'vroeg in de ochtend', morning: '’s ochtends', afternoon: '’s middags',
   evening: '’s avonds', late_evening: 'laat op de avond'},
  wait_warmups: 'nog {n} opwarmingen', wait_warmup: 'nog 1 opwarming', wait_other_days: 'opwarmingen op andere dagen',
  wait_timing: 'geleerd; het water volgt', wait_after: 'zodra het opwarmen geleerd is', wait_other_water: 'opwarmingen met ander water',
  wait_not_found: 'nog niet gevonden', wait_cooling: 'na een nacht zonder verwarming', wait_free: 'nog niet gezien',
  starts: 'Slim opwarmen begint om {at}, zodat het om {time} {t} °C is', estimate: '(schatting)', learns: 'Hij leert van elke ochtend.',
  now: 'Slim opwarmen verwarmt nu, zodat het om {time} {t} °C is', still: 'Slim opwarmen leert nog: voorlopig begint verwarmen om {time}',
  still_more: 'Schatting: vanaf {at} zou het op tijd {t} °C zijn.', held: 'Geen vroege start: {why}',
  why: {window_open: 'raam open', away: 'afwezig', presence_away: 'niemand thuis', summer: 'zomerstand'},
  off_house: 'Slim opwarmen staat uit: verwarmen begint om {time}', off_room: 'Slim opwarmen staat uit voor deze ruimte: verwarmen begint om {time}',
  not_needed: 'Warm genoeg voor {t} °C om {time}; eerder beginnen is niet nodig', trial: 'In de proefperiode zou het om {at} beginnen, zodat het om {time} {t} °C is',
  mornings: 'Op tijd warm, laatste 7 ochtenden', on_time: 'op tijd', late: '{d} te laat', early: '{d} te vroeg', no_check: 'geen controle',
  not_warm: 'niet warm binnen 3 uur', when_today: 'Vandaag', when_yesterday: 'Gisteren', when_date: 'Op {date}',
  arrival: '{when} warm om {at} ({how}).', arrival_never: '{when} niet warm binnen 3 uur na {at}.',
  next_earlier: 'De volgende keer begint het iets eerder.', next_later: 'De volgende keer begint het iets later.',
  next_earlier_min: 'De volgende keer begint het ongeveer {n} eerder.', next_later_min: 'De volgende keer begint het ongeveer {n} later.',
  model: 'Ruimtemodel', model_collecting: 'verzamelt metingen', model_checking: 'voorspellingen {n} van {m} dagen goed',
  model_trusted: 'betrouwbaar: zijn voorspellingen kloppen', model_demoted: 'controleert opnieuw: {n} van {m} dagen goed',
  advice: 'Advies', advice_only: 'Alleen advies: je weekprogramma blijft zoals het is.',
  off_line: 'Uit: de E32 leert hier niets zolang de ruimte uit staat.',
  none: 'De E32 heeft nog niet gemeld wat hij voor deze ruimte geleerd heeft.', min: '{n} min', h: '{h} u', h_m: '{h} u {m} min',
  relearn: 'Opnieuw leren', relearn_question: 'Wis wat de E32 voor {name} leerde?', relearn_more: 'Het leert vanzelf opnieuw; het weekprogramma blijft.',
  cancel: 'Annuleren', relearn_done: 'Gewist: de E32 begint opnieuw te leren voor {name}.', failed: 'Dat lukte niet: {reason}'}};
// ArrivalLearner (src/control/ArrivalLearner.h): on time between 15 min early and 10 min late; 180 min: not warm within 3 h.
const LATE_MIN = 10, EARLY_MIN = -15, NOT_WARM_MIN = 180;
const HISTORY_MS = 5 * 60000, PENDING_MS = 2 * 60000, DAY_MS = 86400000, DAYS = 7;
// Material Design Icons (v7.4.47, Apache 2.0), inline: no ha-icon.
const ICON_PATHS = {
 'check': 'M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z',
 'clock-outline': 'M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z',
 'radiator': 'M7.95,3L6.53,5.19L7.95,7.4H7.94L5.95,10.5L4.22,9.6L5.64,7.39L4.22,5.19L6.22,2.09L7.95,3M13.95,2.89L12.53,5.1L13.95,7.3L13.94,7.31L11.95,10.4L10.22,9.5L11.64,7.3L10.22,5.1L12.22,2L13.95,2.89M20,2.89L18.56,5.1L20,7.3V7.31L18,10.4L16.25,9.5L17.67,7.3L16.25,5.1L18.25,2L20,2.89M2,22V14A2,2 0 0,1 4,12H20A2,2 0 0,1 22,14V22H20V20H4V22H2M6,14A1,1 0 0,0 5,15V17A1,1 0 0,0 6,18A1,1 0 0,0 7,17V15A1,1 0 0,0 6,14M10,14A1,1 0 0,0 9,15V17A1,1 0 0,0 10,18A1,1 0 0,0 11,17V15A1,1 0 0,0 10,14M14,14A1,1 0 0,0 13,15V17A1,1 0 0,0 14,18A1,1 0 0,0 15,17V15A1,1 0 0,0 14,14M18,14A1,1 0 0,0 17,15V17A1,1 0 0,0 18,18A1,1 0 0,0 19,17V15A1,1 0 0,0 18,14Z',
 'power': 'M16.56,5.44L15.11,6.89C16.84,7.94 18,9.83 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12C6,9.83 7.16,7.94 8.88,6.88L7.44,5.44C5.36,6.88 4,9.28 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12C20,9.28 18.64,6.88 16.56,5.44M13,3H11V13H13',
 'clock-start': 'M12,1C8.14,1 5,4.14 5,8A7,7 0 0,0 12,15C15.86,15 19,11.87 19,8C19,4.14 15.86,1 12,1M12,3.15C14.67,3.15 16.85,5.32 16.85,8C16.85,10.68 14.67,12.85 12,12.85A4.85,4.85 0 0,1 7.15,8A4.85,4.85 0 0,1 12,3.15M11,5V8.69L14.19,10.53L14.94,9.23L12.5,7.82V5M4,16V24H6V21H18V24L22,20L18,16V19H6V16',
 'calendar-check-outline': 'M19 3H18V1H16V3H8V1H6V3H5C3.9 3 3 3.9 3 5V19C3 20.11 3.9 21 5 21H19C20.11 21 21 20.11 21 19V5C21 3.9 20.11 3 19 3M19 19H5V9H19V19M5 7V5H19V7H5M10.56 17.46L16.5 11.53L15.43 10.47L10.56 15.34L8.45 13.23L7.39 14.29L10.56 17.46Z',
 'chart-timeline-variant': 'M3,14L3.5,14.07L8.07,9.5C7.89,8.85 8.06,8.11 8.59,7.59C9.37,6.8 10.63,6.8 11.41,7.59C11.94,8.11 12.11,8.85 11.93,9.5L14.5,12.07L15,12C15.18,12 15.35,12 15.5,12.07L19.07,8.5C19,8.35 19,8.18 19,8A2,2 0 0,1 21,6A2,2 0 0,1 23,8A2,2 0 0,1 21,10C20.82,10 20.65,10 20.5,9.93L16.93,13.5C17,13.65 17,13.82 17,14A2,2 0 0,1 15,16A2,2 0 0,1 13,14L13.07,13.5L10.5,10.93C10.18,11 9.82,11 9.5,10.93L4.93,15.5L5,16A2,2 0 0,1 3,18A2,2 0 0,1 1,16A2,2 0 0,1 3,14Z',
 'lightbulb-on-outline': 'M20,11H23V13H20V11M1,11H4V13H1V11M13,1V4H11V1H13M4.92,3.5L7.05,5.64L5.63,7.05L3.5,4.93L4.92,3.5M16.95,5.63L19.07,3.5L20.5,4.93L18.37,7.05L16.95,5.63M12,6A6,6 0 0,1 18,12C18,14.22 16.79,16.16 15,17.2V19A1,1 0 0,1 14,20H10A1,1 0 0,1 9,19V17.2C7.21,16.16 6,14.22 6,12A6,6 0 0,1 12,6M14,21V22A1,1 0 0,1 13,23H11A1,1 0 0,1 10,22V21H14M11,18H13V15.87C14.73,15.43 16,13.86 16,12A4,4 0 0,0 12,8A4,4 0 0,0 8,12C8,13.86 9.27,15.43 11,15.87V18Z'
};

const STYLE = `:host{display:block;
--ot-space:8px;--ot-radius:12px;--ot-radius-s:8px;--ot-touch:44px;--ot-motion:150ms ease;
--ot-text-xl:22px;--ot-line-xl:28px;--ot-text-l:17px;--ot-line-l:24px;--ot-text-m:15px;--ot-line-m:22px;--ot-text-s:13px;--ot-line-s:18px;
--ot-bg:var(--card-background-color);--ot-fg:var(--primary-text-color);--ot-fg-2:var(--secondary-text-color);
--ot-line:var(--divider-color);--ot-accent:var(--primary-color);--ot-on-accent:var(--text-primary-color, #fff);
--ot-heat-ink:#a1500f;--ot-heat-fill:#fbe9db;--ot-along-ink:#886100;--ot-along-fill:#f8efcf;--ot-water-ink:#1f5fa8;--ot-water-fill:#dde9f8;
--ot-rest-ink:#5f6368;--ot-rest-fill:#ebedf0;--ot-attention-ink:#b3261e;--ot-attention-fill:#f9dedc;
/* CONTRACT-1.4.1 §8 (amended): filled buttons and text buttons, readable on HA's default accent */
--ot-fill:color-mix(in srgb,var(--ot-accent) 72%,#000);--ot-link:color-mix(in srgb,var(--ot-accent) 60%,var(--ot-fg));
/* 1.4.3 design §6: "learned" in green, its ink 60 % mixed with the text colour; tiles raised 2.5 % text on the card */
--ot-ok:var(--success-color,#43a047);--ot-ok-ink:color-mix(in srgb,var(--ot-ok) 60%,var(--ot-fg));
--ot-ok-fill:color-mix(in srgb,var(--ot-ok) 16%,var(--ot-bg,#fff));--ot-raised:color-mix(in srgb,var(--ot-fg) 2.5%,var(--ot-bg,#fff));
color:var(--ot-fg)}
:host([data-theme="dark"]){--ot-heat-ink:#f0a060;--ot-heat-fill:rgba(240,160,96,.18);--ot-along-ink:#e6c35c;--ot-along-fill:rgba(230,195,92,.18);
--ot-water-ink:#7fb3f0;--ot-water-fill:rgba(127,179,240,.18);--ot-rest-ink:#b0b4ba;--ot-rest-fill:rgba(176,180,186,.18);
--ot-attention-ink:#f2857c;--ot-attention-fill:rgba(242,133,124,.18)}
:host([data-theme="dark"]){--ot-raised:color-mix(in srgb,var(--ot-fg) 5%,var(--ot-bg,#1c1c1c))}
ha-card{display:block;padding:16px;border-radius:var(--ot-radius);color:var(--ot-fg);height:100%;box-sizing:border-box}
.wrap{container:learn/inline-size;display:flex;flex-direction:column;gap:12px}
p{margin:0}
.ic{display:inline-flex;flex:none;width:var(--ic,20px);height:var(--ic,20px)}.ic svg{display:block;width:100%;height:100%}
.head{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;min-height:28px}
.name{flex:1 1 auto;min-width:0;margin:0;font-size:var(--ot-text-l);line-height:var(--ot-line-l);font-weight:500;overflow-wrap:anywhere}
.chip{display:inline-flex;align-items:center;gap:6px;min-height:26px;max-width:100%;box-sizing:border-box;padding:4px 10px;border-radius:13px;
font-size:var(--ot-text-s);line-height:var(--ot-line-s);font-weight:500}
.chip .ic{--ic:15px}.chip span{min-width:0;overflow-wrap:anywhere}
.chip.ok{background:var(--ot-ok-fill);color:var(--ot-ok-ink)}.chip.busy,.chip.along{background:var(--ot-along-fill);color:var(--ot-along-ink)}
.chip.rest{background:var(--ot-rest-fill);color:var(--ot-rest-ink)}
.tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.tile{display:flex;flex-direction:column;justify-content:space-between;gap:4px;min-width:0;min-height:88px;box-sizing:border-box;padding:10px 12px;
border-radius:var(--ot-radius-s);background:var(--ot-raised)}
.tile.wait{background:none;border:1px dashed color-mix(in srgb,var(--ot-fg) 28%,transparent)}
.value{display:flex;flex-wrap:wrap;align-items:baseline;gap:0 6px;min-width:0;font-size:26px;line-height:32px;font-weight:300;font-variant-numeric:tabular-nums}
.value .pre,.value .unit{font-size:var(--ot-text-s);line-height:var(--ot-line-s);font-weight:400;color:var(--ot-fg-2)}
.value .num{white-space:nowrap}
.need{font-size:var(--ot-text-m);line-height:var(--ot-line-m);color:var(--ot-fg-2);overflow-wrap:anywhere}
.caption{font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2);overflow:hidden;text-overflow:ellipsis;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow-wrap:anywhere}
.rows{display:flex;flex-direction:column;border-top:1px solid var(--ot-line)}
.row{display:grid;grid-template-columns:20px minmax(0,1fr);gap:10px;align-items:start;padding:10px 0;border-bottom:1px solid var(--ot-line)}
.row:last-child{border-bottom:0;padding-bottom:0}
.row>.ic{margin-top:1px;color:var(--ot-fg-2)}.row.go{cursor:pointer;min-height:var(--ot-touch);box-sizing:border-box;border-radius:6px}
.row.go:focus{outline:none}.row.go:focus-visible{outline:2px solid var(--ot-accent);outline-offset:2px}
.text{font-size:var(--ot-text-m);line-height:var(--ot-line-m);overflow-wrap:anywhere}.text b{font-weight:500}
.sub{margin-top:2px;font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2);overflow-wrap:anywhere}
.est{color:var(--ot-along-ink)}
.dots{display:flex;gap:6px;margin:8px 0 2px;flex-wrap:nowrap}
.day{display:flex;flex-direction:column;align-items:center;gap:2px;width:22px;flex:none}
.dot{width:14px;height:14px;border-radius:50%;box-sizing:border-box;border:2px solid color-mix(in srgb,var(--ot-fg) 30%,transparent)}
.dot.ok{border:0;background:var(--ot-ok)}.dot.off{border:0;background:var(--warning-color,#ffa600)}
.wd{font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2)}
.bar{position:relative;height:6px;margin:8px 0 4px;border-radius:3px;background:color-mix(in srgb,var(--ot-fg) 10%,transparent);overflow:hidden}
.bar i{position:absolute;inset:0 auto 0 0;border-radius:3px;background:var(--ot-along-ink)}.bar i.ok{background:var(--ot-ok)}
.muted{font-size:var(--ot-text-m);line-height:var(--ot-line-m);color:var(--ot-fg-2)}
/* 1.4.4: Learn again, a text button at the foot; its question inline (the panel's words), the answer under it */
.foot{display:flex;flex-direction:column;align-items:flex-end;gap:8px;margin-top:-4px}
.btn{min-height:var(--ot-touch);min-width:var(--ot-touch);box-sizing:border-box;padding:0 12px;border:0;border-radius:var(--ot-radius-s);background:none;
font:inherit;font-size:var(--ot-text-m);font-weight:500;color:var(--ot-link);cursor:pointer}
.btn:focus{outline:none}.btn:focus-visible{outline:2px solid var(--ot-accent);outline-offset:2px}.btn[disabled]{opacity:.6;cursor:default}
.btn.filled{background:var(--ot-fill);color:var(--ot-on-accent)}
.ask{align-self:stretch;display:flex;flex-direction:column;gap:4px;padding:12px;border-radius:var(--ot-radius-s);background:var(--ot-raised)}
.ask .q{font-size:var(--ot-text-m);line-height:var(--ot-line-m);font-weight:500;overflow-wrap:anywhere}
.ask .acts{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px;margin-top:4px}
.said{align-self:stretch;font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2);overflow-wrap:anywhere}.said.bad{color:var(--ot-attention-ink)}
@container learn (min-width:620px){.tiles{grid-template-columns:repeat(4,minmax(0,1fr))}}`;

const finite = value => typeof value === 'number' && Number.isFinite(value);
const numeric = value => { const n = typeof value === 'string' && value.trim() !== '' ? Number(value) : value; return finite(n) ? n : null; };
const locale = hass => hass?.locale?.language || hass?.language || 'en';
const lang = hass => /^nl\b/.test(locale(hass)) ? 'nl' : 'en';
const known = st => !!st && typeof st.state === 'string' && !['unknown', 'unavailable', ''].includes(st.state);
const entityId = value => typeof value === 'string' && value.includes('.') ? value : undefined;
const NBSP = ' ';
const together = text => typeof text === 'string' ? text.replace(/ (°C|%|min|h|u)(?=$|[\s·,.;)])/g, NBSP + '$1') : text;
// Dark: Home Assistant's theme when it says so, else the browser's colour scheme (CONTRACT-1.4.1 §8).
const darkOf = hass => {
 if (typeof hass?.themes?.darkMode === 'boolean') return hass.themes.darkMode;
 try { return window.matchMedia('(prefers-color-scheme: dark)').matches; } catch (e) { return false; }
};
/* clock: begin. One clock for the OpenThermostat cards (the same text in house-card.js and room-status-card.js, checked
   by test_room_overview.py): Home Assistant's time zone (the house's, where the E32 and its program live), the viewer's
   12/24-hour choice (a 12-hour clock without a leading zero: "5:00 PM"); a moment today as its time, the day before or
   after as "yesterday 14:05" / "tomorrow 14:30" in the viewer's language, further away with its date ("Sat 14 Nov,
   14:30"): a weekday alone is ambiguous after six days, and a holiday can end months ahead. */
const clockLocale = hass => hass?.locale?.language || hass?.language || 'en';
const clockZone = hass => {
 const zone = hass?.config?.time_zone;
 if (typeof zone !== 'string' || !zone) return undefined;
 try { new Intl.DateTimeFormat('en', {timeZone: zone}); return zone; } catch (e) { return undefined; }
};
const clockHour12 = hass => {
 const chosen = ({'12': true, '24': false})[hass?.locale?.time_format];
 if (chosen !== undefined) return chosen;
 try { return /h1[12]/.test(new Intl.DateTimeFormat(clockLocale(hass), {hour: 'numeric'}).resolvedOptions().hourCycle); } catch (e) { return false; }
};
const clockOptions = hass => {
 const hour12 = clockHour12(hass);
 return {hour: hour12 ? 'numeric' : '2-digit', minute: '2-digit', hour12, timeZone: clockZone(hass)};
};
// The time of day of ms ("14:30", "2:30 PM").
const clockTime = (hass, ms) => {
 try { return new Date(ms).toLocaleTimeString(clockLocale(hass), clockOptions(hass)); } catch (e) { return new Date(ms).toISOString().slice(11, 16); }
};
// The day number of ms in the house's zone (days since 1970), to compare calendar days.
const clockDay = (hass, ms) => {
 try {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {timeZone: clockZone(hass), year: 'numeric', month: 'numeric', day: 'numeric'})
   .formatToParts(new Date(ms)).map(({type, value}) => [type, Number(value)]));
  return Math.round(Date.UTC(p.year, p.month - 1, p.day) / 86400000);
 } catch (e) { return Math.floor(ms / 86400000); }
};
// A moment (an ISO text or ms) for a sentence: "14:30", "tomorrow 14:30", "Sat 14 Nov, 14:30"; '' when not a time.
const clockMoment = (hass, value, now = Date.now()) => {
 const ms = typeof value === 'number' ? value : typeof value === 'string' ? Date.parse(value) : NaN;
 if (!Number.isFinite(ms)) return '';
 const days = clockDay(hass, ms) - clockDay(hass, now), time = clockTime(hass, ms);
 if (days === 0) return time;
 if (Math.abs(days) === 1) {
  try {
   // "tomorrow" in the card's own language (English for a language it has no words for), as the sentence around it.
   const word = new Intl.RelativeTimeFormat(lang(hass), {numeric: 'auto'}).format(days, 'day');
   return word + ' ' + time;
  } catch (e) { /* older browser */ }
 }
 try { return new Date(ms).toLocaleString(clockLocale(hass), {weekday: 'short', day: 'numeric', month: 'short', ...clockOptions(hass)}); }
 catch (e) { return new Date(ms).toISOString().slice(0, 16).replace('T', ' '); }
};
/* clock: end */
// A wall-clock time the sensor gives in Home Assistant's zone ("06:30") in the viewer's 12/24 hours ("6:30 AM").
const wallClock = (hass, text) => {
 const m = typeof text === 'string' ? text.match(/^(\d{1,2}):(\d{2})$/) : null;
 if (!m) return typeof text === 'string' ? text : '';
 const hour12 = clockHour12(hass);
 try {
  return new Date(Date.UTC(2000, 0, 1, Number(m[1]), Number(m[2]))).toLocaleTimeString(clockLocale(hass),
   {hour: hour12 ? 'numeric' : '2-digit', minute: '2-digit', hour12, timeZone: 'UTC'});
 } catch (e) { return text; }
};
const SVG = 'http://www.w3.org/2000/svg';
const make = (tag, attrs = {}, text) => {
 const e = tag.startsWith('svg:') ? document.createElementNS(SVG, tag.slice(4)) : document.createElement(tag);
 for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined && v !== false) e.setAttribute(k, v);
 if (text !== undefined) e.textContent = text;
 return e;
};
const icon = name => {
 const box = make('span', {class: 'ic', 'data-icon': name, 'aria-hidden': 'true'});
 const svg = make('svg:svg', {viewBox: '0 0 24 24', focusable: 'false'});
 svg.append(make('svg:path', {d: ICON_PATHS[name] || '', fill: 'currentColor'}));
 box.append(svg);
 return box;
};
// Home Assistant's history of one entity, as [{s: state, t: ms}] by time ("lc"/"lu" in seconds, or ISO texts).
const changes = rows => (Array.isArray(rows) ? rows : []).map(row => {
 const seconds = numeric(row?.lc) ?? numeric(row?.lu);
 const t = seconds !== null ? seconds * 1000 : Date.parse(row?.last_changed ?? row?.last_updated);
 return {s: row?.s ?? row?.state, t};
}).filter(c => typeof c.s === 'string' && Number.isFinite(c.t)).sort((a, b) => a.t - b.t);

class OpenThermostatLearningRoom extends HTMLElement {
 constructor() {
  super(); this.attachShadow({mode: 'open'});
  this._key = null; this._history = null; this._fetched = 0; this._pending = 0; this._seen = undefined; this._gen = 0;
 }
 static getStubConfig() { return {}; }
 setConfig(config) {
  const id = entityId;
  if (!config || !id(config.learned) || typeof config.room_id !== 'string' || !config.room_id)
   throw new Error('This card needs the "What the E32 learned" sensor of OpenThermostat (learned: sensor.…) and a room (room_id); the OpenThermostat dashboard adds it for you.');
  this._config = {room_id: config.room_id, learned: id(config.learned), learning: id(config.learning), warm_on_time: id(config.warm_on_time),
   heating_start: id(config.heating_start), reason: id(config.reason), state: id(config.state), relearn: id(config.relearn),
   name: typeof config.name === 'string' ? config.name : ''};
  this._asking = false; this._busy = false; this._said = null;
  this._key = null; this._history = null; this._fetched = 0; this._seen = undefined;
  if (this._hass) { this.refresh(); this.render(); }
 }
 set hass(hass) {
  this._hass = hass;
  if (!this._config) return;
  this.refresh();
  // Only a new state of its own entities, language, theme or clock choice redraws; Home Assistant sets hass on every change.
  const c = this._config, key = [c.learned, c.warm_on_time, c.heating_start, c.state, c.relearn].map(id => id && hass?.states?.[id])
   .concat([locale(hass), darkOf(hass), hass?.locale?.time_format, hass?.config?.time_zone, this._history]);
  if (this._key && key.every((v, i) => v === this._key[i])) return;
  this._key = key; this.render();
 }
 connectedCallback() { if (this._hass && this._config) this.refresh(); }
 disconnectedCallback() { this._gen++; this._pending = 0; }
 getCardSize() { return 6; }
 getGridOptions() { return {columns: 12, min_columns: 6}; }
 st(id) { return id ? this._hass?.states?.[id] || null : null; }
 t(key, values = {}) {
  const words = OWN[lang(this._hass)], text = words[key] ?? OWN.en[key] ?? '';
  return together(String(text).replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all));
 }
 number(value, digits = 0) {
  return value.toLocaleString(locale(this._hass), {minimumFractionDigits: 0, maximumFractionDigits: digits, useGrouping: false}).replace('-', '−');
 }
 // Minutes in words as the learned overview says them: half minutes below an hour, else to 5 minutes.
 duration(minutes) {
  if (minutes < 57.5) return this.t('min', {n: this.number(Math.max(0.5, Math.round(minutes * 2) / 2), 1)});
  const rounded = Math.round(minutes / 5) * 5, h = Math.floor(rounded / 60), m = rounded % 60;
  return m ? this.t('h_m', {h: this.number(h), m: this.number(m)}) : this.t('h', {h: this.number(h)});
 }
 whole(minutes) {
  const n = Math.abs(Math.round(minutes));
  if (n < 60) return this.t('min', {n: this.number(n)});
  const h = Math.floor(n / 60), m = n % 60;
  return m ? this.t('h_m', {h: this.number(h), m: this.number(m)}) : this.t('h', {h: this.number(h)});
 }
 // This room's entry of the learned overview (its rooms[], found by the room's id), or null.
 entry() {
  const st = this.st(this._config.learned);
  if (!known(st)) return null;
  const rooms = st.attributes?.rooms;
  return Array.isArray(rooms) ? rooms.find(room => room && room.room_id === this._config.room_id) || null : null;
 }
 // -- the history of "Warm on time yesterday": at most every 5 minutes, and when its state changed --------------------
 refresh() {
  const hass = this._hass, c = this._config, st = this.st(c?.warm_on_time);
  if (!hass || !this.isConnected || !st || typeof hass.callWS !== 'function') return;
  const now = Date.now(), changed = this._seen !== undefined && this._seen !== st.last_changed;
  if (now - this._pending < PENDING_MS) return;
  if (this._fetched && !(changed && now - this._fetched >= HISTORY_MS) && now - this._fetched < 6 * 3600000) return;
  this._seen = st.last_changed;
  this.readHistory(now);
 }
 async readHistory(now) {
  const gen = this._gen, id = this._config.warm_on_time;
  this._pending = now;
  try {
   const result = await this._hass.callWS({type: 'history/history_during_period', start_time: new Date(now - (DAYS + 1) * DAY_MS).toISOString(),
    entity_ids: [id], minimal_response: true, no_attributes: true});
   if (gen !== this._gen) return;
   this._history = {list: changes(result?.[id])};
  } catch (e) {
   if (gen !== this._gen) return;
   this._history = this._history || {list: []};
  }
  this._fetched = Date.now(); this._pending = 0;
  if (this._hass) this.hass = this._hass;
 }
 // The last 7 mornings, oldest first: minutes late (negative: early) or null. A value of "Warm on time yesterday" that
 // came on a day is about the day before it; today's morning is the learned overview's last morning when it is today's.
 mornings(facts) {
  const hass = this._hass, today = clockDay(hass, Date.now()), out = Array(DAYS).fill(null);
  const put = (day, value) => { const i = day - (today - DAYS + 1); if (i >= 0 && i < DAYS && value !== null) out[i] = value; };
  const st = this.st(this._config.warm_on_time);
  const list = [...(this._history?.list || [])];
  if (known(st) && Number.isFinite(Date.parse(st.last_changed))) list.push({s: st.state, t: Date.parse(st.last_changed)});
  for (const c of list) put(clockDay(hass, c.t) - 1, numeric(c.s));
  const a = facts?.arrival;
  if (a && finite(a.minutes_late)) put(a.day === 'today' ? today : a.day === 'yesterday' ? today - 1 : -1, a.minutes_late);
  return out;
 }
 moreInfo(entity) { if (entity) this.dispatchEvent(new CustomEvent('hass-more-info', {bubbles: true, composed: true, detail: {entityId: entity}})); }

 render() {
  const hass = this._hass, c = this._config;
  if (!hass || !c) return;
  const root = this.shadowRoot, focused = root.activeElement?.dataset?.focus;
  if (darkOf(hass)) this.setAttribute('data-theme', 'dark'); else this.removeAttribute('data-theme');
  const card = make('ha-card'), wrap = make('div', {class: 'wrap'});
  card.append(wrap);
  const entry = this.entry(), facts = entry && typeof entry.facts === 'object' && entry.facts ? entry.facts : null;
  const name = (entry && typeof entry.name === 'string' && entry.name) || c.name;
  const head = make('div', {class: 'head'});
  head.append(make('h3', {class: 'name'}, name || ' '));
  wrap.append(head);
  if (!facts) {
   // Nothing reported (yet), or an overview without facts: one quiet sentence, never a raw key or "Unknown".
   wrap.append(make('p', {class: 'muted', 'data-none': ''}, this.t('none')));
  } else {
   const chip = this.chip(facts);
   if (chip) head.append(chip);
   if (facts.status === 'off') wrap.append(make('p', {class: 'muted', 'data-off': ''}, this.t('off_line')));
   else {
    const tiles = this.tiles(facts);
    if (tiles) wrap.append(tiles);
    const rows = make('div', {class: 'rows'});
    for (const row of [this.smartRow(facts), this.morningRow(facts), this.modelRow(facts), this.adviceRow(facts)]) if (row) rows.append(row);
    if (rows.childElementCount) wrap.append(rows);
   }
  }
  const foot = this.relearnFoot(name);
  if (foot) wrap.append(foot);
  root.replaceChildren(make('style', {}, STYLE), card);
  if (focused) root.querySelector(`[data-focus="${focused}"]`)?.focus({preventScroll: true});
 }
 // 1.4.4 (plan 2.3): "Learn again" when the E32 offers it (the room's button entity exists and is there): a tap asks the
 // panel's question in the card, Learn again presses the button (the E32 clears what it learned for this room), the
 // answer stays under it until the next question.
 relearnFoot(name) {
  const id = this._config.relearn, st = this.st(id);
  if (!st || st.state === 'unavailable') return null;
  const foot = make('div', {class: 'foot', 'data-relearn-foot': ''}), words = {name: name || this._config.room_id};
  const button = (text, cls, key, act) => {
   const b = make('button', {type: 'button', class: 'btn' + (cls ? ' ' + cls : ''), 'data-focus': key, ['data-' + key]: ''}, text);
   if (this._busy) b.disabled = true;
   b.addEventListener('click', act);
   return b;
  };
  if (this._asking) {
   const ask = make('div', {class: 'ask', role: 'group', 'aria-label': this.t('relearn')});
   const acts = make('div', {class: 'acts'});
   acts.append(button(this.t('cancel'), '', 'relearn-cancel', () => { this._asking = false; this._focus('relearn'); }),
    button(this.t('relearn'), 'filled', 'relearn-confirm', () => this.relearn(id, words)));
   ask.append(make('p', {class: 'q'}, this.t('relearn_question', words)), make('p', {class: 'sub'}, this.t('relearn_more')), acts);
   foot.append(ask);
  } else foot.append(button(this.t('relearn'), '', 'relearn', () => { this._asking = true; this._said = null; this._focus('relearn-cancel'); }));
  if (this._said) foot.append(make('p', {class: 'said' + (this._said.bad ? ' bad' : ''), role: 'status', 'data-said': ''}, this._said.text));
  return foot;
 }
 _focus(key) {
  this.render();
  this.shadowRoot.querySelector(`[data-focus="${key}"]`)?.focus({preventScroll: true});
 }
 async relearn(id, words) {
  this._busy = true; this.render();
  try {
   await this._hass.callService('button', 'press', {entity_id: id});
   this._said = {text: this.t('relearn_done', words)};
  } catch (err) {
   this._said = {bad: true, text: this.t('failed', {reason: String(err?.message || err?.code || err || '').trim() || '—'})};
  }
  this._busy = false; this._asking = false;
  this._focus('relearn');
 }
 chip(facts) {
  const p = facts.progress || {}, n = finite(p.seen) ? p.seen : 0, m = finite(p.of) ? p.of : 6;
  const [cls, glyph, words] = {
   ready: ['ok', 'check', this.t('learned')],
   timing: ['busy', 'clock-outline', this.t('learning_water')],
   learning: ['busy', 'clock-outline', n < m ? this.t('learning_of', {n: this.number(n), m: this.number(m)}) : this.t('learning')],
   follow: ['along', 'radiator', this.t('heats_along')],
   off: ['rest', 'power', this.t('off')]}[facts.status] || [];
  if (!cls) return null;
  const chip = make('span', {class: 'chip ' + cls, 'data-status': facts.status, title: words});
  chip.append(icon(glyph), make('span', {}, words));
  return chip;
 }
 tile(key, value, caption, title) {
  const box = make('div', {class: 'tile', 'data-fact': key, title: title || null});
  box.append(value, make('p', {class: 'caption'}, caption));
  return box;
 }
 figure(num, unit, pre) {
  const value = make('p', {class: 'value'});
  if (pre) value.append(make('span', {class: 'pre'}, pre));
  value.append(make('span', {class: 'num'}, together(num)));
  if (unit) value.append(make('span', {class: 'unit'}, unit));
  return value;
 }
 // A fact not learned yet: what it still needs, in words, on a dotted tile; never a number for the fact itself.
 waiting(key, need, label) {
  const box = this.tile(key, make('p', {class: 'need'}, need), label, need);
  box.classList.add('wait');
  box.dataset.waiting = '';
  return box;
 }
 tiles(facts) {
  const list = [], p = facts.progress || {}, seen = finite(p.seen) ? p.seen : 0, of = finite(p.of) ? p.of : 6;
  const on = facts.status !== 'follow', deg = v => this.number(v, 1);
  if (on) {
   const w = facts.warmup;
   if (w && finite(w.hours) && finite(w.flow_c))
    list.push(this.tile('warmup', this.figure(this.duration(w.hours * 60), '', this.t('warmup_pre')), this.t('warmup_caption', {flow: this.number(w.flow_c)})));
   else list.push(this.waiting('warmup', facts.status === 'timing' ? this.t('wait_timing') : seen >= of ? this.t('wait_other_days')
    : of - seen === 1 ? this.t('wait_warmup') : this.t('wait_warmups', {n: this.number(of - seen)}), this.t('warmup_label')));
  }
  const cool = facts.cooling;
  if (cool && finite(cool.c_per_h))
   list.push(this.tile('cooling', this.figure(this.number(cool.c_per_h, 2) + ' °C', this.t('per_hour')), this.t('cooling_caption', {out: this.number(finite(cool.outdoor_c) ? cool.outdoor_c : 5)})));
  else list.push(this.waiting('cooling', this.t('wait_cooling'), this.t('cooling_label')));
  // 1.4.4 (plan 2.4): on Heat along only, how often it reached its temperature by heating along (the hours of the last
  // 14 cold days), and before 14 such days which day it counts; nothing for a room with a week program.
  const r = facts.reach;
  if (!on && r && typeof r === 'object' && finite(r.c) && finite(r.days)) {
   const t = this.number(r.c, 1), of = finite(r.of) ? r.of : 14, days = this.number(r.days);
   if (finite(r.pct)) {
    const title = this.t('reach_title', {t, pct: this.number(r.pct), days});
    list.push(this.tile('reach', this.figure(this.number(r.pct) + ' %'), this.t('reach_caption', {t, days}), title));
   } else list.push(this.waiting('reach', r.days > 0 ? this.t('reach_counting', {n: days, m: this.number(of)}) : this.t('reach_counting_plain'),
    this.t('reach_label', {t})));
  }
  if (on) {
   if (finite(facts.lowest_flow_c)) list.push(this.tile('lowest_flow_c', this.figure(this.number(facts.lowest_flow_c) + ' °C'), this.t('lowest_caption')));
   else list.push(this.waiting('lowest_flow_c', facts.status === 'ready' ? this.t('wait_not_found') : facts.status === 'timing'
    ? this.t('wait_other_water') : this.t('wait_after'), this.t('lowest_label')));
   const free = facts.free_heat;
   if (free && finite(free.c_per_h)) {
    const part = (OWN[lang(this._hass)].parts || OWN.en.parts)[free.part] || '';
    const caption = this.t('free_caption', {part}).replace(/\s+\(/, ' (').replace(/\s{2,}/g, ' ');
    list.push(this.tile('free_heat', this.figure('+' + deg(free.c_per_h) + ' °C', this.t('per_hour')), caption, caption));
   } else list.push(this.waiting('free_heat', this.t('wait_free'), this.t('free_label')));
  }
  if (!list.length) return null;
  const grid = make('div', {class: 'tiles'});
  grid.append(...list);
  return grid;
 }
 row(key, glyph, parts, entity) {
  const row = make('div', {class: 'row' + (entity ? ' go' : ''), 'data-row': key});
  const body = make('div');
  for (const part of parts) if (part) body.append(part);
  row.append(icon(glyph), body);
  if (entity && this.st(entity)) {
   Object.assign(row, {tabIndex: 0}); row.setAttribute('role', 'button'); row.dataset.focus = key;
   row.addEventListener('click', () => this.moreInfo(entity));
   row.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); this.moreInfo(entity); } });
  }
  return row;
 }
 smartRow(facts) {
  const s = facts.smart_start;
  if (facts.status === 'follow' || !s || typeof s !== 'object') return null;
  const at = wallClock(this._hass, s.at), time = wallClock(this._hass, s.target_at), t = finite(s.target_c) ? this.number(s.target_c, 1) : '';
  const values = {at, time, t}, why = (OWN[lang(this._hass)].why || {})[s.held_reason];
  const text = make('p', {class: 'text'}), sub = [];
  if (s.held_reason === 'learning') { text.textContent = this.t('still', values) + '.'; sub.push(this.t('still_more', values)); }
  else if (why) text.textContent = this.t('held', {why}) + '.';
  else if (s.held_reason === 'off' || s.held_reason === 'room_off') text.textContent = this.t(s.held_reason === 'off' ? 'off_house' : 'off_room', values) + '.';
  else if (s.held_reason === 'not_needed') text.textContent = this.t('not_needed', values) + '.';
  else if (s.held_reason === 'trial') text.textContent = this.t('trial', values) + '.';
  else {
   text.textContent = this.t(s.now ? 'now' : 'starts', values);
   if (s.estimate) { text.append(' '); text.append(make('span', {class: 'est', 'data-estimate': ''}, this.t('estimate'))); sub.push(this.t('learns')); }
   text.append('.');
  }
  return this.row('smart', 'clock-start', [text, ...sub.map(line => make('p', {class: 'sub'}, line))], this._config.heating_start);
 }
 morningRow(facts) {
  if (!this._config.warm_on_time || !this.st(this._config.warm_on_time)) return null;
  const values = this.mornings(facts), a = facts.arrival;
  if (!values.some(v => v !== null) && !a) return null;
  const hass = this._hass, now = Date.now(), dots = make('div', {class: 'dots', role: 'img'}), said = [];
  values.forEach((v, i) => {
   const ms = now - (DAYS - 1 - i) * DAY_MS;
   let wd = '';
   try { wd = new Date(ms).toLocaleDateString(locale(hass), {weekday: 'narrow', timeZone: clockZone(hass)}); } catch (e) { wd = ''; }
   const state = v === null ? 'none' : v >= LATE_MIN || v <= EARLY_MIN ? 'off' : 'ok';
   const words = v === null ? this.t('no_check') : v >= NOT_WARM_MIN ? this.t('not_warm') : v > 0 ? this.t('late', {d: this.whole(v)})
    : v < 0 ? this.t('early', {d: this.whole(v)}) : this.t('on_time');
   let day = '';
   try { day = new Date(ms).toLocaleDateString(locale(hass), {weekday: 'short', day: 'numeric', month: 'short', timeZone: clockZone(hass)}); } catch (e) { day = ''; }
   const box = make('span', {class: 'day', title: day + ': ' + words});
   box.append(make('i', {class: 'dot ' + (state === 'none' ? '' : state), 'data-dot': state}), make('span', {class: 'wd', 'aria-hidden': 'true'}, wd));
   dots.append(box);
   said.push(day + ': ' + words);
  });
  dots.setAttribute('aria-label', this.t('mornings') + ': ' + said.join('; '));
  const parts = [make('p', {class: 'text'}, this.t('mornings')), dots];
  if (a && finite(a.minutes_late) && typeof a.at === 'string') {
   const when = a.day === 'today' ? this.t('when_today') : a.day === 'yesterday' ? this.t('when_yesterday') : this.t('when_date', {date: this.date(a.day)});
   const m = a.minutes_late, at = wallClock(hass, a.at);
   const line = m >= NOT_WARM_MIN ? this.t('arrival_never', {when, at})
    : this.t('arrival', {when, at, how: m > 0 ? this.t('late', {d: this.whole(m)}) : m < 0 ? this.t('early', {d: this.whole(m)}) : this.t('on_time')});
   const next = a.next === 'earlier' || a.next === 'later'
    ? (finite(a.next_min) ? this.t('next_' + a.next + '_min', {n: this.whole(a.next_min)}) : this.t('next_' + a.next)) : '';
   parts.push(make('p', {class: 'sub', 'data-arrival': ''}, next ? line + ' ' + next : line));
  }
  return this.row('mornings', 'calendar-check-outline', parts, this._config.warm_on_time);
 }
 date(iso) {
  const m = typeof iso === 'string' ? iso.match(/^(\d{4})-(\d{2})-(\d{2})$/) : null;
  if (!m) return '';
  try { return new Date(Date.UTC(+m[1], +m[2] - 1, +m[3], 12)).toLocaleDateString(locale(this._hass), {day: 'numeric', month: 'short', timeZone: 'UTC'}); }
  catch (e) { return iso; }
 }
 modelRow(facts) {
  const model = facts.model;
  if (facts.status === 'follow' || !model || typeof model !== 'object') return null;
  const n = finite(model.good_days) ? model.good_days : null, m = finite(model.of) && model.of > 0 ? model.of : null;
  const words = {collecting: this.t('model_collecting'), trusted: this.t('model_trusted'),
   checking: n !== null && m !== null ? this.t('model_checking', {n: this.number(n), m: this.number(m)}) : this.t('model_collecting'),
   demoted: n !== null && m !== null ? this.t('model_demoted', {n: this.number(n), m: this.number(m)}) : this.t('model_collecting')}[model.state];
  if (!words) return null;
  const share = model.state === 'trusted' ? 1 : n !== null && m !== null ? Math.min(1, Math.max(0, n / m)) : 0;
  const bar = make('div', {class: 'bar', role: 'progressbar', 'aria-valuemin': '0', 'aria-valuemax': '100', 'aria-valuenow': String(Math.round(share * 100)),
   'aria-label': this.t('model') + ': ' + words});
  bar.append(make('i', {class: model.state === 'trusted' ? 'ok' : null, style: `width:${(share * 100).toFixed(1)}%`}));
  return this.row('model', 'chart-timeline-variant', [make('p', {class: 'text'}, this.t('model')), bar, make('p', {class: 'sub'}, words)],
   this._config.learning);
 }
 adviceRow(facts) {
  const advice = facts.advice, waiting = facts.waiting && typeof facts.waiting.advice === 'string' ? facts.waiting.advice : '';
  if (advice && typeof advice.text === 'string' && advice.text) {
   const text = make('p', {class: 'text'});
   text.append(make('b', {}, this.t('advice')), ' · ' + advice.text);
   return this.row('advice', 'lightbulb-on-outline', [text, make('p', {class: 'sub'}, this.t('advice_only'))]);
  }
  return waiting ? this.row('advice', 'lightbulb-on-outline', [make('p', {class: 'sub', 'data-waiting': ''}, waiting)]) : null;
 }
}
// Other dashboard cards (HACS resources) may later replace window.customElements with a scoped-registry
// polyfill whose get() does not see elements defined before it; Home Assistant then reports "Custom element
// doesn't exist". So: define now, and again (a fresh subclass) whenever the registry in use lacks the element.
// Never throws. (The same guard as e32-week-card.js, room-status-card.js and heating-curve-card.js.)
const ensureDefined = (name, cls) => {
 let own = cls;
 const check = () => {
  try { if (!customElements.get(name)) { customElements.define(name, own); own = class extends cls {}; } }
  catch (e) { own = class extends cls {}; }
 };
 check();
 if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', check, {once: true});
 if (document.readyState !== 'complete') window.addEventListener('load', check, {once: true});
 for (const ms of [0, 250, 1000, 3000, 10000]) setTimeout(check, ms);
 window.addEventListener('location-changed', check);
 // A HACS card may replace window.customElements later: a cheap check every 0.5 s for the first 30 s, when the other
 // cards load; after that a navigation (location-changed) or the page coming back into view checks again.
 const timer = setInterval(check, 500);
 setTimeout(() => clearInterval(timer), 30000);
 document.addEventListener('visibilitychange', check);
 return check;
};
ensureDefined('openthermostat-learning-room', OpenThermostatLearningRoom);
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === 'openthermostat-learning-room'))
 window.customCards.push({type: 'openthermostat-learning-room', name: 'OpenThermostat learning per room',
  description: 'What the E32 learned for one room, in figures; what it does not know yet says what it still needs.'});
