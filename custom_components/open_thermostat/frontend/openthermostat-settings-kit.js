/* The settings panel's component kit, version 2 (1.4.1): window.OpenThermostatSettingsKit, loaded by the panel core when the
   Settings tab opens. Design tokens, inline icons, elements, fields, the confirm dialog, time and number helpers (Home
   Assistant's language, time zone, time and number format), the section registry and routes. API:
   HA-INSTELPANEEL-FASE2.nl.md chapter 4 "zoals gebouwd"; 1.4.2: the unused fields days, date and time and routeOf are gone.
   Texts: TEXTS, English key (test/ha-settings-texts.test.cjs). */
const TEXTS = {
 nl: {
  'Search by name': 'Zoek op naam', 'No area': 'Geen gebied', 'Nothing found.': 'Niets gevonden.', 'Remove {name}': '{name} verwijderen',
  'Type to see more.': 'Typ om meer te zien.', 'Cancel': 'Annuleren', 'More': 'Meer uitleg', 'Less': 'Minder uitleg',
  'Day': 'Dag', 'Month': 'Maand', 'Year': 'Jaar', 'Time': 'Tijd',
  'Lower': 'Lager', 'Higher': 'Hoger', 'Enter a time such as {example}.': 'Vul een tijd in zoals {example}.',
  'Choose a moment': 'Kies een moment', 'No moment': 'Geen moment'}};
// Material Design Icons (Apache-2.0), inline.
const ICONS = {
 thermostat: "M16.95,16.95L14.83,14.83C15.55,14.1 16,13.1 16,12C16,11.26 15.79,10.57 15.43,10L17.6,7.81C18.5,9 19,10.43 19,12C19,13.93 18.22,15.68 16.95,16.95M12,5C13.57,5 15,5.5 16.19,6.4L14,8.56C13.43,8.21 12.74,8 12,8A4,4 0 0,0 8,12C8,13.1 8.45,14.1 9.17,14.83L7.05,16.95C5.78,15.68 5,13.93 5,12A7,7 0 0,1 12,5M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z",
 home: "M12 5.69L17 10.19V18H15V12H9V18H7V10.19L12 5.69M12 3L2 12H5V20H11V14H13V20H19V12H22",
 fire: "M17.66 11.2C17.43 10.9 17.15 10.64 16.89 10.38C16.22 9.78 15.46 9.35 14.82 8.72C13.33 7.26 13 4.85 13.95 3C13 3.23 12.17 3.75 11.46 4.32C8.87 6.4 7.85 10.07 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C6.87 12.33 6.69 10.28 7.45 8.64C5.78 10 4.87 12.3 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C18.86 17.66 19.5 15 18.56 12.72L18.43 12.46C18.22 12 17.66 11.2 17.66 11.2M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.78 14.43 12.46 13.77 12.33 13C12.21 12.26 12.23 11.63 12.5 10.94C12.69 11.32 12.89 11.7 13.13 12C13.9 13 15.11 13.44 15.37 14.8C15.41 14.94 15.43 15.08 15.43 15.23C15.46 16.05 15.1 16.95 14.5 17.5H14.5Z",
 devices: "M3 6H21V4H3C1.9 4 1 4.9 1 6V18C1 19.1 1.9 20 3 20H7V18H3V6M13 12H9V13.78C8.39 14.33 8 15.11 8 16C8 16.89 8.39 17.67 9 18.22V20H13V18.22C13.61 17.67 14 16.88 14 16S13.61 14.33 13 13.78V12M11 17.5C10.17 17.5 9.5 16.83 9.5 16S10.17 14.5 11 14.5 12.5 15.17 12.5 16 11.83 17.5 11 17.5M22 8H16C15.5 8 15 8.5 15 9V19C15 19.5 15.5 20 16 20H22C22.5 20 23 19.5 23 19V9C23 8.5 22.5 8 22 8M21 18H17V10H21V18Z",
 bell: "M10 21H14C14 22.1 13.1 23 12 23S10 22.1 10 21M21 19V20H3V19L5 17V11C5 7.9 7 5.2 10 4.3V4C10 2.9 10.9 2 12 2S14 2.9 14 4V4.3C17 5.2 19 7.9 19 11V17L21 19M17 11C17 8.2 14.8 6 12 6S7 8.2 7 11V18H17V11Z",
 flash: "M7,2V13H10V22L17,10H13L17,2H7Z",
 wrench: "M22.7,19L13.6,9.9C14.5,7.6 14,4.9 12.1,3C10.1,1 7.1,0.6 4.7,1.7L9,6L6,9L1.6,4.7C0.4,7.1 0.9,10.1 2.9,12.1C4.8,14 7.5,14.5 9.8,13.6L18.9,22.7C19.3,23.1 19.9,23.1 20.3,22.7L22.6,20.4C23.1,20 23.1,19.3 22.7,19Z",
 radiator: "M7.95,3L6.53,5.19L7.95,7.4H7.94L5.95,10.5L4.22,9.6L5.64,7.39L4.22,5.19L6.22,2.09L7.95,3M13.95,2.89L12.53,5.1L13.95,7.3L13.94,7.31L11.95,10.4L10.22,9.5L11.64,7.3L10.22,5.1L12.22,2L13.95,2.89M20,2.89L18.56,5.1L20,7.3V7.31L18,10.4L16.25,9.5L17.67,7.3L16.25,5.1L18.25,2L20,2.89M2,22V14A2,2 0 0,1 4,12H20A2,2 0 0,1 22,14V22H20V20H4V22H2M6,14A1,1 0 0,0 5,15V17A1,1 0 0,0 6,18A1,1 0 0,0 7,17V15A1,1 0 0,0 6,14M10,14A1,1 0 0,0 9,15V17A1,1 0 0,0 10,18A1,1 0 0,0 11,17V15A1,1 0 0,0 10,14M14,14A1,1 0 0,0 13,15V17A1,1 0 0,0 14,18A1,1 0 0,0 15,17V15A1,1 0 0,0 14,14M18,14A1,1 0 0,0 17,15V17A1,1 0 0,0 18,18A1,1 0 0,0 19,17V15A1,1 0 0,0 18,14Z",
 floor: "M19 17C20.21 17 22 16.2 22 14S20.21 11 19 11H17V9H19C21.2 9 22 7.21 22 6C22 3.8 20.21 3 19 3H17V2H16V3H8V2H7V3H2V5H7V7H5C3.79 7 2 7.8 2 10S3.79 13 5 13H7V15H5C3.79 15 2 15.8 2 18S3.79 21 5 21H7V22H8V21H16V22H17V21H22V19H17V17H19M19 13C19.45 13 20 13.19 20 14S19.45 15 19 15H17V13H19M16 11H8V9H16V11M19 5C19.45 5 20 5.2 20 6C20 6.45 19.81 7 19 7H17V5H19M8 5H16V7H8V5M5 11C4.55 11 4 10.81 4 10S4.55 9 5 9H7V11H5M8 13H16V15H8V13M5 19C4.55 19 4 18.81 4 18S4.55 17 5 17H7V19H5M16 19H8V17H16V19Z",
 door: "M12,3C10.89,3 10,3.89 10,5H3V19H2V21H22V19H21V5C21,3.89 20.11,3 19,3H12M12,5H19V19H12V5M5,11H7V13H5V11Z",
 window: "M21 20V2H3V20H1V23H23V20M19 4V11H17V4M5 4H7V11H5M5 20V13H7V20M9 20V4H15V20M17 20V13H19V20Z",
 bluetooth: "M14.88,16.29L13,18.17V14.41M13,5.83L14.88,7.71L13,9.58M17.71,7.71L12,2H11V9.58L6.41,5L5,6.41L10.59,12L5,17.58L6.41,19L11,14.41V22H12L17.71,16.29L13.41,12L17.71,7.71Z",
 account: "M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z",
 clock: "M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z",
 'chevron-right': "M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z",
 'chevron-left': "M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z",
 'chevron-down': "M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z",
 plus: "M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",
 close: "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",
 check: "M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z",
 alert: "M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",
 info: "M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",
 water: "M12,20A6,6 0 0,1 6,14C6,10 12,3.25 12,3.25C12,3.25 18,10 18,14A6,6 0 0,1 12,20Z",
 calendar: "M12 12H17V17H12V12M19 3H18V1H16V3H8V1H6V3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3M19 5V7H5V5H19M5 19V9H19V19H5Z",
 limits: "M13,9V15H16L12,19L8,15H11V9H8L12,5L16,9H13M4,2H20V4H4V2M4,20H20V22H4V20Z",
 thermometer: "M15 13V5A3 3 0 0 0 9 5V13A5 5 0 1 0 15 13M12 4A1 1 0 0 1 13 5V8H11V5A1 1 0 0 1 12 4Z",
};

const CATALOG = {nl: {...TEXTS.nl}};
const langOf = hass => {
 const l = String(hass?.locale?.language || hass?.language || 'en').slice(0, 2).toLowerCase();
 return l === 'nl' ? 'nl' : 'en';
};
const fill = (text, values = {}) => String(text).replace(/\{(\w+)\}/g, (all, k) => (k in values ? values[k] : all));
const translate = (lang, key, values) => fill((lang !== 'en' && CATALOG[lang]?.[key]) || key, values);
const addTexts = texts => { Object.assign(CATALOG.nl, texts?.nl || {}); };
// "16 °C" never breaks before the unit.
const together = text => String(text).replace(/ (°C|°F|%|kW|min|s|h)(?=$|[\s·,.;)])/g, ' $1');

// Time and date as Home Assistant says them (the cards' clock), in the zone its profile chooses: the server's (default) or
// this device's (locale.time_zone "local").
const clockLocale = hass => hass?.locale?.language || hass?.language || 'en';
const clockZone = hass => {
 const z = hass?.locale?.time_zone === 'local' ? null : hass?.config?.time_zone;
 if (typeof z !== 'string' || !z) return undefined;
 try { new Intl.DateTimeFormat('en', {timeZone: z}); return z; } catch (e) { return undefined; }
};
const hour12 = hass => {
 const chosen = ({'12': true, '24': false})[hass?.locale?.time_format];
 if (chosen !== undefined) return chosen;
 try { return /h1[12]/.test(new Intl.DateTimeFormat(clockLocale(hass), {hour: 'numeric'}).resolvedOptions().hourCycle); } catch (e) { return false; }
};
const clockOptions = hass => { const h12 = hour12(hass); return {hour: h12 ? 'numeric' : '2-digit', minute: '2-digit', hour12: h12, timeZone: clockZone(hass)}; };
const clockDay = (hass, ms) => {
 try {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {timeZone: clockZone(hass), year: 'numeric', month: 'numeric', day: 'numeric'})
   .formatToParts(new Date(ms)).map(({type, value}) => [type, Number(value)]));
  return Math.round(Date.UTC(p.year, p.month - 1, p.day) / 86400000);
 } catch (e) { return Math.floor(ms / 86400000); }
};
const noBreak = s => String(s).replace(/\s/g, ' ');
// "22:00" or "10:00 PM".
function formatTime(hass, hhmm) {
 const m = /^(\d{1,2}):(\d{2})/.exec(String(hhmm || ''));
 if (!m) return '';
 const d = new Date(2024, 0, 1, Number(m[1]), Number(m[2]));
 try { return noBreak(d.toLocaleTimeString(clockLocale(hass), {...clockOptions(hass), timeZone: undefined})); } catch (e) { return `${m[1].padStart(2, '0')}:${m[2]}`; }
}
// "14:30", "tomorrow 14:30", "Sat 19 Dec, 10:00".
function formatMoment(hass, value, now = Date.now()) {
 const ms = typeof value === 'number' ? value : typeof value === 'string' && value ? Date.parse(value) : NaN;
 if (!Number.isFinite(ms)) return '';
 const days = clockDay(hass, ms) - clockDay(hass, now);
 let time;
 try { time = new Date(ms).toLocaleTimeString(clockLocale(hass), clockOptions(hass)); } catch (e) { time = new Date(ms).toISOString().slice(11, 16); }
 if (days === 0) return noBreak(time);
 if (Math.abs(days) === 1) {
  try {
   // "tomorrow" in the panel's own language (English for a language it has no words for), as the sentence around it.
   const word = new Intl.RelativeTimeFormat(langOf(hass), {numeric: 'auto'}).format(days, 'day');
   return noBreak(word + ' ' + time);
  } catch (e) { /* older browser */ }
 }
 try { return new Date(ms).toLocaleString(clockLocale(hass), {weekday: 'short', day: 'numeric', month: 'short', ...clockOptions(hass)}); }
 catch (e) { return new Date(ms).toISOString().slice(0, 16).replace('T', ' '); }
}
// "Sat 19 Dec" (the year when not this one): a moment on its day in Home Assistant's zone, a plain date as it is.
function formatDate(hass, value) {
 const text = String(value || ''), plain = /^\d{4}-\d{2}-\d{2}$/.test(text);
 const ms = plain ? Date.parse(text + 'T12:00Z') : Date.parse(text), zone = plain ? 'UTC' : clockZone(hass);
 if (!Number.isFinite(ms)) return '';
 const year = y => { try { return new Intl.DateTimeFormat('en', {timeZone: zone, year: 'numeric'}).format(y); } catch (e) { return ''; } };
 try { return new Date(ms).toLocaleDateString(clockLocale(hass), {weekday: 'short', day: 'numeric', month: 'short', timeZone: zone,
  ...(year(new Date(ms)) !== year(new Date()) ? {year: 'numeric'} : {})}); } catch (e) { return text.slice(0, 10); }
}
// Monday first.
const weekdays = (hass, style = 'short') => [0, 1, 2, 3, 4, 5, 6].map(i => {
 try { return new Date(2024, 0, 1 + i).toLocaleDateString(clockLocale(hass), {weekday: style}).replace(/\.$/, ''); } catch (e) { return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i]; }
});
const months = hass => Array.from({length: 12}, (x, i) => {
 try { return new Date(2024, i, 1).toLocaleDateString(clockLocale(hass), {month: 'long'}); } catch (e) { return String(i + 1); }
});
// "2200", "10 pm" -> "HH:MM" or null.
function parseTime(text) {
 const m = /^\s*(\d{1,2})(?:[:.h ]?(\d{2}))?\s*([ap])?\.?\s*m?\.?\s*$/i.exec(String(text || ''));
 if (!m) return null;
 let hour = Number(m[1]);
 const minute = Number(m[2] || 0), half = m[3]?.toLowerCase();
 if (half) { if (hour < 1 || hour > 12) return null; hour = hour % 12 + (half === 'p' ? 12 : 0); }
 if (hour > 23 || minute > 59) return null;
 return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
}
// Numbers as Home Assistant's profile says (locale.number_format), given hass; a language alone keeps that language's.
const FORMATS = {comma_decimal: 'en-US', decimal_comma: 'de', space_comma: 'fr', system: undefined};
const numberLocale = where => (typeof where === 'object' && where ? (Object.hasOwn(FORMATS, where.locale?.number_format)
 ? FORMATS[where.locale.number_format] : clockLocale(where)) : where || 'en');
const number = (v, where, digits = 1, least = 0) => Number(v).toLocaleString(numberLocale(where), {maximumFractionDigits: Math.max(digits, least),
 minimumFractionDigits: least, ...(where?.locale?.number_format === 'none' ? {useGrouping: false} : {})});
const degrees = (v, unit, where, digits = 1) => (typeof v === 'number' && Number.isFinite(v) ? `${number(v, where, digits)} ${unit || '°C'}` : '');

let seq = 0;
const uid = p => `ot-${p}-${++seq}`;
const SVG = 'http://www.w3.org/2000/svg';
// h(tag, {class, text, on: {click}, props, ...attributes}, ...children)
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
// icon(name, {label, size}): decorative unless labelled.
function icon(name, {label, size = 24, cls = ''} = {}) {
 const svg = document.createElementNS(SVG, 'svg');
 svg.setAttribute('viewBox', '0 0 24 24'); svg.setAttribute('width', size); svg.setAttribute('height', size);
 svg.setAttribute('class', ('ot-icon ' + cls).trim()); svg.setAttribute('data-icon', name);
 if (label) { svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', label); } else svg.setAttribute('aria-hidden', 'true');
 svg.setAttribute('focusable', 'false');
 const path = document.createElementNS(SVG, 'path');
 path.setAttribute('d', ICONS[name] || ICONS.info); path.setAttribute('fill', 'currentColor');
 svg.append(path);
 return svg;
}
const TONE_ICON = {info: 'info', warning: 'alert', error: 'alert', success: 'check'};
const notice = (text, tone = 'info', ...more) => h('div', {class: 'notice ' + tone, role: tone === 'error' ? 'alert' : 'status'},
 icon(TONE_ICON[tone] || 'info', {cls: 'notice-icon'}), h('div', {class: 'notice-body'}, h('p', {text}), ...more));
const inlineError = text => h('p', {class: 'inline-error', role: 'alert'}, icon('alert', {size: 18}), h('span', {text}));
// Kinds: filled (the one primary), outlined (secondary), text (small), danger (remove, at the bottom).
function button(text, onClick, kind = 'text', attrs = {}) {
 const {icon: name, ...rest} = attrs || {};
 const el = h('button', {type: 'button', class: 'btn ' + kind, on: onClick ? {click: onClick} : null, ...rest});
 if (name) el.append(icon(name, {size: 20}), ...(text ? [h('span', {text})] : []));
 else if (text) el.textContent = text;
 return el;
}
const iconButton = (name, label, onClick, attrs = {}) => {
 const el = h('button', {type: 'button', class: 'btn icon', 'aria-label': label, title: label, on: {click: onClick}, ...attrs});
 el.append(icon(name, {size: 22}));
 return el;
};
const chip = (text, tone = 'rest', name) => h('span', {class: 'ot-chip', 'data-tone': tone}, name ? icon(name, {size: 16}) : null, h('span', {text}));

// A list row: icon, label, summary lines, value, chevron; a link (#...) or a button.
function row({label, summary = [], value, route, onClick, current, badge, disabled, data = {}, icon: name}) {
 const attrs = {class: 'row' + (disabled ? ' muted' : '') + (name ? ' with-icon' : ''), ...(current ? {'aria-current': 'page'} : {})};
 for (const [k, v] of Object.entries(data)) attrs['data-' + k] = v;
 const el = route ? h('a', {...attrs, href: route}) : h('button', {...attrs, type: 'button'});
 if (onClick) el.addEventListener('click', onClick);
 if (name) el.append(h('span', {class: 'row-icon'}, icon(name)));
 const text = h('span', {class: 'row-text'}, h('span', {class: 'row-label'}, label, badge ? h('span', {class: 'badge', text: badge}) : null));
 for (const line of [].concat(summary).filter(Boolean)) text.append(h('span', {class: 'row-line', text: together(line)}));
 el.append(text);
 if (value != null) el.append(h('span', {class: 'row-value', text: value}));
 el.append(h('span', {class: 'chevron'}, icon('chevron-right', {size: 20})));
 return el;
}

// The page frame: back link, title, one sentence; {el, body}.
function frame({title, subtitle, back, status}) {
 const head = h('header', {class: 'head'});
 if (back) head.append(h('a', {class: 'back', href: back.route, 'data-back': '', on: back.onClick ? {click: back.onClick} : null}, icon('chevron-left', {size: 20}), h('span', {text: back.label})));
 head.append(h('h2', {class: 'title', text: title, tabindex: '-1'}));
 if (subtitle) head.append(h('p', {class: 'subtitle', text: subtitle}));
 if (status) head.append(status);
 const body = h('div', {class: 'body'});
 return {el: h('section', {class: 'page'}, head, body), body};
}
function card({title, icon: name, summary, cls = '', data = {}} = {}, ...children) {
 const attrs = {class: ('ot-card ' + cls).trim()};
 for (const [k, v] of Object.entries(data)) attrs['data-' + k] = v;
 const el = h('section', attrs);
 if (title) el.append(h('header', {class: 'ot-card-head'}, name ? h('span', {class: 'ot-card-icon'}, icon(name)) : null,
  h('div', {class: 'ot-card-titles'}, h('h3', {class: 'ot-card-title', text: title}), summary ? h('p', {class: 'ot-card-summary', text: together(summary)}) : null)));
 el.append(...children.flat().filter(c => c != null && c !== false));
 return el;
}
// A collapsible section with its summary line; it opens itself around an invalid field.
function fold({key, title, icon: name, summary, open = false, onToggle, data = {}}, ...children) {
 const id = uid('fold'), body = h('div', {class: 'ot-fold-body', id: id + '-body', role: 'region', 'aria-labelledby': id + '-head'});
 body.append(...children.flat().filter(c => c != null && c !== false));
 if (body.querySelector('.field.invalid, .invalid')) open = true;
 const line = h('span', {class: 'ot-fold-summary', text: together(summary || '')});
 const head = h('button', {type: 'button', class: 'ot-fold-head', id: id + '-head', 'aria-controls': id + '-body', 'aria-expanded': String(!!open)},
  name ? h('span', {class: 'ot-fold-icon'}, icon(name)) : null,
  h('span', {class: 'ot-fold-titles'}, h('span', {class: 'ot-fold-title', text: title}), line), h('span', {class: 'ot-fold-chevron'}, icon('chevron-down')));
 const attrs = {class: 'ot-fold' + (open ? ' open' : ''), 'data-fold': key || ''};
 for (const [k, v] of Object.entries(data)) attrs['data-' + k] = v;
 const el = h('section', attrs, head, body);
 body.hidden = !open;
 const set = (on, user) => {
  el.classList.toggle('open', on); head.setAttribute('aria-expanded', String(on)); body.hidden = !on;
  if (user) onToggle?.(on);
 };
 head.addEventListener('click', () => set(body.hidden, true));
 el.setOpen = on => set(!!on, false);
 el.setSummary = text => { line.textContent = together(text || ''); };
 return el;
}
// The one status line of a screen (tones: heat, along, water, rest, error, ok).
const statusLine = (text, tone = 'rest') => h('p', {class: 'ot-status', 'data-tone': tone, role: 'status'}, h('span', {class: 'ot-dot', 'aria-hidden': 'true'}), h('span', {text: together(text)}));
const empty = ({icon: name = 'info', text, action}) => h('div', {class: 'ot-empty'}, h('span', {class: 'ot-empty-icon'}, icon(name, {size: 32})), h('p', {text}), action || null);
const skeleton = (kind = 'rows', n = 3) => h('div', {class: 'ot-skeleton ' + kind, 'aria-hidden': 'true'},
 ...Array.from({length: n}, () => h('div', {class: 'ot-bone'}, h('span'), h('span'))));
const valueDisplay = ({value, unit, label, tone, size = 'large'}) => h('div', {class: 'ot-value ' + size, 'data-tone': tone || ''},
 h('span', {class: 'ot-value-figure'}, h('span', {text: value ?? '–'}), unit && value != null ? h('small', {text: unit}) : null), label ? h('span', {class: 'ot-value-label', text: label}) : null);
// {name, temperature, unit, target, state: {text, tone}, emitter (icon), lines, route, current, compact}
function roomCard({name, temperature, unit = '°C', target, state, emitter = 'radiator', lines = [], route, onClick, current, compact, data = {}}) {
 const attrs = {class: 'ot-room' + (compact ? ' compact' : ''), href: route, ...(current ? {'aria-current': 'page'} : {})};
 for (const [k, v] of Object.entries(data)) attrs['data-' + k] = v;
 const el = h(route ? 'a' : 'div', attrs);
 if (onClick) el.addEventListener('click', onClick);
 const temp = h('span', {class: 'ot-room-temp'}, h('span', {class: 'ot-room-figure', text: temperature ?? '–'}), temperature != null ? h('small', {text: unit}) : null);
 el.append(...[h('span', {class: 'ot-room-top'}, h('span', {class: 'ot-room-icon'}, icon(emitter, {size: 20})), h('span', {class: 'ot-room-name', text: name}),
  state && !compact ? chip(state.text, state.tone, state.icon) : null),
 h('span', {class: 'ot-room-mid'}, temp, target ? h('span', {class: 'ot-room-target', text: together(target)}) : null), state && compact ? chip(state.text, state.tone, state.icon) : null].filter(Boolean));
 for (const line of lines.filter(Boolean)) el.append(h('span', {class: 'ot-room-line', text: together(line)}));
 return el;
}
// Help is one line; the rest waits behind "More".
function more(text, lang) {
 const id = uid('more'), body = h('p', {class: 'help ot-more-text', id, hidden: true, text});
 const toggle = h('button', {type: 'button', class: 'btn text small ot-more', 'aria-expanded': 'false', 'aria-controls': id, text: translate(lang, 'More')});
 toggle.addEventListener('click', () => {
  const open = body.hidden; body.hidden = !open; toggle.setAttribute('aria-expanded', String(open));
  toggle.textContent = translate(lang, open ? 'Less' : 'More');
 });
 return h('div', {class: 'ot-more-wrap'}, toggle, body);
}
// Per viewer (open sections); never needed to work.
const memory = key => ({
 get() { try { return JSON.parse(localStorage.getItem('openthermostat-settings:' + key) || 'null'); } catch (e) { return null; } },
 set(v) { try { localStorage.setItem('openthermostat-settings:' + key, JSON.stringify(v)); } catch (e) { /* private window */ } }
});

// fields.<kind>(o) -> {el, value, setError, setMark, focus}
function shell(kind, o, control, labelFor = true) {
 const id = o.id || uid(kind), wrap = h('div', {class: 'field ' + kind, 'data-field': o.key || '', 'data-kind': kind});
 const help = o.help ? h('p', {class: 'help', id: id + '-help', text: o.help}) : null;
 const mark = h('p', {class: 'mark', id: id + '-mark', hidden: true});
 const error = h('p', {class: 'error', id: id + '-error', hidden: true});
 const label = o.label ? h(labelFor ? 'label' : 'span', {class: 'label', ...(labelFor ? {for: id} : {id: id + '-label'}), text: o.label}) : null;
 wrap.append(...[label, control, help, o.more ? more(o.more, langOf(o.hass)) : null, mark, error].filter(Boolean));
 const described = () => [help && !help.hidden && help.id, !mark.hidden && mark.id, !error.hidden && error.id].filter(Boolean).join(' ');
 const api = {
  el: wrap, id,
  setError(text) {
   error.textContent = text || ''; error.hidden = !text; wrap.classList.toggle('invalid', !!text);
   api.target?.()?.setAttribute('aria-invalid', text ? 'true' : 'false'); api.describe();
   if (text) wrap.closest('.ot-fold')?.setOpen?.(true);
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
// No browser time input: the viewer's format, kept as "HH:MM".
function timeInput(o, id, onValue) {
 const input = h('input', {id, type: 'text', class: 'input ot-time', inputmode: 'numeric', autocomplete: 'off', 'data-fk': o.key || '', disabled: o.disabled,
  'aria-label': o.label ? null : translate(langOf(o.hass), 'Time'), maxlength: 8});
 let value = parseTime(o.value) || '';
 input.value = value ? formatTime(o.hass, value) : '';
 input.addEventListener('input', () => { const v = parseTime(input.value); if (v) { value = v; onValue(v, true); } else onValue(null, false); });
 input.addEventListener('blur', () => { if (value && parseTime(input.value)) input.value = formatTime(o.hass, value); });
 return {input, get: () => value, set: v => { value = parseTime(v) || ''; input.value = value ? formatTime(o.hass, value) : ''; }};
}
function dateInputs(o, onValue) {
 const lang = langOf(o.hass), t = k => translate(lang, k);
 const now = new Date(), first = Number(String(o.min || '').slice(0, 4)) || now.getFullYear() - 1, last = Number(String(o.max || '').slice(0, 4)) || now.getFullYear() + 2;
 const select = (label, options, cls) => h('select', {class: 'input ' + cls, 'aria-label': label, disabled: o.disabled}, ...options.map(([v, text]) => h('option', {value: v, text})));
 const day = select(t('Day'), Array.from({length: 31}, (x, i) => [String(i + 1), String(i + 1)]), 'ot-day');
 const month = select(t('Month'), months(o.hass).map((m, i) => [String(i + 1), m]), 'ot-month');
 const year = select(t('Year'), Array.from({length: last - first + 1}, (x, i) => [String(first + i), String(first + i)]), 'ot-year');
 const p = n => String(n).padStart(2, '0');
 const set = ymd => {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(ymd || '');
  if (!m) return;
  if (![...year.options].some(x => x.value === String(Number(m[1])))) year.append(h('option', {value: String(Number(m[1])), text: m[1]}));
  year.value = String(Number(m[1])); month.value = String(Number(m[2])); fit(); day.value = String(Math.min(Number(m[3]), day.options.length));
 };
 // As many days as the chosen month has (no 31 February); a day past its end becomes the month's last.
 const fit = () => {
  const n = new Date(Date.UTC(Number(year.value), Number(month.value), 0)).getUTCDate(), chosen = Number(day.value) || 1;
  while (day.options.length > n) day.lastChild.remove();
  while (day.options.length < n) day.append(h('option', {value: String(day.options.length + 1), text: String(day.options.length + 1)}));
  day.value = String(Math.min(chosen, n));
 };
 const get = () => `${year.value}-${p(month.value)}-${p(day.value)}`;
 for (const s of [day, month, year]) s.addEventListener('change', () => { fit(); onValue(get()); });
 set(o.value);
 return {el: h('div', {class: 'ot-date'}, day, month, year), get, set, first: day};
}
const fields = {
 text: o => inputField('text', 'text', o, {maxlength: o.maxlength, autocomplete: 'off', placeholder: o.placeholder}),
 number: o => inputField('number', 'number', o, {step: o.step ?? 'any', min: o.min, max: o.max, inputmode: 'decimal',
  'aria-label': o.unit ? `${o.label} (${o.unit})` : null}),
 stepper(o) {
  const id = o.id || uid('stepper'), lang = langOf(o.hass), step = Number(o.step) || 1, digits = String(step).split('.')[1]?.length || 0;
  const where = o.hass || lang;
  const input = h('input', {id, type: 'text', class: 'input ot-step-input', inputmode: 'decimal', autocomplete: 'off', 'data-fk': o.key || '', disabled: o.disabled,
   'aria-label': o.unit ? `${o.label || ''} (${o.unit})`.trim() : null});
  const show = v => (v == null || Number.isNaN(v) ? '' : Number(v).toLocaleString(numberLocale(where), {minimumFractionDigits: digits && v % 1 ? digits : 0, maximumFractionDigits: Math.max(digits, 1), useGrouping: false}));
  const read = () => { const s = input.value.trim().replace(',', '.'); return s === '' || Number.isNaN(Number(s)) ? null : Number(s); };
  input.value = show(o.value);
  const clamp = v => Math.min(o.max ?? Infinity, Math.max(o.min ?? -Infinity, Math.round(v / step) * step));
  const bump = dir => { const v = read() ?? o.value ?? o.min ?? 0; input.value = show(clamp(Number((v + dir * step).toFixed(4)))); o.onChange?.(read()); };
  const control = h('div', {class: 'ot-stepper'},
   iconButton('chevron-down', translate(lang, 'Lower'), () => bump(-1), {disabled: o.disabled, 'data-step': 'down'}), input,
   o.unit ? h('span', {class: 'unit', 'aria-hidden': 'true', text: o.unit}) : null,
   iconButton('chevron-down', translate(lang, 'Higher'), () => bump(1), {disabled: o.disabled, 'data-step': 'up', class: 'btn icon up'}));
  const api = shell('stepper', {...o, id}, control);
  api.target = () => input; api.input = input;
  Object.defineProperty(api, 'value', {get: read, set: v => { input.value = show(v); }});
  input.addEventListener('input', () => o.onChange?.(read()));
  input.addEventListener('blur', () => { const v = read(); if (v != null) input.value = show(v); });
  api.describe();
  return api;
 },
 // "YYYY-MM-DDTHH:MM"; optional: '' is no moment.
 moment(o) {
  const id = o.id || uid('moment'), lang = langOf(o.hass), t = k => translate(lang, k);
  let value = o.value || '', api;
  const emit = () => o.onChange?.(value);
  const suggest = () => o.suggest || (() => { const d = new Date(Date.now() + 86400000), p = n => String(n).padStart(2, '0'); return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T07:00`; })();
  const holder = h('div', {class: 'ot-moment'});
  let date, time;
  const draw = focus => {
   if (!value && o.optional) {
    holder.replaceChildren(...[h('span', {class: 'ot-moment-none', text: t('No moment')}),
     o.disabled ? null : button(t('Choose a moment'), () => { value = suggest(); draw(true); emit(); }, 'outlined small', {'data-fk': o.key || '', icon: 'calendar', id})].filter(Boolean));
    if (focus) holder.querySelector('button')?.focus();
    return;
   }
   date = dateInputs({...o, value: value.slice(0, 10)}, v => { value = `${v}T${time.get() || '00:00'}`; emit(); });
   date.first.id = id;
   time = timeInput({...o, key: (o.key || '') + ':time', value: value.slice(11, 16), label: null}, uid('t'), (v, ok) => {
    api?.setError(ok ? '' : translate(lang, 'Enter a time such as {example}.', {example: formatTime(o.hass, '22:00')}));
    if (ok) { value = `${date.get()}T${v}`; emit(); }
   });
   holder.replaceChildren(...[date.el, time.input, o.optional && !o.disabled ? iconButton('close', t('No moment'), () => { value = ''; draw(true); emit(); }, {'data-clear': ''}) : null].filter(Boolean));
   if (focus) date.first.focus();
  };
  draw();
  api = shell('moment', {...o, id}, holder);
  api.target = () => holder.querySelector('select, button');
  Object.defineProperty(api, 'value', {get: () => value, set: v => { value = v || ''; draw(); }});
  api.describe();
  return api;
 },
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
   if (opt.help) { text.append(h('span', {class: 'choice-help', id: oid + '-help', text: together(opt.help)})); input.setAttribute('aria-describedby', oid + '-help'); }
   group.append(h('label', {class: 'choice', for: oid}, input, text));
  }
  const api = shell('radio', {...o, id}, group, false);
  api.target = () => group;
  Object.defineProperty(api, 'value', {get: () => inputs.find(i => i.checked)?.value ?? null, set: v => { for (const i of inputs) i.checked = i.value === v; }});
  api.focus = () => (inputs.find(i => i.checked) || inputs[0])?.focus();
  api.describe();
  return api;
 },
 // Two or three states; the chosen one's explanation beneath.
 segmented(o) {
  const id = o.id || uid('seg'), options = o.options || [];
  const group = h('div', {class: 'ot-seg', role: 'radiogroup', 'aria-labelledby': id + '-label'});
  const help = h('p', {class: 'help ot-seg-help', id: id + '-choice'});
  let value = o.value;
  const buttons = options.map(opt => {
   const b = h('button', {type: 'button', role: 'radio', class: 'ot-seg-btn', 'data-value': opt.value, 'data-tone': opt.tone || null,
    'data-fk': o.key ? o.key + ':' + opt.value : '', disabled: o.disabled}, opt.icon ? icon(opt.icon, {size: 18}) : null, h('span', {text: opt.label}));
   b.addEventListener('click', () => { if (value !== opt.value) { set(opt.value); o.onChange?.(opt.value); } });
   b.addEventListener('keydown', e => {
    const step = {ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1}[e.key];
    if (!step) return;
    e.preventDefault();
    const next = options[(options.indexOf(opt) + step + options.length) % options.length];
    set(next.value); o.onChange?.(next.value); buttons[options.indexOf(next)].focus();
   });
   return b;
  });
  const set = v => {
   value = v;
   buttons.forEach((b, i) => { const on = options[i].value === v; b.setAttribute('aria-checked', String(on)); b.tabIndex = on || (v == null && i === 0) ? 0 : -1; });
   const chosen = options.find(x => x.value === v);
   help.textContent = together(chosen?.help || ''); help.hidden = !chosen?.help;
  };
  group.append(...buttons);
  set(value);
  const api = shell('segmented', {...o, id}, h('div', {class: 'ot-seg-wrap'}, group, help), false);
  api.target = () => buttons.find(b => b.getAttribute('aria-checked') === 'true') || buttons[0];
  for (const b of buttons) b.setAttribute('aria-describedby', id + '-choice');
  Object.defineProperty(api, 'value', {get: () => value, set});
  api.describe = () => {};
  return api;
 },
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

// The entity picker over hass.states (or choices), grouped by area; one ('') or several ([...]).
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
 const nameOf = eid => o.names?.[eid] || stateOf(eid)?.attributes?.friendly_name || eid;
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
 const pool = () => (o.choices ? o.choices.filter(eid => o.names?.[eid] || stateOf(eid)) : Object.keys(hass?.states || {}));
 const candidates = () => pool().filter(eid => {
  const st = stateOf(eid);
  if (chosen.includes(eid)) return false;
  if (o.domains && !o.domains.includes(eid.split('.')[0])) return false;
  if (o.deviceClasses && !o.deviceClasses.includes(st?.attributes?.device_class)) return false;
  return !o.filter || o.filter(st, eid);
 });
 const emit = () => o.onChange?.(o.multiple ? [...chosen] : chosen[0] || '');
 const drawChips = () => {
  chips.replaceChildren(...chosen.map(eid => h('span', {class: 'pick', 'data-entity': eid},
   h('span', {class: 'pick-text'}, h('span', {class: 'pick-name', text: nameOf(eid)}), h('span', {class: 'pick-id', text: [o.showIds === false ? '' : eid, valueOf(eid)].filter(Boolean).join(' · ')})),
   o.disabled ? null : iconButton('close', t('Remove {name}', {name: nameOf(eid)}), () => { chosen = chosen.filter(x => x !== eid); drawChips(); emit(); input.focus(); }, {class: 'btn icon remove'}))));
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
  shown = candidates().map((eid, n) => ({eid, n, name: nameOf(eid), area: areaOf(eid)}))
   .filter(c => words.every(w => `${c.name} ${c.eid} ${c.area}`.toLowerCase().includes(w)));
  if (!o.choices) shown.sort((a, b) => (a.area || '￿').localeCompare(b.area || '￿') || a.name.localeCompare(b.name));
  const limit = 60;
  for (const c of shown.slice(0, limit)) { const g = o.choices ? '' : c.area; if (!groups.has(g)) groups.set(g, []); groups.get(g).push(c); }
  const items = [];
  for (const [area, members] of groups) {
   if (!o.choices) items.push(h('li', {class: 'group', role: 'presentation', text: area || t('No area')}));
   for (const c of members) items.push(h('li', {id: uid('o'), role: 'option', class: 'option', 'aria-selected': 'false', 'data-entity': c.eid,
    on: {mousedown: e => { e.preventDefault(); pick(c.eid); }}}, h('span', {class: 'pick-name', text: c.name}), h('span', {class: 'pick-id', text: o.choices ? areaOf(c.eid) || c.eid : c.eid})));
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

// Resolves true for the action.
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

// defineSection(name, spec); the routes.
const SECTIONS = new Map(), listeners = new Set();
function defineSection(name, spec) {
 if (!/^[a-z_]+$/.test(name) || !spec || typeof spec.render !== 'function') throw new Error('defineSection(name, {render}) needs a name and a render function');
 addTexts(spec.texts);
 SECTIONS.set(name, spec);
 for (const fn of listeners) { try { fn(name); } catch (e) { console.error('OpenThermostat settings', e); } }
}
const onSection = fn => { listeners.add(fn); return () => listeners.delete(fn); };
const ALIASES = {room: 'rooms'};  // #room/<id> opens the section rooms with that item
const parseRoute = hash => {
 const raw = String(hash || '').replace(/^#/, ''), [head, ...rest] = raw.split('/');
 const name = ALIASES[head] || head;
 if (!name || name === 'overview' || !/^[a-z_]+$/.test(name)) return {section: null, item: null};
 let item = rest.length ? rest.join('/') : null;
 try { item = item == null ? null : decodeURIComponent(item); } catch (e) { /* keep as typed */ }
 return {section: name, item: item || null};
};
// CONTRACT-1.4.1 §8 tokens (and the 1.4 names on them), then the components.
const STYLE = `:host{display:block;
--ot-space:8px;--ot-radius:12px;--ot-radius-s:8px;--ot-touch:44px;--ot-motion:150ms ease;
--ot-text-xl:22px;--ot-line-xl:28px;--ot-text-l:17px;--ot-line-l:24px;--ot-text-m:15px;--ot-line-m:22px;--ot-text-s:13px;--ot-line-s:18px;
--ot-bg:var(--card-background-color);--ot-fg:var(--primary-text-color);--ot-fg-2:var(--secondary-text-color);
--ot-line:var(--divider-color);--ot-accent:var(--primary-color);--ot-on-accent:var(--text-primary-color, #fff);
--ot-heat-ink:#a1500f;--ot-heat-fill:#fbe9db;--ot-along-ink:#886100;--ot-along-fill:#f8efcf;--ot-water-ink:#1f5fa8;--ot-water-fill:#dde9f8;
--ot-rest-ink:#5f6368;--ot-rest-fill:#ebedf0;--ot-attention-ink:#b3261e;--ot-attention-fill:#f9dedc;
--ot-text:var(--ot-fg);--ot-muted:var(--ot-fg-2);--ot-surface:var(--ot-bg);--ot-divider:var(--ot-line);
--ot-border:color-mix(in srgb,var(--ot-fg-2) 45%,transparent);--ot-raised:color-mix(in srgb,var(--ot-fg) 2.5%,var(--ot-bg));
--ot-fill:color-mix(in srgb,var(--ot-accent) 72%,#000);--ot-link:color-mix(in srgb,var(--ot-accent) 60%,var(--ot-fg));
--ot-error:var(--ot-attention-ink);--ot-warn:var(--warning-color,#ffa600);--ot-ok:var(--success-color,#43a047);
--ot-s1:calc(var(--ot-space)/2);--ot-s2:var(--ot-space);--ot-s3:calc(var(--ot-space)*1.5);--ot-s4:calc(var(--ot-space)*2);--ot-s5:calc(var(--ot-space)*3);
--ot-s6:calc(var(--ot-space)*4);--ot-value:28px;
color:var(--ot-fg);font:400 var(--ot-text-m)/var(--ot-line-m) var(--paper-font-body1_-_font-family,Roboto,'Segoe UI',Arial,sans-serif)}
:host([data-theme="dark"]){--ot-heat-ink:#f0a060;--ot-heat-fill:rgba(240,160,96,.18);--ot-along-ink:#e6c35c;--ot-along-fill:rgba(230,195,92,.18);
--ot-water-ink:#7fb3f0;--ot-water-fill:rgba(127,179,240,.18);--ot-rest-ink:#b0b4ba;--ot-rest-fill:rgba(176,180,186,.18);
--ot-attention-ink:#f2857c;--ot-attention-fill:rgba(242,133,124,.18)}
*{box-sizing:border-box}[hidden]{display:none!important}p{margin:0}h1,h2,h3,h4{margin:0}
.ot-icon{flex:none;display:block}
.card,.ot-card{background:var(--ot-surface);border-radius:var(--ot-radius);border:1px solid var(--ot-divider)}
.card{overflow:hidden}.ot-card{padding:var(--ot-s4)}.ot-card+.ot-card,.ot-card+.card,.card+.ot-card{margin-top:var(--ot-s3)}
.ot-card-head{display:flex;align-items:center;gap:var(--ot-s3);margin-bottom:var(--ot-s3)}
.ot-card-icon,.ot-fold-icon,.row-icon{flex:none;display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:10px;
color:color-mix(in srgb,var(--ot-accent) 55%,var(--ot-text));background:color-mix(in srgb,var(--ot-accent) 12%,var(--ot-surface))}
.ot-card-titles,.ot-fold-titles{min-width:0;display:grid;gap:2px}.ot-card-title,.ot-fold-title{font-size:var(--ot-text-l);font-weight:500;line-height:1.3}
.ot-card-summary,.ot-fold-summary{font-size:var(--ot-text-s);color:var(--ot-muted);overflow-wrap:anywhere}
.row:focus-visible,.btn:focus-visible,.back:focus-visible,.switch:focus-visible,.choice input:focus-visible,.ot-fold-head:focus-visible,.ot-seg-btn:focus-visible,
.ot-room:focus-visible,.ot-tile:focus-visible{outline:3px solid var(--ot-accent);outline-offset:2px}
.input:focus-visible{outline:2px solid var(--ot-accent);outline-offset:0;border-color:var(--ot-accent)}
.form{padding:4px var(--ot-s4)}.fields{display:flex;flex-direction:column}
.field{padding:var(--ot-s4) 0;border-top:1px solid var(--ot-divider);border-left:3px solid transparent;margin-left:-16px;padding-left:13px;display:grid;gap:6px;position:relative}
.field:first-child{border-top:0}.field.changed{border-left-color:var(--ot-accent)}.field.conflict{border-left-color:var(--ot-warn)}
.label{font-weight:500;font-size:var(--ot-text-m)}.help,.choice-help,.mark{color:var(--ot-muted);font-size:var(--ot-text-s);overflow-wrap:anywhere}
.mark{font-weight:500}.field.changed .mark{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.field.conflict .mark{color:color-mix(in srgb,var(--ot-warn) 40%,var(--ot-text))}.error{font-size:var(--ot-text-s);font-weight:500}
.input{font:inherit;color:inherit;background:var(--ot-surface);border:1px solid var(--ot-border);border-radius:var(--ot-radius-s);
min-height:44px;padding:10px 12px;width:100%;max-width:480px}
select.input{padding-right:8px}
.input:disabled,.switch:disabled,.choice input:disabled{opacity:.6;cursor:default}.invalid .input{border-color:var(--ot-error)}
.with-unit{display:flex;align-items:center;gap:8px;max-width:240px}.unit{color:var(--ot-muted);white-space:nowrap}
.toggle-row{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:44px}
.switch{appearance:none;flex:none;width:44px;height:24px;border-radius:12px;position:relative;cursor:pointer;margin:0;
background:color-mix(in srgb,var(--ot-muted) 45%,transparent);transition:background var(--ot-motion)}
.switch::after{content:"";position:absolute;top:3px;left:3px;width:18px;height:18px;border-radius:50%;background:var(--ot-surface);transition:transform var(--ot-motion);box-shadow:0 1px 2px rgba(0,0,0,.3)}
.switch:checked{background:var(--ot-fill)}.switch:checked::after{transform:translateX(20px)}
.choices{display:grid;gap:4px}.choice{display:grid;grid-template-columns:auto 1fr;gap:10px;align-items:start;padding:8px 0;cursor:pointer}
.choice input{margin:3px 0 0;width:18px;height:18px;accent-color:var(--ot-fill)}.choice-text{display:grid;gap:2px}.choice-label{font-weight:500}
.picker{display:grid;gap:8px;max-width:520px}.picked{display:grid;gap:6px}.picked:empty{display:none}
.pick{display:flex;align-items:center;gap:8px;min-height:52px;padding:6px 4px 6px 12px;border:1px solid var(--ot-divider);border-radius:var(--ot-radius-s);background:var(--ot-raised)}
.pick-text{flex:1 1 auto;min-width:0;display:grid}.pick-name{overflow-wrap:anywhere}.pick-id{color:var(--ot-muted);font-size:var(--ot-text-s);overflow-wrap:anywhere}
.combo{position:relative}.options{position:absolute;z-index:4;left:0;right:0;top:calc(100% + 4px);max-height:320px;overflow:auto;margin:0;padding:4px 0;
list-style:none;background:var(--ot-surface);border:1px solid var(--ot-divider);border-radius:var(--ot-radius-s);box-shadow:0 6px 20px rgba(0,0,0,.18)}
.option{display:grid;padding:8px 12px;cursor:pointer;min-height:44px}.option[aria-selected=true],.option:hover{background:color-mix(in srgb,var(--ot-accent) 14%,transparent)}
.group{padding:8px 12px 4px;font-size:12px;font-weight:500;color:var(--ot-muted)}.empty{padding:8px 12px;color:var(--ot-muted)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;font:inherit;font-weight:500;min-height:var(--ot-touch);padding:8px 18px;border-radius:var(--ot-radius);
border:1px solid transparent;cursor:pointer;background:none;color:var(--ot-link);transition:background var(--ot-motion),box-shadow var(--ot-motion);white-space:nowrap}
.btn.text{padding:8px 12px}.btn.text:hover,.btn.outlined:hover{background:color-mix(in srgb,var(--ot-accent) 8%,transparent)}
.btn.small{min-height:36px;padding:4px 12px;font-size:var(--ot-text-s)}.btn.small,.btn.ot-more{position:relative}
.btn.small::after,.btn.ot-more::after{content:"";position:absolute;left:0;right:0;top:-5px;bottom:-5px}.btn.ot-more::after{top:-7px;bottom:-7px}
.btn.outlined{border-color:var(--ot-accent)}.btn.filled{background:var(--ot-fill);color:var(--ot-on-accent)}.btn.filled:hover{box-shadow:0 1px 4px rgba(0,0,0,.25)}
.btn.danger{background:none;border-color:var(--ot-attention-ink);color:var(--ot-attention-ink)}
.btn.filled.danger{background:var(--ot-attention-ink);color:var(--ot-on-accent);border-color:transparent}.btn:disabled{opacity:.5;cursor:default}
.btn.icon{min-height:44px;width:44px;padding:0;border-radius:50%;color:var(--ot-muted)}.btn.icon:hover{background:color-mix(in srgb,var(--ot-text) 8%,transparent)}
@keyframes ot-in{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.ot-fold{background:var(--ot-surface);border:1px solid var(--ot-divider);border-radius:var(--ot-radius)}.ot-fold+.ot-fold{margin-top:var(--ot-s2)}
.ot-fold-head{display:flex;align-items:center;gap:var(--ot-s3);width:100%;min-height:64px;padding:var(--ot-s3) var(--ot-s4);border:0;background:none;color:inherit;font:inherit;
text-align:left;cursor:pointer;border-radius:var(--ot-radius)}
.ot-fold-head:hover .ot-fold-chevron{color:var(--ot-link)}.ot-fold-titles{flex:1 1 auto}
.ot-fold-summary{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ot-fold.open .ot-fold-summary{white-space:normal}
.ot-fold-chevron{flex:none;display:flex;color:var(--ot-muted);transition:transform var(--ot-motion)}.ot-fold.open .ot-fold-chevron{transform:rotate(180deg)}
.ot-fold-body{padding:0 var(--ot-s4) var(--ot-s2);border-top:1px solid var(--ot-divider);animation:ot-in var(--ot-motion)}
.ot-fold-body>.field:first-child{border-top:0}
.ot-seg-wrap{display:grid;gap:6px}.ot-seg{display:inline-flex;flex-wrap:wrap;max-width:100%;border:1px solid var(--ot-border);border-radius:var(--ot-radius-s);overflow:hidden;justify-self:start}
.ot-seg-btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:44px;padding:8px 16px;border:0;border-left:1px solid var(--ot-border);
background:var(--ot-surface);color:var(--ot-text);font:inherit;font-weight:500;cursor:pointer;flex:1 1 auto;transition:background var(--ot-motion),color var(--ot-motion)}
.ot-seg-btn:first-child{border-left:0}.ot-seg-btn:hover{background:color-mix(in srgb,var(--ot-accent) 8%,var(--ot-surface))}
.ot-seg-btn[aria-checked=true]{background:var(--ot-fill);color:var(--ot-on-accent)}.ot-seg-btn:disabled{cursor:default;opacity:.6}
.ot-chip{display:inline-flex;align-items:center;gap:4px;padding:4px 10px;border-radius:12px;font-size:var(--ot-text-s);line-height:var(--ot-line-s);font-weight:500;
white-space:nowrap;background:var(--ot-tone-fill,var(--ot-rest-fill));color:var(--ot-tone-ink,var(--ot-rest-ink))}
[data-tone=heat]{--ot-tone-ink:var(--ot-heat-ink);--ot-tone-fill:var(--ot-heat-fill)}[data-tone=along]{--ot-tone-ink:var(--ot-along-ink);--ot-tone-fill:var(--ot-along-fill)}
[data-tone=water]{--ot-tone-ink:var(--ot-water-ink);--ot-tone-fill:var(--ot-water-fill)}[data-tone=rest]{--ot-tone-ink:var(--ot-rest-ink);--ot-tone-fill:var(--ot-rest-fill)}
[data-tone=attention],[data-tone=error]{--ot-tone-ink:var(--ot-attention-ink);--ot-tone-fill:var(--ot-attention-fill)}
[data-tone=ok]{--ot-tone-ink:color-mix(in srgb,var(--ot-ok) 60%,var(--ot-fg));--ot-tone-fill:color-mix(in srgb,var(--ot-ok) 15%,var(--ot-bg))}
[data-tone=accent]{--ot-tone-ink:var(--ot-link);--ot-tone-fill:color-mix(in srgb,var(--ot-accent) 14%,var(--ot-bg))}
.ot-status{display:flex;align-items:center;gap:8px;font-weight:500;overflow-wrap:anywhere}
.ot-dot{flex:none;width:10px;height:10px;border-radius:50%;background:var(--ot-tone-ink,var(--ot-rest-ink))}
.ot-empty{display:grid;justify-items:center;text-align:center;gap:var(--ot-s3);padding:var(--ot-s6) var(--ot-s4);color:var(--ot-muted)}
.ot-empty-icon{display:flex;width:56px;height:56px;align-items:center;justify-content:center;border-radius:50%;background:var(--ot-raised)}
.ot-skeleton{display:grid;gap:var(--ot-s3)}.ot-bone{display:grid;gap:8px;padding:var(--ot-s4);border-radius:var(--ot-radius);background:var(--ot-surface);border:1px solid var(--ot-divider)}
.ot-bone span{display:block;height:12px;border-radius:6px;background:linear-gradient(90deg,var(--ot-raised),color-mix(in srgb,var(--ot-text) 9%,var(--ot-surface)),var(--ot-raised));
background-size:200% 100%;animation:ot-shine 1.4s linear infinite}.ot-bone span:first-child{width:40%;height:16px}.ot-bone span:last-child{width:70%}
.ot-skeleton.cards{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}.ot-skeleton.cards .ot-bone{min-height:120px}
@keyframes ot-shine{to{background-position:-200% 0}}
.ot-value{display:grid;gap:2px}.ot-value-figure{font-size:var(--ot-value);font-weight:300;line-height:1.05;font-variant-numeric:tabular-nums;white-space:nowrap}
.ot-value.small .ot-value-figure{font-size:var(--ot-text-xl)}.ot-value-figure small{font-size:var(--ot-text-m);color:var(--ot-muted);margin-left:2px;font-weight:400}
.ot-value-label{font-size:var(--ot-text-s);color:var(--ot-muted)}
.ot-room{display:grid;gap:6px;align-content:start;padding:var(--ot-s4);border-radius:var(--ot-radius);background:var(--ot-surface);border:1px solid var(--ot-divider);
color:inherit;text-decoration:none;cursor:pointer;transition:border-color var(--ot-motion),box-shadow var(--ot-motion);min-width:0}
.ot-room:hover{border-color:color-mix(in srgb,var(--ot-accent) 45%,var(--ot-divider));box-shadow:0 2px 10px rgba(0,0,0,.08)}
.ot-room[aria-current=page]{border-color:var(--ot-accent);box-shadow:inset 0 0 0 1px var(--ot-accent)}
.ot-room-top{display:flex;align-items:center;gap:8px;min-width:0}.ot-room-icon{display:flex;color:var(--ot-muted)}
.ot-room-name{flex:1 1 auto;min-width:0;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ot-room-mid{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.ot-room-temp{font-size:var(--ot-value);font-weight:300;line-height:1.1;font-variant-numeric:tabular-nums;white-space:nowrap}
.ot-room-temp small{font-size:var(--ot-text-m);color:var(--ot-muted);margin-left:2px;font-weight:400}
.ot-room-target{color:var(--ot-muted);font-size:var(--ot-text-s);white-space:nowrap}
.ot-room-line{font-size:var(--ot-text-s);color:var(--ot-muted);overflow-wrap:anywhere}
.ot-room.compact{padding:var(--ot-s3);gap:4px}.ot-room.compact>.ot-chip{justify-self:start}.ot-room.compact .ot-room-temp{font-size:var(--ot-text-xl)}
.ot-more-wrap{display:grid;gap:4px;justify-items:start}.btn.ot-more{min-height:32px;padding:2px 8px;margin-left:-8px}
.ot-stepper{display:flex;align-items:center;gap:4px}.ot-step-input{width:88px;text-align:center;font-variant-numeric:tabular-nums}
.ot-stepper .unit{margin-right:4px}.ot-stepper .btn.icon.up .ot-icon{transform:rotate(180deg)}
.ot-time{width:112px;font-variant-numeric:tabular-nums}
.ot-date,.ot-moment{display:flex;flex-wrap:wrap;align-items:center;gap:8px}.ot-date .input{width:auto;max-width:none}.ot-day{min-width:64px}.ot-month{min-width:128px}
.ot-moment-none{color:var(--ot-muted)}
@media(max-width:420px){.form{padding:4px 12px}.field{margin-left:-12px;padding-left:9px}.form .row{margin:0 -12px;width:calc(100% + 24px)}
.ot-fold-head{padding:var(--ot-s3)}.ot-fold-body{padding:0 var(--ot-s3) var(--ot-s2)}.ot-fold-body>.field{margin-left:-12px}
.ot-seg{display:flex;justify-self:stretch}.ot-seg-btn{padding:8px 10px}.ot-card{padding:var(--ot-s3)}.row{padding:var(--ot-s3)}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}`;

const KIT = Object.freeze({version: 2, h, translate, addTexts, langOf, together, defineSection, onSection, row, frame, notice, inlineError, button, iconButton,
 fields, shell, confirm: confirmDialog, parseRoute, sections: SECTIONS, icon, icons: Object.keys(ICONS), card, fold, statusLine, empty, skeleton,
 chip, valueDisplay, roomCard, more, memory, style: STYLE,
 time: Object.freeze({format: formatTime, moment: formatMoment, date: formatDate, parse: parseTime, hour12, weekdays, months}), number, degrees});

// Sections loaded before the kit queued themselves.
if (!window.OpenThermostatSettingsKit || !(window.OpenThermostatSettingsKit.version >= 2)) {
 window.OpenThermostatSettingsKit = KIT;
 const queued = Array.isArray(window.OpenThermostatSettingsSections) ? window.OpenThermostatSettingsSections : [];
 window.OpenThermostatSettingsSections = {push: ([name, spec]) => defineSection(name, spec)};
 for (const [name, spec] of queued) { try { defineSection(name, spec); } catch (e) { console.error('OpenThermostat settings section', name, e); } }
}
