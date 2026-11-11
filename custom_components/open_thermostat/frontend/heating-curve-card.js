/* The Learning view's two cards (OpenThermostat, E32 rc.5): one module, one versioned URL.

   openthermostat-heating-curve — water temperature by outdoor temperature. Reads the attributes of the "Water
   temperature by weather compensation" sensor (e32_flow.py), all in °C (its state is converted on an imperial
   system, so the card never draws from it): the slope in use and where it comes from (standard, learned, or
   estimated from the house), the standard slope from the water temperature in hard frost, the room temperature
   the curve starts from, the outdoor temperature now, the water temperature limits, the line's own value now
   (base_c) and what weather compensation asks (flow_c). It draws what the E32 Home page draws
   (data/html/house.html):
     water = room + slope × max(0, room − outdoor), within the lowest and highest water temperature,
   the standard line dashed, the learned one solid with the gain between them as a soft band, "Now" on the line
   (with what the E32 asks when the room correction adds to it) and the hard-frost point (−10 °C). A crosshair
   reads any outdoor temperature (pointer, touch or arrow keys); the values are also a table. Plain inline SVG;
   marks 2 px, markers with a ring in the card colour. `show_name: false` leaves the card's own title out where a
   heading above it says it (the Learning view).

   openthermostat-knowledge — what the E32 knows: a ring with the percentage beside the headline "The E32 knows
   your house: 70 %" and, below them, the learning path (1.4.3, the Knowledge sensor's ``path``, insight.py): one
   label per part, green with a check once learned, amber with a clock while it is still learning with what it still
   needs ("Warm-up Slaapkamer · 4 of 6"); a part Home Assistant cannot tell about gets no label.

   openthermostat-boiler-learned (1.4.3) — what the E32 learned from the boiler, as tiles: the highest water it goes
   to by itself in today's outdoor band and the most the E32 asks there, its rest, the water from which it burns
   steadily and the water from which it starts heating; only tiles with a value; while nothing is learned the
   Boiler response sensor's sentence. Its own EN/NL words (the viewer's language).

   1.4.3 (design 4.3, one story about the water temperature): "Now" on the curve says what the E32 asks and how much
   the rooms add ("E32 asks 42 °C" over "+5 °C for the rooms"), and the line's learned steepness is a sentence under it.

   The words are the integration's translations (strings.json entity.sensor.flow_curve.state_attributes.chart
   and entity.sensor.knowledge.state_attributes.card), so every viewer reads them in their own Home Assistant
   language; English is only the last resort. Colours: the validated chart steps of the E32 pages
   (history-chart.js), selected per mode, never an inverted light theme. */
const PREFIX = 'component.open_thermostat.entity.sensor.';
const CURVE_TEXT = {title: 'Water temperature by outdoor temperature', standard: 'Standard', learned: 'Learned for your house',
 house: 'Estimated from your house', now: 'Now', frost: 'At −10 °C with {room} °C inside: {flow} °C',
 now_point: '{outdoor} °C outside → {flow} °C', asks: 'E32 asks {flow} °C', would_ask: 'E32 would ask {flow} °C', at: 'At {outdoor} °C outside',
 lower: '{n} °C cooler than standard', higher: '{n} °C warmer than standard', outdoor: 'Outdoor temperature (°C)',
 water: 'Water to heating (°C)', caption: 'The colder it is outside, the warmer the water. The E32 learns the line for your house and keeps it as low as it can.',
 values: 'Show the values', outside: 'Outside', off: 'Weather compensation is off; the lines show what it would ask.',
 waiting: 'The E32 has not reported its weather compensation yet.', rooms_add: '+{n} °C for the rooms',
 slope_learned: 'Learned for your house: the water gets about {s} °C warmer for every degree colder outside.',
 slope_house: 'Estimated from your house: the water gets about {s} °C warmer for every degree colder outside.',
 slope_standard: 'The standard line for now: the water gets about {s} °C warmer for every degree colder outside.'};
const KNOWLEDGE_TEXT = {title: 'The E32 knows your house', ring: 'The E32 knows your house: {pct} %', hint: 'It learns by itself while the heating runs.',
 done: 'It has learned everything it needs; it keeps checking as the seasons change.',
 waiting: 'The E32 has not reported what it knows yet.', path: 'What it learns', learned: '{name}: learned', busy: '{name}: still learning'};
// openthermostat-boiler-learned's own words (1.4.3), English and Dutch, in the viewer's language.
const BOILER_TEXT = {
 en: {ceiling: 'highest water {when}; the E32 asks at most {asks}', ceiling_off: 'highest water {when}; with Smart warm-up on the E32 would ask at most {asks}',
  band_low: 'below {high} °C outside', band: 'at {low} to {high} °C outside', band_high: 'from {low} °C outside', band_none: 'at today’s outdoor temperature',
  rest: 'rest each time it reaches its temperature', steady: 'burns steadily from this water', start: 'starts heating from this water',
  min: '{n} min'},
 nl: {ceiling: 'hoogste water {when}; de E32 vraagt hooguit {asks}', ceiling_off: 'hoogste water {when}; met Slim opwarmen aan vraagt de E32 hooguit {asks}',
  band_low: 'onder {high} °C buiten', band: 'bij {low} tot {high} °C buiten', band_high: 'vanaf {low} °C buiten', band_none: 'bij de buitentemperatuur van nu',
  rest: 'rust telkens als hij zijn temperatuur bereikt', steady: 'brandt rustig door vanaf dit water', start: 'begint te verwarmen vanaf dit water',
  min: '{n} min'}};
// BoilerResponse: the boiler holds about its ceiling + 2 °C (insight.HELD_ABOVE_CEILING_C).
const HELD_ABOVE_CEILING_C = 2;
// Material Design Icons (v7.4.47, Apache 2.0), inline: the learning path's labels.
const PATH_ICONS = {
 'check': 'M21,7L9,19L3.5,13.5L4.91,12.09L9,16.17L19.59,5.59L21,7Z',
 'clock-outline': 'M12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22C6.47,22 2,17.5 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z'
};
// The axes (°C): outdoor −15..20 (wider when it is colder or warmer now), water 20..80. FROST: the design point.
const X0 = -15, X1 = 20, Y0 = 20, Y1 = 80, FROST = -10;
const COLORS = `--hc-learned:#00876f;--hc-now:#b5600c;--hc-learned-soft:rgba(0,135,111,.13);--hc-now-soft:rgba(181,96,12,.18)`;
const DARK = `--hc-learned:#239c8a;--hc-now:#c97a2c;--hc-learned-soft:rgba(35,156,138,.2);--hc-now-soft:rgba(201,122,44,.24)`;
// 1.4.1: the design tokens of CONTRACT-1.4.1 §8 on the host (the kit, the cards and the planner share names and values).
const BASE = `:host{display:block;
--ot-space:8px;--ot-radius:12px;--ot-radius-s:8px;--ot-touch:44px;--ot-motion:150ms ease;
--ot-text-xl:22px;--ot-line-xl:28px;--ot-text-l:17px;--ot-line-l:24px;--ot-text-m:15px;--ot-line-m:22px;--ot-text-s:13px;--ot-line-s:18px;
--ot-bg:var(--card-background-color);--ot-fg:var(--primary-text-color);--ot-fg-2:var(--secondary-text-color);
--ot-line:var(--divider-color);--ot-accent:var(--primary-color);--ot-on-accent:var(--text-primary-color, #fff);
--ot-heat-ink:#a1500f;--ot-heat-fill:#fbe9db;--ot-along-ink:#886100;--ot-along-fill:#f8efcf;--ot-water-ink:#1f5fa8;--ot-water-fill:#dde9f8;
--ot-rest-ink:#5f6368;--ot-rest-fill:#ebedf0;--ot-attention-ink:#b3261e;--ot-attention-fill:#f9dedc;
/* CONTRACT-1.4.1 §8 (amended): filled buttons and text buttons, readable on HA's default accent */
--ot-fill:color-mix(in srgb,var(--ot-accent) 72%,#000);--ot-link:color-mix(in srgb,var(--ot-accent) 60%,var(--ot-fg));
/* 1.4.3 design §6: "learned" in green, its ink 60 % mixed with the text colour; tiles raised 2.5 % text on the card */
--ot-ok:var(--success-color,#43a047);--ot-ok-ink:color-mix(in srgb,var(--ot-ok) 60%,var(--ot-fg));
--ot-ok-fill:color-mix(in srgb,var(--ot-ok) 16%,var(--ot-bg,#fff));--ot-raised:color-mix(in srgb,var(--ot-fg) 2.5%,var(--ot-bg,#fff));
color:var(--ot-fg)}
:host([data-theme="dark"]){--ot-heat-ink:#f0a060;--ot-heat-fill:rgba(240,160,96,.18);--ot-along-ink:#e6c35c;--ot-along-fill:rgba(230,195,92,.18);
--ot-water-ink:#7fb3f0;--ot-water-fill:rgba(127,179,240,.18);--ot-rest-ink:#b0b4ba;--ot-rest-fill:rgba(176,180,186,.18);
--ot-attention-ink:#f2857c;--ot-attention-fill:rgba(242,133,124,.18)}
:host([data-theme="dark"]){--ot-raised:color-mix(in srgb,var(--ot-fg) 5%,var(--ot-bg,#1c1c1c))}
ha-card{display:block;padding:16px;border-radius:var(--ot-radius);color:var(--ot-fg);${COLORS};
--hc-surface:var(--ha-card-background,var(--card-background-color,#fff));--hc-muted:var(--secondary-text-color,#6b6b6b);--hc-grid:var(--divider-color,rgba(127,127,127,.22))}
ha-card.dark{${DARK}}h2{margin:0 0 4px;font-size:1.05rem;font-weight:600;line-height:1.35;overflow-wrap:anywhere}
p{margin:0;line-height:1.45}.muted{color:var(--hc-muted);font-size:.9rem}@media(max-width:480px){ha-card{padding:12px}}`;
const CURVE_STYLE = `${BASE}
.legend{display:flex;flex-wrap:wrap;gap:4px 16px;margin:2px 0 6px;padding:0;list-style:none;font-size:.875rem;color:var(--hc-muted)}
.legend li{display:inline-flex;align-items:center;gap:6px;max-width:100%}
.key{display:inline-block;flex:none;width:18px;border-top:2px solid var(--hc-learned)}.key.standard{border-top:2px dashed var(--hc-muted)}
.key.now{width:10px;height:10px;border:0;border-radius:50%;background:var(--hc-now);box-shadow:0 0 0 3px var(--hc-now-soft)}
.plot{position:relative;touch-action:pan-y}svg{display:block;max-width:100%;height:auto;overflow:visible;-webkit-tap-highlight-color:transparent}
svg:focus{outline:none}svg:focus-visible{outline:2px solid var(--primary-color);outline-offset:4px;border-radius:4px}
.grid{stroke:var(--hc-grid);stroke-width:1;shape-rendering:crispEdges}.tick{font-size:12px;fill:var(--hc-muted);font-variant-numeric:tabular-nums}
.axis-title{font-size:12px;fill:var(--hc-muted)}.band{fill:var(--hc-learned-soft);stroke:none}
.line{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}.line.learned{stroke:var(--hc-learned)}
.line.standard{stroke:var(--hc-muted);stroke-dasharray:6 5}.point{stroke:var(--hc-surface);stroke-width:2}
.point.learned{fill:var(--hc-learned)}.point.standard{fill:var(--hc-muted)}.point.now{fill:var(--hc-now)}.halo{fill:var(--hc-now-soft)}
.label{font-size:12.5px;font-weight:600;fill:var(--primary-text-color);paint-order:stroke;stroke:var(--hc-surface);stroke-width:4px;stroke-linejoin:round}
.label .sub{font-weight:400;fill:var(--hc-muted)}.leader{stroke:var(--hc-muted);stroke-width:1}
.cross{stroke:var(--primary-text-color);stroke-opacity:.35;stroke-width:1;shape-rendering:crispEdges}.hit{fill:transparent;cursor:crosshair}
.tip{position:absolute;top:0;left:0;z-index:1;min-width:132px;padding:6px 10px;border-radius:8px;pointer-events:none;font-size:.875rem;line-height:1.35;
background:var(--hc-surface);color:var(--primary-text-color);border:1px solid var(--hc-grid);box-shadow:0 2px 10px rgba(0,0,0,.18)}.tip[hidden]{display:none}
.tip-head{color:var(--hc-muted);margin-bottom:2px;white-space:nowrap}.tip-row{display:flex;align-items:center;gap:8px;white-space:nowrap}
.tip-row b{font-weight:600;font-variant-numeric:tabular-nums}.tip-row span{color:var(--hc-muted)}
.caption{margin:8px 0 0;color:var(--hc-muted);font-size:.9rem}.note{margin:6px 0 0;font-size:.9rem}
.slope{margin:8px 0 0;font-size:var(--ot-text-m);line-height:var(--ot-line-m)}
details{margin:8px 0 0}summary{cursor:pointer;color:var(--primary-color);font-size:.9rem;padding:6px 0;min-height:24px}
table{border-collapse:collapse;color:inherit;font-size:.875rem;font-variant-numeric:tabular-nums;margin-top:4px}th,td{padding:4px 12px 4px 0;text-align:right;vertical-align:bottom;overflow-wrap:normal}td{white-space:nowrap}
th{font-weight:500;color:var(--hc-muted)}th:first-child,td:first-child{text-align:left}tr+tr td{border-top:1px solid var(--hc-grid)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}`;
const KNOWLEDGE_STYLE = `${BASE}
.head{display:flex;align-items:center;gap:14px}.ring{flex:none;width:72px;height:72px}.ring .track{stroke:var(--hc-learned-soft)}
.ring .fill{stroke:var(--hc-learned)}.ring text{font-size:16px;font-weight:600;fill:var(--primary-text-color)}
.done{margin-top:12px}
.path{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 0;padding:0;list-style:none}
.chip{display:inline-flex;align-items:center;gap:6px;min-height:26px;max-width:100%;box-sizing:border-box;padding:4px 10px;border-radius:13px;
font-size:var(--ot-text-s);line-height:var(--ot-line-s);font-weight:500}
.chip span{min-width:0;overflow-wrap:anywhere}.chip .ic{display:inline-flex;flex:none;width:15px;height:15px}.chip svg{display:block;width:100%;height:100%}
.chip.learned{background:var(--ot-ok-fill);color:var(--ot-ok-ink)}.chip.busy{background:var(--ot-along-fill);color:var(--ot-along-ink)}`;
const BOILER_STYLE = `${BASE}
ha-card{padding:12px 16px}.sentence{margin:0 0 8px;font-size:var(--ot-text-m);line-height:var(--ot-line-m);color:var(--ot-fg-2)}
.wrap{container:boiler/inline-size}.tiles{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.tile{display:flex;flex-direction:column;justify-content:space-between;gap:4px;min-width:0;min-height:84px;box-sizing:border-box;padding:10px 12px;
border-radius:var(--ot-radius-s);background:var(--ot-raised)}
.value{margin:0;font-size:26px;line-height:32px;font-weight:300;font-variant-numeric:tabular-nums;white-space:nowrap}
.label{margin:0;font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-fg-2);overflow-wrap:anywhere}
@container boiler (min-width:560px){.tiles{grid-template-columns:repeat(var(--n,3),minmax(0,1fr))}}`;

const finite = value => typeof value === 'number' && Number.isFinite(value);
const numeric = value => { const n = typeof value === 'string' && value.trim() !== '' ? Number(value) : value; return finite(n) ? n : null; };
const locale = hass => hass?.locale?.language || hass?.language || 'en';
// Dark: Home Assistant's theme when it says so, else the browser's colour scheme (CONTRACT-1.4.1 §8).
const darkOf = hass => {
 if (typeof hass?.themes?.darkMode === 'boolean') return hass.themes.darkMode;
 try { return window.matchMedia('(prefers-color-scheme: dark)').matches; } catch (e) { return false; }
};
const theme = (host, hass) => { if (darkOf(hass)) host.setAttribute('data-theme', 'dark'); else host.removeAttribute('data-theme'); };
const SVG = 'http://www.w3.org/2000/svg';
const make = (tag, attrs = {}, text) => {
 const e = tag.startsWith('svg:') ? document.createElementNS(SVG, tag.slice(4)) : document.createElement(tag);
 for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined) e.setAttribute(k, v);
 if (text !== undefined) e.textContent = text;
 return e;
};
// WeatherCurve::baseCentiC as the E32 computes it, within the water temperature limits where they are known.
const water = (slope, room, low, high) => outdoor =>
 Math.min(high ?? Infinity, Math.max(low ?? -Infinity, room + slope * Math.max(0, room - outdoor)));

/* The chart, drawn into `host` (a .plot element) at its own width; `t(key, values)` gives a text and `n(value,
   digits)` a number in the viewer's language. `keep` ({at, focus}) carries the crosshair and the keyboard focus
   over a redraw (a new state, a new width), so a tooltip being read stays. Returns what the table reads. */
function drawCurve(host, data, t, n, keep = {at: null, focus: false}) {
 const width = Math.max(260, Math.round(host.clientWidth || 320)), M = {left: 34, right: 12, top: 24, bottom: 42};
 const plotH = Math.round(Math.min(240, Math.max(168, width * 0.5))), height = M.top + plotH + M.bottom;
 const x0 = data.outdoor !== null && data.outdoor < X0 ? Math.floor((data.outdoor - 1) / 5) * 5 : X0;
 const x1 = data.outdoor !== null && data.outdoor > X1 ? Math.ceil((data.outdoor + 1) / 5) * 5 : X1;
 const px = v => M.left + (v - x0) / (x1 - x0) * (width - M.left - M.right);
 const py = v => M.top + (Y1 - Math.min(Y1, Math.max(Y0, v))) / (Y1 - Y0) * plotH;
 const svg = make('svg:svg', {width, height, viewBox: `0 0 ${width} ${height}`, tabindex: '0', role: 'img'});
 const tip = make('div', {class: 'tip', hidden: ''}), live = make('span', {class: 'sr', 'aria-live': 'polite'});
 const was = keep.at, refocus = keep.focus; // before the old chart goes (a browser may blur it on the way out)
 host.replaceChildren(svg, tip, live); // in the document first, so the labels can be measured
 const layer = cls => svg.appendChild(make('svg:g', {class: cls}));
 const grid = layer('axes'), marks = layer('marks'), labels = layer('labels'), cross = layer('crosshair');
 for (let v = Y0; v <= Y1; v += 10) {
  grid.append(make('svg:line', {class: 'grid', x1: M.left, x2: width - M.right, y1: py(v), y2: py(v)}),
   make('svg:text', {class: 'tick', x: M.left - 8, y: py(v) + 4, 'text-anchor': 'end'}, n(v)));
 }
 for (let v = Math.ceil(x0 / 5) * 5; v <= x1; v += 5)
  grid.append(make('svg:text', {class: 'tick', x: px(v), y: M.top + plotH + 18, 'text-anchor': 'middle'}, n(v)));
 grid.append(make('svg:text', {class: 'axis-title', x: (M.left + width - M.right) / 2, y: height - 4, 'text-anchor': 'middle'}, t('outdoor')),
  make('svg:text', {class: 'axis-title', x: M.left - 30, y: 12}, t('water')));
 const standard = data.standardSlope !== null ? water(data.standardSlope, data.room, data.low, data.high) : null;
 const own = data.learned ? water(data.slope, data.room, data.low, data.high) : null;
 const sample = f => { const out = []; for (let v = x0; v <= x1 + 1e-9; v += 0.25) out.push([px(v), py(f(v))]); return out; };
 const path = points => 'M' + points.map(p => p[0].toFixed(1) + ',' + p[1].toFixed(1)).join('L');
 const lines = [];
 if (standard && own) marks.append(make('svg:path', {class: 'band', d: path([...sample(own), ...sample(standard).reverse()]) + 'Z'}));
 if (standard) { const s = sample(standard); lines.push(s); marks.append(make('svg:path', {class: 'line standard', 'data-line': 'standard', d: path(s)})); }
 if (own) { const s = sample(own); lines.push(s); marks.append(make('svg:path', {class: 'line learned', 'data-line': 'learned', d: path(s)})); }
 // The hard-frost point of the line in use (the learned one once there is one), and the gain over the standard.
 const used = own || standard, frost = Math.round(used(FROST)), gain = own && standard ? Math.round(standard(FROST) - own(FROST)) : 0;
 const solid = data.house ? 'house' : 'learned'; // the solid line's words: learned, or estimated from the house
 marks.append(make('svg:circle', {class: 'point ' + (own ? 'learned' : 'standard'), 'data-point': 'frost', cx: px(FROST), cy: py(used(FROST)), r: 4.5}));
 // "Now" sits on the line: the E32's own value of it (base_c), else the line here at the outdoor temperature now;
 // what weather compensation asks with the room correction (flow_c) is told beside it when it differs.
 const base = data.outdoor === null ? null
  : data.base !== null ? Math.min(data.high ?? Infinity, Math.max(data.low ?? -Infinity, data.base)) : used(data.outdoor);
 const showNow = base !== null;
 const nowRows = showNow ? [t('now_point', {outdoor: n(data.outdoor, 1), flow: n(Math.round(base))})] : [];
 // 1.4.3 (design 4.3): what the rooms add on top of the line, in the same words as the Learning view's story.
 const added = data.now !== null && showNow ? Math.round(data.now) - Math.round(base) : 0;
 if (showNow && data.now !== null && added !== 0)
  nowRows.push(t('asks', {flow: n(data.now)}), ...(added > 0 ? [t('rooms_add', {n: n(added)})] : []));
 if (showNow) {
  marks.append(make('svg:circle', {class: 'halo', cx: px(data.outdoor), cy: py(base), r: 12}),
   make('svg:circle', {class: 'point now', 'data-point': 'now', cx: px(data.outdoor), cy: py(base), r: 5}));
 }
 // Labels, most important first; each takes the first of its places that overlaps no line, mark or earlier label
 // and stays inside the plot. An optional one that finds none is left out (the legend, tooltip and table still
 // carry it). A required one ("Now", the hard-frost point) then takes the free place of the plot nearest to its
 // point, with a thin leader; in a plot without one it crosses a line (its halo keeps it legible) rather than
 // cover another label or point.
 const taken = [], plot = {l: M.left, r: width - M.right, t: M.top - 4, b: M.top + plotH};
 const crosses = box => lines.some(line => line.some(([x, y]) => x >= box.l - 2 && x <= box.r + 2 && y >= box.t - 2 && y <= box.b + 2));
 const covers = box => taken.some(o => box.l < o.r && box.r > o.l && box.t < o.b && box.b > o.t);
 const place = (attrs, rows, spots, required, near) => {
  const text = make('svg:text', {class: 'label', ...attrs});
  rows.forEach((row, i) => text.append(make('svg:tspan', {class: i ? 'sub' : null, x: 0, dy: i ? 15 : 0}, row)));
  labels.append(text);
  const at = ([x, y, anchor]) => {
   text.setAttribute('text-anchor', anchor);
   text.querySelectorAll('tspan').forEach(s => s.setAttribute('x', x));
   text.setAttribute('y', y);
   let b; try { b = text.getBBox(); } catch (e) { b = null; }
   const w = b && b.width ? b.width : Math.max(...rows.map(r => r.length)) * 7, h = 15 * rows.length;
   const l = anchor === 'end' ? x - w : anchor === 'middle' ? x - w / 2 : x;
   return {l, r: l + w, t: y - 12, b: y - 12 + h};
  };
  // How far a box sticks out of the plot (0: inside); covering a label or point weighs far more than a line.
  const outside = box => Math.max(0, plot.l - box.l) + Math.max(0, box.r - plot.r) + Math.max(0, plot.t - box.t) + Math.max(0, box.b - plot.b);
  const score = box => outside(box) * 10 + (covers(box) ? 100 : 0) + (crosses(box) ? 1 : 0);
  let best = null, size = null;
  for (const spot of spots) {
   const box = at(spot), s = score(box);
   if (s === 0) { taken.push(box); return box; }
   if (!best || s < best[0]) best = [s, 0, spot];
   size = box;
  }
  if (!required || !best) { text.remove(); return null; }
  // Every place of the plot on an 8 px grid: the lowest score, then the nearest to the point.
  const w = size.r - size.l, h = size.b - size.t;
  for (let y = plot.t + 12; y - 12 + h <= plot.b; y += 8) for (let x = plot.l + 4; x + w <= plot.r; x += 8) {
   const box = {l: x, r: x + w, t: y - 12, b: y - 12 + h}, s = score(box);
   const d = Math.hypot(Math.max(box.l - near[0], 0, near[0] - box.r), Math.max(box.t - near[1], 0, near[1] - box.b));
   if (s < best[0] || (s === best[0] && d < best[1])) best = [s, d, [x, y, 'start']];
  }
  const box = at(best[2]); taken.push(box); return box;
 };
 // A label placed away from its point gets a thin leader to it.
 const leader = (x, y, r, box) => {
  const nx = Math.min(box.r, Math.max(box.l, x)), ny = Math.min(box.b, Math.max(box.t, y)), d = Math.hypot(nx - x, ny - y);
  if (d > r + 10) marks.append(make('svg:line', {class: 'leader', x1: x + (nx - x) / d * (r + 2), y1: y + (ny - y) / d * (r + 2), x2: nx, y2: ny}));
 };
 const dot = (x, y, r) => taken.push({l: x - r, r: x + r, t: y - r, b: y + r});
 dot(px(FROST), py(used(FROST)), 6);
 if (showNow) dot(px(data.outdoor), py(base), 12);
 const around = (x, y, gapX, gapY) => [[x + gapX, y - gapY, 'start'], [x + gapX, y + gapY + 12, 'start'], [x - gapX, y - gapY, 'end'],
  [x - gapX, y + gapY + 12, 'end'], [x, y - gapY - 6, 'middle'], [x, y + gapY + 18, 'middle']];
 if (showNow) {
  const x = px(data.outdoor), y = py(base);
  const box = place({'data-label': 'now'}, nowRows, [...around(x, y, 14, 12), ...around(x, y, 14, 28)], true, [x, y]);
  if (box) leader(x, y, 6, box);
 }
 // The hard-frost point is the line at −10 °C for the room temperature the curve starts from (WeatherCurve), so it
 // names that room temperature: the setting "water temperature in hard frost" is for a 20 °C room.
 const frostAt = flow => t('frost', {room: n(data.room, 1), flow: n(flow)});
 const frostRows = [frostAt(frost)];
 if (Math.abs(gain) >= 1) frostRows.push(t(gain > 0 ? 'lower' : 'higher', {n: n(Math.abs(gain))}));
 const fx = px(FROST), fy = py(used(FROST)), upper = Math.min(fy, standard ? py(standard(FROST)) : fy, own ? py(own(FROST)) : fy);
 const frostBox = place({'data-label': 'frost'}, frostRows,
  [[fx + 10, upper - 14 - 15 * (frostRows.length - 1), 'start'], ...around(fx, fy, 10, 10), ...around(fx, fy, 10, 30)], true, [fx, fy]);
 if (frostBox) leader(fx, fy, 5, frostBox);
 // Direct labels at the cold end, where the lines are furthest apart.
 for (const [f, key] of [[own, 'learned'], [standard, 'standard']]) {
  if (!f) continue;
  const x = px(x0) + 6, y = py(f(x0 + 0.5));
  place({'data-label': key}, [t(key === 'learned' ? solid : key)], [[x, y - 9, 'start'], [x, y + 19, 'start']]);
 }
 // The crosshair: the nearest half degree under the pointer, or the arrow keys.
 const hair = make('svg:line', {class: 'cross', y1: M.top, y2: M.top + plotH, visibility: 'hidden'});
 const marksAt = [own && ['learned', own], standard && ['standard', standard]].filter(Boolean);
 const dots = marksAt.map(([key]) => make('svg:circle', {class: 'point ' + key, r: 4, visibility: 'hidden'}));
 cross.append(hair, ...dots, make('svg:rect', {class: 'hit', x: M.left, y: M.top, width: width - M.left - M.right, height: plotH}));
 let at = null;
 const show = (outdoor, announce) => {
  at = keep.at = Math.min(x1, Math.max(x0, Math.round(outdoor * 2) / 2));
  const x = px(at);
  hair.setAttribute('x1', x); hair.setAttribute('x2', x); hair.setAttribute('visibility', 'visible');
  const rows = marksAt.map(([key, f], i) => {
   dots[i].setAttribute('cx', x); dots[i].setAttribute('cy', py(f(at))); dots[i].setAttribute('visibility', 'visible');
   return [key, Math.round(f(at))];
  });
  const head = make('div', {class: 'tip-head'}, t('at', {outdoor: n(at, 1)}));
  const words = key => t(key === 'learned' ? solid : key);
  tip.replaceChildren(head, ...rows.map(([key, value]) => {
   const row = make('div', {class: 'tip-row'});
   row.append(make('i', {class: 'key ' + key}), make('b', {}, n(value) + ' °C'), make('span', {}, words(key)));
   return row;
  }));
  tip.hidden = false;
  const left = Math.min(width - tip.offsetWidth - 2, Math.max(2, x + (x > width / 2 ? -tip.offsetWidth - 12 : 12)));
  tip.style.transform = `translate(${left}px, ${M.top}px)`;
  if (announce) live.textContent = [head.textContent, ...rows.map(([key, value]) => words(key) + ' ' + n(value) + ' °C')].join(', ');
 };
 const hide = () => { at = keep.at = null; tip.hidden = true; hair.setAttribute('visibility', 'hidden'); dots.forEach(d => d.setAttribute('visibility', 'hidden')); };
 const outdoorAt = event => { const box = svg.getBoundingClientRect(); return x0 + ((event.clientX - box.left) / box.width * width - M.left) / (width - M.left - M.right) * (x1 - x0); };
 svg.addEventListener('pointermove', e => show(outdoorAt(e)));
 svg.addEventListener('pointerdown', e => show(outdoorAt(e)));
 svg.addEventListener('pointerleave', e => { if (e.pointerType !== 'touch') hide(); });
 svg.addEventListener('focus', () => { keep.focus = true; show(at ?? data.outdoor ?? 0, true); });
 // Leaving the chart hides the crosshair; a redraw that replaces this chart does not.
 svg.addEventListener('blur', () => { if (svg.isConnected) { keep.focus = false; hide(); } });
 svg.addEventListener('keydown', e => {
  const step = {ArrowLeft: -1, ArrowRight: 1, ArrowDown: -1, ArrowUp: 1}[e.key];
  if (step) { e.preventDefault(); show((at ?? data.outdoor ?? 0) + step * (e.shiftKey ? 5 : 1), true); }
  else if (e.key === 'Home' || e.key === 'End') { e.preventDefault(); show(e.key === 'Home' ? x0 : x1, true); }
  else if (e.key === 'Escape') hide();
 });
 // The chart's accessible name: what it shows, in one sentence per line.
 const name = [t('title')];
 if (standard) name.push(t('standard') + ': ' + frostAt(Math.round(standard(FROST))));
 if (own) name.push(t(solid) + ': ' + frostAt(Math.round(own(FROST))));
 if (showNow) name.push(t('now') + ': ' + nowRows.join(', '));
 svg.setAttribute('aria-label', name.join('. '));
 // A redraw keeps what the viewer had: the crosshair where it was, the keyboard focus on the chart.
 if (refocus) svg.focus({preventScroll: true});
 if (was !== null) show(was);
 return {standard, own, frost, gain, x0, x1, solid};
}

function table(model, t, n) {
 const box = make('details', {class: 'values'}), body = make('table');
 box.append(make('summary', {}, t('values')), body);
 const head = make('tr');
 head.append(make('th', {scope: 'col'}, t('outside')));
 for (const key of ['standard', 'learned']) if (model[key === 'learned' ? 'own' : 'standard']) head.append(make('th', {scope: 'col'}, t(key === 'learned' ? model.solid : key)));
 body.append(head);
 for (let v = Math.ceil(model.x0 / 5) * 5; v <= model.x1; v += 5) {
  const row = make('tr');
  row.append(make('td', {}, n(v) + ' °C'));
  for (const f of [model.standard, model.own]) if (f) row.append(make('td', {}, n(Math.round(f(v))) + ' °C'));
  body.append(row);
 }
 return box;
}

class OpenThermostatCard extends HTMLElement {
 constructor() { super(); this.attachShadow({mode: 'open'}); this._key = null; }
 setConfig(config) {
  if (!config || typeof config.entity !== 'string' || !config.entity.startsWith('sensor.')) throw new Error(this.constructor.configError);
  this._config = config; this._key = null;
  if (this._hass) this.render();
 }
 set hass(hass) {
  this._hass = hass;
  // Only a new state, language or theme redraws; Home Assistant sets hass on every change in the house.
  const st = hass?.states?.[this._config?.entity], key = [st, locale(hass), darkOf(hass), this.trial()];
  if (this._key && key.every((v, i) => v === this._key[i])) return;
  this._key = key; this.render();
 }
 getGridOptions() { return {columns: 12, min_columns: 6}; }
 // HA 1.0.1: the trial run, or active control before the takeover is confirmed (the heat request's mode and control,
 // config ``request``): the E32 asks the boiler nothing, so the curve card says what it would ask (as the house card).
 trial() {
  const a = this._config?.request ? this._hass?.states?.[this._config.request]?.attributes : null;
  return !!a && (a.mode === 'shadow' || a.control === 'awaiting_confirmation');
 }
 // A text of the integration's translations, its {placeholders} filled; English when Home Assistant has none.
 text(base, fallback, key, values = {}) {
  let text = '';
  try { text = this._hass?.localize?.(PREFIX + base + key, values) || ''; } catch (e) { text = ''; }
  return typeof text === 'string' && text ? text : fallback[key].replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all);
 }
 // A number in the viewer's language, with a real minus sign.
 number(value, digits = 0) {
  return value.toLocaleString(locale(this._hass), {maximumFractionDigits: digits, minimumFractionDigits: 0, useGrouping: false}).replace('-', '−');
 }
 frame(style) {
  theme(this, this._hass);
  const card = make('ha-card', darkOf(this._hass) ? {class: 'dark'} : {});
  this.shadowRoot.replaceChildren(make('style', {}, style), card);
  return card;
 }
 missing(card, config, st) {
  if (st) return false;
  const text = this._hass.localize?.('ui.panel.lovelace.warning.entity_not_found', {entity: config.entity}) || 'Entity not available: ' + config.entity;
  card.append(make('p', {class: 'muted'}, text));
  return true;
 }
}

class OpenThermostatHeatingCurve extends OpenThermostatCard {
 static configError = 'This card needs the "Water temperature by weather compensation" sensor of OpenThermostat (entity: sensor.…); the OpenThermostat dashboard adds it for you.';
 constructor() { super(); this._resize = null; this._width = 0; this._keep = {at: null, focus: false}; }
 getCardSize() { return 6; }
 disconnectedCallback() { this._resize?.disconnect(); this._resize = null; }
 render() {
  const hass = this._hass, config = this._config;
  if (!hass || !config) return;
  const trial = this.trial();
  const t = (key, values) => this.text('flow_curve.state_attributes.chart.state.', CURVE_TEXT,
   trial && key === 'asks' ? 'would_ask' : key, values);
  const n = (v, d) => this.number(v, d);
  const card = this.frame(CURVE_STYLE), st = hass.states?.[config.entity];
  // show_name: false where a heading above the card already says it (the Learning view's own section, rc.5).
  if (config.show_name !== false) card.append(make('h2', {}, config.name || t('title')));
  if (this.missing(card, config, st)) return;
  // Everything in °C from the attributes, never from the state (Home Assistant converts that on an imperial system).
  const a = st.attributes || {}, slope = numeric(a.slope), usable = slope !== null && slope > 0;
  const data = {standardSlope: numeric(a.standard_slope) ?? (a.slope_source === 'design' && usable ? slope : null), slope,
   room: numeric(a.room_c) ?? 20, low: numeric(a.minimum_flow_c), high: numeric(a.maximum_flow_c), outdoor: numeric(a.outdoor_c),
   base: numeric(a.base_c), now: numeric(a.flow_c), house: a.slope_source === 'house',
   learned: (a.slope_source === 'learned' || a.slope_source === 'house') && usable};
  if (data.standardSlope === null && !data.learned) { card.append(make('p', {class: 'muted'}, t('waiting'))); return; }
  const legend = make('ul', {class: 'legend'});
  const key = (cls, label) => { const li = make('li', {'data-key': cls}); li.append(make('i', {class: 'key ' + cls}), label); legend.append(li); };
  if (data.standardSlope !== null) key('standard', t('standard'));
  if (data.learned) key('learned', t(data.house ? 'house' : 'learned'));
  if (data.outdoor !== null) key('now', t('now'));
  const plot = make('div', {class: 'plot'});
  card.append(legend, plot);
  // 1.4.3: the steepness of the line in use in one sentence (learned, estimated from the house, or the standard one).
  const steep = data.learned ? data.slope : data.standardSlope;
  if (steep !== null && steep > 0)
   card.append(make('p', {class: 'slope', 'data-slope': data.learned ? (data.house ? 'house' : 'learned') : 'standard'},
    t(data.learned ? (data.house ? 'slope_house' : 'slope_learned') : 'slope_standard', {s: n(steep, 2)})));
  card.append(make('p', {class: 'caption'}, t('caption')));
  if (a.state === 'advice') card.append(make('p', {class: 'note'}, t('off')));
  const draw = () => {
   this._width = plot.clientWidth;
   const model = drawCurve(plot, data, t, n, this._keep), old = card.querySelector('details.values'), values = table(model, t, n);
   values.open = !!old?.open; // an open table stays open over a new width
   old?.remove();
   card.append(values);
  };
  draw();
  // Drawn at the card's own width, so the text stays 12 px on a phone; again when the width changes.
  this._resize?.disconnect();
  if (typeof ResizeObserver === 'function') {
   this._resize = new ResizeObserver(() => { if (plot.isConnected && Math.abs(plot.clientWidth - this._width) > 2) draw(); });
   this._resize.observe(plot);
  }
 }
}

class OpenThermostatKnowledge extends OpenThermostatCard {
 static configError = 'This card needs the Knowledge sensor of OpenThermostat (entity: sensor.…); the OpenThermostat dashboard adds it for you.';
 getCardSize() { return 3; }
 render() {
  const hass = this._hass, config = this._config;
  if (!hass || !config) return;
  const t = (key, values) => this.text('knowledge.state_attributes.card.state.', KNOWLEDGE_TEXT, key, values);
  const card = this.frame(KNOWLEDGE_STYLE), st = hass.states?.[config.entity];
  if (this.missing(card, config, st)) return;
  const pct = numeric(st.state), a = st.attributes || {};
  const missing = Array.isArray(a.missing) ? a.missing.filter(s => typeof s === 'string' && s) : [];
  const more = Number.isInteger(a.more) && a.more > 0 ? a.more : 0, open = missing.length > 0 || more > 0;
  // One story on the card (rc.7): while something is still to learn the figure stays below 100 % (a rounded 99.6 % read
  // as "100 %" over a list of what it still learns), and "learned everything" only at 100 % with nothing left. Then
  // that line says it all, so the hint that it learns while the heating runs is left out; learning never ends: it keeps
  // checking as the seasons change.
  let share = pct === null ? null : Math.min(100, Math.max(0, pct));
  if (share !== null && (open || share < 100)) share = Math.min(99, share);
  const complete = share === 100 && !open;
  const head = make('div', {class: 'head'}), words = make('div');
  // The headline beside the ring says the figure ("The E32 knows your house: 62 %", the owner's sketch, rc.5).
  words.append(make('h2', {}, config.name || (share === null ? t('title') : t('ring', {pct: this.number(share)}))));
  if (!complete) words.append(make('p', {class: 'muted'}, pct === null ? t('waiting') : t('hint')));
  if (pct !== null) {
   const r = 30, length = 2 * Math.PI * r;
   const ring = make('svg:svg', {class: 'ring', viewBox: '0 0 72 72', role: 'img', 'aria-label': t('ring', {pct: this.number(share)})});
   ring.append(make('svg:circle', {class: 'track', cx: 36, cy: 36, r, fill: 'none', 'stroke-width': 7}));
   if (share > 0) ring.append(make('svg:circle', {class: 'fill', cx: 36, cy: 36, r, fill: 'none', 'stroke-width': 7, 'stroke-linecap': 'round',
    'stroke-dasharray': `${(share / 100 * length).toFixed(2)} ${length.toFixed(2)}`, transform: 'rotate(-90 36 36)'}));
   ring.append(make('svg:text', {x: 36, y: 41.5, 'text-anchor': 'middle'}, this.number(share) + ' %'));
   head.append(ring);
  }
  head.append(words);
  card.append(head);
  if (pct === null) return;
  if (complete) card.append(make('p', {class: 'done'}, t('done')));
  // 1.4.3: the learning path (insight.knowledge_path): learned parts green with a check, parts it still learns amber with
  // a clock and what they still need; a part Home Assistant cannot tell about ("unknown") has no label, never a check.
  const path = (Array.isArray(a.path) ? a.path : []).filter(p => p && typeof p.name === 'string' && p.name
   && (p.state === 'learned' || p.state === 'busy'));
  if (!path.length) return;
  const list = make('ul', {class: 'path', 'aria-label': t('path')});
  for (const state of ['learned', 'busy']) for (const part of path.filter(p => p.state === state)) {
   const detail = typeof part.detail === 'string' && part.detail ? part.detail : '';
   const label = part.name + (detail ? ' · ' + detail : ''), box = make('span', {class: 'ic', 'aria-hidden': 'true'});
   const svg = make('svg:svg', {viewBox: '0 0 24 24', focusable: 'false'});
   svg.append(make('svg:path', {d: PATH_ICONS[state === 'learned' ? 'check' : 'clock-outline'], fill: 'currentColor'}));
   box.append(svg);
   const chip = make('li', {class: 'chip ' + state, 'data-key': typeof part.key === 'string' ? part.key : null, 'data-state': state,
    title: label, 'aria-label': t(state, {name: label})});
   chip.append(box, make('span', {}, label));
   list.append(chip);
  }
  card.append(list);
 }
}

// 1.4.3 (design 4.2 item 3): what the E32 learned from the boiler, as tiles, under the curve on the Learning view.
// Config: boiler (the Boiler response sensor), learned (the learned overview), curve (its outdoor temperature for the
// band), smart (the Smart warm-up switch). Only Home Assistant's states; only tiles with a value.
class OpenThermostatBoilerLearned extends HTMLElement {
 constructor() { super(); this.attachShadow({mode: 'open'}); this._key = null; }
 setConfig(config) {
  const id = value => typeof value === 'string' && value.startsWith('sensor.') ? value : null;
  if (!config || !id(config.boiler)) throw new Error('This card needs the "Boiler response" sensor of OpenThermostat (boiler: sensor.…); the OpenThermostat dashboard adds it for you.');
  this._config = {boiler: config.boiler, learned: id(config.learned), curve: id(config.curve),
   smart: typeof config.smart === 'string' ? config.smart : null};
  this._key = null;
  if (this._hass) this.render();
 }
 set hass(hass) {
  this._hass = hass;
  if (!this._config) return;
  const c = this._config, key = [c.boiler, c.learned, c.curve, c.smart].map(id => id && hass?.states?.[id]).concat([locale(hass), darkOf(hass)]);
  if (this._key && key.every((v, i) => v === this._key[i])) return;
  this._key = key; this.render();
 }
 getCardSize() { return 2; }
 getGridOptions() { return {columns: 12, min_columns: 6}; }
 words(key, values = {}) {
  const table = BOILER_TEXT[/^nl\b/.test(locale(this._hass)) ? 'nl' : 'en'];
  return String(table[key] ?? BOILER_TEXT.en[key]).replace(/\{(\w+)\}/g, (all, k) => k in values ? values[k] : all);
 }
 number(value, digits = 0) {
  return value.toLocaleString(locale(this._hass), {maximumFractionDigits: digits, minimumFractionDigits: 0, useGrouping: false}).replace('-', '−');
 }
 render() {
  const hass = this._hass, c = this._config;
  if (!hass || !c) return;
  if (darkOf(hass)) this.setAttribute('data-theme', 'dark'); else this.removeAttribute('data-theme');
  const st = id => (id ? hass.states?.[id] : null) || null, ok = s => !!s && !['unknown', 'unavailable', ''].includes(s.state);
  const boiler = st(c.boiler), learned = st(c.learned), b = ok(boiler) ? boiler.attributes || {} : {}, l = ok(learned) ? learned.attributes || {} : {};
  const deg = v => this.number(Math.round(v)) + ' °C', tiles = [];
  const tile = (key, value, label) => {
   const box = make('div', {class: 'tile', 'data-fact': key, title: label});
   box.append(make('p', {class: 'value'}, value), make('p', {class: 'label'}, label));
   tiles.push(box);
  };
  const ceiling = numeric(b.ceiling_c);
  if (ok(boiler) && boiler.state === 'learned' && ceiling !== null) {
   // The outdoor band the ceiling belongs to (BoilerResponse: 5 K bands from −10 °C, below −5 and from 15 °C open).
   const o = numeric(st(c.curve)?.attributes?.outdoor_c), k = o === null ? null : Math.min(5, Math.max(0, Math.floor((o + 10) / 5)));
   const when = k === null ? this.words('band_none') : k === 0 ? this.words('band_low', {high: this.number(-5)})
    : k === 5 ? this.words('band_high', {low: this.number(15)}) : this.words('band', {low: this.number(-10 + 5 * k), high: this.number(-5 + 5 * k)});
   const off = st(c.smart)?.state === 'off';
   tile('ceiling', deg(ceiling + HELD_ABOVE_CEILING_C), this.words(off ? 'ceiling_off' : 'ceiling', {when, asks: deg(ceiling)}));
  }
  const rest = numeric(b.rest_min);
  if (ok(boiler) && boiler.state === 'learned' && rest !== null && rest > 0)
   tile('rest', this.words('min', {n: this.number(Math.max(1, Math.round(rest)))}), this.words('rest'));
  const steady = numeric(l.steady_burn_floor_c), start = numeric(l.boiler_minimum_flow_c);
  if (steady !== null) tile('steady', deg(steady), this.words('steady'));
  if (start !== null) tile('start', deg(start), this.words('start'));
  const sentence = ok(boiler) && boiler.state !== 'learned' && typeof b.sentence === 'string' ? b.sentence : '';
  const card = make('ha-card', darkOf(hass) ? {class: 'dark'} : {}), wrap = make('div', {class: 'wrap'});
  card.append(wrap);
  if (sentence) wrap.append(make('p', {class: 'sentence', 'data-sentence': ''}, sentence));
  if (tiles.length) {
   const grid = make('div', {class: 'tiles'});
   grid.style.setProperty('--n', Math.min(4, tiles.length));
   grid.append(...tiles);
   wrap.append(grid);
  }
  // Nothing to show: no card at all (the section's other card, the curve, stands alone).
  this.style.display = sentence || tiles.length ? '' : 'none';
  this.shadowRoot.replaceChildren(make('style', {}, BOILER_STYLE), card);
 }
}
// Other dashboard cards (HACS resources) may later replace window.customElements with a scoped-registry
// polyfill whose get() does not see elements defined before it; Home Assistant then reports "Custom element
// doesn't exist". So: define now, and again (a fresh subclass) whenever the registry in use lacks the element.
// Never throws. (The same guard as e32-week-card.js and room-status-card.js.)
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
 // A HACS card may replace window.customElements later (the owner's HA, 31 Oct 2026: an intermittent
 // "Configuration error" on the week view): a cheap check every 0.5 s puts the element back in the registry in
 // use, and Home Assistant's error card then rebuilds the card. 1.4.2 (P22): only for the first 30 s, when the other
 // cards load; after that a navigation (location-changed) or the page coming back into view checks again, so no
 // timer runs for ever on a wall tablet.
 const timer = setInterval(check, 500);
 setTimeout(() => clearInterval(timer), 30000);
 document.addEventListener('visibilitychange', check);
 return check;
};
ensureDefined('openthermostat-heating-curve', OpenThermostatHeatingCurve);
ensureDefined('openthermostat-knowledge', OpenThermostatKnowledge);
ensureDefined('openthermostat-boiler-learned', OpenThermostatBoilerLearned);
window.customCards = window.customCards || [];
for (const [type, name, description] of [
 ['openthermostat-heating-curve', 'OpenThermostat heating curve', 'Water temperature by outdoor temperature: the standard line, the one learned for your house and now.'],
 ['openthermostat-knowledge', 'OpenThermostat knowledge', 'How much the E32 knows about your house, and what it still learns.'],
 ['openthermostat-boiler-learned', 'OpenThermostat boiler learned', 'What the E32 learned from your boiler, as figures.']])
 if (!window.customCards.some(c => c.type === type)) window.customCards.push({type, name, description});
