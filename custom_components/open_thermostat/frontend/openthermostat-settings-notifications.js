/* The section Notifications of the settings panel (1.4): one screen with Configure → Notifications' three forms together,
   People and phones, The house and Rooms, each with what is set now. Backend settings_notifications.py (the forms' own
   checks and write); labels and explanations are Configure's words. */
const TEXTS = {
 nl: {
  'Notifications': 'Meldingen',
  'Messages on your phone about a room or the house. Nothing is on until you switch it on.': 'Berichten op je telefoon over een ruimte of het huis. Er staat niets aan tot je het zelf aanzet.',
  'People and phones': 'Personen en telefoons',
  'The phone or app that gets each person\'s messages, usually the Home Assistant app on their own phone; other notify services (Telegram, e-mail …) work too. Someone without a phone sees the messages in Home Assistant instead.': 'De telefoon of app die de berichten van elke persoon krijgt, meestal de Home Assistant-app op de eigen telefoon; andere meldingsdiensten (Telegram, e-mail …) werken ook. Wie geen telefoon heeft, ziet de berichten in Home Assistant.',
  'There are no people in Home Assistant yet. Add a person under Settings → People, then choose their phone here.': 'Er zijn nog geen personen in Home Assistant. Voeg een persoon toe onder Instellingen → Personen en kies daarna hier de telefoon.',
  'Phone or app': 'Telefoon of app',
  'Choose No phone to stop messages to a phone; they then show in Home Assistant.': 'Kies Geen telefoon om geen berichten meer naar een telefoon te sturen; ze verschijnen dan in Home Assistant.',
  'No phone': 'Geen telefoon',
  '{name} (Home Assistant app)': '{name} (Home Assistant-app)',
  '{service} (not found)': '{service} (niet gevonden)',
  'Suggested: {phone}, the app on their own phone.': 'Voorgesteld: {phone}, de app op de eigen telefoon.',
  'Use it': 'Gebruiken',
  'Also messages about the house': 'Ook meldingen over het huis',
  'Problems and maintenance of the boiler and the E32. Only the people with this on get them.': 'Problemen en onderhoud van de ketel en de E32. Alleen de personen bij wie dit aan staat krijgen ze.',
  'The house': 'Het huis',
  'Messages about the whole house, day and night, also when nobody is home.': 'Berichten over het hele huis, dag en nacht, ook als niemand thuis is.',
  'Each problem has to last a while first, so a short hiccup never sends one; a maintenance message comes once (per code, per version).': 'Elk probleem moet eerst even duren, dus een korte hapering stuurt nooit een bericht; een onderhoudsmelding komt één keer (per code, per versie).',
  'They go to: {people}.': 'Ze gaan naar: {people}.',
  'Nobody gets these yet: switch on “Also messages about the house” for a person above. Until then they show in Home Assistant.': 'Nog niemand krijgt deze: zet hierboven bij een persoon “Ook meldingen over het huis” aan. Tot dan verschijnen ze in Home Assistant.',
  'Notify about the house': 'Meldingen over het huis',
  'Off: no messages about the house.': 'Uit: geen berichten over het huis.',
  'Problems': 'Problemen',
  'Choose which problems you want to hear about.': 'Kies over welke problemen je een bericht wilt.',
  'Maintenance': 'Onderhoud',
  'The boiler asking for maintenance, a new version of the E32 firmware or of this integration, and the daily backup of the E32 settings that keeps failing.': 'De ketel die om onderhoud vraagt, een nieuwe versie van de E32-firmware of van deze integratie, en de dagelijkse back-up van de E32-instellingen die steeds mislukt.',
  'Rooms': 'Ruimtes',
  'Messages about an open window or a cold room go only to the people who are home. Between 23:00 and 07:00 room messages wait until the morning, and the same message comes at most once every 2 hours.': 'Berichten over een open raam of een koude ruimte krijgen alleen de personen die thuis zijn. Tussen 23:00 en 07:00 wachten berichten over ruimtes tot de ochtend, en hetzelfde bericht komt hooguit eens per 2 uur.',
  'The E32 has not reported any rooms yet.': 'De E32 heeft nog geen ruimtes gemeld.',
  'Notify about this room': 'Meldingen over deze ruimte',
  'Off: no messages about this room.': 'Uit: geen berichten over deze ruimte.',
  'Messages about this room go to: {people}.': 'Berichten over deze ruimte gaan naar: {people}.',
  'everyone with a phone (this room has no people of its own)': 'iedereen met een telefoon (deze ruimte heeft geen eigen personen)',
  'Messages': 'Berichten',
  'Choose which messages you want.': 'Kies welke berichten je wilt.',
  'Window or door open while the room heats': 'Raam of deur open terwijl de ruimte verwarmt',
  'Room stays cold (more than 1 °C below its target for over an hour)': 'Ruimte blijft koud (meer dan 1 °C onder de gewenste temperatuur, langer dan een uur)',
  'Temperature sensor silent for 30 minutes': 'Temperatuursensor 30 minuten stil',
  'Battery of a thermometer or valve low': 'Batterij van een thermometer of kraan bijna leeg',
  'Boiler fault': 'Ketelstoring',
  'E32 not reporting for 10 minutes, and when it is back': 'E32 meldt zich 10 minuten niet, en als hij er weer is',
  'E32 waits for your confirmation to control the boiler': 'E32 wacht op je bevestiging om de ketel te regelen',
  'Frost protection on': 'Vorstbeveiliging aan',
  'Water pressure low': 'Waterdruk te laag',
  'Boiler asks for maintenance (H code)': 'Ketel vraagt om onderhoud (H-code)',
  'New version of the E32 firmware or of this integration': 'Nieuwe versie van de E32-firmware of van deze integratie',
  'Daily backup of the E32 settings keeps failing': 'Dagelijkse back-up van de E32-instellingen mislukt steeds',
  'E32 ready to plan the heating (asks for your confirmation once)': 'E32 klaar om de verwarming te plannen (vraagt één keer je bevestiging)',
  'Choose at least one message, or switch notifications off.': 'Kies minstens één bericht, of zet de meldingen uit.',
  'Choose one of the phones in the list.': 'Kies een van de telefoons in de lijst.',
  'These notifications were changed meanwhile. Reload the page and try again.': 'Deze meldingen zijn intussen gewijzigd. Laad de pagina opnieuw en probeer het opnieuw.'
 },
 pl: {
  'Notifications': 'Powiadomienia',
  'Messages on your phone about a room or the house. Nothing is on until you switch it on.': 'Wiadomości na telefon o pomieszczeniu lub domu. Nic nie jest włączone, dopóki sam tego nie włączysz.',
  'People and phones': 'Osoby i telefony',
  'The phone or app that gets each person\'s messages, usually the Home Assistant app on their own phone; other notify services (Telegram, e-mail …) work too. Someone without a phone sees the messages in Home Assistant instead.': 'Telefon lub aplikacja, która otrzymuje wiadomości każdej osoby, zwykle aplikacja Home Assistant na własnym telefonie; inne usługi powiadomień (Telegram, e-mail …) też działają. Kto nie ma telefonu, zobaczy wiadomości w Home Assistant.',
  'There are no people in Home Assistant yet. Add a person under Settings → People, then choose their phone here.': 'W Home Assistant nie ma jeszcze osób. Dodaj osobę w Ustawienia → Osoby, a potem wybierz tutaj jej telefon.',
  'Phone or app': 'Telefon lub aplikacja',
  'Choose No phone to stop messages to a phone; they then show in Home Assistant.': 'Wybierz Brak telefonu, aby nie wysyłać już wiadomości na telefon; pojawią się wtedy w Home Assistant.',
  'No phone': 'Brak telefonu',
  '{name} (Home Assistant app)': '{name} (aplikacja Home Assistant)',
  '{service} (not found)': '{service} (nie znaleziono)',
  'Suggested: {phone}, the app on their own phone.': 'Sugerowane: {phone}, aplikacja na własnym telefonie.',
  'Use it': 'Użyj',
  'Also messages about the house': 'Także wiadomości o domu',
  'Problems and maintenance of the boiler and the E32. Only the people with this on get them.': 'Problemy i konserwacja kotła oraz E32. Otrzymują je tylko osoby, które mają to włączone.',
  'The house': 'Dom',
  'Messages about the whole house, day and night, also when nobody is home.': 'Wiadomości o całym domu, w dzień i w nocy, także gdy nikogo nie ma w domu.',
  'Each problem has to last a while first, so a short hiccup never sends one; a maintenance message comes once (per code, per version).': 'Każdy problem musi najpierw trochę potrwać, więc krótka przerwa nigdy nie wysyła wiadomości; wiadomość o konserwacji przychodzi raz (na kod, na wersję).',
  'They go to: {people}.': 'Trafiają do: {people}.',
  'Nobody gets these yet: switch on “Also messages about the house” for a person above. Until then they show in Home Assistant.': 'Nikt ich jeszcze nie otrzymuje: włącz powyżej „Także wiadomości o domu” przy osobie. Do tego czasu pojawiają się w Home Assistant.',
  'Notify about the house': 'Powiadomienia o domu',
  'Off: no messages about the house.': 'Wyłączone: brak wiadomości o domu.',
  'Problems': 'Problemy',
  'Choose which problems you want to hear about.': 'Wybierz, o których problemach chcesz otrzymywać wiadomości.',
  'Maintenance': 'Konserwacja',
  'The boiler asking for maintenance, a new version of the E32 firmware or of this integration, and the daily backup of the E32 settings that keeps failing.': 'Kocioł wymagający konserwacji, nowa wersja oprogramowania E32 lub tej integracji oraz codzienna kopia ustawień E32, która stale się nie udaje.',
  'Rooms': 'Pomieszczenia',
  'Messages about an open window or a cold room go only to the people who are home. Between 23:00 and 07:00 room messages wait until the morning, and the same message comes at most once every 2 hours.': 'Wiadomości o otwartym oknie lub zimnym pomieszczeniu otrzymują tylko osoby, które są w domu. Między 23:00 a 07:00 wiadomości o pomieszczeniach czekają do rana, a ta sama wiadomość przychodzi najwyżej raz na 2 godziny.',
  'The E32 has not reported any rooms yet.': 'E32 nie zgłosił jeszcze żadnych pomieszczeń.',
  'Notify about this room': 'Powiadomienia o tym pomieszczeniu',
  'Off: no messages about this room.': 'Wyłączone: brak wiadomości o tym pomieszczeniu.',
  'Messages about this room go to: {people}.': 'Wiadomości o tym pomieszczeniu trafiają do: {people}.',
  'everyone with a phone (this room has no people of its own)': 'wszyscy z telefonem (to pomieszczenie nie ma własnych osób)',
  'Messages': 'Wiadomości',
  'Choose which messages you want.': 'Wybierz, które wiadomości chcesz otrzymywać.',
  'Window or door open while the room heats': 'Okno lub drzwi otwarte podczas ogrzewania',
  'Room stays cold (more than 1 °C below its target for over an hour)': 'Pomieszczenie pozostaje zimne (ponad 1 °C poniżej temperatury docelowej przez ponad godzinę)',
  'Temperature sensor silent for 30 minutes': 'Czujnik temperatury milczy od 30 minut',
  'Battery of a thermometer or valve low': 'Słaba bateria termometru lub zaworu',
  'Boiler fault': 'Usterka kotła',
  'E32 not reporting for 10 minutes, and when it is back': 'E32 nie odzywa się od 10 minut, i gdy znów jest dostępny',
  'E32 waits for your confirmation to control the boiler': 'E32 czeka na Twoje potwierdzenie, by sterować kotłem',
  'Frost protection on': 'Ochrona przed mrozem włączona',
  'Water pressure low': 'Ciśnienie wody za niskie',
  'Boiler asks for maintenance (H code)': 'Kocioł wymaga konserwacji (kod H)',
  'New version of the E32 firmware or of this integration': 'Nowa wersja oprogramowania E32 lub tej integracji',
  'Daily backup of the E32 settings keeps failing': 'Codzienna kopia ustawień E32 stale się nie udaje',
  'E32 ready to plan the heating (asks for your confirmation once)': 'E32 gotowy do planowania ogrzewania (raz prosi o potwierdzenie)',
  'Choose at least one message, or switch notifications off.': 'Wybierz co najmniej jedną wiadomość albo wyłącz powiadomienia.',
  'Choose one of the phones in the list.': 'Wybierz jeden z telefonów z listy.',
  'These notifications were changed meanwhile. Reload the page and try again.': 'Te powiadomienia zostały w międzyczasie zmienione. Wczytaj stronę ponownie i spróbuj jeszcze raz.'
 }};
// The messages of a room and of the house, in Configure's words (selector notification_room_kind / notification_house_kind).
const KINDS = {
 window: 'Window or door open while the room heats',
 cold: 'Room stays cold (more than 1 °C below its target for over an hour)',
 sensor: 'Temperature sensor silent for 30 minutes',
 battery: 'Battery of a thermometer or valve low',
 boiler_fault: 'Boiler fault',
 e32_offline: 'E32 not reporting for 10 minutes, and when it is back',
 awaiting_confirmation: 'E32 waits for your confirmation to control the boiler',
 frost: 'Frost protection on',
 pressure_low: 'Water pressure low',
 maintenance: 'Boiler asks for maintenance (H code)',
 update: 'New version of the E32 firmware or of this integration',
 backup: 'Daily backup of the E32 settings keeps failing',
 plan_ready: 'E32 ready to plan the heating (asks for your confirmation once)'};
const ERRORS = {
 notification_kinds_needed: 'Choose at least one message, or switch notifications off.',
 notification_phone_invalid: 'Choose one of the phones in the list.',
 notification_invalid: 'These notifications were changed meanwhile. Reload the page and try again.',
 notification_person_invalid: 'These notifications were changed meanwhile. Reload the page and try again.'};
const CSS = `.ot-block{padding:16px 0 8px;border-top:1px solid var(--ot-divider)}.ot-block:first-of-type{border-top:0;padding-top:6px}
.ot-block>h3{margin:0;font-size:18px;font-weight:500}.ot-block>.help{margin:4px 0 6px}.ot-item{padding:12px 0 2px;border-top:1px solid var(--ot-divider)}
.ot-item>h4{margin:0;font-size:16px;font-weight:500;overflow-wrap:anywhere}.ot-line{margin:4px 0 2px;color:var(--ot-muted);overflow-wrap:anywhere}
.ot-item .field:first-of-type{border-top:0}.ot-suggest{display:flex;flex-wrap:wrap;align-items:center;gap:0 8px}.ot-suggest .btn{min-height:32px;padding:4px 10px}
.ot-checks{display:grid;gap:2px}.ot-check{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:start;padding:7px 0;cursor:pointer}
.ot-check input{margin:2px 0 0;width:18px;height:18px;accent-color:var(--ot-fill)}.ot-check input:focus-visible{outline:3px solid var(--ot-accent);outline-offset:2px}
.ot-check input:disabled{opacity:.6;cursor:default}`;

const none = 'none';  // the value of No phone
let seq = 0;
// The values the screen edits: one key per field (a person's phone and tick, the house, a room's switch and messages).
function values(m) {
 const v = {house_on: m.house.on, house_problems: [...m.house.problems], house_maintenance: [...m.house.maintenance]};
 for (const p of m.people) { v['phone:' + p.id] = p.phone; v['house:' + p.id] = p.house; }
 for (const r of m.rooms) { v['room:' + r.id] = r.on; v['kinds:' + r.id] = [...r.kinds]; }
 return v;
}
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// A group of checkboxes (several messages), built on the kit's field frame: the value is the chosen kinds in their order.
const checks = (kit, kinds, t) => o => {
 const id = 'ot-n-' + ++seq, inputs = [];
 const group = kit.h('div', {class: 'ot-checks', role: 'group', 'aria-labelledby': id + '-label'});
 for (const kind of kinds) {
  const input = kit.h('input', {type: 'checkbox', id: `${id}-${kind}`, value: kind, disabled: o.disabled, 'data-fk': `${o.key}:${kind}`});
  input.checked = (o.value || []).includes(kind);
  input.addEventListener('change', () => o.onChange?.(inputs.filter(i => i.checked).map(i => i.value)));
  inputs.push(input);
  group.append(kit.h('label', {class: 'ot-check', for: input.id}, input, kit.h('span', {text: t(KINDS[kind] || kind)})));
 }
 const api = kit.shell('checks', {...o, id}, group, false);
 api.target = () => group;
 api.focus = () => (inputs.find(i => i.checked) || inputs[0])?.focus();
 api.describe();
 return api;
};

function phoneOptions(m, person, t) {
 const options = [{value: none, label: t('No phone')}, ...m.phones.map(p => ({value: p.service,
  label: p.app ? t('{name} (Home Assistant app)', {name: p.app}) : `notify.${p.service}`}))];
 if (person.phone !== none && !m.phones.some(p => p.service === person.phone))
  options.push({value: person.phone, label: t('{service} (not found)', {service: `notify.${person.phone}`})});  // stays visible
 return options;
}

function people(ctx, refresh) {
 const {kit, t, model: m} = ctx;
 const block = kit.h('section', {class: 'ot-block', 'data-block': 'people'}, kit.h('h3', {text: t('People and phones')}),
  kit.h('p', {class: 'help', text: t('The phone or app that gets each person\'s messages, usually the Home Assistant app on their own phone; other notify services (Telegram, e-mail …) work too. Someone without a phone sees the messages in Home Assistant instead.')}));
 if (!m.people.length) {
  block.append(kit.h('p', {class: 'ot-line', text: t('There are no people in Home Assistant yet. Add a person under Settings → People, then choose their phone here.')}));
  return block;
 }
 for (const p of m.people) {
  const item = kit.h('div', {class: 'ot-item', 'data-person': p.id}, kit.h('h4', {text: p.name}));
  const phone = ctx.field('select', 'phone:' + p.id, {label: t('Phone or app'), options: phoneOptions(m, p, t),
   help: t('Choose No phone to stop messages to a phone; they then show in Home Assistant.'), onChange: () => refresh()});
  item.append(phone);
  const app = p.suggested && m.phones.find(x => x.service === p.suggested);
  if (app && !ctx.readOnly) {
   const label = app.app ? t('{name} (Home Assistant app)', {name: app.app}) : `notify.${app.service}`;
   const line = kit.h('p', {class: 'help ot-suggest', 'data-suggest': p.id}, t('Suggested: {phone}, the app on their own phone.', {phone: label}),
    kit.button(t('Use it'), () => { const s = phone.querySelector('select'); s.value = p.suggested; s.dispatchEvent(new Event('change')); }, 'text'));
   item.append(line);
   refresh.suggest.push(() => { line.hidden = ctx.values['phone:' + p.id] !== none; });
  }
  item.append(ctx.field('toggle', 'house:' + p.id, {label: t('Also messages about the house'),
   help: t('Problems and maintenance of the boiler and the E32. Only the people with this on get them.'), onChange: () => refresh()}));
  block.append(item);
 }
 return block;
}

function house(ctx, refresh) {
 const {kit, t, model: m, values: v} = ctx;
 const who = kit.h('p', {class: 'ot-line', 'data-who': ''});
 refresh.who = () => {
  const names = m.people.filter(p => v['house:' + p.id]).map(p => p.name);
  who.textContent = names.length ? t('They go to: {people}.', {people: names.join(', ')})
   : t('Nobody gets these yet: switch on “Also messages about the house” for a person above. Until then they show in Home Assistant.');
 };
 const kinds = kit.h('div', {class: 'fields', 'data-kinds': 'house'},
  ctx.field(checks(kit, m.kinds.problems, t), 'house_problems', {label: t('Problems'), help: t('Choose which problems you want to hear about.')}),
  ctx.field(checks(kit, m.kinds.maintenance, t), 'house_maintenance', {label: t('Maintenance'),
   help: t('The boiler asking for maintenance, a new version of the E32 firmware or of this integration, and the daily backup of the E32 settings that keeps failing.')}));
 refresh.shown.push(() => { kinds.hidden = !v.house_on; });
 return kit.h('section', {class: 'ot-block', 'data-block': 'house'}, kit.h('h3', {text: t('The house')}),
  kit.h('p', {class: 'help', text: `${t('Messages about the whole house, day and night, also when nobody is home.')} ${t('Each problem has to last a while first, so a short hiccup never sends one; a maintenance message comes once (per code, per version).')}`}),
  who,
  ctx.field('toggle', 'house_on', {label: t('Notify about the house'), help: t('Off: no messages about the house.'), onChange: () => refresh()}),
  kinds);
}

function rooms(ctx, refresh) {
 const {kit, t, model: m, values: v} = ctx;
 const block = kit.h('section', {class: 'ot-block', 'data-block': 'rooms'}, kit.h('h3', {text: t('Rooms')}),
  kit.h('p', {class: 'help', text: t('Messages about an open window or a cold room go only to the people who are home. Between 23:00 and 07:00 room messages wait until the morning, and the same message comes at most once every 2 hours.')}));
 if (!m.rooms.length) { block.append(kit.h('p', {class: 'ot-line', text: t('The E32 has not reported any rooms yet.')})); return block; }
 for (const r of m.rooms) {
  const kinds = kit.h('div', {class: 'fields', 'data-kinds': r.id},
   ctx.field(checks(kit, m.kinds.room, t), 'kinds:' + r.id, {label: t('Messages'), help: t('Choose which messages you want.')}));
  refresh.shown.push(() => { kinds.hidden = !v['room:' + r.id]; });
  block.append(kit.h('div', {class: 'ot-item', 'data-room': r.id}, kit.h('h4', {text: r.name}),
   kit.h('p', {class: 'ot-line', text: t('Messages about this room go to: {people}.', {people: r.people.length ? r.people.join(', ')
    : t('everyone with a phone (this room has no people of its own)')})}),
   ctx.field('toggle', 'room:' + r.id, {label: t('Notify about this room'), help: t('Off: no messages about this room.'), onChange: () => refresh()}),
   kinds));
 }
 return block;
}

(window.OpenThermostatSettingsSections ||= []).push(['notifications', {
 title: 'Notifications',
 subtitle: 'Messages on your phone about a room or the house. Nothing is on until you switch it on.',
 texts: TEXTS,
 errors: ERRORS,
 values,
 // Only what you changed (the backend keeps what is shown for the rest, as each Configure form does).
 toSave: (v, m) => { const before = values(m); return Object.fromEntries(Object.entries(v).filter(([k, x]) => !same(x, before[k]))); },
 // "Changed by you; elsewhere it is now …" in the screen's words.
 shown: (key, value, t) => (Array.isArray(value) ? value.map(k => t(KINDS[k] || k)).join(', ')
  : key.startsWith('phone:') ? (value === none ? t('No phone') : `notify.${value}`) : null),
 render: ctx => {
  const {kit} = ctx;
  // What follows a change without a redraw: who gets the house messages, the messages shown only while switched on.
  const refresh = () => { refresh.who?.(); for (const f of [...refresh.shown, ...refresh.suggest]) f(); };
  refresh.shown = []; refresh.suggest = [];
  const root = kit.h('div', {class: 'ot-notifications', 'data-screen': 'notifications'}, kit.h('style', {text: CSS}),
   people(ctx, refresh), house(ctx, refresh), rooms(ctx, refresh));
  refresh();
  return root;
 }
}]);
