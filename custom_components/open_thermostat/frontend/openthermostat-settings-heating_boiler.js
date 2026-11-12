/* Heating and boiler, part Boiler settings (1.4.5 HA-PANEL-145: split from openthermostat-settings-heating.js, the module
   budget): the screen #heating/boiler, allow, change, watch, put back, Advanced and stop, each step an action of
   settings/action (settings_heating.ACTIONS, CONTRACT-1.4.1 §3), with its texts and errors. Loaded by the panel with the
   other section modules (settings.SECTION_MODULES); it hands boilerSettings to its section through
   window.OpenThermostatSettingsParts, and the section registers once it is here. */
const TEXTS = {
 nl: {
  'Boiler settings': 'Ketelinstellingen',
  'Off': 'Uit',
  'On': 'Aan',
  'Check the boiler': 'Controleer de ketel',
  'Tick the box to allow it.': 'Vink het vakje aan om het toe te staan.',
  'Tick the box to go on at your own risk.': 'Vink het vakje aan om op eigen risico verder te gaan.',
  'Choose a setting from the list.': 'Kies een instelling uit de lijst.',
  'The boiler does not accept this value: choose one in the range shown.': 'De ketel accepteert deze waarde niet: kies er een binnen het getoonde bereik.',
  'This is above the highest water temperature of your room plan: raise that first (Water temperature limits).': 'Dit is hoger dan de hoogste watertemperatuur van je ruimteplan: verhoog die eerst (Grenzen van de watertemperatuur).',
  'This value is outside the everyday range: use Advanced (installer settings).': 'Deze waarde ligt buiten het gewone bereik: gebruik Geavanceerd (installateursinstellingen).',
  'Changing boiler settings is off: choose “Allow the E32 to change boiler settings” first.': 'Ketelinstellingen wijzigen staat uit: kies eerst “De E32 ketelinstellingen laten wijzigen”.',
  'This E32 cannot change boiler settings.': 'Deze E32 kan geen ketelinstellingen wijzigen.',
  'The E32 cannot change boiler settings right now: the boiler test, a reading or an update is busy, or the boiler has not answered yet. Try again later.': 'De E32 kan nu geen ketelinstellingen wijzigen: de keteltest, een uitlezing of een update is bezig, of de ketel heeft nog niet geantwoord. Probeer het later opnieuw.',
  'The E32 is about to restart or update; try again in a minute.': 'De E32 gaat zo herstarten of bijwerken; probeer het over een minuut opnieuw.',
  'Your boiler does not support this setting.': 'Je ketel ondersteunt deze instelling niet.',
  'A setting could not be put back: check the boiler and confirm it under Settings → Repairs first.': 'Een instelling kon niet worden teruggezet: controleer de ketel en bevestig dat eerst onder Instellingen → Reparaties.',
  'Wait half a minute before changing this setting again.': 'Wacht een halve minuut voor je deze instelling weer wijzigt.',
  'The E32 changes at most 12 boiler settings a day. Try again tomorrow.': 'De E32 wijzigt hoogstens 12 ketelinstellingen per dag. Probeer het morgen opnieuw.',
  'The E32 is busy with another boiler setting change. Try again in a few minutes.': 'De E32 is bezig met een andere wijziging van een ketelinstelling. Probeer het over een paar minuten opnieuw.',
  'The E32 could not store this. Try again.': 'De E32 kon dit niet opslaan. Probeer het opnieuw.',
  'The E32 refused the change ({error}).': 'De E32 weigerde de wijziging ({error}).',
  'Really switch it off? This really switches {what} off on the boiler.': 'Echt uitzetten? Dit zet {what} echt uit op de ketel.',
  'Burner rest between starts': 'Rusttijd brander tussen starts',
  'Heating on the boiler': 'Verwarming op de ketel',
  'Boiler maximum': 'Maximum van de ketel',
  'Maximum burner power': 'Maximaal brandervermogen',
  'Switching margin off (hysteresis)': 'Schakelmarge uit (hysterese)',
  'Switching margin on (hysteresis)': 'Schakelmarge aan (hysterese)',
  'Pump run-on': 'Pompnaloop',
  'Highest pump speed': 'Hoogste pompsnelheid',
  'Lowest pump speed': 'Laagste pompsnelheid',
  'Pump mode': 'Pompmodus',
  'Hot water on the boiler': 'Warm water op de ketel',
  'Selected hot water temperature': 'Ingestelde tapwatertemperatuur',
  'Hot water switching margin (hysteresis)': 'Schakelmarge warm water (hysterese)',
  'Hot water charge optimisation': 'Laadoptimalisatie warm water',
  'Extra water temperature for hot water': 'Extra watertemperatuur voor warm water',
  'Hot water circulation pump': 'Circulatiepomp warm water',
  'Hot water circulation times': 'Circulatietijden warm water',
  'Hot water disinfection temperature': 'Desinfectietemperatuur warm water',
  'Hot water comfort': 'Warmwatercomfort',
  'not read yet': 'nog niet gelezen',
  'Hot: always ready': 'Heet: altijd klaar',
  'Eco: saves gas': 'Eco: bespaart gas',
  'Intelligent: learns when you use it': 'Intelligent: leert wanneer je het gebruikt',
  'Follows the heat demand': 'Volgt de warmtevraag',
  'Fixed pressure, level {n}': 'Vaste druk, stand {n}',
  '{n} × 3 minutes an hour': '{n} × 3 minuten per uur',
  'Always on': 'Altijd aan',
  '{low} to {high}': '{low} tot {high}',
  'one of the choices below': 'een van de keuzes hieronder',
  'Verified on this boiler': 'Bevestigd op deze ketel',
  'Not yet verified: try it while you watch': 'Nog niet bevestigd: probeer het terwijl je kijkt',
  'Not supported by this boiler': 'Niet ondersteund door deze ketel',
  'Verified on your boiler: the E32 writes it at once and reads it back.': 'Bevestigd op je ketel: de E32 schrijft het meteen en leest het terug.',
  'Not yet verified on your boiler. After the change, watch the boiler for up to 15 minutes, then keep the new value or put it back. If you do neither, the E32 puts it back by itself.': 'Nog niet bevestigd op je ketel. Kijk na de wijziging tot 15 minuten naar de ketel, en behoud dan de nieuwe waarde of zet hem terug. Doe je geen van beide, dan zet de E32 hem zelf terug.',
  'Changing boiler settings: {state}': 'Ketelinstellingen wijzigen: {state}',
  '**off**: the E32 writes nothing to the boiler.': '**uit**: de E32 schrijft niets naar de ketel.',
  '**on**: {used} of {cap} changes used today.': '**aan**: {used} van {cap} wijzigingen gebruikt vandaag.',
  'a change of {setting} is running.': 'een wijziging van {setting} loopt.',
  '**blocked**: a setting could not be put back. Check the boiler (Settings → Repairs).': '**geblokkeerd**: een instelling kon niet worden teruggezet. Controleer de ketel (Instellingen → Reparaties).',
  'on, but not possible right now (the boiler test, a reading or an update is busy).': 'aan, maar nu niet mogelijk (de keteltest, een uitlezing of een update is bezig).',
  'not possible on this E32.': 'niet mogelijk op deze E32.',
  'Allow the E32 to change boiler settings': 'De E32 ketelinstellingen laten wijzigen',
  'Boiler settings stay in the boiler, also after a restart of the boiler or the E32. A wrong setting can leave the house cold, make the hot water too hot or let the burner switch on and off too often.': 'Ketelinstellingen blijven in de ketel, ook na een herstart van de ketel of de E32. Een verkeerde instelling kan het huis koud laten, het warme water te heet maken of de brander te vaak laten aanslaan.',
  'The E32 changes a setting only when you ask, one at a time and at most {cap} a day. It reads every change back from the boiler and puts it back when the boiler does not take it. You can switch this off here at any time.': 'De E32 wijzigt een instelling alleen als jij erom vraagt, één tegelijk en hoogstens {cap} per dag. Hij leest elke wijziging terug uit de ketel en zet hem terug als de ketel hem niet overneemt. Je kunt dit hier altijd weer uitzetten.',
  'I understand: I watch the boiler after a change': 'Ik begrijp het: ik kijk na een wijziging naar de ketel',
  'Allow': 'Toestaan',
  'Stop the E32 changing boiler settings': 'De E32 geen ketelinstellingen meer laten wijzigen',
  'From now on the E32 changes no boiler setting. A change you are watching is put back first. Settings you kept earlier stay as they are on the boiler.': 'Vanaf nu wijzigt de E32 geen ketelinstelling meer. Een wijziging waar je naar kijkt wordt eerst teruggezet. Instellingen die je eerder behield, blijven zoals ze op de ketel staan.',
  'Change {setting}': '{setting} wijzigen',
  'Now: {current}. You can choose {range}.': 'Nu: {current}. Je kunt kiezen: {range}.',
  'New value': 'Nieuwe waarde',
  'Change': 'Wijzigen',
  'Changed by the E32': 'Gewijzigd door de E32',
  'Being changed': 'Wordt gewijzigd',
  'Really switch it off?': 'Echt uitzetten?',
  'This really switches {what} off on the boiler. While you watch, it stays off for up to 15 minutes; if you keep the change, it stays off until you switch it on again.': 'Dit zet {what} echt uit op de ketel. Terwijl je kijkt, blijft het tot 15 minuten uit; behoud je de wijziging, dan blijft het uit tot je het weer aanzet.',
  'the heating: radiators and floor get no heat': 'de verwarming: radiatoren en vloer krijgen geen warmte',
  'the hot water: the taps stay cold': 'het warme water: de kranen blijven koud',
  'Switch it off': 'Uitzetten',
  'Watch your boiler': 'Kijk naar je ketel',
  'Watch your boiler for up to 15 minutes. {setting} is now {value} (it was {before}); the boiler read it back.': 'Kijk tot 15 minuten naar je ketel. {setting} is nu {value} (het was {before}); de ketel las het terug.',
  'Keep the new value, or put it back? If you choose Done, the E32 puts it back by itself at {until}, 15 minutes after the change.': 'De nieuwe waarde behouden, of terugzetten? Kies je Klaar, dan zet de E32 hem om {until} vanzelf terug, 15 minuten na de wijziging.',
  'Keep the new value': 'De nieuwe waarde behouden',
  'Put it back': 'Terugzetten',
  'Done (the E32 puts it back after 15 minutes)': 'Klaar (de E32 zet hem na 15 minuten terug)',
  'The change you are watching now': 'De wijziging waar je nu naar kijkt',
  'Advanced (installer settings)': 'Geavanceerd (installateursinstellingen)',
  '**At your own risk.** These are the settings an installer sets: burner power, switching margins, the pump and hot water details. A wrong value can waste gas, wear the boiler or stop heating or hot water. Change one only if you know what it does on your boiler, for example from its manual.': '**Op eigen risico.** Dit zijn de instellingen die een installateur instelt: brandervermogen, schakelmarges, de pomp en details van het warme water. Een verkeerde waarde kan gas verspillen, de ketel slijten of verwarming of warm water laten uitvallen. Wijzig er alleen een als je weet wat hij op je ketel doet, bijvoorbeeld uit de handleiding.',
  'Here the everyday settings also offer the boiler\'s whole range.': 'Hier bieden ook de gewone instellingen het hele bereik van de ketel.',
  'I change this at my own risk': 'Ik wijzig dit op eigen risico',
  'Advanced open, {n} min left': 'Geavanceerd open, nog {n} min',
  'Close': 'Sluiten',
  'Cancel': 'Annuleren',
  'Could not put it back: check the boiler': 'Terugzetten niet bevestigd: controleer de ketel',
  'Boiler checked': 'Ketel gecontroleerd',
  'The E32 may now change boiler settings.': 'De E32 mag nu ketelinstellingen wijzigen.',
  'The E32 no longer changes boiler settings.': 'De E32 wijzigt geen ketelinstellingen meer.',
  'Saved: {setting} is now {value}; the boiler read it back.': 'Opgeslagen: {setting} is nu {value}; de ketel las het terug.',
  'Kept: {setting} stays at {value}.': 'Behouden: {setting} blijft {value}.',
  'Put back: {setting} is {before} again.': 'Teruggezet: {setting} is weer {before}.',
  'Written, but the boiler did not take it: {setting} stays at {before}.': 'Geschreven, maar de ketel nam het niet over: {setting} blijft {before}.',
  'The boiler refused it: {setting} stays at {before}.': 'De ketel weigerde het: {setting} blijft {before}.',
  'The boiler went back to {before} by itself: {setting} was not kept.': 'De ketel ging zelf terug naar {before}: {setting} is niet behouden.',
  'Not started: nothing was changed on the boiler.': 'Niet gestart: er is niets gewijzigd op de ketel.',
  'Put back: the boiler did not confirm {value}, so the E32 set {setting} back to {before}.': 'Teruggezet: de ketel bevestigde {value} niet, dus de E32 zette {setting} terug op {before}.',
  'The E32 is still busy with {setting}. Look at Boiler settings again in a minute.': 'De E32 is nog bezig met {setting}. Kijk over een minuut weer bij Ketelinstellingen.',
  'Nothing changed: {setting} is already {value}.': 'Niets veranderd: {setting} is al {value}.',
  'Could not put it back: check the boiler. {setting} should be {before} again, but the boiler did not confirm it. Look at it on the boiler; Settings → Repairs says what to do next.': 'Terugzetten niet bevestigd: controleer de ketel. {setting} hoort weer {before} te zijn, maar de ketel bevestigde het niet. Kijk het na op de ketel; Instellingen → Reparaties zegt wat je daarna doet.'}};
const ERRORS = {
 // Boiler settings (Configure's options.error and options.abort, word for word).
 boiler_setting_unavailable: 'This E32 cannot change boiler settings.',
 boiler_settings_confirm: 'Tick the box to allow it.',
 boiler_settings_own_risk: 'Tick the box to go on at your own risk.',
 boiler_setting_unknown: 'Choose a setting from the list.',
 boiler_setting_out_of_range: 'The boiler does not accept this value: choose one in the range shown.',
 boiler_setting_above_maximum: 'This is above the highest water temperature of your room plan: raise that first (Water temperature limits).',
 boiler_setting_advanced: 'This value is outside the everyday range: use Advanced (installer settings).',
 boiler_setting_writes_off: 'Changing boiler settings is off: choose “Allow the E32 to change boiler settings” first.',
 boiler_setting_not_now: 'The E32 cannot change boiler settings right now: the boiler test, a reading or an update is busy, or the boiler has not answered yet. Try again later.',
 boiler_setting_restarting: 'The E32 is about to restart or update; try again in a minute.',
 boiler_setting_unsupported: 'Your boiler does not support this setting.',
 boiler_setting_check_boiler: 'A setting could not be put back: check the boiler and confirm it under Settings → Repairs first.',
 boiler_setting_too_soon: 'Wait half a minute before changing this setting again.',
 boiler_setting_daily_limit: 'The E32 changes at most 12 boiler settings a day. Try again tomorrow.',
 boiler_setting_busy: 'The E32 is busy with another boiler setting change. Try again in a few minutes.',
 boiler_setting_store_failed: 'The E32 could not store this. Try again.',
 boiler_setting_refused: 'The E32 refused the change ({error}).',
 boiler_setting_switch_off: 'Really switch it off? This really switches {what} off on the boiler.'};
const fmt = (lang, v) => (typeof v === 'number' ? v.toLocaleString(lang) : String(v ?? ''));
// A sentence whose placeholder the answer left out reads without it ("… reached. Nothing …", not "({error})").
const clean = text => String(text).replace(/ ?\(\{\w+\}\)/g, '');
// "**off**: the E32 …" with the bold part bold.
const rich = (h, text) => String(text).split('**').map((part, i) => (i % 2 ? h('strong', {text: part}) : part));
const paragraphs = (h, texts) => h('div', {class: 'ht-text'}, ...texts.map(text => h('p', {}, ...rich(h, text))));
// Boiler settings by their key, in Configure's words (selector.boiler_settings_text), so they read in the viewer's language;
// a setting this module does not know keeps the model's own words (Home Assistant's language).
const SETTINGS = {heatingactivated: 'Heating on the boiler', heatingtemp: 'Boiler maximum', burnmaxpower: 'Maximum burner power',
 boilhystoff: 'Switching margin off (hysteresis)', boilhyston: 'Switching margin on (hysteresis)', burnminperiod: 'Burner rest between starts',
 pumpdelay: 'Pump run-on', pumpmodmax: 'Highest pump speed', pumpmodmin: 'Lowest pump speed', pumpmode: 'Pump mode',
 'dhw.activated': 'Hot water on the boiler', 'dhw.seltemp': 'Selected hot water temperature', 'dhw.hyston': 'Hot water switching margin (hysteresis)',
 'dhw.chargeoptimization': 'Hot water charge optimisation', 'dhw.flowtempoffset': 'Extra water temperature for hot water',
 'dhw.circpump': 'Hot water circulation pump', 'dhw.circmode': 'Hot water circulation times', 'dhw.disinfectiontemp': 'Hot water disinfection temperature',
 'dhw.comfort': 'Hot water comfort'};
const CHOICES = {'dhw.comfort': ['Hot: always ready', 'Eco: saves gas', 'Intelligent: learns when you use it'],
 pumpmode: ['Follows the heat demand', 'Fixed pressure, level {n}'], 'dhw.circmode': ['{n} × 3 minutes an hour', 'Always on']};
const VERIFIED = {verified: 'Verified on this boiler', unverified: 'Not yet verified: try it while you watch', unsupported: 'Not supported by this boiler'};
const HOW = {verified: 'Verified on your boiler: the E32 writes it at once and reads it back.',
 watched: 'Not yet verified on your boiler. After the change, watch the boiler for up to 15 minutes, then keep the new value or put it back. If you do neither, the E32 puts it back by itself.'};
const STATES = {off: '**off**: the E32 writes nothing to the boiler.', on: '**on**: {used} of {cap} changes used today.',
 busy: 'a change of {setting} is running.', blocked: '**blocked**: a setting could not be put back. Check the boiler (Settings → Repairs).',
 not_now: 'on, but not possible right now (the boiler test, a reading or an update is busy).', unavailable: 'not possible on this E32.'};
const OFF = {off_heating: 'the heating: radiators and floor get no heat', off_dhw: 'the hot water: the taps stay cold'};
// The longer texts of Configure's steps, paragraph by paragraph (the "Submit …" lines of a form do not belong here).
const STEPS = {
 allow: ['Boiler settings stay in the boiler, also after a restart of the boiler or the E32. A wrong setting can leave the house cold, make the hot water too hot or let the burner switch on and off too often.',
  'The E32 changes a setting only when you ask, one at a time and at most {cap} a day. It reads every change back from the boiler and puts it back when the boiler does not take it. You can switch this off here at any time.'],
 stop: ['From now on the E32 changes no boiler setting. A change you are watching is put back first. Settings you kept earlier stay as they are on the boiler.'],
 off: ['This really switches {what} off on the boiler. While you watch, it stays off for up to 15 minutes; if you keep the change, it stays off until you switch it on again.'],
 watch: ['Watch your boiler for up to 15 minutes. {setting} is now {value} (it was {before}); the boiler read it back.',
  'Keep the new value, or put it back? If you choose Done, the E32 puts it back by itself at {until}, 15 minutes after the change.'],
 advanced: ['**At your own risk.** These are the settings an installer sets: burner power, switching margins, the pump and hot water details. A wrong value can waste gas, wear the boiler or stop heating or hot water. Change one only if you know what it does on your boiler, for example from its manual.',
  'Here the everyday settings also offer the boiler\'s whole range.']};
// What a change came to (strings.json options.abort, the answers' `result`).
const RESULTS = {boiler_settings_allowed: 'The E32 may now change boiler settings.', boiler_settings_stopped: 'The E32 no longer changes boiler settings.',
 boiler_setting_saved: 'Saved: {setting} is now {value}; the boiler read it back.', boiler_setting_kept: 'Kept: {setting} stays at {value}.',
 boiler_setting_put_back: 'Put back: {setting} is {before} again.',
 boiler_setting_not_taken: 'Written, but the boiler did not take it: {setting} stays at {before}.',
 boiler_setting_rejected: 'The boiler refused it: {setting} stays at {before}.',
 boiler_setting_restored: 'The boiler went back to {before} by itself: {setting} was not kept.',
 boiler_setting_not_started: 'Not started: nothing was changed on the boiler.',
 boiler_setting_reverted: 'Put back: the boiler did not confirm {value}, so the E32 set {setting} back to {before}.',
 boiler_setting_pending: 'The E32 is still busy with {setting}. Look at Boiler settings again in a minute.',
 boiler_setting_unchanged: 'Nothing changed: {setting} is already {value}.',
 boiler_setting_failed: 'Could not put it back: check the boiler. {setting} should be {before} again, but the boiler did not confirm it. Look at it on the boiler; Settings → Repairs says what to do next.'};
const stateTone = {off: 'rest', on: 'ok', busy: 'accent', blocked: 'attention', not_now: 'rest', unavailable: 'rest'};
const resultTone = {boiler_setting_saved: 'success', boiler_setting_kept: 'success', boiler_setting_put_back: 'success', boiler_setting_unchanged: 'info',
 boiler_settings_allowed: 'success', boiler_settings_stopped: 'info', boiler_setting_failed: 'error'};
/* ---- Boiler settings: allow, change, watch, put back, Advanced and stop; each step an action (settings_heating.ACTIONS) ---- */
// A setting's value in the viewer's words: On/Off, a choice, or the figure with its unit.
function valueText(ctx, s, value) {
 const {t, kit, lang} = ctx;
 if (value == null || value === '') return t('not read yet');
 if (!SETTINGS[s.key]) return s.choices?.find(c => c.value === value)?.label ?? (value === s.current ? s.current_text : String(value));
 if (s.kind === 'switch') return t(value ? 'On' : 'Off');
 if (s.key === 'dhw.comfort') return CHOICES[s.key][value] ? t(CHOICES[s.key][value]) : String(value);
 if (s.key === 'pumpmode') return value === 0 ? t(CHOICES.pumpmode[0]) : t(CHOICES.pumpmode[1], {n: value});
 if (s.key === 'dhw.circmode') return value === 7 ? t(CHOICES['dhw.circmode'][1]) : t(CHOICES['dhw.circmode'][0], {n: value});
 return kit.together(`${kit.number(value, lang, 0)} ${s.unit || ''}`.trim());
}
const nameOf = (ctx, s) => (SETTINGS[s.key] ? ctx.t(SETTINGS[s.key]) : s.name || s.key);
// The sentence of an answer's result with its setting and values in the viewer's words (else the answer's own words).
function resultText(ctx, model, answer) {
 const sentence = RESULTS[answer?.result];
 if (!sentence) return '';
 const s = model.settings?.find(x => x.key === answer.setting);
 const words = s ? {setting: nameOf(ctx, s), value: valueText(ctx, s, answer.value), before: valueText(ctx, s, answer.before)} : answer.placeholders || {};
 return ctx.t(sentence, words);
}

// A dialog over the screen (the core's dialog look): a title, paragraphs or fields, buttons; one at a time per screen.
function sheet(host, kit, {title, body, buttons, name}) {
 const {h} = kit, id = 'ht-dialog-' + (++sheet.seq);
 const el = h('dialog', {class: 'confirm ht-dialog', 'aria-labelledby': id, 'data-dialog': name});
 const head = h('h3', {id}), content = h('div', {class: 'ht-dialog-body'}), error = h('p', {class: 'error', role: 'alert', hidden: true}), row = h('div', {class: 'actions'});
 let busy = false;
 const api = {
  el,
  set({title: t2, body: b2 = [], buttons: list = []}) {
   head.textContent = t2; content.replaceChildren(...b2.filter(Boolean)); api.error('');
   row.replaceChildren(...list.map(([text, kind, fn, attrs = {}]) => kit.button(text, async () => {
    if (busy) return;
    api.busy(true);
    try { await fn(api); } finally { api.busy(false); }
   }, kind, attrs)));
  },
  error(text) { error.textContent = text || ''; error.hidden = !text; },
  busy(on) { busy = on; el.setAttribute('aria-busy', String(on)); for (const b of row.querySelectorAll('button')) b.disabled = on; },
  close() { if (el.open) el.close(); el.remove(); api.closed = true; }
 };
 el.addEventListener('cancel', e => { e.preventDefault(); if (!busy) api.close(); });
 el.append(head, content, error, row);
 api.set({title, body, buttons});
 host.append(el);
 try { el.showModal(); } catch (e) { el.setAttribute('open', ''); }
 return api;
}
sheet.seq = 0;
// A question with Configure's paragraphs; resolves true for the action.
const ask = (host, ctx, {title, texts, confirm, name}) => new Promise(resolve => {
 const {kit, t} = ctx;
 const d = sheet(host, kit, {title, name, body: [paragraphs(kit.h, texts)], buttons: [
  [t('Cancel'), 'text', () => { d.close(); resolve(false); }, {'data-cancel': ''}],
  [confirm, 'filled', () => { d.close(); resolve(true); }, {'data-confirm': ''}]]});
 d.el.addEventListener('close', () => resolve(false));
 d.el.querySelector('[data-cancel]')?.focus();
});

// The screen keeps its own fresh model after each action (one read of the E32, never a loop), per model the core loaded.
const boilerPages = new WeakMap();
function boilerSettings(ctx, host) {
 const {kit, t, lang} = ctx, {h} = kit;
 const page = boilerPages.get(ctx.model) || {model: ctx.model, notice: null};
 boilerPages.set(ctx.model, page);
 const box = h('div', {class: 'ht-boiler'});
 const reread = async () => {
  try { page.model = (await ctx.hass.callWS({type: 'open_thermostat/settings/get', entry_id: ctx.entry_id, section: 'heating', item: 'boiler'})).model; }
  catch (err) { page.notice = ['error', clean(ctx.errorText(err?.code || 'unknown', err?.translation_placeholders?.placeholders || {}))]; }
  draw();
 };
 const say = (tone, text) => { page.notice = text ? [tone, text] : null; };
 const failed = err => clean(err?.text || ctx.errorText(err?.code || 'unknown', err?.placeholders || {}));
 // An action of the screen itself (not in a dialog): its button waits, a refusal shows on top.
 const run = (button, name, values, after) => async () => {
  button.disabled = true;
  try { const answer = await ctx.action(name, values); say(resultTone[answer?.result] || 'info', RESULTS[answer?.result] ? t(RESULTS[answer.result]) : ''); after?.(answer); await reread(); }
  catch (err) { say('error', failed(err)); draw(); }
 };

 function draw() {
  const m = page.model, parts = [];
  if (!m.supported) {
   box.replaceChildren(kit.card({}, kit.empty({icon: 'wrench', text: t(sectionErrors[m.reason] || ERRORS.boiler_setting_unavailable)})));
   return;
  }
  const busy = m.settings.find(s => s.pending);
  const line = t('Changing boiler settings: {state}', {state: t(STATES[m.state] || STATES.off, {used: m.writes_today, cap: m.daily_cap,
   setting: busy ? nameOf(ctx, busy) : t('Boiler settings')})});
  parts.push(h('div', {class: 'ht-status', 'data-boiler-state': m.state || ''}, h('p', {class: 'ot-status', 'data-tone': stateTone[m.state] || 'rest', role: 'status'},
   h('span', {class: 'ot-dot', 'aria-hidden': 'true'}), h('span', {}, ...rich(h, kit.together(line))))));
  if (page.notice?.[1]) parts.push(kit.notice(page.notice[1], page.notice[0], ...[]));
  if (m.state === 'blocked') parts.push(blocked(m));
  // Not allowed: the allow card, and under it what the boiler holds now (read only: nothing to press, no labels).
  if (!m.allowed) parts.push(allowCard(m), h('div', {class: 'card list ht-settings ht-readonly', 'data-group': 'readonly'},
   ...m.settings.filter(s => !s.advanced).map(s => h('div', {class: 'row', 'data-setting': s.key},
    h('span', {class: 'row-text'}, h('span', {class: 'row-label', text: nameOf(ctx, s)})), h('span', {class: 'row-value', text: valueText(ctx, s, s.current)})))));
  else {
   if (m.watch) parts.push(watchCard(m));
   parts.push(h('div', {class: 'card list ht-settings', 'data-group': 'everyday'}, ...m.settings.filter(s => !s.advanced).map(s => settingRow(m, s))));
   parts.push(advancedCard(m));
   const stop = kit.button(t('Stop the E32 changing boiler settings'), null, 'text', {'data-stop': '', disabled: ctx.readOnly});
   stop.addEventListener('click', async () => {
    if (await ask(host, ctx, {name: 'stop', title: t('Stop the E32 changing boiler settings'), texts: STEPS.stop.map(x => t(x)), confirm: t('Stop the E32 changing boiler settings')})) run(stop, 'boiler_stop', undefined)();
   });
   parts.push(h('div', {class: 'ht-stop'}, stop));
  }
  box.replaceChildren(...parts);
 }
 function allowCard(m) {
  const tick = h('input', {type: 'checkbox', 'data-fk': 'confirm', disabled: ctx.readOnly}), error = h('p', {class: 'error', role: 'alert', hidden: true});
  tick.addEventListener('change', () => { if (tick.checked) error.hidden = true; });
  const allow = kit.button(t('Allow'), null, 'filled', {'data-allow': '', disabled: ctx.readOnly});
  allow.addEventListener('click', () => {
   if (!tick.checked) { error.textContent = t(ERRORS.boiler_settings_confirm); error.hidden = false; tick.focus(); return; }
   run(allow, 'boiler_allow', {allow: true, confirm: true})();
  });
  return kit.card({title: t('Allow the E32 to change boiler settings'), icon: 'alert', cls: 'ht-allow', data: {group: 'allow'}},
   paragraphs(h, STEPS.allow.map(x => t(x, {cap: m.daily_cap}))), h('label', {class: 'ht-tick'}, tick, h('span', {text: t('I understand: I watch the boiler after a change')})), error, allow);
 }
 function blocked(m) {
  const bad = m.settings.filter(s => s.last_result === 'failed');
  const checked = kit.button(t('Boiler checked'), null, 'outlined', {'data-checked': '', disabled: ctx.readOnly});
  checked.addEventListener('click', run(checked, 'boiler_checked', {ok: true}));
  return kit.card({title: t('Check the boiler'), icon: 'alert', data: {group: 'blocked'}},
   ...bad.map(s => h('p', {class: 'help', text: `${nameOf(ctx, s)}: ${t('Could not put it back: check the boiler')}`})), h('div', {class: 'ht-actions'}, checked));
 }
 function watchCard(m) {
  const w = m.watch, s = m.settings.find(x => x.key === w.setting) || {key: w.setting, name: w.name};
  const open = kit.button(t('Watch your boiler'), () => watchDialog({setting: w.setting}, true), 'filled', {'data-watch-open': '', disabled: ctx.readOnly});
  return kit.card({title: t('The change you are watching now'), icon: 'clock', summary: `${nameOf(ctx, s)}: ${valueText(ctx, s, w.value)}`, data: {group: 'watch'}}, open);
 }
 function settingRow(m, s, advanced = m.advanced_unlocked) {
  const lines = [t(VERIFIED[s.verification] || s.verification_text || '')];
  const el = kit.row({label: nameOf(ctx, s), summary: lines, value: valueText(ctx, s, s.current), disabled: !s.changeable, data: {setting: s.key},
   onClick: () => changeDialog(m, s, advanced)});
  const label = el.querySelector('.row-label');
  if (s.pending) label.append(kit.chip(t('Being changed'), 'accent'));
  else if (s.changed_by_e32) label.append(kit.chip(t('Changed by the E32'), 'rest'));
  if (!s.changeable || ctx.readOnly) el.disabled = true;
  return el;
 }
 function advancedCard(m) {
  if (!m.advanced_unlocked) {
   const row = kit.row({label: t('Advanced (installer settings)'), summary: [t('I change this at my own risk')], icon: 'wrench', data: {advanced: 'open'}, onClick: async () => {
    if (await ask(host, ctx, {name: 'advanced', title: t('Advanced (installer settings)'), texts: STEPS.advanced.map(x => t(x)), confirm: t('I change this at my own risk')}))
     run(row, 'boiler_advanced', {confirm: true})();
   }});
   if (ctx.readOnly) row.disabled = true;
   return h('div', {class: 'card list ht-advanced'}, row);
  }
  const close = kit.button(t('Close'), null, 'text', {'data-advanced-close': '', disabled: ctx.readOnly});
  close.addEventListener('click', run(close, 'boiler_advanced', {confirm: false}));
  const until = Date.parse(m.advanced_until || '');
  const left = () => Math.max(0, Math.ceil((until - Date.now()) / 60000));
  const card = kit.card({title: t('Advanced (installer settings)'), icon: 'wrench', data: {group: 'advanced'},
   summary: Number.isFinite(until) ? t('Advanced open, {n} min left', {n: left()}) : null},
   h('div', {class: 'card list ht-settings'}, ...m.settings.filter(s => s.advanced).map(s => settingRow(m, s, true))));
  card.querySelector('.ot-card-head')?.append(close);
  // The minutes left, once a quarter of a minute; at the end the screen closes Advanced as the backend does.
  if (Number.isFinite(until)) {
   const timer = setInterval(() => {
    const summary = card.querySelector('.ot-card-summary');
    if (!card.isConnected) { clearInterval(timer); return; }
    if (left() <= 0) { clearInterval(timer); page.model = {...page.model, advanced_unlocked: false, advanced_until: null}; draw(); return; }
    if (summary) summary.textContent = kit.together(t('Advanced open, {n} min left', {n: left()}));
   }, 15000);
  }
  return card;
 }

 // Change one setting: its allowed values (a segmented control for up to four, else a list or a stepper), the question
 // before heating or hot water goes off, then boiler_write; a setting not yet verified continues in the watch dialog.
 function changeDialog(m, s, advanced) {
  if (!s.changeable || ctx.readOnly) return;
  const range = advanced ? s.allowed_advanced : s.allowed;
  let value = s.current, field;
  if (s.kind === 'number') {
   field = kit.fields.stepper({key: 'boiler:' + s.key, hass: ctx.hass, label: t('New value'), unit: s.unit || '', step: range.step || 1, min: range.min, max: range.max,
    value: s.current ?? range.min, onChange: v => { value = v; }});
   value = s.current ?? range.min;
  } else {
   const options = (Array.isArray(range) ? range : []).map(v => {
    const text = valueText(ctx, s, v);
    return {value: v, label: s.key === 'dhw.comfort' ? text.split(':')[0] : text, help: s.key === 'dhw.comfort' ? text : null};
   });
   field = options.length <= 4
    ? kit.fields.segmented({key: 'boiler:' + s.key, hass: ctx.hass, label: t('New value'), options, value: s.current, onChange: v => { value = v; }})
    : kit.fields.select({key: 'boiler:' + s.key, hass: ctx.hass, label: t('New value'), options: options.map(o => ({...o, value: String(o.value)})),
     value: s.current == null ? '' : String(s.current), onChange: v => { value = Number(v); }});
  }
  const shownRange = s.kind === 'number' ? t('{low} to {high}', {low: valueText(ctx, s, range.min), high: valueText(ctx, s, range.max)}) : t('one of the choices below');
  const intro = paragraphs(h, [t('Now: {current}. You can choose {range}.', {current: valueText(ctx, s, s.current), range: shownRange}),
   t(s.verification === 'verified' ? HOW.verified : HOW.watched)]);
  const d = sheet(host, kit, {name: 'change', title: t('Change {setting}', {setting: nameOf(ctx, s)}), body: [intro, field.el], buttons: [
   [t('Cancel'), 'text', () => d.close(), {'data-cancel': ''}],
   [t('Change'), 'filled', () => write(false), {'data-write': ''}]]});
  field.focus?.();
  const write = async confirm => {
   if (value == null || Number.isNaN(value)) { field.setError?.(t(ERRORS.boiler_setting_out_of_range)); return; }
   if (!confirm && s.switch_off_question && value === 0) {
    if (await ask(host, ctx, {name: 'switch-off', title: t('Really switch it off?'), texts: [t(STEPS.off[0], {what: t(OFF[s.switch_off_question])})], confirm: t('Switch it off')})) await write(true);
    return;
   }
   let answer;
   try { answer = await ctx.action('boiler_write', {setting: s.key, value, ...(advanced ? {advanced: true} : {}), ...(confirm ? {confirm: true} : {})}); }
   catch (err) {
    // The backend asks too (a model that did not know the question yet): the same question, then again with its answer.
    if (err?.code === 'boiler_setting_switch_off' && !confirm) {
     const what = OFF[err.placeholders?.what_key] ? t(OFF[err.placeholders.what_key]) : err.placeholders?.what || '';
     if (await ask(host, ctx, {name: 'switch-off', title: t('Really switch it off?'), texts: [t(STEPS.off[0], {what})], confirm: t('Switch it off')})) await write(true);
     return;
    }
    if (err?.field === 'value') field.setError?.(failed(err)); else d.error(failed(err));
    return;
   }
   d.close();
   if (answer?.watch) { say(null, ''); watchDialog(answer.watch, false); }
   else say(resultTone[answer?.result] || 'warning', resultText(ctx, page.model, answer));
   await reread();
  };
 }

 // "Watch your boiler": opened after a change that needs watching (its answer already says what), or from the screen
 // (then one boiler_watch, never a loop); keep, put back, or Done (the E32 puts it back at the end of the window).
 async function watchDialog(watch, call) {
  const d = sheet(host, kit, {name: 'watch', title: t('Watch your boiler'), body: [kit.skeleton('rows', 1)], buttons: []});
  let state = 'watching', answer = null;
  if (call) {
   try { answer = await ctx.action('boiler_watch', {setting: watch.setting}); state = answer.state; watch = answer.watch || watch; }
   catch (err) { d.set({title: t('Watch your boiler'), body: [], buttons: [[t('Close'), 'filled', () => d.close(), {'data-close': ''}]]}); d.error(failed(err)); return; }
  }
  const m = page.model, s = m.settings.find(x => x.key === watch.setting) || {key: watch.setting, name: watch.name};
  const closeOnly = text => d.set({title: t('Watch your boiler'), body: [paragraphs(h, [text])], buttons: [[t('Close'), 'filled', async () => { d.close(); await reread(); }, {'data-close': ''}]]});
  if (state === 'writing') return closeOnly(t(RESULTS.boiler_setting_pending, {setting: nameOf(ctx, s)}));
  if (state === 'elsewhere') {
   const other = m.settings.find(x => x.key === answer?.setting) || s;
   return closeOnly(kit.together(t('Changing boiler settings: {state}', {state: t(STATES.busy, {setting: nameOf(ctx, other)})})));
  }
  if (state === 'ended') { if (resultText(ctx, m, answer)) return closeOnly(resultText(ctx, m, answer)); d.close(); return reread(); }
  const done = async (name, values) => {
   let result;
   try { result = await ctx.action(name, values); }
   catch (err) { d.error(failed(err)); return; }
   d.close();
   if (name === 'boiler_checked' && values.ok === false && result?.done !== false) return;  // Done: the watch goes on
   say(resultTone[result?.result] || 'warning', resultText(ctx, m, result));
   await reread();
  };
  d.set({title: t('Watch your boiler'), body: [paragraphs(h, STEPS.watch.map(x => t(x, {setting: nameOf(ctx, s), value: valueText(ctx, s, watch.value),
   before: valueText(ctx, s, watch.before), until: kit.time.moment(ctx.hass, watch.until)})))], buttons: [
   [t('Done (the E32 puts it back after 15 minutes)'), 'text', () => done('boiler_checked', {setting: watch.setting, ok: false}), {'data-later': ''}],
   [t('Put it back'), 'outlined', () => done('boiler_put_back', {setting: watch.setting}), {'data-put-back': ''}],
   [t('Keep the new value'), 'filled', () => done('boiler_checked', {setting: watch.setting, ok: true}), {'data-keep': ''}]]});
  d.el.querySelector('[data-keep]')?.focus();
 }

 draw();
 return box;
}

// Hand this part to its section (openthermostat-settings-heating.js), which registers once every part of it is here.
// The section's whole error table (its own and this part's), for a reason the model names (useErrors, at registration).
let sectionErrors = ERRORS;
const useErrors = all => { sectionErrors = all; };
(window.OpenThermostatSettingsParts ||= {})["heating_boiler"] = {boilerSettings, useErrors, texts: TEXTS, errors: ERRORS};
window.dispatchEvent(new CustomEvent('openthermostat-settings-part', {detail: "heating_boiler"}));
