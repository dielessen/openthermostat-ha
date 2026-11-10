/* Dashboard card: one E32 room at a glance (OpenThermostat 1.1; rc.5 the owner's sketch; 1.4.1 the design language of
   the settings panel, phase 2, HA-INSTELPANEEL-FASE2.nl.md chapters 4 and 7.2, CONTRACT-1.4.1 §8 and §9).
   Reads the room's Reason sensor (room_overview.py) and the room thermostat on the same device:
   - the heating type as a small grey icon (radiator or floor heating, from the dashboard's ``emitter``), the room's name
     and its state as a status label: On (orange), Heat along only (amber), Off (grey), and Summer (grey) while the house
     is in summer mode (the house mode select, the thermostat's ``reason`` or the Reason sensor's state ``summer``);
   - the temperature now large on the right, the target under it;
   - one line "what it does now": the reason's sentence (its short word where the sentence would only repeat the figures
     above it), then the week program's step ("Comfort until 22:30, then Night 18.0 °C");
   - the next reset time in one muted line ("Resets at 22:00 to 14 °C", the room thermostat's next_reset);
   - labels only for deviations: Smart warm-up off (or on) for this room against the house switch, a radiator valve
     with a problem; the valves' opening as a quiet line; the text button "Settings" at the bottom right, which opens
     this room in the dashboard's settings view (<settings_path>#room/<id>). The rest of the card opens the Reason
     sensor's history.
   Words: the integration's translations (strings.json entity.sensor.room_reason) where they exist, so every viewer
   reads them in their own Home Assistant language; the card's own EN/NL/PL table (TEXT) for its new words, and English
   last resorts for every reason key (LINE, CHIP), so a raw key never shows; an unknown key says so in a plain sentence.
   Icons: Material Design Icons as inline SVG (no ha-icon). Times: the shared clock below (Home Assistant's locale,
   time format and time zone). Tokens: CONTRACT-1.4.1 §8 on the host; dark from hass.themes.darkMode, else the
   browser's colour scheme. */
const KEY = 'component.open_thermostat.entity.sensor.room_reason.state_attributes.';
// The reason in one word (state_attributes.chip): the English last resort, key for key as strings.json.
const CHIP = {off: 'Off', window_open: 'Paused', window_pending: 'Pausing soon', no_measurement: 'No measurement', hot_water: 'Waiting',
 boiler_pause: 'Waiting', warm_up: 'Warming up', away_return: 'Warming up', holiday: 'Holiday', away: 'Away', room_away: 'Away',
 house_away: 'Away', boost: 'Boost', temporary: 'Temporary', follow: 'Heats along', heating: 'Heating', wants_heat: 'Wants heat', warm_enough: 'At temperature', summer: 'Summer'};
// The sentence of each variant (state_attributes.line): the English last resort, key for key as strings.json.
const LINE = {off: 'Frost protection only (room off)', window_open: 'Paused: a window or door is open',
 window_open_contact: 'Paused: {contact} open since {since}', window_open_window: 'Paused: a window is open',
 window_open_door: 'Paused: a door is open', window_pending: 'A window or door is open: the room pauses soon',
 window_pending_contact: '{contact} open: the room pauses soon',
 window_pending_window: 'A window is open: the room pauses soon',
 window_pending_door: 'A door is open: the room pauses soon',
 no_measurement: 'No measurement: this room does not ask for heat',
 hot_water: 'Waiting: the boiler is making hot water', boiler_pause: 'Burner resting before the next start',
 away_return: 'Warming up for your return', holiday: 'Holiday until {until} ({target} °C)',
 away: 'Away: the house is set to away ({target} °C)',
 room_away: 'Away: nobody of this room is home ({target} °C)',
 house_away: 'Away: everyone is away ({target} °C)', boost: 'Boost active', boost_until: 'Boost until {until}',
 temporary: 'Temporarily {target} °C', temporary_until: 'Temporarily {target} °C until {until}',
 follow: 'Heats along: it never asks for heat itself',
 follow_frost: 'Heats along; below 8 °C it asks for heat', heating: 'Heating: {temperature} → {target} °C',
 wants_heat: 'Wants heat: {temperature} → {target} °C',
 warm_enough: 'Warm enough: {temperature} °C (target {target} °C)', no_heat_needed: 'No heat needed',
 warm_up: 'Smart warm-up: heating early for {time} ({target} °C)', warm_up_for: 'Warming up for {time}',
 summer: 'Summer mode: the heating stays off until you switch this off; hot water and frost protection stay.'};
// The card's words (state_attributes.card): the same, for the labels and the button.
const WORDS = {smart_on: 'Smart warm-up on', home: 'At home', away: 'Away', holiday: 'Holiday', window_open: 'Window open',
 door_open: 'Door open', window_pending: 'Window open, pausing soon', door_pending: 'Door open, pausing soon', settings: 'Settings'};
// The week program's step (state_attributes.program): the English last resort, key for key as strings.json.
const PROGRAM = {comfort: 'Comfort', eco: 'Eco', night: 'Night', holiday: 'Holiday', step: '{level} until {time}, then {next}'};
// (1.4.1, HA-SUMMER: the reason "summer" after "off", its word Summer and the design's sentence, §5.)
// Sentences that only repeat the figures beside them ("Heating: 20.6 → 22.5 °C"): the reason's short word instead.
const RESTATED = new Set(['heating', 'wants_heat', 'warm_enough']);
const FALLBACK = {temperature: 'Now', setpoint: 'Target', valve_position: 'Radiator valves open'};
// The card's own words (1.4.1), EN/NL/PL: the room states as the room's settings say them (selector e32_room_state, Polish
// "Wyłączone" as the glossary), Summer as the summer mode design §5, the deviation labels, the summer and unknown lines.
const TEXT = {
 en: {on: 'On', follow: 'Heat along only', off: 'Off', summer: 'Summer', smart_off: 'Smart warm-up off', smart_on: 'Smart warm-up on',
  summer_line: 'Summer mode: the heating stays off until you switch this off; hot water and frost protection stay.', unknown: 'The E32 reports something this card does not know yet',
  unavailable: 'Unavailable', missing: 'Entity not available: {entity}'},
 nl: {on: 'Aan', follow: 'Alleen meeverwarmen', off: 'Uit', summer: 'Zomer', smart_off: 'Slim opwarmen uit', smart_on: 'Slim opwarmen aan',
  summer_line: 'Zomerstand: de verwarming staat uit tot je dit uitzet; warm water en vorstbeveiliging blijven.', unknown: 'De E32 meldt iets wat deze kaart nog niet kent',
  unavailable: 'Niet beschikbaar', missing: 'Entiteit niet beschikbaar: {entity}'},
 pl: {on: 'Włączone', follow: 'Grzeje tylko razem z innymi', off: 'Wyłączone', summer: 'Lato', smart_off: 'Inteligentne nagrzewanie wyłączone',
  smart_on: 'Inteligentne nagrzewanie włączone', summer_line: 'Tryb letni: ogrzewanie pozostaje wyłączone, dopóki tego nie wyłączysz; ciepła woda i ochrona przed mrozem działają.',
  unknown: 'E32 zgłasza coś, czego ta karta jeszcze nie zna', unavailable: 'Niedostępny', missing: 'Encja niedostępna: {entity}'}};
// The next reset time's line: [a temperature, a state, On, Heat along only, Off], as the room's settings say them.
const RESET = {en: ['Resets at {time} to {value}', 'At {time} to {value}', 'On', 'Heat along only', 'Off'],
 nl: ['Om {time} terug naar {value}', 'Om {time} naar {value}', 'Aan', 'Alleen meeverwarmen', 'Uit'],
 pl: ['Godzina powrotu {time}: {value}', 'Godzina powrotu {time}: {value}', 'Włączone', 'Grzeje tylko razem z innymi', 'Wyłączone']};
// The status label of each room state: its tone (CONTRACT §8: orange heats, amber heats along, grey rest/off/summer) and icon.
const STATE = {on: ['heat', 'fire'], follow: ['along', 'fire-circle'], off: ['rest', 'power'], summer: ['rest', 'white-balance-sunny']};
// The heating type (the room's emitter in its settings): radiator, floor heating; a room without one: a thermostat.
const TYPE = {radiator: 'radiator', floor: 'heating-coil'};
// Material Design Icons (v7.4.47, Apache 2.0), inline: the test environment has no ha-icon and neither needs one.
const ICONS = {
 'fire': 'M17.66 11.2C17.43 10.9 17.15 10.64 16.89 10.38C16.22 9.78 15.46 9.35 14.82 8.72C13.33 7.26 13 4.85 13.95 3C13 3.23 12.17 3.75 11.46 4.32C8.87 6.4 7.85 10.07 9.07 13.22C9.11 13.32 9.15 13.42 9.15 13.55C9.15 13.77 9 13.97 8.8 14.05C8.57 14.15 8.33 14.09 8.14 13.93C8.08 13.88 8.04 13.83 8 13.76C6.87 12.33 6.69 10.28 7.45 8.64C5.78 10 4.87 12.3 5 14.47C5.06 14.97 5.12 15.47 5.29 15.97C5.43 16.57 5.7 17.17 6 17.7C7.08 19.43 8.95 20.67 10.96 20.92C13.1 21.19 15.39 20.8 17.03 19.32C18.86 17.66 19.5 15 18.56 12.72L18.43 12.46C18.22 12 17.66 11.2 17.66 11.2M14.5 17.5C14.22 17.74 13.76 18 13.4 18.1C12.28 18.5 11.16 17.94 10.5 17.28C11.69 17 12.4 16.12 12.61 15.23C12.78 14.43 12.46 13.77 12.33 13C12.21 12.26 12.23 11.63 12.5 10.94C12.69 11.32 12.89 11.7 13.13 12C13.9 13 15.11 13.44 15.37 14.8C15.41 14.94 15.43 15.08 15.43 15.23C15.46 16.05 15.1 16.95 14.5 17.5H14.5Z',
 'fire-circle': 'M14.66 14.18C14.69 14.29 14.7 14.4 14.7 14.5C14.73 15.15 14.44 15.85 13.97 16.28C13.75 16.47 13.39 16.67 13.11 16.75C12.23 17.06 11.35 16.62 10.83 16.11C11.77 15.89 12.32 15.21 12.5 14.5C12.62 13.89 12.37 13.38 12.27 12.78C12.17 12.2 12.19 11.71 12.4 11.18C12.55 11.47 12.71 11.77 12.9 12C13.5 12.78 14.45 13.12 14.66 14.18M22 12C22 17.5 17.5 22 12 22S2 17.5 2 12 6.5 2 12 2 22 6.5 22 12M17.16 12.56L17.06 12.36C16.9 12 16.45 11.38 16.45 11.38C16.27 11.15 16.05 10.94 15.85 10.74C15.32 10.27 14.73 9.94 14.22 9.45C13.05 8.31 12.79 6.44 13.54 5C12.79 5.18 12.14 5.58 11.58 6.03C9.55 7.65 8.75 10.5 9.71 12.95C9.74 13.03 9.77 13.11 9.77 13.21C9.77 13.38 9.65 13.53 9.5 13.6C9.31 13.67 9.13 13.63 9 13.5C8.93 13.46 8.9 13.42 8.87 13.37C8 12.26 7.84 10.66 8.43 9.39C7.12 10.45 6.41 12.24 6.5 13.92C6.56 14.31 6.6 14.7 6.74 15.09C6.85 15.56 7.06 16 7.3 16.44C8.14 17.78 9.61 18.75 11.19 18.94C12.87 19.15 14.67 18.85 15.96 17.7C17.4 16.4 17.9 14.33 17.16 12.56Z',
 'power': 'M16.56,5.44L15.11,6.89C16.84,7.94 18,9.83 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12C6,9.83 7.16,7.94 8.88,6.88L7.44,5.44C5.36,6.88 4,9.28 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12C20,9.28 18.64,6.88 16.56,5.44M13,3H11V13H13',
 'white-balance-sunny': 'M3.55 19.09L4.96 20.5L6.76 18.71L5.34 17.29M12 6C8.69 6 6 8.69 6 12S8.69 18 12 18 18 15.31 18 12C18 8.68 15.31 6 12 6M20 13H23V11H20M17.24 18.71L19.04 20.5L20.45 19.09L18.66 17.29M20.45 5L19.04 3.6L17.24 5.39L18.66 6.81M13 1H11V4H13M6.76 5.39L4.96 3.6L3.55 5L5.34 6.81L6.76 5.39M1 13H4V11H1M13 20H11V23H13',
 'radiator': 'M7.95,3L6.53,5.19L7.95,7.4H7.94L5.95,10.5L4.22,9.6L5.64,7.39L4.22,5.19L6.22,2.09L7.95,3M13.95,2.89L12.53,5.1L13.95,7.3L13.94,7.31L11.95,10.4L10.22,9.5L11.64,7.3L10.22,5.1L12.22,2L13.95,2.89M20,2.89L18.56,5.1L20,7.3V7.31L18,10.4L16.25,9.5L17.67,7.3L16.25,5.1L18.25,2L20,2.89M2,22V14A2,2 0 0,1 4,12H20A2,2 0 0,1 22,14V22H20V20H4V22H2M6,14A1,1 0 0,0 5,15V17A1,1 0 0,0 6,18A1,1 0 0,0 7,17V15A1,1 0 0,0 6,14M10,14A1,1 0 0,0 9,15V17A1,1 0 0,0 10,18A1,1 0 0,0 11,17V15A1,1 0 0,0 10,14M14,14A1,1 0 0,0 13,15V17A1,1 0 0,0 14,18A1,1 0 0,0 15,17V15A1,1 0 0,0 14,14M18,14A1,1 0 0,0 17,15V17A1,1 0 0,0 18,18A1,1 0 0,0 19,17V15A1,1 0 0,0 18,14Z',
 'heating-coil': 'M19 17C20.21 17 22 16.2 22 14S20.21 11 19 11H17V9H19C21.2 9 22 7.21 22 6C22 3.8 20.21 3 19 3H17V2H16V3H8V2H7V3H2V5H7V7H5C3.79 7 2 7.8 2 10S3.79 13 5 13H7V15H5C3.79 15 2 15.8 2 18S3.79 21 5 21H7V22H8V21H16V22H17V21H22V19H17V17H19M19 13C19.45 13 20 13.19 20 14S19.45 15 19 15H17V13H19M16 11H8V9H16V11M19 5C19.45 5 20 5.2 20 6C20 6.45 19.81 7 19 7H17V5H19M8 5H16V7H8V5M5 11C4.55 11 4 10.81 4 10S4.55 9 5 9H7V11H5M8 13H16V15H8V13M5 19C4.55 19 4 18.81 4 18S4.55 17 5 17H7V19H5M16 19H8V17H16V19Z',
 'thermostat': 'M16.95,16.95L14.83,14.83C15.55,14.1 16,13.1 16,12C16,11.26 15.79,10.57 15.43,10L17.6,7.81C18.5,9 19,10.43 19,12C19,13.93 18.22,15.68 16.95,16.95M12,5C13.57,5 15,5.5 16.19,6.4L14,8.56C13.43,8.21 12.74,8 12,8A4,4 0 0,0 8,12C8,13.1 8.45,14.1 9.17,14.83L7.05,16.95C5.78,15.68 5,13.93 5,12A7,7 0 0,1 12,5M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z',
 'valve': 'M4 22H2V2H4M22 2H20V22H22M17.24 5.34L13.24 9.34A3 3 0 0 0 9.24 13.34L5.24 17.34L6.66 18.76L10.66 14.76A3 3 0 0 0 14.66 10.76L18.66 6.76Z',
 'valve-closed': 'M22 2V22H20V13H14.82A3 3 0 0 1 9.18 13H4V22H2V2H4V11H9.18A3 3 0 0 1 14.82 11H20V2Z',
 'clock-fast': 'M15,4A8,8 0 0,1 23,12A8,8 0 0,1 15,20A8,8 0 0,1 7,12A8,8 0 0,1 15,4M15,6A6,6 0 0,0 9,12A6,6 0 0,0 15,18A6,6 0 0,0 21,12A6,6 0 0,0 15,6M14,8H15.5V11.78L17.83,14.11L16.77,15.17L14,12.4V8M2,18A1,1 0 0,1 1,17A1,1 0 0,1 2,16H5.83C6.14,16.71 6.54,17.38 7,18H2M3,13A1,1 0 0,1 2,12A1,1 0 0,1 3,11H5.05L5,12L5.05,13H3M4,8A1,1 0 0,1 3,7A1,1 0 0,1 4,6H7C6.54,6.62 6.14,7.29 5.83,8H4Z'};
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
ha-card{display:block;box-sizing:border-box;padding:calc(var(--ot-space)*2);border-radius:var(--ot-radius);background:var(--ot-bg);color:var(--ot-fg);cursor:pointer}
ha-card:focus-visible{outline:2px solid var(--ot-accent);outline-offset:2px}
p{margin:0}svg{display:block;flex:none}
.wrap{container:room/inline-size}
.head{display:flex;align-items:flex-start;gap:calc(var(--ot-space)*1.5)}
.type{flex:none;display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:var(--ot-rest-fill);color:var(--ot-rest-ink)}
.titles{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;align-items:flex-start;gap:var(--ot-space)}
.name{font-size:var(--ot-text-l);line-height:var(--ot-line-l);font-weight:500;overflow-wrap:anywhere}
.temps{flex:none;text-align:right}
.now{font-size:var(--ot-text-xl);line-height:var(--ot-line-xl);font-weight:400;font-variant-numeric:tabular-nums;white-space:nowrap}
.now .unit{font-size:var(--ot-text-m);color:var(--ot-fg-2)}.now.none{color:var(--ot-fg-2)}
.target{font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2);white-space:nowrap}
.label{display:inline-flex;align-items:center;gap:6px;max-width:100%;box-sizing:border-box;padding:4px 10px;border-radius:12px;
font-size:var(--ot-text-s);line-height:var(--ot-line-s);font-weight:500;background:var(--fill);color:var(--ink);overflow-wrap:anywhere}
.tone-heat{--ink:var(--ot-heat-ink);--fill:var(--ot-heat-fill)}.tone-along{--ink:var(--ot-along-ink);--fill:var(--ot-along-fill)}
.tone-rest{--ink:var(--ot-rest-ink);--fill:var(--ot-rest-fill)}.tone-attention{--ink:var(--ot-attention-ink);--fill:var(--ot-attention-fill)}
.body{margin:calc(var(--ot-space)*1.5) 0 0 52px}
.why{font-size:var(--ot-text-m);line-height:var(--ot-line-m);overflow-wrap:anywhere}
.reset,.missing{margin-top:4px;font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2);overflow-wrap:anywhere}
.foot{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ot-space);margin:var(--ot-space) 0 calc(var(--ot-space)*-1) 52px}
.meta{display:inline-flex;align-items:center;gap:6px;font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2)}
.settings{margin:0 calc(var(--ot-space)*-1) 0 auto;min-height:var(--ot-touch);padding:0 calc(var(--ot-space)*1.5);border:0;border-radius:var(--ot-radius);
background:none;font:inherit;font-size:var(--ot-text-m);font-weight:500;cursor:pointer;color:var(--ot-link);
transition:background-color var(--ot-motion)}
.settings:hover{background:color-mix(in srgb,var(--ot-accent) 10%,transparent)}
.settings:focus-visible{outline:2px solid var(--ot-accent);outline-offset:-2px}
@container room (max-width:300px){.body,.foot{margin-left:0}}`;

const locale = hass => hass?.locale?.language || hass?.language || 'en';
const lang = hass => /^(nl|pl)\b/.exec(locale(hass))?.[1] || 'en';
const darkOf = hass => {
 if (typeof hass?.themes?.darkMode === 'boolean') return hass.themes.darkMode;
 try { return window.matchMedia('(prefers-color-scheme: dark)').matches; } catch (e) { return false; }
};
// A figure and its unit stay together on a narrow card ("21,2 °C" never breaks before the unit).
const together = text => text.replace(/ (°C|%)/g, ' $1');
// Now with one decimal (20.0); a target as set (21, 22.5).
const degrees = (hass, value, fixed) => typeof value === 'number' && Number.isFinite(value)
 ? value.toLocaleString(locale(hass), {minimumFractionDigits: fixed ? 1 : 0, maximumFractionDigits: 1}) : null;
/* clock: begin. One clock for the OpenThermostat cards (the same text in house-card.js and room-status-card.js, checked
   by test_room_overview.py): Home Assistant's time zone (the house's, where the E32 and its program live), the viewer's
   12/24-hour choice (a 12-hour clock without a leading zero: "5:00 PM"); a moment today as its time, the day before or
   after as "yesterday 14:05" / "tomorrow 14:30" in the viewer's language, further away with its date ("Sat 14 Nov,
   14:30"): a weekday alone is ambiguous after six days, and a holiday can end months ahead. */
const clockLocale = hass => hass?.locale?.language || hass?.language || 'en';
const clockZone = hass => {
 const zone = hass?.config?.time_zone;
 if (typeof zone !== 'string' || !zone) return undefined;
 try { new Intl.DateTimeFormat('en', {timeZone: zone}); return zone; } catch (e) { return undefined; }
};
const clockHour12 = hass => {
 const chosen = ({'12': true, '24': false})[hass?.locale?.time_format];
 if (chosen !== undefined) return chosen;
 try { return /h1[12]/.test(new Intl.DateTimeFormat(clockLocale(hass), {hour: 'numeric'}).resolvedOptions().hourCycle); } catch (e) { return false; }
};
const clockOptions = hass => {
 const hour12 = clockHour12(hass);
 return {hour: hour12 ? 'numeric' : '2-digit', minute: '2-digit', hour12, timeZone: clockZone(hass)};
};
// The time of day of ms ("14:30", "2:30 PM").
const clockTime = (hass, ms) => {
 try { return new Date(ms).toLocaleTimeString(clockLocale(hass), clockOptions(hass)); } catch (e) { return new Date(ms).toISOString().slice(11, 16); }
};
// The day number of ms in the house's zone (days since 1970), to compare calendar days.
const clockDay = (hass, ms) => {
 try {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {timeZone: clockZone(hass), year: 'numeric', month: 'numeric', day: 'numeric'})
   .formatToParts(new Date(ms)).map(({type, value}) => [type, Number(value)]));
  return Math.round(Date.UTC(p.year, p.month - 1, p.day) / 86400000);
 } catch (e) { return Math.floor(ms / 86400000); }
};
// A moment (an ISO text or ms) for a sentence: "14:30", "tomorrow 14:30", "Sat 14 Nov, 14:30"; '' when not a time.
const clockMoment = (hass, value, now = Date.now()) => {
 const ms = typeof value === 'number' ? value : typeof value === 'string' ? Date.parse(value) : NaN;
 if (!Number.isFinite(ms)) return '';
 const days = clockDay(hass, ms) - clockDay(hass, now), time = clockTime(hass, ms);
 if (days === 0) return time;
 if (Math.abs(days) === 1) {
  try {
   const word = new Intl.RelativeTimeFormat(clockLocale(hass), {numeric: 'auto'}).format(days, 'day');
   // Polish "do"/"od"/"na" would need the genitive ("do jutra"): the time first keeps every sentence right ("do 06:30 jutro").
   return /^pl\b/.test(clockLocale(hass)) ? time + ' ' + word : word + ' ' + time;
  } catch (e) { /* older browser */ }
 }
 try { return new Date(ms).toLocaleString(clockLocale(hass), {weekday: 'short', day: 'numeric', month: 'short', ...clockOptions(hass)}); }
 catch (e) { return new Date(ms).toISOString().slice(0, 16).replace('T', ' '); }
};
/* clock: end */
// A moment in a sentence (Back door open since 14:05; Holiday until Sat 14 Nov, 14:30): the shared clock.
const moment = (hass, iso) => clockMoment(hass, iso);

class OpenThermostatRoomStatus extends HTMLElement {
 constructor() { super(); this.attachShadow({mode: 'open'}); this._key = null; }
 setConfig(config) {
  if (!config || typeof config.entity !== 'string' || !config.entity.startsWith('sensor.'))
   throw new Error('This card needs the Reason sensor of an OpenThermostat room (entity: sensor.…); the OpenThermostat dashboard adds it for you.');
  this._config = config; this._key = null;
  if (this._hass) this.render();
 }
 set hass(hass) {
  this._hass = hass;
  // Only a new state of its own entities, language or theme redraws; Home Assistant sets hass on every change in the house.
  const config = this._config || {}, states = hass?.states || {};
  const key = [states[config.entity], states[config.smart], states[config.mode], locale(hass), darkOf(hass),
   hass?.locale?.time_format, states[this.climate()]];
  if (this._key && key.every((v, i) => v === this._key[i])) return;
  this._key = key; this.render();
 }
 getCardSize() { return 3; }
 getGridOptions() { return {columns: 12, min_columns: 6}; }
 // The room thermostat: the climate entity on the Reason sensor's device (looked up again when the registry changes).
 climate() {
  const all = this._hass?.entities;
  if (this._found?.[0] !== all) {
   const device = all?.[this._config?.entity]?.device_id;
   this._found = [all, device && Object.values(all).find(e => e.device_id === device && e.entity_id.startsWith('climate.'))?.entity_id];
  }
  return this._found[1];
 }
 own(key, values = {}) {
  return (TEXT[lang(this._hass)][key] ?? TEXT.en[key]).replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all);
 }
 // "Resets at 22:00 to 14 °C" / "At 23:00 to Heat along only"; '' without a next reset time. The time as the step's.
 reset() {
  const hass = this._hass, a = hass?.states?.[this.climate()]?.attributes || {}, v = a.next_reset_value;
  const t = RESET[lang(hass)], state = ['active', 'follow', 'inactive'].indexOf(v);
  const time = moment(hass, a.next_reset).replace(/\s/g, ' '), degree = degrees(hass, typeof v === 'string' ? Number(v) || null : v);
  if (!time || (state < 0 && degree === null)) return '';
  return together(t[state < 0 ? 0 : 1].replace('{time}', time).replace('{value}', state < 0 ? degree + ' °C' : t[state + 2]));
 }
 _text(key, values) {
  try { const text = this._hass?.localize?.(KEY + key, values); return typeof text === 'string' ? text : ''; } catch (e) { return ''; }
 }
 // The room's state for its label: Summer while the house is in summer mode; else the room thermostat's (Off, Heat along
 // only as its preset, On); without a thermostat the reason's (off, follow, else on); null for a reason the card does
 // not know and no thermostat.
 roomState(st) {
  const states = this._hass?.states || {}, climate = states[this.climate()], c = climate?.attributes || {};
  if (st.state === 'summer' || c.reason === 'summer' || states[this._config.mode]?.state === 'summer') return 'summer';
  if (climate && ['off', 'heat', 'auto'].includes(climate.state)) return climate.state === 'off' ? 'off' : c.preset_mode === 'heat_along' ? 'follow' : 'on';
  if (st.state === 'off' || st.state === 'follow') return st.state;
  return Object.hasOwn(CHIP, st.state) ? 'on' : null;
 }
 // What it does now: the sentence with its values formatted for this viewer; the reason's short word where the sentence
 // would repeat the figures beside it; the summer line; a plain sentence for a key the card does not know.
 sentence(st) {
  const a = st.attributes || {}, v = a.values && typeof a.values === 'object' ? a.values : {}, hass = this._hass;
  if (st.state === 'summer') return this._text('line.state.summer') || this.own('summer_line');
  if (!(Object.hasOwn(CHIP, st.state))) return this._text('line.state.' + a.line) || this.own('unknown');
  if (RESTATED.has(st.state)) return this._text('chip.state.' + st.state) || CHIP[st.state];
  const values = {contact: typeof v.contact === 'string' ? v.contact : '', since: moment(hass, v.since), time: moment(hass, v.time), until: moment(hass, v.until),
   temperature: degrees(hass, v.temperature, true) ?? '–', target: degrees(hass, v.target) ?? '–'};
  const line = typeof a.line === 'string' ? this._text('line.state.' + a.line, values) : '';
  if (line) return together(line);
  const english = (Object.hasOwn(LINE, a.line) && LINE[a.line]) || LINE[st.state];
  return english ? together(english.replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all)) : this._text('chip.state.' + st.state) || CHIP[st.state];
 }
 // The week program's step: "Comfort until 22:30, then Night 18.0 °C" (a level with its own temperature: "21.5 °C
 // until …"); '' without a next step. The time as the sentence's times (today plain, another day with its weekday).
 step(st) {
  const p = st.attributes?.program, hass = this._hass;
  if (!p || typeof p !== 'object' || typeof p.next_at !== 'string') return '';
  // The time kept on one line ("Sun 4:12 PM" never breaks before PM).
  const time = moment(hass, p.next_at).replace(/\s/g, ' '), now = degrees(hass, p.target, true), next = degrees(hass, p.next_target, true);
  if (!time || now === null || next === null) return '';
  const word = (key, values = {}) => {
   const text = this._text('program.state.' + key, values);
   return text || PROGRAM[key].replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all);
  };
  const level = key => ['comfort', 'eco', 'night', 'holiday'].includes(key) ? word(key) : '';
  const nowLevel = level(p.level), nextLevel = level(p.next_level);
  // A level by its name ("Comfort"), its next one with the temperature ("Night 18.0 °C"); a point without a level by its
  // temperature alone. The program's temperatures are the E32's, in °C.
  const deg = value => value + ' °C';
  return together(word('step', {level: nowLevel || deg(now), time, next: nextLevel ? nextLevel + ' ' + deg(next) : deg(next)}));
 }
 render() {
  const hass = this._hass, config = this._config, root = this.shadowRoot;
  if (!hass || !config) return;
  if (darkOf(hass)) this.setAttribute('data-theme', 'dark'); else this.removeAttribute('data-theme');
  const el = (tag, text, attrs = {}) => {
   const e = document.createElement(tag);
   if (text != null) e.textContent = text;
   for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
   return e;
  };
  const card = el('ha-card', null, {tabindex: '0', role: 'button'}), wrap = el('div', null, {class: 'wrap'}), st = hass.states?.[config.entity];
  const head = el('div', null, {class: 'head'}), titles = el('div', null, {class: 'titles'}), body = el('div', null, {class: 'body'});
  const type = el('span', null, {class: 'type', 'aria-hidden': 'true', 'data-type': TYPE[config.emitter] ? config.emitter : 'room'});
  type.append(svgIcon(TYPE[config.emitter] || 'thermostat', 24));
  if (config.name) titles.append(el('p', config.name, {class: 'name'}));
  head.append(type, titles);
  wrap.append(head, body);
  card.append(wrap);
  root.replaceChildren(el('style', STYLE), card);
  if (!st) {
   const words = hass.localize?.('ui.panel.lovelace.warning.entity_not_found', {entity: config.entity}) || this.own('missing', {entity: config.entity});
   body.append(el('p', words, {class: 'missing'}));
   return;
  }
  card.onclick = () => this.dispatchEvent(new CustomEvent('hass-more-info', {bubbles: true, composed: true, detail: {entityId: config.entity}}));
  card.onkeydown = e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); card.onclick(); } };
  if (st.state === 'unavailable' || st.state === 'unknown') {  // Home Assistant's own word for it
   let words = '';
   try { words = hass.formatEntityState?.(st) || ''; } catch (e) { words = ''; }
   body.append(el('p', words && words !== st.state ? words : this.own('unavailable'), {class: 'missing'}));
   return;
  }
  const a = st.attributes || {}, state = this.roomState(st);
  // The state as a status label in its colour, with its icon (Summer instead of the state while summer mode is on).
  if (state) {
   const [tone, glyph] = STATE[state], label = el('span', null, {class: 'label state tone-' + tone, 'data-state': state});
   label.append(svgIcon(glyph, 16), el('span', this.own(state)));
   titles.append(label);
  }
  const label = key => this._text(key + '.name') || FALLBACK[key];
  // Now, large; the target under it (not for a room that is off or in summer); for a screen reader both in one
  // sentence ("Now 20.6 °C, Target 22.5 °C").
  const now = degrees(hass, a.temperature, true), target = state === 'off' || state === 'summer' || st.state === 'off' ? null : degrees(hass, a.setpoint);
  const spoken = [now && `${label('temperature')} ${now} °C`, target && `${label('setpoint')} ${target} °C`].filter(Boolean).join(', ');
  const temps = el('div', null, {class: 'temps', ...(spoken ? {role: 'img', 'aria-label': spoken} : {})});
  const big = el('p', now ?? '–', {class: 'now' + (now ? '' : ' none'), 'data-now': ''});
  if (now) big.append(el('span', ' °C', {class: 'unit'}));
  temps.append(big);
  if (target) temps.append(el('p', together(`${label('setpoint')} ${target} °C`), {class: 'target', 'data-target': ''}));
  head.append(temps);
  // What it does now, then the week program's step after a middle dot; the next reset time in its own muted line.
  const why = el('p', this.sentence(st), {class: 'why', 'data-reason': st.state, ...(a.window === 'open' || a.window === 'pending' ? {'data-window': a.window} : {})});
  const step = this.step(st);
  if (step) why.append(el('span', ' · '), el('span', step, {class: 'step', 'data-step': ''}));
  body.append(why);
  const reset = state === 'summer' ? '' : this.reset();
  if (reset) body.append(el('p', reset, {class: 'reset', 'data-reset': ''}));
  // Labels only for what deviates: this room's Smart warm-up against the house switch (E32 1.4, #8: the Reason sensor's
  // smart_warm_up is the room's own in effect), a radiator valve with a problem. The valves' opening as a quiet line.
  const foot = el('div', null, {class: 'foot'}), flag = (kind, tone, glyph, words) => {
   const l = el('span', null, {class: 'label tone-' + tone, 'data-label': kind});
   l.append(svgIcon(glyph, 16), el('span', words));
   foot.append(l);
   return l;
  };
  const house = config.smart ? hass.states?.[config.smart]?.state : undefined, room = a.smart_warm_up;
  if (state === 'on' && (room === 'on' || room === 'off') && (house === 'on' || house === 'off') && room !== house)
   flag('smart', 'rest', 'clock-fast', room === 'off' ? this.own('smart_off') : this._text('card.state.smart_on') || this.own('smart_on'));
  if (typeof a.valve_position === 'number' && Number.isFinite(a.valve_position)) {
   const words = together(label('valve_position') + ': ' + Math.round(a.valve_position) + ' %');
   if (a.valve_problem) flag('valves', 'attention', 'valve-closed', words).setAttribute('data-valves', 'problem');
   else {
    const meta = el('span', null, {class: 'meta', 'data-valves': ''});
    meta.append(svgIcon('valve', 16), el('span', words));
    foot.append(meta);
   }
  }
  // 1.4: "Settings" opens this room in the settings view (Home Assistant's navigation: the path and location-changed).
  const id = typeof config.room_id === 'string' && config.room_id ? config.room_id : a.room_id;
  if (typeof config.settings_path === 'string' && config.settings_path && typeof id === 'string' && id) {
   const go = el('button', this._text('card.state.settings') || WORDS.settings, {type: 'button', class: 'settings', 'data-settings': ''});
   go.addEventListener('click', e => {
    e.stopPropagation();
    try { history.pushState(null, '', config.settings_path + '#room/' + encodeURIComponent(id)); } catch (err) { return; }
    window.dispatchEvent(new CustomEvent('location-changed', {detail: {replace: false}}));
   });
   go.addEventListener('keydown', e => e.stopPropagation());  // Enter and Space press this button, not the card
   foot.append(go);
  }
  if (foot.childElementCount) wrap.append(foot);
 }
}
// Other dashboard cards (HACS resources) may later replace window.customElements with a scoped-registry
// polyfill whose get() does not see elements defined before it; Home Assistant then reports "Custom element
// doesn't exist". So: define now, and again (a fresh subclass) whenever the registry in use lacks the element.
// Never throws. (The same guard as e32-week-card.js.)
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
ensureDefined('openthermostat-room-status', OpenThermostatRoomStatus);
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === 'openthermostat-room-status'))
 window.customCards.push({type: 'openthermostat-room-status', name: 'OpenThermostat room status', description: 'One E32 room: now, its state, and what it does now.'});
