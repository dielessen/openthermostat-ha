/* The settings panel's section House (1.4; 1.4.1 phase 2, HA-INSTELPANEEL-FASE2.nl.md 3.2): only what belongs to the house:
   who lives here and the away temperature, the house mode with the planned holidays ("Stop holiday" while one runs), and
   the values a new room starts with (each can be changed per room on the room screen). The window and door contacts are on
   the room screen now; an old link to them opens the room. Backend settings_house.py; dates and times in Home Assistant's
   language and time format (the kit). Texts: TEXTS, English key (test/ha-settings-texts.test.cjs). 1.4.2: a screen is known
   by its model's ``screen`` ("presence", "defaults", "mode"), never by one of its fields (P4); the length of a manual change
   is gone (a manual change lasts until the next switch time). */
const TEXTS = {
 nl: {
  'Summer': 'Zomer',
  'Summer mode: the heating stays off until you switch this off; hot water and frost protection stay.': 'Zomerstand: de verwarming staat uit tot je dit uitzet; warm water en vorstbeveiliging blijven.',
  'House': 'Huis',
  'Presence and away temperature': 'Aanwezigheid en afwezigheidstemperatuur',
  'Room defaults': 'Standaardwaarden voor ruimtes',
  'House mode and holiday': 'Huismodus en vakantie',
  'Nobody chosen yet': 'Nog niemand gekozen',
  'Away after {n} min': 'Afwezig na {n} min',
  'Away after {n} min · {temperature} when nobody is home': 'Afwezig na {n} min · {temperature} als niemand thuis is',
  'Without a week program: comfort {comfort}, night {night}': 'Zonder weekprogramma: comfort {comfort}, nacht {night}',
  'Pause after a window {window} min, after a door {door} min': 'Pauze na een raam {window} min, na een deur {door} min',
  'Next holiday: {from} – {until}': 'Volgende vakantie: {from} – {until}',
  'No holidays planned.': 'Geen vakanties gepland.',
  'The E32 does not report the house mode yet.': 'De E32 meldt de huismodus nog niet.',
  'In the house mode Automatic the rooms go to the away temperature when everyone is away. Someone home, or someone whose place is not known, keeps the house warm.': 'In de huismodus Automatisch gaan de ruimtes naar de afwezigheidstemperatuur als iedereen weg is. Iemand thuis, of iemand van wie niet bekend is waar die is, houdt het huis warm.',
  'Who lives here': 'Wie hier woont',
  'Optional. The people of the house, or a group, zone (for example zone.home), device tracker or switch that is on while someone is home.': 'Optioneel. De mensen van het huis, of een groep, zone (bijvoorbeeld zone.home), apparaattracker of schakelaar die aan is als er iemand thuis is.',
  'Away after': 'Afwezig na',
  'Minutes everyone must be away before the house counts as away, so a short errand does not cool the house. 0: at once.': 'Minuten dat iedereen weg moet zijn voordat het huis als afwezig telt, zodat een korte boodschap het huis niet laat afkoelen. 0: meteen.',
  'Temperature when nobody is home': 'Temperatuur als niemand thuis is',
  'Every room stays at most this warm while everyone is away, in house mode Away and on holiday (5–25 °C; frost protection always stays on).': 'Elke ruimte wordt hoogstens zo warm zolang iedereen weg is, in huismodus Afwezig en op vakantie (5–25 °C; vorstbeveiliging blijft altijd aan).',
  'Comfort without a week program': 'Comfort zonder weekprogramma',
  'Comfort for a room without a week program. With a week program, Comfort is its warmest temperature.': 'Comfort van een ruimte zonder weekprogramma. Met een weekprogramma is Comfort de warmste temperatuur daarvan.',
  'Night without a week program': 'Nacht zonder weekprogramma',
  'Night for a room without a week program. With a week program, Night is its coolest temperature.': 'Nacht van een ruimte zonder weekprogramma. Met een weekprogramma is Nacht de koelste temperatuur daarvan.',
  'Pause after a window opens': 'Pauze nadat een raam opengaat',
  'Minutes a window must stay open before a room pauses, so airing briefly does not stop the heating. A paused room still protects against frost.': 'Minuten dat een raam open moet blijven voordat een ruimte pauzeert, zodat kort luchten de verwarming niet stopt. Een gepauzeerde ruimte blijft beschermd tegen vorst.',
  'Pause after a door opens': 'Pauze nadat een deur opengaat',
  'The same for doors, usually longer, so letting the dog out or walking through the front door does not stop the heating. Default 5 minutes.': 'Hetzelfde voor deuren, meestal langer, zodat de hond uitlaten of door de voordeur lopen de verwarming niet stopt. Standaard 5 minuten.',
  'House mode': 'Huismodus',
  'Automatic': 'Automatisch',
  'At home': 'Thuis',
  'Away': 'Afwezig',
  'Holiday': 'Vakantie',
  'The people you set under Presence decide.': 'De mensen die je bij Aanwezigheid instelt, bepalen het.',
  'Always the week programs.': 'Altijd de weekprogramma\'s.',
  'Every room at most the away temperature.': 'Elke ruimte hoogstens de afwezigheidstemperatuur.',
  'From now until the day and time below.': 'Vanaf nu tot de dag en tijd hieronder.',
  'Holiday ends': 'Vakantie eindigt',
  'Only for Holiday: the day and time you are back. At most a year ahead.': 'Alleen voor Vakantie: dag en tijd waarop je terug bent. Hoogstens een jaar vooruit.',
  'Planned holidays': 'Geplande vakanties',
  'On holiday every room stays at most the temperature on holiday and the house is warm again when you are back; then the house mode is as before. Holidays that overlap become one.': 'Op vakantie blijft elke ruimte hoogstens op de temperatuur op vakantie en is het huis weer warm als je terugkomt; daarna staat de huismodus weer zoals ervoor. Vakanties die overlappen, worden één vakantie.',
  'Plan a holiday': 'Vakantie plannen',
  'Holiday {n}': 'Vakantie {n}',
  'Remove holiday {n}': 'Vakantie {n} verwijderen',
  'Starts': 'Begint',
  'Ends (back home)': 'Eindigt (weer thuis)',
  'At most 8 holidays can be planned.': 'Er kunnen hoogstens 8 vakanties gepland worden.',
  'Temperature on holiday': 'Temperatuur op vakantie',
  'Every room stays at most this warm during a holiday (5–25 °C; frost protection always stays on). Until you change it, it is the temperature when nobody is home.': 'Elke ruimte blijft tijdens een vakantie hoogstens zo warm (5–25 °C; de vorstbeveiliging blijft altijd aan). Tot je hem verandert, is dit de temperatuur als niemand thuis is.',
  'Search by name': 'Zoek op naam',
  'Choose a person, group, zone or switch that exists.': 'Kies een bestaande persoon, groep, zone of schakelaar.',
  'Enter a whole number within the limits.': 'Vul een heel getal binnen de grenzen in.',
  'Choose an away temperature between 5 and 25 °C.': 'Kies een afwezigheidstemperatuur tussen 5 en 25 °C.',
  'The E32 did not save the away temperature ({error}), so nothing was saved. Check that the E32 is online and try again.': 'De E32 heeft de afwezigheidstemperatuur niet opgeslagen ({error}), dus er is niets opgeslagen. Controleer of de E32 online is en probeer het opnieuw.',
  'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again.': 'Hiervoor is nieuwere E32-firmware nodig. Werk de E32 eerst bij (Instellingen → Updates → OpenThermostat E32 Firmware) en probeer het opnieuw.',
  'Enter a temperature between 5 and 30 °C.': 'Vul een temperatuur tussen 5 en 30 °C in.',
  'Choose one of the modes.': 'Kies een van de modi.',
  'Choose the day and time the holiday ends.': 'Kies dag en tijd waarop de vakantie eindigt.',
  'Choose a moment in the future, at most a year ahead.': 'Kies een moment in de toekomst, hoogstens een jaar vooruit.',
  'This E32 software does not know this mode. Update the E32 first.': 'Deze E32-software kent deze modus niet. Werk eerst de E32 bij.',
  'The E32 did not accept this ({error}). Try again.': 'De E32 heeft dit niet aangenomen ({error}). Probeer het opnieuw.',
  'This holiday is already over. Choose an end in the future.': 'Deze vakantie is al voorbij. Kies een einde in de toekomst.',
  'Choose an end at most a year ahead.': 'Kies een einde hoogstens een jaar vooruit.',
  'At most 8 holidays can be planned. Remove one first.': 'Er kunnen hoogstens 8 vakanties gepland worden. Verwijder er eerst een.',
  'The holiday must end after it starts.': 'De vakantie moet eindigen na het begin.',
  'The E32 clock is not set yet, so a holiday date cannot be used. Try again in a minute.': 'De klok van de E32 is nog niet gelijkgezet, dus een vakantiedatum kan nog niet. Probeer het over een minuut opnieuw.',
  'A holiday was changed elsewhere meanwhile. Reload the page and try again.': 'Een vakantie is intussen elders gewijzigd. Laad de pagina opnieuw en probeer het opnieuw.',
  'Holiday {line}: choose when it starts and when it ends.': 'Vakantie {line}: kies wanneer die begint en wanneer die eindigt.',
  'Holiday {line}: it must end after it starts.': 'Vakantie {line}: die moet eindigen na het begin.',
  'Holiday {line} is already over. Choose an end in the future.': 'Vakantie {line} is al voorbij. Kies een einde in de toekomst.',
  'Holiday {line}: choose an end at most a year ahead.': 'Vakantie {line}: kies een einde hoogstens een jaar vooruit.',
  'Choose a temperature between 5 and 25 °C.': 'Kies een temperatuur tussen 5 en 25 °C.',
  'Stop holiday': 'Vakantie stoppen',
  'Stop the holiday now?': 'De vakantie nu stoppen?',
  'The house goes back to the mode it had before the holiday.': 'Het huis gaat terug naar de modus van voor de vakantie.',
  'Holiday until {until}': 'Vakantie tot {until}',
  'Per room on the room screen.': 'Per ruimte aan te passen op het ruimtescherm.',
  'New rooms start with these values; each room can change them on its own screen.': 'Nieuwe ruimtes beginnen met deze waarden; elke ruimte kan ze op haar eigen scherm aanpassen.',
  'The people of the house, or a group, zone or switch.': 'De mensen van het huis, of een groep, zone of schakelaar.',
  'Every room stays at most this warm while everyone is away.': 'Elke ruimte wordt hoogstens zo warm zolang iedereen weg is.',
  'The house is warm again when you are back.': 'Het huis is weer warm als je terug bent.',
  'Every room stays at most this warm during a holiday.': 'Elke ruimte wordt hoogstens zo warm tijdens een vakantie.',
  'The pause delay lies between 0 and 30 minutes.': 'De pauzevertraging ligt tussen 0 en 30 minuten.'}};
const ERRORS = {
 presence_entity_invalid: 'Choose a person, group, zone or switch that exists.',
 whole_number_invalid: 'Enter a whole number within the limits.',
 comfort_away_temperature_invalid: 'Choose an away temperature between 5 and 25 °C.',
 away_temperature_not_saved: 'The E32 did not save the away temperature ({error}), so nothing was saved. Check that the E32 is online and try again.',
 away_temperature_update_required: 'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again.',
 temperature_invalid: 'Enter a temperature between 5 and 30 °C.',
 contact_delay_invalid: 'The pause delay lies between 0 and 30 minutes.',
 house_mode_invalid: 'Choose one of the modes.',
 house_holiday_date_needed: 'Choose the day and time the holiday ends.',
 house_holiday_date_invalid: 'Choose a moment in the future, at most a year ahead.',
 house_mode_update_required: 'This E32 software does not know this mode. Update the E32 first.',
 house_mode_not_saved: 'The E32 did not accept this ({error}). Try again.',
 house_holiday_not_saved: 'The E32 did not accept this ({error}). Try again.',
 house_holiday_past: 'This holiday is already over. Choose an end in the future.',
 house_holiday_too_far: 'Choose an end at most a year ahead.',
 house_holiday_too_many: 'At most 8 holidays can be planned. Remove one first.',
 house_holiday_order: 'The holiday must end after it starts.',
 house_holiday_no_clock: 'The E32 clock is not set yet, so a holiday date cannot be used. Try again in a minute.',
 house_holiday_changed: 'A holiday was changed elsewhere meanwhile. Reload the page and try again.',
 house_holiday_line_dates_needed: 'Holiday {line}: choose when it starts and when it ends.',
 house_holiday_line_order: 'Holiday {line}: it must end after it starts.',
 house_holiday_line_past: 'Holiday {line} is already over. Choose an end in the future.',
 house_holiday_line_too_far: 'Holiday {line}: choose an end at most a year ahead.',
 house_holiday_temperature_invalid: 'Choose a temperature between 5 and 25 °C.',
 house_mode_unavailable: 'The E32 does not report the house mode yet.'};

// The House's three parts (HA-INSTELPANEEL-FASE2.nl.md 3.2): [item, title, icon]; window and door contacts live on the
// room screen since 1.4.1 (the old routes #house/contacts[/<room>] lead there).
const PARTS = [['presence', 'Presence and away temperature', 'account'], ['mode', 'House mode and holiday', 'calendar'], ['defaults', 'Room defaults', 'home']];
const MODES = {auto: ['Automatic', 'The people you set under Presence decide.'], home: ['At home', 'Always the week programs.'],
 away: ['Away', 'Every room at most the away temperature.'], holiday: ['Holiday', 'From now until the day and time below.'],
 summer: ['Summer', 'Summer mode: the heating stays off until you switch this off; hot water and frost protection stay.']};
// The values each screen edits, by the name its model gives (model.screen, CONTRACT-1.4.2 §2), never by a field it has.
const FIELDS = {presence: ['presence_entities', 'away_delay', 'away_temperature'],
 defaults: ['comfort_temperature', 'eco_temperature', 'contact_delay', 'door_delay'],
 mode: ['house_mode', 'holiday_until', 'holidays', 'holiday_temperature']};
const PRESENCE_DOMAINS = ['person', 'group', 'zone', 'device_tracker', 'binary_sensor', 'input_boolean'];

const copy = v => JSON.parse(JSON.stringify(v));
// The temperatures' unit as the model gives it (the house's values are the E32's, in °C, until a model names another).
const unitOf = model => model?.unit || '°C';
// A mode by its word; a mode this module does not know yet (summer, CONTRACT-1.4.1 §7) by the house mode select's own word.
const modeName = (ctx, value) => {
 if (MODES[value]) return ctx.t(MODES[value][0]);
 try { return ctx.hass?.localize?.('component.open_thermostat.entity.select.house_mode.state.' + value) || value; } catch (e) { return value; }
};
const part = item => String(item || '').split('/')[0];
const titleOf = item => PARTS.find(p => p[0] === part(item))?.[1];
// A local moment as the date-and-time field holds it, `days` from now at `hour`:00.
const ahead = (days, hour) => {
 const d = new Date(); d.setDate(d.getDate() + days); d.setHours(hour, 0, 0, 0);
 const p = n => String(n).padStart(2, '0');
 return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:00`;
};
// The holiday that runs now: the house mode Holiday, or a planned one between its start and end.
const running = m => {
 const now = Date.now();
 return (m.holidays || []).findIndex(x => Date.parse(x.from) <= now && now < Date.parse(x.until));
};

// The planned holidays: a card per holiday with its start and end (the kit's date and time, Home Assistant's format).
function holidaysField(ctx) {
 return o => {
  const {kit, t} = ctx, {h} = kit;
  let list = copy(o.value || []);
  const body = h('div', {class: 'hh-holidays'}), api = kit.shell('holidays', o, body, false), emit = () => o.onChange?.(copy(list));
  const draw = focus => {
   const rows = list.map((holiday, i) => {
    const n = i + 1, moment = (key, label) => kit.fields.moment({key: `holidays:${i}:${key}`, hass: ctx.hass, label, value: holiday[key], disabled: o.disabled,
     onChange: v => { holiday[key] = v; emit(); }}).el;
    return h('div', {class: 'hh-holiday', role: 'group', 'aria-label': t('Holiday {n}', {n}), 'data-holiday': i},
     h('div', {class: 'hh-holiday-head'}, h('span', {class: 'hh-holiday-title', text: kit.together(`${kit.time.date(ctx.hass, holiday.from)} – ${kit.time.date(ctx.hass, holiday.until)}`)}),
      o.disabled ? null : kit.iconButton('close', t('Remove holiday {n}', {n}), () => { list.splice(i, 1); draw(true); emit(); }, {'data-remove': ''})),
     moment('from', t('Starts')), moment('until', t('Ends (back home)')));
   });
   const parts = rows.length ? rows : [h('p', {class: 'help', text: t('No holidays planned.')})];
   if (!o.disabled) {
    if (list.length >= 8) parts.push(h('p', {class: 'help', text: t('At most 8 holidays can be planned.')}));
    else parts.push(kit.button(t('Plan a holiday'), () => { list.push({from: ahead(1, 10), until: ahead(8, 18)}); draw('last'); emit(); }, 'outlined', {icon: 'plus', 'data-add-holiday': ''}));
   }
   body.replaceChildren(...parts);
   if (focus === 'last') body.querySelector('.hh-holiday:last-of-type select')?.focus();
   else if (focus) body.querySelector('[data-add-holiday]')?.focus();
  };
  draw();
  api.target = () => body.querySelector('select, button');
  api.describe();
  return api;
 };
}

/* ---- the screens ---- */
function overview(ctx) {
 const {kit, t, model: m, hass} = ctx;
 const names = (m.presence.presence_entities || []).map(e => hass?.states?.[e]?.attributes?.friendly_name || e);
 const presence = [names.length ? names.join(', ') : t('Nobody chosen yet'),
  m.presence.has_away && m.presence.away_temperature != null
   ? t('Away after {n} min · {temperature} when nobody is home', {n: kit.number(m.presence.away_delay, hass, 0),
    temperature: kit.degrees(m.presence.away_temperature, unitOf(m.presence), hass)})
   : t('Away after {n} min', {n: kit.number(m.presence.away_delay, hass, 0)})];
 const d = m.defaults;
 const defaults = [t('Without a week program: comfort {comfort}, night {night}', {comfort: kit.degrees(d.comfort_temperature, unitOf(d), hass),
  night: kit.degrees(d.eco_temperature, unitOf(d), hass)}),
  t('Pause after a window {window} min, after a door {door} min', {window: kit.number(d.contact_delay, hass), door: kit.number(d.door_delay, hass)})];
 let mode = [t('The E32 does not report the house mode yet.')];
 if (m.mode) {
  mode = [modeName(ctx, m.mode.house_mode)];
  if (m.mode.planning) mode.push(m.mode.holidays?.length
   ? t('Next holiday: {from} – {until}', {from: kit.time.date(hass, m.mode.holidays[0].from), until: kit.time.date(hass, m.mode.holidays[0].until)}) : t('No holidays planned.'));
 }
 const lines = {presence, mode, defaults};
 return kit.h('div', {class: 'card list hh-overview'}, ...PARTS.map(([key, title, icon]) =>
  ctx.row({label: t(title), icon, summary: lines[key], route: '#house/' + key, data: {part: key}})));
}

function presence(ctx) {
 const {kit, t} = ctx;
 return kit.h('div', {class: 'fields'},
  ctx.field('entity', 'presence_entities', {label: t('Who lives here'), multiple: true, domains: PRESENCE_DOMAINS, placeholder: t('Search by name'),
   help: t('The people of the house, or a group, zone or switch.'),
   more: t('Optional. The people of the house, or a group, zone (for example zone.home), device tracker or switch that is on while someone is home.')}),
  ctx.field('stepper', 'away_delay', {label: t('Away after'), unit: 'min', step: 1, min: 0, max: 240,
   help: t('Minutes everyone must be away before the house counts as away, so a short errand does not cool the house. 0: at once.')}),
  ctx.model.has_away ? ctx.field('stepper', 'away_temperature', {label: t('Temperature when nobody is home'), unit: unitOf(ctx.model), step: 0.5, min: 5, max: 25,
   help: t('Every room stays at most this warm while everyone is away.'),
   more: t('Every room stays at most this warm while everyone is away, in house mode Away and on holiday (5–25 °C; frost protection always stays on).')}) : null);
}

function defaults(ctx) {
 const {kit, t} = ctx, per = t('Per room on the room screen.');
 const field = (key, label, o) => ctx.field('stepper', key, {label, ...o, help: per});
 return kit.h('div', {class: 'fields'},
  field('comfort_temperature', t('Comfort without a week program'), {unit: unitOf(ctx.model), step: 0.5, min: 5, max: 30,
   more: t('Comfort for a room without a week program. With a week program, Comfort is its warmest temperature.')}),
  field('eco_temperature', t('Night without a week program'), {unit: unitOf(ctx.model), step: 0.5, min: 5, max: 30,
   more: t('Night for a room without a week program. With a week program, Night is its coolest temperature.')}),
  field('contact_delay', t('Pause after a window opens'), {unit: 'min', step: 0.5, min: 0, max: 30,
   more: t('Minutes a window must stay open before a room pauses, so airing briefly does not stop the heating. A paused room still protects against frost.')}),
  field('door_delay', t('Pause after a door opens'), {unit: 'min', step: 0.5, min: 0, max: 30,
   more: t('The same for doors, usually longer, so letting the dog out or walking through the front door does not stop the heating. Default 5 minutes.')}));
}

function mode(ctx) {
 const {kit, t, model: m, hass} = ctx, {h} = kit;
 if (m.unavailable) return h('div', {}, kit.notice(t('The E32 does not report the house mode yet.'), 'info'));
 const until = ctx.field('moment', 'holiday_until', {label: t('Holiday ends'), help: t('Only for Holiday: the day and time you are back. At most a year ahead.')});
 until.hidden = ctx.values.house_mode !== 'holiday';
 const parts = [];
 // A holiday that runs now: one status line and "Stop holiday" (the house goes back to the mode it had before).
 const now = running(m);
 if (m.house_mode === 'holiday' || now >= 0) {
  const end = now >= 0 ? m.holidays[now].until : m.holiday_until;
  const stop = ctx.readOnly ? null : kit.button(t('Stop holiday'), () => ctx.act(m.planning && now >= 0 ? {holidays: m.holidays.filter((x, i) => i !== now)} : {house_mode: 'auto'},
   {title: t('Stop the holiday now?'), text: t('The house goes back to the mode it had before the holiday.'), confirm: t('Stop holiday')}), 'outlined', {'data-stop-holiday': ''});
  parts.push(h('div', {class: 'hh-now'}, kit.statusLine(t('Holiday until {until}', {until: kit.time.moment(hass, end)}), 'water'), stop));
 }
 parts.push(ctx.field('radio', 'house_mode', {label: t('House mode'), options: m.modes.map(value => ({value, label: modeName(ctx, value), help: MODES[value] ? t(MODES[value][1]) : null})),
  onChange: v => { until.hidden = v !== 'holiday'; }}), until);
 if (m.planning) {
  parts.push(ctx.field(holidaysField(ctx), 'holidays', {label: t('Planned holidays'), help: t('The house is warm again when you are back.'),
   more: t('On holiday every room stays at most the temperature on holiday and the house is warm again when you are back; then the house mode is as before. Holidays that overlap become one.')}));
  parts.push(ctx.field('stepper', 'holiday_temperature', {label: t('Temperature on holiday'), unit: unitOf(m), step: 0.5, min: 5, max: 25,
   help: t('Every room stays at most this warm during a holiday.'),
   more: t('Every room stays at most this warm during a holiday (5–25 °C; frost protection always stays on). Until you change it, it is the temperature when nobody is home.')}));
 }
 return h('div', {class: 'fields'}, ...parts);
}

const STYLE = `.hh-overview{border:0;border-radius:0;background:none;margin:-4px -16px}.hh-overview .row{min-height:72px;margin:0;width:100%}
.hh-holidays{display:grid;gap:var(--ot-s2);max-width:600px}
.hh-holiday{display:grid;gap:4px;padding:var(--ot-s2) var(--ot-s3) var(--ot-s3);border:1px solid var(--ot-divider);border-radius:var(--ot-radius-s);background:var(--ot-raised)}
.hh-holiday .field{padding:4px 0;margin:0;border:0}.hh-holiday-head{display:flex;align-items:center;justify-content:space-between;gap:8px}
.hh-holiday-title{font-weight:500}.hh-now{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 16px;padding:var(--ot-s3) 0}
@media(max-width:420px){.hh-overview{margin:-4px -12px}}`;

(window.OpenThermostatSettingsSections ||= []).push(['house', {
 title: (model, item) => titleOf(item) || 'House',
 // No intro sentence on the House itself (plan chapter 4: no filler); its three rows say what is set.
 subtitle: (model, item) => (item == null ? null
  : part(item) === 'presence' ? 'In the house mode Automatic the rooms go to the away temperature when everyone is away. Someone home, or someone whose place is not known, keeps the house warm.'
   : part(item) === 'defaults' ? 'New rooms start with these values; each room can change them on its own screen.' : null),
 texts: TEXTS,
 errors: ERRORS,
 // Window and door contacts moved to the room screen (1.4.1): an old link opens the room, or the rooms.
 redirect: item => (part(item) === 'contacts' ? (String(item).split('/')[1] ? '#room/' + String(item).split('/')[1] : '#rooms') : null),
 // The screen by its model's own key (1.4.2, P4); the overview has none, so nothing to save there.
 values: model => {
  const keys = Object.hasOwn(FIELDS, model.screen) ? FIELDS[model.screen] : [];
  return Object.fromEntries(keys.filter(k => k in model).map(k => [k, copy(model[k])]));
 },
 // Only what differs from the screen as shown.
 toSave: (values, model) => Object.fromEntries(Object.entries(values).filter(([k, v]) => JSON.stringify(v) !== JSON.stringify(model[k]))),
 shown: (key, value, t) => {
  if (key === 'house_mode') return MODES[value] ? t(MODES[value][0]) : value;
  if (key === 'holidays') return (value || []).map(x => `${x.from} – ${x.until}`).join(', ');
  return undefined;
 },
 // The style of this section goes last: the first field keeps the look of the kit.
 render: ctx => {
  const p = part(ctx.item);
  const el = ctx.item == null ? overview(ctx) : p === 'presence' ? presence(ctx) : p === 'defaults' ? defaults(ctx) : mode(ctx);
  el.append(ctx.kit.h('style', {text: STYLE}));
  return el;
 }
}]);
