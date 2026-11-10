/* The section Heating and boiler of the settings panel (1.4): the list (#heating) and its screens #heating/flow (Smart
   warm-up, weather compensation, comfort style, water in hard frost), #heating/limits (the water temperature limits,
   the lowest automatic or yours), #heating/circuits, #heating/care (Comfort and boiler care) and #heating/model (the
   boiler model). Backend settings_heating.py; each model names its screen. The words are Configure's and the E32
   pages' (test/ha-settings-texts.test.cjs). Built on the panel's kit (HA-INSTELPANEEL-ONTWERP.nl.md, chapter 10). */
const TEXTS = {
 nl: {
  'Smart warm-up and weather compensation': 'Slim opwarmen en weerafhankelijke regeling',
  'Smart warm-up: on': 'Slim opwarmen: aan',
  'Smart warm-up: off': 'Slim opwarmen: uit',
  'Weather compensation: on': 'Weerafhankelijke regeling: aan',
  'Weather compensation: off': 'Weerafhankelijke regeling: uit',
  'At most {high}, lowest automatic (now {now})': 'Hoogstens {high}, laagste automatisch (nu {now})',
  'At most {high}, lowest automatic': 'Hoogstens {high}, laagste automatisch',
  'Water temperature limits': 'Grenzen van de watertemperatuur',
  'Heating circuits': 'Verwarmingscircuits',
  'Comfort and boiler care': 'Comfort en zorg voor de ketel',
  'Automatic': 'Automatisch',
  '1 setting set by you': '1 instelling door jou ingesteld',
  '{n} settings set by you': '{n} instellingen door jou ingesteld',
  'Boiler model': 'Ketelmodel',
  'No boiler selected yet': 'Nog geen ketel gekozen',
  'Boiler settings (preview)': 'Ketelinstellingen (voorproefje)',
  'Open in Configure': 'Openen in Configureren',
  'Smart warm-up': 'Slim opwarmen',
  'The E32 starts heating early, so a room is warm at the time in its week program, with the coolest water that still does it. Off: heating starts at the program time, so a room can stay cool for a while (floor heating an hour or more).': 'De E32 begint eerder met verwarmen, zodat een ruimte warm is op de tijd in het weekprogramma, met het koelste water dat dat nog haalt. Uit: verwarmen begint pas op de programmatijd, dus een ruimte kan een tijdje koel blijven (vloerverwarming een uur of langer).',
  'Comfort style': 'Comfortstijl',
  'What the E32 weighs when it plans the heating: comfort against burner starts and gas.': 'Wat de E32 zwaarder laat wegen als hij de verwarming plant: comfort tegenover branderstarts en gas.',
  'Weather compensation': 'Weerafhankelijke regeling',
  'The colder it is outside, the warmer the water to your heating gets, before the rooms cool down. The room temperature still corrects it. Without an outdoor temperature the normal room control is used.': 'Hoe kouder het buiten is, hoe warmer het water naar je verwarming wordt, nog voordat de ruimtes afkoelen. De ruimtetemperatuur stuurt nog bij. Zonder buitentemperatuur geldt de gewone ruimteregeling.',
  'Water temperature in hard frost (−10 °C)': 'Watertemperatuur bij strenge vorst (−10 °C)',
  'How warm the water to your heating gets when it is −10 °C outside. In milder weather the E32 picks less. Not sure? Leave it on Automatic: the E32 learns this for your house.': 'Hoe warm het water naar je verwarming wordt als het −10 °C is buiten. Bij milder weer kiest de E32 minder. Niet zeker? Laat het op Automatisch staan: de E32 leert dit voor jouw huis.',
  'Lowest water temperature: automatic': 'Laagste watertemperatuur: automatisch',
  'On: the E32 finds the lowest water temperature itself, from what it learns about your boiler and house (never below 30 °C). Off: the value below.': 'Aan: de E32 zoekt de laagste watertemperatuur zelf uit, met wat hij leert over je ketel en huis (nooit onder 30 °C). Uit: de waarde hieronder.',
  'Lowest water temperature': 'Laagste watertemperatuur',
  'Used only with automatic off: the lowest water temperature the E32 asks for while it heats ({minimum_range}).': 'Alleen gebruikt als automatisch uit staat: de laagste watertemperatuur die de E32 vraagt zolang hij verwarmt ({minimum_range}).',
  'Highest water temperature': 'Hoogste watertemperatuur',
  'The highest water temperature the E32 ever asks for ({maximum_range}, above the lowest). Floor heating fed without a mixing valve: usually at most 45–50 °C. Radiators: often 60–75 °C on cold days.': 'De hoogste watertemperatuur die de E32 ooit vraagt ({maximum_range}, boven de laagste). Vloerverwarming zonder mengklep: meestal hoogstens 45–50 °C. Radiatoren: op koude dagen vaak 60–75 °C.',
  'Boiler maximum: {maximum} (set on the boiler); the E32 never asks for more. A lower limit here is useful for floor heating.': 'Maximum van de ketel: {maximum} (ingesteld op de ketel); de E32 vraagt nooit meer. Een lagere grens hier is nuttig bij vloerverwarming.',
  'Pump control by the E32': 'Pomp door de E32',
  'On: the E32 switches the pump on and off itself, but only while it controls the boiler. Off: it only shows what it would do.': 'Aan: de E32 zet de pomp zelf aan en uit, maar alleen zolang hij de ketel regelt. Uit: hij laat alleen zien wat hij zou doen.',
  'Highest water temperature to the floor': 'Hoogste watertemperatuur naar de vloer',
  'When the water to the floor stays 5 °C above this for 2 minutes, the E32 switches the pump off: the mixing valve lets too hot water through. 50 °C is usual for a floor.': 'Blijft het water naar de vloer 2 minuten lang 5 °C boven deze waarde, dan zet de E32 de pomp uit: de mengklep laat te heet water door. 50 °C is gebruikelijk voor een vloer.',
  'Run on at most (minutes)': 'Hoogstens nalopen (minuten)',
  'After the heat the pump keeps running while the water to the floor is still at least 2 °C warmer than the water back, so the floor takes up the remaining heat. It stops sooner once that difference is gone or a room is warm enough; this is the longest it runs on. 30 minutes is usual. Needs both water probes.': 'Na de warmte loopt de pomp door zolang het water naar de vloer nog minstens 2 °C warmer is dan het water terug, zodat de vloer de restwarmte opneemt. Hij stopt eerder zodra dat verschil weg is of een ruimte warm genoeg is; dit is het langst dat hij naloopt. 30 minuten is gebruikelijk. Daarvoor zijn beide watersondes nodig.',
  'Now: {value}': 'Nu: {value}',
  'Your value': 'Jouw waarde',
  'Value': 'Waarde',
  'Possible: {range}. Standard value: {standard}.': 'Mogelijk: {range}. Standaardwaarde: {standard}.',
  'Back to automatic for all': 'Alles terug naar automatisch',
  'Back to automatic for all?': 'Alles terug naar automatisch?',
  'Every setting you set yourself goes back to automatic: the E32 sets it itself again. The fixed settings keep their values.': 'Elke instelling die je zelf hebt ingesteld gaat terug naar automatisch: de E32 stelt haar weer zelf in. De vaste instellingen houden hun waarde.',
  'Back to automatic': 'Terug naar automatisch',
  'Back to start values': 'Terug naar de startwaarden',
  'Back to start values?': 'Terug naar de startwaarden?',
  'All these settings go back to their start values and the E32 starts learning them again. What it learned about your rooms stays.': 'Al deze instellingen gaan terug naar hun startwaarden en de E32 begint ze opnieuw te leren. Wat hij over je ruimtes heeft geleerd blijft.',
  'Set by the E32 itself': 'Door de E32 zelf ingesteld',
  'Automatic: the E32 sets it itself and keeps adjusting it, at most one small step a day. Switch Automatic off to use your own value.': 'Automatisch: de E32 stelt het zelf in en past het aan, hoogstens één kleine stap per dag. Zet Automatisch uit om je eigen waarde te gebruiken.',
  'Fixed settings': 'Vaste instellingen',
  'Choosing a model only names your boiler; whether the E32 may control it is shown under Boiler recognition.': 'Een model kiezen geeft je ketel alleen een naam; of de E32 hem mag regelen, staat bij Ketelherkenning.',
  'product {product}': 'productnummer {product}',
  'version {version}': 'versie {version}',
  'Unknown model': 'Onbekend model',
  'Recognised on the bus: {boiler}. {sentence}': 'Herkend op de bus: {boiler}. {sentence}',
  'Keep this highest water temperature?': 'Deze hoogste watertemperatuur houden?',
  'Save this maximum': 'Dit maximum opslaan',
  'The lowest and highest temperature of the water the boiler sends to the radiators and floor, for all rooms together.': 'De laagste en hoogste temperatuur van het water dat de ketel naar de radiatoren en vloer stuurt, voor alle ruimtes samen.',
  'While Pump control by the E32 is off, the E32 only shows what it would do with the pump and leaves the pump as it is. Switch it on once that looks right.': 'Zolang Pomp door de E32 uit staat, laat de E32 alleen zien wat hij met de pomp zou doen en laat hij de pomp zoals hij is. Zet het aan zodra dat klopt.',
  'The E32 sets these itself and keeps adjusting them as it learns your house. Change one only if you want it differently. The same settings as on the E32\'s Home page.': 'De E32 stelt deze zelf in en past ze aan terwijl hij je huis leert kennen. Wijzig er alleen een als je het anders wilt. Dezelfde instellingen als op de pagina Huis van de E32.',
  'Choose your boiler, as on the E32\'s Boiler page. It names the boiler in Home Assistant and on the E32 and chooses the explanation of its display codes; it does not change how the boiler is controlled.': 'Kies je ketel, net als op de pagina Ketel van de E32. Het geeft de ketel zijn naam in Home Assistant en op de E32 en kiest de uitleg van zijn displaycodes; het verandert niet hoe de ketel wordt geregeld.',
  'Connect the E32 first: Configure → E32 connection.': 'Verbind eerst de E32: Configureren → E32-verbinding.',
  'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.': 'Deze E32-firmware heeft deze instelling niet. Werk de E32 eerst bij (Firmware-update).',
  'The E32 did not save the change. Check the connection and try again.': 'De E32 heeft de wijziging niet opgeslagen. Controleer de verbinding en probeer het opnieuw.',
  'Enter whole degrees: minimum {minimum_range}, maximum {maximum_range}.': 'Vul hele graden in: minimum {minimum_range}, maximum {maximum_range}.',
  'The lowest water temperature must be below the highest.': 'De laagste watertemperatuur moet lager zijn dan de hoogste.',
  'A room has floor heating. Above {floor_maximum} floor heating without a mixing valve can get too hot.': 'Een ruimte heeft vloerverwarming. Boven {floor_maximum} kan vloerverwarming zonder mengklep te heet worden.',
  'This maximum is above your boiler\'s own maximum; the boiler does not go higher anyway.': 'Dit maximum ligt boven het eigen maximum van je ketel; de ketel gaat toch niet hoger.',
  'The E32 did not accept these water temperature limits. Older E32 software accepts at most 60 °C; update the E32 to use a higher maximum.': 'De E32 accepteert deze grenzen van de watertemperatuur niet. Oudere E32-software accepteert hoogstens 60 °C; werk de E32 bij om een hoger maximum te gebruiken.',
  'The room plan was changed on the E32 twice while saving. Nothing was saved; try again.': 'Het ruimteplan is tijdens het opslaan twee keer op de E32 gewijzigd. Er is niets opgeslagen; probeer het opnieuw.',
  'The room plan is too large for the E32 (4 KB). Use shorter names, fewer sources or fewer switch points. Nothing was saved.': 'Het ruimteplan is te groot voor de E32 (4 KB). Gebruik kortere namen, minder bronnen of minder schakelpunten. Er is niets opgeslagen.',
  'The E32 refused the room plan ({error}). Nothing was saved.': 'De E32 weigerde het ruimteplan ({error}). Er is niets opgeslagen.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'De E32 is niet bereikbaar ({error}). Er is niets opgeslagen.',
  'The E32 could not confirm that the room plan was saved. Check the room before trying again.': 'De E32 kon niet bevestigen dat het ruimteplan is opgeslagen. Controleer de ruimte voordat je het opnieuw probeert.',
  'The E32 returned a room plan this version cannot read. Update the E32 firmware and the integration together.': 'De E32 gaf een ruimteplan dat deze versie niet kan lezen. Werk de E32-firmware en de integratie samen bij.',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'De E32 accepteert het bewaarde wachtwoord niet meer. Home Assistant vraagt om het nieuwe: Instellingen → Apparaten en diensten → OpenThermostat → Opnieuw verifiëren.',
  'The E32 did not store the change ({error}). Try again in a minute.': 'De E32 heeft de wijziging niet opgeslagen ({error}). Probeer het over een minuut opnieuw.',
  'Enter a whole number within the limits.': 'Vul een heel getal binnen de grenzen in.',
  'This value is not possible. Use a value within {range}.': 'Deze waarde kan niet. Gebruik een waarde binnen {range}.',
  'The E32 refused the change ({error}). Nothing was saved.': 'De E32 weigerde de wijziging ({error}). Er is niets opgeslagen.',
  'The E32 could not confirm that the change was saved. Check the setting before trying again.': 'De E32 kon niet bevestigen dat de wijziging is opgeslagen. Controleer de instelling voordat je het opnieuw probeert.',
  'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.': 'De E32 heeft geen vrije websessie: sluit E32-pagina\'s die je niet gebruikt, of wacht twee minuten, en probeer het opnieuw.',
  'This E32 firmware shows these settings but cannot change them from Home Assistant. Update the E32 (Firmware update) first.': 'Deze E32-firmware toont deze instellingen, maar kan ze niet vanuit Home Assistant wijzigen. Werk de E32 eerst bij (Firmware-update).',
  'Choose a model from the list.': 'Kies een model uit de lijst.',
  'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.': 'De E32 kon niet bevestigen dat de instellingen zijn opgeslagen. Controleer ze op de E32 voordat je het opnieuw probeert.',
  'The E32 is updating or restarting. Try again once its web page opens normally.': 'De E32 wordt bijgewerkt of start opnieuw. Probeer het opnieuw zodra zijn webpagina normaal opent.',
  'The E32 refused these settings. Nothing was saved.': 'De E32 weigerde deze instellingen. Er is niets opgeslagen.',
  'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.': 'De E32-instellingen zijn intussen gewijzigd (op zijn webpagina?). Er is niets opgeslagen; probeer het opnieuw.',
  'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.': 'De E32 gebruikt nog het standaardwachtwoord en accepteert geen wijzigingen tot je een nieuw kiest: Instellingen → Reparaties → “E32 gebruikt nog het standaardwachtwoord”.',
  'Comfort first': 'Comfort eerst',
  'Warm on time above all; it may use a little more gas.': 'Vooral op tijd warm; dat mag iets meer gas kosten.',
  'Balanced': 'In balans',
  'Warm on time with as few burner starts and as little gas as fit.': 'Op tijd warm met zo weinig branderstarts en gas als past.',
  'Save most': 'Zuinigst',
  'As little gas and as few burner starts as possible; a room may be a little cooler for a moment.': 'Zo weinig gas en branderstarts als kan; een ruimte kan even iets koeler zijn.',
  'Burner rest between starts': 'Rusttijd brander tussen starts',
  'The burner stays off at least this long before it starts again, so the boiler switches on and off less often.': 'De brander blijft minstens zo lang uit voordat hij weer start, zodat de ketel minder vaak aan en uit gaat.',
  'Shortest burner run': 'Kortste brandtijd',
  'Once the burner starts it runs at least this long, so every start is worth it.': 'Als de brander start, brandt hij minstens zo lang, zodat elke start de moeite waard is.',
  'Start heating when the room is this much below its target': 'Begin met verwarmen als de ruimte zoveel onder de gewenste temperatuur is',
  'A little more means fewer burner starts; a little less keeps the room closer to its target.': 'Iets meer betekent minder starts van de brander; iets minder houdt de ruimte dichter bij de gewenste temperatuur.',
  'Stop heating when the room is this much above its target': 'Stop met verwarmen als de ruimte zoveel boven de gewenste temperatuur is',
  'Less means heating stops earlier, so the room gets less too warm.': 'Minder betekent dat het verwarmen eerder stopt, zodat de ruimte minder te warm wordt.',
  'How strongly the water temperature reacts to a cold room': 'Hoe sterk de watertemperatuur reageert op een koude ruimte',
  'Stronger warms up faster; gentler gets less too warm and uses less gas.': 'Sterker warmt sneller op; rustiger wordt minder te warm en verbruikt minder gas.',
  'Warm-up time for floor heating': 'Opwarmtijd voor vloerverwarming',
  'How early heating starts for the next program step, until a floor-heated room has been learned.': 'Hoe vroeg het verwarmen start voor de volgende stap van het programma, totdat een ruimte met vloerverwarming geleerd is.',
  'Warm-up time for radiators': 'Opwarmtijd voor radiatoren',
  'How early heating starts for the next program step, until a room with radiators has been learned.': 'Hoe vroeg het verwarmen start voor de volgende stap van het programma, totdat een ruimte met radiatoren geleerd is.',
  'Room correction on weather compensation': 'Ruimtecorrectie op de weerafhankelijke regeling',
  'How much a room that is too cold adds to the water temperature of weather compensation.': 'Hoeveel een te koude ruimte optelt bij de watertemperatuur van de weerafhankelijke regeling.',
  'Accepted warm-up time with the learned water temperature': 'Toegestane opwarmtijd met de geleerde watertemperatuur',
  'More allows a slower warm-up at a lower, more economical water temperature.': 'Meer staat langzamer opwarmen toe met een lagere, zuinigere watertemperatuur.',
  'Smallest night saving worth advising': 'Kleinste nachtbesparing die een advies waard is',
  'Below this saving the advice keeps your program\'s own night setback.': 'Is de besparing kleiner, dan houdt het advies de nachtverlaging van je eigen programma aan.',
  'Floor circuit': 'Vloercircuit',
  'Radiator circuit': 'Radiatorcircuit',
  'Lowest water temperature now: {value} (standard).': 'Laagste watertemperatuur nu: {value} (standaard).',
  'Lowest water temperature now: {value} (set by you).': 'Laagste watertemperatuur nu: {value} (door jou ingesteld).',
  'Lowest water temperature now: {value} (learned).': 'Laagste watertemperatuur nu: {value} (geleerd).',
  'Not recognised yet: the E32 is waiting for the boiler to identify itself.': 'Nog niet herkend: de E32 wacht tot de ketel zich meldt.',
  'Reading only: this boiler model has not been tested with OpenThermostat yet. The E32 shows its values and what it would ask, but does not control it.': 'Alleen lezen: dit ketelmodel is nog niet getest met OpenThermostat. De E32 toont de waarden en wat hij zou vragen, maar stuurt de ketel niet aan.',
  'Tested by you: the E32 can control this boiler. Share the result so others can too.': 'Door jou getest: de E32 kan deze ketel aansturen. Deel het resultaat, dan kunnen anderen het ook.',
  'Verified: the E32 can control this boiler.': 'Geverifieerd: de E32 kan deze ketel aansturen.',
  'A different boiler is connected. Control is off until this boiler is confirmed.': 'Er hangt een andere ketel aan. Aansturen staat uit tot deze ketel bevestigd is.',
  'Not in the list yet: the E32 controls it the Classic way, as it did before; share a recording so it can be listed.': 'Nog niet in de lijst: de E32 stuurt hem aan op de Classic-manier, zoals voorheen; deel een opname zodat hij in de lijst kan.',
  'Not tested with OpenThermostat yet: the E32 controls it the Classic way, as it did before; share a recording so it can be tested.': 'Nog niet getest met OpenThermostat: de E32 stuurt hem aan op de Classic-manier, zoals voorheen; deel een opname zodat hij getest kan worden.',
  'Tested by you: the result waits for review; the E32 does not control this boiler yet.': 'Door jou getest: de uitslag wacht op beoordeling; de E32 stuurt deze ketel nog niet aan.',
  'A different boiler is connected. The E32 still controls it the Classic way; confirm the boiler so it is recognised again.': 'Er hangt een andere ketel aan. De E32 stuurt hem nog aan op de Classic-manier; bevestig de ketel zodat hij opnieuw herkend wordt.'
 },
 pl: {
  'Smart warm-up and weather compensation': 'Inteligentne nagrzewanie i kompensacja pogodowa',
  'Smart warm-up: on': 'Inteligentne nagrzewanie: włączone',
  'Smart warm-up: off': 'Inteligentne nagrzewanie: wyłączone',
  'Weather compensation: on': 'Kompensacja pogodowa: włączona',
  'Weather compensation: off': 'Kompensacja pogodowa: wyłączona',
  'At most {high}, lowest automatic (now {now})': 'Najwyżej {high}, najniższa automatycznie (teraz {now})',
  'At most {high}, lowest automatic': 'Najwyżej {high}, najniższa automatycznie',
  'Water temperature limits': 'Limity temperatury wody',
  'Heating circuits': 'Obiegi grzewcze',
  'Comfort and boiler care': 'Komfort i dbałość o kocioł',
  'Automatic': 'Automatycznie',
  '1 setting set by you': 'Ustawione przez Ciebie: 1',
  '{n} settings set by you': 'Ustawione przez Ciebie: {n}',
  'Boiler model': 'Model kotła',
  'No boiler selected yet': 'Nie wybrano jeszcze kotła',
  'Boiler settings (preview)': 'Ustawienia kotła (wersja wstępna)',
  'Open in Configure': 'Otwórz w Konfiguruj',
  'Smart warm-up': 'Inteligentne nagrzewanie',
  'The E32 starts heating early, so a room is warm at the time in its week program, with the coolest water that still does it. Off: heating starts at the program time, so a room can stay cool for a while (floor heating an hour or more).': 'E32 zaczyna grzać wcześniej, aby pomieszczenie było ciepłe o godzinie z programu tygodniowego, przy najchłodniejszej wodzie, która jeszcze wystarcza. Wyłączone: grzanie zaczyna się o godzinie z programu, więc pomieszczenie może być przez jakiś czas chłodne (ogrzewanie podłogowe godzinę lub dłużej).',
  'Comfort style': 'Styl komfortu',
  'What the E32 weighs when it plans the heating: comfort against burner starts and gas.': 'Co E32 bierze pod uwagę przy planowaniu ogrzewania: komfort wobec uruchomień palnika i zużycia gazu.',
  'Weather compensation': 'Kompensacja pogodowa',
  'The colder it is outside, the warmer the water to your heating gets, before the rooms cool down. The room temperature still corrects it. Without an outdoor temperature the normal room control is used.': 'Im zimniej na zewnątrz, tym cieplejsza woda do ogrzewania, zanim pomieszczenia się wychłodzą. Temperatura pomieszczenia nadal ją koryguje. Bez temperatury zewnętrznej działa zwykła regulacja pomieszczeń.',
  'Water temperature in hard frost (−10 °C)': 'Temperatura wody przy silnym mrozie (−10 °C)',
  'How warm the water to your heating gets when it is −10 °C outside. In milder weather the E32 picks less. Not sure? Leave it on Automatic: the E32 learns this for your house.': 'Jak ciepła jest woda do ogrzewania, gdy na zewnątrz jest −10 °C. Przy łagodniejszej pogodzie E32 wybiera mniej. Nie jesteś pewien? Zostaw Automatycznie: E32 uczy się tego dla Twojego domu.',
  'Lowest water temperature: automatic': 'Najniższa temperatura wody: automatycznie',
  'On: the E32 finds the lowest water temperature itself, from what it learns about your boiler and house (never below 30 °C). Off: the value below.': 'Włączone: E32 sam ustala najniższą temperaturę wody na podstawie tego, czego uczy się o kotle i domu (nigdy poniżej 30 °C). Wyłączone: wartość poniżej.',
  'Lowest water temperature': 'Najniższa temperatura wody',
  'Used only with automatic off: the lowest water temperature the E32 asks for while it heats ({minimum_range}).': 'Używana tylko przy wyłączonym trybie automatycznym: najniższa temperatura wody, o jaką E32 prosi podczas grzania ({minimum_range}).',
  'Highest water temperature': 'Najwyższa temperatura wody',
  'The highest water temperature the E32 ever asks for ({maximum_range}, above the lowest). Floor heating fed without a mixing valve: usually at most 45–50 °C. Radiators: often 60–75 °C on cold days.': 'Najwyższa temperatura wody, o jaką E32 kiedykolwiek prosi ({maximum_range}, powyżej najniższej). Ogrzewanie podłogowe zasilane bez zaworu mieszającego: zwykle najwyżej 45–50 °C. Grzejniki: w zimne dni często 60–75 °C.',
  'Boiler maximum: {maximum} (set on the boiler); the E32 never asks for more. A lower limit here is useful for floor heating.': 'Maksimum kotła: {maximum} (ustawione na kotle); E32 nigdy nie żąda więcej. Niższy limit jest tu przydatny przy ogrzewaniu podłogowym.',
  'Pump control by the E32': 'Sterowanie pompą przez E32',
  'On: the E32 switches the pump on and off itself, but only while it controls the boiler. Off: it only shows what it would do.': 'Włączone: E32 sam włącza i wyłącza pompę, ale tylko wtedy, gdy steruje kotłem. Wyłączone: tylko pokazuje, co by zrobił.',
  'Highest water temperature to the floor': 'Najwyższa temperatura wody do podłogi',
  'When the water to the floor stays 5 °C above this for 2 minutes, the E32 switches the pump off: the mixing valve lets too hot water through. 50 °C is usual for a floor.': 'Gdy woda do podłogi przez 2 minuty jest o 5 °C cieplejsza od tej wartości, E32 wyłącza pompę: zawór mieszający przepuszcza za gorącą wodę. Dla podłogi zwykle 50 °C.',
  'Run on at most (minutes)': 'Wybieg najwyżej (minuty)',
  'After the heat the pump keeps running while the water to the floor is still at least 2 °C warmer than the water back, so the floor takes up the remaining heat. It stops sooner once that difference is gone or a room is warm enough; this is the longest it runs on. 30 minutes is usual. Needs both water probes.': 'Po grzaniu pompa pracuje dalej, dopóki woda do podłogi jest co najmniej o 2 °C cieplejsza od wody powrotnej, aby podłoga przejęła resztę ciepła. Zatrzymuje się wcześniej, gdy ta różnica zniknie lub pomieszczenie jest wystarczająco ciepłe; to najdłuższy czas wybiegu. Zwykle 30 minut. Wymaga obu sond wody.',
  'Now: {value}': 'Teraz: {value}',
  'Your value': 'Twoja wartość',
  'Value': 'Wartość',
  'Possible: {range}. Standard value: {standard}.': 'Możliwe: {range}. Wartość standardowa: {standard}.',
  'Back to automatic for all': 'Wszystko z powrotem na automatyczne',
  'Back to automatic for all?': 'Wszystko z powrotem na automatyczne?',
  'Every setting you set yourself goes back to automatic: the E32 sets it itself again. The fixed settings keep their values.': 'Każde ustawienie, które ustawiłeś sam, wraca do trybu automatycznego: E32 znów ustawia je sam. Stałe ustawienia zachowują swoje wartości.',
  'Back to automatic': 'Z powrotem na automatyczne',
  'Back to start values': 'Powrót do wartości początkowych',
  'Back to start values?': 'Powrót do wartości początkowych?',
  'All these settings go back to their start values and the E32 starts learning them again. What it learned about your rooms stays.': 'Wszystkie te ustawienia wracają do wartości początkowych, a E32 zaczyna uczyć się ich od nowa. To, czego nauczył się o Twoich pomieszczeniach, zostaje.',
  'Set by the E32 itself': 'Ustawiane przez E32',
  'Automatic: the E32 sets it itself and keeps adjusting it, at most one small step a day. Switch Automatic off to use your own value.': 'Automatycznie: E32 ustawia to sam i dostosowuje, najwyżej o jeden mały krok dziennie. Wyłącz Automatycznie, aby użyć własnej wartości.',
  'Fixed settings': 'Stałe ustawienia',
  'Choosing a model only names your boiler; whether the E32 may control it is shown under Boiler recognition.': 'Wybór modelu tylko nazywa kocioł; czy E32 może nim sterować, pokazuje Rozpoznanie kotła.',
  'product {product}': 'produkt {product}',
  'version {version}': 'wersja {version}',
  'Unknown model': 'Nieznany model',
  'Recognised on the bus: {boiler}. {sentence}': 'Rozpoznany na magistrali: {boiler}. {sentence}',
  'Keep this highest water temperature?': 'Zachować tę najwyższą temperaturę wody?',
  'Save this maximum': 'Zapisz to maksimum',
  'The lowest and highest temperature of the water the boiler sends to the radiators and floor, for all rooms together.': 'Najniższa i najwyższa temperatura wody, którą kocioł wysyła do grzejników i podłogi, dla wszystkich pomieszczeń razem.',
  'While Pump control by the E32 is off, the E32 only shows what it would do with the pump and leaves the pump as it is. Switch it on once that looks right.': 'Dopóki Sterowanie pompą przez E32 jest wyłączone, E32 tylko pokazuje, co zrobiłby z pompą, i zostawia pompę bez zmian. Włącz to, gdy wygląda to dobrze.',
  'The E32 sets these itself and keeps adjusting them as it learns your house. Change one only if you want it differently. The same settings as on the E32\'s Home page.': 'E32 ustawia je sam i dostosowuje je, poznając Twój dom. Zmieniaj je tylko wtedy, gdy chcesz inaczej. Te same ustawienia co na stronie Dom w E32.',
  'Choose your boiler, as on the E32\'s Boiler page. It names the boiler in Home Assistant and on the E32 and chooses the explanation of its display codes; it does not change how the boiler is controlled.': 'Wybierz swój kocioł, tak jak na stronie Kocioł w E32. Nadaje on kotłowi nazwę w Home Assistant i w E32 oraz wybiera objaśnienia kodów wyświetlacza; nie zmienia sposobu sterowania kotłem.',
  'Connect the E32 first: Configure → E32 connection.': 'Najpierw połącz E32: Konfiguruj → Połączenie z E32.',
  'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.': 'To oprogramowanie E32 nie ma tego ustawienia. Najpierw zaktualizuj E32 (Aktualizacja oprogramowania).',
  'The E32 did not save the change. Check the connection and try again.': 'E32 nie zapisał zmiany. Sprawdź połączenie i spróbuj ponownie.',
  'Enter whole degrees: minimum {minimum_range}, maximum {maximum_range}.': 'Podaj pełne stopnie: minimum {minimum_range}, maksimum {maximum_range}.',
  'The lowest water temperature must be below the highest.': 'Najniższa temperatura wody musi być niższa od najwyższej.',
  'A room has floor heating. Above {floor_maximum} floor heating without a mixing valve can get too hot.': 'W jednym pomieszczeniu jest ogrzewanie podłogowe. Powyżej {floor_maximum} ogrzewanie podłogowe bez zaworu mieszającego może się zbytnio nagrzać.',
  'This maximum is above your boiler\'s own maximum; the boiler does not go higher anyway.': 'To maksimum jest wyższe niż maksimum samego kotła; kocioł i tak nie pójdzie wyżej.',
  'The E32 did not accept these water temperature limits. Older E32 software accepts at most 60 °C; update the E32 to use a higher maximum.': 'E32 nie zaakceptował tych limitów temperatury wody. Starsze oprogramowanie E32 akceptuje najwyżej 60 °C; zaktualizuj E32, aby użyć wyższego maksimum.',
  'The room plan was changed on the E32 twice while saving. Nothing was saved; try again.': 'Plan pomieszczeń został dwukrotnie zmieniony na E32 podczas zapisywania. Nic nie zapisano; spróbuj ponownie.',
  'The room plan is too large for the E32 (4 KB). Use shorter names, fewer sources or fewer switch points. Nothing was saved.': 'Plan pomieszczeń jest za duży dla E32 (4 KB). Użyj krótszych nazw, mniej źródeł lub mniej punktów przełączenia. Nic nie zapisano.',
  'The E32 refused the room plan ({error}). Nothing was saved.': 'E32 odrzucił plan pomieszczeń ({error}). Nic nie zapisano.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'Nie udało się połączyć z E32 ({error}). Nic nie zapisano.',
  'The E32 could not confirm that the room plan was saved. Check the room before trying again.': 'E32 nie mógł potwierdzić zapisania planu pomieszczeń. Sprawdź pomieszczenie przed ponowną próbą.',
  'The E32 returned a room plan this version cannot read. Update the E32 firmware and the integration together.': 'E32 zwrócił plan pomieszczeń, którego ta wersja nie potrafi odczytać. Zaktualizuj razem oprogramowanie E32 i integrację.',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'E32 nie akceptuje już zapisanego hasła. Home Assistant prosi o nowe: Ustawienia → Urządzenia i usługi → OpenThermostat → Uwierzytelnij ponownie.',
  'The E32 did not store the change ({error}). Try again in a minute.': 'E32 nie zapisał zmiany ({error}). Spróbuj ponownie za minutę.',
  'Enter a whole number within the limits.': 'Podaj liczbę całkowitą w dozwolonym zakresie.',
  'This value is not possible. Use a value within {range}.': 'Ta wartość nie jest możliwa. Użyj wartości z zakresu {range}.',
  'The E32 refused the change ({error}). Nothing was saved.': 'E32 odrzucił zmianę ({error}). Nic nie zostało zapisane.',
  'The E32 could not confirm that the change was saved. Check the setting before trying again.': 'E32 nie mógł potwierdzić zapisania zmiany. Sprawdź ustawienie, zanim spróbujesz ponownie.',
  'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.': 'E32 nie ma wolnej sesji WWW: zamknij nieużywane strony E32 lub odczekaj dwie minuty, a potem spróbuj ponownie.',
  'This E32 firmware shows these settings but cannot change them from Home Assistant. Update the E32 (Firmware update) first.': 'To oprogramowanie E32 pokazuje te ustawienia, ale nie może ich zmienić z Home Assistant. Najpierw zaktualizuj E32 (Aktualizacja oprogramowania).',
  'Choose a model from the list.': 'Wybierz model z listy.',
  'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.': 'E32 nie mógł potwierdzić zapisania ustawień. Sprawdź je w E32, zanim spróbujesz ponownie.',
  'The E32 is updating or restarting. Try again once its web page opens normally.': 'E32 jest aktualizowany lub uruchamia się ponownie. Spróbuj ponownie, gdy jego strona otworzy się normalnie.',
  'The E32 refused these settings. Nothing was saved.': 'E32 odrzucił te ustawienia. Nic nie zostało zapisane.',
  'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.': 'Ustawienia E32 zostały w międzyczasie zmienione (na jego stronie?). Nic nie zostało zapisane; spróbuj ponownie.',
  'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.': 'E32 nadal używa domyślnego hasła i nie przyjmuje zmian, dopóki nie wybierzesz nowego: Ustawienia → Naprawy → „E32 nadal używa domyślnego hasła”.',
  'Comfort first': 'Najpierw komfort',
  'Warm on time above all; it may use a little more gas.': 'Przede wszystkim ciepło na czas; może zużyć trochę więcej gazu.',
  'Balanced': 'Zrównoważony',
  'Warm on time with as few burner starts and as little gas as fit.': 'Ciepło na czas przy tak małej liczbie uruchomień palnika i tak małym zużyciu gazu, jak się da.',
  'Save most': 'Maksymalna oszczędność',
  'As little gas and as few burner starts as possible; a room may be a little cooler for a moment.': 'Jak najmniej gazu i uruchomień palnika; pomieszczenie może chwilami być nieco chłodniejsze.',
  'Burner rest between starts': 'Przerwa palnika między startami',
  'The burner stays off at least this long before it starts again, so the boiler switches on and off less often.': 'Palnik pozostaje wyłączony co najmniej tak długo, zanim znów się uruchomi, więc kocioł rzadziej się włącza i wyłącza.',
  'Shortest burner run': 'Najkrótsza praca palnika',
  'Once the burner starts it runs at least this long, so every start is worth it.': 'Gdy palnik się uruchomi, pracuje co najmniej tak długo, aby każde uruchomienie było warte zachodu.',
  'Start heating when the room is this much below its target': 'Zacznij grzać, gdy w pomieszczeniu jest o tyle chłodniej niż zadana temperatura',
  'A little more means fewer burner starts; a little less keeps the room closer to its target.': 'Trochę więcej oznacza mniej uruchomień palnika; trochę mniej utrzymuje pomieszczenie bliżej zadanej temperatury.',
  'Stop heating when the room is this much above its target': 'Przestań grzać, gdy w pomieszczeniu jest o tyle cieplej niż zadana temperatura',
  'Less means heating stops earlier, so the room gets less too warm.': 'Mniej oznacza, że ogrzewanie kończy się wcześniej, więc pomieszczenie mniej się przegrzewa.',
  'How strongly the water temperature reacts to a cold room': 'Jak mocno temperatura wody reaguje na zimne pomieszczenie',
  'Stronger warms up faster; gentler gets less too warm and uses less gas.': 'Silniej nagrzewa szybciej; łagodniej mniej przegrzewa i zużywa mniej gazu.',
  'Warm-up time for floor heating': 'Czas nagrzewania dla ogrzewania podłogowego',
  'How early heating starts for the next program step, until a floor-heated room has been learned.': 'Jak wcześnie zaczyna się ogrzewanie przed następnym krokiem programu, dopóki pomieszczenie z ogrzewaniem podłogowym nie zostanie poznane.',
  'Warm-up time for radiators': 'Czas nagrzewania dla grzejników',
  'How early heating starts for the next program step, until a room with radiators has been learned.': 'Jak wcześnie zaczyna się ogrzewanie przed następnym krokiem programu, dopóki pomieszczenie z grzejnikami nie zostanie poznane.',
  'Room correction on weather compensation': 'Korekta pomieszczenia przy kompensacji pogodowej',
  'How much a room that is too cold adds to the water temperature of weather compensation.': 'Ile zbyt zimne pomieszczenie dodaje do temperatury wody kompensacji pogodowej.',
  'Accepted warm-up time with the learned water temperature': 'Dopuszczalny czas nagrzewania przy wyuczonej temperaturze wody',
  'More allows a slower warm-up at a lower, more economical water temperature.': 'Więcej pozwala na wolniejsze nagrzewanie przy niższej, bardziej oszczędnej temperaturze wody.',
  'Smallest night saving worth advising': 'Najmniejsza nocna oszczędność warta porady',
  'Below this saving the advice keeps your program\'s own night setback.': 'Poniżej tej oszczędności porada zachowuje nocne obniżenie z Twojego programu.',
  'Floor circuit': 'Obieg podłogowy',
  'Radiator circuit': 'Obieg grzejnikowy',
  'Lowest water temperature now: {value} (standard).': 'Najniższa temperatura wody teraz: {value} (standardowa).',
  'Lowest water temperature now: {value} (set by you).': 'Najniższa temperatura wody teraz: {value} (ustawiona przez ciebie).',
  'Lowest water temperature now: {value} (learned).': 'Najniższa temperatura wody teraz: {value} (wyuczona).',
  'Not recognised yet: the E32 is waiting for the boiler to identify itself.': 'Jeszcze nie rozpoznany: E32 czeka, aż kocioł się przedstawi.',
  'Reading only: this boiler model has not been tested with OpenThermostat yet. The E32 shows its values and what it would ask, but does not control it.': 'Tylko odczyt: ten model kotła nie był jeszcze testowany z OpenThermostat. E32 pokazuje jego wartości i to, o co by poprosił, ale nim nie steruje.',
  'Tested by you: the E32 can control this boiler. Share the result so others can too.': 'Przetestowany przez Ciebie: E32 może sterować tym kotłem. Udostępnij wynik, aby inni też mogli.',
  'Verified: the E32 can control this boiler.': 'Zweryfikowany: E32 może sterować tym kotłem.',
  'A different boiler is connected. Control is off until this boiler is confirmed.': 'Podłączono inny kocioł. Sterowanie jest wyłączone do czasu potwierdzenia tego kotła.',
  'Not in the list yet: the E32 controls it the Classic way, as it did before; share a recording so it can be listed.': 'Jeszcze nie na liście: E32 steruje nim w sposób Classic, jak dotąd; udostępnij nagranie, aby można go było dodać do listy.',
  'Not tested with OpenThermostat yet: the E32 controls it the Classic way, as it did before; share a recording so it can be tested.': 'Jeszcze nie testowany z OpenThermostat: E32 steruje nim w sposób Classic, jak dotąd; udostępnij nagranie, aby można go było przetestować.',
  'Tested by you: the result waits for review; the E32 does not control this boiler yet.': 'Przetestowany przez Ciebie: wynik czeka na ocenę; E32 jeszcze nie steruje tym kotłem.',
  'A different boiler is connected. The E32 still controls it the Classic way; confirm the boiler so it is recognised again.': 'Podłączono inny kocioł. E32 nadal steruje nim w sposób Classic; potwierdź kocioł, aby został ponownie rozpoznany.'
 }};
const TITLES = {flow: 'Smart warm-up and weather compensation', limits: 'Water temperature limits', circuits: 'Heating circuits',
 care: 'Comfort and boiler care', model: 'Boiler model'};
const SUBTITLES = {
 limits: 'The lowest and highest temperature of the water the boiler sends to the radiators and floor, for all rooms together.',
 circuits: 'While Pump control by the E32 is off, the E32 only shows what it would do with the pump and leaves the pump as it is. Switch it on once that looks right.',
 care: 'The E32 sets these itself and keeps adjusting them as it learns your house. Change one only if you want it differently. The same settings as on the E32\'s Home page.',
 model: 'Choose your boiler, as on the E32\'s Boiler page. It names the boiler in Home Assistant and on the E32 and chooses the explanation of its display codes; it does not change how the boiler is controlled.'};
const ERRORS = {
 connect_e32: 'Connect the E32 first: Configure → E32 connection.',
 e32_settings_update_required: 'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.',
 e32_flow_options_failed: 'The E32 did not save the change. Check the connection and try again.',
 e32_flow_limits_invalid: 'Enter whole degrees: minimum {minimum_range}, maximum {maximum_range}.',
 e32_flow_limits_order: 'The lowest water temperature must be below the highest.',
 e32_flow_limits_floor_warning: 'A room has floor heating. Above {floor_maximum} floor heating without a mixing valve can get too hot.',
 e32_flow_limits_above_boiler: 'This maximum is above your boiler\'s own maximum; the boiler does not go higher anyway.',
 e32_rejected_flow_limits: 'The E32 did not accept these water temperature limits. Older E32 software accepts at most 60 °C; update the E32 to use a higher maximum.',
 e32_plan_changed: 'The room plan was changed on the E32 twice while saving. Nothing was saved; try again.',
 e32_plan_too_large: 'The room plan is too large for the E32 (4 KB). Use shorter names, fewer sources or fewer switch points. Nothing was saved.',
 e32_rejected: 'The E32 refused the room plan ({error}). Nothing was saved.',
 e32_unreachable: 'The E32 could not be reached ({error}). Nothing was saved.',
 e32_unconfirmed: 'The E32 could not confirm that the room plan was saved. Check the room before trying again.',
 e32_plan_invalid: 'The E32 returned a room plan this version cannot read. Update the E32 firmware and the integration together.',
 e32_password_changed: 'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.',
 heating_circuit_failed: 'The E32 did not store the change ({error}). Try again in a minute.',
 whole_number_invalid: 'Enter a whole number within the limits.',
 care_value_invalid: 'This value is not possible. Use a value within {range}.',
 care_rejected: 'The E32 refused the change ({error}). Nothing was saved.',
 care_unconfirmed: 'The E32 could not confirm that the change was saved. Check the setting before trying again.',
 care_unreachable: 'The E32 could not be reached ({error}). Nothing was saved.',
 care_no_free_session: 'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.',
 care_update_required: 'This E32 firmware shows these settings but cannot change them from Home Assistant. Update the E32 (Firmware update) first.',
 boiler_model_invalid: 'Choose a model from the list.',
 e32_settings_unreachable: 'The E32 could not be reached ({error}). Nothing was saved.',
 e32_settings_unconfirmed: 'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.',
 e32_settings_no_free_session: 'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.',
 e32_settings_busy: 'The E32 is updating or restarting. Try again once its web page opens normally.',
 e32_settings_invalid: 'The E32 refused these settings. Nothing was saved.',
 e32_settings_changed: 'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.',
 e32_settings_password_default: 'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.'};
// The comfort style (Configure's choice: the select's state names, their explanation after the colon) and the knobs of
// Comfort and boiler care (Configure's names, the E32 Home page's explanation).
const STYLES = {comfort: ['Comfort first', 'Warm on time above all; it may use a little more gas.'],
 balanced: ['Balanced', 'Warm on time with as few burner starts and as little gas as fit.'],
 save: ['Save most', 'As little gas and as few burner starts as possible; a room may be a little cooler for a moment.']};
const KNOBS = {
 min_off_s: ['Burner rest between starts', 'The burner stays off at least this long before it starts again, so the boiler switches on and off less often.'],
 min_on_s: ['Shortest burner run', 'Once the burner starts it runs at least this long, so every start is worth it.'],
 heat_start_c: ['Start heating when the room is this much below its target', 'A little more means fewer burner starts; a little less keeps the room closer to its target.'],
 heat_stop_c: ['Stop heating when the room is this much above its target', 'Less means heating stops earlier, so the room gets less too warm.'],
 flow_per_degree_c: ['How strongly the water temperature reacts to a cold room', 'Stronger warms up faster; gentler gets less too warm and uses less gas.'],
 floor_lead_min_per_c: ['Warm-up time for floor heating', 'How early heating starts for the next program step, until a floor-heated room has been learned.'],
 radiator_lead_min_per_c: ['Warm-up time for radiators', 'How early heating starts for the next program step, until a room with radiators has been learned.'],
 curve_correction_pct: ['Room correction on weather compensation', 'How much a room that is too cold adds to the water temperature of weather compensation.'],
 learned_accept_pct: ['Accepted warm-up time with the learned water temperature', 'More allows a slower warm-up at a lower, more economical water temperature.'],
 night_saving_min_pct: ['Smallest night saving worth advising', 'Below this saving the advice keeps your program\'s own night setback.']};
const CIRCUITS = {floor: 'Floor circuit', radiators: 'Radiator circuit'};
const NOW = {standard: 'Lowest water temperature now: {value} (standard).', own: 'Lowest water temperature now: {value} (set by you).',
 learned: 'Lowest water temperature now: {value} (learned).'};
// What the E32 recognised on the bus (boiler_capabilities.py, the words of Configure → Boiler model).
const RECOGNISED = {
 'state.not_recognised': 'Not recognised yet: the E32 is waiting for the boiler to identify itself.',
 'state.read_only': 'Reading only: this boiler model has not been tested with OpenThermostat yet. The E32 shows its values and what it would ask, but does not control it.',
 'state.probe_passed': 'Tested by you: the E32 can control this boiler. Share the result so others can too.',
 'state.verified': 'Verified: the E32 can control this boiler.',
 'state.other_boiler': 'A different boiler is connected. Control is off until this boiler is confirmed.',
 'state.read_only.classic_unlisted': 'Not in the list yet: the E32 controls it the Classic way, as it did before; share a recording so it can be listed.',
 'state.read_only.classic': 'Not tested with OpenThermostat yet: the E32 controls it the Classic way, as it did before; share a recording so it can be tested.',
 'state.probe_passed.plus': 'Tested by you: the result waits for review; the E32 does not control this boiler yet.',
 'state.other_boiler.classic': 'A different boiler is connected. The E32 still controls it the Classic way; confirm the boiler so it is recognised again.'};
const CSS = `.ot-group{padding:14px 0 2px;border-top:1px solid var(--ot-divider)}.ot-group:first-child{border-top:0}
.ot-group h3{margin:0;font-size:16px;font-weight:500}.ot-group>.help{margin-top:2px}.ot-line{padding:10px 0;color:var(--ot-muted);overflow-wrap:anywhere}
.ot-actions{display:flex;flex-wrap:wrap;gap:8px;padding:14px 0}.form .fields>.row:first-child{border-top:0}.ot-heading{margin:18px 0 0;font-size:13px;font-weight:500;text-transform:none;color:var(--ot-muted)}`;

const fmt = (lang, v) => (typeof v === 'number' ? v.toLocaleString(lang) : String(v ?? ''));
const span = (lang, a, b, unit) => `${fmt(lang, a)}–${fmt(lang, b)} ${unit}`;
const upper = s => s.charAt(0).toUpperCase() + s.slice(1);

// The editable values of a screen (its model names it); the list edits nothing.
function values(m) {
 const pick = keys => Object.fromEntries(keys.filter(k => k in m).map(k => [k, m[k]]));
 if (m.screen === 'flow') return pick(['smart_warm_up', 'comfort_style', 'weather_compensation', 'hard_frost_water_temperature']);
 if (m.screen === 'limits') return pick(['minimum_flow_automatic', 'minimum_flow_temperature', 'maximum_flow_temperature']);
 if (m.screen === 'model') return pick(['model']);
 if (m.screen === 'care' || m.screen === 'circuits') return pick(Object.keys(m).filter(k => k.includes(':')));
 return {};
}

// The highest water temperature worth a question first (e32_flow.limit_warnings): above 50 °C with floor heating, above
// the boiler's own maximum. Values in the user's unit, as the model gives them.
function warnings(v, m) {
 const high = v.maximum_flow_temperature, boiler = m.live?.boiler_maximum, out = [];
 if (typeof high !== 'number') return out;
 if (m.floor && high > m.floor_maximum) out.push([ERRORS.e32_flow_limits_floor_warning, {floor_maximum: `${m.floor_maximum} ${m.unit}`}]);
 if (typeof boiler === 'number' && high > boiler) out.push([ERRORS.e32_flow_limits_above_boiler, {}]);
 return out;
}

function list(ctx) {
 const {kit, t, model: m, lang} = ctx, rows = [];
 if (m.flow_offered) {
  const f = m.flow, style = f && STYLES[f.comfort_style];
  rows.push(ctx.row({label: t('Smart warm-up and weather compensation'), route: '#heating/flow', data: {item: 'flow'},
   summary: f ? [[f.smart_warm_up ? t('Smart warm-up: on') : t('Smart warm-up: off'),
    f.weather_compensation ? t('Weather compensation: on') : t('Weather compensation: off'), style && t(style[0])].filter(Boolean).join(' · ')] : []}));
 }
 const l = m.limits;
 let limits = '';
 if (l && typeof l.maximum === 'number') {
  if (l.automatic === true) {
   const now = m.live?.minimum_now;
   limits = now ? t('At most {high}, lowest automatic (now {now})', {high: `${fmt(lang, l.maximum)} ${m.unit}`, now: `${fmt(lang, now.value)} ${m.unit}`})
    : t('At most {high}, lowest automatic', {high: `${fmt(lang, l.maximum)} ${m.unit}`});
  } else if (typeof l.minimum === 'number') limits = span(lang, l.minimum, l.maximum, m.unit);
 }
 rows.push(ctx.row({label: t('Water temperature limits'), summary: [limits], route: '#heating/limits', data: {item: 'limits'}}));
 if (m.circuits?.length) rows.push(ctx.row({label: t('Heating circuits'), route: '#heating/circuits', data: {item: 'circuits'},
  summary: [m.circuits.map(c => t(CIRCUITS[c.kind] || 'Floor circuit')).join(' · ')]}));
 if (m.care_offered) rows.push(ctx.row({label: t('Comfort and boiler care'), route: '#heating/care', data: {item: 'care'},
  summary: m.care ? [!m.care.yours ? t('Automatic') : m.care.yours === 1 ? t('1 setting set by you') : t('{n} settings set by you', {n: m.care.yours})] : []}));
 rows.push(ctx.row({label: t('Boiler model'), summary: [m.boiler_model || t('No boiler selected yet')], route: '#heating/model', data: {item: 'model'}}));
 if (m.boiler_settings) rows.push(ctx.row({label: t('Boiler settings (preview)'), summary: [t('Open in Configure')], data: {item: 'boiler_settings'},
  onClick: () => ctx.open(ctx.paths.configure)}));
 return kit.h('div', {class: 'fields'}, ...rows);
}

function flow(ctx) {
 const {kit, t, values: v} = ctx, parts = [];
 parts.push(ctx.field('toggle', 'smart_warm_up', {label: t('Smart warm-up'),
  help: t('The E32 starts heating early, so a room is warm at the time in its week program, with the coolest water that still does it. Off: heating starts at the program time, so a room can stay cool for a while (floor heating an hour or more).')}));
 if ('comfort_style' in v) parts.push(ctx.field('radio', 'comfort_style', {label: t('Comfort style'),
  help: t('What the E32 weighs when it plans the heating: comfort against burner starts and gas.'),
  options: Object.entries(STYLES).map(([value, [label, help]]) => ({value, label: t(label), help: t(help)}))}));
 parts.push(ctx.field('toggle', 'weather_compensation', {label: t('Weather compensation'),
  help: t('The colder it is outside, the warmer the water to your heating gets, before the rooms cool down. The room temperature still corrects it. Without an outdoor temperature the normal room control is used.')}));
 const choices = [{value: 'automatic', label: t('Automatic')}];
 for (let c = 25; c <= 80; c++) choices.push({value: String(c), label: `${c} °C`});
 parts.push(ctx.field('select', 'hard_frost_water_temperature', {label: t('Water temperature in hard frost (−10 °C)'), options: choices,
  help: t('How warm the water to your heating gets when it is −10 °C outside. In milder weather the E32 picks less. Not sure? Leave it on Automatic: the E32 learns this for your house.')}));
 return kit.h('div', {class: 'fields'}, ...parts);
}

function limits(ctx) {
 const {kit, t, values: v, model: m, lang} = ctx, parts = [], unit = m.unit, live = m.live || {};
 const range = r => span(lang, r[0], r[1], unit);
 let lowest = null;
 if ('minimum_flow_automatic' in v) parts.push(ctx.field('toggle', 'minimum_flow_automatic', {label: t('Lowest water temperature: automatic'),
  help: t('On: the E32 finds the lowest water temperature itself, from what it learns about your boiler and house (never below 30 °C). Off: the value below.'),
  // The lowest value is the E32's own while automatic: its field waits, disabled, until you switch automatic off.
  onChange: on => { const input = lowest?.querySelector('input'); if (input) input.disabled = on === true || ctx.readOnly; }}));
 lowest = ctx.field('number', 'minimum_flow_temperature', {label: t('Lowest water temperature'), unit, step: 1,
  min: m.minimum_range[0], max: m.minimum_range[1], disabled: v.minimum_flow_automatic === true,
  help: t('Used only with automatic off: the lowest water temperature the E32 asks for while it heats ({minimum_range}).', {minimum_range: range(m.minimum_range)})});
 parts.push(lowest);
 if (live.minimum_now && NOW[live.minimum_now.kind]) parts.push(kit.h('p', {class: 'ot-line', 'data-live': 'minimum_now',
  text: t(NOW[live.minimum_now.kind], {value: `${fmt(lang, live.minimum_now.value)} ${unit}`})}));
 parts.push(ctx.field('number', 'maximum_flow_temperature', {label: t('Highest water temperature'), unit, step: 1,
  min: m.maximum_range[0], max: m.maximum_range[1],
  help: t('The highest water temperature the E32 ever asks for ({maximum_range}, above the lowest). Floor heating fed without a mixing valve: usually at most 45–50 °C. Radiators: often 60–75 °C on cold days.', {maximum_range: range(m.maximum_range)})}));
 if (typeof live.boiler_maximum === 'number') parts.push(kit.h('p', {class: 'ot-line', 'data-live': 'boiler_maximum',
  text: t('Boiler maximum: {maximum} (set on the boiler); the E32 never asks for more. A lower limit here is useful for floor heating.', {maximum: `${fmt(lang, live.boiler_maximum)} ${unit}`})}));
 return kit.h('div', {class: 'fields'}, ...parts);
}

function circuits(ctx) {
 const {kit, t, model: m} = ctx, parts = [];
 for (const c of m.circuits) parts.push(kit.h('div', {class: 'ot-group', 'data-circuit': c.id}, kit.h('h3', {text: t(CIRCUITS[c.kind] || 'Floor circuit')}),
  ctx.field('toggle', `control:${c.id}`, {label: t('Pump control by the E32'),
   help: t('On: the E32 switches the pump on and off itself, but only while it controls the boiler. Off: it only shows what it would do.')}),
  ctx.field('number', `max_supply_c:${c.id}`, {label: t('Highest water temperature to the floor'), unit: '°C', step: 1, min: 30, max: 70,
   help: t('When the water to the floor stays 5 °C above this for 2 minutes, the E32 switches the pump off: the mixing valve lets too hot water through. 50 °C is usual for a floor.')}),
  ctx.field('number', `run_on_max_minutes:${c.id}`, {label: t('Run on at most (minutes)'), step: 1, min: 0, max: 120,
   help: t('After the heat the pump keeps running while the water to the floor is still at least 2 °C warmer than the water back, so the floor takes up the remaining heat. It stops sooner once that difference is gone or a room is warm enough; this is the longest it runs on. 30 minutes is usual. Needs both water probes.')})));
 return kit.h('div', {class: 'fields'}, ...parts);
}

function care(ctx) {
 const {kit, t, values: v, model: m, lang} = ctx, auto = [], fixed = [];
 for (const k of m.knobs) {
  const [name, why] = KNOBS[k.key] || [k.key, ''], range = span(lang, k.min, k.max, k.unit);
  const group = kit.h('div', {class: 'ot-group', 'data-knob': k.key}, kit.h('h3', {text: t(name)}), kit.h('p', {class: 'help', text: t(why)}));
  // Automatic: the value the E32 uses now beside the switch; your own value only once you switch Automatic off.
  let value = null;
  if (k.automatic_knob) group.append(ctx.field('toggle', `auto:${k.key}`, {label: t('Automatic'),
   help: t('Now: {value}', {value: `${fmt(lang, m[`value:${k.key}`])} ${k.unit}`}),
   onChange: on => { if (value) value.hidden = on === true; }}));
  value = ctx.field('number', `value:${k.key}`, {label: k.automatic_knob ? t('Your value') : t('Value'), unit: k.unit, step: k.step, min: k.min, max: k.max,
   help: t('Possible: {range}. Standard value: {standard}.', {range, standard: `${fmt(lang, k.standard)} ${k.unit}`})});
  value.hidden = k.automatic_knob && v[`auto:${k.key}`] === true;
  group.append(value);
  (k.automatic_knob ? auto : fixed).push(group);
 }
 const yours = m.knobs.some(k => k.automatic_knob && m[`auto:${k.key}`] === false);
 const actions = kit.h('div', {class: 'ot-actions'},
  yours ? kit.button(t('Back to automatic for all'), () => ctx.act({action: 'auto_all'}, {title: t('Back to automatic for all?'),
   text: t('Every setting you set yourself goes back to automatic: the E32 sets it itself again. The fixed settings keep their values.'),
   confirm: t('Back to automatic')}), 'outlined', {'data-action': 'auto_all', disabled: ctx.readOnly}) : null,
  kit.button(t('Back to start values'), () => ctx.act({action: 'reset'}, {title: t('Back to start values?'),
   text: t('All these settings go back to their start values and the E32 starts learning them again. What it learned about your rooms stays.'),
   confirm: t('Back to start values'), danger: true}), 'outlined', {'data-action': 'reset', disabled: ctx.readOnly}));
 return kit.h('div', {class: 'fields'}, kit.h('p', {class: 'ot-heading', text: t('Set by the E32 itself')}),
  kit.h('p', {class: 'help', text: t('Automatic: the E32 sets it itself and keeps adjusting it, at most one small step a day. Switch Automatic off to use your own value.')}), ...auto,
  kit.h('p', {class: 'ot-heading', text: t('Fixed settings')}), ...fixed, actions);
}

function boiler(ctx) {
 const {kit, t, model: m} = ctx, r = m.live?.recognised, parts = [];
 parts.push(ctx.field('select', 'model', {label: t('Boiler model'), options: [{value: 'none', label: t('No boiler selected yet')}, ...m.options],
  help: t('Choosing a model only names your boiler; whether the E32 may control it is shown under Boiler recognition.')}));
 if (r && RECOGNISED[r.sentence]) {
  const facts = [r.product != null ? t('product {product}', {product: r.product}) : null, r.version ? t('version {version}', {version: r.version}) : null].filter(Boolean);
  const name = (r.name || t('Unknown model')) + (facts.length ? ` (${facts.join(', ')})` : '');
  parts.push(kit.h('p', {class: 'ot-line', 'data-live': 'recognised', text: t('Recognised on the bus: {boiler}. {sentence}', {boiler: name, sentence: t(RECOGNISED[r.sentence])})}));
 }
 return kit.h('div', {class: 'fields'}, ...parts);
}

const SCREENS = {flow, limits, circuits, care, model: boiler};
(window.OpenThermostatSettingsSections ||= []).push(['heating', {
 title: (model, item) => TITLES[item] || 'Heating and boiler',
 subtitle: (model, item) => SUBTITLES[item] || null,
 texts: TEXTS,
 errors: ERRORS,
 values,
 toSave: (v, m) => (m.screen === 'limits' && warnings(v, m).length ? {...v, confirmed: true} : v),
 confirm: (v, m, ctx) => {
  const found = m.screen === 'limits' ? warnings(v, m) : [];
  return found.length ? {title: ctx.t('Keep this highest water temperature?'), text: found.map(([key, values]) => ctx.t(key, values)).join(' '),
   confirm: ctx.t('Save this maximum')} : null;
 },
 render: ctx => ctx.kit.h('div', {class: 'ot-heating', 'data-screen': ctx.model.screen || 'list'}, ctx.kit.h('style', {text: CSS}),
  (SCREENS[ctx.model.screen] || list)(ctx))
}]);
