/* Installation, part Maintenance (1.4.5 HA-PANEL-145: split from openthermostat-settings-installation.js, the module
   budget): restore a backup on this E32, tidy the entity IDs and undo it, remove the old Home Assistant rooms, each with
   its steps and texts. Loaded by the panel with the other section modules (settings.SECTION_MODULES); it hands its
   parts to its section through window.OpenThermostatSettingsParts, and the section registers once it is here. */
const TEXTS = {
 nl: {
}};
const ERRORS = {
};

// What the section shares with this part (its screens' state and helpers) comes in once, when the section registers.
const build = ({ERRORS, w, withGlyph, errorText, when, kilobytes, notice, actions, bar, poll, upload}) => {
const KINDS = {daily: 'kind_daily', manual: 'kind_manual', pre_restore: 'kind_pre_restore'};
const CLOSING = ['e32_restore_done_online', 'e32_restore_done_waiting', 'e32_restore_done_restart', 'e32_restore_done', 'e32_restore_adopted'];
/* ---- Restore a backup on this E32 (e32_backup_flow's steps: choose, check, confirm, apply, done) ---- */
function restoreSummary(ctx) {
 const b = ctx.model.live?.maintenance?.backup;
 if (!b) return ctx.t(ERRORS.e32_restore_unavailable);
 return [b.last ? w(ctx, 'last_backup', {moment: when(ctx, b.last)}) : w(ctx, 'no_backup'), w(ctx, 'kept_n', {n: b.count ?? (b.kept || []).length})].join(' · ');
}
function restorePart(ctx, m, el) {
 const {kit} = ctx, r = m.restore, b = ctx.model.live?.maintenance?.backup;
 if (ctx.readOnly) return kit.h('p', {class: 'help', text: w(ctx, 'admin_only')});
 // A restore that runs when this model was read is followed (once per model read: a closed result stays closed).
 if (ctx.model.live?.maintenance?.restoring && r.model !== ctx.model) { r.model = ctx.model; if (r.phase !== 'done') r.phase = 'applying'; }
 if (r.phase === 'checking') return [kit.statusLine(w(ctx, 'checking'), 'accent'), bar(ctx)];
 if (r.phase === 'applying') { poll(m, 'restore'); return [kit.statusLine(w(ctx, 'applying'), 'accent'), bar(ctx)]; }
 if (r.phase === 'done') return restoreDone(ctx, m);
 if (!b) return notice(ctx, ctx.t(ERRORS.e32_restore_unavailable), 'info');
 if (r.phase === 'checked' && r.check) return restoreChecked(ctx, m, el);
 return restoreChoose(ctx, m);
}
function restoreChoose(ctx, m) {
 const {kit} = ctx, {h} = kit, r = m.restore, kept = ctx.model.live.maintenance.backup.kept || [];
 const redraw = () => m.redraw.restore?.();
 const options = kept.map(k => ({value: 'kept:' + k.id, label: when(ctx, k.created),
  help: [KINDS[k.kind] ? w(ctx, KINDS[k.kind]) : k.kind, kilobytes(k.size), k.keys ? w(ctx, 'kind_secrets') : ''].filter(Boolean).join(' · ')}));
 options.push({value: 'file', label: w(ctx, 'backup_file'), help: w(ctx, 'file_help')});
 if (!options.some(o => o.value === r.source)) r.source = options[0].value;
 const error = r.error || {}, shown = [];
 const fieldError = (api, field) => { if (error.field === field) { api.setError(error.text); shown.push(field); } return api.el; };
 const parts = [h('p', {class: 'help', text: w(ctx, 'restore_choose')}), kit.more(w(ctx, 'restore_kept', {count: kept.length}), ctx.lang)];
 if (!kept.length) parts.push(notice(ctx, ctx.t(ERRORS.e32_restore_no_backups), 'info'));
 parts.push(kit.fields.radio({key: 'iv-source', hass: ctx.hass, label: w(ctx, 'backup'), value: r.source, options, help: w(ctx, 'backup_help'),
  onChange: v => { r.source = v; r.error = null; redraw(); }}).el);
 if (r.source === 'file') {
  const input = h('input', {type: 'file', accept: '.json,application/json', hidden: true, 'data-file': ''});
  input.addEventListener('change', async () => {
   const file = input.files?.[0];
   if (!file) return;
   r.uploading = true; r.error = null; redraw();
   try { r.file = {upload_id: await upload(ctx.hass, file), name: file.name}; }
   catch (e) { r.file = null; r.error = {field: 'upload_id', text: ctx.t(ERRORS.e32_restore_file_missing)}; }
   r.uploading = false; redraw();
  });
  const chooser = h('div', {class: 'field iv-file', 'data-field': 'upload_id'}, h('span', {class: 'label', text: w(ctx, 'backup_file')}),
   h('div', {class: 'iv-file-row'}, withGlyph(kit.button(w(ctx, 'choose_file'), () => input.click(), 'outlined', {icon: 'plus', 'data-action': 'choose-file', disabled: r.uploading}), 'upload'),
    h('span', {class: 'iv-file-name', text: r.uploading ? '…' : r.file?.name || ''})), input);
  if (error.field === 'upload_id') { chooser.append(h('p', {class: 'error', role: 'alert', text: error.text})); chooser.classList.add('invalid'); shown.push('upload_id'); }
  const phrase = kit.fields.text({key: 'iv-passphrase', hass: ctx.hass, label: w(ctx, 'passphrase'), help: w(ctx, 'passphrase_help'), value: r.passphrase || '',
   maxlength: 64, onChange: v => { r.passphrase = v; }});
  phrase.input.type = 'password'; phrase.input.autocomplete = 'off';
  parts.push(chooser, fieldError(phrase, 'passphrase'));
 }
 // A replacement E32: its address and password, as Configure's form (the stored password never goes to another address).
 const other = kit.button(w(ctx, 'other_e32'), () => { r.other = !r.other; redraw(); }, 'text small', {'aria-expanded': String(!!r.other), 'data-action': 'other-e32'});
 parts.push(h('div', {class: 'iv-other'}, other));
 if (r.other) {
  const address = kit.fields.text({key: 'iv-address', hass: ctx.hass, label: w(ctx, 'address'), help: w(ctx, 'address_help'), value: r.address || '', placeholder: 'http://e32.local',
   onChange: v => { r.address = v; }});
  const password = kit.fields.text({key: 'iv-password', hass: ctx.hass, label: w(ctx, 'password'), help: w(ctx, 'password_help'), value: '', onChange: v => { r.password = v; }});
  password.input.type = 'password'; password.input.autocomplete = 'off';
  parts.push(h('p', {class: 'help', text: w(ctx, 'restore_replace')}), fieldError(address, 'address'), fieldError(password, 'password'));
 }
 if (error.text && !shown.includes(error.field)) parts.push(kit.inlineError(error.text));
 const check = async () => {
  const values = {language: ctx.lang}, source = {};
  if (r.source === 'file') {
   if (!r.file) { r.error = {field: 'upload_id', text: ctx.t(ERRORS.e32_restore_file_missing)}; redraw(); return; }
   source.upload_id = r.file.upload_id;
   if (r.passphrase) values.passphrase = r.passphrase;
  } else source.backup = r.source.slice(5);
  if (r.other && (r.address || '').trim()) { values.address = r.address.trim(); if (r.password) values.password = r.password; }
  r.phase = 'checking'; r.error = null; redraw();
  try {
   r.check = await m.action('restore_check', {...values, ...source});
   r.source_values = source; r.address_used = values.address || null; r.phase = 'checked';
  } catch (e) { r.phase = 'choose'; r.error = {field: e?.field || 'base', text: errorText(ctx, e)}; }
  r.password = '';
  redraw();
 };
 parts.push(actions(ctx, kit.button(w(ctx, 'check'), check, 'outlined', {'data-action': 'check', disabled: r.uploading || (r.source === 'file' && !r.file)})));
 return parts;
}
function restoreChecked(ctx, m, el) {
 const {kit} = ctx, {h} = kit, r = m.restore, c = r.check, redraw = () => m.redraw.restore?.();
 const created = c.created ? when(ctx, c.created) : r.file?.name || '–';
 const back = () => { r.phase = 'choose'; r.check = null; r.error = null; redraw(); };
 const parts = [h('div', {class: 'iv-check', 'data-check': ''}, h('p', {class: 'iv-check-of', text: w(ctx, 'confirm_of', {created})}),
  h('p', {class: 'iv-summary', text: c.summary || ''}))];
 if (r.address_used) parts.push(h('p', {class: 'help', text: w(ctx, 'other_e32_text', {address: r.address_used})}));
 if (c.nothing && !c.adopt) {
  parts.push(notice(ctx, ctx.t(ERRORS.e32_restore_nothing), 'info'), actions(ctx, kit.button(w(ctx, 'another'), back, 'text', {'data-action': 'another'})));
  return parts;
 }
 // One question that states every fact: a restore, and (another E32) that Home Assistant uses this E32 from now on.
 const question = c.adopt && c.nothing ? {title: w(ctx, 'adopt_title'), text: w(ctx, 'adopt_text', {created}), confirm: w(ctx, 'adopt_button')}
  : c.adopt ? {title: w(ctx, 'both_title'), text: `${w(ctx, 'both_text')} ${w(ctx, 'confirm_rest')}`, confirm: w(ctx, 'both_button')}
   : {title: w(ctx, 'confirm_title'), text: w(ctx, 'confirm_rest'), confirm: w(ctx, 'confirm_button')};
 const label = c.adopt && c.nothing ? w(ctx, 'adopt_button') : c.adopt ? w(ctx, 'both_button') : w(ctx, 'restore_button');
 if (!(c.adopt && c.nothing)) parts.push(h('p', {class: 'help', text: w(ctx, 'confirm_rest')}));
 if (r.error?.text) parts.push(kit.inlineError(r.error.text));
 const apply = async () => {
  if (!(await kit.confirm(el.getRootNode(), {...question, lang: ctx.lang}))) return;
  r.phase = 'applying'; r.error = null; redraw();
  try { await m.action('restore_apply', {...r.source_values, ...(c.adopt ? {adopt: true} : {})}); poll(m, 'restore'); }
  catch (e) { r.phase = 'checked'; r.error = {field: 'base', text: errorText(ctx, e)}; }
  redraw();
 };
 parts.push(actions(ctx, kit.button(label, apply, 'filled', {'data-action': 'restore'}), kit.button(w(ctx, 'another'), back, 'text', {'data-action': 'another'})));
 return parts;
}
function restoreDone(ctx, m) {
 const {kit} = ctx, r = m.restore, a = r.result || {};
 const text = a.state === 'failed' ? ctx.errorText(a.error || 'e32_restore_failed')
  : ctx.t(ERRORS[a.state] || ERRORS.e32_restore_failed, {reenter: a.reenter || '-'});
 const tone = a.state === 'failed' ? 'error' : CLOSING.includes(a.state) ? 'success' : 'info';
 const close = () => { m.restore = {phase: 'choose', source: r.source, model: r.model}; m.redraw.restore?.(); };
 return [ctx.kit.h('div', {'data-done': a.state || ''}, notice(ctx, text, tone)), actions(ctx, kit.button(w(ctx, 'close'), close, 'text', {'data-action': 'close'}))];
}

/* ---- Tidy entity IDs and undo it (entity_id_tidy: the steps entity_ids and entity_ids_undo) ---- */
function undoCount(ctx, m) { return m.tidy.undo ?? ctx.model.live?.maintenance?.tidy_undo ?? 0; }
function tidySummary(ctx, m) { const n = undoCount(ctx, m); return n ? w(ctx, 'undo_n', {n}) : w(ctx, 'optional'); }
function tidyPart(ctx, m, el) {
 const {kit} = ctx, {h} = kit, s = m.tidy, redraw = () => m.redraw.tidy?.();
 if (ctx.readOnly) return h('p', {class: 'help', text: w(ctx, 'admin_only')});
 const close = () => { s.done = s.undone = null; s.preview = null; redraw(); };
 if (s.done) return [h('div', {'data-done': 'entity_ids_done'}, notice(ctx, ctx.t(ERRORS.entity_ids_done, {count: s.done.count, todo: s.done.todo || '-'}), 'success')),
  actions(ctx, kit.button(w(ctx, 'close'), close, 'text', {'data-action': 'close'}))];
 if (s.undone) return [h('div', {'data-done': 'entity_ids_undone'}, notice(ctx, ctx.t(ERRORS.entity_ids_undone, {count: s.undone.count}), 'success')),
  actions(ctx, kit.button(w(ctx, 'close'), close, 'text', {'data-action': 'close'}))];
 const load = () => {
  s.loading = true; s.error = null;
  m.action('tidy_ids_preview', {only_unused: s.only, language: ctx.lang}).then(a => { s.preview = a; }, e => { s.error = errorText(ctx, e); })
   .finally(() => { s.loading = false; redraw(); });
 };
 if (s.error && !s.preview) return [kit.inlineError(s.error), actions(ctx, kit.button(w(ctx, 'read_again'), () => { s.error = null; redraw(); }, 'text', {'data-action': 'again'}))];
 if (!s.preview) { if (!s.loading) load(); return kit.skeleton('rows', 2); }
 const p = s.preview, parts = [];
 if (p.nothing) parts.push(h('p', {class: 'iv-line', 'data-nothing': '', text: ctx.t(ERRORS.entity_ids_nothing)}));
 else {
  const n = (p.rows || []).length + (p.more || 0);
  parts.push(h('p', {class: 'help', text: w(ctx, 'tidy_text', {count: p.count, used: p.used})}), kit.more(w(ctx, 'tidy_warning', {days: p.days}), ctx.lang),
   kit.fields.radio({key: 'iv-scope', hass: ctx.hass, label: w(ctx, 'scope'), value: s.only ? 'unused' : 'all', help: w(ctx, 'scope_help'),
    options: [{value: 'unused', label: w(ctx, 'scope_unused')}, {value: 'all', label: w(ctx, 'scope_all')}],
    onChange: v => { s.only = v === 'unused'; s.preview = null; redraw(); }}).el,
   h('div', {class: 'iv-ids', 'data-ids': ''}, ...(p.rows || []).map(r => h('div', {class: 'iv-id', 'data-old': r.old},
    r.name ? h('span', {class: 'iv-id-name', text: r.name}) : null,
    h('span', {class: 'iv-id-ids'}, h('span', {class: 'iv-id-old', text: r.old}), h('span', {class: 'iv-arrow', 'aria-hidden': 'true', text: ' → '}), h('span', {class: 'iv-id-new', text: r.new})),
    r.used_in?.length ? h('span', {class: 'iv-id-used', text: w(ctx, 'used_in', {places: r.used_in.join(', ')})}) : null))),
   p.more ? h('p', {class: 'help', text: w(ctx, 'more_n', {n: p.more})}) : null);
  if (s.error) parts.push(kit.inlineError(s.error));
  const tidy = async () => {
   if (!(await kit.confirm(el.getRootNode(), {title: w(ctx, 'rename_title', {count: n}), text: w(ctx, 'tidy_warning', {days: p.days}),
    confirm: w(ctx, 'tidy_confirm'), lang: ctx.lang}))) return;
   try { const a = await m.action('tidy_ids_apply', {only_unused: s.only, language: ctx.lang}); s.done = a; s.undo = a.count; s.preview = null; }
   catch (e) { s.error = errorText(ctx, e); }
   redraw();
  };
  if (n) parts.push(actions(ctx, kit.button(w(ctx, 'tidy_button'), tidy, 'outlined', {'data-action': 'tidy'})));
 }
 const count = undoCount(ctx, m);
 if (count) {
  const undo = async () => {
   if (!(await kit.confirm(el.getRootNode(), {title: w(ctx, 'undo'), text: w(ctx, 'undo_text', {count}), confirm: w(ctx, 'undo_confirm'), lang: ctx.lang}))) return;
   try { s.undone = await m.action('tidy_ids_undo', {language: ctx.lang}); s.undo = 0; s.preview = null; }
   catch (e) { s.error = errorText(ctx, e); }
   redraw();
  };
  parts.push(h('div', {class: 'iv-undo', 'data-undo': ''}, h('h3', {class: 'iv-sub', text: w(ctx, 'undo')}), h('p', {class: 'help', text: w(ctx, 'undo_text', {count})}),
   actions(ctx, kit.button(w(ctx, 'undo_button'), undo, 'outlined', {'data-action': 'undo'}))));
 }
 return parts;
}

/* ---- Remove the old Home Assistant rooms (legacy_rooms_flow: the steps legacy_rooms*, Repairs' too) ---- */
function legacySummary(ctx) {
 const n = ctx.model.live?.maintenance?.legacy_rooms || 0;
 return n === 1 ? w(ctx, 'room_one') : n ? w(ctx, 'rooms_n', {n}) : w(ctx, 'finish');
}
function legacyPart(ctx, m, el) {
 const {kit} = ctx, {h} = kit, l = m.legacy, redraw = () => m.redraw.legacy?.();
 if (ctx.readOnly) return h('p', {class: 'help', text: w(ctx, 'admin_only')});
 if (ctx.model.live?.maintenance?.legacy_removing && l.model !== ctx.model) { l.model = ctx.model; if (!l.phase) l.phase = 'removing'; }
 if (l.phase === 'removing') { poll(m, 'legacy'); return [kit.statusLine(w(ctx, 'removing'), 'accent'), bar(ctx)]; }
 const reload = () => { l.phase = null; l.list = null; l.result = null; l.error = l.failed = null; redraw(); };
 if (l.phase === 'done') {
  const a = l.result || {};
  const text = a.state === 'failed' ? ctx.errorText(a.error || 'legacy_rooms_plan_failed') : ctx.t(ERRORS[a.state] || ERRORS.legacy_rooms_plan_failed, {rooms: a.rooms ?? 0});
  return [h('div', {'data-done': a.state || ''}, notice(ctx, text, a.state === 'failed' ? 'error' : a.state === 'legacy_rooms_removed' ? 'success' : 'info')),
   actions(ctx, kit.button(w(ctx, 'close'), reload, 'text', {'data-action': 'close'}))];
 }
 if (!l.list) {
  // A list that could not be read says why; a refused removal says why above the list read again.
  if (l.failed) return [kit.inlineError(l.failed), actions(ctx, kit.button(w(ctx, 'read_again'), reload, 'text', {'data-action': 'again'}))];
  if (!l.loading) {
   l.loading = true;
   m.action('legacy_rooms', {language: ctx.lang}).then(a => { l.list = a; }, e => { l.failed = errorText(ctx, e); }).finally(() => { l.loading = false; redraw(); });
  }
  return [l.error ? kit.inlineError(l.error) : null, kit.skeleton('rows', 2)];
 }
 const a = l.list, parts = [];
 const remove = async (ids, question) => {
  if (question && !(await kit.confirm(el.getRootNode(), {...question, lang: ctx.lang}))) return;
  l.phase = 'removing'; l.error = null; redraw();
  try { await m.action('legacy_rooms_remove', {ids, language: ctx.lang}); poll(m, 'legacy'); }
  catch (e) { l.phase = null; l.error = errorText(ctx, e); if (e?.code === 'legacy_rooms_changed') l.list = null; }
  redraw();
 };
 if (a.state === 'legacy_rooms_none') return h('p', {class: 'iv-line', text: ctx.t(ERRORS.legacy_rooms_none)});
 if (a.problem) parts.push(notice(ctx, ctx.errorText(a.problem), 'error'));
 if (l.error) parts.push(kit.inlineError(l.error));
 if (a.finish) {
  parts.push(h('p', {class: 'help', text: w(ctx, 'finish_text')}));
  if (!a.problem) parts.push(actions(ctx, kit.button(w(ctx, 'finish'), () => remove([]), 'outlined', {'data-action': 'finish'})));
  return parts;
 }
 parts.push(h('p', {class: 'help', text: w(ctx, 'legacy_text', {rooms: a.rooms.map(r => r.name).join(', ')})}),
  h('div', {class: 'iv-ids', 'data-rooms': ''}, ...a.rooms.map(r => h('div', {class: 'iv-id', 'data-room': r.id}, h('span', {class: 'iv-id-name', text: r.name}),
   r.entities?.length ? h('span', {class: 'iv-id-used', text: r.entities.join(', ')}) : null))),
  h('h3', {class: 'iv-sub', text: w(ctx, 'what_happens')}), h('p', {class: 'iv-summary', 'data-changes': '', text: a.changes || ''}));
 if (!a.problem && a.readable !== false) {
  parts.push(actions(ctx, kit.button(w(ctx, 'legacy'), () => remove(a.rooms.map(r => r.id), {title: w(ctx, 'legacy_question'), text: w(ctx, 'legacy_remove_text'),
   confirm: w(ctx, 'legacy'), danger: true}), 'danger', {'data-action': 'remove'})));
 } else if (a.readable === false) parts.push(actions(ctx, kit.button(w(ctx, 'read_again'), reload, 'text', {'data-action': 'again'})));
 return parts;
}

 return {restoreSummary, restorePart, tidySummary, tidyPart, legacySummary, legacyPart};
};
// Hand this part to its section (openthermostat-settings-installation.js), which registers once every part of it is here.
(window.OpenThermostatSettingsParts ||= {})["installation_maintenance"] = {build, texts: TEXTS, errors: ERRORS};
window.dispatchEvent(new CustomEvent('openthermostat-settings-part', {detail: "installation_maintenance"}));
