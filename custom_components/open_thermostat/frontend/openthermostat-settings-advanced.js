/* The section Advanced of the settings panel (1.4): on #advanced the list (E32 system log, E32 time zone, Tester program,
   the room setup status when there is one, and "More in Configure"), each opening its own screen (#advanced/logging,
   #advanced/time-zone, #advanced/tester, #advanced/status). Backend settings_advanced.py (Configure's own checks and
   writes); the words are Configure's. */
const TEXTS = {
 nl: {
  'Advanced': 'Geavanceerd',
  'What you rarely need: the E32\'s system log and time zone, the tester program, and what stays in Configure.': 'Wat je zelden nodig hebt: het systeemlog en de tijdzone van de E32, het testerprogramma, en wat in Configureren blijft.',
  'E32 system log': 'Systeemlog van de E32',
  'E32 time zone': 'Tijdzone van de E32',
  'Tester program': 'Testerprogramma',
  'Status of the room setup': 'Status van de ruimte-instellingen',
  'More in Configure': 'Meer in Configureren',
  'Send the E32\'s log to a syslog server on your network, for example to look into a problem.': 'Stuur het log van de E32 naar een syslog-server in je netwerk, bijvoorbeeld om een probleem uit te zoeken.',
  'The E32 keeps its own log as well (Diagnostics and system log on its web page).': 'De E32 houdt ook zelf een log bij (Diagnose en systeemlog op zijn webpagina).',
  'The E32 runs the week programs in its own time zone.': 'De E32 voert de weekprogramma\'s uit in zijn eigen tijdzone.',
  'Help test OpenThermostat with your boiler.': 'Help OpenThermostat testen met je ketel.',
  'The checks of the old Home Assistant rooms, read only.': 'De controles van de oude Home Assistant-ruimtes, alleen lezen.',
  'Connect the E32 first: Configure → E32 connection.': 'Verbind eerst de E32: Configureren → E32-verbinding.',
  'On': 'Aan', 'Off': 'Uit',
  'Radiator valves, persons and temperature limits': 'Radiatorkranen, personen en temperatuurgrenzen',
  'Boiler settings (preview)': 'Ketelinstellingen (voorproefje)',
  'Restore settings to this E32': 'Instellingen terugzetten op deze E32',
  'Tidy entity IDs': 'ID\'s van entiteiten opruimen',
  'Remove old Home Assistant rooms': 'Oude Home Assistant-ruimtes verwijderen',
  'Check the old rooms': 'Oude ruimtes controleren',
  'Water temperature limits of the old rooms': 'Grenzen watertemperatuur van de oude ruimtes',
  'Status of the old rooms on the E32': 'Status van de oude ruimtes op de E32',
  'Dashboard and name': 'Dashboard en naam',
  'Send to a syslog server': 'Naar een syslog-server sturen',
  'Off: the E32 keeps its log only on its own page.': 'Uit: de E32 bewaart zijn log alleen op zijn eigen pagina.',
  'Syslog server': 'Syslog-server',
  'The IPv4 address of the syslog server, for example 192.168.1.10. Needed when sending is on.': 'Het IPv4-adres van de syslog-server, bijvoorbeeld 192.168.1.10. Nodig als sturen aan staat.',
  'UDP port': 'UDP-poort',
  'Usually 514.': 'Meestal 514.',
  'Send up to level': 'Sturen tot en met niveau',
  'Error is enough for normal use; Debug and Trace send a lot.': 'Fout is genoeg voor normaal gebruik; Debug en Trace sturen veel.',
  'Send the E32\'s own messages': 'Eigen berichten van de E32 sturen',
  'Messages of the E32 itself: network, heating, updates.': 'Berichten van de E32 zelf: netwerk, verwarming, updates.',
  'Send the boiler bus messages': 'Berichten van de ketelbus sturen',
  'The messages the E32 hears on the boiler bus; useful to look into a boiler problem.': 'De berichten die de E32 op de ketelbus hoort; handig om een probleem met de ketel uit te zoeken.',
  'Keep on the E32 up to level': 'Op de E32 bewaren tot en met niveau',
  'The most detailed level the E32 keeps for its own log page.': 'Het meest gedetailleerde niveau dat de E32 voor zijn eigen logpagina bewaart.',
  'Still-running message every': 'Bericht ‘draait nog’ elke',
  'Seconds between short “still running” messages; 0 is off.': 'Seconden tussen korte berichten ‘draait nog’; 0 is uit.',
  'Error': 'Fout', 'Warning': 'Waarschuwing', 'Info': 'Informatie', 'Debug': 'Foutzoeken', 'Trace': 'Alles (trace)',
  'Time zone': 'Tijdzone',
  'Now on the E32: {e32}. Home Assistant: {home}.': 'Nu op de E32: {e32}. Home Assistant: {home}.',
  'After saving, the E32 restarts once to use the new time zone; the heating continues after about a minute.': 'Na opslaan start de E32 één keer opnieuw om de nieuwe tijdzone te gebruiken; de verwarming gaat na ongeveer een minuut verder.',
  '{zone} (not in the list)': '{zone} (niet in de lijst)',
  'Use the time zone of Home Assistant': 'De tijdzone van Home Assistant gebruiken',
  'Restart the E32 to use the new time zone?': 'De E32 opnieuw starten voor de nieuwe tijdzone?',
  'The heating continues after about a minute.': 'De verwarming gaat na ongeveer een minuut verder.',
  'Save and restart': 'Opslaan en opnieuw starten',
  'The E32 now uses {zone}. It restarts once; the heating continues after about a minute.': 'De E32 gebruikt nu {zone}. Hij start één keer opnieuw; de verwarming gaat na ongeveer een minuut verder.',
  'While this is on, you can make a 30-minute recording of the messages on your boiler\'s cable and share the result with the OpenThermostat project on GitHub, so your boiler model can be tested and verified.': 'Staat dit aan, dan kun je 30 minuten de berichten op de ketelkabel opnemen en het resultaat delen met het OpenThermostat-project op GitHub, zodat je ketelmodel getest en bevestigd kan worden.',
  'Home Assistant never sends anything itself: it writes the files and shows you a link to the GitHub form. You see everything before you post it. Off: nothing is recorded and nothing is read for it.': 'Home Assistant verstuurt zelf nooit iets: het schrijft de bestanden en toont je een link naar het GitHub-formulier. Je ziet alles voordat je het plaatst. Uit: er wordt niets opgenomen en daarvoor niets gelezen.',
  'Take part in the tester program': 'Meedoen met het testerprogramma',
  'You can switch it off here at any time.': 'Je kunt het hier altijd weer uitzetten.',
  'Start a recording, then let the boiler rest, heat (set the thermostat higher) and make hot water (open a hot tap for a few minutes). After 30 minutes choose Share result. Keep your thermostat connected.': 'Start een opname en laat de ketel dan rusten, verwarmen (zet de thermostaat hoger) en warm water maken (open een warme kraan een paar minuten). Kies na 30 minuten Deel resultaat. Laat je thermostaat aangesloten.',
  'Start a bus recording (30 minutes)': 'Busopname starten (30 minuten)',
  'Stop the bus recording': 'Busopname stoppen',
  'Share result': 'Deel resultaat',
  'No bus recording yet.': 'Nog geen busopname.',
  'Recording: {minutes} of 30 minutes, {frames} messages.': 'Opname loopt: {minutes} van 30 minuten, {frames} berichten.',
  'A bus recording is ready: {minutes} minutes, {frames} messages.': 'Er staat een busopname klaar: {minutes} minuten, {frames} berichten.',
  'This E32 cannot make a bus recording (no room in its memory). You can still share the result.': 'Deze E32 kan geen busopname maken (geen ruimte in zijn geheugen). Je kunt het resultaat wel delen.',
  'This E32 firmware cannot make a bus recording yet. Update the E32 first, or share the result without one.': 'Deze E32-firmware kan nog geen busopname maken. Werk de E32 eerst bij, of deel het resultaat zonder opname.',
  'The E32 could not be reached just now.': 'De E32 was net niet bereikbaar.',
  'The tester program is on.': 'Het testerprogramma staat aan.',
  'Recording: the E32 keeps the newest {minutes} minutes of your boiler\'s messages until you stop it or choose Share result.': 'Opname loopt: de E32 houdt de nieuwste {minutes} minuten berichten van je ketel tot je stopt of Deel resultaat kiest.',
  'The bus recording is stopped. Choose Share result to write the files.': 'De busopname is gestopt. Kies Deel resultaat om de bestanden te schrijven.',
  'Ready: open the notification. It lists what is in the files, has the links to download them and the GitHub form. Nothing was sent.': 'Klaar: open de melding. Daarin staat wat er in de bestanden zit, met de links om ze te downloaden en het GitHub-formulier. Er is niets verstuurd.',
  'The tester program is off. Files you already wrote stay in www/open_thermostat until you delete them.': 'Het testerprogramma staat uit. Bestanden die je al schreef blijven in www/open_thermostat tot je ze verwijdert.',
  'There is nothing to check.': 'Er is niets te controleren.',
  'Enter the IPv4 address of the syslog server, for example 192.168.1.10.': 'Vul het IPv4-adres van de syslog-server in, bijvoorbeeld 192.168.1.10.',
  'Use a whole number within the range shown.': 'Gebruik een heel getal binnen het getoonde bereik.',
  'Choose a time zone from the list.': 'Kies een tijdzone uit de lijst.',
  'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.': 'De E32 heeft geen vrije websessie: sluit E32-pagina\'s die je niet gebruikt, of wacht twee minuten, en probeer het opnieuw.',
  'The E32 is updating or restarting. Try again once its web page opens normally.': 'De E32 wordt bijgewerkt of start opnieuw. Probeer het opnieuw zodra zijn webpagina normaal opent.',
  'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.': 'De E32-instellingen zijn intussen gewijzigd (op zijn webpagina?). Er is niets opgeslagen; probeer het opnieuw.',
  'The E32 refused these settings. Nothing was saved.': 'De E32 heeft deze instellingen geweigerd. Er is niets opgeslagen.',
  'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.': 'De E32 kon niet bevestigen dat de instellingen zijn opgeslagen. Controleer ze op de E32 voordat je het opnieuw probeert.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'De E32 was niet bereikbaar ({error}). Er is niets opgeslagen.',
  'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.': 'Deze E32-firmware heeft deze instelling niet. Werk de E32 eerst bij (Firmware-update).',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'De E32 accepteert het bewaarde wachtwoord niet meer. Home Assistant vraagt om het nieuwe: Instellingen → Apparaten en diensten → OpenThermostat → Opnieuw verifiëren.',
  'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.': 'De E32 gebruikt nog het standaardwachtwoord en accepteert geen wijzigingen tot je een nieuw kiest: Instellingen → Reparaties → “E32 gebruikt nog het standaardwachtwoord”.',
  'This E32 has no room in its memory for a bus recording. Restart the E32 and try again. You can still share the result without one.': 'Deze E32 heeft geen ruimte in zijn geheugen voor een busopname. Herstart de E32 en probeer het opnieuw. Je kunt het resultaat ook zonder opname delen.',
  'Home Assistant could not write the files to its www/open_thermostat folder. Check that the configuration folder has free space, then try again.': 'Home Assistant kon de bestanden niet in zijn map www/open_thermostat schrijven. Controleer of er ruimte vrij is in de configuratiemap en probeer het opnieuw.'
 },
 pl: {
  'Advanced': 'Zaawansowane',
  'What you rarely need: the E32\'s system log and time zone, the tester program, and what stays in Configure.': 'To, czego rzadko potrzebujesz: dziennik systemowy i strefa czasowa E32, program testerów oraz to, co zostaje w Konfiguruj.',
  'E32 system log': 'Dziennik systemowy E32',
  'E32 time zone': 'Strefa czasowa E32',
  'Tester program': 'Program testerów',
  'Status of the room setup': 'Stan ustawień pomieszczeń',
  'More in Configure': 'Więcej w Konfiguruj',
  'Send the E32\'s log to a syslog server on your network, for example to look into a problem.': 'Wysyłaj dziennik E32 do serwera syslog w Twojej sieci, na przykład aby zbadać problem.',
  'The E32 keeps its own log as well (Diagnostics and system log on its web page).': 'E32 prowadzi też własny dziennik (Diagnostyka i dziennik systemowy na jego stronie).',
  'The E32 runs the week programs in its own time zone.': 'E32 wykonuje programy tygodniowe we własnej strefie czasowej.',
  'Help test OpenThermostat with your boiler.': 'Pomóż przetestować OpenThermostat ze swoim kotłem.',
  'The checks of the old Home Assistant rooms, read only.': 'Kontrole starych pomieszczeń Home Assistant, tylko do odczytu.',
  'Connect the E32 first: Configure → E32 connection.': 'Najpierw połącz E32: Konfiguruj → Połączenie z E32.',
  'On': 'Włączone', 'Off': 'Wyłączone',
  'Radiator valves, persons and temperature limits': 'Zawory grzejnikowe, osoby i limity temperatury',
  'Boiler settings (preview)': 'Ustawienia kotła (wersja wstępna)',
  'Restore settings to this E32': 'Przywróć ustawienia na tym E32',
  'Tidy entity IDs': 'Uporządkuj identyfikatory encji',
  'Remove old Home Assistant rooms': 'Usuń stare pomieszczenia Home Assistant',
  'Check the old rooms': 'Sprawdź stare pomieszczenia',
  'Water temperature limits of the old rooms': 'Limity temperatury wody starych pomieszczeń',
  'Status of the old rooms on the E32': 'Stan starych pomieszczeń w E32',
  'Dashboard and name': 'Panel i nazwa',
  'Send to a syslog server': 'Wysyłaj do serwera syslog',
  'Off: the E32 keeps its log only on its own page.': 'Wyłączone: E32 przechowuje dziennik tylko na własnej stronie.',
  'Syslog server': 'Serwer syslog',
  'The IPv4 address of the syslog server, for example 192.168.1.10. Needed when sending is on.': 'Adres IPv4 serwera syslog, na przykład 192.168.1.10. Wymagany, gdy wysyłanie jest włączone.',
  'UDP port': 'Port UDP',
  'Usually 514.': 'Zwykle 514.',
  'Send up to level': 'Wysyłaj do poziomu',
  'Error is enough for normal use; Debug and Trace send a lot.': 'Błąd wystarcza do normalnego użytku; Debug i Trace wysyłają dużo.',
  'Send the E32\'s own messages': 'Wysyłaj własne komunikaty E32',
  'Messages of the E32 itself: network, heating, updates.': 'Komunikaty samego E32: sieć, ogrzewanie, aktualizacje.',
  'Send the boiler bus messages': 'Wysyłaj komunikaty magistrali kotła',
  'The messages the E32 hears on the boiler bus; useful to look into a boiler problem.': 'Komunikaty, które E32 słyszy na magistrali kotła; przydatne do zbadania problemu z kotłem.',
  'Keep on the E32 up to level': 'Przechowuj w E32 do poziomu',
  'The most detailed level the E32 keeps for its own log page.': 'Najbardziej szczegółowy poziom, który E32 przechowuje dla własnej strony dziennika.',
  'Still-running message every': 'Komunikat „nadal działa” co',
  'Seconds between short “still running” messages; 0 is off.': 'Sekundy między krótkimi komunikatami „nadal działa”; 0 to wyłączone.',
  'Error': 'Błąd', 'Warning': 'Ostrzeżenie', 'Info': 'Informacje', 'Debug': 'Debugowanie', 'Trace': 'Śledzenie',
  'Time zone': 'Strefa czasowa',
  'Now on the E32: {e32}. Home Assistant: {home}.': 'Teraz w E32: {e32}. Home Assistant: {home}.',
  'After saving, the E32 restarts once to use the new time zone; the heating continues after about a minute.': 'Po zapisaniu E32 uruchomi się ponownie jeden raz, aby użyć nowej strefy czasowej; ogrzewanie działa dalej po około minucie.',
  '{zone} (not in the list)': '{zone} (nie ma na liście)',
  'Use the time zone of Home Assistant': 'Użyj strefy czasowej Home Assistant',
  'Restart the E32 to use the new time zone?': 'Uruchomić ponownie E32, aby użyć nowej strefy czasowej?',
  'The heating continues after about a minute.': 'Ogrzewanie działa dalej po około minucie.',
  'Save and restart': 'Zapisz i uruchom ponownie',
  'The E32 now uses {zone}. It restarts once; the heating continues after about a minute.': 'E32 używa teraz strefy {zone}. Uruchomi się ponownie jeden raz; ogrzewanie działa dalej po około minucie.',
  'While this is on, you can make a 30-minute recording of the messages on your boiler\'s cable and share the result with the OpenThermostat project on GitHub, so your boiler model can be tested and verified.': 'Gdy to jest włączone, możesz przez 30 minut nagrywać komunikaty na przewodzie kotła i udostępnić wynik projektowi OpenThermostat na GitHubie, aby Twój model kotła mógł zostać przetestowany i zweryfikowany.',
  'Home Assistant never sends anything itself: it writes the files and shows you a link to the GitHub form. You see everything before you post it. Off: nothing is recorded and nothing is read for it.': 'Home Assistant nigdy sam niczego nie wysyła: zapisuje pliki i pokazuje link do formularza GitHub. Widzisz wszystko, zanim to opublikujesz. Wyłączone: nic nie jest nagrywane ani w tym celu odczytywane.',
  'Take part in the tester program': 'Biorę udział w programie testerów',
  'You can switch it off here at any time.': 'W każdej chwili możesz to tutaj wyłączyć.',
  'Start a recording, then let the boiler rest, heat (set the thermostat higher) and make hot water (open a hot tap for a few minutes). After 30 minutes choose Share result. Keep your thermostat connected.': 'Uruchom nagrywanie, a potem pozwól kotłu odpocząć, grzać (ustaw termostat wyżej) i przygotować ciepłą wodę (odkręć ciepły kran na kilka minut). Po 30 minutach wybierz Udostępnij wynik. Nie odłączaj termostatu.',
  'Start a bus recording (30 minutes)': 'Uruchom nagrywanie magistrali (30 minut)',
  'Stop the bus recording': 'Zatrzymaj nagrywanie magistrali',
  'Share result': 'Udostępnij wynik',
  'No bus recording yet.': 'Brak jeszcze nagrania magistrali.',
  'Recording: {minutes} of 30 minutes, {frames} messages.': 'Nagrywanie: {minutes} z 30 minut, {frames} komunikatów.',
  'A bus recording is ready: {minutes} minutes, {frames} messages.': 'Nagranie magistrali jest gotowe: {minutes} minut, {frames} komunikatów.',
  'This E32 cannot make a bus recording (no room in its memory). You can still share the result.': 'Ten E32 nie może nagrywać magistrali (brak miejsca w pamięci). Wynik możesz jednak udostępnić.',
  'This E32 firmware cannot make a bus recording yet. Update the E32 first, or share the result without one.': 'To oprogramowanie E32 jeszcze nie nagrywa magistrali. Najpierw zaktualizuj E32 albo udostępnij wynik bez nagrania.',
  'The E32 could not be reached just now.': 'E32 był przed chwilą nieosiągalny.',
  'The tester program is on.': 'Program testerów jest włączony.',
  'Recording: the E32 keeps the newest {minutes} minutes of your boiler\'s messages until you stop it or choose Share result.': 'Nagrywanie trwa: E32 zachowuje najnowsze {minutes} minut komunikatów Twojego kotła, dopóki go nie zatrzymasz lub nie wybierzesz Udostępnij wynik.',
  'The bus recording is stopped. Choose Share result to write the files.': 'Nagrywanie magistrali jest zatrzymane. Wybierz Udostępnij wynik, aby zapisać pliki.',
  'Ready: open the notification. It lists what is in the files, has the links to download them and the GitHub form. Nothing was sent.': 'Gotowe: otwórz powiadomienie. Jest w nim opis zawartości plików, linki do ich pobrania i formularz GitHub. Nic nie zostało wysłane.',
  'The tester program is off. Files you already wrote stay in www/open_thermostat until you delete them.': 'Program testerów jest wyłączony. Zapisane już pliki zostają w www/open_thermostat, dopóki ich nie usuniesz.',
  'There is nothing to check.': 'Nie ma nic do sprawdzenia.',
  'Enter the IPv4 address of the syslog server, for example 192.168.1.10.': 'Wpisz adres IPv4 serwera syslog, na przykład 192.168.1.10.',
  'Use a whole number within the range shown.': 'Użyj liczby całkowitej z pokazanego zakresu.',
  'Choose a time zone from the list.': 'Wybierz strefę czasową z listy.',
  'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.': 'E32 nie ma wolnej sesji WWW: zamknij nieużywane strony E32 lub odczekaj dwie minuty, a potem spróbuj ponownie.',
  'The E32 is updating or restarting. Try again once its web page opens normally.': 'E32 jest aktualizowany lub uruchamia się ponownie. Spróbuj ponownie, gdy jego strona otworzy się normalnie.',
  'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.': 'Ustawienia E32 zostały w międzyczasie zmienione (na jego stronie?). Nic nie zostało zapisane; spróbuj ponownie.',
  'The E32 refused these settings. Nothing was saved.': 'E32 odrzucił te ustawienia. Nic nie zostało zapisane.',
  'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.': 'E32 nie mógł potwierdzić zapisania ustawień. Sprawdź je w E32, zanim spróbujesz ponownie.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'Nie udało się połączyć z E32 ({error}). Nic nie zostało zapisane.',
  'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.': 'To oprogramowanie E32 nie ma tego ustawienia. Najpierw zaktualizuj E32 (Aktualizacja oprogramowania).',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'E32 nie akceptuje już zapisanego hasła. Home Assistant prosi o nowe: Ustawienia → Urządzenia i usługi → OpenThermostat → Uwierzytelnij ponownie.',
  'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.': 'E32 nadal używa domyślnego hasła i nie przyjmuje zmian, dopóki nie wybierzesz nowego: Ustawienia → Naprawy → „E32 nadal używa domyślnego hasła”.',
  'This E32 has no room in its memory for a bus recording. Restart the E32 and try again. You can still share the result without one.': 'Ten E32 nie ma w pamięci miejsca na nagranie magistrali. Uruchom ponownie E32 i spróbuj jeszcze raz. Wynik możesz też udostępnić bez nagrania.',
  'Home Assistant could not write the files to its www/open_thermostat folder. Check that the configuration folder has free space, then try again.': 'Home Assistant nie mógł zapisać plików w swoim folderze www/open_thermostat. Sprawdź, czy w folderze konfiguracji jest wolne miejsce, i spróbuj ponownie.'
 }};
// The screens' titles (#advanced/<item>).
const TITLES = {logging: 'E32 system log', 'time-zone': 'E32 time zone', tester: 'Tester program', status: 'Status of the room setup'};
// The rows of Configure → Advanced and diagnostics, in Configure's words (product_flow._advanced_options); one row per idea.
const CONFIGURE = {
 e32_rooms: 'Radiator valves, persons and temperature limits', boiler_settings: 'Boiler settings (preview)',
 e32_restore: 'Restore settings to this E32', entity_ids: 'Tidy entity IDs', legacy_rooms: 'Remove old Home Assistant rooms',
 configuration_status: 'Check the old rooms', installation: 'Water temperature limits of the old rooms',
 graph_status: 'Status of the old rooms on the E32', general: 'Dashboard and name', e32_logging: 'E32 system log',
 e32_time_zone: 'E32 time zone', tester: 'Tester program'};
// The log levels (Configure's selector e32_log_level).
const LEVELS = {0: 'Off', 1: 'Error', 2: 'Warning', 3: 'Info', 4: 'Debug', 5: 'Trace'};
// The bus recording in one line (Configure's tester_text).
const RECORDING = {
 idle: 'No bus recording yet.', recording: 'Recording: {minutes} of 30 minutes, {frames} messages.',
 ready: 'A bus recording is ready: {minutes} minutes, {frames} messages.',
 unavailable: 'This E32 cannot make a bus recording (no room in its memory). You can still share the result.',
 not_supported: 'This E32 firmware cannot make a bus recording yet. Update the E32 first, or share the result without one.',
 unreachable: 'The E32 could not be reached just now.'};
// What the last action did (Configure's own result lines).
const DONE = {
 switched_on: 'The tester program is on.',
 tester_recording_started: 'Recording: the E32 keeps the newest {minutes} minutes of your boiler\'s messages until you stop it or choose Share result.',
 tester_recording_stopped: 'The bus recording is stopped. Choose Share result to write the files.',
 tester_shared: 'Ready: open the notification. It lists what is in the files, has the links to download them and the GitHub form. Nothing was sent.',
 tester_switched_off: 'The tester program is off. Files you already wrote stay in www/open_thermostat until you delete them.'};
const ERRORS = {
 connect_e32: 'Connect the E32 first: Configure → E32 connection.',
 e32_log_server_invalid: 'Enter the IPv4 address of the syslog server, for example 192.168.1.10.',
 e32_log_number_invalid: 'Use a whole number within the range shown.',
 e32_time_zone_invalid: 'Choose a time zone from the list.',
 e32_settings_no_free_session: 'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.',
 e32_settings_busy: 'The E32 is updating or restarting. Try again once its web page opens normally.',
 e32_settings_changed: 'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.',
 e32_settings_invalid: 'The E32 refused these settings. Nothing was saved.',
 e32_settings_unconfirmed: 'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.',
 e32_settings_unreachable: 'The E32 could not be reached ({error}). Nothing was saved.',
 e32_settings_update_required: 'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.',
 e32_password_changed: 'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.',
 e32_settings_password_default: 'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.',
 tester_recording_unavailable: 'This E32 has no room in its memory for a bus recording. Restart the E32 and try again. You can still share the result without one.',
 tester_share_not_written: 'Home Assistant could not write the files to its www/open_thermostat folder. Check that the configuration folder has free space, then try again.'};
const CSS = `.ot-intro{margin:4px 0 10px}.ot-intro p+p{margin-top:8px}.ot-line{margin:6px 0;color:var(--ot-muted);overflow-wrap:anywhere}
.ot-actions{display:flex;flex-wrap:wrap;gap:8px;padding:10px 0 6px}.ot-done{margin:6px 0 10px}.ot-zone{padding:0 0 8px}
.form .fields>.row:first-child{border-top:0}.ot-status{padding:12px 0;border-top:1px solid var(--ot-divider)}.ot-status:first-child{border-top:0}
.ot-status h3{margin:0 0 6px;font-size:16px;font-weight:500}.ot-status p{margin:0 0 8px;white-space:pre-line;overflow-wrap:anywhere}`;

const logging_keys = ['syslog_enabled', 'server', 'port', 'syslog_level', 'syslog_esp', 'syslog_ems', 'web_level', 'mark_interval_s'];
// The editable values of a screen (its model names it); the list and the status edit nothing.
function values(m) {
 if (m.screen === 'logging') {
  const v = Object.fromEntries(logging_keys.filter(k => k in m).map(k => [k, m[k]]));
  v.syslog_level = String(m.syslog_level); v.web_level = String(m.web_level);
  return v;
 }
 if (m.screen === 'time-zone') return {time_zone: m.time_zone};
 if (m.screen === 'tester') return {tester_enabled: m.tester_enabled};
 return {};
}

function list(ctx) {
 const {kit, t, model: m} = ctx, needs = m.e32 ? null : t('Connect the E32 first: Configure → E32 connection.');
 const configure = [...new Set((m.configure || []).map(k => CONFIGURE[k]).filter(Boolean))].map(text => t(text));
 return kit.h('div', {class: 'fields'},
  ctx.row({label: t('E32 system log'), route: '#advanced/logging', data: {item: 'logging'},
   summary: [needs || t('Send the E32\'s log to a syslog server on your network, for example to look into a problem.')]}),
  ctx.row({label: t('E32 time zone'), route: '#advanced/time-zone', data: {item: 'time-zone'},
   summary: [needs || m.time_zone || t('The E32 runs the week programs in its own time zone.')]}),
  ctx.row({label: t('Tester program'), route: '#advanced/tester', data: {item: 'tester'},
   summary: [needs || (m.tester ? t('On') : t('Off')), m.tester ? '' : t('Help test OpenThermostat with your boiler.')]}),
  m.status ? ctx.row({label: t('Status of the room setup'), route: '#advanced/status', data: {item: 'status'},
   summary: [t('The checks of the old Home Assistant rooms, read only.')]}) : null,
  ctx.row({label: t('More in Configure'), summary: [configure.join(' · ')], data: {item: 'configure'}, onClick: () => ctx.open(ctx.paths.configure)}));
}

function logging(ctx) {
 const {kit, t, model: m, values: v} = ctx;
 const levels = Object.entries(LEVELS).map(([value, label]) => ({value, label: t(label)}));
 const sending = kit.h('div', {class: 'fields', 'data-part': 'sending'},
  ctx.field('text', 'server', {label: t('Syslog server'), maxlength: 15, placeholder: '192.168.1.10',
   help: t('The IPv4 address of the syslog server, for example 192.168.1.10. Needed when sending is on.')}),
  ctx.field('number', 'port', {label: t('UDP port'), min: 1, max: 65535, step: 1, help: t('Usually 514.')}),
  ctx.field('select', 'syslog_level', {label: t('Send up to level'), options: levels, help: t('Error is enough for normal use; Debug and Trace send a lot.')}),
  'syslog_esp' in m ? ctx.field('toggle', 'syslog_esp', {label: t('Send the E32\'s own messages'), help: t('Messages of the E32 itself: network, heating, updates.')}) : null,
  'syslog_ems' in m ? ctx.field('toggle', 'syslog_ems', {label: t('Send the boiler bus messages'),
   help: t('The messages the E32 hears on the boiler bus; useful to look into a boiler problem.')}) : null);
 const show = () => { sending.hidden = !v.syslog_enabled; };
 show();
 return kit.h('div', {class: 'fields'},
  kit.h('div', {class: 'ot-intro help'}, kit.h('p', {text: `${t('Send the E32\'s log to a syslog server on your network, for example to look into a problem.')} ${t('The E32 keeps its own log as well (Diagnostics and system log on its web page).')}`})),
  ctx.field('toggle', 'syslog_enabled', {label: t('Send to a syslog server'), help: t('Off: the E32 keeps its log only on its own page.'), onChange: show}),
  sending,
  ctx.field('select', 'web_level', {label: t('Keep on the E32 up to level'), options: levels, help: t('The most detailed level the E32 keeps for its own log page.')}),
  ctx.field('number', 'mark_interval_s', {label: t('Still-running message every'), unit: 's', min: 0, max: 86400, step: 1,
   help: t('Seconds between short “still running” messages; 0 is off.')}));
}

function timeZone(ctx) {
 const {kit, t, model: m, values: v} = ctx, live = m.live || {};
 const options = m.zones.map(z => ({value: z, label: z}));
 if (!m.time_zone) options.unshift({value: '', label: t('{zone} (not in the list)', {zone: live.e32 || '–'})});
 const field = ctx.field('select', 'time_zone', {label: t('Time zone'), options,
  help: `${t('Now on the E32: {e32}. Home Assistant: {home}.', {e32: live.e32 || '–', home: live.home || '–'})} ${t('After saving, the E32 restarts once to use the new time zone; the heating continues after about a minute.')}`,
  onChange: () => { use.hidden = !live.home_zone || v.time_zone === live.home_zone; }});
 const use = kit.h('div', {class: 'ot-zone'}, ctx.readOnly ? null : kit.button(t('Use the time zone of Home Assistant'), () => {
  const s = field.querySelector('select'); s.value = live.home_zone; s.dispatchEvent(new Event('change'));
 }, 'outlined', {'data-action': 'home-zone'}));
 use.hidden = ctx.readOnly || !live.home_zone || v.time_zone === live.home_zone;
 return kit.h('div', {class: 'fields'},
  live.restarting ? kit.h('div', {class: 'ot-done', 'data-done': 'time-zone'}, kit.notice(t('The E32 now uses {zone}. It restarts once; the heating continues after about a minute.', {zone: m.time_zone}), 'info')) : null,
  kit.h('div', {class: 'ot-intro help'}, kit.h('p', {text: t('The E32 runs the week programs in its own time zone.')})),
  field, use);
}

function tester(ctx) {
 const {kit, t, model: m} = ctx, live = m.live || {}, rec = live.recording;
 const parts = [kit.h('div', {class: 'ot-intro help'},
  kit.h('p', {text: `${t('Help test OpenThermostat with your boiler.')} ${t('While this is on, you can make a 30-minute recording of the messages on your boiler\'s cable and share the result with the OpenThermostat project on GitHub, so your boiler model can be tested and verified.')}`}),
  kit.h('p', {text: t('Home Assistant never sends anything itself: it writes the files and shows you a link to the GitHub form. You see everything before you post it. Off: nothing is recorded and nothing is read for it.')}))];
 if (live.done && DONE[live.done]) parts.push(kit.h('div', {class: 'ot-done', 'data-done': live.done}, kit.notice(t(DONE[live.done], {minutes: 30}), 'info')));
 parts.push(ctx.field('toggle', 'tester_enabled', {label: t('Take part in the tester program'), help: t('You can switch it off here at any time.')}));
 if (m.tester_enabled) {
  const state = rec?.state in RECORDING ? rec.state : 'unreachable';
  const minutes = Math.floor((rec?.seconds > 0 ? rec.seconds : 0) / 60), frames = (rec?.frames > 0 ? rec.frames : 0).toLocaleString(ctx.lang);
  parts.push(kit.h('p', {class: 'ot-line', 'data-recording': state, text: t(RECORDING[state], {minutes, frames})}),
   kit.h('p', {class: 'help', text: t('Start a recording, then let the boiler rest, heat (set the thermostat higher) and make hot water (open a hot tap for a few minutes). After 30 minutes choose Share result. Keep your thermostat connected.')}));
  if (!ctx.readOnly) {
   const act = action => () => ctx.act({action});
   const actions = kit.h('div', {class: 'ot-actions'});
   if (state === 'recording') actions.append(kit.button(t('Stop the bus recording'), act('stop'), 'outlined', {'data-action': 'stop'}));
   else if (!['unavailable', 'not_supported'].includes(state)) actions.append(kit.button(t('Start a bus recording (30 minutes)'), act('start'), 'outlined', {'data-action': 'start'}));
   actions.append(kit.button(t('Share result'), act('share'), 'filled', {'data-action': 'share'}));
   parts.push(actions);
  }
 }
 return kit.h('div', {class: 'fields'}, ...parts);
}

function status(ctx) {
 const {kit, t, model: m} = ctx;
 if (!m.blocks?.length) return kit.h('p', {class: 'ot-line', text: t('There is nothing to check.')});
 return kit.h('div', {}, ...m.blocks.map(b => kit.h('section', {class: 'ot-status'}, kit.h('h3', {text: b.title}),
  ...String(b.text).split(/\n{2,}/).map(p => kit.h('p', {text: p})))));
}

(window.OpenThermostatSettingsSections ||= []).push(['advanced', {
 title: (m, item) => TITLES[item] || 'Advanced',
 subtitle: (m, item) => (item ? null : 'What you rarely need: the E32\'s system log and time zone, the tester program, and what stays in Configure.'),
 texts: TEXTS,
 errors: ERRORS,
 values,
 toSave: (v, m) => (m.screen === 'time-zone' ? {time_zone: v.time_zone, posix: m.posix} : v),
 confirm: (v, m, ctx) => (m.screen === 'time-zone' && v.time_zone !== m.time_zone ? {title: ctx.t('Restart the E32 to use the new time zone?'),
  text: ctx.t('The heating continues after about a minute.'), confirm: ctx.t('Save and restart')} : null),
 shown: (key, value, t) => (key.endsWith('_level') ? t(LEVELS[value] || String(value)) : null),
 render: ctx => {
  const {kit} = ctx, screen = ctx.model.screen || 'list';
  const body = {logging, 'time-zone': timeZone, tester, status}[screen] || list;
  return kit.h('div', {class: 'ot-advanced', 'data-screen': screen}, kit.h('style', {text: CSS}), body(ctx));
 }
}]);
