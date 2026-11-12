/* Dashboard card and room-screen component: the visual week planner for the rooms of the E32 room plan.
   HA authenticates (admin websocket open_thermostat/e32_week/*); the E32 stores and runs the program.
   The planner itself is week-editor.js, the same file the E32 rooms page uses (it stays as it is there). 1.4.1: this
   card adds the reset times you see and edit on the day bars (a marker per reset time: drag it, tap it for its card),
   the same reset times as a list under the planner, the room's own Smart warm-up, and the look of the settings
   panel. One save writes the program, the reset times and Smart warm-up of the room (e32_week.py).
   setConfig({entry_id, room_id, embedded: true}) (the settings panel's room screen, CONTRACT-1.4.1 §4): one room, no
   room tabs, no title, a compact save row, and the event openthermostat-week-dirty ({dirty}) on every change. */
const EDITOR = '/open_thermostat/week-editor-1.4.5.js';
const TEXT = {
 en: {title: 'Week program', loading: 'Loading…', reading: 'Reading the week programs from the E32…', intro: 'The E32 follows this program on its own, also when Home Assistant is offline.',
  follows: 'This room follows {entity} while Home Assistant gives a target temperature; the week program applies when it gives none.',
  save: 'Save to E32', saving: 'Saving…', discard: 'Discard changes', remove: 'Remove week program', reload: 'Reload', unsaved: 'Unsaved changes',
  reloadConfirm: 'Reload and lose the unsaved changes?',
  waiting: 'Waiting for the E32…', retrying: 'Trying again…',
  outdated: 'OpenThermostat was updated. Reload the page (Ctrl+F5) to use the new version of this card.',
  saved: 'Saved on the E32.', removedNote: 'Without a week program the room keeps its fixed temperature of {value}.', rooms: 'Rooms',
  none: 'No rooms yet. Add one on the OpenThermostat dashboard under Settings → Rooms.',
  resetMark: 'Reset time {time}: {value}', states: {active: 'On', follow: 'Heat along only', inactive: 'Off'},
  stateShort: {active: 'on', follow: 'heat along', inactive: 'off'},
  resetNote: 'Reset time: on that moment any manual change ends and the room takes this value; the E32 does not work towards it.',
  resets: 'Reset times', add: 'Reset time', addLabel: 'Add reset time', resetsNone: 'No reset times.', full: 'At most four reset times per room.',
  resetN: 'Reset time {n}', editN: 'Change reset time {n}', removeN: 'Remove reset time {n}',
  time: 'Time', days: 'Days', value: 'Value', temperature: 'Temperature', everyDay: 'Every day', workdays: 'Workdays',
  earlier: '15 minutes earlier', later: '15 minutes later', warmer: 'Half a degree warmer', cooler: 'Half a degree cooler', removeReset: 'Remove', done: 'Done',
  valueHelp: {temperature: 'The room takes this temperature until its next switch time.', active: 'The room can ask for heat.',
   follow: 'The room keeps its target and its radiator valves open for it, but it never asks for heat; it warms while the boiler runs for other rooms.',
   inactive: 'The room asks for no heat.'},
  badTime: 'Type a time such as {example}.', pickDay: 'Choose at least one day.', sameMoment: 'Another reset time is already set for that day and time.',
  dayShort: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], dayNames: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
  textTitle: 'Reset times', textHelp: 'One per line, for example: mon-fri 22:00 14 or daily 23:00 heat along', textApply: 'Apply reset times',
  textBad: 'Line {line} cannot be read: {text}', textOutside: "Line {line}: the temperature is outside the room's temperature limits.",
  textSame: 'Line {line}: another reset time is already set for that day and time.', textApplied: 'Reset times applied.',
  smart: 'Smart warm-up', smartChoices: {house: 'As the house', on: 'On', off: 'Off'},
  smartHelp: {house: 'Follows Smart warm-up of the house (Heating and boiler).', on: 'This room is warm at its switch times.', off: 'This room starts heating at its switch times.'},
  errors: {plan_changed: 'The room plan was changed elsewhere. Reload to see the current program; your changes were not saved.',
   week_changed: 'This week program was changed elsewhere. Reload to see the current program; your changes were not saved.',
   plan_too_large: 'The plan is too large for the E32: use fewer switch times or rooms.', storage_full: 'The E32 storage is full. Remove switch times or a room, then save again.',
   save_unconfirmed: 'The E32 could not confirm the save. Reload and check the program.', room_missing: 'This room no longer exists on the E32. Reload.',
   password_changed: 'The E32 password changed. Reconnect the E32 in the integration settings.', unreachable: 'The E32 cannot be reached. Check the connection and try again.',
   invalid_schedule: 'At most 6 switch times per day, each at a different time.', invalid_schedule_limits: 'Every temperature must lie within the room minimum and maximum.',
   unavailable: 'The E32 room plan is not available for this installation.', unauthorized: 'Only Home Assistant administrators can change week programs.',
   rejected: 'The E32 refused the program. Reload and try again.', editor: 'The week planner could not be loaded. Reload the page (Ctrl+F5) after updating OpenThermostat.',
   not_ready: 'OpenThermostat is still starting or the E32 is not connected yet. This card tries again by itself.',
   disabled: 'This OpenThermostat installation is turned off. Turn it on under Settings → Devices & services → OpenThermostat.',
   unknown_command: 'This page does not match the installed OpenThermostat. Reload the page (Ctrl+F5) after updating OpenThermostat; if that does not help, restart Home Assistant.',
   session_capacity: 'The E32 has too many open sign-ins (for example its own web page in other browsers). This card tries again shortly.',
   try_again_later: 'Too many sign-in attempts on the E32. This card tries again shortly.',
   setup_error: 'OpenThermostat could not start. Open Settings → Devices & services → OpenThermostat to see why, then reload this page.',
   invalid_resets: 'Each reset time needs a time, at least one day and a temperature in whole or half degrees.', too_many_resets: 'At most four reset times per room.',
   resets_outside_limits: 'A reset time\'s temperature is outside the room\'s temperature limits.', resets_same_moment: 'Another reset time is already set for that day and time.',
   gave_up: 'The E32 has not answered for several minutes. Check that it is on and connected, then press Reload.'}},
 nl: {title: 'Weekprogramma', loading: 'Laden…', reading: 'Weekprogramma’s lezen van de E32…', intro: 'De E32 volgt dit programma zelf, ook als Home Assistant offline is.',
  follows: 'Deze ruimte volgt {entity} zolang Home Assistant een gewenste temperatuur geeft; het weekprogramma geldt als die er niet is.',
  save: 'Opslaan op E32', saving: 'Opslaan…', discard: 'Wijzigingen weggooien', remove: 'Weekprogramma verwijderen', reload: 'Opnieuw laden', unsaved: 'Niet opgeslagen wijzigingen',
  reloadConfirm: 'Opnieuw laden en de niet opgeslagen wijzigingen weggooien?',
  waiting: 'Wachten op de E32…', retrying: 'Opnieuw proberen…',
  outdated: 'OpenThermostat is bijgewerkt. Laad de pagina opnieuw (Ctrl+F5) om de nieuwe versie van deze kaart te gebruiken.',
  saved: 'Opgeslagen op de E32.', removedNote: 'Zonder weekprogramma houdt de ruimte de vaste temperatuur van {value} aan.', rooms: 'Ruimtes',
  none: 'Nog geen ruimtes. Voeg er een toe op het OpenThermostat-dashboard via Instellen → Ruimtes.',
  resetMark: 'Terugzetmoment {time}: {value}', states: {active: 'Aan', follow: 'Alleen meeverwarmen', inactive: 'Uit'},
  stateShort: {active: 'aan', follow: 'mee', inactive: 'uit'},
  resetNote: 'Terugzetmoment: op dat moment eindigt een handmatige wijziging en krijgt de ruimte deze waarde; de E32 werkt er niet naartoe.',
  resets: 'Terugzetmomenten', add: 'Terugzetmoment', addLabel: 'Terugzetmoment toevoegen', resetsNone: 'Geen terugzetmomenten.', full: 'Hoogstens vier terugzetmomenten per ruimte.',
  resetN: 'Terugzetmoment {n}', editN: 'Terugzetmoment {n} wijzigen', removeN: 'Terugzetmoment {n} verwijderen',
  time: 'Tijd', days: 'Dagen', value: 'Waarde', temperature: 'Temperatuur', everyDay: 'Elke dag', workdays: 'Werkdagen',
  earlier: '15 minuten eerder', later: '15 minuten later', warmer: 'Halve graad warmer', cooler: 'Halve graad kouder', removeReset: 'Verwijderen', done: 'Klaar',
  valueHelp: {temperature: 'De ruimte krijgt deze temperatuur tot haar volgende schakeltijd.', active: 'De ruimte kan warmte vragen.',
   follow: 'De ruimte houdt de gewenste temperatuur en de radiatorkranen gaan ervoor open, maar ze vraagt nooit warmte; ze warmt mee zolang de ketel voor andere ruimtes stookt.',
   inactive: 'De ruimte vraagt geen warmte.'},
  badTime: 'Typ een tijd, bijvoorbeeld {example}.', pickDay: 'Kies minstens één dag.', sameMoment: 'Op die dag en dat tijdstip staat al een terugzetmoment.',
  dayShort: ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo'], dayNames: ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag'],
  textTitle: 'Terugzetmomenten', textHelp: 'Eén per regel, bijvoorbeeld: ma-vr 22:00 14 of dag 23:00 meeverwarmen', textApply: 'Terugzetmomenten toepassen',
  textBad: 'Regel {line} is niet te lezen: {text}', textOutside: 'Regel {line}: de temperatuur ligt buiten de temperatuurgrenzen van de ruimte.',
  textSame: 'Regel {line}: op die dag en dat tijdstip staat al een terugzetmoment.', textApplied: 'Terugzetmomenten toegepast.',
  smart: 'Slim opwarmen', smartChoices: {house: 'Als het huis', on: 'Aan', off: 'Uit'},
  smartHelp: {house: 'Volgt Slim opwarmen van het huis (Verwarming en ketel).', on: 'Deze ruimte is warm op haar schakeltijden.', off: 'Deze ruimte begint pas op haar schakeltijden met verwarmen.'},
  errors: {plan_changed: 'Het ruimteplan is elders gewijzigd. Laad opnieuw om het huidige programma te zien; je wijzigingen zijn niet opgeslagen.',
   week_changed: 'Dit weekprogramma is elders gewijzigd. Laad opnieuw om het huidige programma te zien; je wijzigingen zijn niet opgeslagen.',
   plan_too_large: 'Het plan is te groot voor de E32: gebruik minder schakeltijden of ruimtes.', storage_full: 'De opslag van de E32 is vol. Verwijder schakeltijden of een ruimte en sla opnieuw op.',
   save_unconfirmed: 'De E32 kon het opslaan niet bevestigen. Laad opnieuw en controleer het programma.', room_missing: 'Deze ruimte bestaat niet meer op de E32. Laad opnieuw.',
   password_changed: 'Het wachtwoord van de E32 is gewijzigd. Verbind de E32 opnieuw in de integratie-instellingen.', unreachable: 'De E32 is niet bereikbaar. Controleer de verbinding en probeer het opnieuw.',
   invalid_schedule: 'Maximaal 6 schakeltijden per dag, elk op een andere tijd.', invalid_schedule_limits: 'Elke temperatuur moet binnen het minimum en maximum van de ruimte liggen.',
   unavailable: 'Het ruimteplan van de E32 is niet beschikbaar voor deze installatie.', unauthorized: 'Alleen beheerders van Home Assistant kunnen weekprogramma’s wijzigen.',
   rejected: 'De E32 weigerde het programma. Laad opnieuw en probeer het nog eens.', editor: 'De weekplanner kon niet worden geladen. Laad de pagina opnieuw (Ctrl+F5) na het bijwerken van OpenThermostat.',
   not_ready: 'OpenThermostat start nog of de E32 is nog niet verbonden. Deze kaart probeert het vanzelf opnieuw.',
   disabled: 'Deze OpenThermostat-installatie staat uit. Zet hem aan via Instellingen → Apparaten en diensten → OpenThermostat.',
   unknown_command: 'Deze pagina past niet bij de geïnstalleerde OpenThermostat. Laad de pagina opnieuw (Ctrl+F5) na het bijwerken van OpenThermostat; helpt dat niet, herstart dan Home Assistant.',
   session_capacity: 'De E32 heeft te veel open aanmeldingen (bijvoorbeeld zijn eigen webpagina in andere browsers). Deze kaart probeert het zo opnieuw.',
   try_again_later: 'Te veel aanmeldpogingen op de E32. Deze kaart probeert het zo opnieuw.',
   setup_error: 'OpenThermostat kon niet starten. Open Instellingen → Apparaten en diensten → OpenThermostat om te zien waarom en laad daarna deze pagina opnieuw.',
   invalid_resets: 'Elk terugzetmoment heeft een tijd, minstens één dag en een temperatuur in hele of halve graden nodig.', too_many_resets: 'Hoogstens vier terugzetmomenten per ruimte.',
   resets_outside_limits: 'De temperatuur van een terugzetmoment ligt buiten de temperatuurgrenzen van de ruimte.', resets_same_moment: 'Op die dag en dat tijdstip staat al een terugzetmoment.',
   gave_up: 'De E32 antwoordt al enkele minuten niet. Controleer of hij aan staat en verbonden is en kies dan Opnieuw laden.'}}};
// The planner's Dutch (week-editor.js T.nl, verbatim but for the two hint lines, one short line each in the HA card:
// the editor takes a host's table over English, so a table it gets must be whole; test/week-editor.test.cjs checks it).
const PLANNER_NL = {days: ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag'], short: ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo'],
  text: ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo'], names: {comfort: 'Comfort', eco: 'Eco', night: 'Nacht'}, levels: 'Temperatuurniveaus',
  warmer: '{level} warmer', cooler: '{level} kouder', custom: 'Eigen temperatuur', template: 'Begin met een sjabloon', choose: 'Kies…',
  templates: {work: 'Werkdagen en weekend', home: 'Thuiswerken', daily: 'Elke dag hetzelfde'}, undo: 'Ongedaan maken',
  applied: '{name} toegepast. Ongedaan maken zet het vorige programma terug.', hint: 'Tik op een blok om het te wijzigen, sleep een lijn om een tijd te verschuiven.',
  empty: 'Nog geen programma: kies een sjabloon om te beginnen.', copyDay: '{day} kopiëren', copyTo: '{day} kopiëren naar', workdays: 'Werkdagen', weekend: 'Weekend', all: 'Alle dagen',
  copy: 'Kopiëren', cancel: 'Annuleren', pickDay: 'Kies minstens één dag.', copied: '{day} gekopieerd.', block: '{day} {from}–{to}', inherited: 'loopt door van de dag ervoor',
  level: 'Niveau', starts: 'Begint om', earlier: '15 minuten eerder', later: '15 minuten later', split: 'Blok splitsen', remove: 'Schakeltijd verwijderen',
  prev: 'Vorig blok', next: 'Volgend blok', close: 'Klaar', full: 'Maximaal 6 schakeltijden per dag.', short15: 'Dit blok is te kort om te splitsen.',
  warmerNight: 'Nacht is nu warmer dan Comfort. Dat mag; controleer of het is wat je wilt.', copyShort: 'Kopiëren…',
  blocks: 'Blokken op {day}', limits: 'Houd temperaturen tussen {min} en {max}.', preview: 'Voorbeeld van de week',
  advanced: 'Geavanceerd: als tekst bewerken', textHelp: 'Eén regel per groep dagen, bijvoorbeeld: ma-vr: 06:30 20,5; 22:30 18', apply: 'Tekst toepassen',
  bad: 'Regel {line} is niet te lezen: {text}', outside: 'Regel {line}: temperaturen moeten tussen {min} en {max} liggen.', many: 'Regel {line}: maximaal 6 schakeltijden per dag.',
  textApplied: 'Tekst toegepast.', inF: 'Temperaturen in °F.',
  warmUp: 'Slim opwarmen staat aan: de ruimte is warm op de tijden die je instelt.',
  warmUpOff: 'Slim opwarmen staat uit: verwarmen begint pas op de tijd die je instelt.'};
// English: the editor's own, but for the two hint lines (one short line each; the warm-up hint names Smart warm-up).
const PLANNER_EN = {hint: 'Tap a block to change it, drag a line to move a time.', warmUp: 'Smart warm-up is on: the room is warm at the times you set.'};
const PLANNER = {en: PLANNER_EN, nl: PLANNER_NL};
// The reset times as text, as the room form reads and writes them (e32_room_flow.format_resets / parse_resets):
// English or Dutch day and state words, the temperature in the user's unit.
const RESET_WORDS = {en: {days: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], every: 'daily', states: {active: 'on', follow: 'heat along', inactive: 'off'}},
 nl: {days: ['ma', 'di', 'wo', 'do', 'vr', 'za', 'zo'], every: 'dag', states: {active: 'aan', follow: 'meeverwarmen', inactive: 'uit'}}};
const TEXT_DAYS = {};
[RESET_WORDS.en.days, RESET_WORDS.nl.days, ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
 ['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag']].forEach(n => n.forEach((d, i) => { TEXT_DAYS[d] = i; }));
const TEXT_EVERY = ['daily', 'every day', 'dag', 'elke dag', 'dagelijks'];
const TEXT_STATES = {on: 'active', aan: 'active', 'heat along': 'follow', 'heat along only': 'follow', meeverwarmen: 'follow', 'alleen meeverwarmen': 'follow', off: 'inactive', uit: 'inactive'};
// The look: the settings panel's tokens (8 px grid, 12 px radius, 22/17/15/13 px text, the status colours of the house
// card, Home Assistant's theme underneath), defined here so the card looks the same without the panel's kit.
const STYLE = `:host{display:block;
/* CONTRACT-1.4.1 §8: the design tokens of the kit, the cards and the planner (the same names and values everywhere). */
--ot-space: 8px;  --ot-radius: 12px;  --ot-radius-s: 8px;  --ot-touch: 44px;  --ot-motion: 150ms ease;
--ot-text-xl: 22px; --ot-line-xl: 28px;   /* values */
--ot-text-l: 17px;  --ot-line-l: 24px;    /* titles */
--ot-text-m: 15px;  --ot-line-m: 22px;    /* body, labels */
--ot-text-s: 13px;  --ot-line-s: 18px;    /* help, meta */
--ot-bg: var(--card-background-color); --ot-fg: var(--primary-text-color); --ot-fg-2: var(--secondary-text-color);
--ot-line: var(--divider-color); --ot-accent: var(--primary-color); --ot-on-accent: var(--text-primary-color, #fff);
/* status colours with meaning: ink = text/icon, fill = label background; light values, then dark */
--ot-heat-ink: #a1500f;      --ot-heat-fill: #fbe9db;     /* heats (orange); 4.85:1 on the fill at 13 px */
--ot-along-ink: #886100;     --ot-along-fill: #f8efcf;    /* heats along only (amber); 4.85:1 */
--ot-water-ink: #1f5fa8;     --ot-water-fill: #dde9f8;    /* hot water (blue) */
--ot-rest-ink: #5f6368;      --ot-rest-fill: #ebedf0;     /* rest, off, summer (grey) */
--ot-attention-ink: #b3261e; --ot-attention-fill: #f9dedc;/* attention (red) */
/* Contrast (§8): white on HA's default accent is only 2.6:1; filled buttons and the chosen segment use --ot-fill, text
   buttons --ot-link (4.8:1). */
--ot-fill: color-mix(in srgb, var(--ot-accent) 72%, black); --ot-link: color-mix(in srgb, var(--ot-accent) 72%, black);
--otw-soft: color-mix(in srgb, var(--ot-fg, #212121) 6%, transparent)}
:host([data-theme="dark"]){--ot-heat-ink: #f0a060; --ot-heat-fill: rgba(240,160,96,.18); --ot-along-ink: #e6c35c; --ot-along-fill: rgba(230,195,92,.18);
      --ot-water-ink: #7fb3f0; --ot-water-fill: rgba(127,179,240,.18); --ot-rest-ink: #b0b4ba; --ot-rest-fill: rgba(176,180,186,.18);
      --ot-attention-ink: #f2857c; --ot-attention-fill: rgba(242,133,124,.18)}
.otw{display:grid;gap:16px;color:var(--ot-fg);font-size:var(--ot-text-m);line-height:var(--ot-line-m);min-width:0}ha-card.otw{padding:24px;max-width:960px;margin:auto;box-sizing:border-box}
@media(max-width:600px){ha-card.otw{padding:16px}}h2{margin:0;font-size:var(--ot-text-xl);font-weight:500;line-height:var(--ot-line-xl)}h3{margin:0;font-size:var(--ot-text-l);line-height:var(--ot-line-l);font-weight:500}p{margin:0}
.muted{color:var(--ot-fg-2);font-size:var(--ot-text-s);line-height:var(--ot-line-s)}
button{font:inherit;font-weight:500;color:inherit;background:transparent;border:1px solid transparent;border-radius:var(--ot-radius);min-height:var(--ot-touch);min-width:var(--ot-touch);padding:0 16px;cursor:pointer;
display:inline-flex;align-items:center;justify-content:center;gap:8px;transition:background-color var(--ot-motion),border-color var(--ot-motion)}
button:disabled{opacity:.45;cursor:default}button:focus-visible{outline:2px solid var(--ot-link);outline-offset:2px}
.primary{background:var(--ot-fill);color:var(--ot-on-accent)}.secondary{border-color:var(--ot-link);color:var(--ot-link)}.text{color:var(--ot-link);padding:0 12px}
.text:not(:disabled):hover,.secondary:not(:disabled):hover,.otw-icon:hover{background:color-mix(in srgb,var(--ot-accent) 8%,transparent)}
svg.i{width:20px;height:20px;fill:currentColor;flex:none}
.tabs{display:flex;flex-wrap:wrap;gap:8px}[role=tab]{border-color:var(--ot-line);border-radius:999px}
[role=tab][aria-selected=true]{background:var(--ot-fill);border-color:var(--ot-fill);color:var(--ot-on-accent);font-weight:600}
.actions{display:flex;flex-wrap:wrap;gap:8px;align-items:center;position:sticky;bottom:0;z-index:4;padding:8px 0;background:var(--ot-bg)}
.otw-embedded .actions{position:static;padding:0}.more{display:flex;flex-wrap:wrap;gap:8px;margin:-8px 0 0 -12px}
.msg:empty{display:none}.msg{border-left:4px solid var(--ot-accent);padding:8px 12px;background:var(--otw-soft);border-radius:8px}.msg.error{border-color:var(--ot-attention-ink)}
.dirty{color:var(--ot-fg-2);font-size:var(--ot-text-s)}.waiting{font-weight:600}
.notice{border-left:4px solid var(--ot-along-ink);padding:8px 12px;background:var(--otw-soft);border-radius:8px}
.skel{display:grid;gap:8px}.skel i{display:block;height:40px;border-radius:8px;background:var(--otw-soft);animation:otw-pulse 1.2s ease-in-out infinite alternate}
@keyframes otw-pulse{to{opacity:.45}}@media(prefers-reduced-motion:reduce){.skel i{animation:none}}
.otw-sec{display:grid;gap:8px;border-top:1px solid var(--ot-line);padding-top:16px}
.otw-seg{display:flex;flex-wrap:wrap;gap:4px;padding:3px;border:1px solid var(--ot-line);border-radius:var(--ot-radius);max-width:100%;box-sizing:border-box;width:fit-content}
.otw-seg button{flex:1 1 auto;border-radius:9px;padding:0 14px}.otw-seg button[aria-pressed=true]{background:var(--ot-fill);color:var(--ot-on-accent);font-weight:600}
.otw-ul{list-style:none;margin:0;padding:0;display:grid}.otw-li{display:grid;grid-template-columns:minmax(0,1fr) auto auto;align-items:center;gap:4px;padding:4px 0;border-bottom:1px solid var(--ot-line)}
.otw-li:last-child{border-bottom:0}.otw-li b{font-size:var(--ot-text-l);line-height:var(--ot-line-l);font-weight:500}.otw-li small{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px;color:var(--ot-fg-2);font-size:var(--ot-text-s);line-height:var(--ot-line-s)}
.otw-status{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:var(--ot-radius);font-size:var(--ot-text-s);line-height:var(--ot-line-s);background:var(--fill);color:var(--ink)}
.otw-status svg.i{width:16px;height:16px}.st-active{--ink:var(--ot-heat-ink);--fill:var(--ot-heat-fill)}.st-follow{--ink:var(--ot-along-ink);--fill:var(--ot-along-fill)}
.st-inactive{--ink:var(--ot-rest-ink);--fill:var(--ot-rest-fill)}.st-temperature{--ink:var(--ot-fg);--fill:var(--ot-rest-fill)}.otw-icon{padding:0;width:44px;color:var(--ot-fg-2)}
.wpe .otw-add{border-color:var(--ot-link);color:var(--ot-link);background:transparent;padding:0 14px 0 10px;display:inline-flex;align-items:center;gap:6px}
.wpe .otw-mk{position:absolute;bottom:-12px;width:44px;height:44px;margin-left:-22px;padding:0;border:0;border-radius:0;background:none;min-height:0;min-width:0;pointer-events:auto;
touch-action:none;user-select:none;-webkit-user-select:none;cursor:grab;z-index:3;--tone:var(--wt)}
.otw-strip{position:absolute;left:0;right:0;bottom:100%;height:0;pointer-events:none}
.wpe .otw-mk{--tone:var(--ink)}
.wpe .otw-pill{position:absolute;top:0;left:50%;transform:translateX(-50%);height:22px;box-sizing:border-box;padding:0 7px;border:1px solid var(--tone);border-radius:11px;background:linear-gradient(var(--fill),var(--fill)),var(--ws);
color:var(--ink);font-size:13px;font-weight:600;line-height:18px;white-space:nowrap}
.wpe .otw-arrow{position:absolute;top:21px;left:16px;width:0;height:0;border-style:solid;border-width:6px 6px 0;border-color:var(--tone) transparent transparent}
.wpe .otw-tick{position:absolute;top:26px;left:21px;width:2px;height:54px;background:var(--wt);box-shadow:0 0 0 1px var(--ws);pointer-events:none}
.wpe .otw-mk[aria-expanded=true] .otw-pill{box-shadow:0 0 0 3px color-mix(in srgb,var(--tone) 40%,transparent)}.wpe .otw-mk.otw-drag{cursor:grabbing}
.wpe .otw-mk:focus-visible{outline:none}.wpe .otw-mk:focus-visible .otw-pill{outline:3px solid var(--wf);outline-offset:2px}span.otw-mk{cursor:default}
.wpe .otw-legend{display:flex;gap:8px;align-items:center;color:var(--wm);font-size:var(--ot-text-s);line-height:var(--ot-line-s);margin-top:-4px}
.wpe .otw-sample{flex:none;width:0;height:0;border-style:solid;border-width:8px 6px 0;border-color:var(--ot-fg-2) transparent transparent}
.wpe .otw-rsmsg{color:var(--ot-along-ink);font-size:var(--ot-text-s);line-height:var(--ot-line-s);padding:4px 10px;background:var(--ot-along-fill);border-radius:var(--ot-radius);justify-self:start}
.wpe .otw-card{border:1px solid var(--ot-line,var(--wl));border-radius:var(--ot-radius);padding:16px;display:grid;gap:16px;background:var(--ot-bg,var(--ws))}.wpe .otw-card h4{font-size:var(--ot-text-l);line-height:var(--ot-line-l);font-weight:500}
.wpe .otw-row{display:grid;gap:8px}.wpe .otw-label{font-size:var(--ot-text-s);color:var(--wm)}.wpe .otw-line{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.wpe .otw-card .otw-time{width:7.5em;text-align:center;font-size:var(--ot-text-l);padding:0 8px}
.wpe .otw-chip{border-radius:999px;padding:0 6px;font-weight:500}.wpe .otw-chip[aria-pressed=true],.wpe .otw-card .otw-seg button[aria-pressed=true]{background:var(--ot-fill);
border-color:var(--ot-fill);color:var(--ot-on-accent);font-weight:600}
.wpe .otw-card .otw-seg{border-color:var(--wl);display:grid;grid-template-columns:repeat(auto-fit,minmax(132px,1fr));width:100%}.wpe .otw-card .otw-seg button{border:0;background:transparent;border-radius:9px;padding:0 12px}
.wpe .otw-quick,.wpe .otw-card .otw-done,.wpe .otw-card .danger{border-color:transparent;background:transparent;color:var(--ot-link)}
.wpe .otw-card .otw-done{border-color:var(--ot-link)}.wpe .otw-card .danger{color:var(--ot-attention-ink);display:inline-flex;align-items:center;gap:6px;padding:0 12px 0 8px}
.wpe .otw-round{border-radius:50%;width:44px;padding:0;display:inline-flex;align-items:center;justify-content:center}.wpe .otw-value{min-width:5em;text-align:center;font-size:var(--ot-text-xl);line-height:var(--ot-line-xl);font-weight:400}
.wpe .otw-help{color:var(--wm);font-size:var(--ot-text-s);line-height:var(--ot-line-s)}.wpe .otw-foot{display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px}
.wpe .otw-rstext{display:grid;gap:4px;margin:8px 0 12px}.wpe .otw-rstext h4{margin-top:8px}.wpe .otw-rstext textarea{min-height:5em;margin:4px 0}
.wpe .otw-rstext .otw-err{color:var(--ot-attention-ink)}.wpe .otw-rstext .otw-err:empty{display:none}`;
// The planner in the same look (after week-editor.js's own styles, so they win; the E32 page keeps its look).
const LOOK = `.wpe{gap:16px;font-size:var(--ot-text-m)}.wpe button,.wpe select,.wpe input,.wpe textarea{border-radius:var(--ot-radius)}.wpe button{font-weight:500}
.wpe small,.wpe .wpe-note{font-size:var(--ot-text-s);line-height:var(--ot-line-s)}.wpe>h4{font-size:var(--ot-text-s);font-weight:500;color:var(--wm);margin-bottom:-8px}
.wpe-lv{border-radius:var(--ot-radius);border-color:transparent;background:var(--ot-rest-fill);padding:0 0 0 12px;gap:0;min-height:44px}.wpe-lv b{min-width:0;font-weight:500;margin-right:4px}
.wpe-lv button{border-color:transparent;border-radius:50%;background:transparent;padding:0;font-size:20px;line-height:1;color:var(--wt)}.wpe-lv button:hover{background:var(--otw-soft)}
.wpe-tools{gap:8px 16px}.wpe-tools label{color:var(--wm);font-size:var(--ot-text-s)}.wpe-tools select{color:var(--wt);font-size:var(--ot-text-m);padding:0 12px}
.wpe-tools [data-k=undo]{border-color:transparent;background:transparent;color:var(--ot-link)}
.wpe-day>button{border-color:transparent;background:transparent;padding:2px 4px;justify-items:start;text-align:left;font-size:var(--ot-text-m);font-weight:600}
.wpe-day>button small{font-size:var(--ot-text-s);font-weight:400;color:var(--wm)}.wpe-day>button:hover{background:var(--w2)}
.wpe-day>button[aria-expanded=true]{background:color-mix(in srgb,var(--ot-accent) 14%,transparent)}
.wpe-axis{font-size:var(--ot-text-s);height:20px}.wpe-seg{font-size:var(--ot-text-s)}.wpe-bar{border-radius:10px}
.wpe-panel{border-color:var(--wl);padding:16px;gap:12px}.wpe-msg{border-left-color:var(--ot-accent)}
.wpe-chart{font-size:var(--ot-text-s);opacity:.85}.wpe-chart svg{height:80px}.wpe-chart line[stroke-width="3"]{stroke-width:2}
.wpe details{border-width:1px 0 0;border-radius:0;padding:0}.wpe summary{color:var(--wm);font-weight:500}`;
// English or Dutch by the Home Assistant language (English otherwise).
const language = hass => (/^nl\b/i.test(hass?.locale?.language || hass?.language || '') ? 'nl' : 'en');
const fill = (s, v) => s.replace(/\{(\w+)\}/g, (a, k) => k in v ? v[k] : a);
const same = (a, b) => JSON.stringify(a ?? null) === JSON.stringify(b ?? null);
const program = week => week && week.some(d => d.length) ? week : null;
// Home Assistant in imperial units: the planner shows and edits °F; the E32 program stays in °C.
const fahrenheit = hass => hass?.config?.unit_system?.temperature === '°F';
const degrees = (hass, centi) => (fahrenheit(hass) ? Math.round(centi * 9 / 50 + 320) / 10 : centi / 100)
 .toLocaleString(hass?.locale?.language || 'en') + (fahrenheit(hass) ? ' °F' : ' °C');
const clock = m => String(m / 60 | 0).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0');
// A time as Home Assistant shows it: its time format, or the language's own (24 hours in Dutch).
const hour12 = hass => {
 const format = hass?.locale?.time_format;
 if (format === '12' || format === '24') return format === '12';
 try { return new Intl.DateTimeFormat(format === 'system' ? undefined : hass?.locale?.language || hass?.language || 'en', {hour: 'numeric'}).resolvedOptions().hour12 === true; }
 catch (e) { return false; }
};
const timeText = (hass, m) => hour12(hass) ? ((m / 60 | 0) % 12 || 12) + ':' + String(m % 60).padStart(2, '0') + (m < 720 ? ' AM' : ' PM') : clock(m);
// A typed time: 22:00, 22.00, 2200, 9:30, 10 pm, 10:15 PM; null when it is not one.
const readTime = text => {
 const m = /^\s*(\d{1,2})(?:[:.]?(\d{2}))?\s*(?:([ap])\.?\s*m?\.?)?\s*$/i.exec(text || '');
 if (!m || (m[2] != null && +m[2] > 59)) return null;
 let hour = +m[1];
 if (m[3]) { if (hour < 1 || hour > 12) return null; hour = hour % 12 + (/p/i.test(m[3]) ? 12 : 0); }
 return hour > 23 ? null : hour * 60 + (m[2] == null ? 0 : +m[2]);
};
// The reset times as the API gives them -> {days, m (minute), state | c (centi °C)}; anything else is left out.
const resetsOf = r => (Array.isArray(r) ? r : []).map(x => x && Array.isArray(x.days) && /^([01]\d|2[0-3]):[0-5]\d$/.test(x.time) && {
 days: [...new Set(x.days.filter(d => Number.isInteger(d) && d >= 0 && d < 7))].sort((a, b) => a - b),
 m: +x.time.slice(0, 2) * 60 + +x.time.slice(3), state: ['active', 'follow', 'inactive'].includes(x.state) ? x.state : null,
 c: Number.isFinite(x.temperature_c) ? Math.round(x.temperature_c * 100) : null}).filter(x => x && x.days.length && (x.state || x.c != null));
const toPlan = x => ({days: [...x.days], time: clock(x.m), ...(x.state ? {state: x.state} : {temperature_c: x.c / 100})});
const copyOf = x => ({...x, days: [...x.days]});
const runs = days => days.reduce((out, d) => { const r = out[out.length - 1]; if (r && r[1] === d - 1) r[1] = d; else out.push([d, d]); return out; }, []);
const resetLine = (x, lang, f) => {
 const w = RESET_WORDS[lang === 'nl' ? 'nl' : 'en'];
 const when = x.days.length === 7 ? w.every : runs(x.days).map(([a, b]) => a === b ? w.days[a] : w.days[a] + '-' + w.days[b]).join(',');
 const shown = String(f ? Math.round(x.c * 9 / 50 + 320) / 10 : x.c / 100);
 return when + ' ' + clock(x.m) + ' ' + (x.state ? w.states[x.state] : lang === 'nl' ? shown.replace('.', ',') : shown);
};
// One reset time per line; an error names the line ({key, line, text}).
const parseResets = (text, min, max, f) => {
 const out = [], taken = new Set();
 (text || '').split(/\r?\n/).forEach((original, n) => {
  const fail = key => { throw {key, line: n + 1, text: original.trim().slice(0, 60)}; };
  const line = original.toLowerCase().replace(/–/g, '-').split(/\s+/).filter(Boolean).join(' ');
  if (!line) return;
  const m = /^(?:([a-z][a-z ,-]*?)\s*:?\s+)?(\d{1,2})[:.](\d{2})\s+(.+)$/.exec(line);
  if (!m || +m[2] > 23 || +m[3] > 59) fail('textBad');
  let days = [0, 1, 2, 3, 4, 5, 6];
  if (m[1] != null && !TEXT_EVERY.includes(m[1].trim())) {
   days = [];
   for (const token of m[1].split(',').map(s => s.trim())) {
    const ends = token.split('-').map(s => s.trim());
    if (ends.length > 2 || ends.some(e => !Object.hasOwn(TEXT_DAYS, e))) fail('textBad');
    const a = TEXT_DAYS[ends[0]], b = TEXT_DAYS[ends[ends.length - 1]];
    for (let s = 0; s <= (b - a + 7) % 7; s++) days.push((a + s) % 7);
   }
   days = [...new Set(days)].sort((a, b) => a - b);
  }
  const x = {days, m: +m[2] * 60 + +m[3], state: null, c: null}, value = m[4].trim();
  if (Object.hasOwn(TEXT_STATES, value)) x.state = TEXT_STATES[value];
  else {
   const t = /^(\d{1,3}(?:[.,]\d{1,2})?)\s*(?:°\s*[cf]?)?$/.exec(value);
   if (!t) fail('textBad');
   const v = parseFloat(t[1].replace(',', '.'));
   x.c = f ? Math.round(Math.round((v - 32) * 500 / 9) / 50) * 50 : Math.round(v * 100);
   if (!f && x.c % 50) fail('textBad');
   if (x.c < min || x.c > max) fail('textOutside');
  }
  if (days.some(d => taken.has(d + '-' + x.m))) fail('textSame');
  days.forEach(d => taken.add(d + '-' + x.m));
  out.push(x);
 });
 return out;
};
// Elements: h('button', {type: 'button', onclick: fn}, 'text', child); null and false children are left out.
const h = (tag, attrs = {}, ...kids) => {
 const e = document.createElement(tag);
 for (const [k, v] of Object.entries(attrs)) {
  if (v == null || v === false) continue;
  if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v === true ? '' : v);
 }
 e.append(...kids.filter(x => x != null && x !== false));
 return e;
};
// Material Design Icons, inline.
const PATH = {plus: 'M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z', minus: 'M19,13H5V11H19V13Z',
 pencil: 'M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z',
 remove: 'M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19M8,9H16V19H8V9M15.5,4L14.5,3H9.5L8.5,4H5V6H19V4H15.5Z',
 thermometer: 'M15 13V5A3 3 0 0 0 9 5V13A5 5 0 1 0 15 13M12 4A1 1 0 0 1 13 5V8H11V5A1 1 0 0 1 12 4Z',
 fire: 'M17.66 11.2C17.43 10.9 17.15 10.64 16.89 10.38C16.22 9.78 15.46 9.35 14.82 8.72C13.33 7.26 13 4.85 13.95 3C13 3.23 12.17 3.75 11.46 4.32C8.87 6.4 7.85 10.07 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C6.87 12.33 6.69 10.28 7.45 8.64C5.78 10 4.87 12.3 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C18.86 17.66 19.5 15 18.56 12.72L18.43 12.46C18.22 12 17.66 11.2 17.66 11.2M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.78 14.43 12.46 13.77 12.33 13C12.21 12.26 12.23 11.63 12.5 10.94C12.69 11.32 12.89 11.7 13.13 12C13.9 13 15.11 13.44 15.37 14.8C15.41 14.94 15.43 15.08 15.43 15.23C15.46 16.05 15.1 16.95 14.5 17.5H14.5Z',
 power: 'M16.56,5.44L15.11,6.89C16.84,7.94 18,9.83 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12C6,9.83 7.16,7.94 8.88,6.88L7.44,5.44C5.36,6.88 4,9.28 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12C20,9.28 18.64,6.88 16.56,5.44M13,3H11V13H13'};
const STATE_ICON = {temperature: 'thermometer', active: 'fire', follow: 'fire', inactive: 'power'};
const icon = name => {
 const ns = 'http://www.w3.org/2000/svg', svg = document.createElementNS(ns, 'svg'), path = document.createElementNS(ns, 'path');
 svg.setAttribute('viewBox', '0 0 24 24'); svg.setAttribute('class', 'i'); svg.setAttribute('aria-hidden', 'true'); path.setAttribute('d', PATH[name]); svg.append(path);
 return svg;
};
const MAX_RESETS = 4, LANE = 28;
let editorReady = null;
// Codes after which the card tries again by itself (HA still starting, E32 not reachable yet).
const RETRY = new Set(['not_ready', 'unreachable', 'session_capacity', 'try_again_later']), RETRY_MS = 15000;
// After this long without an answer the card stops trying by itself and says so (Reload tries again).
const GIVE_UP_MS = 5 * 60000;
// This module's own path: compared with the module the backend serves (a page left open over an update).
const SELF = (() => { try { return new URL(import.meta.url).pathname; } catch (e) { return ''; } })();

class OpenThermostatE32Week extends HTMLElement {
 constructor() {
  super();
  this.attachShadow({mode: 'open'});
  // _drafts: per room the edited program; _levels: per room the planner's state (levels and marks).
  this._rooms = null; this._room = null; this._drafts = {}; this._levels = {}; this._base = {}; this._message = ''; this._error = false; this._busy = false;
  this._waiting = false; this._outdated = false; this._retry = null; this._waitSince = null;
  // 1.4.1: per room the edited reset times (_rs) and Smart warm-up (_sw), the reset time whose card is open (_open),
  // the text view's draft (_rsText); _day: the day last touched in the planner (where "+ Reset time" goes).
  this._rs = {}; this._sw = {}; this._open = null; this._rsMsg = ''; this._rsText = {}; this._rsTextMsg = null; this._day = null; this._dirtyShown = false;
 }
 setConfig(config) {
  if (!config || typeof config.entry_id !== 'string' || !config.entry_id)
   throw new Error('This card needs the entry_id of an OpenThermostat installation: when you add the card by hand, put the ID of the installation in its configuration as entry_id.');
  const changed = !!this._config && this._config.entry_id !== config.entry_id, before = this._config;
  this._config = config;
  // The room screen of the settings panel shows one room (CONTRACT-1.4.1 §4).
  if (typeof config.room_id === 'string' && config.room_id) this._room = config.room_id;
  if (changed && this._hass) { this._rooms = null; this._drafts = {}; this.load(); }
  else if (before && this._rooms && (before.room_id !== config.room_id || before.embedded !== config.embedded)) { this._open = null; this.render(); }
 }
 connectedCallback() { if (this._hass && this._waiting && !this._retry && !this._busy) this.load(); }
 disconnectedCallback() { clearTimeout(this._retry); this._retry = null; }
 getCardSize() { return 12; }
 set hass(hass) {
  const first = !this._hass;
  this._hass = hass;
  this._theme();
  if (first) this.load();
 }
 get t() { return TEXT[language(this._hass)]; }
 get embedded() { return this._config?.embedded === true; }
 // Reset times are edited here only when Home Assistant and the E32 both have them (1.4.1 backend, E32 1.4).
 get editable() { return this._features?.resets === true; }
 // Dark mode (CONTRACT-1.4.1 §8): Home Assistant's theme when it says, else the system's; on the host and the planner.
 get theme() { const dark = this._hass?.themes?.darkMode ?? window.matchMedia?.('(prefers-color-scheme: dark)').matches; return dark ? 'dark' : 'light'; }
 _theme() {
  const theme = this.theme, box = this.shadowRoot.querySelector('.wpe');
  if (theme === 'dark') this.setAttribute('data-theme', 'dark'); else this.removeAttribute('data-theme');
  if (box) box.dataset.theme = theme;
 }
 // When it was saved: the house's clock (Home Assistant's time zone) and the viewer's 12/24-hour choice, as the other cards.
 savedAt() {
  const hass = this._hass, hour12 = ({'12': true, '24': false})[hass?.locale?.time_format], lang = hass?.locale?.language || 'en';
  const options = {hour: hour12 ? 'numeric' : '2-digit', minute: '2-digit', ...(hour12 === undefined ? {} : {hour12})};
  try { return new Date().toLocaleTimeString(lang, {...options, timeZone: hass?.config?.time_zone || undefined}); }
  catch (e) { return new Date().toLocaleTimeString(lang, options); }
 }
 _fail(err) {
  const code = typeof err?.code === 'string' && err.code ? err.code : 'rejected';
  this._message = this.t.errors[code] || this.t.errors.rejected; this._error = true;
  return code;
 }
 _forget() { this._drafts = {}; this._levels = {}; this._base = {}; this._rs = {}; this._sw = {}; this._rsText = {}; this._open = null; this._rsMsg = ''; this._rsTextMsg = null; }
 // fresh: read from the E32 itself (Reload); otherwise Home Assistant answers from the plan it already
 // holds while that plan is current, so opening the page costs the E32 no sign-in.
 async load(fresh = false) {
  clearTimeout(this._retry); this._retry = null;
  if (!this._hass || !this._config) return;
  this._busy = true; this._fresh = fresh; this._message = ''; this.render();
  try {
   editorReady = editorReady || import(EDITOR).then(() => { if (!window.OTWeekEditor) throw {code: 'editor'}; }).catch(e => { editorReady = null; throw e?.code ? e : {code: 'editor'}; });
   const request = {type: 'open_thermostat/e32_week/get', entry_id: this._config.entry_id, ...(fresh ? {fresh: true} : {})};
   const [result] = await Promise.all([this._hass.callWS(request), editorReady]);
   if (!result || !Array.isArray(result.rooms)) throw {code: 'unknown_command'};
   this._rooms = result.rooms; this._forget(); this._waiting = false; this._waitSince = null;
   this._levelsSupported = result.levels_supported === true;
   this._features = result.features && typeof result.features === 'object' ? result.features : null;
   this._smartWarmUp = result.smart_warm_up !== false; // rc.3 Smart warm-up; unknown: on (the default)
   this._outdated = typeof result.card_url === 'string' && !!SELF && result.card_url !== SELF;
   if (this._config.room_id) this._room = this._config.room_id;
   else if (!this._rooms.some(r => r.id === this._room)) this._room = this._rooms[0]?.id ?? null;
  } catch (err) {
   // Still starting or not reachable: say so and try again by itself (never a dead end).
   const code = this._fail(err);
   this._waiting = RETRY.has(code) && !this._rooms;
   if (RETRY.has(code)) {
    this._waitSince = this._waitSince ?? Date.now();
    if (Date.now() - this._waitSince >= GIVE_UP_MS) { this._waiting = false; this._message = this.t.errors.gave_up; }
    else if (this.isConnected) this._retry = setTimeout(() => this.load(fresh), RETRY_MS);
   } else this._waitSince = null;
  }
  this._busy = false; this.render();
 }
 get room() { return this._rooms?.find(r => r.id === this._room); }
 // The room's reset times as shown: the draft, else as loaded.
 _list(r) { return r.id in this._rs ? this._rs[r.id] : resetsOf(r.resets); }
 _smartShown(r) { return this._features?.smart_warm_up === true && ['house', 'on', 'off'].includes(r?.smart_warm_up); }
 _smart(r) { return r.id in this._sw ? this._sw[r.id] : r.smart_warm_up; }
 // Smart warm-up in effect for the room: its own choice, else the house switch (the planner's hint line says it).
 _warm(r) { const own = this._smartShown(r) ? this._smart(r) : 'house'; return own === 'on' ? true : own === 'off' ? false : this._smartWarmUp !== false; }
 // Changed: another program, reset times or Smart warm-up, or (E32 with stored levels) other levels or marks.
 changed(r) {
  if (!r) return false;
  if (r.id in this._drafts && !same(program(this._drafts[r.id]), r.schedule)) return true;
  if (r.id in this._rs && !same(this._rs[r.id].map(toPlan), resetsOf(r.resets).map(toPlan))) return true;
  if (r.id in this._sw && this._sw[r.id] !== r.smart_warm_up) return true;
  const st = this._levels[r.id], base = this._base[r.id];
  return !!st && !!base && this._levelsSupported && (!same(st.levels, base.levels) || st.schedule_levels !== base.schedule_levels);
 }
 get dirty() { return this.changed(this.room); }
 // Any room with unsaved changes (its tab says so; Reload asks before it drops them).
 get anyDirty() { return (this._rooms || []).some(r => this.changed(r)); }
 _tabs() {
  for (const tab of this.shadowRoot.querySelectorAll('[data-tab]')) {
   const r = this._rooms?.find(x => x.id === tab.dataset.tab), changed = this.changed(r);
   tab.textContent = r ? r.name + (changed ? ' •' : '') : tab.textContent;
   if (changed) tab.setAttribute('aria-label', r.name + ', ' + this.t.unsaved); else tab.removeAttribute('aria-label');
  }
 }
 async save() {
  const r = this.room;
  if (!r || this._busy) return;
  this._busy = true; this._message = ''; this.refresh();
  try {
   const st = this._levels[r.id], schedule = program(r.id in this._drafts ? this._drafts[r.id] : r.schedule);
   // 1.4.1: the reset times and Smart warm-up as shown go with the program (also unchanged), guarded as loaded.
   const resets = this.editable, smart = this._smartShown(r);
   const result = await this._hass.callWS({type: 'open_thermostat/e32_week/save', entry_id: this._config.entry_id, room_id: r.id, schedule,
    expected: resets || smart ? {schedule: r.schedule, ...(resets ? {resets: r.resets} : {}), ...(smart ? {smart_warm_up: r.smart_warm_up} : {})} : r.schedule,
    ...(this._levelsSupported && st ? {levels: st.levels, schedule_levels: st.schedule_levels} : {}),
    ...(resets ? {resets: this._list(r).map(toPlan)} : {}), ...(smart ? {smart_warm_up: this._smart(r)} : {})});
   this._rooms = result.rooms; delete this._drafts[r.id]; delete this._levels[r.id]; delete this._base[r.id];
   delete this._rs[r.id]; delete this._sw[r.id]; delete this._rsText[r.id]; this._open = null; this._rsMsg = ''; this._rsTextMsg = null;
   if (result.features && typeof result.features === 'object') this._features = result.features;
   this._message = this.t.saved + ' ✓ ' + this.savedAt(); this._error = false;
   if (!program(this.room?.schedule)) this._message += ' ' + fill(this.t.removedNote, {value: degrees(this._hass, r.fallback_centi_c)});
   this._busy = false; this.render();
  } catch (err) { this._fail(err); this._busy = false; this.refresh(); }
 }
 // Buttons and messages only, so the planner keeps its focus and selection while editing.
 refresh() {
  const root = this.shadowRoot, t = this.t, dirty = this.dirty, r = this.room;
  const msg = root.querySelector('.msg');
  if (msg) { msg.textContent = this._message; msg.className = 'msg' + (this._error ? ' error' : ''); }
  const state = root.querySelector('.dirty');
  if (state) state.textContent = dirty ? t.unsaved : '';
  const save = root.querySelector('[data-save]');
  if (save) { save.disabled = !dirty || this._busy; save.textContent = this._busy ? t.saving : t.save; }
  const discard = root.querySelector('[data-discard]');
  if (discard) discard.disabled = !dirty || this._busy;
  const remove = root.querySelector('[data-remove]');
  if (remove && r) remove.disabled = this._busy || !program(this._room in this._drafts ? this._drafts[this._room] : r.schedule);
  this._tabs();
  // The room screen warns before leaving with unsaved changes: tell it whenever that changes (CONTRACT-1.4.1 §4).
  const shown = this.embedded ? dirty : this.anyDirty;
  if (shown !== this._dirtyShown) {
   this._dirtyShown = shown;
   this.dispatchEvent(new CustomEvent('openthermostat-week-dirty', {detail: {dirty: shown}, bubbles: true, composed: true}));
  }
 }
 // Draw the planner again (its own render calls _decorate) and what is below it.
 _sync() { this._planner?.render(); this._below(); this.refresh(); }
 _change(r, i, patch) {
  const list = this._list(r).map(copyOf), next = {...list[i], ...patch};
  if (!next.days.length) { this._rsMsg = this.t.pickDay; return this._sync(); }
  if (list.some((y, j) => j !== i && y.m === next.m && y.days.some(d => next.days.includes(d)))) { this._rsMsg = this.t.sameMoment; return this._sync(); }
  list[i] = next; this._rs[r.id] = list; this._rsMsg = ''; this._sync();
 }
 _remove(r, i) {
  this._rs[r.id] = this._list(r).filter((x, j) => j !== i).map(copyOf);
  this._open = null; this._rsMsg = ''; this._sync();
  this.shadowRoot.querySelector('[data-k="rs-add"]')?.focus();
 }
 // A temperature for a new reset time: the room's Night level, in half degrees within its limits.
 _defaultC(r) {
  const lo = Math.ceil(r.minimum_centi_c / 50) * 50, hi = Math.floor(r.maximum_centi_c / 50) * 50, night = this._planner?.levels?.().night ?? 1600;
  return Math.max(lo, Math.min(hi, Math.round(night / 50) * 50));
 }
 // "+ Reset time": on the day last touched (else today) at 22:00, or the first free quarter after it.
 _add(r) {
  const list = this._list(r);
  if (list.length >= MAX_RESETS) { this._rsMsg = this.t.full; return this._sync(); }
  const day = this._day ?? (new Date().getDay() + 6) % 7;
  let m = 1320;
  for (let k = 0; k < 96 && list.some(x => x.m === m && x.days.includes(day)); k++) m = (m + 15) % 1440;
  this._closePanels();
  this._rs[r.id] = [...list.map(copyOf), {days: [day], m, state: null, c: this._defaultC(r)}];
  this._open = {room: r.id, i: list.length}; this._rsMsg = ''; this._sync();
  this.shadowRoot.querySelector('[data-k="rs-time"]')?.focus();
 }
 // One panel at a time: the planner's own block or copy panel closes.
 _closePanels() { this.shadowRoot.querySelector('.wpe-panel [data-k="close"], .wpe-panel [data-k="copy-cancel"]')?.click(); }
 _select(r, i) {
  this._closePanels();
  this._open = this._open?.room === r.id && this._open.i === i ? null : {room: r.id, i}; this._rsMsg = ''; this._sync();
 }
 // After every render of the planner: the "+ Reset time" button, the markers on the day bars, the legend, the open
 // reset time's card and the reset times in the text view.
 _decorate(root, r) {
  const t = this.t, list = this._list(r), editable = this.editable;
  if (!root.dataset.otw) {
   root.dataset.otw = '1';
   // The day last touched (a block, a list day, a day's copy button); touching the planner closes the reset card.
   root.addEventListener('click', e => {
    const k = e.target.closest?.('[data-k]')?.getAttribute('data-k') || '', m = /^(seg|row|listday|day)(\d)/.exec(k);
    if (!m) return;
    this._day = +m[2];
    if (this._open && m[1] !== 'listday') { this._open = null; this._rsMsg = ''; }
   }, true);
  }
  const tools = root.querySelector('.wpe-tools');
  if (editable && tools) tools.append(h('button', {type: 'button', class: 'otw-add', 'data-k': 'rs-add', title: t.addLabel, onclick: () => this._add(this.room)}, icon('plus'), t.add));
  root.querySelectorAll('.wpe-bar').forEach((bar, d) => {
   const marks = list.map((x, i) => [x, i]).filter(([x]) => x.days.includes(d));
   if (marks.length) bar.append(h('div', {class: 'otw-strip'}, ...marks.map(([x, i]) => this._marker(r, x, i, d))));
  });
  let after = root.querySelector('.wpe-grid');
  const add = node => { after.after(node); after = node; };
  if (list.length) add(h('p', {class: 'otw-legend reset-note'}, h('span', {class: 'otw-sample', 'aria-hidden': 'true'}), t.resetNote));
  if (this._rsMsg) add(h('p', {class: 'otw-rsmsg', role: 'status'}, this._rsMsg));
  if (editable && this._open?.room === r.id && list[this._open.i]) add(this._card(r, list, this._open.i));
  const details = root.querySelector('details[data-k="text"]');
  if (editable && details) details.append(this._textBlock(r, list));
  this._layout(root);
 }
 _marker(r, x, i, d) {
  const t = this.t, hass = this._hass, edit = this.editable;
  const name = fill(t.resetMark, {time: timeText(hass, x.m), value: x.state ? t.states[x.state] : degrees(hass, x.c)});
  const mk = h(edit ? 'button' : 'span', {class: 'otw-mk st-' + (x.state || 'temperature'), style: 'left:' + x.m / 14.4 + '%', title: name, 'aria-label': name,
   'data-k': 'rs' + d + '-' + i, 'data-i': i, 'data-m': x.m, ...(edit ? {type: 'button', 'aria-expanded': String(this._open?.room === r.id && this._open.i === i)} : {role: 'img'})},
  h('span', {class: 'otw-pill'}, x.state ? t.stateShort[x.state] : degrees(hass, x.c).slice(0, -3) + '°'),
  h('span', {class: 'otw-arrow'}), h('span', {class: 'otw-tick'}));
  if (!edit) return mk;
  // Drag: 15-minute steps, every day of this reset time moves along; a tap opens its card.
  mk.addEventListener('pointerdown', e => {
   if (e.button) return;
   this._dragged = false;
   const bar = mk.closest('.wpe-bar'), wpe = mk.closest('.wpe'), width = bar.getBoundingClientRect().width, x0 = e.clientX, pill = mk.firstChild;
   let minute = x.m, moved = false;
   try { mk.setPointerCapture(e.pointerId); } catch (err) { /* a synthetic event */ }
   const move = ev => {
    if (!moved && Math.abs(ev.clientX - x0) < 6) return;
    moved = true; mk.classList.add('otw-drag');
    minute = Math.max(0, Math.min(1425, Math.round((x.m + (ev.clientX - x0) / width * 1440) / 15) * 15));
    for (const other of wpe.querySelectorAll('.otw-mk[data-i="' + i + '"]')) other.style.left = minute / 14.4 + '%';
    pill.textContent = timeText(hass, minute);
   };
   const end = ev => {
    mk.removeEventListener('pointermove', move); mk.removeEventListener('pointerup', end); mk.removeEventListener('pointercancel', end);
    if (!moved) return;
    this._dragged = true; // the click that may follow a drag opens nothing (however late it comes)
    if (ev.type === 'pointerup' && minute !== x.m) this._change(r, i, {m: minute}); else this._sync();
   };
   mk.addEventListener('pointermove', move); mk.addEventListener('pointerup', end); mk.addEventListener('pointercancel', end);
  });
  mk.addEventListener('click', () => { if (this._dragged) this._dragged = false; else this._select(r, i); });
  // Keyboard: the arrow keys move it by 15 minutes, as a drag does.
  mk.addEventListener('keydown', e => {
   this._dragged = false;
   const by = {ArrowLeft: -15, ArrowRight: 15}[e.key];
   if (!by) return;
   e.preventDefault();
   const m = Math.max(0, Math.min(1439, x.m + by));
   if (m !== x.m) this._change(r, i, {m});
  });
  return mk;
 }
 // Markers measured in place: each label centred on its time within the bar, touching ones a lane higher; the row
 // makes room above its bar. The hour axis gets more hours where there is room.
 _layout(root) {
  const axis = root.querySelector('.wpe-axis');
  if (axis && axis.clientWidth) {
   const hours = axis.clientWidth >= 420 ? [0, 3, 6, 9, 12, 15, 18, 21, 24] : [0, 6, 12, 18, 24];
   if (axis.dataset.hours !== String(hours.length)) {
    axis.dataset.hours = hours.length;
    axis.replaceChildren(...hours.map(x => h('span', {style: 'left:' + x / 0.24 + '%'}, String(x).padStart(2, '0'))));
   }
  }
  for (const strip of root.querySelectorAll('.otw-strip')) {
   const bar = strip.parentElement.getBoundingClientRect(), ends = [];
   if (!bar.width) continue;
   for (const mk of [...strip.children].sort((a, b) => a.dataset.m - b.dataset.m)) {
    const pill = mk.firstChild, w = pill.offsetWidth, x = bar.left + bar.width * mk.dataset.m / 1440;
    const left = Math.max(bar.left, Math.min(bar.right - w, x - w / 2));
    let lane = ends.findIndex(e => e + 4 <= left);
    if (lane < 0) lane = ends.length;
    ends[lane] = left + w;
    // The touch area (44 px) stays inside the bar too; the arrow and its line stay on the time.
    const shift = Math.min(0, bar.right - x - 22) + Math.max(0, bar.left - x + 22);
    mk.style.marginLeft = shift - 22 + 'px'; mk.children[1].style.left = 16 - shift + 'px'; mk.children[2].style.left = 21 - shift + 'px';
    pill.style.left = left - (x - 22 + shift) + 'px'; pill.style.transform = 'none';
    mk.style.bottom = -12 + lane * LANE + 'px'; mk.style.zIndex = 10 - lane;
    mk.querySelector('.otw-tick').style.height = 54 + lane * LANE + 'px';
   }
   strip.parentElement.parentElement.style.paddingTop = ends.length * LANE + 6 + 'px';
  }
 }
 // The card of one reset time: time, days, value; Remove and Done.
 _card(r, list, i) {
  const t = this.t, hass = this._hass, x = list[i], kind = x.state || 'temperature';
  const lo = Math.ceil(r.minimum_centi_c / 50) * 50, hi = Math.floor(r.maximum_centi_c / 50) * 50;
  const time = h('input', {type: 'text', class: 'otw-time', value: timeText(hass, x.m), 'aria-label': t.time, 'data-k': 'rs-time', autocomplete: 'off', spellcheck: 'false',
   inputmode: hour12(hass) ? 'text' : 'numeric'});
  time.addEventListener('change', () => {
   const m = readTime(time.value);
   if (m == null) { this._rsMsg = fill(t.badTime, {example: timeText(hass, 1320)}); this._sync(); } else this._change(r, i, {m});
  });
  const toggle = d => this._change(r, i, {days: x.days.includes(d) ? x.days.filter(y => y !== d) : [...x.days, d].sort((a, b) => a - b)});
  const label = (text, id) => h('span', {class: 'otw-label', id}, text);
  const id = 'otw-rs-' + i;
  return h('div', {class: 'otw-card', role: 'group', 'aria-label': fill(t.resetN, {n: i + 1}), 'data-k': 'rs-card'},
   h('h4', {}, fill(t.resetN, {n: i + 1})),
   h('div', {class: 'otw-row'}, label(t.time, id + '-t'), h('div', {class: 'otw-line'},
    h('button', {type: 'button', class: 'otw-round', 'aria-label': t.earlier, 'data-k': 'rs-earlier', disabled: x.m < 15, onclick: () => this._change(r, i, {m: x.m - 15})}, icon('minus')),
    time,
    h('button', {type: 'button', class: 'otw-round', 'aria-label': t.later, 'data-k': 'rs-later', disabled: x.m > 1424, onclick: () => this._change(r, i, {m: x.m + 15})}, icon('plus')))),
   h('div', {class: 'otw-row', role: 'group', 'aria-labelledby': id + '-d'}, label(t.days, id + '-d'), h('div', {class: 'otw-line'},
    ...t.dayShort.map((s, d) => h('button', {type: 'button', class: 'otw-chip', 'aria-pressed': String(x.days.includes(d)), 'aria-label': t.dayNames[d], 'data-k': 'rs-day' + d, onclick: () => toggle(d)}, s)),
    h('button', {type: 'button', class: 'otw-quick', 'data-k': 'rs-every', onclick: () => this._change(r, i, {days: [0, 1, 2, 3, 4, 5, 6]})}, t.everyDay),
    h('button', {type: 'button', class: 'otw-quick', 'data-k': 'rs-workdays', onclick: () => this._change(r, i, {days: [0, 1, 2, 3, 4]})}, t.workdays))),
   h('div', {class: 'otw-row'}, label(t.value, id + '-v'),
    h('div', {class: 'otw-seg', role: 'group', 'aria-labelledby': id + '-v'}, ...['temperature', 'active', 'follow', 'inactive'].map(v => h('button', {type: 'button', 'aria-pressed': String(kind === v),
     'data-k': 'rs-v-' + v, onclick: () => this._change(r, i, v === 'temperature' ? {state: null, c: x.c ?? this._defaultC(r)} : {state: v})}, v === 'temperature' ? t.temperature : t.states[v]))),
    kind === 'temperature' && h('div', {class: 'otw-line'},
     h('button', {type: 'button', class: 'otw-round', 'aria-label': t.cooler, 'data-k': 'rs-cooler', disabled: x.c - 50 < lo, onclick: () => this._change(r, i, {c: Math.min(hi, x.c - 50)})}, icon('minus')),
     h('output', {class: 'otw-value', 'aria-live': 'polite'}, degrees(hass, x.c)),
     h('button', {type: 'button', class: 'otw-round', 'aria-label': t.warmer, 'data-k': 'rs-warmer', disabled: x.c + 50 > hi, onclick: () => this._change(r, i, {c: Math.max(lo, x.c + 50)})}, icon('plus'))),
    h('p', {class: 'otw-help'}, t.valueHelp[kind])),
   h('div', {class: 'otw-foot'},
    h('button', {type: 'button', class: 'danger', 'data-k': 'rs-remove', onclick: () => this._remove(r, i)}, icon('remove'), t.removeReset),
    h('button', {type: 'button', class: 'otw-done', 'data-k': 'rs-done', onclick: () => { this._open = null; this._rsMsg = ''; this._sync(); this.shadowRoot.querySelector('[data-k="rs' + x.days[0] + '-' + i + '"]')?.focus(); }}, t.done)));
 }
 // "Advanced: edit as text": the reset times as the room form writes them, under the program text.
 _textBlock(r, list) {
  const t = this.t, lang = language(this._hass), f = fahrenheit(this._hass), note = this._rsTextMsg?.room === r.id ? this._rsTextMsg : null;
  const area = h('textarea', {'aria-label': t.textTitle, spellcheck: 'false', 'data-k': 'rs-textarea', rows: 4});
  area.value = this._rsText[r.id] ?? list.map(x => resetLine(x, lang, f)).join('\n');
  area.addEventListener('input', () => { this._rsText[r.id] = area.value; });
  const apply = () => {
   try {
    const next = parseResets(area.value, r.minimum_centi_c, r.maximum_centi_c, f);
    if (next.length > MAX_RESETS) throw {key: 'full'};
    this._rs[r.id] = next; delete this._rsText[r.id]; this._open = null; this._rsMsg = ''; this._rsTextMsg = {room: r.id, text: t.textApplied};
   } catch (err) {
    if (!err?.key) throw err;
    this._rsText[r.id] = area.value; this._rsTextMsg = {room: r.id, text: fill(t[err.key], {line: err.line, text: err.text}), error: true};
   }
   this._sync();
  };
  return h('div', {class: 'otw-rstext'}, h('h4', {}, t.textTitle), h('small', {}, t.textHelp), area,
   h('p', {class: 'otw-err', role: 'alert'}, note?.error ? note.text : ''), note && !note.error ? h('p', {class: 'wpe-note', role: 'status'}, note.text) : null,
   h('button', {type: 'button', 'data-k': 'rs-text-apply', onclick: apply}, t.textApply));
 }
 // Under the planner: the reset times as a list (the second way, for a keyboard, a screen reader or a phone) and the
 // room's own Smart warm-up.
 _below() {
  const box = this._belowBox, r = this.room, t = this.t, hass = this._hass;
  if (!box || !r) return;
  const focus = this.shadowRoot.activeElement?.closest?.('.otw-below') ? this.shadowRoot.activeElement.getAttribute('data-k') : null, parts = [];
  if (this.editable) {
   const list = this._list(r), days = d => d.length === 7 ? t.everyDay : d.join() === '0,1,2,3,4' ? t.workdays : runs(d).map(([a, b]) => a === b ? t.dayShort[a] : t.dayShort[a] + '–' + t.dayShort[b]).join(', ');
   parts.push(h('section', {class: 'otw-sec otw-resets'}, h('h3', {}, t.resets), list.length ? h('ul', {class: 'otw-ul'}, ...list.map((x, i) => h('li', {class: 'otw-li', 'data-k': 'rs-row' + i},
    h('div', {}, h('b', {}, timeText(hass, x.m)), h('small', {}, days(x.days),
     h('span', {class: 'otw-status st-' + (x.state || 'temperature')}, icon(STATE_ICON[x.state || 'temperature']), x.state ? t.states[x.state] : degrees(hass, x.c)))),
    h('button', {type: 'button', class: 'otw-icon', 'aria-label': fill(t.editN, {n: i + 1}), title: fill(t.editN, {n: i + 1}), 'data-k': 'rs-edit' + i, onclick: () => {
     this._open = {room: r.id, i}; this._rsMsg = ''; this._sync();
     const time = this.shadowRoot.querySelector('[data-k="rs-time"]');
     time?.scrollIntoView?.({block: 'center'}); time?.focus();
    }}, icon('pencil')),
    h('button', {type: 'button', class: 'otw-icon', 'aria-label': fill(t.removeN, {n: i + 1}), title: fill(t.removeN, {n: i + 1}), 'data-k': 'rs-del' + i, onclick: () => this._remove(r, i)}, icon('remove')))))
     : h('p', {class: 'muted'}, t.resetsNone)));
  }
  if (this._smartShown(r)) {
   const choice = this._smart(r);
   parts.push(h('section', {class: 'otw-sec otw-smart'}, h('h3', {id: 'otw-sw'}, t.smart),
    h('div', {class: 'otw-seg', role: 'group', 'aria-labelledby': 'otw-sw'}, ...['house', 'on', 'off'].map(v => h('button', {type: 'button', 'aria-pressed': String(choice === v), 'data-k': 'sw-' + v,
     onclick: () => { this._sw[r.id] = v; this._planner?.smartWarmUp(this._warm(r)); this._below(); this.refresh(); }}, t.smartChoices[v]))),
    h('p', {class: 'muted'}, t.smartHelp[choice])));
  }
  box.replaceChildren(...parts);
  if (focus) box.querySelector('[data-k="' + focus + '"]')?.focus();
 }
 render() {
  const t = this.t, root = this.shadowRoot, embedded = this.embedded;
  const card = h(embedded ? 'div' : 'ha-card', {class: embedded ? 'otw otw-embedded' : 'otw'});
  root.replaceChildren(h('style', {}, STYLE), card);
  this._planner = null; this._belowBox = null;
  if (!embedded) card.append(h('h2', {}, t.title));
  if (this._outdated) card.append(h('p', {class: 'notice', role: 'status'}, t.outdated));
  const msg = h('p', {class: 'msg', role: 'status', 'aria-live': 'polite'});
  if (!this._rooms) {
   const status = this._waiting ? (this._busy ? t.retrying : t.waiting) : this._busy ? (this._fresh ? t.reading : t.loading) : '';
   if (this._busy && !this._waiting) card.append(h('div', {class: 'skel', 'aria-hidden': 'true'}, ...Array.from({length: 4}, () => h('i'))));
   card.append(h('p', {class: this._waiting ? 'waiting' : 'muted'}, status), msg);
   if (!this._busy) { const again = h('button', {type: 'button', class: 'secondary'}, t.reload); again.onclick = () => { this._waitSince = null; this.load(true); }; card.append(again); }
   return this.refresh();
  }
  if (!this._rooms.length) { card.append(h('p', {class: 'muted'}, t.none)); return; }
  const r = this.room;
  if (!r) { card.append(h('p', {class: 'msg error', role: 'status'}, t.errors.room_missing)); return; }
  if (!embedded) card.append(h('p', {class: 'muted'}, t.intro));
  if (!embedded && this._rooms.length > 1) {
   const tabs = h('div', {class: 'tabs', role: 'tablist', 'aria-label': t.rooms});
   for (const x of this._rooms) {
    const tab = h('button', {type: 'button', role: 'tab', 'aria-selected': String(x.id === this._room), 'data-tab': x.id}, x.name);
    tab.onclick = () => { this._room = x.id; this._message = ''; this._open = null; this._rsMsg = ''; this.render(); };
    tabs.append(tab);
   }
   card.append(tabs);
  }
  // The setting device by the name the user knows it by (its entity ID while Home Assistant has no state for it).
  if (r.setpoint_entity) card.append(h('p', {class: 'muted'}, fill(t.follows, {entity: this._hass?.states?.[r.setpoint_entity]?.attributes?.friendly_name || r.setpoint_entity})));
  const host = h('div', {class: 'otw-planner'});
  card.append(host);
  const week = this._room in this._drafts ? this._drafts[this._room] : r.schedule, st = this._levels[r.id];
  // The room's stored levels (or, before its first program, the former house settings); none: inferred.
  this._planner = window.OTWeekEditor.mount(host, {week: week || Array.from({length: 7}, () => []), min: r.minimum_centi_c, max: r.maximum_centi_c,
   lang: language(this._hass), text: PLANNER[language(this._hass)], fahrenheit: fahrenheit(this._hass), theme: this.theme,
   levels: st ? st.levels : r.levels, scheduleLevels: st ? st.schedule_levels : r.schedule_levels, smartWarmUp: this._warm(r),
   onChange: (w, state) => { this._drafts[r.id] = w; if (state) this._levels[r.id] = state; this._message = ''; this.refresh(); },
   onLevels: () => { this._levels[r.id] = this._planner.state(); this._message = ''; this.refresh(); },
   decorate: wpe => this._decorate(wpe, r)});
  host.append(h('style', {}, LOOK));
  this._layout(host);
  this._ro?.disconnect();
  if (window.ResizeObserver) { this._ro = new ResizeObserver(() => requestAnimationFrame(() => this._layout(host))); this._ro.observe(host); }
  // What the planner showed at load: levels and marks are compared with this, not with the stored fields.
  if (!(r.id in this._base)) this._base[r.id] = this._planner.state();
  this._belowBox = h('div', {class: 'otw-below', style: 'display:grid;gap:16px'});
  card.append(this._belowBox);
  this._below();
  const actions = h('div', {class: 'actions'}), save = h('button', {type: 'button', class: 'primary', 'data-save': ''}, t.save);
  const discard = h('button', {type: 'button', class: 'text', 'data-discard': ''}, t.discard), remove = h('button', {type: 'button', class: 'text', 'data-remove': ''}, t.remove);
  const reload = h('button', {type: 'button', class: 'text'}, t.reload);
  save.onclick = () => this.save();
  discard.onclick = () => {
   delete this._drafts[r.id]; delete this._levels[r.id]; delete this._base[r.id]; delete this._rs[r.id]; delete this._sw[r.id]; delete this._rsText[r.id];
   this._open = null; this._rsMsg = ''; this._rsTextMsg = null; this._message = ''; this.render();
  };
  remove.onclick = () => { this._drafts[r.id] = Array.from({length: 7}, () => []); this._message = ''; this.render(); };
  reload.onclick = () => {
   // Reloading reads the E32's programs again and drops every draft: never without asking.
   if (this.anyDirty && !window.confirm(t.reloadConfirm)) return;
   this._waitSince = null; this.load(true);
  };
  // Only saving and discarding stay in view at the bottom (four wrapped buttons covered a quarter of a phone
  // screen); removing the program and reading the E32 again are below it, away from Save.
  actions.append(save, discard, h('span', {class: 'dirty', role: 'status'}));
  card.append(actions, msg, h('div', {class: 'more'}, remove, reload));
  this.refresh();
 }
}
// Other dashboard cards (HACS resources) may later replace window.customElements with a scoped-registry
// polyfill whose get() does not see elements defined before it; Home Assistant then reports "Custom element
// doesn't exist". So: define now, and again (a fresh subclass) whenever the registry in use lacks the element.
// Never throws.
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
 // A HACS card may replace window.customElements later (the owner's HA, 31 Oct 2026: an intermittent
 // "Configuration error" on the week view): a cheap check every 0.5 s puts the element back in the registry in
 // use, and Home Assistant's error card then rebuilds the card. 1.4.2 (P22): only for the first 30 s, when the other
 // cards load; after that a navigation (location-changed) or the page coming back into view checks again, so no
 // timer runs for ever on a wall tablet.
 const timer = setInterval(check, 500);
 setTimeout(() => clearInterval(timer), 30000);
 document.addEventListener('visibilitychange', check);
 return check;
};
ensureDefined('openthermostat-e32-week', OpenThermostatE32Week);
