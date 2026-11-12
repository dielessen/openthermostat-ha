/* The Rooms view's room card (OpenThermostat 1.4.3, custom:openthermostat-room; HA-DASHBOARD-ONTWERP-1.4.3.nl.md §3.2,
   §3.2b, §3.3, §6, §7; CONTRACT-1.4.3 §2). One card per room, the big brother of the Overview's room status card
   (room-status-card.js): the same words, the same design tokens (CONTRACT-1.4.1 §8), the same clock, the same history
   call as the house card. From top to bottom:
   1. the head: the heating type in a grey circle, the room's name and its state as a status label (On orange, Heat
      along only amber, Off grey, Summer grey) with labels only for deviations (a window or door open, Smart warm-up
      off or on for this room against the house switch, a radiator valve with a problem);
   2. what it does now: the Reason sensor's sentence and the week program's step;
   3. the temperature: a small arc with the measured temperature and the target as a dot (a tap opens Home
      Assistant's thermostat dialog), the target with − and + in steps of 0.5 °C on the room's thermostat (on Heat
      along only "Heat along up to" on the room's temperature without a week program, the number the room screen
      writes too), the reset time or what the room does once it may heat again; an Off room only its temperature and
      its source, compact;
   3b. the presets of the room's thermostat (Program · Comfort · Eco · Night · Boost, those it lists) and the state
      (On · Heat along only · Off), "Switch on now" on an Off room; in summer mode a tap says why nothing changes;
   4. today: the week program as a bar from 0 to 24 h in the colours of its levels (the Reason sensor's ``today``),
      Smart warm-up's early start hatched before its switch time (the room's "Start Smart warm-up" sensor), the
      hour marks and "now";
   5. the last 24 hours: the measured temperature (blue) and the target (orange, steps) as a small line, from Home
      Assistant's history (history/history_during_period: at most every 5 minutes and when the room's state
      changes); a tap opens the history;
   6. the devices, two tiles per row, each with an icon, its name and one line: the room's thermometer, its radiator
      valves with the E32's finding (``held``) as a second line, windows and doors, persons, the setting device;
   7. the footer: Week program and Settings (the room's screen in the dashboard's Settings tab).
   Only Home Assistant is read; no polling (one timer moves "now" once a minute and stops when the card leaves the
   page). A value that is missing is a quiet word or the block is not drawn: never a raw key, "unknown" or
   "unavailable". Icons: Material Design Icons (v7.4.47, Apache 2.0) as inline SVG. */
const KEY = 'component.open_thermostat.entity.sensor.room_reason.state_attributes.';
// The reason in one word and its sentence: the English last resorts, key for key as strings.json (as room-status-card.js).
const CHIP = {off: 'Off', window_open: 'Paused', window_pending: 'Pausing soon', no_measurement: 'No measurement', hot_water: 'Waiting',
 boiler_pause: 'Waiting', warm_up: 'Warming up', away_return: 'Warming up', holiday: 'Holiday', away: 'Away', room_away: 'Away',
 house_away: 'Away', boost: 'Boost', temporary: 'Temporary', follow: 'Heats along', heating: 'Heating', wants_heat: 'Wants heat', warm_enough: 'At temperature', summer: 'Summer'};
const LINE = {off: 'Frost protection only (room off)', off_until: 'Off until {until}, then on again',
 off_until_follow: 'Off until {until}, then heating along again', window_open: 'Paused: a window or door is open',
 window_open_contact: 'Paused: {contact} open since {since}', window_open_window: 'Paused: a window is open',
 window_open_door: 'Paused: a door is open', window_pending: 'A window or door is open: the room pauses soon',
 window_pending_contact: '{contact} open: the room pauses soon', window_pending_window: 'A window is open: the room pauses soon',
 window_pending_door: 'A door is open: the room pauses soon', no_measurement: 'No measurement: this room does not ask for heat',
 hot_water: 'Waiting: the boiler is making hot water', boiler_pause: 'Burner resting before the next start',
 away_return: 'Warming up for your return', holiday: 'Holiday until {until} ({target} °C)', away: 'Away: the house is set to away ({target} °C)',
 room_away: 'Away: nobody of this room is home ({target} °C)', house_away: 'Away: everyone is away ({target} °C)', boost: 'Boost active',
 boost_until: 'Boost until {until}', temporary: 'Temporarily {target} °C', temporary_until: 'Temporarily {target} °C until {until}',
 follow: 'Heats along: it never asks for heat itself', follow_frost: 'Heats along; below 8 °C it asks for heat',
 heating: 'Heating: {temperature} → {target} °C', wants_heat: 'Wants heat: {temperature} → {target} °C',
 warm_enough: 'Warm enough: {temperature} °C (target {target} °C)', no_heat_needed: 'No heat needed',
 warm_up: 'Smart warm-up: heating early for {time} ({target} °C)', warm_up_for: 'Warming up for {time}',
 summer: 'Summer mode: the heating stays off until you switch this off; hot water and frost protection stay.'};
const PROGRAM = {comfort: 'Comfort', eco: 'Eco', night: 'Night', holiday: 'Holiday', step: '{level} until {time}, then {next}'};
const RESTATED = new Set(['heating', 'wants_heat', 'warm_enough']);
const PAUSED = new Set(['window_open', 'window_pending']);
const AWAY = new Set(['away', 'room_away', 'house_away', 'holiday', 'away_return']);
// The card's own words (1.4.3, glossary block 1.4.3 ROOM-CARD), EN/NL; the room states as the room's settings say them.
const TEXT = {
 en: {on: 'On', follow: 'Heat along only', off: 'Off', summer: 'Summer', smart_off: 'Smart warm-up off', smart_on: 'Smart warm-up on',
  window_open: 'Window open', door_open: 'Door open', valve_problem: 'Valve needs attention', target: 'Target', along_to: 'Heat along up to',
  again_window: 'Heats again once the window is closed', again_door: 'Heats again once the door is closed',
  again_contact: 'Heats again once it is closed', none: 'Program', comfort: 'Comfort', eco: 'Eco', sleep: 'Night', boost: 'Boost',
  state: 'State', presets: 'Presets', program_back: 'Back to the week program', fixed_back: 'Back to the temperature without a week program',
  on_back: 'Switches the room back to On', house_levels: 'Comfort, Eco and Night use the room defaults', switch_on: 'Switch on now', summer_refused: 'Summer mode is on: switch it off first.',
  today: 'Today', smart_start: 'Smart warm-up starts {time} · warm at {at}', smart_start_plain: 'Smart warm-up starts {time}',
  no_start_window: 'No early start: window open', no_start_away: 'No early start: away', no_program: 'No week program',
  now: 'now', smart: 'Smart warm-up', last_day: 'Last 24 hours', measured: 'Measured', devices: 'Devices', week: 'Week program', settings: 'Settings',
  open_pct: '{n} % open', battery: 'battery {n} %', set_to: 'set to {t} °C', put_back: 'put back to {t} °C', put_back_plain: 'put back',
  own_schedule: 'running its own program', off_by_user: 'switched off by you', gave_up: 'not responding to the E32',
  offline: 'not reporting', low_battery: 'battery low', too_large: 'message too large ({kb} KB)', too_large_plain: 'message too large', open_since: 'open since {time}', is_open: 'open', closed: 'closed',
  home: 'home', away: 'away', setting_device: 'setting device · set to {t} °C', setting_plain: 'setting device', pump_on: 'on',
  pump_off: 'off', no_reading: 'no reading', thermometer: 'Thermometer', bluetooth: 'Bluetooth sensor', gateway: 'Valve {id} on BLU Gateway {n}',
  waiting: 'The E32 is not reporting yet.', failed: 'That did not work: {reason}', missing: 'Entity not available: {entity}',
  unknown: 'The E32 reports something this card does not know yet',
  no_source: 'This room has no working temperature source. Choose a source to use it again, or remove the room if you no longer need it.',
  choose: 'Choose a source', remove: 'Remove room'},
 nl: {on: 'Aan', follow: 'Alleen meeverwarmen', off: 'Uit', summer: 'Zomer', smart_off: 'Slim opwarmen uit', smart_on: 'Slim opwarmen aan',
  window_open: 'Raam open', door_open: 'Deur open', valve_problem: 'Kraan met probleem', target: 'Doel', along_to: 'Meeverwarmen tot',
  again_window: 'Verwarmt weer zodra het raam dicht is', again_door: 'Verwarmt weer zodra de deur dicht is',
  again_contact: 'Verwarmt weer zodra het dicht is', none: 'Programma', comfort: 'Comfort', eco: 'Eco', sleep: 'Nacht', boost: 'Boost',
  state: 'Stand', presets: 'Voorkeuzen', program_back: 'Terug naar het weekprogramma', fixed_back: 'Terug naar de temperatuur zonder weekprogramma',
  on_back: 'Zet de ruimte weer op Aan', house_levels: 'Comfort, Eco en Nacht gebruiken de standaardwaarden voor ruimtes', switch_on: 'Nu aanzetten', summer_refused: 'Zomerstand staat aan: zet die eerst uit.',
  today: 'Vandaag', smart_start: 'Slim opwarmen start {time} · warm om {at}', smart_start_plain: 'Slim opwarmen start {time}',
  no_start_window: 'Geen vroege start: raam open', no_start_away: 'Geen vroege start: afwezig', no_program: 'Geen weekprogramma',
  now: 'nu', smart: 'Slim opwarmen', last_day: 'Afgelopen 24 uur', measured: 'Gemeten', devices: 'Apparaten', week: 'Weekprogramma', settings: 'Instellen',
  open_pct: '{n} % open', battery: 'batterij {n} %', set_to: 'staat op {t} °C', put_back: 'teruggezet naar {t} °C', put_back_plain: 'teruggezet',
  own_schedule: 'eigen programma', off_by_user: 'door jou uitgezet', gave_up: 'geeft niet thuis',
  offline: 'meldt zich niet', low_battery: 'batterij bijna leeg', too_large: 'bericht te groot ({kb} KB)', too_large_plain: 'bericht te groot', open_since: 'open sinds {time}', is_open: 'open', closed: 'dicht',
  home: 'thuis', away: 'weg', setting_device: 'instelapparaat · staat op {t} °C', setting_plain: 'instelapparaat', pump_on: 'aan',
  pump_off: 'uit', no_reading: 'geen meting', thermometer: 'Thermometer', bluetooth: 'Bluetooth-sensor', gateway: 'Kraan {id} aan BLU Gateway {n}',
  waiting: 'De E32 meldt zich nog niet.', failed: 'Dat lukte niet: {reason}', missing: 'Entiteit niet beschikbaar: {entity}',
  unknown: 'De E32 meldt iets wat deze kaart nog niet kent',
  no_source: 'Deze ruimte heeft geen werkende temperatuurbron. Kies een bron om de ruimte weer te gebruiken, of verwijder hem als je hem niet meer nodig hebt.',
  choose: 'Kies een bron', remove: 'Ruimte verwijderen'}};
// The next reset time's line: [a temperature, a state, On, Heat along only, Off], as the room status card says it.
const RESET = {en: ['Resets at {time} to {value}', 'At {time} to {value}', 'On', 'Heat along only', 'Off'],
 nl: ['Om {time} terug naar {value}', 'Om {time} naar {value}', 'Aan', 'Alleen meeverwarmen', 'Uit']};
// The status label of each room state: its tone (orange heats, amber heats along, grey rest/off/summer) and icon.
const STATE = {on: ['heat', 'fire'], follow: ['along', 'fire-circle'], off: ['rest', 'power'], summer: ['rest', 'white-balance-sunny']};
const TYPE = {radiator: 'radiator', floor: 'heating-coil'};
// The presets of the room thermostat, in the design's order (e32_comfort.PRESETS); Heat along only is the state menu's.
const PRESETS = ['none', 'comfort', 'eco', 'sleep', 'boost'];
// The E32's finding on a driven valve (e32_valves.HELD): its words and tone; "ok" says nothing.
const HELD = {put_back: 'along', own_schedule: 'along', off_by_user: 'along', gave_up: 'attention'};
const GATEWAY = /^g([1-9][0-9]?):(2[0-9]{2})$/;
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
 'clock-fast': 'M15,4A8,8 0 0,1 23,12A8,8 0 0,1 15,20A8,8 0 0,1 7,12A8,8 0 0,1 15,4M15,6A6,6 0 0,0 9,12A6,6 0 0,0 15,18A6,6 0 0,0 21,12A6,6 0 0,0 15,6M14,8H15.5V11.78L17.83,14.11L16.77,15.17L14,12.4V8M2,18A1,1 0 0,1 1,17A1,1 0 0,1 2,16H5.83C6.14,16.71 6.54,17.38 7,18H2M3,13A1,1 0 0,1 2,12A1,1 0 0,1 3,11H5.05L5,12L5.05,13H3M4,8A1,1 0 0,1 3,7A1,1 0 0,1 4,6H7C6.54,6.62 6.14,7.29 5.83,8H4Z',
 'thermometer': 'M15 13V5A3 3 0 0 0 9 5V13A5 5 0 1 0 15 13M12 4A1 1 0 0 1 13 5V8H11V5A1 1 0 0 1 12 4Z',
 'window': 'M21 20V2H3V20H1V23H23V20M19 4V11H17V4M5 4H7V11H5M5 20V13H7V20M9 20V4H15V20M17 20V13H19V20Z',
 'door': 'M12,3C10.89,3 10,3.89 10,5H3V19H2V21H22V19H21V5C21,3.89 20.11,3 19,3H12M12,5H19V19H12V5M5,11H7V13H5V11Z',
 'account': 'M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z',
 'bluetooth': 'M14.88,16.29L13,18.17V14.41M13,5.83L14.88,7.71L13,9.58M17.71,7.71L12,2H11V9.58L6.41,5L5,6.41L10.59,12L5,17.58L6.41,19L11,14.41V22H12L17.71,16.29L13.41,12L17.71,7.71Z',
 'plug': 'M16,7V3H14V7H10V3H8V7H8C7,7 6,8 6,9V14.5L9.5,18V21H14.5V18L18,14.5V9C18,8 17,7 16,7Z',
 'chevron-down': 'M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z',
 'minus': 'M19,13H5V11H19V13Z',
 'plus': 'M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z',
 'alert': 'M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z'};
const SVG = 'http://www.w3.org/2000/svg';
const make = (tag, attrs = {}, text) => {
 const e = tag.startsWith('svg:') ? document.createElementNS(SVG, tag.slice(4)) : document.createElement(tag);
 for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined && v !== false) e.setAttribute(k, v);
 if (text !== undefined && text !== null) e.textContent = text;
 return e;
};
const svgIcon = (name, size) => {
 const s = make('svg:svg', {viewBox: '0 0 24 24', width: size, height: size, 'aria-hidden': 'true', focusable: 'false', 'data-icon': 'mdi:' + name});
 s.append(make('svg:path', {d: ICONS[name], fill: 'currentColor'}));
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
--ot-raised:color-mix(in srgb,var(--ot-fg) 2.5%,var(--ot-bg));--ot-night:color-mix(in srgb,var(--ot-water-ink) 22%,var(--ot-rest-fill));
color:var(--ot-fg);font-family:var(--paper-font-body1_-_font-family,Roboto,'Segoe UI',Arial,sans-serif)}
:host([data-theme="dark"]){--ot-heat-ink:#f0a060;--ot-heat-fill:rgba(240,160,96,.18);--ot-along-ink:#e6c35c;--ot-along-fill:rgba(230,195,92,.18);
--ot-water-ink:#7fb3f0;--ot-water-fill:rgba(127,179,240,.18);--ot-rest-ink:#b0b4ba;--ot-rest-fill:rgba(176,180,186,.18);
--ot-attention-ink:#f2857c;--ot-attention-fill:rgba(242,133,124,.18);--ot-raised:color-mix(in srgb,var(--ot-fg) 5%,var(--ot-bg));
--ot-night:color-mix(in srgb,var(--ot-water-ink) 28%,transparent)}
ha-card{display:block;box-sizing:border-box;height:100%;padding:16px;border-radius:var(--ot-radius);background:var(--ot-bg);color:var(--ot-fg)}
p{margin:0}svg{display:block;flex:none}button,select{font:inherit;color:inherit}
.wrap{container:room/inline-size;display:flex;flex-direction:column;gap:16px}
.head{display:flex;align-items:center;gap:12px;min-width:0}
.type{flex:none;display:flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:50%;background:var(--ot-rest-fill);color:var(--ot-rest-ink)}
.titles{flex:1 1 auto;min-width:0;display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}
.name{margin-right:auto;font-size:var(--ot-text-l);line-height:var(--ot-line-l);font-weight:500;overflow-wrap:anywhere}
.labels{display:flex;flex-wrap:wrap;gap:6px}
.label{display:inline-flex;align-items:center;gap:6px;max-width:100%;box-sizing:border-box;min-height:26px;padding:2px 10px;border-radius:13px;
font-size:var(--ot-text-s);line-height:var(--ot-line-s);font-weight:500;background:var(--fill);color:var(--ink);overflow-wrap:anywhere}
.tone-heat{--ink:var(--ot-heat-ink);--fill:var(--ot-heat-fill)}.tone-along{--ink:var(--ot-along-ink);--fill:var(--ot-along-fill)}
.tone-rest{--ink:var(--ot-rest-ink);--fill:var(--ot-rest-fill)}.tone-attention{--ink:var(--ot-attention-ink);--fill:var(--ot-attention-fill)}
.why{font-size:var(--ot-text-m);line-height:var(--ot-line-m);overflow-wrap:anywhere}
.muted,.note{font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2);overflow-wrap:anywhere}
.temp{display:flex;align-items:center;gap:16px;min-width:0}
.arc{flex:none;width:128px;padding:0;border:0;background:none;border-radius:var(--ot-radius);cursor:pointer}
.arc svg{width:128px;height:108px}.arc .track{stroke:var(--ot-rest-fill)}.arc .fillarc{stroke:var(--ink)}
.arc .dot{fill:var(--ot-bg);stroke:var(--ot-heat-ink)}.arc .big{fill:var(--ot-fg);font-size:28px;font-weight:300}.arc .unit{fill:var(--ot-fg-2);font-size:13px}
.arc .none{fill:var(--ot-fg-2)}
.ctl{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;gap:4px}
.stepper{display:flex;align-items:center;gap:4px}
.step{flex:none;display:flex;align-items:center;justify-content:center;width:var(--ot-touch);height:var(--ot-touch);padding:0;border:1px solid var(--ot-line);
border-radius:50%;background:var(--ot-raised);cursor:pointer;transition:background-color var(--ot-motion)}
.step:hover:not(:disabled){background:color-mix(in srgb,var(--ot-accent) 10%,var(--ot-bg))}.step:disabled{opacity:.4;cursor:default}
.val{flex:1 1 auto;min-width:0;text-align:center;font-size:28px;line-height:34px;font-weight:300;font-variant-numeric:tabular-nums;white-space:nowrap}
.val .unit{font-size:var(--ot-text-m);color:var(--ot-fg-2)}
.compact{display:flex;align-items:baseline;flex-wrap:wrap;gap:4px 8px;cursor:pointer}
.compact .now{font-size:var(--ot-text-xl);line-height:var(--ot-line-xl);font-weight:300;font-variant-numeric:tabular-nums;white-space:nowrap}
.modes{display:flex;flex-wrap:nowrap;align-items:center;gap:0 6px;margin:0 -4px;padding:0 4px;overflow-x:auto;overscroll-behavior-x:contain;scrollbar-width:none}
.modes::-webkit-scrollbar{display:none}
.presets{display:flex;flex-direction:column;min-width:0}
.chip{flex:none;min-height:var(--ot-touch);padding:0;border:0;background:none;cursor:pointer}
.chip span{display:inline-flex;align-items:center;height:30px;padding:0 8px;box-sizing:border-box;border:1px solid var(--ot-line);border-radius:15px;
font-size:var(--ot-text-s);font-weight:500;white-space:nowrap;transition:background-color var(--ot-motion)}
.chip:focus-visible{outline:none}.chip:focus-visible span{outline:2px solid var(--ot-accent);outline-offset:2px}
.chip:hover span{background:color-mix(in srgb,var(--ot-accent) 10%,transparent)}
.chip[aria-pressed="true"] span{background:var(--ot-fill);border-color:transparent;color:var(--ot-on-accent)}
.menu{position:relative;flex:none;display:flex;align-items:center;max-width:100%;color:var(--ink)}
.menu select{appearance:none;-webkit-appearance:none;min-height:var(--ot-touch);max-width:100%;padding:0 34px 0 36px;border:0;border-radius:22px;field-sizing:content;
background:var(--fill);color:var(--ink);font-size:var(--ot-text-s);font-weight:500;cursor:pointer}
.menu .lead{position:absolute;left:12px;pointer-events:none}
.menu .chev{position:absolute;right:10px;pointer-events:none}
.primary{min-height:var(--ot-touch);padding:0 16px;border:0;border-radius:var(--ot-radius);background:var(--ot-fill);color:var(--ot-on-accent);
font-size:var(--ot-text-m);font-weight:500;cursor:pointer}
.error{font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-attention-ink)}
.block{display:flex;flex-direction:column;gap:6px;min-width:0}
.bar-box{position:relative;margin-top:2px}
.bar{position:relative;height:16px;border-radius:8px;overflow:hidden;background:var(--ot-rest-fill)}
.blk{position:absolute;top:0;bottom:0;box-shadow:inset -1px 0 0 var(--ot-bg)}
.lv-comfort{background:var(--ot-heat-fill)}.lv-eco{background:var(--ot-along-fill)}.lv-night{background:var(--ot-night)}.lv-own{background:var(--ot-rest-fill)}
:host(:not([data-theme="dark"])) .lv-comfort{background:color-mix(in srgb,var(--ot-heat-ink) 30%,var(--ot-heat-fill))}
:host(:not([data-theme="dark"])) .lv-eco{background:color-mix(in srgb,var(--ot-along-ink) 22%,var(--ot-along-fill))}
:host([data-theme="dark"]) .lv-comfort{background:color-mix(in srgb,var(--ot-heat-ink) 45%,var(--ot-bg))}
:host([data-theme="dark"]) .lv-eco{background:color-mix(in srgb,var(--ot-along-ink) 38%,var(--ot-bg))}
:host([data-theme="dark"]) .lv-night{background:color-mix(in srgb,var(--ot-water-ink) 32%,var(--ot-bg))}
.early{position:absolute;top:0;bottom:0;background:repeating-linear-gradient(135deg,var(--ot-heat-ink) 0 2px,transparent 2px 6px);opacity:.55}
.nowmark{position:absolute;top:-4px;bottom:-4px;width:2px;margin-left:-1px;border-radius:1px;background:var(--ot-fg)}
.ticks{position:relative;height:18px;font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2);font-variant-numeric:tabular-nums}
.ticks span{position:absolute;top:0;transform:translateX(-50%);white-space:nowrap}.ticks span:first-child{transform:none}.ticks span:last-child{transform:translateX(-100%)}
.legend{display:flex;flex-wrap:wrap;gap:2px 12px;margin:0;padding:0;list-style:none;font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2)}
.legend li{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}.legend i{width:10px;height:10px;border-radius:3px;flex:none}
.legend .early-key{background:repeating-linear-gradient(135deg,var(--ot-heat-ink) 0 2px,var(--ot-heat-fill) 2px 4px)}
.spark{display:block;width:100%;padding:0;border:0;background:none;cursor:pointer;border-radius:var(--ot-radius-s)}
.spark svg{width:100%;height:64px;overflow:visible}.spark .measured{fill:none;stroke:var(--ot-water-ink);stroke-width:2;stroke-linejoin:round;stroke-linecap:round;vector-effect:non-scaling-stroke}
.spark .target{fill:none;stroke:var(--ot-heat-ink);stroke-width:1.5;vector-effect:non-scaling-stroke}
.spark .base{fill:var(--ot-raised)}
.head-row{display:flex;align-items:baseline;justify-content:space-between;flex-wrap:wrap;gap:2px 12px}
.keys{display:inline-flex;gap:12px}.keys span{display:inline-flex;align-items:center;gap:6px}.keys i{width:12px;height:2px;border-radius:1px}
.keys .m{background:var(--ot-water-ink)}.keys .t{background:var(--ot-heat-ink)}
.tiles{display:grid;grid-template-columns:minmax(0,1fr);gap:8px}
.tile{display:flex;align-items:flex-start;gap:10px;min-width:0;min-height:var(--ot-touch);box-sizing:border-box;padding:10px 12px;border:0;
border-radius:var(--ot-radius-s);background:var(--ot-raised);text-align:left;cursor:pointer}
.tile:hover{background:color-mix(in srgb,var(--ot-accent) 7%,var(--ot-raised))}
.tile>svg{margin-top:1px;color:var(--ot-rest-ink)}.tile.warn>svg{color:var(--ot-attention-ink)}
.tile .txt{display:flex;flex-direction:column;min-width:0;flex:1 1 auto}
.tile .tn,.tile .tv,.tile .t2{overflow-wrap:anywhere}
.tile .tn{font-size:var(--ot-text-m);line-height:var(--ot-line-m);font-weight:500}
.tile .tv{font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2)}
.tile .t2{font-size:var(--ot-text-s);line-height:var(--ot-line-s);font-weight:500;color:var(--ink)}
.tile .low{color:var(--ot-attention-ink);font-weight:500}
.foot{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:4px;margin:-8px -8px -8px 0}
.text{min-height:var(--ot-touch);padding:0 12px;border:0;border-radius:var(--ot-radius);background:none;font-size:var(--ot-text-m);font-weight:500;
cursor:pointer;color:var(--ot-link);transition:background-color var(--ot-motion)}
.text:hover{background:color-mix(in srgb,var(--ot-accent) 10%,transparent)}
button:focus-visible,select:focus-visible,.tile:focus-visible{outline:2px solid var(--ot-accent);outline-offset:2px}
@container room (min-width:440px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}}
@container room (max-width:340px){.temp{gap:8px}.arc,.arc svg{width:112px}.arc svg{height:96px}.val{font-size:26px}}`;

const locale = hass => hass?.locale?.language || hass?.language || 'en';
const lang = hass => /^nl\b/.test(locale(hass)) ? 'nl' : 'en';
const darkOf = hass => {
 if (typeof hass?.themes?.darkMode === 'boolean') return hass.themes.darkMode;
 try { return window.matchMedia('(prefers-color-scheme: dark)').matches; } catch (e) { return false; }
};
const NBSP = ' ';
// A figure and its unit stay together on a narrow card ("21,2 °C" never breaks before the unit).
const together = text => String(text).replace(/ (°C|%)/g, NBSP + '$1');
const finite = value => typeof value === 'number' && Number.isFinite(value);
const numeric = value => { const n = typeof value === 'string' && value.trim() !== '' ? Number(value) : value; return finite(n) ? n : null; };
const known = st => !!st && typeof st.state === 'string' && !['unknown', 'unavailable', ''].includes(st.state);
const id = value => typeof value === 'string' && value.includes('.') ? value : null;
const degrees = (hass, value, fixed) => finite(value)
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
   // "tomorrow" in the card's own language (English for a language it has no words for), as the sentence around it.
   const word = new Intl.RelativeTimeFormat(lang(hass), {numeric: 'auto'}).format(days, 'day');
   return word + ' ' + time;
  } catch (e) { /* older browser */ }
 }
 try { return new Date(ms).toLocaleString(clockLocale(hass), {weekday: 'short', day: 'numeric', month: 'short', ...clockOptions(hass)}); }
 catch (e) { return new Date(ms).toISOString().slice(0, 16).replace('T', ' '); }
};
/* clock: end */
const moment = (hass, iso) => clockMoment(hass, iso);
// Minutes since the house's midnight of ms (Home Assistant's time zone): the today bar's scale.
const dayMinute = (hass, ms) => {
 try {
  const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {timeZone: clockZone(hass), hourCycle: 'h23', hour: 'numeric', minute: 'numeric'})
   .formatToParts(new Date(ms)).map(({type, value}) => [type, Number(value)]));
  return (p.hour % 24) * 60 + p.minute;
 } catch (e) { const d = new Date(ms); return d.getHours() * 60 + d.getMinutes(); }
};
const minuteOf = text => { const m = /^(\d\d):(\d\d)$/.exec(String(text || '')); return m ? Number(m[1]) * 60 + Number(m[2]) : null; };
// Home Assistant's history of one entity as [{v: number, t: ms}] by time ("lc"/"lu" in seconds, or ISO texts).
const series = rows => (Array.isArray(rows) ? rows : []).map(row => {
 const seconds = numeric(row?.lc) ?? numeric(row?.lu);
 return {v: numeric(row?.s ?? row?.state), t: seconds !== null ? seconds * 1000 : Date.parse(row?.last_changed ?? row?.last_updated)};
}).filter(p => Number.isFinite(p.t)).sort((a, b) => a.t - b.t);
const BIN_MS = 10 * 60000, HISTORY_MS = 5 * 60000, DAY_MS = 86400000, TICK_MS = 60000, PENDING_MS = 15000, SEND_MS = 700;

class OpenThermostatRoom extends HTMLElement {
 constructor() {
  super(); this.attachShadow({mode: 'open'});
  this._key = null; this._history = null; this._fetched = 0; this._fetching = 0; this._seen = null; this._gen = 0;
  this._pending = null; this._send = null; this._error = ''; this._timer = null;
 }
 setConfig(config) {
  if (!config || !(id(config.reason) || id(config.climate) || id(config.temperature)))
   throw new Error('This card needs an OpenThermostat room (reason: sensor.…, climate: climate.… or temperature: sensor.…); the OpenThermostat dashboard adds it for you.');
  const list = value => (Array.isArray(value) ? value : []).map(id).filter(Boolean);
  const sensor = config.sensor && typeof config.sensor === 'object' ? config.sensor : {};
  this._config = {...config, reason: id(config.reason), climate: id(config.climate), temperature: id(config.temperature),
   setpoint: id(config.setpoint), heating_start: id(config.heating_start), state: id(config.state), valves: id(config.valves),
   valve_battery: id(config.valve_battery), valve_problem: id(config.valve_problem), fallback: id(config.fallback),
   sensor: {temperature: id(sensor.temperature), humidity: id(sensor.humidity), battery: id(sensor.battery)},
   contacts: list(config.contacts), persons: list(config.persons), sources: list(config.sources),
   setting_device: id(config.setting_device), pump: id(config.pump), mode: id(config.mode), smart: id(config.smart),
   battery_limit: finite(config.battery_limit) ? config.battery_limit : 20};
  this._key = null; this._history = null; this._fetched = 0; this._seen = null;
  if (this._hass) { this.render(); this.refresh(); }
 }
 set hass(hass) {
  this._hass = hass;
  if (!this._config) return;
  // Only a new state of its own entities, language, theme or clock choice redraws; Home Assistant sets hass on every change.
  const key = [...this.entities().map(e => hass?.states?.[e]), locale(hass), darkOf(hass), hass?.locale?.time_format, hass?.config?.time_zone];
  this.refresh();
  if (this._key && key.length === this._key.length && key.every((v, i) => v === this._key[i])) return;
  this._key = key; this.render();
 }
 connectedCallback() {
  // Once a minute "now" moves on the today bar and a history that is due is asked again (Home Assistant only).
  if (!this._timer) this._timer = setInterval(() => { if (this._hass && this._config) { this.moveNow(); this.refresh(); } }, TICK_MS);
  if (this._hass && this._config) this.refresh();
 }
 disconnectedCallback() {
  clearInterval(this._timer); this._timer = null;
  clearTimeout(this._send); this._send = null;
  this._gen++; this._fetching = 0;  // what is still on its way is dropped when it comes
 }
 getCardSize() { return 9; }
 getGridOptions() { return {columns: 12, min_columns: 6}; }
 entities() {
  const c = this._config;
  return [c.reason, c.climate, c.temperature, c.setpoint, c.heating_start, c.state, c.valves, c.valve_battery, c.valve_problem, c.fallback,
   c.sensor.temperature, c.sensor.humidity, c.sensor.battery, ...c.contacts, ...c.persons, ...c.sources, c.setting_device, c.pump, c.mode,
   c.smart].filter(Boolean);
 }
 st(entity) { return entity ? this._hass?.states?.[entity] || null : null; }
 t(key, values = {}) {
  const text = TEXT[lang(this._hass)][key] ?? TEXT.en[key];
  return together(text.replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all));
 }
 word(key, values) {
  try { const text = this._hass?.localize?.(KEY + key, values); return typeof text === 'string' ? text : ''; } catch (e) { return ''; }
 }
 deg(value, fixed) { return degrees(this._hass, value, fixed); }
 name(entity, fallback) {
  const st = this.st(entity), friendly = st?.attributes?.friendly_name;
  return typeof friendly === 'string' && friendly ? friendly : fallback || entity;
 }
 // A device's name in Home Assistant (the Bluetooth sensor's device), else the entity's.
 deviceName(entity, fallback) {
  const hass = this._hass, device = hass?.entities?.[entity]?.device_id, d = device ? hass?.devices?.[device] : null;
  return (d && (d.name_by_user || d.name)) || this.name(entity, fallback);
 }
 moreInfo(entityId) { if (entityId) this.dispatchEvent(new CustomEvent('hass-more-info', {bubbles: true, composed: true, detail: {entityId}})); }

 // -- what the room is and does (the room status card's rules) ------------------------------------------------------
 summer() {
  const c = this._config, reason = this.st(c.reason), climate = this.st(c.climate);
  return reason?.state === 'summer' || climate?.attributes?.reason === 'summer' || this.st(c.mode)?.state === 'summer';
 }
 // On, Heat along only, Off or Summer: the room thermostat's (its preset heat_along, the Reason sensor's room_state),
 // else the reason's; null when nothing is known.
 roomState() {
  const c = this._config, st = this.st(c.reason), climate = this.st(c.climate), a = climate?.attributes || {};
  if (this.summer()) return 'summer';
  const along = a.preset_mode === 'heat_along' || st?.attributes?.room_state === 'follow';
  if (climate && ['off', 'heat', 'auto'].includes(climate.state)) return climate.state === 'off' ? 'off' : along ? 'follow' : 'on';
  if (st?.state === 'off' || st?.state === 'follow') return st.state;
  return known(st) && Object.hasOwn(CHIP, st.state) ? 'on' : null;
 }
 sentence(st) {
  const a = st.attributes || {}, v = a.values && typeof a.values === 'object' ? a.values : {}, hass = this._hass;
  if (st.state === 'summer') return this.word('line.state.summer') || LINE.summer;
  if (!Object.hasOwn(CHIP, st.state)) return this.word('line.state.' + a.line) || this.t('unknown');
  if (RESTATED.has(st.state)) return this.word('chip.state.' + st.state) || CHIP[st.state];
  const values = {contact: typeof v.contact === 'string' ? v.contact : '', since: moment(hass, v.since), time: moment(hass, v.time), until: moment(hass, v.until),
   temperature: this.deg(v.temperature, true) ?? '–', target: this.deg(v.target) ?? '–'};
  const line = typeof a.line === 'string' ? this.word('line.state.' + a.line, values) : '';
  if (line) return together(line);
  const english = (Object.hasOwn(LINE, a.line) && LINE[a.line]) || LINE[st.state];
  return english ? together(english.replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all)) : this.word('chip.state.' + st.state) || CHIP[st.state];
 }
 // The week program's step: "Comfort until 22:30, then Night 18.0 °C"; '' without a next step.
 step(st) {
  const p = st.attributes?.program, hass = this._hass;
  if (!p || typeof p !== 'object' || typeof p.next_at !== 'string') return '';
  const time = moment(hass, p.next_at).replace(/\s/g, NBSP), now = this.deg(p.target, true), next = this.deg(p.next_target, true);
  if (!time || now === null || next === null) return '';
  const word = (key, values = {}) => this.word('program.state.' + key, values) || PROGRAM[key].replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all);
  const level = key => ['comfort', 'eco', 'night', 'holiday'].includes(key) ? word(key) : '';
  const nowLevel = level(p.level), nextLevel = level(p.next_level), deg = value => value + ' °C';
  return together(word('step', {level: nowLevel || deg(now), time, next: nextLevel ? nextLevel + ' ' + deg(next) : deg(next)}));
 }
 // "Resets at 22:00 to 14 °C" / "At 23:00 to Heat along only"; '' without a next reset time.
 reset() {
  const hass = this._hass, a = this.st(this._config.climate)?.attributes || {}, v = a.next_reset_value;
  const t = RESET[lang(hass)], state = ['active', 'follow', 'inactive'].indexOf(v);
  const time = moment(hass, a.next_reset).replace(/\s/g, NBSP), degree = this.deg(typeof v === 'string' ? Number(v) || null : v);
  if (!time || (state < 0 && degree === null)) return '';
  return together(t[state < 0 ? 0 : 1].replace('{time}', time).replace('{value}', state < 0 ? degree + ' °C' : t[state + 2]));
 }

 // -- actions: the room thermostat's own services (and the room's temperature without a week program) --------------
 async call(domain, service, data) {
  if (this.summer()) { this._error = this.summerText(); this.render(); return false; }
  this._error = '';
  try { await this._hass.callService(domain, service, data); return true; }
  catch (e) { this._error = this.t('failed', {reason: e?.message || String(e)}); this.render(); return false; }
 }
 summerText() {
  try {
   const text = this._hass?.localize?.('component.open_thermostat.exceptions.summer_mode_on.message');
   if (typeof text === 'string' && text) return text;
  } catch (e) { /* older frontend */ }
  return this.t('summer_refused');
 }
 // The stepper's value: on Heat along only the room's temperature without a week program (the number the room screen
 // writes, its own route), else the room thermostat's target. [entity, value, min, max] or null.
 target(state) {
  const c = this._config;
  if (state === 'follow' && c.fallback) {
   const st = this.st(c.fallback), a = st?.attributes || {};
   return known(st) ? [c.fallback, numeric(st.state), numeric(a.min) ?? 5, numeric(a.max) ?? 30] : null;
  }
  const climate = this.st(c.climate), a = climate?.attributes || {};
  if (!known(climate)) return null;
  return [c.climate, numeric(a.temperature), numeric(a.min_temp) ?? 5, numeric(a.max_temp) ?? 30];
 }
 nudge(state, delta) {
  if (this.summer()) { this._error = this.summerText(); this.render(); return; }
  const target = this.target(state);
  if (!target) return;
  const [entity, reported, low, high] = target, from = this._pending?.entity === entity ? this._pending.value : reported;
  if (from === null) return;
  const value = Math.min(high, Math.max(low, Math.round((from + delta) * 2) / 2));
  this._pending = {entity, value, sent: 0};
  this._error = '';
  this.render();
  // One service call for a run of taps (the last value), as Home Assistant's own thermostat card does.
  clearTimeout(this._send);
  this._send = setTimeout(async () => {
   this._send = null;
   const pending = this._pending;
   if (!pending) return;
   const ok = entity.startsWith('number.')
    ? await this.call('number', 'set_value', {entity_id: entity, value: pending.value})
    : await this.call('climate', 'set_temperature', {entity_id: entity, temperature: pending.value});
   if (this._pending !== pending) return;
   if (ok) pending.sent = Date.now(); else this._pending = null;
   this.render();
  }, SEND_MS);
 }
 shown(entity, reported) {
  const p = this._pending;
  if (!p || p.entity !== entity) return reported;
  if (p.sent && ((reported !== null && Math.abs(reported - p.value) < 0.05) || Date.now() - p.sent > PENDING_MS)) { this._pending = null; return reported; }
  return p.value;
 }

 // -- history: the last 24 hours of the temperature and the target ------------------------------------------------
 refresh() {
  const hass = this._hass, c = this._config;
  if (!hass || !c || !this.isConnected || typeof hass.callWS !== 'function') return;
  const ids = [c.temperature, c.setpoint].filter(e => e && this.st(e));
  if (!ids.length || this.roomState() === 'off') return;
  const now = Date.now(), seen = [this.st(c.reason)?.state, this.roomState()].join('|');
  const changed = this._seen !== null && seen !== this._seen;
  if (this._fetching && now - this._fetching < 2 * 60000) return;
  if (this._fetched && !changed && now - this._fetched < HISTORY_MS) return;
  if (this._fetched && changed && now - this._fetched < 30000) return;
  this._seen = seen; this.readHistory(ids);
 }
 async readHistory(ids) {
  const gen = this._gen, now = Date.now();
  this._fetching = now;
  try {
   const result = await this._hass.callWS({type: 'history/history_during_period', start_time: new Date(now - DAY_MS).toISOString(),
    entity_ids: ids, minimal_response: true, no_attributes: true});
   if (gen !== this._gen) return;
   const c = this._config;
   this._history = {from: now - DAY_MS, to: now, temperature: series(result?.[c.temperature]), setpoint: series(result?.[c.setpoint])};
  } catch (e) {
   if (gen !== this._gen) return;
   if (!this._history) this._history = {from: now - DAY_MS, to: now, temperature: [], setpoint: []};
  }
  this._fetched = Date.now(); this._fetching = 0;
  this.render();
 }

 // -- drawing -----------------------------------------------------------------------------------------------------
 render() {
  const hass = this._hass, c = this._config, root = this.shadowRoot;
  if (!hass || !c) return;
  if (darkOf(hass)) this.setAttribute('data-theme', 'dark'); else this.removeAttribute('data-theme');
  const focused = root.activeElement?.dataset?.focus;
  const card = make('ha-card'), wrap = make('div', {class: 'wrap'}), st = this.st(c.reason), state = this.roomState();
  card.append(wrap);
  wrap.append(this.head(st, state));
  root.replaceChildren(make('style', {}, STYLE), card);
  if (!st && c.reason) {
   wrap.append(make('p', {class: 'muted'}, hass.localize?.('ui.panel.lovelace.warning.entity_not_found', {entity: c.reason}) || this.t('missing', {entity: c.reason})));
   return;
  }
  if (!c.reason && !c.climate) {
   // An older integration's registry without the room's Reason sensor and thermostat: its temperature, compact.
   wrap.append(this.compact({attributes: {}}));
   const tiles = this.devices(state);
   if (tiles) wrap.append(tiles);
   wrap.append(this.foot(null, state));
   return;
  }
  if (!known(st) || !state) {
   // The E32 is off or not heard yet: a quiet line instead of "Unavailable", the devices Home Assistant still has.
   wrap.append(make('p', {class: 'muted', 'data-waiting': ''}, this.t('waiting')));
   const tiles = this.devices(state);
   if (tiles) wrap.append(tiles);
   wrap.append(this.foot(st, state));
   return;
  }
  const why = make('p', {class: 'why', 'data-reason': st.state}, this.sentence(st)), step = state === 'off' || state === 'summer' ? '' : this.step(st);
  if (step) why.append(make('span', {}, ' · '), make('span', {class: 'prog', 'data-step': ''}, step));
  wrap.append(why);
  if (state === 'off') wrap.append(this.compact(st));
  else {
   wrap.append(this.temperature(st, state), this.controls(st, state));
   const today = this.today(st, state);
   if (today) wrap.append(today);
   const spark = this.spark();
   if (spark) wrap.append(spark);
  }
  if (this._error) wrap.append(make('p', {class: 'error', role: 'alert', 'data-error': ''}, this._error));
  const tiles = this.devices(state);
  if (tiles) wrap.append(tiles);
  wrap.append(this.foot(st, state));
  if (focused) root.querySelector(`[data-focus="${focused}"]`)?.focus({preventScroll: true});
 }
 head(st, state) {
  const c = this._config, a = st?.attributes || {}, head = make('div', {class: 'head'});
  const type = make('span', {class: 'type', 'aria-hidden': 'true', 'data-type': TYPE[c.emitter] ? c.emitter : 'room'});
  type.append(svgIcon(TYPE[c.emitter] || 'thermostat', 24));
  const titles = make('div', {class: 'titles'}), labels = make('div', {class: 'labels'});
  titles.append(make('p', {class: 'name'}, c.name || this.name(c.climate, c.room_id) || ''), labels);
  head.append(type, titles);
  const label = (kind, tone, glyph, words, extra = {}) => {
   const l = make('span', {class: 'label tone-' + tone, 'data-label': kind, ...extra});
   l.append(svgIcon(glyph, 15), make('span', {}, words));
   labels.append(l);
  };
  if ((state === 'on' || state === 'follow') && this.st(c.climate)) labels.append(this.stateMenu(state));
  else if (state) label('state', ...STATE[state], this.t(state), {'data-state': state});
  if (state === 'on' || state === 'follow') {
   if (a.window === 'open') {
    const door = a.opening === 'door';
    label('window', 'attention', door ? 'door' : 'window', this.word('card.state.' + (door ? 'door_open' : 'window_open')) || this.t(door ? 'door_open' : 'window_open'));
   }
   const house = this.st(c.smart)?.state, room = a.smart_warm_up;
   if (state === 'on' && (room === 'on' || room === 'off') && (house === 'on' || house === 'off') && room !== house)
    label('smart', 'rest', 'clock-fast', room === 'off' ? this.t('smart_off') : this.word('card.state.smart_on') || this.t('smart_on'));
  }
  if (this.st(c.valve_problem)?.state === 'on') label('valves', 'attention', 'valve-closed', this.t('valve_problem'));
  return head;
 }
 // An Off room: only its temperature and where it comes from, compact (design §3.2 item 3).
 compact(st) {
  const c = this._config, a = st.attributes || {}, temp = this.st(c.temperature);
  const now = numeric(a.temperature) ?? (known(temp) ? numeric(temp.state) : null);
  const box = make('div', {class: 'block'}), row = make('div', {class: 'compact', role: 'button', tabindex: '0', 'data-compact': '', 'data-focus': 'compact'});
  row.append(svgIcon('thermometer', 20), make('span', {class: 'now'}, now === null ? '–' : this.deg(now, true) + NBSP + '°C'));
  const source = temp?.attributes?.source, sourceName = typeof source === 'string' && source
   ? (source.includes('.') ? this.name(source) : this.t('bluetooth')) : '';
  if (sourceName) row.append(make('span', {class: 'muted', 'data-source': ''}, sourceName));
  const open = () => this.moreInfo(c.climate || c.temperature);
  row.addEventListener('click', open);
  row.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); } });
  box.append(row);
  // 1.4: an Off room without any working source says so, with where to choose one and where to remove the room.
  const hint = c.no_source && typeof c.no_source === 'object' ? c.no_source : null;
  if (hint && typeof hint.choose === 'string' && typeof hint.remove === 'string') {
   box.append(make('p', {class: 'note', 'data-no-source': ''}, this.t('no_source')));
   const links = make('div', {class: 'foot'});
   for (const [key, path] of [['choose', hint.choose], ['remove', hint.remove]]) {
    const b = make('button', {type: 'button', class: 'text', ['data-' + key]: '', 'data-focus': key}, this.t(key));
    b.addEventListener('click', () => {
     try { history.pushState(null, '', path); } catch (err) { return; }
     window.dispatchEvent(new CustomEvent('location-changed', {detail: {replace: false}}));
    });
    links.append(b);
   }
   box.append(links);
   return box;
  }
  if (c.climate && this.st(c.climate)) {
   const on = make('button', {type: 'button', class: 'primary', 'data-switch-on': '', 'data-focus': 'on'}, this.t('switch_on'));
   on.addEventListener('click', () => this.call('climate', 'set_hvac_mode', {entity_id: c.climate, hvac_mode: 'auto'}));
   const line = make('div', {class: 'modes'});
   line.append(on);
   box.append(line);
  }
  return box;
 }
 // The arc with the measured temperature and the target, the − / + stepper and the line under it.
 temperature(st, state) {
  const c = this._config, a = st.attributes || {}, hass = this._hass, climate = this.st(c.climate);
  const box = make('div', {class: 'temp'});
  const now = numeric(climate?.attributes?.current_temperature) ?? numeric(a.temperature);
  const target = this.target(state), shownTarget = target ? this.shown(target[0], target[1]) : null;
  const goal = state === 'follow' ? numeric(a.setpoint) ?? shownTarget : shownTarget ?? numeric(a.setpoint);
  box.append(this.arc(now, goal, state));
  const ctl = make('div', {class: 'ctl'});
  ctl.append(make('p', {class: 'muted', 'data-target-label': ''}, state === 'follow' ? this.t('along_to') : this.t('target')));
  const stepper = make('div', {class: 'stepper'});
  const value = make('p', {class: 'val', 'data-target': '', 'aria-live': 'polite'});
  if (shownTarget === null) value.textContent = '–';
  else value.append(this.deg(shownTarget, true), make('span', {class: 'unit'}, NBSP + '°C'));
  const button = (delta, glyph) => {
   const b = make('button', {type: 'button', class: 'step', 'data-step-by': delta, 'data-focus': 'step' + delta,
    'aria-label': (delta < 0 ? '−' : '+') + ' 0,5 °C'});
   b.append(svgIcon(glyph, 20));
   if (!target || shownTarget === null || (delta < 0 ? shownTarget <= target[2] : shownTarget >= target[3])) b.disabled = true;
   b.addEventListener('click', () => this.nudge(state, delta));
   return b;
  };
  stepper.append(button(-0.5, 'minus'), value, button(0.5, 'plus'));
  ctl.append(stepper);
  // Under it: when it resets, or what the room does once it may heat again.
  let note = '';
  if (state === 'summer') note = '';
  else if (PAUSED.has(st.state)) note = this.t(a.opening === 'door' ? 'again_door' : a.opening === 'window' ? 'again_window' : 'again_contact');
  else note = this.reset();
  if (note) ctl.append(make('p', {class: 'note', 'data-note': ''}, note));
  box.append(ctl);
  return box;
 }
 arc(now, goal, state) {
  const c = this._config, button = make('button', {type: 'button', class: 'arc tone-' + (STATE[state]?.[0] || 'rest'), 'data-arc': '', 'data-focus': 'arc',
   'aria-label': [now !== null && `${this.t('measured')} ${this.deg(now, true)} °C`, goal !== null && `${this.t('target')} ${this.deg(goal)} °C`].filter(Boolean).join(', ')});
  button.addEventListener('click', () => this.moreInfo(c.climate || c.temperature));
  const values = [now, goal].filter(v => v !== null), low = Math.min(14, ...values.map(v => Math.floor(v) - 1)), high = Math.max(26, ...values.map(v => Math.ceil(v) + 1));
  const R = 50, X = 64, Y = 60, START = 150, SWEEP = 240;
  const at = f => { const r = (START + SWEEP * Math.max(0, Math.min(1, f))) * Math.PI / 180; return [X + R * Math.cos(r), Y + R * Math.sin(r)]; };
  const path = f => { const [x0, y0] = at(0), [x1, y1] = at(f); return `M${x0.toFixed(1)},${y0.toFixed(1)}A${R},${R} 0 ${SWEEP * f > 180 ? 1 : 0} 1 ${x1.toFixed(1)},${y1.toFixed(1)}`; };
  const frac = v => (v - low) / (high - low);
  const svg = make('svg:svg', {viewBox: '0 0 128 108', 'aria-hidden': 'true'});
  svg.append(make('svg:path', {class: 'track', d: path(1), fill: 'none', 'stroke-width': 10, 'stroke-linecap': 'round'}));
  if (now !== null && frac(now) > 0.005) svg.append(make('svg:path', {class: 'fillarc', d: path(frac(now)), fill: 'none', 'stroke-width': 10, 'stroke-linecap': 'round', 'data-fill': ''}));
  if (goal !== null) { const [x, y] = at(frac(goal)); svg.append(make('svg:circle', {class: 'dot', cx: x.toFixed(1), cy: y.toFixed(1), r: 6, 'stroke-width': 3, 'data-dot': ''})); }
  const text = make('svg:text', {x: X, y: Y + 10, 'text-anchor': 'middle', class: now === null ? 'big none' : 'big', 'data-now': ''});
  text.textContent = now === null ? '–' : this.deg(now, true);
  svg.append(text);
  if (now !== null) svg.append(make('svg:text', {x: X, y: Y + 30, 'text-anchor': 'middle', class: 'unit'}, '°C'));
  button.append(svg);
  return button;
 }
 // The presets on one row, the same on every room (1.4.4, issue #17): Program · Comfort · Eco · Night · Boost (those the
 // room thermostat lists), the room's current one pressed; on Heat along only none but Boost (its preset is the state).
 // Program goes back to the week program; without one to the room's temperature without a week program; on Heat along
 // only it switches the room back to On, as the thermostat dialog does (its tooltip says which). The levels are the
 // thermostat's (e32_comfort.program_levels); where they are the room defaults (Settings → House) a muted line says so.
 // The five chips fit a 374 px card; on a narrower card the row scrolls sideways inside the card, never wraps.
 controls(st, state) {
  const c = this._config, climate = this.st(c.climate), a = climate?.attributes || {}, row = make('div', {class: 'modes', 'data-modes': ''});
  if (!climate) return row;
  const offered = Array.isArray(a.preset_modes) ? a.preset_modes : [], program = Array.isArray(st.attributes?.today);
  const chosen = a.preset_mode === 'heat_along' ? null : a.preset_mode || 'none';
  const back = this.t(state === 'follow' ? 'on_back' : program ? 'program_back' : 'fixed_back');
  for (const preset of PRESETS.filter(p => offered.includes(p))) {
   const chip = make('button', {type: 'button', class: 'chip', 'data-preset': preset, 'data-focus': 'preset-' + preset, 'aria-pressed': String(chosen === preset),
    ...(preset === 'none' ? {title: back, 'aria-label': this.t(preset) + ', ' + back.charAt(0).toLowerCase() + back.slice(1)} : {})});
   chip.append(make('span', {}, this.t(preset)));
   chip.addEventListener('click', () => { if (chosen !== preset) this.call('climate', 'set_preset_mode', {entity_id: c.climate, preset_mode: preset}); });
   row.append(chip);
  }
  if (a.levels_from !== 'house' || !['comfort', 'eco', 'sleep'].some(p => offered.includes(p))) return row;
  const box = make('div', {class: 'presets'});
  box.append(row, make('p', {class: 'muted', 'data-levels-note': ''}, this.t('house_levels')));
  return box;
 }
 // The state as a status label that is a menu: On · Heat along only · Off, the same plan changes as the room screen and
 // the thermostat (Off: set_hvac_mode off; Heat along only: the preset heat_along; back to On from it: the preset none).
 stateMenu(state) {
  const c = this._config, a = this.st(c.climate)?.attributes || {}, [tone, glyph] = STATE[state];
  const menu = make('label', {class: 'menu label-menu tone-' + tone, 'data-label': 'state', 'data-state': state});
  const select = make('select', {'aria-label': this.t('state'), 'data-state-menu': '', 'data-focus': 'state'});
  const along = Array.isArray(a.preset_modes) && a.preset_modes.includes('heat_along');
  for (const option of ['on', ...(along || state === 'follow' ? ['follow'] : []), 'off']) {
   const o = make('option', {value: option}, this.t(option));
   if (option === state) o.selected = true;
   select.append(o);
  }
  select.addEventListener('change', () => {
   const to = select.value;
   select.value = state;  // the menu shows the room's state until Home Assistant reports the new one
   if (to === 'off') this.call('climate', 'set_hvac_mode', {entity_id: c.climate, hvac_mode: 'off'});
   else if (to === 'follow') this.call('climate', 'set_preset_mode', {entity_id: c.climate, preset_mode: 'heat_along'});
   else if (state === 'follow') this.call('climate', 'set_preset_mode', {entity_id: c.climate, preset_mode: 'none'});
  });
  const lead = svgIcon(glyph, 15), chev = svgIcon('chevron-down', 18);
  lead.setAttribute('class', 'lead'); chev.setAttribute('class', 'chev');
  menu.append(lead, select, chev);
  return menu;
 }
 // Today: the week program as a bar (the Reason sensor's ``today``), Smart warm-up's early start, the hours and now.
 today(st, state) {
  const c = this._config, hass = this._hass, entries = Array.isArray(st.attributes?.today) ? st.attributes.today : null;
  const box = make('div', {class: 'block', 'data-today': ''}), title = make('p', {class: 'muted', 'data-today-title': ''});
  box.append(title);
  if (!entries || !entries.length) { title.textContent = this.t('no_program'); return box; }
  const blocks = entries.map((e, i) => ({...e, from: minuteOf(e.at), to: i + 1 < entries.length ? minuteOf(entries[i + 1].at) : 1440}))
   .filter(b => b.from !== null && b.to !== null && b.to > b.from && finite(b.c));
  if (!blocks.length) { title.textContent = this.t('no_program'); return box; }
  const pct = minute => (minute / 1440 * 100).toFixed(3) + '%';
  const barBox = make('div', {class: 'bar-box'}), bar = make('div', {class: 'bar', role: 'img', 'data-bar': ''});
  const levelName = b => this.word('program.state.' + b.level) || (typeof b.name === 'string' && b.name) || this.deg(b.c) + ' °C';
  const spoken = [];
  for (const b of blocks) {
   const level = ['comfort', 'eco', 'night'].includes(b.level) ? b.level : 'own', words = together(`${levelName(b)} ${this.deg(b.c)} °C`);
   bar.append(make('div', {class: 'blk lv-' + level, style: `left:${pct(b.from)};width:${pct(b.to - b.from)}`, title: words, 'data-level': level}));
   spoken.push(words);
  }
  // Smart warm-up's early start, hatched from its start to the switch time it warms up for (only today, only earlier).
  const start = this.st(c.heating_start), startMs = known(start) ? Date.parse(start.state) : NaN, now = Date.now();
  let titleText = '';
  if (Number.isFinite(startMs) && startMs > now - DAY_MS && state === 'on') {
   const today = clockDay(hass, startMs) === clockDay(hass, now), from = dayMinute(hass, startMs);
   const warm = blocks.find(b => b.from > from);
   if (today && warm) {
    bar.append(make('div', {class: 'early', style: `left:${pct(from)};width:${pct(warm.from - from)}`, 'data-early': ''}));
    titleText = this.t('smart_start', {time: moment(hass, startMs), at: moment(hass, now + (warm.from - dayMinute(hass, now)) * 60000)});
   } else titleText = this.t('smart_start_plain', {time: moment(hass, startMs)});
  } else if (state === 'on' && PAUSED.has(st.state)) titleText = this.t('no_start_window');
  else if (state === 'on' && AWAY.has(st.state)) titleText = this.t('no_start_away');
  title.textContent = titleText || this.t('today');
  bar.setAttribute('aria-label', this.t('today') + ': ' + spoken.join(', '));
  barBox.append(bar, make('span', {class: 'nowmark', style: `left:${pct(dayMinute(hass, now))}`, 'data-nowmark': '', title: this.t('now')}));
  // The hours under it: 0 · 6 · 12 · 18 · 24 in the viewer's clock.
  const ticks = make('div', {class: 'ticks', 'aria-hidden': 'true'}), twelve = clockHour12(hass);
  for (const hour of [0, 6, 12, 18, 24]) {
   let text = String(hour);
   if (twelve) try { text = new Date(Date.UTC(2000, 0, 1, hour % 24)).toLocaleTimeString(locale(hass), {hour: 'numeric', hour12: true, timeZone: 'UTC'}).replace(/\s/g, NBSP); } catch (e) { /* 24 h */ }
   ticks.append(make('span', {style: `left:${pct(hour * 60)}`, 'data-hour': hour}, text));
  }
  // The levels of today with their temperature, once each, in the order they come.
  const legend = make('ul', {class: 'legend'}), seen = new Set();
  for (const b of blocks) {
   const level = ['comfort', 'eco', 'night'].includes(b.level) ? b.level : 'own', key = level + b.c;
   if (seen.has(key)) continue;
   seen.add(key);
   const li = make('li', {'data-legend': level});
   li.append(make('i', {class: 'lv-' + level}), together(level === 'own' ? `${this.deg(b.c)} °C` : `${levelName(b)} ${this.deg(b.c)} °C`));
   legend.append(li);
  }
  if (bar.querySelector('[data-early]')) {
   const li = make('li', {'data-legend': 'early'});
   li.append(make('i', {class: 'early-key'}), this.t('smart'));
   legend.append(li);
  }
  box.append(barBox, ticks, legend);
  return box;
 }
 moveNow() {
  const mark = this.shadowRoot?.querySelector('[data-nowmark]');
  if (mark && this._hass) mark.style.left = (dayMinute(this._hass, Date.now()) / 1440 * 100).toFixed(3) + '%';
 }
 // The last 24 hours: measured (blue) and target (orange, steps), no axes; a quiet box until the history is there.
 spark() {
  const c = this._config;
  if (!c.temperature && !c.setpoint) return null;
  const box = make('div', {class: 'block', 'data-spark': ''}), head = make('div', {class: 'head-row'});
  const keys = make('span', {class: 'keys muted'}), m = make('span'), t = make('span');
  m.append(make('i', {class: 'm'}), this.t('measured'));
  t.append(make('i', {class: 't'}), this.t('target'));
  keys.append(m, t);
  head.append(make('p', {class: 'muted'}, this.t('last_day')), keys);
  const button = make('button', {type: 'button', class: 'spark', 'data-focus': 'spark', 'aria-label': this.t('last_day')});
  button.addEventListener('click', () => this.moreInfo(c.temperature || c.setpoint));
  const W = 300, H = 64, svg = make('svg:svg', {viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'none', 'aria-hidden': 'true'});
  svg.append(make('svg:rect', {class: 'base', x: 0, y: 0, width: W, height: H, rx: 6}));
  const h = this._history;
  if (h) {
   const clip = list => {
    const out = list.filter(p => p.t >= h.from && p.v !== null), before = [...list].reverse().find(p => p.t < h.from && p.v !== null);
    return before ? [{v: before.v, t: h.from}, ...out] : out;
   };
   // The measured line as the mean of each 10 minutes: a sensor that steps by 0.1 °C every minute otherwise draws a
   // zigzag on 300 px.
   const bins = new Map();
   for (const p of clip(h.temperature)) {
    const k = Math.floor((p.t - h.from) / BIN_MS), b = bins.get(k) || {sum: 0, n: 0, t: h.from + (k + 0.5) * BIN_MS};
    b.sum += p.v; b.n++; bins.set(k, b);
   }
   const measured = [...bins.values()].map(b => ({v: b.sum / b.n, t: Math.min(h.to, b.t)})).sort((x, y) => x.t - y.t);
   const target = clip(h.setpoint), all = [...measured, ...target].map(p => p.v);
   if (all.length) {
    let low = Math.min(...all), high = Math.max(...all);
    if (high - low < 2) { const mid = (high + low) / 2; low = mid - 1; high = mid + 1; }
    const pad = (high - low) * 0.12, x = ms => ((ms - h.from) / (h.to - h.from) * W).toFixed(1), y = v => (H - 4 - (v - low + pad) / (high - low + 2 * pad) * (H - 8)).toFixed(1);
    const line = (list, stepped) => list.map((p, i) => (i ? (stepped ? `H${x(p.t)}V${y(p.v)}` : `L${x(p.t)},${y(p.v)}`) : `M${x(p.t)},${y(p.v)}`)).join('')
     + (list.length ? (stepped ? `H${W}` : `L${W},${y(list[list.length - 1].v)}`) : '');
    if (target.length) svg.append(make('svg:path', {class: 'target', d: line(target, true), 'data-line': 'target'}));
    if (measured.length) svg.append(make('svg:path', {class: 'measured', d: line(measured, false), 'data-line': 'measured'}));
   }
  }
  button.append(svg);
  box.append(head, button);
  return box;
 }
 // The devices of the room as tiles: an icon, its name and one line (two for a valve with a finding); a tap opens it.
 devices(state) {
  const c = this._config, hass = this._hass, list = [];
  const tile = (entity, glyph, name, value, extra = {}) => list.push({entity, glyph, name, value, ...extra});
  const battery = n => {
   const span = make('span', {class: finite(n) && n < c.battery_limit ? 'low' : null, 'data-battery': ''}, this.t('battery', {n: Math.round(n)}));
   return span;
  };
  // The thermometer: the room's Bluetooth sensor, its other Home Assistant sources.
  const s = c.sensor, temp = this.st(s.temperature);
  if (temp) {
   const parts = [], t = known(temp) ? numeric(temp.state) : null, hum = this.st(s.humidity), bat = this.st(s.battery);
   if (t !== null) parts.push(this.deg(t, true) + NBSP + '°C');
   if (known(hum) && numeric(hum.state) !== null) parts.push(Math.round(numeric(hum.state)) + NBSP + '%');
   const level = known(bat) ? numeric(bat.state) : null;
   tile(s.temperature, 'thermometer', this.deviceName(s.temperature, this.t('thermometer')), parts.length ? parts.join(' · ') : this.t('no_reading'),
    {battery: level, kind: 'thermometer'});
  }
  for (const source of c.sources) {
   const st = this.st(source);
   if (!st) continue;
   const v = known(st) ? numeric(st.state) : null, unit = st.attributes?.unit_of_measurement;
   tile(source, 'thermometer', this.name(source), v === null ? this.t('no_reading') : together(this.deg(v, true) + ' ' + (typeof unit === 'string' && unit ? unit : '°C')), {kind: 'source'});
  }
  if (c.setting_device && this.st(c.setting_device)) {
   // Its target as the integration reads it (e32_setting_device.device_target): a thermostat's temperature, else (one
   // with only a range, such as the Bosch Room thermostat II through Zigbee2MQTT, issue #16) its target_temp_low; a
   // number's state.
   const st = this.st(c.setting_device), a = st.attributes || {};
   const v = !known(st) ? null : c.setting_device.startsWith('climate.') ? numeric(a.temperature) ?? numeric(a.target_temp_low) : numeric(st.state);
   tile(c.setting_device, 'thermostat', this.name(c.setting_device), v === null ? this.t('setting_plain') : this.t('setting_device', {t: this.deg(v)}), {kind: 'setting'});
  }
  // The radiator valves: per valve its opening (or the temperature it was given) and battery, the E32's finding under it.
  const valves = this.st(c.valves), va = valves?.attributes || {};
  // (All valves driven by temperature: no average opening, the sensor's state is empty but its valves are there.)
  for (const v of valves && valves.state !== 'unavailable' && Array.isArray(va.valves) ? va.valves : []) {
   if (!v || typeof v !== 'object' || typeof v.name !== 'string') continue;
   const match = GATEWAY.exec(v.name), name = match ? this.t('gateway', {n: match[1], id: match[2]}) : v.name.startsWith('climate.') ? this.name(v.name) : v.name;
   const position = numeric(v.position ?? v.position_pct), given = numeric(v.set_to_c), level = numeric(v.battery ?? v.battery_pct), parts = [];
   if (v.health === 'offline') parts.push(this.t('offline'));
   else if (position !== null) parts.push(this.t('open_pct', {n: Math.round(position)}));
   else if (given !== null) parts.push(this.t('set_to', {t: this.deg(given)}));
   let second = '', tone = 'along';
   // 1.4.4 (FW-TRV-STATE): a state the E32 could not read, with its size: red, before any finding (it says nothing now).
   const large = v.health === 'message_too_large', kb = numeric(v.bytes);
   if (large) {
    tone = 'attention';
    second = kb !== null && kb > 0 ? this.t('too_large', {kb: (kb / 1000).toLocaleString(locale(hass), {minimumFractionDigits: 1, maximumFractionDigits: 1})})
     : this.t('too_large_plain');
   } else if (HELD[v.held]) {
    tone = HELD[v.held];
    const to = given ?? numeric(v.setpoint_c) ?? numeric(this.st(c.climate)?.attributes?.temperature);
    second = v.held === 'put_back' ? (to !== null ? this.t('put_back', {t: this.deg(to)}) : this.t('put_back_plain')) : this.t(v.held);
   }
   tile(c.valves, position !== null && position < 1 ? 'valve-closed' : 'valve', name, parts.join(' · '),
    {battery: level, second, tone, warn: v.health === 'offline' || large || v.held === 'gave_up', kind: 'valve', held: v.held || null,
     health: large ? v.health : null});
  }
  // Windows and doors: open since a time (red) or closed.
  for (const contact of c.contacts) {
   const st = this.st(contact);
   if (!st) continue;
   const door = ['door', 'garage_door'].includes(st.attributes?.device_class), open = st.state === 'on';
   const since = open ? moment(hass, st.last_changed) : '';
   tile(contact, door ? 'door' : 'window', this.name(contact), !known(st) ? this.t('no_reading') : open ? (since ? this.t('open_since', {time: since}) : this.t('is_open')) : this.t('closed'),
    {warn: open, kind: 'contact', open});
  }
  for (const person of c.persons) {
   const st = this.st(person);
   if (!st) continue;
   let where = st.state === 'home' ? this.t('home') : st.state === 'not_home' ? this.t('away') : '';
   if (!where && known(st)) { try { where = hass.formatEntityState?.(st) || ''; } catch (e) { where = ''; } }
   tile(person, 'account', this.name(person), where || this.t('no_reading'), {kind: 'person'});
  }
  if (c.pump && this.st(c.pump)) {
   const st = this.st(c.pump);
   tile(c.pump, 'plug', this.name(c.pump), st.state === 'on' ? this.t('pump_on') : st.state === 'off' ? this.t('pump_off') : this.t('no_reading'), {kind: 'pump'});
  }
  if (!list.length) return null;
  const box = make('div', {class: 'block', 'data-devices': ''}), grid = make('div', {class: 'tiles'});
  box.append(make('p', {class: 'muted'}, this.t('devices')), grid);
  for (const item of list) {
   const el = make('button', {type: 'button', class: 'tile' + (item.warn ? ' warn' : ''), 'data-tile': item.kind, 'data-focus': 'tile-' + list.indexOf(item),
    ...(item.held ? {'data-held': item.held} : {}), ...(item.health ? {'data-health': item.health} : {})});
   const txt = make('span', {class: 'txt'}), value = make('span', {class: 'tv'});
   const words = [item.value].filter(Boolean);
   if (item.value) value.append(item.value);
   if (finite(item.battery)) { if (item.value) value.append(' · '); value.append(battery(item.battery)); words.push(this.t('battery', {n: Math.round(item.battery)})); }
   if (item.open) value.classList.add('low');
   txt.append(make('span', {class: 'tn'}, item.name), value);
   if (item.second) { txt.append(make('span', {class: 't2 tone-' + item.tone, 'data-second': ''}, item.second)); words.push(item.second); }
   el.title = [item.name, ...words].join(' · ');
   el.append(svgIcon(item.glyph, 20), txt);
   el.addEventListener('click', () => this.moreInfo(item.entity));
   grid.append(el);
  }
  return box;
 }
 // The footer: the room's week program and its settings, both on the room's screen in the Settings tab.
 foot(st, state) {
  const c = this._config, foot = make('div', {class: 'foot'});
  const room = typeof c.room_id === 'string' && c.room_id ? c.room_id : st?.attributes?.room_id;
  if (typeof c.settings_path !== 'string' || !c.settings_path || typeof room !== 'string' || !room) return foot;
  const go = (key, words) => {
   const b = make('button', {type: 'button', class: 'text', ['data-' + key]: '', 'data-focus': key}, words);
   b.addEventListener('click', () => {
    try { history.pushState(null, '', c.settings_path + '#room/' + encodeURIComponent(room)); } catch (err) { return; }
    window.dispatchEvent(new CustomEvent('location-changed', {detail: {replace: false}}));
   });
   foot.append(b);
  };
  go('week', this.t('week'));
  go('settings', this.word('card.state.settings') || this.t('settings'));
  return foot;
 }
}
// Other dashboard cards (HACS resources) may later replace window.customElements with a scoped-registry polyfill whose
// get() does not see elements defined before it: define now, and again (a fresh subclass) whenever the registry in use
// lacks the element (the same guard as room-status-card.js; only for the first 30 s, then on navigation or view).
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
 const timer = setInterval(check, 500);
 setTimeout(() => clearInterval(timer), 30000);
 document.addEventListener('visibilitychange', check);
 return check;
};
ensureDefined('openthermostat-room', OpenThermostatRoom);
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === 'openthermostat-room'))
 window.customCards.push({type: 'openthermostat-room', name: 'OpenThermostat room', description: 'One E32 room: its temperature, presets, today, the last 24 hours and its devices.'});
