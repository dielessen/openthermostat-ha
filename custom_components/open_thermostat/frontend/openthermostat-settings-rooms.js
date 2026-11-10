/* The settings panel's section Rooms (1.4): the E32 rooms as a list, one room's settings, adding and removing a room.
   Backend settings_rooms.py (the room form's own rules); the kit and the core: openthermostat-settings.js
   (HA-INSTELPANEEL-ONTWERP.nl.md, chapter 10). Live values (temperatures, targets, the setting device) come from
   hass.states and are kept up to date by spec.live without redrawing the page. Texts: TEXTS, English key; the room
   states and their explanations, the reset time sentence and the field labels are Configure's own words
   (test/ha-settings-texts.test.cjs checks them word for word). */
const TEXTS = {
 nl: {
  'Rooms': 'Ruimtes', 'New room': 'Nieuwe ruimte', 'Add room': 'Ruimte toevoegen',
  'The rooms on your E32: what each one is set to and what it measures now.': 'De ruimtes op je E32: hoe elke ruimte is ingesteld en wat ze nu meet.',
  'No rooms yet. Add the first room: give it a name and choose where its temperature comes from.': 'Nog geen ruimtes. Voeg de eerste ruimte toe: geef haar een naam en kies waar haar temperatuur vandaan komt.',
  'The E32 holds at most {max} rooms. Remove a room first.': 'De E32 heeft plaats voor hoogstens {max} ruimtes. Verwijder eerst een ruimte.',
  'On': 'Aan', 'Heat along only': 'Alleen meeverwarmen', 'Off': 'Uit', 'Off until {moment}': 'Uit tot {moment}',
  'Radiators': 'Radiatoren', 'Floor heating': 'Vloerverwarming',
  '{temperature} measured ({source})': '{temperature} gemeten ({source})', '{temperature} measured': '{temperature} gemeten',
  'No temperature yet': 'Nog geen temperatuur', 'Bluetooth sensor {name}': 'Bluetooth-sensor {name}',
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
  'Used first': 'Eerst gebruikt', 'Use first': 'Eerst gebruiken', 'Use {name} first': '{name} eerst gebruiken', 'Remove {name}': '{name} verwijderen',
  'Add a source': 'Bron toevoegen', 'At most four temperature sources per room.': 'Hoogstens vier temperatuurbronnen per ruimte.',
  'No source yet: choose at least one.': 'Nog geen bron: kies er minstens één.',
  'Search by name': 'Zoek op naam', 'Bluetooth sensor on the E32': 'Bluetooth-sensor op de E32', 'No reading': 'Geen meting',
  'just now': 'zojuist', '{n} min ago': '{n} min geleden', '{n} h ago': '{n} uur geleden',
  'Setting device (optional)': 'Instelapparaat (optioneel)',
  'A thermostat or radiator valve (for example a tado or TV02), or a number with a target, to set the room with. Home Assistant writes the week program\'s temperature to it at every switch point; turning it changes the room until the next switch point. Turn off the device\'s own schedule (manual mode), otherwise it changes the temperature by itself.': 'Een thermostaat of radiatorkraan (bijvoorbeeld een tado of TV02), of een getal met een doel, om de ruimte mee in te stellen. Home Assistant zet bij elk schakelpunt de temperatuur van het weekprogramma erop; eraan draaien verandert de ruimte tot het volgende schakelpunt. Zet het eigen programma van het apparaat uit (handmatige stand), anders verandert het de temperatuur zelf.',
  'Last written: {temperature} at {time}': 'Laatst geschreven: {temperature} om {time}',
  'Last turned on the device: {temperature} at {time}': 'Laatst aan het apparaat gedraaid: {temperature} om {time}',
  'Nothing written to it yet.': 'Er is nog niets naartoe geschreven.',
  'Temperature without a week program': 'Temperatuur zonder weekprogramma',
  'The temperature the E32 keeps when Home Assistant gives no target and the room has no week program, or its clock is not set yet.': 'De temperatuur die de E32 aanhoudt als Home Assistant geen doel doorgeeft en de ruimte geen weekprogramma heeft, of zijn klok nog niet is gezet.',
  'Week program': 'Weekprogramma', 'Open in the week planner': 'Openen in de weekplanner',
  'You change the week program in the week planner.': 'Het weekprogramma wijzig je in de weekplanner.',
  'No week program; the room keeps {temperature}.': 'Geen weekprogramma; de ruimte houdt {temperature} aan.',
  'Every day': 'Elke dag',
  'Start with the standard week program': 'Beginnen met het standaardweekprogramma',
  '“Workdays and weekend”: 20 °C by day, 18 °C while away on workdays, 16 °C at night. You change it afterwards in the week planner. Off: the room keeps its temperature without a week program.': '“Werkdagen en weekend”: overdag 20 °C, 18 °C als je op werkdagen weg bent, ’s nachts 16 °C. Je wijzigt het daarna in de weekplanner. Uit: de ruimte houdt haar temperatuur zonder weekprogramma.',
  'Reset times': 'Terugzetmomenten',
  'On that moment any manual change ends and the room takes this value; the E32 does not work towards it.': 'Op dat moment eindigt een handmatige wijziging en krijgt de ruimte deze waarde; de E32 werkt er niet naartoe.',
  'No reset times.': 'Geen terugzetmomenten.', 'Add reset time': 'Terugzetmoment toevoegen', 'Remove reset time {n}': 'Terugzetmoment {n} verwijderen',
  'At most four reset times per room.': 'Hoogstens vier terugzetmomenten per ruimte.',
  'Reset time {n}': 'Terugzetmoment {n}', 'Time': 'Tijd', 'Days': 'Dagen', 'Value': 'Waarde', 'A temperature': 'Een temperatuur',
  'Temperature ({unit})': 'Temperatuur ({unit})',
  'Mon': 'ma', 'Tue': 'di', 'Wed': 'wo', 'Thu': 'do', 'Fri': 'vr', 'Sat': 'za', 'Sun': 'zo',
  'Monday': 'maandag', 'Tuesday': 'dinsdag', 'Wednesday': 'woensdag', 'Thursday': 'donderdag', 'Friday': 'vrijdag', 'Saturday': 'zaterdag', 'Sunday': 'zondag',
  'Smart warm-up': 'Slim opwarmen', 'As the house': 'Als het huis',
  'Follows Smart warm-up of the house (Heating and boiler).': 'Volgt Slim opwarmen van het huis (Verwarming en ketel).',
  'This room is warm at its switch times.': 'Deze ruimte is warm op haar schakeltijden.',
  'This room starts heating at its switch times.': 'Deze ruimte begint pas op haar schakeltijden met verwarmen.',
  'Window and door contacts': 'Raam- en deurcontacten',
  'Window contacts: {n} · door contacts: {d}': 'Raamcontacten: {n} · deurcontacten: {d}', 'No window or door contacts': 'Geen raam- of deurcontacten',
  'Radiator valves, persons and temperature limits': 'Radiatorkranen, personen en temperatuurgrenzen',
  'Radiator valves: {n}': 'Radiatorkranen: {n}', 'You change these in Configure for now.': 'Deze wijzig je voorlopig in Configureren.',
  'Remove room': 'Ruimte verwijderen', 'Remove {name}?': '{name} verwijderen?',
  'The E32 forgets the room with its week program and reset times, and Home Assistant removes its devices. This cannot be undone.': 'De E32 vergeet de ruimte met haar weekprogramma en terugzetmomenten, en Home Assistant verwijdert haar apparaten. Dit kan niet ongedaan worden gemaakt.',
  // errors
  'Give the room a name of up to 40 letters (fewer with accents or emoji).': 'Geef de ruimte een naam van hoogstens 40 tekens (minder met accenten of emoji).',
  '{source} cannot be used here. Choose a thermostat or a temperature sensor; for the setting device a thermostat, radiator valve or number.': '{source} kan hier niet gebruikt worden. Kies een thermostaat of temperatuursensor; als instelapparaat een thermostaat, radiatorkraan of getal.',
  '{source} cannot be used: its name in Home Assistant is longer than 80 characters.': '{source} kan niet gebruikt worden: de naam in Home Assistant is langer dan 80 tekens.',
  '{source} does not exist in Home Assistant.': '{source} bestaat niet in Home Assistant.',
  '{source} reports no current temperature. Choose a thermostat that measures the room, or a temperature sensor.': '{source} meldt geen actuele temperatuur. Kies een thermostaat die de ruimte meet, of een temperatuursensor.',
  '{source} does not report a temperature (°C or °F). Choose a temperature sensor.': '{source} meldt geen temperatuur (°C of °F). Kies een temperatuursensor.',
  'Choose 1 to 4 temperature sources.': 'Kies 1 tot 4 temperatuurbronnen.', 'A source is in the list twice.': 'Een bron staat twee keer in de lijst.',
  'Another room has this name.': 'Een andere ruimte heeft deze naam.',
  'The E32 cannot use this setting device. Choose another one.': 'De E32 kan dit instelapparaat niet gebruiken. Kies een ander.',
  'Choose a temperature within the room\'s temperature limits.': 'Kies een temperatuur binnen de temperatuurgrenzen van de ruimte.',
  'Reset time {line}: choose a time, at least one day and a temperature in whole or half degrees.': 'Terugzetmoment {line}: kies een tijd, minstens één dag en een temperatuur in hele of halve graden.',
  'Reset time {line}: the temperature is outside the room\'s temperature limits.': 'Terugzetmoment {line}: de temperatuur ligt buiten de temperatuurgrenzen van de ruimte.',
  'Reset time {line}: another reset time is already set for that day and time.': 'Terugzetmoment {line}: op die dag en dat tijdstip staat al een terugzetmoment.',
  'The E32 did not accept the reset times ({error}). Check the days, the times and the temperatures.': 'De E32 heeft de terugzetmomenten niet aangenomen ({error}). Controleer de dagen, de tijden en de temperaturen.',
  'Choose a moment in the future (before 2100) for “Off until”, or leave it empty.': 'Kies voor “Uit tot” een moment in de toekomst (voor 2100), of laat het leeg.',
  'The E32 already has 8 rooms. Remove a room first.': 'De E32 heeft al 8 ruimtes. Verwijder eerst een ruimte.',
  'This room is no longer on the E32.': 'Deze ruimte staat niet meer op de E32.',
  'The rooms were changed on the E32 twice while saving. Nothing was saved; try again.': 'De ruimtes zijn tijdens het opslaan twee keer op de E32 gewijzigd. Er is niets opgeslagen; probeer het opnieuw.',
  'The rooms no longer fit on the E32 (4 KB). Use shorter names, fewer sources or fewer switch points. Nothing was saved.': 'De ruimtes passen niet meer op de E32 (4 KB). Gebruik kortere namen, minder bronnen of minder schakelpunten. Er is niets opgeslagen.',
  'The E32 has no storage space left for its rooms. Remove a room you no longer use, or a few switch points, and save again. Nothing was saved.': 'De E32 heeft geen opslagruimte meer voor zijn ruimtes. Verwijder een ruimte die je niet meer gebruikt, of een paar schakelpunten, en sla opnieuw op. Er is niets opgeslagen.',
  'The E32 could not confirm the change. Reload the page to see what is saved.': 'De E32 kon de wijziging niet bevestigen. Laad de pagina opnieuw om te zien wat er is opgeslagen.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'De E32 is niet bereikbaar ({error}). Er is niets opgeslagen.',
  'The E32 sent rooms this version cannot read. Update the E32 firmware and the integration together.': 'De E32 stuurde ruimtes die deze versie niet kan lezen. Werk de E32-firmware en de integratie samen bij.',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'De E32 accepteert het bewaarde wachtwoord niet meer. Home Assistant vraagt om het nieuwe: Instellingen → Apparaten en diensten → OpenThermostat → Opnieuw verifiëren.',
  'The E32 did not accept the room ({error}). Nothing was saved.': 'De E32 heeft de ruimte niet aangenomen ({error}). Er is niets opgeslagen.',
  'The E32 did not accept the week program. Check it in the week planner.': 'De E32 heeft het weekprogramma niet aangenomen. Controleer het in de weekplanner.'},
 pl: {
  'Rooms': 'Pomieszczenia', 'New room': 'Nowe pomieszczenie', 'Add room': 'Dodaj pomieszczenie',
  'The rooms on your E32: what each one is set to and what it measures now.': 'Pomieszczenia na Twoim E32: jak każde jest ustawione i co teraz mierzy.',
  'No rooms yet. Add the first room: give it a name and choose where its temperature comes from.': 'Brak jeszcze pomieszczeń. Dodaj pierwsze pomieszczenie: nadaj mu nazwę i wybierz, skąd pochodzi jego temperatura.',
  'The E32 holds at most {max} rooms. Remove a room first.': 'E32 mieści najwyżej {max} pomieszczeń. Najpierw usuń pomieszczenie.',
  'On': 'Włączone', 'Heat along only': 'Grzeje tylko razem z innymi', 'Off': 'Wyłączone', 'Off until {moment}': 'Wyłączone do {moment}',
  'Radiators': 'Grzejniki', 'Floor heating': 'Ogrzewanie podłogowe',
  '{temperature} measured ({source})': 'Zmierzono {temperature} ({source})', '{temperature} measured': 'Zmierzono {temperature}',
  'No temperature yet': 'Brak jeszcze temperatury', 'Bluetooth sensor {name}': 'Czujnik Bluetooth {name}',
  'Room name': 'Nazwa pomieszczenia',
  'The name you see in Home Assistant and on the E32. Up to 40 letters (fewer with accents or emoji); renaming keeps the room and its history.': 'Nazwa widoczna w Home Assistant i na E32. Do 40 liter (mniej przy znakach diakrytycznych lub emoji); zmiana nazwy zachowuje pomieszczenie i jego historię.',
  'Heating': 'Ogrzewanie',
  'The room can ask for heat.': 'Pomieszczenie może prosić o ciepło.',
  'The room keeps its target and its radiator valves open for it, but it never asks for heat; it warms while the boiler runs for other rooms.': 'Pomieszczenie zachowuje swoją temperaturę docelową, a zawory grzejnikowe otwierają się dla niej, ale nigdy nie prosi o ciepło; nagrzewa się, gdy kocioł grzeje dla innych pomieszczeń.',
  'The room asks for no heat.': 'Pomieszczenie nie prosi o ciepło.',
  'Off until (optional)': 'Wyłączony do (opcjonalnie)',
  'The date and time the room heats again by itself. Empty: off until you turn it on.': 'Data i godzina, od której pomieszczenie samo znów grzeje. Puste: wyłączone, dopóki go nie włączysz.',
  'Heating type': 'Rodzaj ogrzewania',
  'Radiators or floor heating. Floor heating warms up slowly and needs cooler water, so each type gets its own water temperature.': 'Grzejniki lub ogrzewanie podłogowe. Podłogówka nagrzewa się powoli i potrzebuje chłodniejszej wody, więc każdy rodzaj ma własną temperaturę wody.',
  'Temperature sources': 'Źródła temperatury',
  'The first one with a fresh value is used; the others are backups. With one source: if it fails, the room stops asking for heat after 30 minutes. A second source, for example a Bluetooth sensor, covers that.': 'Używany jest pierwszy ze świeżą wartością; pozostałe są zapasowe. Przy jednym źródle: gdy przestanie działać, pomieszczenie po 30 minutach przestaje prosić o ciepło. Drugie źródło, np. czujnik Bluetooth, temu zapobiega.',
  'Used first': 'Używane jako pierwsze', 'Use first': 'Używaj jako pierwszego', 'Use {name} first': 'Używaj {name} jako pierwszego', 'Remove {name}': 'Usuń: {name}',
  'Add a source': 'Dodaj źródło', 'At most four temperature sources per room.': 'Najwyżej cztery źródła temperatury na pomieszczenie.',
  'No source yet: choose at least one.': 'Brak źródła: wybierz co najmniej jedno.',
  'Search by name': 'Szukaj po nazwie', 'Bluetooth sensor on the E32': 'Czujnik Bluetooth na E32', 'No reading': 'Brak odczytu',
  'just now': 'przed chwilą', '{n} min ago': '{n} min temu', '{n} h ago': '{n} godz. temu',
  'Setting device (optional)': 'Urządzenie nastawcze (opcjonalnie)',
  'A thermostat or radiator valve (for example a tado or TV02), or a number with a target, to set the room with. Home Assistant writes the week program\'s temperature to it at every switch point; turning it changes the room until the next switch point. Turn off the device\'s own schedule (manual mode), otherwise it changes the temperature by itself.': 'Termostat lub głowica grzejnikowa (na przykład tado lub TV02) albo liczba z wartością docelową, którymi ustawiasz pomieszczenie. Home Assistant w każdym punkcie przełączenia zapisuje na nim temperaturę z programu tygodniowego; zmiana na nim obowiązuje do następnego punktu przełączenia. Wyłącz własny harmonogram urządzenia (tryb ręczny), inaczej samo zmienia temperaturę.',
  'Last written: {temperature} at {time}': 'Ostatnio zapisano: {temperature} o {time}',
  'Last turned on the device: {temperature} at {time}': 'Ostatnio zmieniono na urządzeniu: {temperature} o {time}',
  'Nothing written to it yet.': 'Jeszcze nic na nim nie zapisano.',
  'Temperature without a week program': 'Temperatura bez programu tygodniowego',
  'The temperature the E32 keeps when Home Assistant gives no target and the room has no week program, or its clock is not set yet.': 'Temperatura, którą E32 utrzymuje, gdy Home Assistant nie podaje celu, a pomieszczenie nie ma programu tygodniowego lub zegar E32 nie jest jeszcze ustawiony.',
  'Week program': 'Program tygodniowy', 'Open in the week planner': 'Otwórz w planerze tygodniowym',
  'You change the week program in the week planner.': 'Program tygodniowy zmieniasz w planerze tygodniowym.',
  'No week program; the room keeps {temperature}.': 'Brak programu tygodniowego; pomieszczenie utrzymuje {temperature}.',
  'Every day': 'Codziennie',
  'Start with the standard week program': 'Zacznij od standardowego programu tygodniowego',
  '“Workdays and weekend”: 20 °C by day, 18 °C while away on workdays, 16 °C at night. You change it afterwards in the week planner. Off: the room keeps its temperature without a week program.': '„Dni robocze i weekend”: 20 °C w dzień, 18 °C podczas nieobecności w dni robocze, 16 °C w nocy. Zmienisz go potem w planerze tygodniowym. Wyłączone: pomieszczenie utrzymuje swoją temperaturę bez programu tygodniowego.',
  'Reset times': 'Godziny powrotu',
  'On that moment any manual change ends and the room takes this value; the E32 does not work towards it.': 'W tym momencie kończy się każda ręczna zmiana i pomieszczenie przyjmuje tę wartość; E32 nie dąży do niej z wyprzedzeniem.',
  'No reset times.': 'Brak godzin powrotu.', 'Add reset time': 'Dodaj godzinę powrotu', 'Remove reset time {n}': 'Usuń godzinę powrotu {n}',
  'At most four reset times per room.': 'Najwyżej cztery godziny powrotu na pomieszczenie.',
  'Reset time {n}': 'Godzina powrotu {n}', 'Time': 'Godzina', 'Days': 'Dni', 'Value': 'Wartość', 'A temperature': 'Temperatura',
  'Temperature ({unit})': 'Temperatura ({unit})',
  'Mon': 'pn', 'Tue': 'wt', 'Wed': 'śr', 'Thu': 'cz', 'Fri': 'pt', 'Sat': 'sb', 'Sun': 'nd',
  'Monday': 'poniedziałek', 'Tuesday': 'wtorek', 'Wednesday': 'środa', 'Thursday': 'czwartek', 'Friday': 'piątek', 'Saturday': 'sobota', 'Sunday': 'niedziela',
  'Smart warm-up': 'Inteligentne nagrzewanie', 'As the house': 'Jak cały dom',
  'Follows Smart warm-up of the house (Heating and boiler).': 'Zgodnie z inteligentnym nagrzewaniem domu (Ogrzewanie i kocioł).',
  'This room is warm at its switch times.': 'To pomieszczenie jest ciepłe w swoich punktach przełączenia.',
  'This room starts heating at its switch times.': 'To pomieszczenie zaczyna grzać dopiero w swoich punktach przełączenia.',
  'Window and door contacts': 'Czujniki okien i drzwi',
  'Window contacts: {n} · door contacts: {d}': 'Czujniki okien: {n} · czujniki drzwi: {d}', 'No window or door contacts': 'Brak czujników okien i drzwi',
  'Radiator valves, persons and temperature limits': 'Zawory grzejnikowe, osoby i limity temperatury',
  'Radiator valves: {n}': 'Zawory grzejnikowe: {n}', 'You change these in Configure for now.': 'Te ustawienia zmieniasz na razie w Konfiguruj.',
  'Remove room': 'Usuń pomieszczenie', 'Remove {name}?': 'Usunąć {name}?',
  'The E32 forgets the room with its week program and reset times, and Home Assistant removes its devices. This cannot be undone.': 'E32 zapomina pomieszczenie wraz z jego programem tygodniowym i godzinami powrotu, a Home Assistant usuwa jego urządzenia. Tego nie można cofnąć.',
  'Give the room a name of up to 40 letters (fewer with accents or emoji).': 'Nadaj pomieszczeniu nazwę do 40 liter (mniej przy znakach diakrytycznych lub emoji).',
  '{source} cannot be used here. Choose a thermostat or a temperature sensor; for the setting device a thermostat, radiator valve or number.': 'Nie można tu użyć {source}. Wybierz termostat lub czujnik temperatury; jako urządzenie nastawcze termostat, głowicę grzejnikową lub liczbę.',
  '{source} cannot be used: its name in Home Assistant is longer than 80 characters.': 'Nie można użyć {source}: jego nazwa w Home Assistant ma więcej niż 80 znaków.',
  '{source} does not exist in Home Assistant.': '{source} nie istnieje w Home Assistant.',
  '{source} reports no current temperature. Choose a thermostat that measures the room, or a temperature sensor.': '{source} nie zgłasza bieżącej temperatury. Wybierz termostat, który mierzy temperaturę pomieszczenia, lub czujnik temperatury.',
  '{source} does not report a temperature (°C or °F). Choose a temperature sensor.': '{source} nie zgłasza temperatury (°C lub °F). Wybierz czujnik temperatury.',
  'Choose 1 to 4 temperature sources.': 'Wybierz od 1 do 4 źródeł temperatury.', 'A source is in the list twice.': 'Źródło występuje na liście dwa razy.',
  'Another room has this name.': 'Inne pomieszczenie ma już tę nazwę.',
  'The E32 cannot use this setting device. Choose another one.': 'E32 nie może użyć tego urządzenia nastawczego. Wybierz inne.',
  'Choose a temperature within the room\'s temperature limits.': 'Wybierz temperaturę w granicach limitów temperatury pomieszczenia.',
  'Reset time {line}: choose a time, at least one day and a temperature in whole or half degrees.': 'Godzina powrotu {line}: wybierz godzinę, co najmniej jeden dzień i temperaturę w pełnych lub połówkowych stopniach.',
  'Reset time {line}: the temperature is outside the room\'s temperature limits.': 'Godzina powrotu {line}: temperatura jest poza limitami temperatury pomieszczenia.',
  'Reset time {line}: another reset time is already set for that day and time.': 'Godzina powrotu {line}: na ten dzień i tę godzinę jest już ustawiona godzina powrotu.',
  'The E32 did not accept the reset times ({error}). Check the days, the times and the temperatures.': 'E32 nie przyjął godzin powrotu ({error}). Sprawdź dni, godziny i temperatury.',
  'Choose a moment in the future (before 2100) for “Off until”, or leave it empty.': 'Wybierz dla „Wyłączony do” przyszłą datę i godzinę (przed 2100) albo zostaw pole puste.',
  'The E32 already has 8 rooms. Remove a room first.': 'E32 ma już 8 pomieszczeń. Najpierw usuń pomieszczenie.',
  'This room is no longer on the E32.': 'Tego pomieszczenia nie ma już na E32.',
  'The rooms were changed on the E32 twice while saving. Nothing was saved; try again.': 'Pomieszczenia zostały dwukrotnie zmienione na E32 podczas zapisywania. Nic nie zapisano; spróbuj ponownie.',
  'The rooms no longer fit on the E32 (4 KB). Use shorter names, fewer sources or fewer switch points. Nothing was saved.': 'Pomieszczenia nie mieszczą się już na E32 (4 KB). Użyj krótszych nazw, mniej źródeł lub mniej punktów przełączenia. Nic nie zapisano.',
  'The E32 has no storage space left for its rooms. Remove a room you no longer use, or a few switch points, and save again. Nothing was saved.': 'E32 nie ma już miejsca na pomieszczenia. Usuń nieużywane pomieszczenie lub kilka punktów przełączenia i zapisz ponownie. Nic nie zapisano.',
  'The E32 could not confirm the change. Reload the page to see what is saved.': 'E32 nie mógł potwierdzić zmiany. Wczytaj stronę ponownie, aby zobaczyć, co zapisano.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'Nie udało się połączyć z E32 ({error}). Nic nie zapisano.',
  'The E32 sent rooms this version cannot read. Update the E32 firmware and the integration together.': 'E32 przesłał pomieszczenia, których ta wersja nie potrafi odczytać. Zaktualizuj razem oprogramowanie E32 i integrację.',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'E32 nie akceptuje już zapisanego hasła. Home Assistant prosi o nowe: Ustawienia → Urządzenia i usługi → OpenThermostat → Uwierzytelnij ponownie.',
  'The E32 did not accept the room ({error}). Nothing was saved.': 'E32 nie przyjął pomieszczenia ({error}). Nic nie zapisano.',
  'The E32 did not accept the week program. Check it in the week planner.': 'E32 nie przyjął programu tygodniowego. Sprawdź go w planerze tygodniowym.'}};
// The sentence of each code settings_rooms.py may answer (the codes of the room form itself).
const ERRORS = {
 e32_name_invalid: 'Give the room a name of up to 40 letters (fewer with accents or emoji).',
 e32_source_wrong_domain: '{source} cannot be used here. Choose a thermostat or a temperature sensor; for the setting device a thermostat, radiator valve or number.',
 e32_source_invalid_id: '{source} cannot be used: its name in Home Assistant is longer than 80 characters.',
 e32_source_not_found: '{source} does not exist in Home Assistant.',
 e32_source_no_temperature: '{source} reports no current temperature. Choose a thermostat that measures the room, or a temperature sensor.',
 e32_source_not_celsius: '{source} does not report a temperature (°C or °F). Choose a temperature sensor.',
 e32_sources_count: 'Choose 1 to 4 temperature sources.', e32_rejected_sources: 'Choose 1 to 4 temperature sources.',
 e32_rejected_duplicate_source: 'A source is in the list twice.', e32_rejected_duplicate_room: 'Another room has this name.',
 e32_rejected_setpoint: 'The E32 cannot use this setting device. Choose another one.',
 e32_limits_invalid: 'Choose a temperature within the room\'s temperature limits.',
 e32_resets_invalid: 'Reset time {line}: choose a time, at least one day and a temperature in whole or half degrees.',
 e32_resets_outside_limits: 'Reset time {line}: the temperature is outside the room\'s temperature limits.',
 e32_resets_same_moment: 'Reset time {line}: another reset time is already set for that day and time.',
 e32_resets_too_many: 'At most four reset times per room.',
 e32_rejected_resets: 'The E32 did not accept the reset times ({error}). Check the days, the times and the temperatures.',
 e32_inactive_until_invalid: 'Choose a moment in the future (before 2100) for “Off until”, or leave it empty.',
 e32_room_limit: 'The E32 already has 8 rooms. Remove a room first.',
 e32_room_missing: 'This room is no longer on the E32.',
 e32_plan_changed: 'The rooms were changed on the E32 twice while saving. Nothing was saved; try again.',
 e32_plan_too_large: 'The rooms no longer fit on the E32 (4 KB). Use shorter names, fewer sources or fewer switch points. Nothing was saved.',
 e32_storage_full: 'The E32 has no storage space left for its rooms. Remove a room you no longer use, or a few switch points, and save again. Nothing was saved.',
 e32_unconfirmed: 'The E32 could not confirm the change. Reload the page to see what is saved.',
 e32_unreachable: 'The E32 could not be reached ({error}). Nothing was saved.',
 e32_plan_invalid: 'The E32 sent rooms this version cannot read. Update the E32 firmware and the integration together.',
 e32_password_changed: 'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.',
 e32_rejected: 'The E32 did not accept the room ({error}). Nothing was saved.',
 e32_rejected_schedule: 'The E32 did not accept the week program. Check it in the week planner.'};

const NEW = 'new-room';
const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const STATE_HELP = {active: 'The room can ask for heat.',
 follow: 'The room keeps its target and its radiator valves open for it, but it never asks for heat; it warms while the boiler runs for other rooms.',
 inactive: 'The room asks for no heat.'};
const STATE_LABEL = {active: 'On', follow: 'Heat along only', inactive: 'Off'};
const WARM_UP = [['house', 'As the house', 'Follows Smart warm-up of the house (Heating and boiler).'],
 ['on', 'On', 'This room is warm at its switch times.'], ['off', 'Off', 'This room starts heating at its switch times.']];
const RESET_STATES = ['active', 'follow', 'inactive'];
const EDITABLE = ['name', 'state', 'emitter', 'sources', 'setpoint_entity', 'fallback_temperature', 'inactive_until', 'resets', 'smart_warm_up', 'standard_program'];
const SOURCE_UNITS = ['°C', '°F', 'K'];

/* ---- small helpers ---- */
const copy = v => JSON.parse(JSON.stringify(v));
const number = (v, lang, digits = 1) => Number(v).toLocaleString(lang, {maximumFractionDigits: digits});
const degrees = (v, unit, lang) => `${number(v, lang)} ${unit}`;
const moment = (text, lang) => {
 const d = new Date(text);
 return Number.isNaN(d.getTime()) ? text : d.toLocaleString(lang, {day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit'});
};
const clock = (iso, lang) => { const d = new Date(iso); return Number.isNaN(d.getTime()) ? '' : d.toLocaleTimeString(lang, {hour: '2-digit', minute: '2-digit'}); };
// The age of a reading in words: just now, 4 min ago, 2 h ago.
const age = (st, t) => {
 const at = Date.parse(st?.last_reported || st?.last_updated || '');
 if (Number.isNaN(at)) return '';
 const minutes = Math.floor((Date.now() - at) / 60000);
 return minutes < 1 ? t('just now') : minutes < 120 ? t('{n} min ago', {n: minutes}) : t('{n} h ago', {n: Math.floor(minutes / 60)});
};
// Days as the week planner writes them: Mon–Fri, Sat, Sun; Every day.
function dayText(days, t) {
 const sorted = [...new Set(days)].sort((a, b) => a - b);
 if (sorted.length === 7) return t('Every day');
 const runs = [];
 for (const d of sorted) { const last = runs[runs.length - 1]; if (last && last[1] === d - 1) last[1] = d; else runs.push([d, d]); }
 return runs.map(([a, b]) => (a === b ? t(DAYS[a]) : b === a + 1 ? `${t(DAYS[a])}, ${t(DAYS[b])}` : `${t(DAYS[a])}–${t(DAYS[b])}`)).join(', ');
}
const programLines = (model, t, lang) => model.program.map(g => `${dayText(g.days, t)} ${g.points.map(([at, c]) => `${at} ${degrees(c, model.unit, lang)}`).join(' · ')}`);
const resetValue = (r, unit, t, lang) => (r.state ? t(STATE_LABEL[r.state]) : degrees(r.temperature, unit, lang));
// The name of a source: a Home Assistant entity by its name, a Bluetooth sensor of the E32 by its own.
const bleOf = (model, id) => (Array.isArray(model.ble) ? model.ble.find(s => s.id === id) : model.ble?.[id] != null ? {id, name: model.ble[id]} : null);
const sourceName = (source, model, hass, t) => (source.type === 'ble'
 ? t('Bluetooth sensor {name}', {name: bleOf(model, source.id)?.name || source.id})
 : hass?.states?.[source.id]?.attributes?.friendly_name || source.id);
// The reading of a source now: [text, state] (a climate entity by its current temperature).
function reading(source, model, hass, lang) {
 const eid = source.type === 'ble' ? bleOf(model, source.id)?.entity_id : source.id, st = eid && hass?.states?.[eid];
 if (!st) return ['', null];
 const value = eid.startsWith('climate.') ? st.attributes?.current_temperature : Number.parseFloat(st.state);
 if (typeof value !== 'number' || !Number.isFinite(value)) return ['', st];
 return [degrees(value, eid.startsWith('climate.') ? model.unit : st.attributes?.unit_of_measurement || model.unit, lang), st];
}
// Sources keep the order the room form stores: the kind of the first one first (Bluetooth or Home Assistant), each
// kind in its own order (settings_rooms.py maps the list to the two lists of the form and "Bluetooth first").
function grouped(list) {
 if (!list.length) return list;
 const first = list[0].type;
 return [...list.filter(s => s.type === first), ...list.filter(s => s.type !== first)];
}

/* ---- the fields of this section (the kit's field contract: {el, setError, setMark, focus}) ---- */
function sourcesField(ctx) {
 return o => {
  const {h, fields, button, shell} = ctx.kit, t = ctx.t, model = ctx.model;
  let list = copy(o.value || []), adding = false;
  const body = h('div', {class: 'rh-sources'});
  const api = shell('sources', o, body, false);
  const own = new Set(model.own || []), bleByEntity = new Map((model.ble || []).filter(s => s.entity_id).map(s => [s.entity_id, s]));
  const emit = () => o.onChange?.(copy(list));
  const draw = focusAdd => {
   const items = list.map((source, i) => {
    const name = sourceName(source, model, ctx.hass, t);
    const detail = h('span', {class: 'pick-id', 'data-detail': ''});
    const live = hass => {
     const [v, s] = reading(source, model, hass, ctx.lang);
     detail.textContent = [source.type === 'ble' ? t('Bluetooth sensor on the E32') : source.id, v || t('No reading'), v ? age(s, t) : ''].filter(Boolean).join(' · ');
    };
    live(ctx.hass);
    const el = h('div', {class: 'rh-src', 'data-source': `${source.type}:${source.id}`, 'data-live': ''},
     h('span', {class: 'pick-text'}, h('span', {class: 'pick-name'}, name, i === 0 && list.length > 1 ? h('span', {class: 'badge rh-first', text: t('Used first')}) : null), detail),
     o.disabled || i === 0 ? null : button(t('Use first'), () => { list = grouped([source, ...list.filter(x => x !== source)]); draw(); emit(); }, 'text rh-small',
      {'aria-label': t('Use {name} first', {name}), 'data-first': ''}),
     o.disabled ? null : button('', () => { list = list.filter(x => x !== source); draw(); emit(); }, 'icon remove',
      {'aria-label': t('Remove {name}', {name}), title: t('Remove {name}', {name}), 'data-remove': ''}));
    el._live = live;
    return el;
   });
   const parts = [...items];
   if (!list.length) parts.push(h('p', {class: 'rh-empty', text: t('No source yet: choose at least one.')}));
   if (!o.disabled && list.length >= (model.max_sources || 4)) parts.push(h('p', {class: 'help', text: t('At most four temperature sources per room.')}));
   else if (!o.disabled && adding) {
    const taken = new Set(list.map(s => (s.type === 'ble' ? bleOf(model, s.id)?.entity_id : s.id)));
    const picker = fields.entity({hass: ctx.hass, key: 'sources-add', placeholder: t('Search by name'), value: '',
     filter: (st, eid) => {
      if (taken.has(eid)) return false;
      if (bleByEntity.has(eid)) return true;
      if (own.has(eid)) return false;
      if (eid.startsWith('climate.')) return typeof st?.attributes?.current_temperature === 'number';
      return eid.startsWith('sensor.') && st?.attributes?.device_class === 'temperature' && SOURCE_UNITS.includes(st?.attributes?.unit_of_measurement);
     },
     onChange: eid => {
      if (!eid) return;
      const ble = bleByEntity.get(eid);
      list = [...list, ble ? {type: 'ble', id: ble.id} : {type: 'ha', id: eid}];
      adding = false; draw(true); emit();
     }});
    parts.push(picker.el);
    queueMicrotask(() => picker.focus());
   } else if (!o.disabled) {
    parts.push(button(t('Add a source'), () => { adding = true; draw(); }, 'outlined rh-add', {'data-add-source': ''}));
   }
   body.replaceChildren(...parts);
   if (focusAdd) body.querySelector('[data-add-source]')?.focus();
  };
  draw();
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}

function resetsField(ctx) {
 return o => {
  const {h, button, shell} = ctx.kit, t = ctx.t, model = ctx.model, unit = model.unit;
  let list = copy(o.value || []);
  const body = h('div', {class: 'rh-resets'});
  const api = shell('resets', o, body, false);
  const emit = () => o.onChange?.(copy(list));
  const draw = focus => {
   const rows = list.map((reset, i) => {
    const n = i + 1;
    const time = h('input', {type: 'time', class: 'input rh-time', 'aria-label': t('Time'), disabled: o.disabled, 'data-fk': `resets:${i}:time`});
    time.value = reset.time || '';
    time.addEventListener('input', () => { reset.time = time.value; emit(); });
    const kind = h('select', {class: 'input rh-kind', 'aria-label': t('Value'), disabled: o.disabled, 'data-fk': `resets:${i}:kind`},
     h('option', {value: 'temperature', text: t('A temperature')}), ...RESET_STATES.map(s => h('option', {value: s, text: t(STATE_LABEL[s])})));
    kind.value = reset.state || 'temperature';
    const temp = h('input', {type: 'number', class: 'input rh-temp', step: unit === '°F' ? '0.1' : '0.5', min: model.limits.minimum, max: model.limits.maximum,
     inputmode: 'decimal', 'aria-label': t('Temperature ({unit})', {unit}), disabled: o.disabled, 'data-fk': `resets:${i}:temperature`});
    temp.value = reset.temperature ?? '';
    temp.addEventListener('input', () => { reset.temperature = temp.value === '' ? null : Number(temp.value); emit(); });
    const tempWrap = h('span', {class: 'with-unit rh-temp-wrap', hidden: !!reset.state}, temp, h('span', {class: 'unit', 'aria-hidden': 'true', text: unit}));
    kind.addEventListener('change', () => {
     if (kind.value === 'temperature') { delete reset.state; reset.temperature = model.fallback_temperature; temp.value = reset.temperature; }
     else { reset.state = kind.value; delete reset.temperature; }
     tempWrap.hidden = !!reset.state; emit();
    });
    const days = h('div', {class: 'rh-days', role: 'group', 'aria-label': t('Days')}, ...DAYS.map((d, day) => {
     const on = (reset.days || []).includes(day);
     const b = h('button', {type: 'button', class: 'rh-day', 'aria-pressed': on ? 'true' : 'false', 'aria-label': t(DAY_NAMES[day]), disabled: o.disabled,
      'data-day': day, text: t(d)});
     b.addEventListener('click', () => {
      const set = new Set(reset.days || []);
      set.has(day) ? set.delete(day) : set.add(day);
      reset.days = [...set].sort((a, b2) => a - b2);
      b.setAttribute('aria-pressed', set.has(day) ? 'true' : 'false'); emit();
     });
     return b;
    }));
    return h('div', {class: 'rh-reset', role: 'group', 'aria-label': t('Reset time {n}', {n}), 'data-reset': i},
     h('div', {class: 'rh-reset-top'}, time, kind, tempWrap),
     o.disabled ? null : button('', () => { list.splice(i, 1); draw('add'); emit(); }, 'icon remove',
      {'aria-label': t('Remove reset time {n}', {n}), title: t('Remove reset time {n}', {n}), 'data-remove': ''}),
     days);
   });
   const parts = rows.length ? rows : [h('p', {class: 'rh-empty', text: t('No reset times.')})];
   if (!o.disabled) {
    if (list.length >= 4) parts.push(h('p', {class: 'help', text: t('At most four reset times per room.')}));
    else parts.push(button(t('Add reset time'), () => {
     list.push({days: [0, 1, 2, 3, 4, 5, 6], time: '22:00', temperature: model.fallback_temperature});
     draw('last'); emit();
    }, 'outlined rh-add', {'data-add-reset': ''}));
   }
   body.replaceChildren(...parts);
   if (focus === 'last') body.querySelector('.rh-reset:last-of-type .rh-time')?.focus();
   if (focus === 'add') (body.querySelector('[data-add-reset]') || body.querySelector('.rh-time'))?.focus();
  };
  draw();
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}

// A date and time ("YYYY-MM-DDTHH:MM", local); empty is none.
function momentField(ctx) {
 return o => {
  const input = ctx.kit.h('input', {type: 'datetime-local', class: 'input', id: o.id, disabled: o.disabled, 'data-fk': o.key, step: 60});
  input.value = o.value || '';
  input.addEventListener('input', () => o.onChange?.(input.value));
  const api = ctx.kit.shell('moment', o, input);
  api.target = () => input;
  api.describe();
  return api;
 };
}

/* ---- the screens ---- */
function roomList(ctx) {
 const {h} = ctx.kit, t = ctx.t, model = ctx.model, lang = ctx.lang;
 const rows = model.rooms.map(room => {
  const state = room.state === 'inactive' && room.inactive_until ? t('Off until {moment}', {moment: moment(room.inactive_until, lang)}) : t(STATE_LABEL[room.state] || 'On');
  const el = ctx.row({label: room.name, summary: [`${state} · ${t(room.emitter === 'floor' ? 'Floor heating' : 'Radiators')}`, ' '], value: ' ',
   route: '#rooms/' + encodeURIComponent(room.id), data: {room: room.id}});
  const line = el.querySelectorAll('.row-line')[1], value = el.querySelector('.row-value');
  el.dataset.live = '';
  el._live = hass => {
   const climate = hass?.states?.[room.entities?.climate], sensor = hass?.states?.[room.entities?.temperature];
   const measured = climate?.attributes?.current_temperature ?? (sensor ? Number.parseFloat(sensor.state) : null);
   const source = sensor?.attributes?.source;
   let name = '';
   if (typeof source === 'string' && source.includes('.')) name = hass?.states?.[source]?.attributes?.friendly_name || source;
   else if (source && source !== 'none' && model.ble?.[source]) name = t('Bluetooth sensor {name}', {name: model.ble[source]});
   const text = typeof measured === 'number' && Number.isFinite(measured)
    ? (name ? t('{temperature} measured ({source})', {temperature: degrees(measured, ctx.model.unit || climate?.attributes?.temperature_unit || '°C', lang), source: name})
     : t('{temperature} measured', {temperature: degrees(measured, ctx.model.unit || '°C', lang)}))
    : t('No temperature yet');
   line.textContent = text.replace(/ (°C|°F)/g, ' $1');
   const target = climate?.attributes?.temperature;
   value.textContent = room.state !== 'inactive' && typeof target === 'number' ? degrees(target, ctx.model.unit || '°C', lang).replace(' ', ' ') : '';
  };
  el._live(ctx.hass);
  return el;
 });
 const add = !ctx.readOnly && model.can_add ? ctx.button(t('Add room'), () => ctx.navigate('#rooms/' + NEW), 'filled rh-add-room', {'data-add-room': ''}) : null;
 return h('div', {class: 'rh-list'}, 
  h('div', {class: 'rh-toolbar'}, h('p', {class: 'help', text: t('The rooms on your E32: what each one is set to and what it measures now.')}), add),
  rows.length ? h('div', {class: 'rh-rows'}, ...rows) : ctx.notice(t('No rooms yet. Add the first room: give it a name and choose where its temperature comes from.')),
  !model.can_add && !ctx.readOnly ? h('p', {class: 'help rh-full', text: t('The E32 holds at most {max} rooms. Remove a room first.', {max: model.max_rooms})}) : null);
}

function settingLine(ctx) {
 const {h} = ctx.kit, t = ctx.t, lang = ctx.lang, model = ctx.model;
 const el = h('p', {class: 'help rh-link', 'data-live': ''});
 el._live = hass => {
  const a = hass?.states?.[model.entities?.climate]?.attributes || {};
  if (!model.setpoint_entity || ctx.values.setpoint_entity !== model.setpoint_entity || a.setting_device !== model.setpoint_entity) { el.hidden = true; return; }
  const lines = [];
  if (typeof a.setting_device_written === 'number') lines.push(t('Last written: {temperature} at {time}', {temperature: degrees(a.setting_device_written, '°C', lang), time: clock(a.setting_device_written_at, lang)}));
  if (typeof a.setting_device_knob === 'number') lines.push(t('Last turned on the device: {temperature} at {time}', {temperature: degrees(a.setting_device_knob, '°C', lang), time: clock(a.setting_device_knob_at, lang)}));
  if (!lines.length) lines.push(t('Nothing written to it yet.'));
  if (a.setting_device_error) lines.push(String(a.setting_device_error));
  el.hidden = false; el.textContent = lines.join(' · ').replace(/ °C/g, ' °C');
 };
 el._live(ctx.hass);
 return el;
}

function roomPage(ctx) {
 const {h} = ctx.kit, t = ctx.t, model = ctx.model, lang = ctx.lang, isNew = ctx.item === NEW;
 if (isNew && model.full) return h('div', {}, ctx.notice(t('The E32 holds at most {max} rooms. Remove a room first.', {max: model.max_rooms}), 'warning'));
 const states = (model.states || ['active', 'inactive']).map(s => ({value: s, label: t(STATE_LABEL[s]), help: t(STATE_HELP[s])}));
 const until = ctx.field(momentField(ctx), 'inactive_until', {label: t('Off until (optional)'),
  help: t('The date and time the room heats again by itself. Empty: off until you turn it on.')});
 until.hidden = ctx.values.state !== 'inactive';
 const own = new Set(model.own || []);
 const parts = [
  ctx.field('text', 'name', {label: t('Room name'), maxlength: 40, required: true,
   help: t('The name you see in Home Assistant and on the E32. Up to 40 letters (fewer with accents or emoji); renaming keeps the room and its history.')}),
  ctx.field('radio', 'state', {label: t('Heating'), options: states, onChange: v => { until.hidden = v !== 'inactive'; }}),
  until,
  ctx.field('select', 'emitter', {label: t('Heating type'), options: [{value: 'radiator', label: t('Radiators')}, {value: 'floor', label: t('Floor heating')}],
   help: t('Radiators or floor heating. Floor heating warms up slowly and needs cooler water, so each type gets its own water temperature.')}),
  ctx.field(sourcesField(ctx), 'sources', {label: t('Temperature sources'),
   help: t('The first one with a fresh value is used; the others are backups. With one source: if it fails, the room stops asking for heat after 30 minutes. A second source, for example a Bluetooth sensor, covers that.')}),
  ctx.field('entity', 'setpoint_entity', {label: t('Setting device (optional)'), domains: ['climate', 'input_number', 'number'], placeholder: t('Search by name'),
   filter: (st, eid) => !own.has(eid),
   help: t('A thermostat or radiator valve (for example a tado or TV02), or a number with a target, to set the room with. Home Assistant writes the week program\'s temperature to it at every switch point; turning it changes the room until the next switch point. Turn off the device\'s own schedule (manual mode), otherwise it changes the temperature by itself.')})];
 if (!isNew) parts.push(settingLine(ctx));
 parts.push(ctx.field('number', 'fallback_temperature', {label: t('Temperature without a week program'), unit: model.unit, step: model.unit === '°F' ? 0.1 : 0.5,
  min: model.limits.minimum, max: model.limits.maximum,
  help: t('The temperature the E32 keeps when Home Assistant gives no target and the room has no week program, or its clock is not set yet.')}));
 // The week program: a summary here, the week planner edits it.
 if (isNew) {
  parts.push(ctx.field('toggle', 'standard_program', {label: t('Start with the standard week program'),
   help: t('“Workdays and weekend”: 20 °C by day, 18 °C while away on workdays, 16 °C at night. You change it afterwards in the week planner. Off: the room keeps its temperature without a week program.')}));
 } else {
  const lines = model.program.length ? programLines(model, t, lang)
   : [t('No week program; the room keeps {temperature}.', {temperature: degrees(model.fallback_temperature, model.unit, lang)})];
  parts.push(h('div', {class: 'field rh-program', 'data-field': 'program'}, h('span', {class: 'label', text: t('Week program')}),
   h('div', {class: 'rh-lines'}, ...lines.map(line => h('p', {text: line.replace(/ (°C|°F)/g, ' $1')}))),
   h('p', {class: 'help', text: t('You change the week program in the week planner.')}),
   h('div', {}, ctx.button(t('Open in the week planner'), () => ctx.open(ctx.paths.week), 'outlined', {'data-week': ''}))));
 }
 if (model.features?.resets) parts.push(ctx.field(resetsField(ctx), 'resets', {label: t('Reset times'),
  help: t('On that moment any manual change ends and the room takes this value; the E32 does not work towards it.')}));
 if (model.features?.smart_warm_up) parts.push(ctx.field('radio', 'smart_warm_up', {label: t('Smart warm-up'),
  options: WARM_UP.map(([value, label, help]) => ({value, label: t(label), help: t(help)}))}));
 if (!isNew) {
  parts.push(h('div', {class: 'rh-more'},
   ctx.row({label: t('Window and door contacts'), route: '#house/contacts/' + encodeURIComponent(model.id),
    summary: [model.contacts?.windows || model.contacts?.doors ? t('Window contacts: {n} · door contacts: {d}', {n: model.contacts.windows, d: model.contacts.doors})
     : t('No window or door contacts')]}),
   ctx.row({label: t('Radiator valves, persons and temperature limits'),
    summary: [model.valves ? t('Radiator valves: {n}', {n: model.valves}) : '', t('You change these in Configure for now.')].filter(Boolean),
    onClick: () => ctx.open(ctx.paths.configure)})));
  if (!ctx.readOnly) parts.push(h('div', {class: 'rh-remove'}, ctx.button(t('Remove room'), () => ctx.act({remove: true}, {
   title: t('Remove {name}?', {name: model.name}),
   text: t('The E32 forgets the room with its week program and reset times, and Home Assistant removes its devices. This cannot be undone.'),
   confirm: t('Remove room'), danger: true}), 'outlined rh-danger', {'data-remove-room': ''})));
 }
 return h('div', {class: 'fields'}, ...parts);
}

const STYLE = `.rh-toolbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;padding:12px 0}
.rh-toolbar .help{flex:1 1 220px}.rh-rows{display:flex;flex-direction:column;margin:0 -16px}.rh-rows .row{margin:0;width:100%}
.rh-full{padding:12px 0}.rh-sources,.rh-resets{display:grid;gap:8px;max-width:520px}
.rh-src{display:flex;align-items:center;gap:6px;padding:8px 6px 8px 12px;border:1px solid var(--ot-divider);border-radius:8px}
.rh-src .pick-name{display:flex;flex-wrap:wrap;align-items:center;gap:6px}.rh-first{font-weight:500}
.btn.rh-small{min-height:36px;padding:4px 10px;flex:none}.rh-add{justify-self:start}.rh-empty{color:var(--ot-muted)}
.rh-reset{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:start;gap:8px;padding:10px 12px;border:1px solid var(--ot-divider);border-radius:8px}
.rh-reset-top{display:flex;flex-wrap:wrap;align-items:center;gap:8px}.rh-reset-top .input{width:auto;min-width:0}
.rh-time{flex:0 0 136px}.rh-kind{flex:1 1 150px}.rh-temp-wrap{flex:0 1 130px}.rh-temp{width:84px!important}
.rh-days{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:4px}
.rh-day{font:inherit;min-width:40px;min-height:36px;padding:4px 6px;border-radius:18px;cursor:pointer;
border:1px solid color-mix(in srgb,var(--ot-muted) 55%,transparent);background:none;color:inherit}
.rh-day[aria-pressed=true]{background:var(--ot-fill);border-color:var(--ot-fill);color:#fff}.rh-day:disabled{opacity:.6;cursor:default}
.rh-day:focus-visible{outline:3px solid var(--ot-accent);outline-offset:2px}
.rh-program .rh-lines{display:grid;gap:2px}.rh-program .btn{margin-top:4px}.rh-link{margin-top:-8px;padding:0 0 12px}
.rh-more{margin:8px -16px 0;border-top:1px solid var(--ot-divider)}.rh-more .row{margin:0;width:100%}
.rh-remove{padding:18px 0 8px}.btn.rh-danger{color:color-mix(in srgb,var(--ot-error) 80%,var(--ot-text));border-color:color-mix(in srgb,var(--ot-error) 55%,transparent)}
@media(max-width:420px){.rh-rows,.rh-more{margin-left:-12px;margin-right:-12px}.rh-time{flex-basis:136px}}`;

(window.OpenThermostatSettingsSections ||= []).push(['rooms', {
 title: (model, item) => (item === NEW ? 'New room' : 'Rooms'),
 texts: TEXTS,
 errors: ERRORS,
 // The values the screen of a room edits (the list has none).
 values: model => Object.fromEntries(EDITABLE.filter(k => k in model).map(k => [k, copy(model[k])])),
 // Only what differs from the room as shown (a new room: everything).
 toSave: (values, model) => Object.fromEntries(Object.entries(values).filter(([k, v]) => model.id === '' || JSON.stringify(v) !== JSON.stringify(model[k]))),
 // After adding: the page of the new room; after removing: the list.
 saved: (model, item) => (model.removed ? '#rooms' : item === NEW && model.id ? '#rooms/' + encodeURIComponent(model.id) : null),
 // A value changed elsewhere too, in the words of this section.
 shown: (key, value, t) => {
  if (key === 'state') return t(STATE_LABEL[value] || value);
  if (key === 'emitter') return t(value === 'floor' ? 'Floor heating' : 'Radiators');
  if (key === 'smart_warm_up') return t((WARM_UP.find(w => w[0] === value) || [])[1] || value);
  if (key === 'sources') return (value || []).map(s => s.id).join(', ');
  if (key === 'resets') return (value || []).map(r => `${r.time} ${r.state ? t(STATE_LABEL[r.state]) : r.temperature}`).join(', ');
  return undefined;
 },
 live: (root, hass) => { for (const el of root.querySelectorAll('[data-live]')) el._live?.(hass); },
 // The style of this section goes last: the first field keeps the look of the kit (no line above it).
 render: ctx => { const el = ctx.item == null ? roomList(ctx) : roomPage(ctx); el.append(ctx.kit.h('style', {text: STYLE})); return el; }
}]);
