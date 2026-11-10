/* The settings panel's section House (1.4): presence and the away temperature, the room defaults, the house mode with
   the planned holidays, and the window and door contacts per room. Backend settings_house.py (the options steps' own
   functions); the kit and the core: openthermostat-settings.js (HA-INSTELPANEEL-ONTWERP.nl.md, chapter 10). Sub-screens
   are the item: #house/presence, #house/defaults, #house/mode, #house/contacts and #house/contacts/<room>. Texts:
   TEXTS, English key; labels and explanations are Configure's own words (Configure → House). */
const TEXTS = {
 nl: {
  'House': 'Huis', 'Settings for the whole house: who is home, the house mode and holiday, and the defaults for rooms.': 'Instellingen voor het hele huis: wie thuis is, de huismodus en vakantie, en de standaardwaarden voor ruimtes.',
  'Presence and away temperature': 'Aanwezigheid en afwezigheidstemperatuur', 'Room defaults': 'Standaardwaarden voor ruimtes',
  'House mode and holiday': 'Huismodus en vakantie', 'Window and door contacts': 'Raam- en deurcontacten',
  'Nobody chosen yet': 'Nog niemand gekozen', 'Away after {n} min': 'Afwezig na {n} min',
  'Away after {n} min · {temperature} when nobody is home': 'Afwezig na {n} min · {temperature} als niemand thuis is',
  'Without a week program: comfort {comfort}, night {night}': 'Zonder weekprogramma: comfort {comfort}, nacht {night}',
  'Pause after a window {window} min, after a door {door} min · a manual change lasts {minutes} min': 'Pauze na een raam {window} min, na een deur {door} min · een handmatige wijziging duurt {minutes} min',
  'Next holiday: {from} – {until}': 'Volgende vakantie: {from} – {until}', 'No holidays planned.': 'Geen vakanties gepland.',
  'The E32 does not report the house mode yet.': 'De E32 meldt de huismodus nog niet.',
  'Rooms with contacts: {rooms} · sensors: {sensors}': 'Ruimtes met contacten: {rooms} · sensoren: {sensors}',
  'No contacts yet': 'Nog geen contacten', 'Add a room first.': 'Voeg eerst een ruimte toe.',
  'In the house mode Automatic the rooms go to the away temperature when everyone is away. Someone home, or someone whose place is not known, keeps the house warm.': 'In de huismodus Automatisch gaan de ruimtes naar de afwezigheidstemperatuur als iedereen weg is. Iemand thuis, of iemand van wie niet bekend is waar die is, houdt het huis warm.',
  'Who lives here': 'Wie hier woont',
  'Optional. The people of the house, or a group, zone (for example zone.home), device tracker or switch that is on while someone is home.': 'Optioneel. De mensen van het huis, of een groep, zone (bijvoorbeeld zone.home), apparaattracker of schakelaar die aan is als er iemand thuis is.',
  'Away after': 'Afwezig na',
  'Minutes everyone must be away before the house counts as away, so a short errand does not cool the house. 0: at once.': 'Minuten dat iedereen weg moet zijn voordat het huis als afwezig telt, zodat een korte boodschap het huis niet laat afkoelen. 0: meteen.',
  'Temperature when nobody is home': 'Temperatuur als niemand thuis is',
  'Every room stays at most this warm while everyone is away, in house mode Away and on holiday (5–25 °C; frost protection always stays on).': 'Elke ruimte wordt hoogstens zo warm zolang iedereen weg is, in huismodus Afwezig en op vakantie (5–25 °C; vorstbeveiliging blijft altijd aan).',
  'For every room: the temperatures of a room without a week program, how long a window or door may be open before the room pauses, and how long a change on a thermostat lasts. A room\'s own settings (Configure → Rooms) take precedence.': 'Voor elke ruimte: de temperaturen van een ruimte zonder weekprogramma, hoe lang een raam of deur open mag staan voordat de ruimte pauzeert, en hoe lang een wijziging op een thermostaat geldt. De eigen instellingen van een ruimte (Configureren → Ruimtes) gaan voor.',
  'Comfort without a week program': 'Comfort zonder weekprogramma',
  'Comfort for a room without a week program. With a week program, Comfort is its warmest temperature.': 'Comfort van een ruimte zonder weekprogramma. Met een weekprogramma is Comfort de warmste temperatuur daarvan.',
  'Night without a week program': 'Nacht zonder weekprogramma',
  'Night for a room without a week program. With a week program, Night is its coolest temperature.': 'Nacht van een ruimte zonder weekprogramma. Met een weekprogramma is Nacht de koelste temperatuur daarvan.',
  'Pause after a window opens': 'Pauze nadat een raam opengaat',
  'Minutes a window must stay open before a room pauses, so airing briefly does not stop the heating. A paused room still protects against frost.': 'Minuten dat een raam open moet blijven voordat een ruimte pauzeert, zodat kort luchten de verwarming niet stopt. Een gepauzeerde ruimte blijft beschermd tegen vorst.',
  'Pause after a door opens': 'Pauze nadat een deur opengaat',
  'The same for doors, usually longer, so letting the dog out or walking through the front door does not stop the heating. Default 5 minutes.': 'Hetzelfde voor deuren, meestal langer, zodat de hond uitlaten of door de voordeur lopen de verwarming niet stopt. Standaard 5 minuten.',
  'Length of a manual change': 'Duur van een handmatige wijziging',
  'A new temperature on the thermostat lasts until the next switch point of the room\'s week program. A room without a week program keeps it this many minutes, then follows its plan again.': 'Een nieuwe temperatuur op de thermostaat geldt tot het volgende schakelpunt van het weekprogramma van de ruimte. Een ruimte zonder weekprogramma houdt hem zoveel minuten vast en volgt daarna weer haar plan.',
  'Choose how the house is heated.': 'Kies hoe het huis wordt verwarmd.',
  'House mode': 'Huismodus', 'Automatic': 'Automatisch', 'At home': 'Thuis', 'Away': 'Afwezig', 'Holiday': 'Vakantie',
  'The people you set under Presence decide.': 'De mensen die je bij Aanwezigheid instelt, bepalen het.',
  'Always the week programs.': 'Altijd de weekprogramma\'s.',
  'Every room at most the away temperature.': 'Elke ruimte hoogstens de afwezigheidstemperatuur.',
  'From now until the day and time below.': 'Vanaf nu tot de dag en tijd hieronder.',
  'Holiday ends': 'Vakantie eindigt',
  'Only for Holiday: the day and time you are back. At most a year ahead.': 'Alleen voor Vakantie: dag en tijd waarop je terug bent. Hoogstens een jaar vooruit.',
  'Planned holidays': 'Geplande vakanties',
  'On holiday every room stays at most the temperature on holiday and the house is warm again when you are back; then the house mode is as before. Holidays that overlap become one.': 'Op vakantie blijft elke ruimte hoogstens op de temperatuur op vakantie en is het huis weer warm als je terugkomt; daarna staat de huismodus weer zoals ervoor. Vakanties die overlappen, worden één vakantie.',
  'Plan a holiday': 'Vakantie plannen', 'Holiday {n}': 'Vakantie {n}', 'Remove holiday {n}': 'Vakantie {n} verwijderen',
  'Starts': 'Begint', 'Ends (back home)': 'Eindigt (weer thuis)', 'At most 8 holidays can be planned.': 'Er kunnen hoogstens 8 vakanties gepland worden.',
  'Temperature on holiday': 'Temperatuur op vakantie',
  'Every room stays at most this warm during a holiday (5–25 °C; frost protection always stays on). Until you change it, it is the temperature when nobody is home.': 'Elke ruimte blijft tijdens een vakantie hoogstens zo warm (5–25 °C; de vorstbeveiliging blijft altijd aan). Tot je hem verandert, is dit de temperatuur als niemand thuis is.',
  'Choose the room whose window and door contacts you want to change.': 'Kies de ruimte waarvan je de raam- en deurcontacten wilt wijzigen.',
  'Window contacts: {n} · door contacts: {d}': 'Raamcontacten: {n} · deurcontacten: {d}', 'No window or door contacts': 'Geen raam- of deurcontacten',
  'When a window has been open for {delay}, or a door for {door_delay}, the room pauses: it drops to frost protection (8 °C) and asks for no heat. When all are closed again, it follows its program. Remove all sensors to switch this off for the room.': 'Staat een raam {delay} open, of een deur {door_delay}, dan pauzeert de ruimte: ze zakt naar vorstbeveiliging (8 °C) en vraagt geen warmte. Zijn ze allemaal weer dicht, dan volgt ze haar programma. Haal alle sensoren weg om dit voor de ruimte uit te zetten.',
  'Window contacts': 'Raamcontacten', 'Door contacts': 'Deurcontacten',
  'Binary sensors of the class window, door, opening or garage door, of any brand (Zigbee, Z-Wave, Shelly, Bluetooth …). Up to 8 windows and doors together.': 'Binaire sensoren van het type raam, deur, opening of garagedeur, van elk merk (Zigbee, Z-Wave, Shelly, Bluetooth …). Tot 8 ramen en deuren samen.',
  'Doors you open often for a moment (front door, back door, the door to the garden). They pause the room only after the longer door delay. A sensor is a window or a door, not both.': 'Deuren die je vaak even opendoet (voordeur, achterdeur, de deur naar de tuin). Ze pauzeren de ruimte pas na de langere deurvertraging. Een sensor is een raam of een deur, niet allebei.',
  'Search by name': 'Zoek op naam',
  // errors
  'Choose a person, group, zone or switch that exists.': 'Kies een bestaande persoon, groep, zone of schakelaar.',
  'Enter a whole number within the limits.': 'Vul een heel getal binnen de grenzen in.',
  'Choose an away temperature between 5 and 25 °C.': 'Kies een afwezigheidstemperatuur tussen 5 en 25 °C.',
  'The E32 did not save the away temperature ({error}), so nothing was saved. Check that the E32 is online and try again.': 'De E32 heeft de afwezigheidstemperatuur niet opgeslagen ({error}), dus er is niets opgeslagen. Controleer of de E32 online is en probeer het opnieuw.',
  'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again.': 'Hiervoor is nieuwere E32-firmware nodig. Werk de E32 eerst bij (Instellingen → Updates → OpenThermostat E32 Firmware) en probeer het opnieuw.',
  'Enter a temperature between 5 and 30 °C.': 'Vul een temperatuur tussen 5 en 30 °C in.',
  'Choose at most eight different sensors.': 'Kies hoogstens acht verschillende sensoren.',
  'Choose window, door or opening sensors only.': 'Kies alleen raam-, deur- of openingssensoren.',
  'A sensor is a window or a door, not both: choose it in one of the two fields.': 'Een sensor is een raam of een deur, niet allebei: kies hem in een van de twee velden.',
  'Choose one of the modes.': 'Kies een van de modi.', 'Choose the day and time the holiday ends.': 'Kies dag en tijd waarop de vakantie eindigt.',
  'Choose a moment in the future, at most a year ahead.': 'Kies een moment in de toekomst, hoogstens een jaar vooruit.',
  'This E32 software does not know this mode. Update the E32 first.': 'Deze E32-software kent deze modus niet. Werk eerst de E32 bij.',
  'The E32 did not accept this ({error}). Try again.': 'De E32 heeft dit niet aangenomen ({error}). Probeer het opnieuw.',
  'This holiday is already over. Choose an end in the future.': 'Deze vakantie is al voorbij. Kies een einde in de toekomst.',
  'Choose an end at most a year ahead.': 'Kies een einde hoogstens een jaar vooruit.',
  'At most 8 holidays can be planned. Remove one first.': 'Er kunnen hoogstens 8 vakanties gepland worden. Verwijder er eerst een.',
  'The holiday must end after it starts.': 'De vakantie moet eindigen na het begin.',
  'The E32 clock is not set yet, so a holiday date cannot be used. Try again in a minute.': 'De klok van de E32 is nog niet gelijkgezet, dus een vakantiedatum kan nog niet. Probeer het over een minuut opnieuw.',
  'A holiday was changed elsewhere meanwhile. Reload the page and try again.': 'Een vakantie is intussen elders gewijzigd. Laad de pagina opnieuw en probeer het opnieuw.',
  'Holiday {line}: choose when it starts and when it ends.': 'Vakantie {line}: kies wanneer die begint en wanneer die eindigt.',
  'Holiday {line}: it must end after it starts.': 'Vakantie {line}: die moet eindigen na het begin.',
  'Holiday {line} is already over. Choose an end in the future.': 'Vakantie {line} is al voorbij. Kies een einde in de toekomst.',
  'Holiday {line}: choose an end at most a year ahead.': 'Vakantie {line}: kies een einde hoogstens een jaar vooruit.',
  'Choose a temperature between 5 and 25 °C.': 'Kies een temperatuur tussen 5 en 25 °C.',
  'This room is no longer on the E32.': 'Deze ruimte staat niet meer op de E32.'},
 pl: {
  'House': 'Dom', 'Settings for the whole house: who is home, the house mode and holiday, and the defaults for rooms.': 'Ustawienia dla całego domu: kto jest w domu, tryb domu i urlop oraz domyślne ustawienia pomieszczeń.',
  'Presence and away temperature': 'Obecność i temperatura podczas nieobecności', 'Room defaults': 'Domyślne ustawienia pomieszczeń',
  'House mode and holiday': 'Tryb domu i urlop', 'Window and door contacts': 'Czujniki okien i drzwi',
  'Nobody chosen yet': 'Nikogo jeszcze nie wybrano', 'Away after {n} min': 'Nieobecność po {n} min',
  'Away after {n} min · {temperature} when nobody is home': 'Nieobecność po {n} min · {temperature}, gdy nikogo nie ma w domu',
  'Without a week program: comfort {comfort}, night {night}': 'Bez programu tygodniowego: komfort {comfort}, noc {night}',
  'Pause after a window {window} min, after a door {door} min · a manual change lasts {minutes} min': 'Przerwa po oknie {window} min, po drzwiach {door} min · ręczna zmiana trwa {minutes} min',
  'Next holiday: {from} – {until}': 'Następny urlop: {from} – {until}', 'No holidays planned.': 'Brak zaplanowanych urlopów.',
  'The E32 does not report the house mode yet.': 'E32 nie zgłasza jeszcze trybu domu.',
  'Rooms with contacts: {rooms} · sensors: {sensors}': 'Pomieszczenia z czujnikami: {rooms} · czujniki: {sensors}',
  'No contacts yet': 'Brak jeszcze czujników', 'Add a room first.': 'Najpierw dodaj pomieszczenie.',
  'In the house mode Automatic the rooms go to the away temperature when everyone is away. Someone home, or someone whose place is not known, keeps the house warm.': 'W trybie domu Automatyczny pomieszczenia przechodzą na temperaturę nieobecności, gdy wszyscy wyszli. Ktoś w domu albo ktoś, kogo położenie jest nieznane, utrzymuje ciepło w domu.',
  'Who lives here': 'Kto tu mieszka',
  'Optional. The people of the house, or a group, zone (for example zone.home), device tracker or switch that is on while someone is home.': 'Opcjonalnie. Domownicy albo grupa, strefa (na przykład zone.home), lokalizator urządzenia lub przełącznik, który jest włączony, gdy ktoś jest w domu.',
  'Away after': 'Nieobecność po',
  'Minutes everyone must be away before the house counts as away, so a short errand does not cool the house. 0: at once.': 'Minuty, przez które wszyscy muszą być poza domem, zanim dom zostanie uznany za pusty, aby krótkie wyjście nie wychładzało domu. 0: od razu.',
  'Temperature when nobody is home': 'Temperatura, gdy nikogo nie ma w domu',
  'Every room stays at most this warm while everyone is away, in house mode Away and on holiday (5–25 °C; frost protection always stays on).': 'Każde pomieszczenie jest najwyżej tak ciepłe, gdy wszyscy wyszli, w trybie domu Nieobecność i podczas urlopu (5–25 °C; ochrona przed mrozem zawsze działa).',
  'For every room: the temperatures of a room without a week program, how long a window or door may be open before the room pauses, and how long a change on a thermostat lasts. A room\'s own settings (Configure → Rooms) take precedence.': 'Dla każdego pomieszczenia: temperatury pomieszczenia bez programu tygodniowego, jak długo okno lub drzwi mogą być otwarte, zanim pomieszczenie wstrzyma ogrzewanie, oraz jak długo obowiązuje zmiana na termostacie. Własne ustawienia pomieszczenia (Konfiguruj → Pomieszczenia) mają pierwszeństwo.',
  'Comfort without a week program': 'Komfort bez programu tygodniowego',
  'Comfort for a room without a week program. With a week program, Comfort is its warmest temperature.': 'Komfort dla pomieszczenia bez programu tygodniowego. Z programem tygodniowym Komfort to jego najcieplejsza temperatura.',
  'Night without a week program': 'Noc bez programu tygodniowego',
  'Night for a room without a week program. With a week program, Night is its coolest temperature.': 'Noc dla pomieszczenia bez programu tygodniowego. Z programem tygodniowym Noc to jego najchłodniejsza temperatura.',
  'Pause after a window opens': 'Przerwa po otwarciu okna',
  'Minutes a window must stay open before a room pauses, so airing briefly does not stop the heating. A paused room still protects against frost.': 'Liczba minut, przez które okno musi pozostać otwarte, zanim pomieszczenie wstrzyma ogrzewanie, aby krótkie wietrzenie nie zatrzymywało ogrzewania. Wstrzymane pomieszczenie nadal jest chronione przed mrozem.',
  'Pause after a door opens': 'Przerwa po otwarciu drzwi',
  'The same for doors, usually longer, so letting the dog out or walking through the front door does not stop the heating. Default 5 minutes.': 'To samo dla drzwi, zwykle dłużej, aby wypuszczenie psa lub przejście przez drzwi wejściowe nie zatrzymywało ogrzewania. Domyślnie 5 minut.',
  'Length of a manual change': 'Czas trwania ręcznej zmiany',
  'A new temperature on the thermostat lasts until the next switch point of the room\'s week program. A room without a week program keeps it this many minutes, then follows its plan again.': 'Nowa temperatura na termostacie obowiązuje do następnego punktu przełączenia programu tygodniowego pomieszczenia. Pomieszczenie bez programu tygodniowego utrzymuje ją przez tyle minut, a potem znowu stosuje swój plan.',
  'Choose how the house is heated.': 'Wybierz, jak ogrzewany jest dom.',
  'House mode': 'Tryb domu', 'Automatic': 'Automatyczny', 'At home': 'W domu', 'Away': 'Nieobecność', 'Holiday': 'Urlop',
  'The people you set under Presence decide.': 'Decydują osoby ustawione w Obecności.',
  'Always the week programs.': 'Zawsze programy tygodniowe.',
  'Every room at most the away temperature.': 'Każde pomieszczenie najwyżej do temperatury nieobecności.',
  'From now until the day and time below.': 'Od teraz do dnia i godziny poniżej.',
  'Holiday ends': 'Koniec urlopu',
  'Only for Holiday: the day and time you are back. At most a year ahead.': 'Tylko dla Urlopu: dzień i godzina powrotu. Najwyżej rok naprzód.',
  'Planned holidays': 'Zaplanowane urlopy',
  'On holiday every room stays at most the temperature on holiday and the house is warm again when you are back; then the house mode is as before. Holidays that overlap become one.': 'Podczas urlopu każde pomieszczenie ma najwyżej temperaturę urlopową, a dom jest znów ciepły, gdy wracasz; potem tryb domu jest taki jak wcześniej. Nakładające się urlopy stają się jednym.',
  'Plan a holiday': 'Zaplanuj urlop', 'Holiday {n}': 'Urlop {n}', 'Remove holiday {n}': 'Usuń urlop {n}',
  'Starts': 'Początek', 'Ends (back home)': 'Koniec (powrót do domu)', 'At most 8 holidays can be planned.': 'Można zaplanować najwyżej 8 urlopów.',
  'Temperature on holiday': 'Temperatura podczas urlopu',
  'Every room stays at most this warm during a holiday (5–25 °C; frost protection always stays on). Until you change it, it is the temperature when nobody is home.': 'Podczas urlopu każde pomieszczenie jest najwyżej tak ciepłe (5–25 °C; ochrona przed mrozem zawsze działa). Dopóki jej nie zmienisz, jest to temperatura, gdy nikogo nie ma w domu.',
  'Choose the room whose window and door contacts you want to change.': 'Wybierz pomieszczenie, którego czujniki okien i drzwi chcesz zmienić.',
  'Window contacts: {n} · door contacts: {d}': 'Czujniki okien: {n} · czujniki drzwi: {d}', 'No window or door contacts': 'Brak czujników okien i drzwi',
  'When a window has been open for {delay}, or a door for {door_delay}, the room pauses: it drops to frost protection (8 °C) and asks for no heat. When all are closed again, it follows its program. Remove all sensors to switch this off for the room.': 'Gdy okno jest otwarte przez {delay} lub drzwi przez {door_delay}, pomieszczenie wstrzymuje ogrzewanie: spada do ochrony przed mrozem (8 °C) i nie żąda ciepła. Gdy wszystkie są znów zamknięte, wraca do swojego programu. Usuń wszystkie czujniki, aby wyłączyć to dla pomieszczenia.',
  'Window contacts': 'Czujniki okien', 'Door contacts': 'Czujniki drzwi',
  'Binary sensors of the class window, door, opening or garage door, of any brand (Zigbee, Z-Wave, Shelly, Bluetooth …). Up to 8 windows and doors together.': 'Czujniki binarne klasy okno, drzwi, otwarcie lub brama garażowa, dowolnej marki (Zigbee, Z-Wave, Shelly, Bluetooth …). Łącznie do 8 okien i drzwi.',
  'Doors you open often for a moment (front door, back door, the door to the garden). They pause the room only after the longer door delay. A sensor is a window or a door, not both.': 'Drzwi, które często otwierasz na chwilę (drzwi wejściowe, tylne, do ogrodu). Wstrzymują pomieszczenie dopiero po dłuższym opóźnieniu dla drzwi. Czujnik jest oknem albo drzwiami, nie jednym i drugim.',
  'Search by name': 'Szukaj po nazwie',
  'Choose a person, group, zone or switch that exists.': 'Wybierz istniejącą osobę, grupę, strefę lub przełącznik.',
  'Enter a whole number within the limits.': 'Podaj liczbę całkowitą w dozwolonym zakresie.',
  'Choose an away temperature between 5 and 25 °C.': 'Wybierz temperaturę nieobecności od 5 do 25 °C.',
  'The E32 did not save the away temperature ({error}), so nothing was saved. Check that the E32 is online and try again.': 'E32 nie zapisał temperatury nieobecności ({error}), więc nic nie zapisano. Sprawdź, czy E32 jest online, i spróbuj ponownie.',
  'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again.': 'To wymaga nowszego oprogramowania E32. Najpierw zaktualizuj E32 (Ustawienia → Aktualizacje → OpenThermostat E32 Firmware), a potem spróbuj ponownie.',
  'Enter a temperature between 5 and 30 °C.': 'Podaj temperaturę od 5 do 30 °C.',
  'Choose at most eight different sensors.': 'Wybierz najwyżej osiem różnych czujników.',
  'Choose window, door or opening sensors only.': 'Wybierz tylko czujniki okien, drzwi lub otwarcia.',
  'A sensor is a window or a door, not both: choose it in one of the two fields.': 'Czujnik jest oknem albo drzwiami, nie jednym i drugim: wybierz go w jednym z dwóch pól.',
  'Choose one of the modes.': 'Wybierz jeden z trybów.', 'Choose the day and time the holiday ends.': 'Wybierz dzień i godzinę końca urlopu.',
  'Choose a moment in the future, at most a year ahead.': 'Wybierz moment w przyszłości, najwyżej rok naprzód.',
  'This E32 software does not know this mode. Update the E32 first.': 'To oprogramowanie E32 nie zna tego trybu. Najpierw zaktualizuj E32.',
  'The E32 did not accept this ({error}). Try again.': 'E32 nie przyjął tej zmiany ({error}). Spróbuj ponownie.',
  'This holiday is already over. Choose an end in the future.': 'Ten urlop już minął. Wybierz koniec w przyszłości.',
  'Choose an end at most a year ahead.': 'Wybierz koniec najwyżej rok naprzód.',
  'At most 8 holidays can be planned. Remove one first.': 'Można zaplanować najwyżej 8 urlopów. Najpierw usuń jeden.',
  'The holiday must end after it starts.': 'Urlop musi się kończyć po rozpoczęciu.',
  'The E32 clock is not set yet, so a holiday date cannot be used. Try again in a minute.': 'Zegar E32 nie jest jeszcze ustawiony, więc data urlopu nie może być użyta. Spróbuj ponownie za minutę.',
  'A holiday was changed elsewhere meanwhile. Reload the page and try again.': 'Urlop został w międzyczasie zmieniony w innym miejscu. Wczytaj stronę ponownie i spróbuj jeszcze raz.',
  'Holiday {line}: choose when it starts and when it ends.': 'Urlop {line}: wybierz, kiedy się zaczyna i kiedy się kończy.',
  'Holiday {line}: it must end after it starts.': 'Urlop {line}: musi się kończyć po rozpoczęciu.',
  'Holiday {line} is already over. Choose an end in the future.': 'Urlop {line} już minął. Wybierz koniec w przyszłości.',
  'Holiday {line}: choose an end at most a year ahead.': 'Urlop {line}: wybierz koniec najwyżej rok naprzód.',
  'Choose a temperature between 5 and 25 °C.': 'Wybierz temperaturę od 5 do 25 °C.',
  'This room is no longer on the E32.': 'Tego pomieszczenia nie ma już na E32.'}};
// The sentence of each code settings_house.py may answer (the codes of the options steps).
const ERRORS = {
 presence_entity_invalid: 'Choose a person, group, zone or switch that exists.',
 whole_number_invalid: 'Enter a whole number within the limits.',
 comfort_away_temperature_invalid: 'Choose an away temperature between 5 and 25 °C.',
 away_temperature_not_saved: 'The E32 did not save the away temperature ({error}), so nothing was saved. Check that the E32 is online and try again.',
 away_temperature_update_required: 'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again.',
 temperature_invalid: 'Enter a temperature between 5 and 30 °C.',
 contacts_invalid: 'Choose at most eight different sensors.',
 not_contact_sensor: 'Choose window, door or opening sensors only.',
 contact_window_and_door: 'A sensor is a window or a door, not both: choose it in one of the two fields.',
 house_mode_invalid: 'Choose one of the modes.',
 house_holiday_date_needed: 'Choose the day and time the holiday ends.',
 house_holiday_date_invalid: 'Choose a moment in the future, at most a year ahead.',
 house_mode_update_required: 'This E32 software does not know this mode. Update the E32 first.',
 house_mode_not_saved: 'The E32 did not accept this ({error}). Try again.',
 house_holiday_not_saved: 'The E32 did not accept this ({error}). Try again.',
 house_holiday_past: 'This holiday is already over. Choose an end in the future.',
 house_holiday_too_far: 'Choose an end at most a year ahead.',
 house_holiday_too_many: 'At most 8 holidays can be planned. Remove one first.',
 house_holiday_order: 'The holiday must end after it starts.',
 house_holiday_no_clock: 'The E32 clock is not set yet, so a holiday date cannot be used. Try again in a minute.',
 house_holiday_changed: 'A holiday was changed elsewhere meanwhile. Reload the page and try again.',
 house_holiday_line_dates_needed: 'Holiday {line}: choose when it starts and when it ends.',
 house_holiday_line_order: 'Holiday {line}: it must end after it starts.',
 house_holiday_line_past: 'Holiday {line} is already over. Choose an end in the future.',
 house_holiday_line_too_far: 'Holiday {line}: choose an end at most a year ahead.',
 house_holiday_temperature_invalid: 'Choose a temperature between 5 and 25 °C.',
 house_mode_unavailable: 'The E32 does not report the house mode yet.',
 comfort_no_rooms: 'This room is no longer on the E32.'};

const PARTS = {presence: 'Presence and away temperature', defaults: 'Room defaults', mode: 'House mode and holiday', contacts: 'Window and door contacts'};
const MODES = {auto: ['Automatic', 'The people you set under Presence decide.'], home: ['At home', 'Always the week programs.'],
 away: ['Away', 'Every room at most the away temperature.'], holiday: ['Holiday', 'From now until the day and time below.']};
const FIELDS = {presence: ['presence_entities', 'away_delay', 'away_temperature'],
 defaults: ['comfort_temperature', 'eco_temperature', 'contact_delay', 'door_delay', 'override_minutes'],
 mode: ['house_mode', 'holiday_until', 'holidays', 'holiday_temperature'], room: ['contacts', 'door_contacts']};
const CONTACT_CLASSES = ['window', 'door', 'opening', 'garage_door'];
const PRESENCE_DOMAINS = ['person', 'group', 'zone', 'device_tracker', 'binary_sensor', 'input_boolean'];

const copy = v => JSON.parse(JSON.stringify(v));
const number = (v, lang) => Number(v).toLocaleString(lang, {maximumFractionDigits: 1});
const degrees = (v, lang) => `${number(v, lang)} °C`;
const nb = text => String(text).replace(/ (°C|min)(?=$|[\s·,.;)])/g, ' $1');
const when = (text, lang) => {
 const d = new Date(text);
 return Number.isNaN(d.getTime()) ? text : d.toLocaleString(lang, {day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'});
};
const part = item => String(item || '').split('/')[0];
// A local moment as the date-and-time field holds it, `days` from now at `hour`:00.
const ahead = (days, hour) => {
 const d = new Date(); d.setDate(d.getDate() + days); d.setHours(hour, 0, 0, 0);
 const p = n => String(n).padStart(2, '0');
 return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:00`;
};

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

// The planned holidays: from and until per holiday; add and remove.
function holidaysField(ctx) {
 return o => {
  const {h, button, shell} = ctx.kit, t = ctx.t;
  let list = copy(o.value || []);
  const body = h('div', {class: 'hh-holidays'});
  const api = shell('holidays', o, body, false);
  const emit = () => o.onChange?.(copy(list));
  const draw = focus => {
   const rows = list.map((holiday, i) => {
    const n = i + 1, input = (key, label) => {
     const el = h('input', {type: 'datetime-local', class: 'input', step: 60, disabled: o.disabled, 'data-fk': `holidays:${i}:${key}`});
     el.value = holiday[key] || '';
     el.addEventListener('input', () => { holiday[key] = el.value; emit(); });
     return h('label', {class: 'hh-moment'}, h('span', {class: 'help', text: label}), el);
    };
    return h('div', {class: 'hh-holiday', role: 'group', 'aria-label': t('Holiday {n}', {n}), 'data-holiday': i},
     input('from', t('Starts')), input('until', t('Ends (back home)')),
     o.disabled ? null : button('', () => { list.splice(i, 1); draw(true); emit(); }, 'icon remove',
      {'aria-label': t('Remove holiday {n}', {n}), title: t('Remove holiday {n}', {n}), 'data-remove': ''}));
   });
   const parts = rows.length ? rows : [h('p', {class: 'hh-empty', text: t('No holidays planned.')})];
   if (!o.disabled) {
    if (list.length >= 8) parts.push(h('p', {class: 'help', text: t('At most 8 holidays can be planned.')}));
    else parts.push(button(t('Plan a holiday'), () => { list.push({from: ahead(1, 10), until: ahead(8, 18)}); draw('last'); emit(); }, 'outlined hh-add', {'data-add-holiday': ''}));
   }
   body.replaceChildren(...parts);
   if (focus === 'last') body.querySelector('.hh-holiday:last-of-type input')?.focus();
   else if (focus) body.querySelector('[data-add-holiday]')?.focus();
  };
  draw();
  api.target = () => body.querySelector('input, button');
  api.describe();
  return api;
 };
}

/* ---- the screens ---- */
function overview(ctx) {
 const {h} = ctx.kit, t = ctx.t, m = ctx.model, lang = ctx.lang;
 const names = (m.presence.presence_entities || []).map(e => ctx.hass?.states?.[e]?.attributes?.friendly_name || e);
 const presence = [names.length ? names.join(', ') : t('Nobody chosen yet'),
  m.presence.has_away && m.presence.away_temperature != null
   ? t('Away after {n} min · {temperature} when nobody is home', {n: m.presence.away_delay, temperature: degrees(m.presence.away_temperature, lang)})
   : t('Away after {n} min', {n: m.presence.away_delay})];
 const d = m.defaults;
 const defaults = [t('Without a week program: comfort {comfort}, night {night}', {comfort: degrees(d.comfort_temperature, lang), night: degrees(d.eco_temperature, lang)}),
  t('Pause after a window {window} min, after a door {door} min · a manual change lasts {minutes} min',
   {window: number(d.contact_delay, lang), door: number(d.door_delay, lang), minutes: d.override_minutes})];
 let mode = [t('The E32 does not report the house mode yet.')];
 if (m.mode) {
  mode = [t(MODES[m.mode.house_mode]?.[0] || 'Automatic')];
  if (m.mode.planning) mode.push(m.mode.holidays?.length
   ? t('Next holiday: {from} – {until}', {from: when(m.mode.holidays[0].from, lang), until: when(m.mode.holidays[0].until, lang)}) : t('No holidays planned.'));
 }
 const c = m.contacts;
 const contacts = [!c.any_room ? t('Add a room first.') : c.rooms ? t('Rooms with contacts: {rooms} · sensors: {sensors}', {rooms: c.rooms, sensors: c.sensors}) : t('No contacts yet')];
 return h('div', {class: 'hh-overview'}, 
  h('p', {class: 'help hh-intro', text: t('Settings for the whole house: who is home, the house mode and holiday, and the defaults for rooms.')}),
  h('div', {class: 'hh-rows'},
   ctx.row({label: t(PARTS.presence), summary: presence.map(nb), route: '#house/presence', data: {part: 'presence'}}),
   ctx.row({label: t(PARTS.defaults), summary: defaults.map(nb), route: '#house/defaults', data: {part: 'defaults'}}),
   ctx.row({label: t(PARTS.mode), summary: mode, route: '#house/mode', data: {part: 'mode'}}),
   ctx.row({label: t(PARTS.contacts), summary: contacts, route: '#house/contacts', data: {part: 'contacts'}})));
}

function presence(ctx) {
 const {h} = ctx.kit, t = ctx.t;
 return h('div', {class: 'fields'}, 
  h('p', {class: 'help hh-intro', text: t('In the house mode Automatic the rooms go to the away temperature when everyone is away. Someone home, or someone whose place is not known, keeps the house warm.')}),
  ctx.field('entity', 'presence_entities', {label: t('Who lives here'), multiple: true, domains: PRESENCE_DOMAINS, placeholder: t('Search by name'),
   help: t('Optional. The people of the house, or a group, zone (for example zone.home), device tracker or switch that is on while someone is home.')}),
  ctx.field('number', 'away_delay', {label: t('Away after'), unit: 'min', step: 1, min: 0, max: 240,
   help: t('Minutes everyone must be away before the house counts as away, so a short errand does not cool the house. 0: at once.')}),
  ctx.model.has_away ? ctx.field('number', 'away_temperature', {label: t('Temperature when nobody is home'), unit: '°C', step: 0.5, min: 5, max: 25,
   help: t('Every room stays at most this warm while everyone is away, in house mode Away and on holiday (5–25 °C; frost protection always stays on).')}) : null);
}

function defaults(ctx) {
 const {h} = ctx.kit, t = ctx.t;
 return h('div', {class: 'fields'}, 
  h('p', {class: 'help hh-intro', text: t('For every room: the temperatures of a room without a week program, how long a window or door may be open before the room pauses, and how long a change on a thermostat lasts. A room\'s own settings (Configure → Rooms) take precedence.')}),
  ctx.field('number', 'comfort_temperature', {label: t('Comfort without a week program'), unit: '°C', step: 0.5, min: 5, max: 30,
   help: t('Comfort for a room without a week program. With a week program, Comfort is its warmest temperature.')}),
  ctx.field('number', 'eco_temperature', {label: t('Night without a week program'), unit: '°C', step: 0.5, min: 5, max: 30,
   help: t('Night for a room without a week program. With a week program, Night is its coolest temperature.')}),
  ctx.field('number', 'contact_delay', {label: t('Pause after a window opens'), unit: 'min', step: 0.5, min: 0, max: 30,
   help: t('Minutes a window must stay open before a room pauses, so airing briefly does not stop the heating. A paused room still protects against frost.')}),
  ctx.field('number', 'door_delay', {label: t('Pause after a door opens'), unit: 'min', step: 0.5, min: 0, max: 30,
   help: t('The same for doors, usually longer, so letting the dog out or walking through the front door does not stop the heating. Default 5 minutes.')}),
  ctx.field('number', 'override_minutes', {label: t('Length of a manual change'), unit: 'min', step: 1, min: 1, max: 1440,
   help: t('A new temperature on the thermostat lasts until the next switch point of the room\'s week program. A room without a week program keeps it this many minutes, then follows its plan again.')}));
}

function mode(ctx) {
 const {h} = ctx.kit, t = ctx.t, m = ctx.model;
 if (m.unavailable) return h('div', {}, ctx.notice(t('The E32 does not report the house mode yet.'), 'info'));
 const until = ctx.field(momentField(ctx), 'holiday_until', {label: t('Holiday ends'),
  help: t('Only for Holiday: the day and time you are back. At most a year ahead.')});
 until.hidden = ctx.values.house_mode !== 'holiday';
 const parts = [h('p', {class: 'help hh-intro', text: t('Choose how the house is heated.')}),
  ctx.field('radio', 'house_mode', {label: t('House mode'), options: m.modes.map(value => ({value, label: t(MODES[value][0]), help: t(MODES[value][1])})),
   onChange: v => { until.hidden = v !== 'holiday'; }}),
  until];
 if (m.planning) {
  parts.push(ctx.field(holidaysField(ctx), 'holidays', {label: t('Planned holidays'),
   help: t('On holiday every room stays at most the temperature on holiday and the house is warm again when you are back; then the house mode is as before. Holidays that overlap become one.')}));
  parts.push(ctx.field('number', 'holiday_temperature', {label: t('Temperature on holiday'), unit: '°C', step: 0.5, min: 5, max: 25,
   help: t('Every room stays at most this warm during a holiday (5–25 °C; frost protection always stays on). Until you change it, it is the temperature when nobody is home.')}));
 }
 return h('div', {class: 'fields'}, ...parts);
}

function contactRooms(ctx) {
 const {h} = ctx.kit, t = ctx.t;
 const rows = ctx.model.rooms.map(room => ctx.row({label: room.name, route: '#house/contacts/' + encodeURIComponent(room.id), data: {room: room.id},
  summary: [room.windows || room.doors ? t('Window contacts: {n} · door contacts: {d}', {n: room.windows, d: room.doors}) : t('No window or door contacts')]}));
 return h('div', {class: 'hh-overview'}, 
  h('p', {class: 'help hh-intro', text: t('Choose the room whose window and door contacts you want to change.')}),
  rows.length ? h('div', {class: 'hh-rows'}, ...rows) : ctx.notice(t('Add a room first.')));
}

function roomContacts(ctx) {
 const {h} = ctx.kit, t = ctx.t, m = ctx.model;
 const contact = other => (st, eid) => CONTACT_CLASSES.includes(st?.attributes?.device_class) && !(ctx.values[other] || []).includes(eid);
 return h('div', {class: 'fields'}, 
  h('p', {class: 'help hh-intro', text: nb(t('When a window has been open for {delay}, or a door for {door_delay}, the room pauses: it drops to frost protection (8 °C) and asks for no heat. When all are closed again, it follows its program. Remove all sensors to switch this off for the room.', {delay: m.delay, door_delay: m.door_delay}))}),
  ctx.field('entity', 'contacts', {label: t('Window contacts'), multiple: true, domains: ['binary_sensor'], filter: contact('door_contacts'), placeholder: t('Search by name'),
   help: t('Binary sensors of the class window, door, opening or garage door, of any brand (Zigbee, Z-Wave, Shelly, Bluetooth …). Up to 8 windows and doors together.')}),
  ctx.field('entity', 'door_contacts', {label: t('Door contacts'), multiple: true, domains: ['binary_sensor'], filter: contact('contacts'), placeholder: t('Search by name'),
   help: t('Doors you open often for a moment (front door, back door, the door to the garden). They pause the room only after the longer door delay. A sensor is a window or a door, not both.')}));
}

const STYLE = `.hh-intro{padding:12px 0 4px}.hh-rows{display:flex;flex-direction:column;margin:8px -16px 0}.hh-rows .row{margin:0;width:100%}
.hh-holidays{display:grid;gap:8px;max-width:560px}.hh-empty{color:var(--ot-muted)}.hh-add{justify-self:start}
.hh-holiday{display:flex;flex-wrap:wrap;align-items:flex-end;gap:8px 12px;padding:10px 12px;border:1px solid var(--ot-divider);border-radius:8px}
.hh-moment{display:grid;gap:4px;flex:1 1 200px}.hh-moment .input{width:100%}.hh-holiday .remove{margin-left:auto}
@media(max-width:420px){.hh-rows{margin-left:-12px;margin-right:-12px}}`;

(window.OpenThermostatSettingsSections ||= []).push(['house', {
 title: (model, item) => PARTS[part(item)] || 'House',
 texts: TEXTS,
 errors: ERRORS,
 // The contacts of a room open from the list of rooms; back goes there.
 parent: item => (part(item) === 'contacts' && item.includes('/') ? {route: '#house/contacts', label: PARTS.contacts} : null),
 values: model => {
  const keys = 'room' in model ? FIELDS.room : 'modes' in model ? FIELDS.mode : 'away_delay' in model ? FIELDS.presence : 'override_minutes' in model ? FIELDS.defaults : [];
  return Object.fromEntries(keys.filter(k => k in model).map(k => [k, copy(model[k])]));
 },
 // Only what differs from the screen as shown.
 toSave: (values, model) => Object.fromEntries(Object.entries(values).filter(([k, v]) => JSON.stringify(v) !== JSON.stringify(model[k]))),
 shown: (key, value, t) => {
  if (key === 'house_mode') return t(MODES[value]?.[0] || value);
  if (key === 'holidays') return (value || []).map(x => `${x.from} – ${x.until}`).join(', ');
  return undefined;
 },
 // The style of this section goes last: the first field keeps the look of the kit.
 render: ctx => {
  const p = part(ctx.item);
  const el = ctx.item == null ? overview(ctx) : p === 'presence' ? presence(ctx) : p === 'defaults' ? defaults(ctx) : p === 'mode' ? mode(ctx)
   : ctx.item.includes('/') ? roomContacts(ctx) : contactRooms(ctx);
  el.append(ctx.kit.h('style', {text: STYLE}));
  return el;
 }
}]);
