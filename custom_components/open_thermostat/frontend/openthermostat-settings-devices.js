/* The section Devices of the settings panel (1.4): the three blocks of the E32's page System → Devices on #devices (the
   Bluetooth sensors renamed and forgotten in one save, which restarts the E32; the Shelly devices with Remove for a
   device and for a gateway's valve; the boiler bus, read-only), #devices/shelly-add (add a Shelly device by its address,
   with its password: the E32 gets it, nothing shows it again) and #devices/valve-add (a valve of a BLU Gateway by its
   number). Backend settings_devices.py; the words are Configure's and the E32 page's. */
const TEXTS = {
 nl: {
  '{name} added.': '{name} toegevoegd.',
  '{name} removed.': '{name} verwijderd.',
  'Valves removed: {count}.': 'Kranen verwijderd: {count}.',
  'Valve {id}': 'Kraan {id}',
  'Bluetooth sensors': 'Bluetooth-sensoren',
  'Rename or forget them here and save them together: after saving, the E32 restarts once, about 30 seconds later, to use them. Pairing a new sensor (scan and key) is done on the E32\'s page System → Devices, next to the sensor. Which room a sensor measures is set per room under Rooms.': 'Geef ze hier een andere naam of vergeet ze en sla ze samen op: na opslaan start de E32 één keer opnieuw, ongeveer 30 seconden later, om ze te gebruiken. Een nieuwe sensor koppelen (zoeken en sleutel) doe je op de pagina Systeem → Apparaten van de E32, bij de sensor. Welke ruimte een sensor meet stel je per ruimte in onder Ruimtes.',
  'No Bluetooth sensor is paired with the E32 yet. Pair one on the E32\'s page System → Devices first.': 'Er is nog geen Bluetooth-sensor aan de E32 gekoppeld. Koppel er eerst een op de pagina Systeem → Apparaten van de E32.',
  'battery {value}': 'batterij {value}',
  'used by {rooms}': 'gebruikt door {rooms}',
  'no room uses it': 'geen ruimte gebruikt hem',
  'Name': 'Naam',
  'Bluetooth address {address}. At most 40 characters (fewer with special letters).': 'Bluetooth-adres {address}. Hoogstens 40 tekens (minder met bijzondere letters).',
  'Forget this sensor': 'Deze sensor vergeten',
  'The E32 stops reading it and deletes its key; to use it again, pair it again on the E32.': 'De E32 leest hem niet meer en wist zijn sleutel; om hem weer te gebruiken koppel je hem opnieuw op de E32.',
  'Shelly devices': 'Shelly-apparaten',
  'The Plug of the floor pump, The Pill with its temperature probes and the BLU Gateway of the radiator valves. The E32 talks to them itself over your home network, also without Home Assistant.': 'De plug van de vloerpomp, The Pill met zijn temperatuursondes en de BLU Gateway van de radiatorkranen. De E32 praat er zelf mee over je thuisnetwerk, ook zonder Home Assistant.',
  'No Shelly devices yet.': 'Nog geen Shelly-apparaten.',
  'room: {room}': 'ruimte: {room}',
  'Remove': 'Verwijderen',
  'Remove {name}?': '{name} verwijderen?',
  'The E32 stops reading and driving these valves. A valve in a room stays there until you remove it under Rooms → the room → Radiator valves.': 'De E32 leest en stuurt deze kranen niet meer. Een kraan in een ruimte blijft daar tot je hem verwijdert onder Ruimtes → de ruimte → Radiatorkranen.',
  'No valves yet.': 'Nog geen kranen.',
  'Add a valve': 'Kraan toevoegen',
  'Remove device': 'Apparaat verwijderen',
  'The E32 stops reading and switching the device. The valves of a BLU Gateway stay in their rooms until you remove them under Rooms.': 'De E32 leest en schakelt het apparaat niet meer. De kranen van een BLU Gateway blijven in hun ruimtes tot je ze onder Ruimtes verwijdert.',
  'Add a Shelly device': 'Shelly-apparaat toevoegen',
  'On the boiler bus': 'Op de ketelbus',
  'The devices the E32 hears on the boiler bus. There is nothing to set here.': 'De apparaten die de E32 op de ketelbus hoort. Hier valt niets in te stellen.',
  'The E32 has not reported them yet.': 'De E32 heeft ze nog niet gemeld.',
  'Nothing heard yet.': 'Nog niets gehoord.',
  'Device password': 'Wachtwoord van het apparaat',
  'The password you set in the Shelly app. It goes to the E32 only, which keeps a fingerprint of it; Home Assistant does not keep it. Leave it empty if the device has none.': 'Het wachtwoord dat je in de Shelly-app hebt ingesteld. Het gaat alleen naar de E32, die er een vingerafdruk van bewaart; Home Assistant bewaart het niet. Laat het leeg als het apparaat er geen heeft.',
  'IP address': 'IP-adres',
  'For example 192.168.1.40. When you save, the E32 asks the device who it is, which takes up to 16 seconds.': 'Bijvoorbeeld 192.168.1.40. Als je opslaat, vraagt de E32 het apparaat wie het is; dat duurt tot 16 seconden.',
  'What does it do?': 'Wat doet het?',
  'As the device says': 'Zoals het apparaat zegt',
  'The E32 asks the device what it is when you save.': 'De E32 vraagt het apparaat wat het is als je opslaat.',
  'The name the E32 and Home Assistant show, up to 32 characters.': 'De naam die de E32 en Home Assistant tonen, hoogstens 32 tekens.',
  'There is no BLU Gateway in the list yet. Add one first.': 'Er staat nog geen BLU Gateway in de lijst. Voeg er eerst een toe.',
  'The gateway the valve is paired with.': 'De gateway waaraan de kraan gekoppeld is.',
  'Valve number': 'Kraannummer',
  'The number the gateway gave the valve, from 200 to 299.': 'Het nummer dat de gateway de kraan gaf, van 200 tot 299.',
  'Optional, for example Bathroom.': 'Niet verplicht, bijvoorbeeld Badkamer.',
  'Save the Bluetooth changes?': 'De Bluetooth-wijzigingen opslaan?',
  'The E32 saves these changes and restarts once, about 30 seconds later; the heating continues after about a minute.': 'De E32 slaat deze wijzigingen op en start één keer opnieuw, ongeveer 30 seconden later; de verwarming gaat na ongeveer een minuut verder.',
  'Save and let the E32 restart': 'Opslaan en de E32 opnieuw laten starten',
  'First set the device up in the Shelly app: your Wi-Fi, a password and the cloud off. Give it a fixed address in your router (a DHCP reservation), so the E32 always finds it.': 'Stel het apparaat eerst in met de Shelly-app: je wifi, een wachtwoord en de cloud uit. Geef het een vast adres in je router (een DHCP-reservering), zodat de E32 het altijd vindt.',
  'Pair the valve with the gateway in the Shelly app first. Then add it here by its number: the first one is usually 200, the next 201 and so on. Choose the valve\'s room under Rooms → the room → Radiator valves.': 'Koppel de kraan eerst in de Shelly-app aan de gateway. Voeg hem dan hier toe met zijn nummer: de eerste is meestal 200, de volgende 201 enzovoort. De ruimte van de kraan kies je onder Ruimtes → de ruimte → Radiatorkranen.',
  'Connect the E32 first: Configure → E32 connection.': 'Verbind eerst de E32: Configureren → E32-verbinding.',
  'This E32 has no Shelly support. Shelly devices need an E32 V2 with firmware 1.1 or newer.': 'Deze E32 kan niet met Shelly-apparaten werken. Daarvoor is een E32 V2 met firmware 1.1 of nieuwer nodig.',
  'Use a name of 1 to 40 characters without line breaks.': 'Gebruik een naam van 1 tot 40 tekens zonder regeleinden.',
  'The E32 has no room left to store the sensors. Nothing was saved.': 'De E32 heeft geen ruimte meer om de sensoren op te slaan. Er is niets opgeslagen.',
  'The E32 refused the changes ({error}). Nothing was saved.': 'De E32 weigerde de wijzigingen ({error}). Er is niets opgeslagen.',
  'The Bluetooth sensors were changed on the E32 meanwhile. Nothing was saved; open Bluetooth sensors again.': 'De Bluetooth-sensoren zijn intussen op de E32 gewijzigd. Er is niets opgeslagen; open Bluetooth-sensoren opnieuw.',
  'Enter the address as four numbers, for example 192.168.1.40.': 'Vul het adres in als vier getallen, bijvoorbeeld 192.168.1.40.',
  'Another device in the list has this address.': 'Een ander apparaat in de lijst heeft dit adres.',
  'Nothing answers at this address. Check the address and that the device is on the same network.': 'Op dit adres antwoordt niets. Controleer het adres en of het apparaat op hetzelfde netwerk zit.',
  'The device did not answer in time. Try again.': 'Het apparaat antwoordde niet op tijd. Probeer het opnieuw.',
  'The device asks for a password before it says what it is. Check the address.': 'Het apparaat vraagt een wachtwoord voordat het zegt wat het is. Controleer het adres.',
  'This address does not answer like a Shelly device of the third generation.': 'Dit adres antwoordt niet als een Shelly-apparaat van de derde generatie.',
  'A test is already running. Try again in a moment.': 'Er loopt al een test. Probeer het zo opnieuw.',
  'This device is already in the list.': 'Dit apparaat staat al in de lijst.',
  'The E32 has no room for this device: it takes at most 6 Shelly devices. Remove a device or use shorter names.': 'De E32 heeft geen ruimte voor dit apparaat: hij neemt hoogstens 6 Shelly-apparaten. Verwijder een apparaat of gebruik kortere namen.',
  'Use a name of up to 32 characters.': 'Gebruik een naam van hoogstens 32 tekens.',
  'Use a password of up to 64 characters, without accents.': 'Gebruik een wachtwoord van hoogstens 64 tekens, zonder accenten.',
  'The device has a password: enter it, so the E32 can talk to it.': 'Het apparaat heeft een wachtwoord: vul het in, zodat de E32 ermee kan praten.',
  'A heating circuit uses this plug for its pump. Take the pump out of the circuit first (on the E32: Home → Heating settings).': 'Een verwarmingscircuit gebruikt deze plug voor zijn pomp. Haal de pomp eerst uit het circuit (op de E32: Huis → Verwarming).',
  'A heating circuit uses a probe of this device. Change the circuit first (on the E32: Home → Heating settings).': 'Een verwarmingscircuit gebruikt een sonde van dit apparaat. Pas eerst het circuit aan (op de E32: Huis → Verwarming).',
  'Use the valve\'s number, from 200 to 299.': 'Gebruik het nummer van de kraan, van 200 tot 299.',
  'This valve number is already in the list.': 'Dit kraannummer staat al in de lijst.',
  'Use a valve name of up to 32 characters, without quotes or backslashes.': 'Gebruik een kraannaam van hoogstens 32 tekens, zonder aanhalingstekens of backslashes.',
  'A gateway takes at most 5 valves.': 'Een gateway neemt hoogstens 5 kranen.',
  'The E32 refused this ({error}). Nothing was saved.': 'De E32 weigerde dit ({error}). Er is niets opgeslagen.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'De E32 is niet bereikbaar ({error}). Er is niets opgeslagen.',
  'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.': 'De E32 kon niet bevestigen dat de instellingen zijn opgeslagen. Controleer ze op de E32 voordat je het opnieuw probeert.',
  'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.': 'De E32 heeft geen vrije websessie: sluit E32-pagina\'s die je niet gebruikt, of wacht twee minuten, en probeer het opnieuw.',
  'The E32 is updating or restarting. Try again once its web page opens normally.': 'De E32 wordt bijgewerkt of start opnieuw. Probeer het opnieuw zodra zijn webpagina normaal opent.',
  'The E32 refused these settings. Nothing was saved.': 'De E32 weigerde deze instellingen. Er is niets opgeslagen.',
  'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.': 'De E32-instellingen zijn intussen gewijzigd (op zijn webpagina?). Er is niets opgeslagen; probeer het opnieuw.',
  'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.': 'Deze E32-firmware heeft deze instelling niet. Werk de E32 eerst bij (Firmware-update).',
  'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.': 'De E32 gebruikt nog het standaardwachtwoord en accepteert geen wijzigingen tot je een nieuw kiest: Instellingen → Reparaties → “E32 gebruikt nog het standaardwachtwoord”.',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'De E32 accepteert het bewaarde wachtwoord niet meer. Home Assistant vraagt om het nieuwe: Instellingen → Apparaten en diensten → OpenThermostat → Opnieuw verifiëren.',
  'Plug: switches the floor pump': 'Plug: schakelt de vloerpomp',
  'The Pill: temperature probes on the pipes': 'The Pill: temperatuursondes op de leidingen',
  'BLU Gateway: Shelly BLU TRV radiator valves': 'BLU Gateway: Shelly BLU TRV-radiatorkranen',
  'waiting for the first answer': 'wacht op het eerste antwoord',
  'connected': 'verbonden',
  'not reachable': 'niet bereikbaar',
  'another device answers at this address': 'op dit adres antwoordt een ander apparaat',
  'the password is not accepted': 'het wachtwoord wordt niet geaccepteerd',
  'the device reports an error': 'het apparaat meldt een fout',
  'waiting for a report': 'wacht op een melding',
  'reporting': 'meldt zich',
  'silent for 15 minutes': 'al 15 minuten stil',
  'not reporting': 'meldt zich niet',
  'not found at the gateway': 'niet gevonden bij de gateway',
  'not paired with the gateway': 'niet gekoppeld aan de gateway',
  'gateway not reachable': 'gateway niet bereikbaar',
  'Boiler': 'Ketel',
  'Thermostat': 'Thermostaat',
  'EMS device': 'EMS-apparaat',
  'Saved on the E32. It restarts in about 30 seconds to use the changes.': 'Opgeslagen op de E32. Hij start over ongeveer 30 seconden opnieuw om de wijzigingen te gebruiken.',
  'Saved on the E32. It restarts to use the changes as soon as an update or boiler test has finished.': 'Opgeslagen op de E32. Hij start opnieuw om de wijzigingen te gebruiken zodra een update of keteltest klaar is.',
  'Nothing changed; the E32 was not written.': 'Er is niets gewijzigd; er is niets naar de E32 geschreven.'
 },
 pl: {
  '{name} added.': 'Dodano: {name}.',
  '{name} removed.': 'Usunięto: {name}.',
  'Valves removed: {count}.': 'Usunięto zawory: {count}.',
  'Valve {id}': 'Zawór {id}',
  'Bluetooth sensors': 'Czujniki Bluetooth',
  'Rename or forget them here and save them together: after saving, the E32 restarts once, about 30 seconds later, to use them. Pairing a new sensor (scan and key) is done on the E32\'s page System → Devices, next to the sensor. Which room a sensor measures is set per room under Rooms.': 'Tutaj możesz zmienić ich nazwę lub je usunąć i zapisać je razem: po zapisaniu E32 uruchomi się ponownie jeden raz, około 30 sekund później, aby ich użyć. Parowanie nowego czujnika (wyszukiwanie i klucz) odbywa się na stronie E32 System → Devices, przy czujniku. To, które pomieszczenie mierzy czujnik, ustawia się dla każdego pomieszczenia w Pomieszczenia.',
  'No Bluetooth sensor is paired with the E32 yet. Pair one on the E32\'s page System → Devices first.': 'Z E32 nie sparowano jeszcze żadnego czujnika Bluetooth. Najpierw sparuj czujnik na stronie E32 System → Devices.',
  'battery {value}': 'bateria {value}',
  'used by {rooms}': 'używa go: {rooms}',
  'no room uses it': 'nie używa go żadne pomieszczenie',
  'Name': 'Nazwa',
  'Bluetooth address {address}. At most 40 characters (fewer with special letters).': 'Adres Bluetooth {address}. Najwyżej 40 znaków (mniej przy znakach specjalnych).',
  'Forget this sensor': 'Usuń ten czujnik',
  'The E32 stops reading it and deletes its key; to use it again, pair it again on the E32.': 'E32 przestaje go odczytywać i kasuje jego klucz; aby znów go używać, sparuj go ponownie w E32.',
  'Shelly devices': 'Urządzenia Shelly',
  'The Plug of the floor pump, The Pill with its temperature probes and the BLU Gateway of the radiator valves. The E32 talks to them itself over your home network, also without Home Assistant.': 'Wtyczka Plug pompy podłogowej, The Pill z sondami temperatury i BLU Gateway zaworów grzejnikowych. E32 rozmawia z nimi sam przez sieć domową, także bez Home Assistant.',
  'No Shelly devices yet.': 'Brak urządzeń Shelly.',
  'room: {room}': 'pomieszczenie: {room}',
  'Remove': 'Usuń',
  'Remove {name}?': 'Usunąć {name}?',
  'The E32 stops reading and driving these valves. A valve in a room stays there until you remove it under Rooms → the room → Radiator valves.': 'E32 przestaje odczytywać i sterować tymi zaworami. Zawór w pomieszczeniu zostaje tam, dopóki go nie usuniesz w Pomieszczenia → pomieszczenie → Zawory grzejnikowe.',
  'No valves yet.': 'Brak jeszcze zaworów.',
  'Add a valve': 'Dodaj zawór',
  'Remove device': 'Usuń urządzenie',
  'The E32 stops reading and switching the device. The valves of a BLU Gateway stay in their rooms until you remove them under Rooms.': 'E32 przestaje odczytywać i przełączać urządzenie. Zawory BLU Gateway zostają w swoich pomieszczeniach, dopóki ich nie usuniesz w Pomieszczenia.',
  'Add a Shelly device': 'Dodaj urządzenie Shelly',
  'On the boiler bus': 'Na magistrali kotła',
  'The devices the E32 hears on the boiler bus. There is nothing to set here.': 'Urządzenia, które E32 słyszy na magistrali kotła. Nie ma tu nic do ustawienia.',
  'The E32 has not reported them yet.': 'E32 jeszcze ich nie zgłosił.',
  'Nothing heard yet.': 'Na razie nic nie słychać.',
  'Device password': 'Hasło urządzenia',
  'The password you set in the Shelly app. It goes to the E32 only, which keeps a fingerprint of it; Home Assistant does not keep it. Leave it empty if the device has none.': 'Hasło ustawione w aplikacji Shelly. Trafia tylko do E32, który przechowuje jego odcisk; Home Assistant go nie przechowuje. Zostaw puste, jeśli urządzenie nie ma hasła.',
  'IP address': 'Adres IP',
  'For example 192.168.1.40. When you save, the E32 asks the device who it is, which takes up to 16 seconds.': 'Na przykład 192.168.1.40. Po zapisaniu E32 zapyta urządzenie, czym jest, co trwa do 16 sekund.',
  'What does it do?': 'Do czego służy?',
  'As the device says': 'Tak, jak podaje urządzenie',
  'The E32 asks the device what it is when you save.': 'E32 zapyta urządzenie, czym jest, gdy zapiszesz.',
  'The name the E32 and Home Assistant show, up to 32 characters.': 'Nazwa wyświetlana przez E32 i Home Assistant, najwyżej 32 znaki.',
  'There is no BLU Gateway in the list yet. Add one first.': 'Na liście nie ma jeszcze BLU Gateway. Najpierw dodaj bramkę.',
  'The gateway the valve is paired with.': 'Bramka, z którą zawór jest sparowany.',
  'Valve number': 'Numer zaworu',
  'The number the gateway gave the valve, from 200 to 299.': 'Numer nadany zaworowi przez bramkę, od 200 do 299.',
  'Optional, for example Bathroom.': 'Opcjonalnie, na przykład Łazienka.',
  'Save the Bluetooth changes?': 'Zapisać zmiany Bluetooth?',
  'The E32 saves these changes and restarts once, about 30 seconds later; the heating continues after about a minute.': 'E32 zapisze te zmiany i uruchomi się ponownie jeden raz, około 30 sekund później; ogrzewanie działa dalej po około minucie.',
  'Save and let the E32 restart': 'Zapisz i pozwól E32 uruchomić się ponownie',
  'First set the device up in the Shelly app: your Wi-Fi, a password and the cloud off. Give it a fixed address in your router (a DHCP reservation), so the E32 always finds it.': 'Najpierw skonfiguruj urządzenie w aplikacji Shelly: Wi-Fi, hasło i wyłączona chmura. Nadaj mu stały adres w routerze (rezerwacja DHCP), aby E32 zawsze je znalazł.',
  'Pair the valve with the gateway in the Shelly app first. Then add it here by its number: the first one is usually 200, the next 201 and so on. Choose the valve\'s room under Rooms → the room → Radiator valves.': 'Najpierw sparuj zawór z bramką w aplikacji Shelly. Potem dodaj go tutaj po numerze: pierwszy to zwykle 200, następny 201 i tak dalej. Pomieszczenie zaworu wybierasz w Pomieszczenia → pomieszczenie → Zawory grzejnikowe.',
  'Connect the E32 first: Configure → E32 connection.': 'Najpierw połącz E32: Konfiguruj → Połączenie z E32.',
  'This E32 has no Shelly support. Shelly devices need an E32 V2 with firmware 1.1 or newer.': 'Ten E32 nie obsługuje urządzeń Shelly. Potrzebny jest E32 V2 z oprogramowaniem 1.1 lub nowszym.',
  'Use a name of 1 to 40 characters without line breaks.': 'Użyj nazwy od 1 do 40 znaków bez podziału wiersza.',
  'The E32 has no room left to store the sensors. Nothing was saved.': 'E32 nie ma już miejsca na zapisanie czujników. Nic nie zostało zapisane.',
  'The E32 refused the changes ({error}). Nothing was saved.': 'E32 odrzucił zmiany ({error}). Nic nie zostało zapisane.',
  'The Bluetooth sensors were changed on the E32 meanwhile. Nothing was saved; open Bluetooth sensors again.': 'Czujniki Bluetooth zostały w międzyczasie zmienione w E32. Nic nie zostało zapisane; otwórz ponownie Czujniki Bluetooth.',
  'Enter the address as four numbers, for example 192.168.1.40.': 'Wpisz adres jako cztery liczby, na przykład 192.168.1.40.',
  'Another device in the list has this address.': 'Inne urządzenie na liście ma ten adres.',
  'Nothing answers at this address. Check the address and that the device is on the same network.': 'Pod tym adresem nic nie odpowiada. Sprawdź adres i czy urządzenie jest w tej samej sieci.',
  'The device did not answer in time. Try again.': 'Urządzenie nie odpowiedziało na czas. Spróbuj ponownie.',
  'The device asks for a password before it says what it is. Check the address.': 'Urządzenie prosi o hasło, zanim powie, czym jest. Sprawdź adres.',
  'This address does not answer like a Shelly device of the third generation.': 'Ten adres nie odpowiada jak urządzenie Shelly trzeciej generacji.',
  'A test is already running. Try again in a moment.': 'Test już trwa. Spróbuj ponownie za chwilę.',
  'This device is already in the list.': 'To urządzenie jest już na liście.',
  'The E32 has no room for this device: it takes at most 6 Shelly devices. Remove a device or use shorter names.': 'E32 nie ma miejsca na to urządzenie: przyjmuje najwyżej 6 urządzeń Shelly. Usuń urządzenie lub użyj krótszych nazw.',
  'Use a name of up to 32 characters.': 'Użyj nazwy o długości najwyżej 32 znaków.',
  'Use a password of up to 64 characters, without accents.': 'Użyj hasła o długości najwyżej 64 znaków, bez znaków diakrytycznych.',
  'The device has a password: enter it, so the E32 can talk to it.': 'Urządzenie ma hasło: wpisz je, aby E32 mógł się z nim komunikować.',
  'A heating circuit uses this plug for its pump. Take the pump out of the circuit first (on the E32: Home → Heating settings).': 'Obieg grzewczy używa tej wtyczki do swojej pompy. Najpierw wyjmij pompę z obiegu (w E32: Home → Heating settings).',
  'A heating circuit uses a probe of this device. Change the circuit first (on the E32: Home → Heating settings).': 'Obieg grzewczy używa sondy tego urządzenia. Najpierw zmień obieg (w E32: Home → Heating settings).',
  'Use the valve\'s number, from 200 to 299.': 'Użyj numeru zaworu, od 200 do 299.',
  'This valve number is already in the list.': 'Ten numer zaworu jest już na liście.',
  'Use a valve name of up to 32 characters, without quotes or backslashes.': 'Użyj nazwy zaworu o długości najwyżej 32 znaków, bez cudzysłowów i ukośników wstecznych.',
  'A gateway takes at most 5 valves.': 'Bramka przyjmuje najwyżej 5 zaworów.',
  'The E32 refused this ({error}). Nothing was saved.': 'E32 odrzucił to ({error}). Nic nie zapisano.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'Nie udało się połączyć z E32 ({error}). Nic nie zapisano.',
  'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.': 'E32 nie mógł potwierdzić zapisania ustawień. Sprawdź je w E32, zanim spróbujesz ponownie.',
  'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.': 'E32 nie ma wolnej sesji WWW: zamknij nieużywane strony E32 lub odczekaj dwie minuty, a potem spróbuj ponownie.',
  'The E32 is updating or restarting. Try again once its web page opens normally.': 'E32 jest aktualizowany lub uruchamia się ponownie. Spróbuj ponownie, gdy jego strona otworzy się normalnie.',
  'The E32 refused these settings. Nothing was saved.': 'E32 odrzucił te ustawienia. Nic nie zostało zapisane.',
  'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.': 'Ustawienia E32 zostały w międzyczasie zmienione (na jego stronie?). Nic nie zostało zapisane; spróbuj ponownie.',
  'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.': 'To oprogramowanie E32 nie ma tego ustawienia. Najpierw zaktualizuj E32 (Aktualizacja oprogramowania).',
  'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.': 'E32 nadal używa domyślnego hasła i nie przyjmuje zmian, dopóki nie wybierzesz nowego: Ustawienia → Naprawy → „E32 nadal używa domyślnego hasła”.',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'E32 nie akceptuje już zapisanego hasła. Home Assistant prosi o nowe: Ustawienia → Urządzenia i usługi → OpenThermostat → Uwierzytelnij ponownie.',
  'Plug: switches the floor pump': 'Plug: przełącza pompę podłogową',
  'The Pill: temperature probes on the pipes': 'The Pill: sondy temperatury na rurach',
  'BLU Gateway: Shelly BLU TRV radiator valves': 'BLU Gateway: zawory grzejnikowe Shelly BLU TRV',
  'waiting for the first answer': 'czeka na pierwszą odpowiedź',
  'connected': 'połączono',
  'not reachable': 'nieosiągalne',
  'another device answers at this address': 'pod tym adresem odpowiada inne urządzenie',
  'the password is not accepted': 'hasło nie jest akceptowane',
  'the device reports an error': 'urządzenie zgłasza błąd',
  'waiting for a report': 'czeka na zgłoszenie',
  'reporting': 'zgłasza się',
  'silent for 15 minutes': 'cisza od 15 minut',
  'not reporting': 'nie zgłasza się',
  'not found at the gateway': 'nie znaleziono w bramce',
  'not paired with the gateway': 'nie sparowano z bramką',
  'gateway not reachable': 'bramka nieosiągalna',
  'Boiler': 'Kocioł',
  'Thermostat': 'Termostat',
  'EMS device': 'Urządzenie EMS',
  'Saved on the E32. It restarts in about 30 seconds to use the changes.': 'Zapisano w E32. Uruchomi się ponownie za około 30 sekund, aby użyć zmian.',
  'Saved on the E32. It restarts to use the changes as soon as an update or boiler test has finished.': 'Zapisano w E32. Uruchomi się ponownie, aby użyć zmian, gdy tylko zakończy się aktualizacja lub test kotła.',
  'Nothing changed; the E32 was not written.': 'Nic się nie zmieniło; nic nie zostało zapisane w E32.'
 }};
const TITLES = {'shelly-add': 'Add a Shelly device', 'valve-add': 'Add a valve'};
const SUBTITLES = {
 'shelly-add': 'First set the device up in the Shelly app: your Wi-Fi, a password and the cloud off. Give it a fixed address in your router (a DHCP reservation), so the E32 always finds it.',
 'valve-add': 'Pair the valve with the gateway in the Shelly app first. Then add it here by its number: the first one is usually 200, the next 201 and so on. Choose the valve\'s room under Rooms → the room → Radiator valves.'};
const ERRORS = {
 connect_e32: 'Connect the E32 first: Configure → E32 connection.',
 shelly_unsupported: 'This E32 has no Shelly support. Shelly devices need an E32 V2 with firmware 1.1 or newer.',
 ble_name_invalid: 'Use a name of 1 to 40 characters without line breaks.',
 ble_storage_full: 'The E32 has no room left to store the sensors. Nothing was saved.',
 ble_rejected: 'The E32 refused the changes ({error}). Nothing was saved.',
 ble_changed: 'The Bluetooth sensors were changed on the E32 meanwhile. Nothing was saved; open Bluetooth sensors again.',
 shelly_ip_invalid: 'Enter the address as four numbers, for example 192.168.1.40.',
 shelly_ip_duplicate: 'Another device in the list has this address.',
 shelly_connect_failed: 'Nothing answers at this address. Check the address and that the device is on the same network.',
 shelly_timeout: 'The device did not answer in time. Try again.',
 shelly_auth_required: 'The device asks for a password before it says what it is. Check the address.',
 shelly_not_a_shelly: 'This address does not answer like a Shelly device of the third generation.',
 shelly_probe_busy: 'A test is already running. Try again in a moment.',
 shelly_duplicate_device: 'This device is already in the list.',
 shelly_full: 'The E32 has no room for this device: it takes at most 6 Shelly devices. Remove a device or use shorter names.',
 shelly_label_invalid: 'Use a name of up to 32 characters.',
 shelly_password_invalid: 'Use a password of up to 64 characters, without accents.',
 shelly_password_needed: 'The device has a password: enter it, so the E32 can talk to it.',
 shelly_pump_in_use: 'A heating circuit uses this plug for its pump. Take the pump out of the circuit first (on the E32: Home → Heating settings).',
 shelly_probe_in_use: 'A heating circuit uses a probe of this device. Change the circuit first (on the E32: Home → Heating settings).',
 shelly_valve_invalid: 'Use the valve\'s number, from 200 to 299.',
 shelly_valve_duplicate: 'This valve number is already in the list.',
 shelly_valve_name_invalid: 'Use a valve name of up to 32 characters, without quotes or backslashes.',
 shelly_valves_full: 'A gateway takes at most 5 valves.',
 shelly_rejected: 'The E32 refused this ({error}). Nothing was saved.',
 e32_settings_unreachable: 'The E32 could not be reached ({error}). Nothing was saved.',
 e32_settings_unconfirmed: 'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.',
 e32_settings_no_free_session: 'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.',
 e32_settings_busy: 'The E32 is updating or restarting. Try again once its web page opens normally.',
 e32_settings_invalid: 'The E32 refused these settings. Nothing was saved.',
 e32_settings_changed: 'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.',
 e32_settings_update_required: 'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.',
 e32_settings_password_default: 'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.',
 e32_password_changed: 'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.'};
// Configure's and the E32 page's words for a Shelly device and its state (e32_devices.WORDS); the product names stay as they
// are in every language.
const NAMES = {switch: 'Plug', probes: 'The Pill', gateway: 'BLU Gateway'};
const JOBS = {switch: 'Plug: switches the floor pump', probes: 'The Pill: temperature probes on the pipes', gateway: 'BLU Gateway: Shelly BLU TRV radiator valves'};
const HEALTH = {waiting: 'waiting for the first answer', ok: 'connected', unreachable: 'not reachable', wrong_device: 'another device answers at this address',
 auth_failed: 'the password is not accepted', error: 'the device reports an error'};
const VALVE_HEALTH = {waiting: 'waiting for a report', ok: 'reporting', silent: 'silent for 15 minutes', offline: 'not reporting',
 missing: 'not found at the gateway', unpaired: 'not paired with the gateway', gateway: 'gateway not reachable'};
const ROLES = {boiler: 'Boiler', thermostat: 'Thermostat', device: 'EMS device'};
const DONE = {ble_saved: 'Saved on the E32. It restarts in about 30 seconds to use the changes.',
 ble_saved_restart_later: 'Saved on the E32. It restarts to use the changes as soon as an update or boiler test has finished.',
 ble_unchanged: 'Nothing changed; the E32 was not written.'};
const CSS = `.ot-block{padding:16px 0 6px;border-top:1px solid var(--ot-divider)}.ot-block:first-of-type{border-top:0;padding-top:6px}
.ot-block>h3{margin:0;font-size:18px;font-weight:500}.ot-block>.help{margin:4px 0 6px}.ot-item{padding:12px 0 4px;border-top:1px solid var(--ot-divider)}
.ot-item>h4{margin:0;font-size:16px;font-weight:500;overflow-wrap:anywhere}.ot-line{margin-top:2px;color:var(--ot-muted);overflow-wrap:anywhere}
.ot-valves{margin:8px 0 0;padding:0;list-style:none;display:grid;gap:4px}.ot-valves li{display:flex;flex-wrap:wrap;align-items:center;gap:4px 12px;
justify-content:space-between}.ot-actions{display:flex;flex-wrap:wrap;gap:8px;padding:10px 0 6px}.ot-done{margin:6px 0 10px}`;

const fmt = (lang, v, digits) => (typeof v === 'number' ? v.toLocaleString(lang, digits == null ? {} : {maximumFractionDigits: digits}) : '');
const hex = address => address.match(/../g).join(':').toUpperCase();
const deviceName = d => d.label || NAMES[d.kind];

// The editable values: each paired sensor's name and whether to forget it ("Save" saves them together); the add forms.
function values(m) {
 if (m.screen === 'shelly-add') return {ip: '', kind: 'auto', label: '', password: ''};
 if (m.screen === 'valve-add') {
  const g = m.gateways?.find(x => x.valves.length < m.max_valves) || m.gateways?.[0];
  let valve = m.valve_range?.[0] ?? 200;
  while (g && g.valves.includes(valve)) valve++;
  return {gateway: g ? String(g.n) : '', valve, name: ''};
 }
 const out = {};
 for (const s of m.bluetooth || []) { out[`ble_name:${s.address}`] = s.name; out[`ble_forget:${s.address}`] = false; }
 return out;
}
const bleChanged = (v, m) => (m.bluetooth || []).some(s => v[`ble_forget:${s.address}`] === true || (v[`ble_name:${s.address}`] ?? s.name).trim() !== s.name);

// What the last save did (the model's live.saved), in Configure's words.
function saved(ctx, kinds) {
 const {kit, t, model: m} = ctx, done = m.live?.saved;
 if (!done || !kinds.includes(done.done)) return null;
 const name = done.name || NAMES[done.kind] || '';
 const text = done.done === 'added' ? t('{name} added.', {name}) : done.done === 'removed' ? t('{name} removed.', {name})
  : done.done === 'valves_removed' ? t('Valves removed: {count}.', {count: done.count})
  : done.done === 'valve_added' ? t('{name} added.', {name: t('Valve {id}', {id: done.valve}) + (done.name ? ` · ${done.name}` : '')})
  : t(DONE[done.done]);
 return kit.h('div', {class: 'ot-done', 'data-done': done.done}, kit.notice(text, 'info'));
}

function bluetooth(ctx) {
 const {kit, t, model: m, hass, lang} = ctx, live = m.live?.bluetooth || {};
 const block = kit.h('section', {class: 'ot-block', 'data-block': 'bluetooth'}, kit.h('h3', {text: t('Bluetooth sensors')}),
  kit.h('p', {class: 'help', text: t('Rename or forget them here and save them together: after saving, the E32 restarts once, about 30 seconds later, to use them. Pairing a new sensor (scan and key) is done on the E32\'s page System → Devices, next to the sensor. Which room a sensor measures is set per room under Rooms.')}));
 const done = saved(ctx, ['ble_saved', 'ble_saved_restart_later', 'ble_unchanged']);
 if (done) block.append(done);
 if (m.bluetooth == null) return block;
 if (!m.bluetooth.length) { block.append(kit.h('p', {class: 'ot-line', text: t('No Bluetooth sensor is paired with the E32 yet. Pair one on the E32\'s page System → Devices first.')})); return block; }
 for (const s of m.bluetooth) {
  // The readings now, from the sensor's own Home Assistant entities (in Home Assistant's units).
  const info = live[s.address] || {}, facts = [];
  const reading = (id, digits) => {
   const st = id && hass?.states?.[id], value = st ? Number(st.state) : NaN;
   return st && st.state !== '' && Number.isFinite(value) ? `${fmt(lang, value, digits)} ${st.attributes?.unit_of_measurement || ''}`.trim() : null;
  };
  const temperature = reading(info.temperature, 1), humidity = reading(info.humidity, 0), battery = reading(info.battery, 0);
  if (temperature) facts.push(temperature);
  if (humidity) facts.push(humidity);
  if (battery) facts.push(t('battery {value}', {value: battery}));
  if (info.rooms?.length) facts.push(t('used by {rooms}', {rooms: info.rooms.join(', ')}));
  else facts.push(t('no room uses it'));
  block.append(kit.h('div', {class: 'ot-item', 'data-sensor': s.address}, kit.h('h4', {text: s.name || hex(s.address)}),
   kit.h('p', {class: 'ot-line', 'data-live': 'sensor', text: facts.join(' · ')}),
   ctx.field('text', `ble_name:${s.address}`, {label: t('Name'), maxlength: 40, help: t('Bluetooth address {address}. At most 40 characters (fewer with special letters).', {address: hex(s.address)})}),
   ctx.field('toggle', `ble_forget:${s.address}`, {label: t('Forget this sensor'),
    help: t('The E32 stops reading it and deletes its key; to use it again, pair it again on the E32.')})));
 }
 return block;
}

function shelly(ctx) {
 const {kit, t, model: m} = ctx, live = m.live?.shelly || {}, sh = m.shelly;
 const block = kit.h('section', {class: 'ot-block', 'data-block': 'shelly'}, kit.h('h3', {text: t('Shelly devices')}),
  kit.h('p', {class: 'help', text: t('The Plug of the floor pump, The Pill with its temperature probes and the BLU Gateway of the radiator valves. The E32 talks to them itself over your home network, also without Home Assistant.')}));
 const done = saved(ctx, ['removed', 'valves_removed']);
 if (done) block.append(done);
 if (!sh) { block.append(kit.h('p', {class: 'ot-line', text: t(ERRORS.shelly_unsupported)})); return block; }
 if (!sh.devices.length) block.append(kit.h('p', {class: 'ot-line', text: t('No Shelly devices yet.')}));
 for (const d of sh.devices) {
  const name = deviceName(d), health = HEALTH[live[String(d.n)]];
  const item = kit.h('div', {class: 'ot-item', 'data-device': d.id}, kit.h('h4', {text: name}),
   kit.h('p', {class: 'ot-line', text: [t(JOBS[d.kind]), d.ip, health && t(health)].filter(Boolean).join(' · ')}));
  if (d.kind === 'gateway') {
   const list = kit.h('ul', {class: 'ot-valves'});
   for (const v of d.valves || []) {
    const key = `${d.n}:${v.id}`, room = live['room:' + key], state = VALVE_HEALTH[live[key]];
    const text = [t('Valve {id}', {id: v.id}) + (v.name ? ` · ${v.name}` : ''), state && t(state), room && t('room: {room}', {room})].filter(Boolean).join(' · ');
    list.append(kit.h('li', {'data-valve': key}, kit.h('span', {text}),
     kit.button(t('Remove'), () => ctx.act({action: 'valves_remove', valves: [key]}, {title: t('Remove {name}?', {name: t('Valve {id}', {id: v.id})}),
      text: t('The E32 stops reading and driving these valves. A valve in a room stays there until you remove it under Rooms → the room → Radiator valves.'),
      confirm: t('Remove'), danger: true}), 'text', {disabled: ctx.readOnly, 'data-remove-valve': key})));
   }
   if (!d.valves?.length) list.append(kit.h('li', {class: 'ot-line', text: t('No valves yet.')}));
   item.append(list);
  }
  const actions = kit.h('div', {class: 'ot-actions'});
  if (d.kind === 'gateway' && (d.valves || []).length < sh.max_valves)
   actions.append(kit.button(t('Add a valve'), () => ctx.navigate('#devices/valve-add'), 'outlined', {disabled: ctx.readOnly, 'data-add-valve': d.id}));
  if (d.pump) item.append(kit.h('p', {class: 'ot-line', text: t(ERRORS.shelly_pump_in_use)}));
  else actions.append(kit.button(t('Remove device'), () => ctx.act({action: 'shelly_remove', device: d.id}, {title: t('Remove {name}?', {name}),
   text: t('The E32 stops reading and switching the device. The valves of a BLU Gateway stay in their rooms until you remove them under Rooms.'),
   confirm: t('Remove device'), danger: true}), 'text', {disabled: ctx.readOnly, 'data-remove-device': d.id}));
  if (actions.childElementCount) item.append(actions);
  block.append(item);
 }
 if (sh.devices.length < sh.max_devices) block.append(kit.h('div', {class: 'ot-actions'},
  kit.button(t('Add a Shelly device'), () => ctx.navigate('#devices/shelly-add'), 'outlined', {disabled: ctx.readOnly, 'data-add-device': ''})));
 return block;
}

function bus(ctx) {
 const {kit, t, model: m} = ctx, devices = m.live?.bus;
 const block = kit.h('section', {class: 'ot-block', 'data-block': 'bus'}, kit.h('h3', {text: t('On the boiler bus')}),
  kit.h('p', {class: 'help', text: t('The devices the E32 hears on the boiler bus. There is nothing to set here.')}));
 if (devices == null) block.append(kit.h('p', {class: 'ot-line', text: t('The E32 has not reported them yet.')}));
 else if (!devices.length) block.append(kit.h('p', {class: 'ot-line', text: t('Nothing heard yet.')}));
 else block.append(kit.h('ul', {class: 'ot-valves'}, ...devices.map(d => kit.h('li', {'data-bus': d.address},
  kit.h('span', {text: `${d.name || t(ROLES[d.role] || 'EMS device')} (${d.address})`})))));
 return block;
}

function addDevice(ctx) {
 const {kit, t} = ctx;
 // The password goes to the E32 only (settings_devices.py): never in a model, an error or the log; shown as dots.
 const password = ctx.field('text', 'password', {label: t('Device password'), maxlength: 64,
  help: t('The password you set in the Shelly app. It goes to the E32 only, which keeps a fingerprint of it; Home Assistant does not keep it. Leave it empty if the device has none.')});
 Object.assign(password.querySelector('input'), {type: 'password', autocomplete: 'new-password'});
 return kit.h('div', {class: 'fields'}, saved(ctx, ['added']),
  ctx.field('text', 'ip', {label: t('IP address'), maxlength: 15, placeholder: '192.168.1.40',
   help: t('For example 192.168.1.40. When you save, the E32 asks the device who it is, which takes up to 16 seconds.')}),
  ctx.field('radio', 'kind', {label: t('What does it do?'), options: [
   {value: 'auto', label: t('As the device says'), help: t('The E32 asks the device what it is when you save.')},
   ...Object.entries(JOBS).map(([value, label]) => ({value, label: t(label)}))]}),
  ctx.field('text', 'label', {label: t('Name'), maxlength: 32, help: t('The name the E32 and Home Assistant show, up to 32 characters.')}),
  password);
}

function addValve(ctx) {
 const {kit, t, model: m} = ctx;
 if (!m.gateways?.length) return kit.h('div', {class: 'fields'}, kit.h('p', {class: 'ot-line', text: t('There is no BLU Gateway in the list yet. Add one first.')}));
 return kit.h('div', {class: 'fields'}, saved(ctx, ['valve_added']),
  ctx.field('select', 'gateway', {label: NAMES.gateway, help: t('The gateway the valve is paired with.'),
   options: m.gateways.map(g => ({value: String(g.n), label: `${g.label || NAMES.gateway} (${g.ip})`}))}),
  ctx.field('number', 'valve', {label: t('Valve number'), step: 1, min: m.valve_range[0], max: m.valve_range[1],
   help: t('The number the gateway gave the valve, from 200 to 299.')}),
  ctx.field('text', 'name', {label: t('Name'), maxlength: 32, help: t('Optional, for example Bathroom.')}));
}

(window.OpenThermostatSettingsSections ||= []).push(['devices', {
 title: (model, item) => TITLES[item] || 'Devices',
 subtitle: (model, item) => SUBTITLES[item] || null,
 texts: TEXTS,
 errors: ERRORS,
 values,
 confirm: (v, m, ctx) => (!m.screen && bleChanged(v, m) ? {title: ctx.t('Save the Bluetooth changes?'),
  text: ctx.t('The E32 saves these changes and restarts once, about 30 seconds later; the heating continues after about a minute.'),
  confirm: ctx.t('Save and let the E32 restart')} : null),
 render: ctx => {
  const {kit} = ctx, root = kit.h('div', {class: 'ot-devices', 'data-screen': ctx.model.screen || 'list'}, kit.h('style', {text: CSS}));
  if (ctx.model.screen === 'shelly-add') root.append(addDevice(ctx));
  else if (ctx.model.screen === 'valve-add') root.append(addValve(ctx));
  else root.append(bluetooth(ctx), shelly(ctx), bus(ctx));
  return root;
 }
}]);
