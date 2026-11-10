/* The settings panel of the OpenThermostat dashboard: the tab "Settings" / "Instellen" / "Ustawienia" (1.4; 1.4.1 phase 2).
   One web component that knows only `hass` and its route (after #: #overview, #<section>, #<section>/<item>, #room/<id>;
   pushState and popstate); backend settings.py. This core is the only module every Home Assistant page loads; when the
   tab opens it loads the component kit (openthermostat-settings-kit.js, window.OpenThermostatSettingsKit) and the section
   modules from the overview's `modules` list. The core draws the overview (seven entries; on a wide screen the
   installation at a glance beside them), the frame, the save bar, the read-only sentence, the "changed elsewhere" banner
   and the fallback page; a section draws its screens with the kit. Texts: TEXTS, English key, Dutch and Polish values
   (test/ha-settings-texts.test.cjs). How to build a section: HA-INSTELPANEEL-ONTWERP.nl.md chapter 10 and
   HA-INSTELPANEEL-FASE2.nl.md chapter 4. */
// The overview's seven entries: [route, title, icon]; "installation" is the section of that name once one is
// registered, else Dashboard and name and Advanced on one page.
const ENTRIES = [['rooms', 'Rooms', 'thermostat'], ['house', 'House', 'home'], ['heating', 'Heating and boiler', 'fire'], ['devices', 'Devices', 'devices'],
 ['notifications', 'Notifications', 'bell'], ['energy', 'Energy and outdoor temperature', 'flash'], ['installation', 'Installation', 'wrench']];
const TITLES = {rooms: 'Rooms', house: 'House', heating: 'Heating and boiler', devices: 'Devices', notifications: 'Notifications',
 energy: 'Energy and outdoor temperature', general: 'Dashboard and name', advanced: 'Advanced', installation: 'Installation'};
const WIDE = 960;
const CONFIGURE = '/config/integrations/integration/open_thermostat';
const TEXTS = {
 nl: {
  'Settings': 'Instellen',
  'Rooms': 'Ruimtes', 'House': 'Huis', 'Heating and boiler': 'Verwarming en ketel', 'Devices': 'Apparaten', 'Notifications': 'Meldingen',
  'Energy and outdoor temperature': 'Energie en buitentemperatuur', 'Dashboard and name': 'Dashboard en naam', 'Advanced': 'Geavanceerd',
  'Installation': 'Installatie',
  'Only an administrator of Home Assistant can change this.': 'Alleen een beheerder van Home Assistant kan dit wijzigen.',
  'Loading…': 'Laden…', 'Saving…': 'Opslaan…', 'Saved.': 'Opgeslagen.', 'You changed something.': 'Je hebt iets gewijzigd.',
  'Save': 'Opslaan', 'Undo': 'Ongedaan maken', 'Not saved': 'Niet opgeslagen',
  'Back to {page}': 'Terug naar {page}',
  'You change this part in Configure for now.': 'Dit onderdeel wijzig je voorlopig in Configureren.',
  'Connect the E32 first: Configure → E32 connection.': 'Verbind eerst de E32: Configureren → E32-verbinding.',
  'Open Configure': 'Configureren openen',
  'Changed elsewhere': 'Elders gewijzigd',
  'These settings were changed elsewhere while you were editing. What you changed is kept and marked; the rest now shows what is saved. Save again to keep your changes.': 'Deze instellingen zijn intussen elders gewijzigd. Wat jij wijzigde blijft staan en is gemarkeerd; de rest toont nu wat er is opgeslagen. Sla opnieuw op om je wijzigingen te bewaren.',
  'Changed by you': 'Door jou gewijzigd',
  'Changed by you; elsewhere it is now {value}.': 'Door jou gewijzigd; elders is het nu {value}.',
  'On': 'Aan', 'Off': 'Uit', 'Heat along only': 'Alleen meeverwarmen',
  'The E32 could not be reached. Check the connection and try again.': 'De E32 is niet bereikbaar. Controleer de verbinding en probeer het opnieuw.',
  'The change could not be confirmed. Reload the page to see what is saved.': 'De wijziging kon niet worden bevestigd. Laad de pagina opnieuw om te zien wat er is opgeslagen.',
  'This installation is not available. Look under Settings → Devices & services → OpenThermostat.': 'Deze installatie is niet beschikbaar. Kijk bij Instellingen → Apparaten en diensten → OpenThermostat.',
  'This page does not match the installed OpenThermostat. Reload the page.': 'Deze pagina past niet bij de geïnstalleerde OpenThermostat. Laad de pagina opnieuw.',
  'The settings were changed elsewhere. Reload the page and try again.': 'De instellingen zijn elders gewijzigd. Laad de pagina opnieuw en probeer het opnieuw.',
  'This version of Home Assistant cannot store this change. Update Home Assistant and try again.': 'Deze versie van Home Assistant kan deze wijziging niet bewaren. Werk Home Assistant bij en probeer het opnieuw.',
  'This value cannot be saved. Check the fields and try again.': 'Deze waarde kan niet worden opgeslagen. Controleer de velden en probeer het opnieuw.',
  'The change was not saved ({code}). Try again.': 'De wijziging is niet opgeslagen ({code}). Probeer het opnieuw.',
  'These settings could not be read ({code}). Reload the page.': 'Deze instellingen konden niet worden gelezen ({code}). Laad de pagina opnieuw.',
  'OpenThermostat was updated. Reload the page to use the new version.': 'OpenThermostat is bijgewerkt. Laad de pagina opnieuw om de nieuwe versie te gebruiken.',
  'The settings could not be loaded. Reload the page.': 'De instellingen konden niet worden geladen. Laad de pagina opnieuw.',
  'At a glance': 'In één oogopslag', 'Boiler': 'Ketel', 'Smart warm-up': 'Slim opwarmen', 'Weather compensation': 'Weerafhankelijke regeling',
  'Holiday until {until}': 'Vakantie tot {until}', 'Next holiday: {from} – {until}': 'Volgende vakantie: {from} – {until}',
  'No holiday planned': 'Geen vakantie gepland', 'No rooms yet': 'Nog geen ruimtes',
  // The section Dashboard and name: the words of Configure → Dashboard and name.
  'The name of this installation in Home Assistant and whether it shows the OpenThermostat dashboard.': 'De naam van deze installatie in Home Assistant en of het OpenThermostat-dashboard getoond wordt.',
  'Installation name': 'Naam installatie',
  'A recognisable name in Home Assistant. Your devices and their history stay as they are.': 'Een herkenbare naam in Home Assistant. Je apparaten en hun geschiedenis blijven zoals ze zijn.',
  'Show the OpenThermostat dashboard': 'OpenThermostat-dashboard tonen',
  'The OpenThermostat dashboard: your rooms at a glance, the week planner and the boiler. Your own dashboards are preserved.': 'Het OpenThermostat-dashboard: je ruimtes in één oogopslag, de weekplanner en de ketel. Je bestaande dashboards blijven behouden.',
  'Give a name of 1 to 80 characters.': 'Geef een naam van 1 tot 80 tekens.',
  'Hide the OpenThermostat dashboard?': 'OpenThermostat-dashboard verbergen?',
  'This tab goes with it. You can show the dashboard again in Configure → Dashboard and name.': 'Dit tabblad verdwijnt dan ook. Je kunt het dashboard weer tonen via Configureren → Dashboard en naam.',
  'Hide the dashboard': 'Dashboard verbergen'},
 pl: {
  'Settings': 'Ustawienia',
  'Rooms': 'Pomieszczenia', 'House': 'Dom', 'Heating and boiler': 'Ogrzewanie i kocioł', 'Devices': 'Urządzenia', 'Notifications': 'Powiadomienia',
  'Energy and outdoor temperature': 'Energia i temperatura zewnętrzna', 'Dashboard and name': 'Panel i nazwa', 'Advanced': 'Zaawansowane',
  'Installation': 'Instalacja',
  'Only an administrator of Home Assistant can change this.': 'Tylko administrator Home Assistant może to zmienić.',
  'Loading…': 'Ładowanie…', 'Saving…': 'Zapisywanie…', 'Saved.': 'Zapisano.', 'You changed something.': 'Wprowadzono zmiany.',
  'Save': 'Zapisz', 'Undo': 'Cofnij', 'Not saved': 'Niezapisane',
  'Back to {page}': 'Wróć do: {page}',
  'You change this part in Configure for now.': 'Tę część zmieniasz na razie w Konfiguruj.',
  'Connect the E32 first: Configure → E32 connection.': 'Najpierw połącz E32: Konfiguruj → Połączenie z E32.',
  'Open Configure': 'Otwórz Konfiguruj',
  'Changed elsewhere': 'Zmieniono w innym miejscu',
  'These settings were changed elsewhere while you were editing. What you changed is kept and marked; the rest now shows what is saved. Save again to keep your changes.': 'Te ustawienia zostały w międzyczasie zmienione w innym miejscu. Twoje zmiany zostają i są oznaczone; reszta pokazuje teraz to, co zapisano. Zapisz ponownie, aby zachować swoje zmiany.',
  'Changed by you': 'Zmienione przez ciebie',
  'Changed by you; elsewhere it is now {value}.': 'Zmienione przez ciebie; w innym miejscu jest teraz {value}.',
  'On': 'Włączone', 'Off': 'Wyłączone', 'Heat along only': 'Grzeje tylko razem z innymi',
  'The E32 could not be reached. Check the connection and try again.': 'Nie można połączyć się z E32. Sprawdź połączenie i spróbuj ponownie.',
  'The change could not be confirmed. Reload the page to see what is saved.': 'Nie udało się potwierdzić zmiany. Wczytaj stronę ponownie, aby zobaczyć, co zapisano.',
  'This installation is not available. Look under Settings → Devices & services → OpenThermostat.': 'Ta instalacja jest niedostępna. Sprawdź w Ustawienia → Urządzenia i usługi → OpenThermostat.',
  'This page does not match the installed OpenThermostat. Reload the page.': 'Ta strona nie pasuje do zainstalowanego OpenThermostat. Wczytaj stronę ponownie.',
  'The settings were changed elsewhere. Reload the page and try again.': 'Ustawienia zostały zmienione w innym miejscu. Wczytaj stronę ponownie i spróbuj jeszcze raz.',
  'This version of Home Assistant cannot store this change. Update Home Assistant and try again.': 'Ta wersja Home Assistant nie może zapisać tej zmiany. Zaktualizuj Home Assistant i spróbuj ponownie.',
  'This value cannot be saved. Check the fields and try again.': 'Nie można zapisać tej wartości. Sprawdź pola i spróbuj ponownie.',
  'The change was not saved ({code}). Try again.': 'Zmiana nie została zapisana ({code}). Spróbuj ponownie.',
  'These settings could not be read ({code}). Reload the page.': 'Nie udało się odczytać tych ustawień ({code}). Wczytaj stronę ponownie.',
  'OpenThermostat was updated. Reload the page to use the new version.': 'OpenThermostat został zaktualizowany. Wczytaj stronę ponownie, aby użyć nowej wersji.',
  'The settings could not be loaded. Reload the page.': 'Nie udało się wczytać ustawień. Wczytaj stronę ponownie.',
  'At a glance': 'W skrócie', 'Boiler': 'Kocioł', 'Smart warm-up': 'Inteligentne nagrzewanie', 'Weather compensation': 'Kompensacja pogodowa',
  'Holiday until {until}': 'Urlop do {until}', 'Next holiday: {from} – {until}': 'Następny urlop: {from} – {until}',
  'No holiday planned': 'Brak zaplanowanego urlopu', 'No rooms yet': 'Brak jeszcze pomieszczeń',
  'The name of this installation in Home Assistant and whether it shows the OpenThermostat dashboard.': 'Nazwa tej instalacji w Home Assistant i to, czy pokazywany jest panel OpenThermostat.',
  'Installation name': 'Nazwa instalacji',
  'A recognisable name in Home Assistant. Your devices and their history stay as they are.': 'Rozpoznawalna nazwa w Home Assistant. Twoje urządzenia i ich historia pozostają bez zmian.',
  'Show the OpenThermostat dashboard': 'Pokaż panel OpenThermostat',
  'The OpenThermostat dashboard: your rooms at a glance, the week planner and the boiler. Your own dashboards are preserved.': 'Panel OpenThermostat: Twoje pomieszczenia w skrócie, planer tygodniowy i kocioł. Twoje własne panele pozostają bez zmian.',
  'Give a name of 1 to 80 characters.': 'Podaj nazwę o długości od 1 do 80 znaków.',
  'Hide the OpenThermostat dashboard?': 'Ukryć panel OpenThermostat?',
  'This tab goes with it. You can show the dashboard again in Configure → Dashboard and name.': 'Ta karta również zniknie. Panel możesz ponownie pokazać w Konfiguruj → Panel i nazwa.',
  'Hide the dashboard': 'Ukryj panel'}};
// The sentence of each error code the backend sends (settings.py); a section adds its own (spec.errors).
const ERRORS = {
 e32_unreachable: 'The E32 could not be reached. Check the connection and try again.',
 save_uncertain: 'The change could not be confirmed. Reload the page to see what is saved.',
 setup_save_uncertain: 'The change could not be confirmed. Reload the page to see what is saved.',
 unavailable: 'This installation is not available. Look under Settings → Devices & services → OpenThermostat.',
 unknown_section: 'This page does not match the installed OpenThermostat. Reload the page.',
 unknown_action: 'This page does not match the installed OpenThermostat. Reload the page.',
 unknown_command: 'This page does not match the installed OpenThermostat. Reload the page.',
 not_admin: 'Only an administrator of Home Assistant can change this.',
 unauthorized: 'Only an administrator of Home Assistant can change this.',
 setup_changed: 'The settings were changed elsewhere. Reload the page and try again.',
 setup_platform_unsupported: 'This version of Home Assistant cannot store this change. Update Home Assistant and try again.',
 setup_invalid: 'This value cannot be saved. Check the fields and try again.'};
const STATES = {active: ['On', 'heat', 'fire'], follow: ['Heat along only', 'along', 'thermometer'], inactive: ['Off', 'rest', 'close']};
// What the boiler does (the boiler activity sensor), in the Boiler now card's words: the sensor's own state words through
// Home Assistant ("Resting" for idle, as the card's band); this table [en, nl, pl] only when Home Assistant has none. A state
// without a word here (unknown, unavailable, a newer one) shows nothing: never a raw state.
const ACTIVITY = {idle: ['Resting', 'In rust', 'Spoczynek'], heating: ['Heating', 'Verwarmen', 'Ogrzewanie'], tapping: ['Tapping', 'Tappen', 'Pobór wody'],
 keep_warm: ['Keeping warm', 'Warmhouden', 'Podtrzymanie ciepła'], charging: ['Heating the hot water tank', 'Warmwatervoorraad opwarmen', 'Nagrzewanie zasobnika'],
 hot_water: ['Hot water', 'Warm water', 'Ciepła woda']};
const activityWord = (hass, st, lang) => {
 const own = st && Object.hasOwn(ACTIVITY, st.state) ? ACTIVITY[st.state] : null;
 if (!own) return '';
 let text = '';
 try {
  if (st.state !== 'idle') text = hass.formatEntityState?.(st) || '';
  if (!text || text === st.state) text = hass.localize?.('component.open_thermostat.entity.sensor.boiler_activity.'
   + (st.state === 'idle' ? 'state_attributes.card.state.resting' : 'state.' + st.state)) || '';
 } catch (e) { text = ''; }
 return typeof text === 'string' && text && text !== st.state ? text : own[['en', 'nl', 'pl'].indexOf(lang)] || own[0];
};

/* ---- loading the kit and the sections ---------------------------------------------------------------------------- */
const SELF = (() => { try { return new URL(import.meta.url).pathname; } catch (e) { return ''; } })();
let KIT = null;
const hosts = new Set(), imports = new Map();
const load = url => {
 if (!imports.has(url)) imports.set(url, import(url).then(() => true, err => { console.error('OpenThermostat settings module', url, err); imports.delete(url); return false; }));
 return imports.get(url);
};
// The kit at the panel's own version (the overview names it too); the core's words and Dashboard and name join it.
let kitReady = null;
const adopt = kit => {
 if (KIT) return;
 KIT = kit; kit.addTexts(TEXTS); defineGeneral(kit);
 kit.onSection(name => { for (const host of hosts) host._sectionDefined(name); });
};
const kitFrom = url => {
 if (KIT) return Promise.resolve(KIT);
 kitReady = load(url).then(() => {
  const kit = window.OpenThermostatSettingsKit;
  if (!(kit?.version >= 2)) { kitReady = null; for (const host of hosts) host._start(); return null; }
  adopt(kit);
  for (const host of hosts) host._start();
  return KIT;
 });
 return kitReady;
};
const KIT_GUESS = SELF.startsWith('/open_thermostat/openthermostat-settings-') ? SELF.replace('/openthermostat-settings-', '/openthermostat-settings-kit-') : '';
const fill = (text, values = {}) => String(text).replace(/\{(\w+)\}/g, (all, k) => (k in values ? values[k] : all));
const langOf = hass => {
 const l = String(hass?.locale?.language || hass?.language || 'en').slice(0, 2).toLowerCase();
 return l === 'nl' || l === 'pl' ? l : 'en';
};
const say = (lang, key, values) => (KIT ? KIT.translate(lang, key, values) : fill((lang !== 'en' && TEXTS[lang]?.[key]) || key, values));
const clone = v => (v === undefined ? undefined : JSON.parse(JSON.stringify(v)));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const routeOf = (section, item) => '#' + (section ? section + (item ? '/' + encodeURIComponent(item) : '') : 'overview');
// A websocket error ({code, translation_placeholders}); anything else is a fault of the page itself: logged, said plainly.
const errorOf = err => {
 const code = err && (err.code || err.error?.code);
 if (!code) console.error('OpenThermostat settings', err);
 return {code: code || 'unknown', data: err?.translation_placeholders || err?.error?.translation_placeholders || {}};
};
const numberOf = v => (typeof v === 'number' && Number.isFinite(v) ? v : typeof v === 'string' && v.trim() !== '' && Number.isFinite(Number(v)) ? Number(v) : null);

/* ---- the panel ------------------------------------------------------------------------------------------------ */
class OpenThermostatSettings extends HTMLElement {
 constructor() {
  super();
  this.attachShadow({mode: 'open'});
  this._route = this._parse(location.hash);
  this._drafts = new Map();  // section/item -> {values, original, token}: a draft kept while you look elsewhere
  this._overview = null; this._overviewError = null; this._page = null; this._wide = false; this._generation = 0;
  this._onPop = () => this._go(location.hash, false);
  this._onUnload = e => { if (this._page?.guard?.()) { e.preventDefault(); e.returnValue = ''; } };
 }
 setConfig(config) {
  if (!config || typeof config.entry_id !== 'string' || !config.entry_id)
   throw new Error('This card needs the entry_id of an OpenThermostat installation; the OpenThermostat dashboard adds it for you.');
  this._config = {...config};
  if (this._hass) this._start();
 }
 set hass(hass) {
  const before = this._hass;
  this._hass = hass;
  // Light or dark (CONTRACT-1.4.1 §8): Home Assistant's theme, else the system's; the kit's dark values follow the host.
  const dark = typeof hass?.themes?.darkMode === 'boolean' ? hass.themes.darkMode : !!window.matchMedia?.('(prefers-color-scheme: dark)').matches;
  if (this.dataset.theme !== (dark ? 'dark' : 'light')) this.dataset.theme = dark ? 'dark' : 'light';
  const key = [langOf(hass), hass?.user?.is_admin];
  if (!before || !same(key, this._key)) { this._key = key; if (this._config) this._start(); return; }
  this._live();
 }
 get hass() { return this._hass; }
 getCardSize() { return 12; }
 getGridOptions() { return {columns: 'full'}; }
 connectedCallback() {
  hosts.add(this);
  window.addEventListener('popstate', this._onPop);
  window.addEventListener('beforeunload', this._onUnload);
  if (typeof ResizeObserver === 'function') {
   this._resize = new ResizeObserver(entries => this._measure(entries[0]?.contentRect?.width));
   this._resize.observe(this);
  }
  this._route = this._parse(location.hash);
  if (this._hass && this._config) this._start();
 }
 disconnectedCallback() {
  hosts.delete(this);
  window.removeEventListener('popstate', this._onPop);
  window.removeEventListener('beforeunload', this._onUnload);
  this._resize?.disconnect();
  clearTimeout(this._savedTimer);
 }
 get lang() { return langOf(this._hass); }
 t(key, values) { return say(this.lang, key, values); }
 get admin() { return this._hass?.user?.is_admin !== false && this._overview?.admin !== false; }
 // The route; Dashboard and name and Advanced's list are the page Installation while no section "installation" exists.
 _parse(hash) {
  let route = {section: null, item: null};
  if (KIT) route = KIT.parseRoute(hash);
  else {
   const [head, ...rest] = String(hash || '').replace(/^#/, '').split('/');
   if (head && head !== 'overview' && /^[a-z_]+$/.test(head)) route = {section: head === 'room' ? 'rooms' : head, item: rest.join('/') || null};
  }
  if (!this._ownInstallation() && (route.section === 'general' || (route.section === 'advanced' && !route.item))) return {section: 'installation', item: null};
  return route;
 }
 _ownInstallation() { return !!KIT?.sections.has('installation') && !!this._overview?.sections?.some(s => s.name === 'installation'); }
 _measure(width) {
  const wide = (width ?? this.getBoundingClientRect().width) >= WIDE;
  if (wide === this._wide) return;
  this._wide = wide;
  this.shadowRoot.querySelector('.shell')?.classList.toggle('wide', wide);
  if (KIT) { this._renderList(); this._renderPage(); }  // one column shows the list or the page; the back link differs
 }
 _start() {
  if (!this.isConnected || !this._hass || !this._config) return;
  if (!KIT) {
   this._boot();
   if (!this._overview && !this._booting) { this._booting = true; this._loadOverview(); }
   if (!kitReady && KIT_GUESS) kitFrom(KIT_GUESS);
   return;
  }
  this._route = this._parse(location.hash);
  this._keepDraft();
  this._measure();
  this._renderShell();
  if (!this._overview && !this._booting) this._loadOverview();
  this._booting = false;
  this._openPage();
 }
 // Before the kit arrives: quiet placeholders in the shape of the overview (or an error that says what to do).
 _boot() {
  const box = document.createElement('div');
  box.className = 'boot'; box.setAttribute('role', 'status'); box.setAttribute('aria-label', this.t('Loading…'));
  if (this._overviewError && !kitReady) box.append(Object.assign(document.createElement('p'), {textContent: this.t('The settings could not be loaded. Reload the page.')}));
  else box.innerHTML = '<p class="boot-title"></p>' + '<div class="boot-bone"></div>'.repeat(4);
  const style = document.createElement('style'); style.textContent = BOOT;
  this.shadowRoot.replaceChildren(style, box);
 }
 _sectionDefined(name) {
  const p = this._page;
  if (!p) return;
  if ((p.section === name || (p.section === 'installation' && name === 'installation')) && ['fallback', 'waiting'].includes(p.status)) this._openPage();
  else if (p.composite && name === 'advanced' && !p.extra) this._openPage();
 }
 // Navigation inside the panel: a route (#general) pushed on the history, or (popstate) the one the browser went to.
 async _go(hash, push = true) {
  const route = this._parse(hash);
  // A popstate to where the panel already is (Home Assistant closing a dialog it opened): nothing to do.
  if (!push && route.section === this._route.section && route.item === this._route.item) return;
  // A section that holds unsaved work of its own (the week planner) asks first.
  const question = this._page?.guard?.();
  if (question && KIT) {
   if (!push) { try { history.pushState({openthermostat_settings: true}, '', routeOf(this._route.section, this._route.item)); } catch (e) { /* no history */ } }
   if (!(await KIT.confirm(this.shadowRoot, {...question, lang: this.lang}))) return;
   push = true;
  }
  this._keepDraft();
  if (push) { try { history.pushState({openthermostat_settings: true}, '', routeOf(route.section, route.item)); } catch (e) { /* no history here */ } }
  this._route = route;
  this._renderList();
  this._openPage();
  if (route.section == null) this._loadOverview();
  if (!this._wide && this.getBoundingClientRect().top < 0) this.scrollIntoView({block: 'start'});
 }
 // Navigation elsewhere in Home Assistant (Configure): its path and location-changed.
 _navigate(path) {
  try { history.pushState(null, '', path); } catch (e) { return; }
  window.dispatchEvent(new CustomEvent('location-changed', {detail: {replace: false}}));
 }
 _ws(msg) { return this._hass.callWS({entry_id: this._config.entry_id, ...msg}); }
 async _loadOverview() {
  const generation = ++this._generation;
  try {
   const result = await this._ws({type: 'open_thermostat/settings/overview', language: this.lang});
   if (generation !== this._generation) return;
   this._overview = result; this._overviewError = null;
   this._loadModules(result.modules);
  } catch (err) {
   if (generation !== this._generation) return;
   this._overviewError = errorOf(err).code;
   this._settled = true;
   if (!KIT) { if (!kitReady) this._boot(); return; }
  }
  if (!KIT) return;
  this._renderList();
  if (!this._page) this._renderPage();
  if (['fallback', 'waiting'].includes(this._page?.status) || (this._route.section === 'installation' && this._page?.section !== 'installation' && this._ownInstallation())) this._openPage();
 }
 // The kit first (when the guess from this module's own address did not bring it), then every section in parallel.
 _loadModules(list = []) {
  const kit = list.find(m => m?.name === 'kit');
  if (!KIT && kit?.url && kit.url !== KIT_GUESS) kitFrom(kit.url);
  const all = list.filter(m => m?.name !== 'kit' && typeof m?.url === 'string').map(m => load(m.url));
  Promise.allSettled(all).then(() => { this._settled = true; if (KIT && this._page?.status === 'waiting') this._openPage(); });
 }
 _keepDraft() {
  const p = this._page;
  if (p?.status === 'ready' && this._dirty()) this._drafts.set(p.key, {values: clone(p.values), original: clone(p.original), token: p.token});
 }
 async _openPage() {
  let {section} = this._route;
  const {item} = this._route;
  clearTimeout(this._savedTimer);
  if (!section) { this._page = null; this._renderPage(); this._renderList(); return; }
  const composite = section === 'installation' && !this._ownInstallation();
  if (composite) section = 'general';
  const key = (composite ? 'installation' : section) + '/' + (item ?? ''), spec = KIT.sections.get(section);
  const info = this._overview?.sections?.find(s => s.name === section);
  // A section that moved a screen elsewhere (the House's contacts are on the room screen now) says where it went.
  const moved = spec?.redirect?.(item);
  if (moved) { try { history.replaceState(history.state, '', moved); } catch (e) { /* no history */ } this._route = this._parse(moved); this._openPage(); return; }
  if (!spec && !this._settled && !composite) { this._page = {key, section, item, status: 'waiting'}; this._renderPage(); return; }
  if (!spec || (info && (!info.editable || !info.available))) { this._page = {key, section, item, status: 'fallback'}; this._renderPage(); return; }
  const page = this._page = {key, section, item, spec, composite, status: 'loading', errors: {}, conflicts: new Set()};
  this._renderPage(); this._renderList();
  try {
   const [result, extra] = await Promise.all([this._ws({type: 'open_thermostat/settings/get', section, item}),
    composite && KIT.sections.has('advanced') ? this._ws({type: 'open_thermostat/settings/get', section: 'advanced'}).catch(() => null) : null]);
   if (this._page !== page) return;
   page.extra = extra;
   this._ready(page, result, this._drafts.get(key));
   this._drafts.delete(key);
  } catch (err) {
   if (this._page !== page) return;
   const {code, data} = errorOf(err);
   if (code === 'unknown_section') { page.status = 'fallback'; } else { page.status = 'error'; page.baseError = code; page.basePlaceholders = data.placeholders; }
  }
  this._renderPage(); this._renderList();
 }
 // A model came in: the values to edit, with a kept draft laid over it (its changes marked; a conflict when the
 // value elsewhere moved too).
 _ready(page, {model, token}, draft) {
  const values = page.spec.values ? page.spec.values(clone(model)) : clone(model);
  page.status = 'ready'; page.model = model; page.token = token; page.original = clone(values); page.values = clone(values);
  page.conflicts = new Set(); page.banner = false;
  if (draft) this._merge(page, draft);
 }
 _merge(page, draft) {
  for (const k of Object.keys(draft.values)) {
   // Not changed by you, or what you changed is what is saved now: the fresh value stays.
   if (same(draft.values[k], draft.original[k]) || same(draft.values[k], page.original[k])) continue;
   page.values[k] = clone(draft.values[k]);
   if (draft.token !== page.token && !same(page.original[k], draft.original[k])) page.conflicts.add(k);
  }
  page.banner = draft.token !== page.token && this._dirty(page);
 }
 _dirty(p = this._page) { return !!p && p.status === 'ready' && !same(p.values, p.original); }
 _changed(key) {
  const p = this._page;
  if (!p || p.status !== 'ready') return;
  if (p.errors[key]) { delete p.errors[key]; p.fields?.[key]?.setError(''); }
  this._markField(key);
  this._renderBar();
  if (this._dirty() !== !!this._listDirty) this._renderList();  // the list's "Not saved" follows
 }
 _markField(key) {
  const p = this._page, f = p.fields?.[key];
  if (!f) return;
  const mine = !same(p.values[key], p.original[key]);
  if (mine && p.conflicts.has(key)) f.setMark('conflict', this.t('Changed by you; elsewhere it is now {value}.', {value: p.spec.shown?.(key, p.original[key], (k, v) => this.t(k, v)) ?? this._shown(p.original[key])}));
  else f.setMark(mine ? 'changed' : null, mine ? this.t('Changed by you') : '');
 }
 _shown(v) {
  if (v === true) return this.t('On');
  if (v === false) return this.t('Off');
  if (Array.isArray(v)) return v.join(', ');
  return typeof v === 'number' ? v.toLocaleString(this.lang) : String(v ?? '');
 }
 _undo() {
  const p = this._page;
  if (!p || p.status !== 'ready') return;
  p.values = clone(p.original); p.errors = {}; p.baseError = null; p.conflicts = new Set(); p.banner = false;
  this._renderPage(); this._renderList();
 }
 // Save the page's fields; or (act) an action's own values at once, after its question; your unsaved fields stay.
 async _save(act, question) {
  const p = this._page;
  if (!p || p.status !== 'ready' || p.saving || !(act || this._dirty()) || !this.admin) return false;
  if (!act) question = p.spec.confirm?.(clone(p.values), p.model, this._ctx(p));
  if (question && !(await KIT.confirm(this.shadowRoot, {...question, lang: this.lang}))) return false;
  if (this._page !== p) return false;
  const draft = act && this._dirty() ? {values: clone(p.values), original: clone(p.original), token: p.token} : null;
  p.saving = true; p.baseError = null; this._renderBar();
  try {
   const values = act || (p.spec.toSave ? p.spec.toSave(clone(p.values), p.model) : clone(p.values));
   const result = await this._ws({type: 'open_thermostat/settings/save', section: p.section, item: p.item, token: p.token, values});
   if (this._page !== p) return true;
   this._ready(p, result, draft);
   // spec.saved: a route after the save (a new room's own page).
   const next = p.spec.saved?.(result.model, p.item);
   if (next) { try { history.replaceState(history.state, '', next); } catch (e) {} this._route = this._parse(next); this._renderList(); this._openPage(); this._loadOverview(); return true; }
   p.banner = false; p.saving = false; p.saved = true;
   this._savedTimer = setTimeout(() => { if (this._page === p) { p.saved = false; this._renderBar(); } }, 4000);
   this._renderPage();
   this._loadOverview();
   return true;
  } catch (err) {
   if (this._page !== p) return false;
   p.saving = false;
   const {code, data} = errorOf(err);
   if (code === 'changed_elsewhere' && data.model && data.token) {
    const mine = {values: clone(p.values), original: clone(p.original), token: p.token};
    this._ready(p, {model: data.model, token: data.token}, mine);
    p.banner = true;
   } else if (code === 'changed_elsewhere') {
    this._keepDraft(); this._openPage(); return false;
   } else if (data.field && data.field !== 'base' && p.fields?.[data.field]) {
    p.errors[data.field] = this._error(code, data.placeholders);
   } else {
    p.baseError = code; p.basePlaceholders = data.placeholders;
   }
   this._renderPage();
   const first = Object.keys(p.errors)[0];
   if (first) p.fields?.[first]?.focus();
   return false;
  }
 }
 _error(code, placeholders = {}, spec = this._page?.spec) {
  const sentence = spec?.errors?.[code] || ERRORS[code];
  return sentence ? this.t(sentence, placeholders || {}) : this.t('The change was not saved ({code}). Try again.', {code});
 }
 // An action of the section (CONTRACT-1.4.1 §3): a Promise of its answer, or it throws {code, field, placeholders, text}.
 async _action(p, name, values) {
  try {
   return await this._ws({type: 'open_thermostat/settings/action', section: p.section, ...(p.item != null ? {item: p.item} : {}), action: name,
    ...(values !== undefined ? {values} : {})});
  } catch (err) {
   const {code, data} = errorOf(err);
   throw {code, field: data.field || 'base', placeholders: data.placeholders || {}, text: this._error(code, data.placeholders, p.spec)};
  }
 }
 // What a section's render gets: the model, the values it edits and the kit bound to this page.
 _ctx(p) {
  const self = this, readOnly = !this.admin;
  const settings = this._config.settings_path || '';
  return {
   hass: this._hass, lang: this.lang, admin: !readOnly, readOnly, model: p.model, values: p.values, item: p.item, section: p.section,
   entry_id: this._config.entry_id, overview: this._overview, wide: this._wide,
   kit: KIT, t: (k, v) => this.t(k, v),
   paths: {settings, configure: this._overview?.configure_path || CONFIGURE},
   navigate: hash => this._go(hash), open: path => this._navigate(path),
   // A field bound to values[key]: its edits mark it and show the save bar; disabled for a non-administrator.
   field(kind, key, o = {}) {
    const f = (typeof kind === 'function' ? kind : KIT.fields[kind])({...o, key, hass: self._hass, value: p.values[key], disabled: readOnly || o.disabled,
     onChange: v => { p.values[key] = v; o.onChange?.(v); self._changed(key); }});
    (p.fields ||= {})[key] = f;
    if (p.errors[key]) f.setError(p.errors[key]);
    queueMicrotask(() => self._markField(key));
    return f.el;
   },
   row: o => KIT.row({...o, route: o.route, onClick: o.route ? e => { e.preventDefault(); self._go(o.route); } : o.onClick}),
   // An action that saves (Remove, Back to automatic): its own values at once after the question; resolves true once saved.
   act: (values, question) => self._save(clone(values), question),
   // An operation that is not a save (a scan, a probe, a restore step): settings/action.
   action: (name, values) => self._action(p, name, values),
   // A section's own unsaved work (the week planner): fn() -> a question, or null; asked before the page is left.
   guard: fn => { p.guard = fn; },
   errorText: (code, placeholders) => self._error(code, placeholders, p.spec),
   notice: KIT.notice, inlineError: KIT.inlineError, button: KIT.button
  };
 }
 // Live values (the glance, a section's readings) follow hass without a redraw.
 _live() {
  const root = this.shadowRoot, p = this._page;
  for (const el of root.querySelectorAll('.list-col [data-live], .glance [data-live]')) el._live?.(this._hass);
  if (p?.status === 'ready') p.spec.live?.(root, this._hass);
 }

 /* ---- drawing ---- */
 _renderShell() {
  const {h} = KIT;
  this.shadowRoot.replaceChildren(h('style', {text: KIT.style + STYLE}), h('div', {class: 'shell' + (this._wide ? ' wide' : '')},
   h('nav', {class: 'list-col', 'aria-label': this.t('Settings')}), h('main', {class: 'page-col'})));
  this._renderList(); this._renderPage();
 }
 _focusKey() {
  const a = this.shadowRoot.activeElement;
  return a ? {key: a.dataset?.fk || a.dataset?.section || (a.matches?.('[data-back]') ? 'back' : null), sel: [a.selectionStart, a.selectionEnd]} : null;
 }
 _refocus(state) {
  if (!state?.key) return;
  const el = this.shadowRoot.querySelector(`[data-fk="${CSS.escape(state.key)}"], [data-section="${CSS.escape(state.key)}"]`)
   || (state.key === 'back' ? this.shadowRoot.querySelector('[data-back]') : null);
  if (!el) return;
  el.focus({preventScroll: true});
  try { if (state.sel[0] != null) el.setSelectionRange(...state.sel); } catch (e) { /* not a text field */ }
 }
 _summary(name) {
  const o = this._overview, by = new Map((o?.sections || []).map(s => [s.name, s]));
  if (!o) return {lines: [], available: true};
  if (name === 'installation' && !by.has('installation')) {
   const general = by.get('general'), advanced = by.get('advanced');
   return {lines: [...(general?.summary || []), ...(advanced?.summary || [])], available: true};
  }
  const s = by.get(name);
  if (!s) return null;
  return {lines: s.available ? s.summary : [this._reasonText(s.reason), ...s.summary].filter(Boolean), available: s.available};
 }
 _renderList() {
  const nav = this.shadowRoot.querySelector('.list-col');
  if (!nav || !KIT) return;
  const {h, row, notice} = KIT, focus = this._focusKey(), o = this._overview, p = this._page;
  const current = this._route.section;
  this._listDirty = this._dirty();
  nav.hidden = !this._wide && current != null;
  // A section with a list of its own (the rooms) shows it here beside an open item on a wide screen.
  const own = this._wide && p?.item != null && p.spec?.nav ? p.spec.nav(this._navCtx(p)) : null;
  if (own) {
   nav.replaceChildren(h('a', {class: 'back nav-back', href: routeOf(null), 'data-back': 'overview', on: {click: e => { e.preventDefault(); this._go(routeOf(null)); }}},
    KIT.icon('chevron-left', {size: 20}), h('span', {text: this.t('Settings')})), own);
   this._refocus(focus);
   return;
  }
  const parts = [h('header', {class: 'head'}, h('h1', {class: 'title', text: this.t('Settings')}))];
  if (!this.admin) parts.push(notice(this.t('Only an administrator of Home Assistant can change this.'), 'info'));
  if (this._overviewError) parts.push(notice(this._errorText(this._overviewError), 'error'));
  if (o?.module_url && SELF && SELF.startsWith('/open_thermostat/') && o.module_url !== SELF)
   parts.push(notice(this.t('OpenThermostat was updated. Reload the page to use the new version.'), 'warning'));
  const list = h('div', {class: 'card list entries'});
  for (const [name, title, icon] of ENTRIES) {
   const s = this._summary(name);
   if (!s) continue;
   const drafted = [...this._drafts.keys()].some(k => k.startsWith(name + '/')) || (current === name && this._dirty());
   list.append(row({label: this.t(title), icon, summary: s.lines, route: routeOf(name), current: current === name,
    badge: drafted ? this.t('Not saved') : null, disabled: !s.available, data: {section: name},
    onClick: e => { if (e.button || e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); this._go(routeOf(name)); }}));
  }
  if (!o && !this._overviewError) list.replaceChildren(KIT.skeleton('rows', 7));
  parts.push(list);
  nav.replaceChildren(...parts);
  this._refocus(focus);
 }
 _navCtx(p) {
  return {hass: this._hass, lang: this.lang, kit: KIT, t: (k, v) => this.t(k, v), overview: this._overview, item: p.item, model: p.model,
   readOnly: !this.admin, navigate: hash => this._go(hash)};
 }
 _reasonText(reason) {
  return reason === 'connect_e32' ? this.t('Connect the E32 first: Configure → E32 connection.') : '';
 }
 _errorText(code) { return ERRORS[code] ? this.t(ERRORS[code]) : this.t('The change was not saved ({code}). Try again.', {code}); }
 // The installation at a glance (wide screen, nothing open): the rooms, the boiler, what is on, the next holiday.
 _glance() {
  const {h, roomCard, card, row} = KIT, g = this._overview?.glance, hass = this._hass, lang = this.lang;
  if (!this._overview) return h('div', {class: 'glance'}, KIT.skeleton('cards', 4));
  if (!g) return h('div', {class: 'glance'});
  const go = route => e => { e.preventDefault(); this._go(route); };
  const rooms = (g.rooms || []).map(r => {
   const el = h('div', {class: 'tile', 'data-live': '', 'data-room': r.id}), route = '#room/' + encodeURIComponent(r.id);
   el._live = s => {
    const c = s?.states?.[r.entities?.climate], sensor = s?.states?.[r.entities?.temperature];
    const now = numberOf(c?.attributes?.current_temperature) ?? numberOf(sensor?.state), target = numberOf(c?.attributes?.temperature);
    const [word, tone, icon] = STATES[r.state] || STATES.active;
    el.replaceChildren(roomCard({name: r.name, compact: true, emitter: r.emitter === 'floor' ? 'floor' : 'radiator', route, onClick: go(route),
     temperature: now == null ? null : now.toLocaleString(lang, {minimumFractionDigits: 1, maximumFractionDigits: 1}), unit: c?.attributes?.temperature_unit || '°C',
     target: target != null && r.state !== 'inactive' ? '→ ' + KIT.degrees(target, '°C', lang) : null, state: {text: this.t(word), tone, icon}}));
   };
   el._live(hass);
   return el;
  });
  const boiler = g.boiler || {}, activity = h('span', {'data-live': ''});
  activity._live = s => {
   const text = activityWord(s, s?.states?.[boiler.activity], this.lang);
   activity.textContent = text ? '· ' + text : '';
  };
  activity._live(hass);
  const onOff = v => this.t(v ? 'On' : 'Off');
  const flow = [g.smart_warm_up == null ? '' : `${this.t('Smart warm-up')}: ${onOff(g.smart_warm_up)}`,
   g.weather_compensation == null ? '' : `${this.t('Weather compensation')}: ${onOff(g.weather_compensation)}`].filter(Boolean).join(' · ');
  const holiday = g.holiday ? (g.holiday.running || !g.holiday.from ? this.t('Holiday until {until}', {until: KIT.time.moment(hass, g.holiday.until)})
   : this.t('Next holiday: {from} – {until}', {from: KIT.time.date(hass, g.holiday.from), until: KIT.time.date(hass, g.holiday.until)})) : this.t('No holiday planned');
  const lines = h('div', {class: 'card list'},
   row({label: this.t('Boiler'), icon: 'fire', summary: [boiler.name], route: '#heating', onClick: go('#heating'), data: {glance: 'boiler'}}),
   flow ? row({label: this.t('Heating and boiler'), icon: 'thermometer', route: '#heating', onClick: go('#heating'), data: {glance: 'flow'}, summary: [flow]}) : null,
   row({label: this.t('House'), icon: 'calendar', summary: [holiday], route: '#house/mode', onClick: go('#house/mode'), data: {glance: 'holiday'}}));
  lines.querySelector('[data-glance=boiler] .row-label')?.append(activity);
  const tiles = rooms.length ? h('div', {class: 'tiles'}, ...rooms) : h('p', {class: 'help', text: this.t('No rooms yet')});
  return h('div', {class: 'glance', 'data-glance': ''}, h('header', {class: 'head'}, h('h2', {class: 'title', text: this.t('At a glance')})),
   card({title: this.t('Rooms'), icon: 'thermostat', cls: 'glance-rooms'}, tiles), lines);
 }
 _renderPage() {
  const main = this.shadowRoot.querySelector('.page-col');
  if (!main || !KIT) return;
  const {h, frame, notice, button, inlineError} = KIT, focus = this._focusKey(), p = this._page;
  main.hidden = !this._wide && !p;
  if (!p) {
   main.replaceChildren(this._wide ? this._glance() : '');
   return;
  }
  const spec = p.spec || KIT.sections.get(p.section), info = this._overview?.sections?.find(s => s.name === p.section);
  const per = v => (typeof v === 'function' ? v(p.model || {}, p.item) : v);  // a section's title or subtitle per (model, item)
  const underInstallation = p.composite || ((p.section === 'advanced' || p.section === 'general') && !this._ownInstallation());
  const title = p.composite ? this.t('Installation') : this.t(per(spec?.title) || TITLES[p.section] || p.section);
  const up = p.item != null && spec?.parent?.(p.item);
  const parent = up ? {route: up.route, label: this.t(up.label)}
   : p.item != null ? (underInstallation ? {route: '#installation', label: this.t('Installation')} : {route: routeOf(p.section), label: this.t(TITLES[p.section] || p.section)})
    : this._wide ? null : {route: routeOf(null), label: this.t('Settings')};
  const back = parent && {route: parent.route, label: this.t('Back to {page}', {page: parent.label}),
   onClick: e => { e.preventDefault(); this._go(parent.route); }};
  const {el, body} = frame({title: p.item != null && p.model?.name ? p.model.name : title,
   subtitle: !p.composite && per(spec?.subtitle) ? this.t(per(spec.subtitle)) : null, back});
  el.dataset.page = p.composite ? 'installation' : p.section;
  if (p.status !== 'ready') el.dataset.status = p.status;
  if (p.status === 'fallback') {
   if (info?.summary?.length) body.append(h('div', {class: 'card lines'}, ...info.summary.map(line => h('p', {text: KIT.together(line)}))));
   const reason = info && !info.available ? this._reasonText(info.reason) : '';
   body.append(notice(reason || this.t('You change this part in Configure for now.'), 'info',
    button(this.t('Open Configure'), () => this._navigate(this._overview?.configure_path || CONFIGURE), 'outlined', {'data-configure': ''})));
  } else if (p.status === 'loading' || p.status === 'waiting') {
   body.append(h('div', {class: 'loading', role: 'status', 'aria-label': this.t('Loading…')}, KIT.skeleton(spec?.skeleton || 'rows', 3)));
  } else if (p.status === 'error') {
   body.append(notice(ERRORS[p.baseError] || spec?.errors?.[p.baseError] ? this._error(p.baseError, p.basePlaceholders) : this.t('These settings could not be read ({code}). Reload the page.', {code: p.baseError}), 'error'));
  } else {
   // On a wide screen the list beside it says it already, at the top of the panel.
   if (!this.admin && !this._wide) body.append(notice(this.t('Only an administrator of Home Assistant can change this.'), 'info'));
   if (p.banner) body.append(h('div', {class: 'notice warning banner', role: 'alert', 'data-banner': 'changed_elsewhere'}, KIT.icon('alert', {cls: 'notice-icon'}),
    h('div', {class: 'notice-body'}, h('p', {class: 'notice-title', text: this.t('Changed elsewhere')}),
     h('p', {text: this.t('These settings were changed elsewhere while you were editing. What you changed is kept and marked; the rest now shows what is saved. Save again to keep your changes.')}))));
   if (p.baseError) body.append(inlineError(this._error(p.baseError, p.basePlaceholders)));
   p.fields = {};
   const content = spec.render(this._ctx(p));
   // A section that draws its own cards (spec.cards) stands on the page; the others get the one form card of 1.4.
   if (p.composite) body.append(KIT.card({title: this.t('Dashboard and name'), cls: 'card form', data: {group: 'general'}}, content));
   else body.append(spec.cards ? content : h('div', {class: 'card form'}, content));
   const adv = p.composite && p.extra?.model && KIT.sections.get('advanced');
   if (adv) {
    const q = {...p, section: 'advanced', item: null, spec: adv, model: p.extra.model, values: clone(p.extra.model), fields: {}, errors: {}};
    body.append(KIT.card({title: this.t('Advanced'), cls: 'card form', data: {group: 'advanced'}}, adv.render(this._ctx(q))));
   }
  }
  const bar = h('div', {class: 'savebar', 'data-state': 'idle'}, h('p', {class: 'status', 'aria-live': 'polite', role: 'status'}),
   h('div', {class: 'actions'}, button(this.t('Undo'), () => this._undo(), 'text', {'data-undo': ''}),
    button(this.t('Save'), () => this._save(), 'filled', {'data-save': ''})));
  main.replaceChildren(el, bar);
  this._renderBar();
  this._refocus(focus);
 }
 _renderBar() {
  const bar = this.shadowRoot.querySelector('.savebar'), p = this._page;
  if (!bar) return;
  const state = !p || p.status !== 'ready' ? 'idle' : p.saving ? 'saving' : this._dirty() && this.admin ? 'dirty' : p.saved ? 'saved' : 'idle';
  bar.dataset.state = state;
  bar.querySelector('.status').textContent = {dirty: this.t('You changed something.'), saving: this.t('Saving…'), saved: this.t('Saved.')}[state] || '';
  for (const b of bar.querySelectorAll('button')) b.disabled = state !== 'dirty';
 }
}

/* ---- Dashboard and name (settings.py read_general / save_general), on the page Installation ------------------- */
function defineGeneral(kit) {
 kit.defineSection('general', {
  title: 'Dashboard and name',
  subtitle: 'The name of this installation in Home Assistant and whether it shows the OpenThermostat dashboard.',
  errors: {invalid_name: 'Give a name of 1 to 80 characters.'},
  render: ctx => kit.h('div', {class: 'fields'},
   ctx.field('text', 'name', {label: ctx.t('Installation name'), maxlength: 80, required: true,
    help: ctx.t('A recognisable name in Home Assistant. Your devices and their history stay as they are.')}),
   ctx.field('toggle', 'create_dashboard', {label: ctx.t('Show the OpenThermostat dashboard'),
    help: ctx.t('The OpenThermostat dashboard: your rooms at a glance, the week planner and the boiler. Your own dashboards are preserved.')})),
  // Switching the dashboard off removes this tab too: asked first.
  confirm: (values, model, ctx) => (model.create_dashboard && values.create_dashboard === false
   ? {title: ctx.t('Hide the OpenThermostat dashboard?'), text: ctx.t('This tab goes with it. You can show the dashboard again in Configure → Dashboard and name.'),
      confirm: ctx.t('Hide the dashboard'), danger: true} : null)
 });
}

/* ---- style: the kit's tokens and components come first; the core adds its frame, rows, notices, save bar, dialog,
   the overview and the glance ---- */
const BOOT = `:host{display:block}.boot{max-width:960px;margin:0 auto;padding:24px 16px;display:grid;gap:12px}
.boot-title{height:26px;width:160px;border-radius:8px;background:var(--divider-color,rgba(0,0,0,.12))}
.boot-bone{height:72px;border-radius:12px;background:var(--card-background-color,#fff);border:1px solid var(--divider-color,rgba(0,0,0,.12))}`;
const STYLE = `
.shell{display:block;max-width:960px;margin:0 auto;padding:var(--ot-s4)}
.shell.wide{display:grid;grid-template-columns:minmax(260px,320px) minmax(0,960px);gap:var(--ot-s5);align-items:start;padding:var(--ot-s5);max-width:1340px}
.shell.wide .list-col{position:sticky;top:var(--ot-s4)}
.head{margin:0 0 var(--ot-s4);display:grid;gap:var(--ot-s1)}
.title{font-size:var(--ot-text-xl);font-weight:500;line-height:1.25;letter-spacing:-.01em;overflow-wrap:anywhere}.title:focus{outline:none}
.subtitle{color:var(--ot-muted);overflow-wrap:anywhere}
.back{display:inline-flex;align-items:center;gap:2px;min-height:44px;margin:-8px 0 0 -6px;padding-right:8px;color:var(--ot-link);text-decoration:none;font-weight:500;justify-self:start;border-radius:22px}
.nav-back{margin:0 0 var(--ot-s2) -6px}
.list{display:flex;flex-direction:column}
.row{display:flex;align-items:center;gap:var(--ot-s3);width:100%;min-height:56px;padding:var(--ot-s3) var(--ot-s4);border:0;border-top:1px solid var(--ot-divider);
background:none;color:inherit;font:inherit;text-align:left;text-decoration:none;cursor:pointer;transition:background var(--ot-motion)}
.row:first-child{border-top:0}.row:hover .chevron{color:var(--ot-link)}.row:hover .row-label{color:var(--ot-link)}
.row[aria-current=page]{background:color-mix(in srgb,var(--ot-accent) 12%,transparent);box-shadow:inset 3px 0 0 var(--ot-accent)}
.form .row{margin:0 -16px;width:calc(100% + 32px);border-top:1px solid var(--ot-divider)}
.row-text{flex:1 1 auto;min-width:0;display:flex;flex-direction:column;gap:2px}
.row-label{font-size:var(--ot-text-m);font-weight:500;display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px}
.row-line{color:var(--ot-muted);font-size:var(--ot-text-s);overflow-wrap:anywhere}.row-value{flex:none;color:var(--ot-muted);white-space:nowrap}
.row.muted .row-label{color:var(--ot-muted)}.chevron{flex:none;display:flex;color:var(--ot-muted)}
.entries .row{min-height:72px}.entries .row-line{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.row-label>[data-live]{font-weight:400;color:var(--ot-muted);font-size:var(--ot-text-s)}
.badge{font-size:12px;font-weight:500;padding:1px 8px;border-radius:10px;background:color-mix(in srgb,var(--ot-warn) 22%,var(--ot-surface));
color:color-mix(in srgb,var(--ot-warn) 35%,var(--ot-text))}
.notice{display:flex;gap:var(--ot-s3);align-items:flex-start;margin:0 0 var(--ot-s4);padding:var(--ot-s3) var(--ot-s4);border-radius:var(--ot-radius);
border:1px solid color-mix(in srgb,var(--ot-accent) 35%,var(--ot-divider));background:color-mix(in srgb,var(--ot-accent) 8%,var(--ot-surface));overflow-wrap:anywhere}
.notice-icon{color:color-mix(in srgb,var(--ot-accent) 60%,var(--ot-text));margin-top:1px}.notice-body{flex:1 1 auto;min-width:0;display:grid;gap:4px}
.notice.warning{border-color:color-mix(in srgb,var(--ot-warn) 60%,var(--ot-divider));background:color-mix(in srgb,var(--ot-warn) 12%,var(--ot-surface))}
.notice.warning .notice-icon{color:color-mix(in srgb,var(--ot-warn) 50%,var(--ot-text))}
.notice.error{border-color:color-mix(in srgb,var(--ot-error) 55%,var(--ot-divider));background:color-mix(in srgb,var(--ot-error) 9%,var(--ot-surface))}
.notice.error .notice-icon{color:color-mix(in srgb,var(--ot-error) 75%,var(--ot-text))}
.notice .btn{margin-top:6px;justify-self:start}.notice-title{font-weight:500}
.inline-error,.error{color:color-mix(in srgb,var(--ot-error) 80%,var(--ot-text))}.inline-error{display:flex;gap:8px;align-items:center;margin:0 2px var(--ot-s4);font-weight:500}
.lines{padding:var(--ot-s4);margin-bottom:var(--ot-s4);display:grid;gap:4px}.loading{padding:0}
.savebar{position:sticky;bottom:12px;z-index:3;display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin-top:var(--ot-s4);padding:10px 12px 10px 16px;
background:var(--ot-surface);border:1px solid var(--ot-divider);border-radius:var(--ot-radius);box-shadow:0 4px 24px rgba(0,0,0,.18);animation:ot-up var(--ot-motion)}
.savebar .status{flex:1 1 180px;font-weight:500}.savebar .actions{display:flex;gap:8px;margin-left:auto}
.savebar[data-state=idle]{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);padding:0;border:0;margin:0;animation:none}
.savebar[data-state=saved] .actions{display:none}.savebar[data-state=saved] .status{color:color-mix(in srgb,var(--ot-ok) 60%,var(--ot-text))}
@keyframes ot-up{from{transform:translateY(12px);opacity:0}to{transform:none;opacity:1}}
dialog.confirm{border:0;border-radius:var(--ot-radius);padding:var(--ot-s5);max-width:min(440px,calc(100vw - 32px));background:var(--ot-surface);color:var(--ot-text);box-shadow:0 12px 40px rgba(0,0,0,.3)}
dialog.confirm::backdrop{background:rgba(0,0,0,.45)}dialog.confirm h3{margin:0 0 8px;font-size:var(--ot-text-l);font-weight:500}
dialog.confirm .actions{display:flex;justify-content:flex-end;flex-wrap:wrap;gap:8px;margin-top:var(--ot-s5)}
.ot-card.form{padding:var(--ot-s4) var(--ot-s4) var(--ot-s1)}.ot-card.form>.ot-card-head{margin-bottom:0}
.glance{display:grid;gap:var(--ot-s3)}.glance .head{margin-bottom:var(--ot-s1)}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:var(--ot-s2)}.tile{display:grid}
.glance-rooms .ot-room{background:var(--ot-raised)}
@media(max-width:420px){.shell{padding:var(--ot-s3) var(--ot-s2)}.form .row{margin:0 -12px;width:calc(100% + 24px)}}`;

/* ---- registration ---------------------------------------------------------------------------------------------- */
// As the other cards: define again (a fresh subclass) whenever a scoped-registry polyfill lost the element.
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
// A kit already on the page (loaded before this module) is adopted at once.
if (window.OpenThermostatSettingsKit?.version >= 2) adopt(window.OpenThermostatSettingsKit);
ensureDefined('openthermostat-settings', OpenThermostatSettings);
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c.type === 'openthermostat-settings'))
 window.customCards.push({type: 'openthermostat-settings', name: 'OpenThermostat settings', description: 'The settings of an OpenThermostat installation: rooms, house, heating and more, in one place.'});
