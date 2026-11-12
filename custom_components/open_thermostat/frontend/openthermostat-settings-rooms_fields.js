/* Rooms, part the room's fields (1.4.5 HA-PANEL-145: split from openthermostat-settings-rooms.js, the module budget): the
   fields of a room's screen that are this section's own (the kit's field contract {el, setError, setMark, focus}): the
   temperature sources, windows and doors with their pause delays, the radiator valves, the persons and the notifications
   with who gets them. Loaded by the panel with the other section modules (settings.SECTION_MODULES); it hands its fields
   to its section through window.OpenThermostatSettingsParts, and the section registers once it is here. */
const TEXTS = {
 nl: {
  'Driven by temperature; the position cannot be read': 'Gestuurd op temperatuur; de stand is niet uit te lezen',
  'Regulates itself to the target; the position cannot be read': 'Regelt zichzelf naar het doel; de stand is niet uit te lezen',
  'Through Home Assistant': 'Via Home Assistant',
  'Valve control': 'Radiatorkranen aansturen',
  'On: these valves follow the room (only while the E32 controls the boiler itself). Off: the valves keep their own settings and nothing is sent to them.': 'Aan: deze kranen volgen de ruimte (alleen zolang de E32 de ketel zelf aanstuurt). Uit: de kranen houden hun eigen instellingen en er gaat niets naar ze toe.',
  'Kept on the E32': 'Bewaard op de E32',
  'On the BLU Gateway': 'Aan de BLU Gateway',
  'Add from the BLU Gateway': 'Toevoegen van de BLU Gateway',
  'Choose a valve': 'Kies een kraan',
  'The E32 measures this thermometer itself; choose it as the source, so it also works without Home Assistant.': 'De E32 meet deze thermometer zelf; kies hem als bron, dan werkt het ook zonder Home Assistant.',
  'Use the E32\'s sensor': 'Sensor van de E32 gebruiken',
  'Used first': 'Eerst gebruikt',
  'Use first': 'Eerst gebruiken',
  'Use {name} first': '{name} eerst gebruiken',
  'Remove {name}': '{name} verwijderen',
  'Add a source': 'Bron toevoegen',
  'At most four temperature sources per room.': 'Hoogstens vier temperatuurbronnen per ruimte.',
  'No source yet: choose at least one.': 'Nog geen bron: kies er minstens één.',
  'Search by name': 'Zoek op naam',
  'Bluetooth sensor on the E32': 'Bluetooth-sensor op de E32',
  'No reading': 'Geen meting',
  'just now': 'zojuist',
  '{n} min ago': '{n} min geleden',
  '{n} h ago': '{n} uur geleden',
  'As the house': 'Als het huis',
  'Window contacts': 'Raamcontacten',
  'Door contacts': 'Deurcontacten',
  'Pause after (windows)': 'Pauze na (ramen)',
  'Pause after (doors)': 'Pauze na (deuren)',
  'As the house ({value})': 'Als het huis ({value})',
  'The house value applies; you change it under House.': 'De waarde van het huis geldt; die wijzig je onder Huis.',
  'Own value': 'Eigen waarde',
  'This room uses its own value.': 'Deze ruimte gebruikt een eigen waarde.',
  'Battery {level}': 'Batterij {level}',
  'Battery low': 'Batterij bijna leeg',
  'Last report {age}': 'Laatste melding {age}',
  'Not found in Home Assistant': 'Niet gevonden in Home Assistant',
  'Model of {name}': 'Model van {name}',
  'No radiator valves in this room.': 'Geen radiatorkranen in deze ruimte.',
  'At most {max} radiator valves per room.': 'Hoogstens {max} radiatorkranen per ruimte.',
  'Add a valve': 'Kraan toevoegen',
  'Driven by position': 'Gestuurd op stand',
  'Persons of this room': 'Personen van deze ruimte',
  'Empty: the room follows the house.': 'Leeg: de ruimte volgt het huis.',
  'Temperature when this room\'s people are away': 'Temperatuur als de mensen van deze ruimte weg zijn',
  'Who gets them': 'Wie krijgt ze',
  'Everyone with a phone': 'Iedereen met een telefoon',
  'Chosen people': 'Gekozen personen',
  'Recipients': 'Ontvangers',
  '{name} (not found)': '{name} (niet gevonden)',
  'Messages about {room} go to {people}.': 'Berichten van {room} gaan naar {people}.',
  'Messages about {room} go to everyone with a phone.': 'Berichten van {room} gaan naar iedereen met een telefoon.',
  'Messages about {room} go to nobody; they show in Home Assistant only.': 'Berichten van {room} gaan naar niemand; ze verschijnen alleen in Home Assistant.',
  ' and ': ' en ',
  'Notify about this room': 'Meldingen over deze ruimte',
  'Off: no messages about this room.': 'Uit: geen berichten over deze ruimte.',
  'Messages': 'Berichten',
  'Window or door open while the room heats': 'Raam of deur open terwijl de ruimte verwarmt',
  'Room stays cold (more than 1 °C below its target for over an hour)': 'Ruimte blijft koud (meer dan 1 °C onder de gewenste temperatuur, langer dan een uur)',
  'Temperature sensor silent for 30 minutes, or another device for 24 hours': 'Temperatuursensor 30 minuten stil, of een ander apparaat 24 uur',
  'Battery low of a thermometer, valve, window or door contact or setting device': 'Batterij bijna leeg van een thermometer, kraan, raam- of deurcontact of instelapparaat'}};
const ERRORS = {
};
/* ---- small helpers ---- */
const copy = v => JSON.parse(JSON.stringify(v));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const num = v => (typeof v === 'number' && Number.isFinite(v) ? v : typeof v === 'string' && v.trim() !== '' && Number.isFinite(Number(v)) ? Number(v) : null);
// The age of a reading in words: just now, 4 min ago, 2 h ago.
const age = (st, t) => {
 const at = Date.parse(st?.last_reported || st?.last_updated || '');
 if (Number.isNaN(at)) return '';
 const minutes = Math.floor((Date.now() - at) / 60000);
 return minutes < 1 ? t('just now') : minutes < 120 ? t('{n} min ago', {n: minutes}) : t('{n} h ago', {n: Math.floor(minutes / 60)});
};
const names = list => Object.fromEntries((list || []).map(c => [c.entity_id, c.name]));
// The valve control as the glossary says it (radiator valve: driven by temperature, or by position).
// How a valve is driven (radiator_valves.list[].driven), in the glossary's words (1.4.1 ROOM-BACKEND).
const DRIVEN = {position: 'Driven by position', temperature: 'Driven by temperature; the position cannot be read', home_assistant: 'Through Home Assistant'};
const KINDS = {window: 'Window or door open while the room heats', cold: 'Room stays cold (more than 1 °C below its target for over an hour)',
 sensor: 'Temperature sensor silent for 30 minutes, or another device for 24 hours',
 battery: 'Battery low of a thermometer, valve, window or door contact or setting device'};
const SOURCE_UNITS = ['°C', '°F', 'K'];
/* ---- the fields of this section (the kit's field contract: {el, setError, setMark, focus}) ---- */
const bleOf = (model, id) => (Array.isArray(model.ble) ? model.ble.find(s => s.id === id) : model.ble?.[id] != null ? {id, name: model.ble[id]} : null);
// A source by the name you know it by: the E32's Bluetooth sensor by its name, a Home Assistant entity by its name.
const sourceName = (source, model, hass) => (source.type === 'ble' ? bleOf(model, source.id)?.name || source.id
 : hass?.states?.[source.id]?.attributes?.friendly_name || source.id);
// What a source is, in words (owner 10 Nov, "dat is echt onduidelijk"): "Bluetooth sensor on the E32 · A3:E8:DB" or
// "Home Assistant · BTHome · sensor.atc_a3e8db_temperature" (the integration from live.integrations).
const address = id => (/^[0-9a-f]{12}$/i.test(id) ? id.slice(6).toUpperCase().replace(/(..)(?=.)/g, '$1:') : id);
function sourceKind(source, model, hass, t) {
 if (source.type === 'ble') return [t('Bluetooth sensor on the E32'), address(source.id)];
 const platform = hass?.entities?.[source.id]?.platform;
 return ['Home Assistant', platform ? model.live?.integrations?.[platform] || platform : '', source.id];
}
function reading(kit, source, model, hass) {
 const eid = source.type === 'ble' ? bleOf(model, source.id)?.entity_id : source.id, st = eid && hass?.states?.[eid];
 if (!st) return ['', null];
 const value = eid.startsWith('climate.') ? num(st.attributes?.current_temperature) : num(st.state);
 return value == null ? ['', st] : [kit.degrees(value, eid.startsWith('climate.') ? model.unit : st.attributes?.unit_of_measurement || model.unit, hass), st];
}
// Sources keep the order the room form stores: the kind of the first one first (Bluetooth or Home Assistant).
const grouped = list => (list.length ? [...list.filter(s => s.type === list[0].type), ...list.filter(s => s.type !== list[0].type)] : list);
function sourcesField(ctx) {
 return o => {
  const {kit, t, model} = ctx, {h, fields, button, iconButton, shell, chip} = kit;
  let list = copy(o.value || []), adding = false;
  const body = h('div', {class: 'rr-list'}), api = shell('sources', o, body, false);
  const own = new Set(model.own || []), bleByEntity = new Map((model.ble || []).filter(s => s.entity_id).map(s => [s.entity_id, s]));
  const emit = () => o.onChange?.(copy(list));
  // HA-DEVICES (1.4.2): a Home Assistant source that is the same thermometer as a Bluetooth sensor paired on the E32.
  const twin = model.live?.e32_sensor_suggestion;
  const draw = focusAdd => {
   const items = list.flatMap((source, i) => {
    const name = sourceName(source, model, ctx.hass), kind = h('span', {class: 'pick-id rr-kind', text: sourceKind(source, model, ctx.hass, t).filter(Boolean).join(' · ')});
    const detail = h('span', {class: 'pick-id'});
    const el = h('div', {class: 'pick', 'data-source': `${source.type}:${source.id}`, 'data-live': ''},
     h('span', {class: 'pick-text'}, h('span', {class: 'pick-name'}, h('span', {text: name}), i === 0 && list.length > 1 ? chip(t('Used first'), 'accent') : null), kind, detail),
     o.disabled || i === 0 ? null : button(t('Use first'), () => { list = grouped([source, ...list.filter(x => x !== source)]); draw(); emit(); }, 'text small',
      {'aria-label': t('Use {name} first', {name}), 'data-first': ''}),
     o.disabled ? null : iconButton('close', t('Remove {name}', {name}), () => { list = list.filter(x => x !== source); draw(); emit(); }, {'data-remove': ''}));
    el._live = hass => {
     const [v, s] = reading(kit, source, model, hass);
     detail.textContent = [v || t('No reading'), v ? age(s, t) : ''].filter(Boolean).join(' · ');
    };
    el._live(ctx.hass);
    if (source.type !== 'ha' || !twin || twin.entity_id !== source.id || list.some(x => x.type === 'ble' && x.id === twin.address)) return [el];
    const swap = () => { list = list.map(x => (x === source ? {type: 'ble', id: twin.address} : x)); draw(); emit(); };
    return [el, h('div', {class: 'rr-twin', 'data-twin': source.id}, h('p', {class: 'help', text: t('The E32 measures this thermometer itself; choose it as the source, so it also works without Home Assistant.')}),
     o.disabled ? null : button(t('Use the E32\'s sensor'), swap, 'text small', {'data-use-twin': ''}))];
   });
   const parts = [...items];
   if (!list.length) parts.push(h('p', {class: 'help', text: t('No source yet: choose at least one.')}));
   if (!o.disabled && list.length >= (model.max_sources || 4)) parts.push(h('p', {class: 'help', text: t('At most four temperature sources per room.')}));
   else if (!o.disabled && adding) {
    const taken = new Set(list.map(s => (s.type === 'ble' ? bleOf(model, s.id)?.entity_id : s.id)));
    const picker = fields.entity({hass: ctx.hass, key: 'sources-add', placeholder: t('Search by name'), value: '', filter: (st, eid) => {
     if (taken.has(eid)) return false;
     if (bleByEntity.has(eid)) return true;
     if (own.has(eid)) return false;
     if (eid.startsWith('climate.')) return typeof st?.attributes?.current_temperature === 'number';
     return eid.startsWith('sensor.') && st?.attributes?.device_class === 'temperature' && SOURCE_UNITS.includes(st?.attributes?.unit_of_measurement);
    }, onChange: eid => {
     if (!eid) return;
     const ble = bleByEntity.get(eid);
     list = [...list, ble ? {type: 'ble', id: ble.id} : {type: 'ha', id: eid}];
     adding = false; draw(true); emit();
    }});
    parts.push(picker.el);
    queueMicrotask(() => picker.focus());
   } else if (!o.disabled) parts.push(button(t('Add a source'), () => { adding = true; draw(); }, 'outlined', {icon: 'plus', 'data-add-source': ''}));
   body.replaceChildren(...parts);
   if (focusAdd) body.querySelector('[data-add-source]')?.focus();
  };
  draw();
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}
// A value with the house's as default: [As the house (2 min) | Own] and a stepper for the own one.
function ownOrHouse(ctx, {key, label, house, value, unit, step, min, max, onChange, disabled, help}) {
 const {kit, t} = ctx, wrap = kit.h('div', {class: 'rr-own'});
 let own = value != null;
 const shownHouse = house == null ? '' : kit.degrees(house, unit, ctx.hass);
 const seg = kit.fields.segmented({key: key + ':own', hass: ctx.hass, label, disabled, value: own ? 'own' : 'house', help,
  options: [{value: 'house', label: shownHouse ? t('As the house ({value})', {value: shownHouse}) : t('As the house'), help: t('The house value applies; you change it under House.')},
   {value: 'own', label: t('Own value'), help: t('This room uses its own value.')}],
  onChange: v => { own = v === 'own'; draw(); onChange(own ? (stepper?.value ?? house ?? min) : null); }});
 let stepper = null;
 const draw = () => {
  stepper = own ? kit.fields.stepper({key, hass: ctx.hass, value: value ?? house ?? min, unit, step, min, max, disabled, label: null,
   onChange: v => { value = v; onChange(v); }}) : null;
  wrap.replaceChildren(seg.el, ...(stepper ? [stepper.el] : []));
 };
 draw();
 return wrap;
}
function contactsField(ctx) {
 return o => {
  const {kit, t, model} = ctx, m = model.contacts, minutes = s => (s == null ? null : s / 60);
  const value = copy(o.value), body = kit.h('div', {class: 'rr-group'}), api = kit.shell('contacts', o, body, false);
  const ids = (m.choices || []).map(c => c.entity_id), label = names(m.choices);
  const emit = () => o.onChange?.(copy(value));
  const picker = (kind, other, title) => kit.fields.entity({hass: ctx.hass, key: 'contacts:' + kind, label: title, multiple: true, disabled: o.disabled,
   choices: ids, names: label, value: value[kind], placeholder: t('Search by name'), filter: (st, eid) => !value[other].includes(eid),
   onChange: v => { value[kind] = v; emit(); }});
  body.append(picker('windows', 'doors', t('Window contacts')).el,
   ownOrHouse(ctx, {key: 'contacts:window_delay_s', label: t('Pause after (windows)'), house: minutes(m.house?.window_delay_s), value: minutes(value.window_delay_s),
    unit: 'min', step: 0.5, min: 0, max: 30, disabled: o.disabled, onChange: v => { value.window_delay_s = v == null ? null : Math.round(v * 60); emit(); }}),
   picker('doors', 'windows', t('Door contacts')).el,
   ownOrHouse(ctx, {key: 'contacts:door_delay_s', label: t('Pause after (doors)'), house: minutes(m.house?.door_delay_s), value: minutes(value.door_delay_s),
    unit: 'min', step: 0.5, min: 0, max: 30, disabled: o.disabled, onChange: v => { value.door_delay_s = v == null ? null : Math.round(v * 60); emit(); }}));
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}
// A valve's battery and last report: its battery entity as the backend names it (battery_entity_id, 1.4.2 P21: no
// registry scan here), a percentage or a "low" binary sensor, and the valve's own state (hass.states).
function valveStatus(kit, hass, eid, t, batteryId) {
 const st = hass?.states?.[eid], battery = batteryId ? hass?.states?.[batteryId] : null, level = num(battery?.state);
 const said = level != null ? t('Battery {level}', {level: `${kit.number(level, hass, 0)} %`}) : battery?.state === 'on' ? t('Battery low') : '';
 return [said, st ? t('Last report {age}', {age: age(st, t)}) : t('Not found in Home Assistant')].filter(Boolean).join(' · ');
}
// A valve as the save takes it (S-ROOM-BACKEND: {entity_id, model}, a kept valve {id}, a BLU Gateway valve {id, role, keep_open}).
const valveSave = v => (v.kind === 'kept' ? {id: v.id} : v.kind === 'gateway' ? {id: v.id, role: v.role ?? null, keep_open: !!v.keep_open}
 : {entity_id: v.entity_id, model: v.model ?? null});
const valveKey = v => v.entity_id || v.id;
function valvesField(ctx) {
 return o => {
  const {kit, t, model} = ctx, m = model.radiator_valves, {h} = kit;
  const value = copy(o.value), body = h('div', {class: 'rr-group'}), api = kit.shell('radiator_valves', o, body, false);
  // What each valve is: the model's own rows, then what was added here (a Home Assistant valve or a BLU Gateway valve).
  const known = new Map((m.list || []).map(v => [valveKey(v), v]));
  for (const c of m.choices || []) if (!known.has(c.entity_id)) known.set(c.entity_id, {entity_id: c.entity_id, name: c.name, kind: 'home_assistant', choose_model: false});
  for (const g of m.gateway_choices || []) if (!known.has(g.id)) known.set(g.id, {id: g.id, name: g.name, kind: 'gateway'});
  let adding = null;
  const emit = () => o.onChange?.(copy(value));
  const draw = focusAdd => {
   const shownIds = new Set(value.list.map(valveKey));
   const rows = value.list.map((save, i) => {
    const v = known.get(valveKey(save)) || {name: valveKey(save)}, name = v.name || valveKey(save), status = h('span', {class: 'pick-id'});
    // HA-DEVICES (HC-11): a valve Home Assistant drives that reports no opening regulates itself to the target.
    const selfRegulating = (model.live?.self_regulating || []).some(x => x === v.id || x === v.entity_id || x === v.name);
    const word = [v.kind === 'kept' ? t('Kept on the E32') : v.kind === 'gateway' ? t('On the BLU Gateway') : '',
     selfRegulating ? t('Regulates itself to the target; the position cannot be read') : v.driven ? t(DRIVEN[v.driven] || v.driven) : '']
     .filter(Boolean).join(' · ');
    const select = v.choose_model ? h('select', {class: 'input rr-model', 'aria-label': t('Model of {name}', {name}), disabled: o.disabled, 'data-fk': `radiator_valves:${i}:model`},
     ...(m.models || []).map(x => h('option', {value: x.key, text: x.name}))) : null;
    if (select) { select.value = save.model || v.model || ''; select.addEventListener('change', () => { save.model = select.value || null; emit(); }); }
    const el = h('div', {class: 'pick rr-valve', 'data-valve': valveKey(save), 'data-live': ''},
     h('span', {class: 'pick-text'}, h('span', {class: 'pick-name', text: name}), word ? h('span', {class: 'pick-id', text: word}) : null, save.entity_id ? status : null, select),
     o.disabled ? null : kit.iconButton('close', t('Remove {name}', {name}), () => { value.list.splice(i, 1); draw(true); emit(); }, {'data-remove': ''}));
    el._live = hass => { if (save.entity_id) status.textContent = valveStatus(kit, hass, save.entity_id, t, v.battery_entity_id); };
    el._live(ctx.hass);
    return el;
   });
   const parts = rows.length ? rows : [h('p', {class: 'help', text: t('No radiator valves in this room.')})];
   const own = value.list.filter(v => !('role' in v)).length, all = value.list.length;
   const roomForOwn = own < (m.max || 4) && all < (m.max_with_gateway || m.max || 4), roomForGateway = all < (m.max_with_gateway || m.max || 4);
   const gateway = (m.gateway_choices || []).filter(g => !shownIds.has(g.id));
   if (!o.disabled && adding === 'ha') {
    const picker = kit.fields.entity({hass: ctx.hass, key: 'radiator_valves-add', placeholder: t('Search by name'), value: '', choices: (m.choices || []).map(c => c.entity_id),
     names: Object.fromEntries((m.choices || []).map(c => [c.entity_id, c.name])), filter: (st, eid) => !shownIds.has(eid),
     onChange: eid => { if (!eid) return; value.list.push({entity_id: eid, model: null}); adding = null; draw(true); emit(); }});
    parts.push(picker.el);
    queueMicrotask(() => picker.focus());
   } else if (!o.disabled && adding === 'gateway') {
    const select = h('select', {class: 'input', 'aria-label': t('Add from the BLU Gateway'), 'data-fk': 'radiator_valves-gateway'},
     h('option', {value: '', text: t('Choose a valve')}), ...gateway.map(g => h('option', {value: g.id, text: g.name})));
    select.addEventListener('change', () => { if (!select.value) return; value.list.push({id: select.value, role: null, keep_open: false}); adding = null; draw(true); emit(); });
    parts.push(select);
    queueMicrotask(() => select.focus());
   } else if (!o.disabled) {
    const buttons = [];
    if (roomForOwn && (m.choices || []).length) buttons.push(kit.button(t('Add a valve'), () => { adding = 'ha'; draw(); }, 'outlined', {icon: 'plus', 'data-add-valve': ''}));
    if (roomForGateway && gateway.length) buttons.push(kit.button(t('Add from the BLU Gateway'), () => { adding = 'gateway'; draw(); }, 'text', {icon: 'plus', 'data-add-gateway': ''}));
    if (!roomForOwn && !roomForGateway) parts.push(h('p', {class: 'help', text: t('At most {max} radiator valves per room.', {max: m.max_with_gateway || m.max || 4})}));
    if (buttons.length) parts.push(h('div', {class: 'rr-buttons'}, ...buttons));
   }
   if (value.control !== null && value.control !== undefined) parts.push(kit.fields.toggle({key: 'radiator_valves:control', hass: ctx.hass, label: t('Valve control'),
    value: value.control, disabled: o.disabled, help: t('On: these valves follow the room (only while the E32 controls the boiler itself). Off: the valves keep their own settings and nothing is sent to them.'),
    onChange: v => { value.control = v; emit(); }}).el);
   body.replaceChildren(...parts);
   if (focusAdd) (body.querySelector('[data-add-valve], [data-add-gateway]') || body.querySelector('select'))?.focus();
  };
  draw();
  api.target = () => body.querySelector('select, input, button');
  api.describe();
  return api;
 };
}
function personsField(ctx) {
 return o => {
  const {kit, t, model} = ctx, m = model.persons, value = copy(o.value), body = kit.h('div', {class: 'rr-group'});
  const api = kit.shell('persons', o, body, false), emit = () => o.onChange?.(copy(value)), unit = model.unit || '°C';
  const range = m.away_range || {minimum: unit === '°F' ? 41 : 5, maximum: unit === '°F' ? 77 : 25};
  body.append(kit.fields.entity({hass: ctx.hass, key: 'persons:entity_ids', label: t('Persons of this room'), multiple: true, disabled: o.disabled, showIds: false,
   choices: (m.choices || []).map(c => c.entity_id), names: names(m.choices), value: value.entity_ids, placeholder: t('Search by name'),
   help: t('Empty: the room follows the house.'), onChange: v => { value.entity_ids = v; emit(); }}).el);
  if (model.features?.room_away !== false) body.append(ownOrHouse(ctx, {key: 'persons:away_temperature', label: t('Temperature when this room\'s people are away'),
   house: m.house_away_temperature, value: value.away_temperature, unit, step: unit === '°F' ? 1 : 0.5, min: range.minimum, max: range.maximum,
   disabled: o.disabled, onChange: v => { value.away_temperature = v; emit(); }}));
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}
// Who gets a room's messages in one sentence (HA-NOTIFY's recipients_line): the backend's while you did not change the
// choice, else the same words for what you chose (names joined as the backend joins them).
function recipientsLine(ctx, chosen) {
 const {t, model} = ctx, people = model.live?.notifications?.people || [], room = model.name || '';
 const stored = model.live?.notifications?.recipients_line;
 if (stored && same(chosen, model.notifications.recipients ?? null)) return stored[ctx.kit.langOf(ctx.hass)] || stored.en || '';
 if (chosen == null) return t('Messages about {room} go to everyone with a phone.', {room});
 if (!chosen.length) return t('Messages about {room} go to nobody; they show in Home Assistant only.', {room});
 const names = chosen.map(id => people.find(p => p.person === id)?.name || id);
 return t('Messages about {room} go to {people}.', {room, people: names.length === 1 ? names[0] : names.slice(0, -1).join(', ') + t(' and ') + names.at(-1)});
}
function notificationsField(ctx) {
 return o => {
  const {kit, t, model} = ctx, m = model.notifications, {h} = kit, value = copy(o.value), body = h('div', {class: 'rr-group'});
  const api = kit.shell('notifications', o, body, false), emit = () => o.onChange?.(copy(value));
  const people = model.live?.notifications?.people || [];
  const draw = () => {
   const toggle = kit.fields.toggle({key: 'notifications:on', hass: ctx.hass, label: t('Notify about this room'), value: value.on, disabled: o.disabled,
    help: value.on ? '' : t('Off: no messages about this room.'), onChange: v => { value.on = v; if (v && !value.kinds.length) value.kinds = [...(m.kind_choices || [])]; draw(); emit(); }});
   const kinds = value.on ? h('div', {class: 'choices', role: 'group', 'aria-label': t('Messages')}, ...(m.kind_choices || []).map(k => {
    const box = h('input', {type: 'checkbox', disabled: o.disabled, 'data-fk': 'notifications:kind:' + k});
    box.checked = value.kinds.includes(k);
    box.addEventListener('change', () => { value.kinds = (m.kind_choices || []).filter(x => (x === k ? box.checked : value.kinds.includes(x))); emit(); });
    return h('label', {class: 'choice'}, box, h('span', {class: 'choice-text'}, h('span', {class: 'choice-label', text: KINDS[k] ? t(KINDS[k]) : k})));
   })) : null;
   // 1.4.2 (plan 3.4): who gets them, the room's own recipients apart from its persons for presence.
   const who = value.on && 'recipients' in value ? recipientsPicker(ctx, o, value, people, () => { draw(); emit(); }) : [];
   body.replaceChildren(toggle.el, ...(kinds ? [kinds] : []), ...who);
  };
  draw();
  api.target = () => body.querySelector('input');
  api.describe();
  return api;
 };
}

// [Everyone with a phone | Chosen people], the people as chips (fields.entity with multiple), and the line who gets them.
function recipientsPicker(ctx, o, value, people, changed) {
 const {kit, t} = ctx, chosen = value.recipients;
 const seg = kit.fields.segmented({key: 'notifications:who', hass: ctx.hass, label: t('Who gets them'), disabled: o.disabled, value: chosen == null ? 'everyone' : 'chosen',
  options: [{value: 'everyone', label: t('Everyone with a phone')}, {value: 'chosen', label: t('Chosen people')}],
  onChange: v => { value.recipients = v === 'everyone' ? null : people.filter(p => p.chosen).map(p => p.person); changed(); }});
 const names = Object.fromEntries(people.map(p => [p.person, p.found === false ? t('{name} (not found)', {name: p.name}) : p.name]));
 const picker = chosen == null ? null : kit.fields.entity({hass: ctx.hass, key: 'notifications:recipients', label: t('Recipients'), multiple: true, showIds: false,
  disabled: o.disabled, choices: people.map(p => p.person), names, value: chosen, placeholder: t('Search by name'),
  onChange: v => { value.recipients = v; line.textContent = recipientsLine(ctx, v); o.onChange?.(copy(value)); }});
 const line = kit.h('p', {class: 'help rr-recipients', 'data-recipients': '', text: recipientsLine(ctx, chosen)});
 return [seg.el, ...(picker ? [picker.el] : []), line];
}

// Hand this part to its section (openthermostat-settings-rooms.js), which registers once every part of it is here.
(window.OpenThermostatSettingsParts ||= {})["rooms_fields"] = {sourcesField, contactsField, valveSave, valveKey, valvesField, personsField, notificationsField, texts: TEXTS, errors: ERRORS};
window.dispatchEvent(new CustomEvent('openthermostat-settings-part', {detail: "rooms_fields"}));
