/* The house banner (OpenThermostat 1.4.1, CONTRACT-1.4.1 §9; design docs/engineering/ZOMERSTAND-ONTWERP.nl.md §4, §5).
   At the top of every view of the OpenThermostat dashboard (dashboard.py: the view's header in a sections view, the
   first card of a stack in a panel view), shown only while the house is in a house-wide state that changes what every
   room does; empty (zero height) otherwise. 1.4.1 knows one such state: summer mode (the house mode select's state
   ``summer``). Then one grey line with the design's sentence and one text button, "Switch summer mode off", which asks
   first and then sets the house mode select back to the mode before summer (its attribute ``previous_mode`` when the
   integration gives it and the select offers it, else Automatic); the E32 restores what was planned around it.
   Config: {type: custom:openthermostat-house-banner, entity: select.<house mode>}. Words EN/NL/PL in TEXT; the
   house mode names are the integration's (the select's own translation), with these as the last resort. Tokens:
   CONTRACT §8 on the host; dark from hass.themes.darkMode, else the browser's colour scheme. Icons inline (no ha-icon). */
const TEXT = {
 en: {summer: 'Summer mode: the heating stays off until you switch this off; hot water and frost protection stay.',
  off: 'Switch summer mode off', ask: 'Switch summer mode off? The house mode becomes {mode}.', yes: 'Switch off', no: 'Cancel',
  failed: 'Summer mode could not be switched off: {reason}', modes: {auto: 'Automatic', home: 'At home', away: 'Away', holiday: 'Holiday'}},
 nl: {summer: 'Zomerstand: de verwarming staat uit tot je dit uitzet; warm water en vorstbeveiliging blijven.',
  off: 'Zomerstand uitzetten', ask: 'Zomerstand uitzetten? De huismodus wordt {mode}.', yes: 'Uitzetten', no: 'Annuleren',
  failed: 'Zomerstand uitzetten lukte niet: {reason}', modes: {auto: 'Automatisch', home: 'Thuis', away: 'Afwezig', holiday: 'Vakantie'}},
 pl: {summer: 'Tryb letni: ogrzewanie pozostaje wyłączone, dopóki tego nie wyłączysz; ciepła woda i ochrona przed mrozem działają.',
  off: 'Wyłącz tryb letni', ask: 'Wyłączyć tryb letni? Tryb domu: {mode}.', yes: 'Wyłącz', no: 'Anuluj',
  failed: 'Nie udało się wyłączyć trybu letniego: {reason}', modes: {auto: 'Automatycznie', home: 'W domu', away: 'Nieobecność', holiday: 'Urlop'}}};
// Material Design Icons (v7.4.47, Apache 2.0), inline.
const ICONS = {
 'white-balance-sunny': 'M3.55 19.09L4.96 20.5L6.76 18.71L5.34 17.29M12 6C8.69 6 6 8.69 6 12S8.69 18 12 18 18 15.31 18 12C18 8.68 15.31 6 12 6M20 13H23V11H20M17.24 18.71L19.04 20.5L20.45 19.09L18.66 17.29M20.45 5L19.04 3.6L17.24 5.39L18.66 6.81M13 1H11V4H13M6.76 5.39L4.96 3.6L3.55 5L5.34 6.81L6.76 5.39M1 13H4V11H1M13 20H11V23H13'};
const SVG = 'http://www.w3.org/2000/svg';
const svgIcon = (name, size) => {
 const s = document.createElementNS(SVG, 'svg'), p = document.createElementNS(SVG, 'path');
 for (const [k, v] of Object.entries({viewBox: '0 0 24 24', width: size, height: size, 'aria-hidden': 'true', focusable: 'false', 'data-icon': 'mdi:' + name}))
  s.setAttribute(k, v);
 p.setAttribute('d', ICONS[name]); p.setAttribute('fill', 'currentColor');
 s.append(p);
 return s;
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
color:var(--ot-fg);font-family:var(--paper-font-body1_-_font-family,Roboto,'Segoe UI',Arial,sans-serif)}
:host([data-theme="dark"]){--ot-heat-ink:#f0a060;--ot-heat-fill:rgba(240,160,96,.18);--ot-along-ink:#e6c35c;--ot-along-fill:rgba(230,195,92,.18);
--ot-water-ink:#7fb3f0;--ot-water-fill:rgba(127,179,240,.18);--ot-rest-ink:#b0b4ba;--ot-rest-fill:rgba(176,180,186,.18);
--ot-attention-ink:#f2857c;--ot-attention-fill:rgba(242,133,124,.18)}
:host(:not([data-kind])){display:none}
p{margin:0}svg{display:block;flex:none}
.banner{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ot-space) calc(var(--ot-space)*1.5);box-sizing:border-box;
padding:calc(var(--ot-space)*1.5) calc(var(--ot-space)*2);border-radius:var(--ot-radius);background:var(--ot-rest-fill);color:var(--ot-fg)}
.banner>svg{color:var(--ot-rest-ink)}
.words{flex:1 1 220px;min-width:0;font-size:var(--ot-text-m);line-height:var(--ot-line-m);overflow-wrap:anywhere}
.actions{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ot-space);margin-left:auto}
button{min-height:var(--ot-touch);padding:0 calc(var(--ot-space)*2);border-radius:var(--ot-radius);font:inherit;font-size:var(--ot-text-m);
font-weight:500;cursor:pointer;transition:background-color var(--ot-motion)}
button:focus-visible{outline:2px solid var(--ot-accent);outline-offset:2px}button:disabled{cursor:default;opacity:.6}
.text{border:0;background:none;color:var(--ot-link)}
.text:hover:not(:disabled){background:color-mix(in srgb,var(--ot-accent) 10%,transparent)}
.primary{border:0;background:var(--ot-fill);color:var(--ot-on-accent)}
.error{flex:1 1 100%;font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-attention-ink)}`;

const locale = hass => hass?.locale?.language || hass?.language || 'en';
const lang = hass => /^(nl|pl)\b/.exec(locale(hass))?.[1] || 'en';
const darkOf = hass => {
 if (typeof hass?.themes?.darkMode === 'boolean') return hass.themes.darkMode;
 try { return window.matchMedia('(prefers-color-scheme: dark)').matches; } catch (e) { return false; }
};

class OpenThermostatHouseBanner extends HTMLElement {
 constructor() { super(); this.attachShadow({mode: 'open'}); this._key = null; this._asking = false; this._busy = false; this._error = ''; }
 setConfig(config) {
  this._config = {entity: typeof config?.entity === 'string' && config.entity.startsWith('select.') ? config.entity : null};
  this._key = null;
  if (this._hass) this.render();
 }
 set hass(hass) {
  this._hass = hass;
  const st = this._config?.entity ? hass?.states?.[this._config.entity] : undefined;
  const key = [st, locale(hass), darkOf(hass)];
  if (this._key && key.every((v, i) => v === this._key[i])) return;
  // Summer mode ended (here or elsewhere): a question or an error left from it goes.
  if (st?.state !== 'summer') { this._asking = false; this._error = ''; this._busy = false; }
  this._key = key; this.render();
 }
 getCardSize() { return this.kind() ? 1 : 0; }
 getGridOptions() { return {columns: 'full'}; }
 t(key, values = {}) {
  return (TEXT[lang(this._hass)][key] ?? TEXT.en[key]).replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all);
 }
 // The house-wide state the banner shows, or null: 1.4.1 knows summer mode only.
 kind() {
  const st = this._config?.entity ? this._hass?.states?.[this._config.entity] : null;
  return st?.state === 'summer' ? 'summer' : null;
 }
 // The mode summer mode gives way to: the one before it when the select names it and offers it, else Automatic.
 previous() {
  const a = this._hass?.states?.[this._config.entity]?.attributes || {}, options = Array.isArray(a.options) ? a.options : null;
  const before = a.previous_mode;
  return typeof before === 'string' && before !== 'summer' && (!options || options.includes(before)) ? before : 'auto';
 }
 modeName(mode) {
  const st = this._hass?.states?.[this._config.entity];
  try { const text = this._hass?.formatEntityState?.(st, mode); if (typeof text === 'string' && text && text !== mode) return text; } catch (e) { /* older frontend */ }
  return TEXT[lang(this._hass)].modes[mode] || TEXT.en.modes[mode] || mode;
 }
 async switchOff() {
  if (this._busy) return;
  this._busy = true; this._error = ''; this.render();
  try {
   await this._hass.callService('select', 'select_option', {entity_id: this._config.entity, option: this.previous()});
   this._asking = false;
  } catch (e) {
   this._error = this.t('failed', {reason: e?.message || String(e)});
  }
  this._busy = false; this.render();
 }
 render() {
  const hass = this._hass, root = this.shadowRoot;
  if (!hass || !this._config) return;
  if (darkOf(hass)) this.setAttribute('data-theme', 'dark'); else this.removeAttribute('data-theme');
  const kind = this.kind(), focused = root.activeElement?.dataset?.action;
  const make = (tag, attrs = {}, text) => {
   const e = document.createElement(tag);
   for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
   if (text !== undefined) e.textContent = text;
   return e;
  };
  // Nothing house-wide: the host is not displayed (zero height), only its style stays.
  if (!kind) { this.removeAttribute('data-kind'); root.replaceChildren(make('style', {}, STYLE)); return; }
  this.setAttribute('data-kind', kind);
  const box = make('div', {class: 'banner', role: 'status', 'data-banner': kind}), actions = make('div', {class: 'actions'});
  const button = (action, style, words, run) => {
   const b = make('button', {type: 'button', class: style, 'data-action': action}, words);
   if (this._busy) b.disabled = true;
   b.addEventListener('click', run);
   actions.append(b);
   return b;
  };
  box.append(svgIcon('white-balance-sunny', 24));
  if (this._asking) {
   box.append(make('p', {class: 'words', 'data-question': ''}, this.t('ask', {mode: this.modeName(this.previous())})));
   button('cancel', 'text', this.t('no'), () => { this._asking = false; this._error = ''; this.render(); });
   button('confirm', 'primary', this.t('yes'), () => this.switchOff());
  } else {
   box.append(make('p', {class: 'words'}, this.t('summer')));
   button('ask', 'text', this.t('off'), () => { this._asking = true; this.render(); });
  }
  box.append(actions);
  if (this._error) box.append(make('p', {class: 'error', role: 'alert', 'data-error': ''}, this._error));
  root.replaceChildren(make('style', {}, STYLE), box);
  const again = root.querySelector(`[data-action="${this._asking ? (focused === 'confirm' ? 'confirm' : 'cancel') : 'ask'}"]`);
  if (focused && again) again.focus({preventScroll: true});
 }
}
// The same registry guard as the other OpenThermostat cards (a scoped-registry polyfill of another card may replace
// customElements later: define again whenever the registry in use lacks the element). Never throws.
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
ensureDefined('openthermostat-house-banner', OpenThermostatHouseBanner);
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === 'openthermostat-house-banner'))
 window.customCards.push({type: 'openthermostat-house-banner', name: 'OpenThermostat house banner',
  description: 'A line at the top of the dashboard while the house is in summer mode, with a button to switch it off.'});
