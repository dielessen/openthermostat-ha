/* The settings panel of the OpenThermostat dashboard (1.4): the tab "Settings" / "Instellen" / "Ustawienia".
   One web component that knows only `hass` and its route (after #: #overview, #<section>, #<section>/<item>, #room/<id>;
   pushState and popstate); backend settings.py. The kit (window.OpenThermostatSettingsKit) builds a section; the core
   owns the save bar, the read-only page and the "changed elsewhere" banner. Texts: TEXTS, English key, Dutch and Polish
   values (test/ha-settings-texts.test.cjs). How to build a section: HA-INSTELPANEEL-ONTWERP.nl.md, chapter 10. */
const SECTION_ORDER = ['rooms', 'house', 'heating', 'devices', 'notifications', 'energy', 'general', 'advanced'];
const TITLES = {rooms: 'Rooms', house: 'House', heating: 'Heating and boiler', devices: 'Devices', notifications: 'Notifications',
 energy: 'Energy and outdoor temperature', general: 'Dashboard and name', advanced: 'Advanced'};
const ALIASES = {room: 'rooms'};  // #room/<id> opens the section rooms with that item
const WIDE = 700;
const CONFIGURE = '/config/integrations/integration/open_thermostat';
const TEXTS = {
 nl: {
  'Settings': 'Instellen',
  'The E32 keeps most of these settings and works with them, also without Home Assistant.': 'De E32 bewaart de meeste van deze instellingen en regelt ermee, ook zonder Home Assistant.',
  'Rooms': 'Ruimtes', 'House': 'Huis', 'Heating and boiler': 'Verwarming en ketel', 'Devices': 'Apparaten', 'Notifications': 'Meldingen',
  'Energy and outdoor temperature': 'Energie en buitentemperatuur', 'Dashboard and name': 'Dashboard en naam', 'Advanced': 'Geavanceerd',
  'Only an administrator of Home Assistant can change this.': 'Alleen een beheerder van Home Assistant kan dit wijzigen.',
  'Loading…': 'Laden…', 'Saving…': 'Opslaan…', 'Saved.': 'Opgeslagen.', 'You changed something.': 'Je hebt iets gewijzigd.',
  'Save': 'Opslaan', 'Undo': 'Ongedaan maken', 'Cancel': 'Annuleren', 'Not saved': 'Niet opgeslagen',
  'Choose a part on the left to see and change it.': 'Kies links een onderdeel om het te bekijken en te wijzigen.',
  'Back to {page}': 'Terug naar {page}',
  'You change this part in Configure for now.': 'Dit onderdeel wijzig je voorlopig in Configureren.',
  'Connect the E32 first: Configure → E32 connection.': 'Verbind eerst de E32: Configureren → E32-verbinding.',
  'Open Configure': 'Configureren openen',
  'Changed elsewhere': 'Elders gewijzigd',
  'These settings were changed elsewhere while you were editing. What you changed is kept and marked; the rest now shows what is saved. Save again to keep your changes.': 'Deze instellingen zijn intussen elders gewijzigd. Wat jij wijzigde blijft staan en is gemarkeerd; de rest toont nu wat er is opgeslagen. Sla opnieuw op om je wijzigingen te bewaren.',
  'Changed by you': 'Door jou gewijzigd',
  'Changed by you; elsewhere it is now {value}.': 'Door jou gewijzigd; elders is het nu {value}.',
  'On': 'Aan', 'Off': 'Uit',
  'Search by name': 'Zoek op naam', 'No area': 'Geen gebied', 'Nothing found.': 'Niets gevonden.', 'Remove {name}': '{name} verwijderen',
  'Type to see more.': 'Typ om meer te zien.',
  'The E32 could not be reached. Check the connection and try again.': 'De E32 is niet bereikbaar. Controleer de verbinding en probeer het opnieuw.',
  'The change could not be confirmed. Reload the page to see what is saved.': 'De wijziging kon niet worden bevestigd. Laad de pagina opnieuw om te zien wat er is opgeslagen.',
  'This installation is not available. Look under Settings → Devices & services → OpenThermostat.': 'Deze installatie is niet beschikbaar. Kijk bij Instellingen → Apparaten en diensten → OpenThermostat.',
  'This page does not match the installed OpenThermostat. Reload the page.': 'Deze pagina past niet bij de geïnstalleerde OpenThermostat. Laad de pagina opnieuw.',
  'The settings were changed elsewhere. Reload the page and try again.': 'De instellingen zijn elders gewijzigd. Laad de pagina opnieuw en probeer het opnieuw.',
  'This version of Home Assistant cannot store this change. Update Home Assistant and try again.': 'Deze versie van Home Assistant kan deze wijziging niet bewaren. Werk Home Assistant bij en probeer het opnieuw.',
  'This value cannot be saved. Check the fields and try again.': 'Deze waarde kan niet worden opgeslagen. Controleer de velden en probeer het opnieuw.',
  'The change was not saved ({code}). Try again.': 'De wijziging is niet opgeslagen ({code}). Probeer het opnieuw.',
  'These settings could not be read ({code}). Reload the page.': 'Deze instellingen konden niet worden gelezen ({code}). Laad de pagina opnieuw.',
  'OpenThermostat was updated. Reload the page to use the new version.': 'OpenThermostat is bijgewerkt. Laad de pagina opnieuw om de nieuwe versie te gebruiken.',
  // The section Dashboard and name: the words of Configure → Dashboard and name.
  'The name of this installation in Home Assistant and whether it shows the OpenThermostat dashboard.': 'De naam van deze installatie in Home Assistant en of het OpenThermostat-dashboard getoond wordt.',
  'Installation name': 'Naam installatie',
  'A recognisable name in Home Assistant. Your devices and their history stay as they are.': 'Een herkenbare naam in Home Assistant. Je apparaten en hun geschiedenis blijven zoals ze zijn.',
  'Show the OpenThermostat dashboard': 'OpenThermostat-dashboard tonen',
  'The OpenThermostat dashboard: your rooms at a glance, the week planner and the boiler. Your own dashboards are preserved.': 'Het OpenThermostat-dashboard: je ruimtes in één oogopslag, de weekplanner en de ketel. Je bestaande dashboards blijven behouden.',
  'Give a name of 1 to 80 characters.': 'Geef een naam van 1 tot 80 tekens.',
  'Hide the OpenThermostat dashboard?': 'OpenThermostat-dashboard verbergen?',
  'This tab goes with it. You can show the dashboard again in Configure → Dashboard and name.': 'Dit tabblad verdwijnt dan ook. Je kunt het dashboard weer tonen via Configureren → Dashboard en naam.',
  'Hide the dashboard': 'Dashboard verbergen'},
 pl: {
  'Settings': 'Ustawienia',
  'The E32 keeps most of these settings and works with them, also without Home Assistant.': 'E32 przechowuje większość tych ustawień i działa według nich, także bez Home Assistant.',
  'Rooms': 'Pomieszczenia', 'House': 'Dom', 'Heating and boiler': 'Ogrzewanie i kocioł', 'Devices': 'Urządzenia', 'Notifications': 'Powiadomienia',
  'Energy and outdoor temperature': 'Energia i temperatura zewnętrzna', 'Dashboard and name': 'Panel i nazwa', 'Advanced': 'Zaawansowane',
  'Only an administrator of Home Assistant can change this.': 'Tylko administrator Home Assistant może to zmienić.',
  'Loading…': 'Ładowanie…', 'Saving…': 'Zapisywanie…', 'Saved.': 'Zapisano.', 'You changed something.': 'Wprowadzono zmiany.',
  'Save': 'Zapisz', 'Undo': 'Cofnij', 'Cancel': 'Anuluj', 'Not saved': 'Niezapisane',
  'Choose a part on the left to see and change it.': 'Wybierz część po lewej, aby ją zobaczyć i zmienić.',
  'Back to {page}': 'Wróć do: {page}',
  'You change this part in Configure for now.': 'Tę część zmieniasz na razie w Konfiguruj.',
  'Connect the E32 first: Configure → E32 connection.': 'Najpierw połącz E32: Konfiguruj → Połączenie z E32.',
  'Open Configure': 'Otwórz Konfiguruj',
  'Changed elsewhere': 'Zmieniono w innym miejscu',
  'These settings were changed elsewhere while you were editing. What you changed is kept and marked; the rest now shows what is saved. Save again to keep your changes.': 'Te ustawienia zostały w międzyczasie zmienione w innym miejscu. Twoje zmiany zostają i są oznaczone; reszta pokazuje teraz to, co zapisano. Zapisz ponownie, aby zachować swoje zmiany.',
  'Changed by you': 'Zmienione przez ciebie',
  'Changed by you; elsewhere it is now {value}.': 'Zmienione przez ciebie; w innym miejscu jest teraz {value}.',
  'On': 'Włączone', 'Off': 'Wyłączone',
  'Search by name': 'Szukaj po nazwie', 'No area': 'Bez obszaru', 'Nothing found.': 'Nic nie znaleziono.', 'Remove {name}': 'Usuń: {name}',
  'Type to see more.': 'Pisz dalej, aby zobaczyć więcej.',
  'The E32 could not be reached. Check the connection and try again.': 'Nie można połączyć się z E32. Sprawdź połączenie i spróbuj ponownie.',
  'The change could not be confirmed. Reload the page to see what is saved.': 'Nie udało się potwierdzić zmiany. Wczytaj stronę ponownie, aby zobaczyć, co zapisano.',
  'This installation is not available. Look under Settings → Devices & services → OpenThermostat.': 'Ta instalacja jest niedostępna. Sprawdź w Ustawienia → Urządzenia i usługi → OpenThermostat.',
  'This page does not match the installed OpenThermostat. Reload the page.': 'Ta strona nie pasuje do zainstalowanego OpenThermostat. Wczytaj stronę ponownie.',
  'The settings were changed elsewhere. Reload the page and try again.': 'Ustawienia zostały zmienione w innym miejscu. Wczytaj stronę ponownie i spróbuj jeszcze raz.',
  'This version of Home Assistant cannot store this change. Update Home Assistant and try again.': 'Ta wersja Home Assistant nie może zapisać tej zmiany. Zaktualizuj Home Assistant i spróbuj ponownie.',
  'This value cannot be saved. Check the fields and try again.': 'Nie można zapisać tej wartości. Sprawdź pola i spróbuj ponownie.',
  'The change was not saved ({code}). Try again.': 'Zmiana nie została zapisana ({code}). Spróbuj ponownie.',
  'These settings could not be read ({code}). Reload the page.': 'Nie udało się odczytać tych ustawień ({code}). Wczytaj stronę ponownie.',
  'OpenThermostat was updated. Reload the page to use the new version.': 'OpenThermostat został zaktualizowany. Wczytaj stronę ponownie, aby użyć nowej wersji.',
  'The name of this installation in Home Assistant and whether it shows the OpenThermostat dashboard.': 'Nazwa tej instalacji w Home Assistant i to, czy pokazywany jest panel OpenThermostat.',
  'Installation name': 'Nazwa instalacji',
  'A recognisable name in Home Assistant. Your devices and their history stay as they are.': 'Rozpoznawalna nazwa w Home Assistant. Twoje urządzenia i ich historia pozostają bez zmian.',
  'Show the OpenThermostat dashboard': 'Pokaż panel OpenThermostat',
  'The OpenThermostat dashboard: your rooms at a glance, the week planner and the boiler. Your own dashboards are preserved.': 'Panel OpenThermostat: Twoje pomieszczenia w skrócie, planer tygodniowy i kocioł. Twoje własne panele pozostają bez zmian.',
  'Give a name of 1 to 80 characters.': 'Podaj nazwę o długości od 1 do 80 znaków.',
  'Hide the OpenThermostat dashboard?': 'Ukryć panel OpenThermostat?',
  'This tab goes with it. You can show the dashboard again in Configure → Dashboard and name.': 'Ta karta również zniknie. Panel możesz ponownie pokazać w Konfiguruj → Panel i nazwa.',
  'Hide the dashboard': 'Ukryj panel'}};
// The sentence of each error code the backend sends (settings.py); a section adds its own (spec.errors).
const ERRORS = {
 e32_unreachable: 'The E32 could not be reached. Check the connection and try again.',
 save_uncertain: 'The change could not be confirmed. Reload the page to see what is saved.',
 setup_save_uncertain: 'The change could not be confirmed. Reload the page to see what is saved.',
 unavailable: 'This installation is not available. Look under Settings → Devices & services → OpenThermostat.',
 unknown_section: 'This page does not match the installed OpenThermostat. Reload the page.',
 unknown_command: 'This page does not match the installed OpenThermostat. Reload the page.',
 not_admin: 'Only an administrator of Home Assistant can change this.',
 unauthorized: 'Only an administrator of Home Assistant can change this.',
 setup_changed: 'The settings were changed elsewhere. Reload the page and try again.',
 setup_platform_unsupported: 'This version of Home Assistant cannot store this change. Update Home Assistant and try again.',
 setup_invalid: 'This value cannot be saved. Check the fields and try again.'};

/* ---- texts --------------------------------------------------------------------------------------------------- */
const CATALOG = {nl: {...TEXTS.nl}, pl: {...TEXTS.pl}};
const langOf = hass => {
 const l = String(hass?.locale?.language || hass?.language || 'en').slice(0, 2).toLowerCase();
 return l === 'nl' || l === 'pl' ? l : 'en';
};
const fill = (text, values = {}) => String(text).replace(/\{(\w+)\}/g, (all, k) => (k in values ? values[k] : all));
const translate = (lang, key, values) => fill((lang !== 'en' && CATALOG[lang]?.[key]) || key, values);
// A figure and its unit stay on one line ("16 °C" never breaks before the unit), as on the room status card.
const together = text => String(text).replace(/ (°C|%|kW|min)(?=$|[\s·,.;)])/g, '\u00a0$1');

/* ---- the kit: elements ---------------------------------------------------------------------------------------- */
let seq = 0;
const uid = p => `ot-${p}-${++seq}`;
// h('div', {class, text, hidden, on: {click}, style, ...attributes}, ...children): one element.
function h(tag, props = {}, ...children) {
 const el = document.createElement(tag);
 for (const [k, v] of Object.entries(props || {})) {
  if (v == null || v === false) continue;
  if (k === 'text') el.textContent = v;
  else if (k === 'on') for (const [ev, fn] of Object.entries(v)) el.addEventListener(ev, fn);
  else if (k === 'props') Object.assign(el, v);
  else el.setAttribute(k, v === true ? '' : v);
 }
 for (const c of children.flat()) if (c != null && c !== false) el.append(c instanceof Node ? c : String(c));
 return el;
}
const notice = (text, tone = 'info', ...more) => h('div', {class: 'notice ' + tone, role: tone === 'error' ? 'alert' : 'status'}, h('p', {text}), ...more);
const inlineError = text => h('p', {class: 'inline-error', role: 'alert', text});
const button = (text, onClick, kind = 'text', attrs = {}) => h('button', {type: 'button', class: 'btn ' + kind, on: {click: onClick}, text, ...attrs});

// A list row: the label, its summary lines under it and a chevron; a link to an in-panel route (#...), or a button.
function row({label, summary = [], value, route, onClick, current, badge, disabled, data = {}}) {
 const attrs = {class: 'row' + (disabled ? ' muted' : ''), ...(current ? {'aria-current': 'page'} : {})};
 for (const [k, v] of Object.entries(data)) attrs['data-' + k] = v;
 const el = route ? h('a', {...attrs, href: route}) : h('button', {...attrs, type: 'button'});
 if (onClick) el.addEventListener('click', onClick);
 const text = h('span', {class: 'row-text'}, h('span', {class: 'row-label'}, label, badge ? h('span', {class: 'badge', text: badge}) : null));
 for (const line of [].concat(summary).filter(Boolean)) text.append(h('span', {class: 'row-line', text: together(line)}));
 el.append(text);
 if (value != null) el.append(h('span', {class: 'row-value', text: value}));
 el.append(h('span', {class: 'chevron', 'aria-hidden': 'true'}));
 return el;
}

// The page frame: a back link (optional), the title and a subtitle; returns {el, body}.
function frame({title, subtitle, back}) {
 const head = h('header', {class: 'head'});
 if (back) head.append(h('a', {class: 'back', href: back.route, 'data-back': '', on: back.onClick ? {click: back.onClick} : null}, back.label));
 head.append(h('h2', {class: 'title', text: title, tabindex: '-1'}));
 if (subtitle) head.append(h('p', {class: 'subtitle', text: subtitle}));
 const body = h('div', {class: 'body'});
 return {el: h('section', {class: 'page'}, head, body), body};
}

/* ---- the kit: fields: fields.<kind>({key, label, help, value, disabled, onChange, ...}) -> {el, value, setError(text),
   setMark('changed' | 'conflict' | null, text), focus()} ---- */
function shell(kind, o, control, labelFor = true) {
 const id = o.id || uid(kind), wrap = h('div', {class: 'field ' + kind, 'data-field': o.key || '', 'data-kind': kind});
 const help = o.help ? h('p', {class: 'help', id: id + '-help', text: o.help}) : null;
 const mark = h('p', {class: 'mark', id: id + '-mark', hidden: true});
 const error = h('p', {class: 'error', id: id + '-error', hidden: true});
 const label = o.label ? h(labelFor ? 'label' : 'span', {class: 'label', ...(labelFor ? {for: id} : {id: id + '-label'}), text: o.label}) : null;
 wrap.append(...[label, control, help, mark, error].filter(Boolean));
 const described = () => [help && !help.hidden && help.id, !mark.hidden && mark.id, !error.hidden && error.id].filter(Boolean).join(' ');
 const api = {
  el: wrap, id,
  setError(text) {
   error.textContent = text || ''; error.hidden = !text; wrap.classList.toggle('invalid', !!text);
   api.target?.()?.setAttribute('aria-invalid', text ? 'true' : 'false'); api.describe();
  },
  setMark(kind2, text) {
   wrap.classList.toggle('changed', kind2 === 'changed'); wrap.classList.toggle('conflict', kind2 === 'conflict');
   mark.textContent = text || ''; mark.hidden = !kind2 || !text; api.describe();
  },
  describe() { const t = api.target?.(); if (t) { const d = described(); d ? t.setAttribute('aria-describedby', d) : t.removeAttribute('aria-describedby'); } },
  focus() { api.target?.()?.focus(); }
 };
 return api;
}
function inputField(kind, type, o, extra = {}) {
 const id = o.id || uid(kind);
 const input = h('input', {id, type, class: 'input', 'data-fk': o.key || '', disabled: o.disabled, required: o.required, ...extra});
 input.value = o.value ?? '';
 const control = o.unit ? h('div', {class: 'with-unit'}, input, h('span', {class: 'unit', 'aria-hidden': 'true', text: o.unit})) : input;
 const api = shell(kind, {...o, id}, control);
 api.target = () => input; api.input = input;
 const read = kind === 'number' ? () => (input.value === '' ? null : Number(input.value)) : () => input.value;
 Object.defineProperty(api, 'value', {get: read, set: v => { input.value = v ?? ''; }});
 input.addEventListener('input', () => o.onChange?.(read()));
 api.describe();
 return api;
}
const fields = {
 text: o => inputField('text', 'text', o, {maxlength: o.maxlength, autocomplete: 'off', placeholder: o.placeholder}),
 number: o => inputField('number', 'number', o, {step: o.step ?? 'any', min: o.min, max: o.max, inputmode: 'decimal',
  'aria-label': o.unit ? `${o.label} (${o.unit})` : null}),
 time: o => inputField('time', 'time', o, {step: o.seconds ? 1 : 60}),
 date: o => inputField('date', 'date', o, {min: o.min, max: o.max}),
 select(o) {
  const id = o.id || uid('select');
  const select = h('select', {id, class: 'input', 'data-fk': o.key || '', disabled: o.disabled});
  for (const opt of o.options || []) select.append(h('option', {value: opt.value, text: opt.label}));
  select.value = o.value ?? '';
  const api = shell('select', {...o, id}, select);
  api.target = () => select;
  Object.defineProperty(api, 'value', {get: () => select.value, set: v => { select.value = v ?? ''; }});
  select.addEventListener('change', () => o.onChange?.(select.value));
  api.describe();
  return api;
 },
 // Radio group: one choice, each option with its own explanation line right under it (design 4, rule 2).
 radio(o) {
  const id = o.id || uid('radio'), name = id + '-name';
  const group = h('div', {class: 'choices', role: 'radiogroup', 'aria-labelledby': id + '-label'});
  const inputs = [];
  for (const opt of o.options || []) {
   const oid = uid('opt'), input = h('input', {type: 'radio', id: oid, name, value: opt.value, disabled: o.disabled, 'data-fk': o.key ? o.key + ':' + opt.value : ''});
   input.checked = opt.value === o.value;
   input.addEventListener('change', () => { if (input.checked) o.onChange?.(opt.value); });
   inputs.push(input);
   const text = h('span', {class: 'choice-text'}, h('span', {class: 'choice-label', text: opt.label}));
   if (opt.help) { text.append(h('span', {class: 'choice-help', id: oid + '-help', text: opt.help})); input.setAttribute('aria-describedby', oid + '-help'); }
   group.append(h('label', {class: 'choice', for: oid}, input, text));
  }
  const api = shell('radio', {...o, id}, group, false);
  api.target = () => group;
  Object.defineProperty(api, 'value', {get: () => inputs.find(i => i.checked)?.value ?? null, set: v => { for (const i of inputs) i.checked = i.value === v; }});
  api.focus = () => (inputs.find(i => i.checked) || inputs[0])?.focus();
  api.describe();
  return api;
 },
 // Toggle: a switch with its label beside it; the value is true or false.
 toggle(o) {
  const id = o.id || uid('toggle');
  const input = h('input', {type: 'checkbox', role: 'switch', id, class: 'switch', 'data-fk': o.key || '', disabled: o.disabled});
  input.checked = o.value === true;
  const control = h('div', {class: 'toggle-row'}, h('label', {class: 'label', for: id, text: o.label}), input);
  const api = shell('toggle', {...o, label: null, id}, control);
  api.target = () => input;
  Object.defineProperty(api, 'value', {get: () => input.checked, set: v => { input.checked = v === true; }});
  input.addEventListener('change', () => o.onChange?.(input.checked));
  api.describe();
  return api;
 },
 entity: o => entityPicker(o)
};

/* The entity picker: hass.states by domains, device classes or a filter, grouped by area (hass.entities, hass.devices,
   hass.areas); one entity ('' or 'sensor.x') or several (multiple: true, [...]), each shown with its value now. */
function entityPicker(o) {
 const hass = o.hass, lang = langOf(hass), t = (k, v) => translate(lang, k, v), id = o.id || uid('entity'), listId = id + '-list';
 let chosen = [].concat(o.value || []).filter(Boolean), active = -1, shown = [];
 const input = h('input', {id, type: 'text', class: 'input', role: 'combobox', 'aria-autocomplete': 'list', 'aria-expanded': 'false',
  'aria-controls': listId, autocomplete: 'off', spellcheck: 'false', placeholder: o.placeholder || t('Search by name'), 'data-fk': o.key || '',
  disabled: o.disabled});
 const list = h('ul', {id: listId, class: 'options', role: 'listbox', hidden: true});
 const chips = h('div', {class: 'picked'});
 const control = h('div', {class: 'picker'}, chips, h('div', {class: 'combo'}, input, list));
 const api = shell('entity', {...o, id}, control);
 api.target = () => input;
 const stateOf = eid => hass?.states?.[eid];
 const nameOf = eid => stateOf(eid)?.attributes?.friendly_name || eid;
 const areaOf = eid => {
  const ent = hass?.entities?.[eid], area = ent?.area_id || hass?.devices?.[ent?.device_id]?.area_id;
  return (area && hass?.areas?.[area]?.name) || '';
 };
 const valueOf = eid => {
  const st = stateOf(eid);
  if (!st) return '';
  try { const v = hass.formatEntityState?.(st); if (typeof v === 'string' && v) return v; } catch (e) { /* older Home Assistant */ }
  return [st.state, st.attributes?.unit_of_measurement].filter(Boolean).join(' ');
 };
 const candidates = () => Object.keys(hass?.states || {}).filter(eid => {
  const st = stateOf(eid);
  if (chosen.includes(eid)) return false;
  if (o.domains && !o.domains.includes(eid.split('.')[0])) return false;
  if (o.deviceClasses && !o.deviceClasses.includes(st?.attributes?.device_class)) return false;
  return !o.filter || o.filter(st, eid);
 });
 const emit = () => o.onChange?.(o.multiple ? [...chosen] : chosen[0] || '');
 const drawChips = () => {
  chips.replaceChildren(...chosen.map(eid => h('span', {class: 'pick', 'data-entity': eid},
   h('span', {class: 'pick-text'}, h('span', {class: 'pick-name', text: nameOf(eid)}), h('span', {class: 'pick-id', text: [eid, valueOf(eid)].filter(Boolean).join(' · ')})),
   o.disabled ? null : button('', () => { chosen = chosen.filter(x => x !== eid); drawChips(); emit(); input.focus(); }, 'icon remove',
    {'aria-label': t('Remove {name}', {name: nameOf(eid)}), title: t('Remove {name}', {name: nameOf(eid)})}))));
  input.hidden = !o.multiple && chosen.length > 0;
 };
 const close = () => { list.hidden = true; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); active = -1; };
 const pick = eid => { chosen = o.multiple ? [...chosen, eid] : [eid]; input.value = ''; close(); drawChips(); emit(); if (!input.hidden) input.focus(); else chips.querySelector('button')?.focus(); };
 const highlight = i => {
  const opts = [...list.querySelectorAll('[role=option]')];
  if (!opts.length) return;
  active = (i + opts.length) % opts.length;
  opts.forEach((el, n) => el.setAttribute('aria-selected', n === active ? 'true' : 'false'));
  input.setAttribute('aria-activedescendant', opts[active].id); opts[active].scrollIntoView?.({block: 'nearest'});
 };
 const open = () => {
  const words = input.value.toLowerCase().split(/\s+/).filter(Boolean), groups = new Map();
  shown = candidates().map(eid => ({eid, name: nameOf(eid), area: areaOf(eid)}))
   .filter(c => words.every(w => `${c.name} ${c.eid} ${c.area}`.toLowerCase().includes(w)))
   .sort((a, b) => (a.area || '￿').localeCompare(b.area || '￿') || a.name.localeCompare(b.name));
  const limit = 60;
  for (const c of shown.slice(0, limit)) { if (!groups.has(c.area)) groups.set(c.area, []); groups.get(c.area).push(c); }
  const items = [];
  for (const [area, members] of groups) {
   items.push(h('li', {class: 'group', role: 'presentation', text: area || t('No area')}));
   for (const c of members) items.push(h('li', {id: uid('o'), role: 'option', class: 'option', 'aria-selected': 'false', 'data-entity': c.eid,
    on: {mousedown: e => { e.preventDefault(); pick(c.eid); }}}, h('span', {class: 'pick-name', text: c.name}), h('span', {class: 'pick-id', text: c.eid})));
  }
  if (!shown.length) items.push(h('li', {class: 'empty', role: 'presentation', text: t('Nothing found.')}));
  else if (shown.length > limit) items.push(h('li', {class: 'empty', role: 'presentation', text: t('Type to see more.')}));
  list.replaceChildren(...items); list.hidden = false; input.setAttribute('aria-expanded', 'true'); active = -1;
 };
 input.addEventListener('focus', open);
 input.addEventListener('input', open);
 input.addEventListener('blur', () => setTimeout(close, 0));
 input.addEventListener('keydown', e => {
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); if (list.hidden) open(); highlight(active + (e.key === 'ArrowDown' ? 1 : -1)); }
  else if (e.key === 'Enter' && !list.hidden && active >= 0) { e.preventDefault(); pick(list.querySelectorAll('[role=option]')[active].dataset.entity); }
  else if (e.key === 'Escape' && !list.hidden) { e.preventDefault(); close(); }
 });
 Object.defineProperty(api, 'value', {get: () => (o.multiple ? [...chosen] : chosen[0] || ''), set: v => { chosen = [].concat(v || []).filter(Boolean); drawChips(); }});
 drawChips(); api.describe();
 return api;
}

// The confirm dialog: a question, its consequence and two buttons; resolves true for the action, false otherwise.
function confirmDialog(root, {title, text, confirm, cancel, danger, lang = 'en'}) {
 return new Promise(resolve => {
  const t = k => translate(lang, k);
  const dialog = h('dialog', {class: 'confirm', 'aria-labelledby': 'ot-confirm-title', 'aria-describedby': 'ot-confirm-text'});
  const done = answer => { dialog.close(); dialog.remove(); resolve(answer); };
  dialog.append(h('h3', {id: 'ot-confirm-title', text: title}), text ? h('p', {id: 'ot-confirm-text', text}) : '',
   h('div', {class: 'actions'}, button(cancel || t('Cancel'), () => done(false), 'text', {'data-cancel': ''}),
    button(confirm, () => done(true), danger ? 'filled danger' : 'filled', {'data-confirm': ''})));
  dialog.addEventListener('cancel', e => { e.preventDefault(); done(false); });
  root.append(dialog);
  try { dialog.showModal(); } catch (e) { dialog.setAttribute('open', ''); }
  dialog.querySelector('[data-cancel]').focus();
 });
}

/* ---- sections: defineSection(name, {title, subtitle, texts: {nl, pl}, errors: {code: sentence}, render(ctx),
   values(model)?, toSave(values, model)?, confirm(values, model, ctx)?}); a module loaded before this one queues
   [name, spec] in window.OpenThermostatSettingsSections. ---- */
const SECTIONS = new Map();
const hosts = new Set();
function defineSection(name, spec) {
 if (!/^[a-z_]+$/.test(name) || !spec || typeof spec.render !== 'function') throw new Error('defineSection(name, {render}) needs a name and a render function');
 for (const lang of ['nl', 'pl']) Object.assign(CATALOG[lang], spec.texts?.[lang] || {});
 SECTIONS.set(name, spec);
 for (const host of hosts) host._sectionDefined(name);
}

const clone = v => (v === undefined ? undefined : JSON.parse(JSON.stringify(v)));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const parseRoute = hash => {
 const raw = String(hash || '').replace(/^#/, ''), [head, ...rest] = raw.split('/');
 const name = ALIASES[head] || head;
 if (!name || name === 'overview' || !/^[a-z_]+$/.test(name)) return {section: null, item: null};
 let item = rest.length ? rest.join('/') : null;
 try { item = item == null ? null : decodeURIComponent(item); } catch (e) { /* keep as typed */ }
 return {section: name, item: item || null};
};
const routeOf = (section, item) => '#' + (section ? section + (item ? '/' + encodeURIComponent(item) : '') : 'overview');
// A websocket error ({code, translation_placeholders}); anything else is a fault of the page itself: logged, said plainly.
const errorOf = err => {
 const code = err && (err.code || err.error?.code);
 if (!code) console.error('OpenThermostat settings', err);
 return {code: code || 'unknown', data: err?.translation_placeholders || err?.error?.translation_placeholders || {}};
};

/* ---- the panel ------------------------------------------------------------------------------------------------ */
class OpenThermostatSettings extends HTMLElement {
 constructor() {
  super();
  this.attachShadow({mode: 'open'});
  this._route = parseRoute(location.hash);
  this._drafts = new Map();  // section/item -> {values, original, token}: a draft kept while you look elsewhere
  this._overview = null; this._overviewError = null; this._page = null; this._wide = false; this._generation = 0;
  this._onPop = () => this._go(location.hash, false);
 }
 setConfig(config) {
  if (!config || typeof config.entry_id !== 'string' || !config.entry_id)
   throw new Error('This card needs the entry_id of an OpenThermostat installation; the OpenThermostat dashboard adds it for you.');
  this._config = {...config};
  if (this._hass) this._start();
 }
 set hass(hass) {
  const before = this._hass;
  this._hass = hass;
  const key = [langOf(hass), hass?.user?.is_admin];
  if (!before || !same(key, this._key)) { this._key = key; if (this._config) this._start(); return; }
  this._live();
 }
 get hass() { return this._hass; }
 getCardSize() { return 12; }
 getGridOptions() { return {columns: 'full'}; }
 connectedCallback() {
  hosts.add(this);
  window.addEventListener('popstate', this._onPop);
  if (typeof ResizeObserver === 'function') {
   this._resize = new ResizeObserver(entries => this._measure(entries[0]?.contentRect?.width));
   this._resize.observe(this);
  }
  this._route = parseRoute(location.hash);
  if (this._hass && this._config) this._start();
 }
 disconnectedCallback() {
  hosts.delete(this);
  window.removeEventListener('popstate', this._onPop);
  this._resize?.disconnect();
  clearTimeout(this._savedTimer);
 }
 get lang() { return langOf(this._hass); }
 t(key, values) { return translate(this.lang, key, values); }
 get admin() { return this._hass?.user?.is_admin !== false && this._overview?.admin !== false; }
 _measure(width) {
  const wide = (width ?? this.getBoundingClientRect().width) >= WIDE;
  if (wide === this._wide) return;
  this._wide = wide;
  this.shadowRoot.querySelector('.shell')?.classList.toggle('wide', wide);
  this._renderList(); this._renderPage();  // one column shows the list or the page; the back link differs
 }
 _start() {
  if (!this.isConnected) return;
  this._keepDraft();
  this._measure();
  this._renderShell();
  this._loadOverview();
  this._openPage();
 }
 _sectionDefined(name) { if (this._page?.section === name && this._page.status === 'fallback') this._openPage(); }
 // Navigation inside the panel: a route (#general) pushed on the history, or (popstate) the one the browser went to.
 _go(hash, push = true) {
  const route = parseRoute(hash);
  // A popstate to where the panel already is (Home Assistant closing a dialog it opened): nothing to do.
  if (!push && route.section === this._route.section && route.item === this._route.item) return;
  this._keepDraft();
  if (push) { try { history.pushState({openthermostat_settings: true}, '', routeOf(route.section, route.item)); } catch (e) { /* no history here */ } }
  this._route = route;
  this._renderList();
  this._openPage();
  if (route.section == null) this._loadOverview();
  if (!this._wide && this.getBoundingClientRect().top < 0) this.scrollIntoView({block: 'start'});
 }
 // Navigation elsewhere in Home Assistant (Configure, the week planner): its path and location-changed.
 _navigate(path) {
  try { history.pushState(null, '', path); } catch (e) { return; }
  window.dispatchEvent(new CustomEvent('location-changed', {detail: {replace: false}}));
 }
 _ws(msg) { return this._hass.callWS({entry_id: this._config.entry_id, ...msg}); }
 async _loadOverview() {
  const generation = ++this._generation;
  try {
   const result = await this._ws({type: 'open_thermostat/settings/overview', language: this.lang});
   if (generation !== this._generation) return;
   this._overview = result; this._overviewError = null;
  } catch (err) {
   if (generation !== this._generation) return;
   this._overviewError = errorOf(err).code;
  }
  this._renderList();
  if (this._page?.status === 'fallback') this._renderPage();
 }
 _keepDraft() {
  const p = this._page;
  if (p?.status === 'ready' && this._dirty()) this._drafts.set(p.key, {values: clone(p.values), original: clone(p.original), token: p.token});
 }
 async _openPage() {
  const {section, item} = this._route;
  clearTimeout(this._savedTimer);
  if (!section) { this._page = null; this._renderPage(); return; }
  const key = section + '/' + (item ?? ''), spec = SECTIONS.get(section);
  const info = this._overview?.sections?.find(s => s.name === section);
  if (!spec || (info && (!info.editable || !info.available))) { this._page = {key, section, item, status: 'fallback'}; this._renderPage(); return; }
  const page = this._page = {key, section, item, spec, status: 'loading', errors: {}, conflicts: new Set()};
  this._renderPage();
  try {
   const result = await this._ws({type: 'open_thermostat/settings/get', section, item});
   if (this._page !== page) return;
   this._ready(page, result, this._drafts.get(key));
   this._drafts.delete(key);
  } catch (err) {
   if (this._page !== page) return;
   const {code, data} = errorOf(err);
   if (code === 'unknown_section') { page.status = 'fallback'; } else { page.status = 'error'; page.baseError = code; page.basePlaceholders = data.placeholders; }
  }
  this._renderPage();
 }
 // A model came in: the values to edit, with a kept draft laid over it (its changes marked; a conflict when the
 // value elsewhere moved too).
 _ready(page, {model, token}, draft) {
  const values = page.spec.values ? page.spec.values(clone(model)) : clone(model);
  page.status = 'ready'; page.model = model; page.token = token; page.original = clone(values); page.values = clone(values);
  page.conflicts = new Set(); page.banner = false;
  if (draft) this._merge(page, draft);
 }
 _merge(page, draft) {
  for (const k of Object.keys(draft.values)) {
   // Not changed by you, or what you changed is what is saved now: the fresh value stays.
   if (same(draft.values[k], draft.original[k]) || same(draft.values[k], page.original[k])) continue;
   page.values[k] = clone(draft.values[k]);
   if (draft.token !== page.token && !same(page.original[k], draft.original[k])) page.conflicts.add(k);
  }
  page.banner = draft.token !== page.token && this._dirty(page);
 }
 _dirty(p = this._page) { return !!p && p.status === 'ready' && !same(p.values, p.original); }
 _changed(key) {
  const p = this._page;
  if (!p || p.status !== 'ready') return;
  if (p.errors[key]) { delete p.errors[key]; p.fields?.[key]?.setError(''); }
  this._markField(key);
  this._renderBar();
  if (this._dirty() !== !!this._listDirty) this._renderList();  // the list's "Not saved" follows
 }
 _markField(key) {
  const p = this._page, f = p.fields?.[key];
  if (!f) return;
  const mine = !same(p.values[key], p.original[key]);
  if (mine && p.conflicts.has(key)) f.setMark('conflict', this.t('Changed by you; elsewhere it is now {value}.', {value: p.spec.shown?.(key, p.original[key], (k, v) => this.t(k, v)) ?? this._shown(p.original[key])}));
  else f.setMark(mine ? 'changed' : null, mine ? this.t('Changed by you') : '');
 }
 _shown(v) {
  if (v === true) return this.t('On');
  if (v === false) return this.t('Off');
  if (Array.isArray(v)) return v.join(', ');
  return typeof v === 'number' ? v.toLocaleString(this.lang) : String(v ?? '');
 }
 _undo() {
  const p = this._page;
  if (!p || p.status !== 'ready') return;
  p.values = clone(p.original); p.errors = {}; p.baseError = null; p.conflicts = new Set(); p.banner = false;
  this._renderPage(); this._renderList();
 }
 // Save the page's fields; or (act) an action's own values at once, after its question; your unsaved fields stay.
 async _save(act, question) {
  const p = this._page;
  if (!p || p.status !== 'ready' || p.saving || !(act || this._dirty()) || !this.admin) return false;
  if (!act) question = p.spec.confirm?.(clone(p.values), p.model, this._ctx(p));
  if (question && !(await confirmDialog(this.shadowRoot, {...question, lang: this.lang}))) return false;
  if (this._page !== p) return false;
  const draft = act && this._dirty() ? {values: clone(p.values), original: clone(p.original), token: p.token} : null;
  p.saving = true; p.baseError = null; this._renderBar();
  try {
   const values = act || (p.spec.toSave ? p.spec.toSave(clone(p.values), p.model) : clone(p.values));
   const result = await this._ws({type: 'open_thermostat/settings/save', section: p.section, item: p.item, token: p.token, values});
   if (this._page !== p) return true;
   this._ready(p, result, draft);
   // spec.saved: a route after the save (a new room's own page).
   const next = p.spec.saved?.(result.model, p.item);
   if (next) { try { history.replaceState(history.state, '', next); } catch (e) {} this._route = parseRoute(next); this._renderList(); this._openPage(); this._loadOverview(); return; }
   p.banner = false; p.saving = false; p.saved = true;
   this._savedTimer = setTimeout(() => { if (this._page === p) { p.saved = false; this._renderBar(); } }, 4000);
   this._renderPage();
   this._loadOverview();
   return true;
  } catch (err) {
   if (this._page !== p) return false;
   p.saving = false;
   const {code, data} = errorOf(err);
   if (code === 'changed_elsewhere' && data.model && data.token) {
    const draft = {values: clone(p.values), original: clone(p.original), token: p.token};
    this._ready(p, {model: data.model, token: data.token}, draft);
    p.banner = true;
   } else if (code === 'changed_elsewhere') {
    this._keepDraft(); this._openPage(); return false;
   } else if (data.field && data.field !== 'base' && p.fields?.[data.field]) {
    p.errors[data.field] = this._error(code, data.placeholders);
   } else {
    p.baseError = code; p.basePlaceholders = data.placeholders;
   }
   this._renderPage();
   const first = Object.keys(p.errors)[0];
   if (first) p.fields?.[first]?.focus();
   return false;
  }
 }
 _error(code, placeholders = {}) {
  const sentence = this._page?.spec?.errors?.[code] || ERRORS[code];
  return sentence ? this.t(sentence, placeholders || {}) : this.t('The change was not saved ({code}). Try again.', {code});
 }
 // What a section's render gets: the model, the values it edits and the kit bound to this page.
 _ctx(p) {
  const self = this, readOnly = !this.admin;
  const settings = this._config.settings_path || '';
  return {
   hass: this._hass, lang: this.lang, admin: !readOnly, readOnly, model: p.model, values: p.values, item: p.item, section: p.section,
   kit: KIT, t: (k, v) => this.t(k, v),
   paths: {settings, configure: this._overview?.configure_path || CONFIGURE, week: settings.replace(/\/[^/]*$/, '/week-program')},
   navigate: hash => this._go(hash), open: path => this._navigate(path),
   // A field bound to values[key]: its edits mark it and show the save bar; disabled for a non-administrator.
   field(kind, key, o = {}) {
    const f = (typeof kind === 'function' ? kind : fields[kind])({...o, key, hass: self._hass, value: p.values[key], disabled: readOnly || o.disabled,
     onChange: v => { p.values[key] = v; o.onChange?.(v); self._changed(key); }});
    (p.fields ||= {})[key] = f;
    if (p.errors[key]) f.setError(p.errors[key]);
    queueMicrotask(() => self._markField(key));
    return f.el;
   },
   row: o => row({...o, route: o.route, onClick: o.route ? e => { e.preventDefault(); self._go(o.route); } : o.onClick}),
   // An action (Remove, Back to automatic): its own values saved at once after the question; resolves true once saved.
   act: (values, question) => self._save(clone(values), question),
   notice, inlineError, button
  };
 }
 // A section updates its live values itself (spec.live).
 _live() { const p = this._page; if (p?.status === 'ready') p.spec.live?.(this.shadowRoot, this._hass); }

 /* ---- drawing ---- */
 _renderShell() {
  const root = this.shadowRoot;
  root.replaceChildren(h('style', {text: STYLE}), h('div', {class: 'shell' + (this._wide ? ' wide' : '')},
   h('nav', {class: 'list-col', 'aria-label': this.t('Settings')}), h('main', {class: 'page-col'})));
  this._renderList(); this._renderPage();
 }
 _focusKey() {
  const a = this.shadowRoot.activeElement;
  return a ? {key: a.dataset?.fk || a.dataset?.section || (a.matches?.('[data-back]') ? 'back' : null), sel: [a.selectionStart, a.selectionEnd]} : null;
 }
 _refocus(state) {
  if (!state?.key) return;
  const el = this.shadowRoot.querySelector(`[data-fk="${CSS.escape(state.key)}"], [data-section="${CSS.escape(state.key)}"]`)
   || (state.key === 'back' ? this.shadowRoot.querySelector('[data-back]') : null);
  if (!el) return;
  el.focus({preventScroll: true});
  try { if (state.sel[0] != null) el.setSelectionRange(...state.sel); } catch (e) { /* not a text field */ }
 }
 _renderList() {
  const nav = this.shadowRoot.querySelector('.list-col');
  if (!nav) return;
  const focus = this._focusKey(), o = this._overview, current = this._route.section;
  this._listDirty = this._dirty();
  nav.hidden = !this._wide && current != null;
  const head = h('header', {class: 'head'}, h('h1', {class: 'title', text: this.t('Settings')}),
   h('p', {class: 'subtitle', text: this.t('The E32 keeps most of these settings and works with them, also without Home Assistant.')}));
  const parts = [head];
  if (!this.admin) parts.push(notice(this.t('Only an administrator of Home Assistant can change this.'), 'info'));
  if (this._overviewError) parts.push(notice(this._errorText(this._overviewError), 'error'));
  if (o?.module_url && SELF && SELF.startsWith('/open_thermostat/') && o.module_url !== SELF)
   parts.push(notice(this.t('OpenThermostat was updated. Reload the page to use the new version.'), 'warning'));
  const list = h('div', {class: 'card list'});
  const byName = new Map((o?.sections || []).map(s => [s.name, s]));
  for (const name of SECTION_ORDER.filter(n => !o || byName.has(n)).concat((o?.sections || []).map(s => s.name).filter(n => !SECTION_ORDER.includes(n)))) {
   const s = byName.get(name), drafted = [...this._drafts.keys()].some(k => k.startsWith(name + '/'))
    || (this._page?.section === name && this._dirty());
   const summary = !o ? (this._overviewError ? [] : [this.t('Loading…')]) : s.available ? s.summary : [this._reasonText(s.reason), ...s.summary].filter(Boolean);
   const el = row({label: this.t(TITLES[name] || name), summary, route: routeOf(name), current: current === name,
    badge: drafted ? this.t('Not saved') : null, disabled: s && !s.available, data: {section: name},
    onClick: e => { if (e.button || e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); this._go(routeOf(name)); }});
   list.append(el);
  }
  parts.push(list);
  nav.replaceChildren(...parts);
  this._refocus(focus);
 }
 _reasonText(reason) {
  return reason === 'connect_e32' ? this.t('Connect the E32 first: Configure → E32 connection.') : '';
 }
 _errorText(code) { return ERRORS[code] ? this.t(ERRORS[code]) : this.t('The change was not saved ({code}). Try again.', {code}); }
 _renderPage() {
  const main = this.shadowRoot.querySelector('.page-col');
  if (!main) return;
  const focus = this._focusKey(), p = this._page;
  main.hidden = !this._wide && !p;
  if (!p) {
   main.replaceChildren(this._wide ? h('div', {class: 'card intro'}, h('p', {text: this.t('Choose a part on the left to see and change it.')})) : '');
   return;
  }
  const spec = p.spec || SECTIONS.get(p.section), info = this._overview?.sections?.find(s => s.name === p.section);
  const per = v => (typeof v === 'function' ? v(p.model || {}, p.item) : v);  // a section's title or subtitle per (model, item)
  const title = this.t(per(spec?.title) || TITLES[p.section] || p.section);
  const up = p.item != null && spec?.parent?.(p.item);
  const parent = up ? {route: up.route, label: this.t(up.label)} : p.item != null ? {route: routeOf(p.section), label: this.t(TITLES[p.section] || p.section)}
   : this._wide ? null : {route: routeOf(null), label: this.t('Settings')};
  const back = parent && {route: parent.route, label: this.t('Back to {page}', {page: parent.label}),
   onClick: e => { e.preventDefault(); this._go(parent.route); }};
  const {el, body} = frame({title: p.item != null && p.model?.name ? p.model.name : title,
   subtitle: per(spec?.subtitle) ? this.t(per(spec.subtitle)) : null, back});
  el.dataset.page = p.section;
  if (p.status !== 'ready') el.dataset.status = p.status;
  if (p.status === 'fallback') {
   if (info?.summary?.length) body.append(h('div', {class: 'card lines'}, ...info.summary.map(line => h('p', {text: together(line)}))));
   const reason = info && !info.available ? this._reasonText(info.reason) : '';
   body.append(notice(reason || this.t('You change this part in Configure for now.'), 'info',
    button(this.t('Open Configure'), () => this._navigate(this._overview?.configure_path || CONFIGURE), 'outlined', {'data-configure': ''})));
  } else if (p.status === 'loading') {
   body.append(h('p', {class: 'loading', role: 'status', text: this.t('Loading…')}));
  } else if (p.status === 'error') {
   body.append(notice(ERRORS[p.baseError] || spec?.errors?.[p.baseError] ? this._error(p.baseError, p.basePlaceholders) : this.t('These settings could not be read ({code}). Reload the page.', {code: p.baseError}), 'error'));
  } else {
   // On a wide screen the list beside it says it already, at the top of the panel.
   if (!this.admin && !this._wide) body.append(notice(this.t('Only an administrator of Home Assistant can change this.'), 'info'));
   if (p.banner) body.append(h('div', {class: 'notice warning banner', role: 'alert', 'data-banner': 'changed_elsewhere'},
    h('p', {class: 'notice-title', text: this.t('Changed elsewhere')}),
    h('p', {text: this.t('These settings were changed elsewhere while you were editing. What you changed is kept and marked; the rest now shows what is saved. Save again to keep your changes.')})));
   if (p.baseError) body.append(inlineError(this._error(p.baseError, p.basePlaceholders)));
   p.fields = {};
   const content = spec.render(this._ctx(p));
   body.append(h('div', {class: 'card form'}, content));
  }
  const bar = h('div', {class: 'savebar', 'data-state': 'idle'}, h('p', {class: 'status', 'aria-live': 'polite', role: 'status'}),
   h('div', {class: 'actions'}, button(this.t('Undo'), () => this._undo(), 'text', {'data-undo': ''}),
    button(this.t('Save'), () => this._save(), 'filled', {'data-save': ''})));
  main.replaceChildren(el, bar);
  this._renderBar();
  this._refocus(focus);
 }
 _renderBar() {
  const bar = this.shadowRoot.querySelector('.savebar'), p = this._page;
  if (!bar) return;
  const state = !p || p.status !== 'ready' ? 'idle' : p.saving ? 'saving' : this._dirty() && this.admin ? 'dirty' : p.saved ? 'saved' : 'idle';
  bar.dataset.state = state;
  bar.querySelector('.status').textContent = {dirty: this.t('You changed something.'), saving: this.t('Saving…'), saved: this.t('Saved.')}[state] || '';
  for (const b of bar.querySelectorAll('button')) b.disabled = state !== 'dirty';
 }
}
const SELF = (() => { try { return new URL(import.meta.url).pathname; } catch (e) { return ''; } })();

/* ---- the example section: Dashboard and name (settings.py read_general / save_general) ----------------------- */
defineSection('general', {
 title: 'Dashboard and name',
 subtitle: 'The name of this installation in Home Assistant and whether it shows the OpenThermostat dashboard.',
 errors: {invalid_name: 'Give a name of 1 to 80 characters.'},
 render: ctx => h('div', {class: 'fields'},
  ctx.field('text', 'name', {label: ctx.t('Installation name'), maxlength: 80, required: true,
   help: ctx.t('A recognisable name in Home Assistant. Your devices and their history stay as they are.')}),
  ctx.field('toggle', 'create_dashboard', {label: ctx.t('Show the OpenThermostat dashboard'),
   help: ctx.t('The OpenThermostat dashboard: your rooms at a glance, the week planner and the boiler. Your own dashboards are preserved.')})),
 // Switching the dashboard off removes this tab too: asked first.
 confirm: (values, model, ctx) => (model.create_dashboard && values.create_dashboard === false
  ? {title: ctx.t('Hide the OpenThermostat dashboard?'), text: ctx.t('This tab goes with it. You can show the dashboard again in Configure → Dashboard and name.'),
     confirm: ctx.t('Hide the dashboard'), danger: true} : null)
});

const KIT = Object.freeze({version: 1, h, translate, defineSection, row, frame, notice, inlineError, button, fields, shell, confirm: confirmDialog,
 parseRoute, routeOf, sections: SECTIONS});

/* ---- style: Home Assistant's theme variables; the build of the E32 pages (header, card, row, field) ---- */
const STYLE = `:host{display:block;--ot-text:var(--primary-text-color,#212121);--ot-muted:var(--secondary-text-color,#727272);
--ot-surface:var(--card-background-color,var(--ha-card-background,#fff));--ot-divider:var(--divider-color,rgba(0,0,0,.12));
--ot-accent:var(--primary-color,#03a9f4);--ot-error:var(--error-color,#db4437);--ot-warn:var(--warning-color,#ffa600);
--ot-link:color-mix(in srgb,var(--ot-accent) 60%,var(--ot-text));--ot-fill:color-mix(in srgb,var(--ot-accent) 72%,#000);
--ot-radius:var(--ha-card-border-radius,12px);color:var(--ot-text);font:14px/1.45 var(--paper-font-body1_-_font-family,Roboto,Arial,sans-serif)}
*{box-sizing:border-box}[hidden]{display:none!important}p{margin:0}
.shell{display:block;max-width:1120px;margin:0 auto;padding:16px}
.shell.wide{display:grid;grid-template-columns:minmax(260px,340px) minmax(0,1fr);gap:24px;align-items:start;padding:24px}
.head{margin:4px 2px 14px}.title{margin:0;font-size:22px;font-weight:500;line-height:1.25;overflow-wrap:anywhere}.title:focus{outline:none}
h1.title{font-size:24px}.subtitle{margin-top:6px;color:var(--ot-muted);overflow-wrap:anywhere}
.back{display:inline-flex;align-items:center;gap:4px;min-height:32px;margin-bottom:6px;color:var(--ot-link);text-decoration:none;font-weight:500}
.back::before{content:"";width:8px;height:8px;border-left:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg);margin:0 4px 0 2px}
.card{background:var(--ot-surface);border-radius:var(--ot-radius);border:1px solid var(--ot-divider);overflow:hidden}
.list{display:flex;flex-direction:column}
.row{display:flex;align-items:center;gap:12px;width:100%;min-height:56px;padding:12px 16px;border:0;border-top:1px solid var(--ot-divider);
background:none;color:inherit;font:inherit;text-align:left;text-decoration:none;cursor:pointer}
.row:first-child{border-top:0}.row:hover{background:color-mix(in srgb,var(--ot-accent) 6%,transparent)}
.row[aria-current=page]{background:color-mix(in srgb,var(--ot-accent) 12%,transparent);box-shadow:inset 3px 0 0 var(--ot-accent)}
.row:focus-visible,.btn:focus-visible,.back:focus-visible,.switch:focus-visible,.choice input:focus-visible{outline:3px solid var(--ot-accent);outline-offset:2px}
.input:focus-visible{outline:2px solid var(--ot-accent);outline-offset:0;border-color:var(--ot-accent)}
.form .row{margin:0 -16px;width:calc(100% + 32px);border-top:1px solid var(--ot-divider)}
.row-text{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;gap:2px}
.row-label{font-size:16px;font-weight:500;display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.row-line{color:var(--ot-muted);overflow-wrap:anywhere}.row-value{flex:none;color:var(--ot-muted);white-space:nowrap}
.row.muted .row-label{color:var(--ot-muted)}
.chevron{flex:none;width:8px;height:8px;border-right:2px solid var(--ot-muted);border-top:2px solid var(--ot-muted);transform:rotate(45deg);margin-right:4px}
.badge{font-size:12px;font-weight:500;padding:1px 8px;border-radius:10px;background:color-mix(in srgb,var(--ot-warn) 22%,var(--ot-surface));
color:color-mix(in srgb,var(--ot-warn) 35%,var(--ot-text))}
.notice{margin:0 0 14px;padding:12px 14px;border-radius:var(--ot-radius);border:1px solid color-mix(in srgb,var(--ot-accent) 35%,var(--ot-divider));
background:color-mix(in srgb,var(--ot-accent) 8%,var(--ot-surface));overflow-wrap:anywhere}
.notice.warning{border-color:color-mix(in srgb,var(--ot-warn) 60%,var(--ot-divider));background:color-mix(in srgb,var(--ot-warn) 12%,var(--ot-surface))}
.notice.error{border-color:color-mix(in srgb,var(--ot-error) 55%,var(--ot-divider));background:color-mix(in srgb,var(--ot-error) 9%,var(--ot-surface))}
.notice .btn{margin-top:10px}.notice-title{font-weight:500;margin-bottom:4px}
.inline-error,.error{color:color-mix(in srgb,var(--ot-error) 80%,var(--ot-text))}.inline-error{margin:0 2px 14px;font-weight:500}
.lines{padding:14px 16px;margin-bottom:14px;display:grid;gap:4px}.intro{padding:24px;color:var(--ot-muted)}.loading{padding:8px 2px;color:var(--ot-muted)}
.form{padding:6px 16px}.fields{display:flex;flex-direction:column}
.field{padding:14px 0;border-top:1px solid var(--ot-divider);border-left:3px solid transparent;margin-left:-16px;padding-left:13px;display:grid;gap:6px}
.field:first-child{border-top:0}.field.changed{border-left-color:var(--ot-accent)}.field.conflict{border-left-color:var(--ot-warn)}
.label{font-weight:500}.help,.choice-help,.mark{color:var(--ot-muted);font-size:13px;overflow-wrap:anywhere}
.mark{font-weight:500}.field.changed .mark{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}.field.conflict .mark{color:color-mix(in srgb,var(--ot-warn) 40%,var(--ot-text))}.error{font-size:13px;font-weight:500}
.input{font:inherit;color:inherit;background:var(--ot-surface);border:1px solid color-mix(in srgb,var(--ot-muted) 55%,transparent);border-radius:8px;
min-height:44px;padding:10px 12px;width:100%;max-width:480px}
.input:disabled,.switch:disabled,.choice input:disabled{opacity:.6;cursor:default}.invalid .input{border-color:var(--ot-error)}
.with-unit{display:flex;align-items:center;gap:8px;max-width:240px}.unit{color:var(--ot-muted);white-space:nowrap}
.toggle-row{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:44px}
.switch{appearance:none;flex:none;width:44px;height:24px;border-radius:12px;position:relative;cursor:pointer;margin:0;
background:color-mix(in srgb,var(--ot-muted) 45%,transparent);transition:background .15s}
.switch::after{content:"";position:absolute;top:3px;left:3px;width:18px;height:18px;border-radius:50%;background:var(--ot-surface);transition:transform .15s;box-shadow:0 1px 2px rgba(0,0,0,.3)}
.switch:checked{background:var(--ot-fill)}.switch:checked::after{transform:translateX(20px)}
.choices{display:grid;gap:4px}.choice{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:start;padding:8px 0;cursor:pointer}
.choice input{margin:3px 0 0;width:18px;height:18px;accent-color:var(--ot-fill)}.choice-text{display:grid;gap:2px}.choice-label{font-weight:500}
.picker{display:grid;gap:8px;max-width:480px}.picked{display:grid;gap:6px}.picked:empty{display:none}
.pick{display:flex;align-items:center;gap:8px;padding:8px 8px 8px 12px;border:1px solid var(--ot-divider);border-radius:8px}
.pick-text{flex:1 1 auto;min-width:0;display:grid}.pick-name{overflow-wrap:anywhere}.pick-id{color:var(--ot-muted);font-size:12px;overflow-wrap:anywhere}
.combo{position:relative}.options{position:absolute;z-index:2;left:0;right:0;top:calc(100% + 4px);max-height:320px;overflow:auto;margin:0;padding:4px 0;
list-style:none;background:var(--ot-surface);border:1px solid var(--ot-divider);border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.18)}
.option{display:grid;padding:8px 12px;cursor:pointer}.option[aria-selected=true],.option:hover{background:color-mix(in srgb,var(--ot-accent) 14%,transparent)}
.group{padding:8px 12px 4px;font-size:12px;font-weight:500;color:var(--ot-muted);text-transform:none}.empty{padding:8px 12px;color:var(--ot-muted)}
.btn{font:inherit;font-weight:500;min-height:40px;padding:8px 16px;border-radius:20px;border:1px solid transparent;cursor:pointer;background:none;color:var(--ot-link)}
.btn.outlined{border-color:color-mix(in srgb,var(--ot-muted) 55%,transparent)}.btn.filled{background:var(--ot-fill);color:#fff}
.btn.danger{background:color-mix(in srgb,var(--ot-error) 82%,#000);color:#fff}.btn:disabled{opacity:.5;cursor:default}
.btn.icon{min-height:36px;width:36px;padding:0;border-radius:50%;position:relative;color:var(--ot-muted)}
.btn.remove::before,.btn.remove::after{content:"";position:absolute;left:11px;top:17px;width:14px;height:2px;background:currentColor;transform:rotate(45deg)}
.btn.remove::after{transform:rotate(-45deg)}
.savebar{position:sticky;bottom:0;z-index:3;display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-top:14px;padding:10px 12px 10px 16px;
background:var(--ot-surface);border:1px solid var(--ot-divider);border-radius:var(--ot-radius);box-shadow:0 -2px 12px rgba(0,0,0,.12)}
.savebar .status{flex:1 1 180px;font-weight:500}.savebar .actions{display:flex;gap:8px;margin-left:auto}
.savebar[data-state=idle]{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);padding:0;border:0;margin:0}
.savebar[data-state=saved] .actions{display:none}
dialog.confirm{border:0;border-radius:var(--ot-radius);padding:20px;max-width:min(440px,calc(100vw - 32px));background:var(--ot-surface);color:var(--ot-text)}
dialog.confirm::backdrop{background:rgba(0,0,0,.45)}dialog.confirm h3{margin:0 0 8px;font-size:18px;font-weight:500}
dialog.confirm .actions{display:flex;justify-content:flex-end;flex-wrap:wrap;gap:8px;margin-top:20px}
@media(max-width:420px){.shell{padding:12px 8px}.row{padding:12px}.form{padding:4px 12px}.field{margin-left:-12px;padding-left:9px}
.form .row{margin:0 -12px;width:calc(100% + 24px)}}
@media(prefers-reduced-motion:reduce){.switch,.switch::after{transition:none}}`;

/* ---- registration ---------------------------------------------------------------------------------------------- */
// As the other cards: define again (a fresh subclass) whenever a scoped-registry polyfill lost the element.
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
 setInterval(check, 500);
 return check;
};
if (!window.OpenThermostatSettingsKit) {
 window.OpenThermostatSettingsKit = KIT;
 // Section modules loaded before this one queued themselves; later ones call defineSection directly.
 const queued = Array.isArray(window.OpenThermostatSettingsSections) ? window.OpenThermostatSettingsSections : [];
 window.OpenThermostatSettingsSections = {push: ([name, spec]) => defineSection(name, spec)};
 for (const [name, spec] of queued) { try { defineSection(name, spec); } catch (e) { console.error('OpenThermostat settings section', name, e); } }
}
ensureDefined('openthermostat-settings', OpenThermostatSettings);
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === 'openthermostat-settings'))
 window.customCards.push({type: 'openthermostat-settings', name: 'OpenThermostat settings', description: 'The settings of an OpenThermostat installation: rooms, house, heating and more, in one place.'});
