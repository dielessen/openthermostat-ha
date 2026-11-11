/* The settings panel's section Rooms (1.4; 1.4.1 phase 2): the rooms as cards, and one room's whole screen in collapsible
   sections (HA-INSTELPANEEL-FASE2.nl.md 3.1): General, Temperature, Week program (the week planner itself, CONTRACT-1.4.1
   §4), Windows and doors, Radiator valves, Persons, Notifications for this room, Temperature limits, and Remove room.
   Backend settings_rooms.py (CONTRACT-1.4.1 §1: the room model, its save keys and the form's codes); the kit and the
   core: openthermostat-settings-kit.js, openthermostat-settings.js. Live values (temperatures, what the room does now,
   batteries) come from hass.states and follow it without a redraw. Texts: TEXTS, English key; Configure's words for
   the same settings, word for word (test/ha-settings-texts.test.cjs). */
const TEXTS = {
 nl: {
  'Driven by temperature; the position cannot be read': 'Gestuurd op temperatuur; de stand is niet uit te lezen',
  'Regulates itself to the target; the position cannot be read': 'Regelt zichzelf naar het doel; de stand is niet uit te lezen',
  'Set to manual by Home Assistant at {time}': 'Door Home Assistant op handmatig gezet om {time}',
  'Through Home Assistant': 'Via Home Assistant',
  'Valve control': 'Radiatorkranen aansturen',
  'On: these valves follow the room (only while the E32 controls the boiler itself). Off: the valves keep their own settings and nothing is sent to them.': 'Aan: deze kranen volgen de ruimte (alleen zolang de E32 de ketel zelf aanstuurt). Uit: de kranen houden hun eigen instellingen en er gaat niets naar ze toe.',
  'Kept on the E32': 'Bewaard op de E32',
  'On the BLU Gateway': 'Aan de BLU Gateway',
  'Add from the BLU Gateway': 'Toevoegen van de BLU Gateway',
  'Choose a valve': 'Kies een kraan',
  'Use limits between {range} with the minimum not above the maximum, and a temperature without a week program within them.': 'Gebruik grenzen tussen {range} met het minimum niet boven het maximum, en een temperatuur zonder weekprogramma daartussen.',
  'A temperature of the week program is outside the room\'s temperature limits.': 'Een temperatuur van het weekprogramma ligt buiten de temperatuurgrenzen van de ruimte.',
  'A floor loop valve cannot be kept open as the water\'s path: choose it in one of the two lists only.': 'Een kraan van een vloergroep kan niet open blijven als weg voor het water: kies hem in maar één van de twee lijsten.',
  'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again. Nothing has been changed.': 'Hiervoor is nieuwere E32-firmware nodig. Werk de E32 eerst bij (Instellingen → Updates → OpenThermostat E32 Firmware) en probeer het opnieuw. Er is niets gewijzigd.',
  'Something in the form was not valid. Try again.': 'Iets in het formulier klopte niet. Probeer het opnieuw.',
  'Rooms': 'Ruimtes',
  'New room': 'Nieuwe ruimte',
  'Add room': 'Ruimte toevoegen',
  'The E32 holds at most {max} rooms. Remove a room first.': 'De E32 heeft plaats voor hoogstens {max} ruimtes. Verwijder eerst een ruimte.',
  'On': 'Aan',
  'Heat along only': 'Alleen meeverwarmen',
  'Off': 'Uit',
  'Off until {moment}, then on again': 'Uit tot {moment}, daarna weer aan',
  'Off until {moment}, then heating along again': 'Uit tot {moment}, daarna weer meeverwarmen',
  'Radiators': 'Radiatoren',
  'Floor heating': 'Vloerverwarming',
  'No temperature yet': 'Nog geen temperatuur',
  'The E32 measures this thermometer itself; choose it as the source, so it also works without Home Assistant.': 'De E32 meet deze thermometer zelf; kies hem als bron, dan werkt het ook zonder Home Assistant.',
  'Use the E32\'s sensor': 'Sensor van de E32 gebruiken',
  'Room name': 'Naam van de ruimte',
  'The name you see in Home Assistant and on the E32. Up to 40 letters (fewer with accents or emoji); renaming keeps the room and its history.': 'De naam die je in Home Assistant en op de E32 ziet. Maximaal 40 tekens (minder met accenten of emoji); hernoemen behoudt de ruimte en haar geschiedenis.',
  'Heating': 'Verwarmen',
  'The room can ask for heat.': 'De ruimte kan warmte vragen.',
  'The room keeps its target and its radiator valves open for it, but it never asks for heat; it warms while the boiler runs for other rooms.': 'De ruimte houdt de gewenste temperatuur en de radiatorkranen gaan ervoor open, maar ze vraagt nooit warmte; ze warmt mee zolang de ketel voor andere ruimtes stookt.',
  'The room asks for no heat.': 'De ruimte vraagt geen warmte.',
  'Off until (optional)': 'Uit tot (optioneel)',
  'The date and time the room heats again by itself. Empty: off until you turn it on.': 'Het moment waarop de ruimte vanzelf weer verwarmt. Leeg: uit tot je haar weer aanzet.',
  'Heating type': 'Verwarmingstype',
  'Radiators or floor heating. Floor heating warms up slowly and needs cooler water, so each type gets its own water temperature.': 'Radiatoren of vloerverwarming. Vloerverwarming warmt langzaam op en wil koeler water, dus elk type krijgt een eigen watertemperatuur.',
  'Temperature sources': 'Temperatuurbronnen',
  'The first one with a fresh value is used; the others are backups. With one source: if it fails, the room stops asking for heat after 30 minutes. A second source, for example a Bluetooth sensor, covers that.': 'De eerste met een actuele waarde wordt gebruikt; de andere zijn reserve. Met één bron: valt die weg, dan vraagt de ruimte na 30 minuten geen warmte meer. Een tweede bron, bijvoorbeeld een Bluetooth-sensor, vangt dat op.',
  'Used first': 'Eerst gebruikt',
  'Use first': 'Eerst gebruiken',
  'Use {name} first': '{name} eerst gebruiken',
  'Remove {name}': '{name} verwijderen',
  'Add a source': 'Bron toevoegen',
  'At most four temperature sources per room.': 'Hoogstens vier temperatuurbronnen per ruimte.',
  'No source yet: choose at least one.': 'Nog geen bron: kies er minstens één.',
  'Search by name': 'Zoek op naam',
  'Bluetooth sensor on the E32': 'Bluetooth-sensor op de E32',
  'No reading': 'Geen meting',
  'just now': 'zojuist',
  '{n} min ago': '{n} min geleden',
  '{n} h ago': '{n} uur geleden',
  'Setting device (optional)': 'Instelapparaat (optioneel)',
  'A thermostat or radiator valve (for example a tado or TV02), or a number with a target, to set the room with. Home Assistant keeps it at the room\'s temperature; turning it changes the room (until the next switch time with a week program, for good without one). Turn off the device\'s own schedule (manual mode), otherwise it changes the temperature by itself.': 'Een thermostaat of radiatorkraan (bijvoorbeeld een tado of TV02), of een getal met een doel, om de ruimte mee in te stellen. Home Assistant houdt het op de temperatuur van de ruimte; eraan draaien verandert de ruimte (met een weekprogramma tot de volgende schakeltijd, zonder weekprogramma voorgoed). Zet het eigen programma van het apparaat uit (handmatige stand), anders verandert het de temperatuur zelf.',
  'With On, this valve regulates on its own sensor and often closes before the room is warm; consider valve control with a separate thermometer instead.': 'Op Aan regelt deze kraan op zijn eigen voeler en sluit hij vaak vóór de ruimte warm is; overweeg kraansturing met een losse thermometer.',
  'Last written: {temperature} at {time}': 'Laatst geschreven: {temperature} om {time}',
  'Last turned on the device: {temperature} at {time}': 'Laatst aan het apparaat gedraaid: {temperature} om {time}',
  'Nothing written to it yet.': 'Er is nog niets naartoe geschreven.',
  'Temperature without a week program': 'Temperatuur zonder weekprogramma',
  'The temperature the room keeps when it has no week program, and while the E32\'s clock is not set yet. Without a week program a manual change becomes this temperature.': 'De temperatuur die de ruimte aanhoudt als ze geen weekprogramma heeft, en zolang de klok van de E32 nog niet gezet is. Zonder weekprogramma wordt een handmatige wijziging deze temperatuur.',
  'Heat along up to': 'Meeverwarmen tot',
  'The valve opens up to this temperature; the room asks for no heat itself. This is the same setting as the temperature without a week program.': 'De kraan gaat open tot deze temperatuur; de ruimte vraagt zelf geen warmte. Dit is dezelfde instelling als de temperatuur zonder weekprogramma.',
  'This room follows its week program; the valve gets those temperatures.': 'Deze ruimte volgt haar weekprogramma; de kraan krijgt die temperaturen.',
  'Use one fixed temperature': 'Gebruik één vaste temperatuur',
  'Use one fixed temperature?': 'Eén vaste temperatuur gebruiken?',
  'The week program of {name} is removed, and {temperature} becomes its temperature from now on. You can change that temperature here afterwards.': 'Het weekprogramma van {name} wordt verwijderd en {temperature} wordt vanaf nu haar temperatuur. Die temperatuur kun je hier daarna nog wijzigen.',
  'Remove the week program': 'Weekprogramma verwijderen',
  'Now {temperature} from the week program, until {time}': 'Nu {temperature} uit het weekprogramma, tot {time}',
  'Now {temperature} from the week program': 'Nu {temperature} uit het weekprogramma',
  'Now {temperature}: the temperature without a week program': 'Nu {temperature}: de temperatuur zonder weekprogramma',
  'Temporarily {temperature} until {time}': 'Tijdelijk {temperature} tot {time}',
  'Temporarily {temperature}': 'Tijdelijk {temperature}',
  'Now {temperature} from the reset time of {time}': 'Nu {temperature} door het terugzetmoment van {time}',
  'Now {temperature} from a reset time': 'Nu {temperature} door een terugzetmoment',
  '{temperature}: summer mode': '{temperature}: Zomerstand',
  '{temperature}: a window or door is open': '{temperature}: er staat een raam of deur open',
  'Boost until {time}': 'Boost tot {time}',
  'Boost active': 'Boost actief',
  'Use {temperature}': 'Neem {temperature} over',
  'The advice changed in the meantime. Reload the page.': 'Het advies is intussen veranderd. Herlaad de pagina.',
  'There is no advice to use for this room right now. Reload the page.': 'Er is nu geen advies om over te nemen voor deze ruimte. Herlaad de pagina.',
  'Week program': 'Weekprogramma',
  'Every day': 'Elke dag',
  'Start with the standard week program': 'Beginnen met het standaardweekprogramma',
  '“Workdays and weekend”: 20 °C by day, 18 °C while away on workdays, 16 °C at night. You change it afterwards in the week planner. Off: the room keeps its temperature without a week program.': '“Werkdagen en weekend”: overdag 20 °C, 18 °C als je op werkdagen weg bent, ’s nachts 16 °C. Je wijzigt het daarna in de weekplanner. Uit: de ruimte houdt haar temperatuur zonder weekprogramma.',
  'At most four reset times per room.': 'Hoogstens vier terugzetmomenten per ruimte.',
  'Smart warm-up': 'Slim opwarmen',
  'As the house': 'Als het huis',
  'No window or door contacts': 'Geen raam- of deurcontacten',
  'Remove room': 'Ruimte verwijderen',
  'Remove {name}?': '{name} verwijderen?',
  'The E32 forgets the room with its week program and reset times, and Home Assistant removes its devices. This cannot be undone.': 'De E32 vergeet de ruimte met haar weekprogramma en terugzetmomenten, en Home Assistant verwijdert haar apparaten. Dit kan niet ongedaan worden gemaakt.',
  'Give the room a name of up to 40 letters (fewer with accents or emoji).': 'Geef de ruimte een naam van hoogstens 40 tekens (minder met accenten of emoji).',
  '{source} cannot be used here. Choose a thermostat or a temperature sensor; for the setting device a thermostat, radiator valve or number.': '{source} kan hier niet gebruikt worden. Kies een thermostaat of temperatuursensor; als instelapparaat een thermostaat, radiatorkraan of getal.',
  '{source} cannot be used: its name in Home Assistant is longer than 80 characters.': '{source} kan niet gebruikt worden: de naam in Home Assistant is langer dan 80 tekens.',
  '{source} does not exist in Home Assistant.': '{source} bestaat niet in Home Assistant.',
  '{source} reports no current temperature. Choose a thermostat that measures the room, or a temperature sensor.': '{source} meldt geen actuele temperatuur. Kies een thermostaat die de ruimte meet, of een temperatuursensor.',
  '{source} does not report a temperature (°C or °F). Choose a temperature sensor.': '{source} meldt geen temperatuur (°C of °F). Kies een temperatuursensor.',
  'Choose 1 to 4 temperature sources.': 'Kies 1 tot 4 temperatuurbronnen.',
  'A source is in the list twice.': 'Een bron staat twee keer in de lijst.',
  'Another room has this name.': 'Een andere ruimte heeft deze naam.',
  'The E32 cannot use this setting device. Choose another one.': 'De E32 kan dit instelapparaat niet gebruiken. Kies een ander.',
  'Reset time {line}: choose a time, at least one day and a temperature in whole or half degrees.': 'Terugzetmoment {line}: kies een tijd, minstens één dag en een temperatuur in hele of halve graden.',
  'Reset time {line}: the temperature is outside the room\'s temperature limits.': 'Terugzetmoment {line}: de temperatuur ligt buiten de temperatuurgrenzen van de ruimte.',
  'Reset time {line}: another reset time is already set for that day and time.': 'Terugzetmoment {line}: op die dag en dat tijdstip staat al een terugzetmoment.',
  'The E32 did not accept the reset times ({error}). Check the days, the times and the temperatures.': 'De E32 heeft de terugzetmomenten niet aangenomen ({error}). Controleer de dagen, de tijden en de temperaturen.',
  'Choose a moment in the future (before 2100) for “Off until”, or leave it empty.': 'Kies voor “Uit tot” een moment in de toekomst (voor 2100), of laat het leeg.',
  'The E32 already has 8 rooms. Remove a room first.': 'De E32 heeft al 8 ruimtes. Verwijder eerst een ruimte.',
  'This room is no longer on the E32.': 'Deze ruimte staat niet meer op de E32.',
  'The rooms were changed on the E32 twice while saving. Nothing was saved; try again.': 'De ruimtes zijn tijdens het opslaan twee keer op de E32 gewijzigd. Er is niets opgeslagen; probeer het opnieuw.',
  'The rooms no longer fit on the E32 (4 KB). Use shorter names, fewer sources or fewer switch times. Nothing was saved.': 'De ruimtes passen niet meer op de E32 (4 KB). Gebruik kortere namen, minder bronnen of minder schakeltijden. Er is niets opgeslagen.',
  'The E32 has no storage space left for its rooms. Remove a room you no longer use, or a few switch times, and save again. Nothing was saved.': 'De E32 heeft geen opslagruimte meer voor zijn ruimtes. Verwijder een ruimte die je niet meer gebruikt, of een paar schakeltijden, en sla opnieuw op. Er is niets opgeslagen.',
  'A device can be the room\'s setting device or a radiator valve the E32 drives, not both. Choose one.': 'Een apparaat kan het instelapparaat van de ruimte zijn óf een kraan die de E32 aanstuurt, niet allebei. Kies er één.',
  'Choose one of the people in the list.': 'Kies een van de personen in de lijst.',
  'The E32 could not confirm the change. Reload the page to see what is saved.': 'De E32 kon de wijziging niet bevestigen. Laad de pagina opnieuw om te zien wat er is opgeslagen.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'De E32 was niet bereikbaar ({error}). Er is niets opgeslagen.',
  'The E32 sent rooms this version cannot read. Update the E32 firmware and the integration together.': 'De E32 stuurde ruimtes die deze versie niet kan lezen. Werk de E32-firmware en de integratie samen bij.',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'De E32 accepteert het bewaarde wachtwoord niet meer. Home Assistant vraagt om het nieuwe: Instellingen → Apparaten en diensten → OpenThermostat → Opnieuw verifiëren.',
  'The E32 did not accept the room ({error}). Nothing was saved.': 'De E32 heeft de ruimte niet aangenomen ({error}). Er is niets opgeslagen.',
  'The E32 did not accept the week program. Check it in the week planner.': 'De E32 heeft het weekprogramma niet aangenomen. Controleer het in de weekplanner.',
  'General': 'Algemeen',
  'Temperature': 'Temperatuur',
  'Windows and doors': 'Ramen en deuren',
  'Radiator valves': 'Radiatorkranen',
  'Persons': 'Personen',
  'Notifications for this room': 'Meldingen voor deze ruimte',
  'Temperature limits': 'Temperatuurgrenzen',
  'Window contacts': 'Raamcontacten',
  'Door contacts': 'Deurcontacten',
  'Pause after (windows)': 'Pauze na (ramen)',
  'Pause after (doors)': 'Pauze na (deuren)',
  'As the house ({value})': 'Als het huis ({value})',
  'The house value applies; you change it under House.': 'De waarde van het huis geldt; die wijzig je onder Huis.',
  'Own value': 'Eigen waarde',
  'This room uses its own value.': 'Deze ruimte gebruikt een eigen waarde.',
  'Battery {level}': 'Batterij {level}',
  'Battery low': 'Batterij bijna leeg',
  'Last report {age}': 'Laatste melding {age}',
  'Not found in Home Assistant': 'Niet gevonden in Home Assistant',
  'Model of {name}': 'Model van {name}',
  'No radiator valves in this room.': 'Geen radiatorkranen in deze ruimte.',
  'The radiator valves could not be read ({error}). Reload.': 'De radiatorkranen konden niet gelezen worden ({error}). Herlaad.',
  'Reload': 'Opnieuw laden',
  'Could not be read': 'Niet te lezen',
  'At most {max} radiator valves per room.': 'Hoogstens {max} radiatorkranen per ruimte.',
  'Add a valve': 'Kraan toevoegen',
  'Driven by position': 'Gestuurd op stand',
  'Persons of this room': 'Personen van deze ruimte',
  'Empty: the room follows the house.': 'Leeg: de ruimte volgt het huis.',
  'Temperature when this room\'s people are away': 'Temperatuur als de mensen van deze ruimte weg zijn',
  'Who gets them': 'Wie krijgt ze',
  'Everyone with a phone': 'Iedereen met een telefoon',
  'Chosen people': 'Gekozen personen',
  'Recipients': 'Ontvangers',
  '{name} (not found)': '{name} (niet gevonden)',
  'Messages about {room} go to {people}.': 'Berichten van {room} gaan naar {people}.',
  'Messages about {room} go to everyone with a phone.': 'Berichten van {room} gaan naar iedereen met een telefoon.',
  'Messages about {room} go to nobody; they show in Home Assistant only.': 'Berichten van {room} gaan naar niemand; ze verschijnen alleen in Home Assistant.',
  ' and ': ' en ',
  'Notify about this room': 'Meldingen over deze ruimte',
  'Off: no messages about this room.': 'Uit: geen berichten over deze ruimte.',
  'Messages': 'Berichten',
  'Window or door open while the room heats': 'Raam of deur open terwijl de ruimte verwarmt',
  'Room stays cold (more than 1 °C below its target for over an hour)': 'Ruimte blijft koud (meer dan 1 °C onder de gewenste temperatuur, langer dan een uur)',
  'Temperature sensor silent for 30 minutes, or another device for 24 hours': 'Temperatuursensor 30 minuten stil, of een ander apparaat 24 uur',
  'Battery low of a thermometer, valve, window or door contact or setting device': 'Batterij bijna leeg van een thermometer, kraan, raam- of deurcontact of instelapparaat',
  'window open': 'raam open',
  'too cold': 'te koud',
  'sensor silent': 'sensor stil',
  'battery low': 'batterij bijna leeg',
  'Resets at {time} to {value}': 'Om {time} terug naar {value}',
  'At {time} to {value}': 'Om {time} naar {value}',
  'Room': 'Ruimte',
  'No rooms yet. Add your first room.': 'Nog geen ruimtes. Voeg je eerste ruimte toe.',
  '1 room': '1 ruimte',
  '{n} rooms': '{n} ruimtes',
  '{temperature} now': 'nu {temperature}',
  '1 source': '1 bron',
  '{n} sources': '{n} bronnen',
  'setting device {name}': 'instelapparaat {name}',
  'No week program': 'Geen weekprogramma',
  'Reset times': 'Terugzetmomenten',
  'Windows: {n}': 'Ramen: {n}',
  'doors: {n}': 'deuren: {n}',
  '1 valve': '1 kraan',
  '{n} valves': '{n} kranen',
  'No radiator valves': 'Geen radiatorkranen',
  'Follows the house': 'Volgt het huis',
  'The first one with a fresh value is used; the others are backups.': 'De eerste met een actuele waarde wordt gebruikt; de andere zijn reserve.',
  'A thermostat or valve you set the room with.': 'Een thermostaat of kraan waarmee je de ruimte instelt.',
  'The target temperature, the temperature without a week program and the program stay within these limits.': 'De gewenste temperatuur, de temperatuur zonder weekprogramma en het programma blijven binnen deze grenzen.',
  'Minimum temperature': 'Minimumtemperatuur',
  'Maximum temperature': 'Maximumtemperatuur',
  'The week planner is not loaded on this page.': 'De weekplanner is op deze pagina niet geladen.',
  'Leave without saving the week program?': 'Weggaan zonder het weekprogramma op te slaan?',
  'What you changed in the week program of {name} is lost.': 'Wat je in het weekprogramma van {name} hebt gewijzigd, gaat verloren.',
  'Leave': 'Weggaan',
  'Choose at most eight different sensors.': 'Kies hoogstens acht verschillende sensoren.',
  'Choose window, door or opening sensors only.': 'Kies alleen raam-, deur- of openingssensoren.',
  'A sensor is a window or a door, not both: choose it in one of the two fields.': 'Een sensor is een raam of een deur, niet allebei: kies hem in een van de twee velden.',
  'The pause delay lies between 0 and 30 minutes.': 'De pauzevertraging ligt tussen 0 en 30 minuten.',
  'This valve is already used (here or in another room).': 'Deze kraan is al in gebruik (hier of in een andere ruimte).',
  'Choose the valve\'s model.': 'Kies het model van de kraan.',
  'The E32 drives at most 16 radiator valves, 24 with the BLU Gateway (E32 1.1).': 'De E32 stuurt hoogstens 16 radiatorkranen aan, 24 met de BLU Gateway (E32 1.1).',
  'Choose a radiator valve from the list (not an OpenThermostat thermostat or this room\'s temperature source).': 'Kies een radiatorkraan uit de lijst (geen OpenThermostat-thermostaat of temperatuurbron van deze ruimte).',
  'A room has at most 8 radiator valves, and at most 4 that are not on the BLU Gateway.': 'Een ruimte heeft hoogstens 8 radiatorkranen, en hoogstens 4 die niet aan de BLU Gateway hangen.',
  'The E32 did not accept the radiator valves ({error}).': 'De E32 heeft de radiatorkranen niet aangenomen ({error}).',
  'Choose a temperature between {away_range}, or leave it empty for the house away temperature.': 'Kies een temperatuur tussen {away_range}, of laat het veld leeg voor de afwezigheidstemperatuur van het huis.',
  'Choose a person, group, zone or switch that exists.': 'Kies een bestaande persoon, groep, zone of schakelaar.',
  'Choose at least one message, or switch notifications off.': 'Kies minstens één bericht, of zet de meldingen uit.'}};
// The sentence of each code; Configure's own (strings.json options.error), the new parts' as ROOM-BACKEND sends them.
const ERRORS = {
 e32_name_invalid: 'Give the room a name of up to 40 letters (fewer with accents or emoji).',
 e32_source_wrong_domain: '{source} cannot be used here. Choose a thermostat or a temperature sensor; for the setting device a thermostat, radiator valve or number.',
 e32_source_invalid_id: '{source} cannot be used: its name in Home Assistant is longer than 80 characters.',
 e32_source_not_found: '{source} does not exist in Home Assistant.',
 e32_source_no_temperature: '{source} reports no current temperature. Choose a thermostat that measures the room, or a temperature sensor.',
 e32_source_not_celsius: '{source} does not report a temperature (°C or °F). Choose a temperature sensor.',
 e32_sources_count: 'Choose 1 to 4 temperature sources.',
 e32_rejected_sources: 'Choose 1 to 4 temperature sources.',
 e32_rejected_duplicate_source: 'A source is in the list twice.',
 e32_rejected_duplicate_room: 'Another room has this name.',
 e32_rejected_setpoint: 'The E32 cannot use this setting device. Choose another one.',
 e32_limits_invalid: 'Use limits between {range} with the minimum not above the maximum, and a temperature without a week program within them.',
 e32_program_outside_limits: 'A temperature of the week program is outside the room\'s temperature limits.',
 e32_valve_keep_open_loop: 'A floor loop valve cannot be kept open as the water\'s path: choose it in one of the two lists only.',
 controller_room_plan_update_required: 'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again. Nothing has been changed.',
 notification_invalid: 'Something in the form was not valid. Try again.',
 e32_resets_invalid: 'Reset time {line}: choose a time, at least one day and a temperature in whole or half degrees.',
 e32_resets_outside_limits: 'Reset time {line}: the temperature is outside the room\'s temperature limits.',
 e32_resets_same_moment: 'Reset time {line}: another reset time is already set for that day and time.',
 e32_resets_too_many: 'At most four reset times per room.',
 e32_rejected_resets: 'The E32 did not accept the reset times ({error}). Check the days, the times and the temperatures.',
 e32_inactive_until_invalid: 'Choose a moment in the future (before 2100) for “Off until”, or leave it empty.',
 e32_room_limit: 'The E32 already has 8 rooms. Remove a room first.',
 e32_room_missing: 'This room is no longer on the E32.',
 e32_plan_changed: 'The rooms were changed on the E32 twice while saving. Nothing was saved; try again.',
 e32_plan_too_large: 'The rooms no longer fit on the E32 (4 KB). Use shorter names, fewer sources or fewer switch times. Nothing was saved.',
 e32_storage_full: 'The E32 has no storage space left for its rooms. Remove a room you no longer use, or a few switch times, and save again. Nothing was saved.',
 e32_unconfirmed: 'The E32 could not confirm the change. Reload the page to see what is saved.',
 e32_unreachable: 'The E32 could not be reached ({error}). Nothing was saved.',
 e32_plan_invalid: 'The E32 sent rooms this version cannot read. Update the E32 firmware and the integration together.',
 e32_password_changed: 'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.',
 e32_rejected: 'The E32 did not accept the room ({error}). Nothing was saved.',
 e32_rejected_schedule: 'The E32 did not accept the week program. Check it in the week planner.',
 contacts_invalid: 'Choose at most eight different sensors.',
 not_contact_sensor: 'Choose window, door or opening sensors only.',
 contact_window_and_door: 'A sensor is a window or a door, not both: choose it in one of the two fields.',
 contact_delay_invalid: 'The pause delay lies between 0 and 30 minutes.',
 e32_valve_duplicate: 'This valve is already used (here or in another room).',
 e32_valve_model_missing: 'Choose the valve\'s model.',
 e32_valve_limit: 'The E32 drives at most 16 radiator valves, 24 with the BLU Gateway (E32 1.1).',
 e32_valve_entity_invalid: 'Choose a radiator valve from the list (not an OpenThermostat thermostat or this room\'s temperature source).',
 e32_valve_room_limit: 'A room has at most 8 radiator valves, and at most 4 that are not on the BLU Gateway.',
 e32_valves_rejected: 'The E32 did not accept the radiator valves ({error}).',
 e32_away_invalid: 'Choose a temperature between {away_range}, or leave it empty for the house away temperature.',
 presence_entity_invalid: 'Choose a person, group, zone or switch that exists.',
 notification_kinds_needed: 'Choose at least one message, or switch notifications off.',
 // 1.4.2: one role per valve (HA-SETDEV's check, on the field setpoint_entity), the recipients and the advice button.
 device_two_roles: 'A device can be the room\'s setting device or a radiator valve the E32 drives, not both. Choose one.',
 notification_person_invalid: 'Choose one of the people in the list.',
 advice_changed: 'The advice changed in the meantime. Reload the page.',
 advice_unavailable: 'There is no advice to use for this room right now. Reload the page.'};

const NEW = 'new-room';
// A room's state: its word, the label's tone (orange heats, amber heats along, grey off) and its one-line explanation
// (Configure's sentence, split per state, word for word).
const STATES = {active: ['On', 'heat', 'The room can ask for heat.', 'fire'],
 follow: ['Heat along only', 'along', 'The room keeps its target and its radiator valves open for it, but it never asks for heat; it warms while the boiler runs for other rooms.', 'thermometer'],
 inactive: ['Off', 'rest', 'The room asks for no heat.', 'close']};
// "Off until 14:00, then on again" / "then heating along again" (CONTRACT-1.4.2 §3, the room card's words): what the room
// returns to (the model's ``after``, 1.4.2 P10).
const OFF_UNTIL = {active: 'Off until {moment}, then on again', follow: 'Off until {moment}, then heating along again'};
const offUntil = (kit, hass, t, moment, after) => t(OFF_UNTIL[after] || OFF_UNTIL.active, {moment: kit.time.moment(hass, moment)});
// What a room that is Off returns to as the screen shows it: the stored one while it is Off, else the state it is
// switched off from (the E32 remembers Heat along only).
const afterOf = (model, values) => (model.state === 'inactive' ? model.after || 'active' : values.state === 'inactive' && model.state === 'follow' ? 'follow' : 'active');
const EMITTERS = {radiator: ['Radiators', 'radiator'], floor: ['Floor heating', 'floor']};
const WARM_UP = {house: 'As the house', on: 'On', off: 'Off'};
// The valve control as the glossary says it (radiator valve: driven by temperature, or by position).
// How a valve is driven (radiator_valves.list[].driven), in the glossary's words (1.4.1 ROOM-BACKEND).
const DRIVEN = {position: 'Driven by position', temperature: 'Driven by temperature; the position cannot be read', home_assistant: 'Through Home Assistant'};
const KINDS = {window: 'Window or door open while the room heats', cold: 'Room stays cold (more than 1 °C below its target for over an hour)',
 sensor: 'Temperature sensor silent for 30 minutes, or another device for 24 hours',
 battery: 'Battery low of a thermometer, valve, window or door contact or setting device'};
const KIND_SHORT = {window: 'window open', cold: 'too cold', sensor: 'sensor silent', battery: 'battery low'};
// The next reset time on the room card's words (room-status-card.js RESET, word for word).
const RESET = ['Resets at {time} to {value}', 'At {time} to {value}'];
const SOURCE_UNITS = ['°C', '°F', 'K'];
const REASON = 'component.open_thermostat.entity.sensor.room_reason.state_attributes.';
// The sections of a room's screen, in the plan's order (HA-INSTELPANEEL-FASE2.nl.md 3.1): [key, title, icon].
const FOLDS = [['general', 'General', 'thermostat'], ['temperature', 'Temperature', 'thermometer'], ['week', 'Week program', 'calendar'],
 ['contacts', 'Windows and doors', 'window'], ['valves', 'Radiator valves', 'radiator'], ['persons', 'Persons', 'account'],
 ['notifications', 'Notifications for this room', 'bell'], ['limits', 'Temperature limits', 'limits']];
// The values of a room's screen (save keys, CONTRACT-1.4.1 §1); the planner saves the program, reset times and Smart warm-up.
const PLAIN = ['name', 'state', 'emitter', 'sources', 'setpoint_entity', 'fallback_temperature', 'inactive_until', 'standard_program'];

/* ---- small helpers ---- */
const copy = v => JSON.parse(JSON.stringify(v));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const num = v => (typeof v === 'number' && Number.isFinite(v) ? v : typeof v === 'string' && v.trim() !== '' && Number.isFinite(Number(v)) ? Number(v) : null);
// A value the E32 keeps in °C (a reset value, what was written to the setting device) in the house's unit (model.unit).
const inUnit = (celsius, unit) => (unit === '°F' ? Math.round((celsius * 9 / 5 + 32) * 10) / 10 : celsius);
// The age of a reading in words: just now, 4 min ago, 2 h ago.
const age = (st, t) => {
 const at = Date.parse(st?.last_reported || st?.last_updated || '');
 if (Number.isNaN(at)) return '';
 const minutes = Math.floor((Date.now() - at) / 60000);
 return minutes < 1 ? t('just now') : minutes < 120 ? t('{n} min ago', {n: minutes}) : t('{n} h ago', {n: Math.floor(minutes / 60)});
};
const nameOf = (hass, eid, choices) => choices?.find(c => c.entity_id === eid)?.name || hass?.states?.[eid]?.attributes?.friendly_name || eid;
const names = list => Object.fromEntries((list || []).map(c => [c.entity_id, c.name]));
// Days as the week planner writes them: Mon–Fri, Sat, Sun; Every day (the kit's day names in Home Assistant's language).
function dayText(days, kit, hass, t) {
 const short = kit.time.weekdays(hass), sorted = [...new Set(days)].sort((a, b) => a - b);
 if (sorted.length === 7) return t('Every day');
 const runs = [];
 for (const d of sorted) { const last = runs[runs.length - 1]; if (last && last[1] === d - 1) last[1] = d; else runs.push([d, d]); }
 return runs.map(([a, b]) => (a === b ? short[a] : b === a + 1 ? `${short[a]}, ${short[b]}` : `${short[a]}–${short[b]}`)).join(', ');
}
// The room's Reason sensor: on the room thermostat's device, the sensor with a sentence (room_overview.py).
const reasonCache = new WeakMap();
function reasonOf(hass, room) {
 if (room.entities?.reason) return room.entities.reason;
 const all = hass?.entities, climate = room.entities?.climate;
 if (!all || !climate) return null;
 let found = reasonCache.get(all);
 if (!found) reasonCache.set(all, found = new Map());
 if (!found.has(climate)) {
  const device = all[climate]?.device_id;
  found.set(climate, device ? Object.values(all).find(e => e.device_id === device && e.entity_id.startsWith('sensor.') && hass.states?.[e.entity_id]?.attributes?.line !== undefined)?.entity_id || null : null);
 }
 return found.get(climate);
}
// What the room does now, in the integration's own words (Home Assistant translates the Reason sensor's sentence).
function doing(kit, hass, st) {
 if (!st) return '';
 const a = st.attributes || {}, v = a.values && typeof a.values === 'object' ? a.values : {};
 const fixed = x => (num(x) == null ? '–' : kit.number(num(x), hass, 1, 1));
 const values = {contact: typeof v.contact === 'string' ? v.contact : '', since: kit.time.moment(hass, v.since), time: kit.time.moment(hass, v.time),
  until: kit.time.moment(hass, v.until), temperature: fixed(v.temperature), target: num(v.target) == null ? '–' : kit.number(num(v.target), hass)};
 let line = '';
 try { line = typeof a.line === 'string' ? hass?.localize?.(REASON + 'line.state.' + a.line, values) || '' : ''; } catch (e) { line = ''; }
 if (line) return line;
 try { const text = hass?.formatEntityState?.(st); return text && text !== st.state ? text : ''; } catch (e) { return ''; }
}
// "Resets at 22:00 to 14 °C" / "At 23:00 to Heat along only": the room thermostat's next reset time, as the room card says it.
function resetLine(kit, hass, climate, t, unit = '°C') {
 const a = hass?.states?.[climate]?.attributes || {}, v = a.next_reset_value, time = kit.time.moment(hass, a.next_reset);
 if (!time) return '';
 if (STATES[v]) return t(RESET[1], {time, value: t(STATES[v][0])});
 const degree = num(v);
 return degree == null ? '' : t(RESET[0], {time, value: kit.degrees(inUnit(degree, unit), unit, hass)});
}
const measured = (hass, entities) => {
 const c = hass?.states?.[entities?.climate], s = hass?.states?.[entities?.temperature];
 return num(c?.attributes?.current_temperature) ?? num(s?.state);
};
// A room as a card on the list, the glance and the side list: temperature large, target, state label, what it does now.
function card(ctx, room, {compact, current} = {}) {
 const {kit, t} = ctx, route = '#room/' + encodeURIComponent(room.id), wrap = kit.h('div', {class: 'rr-card', 'data-live': '', 'data-room': room.id});
 wrap._live = hass => {
  const now = measured(hass, room.entities), target = num(hass?.states?.[room.entities?.climate]?.attributes?.temperature), unit = ctx.model?.unit || '°C';
  const [word, tone, , icon] = STATES[room.state] || STATES.active;
  const until = room.state === 'inactive' && room.inactive_until ? offUntil(kit, hass, t, room.inactive_until, room.after) : '';
  const lines = compact ? [] : [doing(kit, hass, hass?.states?.[reasonOf(hass, room)]) || (now == null ? t('No temperature yet') : ''), until, resetLine(kit, hass, room.entities?.climate, t, unit)];
  wrap.replaceChildren(kit.roomCard({name: room.name, compact, current, route, emitter: EMITTERS[room.emitter]?.[1] || 'radiator',
   onClick: e => { e.preventDefault(); ctx.navigate(route); }, temperature: now == null ? null : kit.number(now, hass, 1, 1),
   unit, target: target != null && room.state !== 'inactive' ? '→ ' + kit.degrees(target, unit, hass) : null,
   state: {text: t(word), tone, icon}, lines}));
 };
 wrap._live(ctx.hass);
 return wrap;
}

/* ---- the fields of this section (the kit's field contract: {el, setError, setMark, focus}) ---- */
const bleOf = (model, id) => (Array.isArray(model.ble) ? model.ble.find(s => s.id === id) : model.ble?.[id] != null ? {id, name: model.ble[id]} : null);
// A source by the name you know it by: the E32's Bluetooth sensor by its name, a Home Assistant entity by its name.
const sourceName = (source, model, hass) => (source.type === 'ble' ? bleOf(model, source.id)?.name || source.id
 : hass?.states?.[source.id]?.attributes?.friendly_name || source.id);
// What a source is, in words (owner 10 Nov, "dat is echt onduidelijk"): "Bluetooth sensor on the E32 · A3:E8:DB" or
// "Home Assistant · BTHome · sensor.atc_a3e8db_temperature" (the integration from live.integrations).
const address = id => (/^[0-9a-f]{12}$/i.test(id) ? id.slice(6).toUpperCase().replace(/(..)(?=.)/g, '$1:') : id);
function sourceKind(source, model, hass, t) {
 if (source.type === 'ble') return [t('Bluetooth sensor on the E32'), address(source.id)];
 const platform = hass?.entities?.[source.id]?.platform;
 return ['Home Assistant', platform ? model.live?.integrations?.[platform] || platform : '', source.id];
}
function reading(kit, source, model, hass) {
 const eid = source.type === 'ble' ? bleOf(model, source.id)?.entity_id : source.id, st = eid && hass?.states?.[eid];
 if (!st) return ['', null];
 const value = eid.startsWith('climate.') ? num(st.attributes?.current_temperature) : num(st.state);
 return value == null ? ['', st] : [kit.degrees(value, eid.startsWith('climate.') ? model.unit : st.attributes?.unit_of_measurement || model.unit, hass), st];
}
// Sources keep the order the room form stores: the kind of the first one first (Bluetooth or Home Assistant).
const grouped = list => (list.length ? [...list.filter(s => s.type === list[0].type), ...list.filter(s => s.type !== list[0].type)] : list);
function sourcesField(ctx) {
 return o => {
  const {kit, t, model} = ctx, {h, fields, button, iconButton, shell, chip} = kit;
  let list = copy(o.value || []), adding = false;
  const body = h('div', {class: 'rr-list'}), api = shell('sources', o, body, false);
  const own = new Set(model.own || []), bleByEntity = new Map((model.ble || []).filter(s => s.entity_id).map(s => [s.entity_id, s]));
  const emit = () => o.onChange?.(copy(list));
  // HA-DEVICES (1.4.2): a Home Assistant source that is the same thermometer as a Bluetooth sensor paired on the E32.
  const twin = model.live?.e32_sensor_suggestion;
  const draw = focusAdd => {
   const items = list.flatMap((source, i) => {
    const name = sourceName(source, model, ctx.hass), kind = h('span', {class: 'pick-id rr-kind', text: sourceKind(source, model, ctx.hass, t).filter(Boolean).join(' · ')});
    const detail = h('span', {class: 'pick-id'});
    const el = h('div', {class: 'pick', 'data-source': `${source.type}:${source.id}`, 'data-live': ''},
     h('span', {class: 'pick-text'}, h('span', {class: 'pick-name'}, h('span', {text: name}), i === 0 && list.length > 1 ? chip(t('Used first'), 'accent') : null), kind, detail),
     o.disabled || i === 0 ? null : button(t('Use first'), () => { list = grouped([source, ...list.filter(x => x !== source)]); draw(); emit(); }, 'text small',
      {'aria-label': t('Use {name} first', {name}), 'data-first': ''}),
     o.disabled ? null : iconButton('close', t('Remove {name}', {name}), () => { list = list.filter(x => x !== source); draw(); emit(); }, {'data-remove': ''}));
    el._live = hass => {
     const [v, s] = reading(kit, source, model, hass);
     detail.textContent = [v || t('No reading'), v ? age(s, t) : ''].filter(Boolean).join(' · ');
    };
    el._live(ctx.hass);
    if (source.type !== 'ha' || !twin || twin.entity_id !== source.id || list.some(x => x.type === 'ble' && x.id === twin.address)) return [el];
    const swap = () => { list = list.map(x => (x === source ? {type: 'ble', id: twin.address} : x)); draw(); emit(); };
    return [el, h('div', {class: 'rr-twin', 'data-twin': source.id}, h('p', {class: 'help', text: t('The E32 measures this thermometer itself; choose it as the source, so it also works without Home Assistant.')}),
     o.disabled ? null : button(t('Use the E32\'s sensor'), swap, 'text small', {'data-use-twin': ''}))];
   });
   const parts = [...items];
   if (!list.length) parts.push(h('p', {class: 'help', text: t('No source yet: choose at least one.')}));
   if (!o.disabled && list.length >= (model.max_sources || 4)) parts.push(h('p', {class: 'help', text: t('At most four temperature sources per room.')}));
   else if (!o.disabled && adding) {
    const taken = new Set(list.map(s => (s.type === 'ble' ? bleOf(model, s.id)?.entity_id : s.id)));
    const picker = fields.entity({hass: ctx.hass, key: 'sources-add', placeholder: t('Search by name'), value: '', filter: (st, eid) => {
     if (taken.has(eid)) return false;
     if (bleByEntity.has(eid)) return true;
     if (own.has(eid)) return false;
     if (eid.startsWith('climate.')) return typeof st?.attributes?.current_temperature === 'number';
     return eid.startsWith('sensor.') && st?.attributes?.device_class === 'temperature' && SOURCE_UNITS.includes(st?.attributes?.unit_of_measurement);
    }, onChange: eid => {
     if (!eid) return;
     const ble = bleByEntity.get(eid);
     list = [...list, ble ? {type: 'ble', id: ble.id} : {type: 'ha', id: eid}];
     adding = false; draw(true); emit();
    }});
    parts.push(picker.el);
    queueMicrotask(() => picker.focus());
   } else if (!o.disabled) parts.push(button(t('Add a source'), () => { adding = true; draw(); }, 'outlined', {icon: 'plus', 'data-add-source': ''}));
   body.replaceChildren(...parts);
   if (focusAdd) body.querySelector('[data-add-source]')?.focus();
  };
  draw();
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}
// A value with the house's as default: [As the house (2 min) | Own] and a stepper for the own one.
function ownOrHouse(ctx, {key, label, house, value, unit, step, min, max, onChange, disabled, help}) {
 const {kit, t} = ctx, wrap = kit.h('div', {class: 'rr-own'});
 let own = value != null;
 const shownHouse = house == null ? '' : kit.degrees(house, unit, ctx.hass);
 const seg = kit.fields.segmented({key: key + ':own', hass: ctx.hass, label, disabled, value: own ? 'own' : 'house', help,
  options: [{value: 'house', label: shownHouse ? t('As the house ({value})', {value: shownHouse}) : t('As the house'), help: t('The house value applies; you change it under House.')},
   {value: 'own', label: t('Own value'), help: t('This room uses its own value.')}],
  onChange: v => { own = v === 'own'; draw(); onChange(own ? (stepper?.value ?? house ?? min) : null); }});
 let stepper = null;
 const draw = () => {
  stepper = own ? kit.fields.stepper({key, hass: ctx.hass, value: value ?? house ?? min, unit, step, min, max, disabled, label: null,
   onChange: v => { value = v; onChange(v); }}) : null;
  wrap.replaceChildren(seg.el, ...(stepper ? [stepper.el] : []));
 };
 draw();
 return wrap;
}
function contactsField(ctx) {
 return o => {
  const {kit, t, model} = ctx, m = model.contacts, minutes = s => (s == null ? null : s / 60);
  const value = copy(o.value), body = kit.h('div', {class: 'rr-group'}), api = kit.shell('contacts', o, body, false);
  const ids = (m.choices || []).map(c => c.entity_id), label = names(m.choices);
  const emit = () => o.onChange?.(copy(value));
  const picker = (kind, other, title) => kit.fields.entity({hass: ctx.hass, key: 'contacts:' + kind, label: title, multiple: true, disabled: o.disabled,
   choices: ids, names: label, value: value[kind], placeholder: t('Search by name'), filter: (st, eid) => !value[other].includes(eid),
   onChange: v => { value[kind] = v; emit(); }});
  body.append(picker('windows', 'doors', t('Window contacts')).el,
   ownOrHouse(ctx, {key: 'contacts:window_delay_s', label: t('Pause after (windows)'), house: minutes(m.house?.window_delay_s), value: minutes(value.window_delay_s),
    unit: 'min', step: 0.5, min: 0, max: 30, disabled: o.disabled, onChange: v => { value.window_delay_s = v == null ? null : Math.round(v * 60); emit(); }}),
   picker('doors', 'windows', t('Door contacts')).el,
   ownOrHouse(ctx, {key: 'contacts:door_delay_s', label: t('Pause after (doors)'), house: minutes(m.house?.door_delay_s), value: minutes(value.door_delay_s),
    unit: 'min', step: 0.5, min: 0, max: 30, disabled: o.disabled, onChange: v => { value.door_delay_s = v == null ? null : Math.round(v * 60); emit(); }}));
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}
// A valve's battery and last report: its battery entity as the backend names it (battery_entity_id, 1.4.2 P21: no
// registry scan here), a percentage or a "low" binary sensor, and the valve's own state (hass.states).
function valveStatus(kit, hass, eid, t, batteryId) {
 const st = hass?.states?.[eid], battery = batteryId ? hass?.states?.[batteryId] : null, level = num(battery?.state);
 const said = level != null ? t('Battery {level}', {level: `${kit.number(level, hass, 0)} %`}) : battery?.state === 'on' ? t('Battery low') : '';
 return [said, st ? t('Last report {age}', {age: age(st, t)}) : t('Not found in Home Assistant')].filter(Boolean).join(' · ');
}
// A valve as the save takes it (S-ROOM-BACKEND: {entity_id, model}, a kept valve {id}, a BLU Gateway valve {id, role, keep_open}).
const valveSave = v => (v.kind === 'kept' ? {id: v.id} : v.kind === 'gateway' ? {id: v.id, role: v.role ?? null, keep_open: !!v.keep_open}
 : {entity_id: v.entity_id, model: v.model ?? null});
const valveKey = v => v.entity_id || v.id;
function valvesField(ctx) {
 return o => {
  const {kit, t, model} = ctx, m = model.radiator_valves, {h} = kit;
  const value = copy(o.value), body = h('div', {class: 'rr-group'}), api = kit.shell('radiator_valves', o, body, false);
  // What each valve is: the model's own rows, then what was added here (a Home Assistant valve or a BLU Gateway valve).
  const known = new Map((m.list || []).map(v => [valveKey(v), v]));
  for (const c of m.choices || []) if (!known.has(c.entity_id)) known.set(c.entity_id, {entity_id: c.entity_id, name: c.name, kind: 'home_assistant', choose_model: false});
  for (const g of m.gateway_choices || []) if (!known.has(g.id)) known.set(g.id, {id: g.id, name: g.name, kind: 'gateway'});
  let adding = null;
  const emit = () => o.onChange?.(copy(value));
  const draw = focusAdd => {
   const shownIds = new Set(value.list.map(valveKey));
   const rows = value.list.map((save, i) => {
    const v = known.get(valveKey(save)) || {name: valveKey(save)}, name = v.name || valveKey(save), status = h('span', {class: 'pick-id'});
    // HA-DEVICES (HC-11): a valve Home Assistant drives that reports no opening regulates itself to the target.
    const selfRegulating = (model.live?.self_regulating || []).some(x => x === v.id || x === v.entity_id || x === v.name);
    const word = [v.kind === 'kept' ? t('Kept on the E32') : v.kind === 'gateway' ? t('On the BLU Gateway') : '',
     selfRegulating ? t('Regulates itself to the target; the position cannot be read') : v.driven ? t(DRIVEN[v.driven] || v.driven) : '']
     .filter(Boolean).join(' · ');
    const select = v.choose_model ? h('select', {class: 'input rr-model', 'aria-label': t('Model of {name}', {name}), disabled: o.disabled, 'data-fk': `radiator_valves:${i}:model`},
     ...(m.models || []).map(x => h('option', {value: x.key, text: x.name}))) : null;
    if (select) { select.value = save.model || v.model || ''; select.addEventListener('change', () => { save.model = select.value || null; emit(); }); }
    const el = h('div', {class: 'pick rr-valve', 'data-valve': valveKey(save), 'data-live': ''},
     h('span', {class: 'pick-text'}, h('span', {class: 'pick-name', text: name}), word ? h('span', {class: 'pick-id', text: word}) : null, save.entity_id ? status : null, select),
     o.disabled ? null : kit.iconButton('close', t('Remove {name}', {name}), () => { value.list.splice(i, 1); draw(true); emit(); }, {'data-remove': ''}));
    el._live = hass => { if (save.entity_id) status.textContent = valveStatus(kit, hass, save.entity_id, t, v.battery_entity_id); };
    el._live(ctx.hass);
    return el;
   });
   const parts = rows.length ? rows : [h('p', {class: 'help', text: t('No radiator valves in this room.')})];
   const own = value.list.filter(v => !('role' in v)).length, all = value.list.length;
   const roomForOwn = own < (m.max || 4) && all < (m.max_with_gateway || m.max || 4), roomForGateway = all < (m.max_with_gateway || m.max || 4);
   const gateway = (m.gateway_choices || []).filter(g => !shownIds.has(g.id));
   if (!o.disabled && adding === 'ha') {
    const picker = kit.fields.entity({hass: ctx.hass, key: 'radiator_valves-add', placeholder: t('Search by name'), value: '', choices: (m.choices || []).map(c => c.entity_id),
     names: Object.fromEntries((m.choices || []).map(c => [c.entity_id, c.name])), filter: (st, eid) => !shownIds.has(eid),
     onChange: eid => { if (!eid) return; value.list.push({entity_id: eid, model: null}); adding = null; draw(true); emit(); }});
    parts.push(picker.el);
    queueMicrotask(() => picker.focus());
   } else if (!o.disabled && adding === 'gateway') {
    const select = h('select', {class: 'input', 'aria-label': t('Add from the BLU Gateway'), 'data-fk': 'radiator_valves-gateway'},
     h('option', {value: '', text: t('Choose a valve')}), ...gateway.map(g => h('option', {value: g.id, text: g.name})));
    select.addEventListener('change', () => { if (!select.value) return; value.list.push({id: select.value, role: null, keep_open: false}); adding = null; draw(true); emit(); });
    parts.push(select);
    queueMicrotask(() => select.focus());
   } else if (!o.disabled) {
    const buttons = [];
    if (roomForOwn && (m.choices || []).length) buttons.push(kit.button(t('Add a valve'), () => { adding = 'ha'; draw(); }, 'outlined', {icon: 'plus', 'data-add-valve': ''}));
    if (roomForGateway && gateway.length) buttons.push(kit.button(t('Add from the BLU Gateway'), () => { adding = 'gateway'; draw(); }, 'text', {icon: 'plus', 'data-add-gateway': ''}));
    if (!roomForOwn && !roomForGateway) parts.push(h('p', {class: 'help', text: t('At most {max} radiator valves per room.', {max: m.max_with_gateway || m.max || 4})}));
    if (buttons.length) parts.push(h('div', {class: 'rr-buttons'}, ...buttons));
   }
   if (value.control !== null && value.control !== undefined) parts.push(kit.fields.toggle({key: 'radiator_valves:control', hass: ctx.hass, label: t('Valve control'),
    value: value.control, disabled: o.disabled, help: t('On: these valves follow the room (only while the E32 controls the boiler itself). Off: the valves keep their own settings and nothing is sent to them.'),
    onChange: v => { value.control = v; emit(); }}).el);
   body.replaceChildren(...parts);
   if (focusAdd) (body.querySelector('[data-add-valve], [data-add-gateway]') || body.querySelector('select'))?.focus();
  };
  draw();
  api.target = () => body.querySelector('select, input, button');
  api.describe();
  return api;
 };
}
function personsField(ctx) {
 return o => {
  const {kit, t, model} = ctx, m = model.persons, value = copy(o.value), body = kit.h('div', {class: 'rr-group'});
  const api = kit.shell('persons', o, body, false), emit = () => o.onChange?.(copy(value)), unit = model.unit || '°C';
  const range = m.away_range || {minimum: unit === '°F' ? 41 : 5, maximum: unit === '°F' ? 77 : 25};
  body.append(kit.fields.entity({hass: ctx.hass, key: 'persons:entity_ids', label: t('Persons of this room'), multiple: true, disabled: o.disabled, showIds: false,
   choices: (m.choices || []).map(c => c.entity_id), names: names(m.choices), value: value.entity_ids, placeholder: t('Search by name'),
   help: t('Empty: the room follows the house.'), onChange: v => { value.entity_ids = v; emit(); }}).el);
  if (model.features?.room_away !== false) body.append(ownOrHouse(ctx, {key: 'persons:away_temperature', label: t('Temperature when this room\'s people are away'),
   house: m.house_away_temperature, value: value.away_temperature, unit, step: unit === '°F' ? 1 : 0.5, min: range.minimum, max: range.maximum,
   disabled: o.disabled, onChange: v => { value.away_temperature = v; emit(); }}));
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}
// Who gets a room's messages in one sentence (HA-NOTIFY's recipients_line): the backend's while you did not change the
// choice, else the same words for what you chose (names joined as the backend joins them).
function recipientsLine(ctx, chosen) {
 const {t, model} = ctx, people = model.live?.notifications?.people || [], room = model.name || '';
 const stored = model.live?.notifications?.recipients_line;
 if (stored && same(chosen, model.notifications.recipients ?? null)) return stored[ctx.kit.langOf(ctx.hass)] || stored.en || '';
 if (chosen == null) return t('Messages about {room} go to everyone with a phone.', {room});
 if (!chosen.length) return t('Messages about {room} go to nobody; they show in Home Assistant only.', {room});
 const names = chosen.map(id => people.find(p => p.person === id)?.name || id);
 return t('Messages about {room} go to {people}.', {room, people: names.length === 1 ? names[0] : names.slice(0, -1).join(', ') + t(' and ') + names.at(-1)});
}
function notificationsField(ctx) {
 return o => {
  const {kit, t, model} = ctx, m = model.notifications, {h} = kit, value = copy(o.value), body = h('div', {class: 'rr-group'});
  const api = kit.shell('notifications', o, body, false), emit = () => o.onChange?.(copy(value));
  const people = model.live?.notifications?.people || [];
  const draw = () => {
   const toggle = kit.fields.toggle({key: 'notifications:on', hass: ctx.hass, label: t('Notify about this room'), value: value.on, disabled: o.disabled,
    help: value.on ? '' : t('Off: no messages about this room.'), onChange: v => { value.on = v; if (v && !value.kinds.length) value.kinds = [...(m.kind_choices || [])]; draw(); emit(); }});
   const kinds = value.on ? h('div', {class: 'choices', role: 'group', 'aria-label': t('Messages')}, ...(m.kind_choices || []).map(k => {
    const box = h('input', {type: 'checkbox', disabled: o.disabled, 'data-fk': 'notifications:kind:' + k});
    box.checked = value.kinds.includes(k);
    box.addEventListener('change', () => { value.kinds = (m.kind_choices || []).filter(x => (x === k ? box.checked : value.kinds.includes(x))); emit(); });
    return h('label', {class: 'choice'}, box, h('span', {class: 'choice-text'}, h('span', {class: 'choice-label', text: KINDS[k] ? t(KINDS[k]) : k})));
   })) : null;
   // 1.4.2 (plan 3.4): who gets them, the room's own recipients apart from its persons for presence.
   const who = value.on && 'recipients' in value ? recipientsPicker(ctx, o, value, people, () => { draw(); emit(); }) : [];
   body.replaceChildren(toggle.el, ...(kinds ? [kinds] : []), ...who);
  };
  draw();
  api.target = () => body.querySelector('input');
  api.describe();
  return api;
 };
}

// [Everyone with a phone | Chosen people], the people as chips (fields.entity with multiple), and the line who gets them.
function recipientsPicker(ctx, o, value, people, changed) {
 const {kit, t} = ctx, chosen = value.recipients;
 const seg = kit.fields.segmented({key: 'notifications:who', hass: ctx.hass, label: t('Who gets them'), disabled: o.disabled, value: chosen == null ? 'everyone' : 'chosen',
  options: [{value: 'everyone', label: t('Everyone with a phone')}, {value: 'chosen', label: t('Chosen people')}],
  onChange: v => { value.recipients = v === 'everyone' ? null : people.filter(p => p.chosen).map(p => p.person); changed(); }});
 const names = Object.fromEntries(people.map(p => [p.person, p.found === false ? t('{name} (not found)', {name: p.name}) : p.name]));
 const picker = chosen == null ? null : kit.fields.entity({hass: ctx.hass, key: 'notifications:recipients', label: t('Recipients'), multiple: true, showIds: false,
  disabled: o.disabled, choices: people.map(p => p.person), names, value: chosen, placeholder: t('Search by name'),
  onChange: v => { value.recipients = v; line.textContent = recipientsLine(ctx, v); o.onChange?.(copy(value)); }});
 const line = kit.h('p', {class: 'help rr-recipients', 'data-recipients': '', text: recipientsLine(ctx, chosen)});
 return [seg.el, ...(picker ? [picker.el] : []), line];
}

/* ---- the screens ---- */
function roomList(ctx) {
 const {kit, t, model} = ctx, {h} = kit;
 const add = !ctx.readOnly && model.can_add ? kit.button(t('Room'), () => ctx.navigate('#rooms/' + NEW), 'filled', {icon: 'plus', 'aria-label': t('Add room'), 'data-add-room': ''}) : null;
 if (!model.rooms.length) return h('div', {class: 'rr-page ot-card'}, kit.empty({icon: 'thermostat', text: t('No rooms yet. Add your first room.'), action: add}));
 return h('div', {class: 'rr-page'},
  h('div', {class: 'rr-toolbar'}, h('p', {class: 'help', text: model.rooms.length === 1 ? t('1 room') : t('{n} rooms', {n: model.rooms.length})}), add),
  h('div', {class: 'rr-cards'}, ...model.rooms.map(room => card(ctx, room))),
  !model.can_add && !ctx.readOnly ? h('p', {class: 'help rr-full', text: t('The E32 holds at most {max} rooms. Remove a room first.', {max: model.max_rooms})}) : null);
}
// The open sections of each room, kept per viewer (and in memory when the browser keeps nothing).
const opened = new Map();
function summaries(ctx) {
 const {kit, t, model: m, values: v, hass} = ctx, unit = m.unit || '°C', out = {};
 const state = v.state === 'inactive' && v.inactive_until ? offUntil(kit, hass, t, v.inactive_until, afterOf(m, v)) : t(STATES[v.state]?.[0] || 'On');
 out.general = `${state} · ${t(EMITTERS[v.emitter]?.[0] || 'Radiators')}`;
 const now = measured(hass, m.entities);
 out.temperature = [now == null ? t('No temperature yet') : t('{temperature} now', {temperature: kit.degrees(now, unit, hass)}),
  (v.sources || []).length === 1 ? t('1 source') : t('{n} sources', {n: (v.sources || []).length}),
  v.setpoint_entity ? t('setting device {name}', {name: nameOf(hass, v.setpoint_entity)}) : ''].filter(Boolean).join(' · ');
 // The week program, its reset times and Smart warm-up are read values (live, 1.4.2 P1): the planner saves them.
 const live = m.live || {}, groups = live.program || [];
 out.week = [groups.length ? groups.slice(0, 2).map(g => `${dayText(g.days, kit, hass, t)} ${g.points.map(([at]) => kit.time.format(hass, at)).join(', ')}`).join(' · ')
  : t('No week program'), (live.resets || []).length ? `${t('Reset times')}: ${live.resets.length}` : '',
  live.smart_warm_up ? `${t('Smart warm-up')}: ${t(WARM_UP[live.smart_warm_up] || 'As the house')}` : ''].filter(Boolean).join(' · ');
 const c = v.contacts;
 if (c) out.contacts = c.windows.length || c.doors.length ? [t('Windows: {n}', {n: c.windows.length}), t('doors: {n}', {n: c.doors.length})].join(' · ') : t('No window or door contacts');
 const rv = v.radiator_valves;
 if (rv) out.valves = rv.list.length ? [rv.list.length === 1 ? t('1 valve') : t('{n} valves', {n: rv.list.length}),
  rv.control === true || rv.control === false ? `${t('Valve control')}: ${t(rv.control ? 'On' : 'Off')}` : ''].filter(Boolean).join(' · ') : t('No radiator valves');
 else if (live.radiator_valves_error) out.valves = t('Could not be read');
 const p = v.persons;
 if (p) out.persons = p.entity_ids.length ? p.entity_ids.map(e => nameOf(hass, e, m.persons.choices)).join(', ') : t('Follows the house');
 const n = v.notifications;
 if (n) out.notifications = n.on ? [`${t('On')}: ${n.kinds.map(k => t(KIND_SHORT[k] || k)).join(', ')}`, !('recipients' in n) ? ''
  : n.recipients == null ? t('Everyone with a phone') : n.recipients.map(id => (live.notifications?.people || []).find(p => p.person === id)?.name || id).join(', ')]
  .filter(Boolean).join(' · ') : t('Off');
 if (v.minimum_temperature != null) out.limits = `${kit.number(v.minimum_temperature, hass)}–${kit.degrees(v.maximum_temperature, unit, hass)}`;
 return out;
}
function roomPage(ctx) {
 const {kit, t, model: m, values: v, lang} = ctx, {h} = kit, isNew = ctx.item === NEW, unit = m.unit || '°C';
 if (isNew && m.full) return h('div', {}, kit.notice(t('The E32 holds at most {max} rooms. Remove a room first.', {max: m.max_rooms}), 'warning'));
 const memory = kit.memory('room-folds:' + (m.id || NEW)), remembered = memory.get() || opened.get(m.id || NEW) || (isNew ? {general: true, temperature: true} : {});
 const keep = (key, on) => { remembered[key] = on; opened.set(m.id || NEW, remembered); memory.set(remembered); };
 const sum = summaries(ctx), made = {};
 const fold = (key, ...children) => {
  const [, title, icon] = FOLDS.find(f => f[0] === key);
  return made[key] = kit.fold({key, title: t(title), icon, summary: sum[key], open: !!remembered[key], onToggle: on => keep(key, on), data: {section: key}}, ...children);
 };
 // 1. General
 const until = ctx.field('moment', 'inactive_until', {label: t('Off until (optional)'), optional: true,
  help: t('The date and time the room heats again by itself. Empty: off until you turn it on.')});
 until.hidden = v.state !== 'inactive';
 const states = (m.states || ['active', 'inactive']).map(s => ({value: s, label: t(STATES[s][0]), help: t(STATES[s][2]), tone: STATES[s][1]}));
 // The temperature without a week program: on Heat along only it is "Heat along up to" in General, right under the state
 // (plan 3.3, one field, not two); otherwise in Temperature. It moves with the state you choose.
 const fixed = h('div', {class: 'rr-fixed', 'data-fixed': ''}), inGeneral = h('div', {class: 'rr-slot'}), inTemperature = h('div', {class: 'rr-slot'});
 const placeFixed = () => { const follow = v.state === 'follow'; fixed.replaceChildren(...fixedBlock(ctx, follow)); (follow ? inGeneral : inTemperature).append(fixed); };
 const hint = h('div', {class: 'rr-hint', 'data-hint': ''});
 const drawHint = () => hint.replaceChildren(...(valveHint(m, v) ? [kit.notice(t('With On, this valve regulates on its own sensor and often closes before the room is warm; consider valve control with a separate thermometer instead.'), 'info')] : []));
 const parts = [fold('general',
  ctx.field('text', 'name', {label: t('Room name'), maxlength: 40, required: true,
   more: t('The name you see in Home Assistant and on the E32. Up to 40 letters (fewer with accents or emoji); renaming keeps the room and its history.')}),
  ctx.field('segmented', 'state', {label: t('Heating'), options: states, onChange: s => { until.hidden = s !== 'inactive'; placeFixed(); drawHint(); }}),
  until, inGeneral,
  ctx.field('segmented', 'emitter', {label: t('Heating type'), options: Object.entries(EMITTERS).map(([value, [label, icon]]) => ({value, label: t(label), icon})),
   more: t('Radiators or floor heating. Floor heating warms up slowly and needs cooler water, so each type gets its own water temperature.')}))];
 // 2. Temperature
 parts.push(fold('temperature',
  ctx.field(sourcesField(ctx), 'sources', {label: t('Temperature sources'), help: t('The first one with a fresh value is used; the others are backups.'),
   more: t('The first one with a fresh value is used; the others are backups. With one source: if it fails, the room stops asking for heat after 30 minutes. A second source, for example a Bluetooth sensor, covers that.')}),
  ctx.field('entity', 'setpoint_entity', {label: t('Setting device (optional)'), domains: ['climate', 'input_number', 'number'], placeholder: t('Search by name'),
   filter: (st, eid) => !(m.own || []).includes(eid), help: t('A thermostat or valve you set the room with.'), onChange: drawHint,
   more: t('A thermostat or radiator valve (for example a tado or TV02), or a number with a target, to set the room with. Home Assistant keeps it at the room\'s temperature; turning it changes the room (until the next switch time with a week program, for good without one). Turn off the device\'s own schedule (manual mode), otherwise it changes the temperature by itself.')}),
  hint, isNew ? null : settingLine(ctx), inTemperature));
 placeFixed(); drawHint();
 // 3. Week program: the planner itself (WEEK-V2: the program, the reset times and Smart warm-up live in it).
 parts.push(fold('week', isNew ? ctx.field('toggle', 'standard_program', {label: t('Start with the standard week program'),
  more: t('“Workdays and weekend”: 20 °C by day, 18 °C while away on workdays, 16 °C at night. You change it afterwards in the week planner. Off: the room keeps its temperature without a week program.')})
  : planner(ctx)));
 // 4.–8. Windows and doors, radiator valves, persons, notifications, limits: each only where this firmware has it.
 if (!isNew && m.contacts) parts.push(fold('contacts', ctx.field(contactsField(ctx), 'contacts', {})));
 if (!isNew && m.radiator_valves) parts.push(fold('valves', ctx.field(valvesField(ctx), 'radiator_valves', {})));
 // P12: the valve record could not be read now: the block stays, says why and offers a new read (HA-DEVICES' key).
 else if (!isNew && m.features?.radiator_valves !== false && m.live?.radiator_valves_error) parts.push(fold('valves',
  kit.notice(t('The radiator valves could not be read ({error}). Reload.', {error: m.live.radiator_valves_error}), 'warning',
   kit.button(t('Reload'), () => ctx.reload(), 'text', {'data-reload-valves': ''}))));
 if (!isNew && m.persons) parts.push(fold('persons', ctx.field(personsField(ctx), 'persons', {})));
 if (!isNew && m.notifications) parts.push(fold('notifications', ctx.field(notificationsField(ctx), 'notifications', {})));
 if (v.minimum_temperature != null) {
  const range = {unit, step: unit === '°F' ? 1 : 0.5, min: m.limits?.lowest ?? (unit === '°F' ? 41 : 5), max: m.limits?.highest ?? (unit === '°F' ? 95 : 35)};
  parts.push(fold('limits', h('p', {class: 'help rr-why', text: t('The target temperature, the temperature without a week program and the program stay within these limits.')}),
   ctx.field('stepper', 'minimum_temperature', {label: t('Minimum temperature'), ...range}),
   ctx.field('stepper', 'maximum_temperature', {label: t('Maximum temperature'), ...range})));
 }
 // 9. Remove room, at the bottom, after the question.
 if (!isNew && !ctx.readOnly) parts.push(h('div', {class: 'rr-remove'}, kit.button(t('Remove room'), () => ctx.act({remove: true}, {
  title: t('Remove {name}?', {name: m.name}),
  text: t('The E32 forgets the room with its week program and reset times, and Home Assistant removes its devices. This cannot be undone.'),
  confirm: t('Remove room'), danger: true}), 'danger', {icon: 'close', 'data-remove-room': ''})));
 // The status line: what the room does now (the only line that moves).
 const status = h('div', {class: 'rr-status', 'data-live': ''});
 status._live = hass => {
  const text = doing(kit, hass, hass?.states?.[reasonOf(hass, m)]);
  const tone = STATES[m.state]?.[1] || 'rest';
  status.replaceChildren(...(text ? [kit.statusLine(text, tone)] : []));
 };
 if (!isNew) status._live(ctx.hass);
 const page = h('div', {class: 'rr-room'}, status, ...parts);
 // Every field change updates its section's summary line.
 page.addEventListener('input', () => queueMicrotask(() => { const s = summaries(ctx); for (const [k, el] of Object.entries(made)) el.setSummary?.(s[k]); }));
 page.addEventListener('click', () => queueMicrotask(() => { const s = summaries(ctx); for (const [k, el] of Object.entries(made)) el.setSummary?.(s[k]); }));
 page.addEventListener('change', () => queueMicrotask(() => { const s = summaries(ctx); for (const [k, el] of Object.entries(made)) el.setSummary?.(s[k]); }));
 return page;
}
// A radiator valve as the setting device of a room that is On (CONTRACT-1.4.2 §2 setting_device_hint): said while you
// choose (the climate entities that are valves, live.valve_setting_devices), and for the stored choice.
const valveHint = (m, v) => v.state === 'active' && !!v.setpoint_entity && ((m.live?.valve_setting_devices || []).includes(v.setpoint_entity)
 || (m.live?.setting_device_hint === 'valve_on_active' && v.setpoint_entity === m.setpoint_entity && m.state === 'active'));
// Where the room's target comes from now, in the room card's words (live.target_source; plan 3.3).
function sourceLine(ctx) {
 const {kit, t, model: m, hass} = ctx, s = m.live?.target_source;
 if (!s || ctx.item === NEW) return null;
 const temperature = kit.degrees(num(s.temperature), m.unit || '°C', hass), time = s.until ? kit.time.moment(hass, s.until) : '';
 const words = {
  program: time ? ['Now {temperature} from the week program, until {time}', {temperature, time}] : ['Now {temperature} from the week program', {temperature}],
  fixed: ['Now {temperature}: the temperature without a week program', {temperature}],
  manual: time ? ['Temporarily {temperature} until {time}', {temperature, time}] : ['Temporarily {temperature}', {temperature}],
  reset: s.reset_time ? ['Now {temperature} from the reset time of {time}', {temperature, time: kit.time.format(hass, s.reset_time)}] : ['Now {temperature} from a reset time', {temperature}],
  summer: ['{temperature}: summer mode', {temperature}], window: ['{temperature}: a window or door is open', {temperature}],
  boost: time ? ['Boost until {time}', {time}] : ['Boost active', {}]}[s.source];
 return words && (temperature || s.source === 'boost') ? kit.h('p', {class: 'help rr-source', 'data-target-source': s.source, text: kit.together(t(...words))}) : null;
}
// HA-ADVICE's sentence beside the field (live.advice: heat along or a fixed temperature), its "More" and "Use 18 °C".
function adviceBlock(ctx) {
 const {kit, t, model: m} = ctx, a = m.live?.advice, lang = kit.langOf(ctx.hass), unit = m.unit || '°C';
 const text = a && (a['text_' + lang] || a.text_en);
 if (!text || ctx.item === NEW) return null;
 const more = a['more_' + lang] || a.more_en, target = num(a.target_c), error = kit.h('div', {class: 'rr-advice-error'});
 // The room model's plain sentence (live.model: how fast it cools and warms) goes under "More" with the assumptions.
 const model = m.live?.model?.['sentence_' + lang] || m.live?.model?.sentence_en;
 const box = kit.h('div', {class: 'rr-advice', 'data-advice': ''}, kit.h('p', {class: 'help', text: kit.together(text)}),
  more || model ? kit.more([more, model].filter(Boolean).join(' '), lang) : null);
 if (target == null || ctx.readOnly) return box;
 const use = kit.button(t('Use {temperature}', {temperature: kit.degrees(inUnit(target, unit), unit, ctx.hass)}), async () => {
  use.disabled = true; error.replaceChildren();
  // A routine plan write of HA-ADVICE (the self-tuning does not restart); then the screen reads the room again.
  try { await ctx.action('adopt_advice', {temperature: target}); ctx.reload(); }
  catch (err) { use.disabled = false; error.replaceChildren(kit.inlineError(err?.text || ctx.errorText(err?.code || 'unknown'))); }
 }, 'text', {'data-adopt': ''});
 box.append(use, error);
 return box;
}
// The fixed temperature's block: the field (or, on Heat along only with a week program, the sentence and "Use one fixed
// temperature"), the line where the target comes from now, and the advice.
function fixedBlock(ctx, follow) {
 const {kit, t, model: m, values: v} = ctx, {h} = kit, unit = m.unit || '°C';
 const program = ctx.item !== NEW && (m.live?.program || []).length > 0;
 const parts = [];
 if (follow && program) {
  const temperature = kit.degrees(num(v.fallback_temperature), unit, ctx.hass);
  parts.push(h('div', {class: 'field rr-program-note', 'data-field': 'fallback_temperature'}, h('span', {class: 'label', text: t('Heat along up to')}),
   h('p', {class: 'help', text: t('This room follows its week program; the valve gets those temperatures.')}),
   ctx.readOnly ? null : kit.button(t('Use one fixed temperature'), () => ctx.act({remove_program: true, fallback_temperature: v.fallback_temperature}, {
    title: t('Use one fixed temperature?'), confirm: t('Remove the week program'), danger: true,
    text: t('The week program of {name} is removed, and {temperature} becomes its temperature from now on. You can change that temperature here afterwards.', {name: m.name, temperature})}),
   'text', {'data-remove-program': ''})));
 } else {
  parts.push(ctx.field('stepper', 'fallback_temperature', {label: t(follow ? 'Heat along up to' : 'Temperature without a week program'), unit, step: unit === '°F' ? 1 : 0.5,
   min: m.limits?.minimum, max: m.limits?.maximum, help: follow ? t('The valve opens up to this temperature; the room asks for no heat itself. This is the same setting as the temperature without a week program.') : null,
   more: follow ? null : t('The temperature the room keeps when it has no week program, and while the E32\'s clock is not set yet. Without a week program a manual change becomes this temperature.')}));
 }
 return [...parts, sourceLine(ctx), adviceBlock(ctx)].filter(Boolean);
}
function settingLine(ctx) {
 const {kit, t, model} = ctx, el = kit.h('p', {class: 'help rr-setting', 'data-live': ''}), unit = model.unit || '°C';
 el._live = hass => {
  const a = hass?.states?.[model.entities?.climate]?.attributes || {};
  if (!model.setpoint_entity || ctx.values.setpoint_entity !== model.setpoint_entity || a.setting_device !== model.setpoint_entity) { el.hidden = true; return; }
  const lines = [];
  if (typeof a.setting_device_written === 'number') lines.push(t('Last written: {temperature} at {time}', {temperature: kit.degrees(inUnit(a.setting_device_written, unit), unit, hass), time: kit.time.moment(hass, a.setting_device_written_at)}));
  if (typeof a.setting_device_knob === 'number') lines.push(t('Last turned on the device: {temperature} at {time}', {temperature: kit.degrees(inUnit(a.setting_device_knob, unit), unit, hass), time: kit.time.moment(hass, a.setting_device_knob_at)}));
  if (!lines.length) lines.push(t('Nothing written to it yet.'));
  // HA-SETDEV (V4): when Home Assistant last set the device to manual (it ran its own schedule).
  if (a.setting_device_set_to_manual) lines.push(t('Set to manual by Home Assistant at {time}', {time: kit.time.moment(hass, a.setting_device_set_to_manual)}));
  if (a.setting_device_error) lines.push(String(a.setting_device_error));
  el.hidden = false; el.textContent = kit.together(lines.join(' · '));
 };
 el._live(ctx.hass);
 return el;
}
// The week planner of this one room (CONTRACT-1.4.1 §4): the same element as the dashboard's card, kept per room so a
// redraw of the screen never loses what you changed in it; it saves on its own button. 1.4.2 (P11): a room that is
// removed or added again (same name, same id) gets a new one; the element reads again when the screen opens after
// PLANNER_FRESH_MS (a tablet that stays open) or when the room's program changed elsewhere, never while it holds changes.
const PLANNER_FRESH_MS = 5 * 60000;
const planners = new Map();
const forgetPlanners = id => { for (const key of [...planners.keys()]) if (key.endsWith('/' + id)) planners.delete(key); };
function planner(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit, key = ctx.entry_id + '/' + m.id, program = JSON.stringify(m.live?.program || []);
 if (!customElements.get('openthermostat-e32-week')) {
  // The dashboard's Week program view is gone (1.4.1): no link to it, only the plain fact.
  return h('div', {class: 'rr-week'}, kit.notice(t('The week planner is not loaded on this page.'), 'warning'));
 }
 let entry = planners.get(key);
 if (!entry) {
  const el = document.createElement('openthermostat-e32-week');
  entry = {el, dirty: false, loaded: Date.now(), program};
  el.addEventListener('openthermostat-week-dirty', e => { entry.dirty = !!e.detail?.dirty; });
  el.setConfig({type: 'custom:openthermostat-e32-week', entry_id: ctx.entry_id, room_id: m.id, embedded: true});
  planners.set(key, entry);
 } else if (!(entry.dirty || entry.el.dirty === true || entry.el.anyDirty === true)
  && (Date.now() - entry.loaded > PLANNER_FRESH_MS || entry.program !== program)) {
  entry.loaded = Date.now(); entry.program = program;
  if (ctx.hass) entry.el.load?.();  // Home Assistant answers from the plan it holds: no E32 sign-in
 }
 entry.el.hass = ctx.hass;
 ctx.guard(() => (entry.dirty || entry.el.dirty === true || entry.el.anyDirty === true ? {title: t('Leave without saving the week program?'),
  text: t('What you changed in the week program of {name} is lost.', {name: m.name}), confirm: t('Leave'), danger: true} : null));
 const box = h('div', {class: 'rr-week', 'data-live': ''}, entry.el);
 box._live = hass => { entry.el.hass = hass; };
 return box;
}
// The rooms beside an open room on a wide screen: the glance's rooms as small cards, the current one marked.
function nav(ctx) {
 const {kit, t} = ctx, rooms = ctx.overview?.glance?.rooms;
 if (!Array.isArray(rooms)) return null;
 const list = kit.h('div', {class: 'rr-nav'}, kit.h('h2', {class: 'title', text: t('Rooms')}),
  ...rooms.map(room => card({...ctx, model: null}, room, {compact: true, current: room.id === ctx.item})));
 if (!ctx.readOnly) list.append(kit.button(t('Room'), () => ctx.navigate('#rooms/' + NEW), 'outlined', {icon: 'plus', 'aria-label': t('Add room'), 'data-add-room': ''}));
 return list;
}

// The values of a room's screen (the list has none): the 1.4 keys, then the parts of CONTRACT-1.4.1 §1 this firmware has.
function valuesOf(model) {
 if (!('id' in model)) return {};
 const v = Object.fromEntries(PLAIN.filter(k => k in model).map(k => [k, copy(model[k])]));
 if (model.contacts) { const {windows = [], doors = [], window_delay_s = null, door_delay_s = null} = model.contacts; v.contacts = {windows: [...windows], doors: [...doors], window_delay_s, door_delay_s}; }
 if (model.radiator_valves) v.radiator_valves = {list: (model.radiator_valves.list || []).map(valveSave), control: model.radiator_valves.control ?? null};
 if (model.persons) v.persons = {entity_ids: [...(model.persons.entity_ids || [])], away_temperature: model.persons.away_temperature ?? null};
 if (model.notifications) v.notifications = {on: !!model.notifications.on, kinds: [...(model.notifications.kinds || [])],
  ...('recipients' in model.notifications ? {recipients: model.notifications.recipients == null ? null : [...model.notifications.recipients]} : {})};
 if (model.limits && model.limits.minimum != null) { v.minimum_temperature = model.limits.minimum; v.maximum_temperature = model.limits.maximum; }
 return v;
}

// A temperature source on a phone: its name and reading beside the remove button, "Use first" on a row of its own.
const STYLE = `.rr-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:-4px 0 var(--ot-s3)}
.rr-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:var(--ot-s3)}.rr-card{display:grid}
.rr-room{display:grid;gap:0}.rr-status{margin:-8px 0 var(--ot-s3)}.rr-status:empty{display:none}
.rr-list,.rr-group{display:grid;gap:var(--ot-s2);max-width:560px}.rr-group>.field{padding:var(--ot-s2) 0;margin:0;border:0}
.rr-group>.field:first-child{padding-top:0}.rr-own{display:grid;gap:var(--ot-s2);padding:var(--ot-s2) 0}.rr-own>.field{padding:0;margin:0;border:0}
.pick .btn{flex:none}.rr-valve .pick-text{gap:4px}.rr-model{max-width:320px;min-height:40px;padding:6px 10px;margin-top:4px}
.rr-list .pick-name{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px}.rr-twin{display:grid;justify-items:start;gap:0;margin:-4px 0 0 12px}
.rr-fixed{display:grid}.rr-fixed>.field{padding:var(--ot-s3) 0;margin:0;border:0}.rr-source{margin:-8px 0 0;padding-bottom:var(--ot-s3)}
.rr-advice{display:grid;justify-items:start;gap:4px;padding-bottom:var(--ot-s3)}.rr-program-note{display:grid;justify-items:start;gap:4px}
.rr-hint .notice{margin:0 0 var(--ot-s3)}.rr-recipients{margin:0}
.rr-setting{margin:-8px 0 0;padding-bottom:var(--ot-s3)}.rr-why{padding:var(--ot-s3) 0 0}
.rr-week{padding:var(--ot-s3) 0}.rr-full{margin-top:var(--ot-s3)}.rr-remove{margin-top:var(--ot-s5);display:flex;justify-content:flex-start}
.rr-nav{display:grid;gap:var(--ot-s2)}.rr-nav .title{margin-bottom:var(--ot-s1)}.rr-nav .btn{justify-self:start;margin-top:var(--ot-s1)}
@media(max-width:420px){.rr-cards{grid-template-columns:1fr}}
@media(max-width:520px){.pick[data-source]{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:0 8px}
.pick[data-source] [data-first]{grid-row:2;grid-column:1;justify-self:start;min-height:44px;margin-left:-12px}}`;

(window.OpenThermostatSettingsSections ||= []).push(['rooms', {
 title: (model, item) => (item === NEW ? 'New room' : 'Rooms'),
 texts: TEXTS,
 errors: ERRORS,
 cards: true,
 skeleton: 'cards',
 values: valuesOf,
 // Only what differs from the room as shown (a new room: everything), each top key whole.
 toSave: (values, model) => {
  // A new room: what its screen shows; its windows, valves, persons and notifications come once it exists.
  if (model.id === '') return Object.fromEntries(Object.entries(values).filter(([k]) => !['contacts', 'radiator_valves', 'persons', 'notifications'].includes(k)));
  const shown = valuesOf(model);
  return Object.fromEntries(Object.entries(values).filter(([k, x]) => !same(x, shown[k])));
 },
 // After adding: the page of the new room; after removing: the list. Either way that room's planner starts afresh (P11).
 saved: (model, item) => {
  if (model.removed || item === NEW) forgetPlanners(model.id);
  return model.removed ? '#rooms' : item === NEW && model.id ? '#rooms/' + encodeURIComponent(model.id) : null;
 },
 // A value changed elsewhere too, in the words of this section.
 shown: (key, value, t) => {
  if (key === 'state') return t(STATES[value]?.[0] || value);
  if (key === 'emitter') return t(EMITTERS[value]?.[0] || value);
  if (key === 'sources') return (value || []).map(s => s.id).join(', ');
  if (key === 'contacts') return [...(value?.windows || []), ...(value?.doors || [])].join(', ');
  if (key === 'radiator_valves') return (value?.list || []).map(valveKey).join(', ');
  if (key === 'persons') return (value?.entity_ids || []).join(', ');
  if (key === 'notifications') return [t(value?.on ? 'On' : 'Off'), ...(value?.recipients ? [value.recipients.join(', ')] : [])].join(' · ');
  return undefined;
 },
 nav,
 live: (root, hass) => { for (const el of root.querySelectorAll('.page-col [data-live]')) el._live?.(hass); },
 // The style of this section goes last.
 render: ctx => { const el = ctx.item == null ? roomList(ctx) : roomPage(ctx); el.append(ctx.kit.h('style', {text: STYLE})); return el; }
}]);
