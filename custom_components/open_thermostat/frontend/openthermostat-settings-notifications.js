/* The settings panel's section Notifications (1.4.1, HA-INSTELPANEEL-FASE2.nl.md 3.5): two questions, each on its own
   calm screen. #notifications: one status line (where messages go now) and two rows; #notifications/people: "Who gets
   messages", a row per person; #notifications/person/<person>: one person's phone and the tick "Also messages about
   the house"; #notifications/house: "Which messages", the house (its switch and, while on, the messages in two groups
   with what causes each) and the rooms (a row per room with its summary and, while on, who gets its messages; a room's
   messages and their recipients are set on the room screen, #room/<id>, which saves the recipients through this
   section's item room/<id>, 1.4.2). Backend settings_notifications.py (one item per screen, its own token; CONTRACT-1.4.1, the
   S-NOTIFY-BACKEND report); the kit and the core: openthermostat-settings-kit.js, openthermostat-settings.js. Words:
   Configure's for the same settings, the backend's cause sentences (glossary block 1.4.1 NOTIFY-BACKEND), word for
   word (test/ha-settings-texts.test.cjs). */
const TEXTS = {
 nl: {
  'Notifications': 'Meldingen',
  'Messages on your phone about a room or the house. Nothing is on until you switch it on.': 'Berichten op je telefoon over een ruimte of het huis. Er staat niets aan tot je het zelf aanzet.',
  'Who gets messages': 'Wie krijgt berichten',
  'Each person\'s phone, and whether they also get the messages about the house.': 'De telefoon van elke persoon, en of die ook de meldingen over het huis krijgt.',
  'The phone or app that gets this person\'s messages.': 'De telefoon of app die de berichten van deze persoon krijgt.',
  'Which messages': 'Welke berichten',
  'Messages about the house and about each room.': 'Berichten over het huis en over elke ruimte.',
  'No people in Home Assistant yet.': 'Nog geen personen in Home Assistant.',
  'House: on': 'Huis: aan',
  'House: off': 'Huis: uit',
  'no rooms': 'geen ruimtes',
  '1 room': '1 ruimte',
  '{n} rooms': '{n} ruimtes',
  'There are no people in Home Assistant yet. Add a person under Settings → People, then choose their phone here.': 'Er zijn nog geen personen in Home Assistant. Voeg een persoon toe onder Instellingen → Personen en kies daarna hier de telefoon.',
  'No phone': 'Geen telefoon',
  '{name} (Home Assistant app)': '{name} (Home Assistant-app)',
  '{service} (not found)': '{service} (niet gevonden)',
  'Also house messages': 'Ook huisberichten',
  'Phone or app': 'Telefoon of app',
  'Choose No phone to stop messages to a phone; they then show in Home Assistant.': 'Kies Geen telefoon om geen berichten meer naar een telefoon te sturen; ze verschijnen dan in Home Assistant.',
  'Suggested: the app on {name}\'s own phone. Choose Save to use it.': 'Voorgesteld: de app op de eigen telefoon van {name}. Kies Opslaan om hem te gebruiken.',
  'This phone is no longer in Home Assistant: the messages show in Home Assistant until you choose another one.': 'Deze telefoon is niet meer in Home Assistant: de berichten verschijnen in Home Assistant tot je een andere kiest.',
  'Also messages about the house': 'Ook meldingen over het huis',
  '{name} gets the messages about the house too.': '{name} krijgt ook de meldingen over het huis.',
  'Off: {name} gets no messages about the house.': 'Uit: {name} krijgt geen meldingen over het huis.',
  'The house': 'Het huis',
  'Notify about the house': 'Meldingen over het huis',
  'Off: no messages about the house.': 'Uit: geen berichten over het huis.',
  'They go to: {people}.': 'Ze gaan naar: {people}.',
  '{name} (no phone: in Home Assistant)': '{name} (geen telefoon: in Home Assistant)',
  'Nobody gets these yet: switch on “Also messages about the house” for a person under Who gets messages.': 'Nog niemand krijgt deze: zet bij een persoon onder Wie krijgt berichten “Ook meldingen over het huis” aan.',
  'Messages about the whole house, day and night, also when nobody is home.': 'Berichten over het hele huis, dag en nacht, ook als niemand thuis is.',
  'Problems': 'Problemen',
  'Maintenance': 'Onderhoud',
  'Rooms': 'Ruimtes',
  'A room\'s messages, and who gets them, are set on its own screen.': 'De meldingen van een ruimte, en wie ze krijgt, stel je in op haar eigen scherm.',
  'The E32 has not reported any rooms yet.': 'De E32 heeft nog geen ruimtes gemeld.',
  'The rooms could not be read. Reload the page.': 'De ruimtes konden niet worden gelezen. Laad de pagina opnieuw.',
  'Boiler fault': 'Ketelstoring',
  'E32 not reporting for 10 minutes, and when it is back': 'E32 meldt zich 10 minuten niet, en als hij er weer is',
  'E32 waits for your confirmation to control the boiler': 'E32 wacht op je bevestiging om de ketel te regelen',
  'Frost protection on': 'Vorstbeveiliging aan',
  'Water pressure low': 'Waterdruk te laag',
  'Boiler asks for maintenance (H code)': 'Ketel vraagt om onderhoud (H-code)',
  'New version of the E32 firmware or of this integration': 'Nieuwe versie van de E32-firmware of van deze integratie',
  'Daily backup of the E32 settings keeps failing': 'Dagelijkse back-up van de E32-instellingen mislukt steeds',
  'E32 ready to plan the heating (asks for your confirmation once)': 'E32 klaar om de verwarming te plannen (vraagt één keer je bevestiging)',
  'Season: switch summer mode on or off?': 'Seizoen: zomerstand aan- of uitzetten?',
  'The boiler reports a fault.': 'De ketel meldt een storing.',
  'The E32 has not reported for 10 minutes; a second message when it is back.': 'De E32 meldt zich al 10 minuten niet; een tweede bericht als hij er weer is.',
  'The E32 waits for your confirmation before it controls the boiler.': 'De E32 wacht op je bevestiging voordat hij de ketel regelt.',
  'A room cooled below 8 °C, so the E32 heats against frost.': 'Een ruimte is afgekoeld tot onder 8 °C, dus de E32 verwarmt tegen vorst.',
  'The water pressure of the heating is too low.': 'De waterdruk van de verwarming is te laag.',
  'The boiler asks for maintenance (an H code).': 'De ketel vraagt om onderhoud (een H-code).',
  'A new version of the E32 firmware or of this integration is available.': 'Er is een nieuwe versie van de E32-firmware of van deze integratie.',
  'The daily backup of the E32 settings has failed for more than 3 days.': 'De dagelijkse back-up van de E32-instellingen mislukt al meer dan 3 dagen.',
  'The E32 is ready to plan the heating and asks for your confirmation once.': 'De E32 is klaar om de verwarming te plannen en vraagt één keer je bevestiging.',
  'Five days above 17 °C outside, or three cold days while summer mode is on.': 'Vijf dagen boven 17 °C buiten, of drie koude dagen terwijl de zomerstand aan staat.',
  'Choose at least one message, or switch notifications off.': 'Kies minstens één bericht, of zet de meldingen uit.',
  'Choose one of the phones in the list.': 'Kies een van de telefoons in de lijst.',
  'Something in the form was not valid. Try again.': 'Iets in het formulier klopte niet. Probeer het opnieuw.',
  'Choose one of the people in the list.': 'Kies een van de personen in de lijst.'
 }};
// The house messages in Configure's words (selector notification_house_kind), and what causes each (the backend's
// CAUSES by cause_key, glossary block 1.4.1 NOTIFY-BACKEND).
const KINDS = {
 boiler_fault: 'Boiler fault',
 e32_offline: 'E32 not reporting for 10 minutes, and when it is back',
 awaiting_confirmation: 'E32 waits for your confirmation to control the boiler',
 frost: 'Frost protection on',
 pressure_low: 'Water pressure low',
 maintenance: 'Boiler asks for maintenance (H code)',
 update: 'New version of the E32 firmware or of this integration',
 backup: 'Daily backup of the E32 settings keeps failing',
 plan_ready: 'E32 ready to plan the heating (asks for your confirmation once)',
 season: 'Season: switch summer mode on or off?'};
const CAUSES = {
 cause_boiler_fault: 'The boiler reports a fault.',
 cause_e32_offline: 'The E32 has not reported for 10 minutes; a second message when it is back.',
 cause_awaiting_confirmation: 'The E32 waits for your confirmation before it controls the boiler.',
 cause_frost: 'A room cooled below 8 °C, so the E32 heats against frost.',
 cause_pressure_low: 'The water pressure of the heating is too low.',
 cause_maintenance: 'The boiler asks for maintenance (an H code).',
 cause_update: 'A new version of the E32 firmware or of this integration is available.',
 cause_backup: 'The daily backup of the E32 settings has failed for more than 3 days.',
 cause_plan_ready: 'The E32 is ready to plan the heating and asks for your confirmation once.',
 cause_season: 'Five days above 17 °C outside, or three cold days while summer mode is on.'};
const ERRORS = {
 notification_kinds_needed: 'Choose at least one message, or switch notifications off.',
 notification_phone_invalid: 'Choose one of the phones in the list.',
 notification_invalid: 'Something in the form was not valid. Try again.',
 notification_person_invalid: 'Choose one of the people in the list.'};
const CSS = `.nn-page{display:grid;gap:var(--ot-s3)}.nn-status{margin:-4px 0 0}.nn-status:empty{display:none}
.nn-list .row{min-height:72px}.nn-card .ot-card-head{margin-bottom:var(--ot-s1)}
.nn-card .ot-card-head+.field,.nn-card>.field:first-child{border-top:0}.nn-card>.field:first-child{padding-top:0}
.nn-groups>.field{padding-bottom:var(--ot-s2)}.nn-groups .choices{gap:0}.nn-groups .choice{padding:10px 0}
.choice-help{display:block;line-height:var(--ot-line-s)}.nn-groups .choice-label{font-weight:400}
.nn-rows{margin:var(--ot-s2) calc(-1 * var(--ot-s4)) calc(-1 * var(--ot-s4));border-top:1px solid var(--ot-divider)}
.nn-rows .row{min-height:64px}.nn-rows>.ot-empty,.nn-rows>.notice{margin:var(--ot-s3) var(--ot-s4) var(--ot-s4)}
.nn-rows>.ot-skeleton{padding:var(--ot-s3) var(--ot-s4)}
@media(max-width:420px){.nn-rows{margin:var(--ot-s2) calc(-1 * var(--ot-s3)) calc(-1 * var(--ot-s3))}}`;

const none = 'none';  // "No phone" in the select (sent as null)
const person_ = 'person/';
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const say = (ctx, map) => map[ctx.lang] || map.en || '';

// What each screen edits: a person's phone and tick, or the house's switch and messages; the others edit nothing.
function values(m) {
 if ('person' in m) return {phone: m.phone ?? none, house_too: m.house_too === true};
 if ('kinds' in m && 'on' in m) return {on: m.on === true, problems: [...(m.problems || [])], maintenance: [...(m.maintenance || [])]};
 return {};
}

// A phone as this screen says it: "Pixel 8 (Home Assistant app)", "notify.telegram", "… (not found)", "No phone".
function phoneText(t, label, kind) {
 if (!label || !kind) return t('No phone');
 if (kind === 'app') return t('{name} (Home Assistant app)', {name: label});
 if (kind === 'gone') return t('{service} (not found)', {service: label});
 return label;
}

// What the overview loaded (the status) and the rooms, per installation: "Which messages" shows them at once and
// reads them again once per visit (each screen is its own item of settings/get).
const known = new Map(), asked = new WeakMap();
function fetchExtra(ctx, apply) {
 const key = ctx.entry_id, before = known.get(key) || {};
 apply(before);
 if (!asked.has(ctx.model)) {
  const get = item => ctx.hass.callWS({type: 'open_thermostat/settings/get', entry_id: key, section: 'notifications', ...(item ? {item} : {})}).then(r => r.model);
  asked.set(ctx.model, Promise.all([get(null).catch(() => null), get('rooms').catch(() => null)]).then(([status, rooms]) => {
   const now = {status: status?.status ? status : before.status, rooms: rooms || {failed: true}};
   known.set(key, now);
   return now;
  }));
 }
 asked.get(ctx.model).then(apply);
}

// Who gets the house messages, someone without a phone said as such (as the status line says it).
function houseWho(t, overviewModel) {
 if (!overviewModel?.status) return '';
 const s = overviewModel.status, without = new Set(s.without_phone || []), names = s.house_recipients || [];
 return names.length ? t('They go to: {people}.', {people: names.map(n => (without.has(n) ? t('{name} (no phone: in Home Assistant)', {name: n}) : n)).join(', ')})
  : t('Nobody gets these yet: switch on “Also messages about the house” for a person under Who gets messages.');
}

// A group of message kinds as checkboxes, each with what causes it: the value is the chosen kinds in their order.
const kindsField = (kit, t, rows) => o => {
 const {h} = kit, id = 'nn-' + o.key, inputs = [];
 const group = h('div', {class: 'choices', role: 'group', 'aria-labelledby': id + '-label'});
 for (const {kind, cause_key: cause} of rows) {
  const input = h('input', {type: 'checkbox', value: kind, disabled: o.disabled, 'data-fk': `${o.key}:${kind}`});
  input.checked = (o.value || []).includes(kind);
  input.addEventListener('change', () => o.onChange?.(inputs.filter(i => i.checked).map(i => i.value)));
  inputs.push(input);
  group.append(h('label', {class: 'choice', 'data-kind': kind}, input, h('span', {class: 'choice-text'},
   h('span', {class: 'choice-label', text: KINDS[kind] ? t(KINDS[kind]) : kind}),
   CAUSES[cause] ? h('span', {class: 'choice-help', text: t(CAUSES[cause])}) : null)));
 }
 const api = kit.shell('kinds', {...o, id}, group, false);
 api.target = () => group;
 api.focus = () => (inputs.find(i => i.checked) || inputs[0])?.focus();
 api.describe();
 return api;
};

// A field's one help line, rewritten when the field's state changes (the help follows the switch).
const setHelp = (el, text) => { const help = el.querySelector(':scope > .help'); if (help) { help.textContent = text; help.hidden = !text; } };

/* ---- the screens ---- */
// #notifications: where messages go now (the one status line), then the two questions.
function overview(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit, s = m.status || {};
 known.set(ctx.entry_id, {...known.get(ctx.entry_id), status: m});
 const tone = (s.recipients || []).some(r => r.phone_kind === 'gone') ? 'attention' : (s.recipients || []).length ? 'ok' : 'rest';
 const names = [...(s.recipients || []).map(r => r.name), ...(s.without_phone || [])];
 const rooms = (m.rooms_on || []).length;
 const which = `${t(m.house_on ? 'House: on' : 'House: off')} · ${rooms === 0 ? t('no rooms') : rooms === 1 ? t('1 room') : t('{n} rooms', {n: rooms})}`;
 return h('div', {class: 'nn-page', 'data-screen': 'notifications'},
  h('div', {class: 'nn-status', 'data-status': ''}, s.line ? kit.statusLine(say(ctx, s.line), tone) : null),
  h('div', {class: 'card list nn-list'},
   ctx.row({label: t('Who gets messages'), icon: 'account', summary: [names.length ? names.join(', ') : t('No people in Home Assistant yet.')],
    route: '#notifications/people', data: {item: 'people'}}),
   ctx.row({label: t('Which messages'), icon: 'bell', summary: [which], route: '#notifications/house', data: {item: 'house'}})));
}

// #notifications/people: a row per person with the phone and, when on, the label "Also house messages".
function people(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit;
 if (!(m.people || []).length) return h('div', {class: 'nn-page', 'data-screen': 'people'},
  h('div', {class: 'ot-card'}, kit.empty({icon: 'account', text: t('There are no people in Home Assistant yet. Add a person under Settings → People, then choose their phone here.')})));
 return h('div', {class: 'nn-page', 'data-screen': 'people'}, h('div', {class: 'card list nn-list'}, ...m.people.map(p => {
  const row = ctx.row({label: p.name, icon: 'account', summary: [phoneText(t, p.phone_label, p.phone_kind)],
   route: '#notifications/' + person_ + encodeURIComponent(p.person), data: {person: p.person}});
  if (p.house_too) row.querySelector('.row-label').append(kit.chip(t('Also house messages'), 'rest', 'home'));
  return row;
 })));
}

// #notifications/person/<person>: the phone (the suggested app preselected while nothing is chosen) and the tick.
const preselected = new WeakSet();
function person(ctx) {
 const {kit, t, model: m, values: v} = ctx, {h} = kit, name = m.name, suggested = m.suggested?.service;
 // The plan (3.5): the app on the person's own phone stands chosen while nothing is; Save stores it. Once per
 // reading of the model, so Undo goes back to No phone.
 if (m.phone == null && suggested && !ctx.readOnly && !preselected.has(m)) { preselected.add(m); v.phone = suggested; }
 const phones = m.phones || [];
 const options = phones.map(p => ({value: p.service, label: phoneText(t, p.label, p.kind)}));
 const noPhone = {value: none, label: t('No phone')};
 if (suggested && options[0]?.value === suggested) options.splice(1, 0, noPhone); else options.unshift(noPhone);
 const phoneHelp = value => (value === suggested && m.phone == null ? t('Suggested: the app on {name}\'s own phone. Choose Save to use it.', {name})
  : phones.some(p => p.service === value && p.kind === 'gone') ? t('This phone is no longer in Home Assistant: the messages show in Home Assistant until you choose another one.')
   : t('Choose No phone to stop messages to a phone; they then show in Home Assistant.'));
 const houseHelp = on => (on ? t('{name} gets the messages about the house too.', {name}) : t('Off: {name} gets no messages about the house.', {name}));
 // Leaving with only the suggestion standing (nothing touched): it was a proposal, not your change, so no "Not saved"
 // draft stays behind; the next visit proposes it again. Never a question.
 if (suggested) ctx.guard(() => { if (m.phone == null && v.phone === suggested && v.house_too === (m.house_too === true)) v.phone = none; return null; });
 const phone = ctx.field('select', 'phone', {label: t('Phone or app'), options, help: phoneHelp(v.phone), onChange: value => setHelp(phone, phoneHelp(value))});
 const house = ctx.field('toggle', 'house_too', {label: t('Also messages about the house'), help: houseHelp(v.house_too), onChange: on => setHelp(house, houseHelp(on))});
 return h('div', {class: 'nn-page', 'data-screen': 'person'}, h('div', {class: 'ot-card nn-card'}, phone, house));
}

// #notifications/house: "Which messages": the house, then the rooms (each opens its own screen).
function house(ctx) {
 const {kit, t, model: m, values: v} = ctx, {h} = kit;
 const groups = h('div', {class: 'nn-groups', 'data-kinds': 'house'},
  ctx.field(kindsField(kit, t, m.kinds?.problems || []), 'problems', {label: t('Problems')}),
  ctx.field(kindsField(kit, t, m.kinds?.maintenance || []), 'maintenance', {label: t('Maintenance')}));
 groups.hidden = !v.on;
 let status = null;
 const help = on => (on ? houseWho(t, status) || t('Messages about the whole house, day and night, also when nobody is home.') : t('Off: no messages about the house.'));
 const toggle = ctx.field('toggle', 'on', {label: t('Notify about the house'), help: help(v.on),
  onChange: on => { groups.hidden = !on; setHelp(toggle, help(on)); }});
 const rows = h('div', {class: 'nn-rows', 'data-rooms': ''}, kit.skeleton('rows', 2));
 fetchExtra(ctx, got => {
  if (got.status) { status = got.status; setHelp(toggle, help(ctx.values.on)); }
  if (!got.rooms) return;
  if (got.rooms.failed) { rows.replaceChildren(kit.notice(t('The rooms could not be read. Reload the page.'), 'error')); return; }
  const list = got.rooms.rooms || [];
  rows.replaceChildren(...(list.length ? list.map(r => {
   const route = '#room/' + encodeURIComponent(r.room);
   // The room screen opens with its section "Notifications for this room" open (the rooms module remembers folds).
   // While on: who gets them, in the backend's sentence (1.4.2, recipients per room; chosen on the room screen).
   const who = r.on && r.recipients_line ? [say(ctx, r.recipients_line)] : [];
   return kit.row({label: r.name, summary: [say(ctx, r.summary || {}), ...who], route, data: {room: r.room}, onClick: e => {
    if (e.button || e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault();
    const folds = kit.memory('room-folds:' + r.room), shadow = e.currentTarget.getRootNode();
    folds.set({...(folds.get() || {}), notifications: true});
    ctx.navigate(route);
    // On a phone that section is far down the room screen: brought into view once the screen is drawn (at most 5 s).
    const until = Date.now() + 5000, look = () => {
     const fold = shadow.querySelector?.('[data-page="rooms"] .ot-fold[data-fold="notifications"]');
     if (fold) fold.scrollIntoView({block: 'start'}); else if (Date.now() < until) requestAnimationFrame(look);
    };
    requestAnimationFrame(look);
   }});
  }) : [kit.empty({icon: 'thermostat', text: t('The E32 has not reported any rooms yet.')})]));
 });
 return h('div', {class: 'nn-page', 'data-screen': 'house'},
  kit.card({title: t('The house'), icon: 'home', cls: 'nn-card', data: {block: 'house'}}, toggle, groups),
  kit.card({title: t('Rooms'), icon: 'thermostat', summary: t('A room\'s messages, and who gets them, are set on its own screen.'), cls: 'nn-card', data: {block: 'rooms'}}, rows));
}

(window.OpenThermostatSettingsSections ||= []).push(['notifications', {
 title: (model, item) => (item === 'people' ? 'Who gets messages' : item === 'house' ? 'Which messages' : 'Notifications'),
 subtitle: (model, item) => (item == null ? 'Messages on your phone about a room or the house. Nothing is on until you switch it on.'
  : item === 'people' ? 'Each person\'s phone, and whether they also get the messages about the house.'
   : item === 'house' ? 'Messages about the house and about each room.' : 'The phone or app that gets this person\'s messages.'),
 parent: item => (String(item).startsWith(person_) ? {route: '#notifications/people', label: 'Who gets messages'} : null),
 texts: TEXTS,
 errors: ERRORS,
 cards: true,
 skeleton: 'rows',
 values,
 // Only what differs from the screen as shown; No phone is sent as null. A preselected suggestion counts as a change.
 toSave: (v, m) => {
  const shown = values(m), out = Object.fromEntries(Object.entries(v).filter(([k, x]) => !same(x, shown[k])));
  if (out.phone === none) out.phone = null;
  return out;
 },
 // "Changed by you; elsewhere it is now …" in this screen's words.
 shown: (key, value, t) => (Array.isArray(value) ? value.map(k => (KINDS[k] ? t(KINDS[k]) : k)).join(', ')
  : key === 'phone' ? (value === none ? t('No phone') : `notify.${value}`) : undefined),
 render: ctx => {
  const {item} = ctx;
  const el = item == null ? overview(ctx) : item === 'people' ? people(ctx) : item === 'house' ? house(ctx) : person(ctx);
  el.append(ctx.kit.h('style', {text: CSS}));
  return el;
 }
}]);
