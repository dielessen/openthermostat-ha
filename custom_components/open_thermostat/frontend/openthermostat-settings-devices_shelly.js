/* Devices, part Shelly devices (1.4.5 HA-PANEL-145: split from openthermostat-settings-devices.js, the module budget):
   the screens #devices/shelly and #devices/shelly/<id> (a device's health, The Pill's probes, a BLU Gateway's valves and
   the pump by hand), with their texts. Loaded by the panel with the other section modules (settings.SECTION_MODULES);
   it hands its screens to its section through window.OpenThermostatSettingsParts, and the section registers once it
   is here. */
const TEXTS = {
 nl: {
  'Saving…': 'Opslaan…',
  'Shelly devices': 'Shelly-apparaten',
  '1 valve': '1 kraan',
  '{n} valves': '{n} kranen',
  'No reading': 'Geen meting',
  'Shelly device': 'Shelly-apparaat',
  'Add a Shelly device': 'Shelly-apparaat toevoegen',
  'No Shelly devices yet.': 'Nog geen Shelly-apparaten.',
  'IP address': 'IP-adres',
  'Remove device': 'Apparaat verwijderen',
  'Remove {name}?': '{name} verwijderen?',
  'The E32 stops reading and switching the device. The valves of a BLU Gateway stay in their rooms until you remove them under Rooms.': 'De E32 leest en schakelt het apparaat niet meer. De kranen van een BLU Gateway blijven in hun ruimtes tot je ze onder Ruimtes verwijdert.',
  'Probe roles': 'Sonderollen',
  'Give each probe the pipe it sits on.': 'Geef elke sonde de leiding waar hij op zit.',
  'The E32 uses the water to and back from the floor for the pump and to watch for too hot water.': 'De E32 gebruikt het water naar en terug van de vloer voor de pomp en om te bewaken of het water te heet wordt.',
  'Probe {n}': 'Sonde {n}',
  'Back from floor loop {n}': 'Terug van vloergroep {n}',
  'Other probe {n}': 'Andere sonde {n}',
  'Not used': 'Niet gebruikt',
  'A heating circuit measures with this probe. Change the circuit first (on the E32: Home → Heating settings).': 'Een verwarmingscircuit meet met deze sonde. Pas eerst het circuit aan (op de E32: Huis → Verwarming).',
  'Save probe roles': 'Sonderollen opslaan',
  'Probe roles saved.': 'Sonderollen opgeslagen.',
  'The Pill reports no probes yet.': 'The Pill meldt nog geen sondes.',
  'Try again': 'Opnieuw proberen',
  'Valves': 'Kranen',
  'Valve {id}': 'Kraan {id}',
  'room: {room}': 'ruimte: {room}',
  'No valves yet.': 'Nog geen kranen.',
  'Add a valve': 'Kraan toevoegen',
  'Remove': 'Verwijderen',
  'Remove {valve}': '{valve} verwijderen',
  'The E32 stops reading and driving these valves. A valve in a room stays there until you remove it under Rooms → the room → Radiator valves.': 'De E32 leest en stuurt deze kranen niet meer. Een kraan in een ruimte blijft daar tot je hem verwijdert onder Ruimtes → de ruimte → Radiatorkranen.',
  'Look for valves at the gateway': 'Kranen zoeken bij de gateway',
  'Looking for valves at the gateway…': 'Kranen zoeken bij de gateway…',
  'Tap a valve to add it.': 'Tik op een kraan om hem toe te voegen.',
  'Already in the list': 'Staat al in de lijst',
  'The gateway reports no paired valves. Pair them in the Shelly app first.': 'De gateway meldt geen gekoppelde kranen. Koppel ze eerst in de Shelly-app.',
  'The gateway reported more devices than the E32 reads; not every valve may be listed.': 'De gateway meldde meer apparaten dan de E32 leest; misschien staat niet elke kraan in de lijst.',
  'A gateway takes at most 5 valves.': 'Een gateway neemt hoogstens 5 kranen.',
  'waiting for the first answer': 'wacht op het eerste antwoord',
  'connected': 'verbonden',
  'not reachable': 'niet bereikbaar',
  'another device answers at this address': 'op dit adres antwoordt een ander apparaat',
  'the password is not accepted': 'het wachtwoord wordt niet geaccepteerd',
  'the device reports an error': 'het apparaat meldt een fout',
  'waiting for a report': 'wacht op een melding',
  'reporting': 'meldt zich',
  'silent for 15 minutes': 'al 15 minuten stil',
  'not reporting': 'meldt zich niet',
  'not found at the gateway': 'niet gevonden bij de gateway',
  'not paired with the gateway': 'niet gekoppeld aan de gateway',
  'gateway not reachable': 'gateway niet bereikbaar',
  'Water to the floor (after the mixing valve)': 'Water naar de vloer (na de mengklep)',
  'Water back from the floor': 'Water terug van de vloer',
  'Waiting for a reading': 'Wacht op een meting',
  'Not found on The Pill': 'Niet gevonden op The Pill',
  'The gateway did not answer. Try again, or add the valves by number below.': 'De gateway antwoordde niet. Probeer het opnieuw, of voeg de kranen hieronder toe met hun nummer.',
  'The search was interrupted. Try again.': 'Het zoeken werd onderbroken. Probeer het opnieuw.',
  'Another device answers at this address': 'Op dit adres antwoordt een ander apparaat',
  'The password is not accepted': 'Het wachtwoord wordt niet geaccepteerd',
  'The gateway gave no list of its valves. Update its firmware in the Shelly app, or add the valves by number below.': 'De gateway gaf geen lijst van zijn kranen. Werk zijn firmware bij in de Shelly-app, of voeg de kranen hieronder toe met hun nummer.'}};
const ERRORS = {
};

// What the section shares with this part (its screens' state and helpers) comes in once, when the section registers.
const build = ({ERRORS, SCREENS, JOBS, deviceName, sleep, icon, card, button, item, problem, state, routeTo, show, redraw, head, saved, flash, errorLine, POLL_GATEWAY_MS, GATEWAY_MS}) => {
const HEALTH = {waiting: 'waiting for the first answer', ok: 'connected', unreachable: 'not reachable', wrong_device: 'another device answers at this address',
 auth_failed: 'the password is not accepted', error: 'the device reports an error'};
const VALVE_HEALTH = {waiting: 'waiting for a report', ok: 'reporting', silent: 'silent for 15 minutes', offline: 'not reporting',
 missing: 'not found at the gateway', unpaired: 'not paired with the gateway', gateway: 'gateway not reachable'};
// The pipes of The Pill's probes (heating_link.PROBE_ROLES; the E32 page's words); loop_return_<n> and other_<n> are numbered.
const PIPES = {floor_supply: 'Water to the floor (after the mixing valve)', floor_return: 'Water back from the floor'};
const PROBE_HEALTH = {waiting: 'Waiting for a reading', no_reading: 'No reading', missing: 'Not found on The Pill'};
// Why the gateway's search found nothing (gateway_scan_result reason; the E32 page's words).
const REASONS = {no_answer: 'The gateway did not answer. Try again, or add the valves by number below.', interrupted: 'The search was interrupted. Try again.',
 wrong_device: 'Another device answers at this address', password: 'The password is not accepted',
 no_list: 'The gateway gave no list of its valves. Update its firmware in the Shelly app, or add the valves by number below.'};
const KIND_ICON = Object.freeze({switch: 'plug', probes: 'probe', gateway: 'gateway'});
const pipeOf = (role, t) => {
 if (PIPES[role]) return t(PIPES[role]);
 const m = /^(loop_return|other)_(\d+)$/.exec(role || '');
 return m ? t(m[1] === 'loop_return' ? 'Back from floor loop {n}' : 'Other probe {n}', {n: m[2]}) : role;
};
/* ---- Shelly devices ---- */
function healthChip(t, health) {
 if (!HEALTH[health]) return null;
 const bad = !['ok', 'waiting'].includes(health);
 return [t(HEALTH[health]), problem(bad), bad ? 'alert' : health === 'ok' ? 'check' : null];
}
function shellyScreen(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit, sh = m.shelly, live = m.live?.shelly || {};
 const out = [head(ctx, t('Shelly devices'), t(SCREENS.shelly[1]))];
 out.push(flash(ctx, 'shelly') || saved(ctx, ['removed']));
 if (!sh) return [...out, kit.notice(t(ERRORS.shelly_unsupported), 'info')];
 const full = sh.devices.length >= sh.max_devices;
 const add = button(kit, t('Shelly device'), () => ctx.navigate('#devices/shelly-add'), 'filled', 'plus',
  {disabled: ctx.readOnly || full, 'aria-label': t('Add a Shelly device'), 'data-add-device': ''});
 if (!sh.devices.length) return [...out, h('div', {class: 'ot-card'}, kit.empty({icon: 'devices', text: t('No Shelly devices yet.'), action: add}))];
 out.push(kit.h('div', {class: 'dv-toolbar end'}, add));
 if (full) out.push(h('p', {class: 'help dv-full', text: t(ERRORS.shelly_full)}));
 const list = h('div', {class: 'card list', 'data-list': 'shelly'});
 for (const d of sh.devices) {
  const valves = d.kind === 'gateway' ? (d.valves || []).length : null;
  list.append(item(kit, {name: KIND_ICON[d.kind] || 'devices', label: deviceName(d), data: {device: d.id},
   lines: [[t(JOBS[d.kind]), d.ip].join(' · '), valves == null ? '' : valves === 1 ? t('1 valve') : t('{n} valves', {n: valves})],
   chips: [healthChip(t, live[String(d.n)])], route: routeTo('device/' + d.id), onClick: () => show('device/' + d.id)}));
 }
 out.push(list);
 return out;
}
function deviceScreen(ctx, id) {
 const {kit, t, model: m} = ctx, {h} = kit, d = m.device, live = m.live?.shelly || {};
 if (m.supported === false) return [head(ctx, t('Shelly device'), null), kit.notice(t(ERRORS.shelly_unsupported), 'info')];
 if (!d) {  // a link to a device that was removed
  return [head(ctx, t('Shelly device'), null), kit.notice(t('No Shelly devices yet.'), 'info',
   kit.button(t('Shelly devices'), () => show('shelly'), 'outlined', {'data-to-list': ''}))];
 }
 const out = [head(ctx, deviceName(d), t(JOBS[d.kind]))];
 const chip = healthChip(t, live[String(d.n)]);
 out.push(h('div', {class: 'ot-card dv-facts'}, h('span', {class: 'row-icon'}, icon(kit, KIND_ICON[d.kind] || 'devices')),
  h('div', {class: 'dv-fact'}, h('span', {class: 'label', text: t('IP address')}), h('span', {class: 'dv-ip', text: d.ip})),
  chip ? kit.chip(...chip) : null));
 if (d.kind === 'probes') out.push(pillCard(ctx, d));
 if (d.kind === 'gateway') out.push(flash(ctx, 'valve') || saved(ctx, ['valves_removed']), ...gatewayCards(ctx, d));
 if (d.pump) out.push(h('p', {class: 'help dv-why', 'data-pump': '', text: t(ERRORS.shelly_pump_in_use)}));
 else if (!ctx.readOnly) out.push(h('div', {class: 'dv-remove'}, button(kit, t('Remove device'), () => ctx.act({action: 'shelly_remove', device: d.id}, {
  title: t('Remove {name}?', {name: deviceName(d)}),
  text: t('The E32 stops reading and switching the device. The valves of a BLU Gateway stay in their rooms until you remove them under Rooms.'),
  confirm: t('Remove device'), danger: true}), 'danger', 'trash', {'data-remove-device': d.id})));
 return out;
}

/* The Pill: each probe's pipe, read with pill_roles and saved whole with set_pill_roles. */
async function loadPill(id) {
 const run = state.pill = {id, loading: true, answer: null, chosen: {}, error: null, errors: {}, busy: false, done: false};
 redraw();
 try {
  const answer = await state.ctx.action('pill_roles', {device: id});
  if (state.pill !== run) return;
  run.answer = answer;
  for (const p of answer.probes || []) run.chosen[p.c] = p.role || '';
 } catch (e) { if (state.pill === run) run.error = e.text; }
 if (state.pill === run) { run.loading = false; redraw(); }
}
function pillCard(ctx, d) {
 const {kit, t, lang} = ctx, {h} = kit, p = state.pill;
 const head = {title: t('Probe roles'), icon: 'probe', summary: t('Give each probe the pipe it sits on.'), data: {card: 'roles'}};
 const more = kit.more(t('The E32 uses the water to and back from the floor for the pump and to watch for too hot water.'), ctx.lang);
 // Reading the probes is an action, and actions are for administrators (CONTRACT-1.4.1 §3).
 if (ctx.readOnly) return card(kit, head, more);
 if (!p || p.id !== d.id) queueMicrotask(() => { if (state.screen === 'device/' + d.id && state.pill?.id !== d.id) loadPill(d.id); });
 const body = [];
 if (!p || p.id !== d.id || p.loading) body.push(h('div', {role: 'status', 'aria-label': t('Probe roles')}, kit.skeleton('rows', 2)));
 else if (p.error && !p.answer) body.push(kit.inlineError(p.error), kit.button(t('Try again'), () => loadPill(d.id), 'text', {'data-retry': ''}));
 else {
  const a = p.answer, used = a.in_use || {}, probes = a.probes || [];
  if (p.done) body.push(h('div', {class: 'dv-done', 'data-done': 'roles'}, kit.notice(t('Probe roles saved.'), 'success')));
  body.push(errorLine(kit, p.error));
  if (!probes.length) body.push(h('p', {class: 'help', text: t('The Pill reports no probes yet.')}));
  const fields = h('div', {class: 'fields'});
  for (const probe of probes) {
   const mine = p.chosen[probe.c] || '', held = probe.role && used[probe.role] && mine === probe.role && (a.roles || {})[probe.c] === probe.role;
   const now = probe.health === 'ok' && typeof probe.t_c === 'number' ? kit.degrees(probe.t_c, '°C', lang) : t(PROBE_HEALTH[probe.health] || PROBE_HEALTH.waiting);
   const taken = new Set(Object.entries(p.chosen).filter(([c, r]) => r && Number(c) !== probe.c).map(([, r]) => r));
   const api = kit.fields.select({key: `role:${probe.c}`, label: t('Probe {n}', {n: probe.c - 99}), value: mine, hass: ctx.hass, disabled: ctx.readOnly || held || p.busy,
    help: held ? `${kit.together(now)} · ${t('A heating circuit measures with this probe. Change the circuit first (on the E32: Home → Heating settings).')}` : kit.together(now),
    options: [{value: '', label: t('Not used')}, ...(a.choices || []).map(role => ({value: role, label: pipeOf(role, t)}))],
    onChange: v => { p.chosen[probe.c] = v; p.done = false; delete p.errors[probe.c]; redraw(); }});
   for (const option of api.el.querySelectorAll('option')) if (option.value && taken.has(option.value)) option.disabled = true;
   if (p.errors[probe.c]) api.setError(p.errors[probe.c]);
   api.el.dataset.probe = String(probe.c);
   fields.append(api.el);
  }
  body.push(fields);
  const changed = probes.some(x => (p.chosen[x.c] || '') !== ((a.roles || {})[x.c] || ''));
  if (probes.length) body.push(h('div', {class: 'dv-actions'}, kit.button(p.busy ? t('Saving…') : t('Save probe roles'), () => saveRoles(d.id), 'filled',
   {disabled: ctx.readOnly || p.busy || !changed, 'data-save-roles': ''})));
 }
 return card(kit, head, more, ...body);
}
async function saveRoles(id) {
 const p = state.pill;
 if (!p?.answer || p.busy) return;
 const roles = Object.fromEntries((p.answer.probes || []).map(x => [String(x.c), p.chosen[x.c] || null]));
 p.busy = true; p.error = null; p.errors = {}; p.done = false; redraw();
 try {
  const r = await state.ctx.action('set_pill_roles', {device: id, roles});
  if (state.pill !== p) return;
  p.answer = {...p.answer, roles: r.roles || {}, probes: p.answer.probes.map(x => ({...x, role: (r.roles || {})[x.c] || null}))};
  for (const x of p.answer.probes) p.chosen[x.c] = x.role || '';
  p.done = true;
 } catch (e) {
  if (state.pill !== p) return;
  const m = /^role:(\d+)$/.exec(e.field || '');
  if (m) p.errors[m[1]] = e.text; else p.error = e.text;
 }
 p.busy = false; redraw();
}

/* The BLU Gateway: its valves, and the search for the valves paired with it in the Shelly app. */
async function startGatewayScan(d) {
 const ctx = state.ctx;
 if (!ctx || ctx.readOnly) return;
 const run = state.gateway = {id: d.id, n: d.n, running: true, result: null, error: null, timeout: false, until: Date.now() + GATEWAY_MS};
 redraw();
 const alive = () => state.gateway === run && run.running && state.root?.isConnected && state.screen === 'device/' + d.id;
 try { await ctx.action('gateway_scan', {gateway: d.n}); } catch (e) { if (state.gateway === run) { run.running = false; run.error = e.text; redraw(); } return; }
 while (alive()) {
  await sleep(POLL_GATEWAY_MS);
  if (!alive()) break;
  try {
   const r = await state.ctx.action('gateway_scan_result', {gateway: d.n});
   if (state.gateway !== run) return;
   run.result = r;
   if (r.done) run.running = false;
   else if (Date.now() >= run.until) { run.running = false; run.timeout = true; }
  } catch (e) { if (state.gateway !== run) return; run.running = false; run.error = e.text; }
  if (state.screen === 'device/' + d.id) redraw();
 }
 if (state.gateway === run) run.running = false;
}
function gatewayCards(ctx, d) {
 const {kit, t, model: m} = ctx, {h} = kit, live = m.live?.shelly || {}, max = m.max_valves, valves = d.valves || [];
 const full = valves.length >= max;
 const list = h('div', {class: 'card list dv-inner', 'data-list': 'valves'});
 for (const v of valves) {
  const key = `${d.n}:${v.id}`, health = live[key], name = t('Valve {id}', {id: v.id}) + (v.name ? ` · ${v.name}` : '');
  const bad = health && !['ok', 'waiting'].includes(health);
  list.append(item(kit, {name: 'valve', label: name, data: {valve: key}, lines: [live['room:' + key] ? t('room: {room}', {room: live['room:' + key]}) : ''],
   chips: [VALVE_HEALTH[health] ? [t(VALVE_HEALTH[health]), problem(bad), bad ? 'alert' : null] : null],
   trailing: ctx.readOnly ? null : kit.iconButton('close', t('Remove {valve}', {valve: t('Valve {id}', {id: v.id})}), () => ctx.act({action: 'valves_remove', valves: [key]}, {
    title: t('Remove {name}?', {name: t('Valve {id}', {id: v.id})}),
    text: t('The E32 stops reading and driving these valves. A valve in a room stays there until you remove it under Rooms → the room → Radiator valves.'),
    confirm: t('Remove'), danger: true}), {'data-remove-valve': key})}));
 }
 if (!valves.length) list.append(h('p', {class: 'help dv-none', text: t('No valves yet.')}));
 const from = {id: d.id, name: deviceName(d)};
 const byNumber = kit.button(t('Add a valve'), () => { state.prefill = {gateway: String(d.n)}; state.valveFrom = from; ctx.navigate('#devices/valve-add'); }, 'text',
  {disabled: ctx.readOnly || full, 'data-add-valve': d.id});
 const valvesCard = card(kit, {title: t('Valves'), icon: 'valve', data: {card: 'valves'}}, list,
  full ? h('p', {class: 'help dv-full', text: t('A gateway takes at most 5 valves.')}) : null, h('div', {class: 'dv-actions'}, byNumber));
 // The search.
 const g = state.gateway?.id === d.id ? state.gateway : null, r = g?.result, body = [];
 const look = button(kit, t('Look for valves at the gateway'), () => startGatewayScan(d), 'filled', 'magnify',
  {disabled: ctx.readOnly || full || !!g?.running, 'data-gateway-scan': d.id});
 if (g?.running) body.push(h('div', {class: 'dv-status', 'data-status': 'looking'}, kit.statusLine(t('Looking for valves at the gateway…'), 'accent')));
 else body.push(h('div', {class: 'dv-actions'}, look));
 if (g?.error) body.push(kit.inlineError(g.error));
 else if (g?.timeout) body.push(h('div', {'data-status': 'no_answer'}, kit.statusLine(t(REASONS.no_answer), 'attention')));
 else if (r?.state === 'failed') body.push(h('div', {'data-status': r.reason || 'failed'}, kit.statusLine(t(REASONS[r.reason] || REASONS.interrupted), 'attention')));
 if (r?.more) body.push(h('p', {class: 'help', text: t('The gateway reported more devices than the E32 reads; not every valve may be listed.')}));
 const found = r?.state === 'ok' ? r.valves || [] : [];
 if (found.length) {
  const room = !full && !r.full;
  body.push(h('p', {class: 'help', text: room ? t('Tap a valve to add it.') : t('A gateway takes at most 5 valves.')}));
  const rows = h('div', {class: 'card list dv-inner', 'data-list': 'found-valves'});
  for (const v of found) rows.append(item(kit, {name: 'valve', label: t('Valve {id}', {id: v.id}) + (v.name ? ` · ${v.name}` : ''), data: {'found-valve': v.id},
   chips: [v.known ? [t('Already in the list'), 'rest', 'check'] : null], disabled: v.known || !room || ctx.readOnly,
   onClick: () => { state.prefill = {gateway: String(d.n), valve: v.id, name: v.name || ''}; state.valveFrom = from; ctx.navigate('#devices/valve-add'); }}));
  body.push(rows);
 } else if (r?.state === 'ok' && !g.running) body.push(h('p', {class: 'help', 'data-status': 'none', text: t('The gateway reports no paired valves. Pair them in the Shelly app first.')}));
 else if (g?.running) body.push(kit.skeleton('rows', 2));
 return [valvesCard, kit.h('section', {class: 'ot-card dv-search', 'data-card': 'search'}, ...body)];
}

 return {shellyScreen, deviceScreen};
};
// Hand this part to its section (openthermostat-settings-devices.js), which registers once every part of it is here.
(window.OpenThermostatSettingsParts ||= {})["devices_shelly"] = {build, texts: TEXTS, errors: ERRORS};
window.dispatchEvent(new CustomEvent('openthermostat-settings-part', {detail: "devices_shelly"}));
