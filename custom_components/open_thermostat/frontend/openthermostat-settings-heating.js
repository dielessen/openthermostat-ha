/* The section Heating and boiler of the settings panel, on the kit v2 (1.4.1): the list (#heating) and its screens
   #heating/flow (Smart warm-up, weather compensation, comfort style, water in hard frost), #heating/limits (the water
   temperature limits), #heating/circuits, #heating/care (Comfort and boiler care: a compact list, each setting its own
   small screen inside the page), #heating/model (the boiler model) and #heating/boiler (Boiler settings: allow, change,
   watch, put back, Advanced, stop; every change an action of settings/action, CONTRACT-1.4.1 §3). Backend
   settings_heating.py; each model names its screen. The words are Configure's and the E32 pages'
   (test/ha-settings-texts.test.cjs); the boiler settings are worded by their key, so the viewer's language applies.
   Design: HA-INSTELPANEEL-FASE2.nl.md, 3.3 and chapter 4. */
const TEXTS = {
 nl: {
  'Smart warm-up and weather compensation': 'Slim opwarmen en weerafhankelijke regeling',
  // 1.4.4 (HA-CARDS-144): Learn again for the house (plan 2.3).
  'Learn again: house': 'Opnieuw leren: huis',
  'Learn again': 'Opnieuw leren',
  'Clears what the E32 learned about the whole house: the weather compensation and the water and rhythm of the boiler. It learns them again by itself; the week programs and the settings stay.': 'Wist wat de E32 over het hele huis leerde: de weerafhankelijke regeling en het water en ritme van de ketel. Hij leert ze vanzelf opnieuw; de weekprogramma\'s en de instellingen blijven.',
  'Clear what the E32 learned for the house?': 'Wis wat de E32 voor het huis leerde?',
  'It learns again by itself; the week programs stay.': 'Het leert vanzelf opnieuw; de weekprogramma\'s blijven.',
  'Cleared: the E32 starts learning the house again.': 'Gewist: de E32 begint opnieuw te leren voor het huis.',
  'This E32 firmware cannot start learning again on request. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware).': 'Deze E32-firmware kan niet op verzoek opnieuw beginnen met leren. Werk de E32 eerst bij (Instellingen → Updates → OpenThermostat E32 Firmware).',
  'The E32 did not clear what it learned ({error}). Check the connection and try again.': 'De E32 heeft niet gewist wat hij geleerd heeft ({error}). Controleer de verbinding en probeer het opnieuw.',
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
  'Boiler settings': 'Ketelinstellingen',
  'Off': 'Uit',
  'On': 'Aan',
  'On · {n} changes today': 'Aan · {n} wijzigingen vandaag',
  'On · a change is running': 'Aan · er loopt een wijziging',
  'Check the boiler': 'Controleer de ketel',
  'Smart warm-up': 'Slim opwarmen',
  'Warm on time, with the coolest water that does it.': 'Op tijd warm, met het koelste water dat dat haalt.',
  'The E32 starts heating early, so a room is warm at the time in its week program, with the coolest water that still does it. Off: heating starts at the program time, so a room can stay cool for a while (floor heating an hour or more).': 'De E32 begint eerder met verwarmen, zodat een ruimte warm is op de tijd in het weekprogramma, met het koelste water dat dat nog haalt. Uit: verwarmen begint pas op de programmatijd, dus een ruimte kan een tijdje koel blijven (vloerverwarming een uur of langer).',
  'Comfort style': 'Comfortstijl',
  'What the E32 weighs when it plans the heating: comfort against burner starts and gas.': 'Wat de E32 zwaarder laat wegen als hij de verwarming plant: comfort tegenover branderstarts en gas.',
  'Weather compensation': 'Weerafhankelijke regeling',
  'The colder it is outside, the warmer the water to your heating.': 'Hoe kouder het buiten is, hoe warmer het water naar je verwarming.',
  'The colder it is outside, the warmer the water to your heating gets, before the rooms cool down. The room temperature still corrects it. Without an outdoor temperature the normal room control is used.': 'Hoe kouder het buiten is, hoe warmer het water naar je verwarming wordt, nog voordat de ruimtes afkoelen. De ruimtetemperatuur stuurt nog bij. Zonder buitentemperatuur geldt de gewone ruimteregeling.',
  'Water temperature in hard frost (−10 °C)': 'Watertemperatuur bij strenge vorst (−10 °C)',
  'How warm the water gets at −10 °C outside.': 'Hoe warm het water wordt bij −10 °C buiten.',
  'How warm the water to your heating gets when it is −10 °C outside. In milder weather the E32 picks less. Not sure? Leave it on Automatic: the E32 learns this for your house.': 'Hoe warm het water naar je verwarming wordt als het −10 °C is buiten. Bij milder weer kiest de E32 minder. Niet zeker? Laat het op Automatisch staan: de E32 leert dit voor jouw huis.',
  'Lowest water temperature: automatic': 'Laagste watertemperatuur: automatisch',
  'The E32 finds it itself, never below 30 °C.': 'De E32 zoekt hem zelf uit, nooit onder 30 °C.',
  'On: the E32 finds the lowest water temperature itself, from what it learns about your boiler and house (never below 30 °C). Off: the value below.': 'Aan: de E32 zoekt de laagste watertemperatuur zelf uit, met wat hij leert over je ketel en huis (nooit onder 30 °C). Uit: de waarde hieronder.',
  'Lowest water temperature': 'Laagste watertemperatuur',
  'The lowest the E32 asks for while it heats ({minimum_range}).': 'Het laagste dat de E32 vraagt zolang hij verwarmt ({minimum_range}).',
  'Highest water temperature': 'Hoogste watertemperatuur',
  'The most the E32 ever asks for ({maximum_range}).': 'Het meeste dat de E32 ooit vraagt ({maximum_range}).',
  'The highest water temperature the E32 ever asks for ({maximum_range}, above the lowest). Floor heating fed without a mixing valve: usually at most 45–50 °C. Radiators: often 60–75 °C on cold days.': 'De hoogste watertemperatuur die de E32 ooit vraagt ({maximum_range}, boven de laagste). Vloerverwarming zonder mengklep: meestal hoogstens 45–50 °C. Radiatoren: op koude dagen vaak 60–75 °C.',
  'The boiler itself goes up to {maximum}': 'De ketel zelf gaat tot {maximum}',
  'Pump control by the E32': 'Pomp door de E32',
  'The E32 switches the pump itself while it controls the boiler.': 'De E32 zet de pomp zelf aan en uit zolang hij de ketel regelt.',
  'On: the E32 switches the pump on and off itself, but only while it controls the boiler. Off: it only shows what it would do.': 'Aan: de E32 zet de pomp zelf aan en uit, maar alleen zolang hij de ketel regelt. Uit: hij laat alleen zien wat hij zou doen.',
  'Highest water temperature to the floor': 'Hoogste watertemperatuur naar de vloer',
  '50 °C is usual for a floor.': '50 °C is gebruikelijk voor een vloer.',
  'When the water to the floor stays 5 °C above this for 2 minutes, the E32 switches the pump off: the mixing valve lets too hot water through. 50 °C is usual for a floor.': 'Blijft het water naar de vloer 2 minuten lang 5 °C boven deze waarde, dan zet de E32 de pomp uit: de mengklep laat te heet water door. 50 °C is gebruikelijk voor een vloer.',
  'Run on at most (minutes)': 'Hoogstens nalopen (minuten)',
  '30 minutes is usual; needs both water probes.': '30 minuten is gebruikelijk; daarvoor zijn beide watersondes nodig.',
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
  'The E32 adjusts these itself, at most one small step a day.': 'De E32 past deze zelf aan, hoogstens één kleine stap per dag.',
  'Fixed settings': 'Vaste instellingen',
  'Choosing a model only names your boiler; whether the E32 may control it is shown under Boiler recognition.': 'Een model kiezen geeft je ketel alleen een naam; of de E32 hem mag regelen, staat bij Ketelherkenning.',
  'It names the boiler in Home Assistant and on the E32 and chooses the explanation of its display codes; it does not change how the boiler is controlled.': 'Het geeft de ketel zijn naam in Home Assistant en op de E32 en kiest de uitleg van zijn displaycodes; het verandert niet hoe de ketel wordt geregeld.',
  'product {product}': 'productnummer {product}',
  'version {version}': 'versie {version}',
  'Unknown model': 'Onbekend model',
  'Recognised on the bus: {boiler}. {sentence}': 'Herkend op de bus: {boiler}. {sentence}',
  'Keep this highest water temperature?': 'Deze hoogste watertemperatuur houden?',
  'Save this maximum': 'Dit maximum opslaan',
  'The lowest and highest temperature of the water the boiler sends to the radiators and floor, for all rooms together.': 'De laagste en hoogste temperatuur van het water dat de ketel naar de radiatoren en vloer stuurt, voor alle ruimtes samen.',
  'While Pump control by the E32 is off, the E32 only shows what it would do with the pump and leaves the pump as it is. Switch it on once that looks right.': 'Zolang Pomp door de E32 uit staat, laat de E32 alleen zien wat hij met de pomp zou doen en laat hij de pomp zoals hij is. Zet het aan zodra dat klopt.',
  'The E32 sets these itself as it learns your house; change one only if you want it differently.': 'De E32 stelt deze zelf in terwijl hij je huis leert kennen; wijzig er alleen een als je het anders wilt.',
  'Choose your boiler, as on the E32\'s Boiler page.': 'Kies je ketel, net als op de pagina Ketel van de E32.',
  'The boiler\'s own settings, such as the hot water temperature.': 'De eigen instellingen van de ketel, zoals de warmwatertemperatuur.',
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
  'The E32 could not be reached ({error}). Nothing was saved.': 'De E32 was niet bereikbaar ({error}). Er is niets opgeslagen.',
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
  'A different boiler is connected. The E32 still controls it the Classic way; confirm the boiler so it is recognised again.': 'Er hangt een andere ketel aan. De E32 stuurt hem nog aan op de Classic-manier; bevestig de ketel zodat hij opnieuw herkend wordt.',
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
  'Could not put it back: check the boiler. {setting} should be {before} again, but the boiler did not confirm it. Look at it on the boiler; Settings → Repairs says what to do next.': 'Terugzetten niet bevestigd: controleer de ketel. {setting} hoort weer {before} te zijn, maar de ketel bevestigde het niet. Kijk het na op de ketel; Instellingen → Reparaties zegt wat je daarna doet.'
 }};
const TITLES = {flow: 'Smart warm-up and weather compensation', limits: 'Water temperature limits', circuits: 'Heating circuits',
 care: 'Comfort and boiler care', model: 'Boiler model', boiler: 'Boiler settings'};
const SUBTITLES = {
 limits: 'The lowest and highest temperature of the water the boiler sends to the radiators and floor, for all rooms together.',
 circuits: 'While Pump control by the E32 is off, the E32 only shows what it would do with the pump and leaves the pump as it is. Switch it on once that looks right.',
 care: 'The E32 sets these itself as it learns your house; change one only if you want it differently.',
 model: 'Choose your boiler, as on the E32\'s Boiler page.',
 boiler: 'The boiler\'s own settings, such as the hot water temperature.'};
const ERRORS = {
 connect_e32: 'Connect the E32 first: Configure → E32 connection.',
 // 1.4.4: Learn again: house (e32_learned.relearn_action).
 relearn_update_required: 'This E32 firmware cannot start learning again on request. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware).',
 relearn_no_free_session: 'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.',
 relearn_failed: 'The E32 did not clear what it learned ({error}). Check the connection and try again.',
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
 e32_settings_password_default: 'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.',
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
// Colours with meaning (CONTRACT-1.4.1 §8): the boiler settings' state, a result, what the E32 recognised.
const stateTone = {off: 'rest', on: 'ok', busy: 'accent', blocked: 'attention', not_now: 'rest', unavailable: 'rest'};
const resultTone = {boiler_setting_saved: 'success', boiler_setting_kept: 'success', boiler_setting_put_back: 'success', boiler_setting_unchanged: 'info',
 boiler_settings_allowed: 'success', boiler_settings_stopped: 'info', boiler_setting_failed: 'error'};
const recognisedTone = {'state.verified': 'ok', 'state.probe_passed': 'ok', 'state.other_boiler': 'attention', 'state.other_boiler.classic': 'attention'};
const CSS = `.ot-heating{display:block}.ht-status{margin:-8px 0 var(--ot-s3)}.ht-status strong{font-weight:700}
.ht-stack{display:grid;gap:var(--ot-s3)}.ht-relearn{display:grid;justify-items:start;gap:var(--ot-s2)}.ht-relearn-said:empty{display:none}
.ht-list .row{min-height:64px}.ht-list .row-line{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ht-knobs{display:flex;flex-direction:column;margin:0 calc(-1 * var(--ot-s4))}
.ht-knob{display:flex;align-items:center;gap:var(--ot-s2);border-top:1px solid var(--ot-divider);padding-right:var(--ot-s2)}.ht-knob:first-child{border-top:0}
.ht-open{flex:1 1 auto;min-width:0;display:grid;gap:2px;align-content:center;min-height:56px;padding:var(--ot-s2) var(--ot-s1) var(--ot-s2) var(--ot-s4);
border:0;background:none;color:inherit;font:inherit;text-align:left;cursor:pointer;border-radius:var(--ot-radius-s)}
.ht-knob:hover .ht-name{color:var(--ot-link)}.ht-open:focus-visible{outline:3px solid var(--ot-accent);outline-offset:-3px}.ht-name{font-weight:500;overflow-wrap:anywhere}
.ht-chevron{flex:none;display:flex;align-items:center;justify-content:center;width:32px;min-height:56px;padding:0;border:0;background:none;color:var(--ot-muted);cursor:pointer}
.ht-plain>.fields>.field:first-child{padding-top:var(--ot-s1)}
.ht-now{font-size:var(--ot-text-m);color:var(--ot-fg);font-variant-numeric:tabular-nums}.ht-knob.changed .ht-now{color:var(--ot-link)}
.ht-auto>.field{padding:0;margin:0;border:0}.ht-auto .toggle-row{gap:var(--ot-s2)}.ht-auto .label{font-size:var(--ot-text-s);font-weight:400;color:var(--ot-muted)}
.ht-auto .mark,.ht-auto .help{display:none}
.ht-sub>.btn{margin:-4px 0 var(--ot-s2) -8px}.ht-why{padding:var(--ot-s1) 0 var(--ot-s2)}
.ht-actions{display:flex;flex-wrap:wrap;gap:var(--ot-s2);margin-top:var(--ot-s4)}
.ht-stop{margin-top:var(--ot-s4);display:flex}
.ht-boiler>.card+.card,.ht-boiler>.card+.ot-card{margin-top:var(--ot-s3)}.ht-boiler .ot-card-head>.btn{margin-left:auto}
.ot-card>.ht-settings{margin:var(--ot-s3) calc(-1 * var(--ot-s4)) calc(-1 * var(--ot-s4));border-width:1px 0 0;border-radius:0 0 var(--ot-radius) var(--ot-radius)}
.ht-settings .row{min-height:64px}.ht-settings .row-value{color:var(--ot-fg);font-weight:500;font-variant-numeric:tabular-nums;white-space:normal;text-align:right;max-width:45%}
.ht-settings .row:disabled,.ht-readonly .row{cursor:default}.ht-readonly .row:hover .row-label{color:inherit}.ht-settings .row:disabled .chevron{visibility:hidden}.ht-settings .ot-chip{font-weight:500}
.ht-card-head{display:flex;align-items:center;justify-content:space-between;gap:var(--ot-s2);flex-wrap:wrap}
.ht-tick{display:flex;gap:10px;align-items:flex-start;min-height:44px;padding:var(--ot-s2) 0;cursor:pointer;font-weight:500}
.ht-tick input{flex:none;width:20px;height:20px;margin:1px 0 0;accent-color:var(--ot-fill)}.ht-tick input:focus-visible{outline:3px solid var(--ot-accent);outline-offset:2px}
.ht-text{display:grid;gap:var(--ot-s2)}.ht-text strong{font-weight:700}.ht-allow .btn.filled{margin-top:var(--ot-s2)}
.ht-dialog{width:min(480px,calc(100vw - 32px))}.ht-dialog .ht-text{margin-bottom:var(--ot-s3)}.ht-dialog .field{margin:0;padding:var(--ot-s2) 0 0;border:0}
.ht-dialog .actions{align-items:center}.ht-dialog .error{color:var(--ot-error);font-weight:500}
@media(max-width:420px){.ht-knobs{margin:0 calc(-1 * var(--ot-s3))}.ht-open{padding-left:var(--ot-s3)}.ht-knob{padding-right:var(--ot-s1)}
.ot-card>.ht-settings{margin:var(--ot-s3) calc(-1 * var(--ot-s3)) calc(-1 * var(--ot-s3))}.ht-dialog .actions{flex-direction:column-reverse;align-items:stretch}}`;

const fmt = (lang, v) => (typeof v === 'number' ? v.toLocaleString(lang) : String(v ?? ''));
const span = (lang, a, b, unit) => `${fmt(lang, a)}–${fmt(lang, b)} ${unit}`;
// A sentence whose placeholder the answer left out reads without it ("… reached. Nothing …", not "({error})").
const clean = text => String(text).replace(/ ?\(\{\w+\}\)/g, '');
// "**off**: the E32 …" with the bold part bold.
const rich = (h, text) => String(text).split('**').map((part, i) => (i % 2 ? h('strong', {text: part}) : part));
const paragraphs = (h, texts) => h('div', {class: 'ht-text'}, ...texts.map(text => h('p', {}, ...rich(h, text))));

// The editable values of a screen (its model names it); the list and Boiler settings edit nothing through the save bar.
function values(m) {
 const pick = keys => Object.fromEntries(keys.filter(k => k in m).map(k => [k, m[k]]));
 if (m.screen === 'flow') return pick(['smart_warm_up', 'comfort_style', 'weather_compensation', 'hard_frost_water_temperature']);
 if (m.screen === 'limits') return pick(['minimum_flow_automatic', 'minimum_flow_temperature', 'maximum_flow_temperature']);
 if (m.screen === 'model') return pick(['model']);
 if (m.screen === 'circuits') return pick(Object.keys(m).filter(k => k.includes(':')));
 // Care (1.4.2): an automatic knob's value is the self-tuning's, under live (outside the token); it starts your own.
 if (m.screen === 'care') return {...pick(Object.keys(m).filter(k => k.includes(':'))), ...Object.fromEntries(Object.entries(m.live || {})
  .filter(([k]) => k.startsWith('value:') && !(k in m)))};
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

/* ---- the list ---- */
// The Boiler settings row: off, on with the changes of today, a change running, or the boiler to check (telemetry).
function boilerLine(t, now) {
 if (!now) return '';
 if (now.state === 'blocked') return t('Check the boiler');
 if (now.state === 'busy') return t('On · a change is running');
 if (now.state === 'on') return now.writes_today ? t('On · {n} changes today', {n: now.writes_today}) : t('On');
 return t('Off');
}
function list(ctx) {
 const {kit, t, model: m, lang} = ctx, rows = [];
 if (m.flow_offered) {
  const f = m.flow, style = f && STYLES[f.comfort_style];
  rows.push(ctx.row({label: t('Smart warm-up and weather compensation'), icon: 'clock', route: '#heating/flow', data: {item: 'flow'},
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
 rows.push(ctx.row({label: t('Water temperature limits'), icon: 'limits', summary: [limits], route: '#heating/limits', data: {item: 'limits'}}));
 if (m.circuits?.length) rows.push(ctx.row({label: t('Heating circuits'), icon: 'floor', route: '#heating/circuits', data: {item: 'circuits'},
  summary: [m.circuits.map(c => t(CIRCUITS[c.kind] || 'Floor circuit')).join(' · ')]}));
 if (m.care_offered) rows.push(ctx.row({label: t('Comfort and boiler care'), icon: 'thermostat', route: '#heating/care', data: {item: 'care'},
  summary: m.care ? [!m.care.yours ? t('Automatic') : m.care.yours === 1 ? t('1 setting set by you') : t('{n} settings set by you', {n: m.care.yours})] : []}));
 rows.push(ctx.row({label: t('Boiler model'), icon: 'fire', summary: [m.boiler_model || t('No boiler selected yet')], route: '#heating/model', data: {item: 'model'}}));
 if (m.boiler_settings) {
  const now = m.live?.boiler_settings;
  rows.push(ctx.row({label: now?.preview === false ? t('Boiler settings') : t('Boiler settings (preview)'), icon: 'wrench', route: '#heating/boiler',
   data: {item: 'boiler'}, summary: [boilerLine(t, now)]}));
 }
 const box = kit.h('div', {class: 'card list ht-list'}, ...rows);
 // 1.4.4 (plan 2.3): Learn again for the house, under the list, only on firmware that offers it, for an administrator.
 return m.relearn && !ctx.readOnly ? kit.h('div', {class: 'ht-stack'}, box, relearnHouse(ctx)) : box;
}
function relearnHouse(ctx) {
 const {kit, t} = ctx, {h} = kit, said = h('div', {class: 'ht-relearn-said', 'data-relearn-said': ''});
 const go = kit.button(t('Learn again'), async () => {
  if (!(await kit.confirm(go.getRootNode(), {title: t('Clear what the E32 learned for the house?'), text: t('It learns again by itself; the week programs stay.'),
   confirm: t('Learn again'), lang: ctx.lang}))) return;
  go.disabled = true; said.replaceChildren();
  try { await ctx.action('relearn', {house: true}); said.replaceChildren(kit.notice(t('Cleared: the E32 starts learning the house again.'), 'success')); }
  catch (err) { said.replaceChildren(kit.inlineError(err?.text || ctx.errorText(err?.code || 'unknown'))); }
  go.disabled = false;
 }, 'outlined', {'data-relearn': ''});
 return kit.card({title: t('Learn again: house'), icon: 'clock', cls: 'form ht-relearn', data: {relearn: 'house'}},
  h('p', {class: 'help', text: t('Clears what the E32 learned about the whole house: the weather compensation and the water and rhythm of the boiler. It learns them again by itself; the week programs and the settings stay.')}),
  go, said);
}

/* ---- Smart warm-up and weather compensation ---- */
function flow(ctx) {
 const {kit, t, values: v} = ctx, parts = [];
 parts.push(ctx.field('toggle', 'smart_warm_up', {label: t('Smart warm-up'), help: t('Warm on time, with the coolest water that does it.'),
  more: t('The E32 starts heating early, so a room is warm at the time in its week program, with the coolest water that still does it. Off: heating starts at the program time, so a room can stay cool for a while (floor heating an hour or more).')}));
 if ('comfort_style' in v) parts.push(ctx.field('segmented', 'comfort_style', {label: t('Comfort style'),
  more: t('What the E32 weighs when it plans the heating: comfort against burner starts and gas.'),
  options: Object.entries(STYLES).map(([value, [label, help]]) => ({value, label: t(label), help: t(help)}))}));
 parts.push(ctx.field('toggle', 'weather_compensation', {label: t('Weather compensation'), help: t('The colder it is outside, the warmer the water to your heating.'),
  more: t('The colder it is outside, the warmer the water to your heating gets, before the rooms cool down. The room temperature still corrects it. Without an outdoor temperature the normal room control is used.')}));
 const choices = [{value: 'automatic', label: t('Automatic')}];
 for (let c = 25; c <= 80; c++) choices.push({value: String(c), label: kit.together(`${c} °C`)});
 parts.push(ctx.field('select', 'hard_frost_water_temperature', {label: t('Water temperature in hard frost (−10 °C)'), options: choices,
  help: kit.together(t('How warm the water gets at −10 °C outside.')),
  more: t('How warm the water to your heating gets when it is −10 °C outside. In milder weather the E32 picks less. Not sure? Leave it on Automatic: the E32 learns this for your house.')}));
 return kit.card({cls: 'form ht-plain'}, kit.h('div', {class: 'fields'}, ...parts));
}

/* ---- the water temperature limits ---- */
function limits(ctx) {
 const {kit, t, values: v, model: m, lang} = ctx, {h} = kit, unit = m.unit, live = m.live || {};
 const range = r => span(lang, r[0], r[1], unit), parts = [];
 // The boiler's own maximum: the screen's one status line.
 const status = typeof live.boiler_maximum === 'number'
  ? h('div', {class: 'ht-status', 'data-live': 'boiler_maximum'}, kit.statusLine(t('The boiler itself goes up to {maximum}', {maximum: `${fmt(lang, live.boiler_maximum)} ${unit}`}), 'rest')) : null;
 let lowest = null;
 if ('minimum_flow_automatic' in v) {
  const now = live.minimum_now && NOW[live.minimum_now.kind] ? t(NOW[live.minimum_now.kind], {value: `${fmt(lang, live.minimum_now.value)} ${unit}`}) : null;
  parts.push(ctx.field('toggle', 'minimum_flow_automatic', {label: t('Lowest water temperature: automatic'), help: kit.together(now || t('The E32 finds it itself, never below 30 °C.')),
   more: t('On: the E32 finds the lowest water temperature itself, from what it learns about your boiler and house (never below 30 °C). Off: the value below.'),
   // The lowest value is the E32's own while automatic: its field waits until you switch automatic off.
   onChange: on => { if (lowest) lowest.hidden = on === true; }}));
 }
 lowest = ctx.field('stepper', 'minimum_flow_temperature', {label: t('Lowest water temperature'), unit, step: 1, min: m.minimum_range[0], max: m.minimum_range[1],
  help: kit.together(t('The lowest the E32 asks for while it heats ({minimum_range}).', {minimum_range: range(m.minimum_range)}))});
 lowest.hidden = v.minimum_flow_automatic === true;
 parts.push(lowest);
 parts.push(ctx.field('stepper', 'maximum_flow_temperature', {label: t('Highest water temperature'), unit, step: 1, min: m.maximum_range[0], max: m.maximum_range[1],
  help: kit.together(t('The most the E32 ever asks for ({maximum_range}).', {maximum_range: range(m.maximum_range)})),
  more: t('The highest water temperature the E32 ever asks for ({maximum_range}, above the lowest). Floor heating fed without a mixing valve: usually at most 45–50 °C. Radiators: often 60–75 °C on cold days.', {maximum_range: range(m.maximum_range)})}));
 return h('div', {}, status, kit.card({cls: 'form ht-plain'}, h('div', {class: 'fields'}, ...parts)));
}

/* ---- the heating circuits ---- */
function circuits(ctx) {
 const {kit, t, model: m} = ctx;
 return kit.h('div', {}, ...m.circuits.map(c => kit.card({title: t(CIRCUITS[c.kind] || 'Floor circuit'), icon: c.kind === 'radiators' ? 'radiator' : 'floor', cls: 'form',
  data: {circuit: c.id}}, kit.h('div', {class: 'fields'},
  ctx.field('toggle', `control:${c.id}`, {label: t('Pump control by the E32'), help: t('The E32 switches the pump itself while it controls the boiler.'),
   more: t('On: the E32 switches the pump on and off itself, but only while it controls the boiler. Off: it only shows what it would do.')}),
  ctx.field('stepper', `max_supply_c:${c.id}`, {label: t('Highest water temperature to the floor'), unit: '°C', step: 1, min: 30, max: 70, help: kit.together(t('50 °C is usual for a floor.')),
   more: t('When the water to the floor stays 5 °C above this for 2 minutes, the E32 switches the pump off: the mixing valve lets too hot water through. 50 °C is usual for a floor.')}),
  ctx.field('stepper', `run_on_max_minutes:${c.id}`, {label: t('Run on at most (minutes)'), step: 1, min: 0, max: 120, help: t('30 minutes is usual; needs both water probes.'),
   more: t('After the heat the pump keeps running while the water to the floor is still at least 2 °C warmer than the water back, so the floor takes up the remaining heat. It stops sooner once that difference is gone or a room is warm enough; this is the longest it runs on. 30 minutes is usual. Needs both water probes.')})))));
}

/* ---- Comfort and boiler care: a compact list; each setting its own small screen inside the page ---- */
// The setting whose screen is open, for the page's values it was opened on: a redraw of that page (an error after a save)
// keeps it open; a fresh page (another visit, a save that went through) shows the list.
const careOpen = {values: null, key: null};
function care(ctx) {
 const {kit, t, values: v, model: m, lang} = ctx, {h} = kit, rows = {auto: [], fixed: []}, subs = {}, opens = {};
 const shown = (k, value) => kit.together(`${fmt(lang, value)} ${k.unit}`);
 // The value in effect: yours, or (automatic) the self-tuning's, which the model gives under live since 1.4.2.
 const cur = k => m[`value:${k.key}`] ?? m.live?.[`value:${k.key}`];
 const now = k => (k.automatic_knob && v[`auto:${k.key}`] === true ? cur(k) : v[`value:${k.key}`]);
 const listView = h('div', {class: 'ht-care-list'}), subView = h('div', {class: 'ht-care-subs'});
 const show = key => {
  careOpen.values = v; careOpen.key = key;
  listView.hidden = !!key;
  for (const [k, el] of Object.entries(subs)) el.hidden = k !== key;
  queueMicrotask(() => (key ? subs[key]?.querySelector('.btn') : opens[careOpen.last])?.focus?.());
  if (key) careOpen.last = key;
 };
 for (const k of m.knobs) {
  const [name, why] = KNOBS[k.key] || [k.key, ''], range = span(lang, k.min, k.max, k.unit);
  const value = h('span', {class: 'ht-now'}), row = h('div', {class: 'ht-knob', 'data-knob': k.key});
  const refresh = () => { value.textContent = shown(k, now(k)); row.classList.toggle('changed', v[`value:${k.key}`] !== cur(k) || v[`auto:${k.key}`] !== m[`auto:${k.key}`]); };
  // The name and value open the setting's screen; so does the chevron at the end (one stop for the keyboard).
  opens[k.key] = h('button', {type: 'button', class: 'ht-open', 'data-open': k.key, on: {click: () => show(k.key)}}, h('span', {class: 'ht-name', text: t(name)}), value);
  row.append(opens[k.key]);
  const chevron = h('button', {type: 'button', class: 'ht-chevron', tabindex: '-1', 'aria-hidden': 'true', on: {click: () => show(k.key)}}, kit.icon('chevron-right', {size: 20}));
  // Automatic or yours, in the row itself and on the setting's own screen: one value, two switches that follow each other.
  const twins = [];
  let own = null;
  const automatic = () => {
   let api;
   const el = ctx.field(o => (api = kit.fields.toggle(o)), `auto:${k.key}`, {label: t('Automatic'), help: kit.together(t('Now: {value}', {value: shown(k, cur(k))})),
    onChange: on => { for (const x of twins) if (x !== api) x.value = on; if (own) own.hidden = on === true; refresh(); }});
   el.querySelector('input')?.setAttribute('aria-label', `${t(name)}: ${t('Automatic')}`);
   twins.push(api);
   return el;
  };
  if (k.automatic_knob) row.append(h('div', {class: 'ht-auto'}, automatic()));
  row.append(chevron);
  const sub = h('div', {class: 'ht-sub', 'data-sub': k.key, hidden: true},
   kit.button(t('Comfort and boiler care'), () => show(null), 'text', {icon: 'chevron-left', 'data-back-care': ''}));
  const fields = [];
  if (k.automatic_knob) fields.push(automatic());
  own = ctx.field('stepper', `value:${k.key}`, {label: k.automatic_knob ? t('Your value') : t('Value'), unit: k.unit, step: k.step, min: k.min, max: k.max,
   help: kit.together(t('Possible: {range}. Standard value: {standard}.', {range, standard: shown(k, k.standard)})), onChange: refresh});
  own.hidden = k.automatic_knob && v[`auto:${k.key}`] === true;
  fields.push(own);
  sub.append(kit.card({title: t(name), cls: 'form'}, h('p', {class: 'help ht-why', text: t(why)}), h('div', {class: 'fields'}, ...fields)));
  subs[k.key] = sub;
  refresh();
  (k.automatic_knob ? rows.auto : rows.fixed).push(row);
 }
 const yours = m.knobs.some(k => k.automatic_knob && m[`auto:${k.key}`] === false);
 const actions = h('div', {class: 'ht-actions'},
  yours ? kit.button(t('Back to automatic for all'), () => ctx.act({action: 'auto_all'}, {title: t('Back to automatic for all?'),
   text: t('Every setting you set yourself goes back to automatic: the E32 sets it itself again. The fixed settings keep their values.'),
   confirm: t('Back to automatic')}), 'outlined', {'data-action': 'auto_all', disabled: ctx.readOnly}) : null,
  kit.button(t('Back to start values'), () => ctx.act({action: 'reset'}, {title: t('Back to start values?'),
   text: t('All these settings go back to their start values and the E32 starts learning them again. What it learned about your rooms stays.'),
   confirm: t('Back to start values'), danger: true}), 'danger', {'data-action': 'reset', disabled: ctx.readOnly}));
 listView.append(
  kit.card({title: t('Set by the E32 itself'), summary: t('The E32 adjusts these itself, at most one small step a day.'), data: {group: 'auto'}}, h('div', {class: 'ht-knobs'}, ...rows.auto)),
  rows.fixed.length ? kit.card({title: t('Fixed settings'), data: {group: 'fixed'}}, h('div', {class: 'ht-knobs'}, ...rows.fixed)) : null, actions);
 subView.append(...Object.values(subs));
 // A field the save refused opens its screen; otherwise the screen that was open on this page stays open.
 const invalid = Object.keys(subs).find(key => subs[key].querySelector('.field.invalid'));
 const open = invalid || (careOpen.values === v ? careOpen.key : null);
 if (careOpen.values !== v) { careOpen.values = null; careOpen.key = null; }
 listView.hidden = !!open;
 for (const [key, el] of Object.entries(subs)) el.hidden = key !== open;
 if (open) { careOpen.values = v; careOpen.key = open; }
 return h('div', {class: 'ht-care'}, listView, subView);
}

/* ---- the boiler model ---- */
function boiler(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit, r = m.live?.recognised;
 let status = null;
 if (r && RECOGNISED[r.sentence]) {
  const facts = [r.product != null ? t('product {product}', {product: r.product}) : null, r.version ? t('version {version}', {version: r.version}) : null].filter(Boolean);
  const name = (r.name || t('Unknown model')) + (facts.length ? ` (${facts.join(', ')})` : '');
  status = h('div', {class: 'ht-status', 'data-live': 'recognised'},
   kit.statusLine(t('Recognised on the bus: {boiler}. {sentence}', {boiler: name, sentence: t(RECOGNISED[r.sentence])}), recognisedTone[r.sentence] || 'rest'));
 }
 return h('div', {}, status, kit.card({cls: 'form ht-plain'}, h('div', {class: 'fields'},
  ctx.field('select', 'model', {label: t('Boiler model'), options: [{value: 'none', label: t('No boiler selected yet')}, ...m.options],
   help: t('Choosing a model only names your boiler; whether the E32 may control it is shown under Boiler recognition.'),
   more: t('It names the boiler in Home Assistant and on the E32 and chooses the explanation of its display codes; it does not change how the boiler is controlled.')}))));
}

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
   box.replaceChildren(kit.card({}, kit.empty({icon: 'wrench', text: t(ERRORS[m.reason] || ERRORS.boiler_setting_unavailable)})));
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

const SCREENS = {flow, limits, circuits, care, model: boiler};
(window.OpenThermostatSettingsSections ||= []).push(['heating', {
 title: (model, item) => (item === 'boiler' && model?.preview !== false ? 'Boiler settings (preview)' : TITLES[item] || 'Heating and boiler'),
 subtitle: (model, item) => SUBTITLES[item] || null,
 texts: TEXTS,
 errors: ERRORS,
 cards: true,
 values,
 toSave: (v, m) => (m.screen === 'limits' && warnings(v, m).length ? {...v, confirmed: true} : v),
 confirm: (v, m, ctx) => {
  const found = m.screen === 'limits' ? warnings(v, m) : [];
  return found.length ? {title: ctx.t('Keep this highest water temperature?'), text: found.map(([key, values]) => ctx.t(key, values)).join(' '),
   confirm: ctx.t('Save this maximum')} : null;
 },
 // The style of this section goes first; Boiler settings draws itself (its dialogs hang on this element, not on what it redraws).
 render: ctx => {
  const {h} = ctx.kit, screen = ctx.model.screen || 'list', root = h('div', {class: 'ot-heating', 'data-screen': screen}, h('style', {text: CSS}));
  root.append(screen === 'boiler' ? boilerSettings(ctx, root) : (SCREENS[screen] || list)(ctx));
  return root;
 }
}]);
