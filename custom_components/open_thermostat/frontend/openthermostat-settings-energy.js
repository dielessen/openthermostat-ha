/* The section Energy and outdoor temperature of the settings panel (1.4): one screen with the eight optional fields of
   Configure → Energy and outdoor temperature, each entity with its value now beside it (the kit's entity picker). Backend
   settings_energy.py (Configure's own check and write); the words are Configure's. 1.4.1 (HA-INSTELPANEEL-FASE2.nl.md
   3.6, 7.2): one line of help per field with Configure's whole explanation behind "More", and the chosen entity's value
   large under it, following Home Assistant live. */
const TEXTS = {
 nl: {
  'Gas meter': 'Gasmeter',
  'A gas meter reading in m³ or kWh that only goes up (not a usage per hour), for example from a smart meter or a gas pulse counter. A reading in kWh is converted to m³ with the calorific value. It also splits your gas into heating and hot water for the Energy dashboard.': 'Een gasmeterstand in m³ of kWh die alleen oploopt (geen verbruik per uur), bijvoorbeeld van een slimme meter of een gaspulsteller. Een stand in kWh wordt met de calorische waarde omgerekend naar m³. Hij verdeelt ook je gas over verwarmen en warm water voor het energiedashboard.',
  'Gas price sensor': 'Gasprijssensor',
  'A sensor or input number with the gas price per m³ or per kWh (unit such as EUR/m³ or GBP/kWh). Use this or a fixed price, not both.': 'Een sensor of invoergetal met de gasprijs per m³ of per kWh (eenheid zoals EUR/m³ of GBP/kWh). Gebruik dit of een vaste prijs, niet allebei.',
  'Fixed gas price': 'Vaste gasprijs',
  'The price per m³ of gas in your Home Assistant currency when you have no price sensor, for example 1.35.': 'De prijs per m³ gas in de valuta van je Home Assistant als je geen prijssensor hebt, bijvoorbeeld 1,35.',
  'Calorific value of the gas': 'Calorische waarde van het gas',
  'Energy per m³ of gas; your gas bill or supplier states it. Empty: 9.77 kWh/m³ (Dutch gas). Elsewhere it differs, for example about 11 kWh/m³ in the UK; natural gas is usually between 8 and 12 kWh/m³.': 'Energie per m³ gas; die staat op je jaarafrekening of vraag je aan je leverancier. Leeg: 9,77 kWh/m³ (Nederlands gas). Elders is het anders, bijvoorbeeld ongeveer 11 kWh/m³ in het Verenigd Koninkrijk; aardgas zit meestal tussen 8 en 12 kWh/m³.',
  'Outdoor temperature': 'Buitentemperatuur',
  'A temperature sensor outside (°C or °F) or a weather entity. It helps the E32 learn how fast rooms cool down.': 'Een temperatuursensor buiten (°C of °F) of een weerentiteit. Daarmee leert de E32 hoe snel ruimtes afkoelen.',
  'Weather forecast': 'Weersverwachting',
  'A weather entity with an hourly forecast. Every hour Home Assistant sends the outdoor temperature of the next 24 hours to the E32, so it can plan the heating ahead. When your outdoor temperature comes from a weather entity, that one is already filled in. Leave it empty for no forecast: the E32 then uses its own daily pattern of the outdoor temperature.': 'Een weerentiteit met een verwachting per uur. Elk uur stuurt Home Assistant de buitentemperatuur van de komende 24 uur naar de E32, zodat die de verwarming vooruit kan plannen. Komt je buitentemperatuur van een weerentiteit, dan staat die hier al ingevuld. Laat het leeg voor geen verwachting: de E32 gebruikt dan zijn eigen dagpatroon van de buitentemperatuur.',
  'Boiler heating power': 'Verwarmingsvermogen ketel',
  'The boiler\'s nominal heating power in kW (type plate or manual), 3–60 kW. Suggested: {boiler_kw_suggested} kW ({boiler_kw_basis}); empty keeps that suggestion.': 'Het nominale verwarmingsvermogen van de ketel in kW (typeplaatje of handleiding), 3–60 kW. Voorgesteld: {boiler_kw_suggested} kW ({boiler_kw_basis}); leeg houdt dat voorstel.',
  'Water meter': 'Watermeter',
  'Optional: a water flow (L/min) or a water meter reading (m³ or L) that only goes up. With it, a hot-water round with water flowing is counted as tapping and one without as keeping warm, more reliably than from the boiler\'s temperatures alone. It stays in Home Assistant. With a hot water tank there is no such split: the E32 counts the taps itself.': 'Optioneel: een waterdebiet (L/min) of een watermeterstand (m³ of L) die alleen oploopt. Daarmee telt een warmwaterronde met stromend water als tappen en een zonder als warmhouden, betrouwbaarder dan alleen uit de temperaturen van de ketel. Hij blijft in Home Assistant. Met een warmwatervat is er geen splitsing: de E32 telt het tappen zelf.',
  'This sensor no longer exists in Home Assistant.': 'Deze sensor bestaat niet meer in Home Assistant.',
  'Choose a gas meter sensor in m³, or in kWh with device class gas or energy.': 'Kies een gasmetersensor in m³, of in kWh met apparaatklasse gas of energie.',
  'Choose a meter reading (state class total or total increasing), not a usage rate.': 'Kies een meterstand (statusklasse total of total increasing), geen verbruikssnelheid.',
  'Choose a price per m³ or per kWh (unit such as EUR/m³ or GBP/kWh).': 'Kies een prijs per m³ of per kWh (eenheid zoals EUR/m³ of GBP/kWh).',
  'Enter a gas price above 0 and at most 1000 (per m³ or per kWh, in your own currency).': 'Vul een gasprijs in boven 0 en hoogstens 1000 (per m³ of per kWh, in je eigen valuta).',
  'Use a gas price sensor or a fixed gas price, not both.': 'Gebruik een gasprijssensor of een vaste gasprijs, niet allebei.',
  'The calorific value must be between 5 and 15 kWh/m³.': 'De calorische waarde moet tussen 5 en 15 kWh/m³ liggen.',
  'Choose a temperature sensor in °C or °F, or a weather entity with a temperature.': 'Kies een temperatuursensor in °C of °F, of een weerentiteit met een temperatuur.',
  'The boiler power must be between 3 and 60 kW.': 'Het ketelvermogen moet tussen 3 en 60 kW liggen.',
  'Choose a water flow sensor (L/min, L/h, m³/h) or a water meter reading (m³, L).': 'Kies een waterdebietsensor (L/min, L/h, m³/h) of een watermeterstand (m³, L).',
  'Choose a water meter reading (state class total or total increasing), or a flow sensor in L/min.': 'Kies een watermeterstand (state class total of total increasing), of een debietsensor in L/min.',
  'Choose a weather entity (weather.…) for the forecast.': 'Kies een weerentiteit (weather.…) voor de verwachting.',
  'This weather entity gives no hourly forecast. Choose another one, or leave the field empty.': 'Deze weerentiteit geeft geen verwachting per uur. Kies een andere, of laat het veld leeg.',
  'A meter reading in m³ or kWh that only goes up.': 'Een meterstand in m³ of kWh die alleen oploopt.',
  'The gas price per m³ or per kWh, from a sensor.': 'De gasprijs per m³ of per kWh, uit een sensor.',
  'Without a price sensor: the price per m³ of gas.': 'Zonder prijssensor: de prijs per m³ gas.',
  'On your gas bill. Empty: 9.77 kWh/m³ (Dutch gas).': 'Staat op je jaarafrekening. Leeg: 9,77 kWh/m³ (Nederlands gas).',
  'A temperature sensor outside, or a weather entity.': 'Een temperatuursensor buiten, of een weerentiteit.',
  'A weather entity with an hourly forecast, to plan ahead.': 'Een weerentiteit met een verwachting per uur, om vooruit te plannen.',
  'Type plate or manual, 3–60 kW. Suggested: {boiler_kw_suggested} kW ({boiler_kw_basis}).': 'Typeplaatje of handleiding, 3–60 kW. Voorgesteld: {boiler_kw_suggested} kW ({boiler_kw_basis}).',
  'Optional: a water flow, or a meter reading that only goes up.': 'Optioneel: een waterdebiet, of een meterstand die alleen oploopt.',
  'Optional. With these the E32 calibrates its heat and gas estimates; without them everything keeps working.': 'Optioneel. Hiermee kalibreert de E32 zijn warmte- en gasschattingen; zonder werkt alles ook.',
  'Now': 'Nu',
  'measured with your gas meter': 'gemeten met je gasmeter',
  'reported by the boiler': 'gemeld door de ketel',
  'known for this boiler type': 'bekend voor dit keteltype',
  'a default value: check the type plate': 'een standaardwaarde: controleer het typeplaatje',
  'Energy and outdoor temperature': 'Energie en buitentemperatuur'
 }};
const ERRORS = {
 entity_not_found: 'This sensor no longer exists in Home Assistant.',
 gas_meter_unit: 'Choose a gas meter sensor in m³, or in kWh with device class gas or energy.',
 gas_meter_not_total: 'Choose a meter reading (state class total or total increasing), not a usage rate.',
 gas_price_unit: 'Choose a price per m³ or per kWh (unit such as EUR/m³ or GBP/kWh).',
 gas_price_invalid: 'Enter a gas price above 0 and at most 1000 (per m³ or per kWh, in your own currency).',
 gas_price_twice: 'Use a gas price sensor or a fixed gas price, not both.',
 gas_kwh_per_m3_invalid: 'The calorific value must be between 5 and 15 kWh/m³.',
 outdoor_unit: 'Choose a temperature sensor in °C or °F, or a weather entity with a temperature.',
 boiler_kw_invalid: 'The boiler power must be between 3 and 60 kW.',
 water_meter_unit: 'Choose a water flow sensor (L/min, L/h, m³/h) or a water meter reading (m³, L).',
 water_meter_not_total: 'Choose a water meter reading (state class total or total increasing), or a flow sensor in L/min.',
 forecast_not_weather: 'Choose a weather entity (weather.…) for the forecast.',
 forecast_no_hourly: 'This weather entity gives no hourly forecast. Choose another one, or leave the field empty.'};
// Where the suggested boiler power comes from (boiler_power.BASIS).
const BASIS = {gas_meter: 'measured with your gas meter', boiler: 'reported by the boiler', product: 'known for this boiler type',
 default: 'a default value: check the type plate'};
const SUBTITLES = {energy: 'Optional. With these the E32 calibrates its heat and gas estimates; without them everything keeps working.'};
// The chosen entity's value now, large under its field (a weather entity: its temperature); nothing while none is chosen.
function nowValues(ctx) {
 const {kit, t, lang} = ctx, boxes = new Map();
 const shown = st => {
  if (!st || ['unknown', 'unavailable'].includes(st.state)) return null;
  const a = st.attributes || {};
  if (st.entity_id?.startsWith('weather.') && typeof a.temperature === 'number') return {value: a.temperature.toLocaleString(lang, {maximumFractionDigits: 1}), unit: a.temperature_unit || '°C'};
  const n = Number(st.state);
  if (st.state !== '' && Number.isFinite(n)) return {value: n.toLocaleString(lang, {maximumFractionDigits: 3}), unit: a.unit_of_measurement || ''};
  let text = st.state;
  try { text = ctx.hass.formatEntityState?.(st) || st.state; } catch (e) { /* older Home Assistant */ }
  return {value: text, unit: ''};
 };
 const draw = (key, hass) => {
  const el = boxes.get(key), v = shown(hass?.states?.[ctx.values[key]]);
  if (!el) return;
  el.hidden = !v;
  el.replaceChildren(...(v ? [kit.valueDisplay({value: v.value, unit: v.unit || null, label: t('Now')})] : []));
 };
 const now = key => {
  const el = kit.h('div', {class: 'en-now', 'data-now': key});
  el._live = hass => draw(key, hass);
  boxes.set(key, el); draw(key, ctx.hass);
  return el;
 };
 now.update = () => queueMicrotask(() => { for (const key of boxes.keys()) draw(key, ctx.hass); });
 return now;
}
const STYLE = `.en-now{padding-top:2px}.en-now .ot-value-figure{overflow-wrap:anywhere;white-space:normal}`;
const FIELDS = ['gas_meter', 'gas_price_entity', 'gas_price', 'gas_kwh_per_m3', 'outdoor_entity', 'forecast_entity', 'boiler_kw', 'water_meter'];

(window.OpenThermostatSettingsSections ||= []).push(['energy', {
 title: 'Energy and outdoor temperature',
 subtitle: () => SUBTITLES.energy,
 texts: TEXTS,
 errors: ERRORS,
 values: m => Object.fromEntries(FIELDS.map(k => [k, m[k] === '' ? (['gas_price', 'gas_kwh_per_m3', 'boiler_kw'].includes(k) ? null : '') : m[k]])),
 render: ctx => {
  const {kit, t, model: m, lang} = ctx, live = m.live || {};
  const basis = t(BASIS[live.boiler_kw_basis] || BASIS.default) + (live.boiler_kw_basis === 'product' && live.boiler_model ? `: ${live.boiler_model}` : '');
  const temperature = (st, eid) => eid.startsWith('weather.') || (eid.startsWith('sensor.') && st?.attributes?.device_class === 'temperature');
  const suggested = {boiler_kw_suggested: typeof live.boiler_kw_suggested === 'number' ? live.boiler_kw_suggested.toLocaleString(lang) : '–', boiler_kw_basis: basis};
  const now = nowValues(ctx);
  const box = kit.h('div', {class: 'fields', 'data-screen': 'energy'},
   ctx.field('entity', 'gas_meter', {label: t('Gas meter'), domains: ['sensor'], onChange: now.update, help: t('A meter reading in m³ or kWh that only goes up.'),
    more: t('A gas meter reading in m³ or kWh that only goes up (not a usage per hour), for example from a smart meter or a gas pulse counter. A reading in kWh is converted to m³ with the calorific value. It also splits your gas into heating and hot water for the Energy dashboard.')}),
   now('gas_meter'),
   ctx.field('entity', 'gas_price_entity', {label: t('Gas price sensor'), domains: ['sensor', 'input_number'], onChange: now.update,
    help: t('The gas price per m³ or per kWh, from a sensor.'), more: t('A sensor or input number with the gas price per m³ or per kWh (unit such as EUR/m³ or GBP/kWh). Use this or a fixed price, not both.')}),
   now('gas_price_entity'),
   ctx.field('number', 'gas_price', {label: t('Fixed gas price'), unit: `${m.currency}/m³`, min: 0, max: 1000, step: 'any',
    help: t('Without a price sensor: the price per m³ of gas.'), more: t('The price per m³ of gas in your Home Assistant currency when you have no price sensor, for example 1.35.')}),
   ctx.field('number', 'gas_kwh_per_m3', {label: t('Calorific value of the gas'), unit: 'kWh/m³', min: 5, max: 15, step: 0.01,
    help: t('On your gas bill. Empty: 9.77 kWh/m³ (Dutch gas).'), more: t('Energy per m³ of gas; your gas bill or supplier states it. Empty: 9.77 kWh/m³ (Dutch gas). Elsewhere it differs, for example about 11 kWh/m³ in the UK; natural gas is usually between 8 and 12 kWh/m³.')}),
   ctx.field('entity', 'outdoor_entity', {label: t('Outdoor temperature'), filter: temperature, onChange: now.update,
    help: t('A temperature sensor outside, or a weather entity.'), more: t('A temperature sensor outside (°C or °F) or a weather entity. It helps the E32 learn how fast rooms cool down.')}),
   now('outdoor_entity'),
   ctx.field('entity', 'forecast_entity', {label: t('Weather forecast'), domains: ['weather'], onChange: now.update,
    help: t('A weather entity with an hourly forecast, to plan ahead.'), more: t('A weather entity with an hourly forecast. Every hour Home Assistant sends the outdoor temperature of the next 24 hours to the E32, so it can plan the heating ahead. When your outdoor temperature comes from a weather entity, that one is already filled in. Leave it empty for no forecast: the E32 then uses its own daily pattern of the outdoor temperature.')}),
   now('forecast_entity'),
   ctx.field('number', 'boiler_kw', {label: t('Boiler heating power'), unit: 'kW', min: 3, max: 60, step: 0.1,
    help: t('Type plate or manual, 3–60 kW. Suggested: {boiler_kw_suggested} kW ({boiler_kw_basis}).', suggested),
    more: t('The boiler\'s nominal heating power in kW (type plate or manual), 3–60 kW. Suggested: {boiler_kw_suggested} kW ({boiler_kw_basis}); empty keeps that suggestion.', suggested)}),
   ctx.field('entity', 'water_meter', {label: t('Water meter'), domains: ['sensor'], onChange: now.update,
    help: t('Optional: a water flow, or a meter reading that only goes up.'), more: t('Optional: a water flow (L/min) or a water meter reading (m³ or L) that only goes up. With it, a hot-water round with water flowing is counted as tapping and one without as keeping warm, more reliably than from the boiler\'s temperatures alone. It stays in Home Assistant. With a hot water tank there is no such split: the E32 counts the taps itself.')}),
   now('water_meter'));
  // Each value under its own field; the style last (the first field stays the first child).
  box.append(kit.h('style', {text: STYLE}));
  for (const el of [...box.querySelectorAll('[data-now]')]) box.querySelector(`[data-field="${el.dataset.now}"]`)?.append(el);
  return box;
 },
 // The values now follow Home Assistant without a redraw.
 live: (root, hass) => { for (const el of root.querySelectorAll('.page-col [data-now]')) el._live?.(hass); }
}]);
