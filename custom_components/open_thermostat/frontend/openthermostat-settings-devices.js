/* The section Devices of the settings panel (1.4.1, golf B; plan HA-INSTELPANEEL-FASE2.nl.md 3.4 and 7.2): one screen per
   block, built on kit v2. #devices lists the three blocks. Bluetooth sensors: the list with each sensor's reading,
   battery and rooms; a sensor's screen (its readings, its name, Forget sensor with a question); Pair a sensor (the E32
   searches, you choose what it heard, give it a name, its type and, when it encrypts, its key). Shelly devices: the
   list; a device's screen (The Pill's probe roles, a BLU Gateway's valves and Look for valves at the gateway, Remove
   device with a question); Add a Shelly device (#devices/shelly-add) and Add a valve (#devices/valve-add) as in 1.4.
   On the boiler bus: read-only.
   Backend settings_devices.py: every screen has its own address and model (1.4.2, plan 3.9): #devices (the three
   blocks), #devices/bluetooth, #devices/pair, #devices/pair/<address> (the form of a device the search heard),
   #devices/sensor/<address> (its own name, the room it measures for, Forget sensor), #devices/shelly,
   #devices/device/<id>, #devices/bus, #devices/shelly-add and #devices/valve-add; the core reads and saves each, so
   the browser's back button, a reload and a link work as on every other screen. The actions of CONTRACT-1.4.1 §3
   (scan, scan_result, pair, pill_roles, set_pill_roles, gateway_scan, gateway_scan_result). The Search: with E32
   1.4.2 (ble.discovery.v1) it is off only while a requested search is queued or running (live.discovery); older
   firmware keeps the panel's own 95 s. Polling as the backend asks: scan_result every 3 s, gateway_scan_result every
   2 s for at most a minute, both stopped at done or when the screen is left (the E32 has four web sessions). A
   bindkey and a device password go to the backend once and stay in no state, log or page. */
const TEXTS = {
 nl: {
  'Devices': 'Apparaten',
  'Back to {page}': 'Terug naar {page}',
  'Saving…': 'Opslaan…',
  'Bluetooth sensors': 'Bluetooth-sensoren',
  'Shelly devices': 'Shelly-apparaten',
  'On the boiler bus': 'Op de ketelbus',
  '{n} paired': '{n} gekoppeld',
  '{n} of 8 paired': '{n} van 8 gekoppeld',
  '1 valve': '1 kraan',
  '{n} valves': '{n} kranen',
  'Choose your sensor.': 'Kies je sensor.',
  'Devices found': 'Gevonden apparaten',
  '{n} without a reading': '{n} zonder meting',
  'No sensors paired yet': 'Nog geen sensoren gekoppeld',
  'Needs a newer E32 firmware': 'Vraagt om nieuwere E32-firmware',
  '{gateway} with 1 valve': '{gateway} met 1 kraan',
  '{gateway} with {n} valves': '{gateway} met {n} kranen',
  'Choose on a sensor\'s screen which room it measures for.': 'Op het scherm van een sensor kies je voor welke ruimte hij meet.',
  'Pair a sensor': 'Sensor koppelen',
  'No Bluetooth sensors yet. Pair your first sensor.': 'Nog geen Bluetooth-sensoren. Koppel je eerste sensor.',
  'Measures for {rooms}': 'Meet voor {rooms}',
  'Not assigned to a room yet': 'Nog aan geen ruimte toegewezen',
  'Last reading {n} s ago': 'Laatste meting {n} s geleden',
  'Last reading {n} min ago': 'Laatste meting {n} min geleden',
  'Last reading {n} h ago': 'Laatste meting {n} uur geleden',
  'automatic': 'automatisch',
  'Without a name of its own, the sensor is named after the room that measures with it.': 'Zonder eigen naam heet de sensor naar de ruimte die ermee meet.',
  'Keep this name': 'Deze naam houden',
  'Measures for': 'Meet voor',
  'No room': 'Geen ruimte',
  'The room uses it as its first temperature source; other rooms stop using it.': 'De ruimte gebruikt hem als eerste temperatuurbron; andere ruimtes gebruiken hem dan niet meer.',
  'The entity IDs in Home Assistant still carry an older name.': 'De ID\'s van de entiteiten in Home Assistant dragen nog een oudere naam.',
  'Tidy entity IDs': 'ID\'s van entiteiten opruimen',
  'Saved: it measures for {room} now.': 'Opgeslagen: hij meet nu voor {room}.',
  'Saved: no room measures with it now.': 'Opgeslagen: geen ruimte meet er nu mee.',
  'Searching… (up to 90 s)': 'Zoeken… (tot 90 s)',
  '{room} already has {max} temperature sources. Remove one there first.': '{room} heeft al {max} temperatuurbronnen. Haal er daar eerst een weg.',
  '{room} measures only with this sensor. Give {room} another temperature source first.': '{room} meet alleen met deze sensor. Geef {room} eerst een andere temperatuurbron.',
  'The temperature sources of {room} cannot be changed like this ({error}). Change them on the room\'s screen.': 'De temperatuurbronnen van {room} kunnen zo niet worden gewijzigd ({error}). Wijzig ze op het scherm van de ruimte.',
  'The room could not be changed on the E32 ({error}). Nothing was changed.': 'De ruimte kon niet op de E32 worden gewijzigd ({error}). Er is niets gewijzigd.',
  'This room no longer exists. Choose another room.': 'Deze ruimte bestaat niet meer. Kies een andere ruimte.',
  'battery {value}': 'batterij {value}',
  'No reading': 'Geen meting',
  'Address {address}': 'Adres {address}',
  'Temperature': 'Temperatuur',
  'Humidity': 'Luchtvochtigheid',
  'Battery': 'Batterij',
  'Name': 'Naam',
  'At most 40 characters (fewer with special letters).': 'Hoogstens 40 tekens (minder met bijzondere letters).',
  'Forget sensor': 'Sensor vergeten',
  'Forget': 'Vergeten',
  'Forget {name}?': '{name} vergeten?',
  'The E32 stops reading it and deletes its key, then restarts once, about 30 seconds later. To use it again, pair it again.': 'De E32 leest hem niet meer en wist zijn sleutel, en start daarna één keer opnieuw, ongeveer 30 seconden later. Om hem weer te gebruiken koppel je hem opnieuw.',
  'Rooms that measure with it: {rooms}.': 'Ruimtes die ermee meten: {rooms}.',
  'The E32 listens for about 30 seconds. Wake the sensor if needed.': 'De E32 luistert ongeveer 30 seconden. Maak de sensor zo nodig wakker.',
  'Search nearby': 'Zoek in de buurt',
  'Searching nearby…': 'Zoeken in de buurt…',
  'No devices found yet. Start a search and wake the sensor if needed.': 'Nog geen apparaten gevonden. Zoek opnieuw en maak de sensor zo nodig wakker.',
  'Unnamed Bluetooth device': 'Bluetooth-apparaat zonder naam',
  'Already added': 'Al toegevoegd',
  'Strong signal': 'Sterk signaal',
  'Fair signal': 'Redelijk signaal',
  'Weak signal': 'Zwak signaal',
  'More devices were received than this list can hold. Search again nearer to the device you want to add.': 'Er zijn meer apparaten ontvangen dan in deze lijst passen. Zoek opnieuw dichter bij het apparaat dat je wilt toevoegen.',
  'Sensor type': 'Sensortype',
  'Guessed from the device name: check it.': 'Geraden uit de apparaatnaam: controleer het.',
  'Thermometer with pvvx firmware (BTHome)': 'Thermometer met pvvx-firmware (BTHome)',
  'Encryption': 'Versleuteling',
  'Unencrypted': 'Onversleuteld',
  'BTHome v2 encrypted': 'BTHome v2 versleuteld',
  'MiBeacon v4/v5 encrypted': 'MiBeacon v4/v5 versleuteld',
  'Encryption key (bindkey)': 'Sleutel (bindkey)',
  'An encrypted sensor needs its 32-character key (bindkey); the E32 stores it and never shows it again.': 'Een versleutelde sensor heeft zijn sleutel van 32 tekens (bindkey) nodig; de E32 bewaart die en toont hem nooit meer.',
  'Pair': 'Koppelen',
  'Pairing…': 'Koppelen…',
  '{name} paired.': '{name} gekoppeld.',
  'The E32 talks to them itself over your home network, also without Home Assistant.': 'De E32 praat er zelf mee over je thuisnetwerk, ook zonder Home Assistant.',
  'Shelly device': 'Shelly-apparaat',
  'Add a Shelly device': 'Shelly-apparaat toevoegen',
  'No Shelly devices yet.': 'Nog geen Shelly-apparaten.',
  'IP address': 'IP-adres',
  'Remove device': 'Apparaat verwijderen',
  'Remove {name}?': '{name} verwijderen?',
  'The E32 stops reading and switching the device. The valves of a BLU Gateway stay in their rooms until you remove them under Rooms.': 'De E32 leest en schakelt het apparaat niet meer. De kranen van een BLU Gateway blijven in hun ruimtes tot je ze onder Ruimtes verwijdert.',
  'Probe roles': 'Sonderollen',
  'Give each probe the pipe it sits on.': 'Geef elke sonde de leiding waar hij op zit.',
  'The E32 uses the water to and back from the floor for the pump and to watch for too hot water.': 'De E32 gebruikt het water naar en terug van de vloer voor de pomp en om te bewaken of het water te heet wordt.',
  'Probe {n}': 'Sonde {n}',
  'Back from floor loop {n}': 'Terug van vloergroep {n}',
  'Other probe {n}': 'Andere sonde {n}',
  'Not used': 'Niet gebruikt',
  'A heating circuit measures with this probe. Change the circuit first (on the E32: Home → Heating settings).': 'Een verwarmingscircuit meet met deze sonde. Pas eerst het circuit aan (op de E32: Huis → Verwarming).',
  'Save probe roles': 'Sonderollen opslaan',
  'Probe roles saved.': 'Sonderollen opgeslagen.',
  'The Pill reports no probes yet.': 'The Pill meldt nog geen sondes.',
  'Try again': 'Opnieuw proberen',
  'Valves': 'Kranen',
  'Valve {id}': 'Kraan {id}',
  'room: {room}': 'ruimte: {room}',
  'No valves yet.': 'Nog geen kranen.',
  'Add a valve': 'Kraan toevoegen',
  'Remove': 'Verwijderen',
  'Remove {valve}': '{valve} verwijderen',
  'The E32 stops reading and driving these valves. A valve in a room stays there until you remove it under Rooms → the room → Radiator valves.': 'De E32 leest en stuurt deze kranen niet meer. Een kraan in een ruimte blijft daar tot je hem verwijdert onder Ruimtes → de ruimte → Radiatorkranen.',
  'Look for valves at the gateway': 'Kranen zoeken bij de gateway',
  'Looking for valves at the gateway…': 'Kranen zoeken bij de gateway…',
  'Tap a valve to add it.': 'Tik op een kraan om hem toe te voegen.',
  'Already in the list': 'Staat al in de lijst',
  'The gateway reports no paired valves. Pair them in the Shelly app first.': 'De gateway meldt geen gekoppelde kranen. Koppel ze eerst in de Shelly-app.',
  'The gateway reported more devices than the E32 reads; not every valve may be listed.': 'De gateway meldde meer apparaten dan de E32 leest; misschien staat niet elke kraan in de lijst.',
  'A gateway takes at most 5 valves.': 'Een gateway neemt hoogstens 5 kranen.',
  'The devices the E32 hears on the boiler bus. There is nothing to set here.': 'De apparaten die de E32 op de ketelbus hoort. Hier valt niets in te stellen.',
  'The E32 has not reported them yet.': 'De E32 heeft ze nog niet gemeld.',
  'Nothing heard yet.': 'Nog niets gehoord.',
  'Device password': 'Wachtwoord van het apparaat',
  'The password you set in the Shelly app. It goes to the E32 only, which keeps a fingerprint of it; Home Assistant does not keep it. Leave it empty if the device has none.': 'Het wachtwoord dat je in de Shelly-app hebt ingesteld. Het gaat alleen naar de E32, die er een vingerafdruk van bewaart; Home Assistant bewaart het niet. Laat het leeg als het apparaat er geen heeft.',
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
  'First set the device up in the Shelly app: your Wi-Fi, a password and the cloud off.': 'Stel het apparaat eerst in met de Shelly-app: je wifi, een wachtwoord en de cloud uit.',
  'Give it a fixed address in your router (a DHCP reservation), so the E32 always finds it.': 'Geef het een vast adres in je router (een DHCP-reservering), zodat de E32 het altijd vindt.',
  'Pair the valve with the gateway in the Shelly app first.': 'Koppel de kraan eerst in de Shelly-app aan de gateway.',
  'Then add it here by its number: the first one is usually 200, the next 201 and so on. Choose the valve\'s room under Rooms → the room → Radiator valves.': 'Voeg hem dan hier toe met zijn nummer: de eerste is meestal 200, de volgende 201 enzovoort. De ruimte van de kraan kies je onder Ruimtes → de ruimte → Radiatorkranen.',
  '{name} added.': '{name} toegevoegd.',
  '{name} removed.': '{name} verwijderd.',
  'Valves removed: {count}.': 'Kranen verwijderd: {count}.',
  'Connect the E32 first: Configure → E32 connection.': 'Verbind eerst de E32: Configureren → E32-verbinding.',
  'This E32 has no Shelly support. Shelly devices need an E32 V2 with firmware 1.1 or newer.': 'Deze E32 kan niet met Shelly-apparaten werken. Daarvoor is een E32 V2 met firmware 1.1 of nieuwer nodig.',
  'Use a name of 1 to 40 characters without line breaks.': 'Gebruik een naam van 1 tot 40 tekens zonder regeleinden.',
  'The E32 has no room left to store the sensors. Nothing was saved.': 'De E32 heeft geen ruimte meer om de sensoren op te slaan. Er is niets opgeslagen.',
  'The E32 refused the changes ({error}). Nothing was saved.': 'De E32 weigerde de wijzigingen ({error}). Er is niets opgeslagen.',
  'The Bluetooth sensors were changed on the E32 meanwhile. Nothing was saved; open Bluetooth sensors again.': 'De Bluetooth-sensoren zijn intussen op de E32 gewijzigd. Er is niets opgeslagen; open Bluetooth-sensoren opnieuw.',
  'Enter a Bluetooth address with six hexadecimal pairs.': 'Voer een Bluetooth-adres met zes hexadecimale paren in.',
  'This sensor is already paired with the E32.': 'Deze sensor is al aan de E32 gekoppeld.',
  'You can add at most 8 Bluetooth devices.': 'Je kunt hoogstens 8 Bluetooth-apparaten toevoegen.',
  'Choose the sensor type: the E32 cannot tell it from the name.': 'Kies het sensortype: de E32 kan het niet uit de naam afleiden.',
  'This Bluetooth device profile is not supported.': 'Dit Bluetooth-apparaatprofiel wordt niet ondersteund.',
  'Select the encryption offered for this device profile.': 'Kies de versleuteling die bij dit apparaatprofiel hoort.',
  'This sensor sends encrypted readings: enter its 32-character key (bindkey).': 'Deze sensor versleutelt zijn metingen: vul zijn sleutel van 32 tekens (bindkey) in.',
  'Enter exactly 32 hexadecimal characters for the bindkey.': 'Voer precies 32 hexadecimale tekens voor de bindkey in.',
  'Unencrypted readings need no key: leave the bindkey empty or choose encrypted BTHome.': 'Onversleutelde metingen hebben geen sleutel nodig: laat de bindkey leeg of kies versleutelde BTHome.',
  'Search did not start. A scan may already be running, disabled, cooling down or unavailable.': 'Zoeken is niet gestart. Misschien loopt er al een zoekactie, staat zoeken uit of moet je even wachten.',
  'Each probe role can be used once.': 'Elke sonderol kan één keer worden gebruikt.',
  'Choose a pipe from the list for each probe.': 'Kies voor elke sonde een leiding uit de lijst.',
  'A search runs at another gateway. Try again in a minute.': 'Er loopt al een zoekactie bij een andere gateway. Probeer het over een minuut opnieuw.',
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
  'The E32 refused this ({error}). Nothing was saved.': 'De E32 weigerde dit ({error}). Er is niets opgeslagen.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'De E32 was niet bereikbaar ({error}). Er is niets opgeslagen.',
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
  'Water to the floor (after the mixing valve)': 'Water naar de vloer (na de mengklep)',
  'Water back from the floor': 'Water terug van de vloer',
  'Waiting for a reading': 'Wacht op een meting',
  'Not found on The Pill': 'Niet gevonden op The Pill',
  'The gateway did not answer. Try again, or add the valves by number below.': 'De gateway antwoordde niet. Probeer het opnieuw, of voeg de kranen hieronder toe met hun nummer.',
  'The search was interrupted. Try again.': 'Het zoeken werd onderbroken. Probeer het opnieuw.',
  'Another device answers at this address': 'Op dit adres antwoordt een ander apparaat',
  'The password is not accepted': 'Het wachtwoord wordt niet geaccepteerd',
  'The gateway gave no list of its valves. Update its firmware in the Shelly app, or add the valves by number below.': 'De gateway gaf geen lijst van zijn kranen. Werk zijn firmware bij in de Shelly-app, of voeg de kranen hieronder toe met hun nummer.',
  'Boiler': 'Ketel',
  'Thermostat': 'Thermostaat',
  'EMS device': 'EMS-apparaat',
  'Saved on the E32. It restarts in about 30 seconds to use the changes.': 'Opgeslagen op de E32. Hij start over ongeveer 30 seconden opnieuw om de wijzigingen te gebruiken.',
  'Saved on the E32. It restarts to use the changes as soon as an update or boiler test has finished.': 'Opgeslagen op de E32. Hij start opnieuw om de wijzigingen te gebruiken zodra een update of keteltest klaar is.',
  'Nothing changed; the E32 was not written.': 'Er is niets gewijzigd; er is niets naar de E32 geschreven.',
  'Batteries': 'Batterijen',
  'Every device that reports a battery, the lowest first.': 'Elk apparaat dat een batterij meldt, de laagste bovenaan.',
  'No device reports a battery.': 'Geen apparaat meldt een batterij.',
  'Warn below': 'Waarschuwen onder',
  'Below this a battery counts as low: on this list, in the messages and on the dashboard.': 'Daaronder telt een batterij als laag: op deze lijst, in de meldingen en op het dashboard.',
  'The E32 keeps its own 20 % for the radiator valves it drives itself: at 20 % and below such a valve also shows Radiator valve problem.': 'De E32 houdt voor de radiatorkranen die hij zelf aanstuurt zijn eigen 20 % aan: op 20 % en lager toont zo’n kraan ook Probleem radiatorkraan.',
  '1 device': '1 apparaat',
  '{n} devices': '{n} apparaten',
  '{n} low': '{n} laag',
  'Low': 'Laag',
  'Fine': 'In orde',
  'No report': 'Geen melding',
  'Not in a room': 'In geen ruimte',
  'last reported {moment}': 'voor het laatst gemeld {moment}',
  'Bluetooth sensor': 'Bluetooth-sensor',
  'Radiator valve': 'Radiatorkraan',
  'Window or door contact': 'Raam- of deurcontact',
  'Setting device': 'Instelapparaat',
  'Temperature source': 'Temperatuurbron',
  'Choose 15, 20, 25 or 30 %.': 'Kies 15, 20, 25 of 30 %.'
 }};
const TITLES = {'shelly-add': 'Add a Shelly device', 'valve-add': 'Add a valve', batteries: 'Batteries'};
const SUBTITLES = {'shelly-add': 'First set the device up in the Shelly app: your Wi-Fi, a password and the cloud off.',
 'valve-add': 'Pair the valve with the gateway in the Shelly app first.', batteries: 'Every device that reports a battery, the lowest first.'};
// The rest of each add form's explanation, behind "More".
const MORE = {'shelly-add': 'Give it a fixed address in your router (a DHCP reservation), so the E32 always finds it.',
 'valve-add': 'Then add it here by its number: the first one is usually 200, the next 201 and so on. Choose the valve\'s room under Rooms → the room → Radiator valves.'};
// The block screens of #devices: [title, one sentence]; the screen above each in PARENTS.
const SCREENS = {
 bluetooth: ['Bluetooth sensors', 'Choose on a sensor\'s screen which room it measures for.'],
 pair: ['Pair a sensor', 'The E32 listens for about 30 seconds. Wake the sensor if needed.'],
 shelly: ['Shelly devices', 'The E32 talks to them itself over your home network, also without Home Assistant.'],
 bus: ['On the boiler bus', 'The devices the E32 hears on the boiler bus. There is nothing to set here.']};
const PARENTS = Object.freeze({bluetooth: 'list', pair: 'bluetooth', shelly: 'list', bus: 'list', sensor: 'bluetooth', device: 'shelly', batteries: 'list'});
// The error codes of the save and of the actions (Configure's sentences; the actions' codes as glossary block "1.4.1 DEVICES-WS").
const ERRORS = {
 connect_e32: 'Connect the E32 first: Configure → E32 connection.',
 shelly_unsupported: 'This E32 has no Shelly support. Shelly devices need an E32 V2 with firmware 1.1 or newer.',
 ble_name_invalid: 'Use a name of 1 to 40 characters without line breaks.',
 ble_storage_full: 'The E32 has no room left to store the sensors. Nothing was saved.',
 ble_rejected: 'The E32 refused the changes ({error}). Nothing was saved.',
 ble_changed: 'The Bluetooth sensors were changed on the E32 meanwhile. Nothing was saved; open Bluetooth sensors again.',
 ble_address_invalid: 'Enter a Bluetooth address with six hexadecimal pairs.',
 ble_already_paired: 'This sensor is already paired with the E32.',
 ble_full: 'You can add at most 8 Bluetooth devices.',
 ble_profile_needed: 'Choose the sensor type: the E32 cannot tell it from the name.',
 ble_profile_invalid: 'This Bluetooth device profile is not supported.',
 ble_encryption_invalid: 'Select the encryption offered for this device profile.',
 ble_key_needed: 'This sensor sends encrypted readings: enter its 32-character key (bindkey).',
 ble_key_invalid: 'Enter exactly 32 hexadecimal characters for the bindkey.',
 ble_key_not_used: 'Unencrypted readings need no key: leave the bindkey empty or choose encrypted BTHome.',
 ble_scan_not_started: 'Search did not start. A scan may already be running, disabled, cooling down or unavailable.',
 // 1.4.2 (plan 3.9): "Measures for" on a sensor's screen (glossary block 1.4.2 HA-DEVICES).
 ble_room_full: '{room} already has {max} temperature sources. Remove one there first.',
 ble_room_only_source: '{room} measures only with this sensor. Give {room} another temperature source first.',
 ble_room_refused: 'The temperature sources of {room} cannot be changed like this ({error}). Change them on the room\'s screen.',
 ble_room_not_saved: 'The room could not be changed on the E32 ({error}). Nothing was changed.',
 ble_room_missing: 'This room no longer exists. Choose another room.',
 shelly_probe_role_duplicate: 'Each probe role can be used once.',
 shelly_probe_invalid: 'Choose a pipe from the list for each probe.',
 scan_busy: 'A search runs at another gateway. Try again in a minute.',
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
 e32_password_changed: 'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.',
 battery_limit_invalid: 'Choose 15, 20, 25 or 30 %.'};
// Product names and short type names stay as they are in every language.
const NAMES = {switch: 'Plug', probes: 'The Pill', gateway: 'BLU Gateway', pvvx_thermometer: 'pvvx', shelly_ht_display: 'Shelly H&T',
 xiaomi_monitor_3: 'Xiaomi', shelly_ht_full: 'Shelly BLU H&T Display', xiaomi_full: 'Xiaomi Monitor 3 (MJWSD05MMC)'};
// Configure's and the E32 page's words for a Shelly device and its state (e32_devices.WORDS).
const JOBS = {switch: 'Plug: switches the floor pump', probes: 'The Pill: temperature probes on the pipes', gateway: 'BLU Gateway: Shelly BLU TRV radiator valves'};
const HEALTH = {waiting: 'waiting for the first answer', ok: 'connected', unreachable: 'not reachable', wrong_device: 'another device answers at this address',
 auth_failed: 'the password is not accepted', error: 'the device reports an error'};
const VALVE_HEALTH = {waiting: 'waiting for a report', ok: 'reporting', silent: 'silent for 15 minutes', offline: 'not reporting',
 missing: 'not found at the gateway', unpaired: 'not paired with the gateway', gateway: 'gateway not reachable'};
const ROLES = {boiler: 'Boiler', thermostat: 'Thermostat', device: 'EMS device'};
const DONE = {ble_saved: 'Saved on the E32. It restarts in about 30 seconds to use the changes.',
 ble_saved_restart_later: 'Saved on the E32. It restarts to use the changes as soon as an update or boiler test has finished.',
 ble_unchanged: 'Nothing changed; the E32 was not written.'};
// The pipes of The Pill's probes (heating_link.PROBE_ROLES; the E32 page's words); loop_return_<n> and other_<n> are numbered.
const PIPES = {floor_supply: 'Water to the floor (after the mixing valve)', floor_return: 'Water back from the floor'};
const PROBE_HEALTH = {waiting: 'Waiting for a reading', no_reading: 'No reading', missing: 'Not found on The Pill'};
// Why the gateway's search found nothing (gateway_scan_result reason; the E32 page's words).
const REASONS = {no_answer: 'The gateway did not answer. Try again, or add the valves by number below.', interrupted: 'The search was interrupted. Try again.',
 wrong_device: 'Another device answers at this address', password: 'The password is not accepted',
 no_list: 'The gateway gave no list of its valves. Update its firmware in the Shelly app, or add the valves by number below.'};
// The three sensor types the panel pairs (a Shelly BLU TRV goes through the BLU Gateway) and the encryptions each takes, its own first.
const TYPES = Object.freeze({pvvx_thermometer: ['none', 'bthome_v2'], shelly_ht_display: ['bthome_v2', 'none'], xiaomi_monitor_3: ['mibeacon_v4_v5']});
const ENCRYPTIONS = {none: 'Unencrypted', bthome_v2: 'BTHome v2 encrypted', mibeacon_v4_v5: 'MiBeacon v4/v5 encrypted'};
// Polling (S-DEVICES-WS): the Bluetooth search every 3 s until done; the gateway every 2 s for at most a minute.
const POLL_BLE_MS = 3000, POLL_GATEWAY_MS = 2000, GATEWAY_MS = 60000, MAX_SENSORS = 8;
// Material Design Icons (Apache-2.0) the kit does not carry.
const ICON_PATHS = Object.freeze({
 plug: 'M16,7V3H14V7H10V3H8V7H8C7,7 6,8 6,9V14.5L9.5,18V21H14.5V18L18,14.5V9C18,8 17,7 16,7Z',
 probe: 'M19.47 3.47L13.47 9.47L10.53 10C10.22 10.03 9.94 10.18 9.72 10.4L2.81 17.31C1.74 18.38 1.74 20.12 2.81 21.2C3.88 22.27 5.62 22.27 6.7 21.2L13.61 14.29C13.83 14.07 14 13.79 14.03 13.5L14.54 10.54L20.54 4.54L22 2L19.47 3.47M11 14.38C10.24 14.38 9.62 13.76 9.62 13S10.24 11.62 11 11.62 12.38 12.24 12.38 13C12.37 13.76 11.76 14.38 11 14.38Z',
 gateway: 'M20.2,5.9L21,5.1C19.6,3.7 17.8,3 16,3C14.2,3 12.4,3.7 11,5.1L11.8,5.9C13,4.8 14.5,4.2 16,4.2C17.5,4.2 19,4.8 20.2,5.9M19.3,6.7C18.4,5.8 17.2,5.3 16,5.3C14.8,5.3 13.6,5.8 12.7,6.7L13.5,7.5C14.2,6.8 15.1,6.5 16,6.5C16.9,6.5 17.8,6.8 18.5,7.5L19.3,6.7M19,13H17V9H15V13H5A2,2 0 0,0 3,15V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V15A2,2 0 0,0 19,13M8,18H6V16H8V18M11.5,18H9.5V16H11.5V18M15,18H13V16H15V18Z',
 wifi: 'M12,21L15.6,16.2C14.6,15.45 13.35,15 12,15C10.65,15 9.4,15.45 8.4,16.2L12,21M12,3C7.95,3 4.21,4.34 1.2,6.6L3,9C5.5,7.12 8.62,6 12,6C15.38,6 18.5,7.12 21,9L22.8,6.6C19.79,4.34 16.05,3 12,3M12,9C9.3,9 6.81,9.89 4.8,11.4L6.6,13.8C8.1,12.67 9.97,12 12,12C14.03,12 15.9,12.67 17.4,13.8L19.2,11.4C17.19,9.89 14.7,9 12,9Z',
 bus: 'M18,11H14.82C14.4,9.84 13.3,9 12,9C10.7,9 9.6,9.84 9.18,11H6C5.67,11 4,10.9 4,9V8C4,6.17 5.54,6 6,6H16.18C16.6,7.16 17.7,8 19,8A3,3 0 0,0 22,5A3,3 0 0,0 19,2C17.7,2 16.6,2.84 16.18,4H6C4.39,4 2,5.06 2,8V9C2,11.94 4.39,13 6,13H9.18C9.6,14.16 10.7,15 12,15C13.3,15 14.4,14.16 14.82,13H18C18.33,13 20,13.1 20,15V16C20,17.83 18.46,18 18,18H7.82C7.4,16.84 6.3,16 5,16A3,3 0 0,0 2,19A3,3 0 0,0 5,22C6.3,22 7.4,21.16 7.82,20H18C19.61,20 22,18.93 22,16V15C22,12.07 19.61,11 18,11M19,4A1,1 0 0,1 20,5A1,1 0 0,1 19,6A1,1 0 0,1 18,5A1,1 0 0,1 19,4M5,20A1,1 0 0,1 4,19A1,1 0 0,1 5,18A1,1 0 0,1 6,19A1,1 0 0,1 5,20Z',
 valve: 'M4 22H2V2H4M22 2H20V22H22M17.24 5.34L13.24 9.34A3 3 0 0 0 9.24 13.34L5.24 17.34L6.66 18.76L10.66 14.76A3 3 0 0 0 14.66 10.76L18.66 6.76Z',
 magnify: 'M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z',
 trash: 'M9,3V4H4V6H5V19A2,2 0 0,0 7,21H17A2,2 0 0,0 19,19V6H20V4H15V3H9M7,6H17V19H7V6M9,8V17H11V8H9M13,8V17H15V8H13Z',
 signal3: 'M21,4H16V20H21V4M14,9H9V20H14V9M7,14H2V20H7V14Z',
 signal2: 'M19.5,5.5V18.5H17.5V5.5H19.5M21,4H16V20H21V4M14,9H9V20H14V9M7,14H2V20H7V14Z',
 signal1: 'M19.5,5.5V18.5H17.5V5.5H19.5M12.5,10.5V18.5H10.5V10.5H12.5M21,4H16V20H21V4M14,9H9V20H14V9M7,14H2V20H7V14Z',
 battery: 'M16,20H8V6H16M16.67,4H15V2H9V4H7.33A1.33,1.33 0 0,0 6,5.33V20.67C6,21.4 6.6,22 7.33,22H16.67A1.33,1.33 0 0,0 18,20.67V5.33C18,4.6 17.4,4 16.67,4Z'});
const KIND_ICON = Object.freeze({switch: 'plug', probes: 'probe', gateway: 'gateway'});
const BUS_ICON = Object.freeze({boiler: 'fire', thermostat: 'thermostat', device: 'devices'});

/* ---- helpers of this section (the kit is full: they live here) ---- */
const hex = address => String(address).match(/../g).join(':').toUpperCase();
const deviceName = d => d.label || NAMES[d.kind];
const sleep = ms => new Promise(done => setTimeout(done, ms));
function icon(kit, name, size = 24) {
 if (kit.icons.includes(name)) return kit.icon(name, {size});
 const svg = kit.icon('info', {size});
 svg.setAttribute('data-icon', name);
 svg.firstChild.setAttribute('d', ICON_PATHS[name] || ICON_PATHS.wifi);
 return svg;
}
// A card whose head icon may be one of this section's.
function card(kit, {icon: name, ...o}, ...children) {
 const el = kit.card({...o, icon: kit.icons.includes(name) ? name : 'info'}, ...children);
 if (!kit.icons.includes(name)) el.querySelector('.ot-card-icon')?.replaceChildren(icon(kit, name));
 return el;
}
// A button with one of this section's icons (kit.button knows only the kit's).
function button(kit, text, onClick, kind, name, attrs = {}) {
 const el = kit.button('', onClick, kind, attrs);
 el.replaceChildren(...[name ? icon(kit, name, 20) : null, kit.h('span', {text})].filter(Boolean));
 return el;
}
// A list row in the core's row look, with status labels and a value on the right: a link (route), a button or static.
function item(kit, {name, label, lines = [], chips = [], value, route, onClick, disabled, data = {}, trailing, live}) {
 const {h} = kit, attrs = {class: 'row with-icon dv-row' + (disabled ? ' muted' : '') + (route || onClick ? '' : ' static')};
 for (const [k, v] of Object.entries(data)) attrs['data-' + k] = v;
 const el = route && !disabled ? h('a', {...attrs, href: route}) : onClick ? h('button', {...attrs, type: 'button', disabled}) : h('div', attrs);
 if (onClick && !disabled) el.addEventListener('click', e => { if (e.button || e.metaKey || e.ctrlKey || e.shiftKey) return; e.preventDefault(); onClick(e); });
 const text = h('span', {class: 'row-text'}, h('span', {class: 'row-label'}, label));
 for (const line of lines.filter(Boolean)) text.append(h('span', {class: 'row-line', text: kit.together(line)}));
 const tags = h('span', {class: 'dv-chips'});
 text.append(tags);
 const right = h('span', {class: 'dv-value'});
 const draw = hass => {
  const now = live ? live(hass) : {chips, value};
  tags.replaceChildren(...(now.chips || []).filter(Boolean).map(([t, tone, i]) => kit.chip(kit.together(t), tone, i)));
  tags.hidden = !tags.childElementCount;
  right.textContent = now.value ? kit.together(now.value) : '';
  right.hidden = !now.value;
 };
 if (live) { el.setAttribute('data-live', ''); el._live = draw; }
 draw(null);
 el.append(h('span', {class: 'row-icon'}, icon(kit, name)), text, right);
 if (trailing) el.append(trailing);
 else if ((route || onClick) && !disabled) el.append(h('span', {class: 'chevron'}, kit.icon('chevron-right', {size: 20})));
 return el;
}
// A reading of a Home Assistant sensor: {value, unit} or null.
function reading(hass, id) {
 const st = id && hass?.states?.[id], value = st && st.state !== '' ? Number(st.state) : NaN;
 return st && Number.isFinite(value) ? {value, unit: st.attributes?.unit_of_measurement || ''} : null;
}
const shown = (kit, r, lang, digits) => (r ? `${kit.number(r.value, lang, digits)} ${r.unit}`.trim() : '');
const signal = rssi => (typeof rssi !== 'number' ? null : rssi >= -65 ? ['Strong signal', 'signal3'] : rssi >= -80 ? ['Fair signal', 'signal2'] : ['Weak signal', 'signal1']);
const pipeOf = (role, t) => {
 if (PIPES[role]) return t(PIPES[role]);
 const m = /^(loop_return|other)_(\d+)$/.exec(role || '');
 return m ? t(m[1] === 'loop_return' ? 'Back from floor loop {n}' : 'Other probe {n}', {n: m[2]}) : role;
};
const problem = tone => (tone ? 'attention' : 'rest');

/* ---- the screens of #devices, one address each (1.4.2): the core reads, saves and keeps the history ---- */
const state = {screen: 'list', root: null, ctx: null, item: null, flash: null, quiet: null, form: null, scan: null, pill: null, gateway: null,
 prefill: null, valveGateway: null, valveFrom: null, autostart: false, followed: null};
const SCREEN = /^(bluetooth|pair|shelly|bus|batteries|sensor\/[0-9a-f]{12}|pair\/[0-9a-f]{12}|device\/[^/]+)$/;
const screenOf = item => (item && SCREEN.test(item) ? item : 'list');
const parentOf = screen => (screen.startsWith('pair/') ? 'pair' : PARENTS[screen.split('/')[0]] || 'list');
const routeTo = screen => (screen === 'list' ? '#devices' : '#devices/' + screen);
// Open a screen: one step in the browser's history (the core's), its model read for it.
function show(screen) { state.ctx?.navigate(routeTo(screen)); }
// The screen changed (a link, back, forward, a reload): what belonged to the one before goes.
function moveTo(screen) {
 if (screen === state.screen) return false;
 state.screen = screen; state.flash = state.flash?.model ? null : state.flash; state.quiet = null;
 // A bindkey never outlives its form; a device's screen reads its probes again.
 if (state.form && screen !== 'pair/' + state.form.address) state.form.bindkey = '';
 if (!screen.startsWith('device/')) state.pill = null;
 return true;
}
const FOCUS = Object.freeze(['fk', 'found', 'foundValve', 'search', 'gatewayScan', 'saveRoles', 'pairSubmit', 'removeValve']);
function redraw(moved) {
 const {root, ctx} = state;
 if (!root?.isConnected || !ctx || screenOf(ctx.item) !== state.screen) return;
 // Focus stays where it was across a redraw (a field, a row the search found, a button), unless the screen moved.
 const a = root.getRootNode().activeElement, key = !moved && a && root.contains(a) ? FOCUS.find(k => a.dataset?.[k] != null) : null;
 const focus = key && `[data-${key.replace(/[A-Z]/g, c => '-' + c.toLowerCase())}="${CSS.escape(a.dataset[key])}"]`;
 root.replaceChildren(...drawScreen(ctx).filter(Boolean), ctx.kit.h('style', {text: STYLE + BATTERY_STYLE}));
 root.dataset.screen = state.screen.split('/')[0];
 if (focus) root.querySelector(focus)?.focus({preventScroll: true});
}
// A new screen: its title gets the focus (keyboard and screen reader users start there), the page scrolled up to it.
function focusTitle(root) {
 queueMicrotask(() => {
  if (!root.isConnected) return;
  const host = root.getRootNode().host;
  if (host && host.getBoundingClientRect().top < 0) host.scrollIntoView({block: 'start'});
  (root.querySelector('.dv-head .title') || root.closest('.page')?.querySelector('.title'))?.focus({preventScroll: true});
 });
}
// A screen's own head (the core's head stays for the list): back to the screen above, title, one sentence.
function head(ctx, title, subtitle) {
 const {kit, t} = ctx, {h} = kit, up = parentOf(state.screen);
 const label = up === 'list' ? t('Devices') : up === 'pair' ? t('Devices found') : t(SCREENS[up][0]);
 return h('header', {class: 'head dv-head'},
  h('a', {class: 'back', href: routeTo(up), 'data-dv-back': up, on: {click: e => { e.preventDefault(); show(up); }}},
   kit.icon('chevron-left', {size: 20}), h('span', {text: t('Back to {page}', {page: label})})),
  h('h2', {class: 'title', text: title, tabindex: '-1'}), subtitle ? h('p', {class: 'subtitle', text: subtitle}) : null);
}
// What the last save did (model.live.saved), on the screens it belongs to, until you move on.
function saved(ctx, kinds) {
 const {kit, t, model: m} = ctx, done = m.live?.saved;
 if (!done || !kinds.includes(done.done) || state.quiet === m) return null;
 const name = done.name || NAMES[done.kind] || '';
 // "Measures for" (1.4.2): the room it measures for now, then what the E32 does with a new name.
 const room = done.room === undefined ? '' : done.room ? t('Saved: it measures for {room} now.', {room: done.room}) : t('Saved: no room measures with it now.');
 const text = done.done === 'removed' ? t('{name} removed.', {name}) : done.done === 'valves_removed' ? t('Valves removed: {count}.', {count: done.count})
  : done.done === 'room_saved' ? room : [room, t(DONE[done.done])].filter(Boolean).join(' ');
 return kit.h('div', {class: 'dv-done', 'data-done': done.done}, kit.notice(text, 'success'));
}
// What was just added or paired, on the screen it went to, until you move on or save something else.
const flash = (ctx, kind) => {
 const f = state.flash;
 return f?.kind === kind && f.model === ctx.model ? ctx.kit.h('div', {class: 'dv-done', 'data-done': f.done}, ctx.kit.notice(f.text, 'success')) : null;
};
const toolbar = (kit, text, action) => kit.h('div', {class: 'dv-toolbar'}, kit.h('p', {class: 'help', text}), action);
const errorLine = (kit, text) => (text ? kit.inlineError(text) : null);

function drawScreen(ctx) {
 const s = state.screen;
 if (s === 'bluetooth') return bluetoothScreen(ctx);
 if (s === 'pair') return pairScreen(ctx);
 if (s.startsWith('pair/')) return pairForm(ctx, s.slice(5));
 if (s.startsWith('sensor/')) return sensorScreen(ctx, s.slice(7));
 if (s === 'shelly') return shellyScreen(ctx);
 if (s.startsWith('device/')) return deviceScreen(ctx, s.slice(7));
 if (s === 'bus') return busScreen(ctx);
 if (s === 'batteries') return batteriesScreen(ctx);
 return listScreen(ctx);
}

/* ---- #devices: the three blocks ---- */
function bleFacts(ctx) {
 const m = ctx.model, live = m.live?.bluetooth || {};
 return (m.bluetooth || []).map(s => ({sensor: s, info: live[s.address] || {}, temperature: reading(ctx.hass, live[s.address]?.temperature)}));
}
// The room a sensor measures for (the rooms whose temperature sources list it), or that it has none yet.
const measuresLine = (t, info) => (info.rooms?.length ? t('Measures for {rooms}', {rooms: info.rooms.join(', ')}) : t('Not assigned to a room yet'));
// The age of the sensor's last reading, from its temperature entity (age_s, sent with every E32 message).
function lastReading(t, hass, id) {
 const age = hass?.states?.[id]?.attributes?.age_s;
 if (typeof age !== 'number' || age < 0) return null;
 return age < 60 ? t('Last reading {n} s ago', {n: Math.round(age)}) : age < 3600 ? t('Last reading {n} min ago', {n: Math.floor(age / 60)})
  : t('Last reading {n} h ago', {n: Math.floor(age / 3600)});
}
function listScreen(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit;
 const ble = m.bluetooth, sh = m.shelly, bus = m.live?.bus;
 const silent = ble ? bleFacts(ctx).filter(f => !f.temperature).length : 0;
 const bleLine = ble == null ? t('Needs a newer E32 firmware') : !ble.length ? t('No sensors paired yet')
  : [t('{n} paired', {n: ble.length}), silent ? t('{n} without a reading', {n: silent}) : ''].filter(Boolean).join(' · ');
 const shellyLine = sh == null ? t('Needs a newer E32 firmware') : !sh.devices.length ? t('No Shelly devices yet.')
  : sh.devices.map(d => (d.kind === 'gateway' ? ((d.valves || []).length === 1 ? t('{gateway} with 1 valve', {gateway: deviceName(d)})
   : t('{gateway} with {n} valves', {gateway: deviceName(d), n: (d.valves || []).length})) : deviceName(d))).join(' · ');
 const busLine = bus == null ? t('The E32 has not reported them yet.') : !bus.length ? t('Nothing heard yet.')
  : bus.map(d => d.name || t(ROLES[d.role] || 'EMS device')).join(' · ');
 const go = screen => ({route: routeTo(screen), onClick: () => show(screen)});
 return [h('div', {class: 'card list dv-blocks'},
  item(kit, {name: 'bluetooth', label: t('Bluetooth sensors'), lines: [bleLine], data: {block: 'bluetooth'}, ...go('bluetooth')}),
  item(kit, {name: 'wifi', label: t('Shelly devices'), lines: [shellyLine], data: {block: 'shelly'}, ...go('shelly')}),
  item(kit, {name: 'bus', label: t('On the boiler bus'), lines: [busLine], data: {block: 'bus'}, ...go('bus')}),
  batteriesRow(ctx))];
}

/* ---- Bluetooth sensors ---- */
function bluetoothScreen(ctx) {
 const {kit, t, model: m, lang} = ctx, {h} = kit, out = [head(ctx, t('Bluetooth sensors'), t(SCREENS.bluetooth[1]))];
 out.push(flash(ctx, 'paired') || flash(ctx, 'ble') || saved(ctx, ['ble_saved', 'ble_saved_restart_later', 'ble_unchanged']));
 if (m.bluetooth == null) return [...out, kit.notice(t(ERRORS.e32_settings_update_required), 'info')];
 const full = m.bluetooth.length >= MAX_SENSORS;
 // Pair a sensor opens the search and starts it (a reload or a link to #devices/pair waits for you to search).
 const pair = button(kit, t('Pair a sensor'), () => { state.autostart = true; show('pair'); }, 'filled', 'plus', {disabled: ctx.readOnly || full, 'data-pair': ''});
 if (!m.bluetooth.length) return [...out, h('div', {class: 'ot-card'}, kit.empty({icon: 'bluetooth', text: t('No Bluetooth sensors yet. Pair your first sensor.'), action: pair}))];
 out.push(toolbar(kit, t('{n} of 8 paired', {n: m.bluetooth.length}), pair));
 if (full) out.push(h('p', {class: 'help dv-full', text: t('You can add at most 8 Bluetooth devices.')}));
 const list = h('div', {class: 'card list', 'data-list': 'sensors'});
 for (const f of bleFacts(ctx)) {
  const s = f.sensor, info = f.info, sig = signal(info.rssi);
  // Per sensor: its name (marked when it is automatic), the room it measures for, its reading, battery, signal and age.
  list.append(item(kit, {name: 'bluetooth', label: info.shown || s.name || hex(s.address), data: {sensor: s.address}, route: routeTo('sensor/' + s.address),
   onClick: () => show('sensor/' + s.address), lines: [measuresLine(t, info)],
   live: hass => {
    const temp = reading(hass || ctx.hass, info.temperature), battery = reading(hass || ctx.hass, info.battery), age = lastReading(t, hass || ctx.hass, info.temperature);
    return {value: temp ? shown(kit, temp, lang, 1) : '', chips: [info.automatic ? [t('automatic'), 'rest'] : null, !temp ? [t('No reading'), 'attention', 'alert'] : null,
     battery ? [t('battery {value}', {value: shown(kit, battery, lang, 0)}), problem(battery.value < (m.live?.battery_limit ?? 20))] : null, sig ? [t(sig[0]), 'rest'] : null,
     temp && age ? [age, 'rest'] : null]};
   }}));
 }
 out.push(list);
 return out;
}

// The question of a Bluetooth save: the E32 restarts once (Configure's words).
const restartQuestion = ctx => ({title: ctx.t('Save the Bluetooth changes?'),
 text: ctx.t('The E32 saves these changes and restarts once, about 30 seconds later; the heating continues after about a minute.'),
 confirm: ctx.t('Save and let the E32 restart')});
function sensorScreen(ctx, address) {
 const {kit, t, model: m, lang} = ctx, {h} = kit;
 if (m.missing) {  // a link to a sensor that was forgotten
  return [head(ctx, hex(address), t('Address {address}', {address: hex(address)})), kit.notice(t(ERRORS.ble_changed), 'info',
   kit.button(t('Bluetooth sensors'), () => show('bluetooth'), 'outlined', {'data-to-list': ''}))];
 }
 const info = m.live || {}, type = TYPES[m.profile] ? NAMES[m.profile] : m.profile, name = info.shown || m.own_name || hex(address);
 const out = [head(ctx, name, [type, t('Address {address}', {address: hex(address)})].join(' · '))];
 out.push(saved(ctx, ['ble_saved', 'ble_saved_restart_later', 'ble_unchanged', 'room_saved']));
 // The readings now, from the sensor's own Home Assistant entities (in Home Assistant's units).
 const values = h('div', {class: 'dv-readings', 'data-live': ''});
 values._live = hass => {
  const temp = reading(hass, info.temperature), hum = reading(hass, info.humidity), bat = reading(hass, info.battery);
  values.replaceChildren(kit.valueDisplay({value: temp ? kit.number(temp.value, lang, 1) : null, unit: temp?.unit, label: t('Temperature')}),
   ...(hum ? [kit.valueDisplay({value: kit.number(hum.value, lang, 0), unit: hum.unit, label: t('Humidity'), size: 'small'})] : []),
   ...(bat ? [kit.valueDisplay({value: kit.number(bat.value, lang, 0), unit: bat.unit, label: t('Battery'), size: 'small', tone: bat.value < (m.live?.battery_limit ?? 20) ? 'attention' : ''})] : []));
 };
 values._live(ctx.hass);
 const age = h('p', {class: 'help', 'data-live': ''});
 age._live = hass => { const text = lastReading(t, hass, info.temperature); age.textContent = text || ''; age.hidden = !text; };
 age._live(ctx.hass);
 out.push(h('div', {class: 'ot-card dv-sensor'}, values, h('p', {class: 'help', 'data-measures': '', text: measuresLine(t, info)}), age));
 // Its own name on the E32 (a sensor without one is named after its room: marked "automatic", kept with one tap) and
 // the room it measures for (that room's first temperature source; one plan write).
 const auto = info.automatic ? h('div', {class: 'dv-auto', 'data-automatic': ''}, kit.chip(t('automatic'), 'rest'),
  ctx.readOnly ? null : kit.button(t('Keep this name'), () => ctx.act({name}, restartQuestion(ctx)), 'text', {'data-keep-name': ''})) : null;
 out.push(h('div', {class: 'card form'}, h('div', {class: 'fields'},
  ctx.field('text', 'name', {label: t('Name'), maxlength: 40, help: t('Without a name of its own, the sensor is named after the room that measures with it.')}), auto,
  ctx.field('select', 'measures_for', {label: t('Measures for'), help: t('The room uses it as its first temperature source; other rooms stop using it.'),
   options: [{value: '', label: t('No room')}, ...(m.rooms || []).map(r => ({value: r.id, label: r.name}))]}))));
 // Its entities still carry an older name: Installation → Tidy entity IDs renames them (with a preview first).
 if (info.ids_stale && !ctx.readOnly) out.push(h('div', {'data-ids-stale': ''}, kit.notice(t('The entity IDs in Home Assistant still carry an older name.'), 'info',
  kit.button(t('Tidy entity IDs'), () => ctx.navigate('#installation'), 'outlined', {'data-tidy': ''}))));
 if (!ctx.readOnly) out.push(h('div', {class: 'dv-remove'}, button(kit, t('Forget sensor'), () => ctx.act({[`ble_forget:${address}`]: true}, {
  title: t('Forget {name}?', {name}),
  text: [t('The E32 stops reading it and deletes its key, then restarts once, about 30 seconds later. To use it again, pair it again.'),
   info.rooms?.length ? t('Rooms that measure with it: {rooms}.', {rooms: info.rooms.join(', ')}) : ''].filter(Boolean).join(' '),
  confirm: t('Forget'), danger: true}), 'danger', 'trash', {'data-forget': address})));
 return out;
}

/* ---- Pair a sensor: the E32 searches, the panel shows what it hears ---- */
// start: ask the E32 to search (Search); without it, follow a search that already runs (one started before, here or on
// the E32's page) until it is done.
async function startScan(start = true) {
 const ctx = state.ctx;
 if (!ctx || ctx.readOnly) return;
 const kept = start ? [] : state.scan?.sensors || [];
 const run = state.scan = {running: true, sensors: kept, error: null, full: false, paired: null, max: MAX_SENSORS,
  discovery: ctx.model.live?.discovery != null};
 redraw();
 const alive = () => state.scan === run && run.running && state.root?.isConnected && state.ctx?.item === 'pair' && state.screen === 'pair';
 if (start) {
  try { await ctx.action('scan'); } catch (e) { if (state.scan === run) { run.running = false; run.error = e.text; redraw(); } return; }
 }
 while (alive()) {
  await sleep(POLL_BLE_MS);
  if (!alive()) break;
  try {
   const r = await state.ctx.action('scan_result');
   if (state.scan !== run) return;
   Object.assign(run, {sensors: r.sensors || [], full: r.full === true, paired: r.paired, max: r.max || MAX_SENSORS,
    discovery: r.discovery != null});
   if (r.done) run.running = false;
  } catch (e) { if (state.scan !== run) return; run.running = false; run.error = e.text; }
  if (state.screen === 'pair') redraw();
 }
 // Left the screen: no poller stays behind (the E32 has four web sessions); what was found stays.
 if (state.scan === run) run.running = false;
}
function pairScreen(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit, out = [head(ctx, t('Pair a sensor'), t(SCREENS.pair[1]))];
 if (m.supported === false) return [...out, kit.notice(t(ERRORS.e32_settings_update_required), 'info')];
 // Opened from Pair a sensor: search at once. Opened while a search runs (E32 1.4.2: queued or running; older firmware:
 // the panel's own, younger than 95 s): follow it, Search stays off until it is done. An automatic scan of the E32
 // (it reads its paired sensors) is no search: Search stays on.
 const follow = !!m.live?.searching && state.followed !== m;
 if (!ctx.readOnly && !state.scan?.running && (state.autostart || follow)) {
  const start = state.autostart;
  state.autostart = false; state.followed = m;
  queueMicrotask(() => startScan(start));
 }
 const scan = state.scan, running = !!scan?.running || follow, found = scan?.sensors || [];
 const atMax = scan?.paired != null ? scan.paired >= scan.max : m.paired >= (m.max || MAX_SENSORS);
 const searching = (scan ? scan.discovery : m.live?.discovery != null) ? t('Searching… (up to 90 s)') : t('Searching nearby…');
 if (running) out.push(h('div', {class: 'dv-status', 'data-status': 'searching'}, kit.statusLine(searching, 'accent')));
 out.push(errorLine(kit, scan?.error));
 const again = button(kit, t('Search nearby'), () => startScan(), found.length ? 'outlined' : 'filled', 'magnify', {disabled: ctx.readOnly || running, 'data-search': ''});
 if (!running) out.push(h('div', {class: 'dv-actions'}, again));
 if (atMax) out.push(kit.notice(t('You can add at most 8 Bluetooth devices.'), 'warning'));
 if (scan?.full) out.push(kit.notice(t('More devices were received than this list can hold. Search again nearer to the device you want to add.'), 'info'));
 if (found.length) {
  out.push(h('p', {class: 'help dv-lead', text: t('Choose your sensor.')}));
  const list = h('div', {class: 'card list', 'data-list': 'found'});
  for (const d of found) {
   const sig = signal(d.rssi), type = TYPES[d.kind] ? NAMES[d.kind] : null;
   list.append(item(kit, {name: 'bluetooth', label: d.name || t('Unnamed Bluetooth device'), data: {found: d.address},
    lines: [[hex(d.address), sig ? t(sig[0]) : ''].filter(Boolean).join(' · ')],
    chips: [d.known ? [t('Already added'), 'rest', 'check'] : type ? [type, 'accent'] : null],
    disabled: d.known || atMax || ctx.readOnly, onClick: () => openForm(d)}));
  }
  out.push(list);
 } else if (running) out.push(h('div', {class: 'dv-wait', role: 'status', 'aria-label': searching}, kit.skeleton('rows', 3)));
 else if (scan && !scan.error) out.push(h('div', {class: 'ot-card'}, kit.empty({icon: 'bluetooth', text: t('No devices found yet. Start a search and wake the sensor if needed.')})));
 return out;
}
function formOf(d) {
 const profile = TYPES[d.kind] ? d.kind : null;
 return {address: d.address, heard: d.name || '', rssi: d.rssi, name: d.name || '', profile, guessed: !!profile,
  encryption: profile ? (TYPES[profile].includes(d.encryption) ? d.encryption : TYPES[profile][0]) : null, bindkey: '', errors: {}, base: null, busy: false};
}
function openForm(d) {
 state.form = formOf(d);
 show('pair/' + d.address);
}
function pairForm(ctx, address) {
 const {kit, t, hass, model: m} = ctx, {h} = kit;
 // A link or a reload: the form from what the E32 heard (#devices/pair/<address> reads it), else empty.
 if (!state.form || state.form.address !== address) state.form = formOf({address, ...(m.live?.heard || {})});
 const f = state.form, sig = signal(f.rssi);
 const out = [head(ctx, f.heard || t('Unnamed Bluetooth device'), [t('Address {address}', {address: hex(address)}), sig ? t(sig[0]) : ''].filter(Boolean).join(' · '))];
 const fields = {};
 const add = (key, api) => { fields[key] = api; if (f.errors[key]) api.setError(f.errors[key]); return api.el; };
 const name = add('name', kit.fields.text({key: 'name', label: t('Name'), value: f.name, hass, maxlength: 40, required: true, disabled: ctx.readOnly,
  help: t('At most 40 characters (fewer with special letters).'), onChange: v => { f.name = v; }}));
 const help = {pvvx_thermometer: t('Thermometer with pvvx firmware (BTHome)'), shelly_ht_display: NAMES.shelly_ht_full,
  xiaomi_monitor_3: `${NAMES.xiaomi_full} · ${t(ENCRYPTIONS.mibeacon_v4_v5)}`};
 const type = add('profile', kit.fields.segmented({key: 'profile', label: t('Sensor type'), value: f.profile, hass, disabled: ctx.readOnly,
  help: f.guessed ? t('Guessed from the device name: check it.') : null,
  options: Object.keys(TYPES).map(value => ({value, label: NAMES[value], help: help[value]})),
  onChange: v => { f.profile = v; f.guessed = false; f.encryption = TYPES[v][0]; delete f.errors.profile; redraw(); root().querySelector(`[data-fk="profile:${v}"]`)?.focus(); }}));
 const parts = [name, type];
 if (f.profile && TYPES[f.profile].length > 1) parts.push(add('encryption', kit.fields.segmented({key: 'encryption', label: t('Encryption'), value: f.encryption, hass,
  disabled: ctx.readOnly, options: TYPES[f.profile].map(value => ({value, label: t(ENCRYPTIONS[value])})),
  onChange: v => { f.encryption = v; delete f.errors.encryption; redraw(); root().querySelector(`[data-fk="encryption:${v}"]`)?.focus(); }})));
 if (f.profile && f.encryption !== 'none') {
  // The key goes to the E32 once, in the pair action; shown as dots, never kept after it.
  const key = kit.fields.text({key: 'bindkey', label: t('Encryption key (bindkey)'), value: f.bindkey, hass, maxlength: 32, disabled: ctx.readOnly,
   help: t('An encrypted sensor needs its 32-character key (bindkey); the E32 stores it and never shows it again.'), onChange: v => { f.bindkey = v; }});
  Object.assign(key.input, {type: 'password', autocomplete: 'off', spellcheck: false});
  parts.push(add('bindkey', key));
 }
 if (m.known) out.push(kit.notice(t(ERRORS.ble_already_paired), 'info'));
 out.push(h('div', {class: 'card form'}, errorLine(kit, f.base), h('div', {class: 'fields'}, ...parts)));
 out.push(h('div', {class: 'dv-actions'}, button(kit, f.busy ? t('Pairing…') : t('Pair'), () => pair(fields), 'filled', 'bluetooth',
  {disabled: ctx.readOnly || f.busy || !!m.known, 'data-pair-submit': ''})));
 return out;
}
const root = () => state.root;
async function pair(fields) {
 const f = state.form, ctx = state.ctx;
 if (!f || f.busy) return;
 const values = {address: f.address, name: f.name};
 if (f.profile) { values.profile = f.profile; values.encryption = f.encryption; }
 if (f.profile && f.encryption !== 'none' && f.bindkey.trim()) values.bindkey = f.bindkey.trim();
 f.busy = true; f.errors = {}; f.base = null; redraw();
 try {
  const r = await ctx.action('pair', values);
  const restart = r.restart === false ? DONE.ble_saved_restart_later : DONE.ble_saved;
  const sensor = state.scan?.sensors?.find(d => d.address === f.address);
  if (sensor) sensor.known = true;
  state.form = null;  // the key with it
  state.flash = {kind: 'paired', done: 'paired', text: `${ctx.t('{name} paired.', {name: values.name.trim()})} ${ctx.t(restart)}`};
  ctx.navigate(routeTo('bluetooth'));
 } catch (e) {
  if (state.form !== f) return;
  f.busy = false;
  if (fields[e.field]) f.errors[e.field] = e.text; else f.base = e.text;
  redraw();
  root()?.querySelector(`[data-field="${CSS.escape(e.field)}"] input, [data-field="${CSS.escape(e.field)}"] button`)?.focus();
 }
}

/* ---- Shelly devices ---- */
function healthChip(t, health) {
 if (!HEALTH[health]) return null;
 const bad = !['ok', 'waiting'].includes(health);
 return [t(HEALTH[health]), problem(bad), bad ? 'alert' : health === 'ok' ? 'check' : null];
}
function shellyScreen(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit, sh = m.shelly, live = m.live?.shelly || {};
 const out = [head(ctx, t('Shelly devices'), t(SCREENS.shelly[1]))];
 out.push(flash(ctx, 'shelly') || saved(ctx, ['removed']));
 if (!sh) return [...out, kit.notice(t(ERRORS.shelly_unsupported), 'info')];
 const full = sh.devices.length >= sh.max_devices;
 const add = button(kit, t('Shelly device'), () => ctx.navigate('#devices/shelly-add'), 'filled', 'plus',
  {disabled: ctx.readOnly || full, 'aria-label': t('Add a Shelly device'), 'data-add-device': ''});
 if (!sh.devices.length) return [...out, h('div', {class: 'ot-card'}, kit.empty({icon: 'devices', text: t('No Shelly devices yet.'), action: add}))];
 out.push(kit.h('div', {class: 'dv-toolbar end'}, add));
 if (full) out.push(h('p', {class: 'help dv-full', text: t(ERRORS.shelly_full)}));
 const list = h('div', {class: 'card list', 'data-list': 'shelly'});
 for (const d of sh.devices) {
  const valves = d.kind === 'gateway' ? (d.valves || []).length : null;
  list.append(item(kit, {name: KIND_ICON[d.kind] || 'devices', label: deviceName(d), data: {device: d.id},
   lines: [[t(JOBS[d.kind]), d.ip].join(' · '), valves == null ? '' : valves === 1 ? t('1 valve') : t('{n} valves', {n: valves})],
   chips: [healthChip(t, live[String(d.n)])], route: routeTo('device/' + d.id), onClick: () => show('device/' + d.id)}));
 }
 out.push(list);
 return out;
}
function deviceScreen(ctx, id) {
 const {kit, t, model: m} = ctx, {h} = kit, d = m.device, live = m.live?.shelly || {};
 if (m.supported === false) return [head(ctx, t('Shelly device'), null), kit.notice(t(ERRORS.shelly_unsupported), 'info')];
 if (!d) {  // a link to a device that was removed
  return [head(ctx, t('Shelly device'), null), kit.notice(t('No Shelly devices yet.'), 'info',
   kit.button(t('Shelly devices'), () => show('shelly'), 'outlined', {'data-to-list': ''}))];
 }
 const out = [head(ctx, deviceName(d), t(JOBS[d.kind]))];
 const chip = healthChip(t, live[String(d.n)]);
 out.push(h('div', {class: 'ot-card dv-facts'}, h('span', {class: 'row-icon'}, icon(kit, KIND_ICON[d.kind] || 'devices')),
  h('div', {class: 'dv-fact'}, h('span', {class: 'label', text: t('IP address')}), h('span', {class: 'dv-ip', text: d.ip})),
  chip ? kit.chip(...chip) : null));
 if (d.kind === 'probes') out.push(pillCard(ctx, d));
 if (d.kind === 'gateway') out.push(flash(ctx, 'valve') || saved(ctx, ['valves_removed']), ...gatewayCards(ctx, d));
 if (d.pump) out.push(h('p', {class: 'help dv-why', 'data-pump': '', text: t(ERRORS.shelly_pump_in_use)}));
 else if (!ctx.readOnly) out.push(h('div', {class: 'dv-remove'}, button(kit, t('Remove device'), () => ctx.act({action: 'shelly_remove', device: d.id}, {
  title: t('Remove {name}?', {name: deviceName(d)}),
  text: t('The E32 stops reading and switching the device. The valves of a BLU Gateway stay in their rooms until you remove them under Rooms.'),
  confirm: t('Remove device'), danger: true}), 'danger', 'trash', {'data-remove-device': d.id})));
 return out;
}

/* The Pill: each probe's pipe, read with pill_roles and saved whole with set_pill_roles. */
async function loadPill(id) {
 const run = state.pill = {id, loading: true, answer: null, chosen: {}, error: null, errors: {}, busy: false, done: false};
 redraw();
 try {
  const answer = await state.ctx.action('pill_roles', {device: id});
  if (state.pill !== run) return;
  run.answer = answer;
  for (const p of answer.probes || []) run.chosen[p.c] = p.role || '';
 } catch (e) { if (state.pill === run) run.error = e.text; }
 if (state.pill === run) { run.loading = false; redraw(); }
}
function pillCard(ctx, d) {
 const {kit, t, lang} = ctx, {h} = kit, p = state.pill;
 const head = {title: t('Probe roles'), icon: 'probe', summary: t('Give each probe the pipe it sits on.'), data: {card: 'roles'}};
 const more = kit.more(t('The E32 uses the water to and back from the floor for the pump and to watch for too hot water.'), ctx.lang);
 // Reading the probes is an action, and actions are for administrators (CONTRACT-1.4.1 §3).
 if (ctx.readOnly) return card(kit, head, more);
 if (!p || p.id !== d.id) queueMicrotask(() => { if (state.screen === 'device/' + d.id && state.pill?.id !== d.id) loadPill(d.id); });
 const body = [];
 if (!p || p.id !== d.id || p.loading) body.push(h('div', {role: 'status', 'aria-label': t('Probe roles')}, kit.skeleton('rows', 2)));
 else if (p.error && !p.answer) body.push(kit.inlineError(p.error), kit.button(t('Try again'), () => loadPill(d.id), 'text', {'data-retry': ''}));
 else {
  const a = p.answer, used = a.in_use || {}, probes = a.probes || [];
  if (p.done) body.push(h('div', {class: 'dv-done', 'data-done': 'roles'}, kit.notice(t('Probe roles saved.'), 'success')));
  body.push(errorLine(kit, p.error));
  if (!probes.length) body.push(h('p', {class: 'help', text: t('The Pill reports no probes yet.')}));
  const fields = h('div', {class: 'fields'});
  for (const probe of probes) {
   const mine = p.chosen[probe.c] || '', held = probe.role && used[probe.role] && mine === probe.role && (a.roles || {})[probe.c] === probe.role;
   const now = probe.health === 'ok' && typeof probe.t_c === 'number' ? kit.degrees(probe.t_c, '°C', lang) : t(PROBE_HEALTH[probe.health] || PROBE_HEALTH.waiting);
   const taken = new Set(Object.entries(p.chosen).filter(([c, r]) => r && Number(c) !== probe.c).map(([, r]) => r));
   const api = kit.fields.select({key: `role:${probe.c}`, label: t('Probe {n}', {n: probe.c - 99}), value: mine, hass: ctx.hass, disabled: ctx.readOnly || held || p.busy,
    help: held ? `${kit.together(now)} · ${t('A heating circuit measures with this probe. Change the circuit first (on the E32: Home → Heating settings).')}` : kit.together(now),
    options: [{value: '', label: t('Not used')}, ...(a.choices || []).map(role => ({value: role, label: pipeOf(role, t)}))],
    onChange: v => { p.chosen[probe.c] = v; p.done = false; delete p.errors[probe.c]; redraw(); }});
   for (const option of api.el.querySelectorAll('option')) if (option.value && taken.has(option.value)) option.disabled = true;
   if (p.errors[probe.c]) api.setError(p.errors[probe.c]);
   api.el.dataset.probe = String(probe.c);
   fields.append(api.el);
  }
  body.push(fields);
  const changed = probes.some(x => (p.chosen[x.c] || '') !== ((a.roles || {})[x.c] || ''));
  if (probes.length) body.push(h('div', {class: 'dv-actions'}, kit.button(p.busy ? t('Saving…') : t('Save probe roles'), () => saveRoles(d.id), 'filled',
   {disabled: ctx.readOnly || p.busy || !changed, 'data-save-roles': ''})));
 }
 return card(kit, head, more, ...body);
}
async function saveRoles(id) {
 const p = state.pill;
 if (!p?.answer || p.busy) return;
 const roles = Object.fromEntries((p.answer.probes || []).map(x => [String(x.c), p.chosen[x.c] || null]));
 p.busy = true; p.error = null; p.errors = {}; p.done = false; redraw();
 try {
  const r = await state.ctx.action('set_pill_roles', {device: id, roles});
  if (state.pill !== p) return;
  p.answer = {...p.answer, roles: r.roles || {}, probes: p.answer.probes.map(x => ({...x, role: (r.roles || {})[x.c] || null}))};
  for (const x of p.answer.probes) p.chosen[x.c] = x.role || '';
  p.done = true;
 } catch (e) {
  if (state.pill !== p) return;
  const m = /^role:(\d+)$/.exec(e.field || '');
  if (m) p.errors[m[1]] = e.text; else p.error = e.text;
 }
 p.busy = false; redraw();
}

/* The BLU Gateway: its valves, and the search for the valves paired with it in the Shelly app. */
async function startGatewayScan(d) {
 const ctx = state.ctx;
 if (!ctx || ctx.readOnly) return;
 const run = state.gateway = {id: d.id, n: d.n, running: true, result: null, error: null, timeout: false, until: Date.now() + GATEWAY_MS};
 redraw();
 const alive = () => state.gateway === run && run.running && state.root?.isConnected && state.screen === 'device/' + d.id;
 try { await ctx.action('gateway_scan', {gateway: d.n}); } catch (e) { if (state.gateway === run) { run.running = false; run.error = e.text; redraw(); } return; }
 while (alive()) {
  await sleep(POLL_GATEWAY_MS);
  if (!alive()) break;
  try {
   const r = await state.ctx.action('gateway_scan_result', {gateway: d.n});
   if (state.gateway !== run) return;
   run.result = r;
   if (r.done) run.running = false;
   else if (Date.now() >= run.until) { run.running = false; run.timeout = true; }
  } catch (e) { if (state.gateway !== run) return; run.running = false; run.error = e.text; }
  if (state.screen === 'device/' + d.id) redraw();
 }
 if (state.gateway === run) run.running = false;
}
function gatewayCards(ctx, d) {
 const {kit, t, model: m} = ctx, {h} = kit, live = m.live?.shelly || {}, max = m.max_valves, valves = d.valves || [];
 const full = valves.length >= max;
 const list = h('div', {class: 'card list dv-inner', 'data-list': 'valves'});
 for (const v of valves) {
  const key = `${d.n}:${v.id}`, health = live[key], name = t('Valve {id}', {id: v.id}) + (v.name ? ` · ${v.name}` : '');
  const bad = health && !['ok', 'waiting'].includes(health);
  list.append(item(kit, {name: 'valve', label: name, data: {valve: key}, lines: [live['room:' + key] ? t('room: {room}', {room: live['room:' + key]}) : ''],
   chips: [VALVE_HEALTH[health] ? [t(VALVE_HEALTH[health]), problem(bad), bad ? 'alert' : null] : null],
   trailing: ctx.readOnly ? null : kit.iconButton('close', t('Remove {valve}', {valve: t('Valve {id}', {id: v.id})}), () => ctx.act({action: 'valves_remove', valves: [key]}, {
    title: t('Remove {name}?', {name: t('Valve {id}', {id: v.id})}),
    text: t('The E32 stops reading and driving these valves. A valve in a room stays there until you remove it under Rooms → the room → Radiator valves.'),
    confirm: t('Remove'), danger: true}), {'data-remove-valve': key})}));
 }
 if (!valves.length) list.append(h('p', {class: 'help dv-none', text: t('No valves yet.')}));
 const from = {id: d.id, name: deviceName(d)};
 const byNumber = kit.button(t('Add a valve'), () => { state.prefill = {gateway: String(d.n)}; state.valveFrom = from; ctx.navigate('#devices/valve-add'); }, 'text',
  {disabled: ctx.readOnly || full, 'data-add-valve': d.id});
 const valvesCard = card(kit, {title: t('Valves'), icon: 'valve', data: {card: 'valves'}}, list,
  full ? h('p', {class: 'help dv-full', text: t('A gateway takes at most 5 valves.')}) : null, h('div', {class: 'dv-actions'}, byNumber));
 // The search.
 const g = state.gateway?.id === d.id ? state.gateway : null, r = g?.result, body = [];
 const look = button(kit, t('Look for valves at the gateway'), () => startGatewayScan(d), 'filled', 'magnify',
  {disabled: ctx.readOnly || full || !!g?.running, 'data-gateway-scan': d.id});
 if (g?.running) body.push(h('div', {class: 'dv-status', 'data-status': 'looking'}, kit.statusLine(t('Looking for valves at the gateway…'), 'accent')));
 else body.push(h('div', {class: 'dv-actions'}, look));
 if (g?.error) body.push(kit.inlineError(g.error));
 else if (g?.timeout) body.push(h('div', {'data-status': 'no_answer'}, kit.statusLine(t(REASONS.no_answer), 'attention')));
 else if (r?.state === 'failed') body.push(h('div', {'data-status': r.reason || 'failed'}, kit.statusLine(t(REASONS[r.reason] || REASONS.interrupted), 'attention')));
 if (r?.more) body.push(h('p', {class: 'help', text: t('The gateway reported more devices than the E32 reads; not every valve may be listed.')}));
 const found = r?.state === 'ok' ? r.valves || [] : [];
 if (found.length) {
  const room = !full && !r.full;
  body.push(h('p', {class: 'help', text: room ? t('Tap a valve to add it.') : t('A gateway takes at most 5 valves.')}));
  const rows = h('div', {class: 'card list dv-inner', 'data-list': 'found-valves'});
  for (const v of found) rows.append(item(kit, {name: 'valve', label: t('Valve {id}', {id: v.id}) + (v.name ? ` · ${v.name}` : ''), data: {'found-valve': v.id},
   chips: [v.known ? [t('Already in the list'), 'rest', 'check'] : null], disabled: v.known || !room || ctx.readOnly,
   onClick: () => { state.prefill = {gateway: String(d.n), valve: v.id, name: v.name || ''}; state.valveFrom = from; ctx.navigate('#devices/valve-add'); }}));
  body.push(rows);
 } else if (r?.state === 'ok' && !g.running) body.push(h('p', {class: 'help', 'data-status': 'none', text: t('The gateway reports no paired valves. Pair them in the Shelly app first.')}));
 else if (g?.running) body.push(kit.skeleton('rows', 2));
 return [valvesCard, kit.h('section', {class: 'ot-card dv-search', 'data-card': 'search'}, ...body)];
}

/* ---- On the boiler bus (read-only) ---- */
function busScreen(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit, bus = m.live?.bus, out = [head(ctx, t('On the boiler bus'), t(SCREENS.bus[1]))];
 if (bus == null || !bus.length) return [...out, h('div', {class: 'ot-card'}, kit.empty({icon: 'fire', text: t(bus == null ? 'The E32 has not reported them yet.' : 'Nothing heard yet.')}))];
 out.push(h('div', {class: 'card list', 'data-list': 'bus'}, ...bus.map(d => item(kit, {name: BUS_ICON[d.role] || 'devices', label: d.name || t(ROLES[d.role] || 'EMS device'),
  data: {bus: d.address}, lines: [[d.name ? t(ROLES[d.role] || 'EMS device') : '', d.address].filter(Boolean).join(' · ')]}))));
 return out;
}

/* ---- #devices/batteries (1.4.2, HA-BATTERIES): every battery on one list, the limit in its head ---- */
// The backend's item "batteries" (settings_devices.py, device_battery.collect): {limit_pct, limits, live.devices: [{id, name,
// room, room_name, kind, pct, low, reported_at, source, entity_id}]}, low first. Read from Home Assistant alone (no E32 sign-in).
const BATTERY_KINDS = Object.freeze({thermometer: ['Bluetooth sensor', 'bluetooth'], valve: ['Radiator valve', 'valve'],
 contact: ['Window or door contact', 'window'], setting_device: ['Setting device', 'thermostat'],
 temperature_source: ['Temperature source', 'thermometer'], gateway: ['Gateway', 'gateway']});
const BATTERY_STYLE = `.dv-bat .ot-card-head{margin-bottom:var(--ot-s2)}.dv-bat>.field{border-top:0;padding-top:0}
.dv-bat>.dv-inner{margin-top:var(--ot-s3)}.dv-bat>.ot-empty{padding:var(--ot-s4) var(--ot-s2)}.dv-bat .btn.ot-more{min-height:44px}
.dv-bat .ot-seg-btn{min-height:44px;min-width:44px}`;
// The row on #devices: how many devices report a battery, a red label while one is low.
function batteriesRow(ctx) {
 const {kit, t, model: m} = ctx, b = m.live?.batteries;
 if (!b) return null;
 const line = !b.devices ? t('No device reports a battery.') : b.devices === 1 ? t('1 device') : t('{n} devices', {n: b.devices});
 return item(kit, {name: 'battery', label: t('Batteries'), lines: [line], data: {block: 'batteries'}, route: routeTo('batteries'), onClick: () => show('batteries'),
  chips: [b.low ? [t('{n} low', {n: b.low}), 'attention', 'alert'] : null]});
}
function batteriesScreen(ctx) {
 const {kit, t, model: m, lang, hass} = ctx, {h} = kit, rows = m.live?.devices || [];
 const lows = rows.filter(r => r.low).length;
 const head = rows.length ? [rows.length === 1 ? t('1 device') : t('{n} devices', {n: rows.length}), lows ? t('{n} low', {n: lows}) : ''].filter(Boolean).join(' · ') : '';
 const limit = ctx.field('segmented', 'limit_pct', {label: t('Warn below'), help: t('Below this a battery counts as low: on this list, in the messages and on the dashboard.'),
  more: t('The E32 keeps its own 20 % for the radiator valves it drives itself: at 20 % and below such a valve also shows Radiator valve problem.'),
  options: (m.limits || [15, 20, 25, 30]).map(v => ({value: v, label: kit.together(`${kit.number(v, lang, 0)} %`)}))});
 const body = card(kit, {icon: 'battery', title: t('Batteries'), summary: head, cls: 'dv-bat', data: {card: 'batteries'}}, limit);
 if (!rows.length) { body.append(kit.empty({icon: 'info', text: t('No device reports a battery.')})); return [body]; }
 const list = h('div', {class: 'card list dv-inner', 'data-list': 'batteries'});
 for (const r of rows) {
  const [kind, name] = BATTERY_KINDS[r.kind] || BATTERY_KINDS.thermometer;
  const when = r.reported_at ? kit.time.moment(hass, r.reported_at) : '';
  list.append(item(kit, {name, label: r.name, data: {battery: r.id, low: r.low === true ? 'true' : r.low === false ? 'false' : 'unknown'},
   lines: [[r.room_name || t('Not in a room'), t(kind)].join(' · '), when ? t('last reported {moment}', {moment: when}) : ''],
   value: r.pct != null ? `${kit.number(r.pct, lang, 0)} %` : r.low === false ? t('Fine') : r.low == null ? t('No report') : '',
   chips: [r.low ? [t('Low'), 'attention', 'alert'] : null]}));
 }
 body.append(list);
 return [body];
}

/* ---- #devices/shelly-add and #devices/valve-add (1.4's forms, in a card) ---- */
function addDevice(ctx) {
 const {kit, t} = ctx;
 // The password goes to the E32 only (settings_devices.py): never in a model, an error or the log; shown as dots.
 const password = ctx.field('text', 'password', {label: t('Device password'), maxlength: 64,
  help: t('The password you set in the Shelly app. It goes to the E32 only, which keeps a fingerprint of it; Home Assistant does not keep it. Leave it empty if the device has none.')});
 Object.assign(password.querySelector('input'), {type: 'password', autocomplete: 'new-password'});
 return kit.h('div', {class: 'card form'}, kit.h('div', {class: 'fields'},
  ctx.field('text', 'ip', {label: t('IP address'), maxlength: 15, placeholder: '192.168.1.40',
   help: t('For example 192.168.1.40. When you save, the E32 asks the device who it is, which takes up to 16 seconds.')}),
  ctx.field('radio', 'kind', {label: t('What does it do?'), options: [
   {value: 'auto', label: t('As the device says'), help: t('The E32 asks the device what it is when you save.')},
   ...Object.entries(JOBS).map(([value, label]) => ({value, label: t(label)}))]}),
  ctx.field('text', 'label', {label: t('Name'), maxlength: 32, help: t('The name the E32 and Home Assistant show, up to 32 characters.')}),
  password), kit.more(t(MORE['shelly-add']), ctx.lang));
}
function addValve(ctx) {
 const {kit, t, model: m} = ctx;
 if (!m.gateways?.length) return kit.h('div', {class: 'ot-card'}, kit.empty({icon: 'radiator', text: t('There is no BLU Gateway in the list yet. Add one first.')}));
 // A valve the gateway's search found, or the gateway it came from: filled in, to be saved.
 const fill = state.prefill;
 state.prefill = null;
 if (fill) {
  if (fill.gateway && m.gateways.some(g => String(g.n) === fill.gateway)) ctx.values.gateway = fill.gateway;
  if (fill.valve != null) { ctx.values.valve = fill.valve; ctx.values.name = fill.name; }
 }
 return kit.h('div', {class: 'card form'}, kit.h('div', {class: 'fields'},
  ctx.field('select', 'gateway', {label: NAMES.gateway, help: t('The gateway the valve is paired with.'),
   options: m.gateways.map(g => ({value: String(g.n), label: `${g.label || NAMES.gateway} (${g.ip})`}))}),
  ctx.field('number', 'valve', {label: t('Valve number'), step: 1, min: m.valve_range[0], max: m.valve_range[1],
   help: t('The number the gateway gave the valve, from 200 to 299.')}),
  ctx.field('text', 'name', {label: t('Name'), maxlength: 32, help: t('Optional, for example Bathroom.')})), kit.more(t(MORE['valve-add']), ctx.lang));
}

// The editable values: a sensor's name and the room it measures for (#devices/sensor/<address>); the add forms.
function values(m) {
 if (m.screen === 'shelly-add') return {ip: '', kind: 'auto', label: '', password: ''};
 if (m.screen === 'batteries') return {limit_pct: m.limit_pct};
 if (m.screen === 'valve-add') {
  const g = m.gateways?.find(x => x.valves.length < m.max_valves) || m.gateways?.[0];
  let valve = m.valve_range?.[0] ?? 200;
  while (g && g.valves.includes(valve)) valve++;
  return {gateway: g ? String(g.n) : '', valve, name: ''};
 }
 if (m.screen === 'sensor' && !m.missing) return {name: m.live?.shown || m.own_name || '', measures_for: m.measures_for || ''};
 return {};
}
// What a sensor's save sends: only what you changed ("" for no room is null).
function sensorSave(v, m) {
 const was = values(m), out = {};
 if (String(v.name ?? '').trim() !== String(was.name).trim()) out.name = String(v.name ?? '').trim();
 if ((v.measures_for || '') !== was.measures_for) out.measures_for = v.measures_for || null;
 return out;
}

const STYLE = `.dv{display:grid;gap:var(--ot-s3)}.dv>*{margin:0}.page:has(.dv-head)>.head{display:none}.dv-head{margin-bottom:var(--ot-s1)}
.dv .notice,.dv .inline-error{margin:0}.dv-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:44px}.dv-toolbar.end{justify-content:flex-end}
.dv-actions{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.dv-remove{margin-top:var(--ot-s4);display:flex}
.dv-row .row-text{gap:4px}.dv-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:2px}
.dv-value{flex:none;font-size:var(--ot-text-l);font-variant-numeric:tabular-nums;white-space:nowrap}
.dv-row.static{cursor:default}.dv-row.static:hover .row-label{color:inherit}button.dv-row:disabled{cursor:default;opacity:1}
button.dv-row:disabled .row-label{color:var(--ot-muted)}button.dv-row:disabled:hover .row-label{color:var(--ot-muted)}
.dv-row .btn.icon{flex:none;margin:-8px -8px -8px 0}
.dv-inner{margin:0 calc(-1 * var(--ot-s4))}.ot-card>.dv-inner{border-left:0;border-right:0;border-radius:0}
.ot-card>.dv-actions,.ot-card>.dv-status,.ot-card>.help,.ot-card>.inline-error,.ot-card>[data-status],.ot-card>.dv-done,.ot-card>.ot-skeleton{margin-top:var(--ot-s3)}
.ot-card>.dv-inner+.dv-actions{margin-top:var(--ot-s2)}.dv-none{padding:var(--ot-s3) var(--ot-s4)}
.dv-readings{display:flex;flex-wrap:wrap;align-items:flex-end;gap:var(--ot-s5)}.dv-sensor{display:grid;gap:var(--ot-s2)}
.dv-search{display:grid;gap:var(--ot-s3)}.dv-search>:not(.dv-inner){margin:0!important}.dv-lead{margin-bottom:calc(-1 * var(--ot-s1))!important}
.card.form>.ot-more-wrap{padding:0 0 var(--ot-s3)}
.dv-facts{display:flex;align-items:center;gap:var(--ot-s3);flex-wrap:wrap}.dv-fact{display:grid;gap:2px;flex:1 1 auto;min-width:0}
.dv-ip{font-variant-numeric:tabular-nums;overflow-wrap:anywhere}.dv-why{padding:0 var(--ot-s1)}
.dv-auto{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:calc(-1 * var(--ot-s2))}
.ot-value[data-tone=attention] .ot-value-figure{color:var(--ot-attention-ink)}
@media(max-width:420px){.dv-inner{margin:0 calc(-1 * var(--ot-s3))}.dv-none{padding:var(--ot-s3)}.dv-value{font-size:var(--ot-text-m)}}`;

// The title of a screen while its model loads (its own head replaces it then).
const LOADING = {bluetooth: 'Bluetooth sensors', pair: 'Pair a sensor', shelly: 'Shelly devices', bus: 'On the boiler bus', sensor: 'Bluetooth sensors',
 device: 'Shelly devices', batteries: 'Batteries'};

(window.OpenThermostatSettingsSections ||= []).push(['devices', {
 title: (model, item) => TITLES[item] || (item && SCREEN.test(item) ? LOADING[item.split('/')[0]] : null) || 'Devices',
 subtitle: (model, item) => SUBTITLES[item] || null,
 texts: TEXTS,
 errors: ERRORS,
 cards: true,
 values,
 // The screen above: a block's list, the search above its form; the add forms go back to the screen they came from.
 parent: item => {
  if (item === 'valve-add' && state.valveFrom) return {route: routeTo('device/' + state.valveFrom.id), label: state.valveFrom.name};
  if (item === 'shelly-add' || item === 'valve-add') return {route: routeTo('shelly'), label: 'Shelly devices'};
  const up = SCREEN.test(item) ? parentOf(item) : 'list';
  return {route: routeTo(up), label: up === 'list' ? 'Devices' : up === 'pair' ? 'Devices found' : SCREENS[up][0]};
 },
 // A sensor's screen: only what you changed; the add forms as they are; the blocks have nothing to save.
 toSave: (v, m) => {
  if (m.screen === 'valve-add') state.valveGateway = v.gateway;
  return m.screen === 'sensor' ? sensorSave(v, m) : m.screen ? v : {};
 },
 // A new name on the E32 restarts it once: asked first (Configure's words).
 confirm: (v, m, ctx) => (m.screen === 'sensor' && sensorSave(v, m).name !== undefined ? restartQuestion(ctx) : null),
 // After adding: the list the device or valve went into, with what was added; after forgetting or removing: the list.
 saved: (model, item) => {
  const done = model.live?.saved;
  if (item === 'shelly-add' && done?.done === 'added') {
   const name = done.name || NAMES[done.kind] || '';
   state.flash = {kind: 'shelly', done: 'added', make: t => t('{name} added.', {name})};
   return routeTo('shelly');
  }
  if (item === 'valve-add' && done?.done === 'valve_added') {
   const g = (model.gateways || []).find(x => String(x.n) === String(state.valveGateway));
   const found = g && state.gateway?.id === g.id ? state.gateway.result?.valves?.find(v => v.id === done.valve) : null;
   if (found) found.known = true;
   state.flash = {kind: 'valve', done: 'valve_added', make: t => t('{name} added.', {name: t('Valve {id}', {id: done.valve}) + (done.name ? ` · ${done.name}` : '')})};
   return g ? routeTo('device/' + g.id) : routeTo('shelly');
  }
  if (model.screen === 'sensor' && model.missing && DONE[done?.done]) {
   state.flash = {kind: 'ble', done: done.done, make: t => t(DONE[done.done])};
   return routeTo('bluetooth');
  }
  if (model.screen === 'device' && !model.device && done?.done === 'removed') {
   const name = done.name || NAMES[done.kind] || '';
   state.flash = {kind: 'shelly', done: 'removed', make: t => t('{name} removed.', {name})};
   return routeTo('shelly');
  }
  return null;
 },
 live: (root, hass) => { for (const el of root.querySelectorAll('.page-col .dv [data-live]')) el._live?.(hass); },
 render: ctx => {
  const {kit} = ctx, el = kit.h('div', {class: 'dv'});
  state.ctx = ctx; state.root = el; state.item = ctx.item;
  if (ctx.item === 'shelly-add' || ctx.item === 'valve-add') {
   moveTo(ctx.item);
   el.dataset.screen = ctx.item;
   el.append(ctx.item === 'shelly-add' ? addDevice(ctx) : addValve(ctx), kit.h('style', {text: STYLE + BATTERY_STYLE}));
   return el;
  }
  const moved = moveTo(screenOf(ctx.item));
  // What was just added, paired or forgotten belongs to the model read after it.
  const f = state.flash;
  if (f && !f.model) { f.model = ctx.model; if (f.make) f.text = f.make(ctx.t); }
  el.append(...drawScreen(ctx).filter(Boolean), kit.h('style', {text: STYLE + BATTERY_STYLE}));
  el.dataset.screen = state.screen.split('/')[0];
  if (moved) focusTitle(el);
  return el;
 }
}]);
