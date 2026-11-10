/* The settings panel's section Installation (1.4.1, HA-INSTELPANEEL-FASE2.nl.md 3.7): on #installation Dashboard and name,
   the E32's own settings as rows (E32 system log, E32 time zone, Tester program, and the status of the room setup while
   old rooms are left), each opening its screen (#installation/logging, /time-zone, /tester, /status), and under the
   heading Maintenance: restoring a backup on this E32 (a backup Home Assistant keeps, or a file with its passphrase),
   tidying entity IDs and undoing it, and removing the old Home Assistant rooms. Backend settings_installation.py
   (CONTRACT-1.4.1 §3: the model, the save of Dashboard and name, the nine actions); every question and sentence is
   Configure's own (the same steps), word for word in English and Dutch. The 1.4 routes #general and
   #advanced/<item> lead here (the core's MOVED, 1.4.2). Texts: TEXTS, English key (test/ha-settings-texts.test.cjs);
   WORDS and ERRORS hold what the screens say. */
const TEXTS = {
 nl: {
  'Restore settings to this E32': 'Instellingen terugzetten op deze E32',
  'Home Assistant backs up the settings of your E32 every day and keeps {count} backup(s): the newest of each of the last 7 days, and the one made right before the last restore. A backup holds the network and time settings, MQTT and the Home Assistant link, the rooms with their week programs, the Bluetooth sensors, the water temperature settings and the boiler model, with the MQTT password and Bluetooth keys encrypted. The Wi-Fi password and the E32 password are never in it.': 'Home Assistant maakt elke dag een back-up van de instellingen van je E32 en bewaart er {count}: de nieuwste van elk van de laatste 7 dagen, en de back-up van vlak voor de laatste keer terugzetten. Een back-up bevat de netwerk- en tijdinstellingen, MQTT en de koppeling met Home Assistant, de ruimtes met hun weekprogramma\'s, de Bluetooth-sensoren, de instellingen van de watertemperatuur en het ketelmodel, met het MQTT-wachtwoord en de Bluetooth-sleutels versleuteld. Het wifi-wachtwoord en het E32-wachtwoord zitten er nooit in.',
  'Choose the backup to put back. The E32 checks it first and shows what changes; nothing changes before you confirm.': 'Kies de back-up die je wilt terugzetten. De E32 controleert hem eerst en laat zien wat er verandert; er verandert niets voordat je bevestigt.',
  'Replacing a broken E32: flash the firmware over USB, connect the new E32 to your network (Wi-Fi setup or Ethernet), then enter its address and password here.': 'Een kapotte E32 vervangen: zet de firmware er via USB op, verbind de nieuwe E32 met je netwerk (wifi-installatie of ethernet) en vul hier zijn adres en wachtwoord in.',
  'Backup': 'Back-up',
  'When the backup was made. Daily backups are made by Home Assistant; manual ones with the Back up E32 settings now button.': 'Wanneer de back-up is gemaakt. Dagelijkse back-ups maakt Home Assistant zelf; handmatige met de knop Nu een back-up van de E32 maken.',
  'E32 web address': 'Webadres van de E32',
  'The address of the E32 to restore, for example http://192.168.1.50. Keep it for this E32; enter the new address for a replacement E32.': 'Het adres van de E32 die je terugzet, bijvoorbeeld http://192.168.1.50. Laat het staan voor deze E32; vul voor een vervangende E32 het nieuwe adres in.',
  'E32 password': 'Wachtwoord van de E32',
  'The password you sign in with on that E32\'s web page (user admin). Leave empty to use the saved one; needed when the address is another one.': 'Het wachtwoord waarmee je inlogt op de webpagina van die E32 (gebruiker admin). Laat leeg om het opgeslagen wachtwoord te gebruiken; nodig als het adres een ander is.',
  'The E32 checks the backup and compares it with its own settings. This takes a few seconds; nothing is changed yet.': 'De E32 controleert de back-up en vergelijkt hem met zijn eigen instellingen. Dit duurt een paar seconden; er verandert nog niets.',
  'Restore these settings?': 'Deze instellingen terugzetten?',
  'Backup of {created}, as the E32 checked it:': 'Back-up van {created}, zoals de E32 hem heeft gecontroleerd:',
  'The rooms keep the mode of the backup. The takeover of the boiler is not part of a backup: a new or reset E32 sends nothing to the boiler until you confirm the takeover on its page (Rooms → Active control). Before the restore Home Assistant also saves a backup of the E32 as it is now.': 'De ruimtes houden de modus uit de back-up. De overname van de ketel zit niet in een back-up: een nieuwe of gewiste E32 stuurt niets naar de ketel tot je de overname bevestigt op zijn pagina (Ruimtes → Actieve regeling). Vóór het terugzetten bewaart Home Assistant ook een back-up van de E32 zoals hij nu is.',
  'Restore these settings on this E32': 'Deze instellingen op deze E32 terugzetten',
  'Use this E32 from now on?': 'Deze E32 voortaan gebruiken?',
  'Use this E32 from now on': 'Deze E32 voortaan gebruiken',
  'Home Assistant backs up the E32 as it is now and restores the chosen backup. When the network or Bluetooth settings change, the E32 restarts and Home Assistant waits until it answers again; this can take up to three minutes.': 'Home Assistant maakt een back-up van de E32 zoals hij nu is en zet de gekozen back-up terug. Veranderen de netwerk- of Bluetooth-instellingen, dan start de E32 opnieuw op en wacht Home Assistant tot hij weer antwoordt; dat kan tot drie minuten duren.',
  'Tidy entity IDs': 'ID\'s van entiteiten opruimen',
  'Optional. The new IDs are the ones Home Assistant itself would give these entities today. History and statistics move along with them. {count} entities can get a shorter ID; {used} of them are used in your automations, scripts or dashboards.': 'Optioneel. De nieuwe ID\'s zijn de ID\'s die Home Assistant deze entiteiten vandaag zelf zou geven. Historie en statistieken verhuizen mee. {count} entiteiten kunnen een kortere ID krijgen; {used} daarvan worden gebruikt in je automatiseringen, scripts of dashboards.',
  'Warning: an automation, script or dashboard that uses an old ID stops working until you change it. OpenThermostat\'s own dashboard follows by itself. You can undo this for {days} days. Other places, such as templates in YAML and other integrations, are not searched.': 'Let op: een automatisering, script of dashboard met een oude ID werkt niet meer tot je die aanpast. Het eigen dashboard van OpenThermostat past zich vanzelf aan. Je kunt dit {days} dagen terugzetten. Andere plekken, zoals templates in YAML en andere integraties, worden niet doorzocht.',
  'Which entities': 'Welke entiteiten',
  'The unused ones are the safe choice: nothing refers to them. All also renames the used ones listed above; update those places yourself afterwards.': 'De ongebruikte zijn de veilige keuze: niets verwijst ernaar. Alle hernoemt ook de gebruikte uit de lijst hierboven; pas die plekken daarna zelf aan.',
  'Only entities that are not used anywhere': 'Alleen entiteiten die nergens gebruikt worden',
  'All, I will update the places where they are used': 'Alle, ik pas de plekken waar ze gebruikt worden zelf aan',
  'I have read the list and want to rename these entities': 'Ik heb de lijst gelezen en wil deze entiteiten hernoemen',
  'Undo the entity ID tidy': 'Opruimen van ID\'s van entiteiten terugzetten',
  '{count} entities get their previous ID back (where it is still free). History moves along with them.': '{count} entiteiten krijgen hun vorige ID terug (waar die nog vrij is). Historie verhuist mee.',
  'Put the old IDs back': 'Zet de oude ID\'s terug',
  'Remove old Home Assistant rooms': 'Oude Home Assistant-ruimtes verwijderen',
  'These older Home Assistant rooms were only needed to connect the E32 and are no longer used: {rooms}.': 'Deze oudere Home Assistant-ruimtes waren alleen nodig om de E32 te koppelen en worden niet meer gebruikt: {rooms}.',
  'What happens:': 'Wat er gebeurt:',
  'Removing them deletes their room devices and entities from this integration. Your sensors, thermostats and radiator valves of other integrations stay as they are. The E32 stays connected; it may restart once (about 30 seconds).': 'Bij verwijderen verdwijnen hun ruimteapparaten en entiteiten van deze integratie. Je sensoren, thermostaten en radiatorkranen van andere integraties blijven zoals ze zijn. De E32 blijft verbonden; hij kan eenmaal herstarten (ongeveer 30 seconden).',
  'Finish removing the old room': 'Verwijderen van de oude ruimte afronden',
  'An older Home Assistant room was removed, but the E32 still has its old connection settings. Submit to connect the E32 again without it. The rooms on the E32 stay as they are; the E32 may restart once (about 30 seconds).': 'Een oudere Home Assistant-ruimte is verwijderd, maar de E32 heeft nog de oude verbindingsinstellingen. Bevestig om de E32 opnieuw zonder die ruimte te koppelen. De ruimtes op de E32 blijven zoals ze zijn; de E32 kan eenmaal herstarten (ongeveer 30 seconden).',
  'Removing the old rooms and reconnecting the E32. This can take up to two minutes.': 'De oude ruimtes worden verwijderd en de E32 wordt opnieuw gekoppeld. Dit kan tot twee minuten duren.',
  'Dashboard and name': 'Dashboard en naam',
  'Installation name': 'Naam installatie',
  'Show the OpenThermostat dashboard': 'OpenThermostat-dashboard tonen',
  'The OpenThermostat dashboard: your rooms at a glance, the week planner and the boiler. Your own dashboards are preserved.': 'Het OpenThermostat-dashboard: je ruimtes in één oogopslag, de weekplanner en de ketel. Je bestaande dashboards blijven behouden.',
  daily: 'dagelijks',
  manual: 'handmatig',
  'before a restore': 'vóór terugzetten',
  'with passwords and keys': 'met wachtwoorden en sleutels',
  'A recognisable name in Home Assistant. Your devices and their history stay as they are.': 'Een herkenbare naam in Home Assistant. Je apparaten en hun geschiedenis blijven zoals ze zijn.',
  'Hide the OpenThermostat dashboard?': 'OpenThermostat-dashboard verbergen?',
  'This tab goes with it. You can show the dashboard again in Configure → Dashboard and name.': 'Dit tabblad verdwijnt dan ook. Je kunt het dashboard weer tonen via Configureren → Dashboard en naam.',
  'Hide the dashboard': 'Dashboard verbergen',
  'Only an administrator of Home Assistant can change this.': 'Alleen een beheerder van Home Assistant kan dit wijzigen.',
  'Undo': 'Ongedaan maken',
  'On': 'Aan',
  'Off': 'Uit',
  'Installation': 'Installatie',
  'Maintenance': 'Onderhoud',
  'Backup file': 'Back-upbestand',
  'Passphrase of this backup': 'Wachtzin van deze back-up',
  'Leave empty to restore without passwords and keys.': 'Laat leeg om zonder wachtwoorden en sleutels terug te zetten.',
  'Check backup': 'Back-up controleren',
  'No backup yet': 'Nog geen back-up',
  '1 old Home Assistant room': '1 oude Home Assistant-ruimte',
  '{n} old Home Assistant rooms': '{n} oude Home Assistant-ruimtes',
  'Choose a file…': 'Bestand kiezen…',
  'A backup file you saved on the E32 page.': 'Een back-upbestand dat je op de E32-pagina hebt bewaard.',
  'Another E32 (replacing a broken one)': 'Een andere E32 (een kapotte vervangen)',
  'Restore': 'Terugzetten',
  'Restore these settings and use this E32 from now on?': 'Deze instellingen terugzetten en voortaan deze E32 gebruiken?',
  'This is not the E32 this installation uses now: the settings of the backup go onto it, and Home Assistant uses it from now on.': 'Dit is niet de E32 die deze installatie nu gebruikt: de instellingen van de back-up komen erop, en Home Assistant gebruikt voortaan deze E32.',
  'Restore and use this E32': 'Terugzetten en deze E32 gebruiken',
  'This E32 already has the settings of the backup of {created}: there is nothing to restore. Home Assistant still uses the previous E32 for this installation.': 'Deze E32 heeft de instellingen van de back-up van {created} al: er is niets terug te zetten. Home Assistant gebruikt voor deze installatie nog de vorige E32.',
  'Choose another backup': 'Een andere back-up kiezen',
  'Close': 'Sluiten',
  'Last backup: {moment}': 'Laatste back-up: {moment}',
  '{n} kept': '{n} bewaard',
  'Optional': 'Optioneel',
  'Undo possible for {n} IDs': 'Terugzetten kan voor {n} ID\'s',
  'and {n} more': 'en nog {n}',
  'Used in: {places}': 'Gebruikt in: {places}',
  'Tidy': 'Opruimen',
  'Rename {count} entities?': '{count} entiteiten hernoemen?',
  'Remove the old Home Assistant rooms?': 'De oude Home Assistant-ruimtes verwijderen?',
  'Read the list again': 'Lijst opnieuw lezen',
  'Sends to {server}': 'Stuurt naar {server}',
  'In use for this restore: {address}': 'Gebruikt voor dit terugzetten: {address}',
  'The E32 refuses a restore while it controls the boiler or a boiler test or boiler settings write is running. Hand back control on the E32 page (Rooms → Active control) or wait until the test has finished, then try again.': 'De E32 weigert terug te zetten zolang hij de ketel regelt of er een keteltest of ketelinstelling loopt. Geef de regeling terug op de E32-pagina (Ruimtes → Actieve regeling) of wacht tot de test klaar is, en probeer het opnieuw.',
  'The E32 is busy (a firmware update, or it is short of memory). Wait a minute and try again.': 'De E32 is bezig (een firmware-update, of hij heeft te weinig geheugen). Wacht een minuut en probeer het opnieuw.',
  'The settings on the E32 changed after the check. Choose the backup again so that the E32 checks it once more.': 'De instellingen op de E32 zijn na de controle veranderd. Kies de back-up opnieuw, zodat de E32 hem nog een keer controleert.',
  'The E32 could not open the passwords and keys in this backup. Choose another backup.': 'De E32 kon de wachtwoorden en sleutels in deze back-up niet openen. Kies een andere back-up.',
  'This backup was made by newer E32 firmware. Update this E32 first (the Firmware update entity, or System → Firmware update on its page), then restore.': 'Deze back-up is gemaakt met nieuwere E32-firmware. Werk deze E32 eerst bij (Instellingen → Updates, of Systeem → Firmware-update op zijn pagina) en zet daarna terug.',
  'The E32 could not save the restored settings and kept its previous settings. Try again; if it keeps failing, restart the E32.': 'De E32 kon de teruggezette instellingen niet opslaan en heeft zijn vorige instellingen gehouden. Probeer het opnieuw; lukt het steeds niet, start de E32 dan opnieuw op.',
  'Saving failed on the E32 and not every previous setting could be put back. Check the settings pages of the E32, or restore again.': 'Opslaan is mislukt op de E32 en niet alle vorige instellingen konden worden teruggezet. Controleer de instellingenpagina\'s van de E32, of zet opnieuw terug.',
  'The E32 refused this backup: it does not fit this E32 or its firmware. Choose another backup.': 'De E32 weigert deze back-up: hij past niet bij deze E32 of zijn firmware. Kies een andere back-up.',
  'The restore could not be completed. Check that the E32 is on and its web page opens, then try again.': 'Het terugzetten kon niet worden afgerond. Controleer of de E32 aan staat en zijn webpagina opent, en probeer het opnieuw.',
  'This E32 belongs to another OpenThermostat installation in Home Assistant, so nothing was restored. Enter the address of this installation\'s E32, or remove the other installation first.': 'Deze E32 hoort bij een andere OpenThermostat-installatie in Home Assistant, dus er is niets teruggezet. Vul het adres in van de E32 van deze installatie, of verwijder eerst de andere installatie.',
  'Tick the box to use this E32 from now on.': 'Vink het vakje aan om deze E32 voortaan te gebruiken.',
  'Home Assistant could not switch to this E32. Try again, or connect it under Configure → E32 connection.': 'Home Assistant kon deze E32 niet in gebruik nemen. Probeer het opnieuw, of verbind hem onder Configureren → E32-verbinding.',
  'The E32 did not answer after the restore, so it is not known whether the settings arrived. Check that the E32 is on and its web page opens, then choose the backup again: the E32 checks what is still different.': 'De E32 antwoordde niet na het terugzetten, dus het is niet bekend of de instellingen zijn aangekomen. Controleer of de E32 aan staat en zijn webpagina opent, en kies de back-up daarna opnieuw: de E32 controleert wat nog anders is.',
  'The E32 did not confirm the restore, and its check shows that not all settings arrived. Choose the backup again to restore it once more.': 'De E32 bevestigde het terugzetten niet, en zijn controle laat zien dat niet alle instellingen zijn aangekomen. Kies de back-up opnieuw om hem nog een keer terug te zetten.',
  'Enter the local E32 web address: a local IP address or a home-network name, for example http://192.168.1.50, http://e32.local or http://e32.fritz.box. Paths and login details do not belong in the address.': 'Vul het lokale webadres van de E32 in: een lokaal IP-adres of een naam in je thuisnetwerk, bijvoorbeeld http://192.168.1.50, http://e32.local of http://e32.fritz.box. Zet geen pad of inloggegevens in het adres.',
  'Enter the E32 administrator password. A saved password can only be reused for the same address.': 'Vul het beheerderswachtwoord van de E32 in. Een bewaard wachtwoord wordt alleen voor hetzelfde adres hergebruikt.',
  'The E32 did not accept this password. Use the password of the E32 web page (user admin).': 'De E32 accepteert dit wachtwoord niet. Gebruik het wachtwoord van de webpagina van de E32 (gebruiker admin).',
  'The E32 could not be reached. Check its address and network connection.': 'De E32 is niet bereikbaar. Controleer het adres en de netwerkverbinding.',
  'The firmware on this E32 is too old for this version of the integration. Update the E32 first: on its web page open System → Firmware update and install the latest release, then connect again.': 'De firmware op deze E32 is te oud voor deze versie van de integratie. Werk de E32 eerst bij: open op zijn webpagina Systeem → Firmware bijwerken en installeer de nieuwste release; verbind daarna opnieuw.',
  'The E32 has too many open sign-ins. Sign out on the E32 web page (or sign in there with “End previous web sessions and sign in”) or restart the E32, then try again.': 'De E32 heeft te veel open aanmeldingen. Meld je af op de webpagina van de E32 (of meld je daar aan met “Eerdere websessies beëindigen en aanmelden”) of herstart de E32, en probeer het daarna opnieuw.',
  'Too many sign-in attempts on the E32. Wait 30 seconds, then try again.': 'Te veel aanmeldpogingen op de E32. Wacht 30 seconden en probeer het daarna opnieuw.',
  'The E32 returned an unexpected response. Check its firmware and connection.': 'De E32 geeft een onverwacht antwoord. Controleer de firmware en verbinding.',
  'The E32 room plan changed since this list was made (on the E32 page or elsewhere). Nothing has been removed. Check the updated list and submit again.': 'Het ruimteplan van de E32 is veranderd sinds dit overzicht gemaakt is (op de E32-pagina of elders). Er is niets verwijderd. Bekijk het bijgewerkte overzicht en verstuur opnieuw.',
  'The E32 did not save the updated room plan, so nothing has been removed. Check that the E32 is ready and try again.': 'De E32 heeft het bijgewerkte ruimteplan niet opgeslagen, dus er is niets verwijderd. Controleer of de E32 klaar is en probeer het opnieuw.',
  'The E32 room plan could not be read, so nothing has been removed. Check that the E32 is on and connected, then try again.': 'Het ruimteplan van de E32 kon niet gelezen worden, dus er is niets verwijderd. Controleer of de E32 aan staat en verbonden is en probeer het opnieuw.',
  'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again. Nothing has been changed.': 'Hiervoor is nieuwere E32-firmware nodig. Werk de E32 eerst bij (Instellingen → Updates → OpenThermostat E32 Firmware) en probeer het opnieuw. Er is niets gewijzigd.',
  'Connecting stopped halfway: some settings may already be saved on the E32. Submit again to finish the connection; Home Assistant checks what is already there.': 'Het verbinden stopte halverwege: een deel van de instellingen kan al op de E32 staan. Verstuur opnieuw om de verbinding af te maken; Home Assistant controleert wat er al staat.',
  'The connection could not be completed. Check that the E32 is on and its web page opens, wait a minute and submit again. If it keeps failing, the E32 web page shows the reason under System → Diagnostics and system log.': 'De verbinding kon niet worden afgerond. Controleer of de E32 aan staat en zijn webpagina opent, wacht een minuut en verstuur opnieuw. Blijft het misgaan, dan staat de reden op de webpagina van de E32 onder Systeem → Diagnose en systeemlog.',
  'Restoring needs a connected E32. Connect it under Configure → E32 connection first.': 'Terugzetten kan alleen met een verbonden E32. Verbind hem eerst onder Configureren → E32-verbinding.',
  'Nothing to restore: this E32 already has exactly these settings.': 'Niets terug te zetten: deze E32 heeft precies deze instellingen al.',
  'The restore was cancelled; nothing was changed.': 'Het terugzetten is afgebroken; er is niets veranderd.',
  'Settings restored. The E32 restarted and answers again. The rooms keep the mode of the backup; a new or reset E32 controls the boiler only after you confirm the takeover on its Rooms page.\n\nEnter these again on the E32 page:\n{reenter}': 'Instellingen teruggezet. De E32 is opnieuw opgestart en antwoordt weer. De ruimtes houden de modus uit de back-up; een nieuwe of gewiste E32 regelt de ketel pas nadat je de overname bevestigt op zijn pagina Ruimtes.\n\nVoer dit opnieuw in op de E32-pagina:\n{reenter}',
  'Settings restored. The E32 is restarting and did not answer yet; Home Assistant reconnects by itself as soon as it is back. The rooms keep the mode of the backup; a new or reset E32 controls the boiler only after you confirm the takeover on its Rooms page.\n\nEnter these again on the E32 page:\n{reenter}': 'Instellingen teruggezet. De E32 start opnieuw op en antwoordt nog niet; Home Assistant maakt vanzelf weer verbinding zodra hij terug is. De ruimtes houden de modus uit de back-up; een nieuwe of gewiste E32 regelt de ketel pas nadat je de overname bevestigt op zijn pagina Ruimtes.\n\nVoer dit opnieuw in op de E32-pagina:\n{reenter}',
  'Settings restored. Restart the E32 (System → Restart device on its page) to use all of them. The rooms keep the mode of the backup; a new or reset E32 controls the boiler only after you confirm the takeover on its Rooms page.\n\nEnter these again on the E32 page:\n{reenter}': 'Instellingen teruggezet. Start de E32 opnieuw op (Systeem → Apparaat herstarten op zijn pagina) om ze allemaal te gebruiken. De ruimtes houden de modus uit de back-up; een nieuwe of gewiste E32 regelt de ketel pas nadat je de overname bevestigt op zijn pagina Ruimtes.\n\nVoer dit opnieuw in op de E32-pagina:\n{reenter}',
  'Settings restored. The rooms keep the mode of the backup; a new or reset E32 controls the boiler only after you confirm the takeover on its Rooms page.\n\nEnter these again on the E32 page:\n{reenter}': 'Instellingen teruggezet. De ruimtes houden de modus uit de back-up; een nieuwe of gewiste E32 regelt de ketel pas nadat je de overname bevestigt op zijn pagina Ruimtes.\n\nVoer dit opnieuw in op de E32-pagina:\n{reenter}',
  'Done: Home Assistant uses this E32 from now on. Nothing was restored; it already had these settings.': 'Klaar: Home Assistant gebruikt voortaan deze E32. Er is niets teruggezet; hij had deze instellingen al.',
  'Home Assistant has no E32 backup yet. Make one with the Back up E32 settings now button on the E32 device.': 'Home Assistant heeft nog geen back-up van de E32. Maak er een met de knop Nu een back-up van de E32 maken op het E32-apparaat.',
  'All OpenThermostat entity IDs already match what Home Assistant would give them.': 'Alle ID\'s van entiteiten van OpenThermostat zijn al zoals Home Assistant ze zou geven.',
  '{count} entity IDs renamed. Update these places yourself:\n\n{todo}': '{count} ID\'s van entiteiten hernoemd. Pas deze plekken zelf aan:\n\n{todo}',
  '{count} entity IDs are back to their old names.': '{count} ID\'s van entiteiten hebben hun oude naam terug.',
  'The old Home Assistant rooms have been removed. The E32 stays connected with {rooms} room(s) in its plan.': 'De oude Home Assistant-ruimtes zijn verwijderd. De E32 blijft verbonden met {rooms} ruimte(s) in zijn plan.',
  'There are no old Home Assistant rooms to remove.': 'Er zijn geen oude Home Assistant-ruimtes om te verwijderen.',
  'Cancelled. Choose Configure → E32 connection to check the connection; some settings may already be saved on the E32.': 'Geannuleerd. Kies Configureren → E32-verbinding om de verbinding te controleren; sommige instellingen kunnen al op de E32 zijn opgeslagen.',
  'This file is not an OpenThermostat E32 backup.': 'Dit bestand is geen back-up van een OpenThermostat E32.',
  'The file did not arrive. Choose the backup file again.': 'Het bestand is niet aangekomen. Kies het back-upbestand opnieuw.',
  'Use a passphrase of 8 to 64 characters.': 'Gebruik een wachtzin van 8 tot 64 tekens.',
  'The passphrase is not correct.': 'De wachtzin klopt niet.',
  'Check the backup again before you restore it.': 'Controleer de back-up opnieuw voordat je hem terugzet.',
  'The old rooms changed since this list was made. Nothing has been removed. Check the list again.': 'De oude ruimtes zijn veranderd sinds deze lijst gemaakt is. Er is niets verwijderd. Bekijk de lijst opnieuw.',
  'This installation still uses an older Home Assistant room profile, which belongs to the previous E32. Remove the old Home Assistant rooms first (below, under Maintenance), then restore.': 'Deze installatie gebruikt nog een ouder ruimteprofiel van Home Assistant, dat bij de vorige E32 hoort. Verwijder eerst de oude Home Assistant-ruimtes (hieronder, bij Onderhoud) en zet daarna terug.',
  'Give a name of 1 to 80 characters.': 'Geef een naam van 1 tot 80 tekens.',
  'Connect the E32 first: Configure → E32 connection.': 'Verbind eerst de E32: Configureren → E32-verbinding.',
  'Enter the IPv4 address of the syslog server, for example 192.168.1.10.': 'Vul het IPv4-adres van de syslog-server in, bijvoorbeeld 192.168.1.10.',
  'Use a whole number within the range shown.': 'Gebruik een heel getal binnen het getoonde bereik.',
  'Choose a time zone from the list.': 'Kies een tijdzone uit de lijst.',
  'The E32 has no free web session: close E32 pages you do not use, or wait two minutes, then try again.': 'De E32 heeft geen vrije websessie: sluit E32-pagina\'s die je niet gebruikt, of wacht twee minuten, en probeer het opnieuw.',
  'The E32 is updating or restarting. Try again once its web page opens normally.': 'De E32 wordt bijgewerkt of start opnieuw. Probeer het opnieuw zodra zijn webpagina normaal opent.',
  'The E32 settings were changed meanwhile (on its web page?). Nothing was saved; try again.': 'De E32-instellingen zijn intussen gewijzigd (op zijn webpagina?). Er is niets opgeslagen; probeer het opnieuw.',
  'The E32 refused these settings. Nothing was saved.': 'De E32 weigerde deze instellingen. Er is niets opgeslagen.',
  'The E32 could not confirm that the settings were saved. Check them on the E32 before trying again.': 'De E32 kon niet bevestigen dat de instellingen zijn opgeslagen. Controleer ze op de E32 voordat je het opnieuw probeert.',
  'The E32 could not be reached ({error}). Nothing was saved.': 'De E32 is niet bereikbaar ({error}). Er is niets opgeslagen.',
  'This E32 firmware does not offer this setting. Update the E32 (Firmware update) first.': 'Deze E32-firmware heeft deze instelling niet. Werk de E32 eerst bij (Firmware-update).',
  'The E32 no longer accepts the saved password. Home Assistant asks for the new one: Settings → Devices & services → OpenThermostat → Re-authenticate.': 'De E32 accepteert het bewaarde wachtwoord niet meer. Home Assistant vraagt om het nieuwe: Instellingen → Apparaten en diensten → OpenThermostat → Opnieuw verifiëren.',
  'The E32 still uses its default password and accepts no changes until you choose a new one: Settings → Repairs → “E32 still uses the default password”.': 'De E32 gebruikt nog het standaardwachtwoord en accepteert geen wijzigingen tot je een nieuw kiest: Instellingen → Reparaties → “E32 gebruikt nog het standaardwachtwoord”.',
  'This E32 has no room in its memory for a bus recording. Restart the E32 and try again. You can still share the result without one.': 'Deze E32 heeft geen ruimte in zijn geheugen voor een busopname. Herstart de E32 en probeer het opnieuw. Je kunt het resultaat ook zonder opname delen.',
  'Home Assistant could not write the files to its www/open_thermostat folder. Check that the configuration folder has free space, then try again.': 'Home Assistant kon de bestanden niet in zijn map www/open_thermostat schrijven. Controleer of er ruimte vrij is in de configuratiemap en probeer het opnieuw.',
  'E32 system log': 'Systeemlog van de E32',
  'E32 time zone': 'Tijdzone van de E32',
  'Tester program': 'Testerprogramma',
  'Status of the room setup': 'Status van de ruimte-instellingen',
  'Send the E32\'s log to a syslog server on your network, for example to look into a problem.': 'Stuur het log van de E32 naar een syslog-server in je netwerk, bijvoorbeeld om een probleem uit te zoeken.',
  'The E32 keeps its own log as well (Diagnostics and system log on its web page).': 'De E32 houdt ook zelf een log bij (Diagnose en systeemlog op zijn webpagina).',
  'The E32 runs the week programs in its own time zone.': 'De E32 voert de weekprogramma\'s uit in zijn eigen tijdzone.',
  'Help test OpenThermostat with your boiler.': 'Help OpenThermostat testen met je ketel.',
  'The checks of the old Home Assistant rooms, read only.': 'De controles van de oude Home Assistant-ruimtes, alleen lezen.',
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
  'Error': 'Fout',
  'Warning': 'Waarschuwing',
  'Info': 'Informatie',
  'Debug': 'Foutzoeken',
  'Trace': 'Alles (trace)',
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
  'There is nothing to check.': 'Er is niets te controleren.'
 }};
// What the screens say, by id (Configure's own words where Configure says the same thing; HA-INSTELPANEEL-FASE2.nl.md 3.7).
const WORDS = {
 restore: 'Restore settings to this E32',
 restore_kept: 'Home Assistant backs up the settings of your E32 every day and keeps {count} backup(s): the newest of each of the last 7 days, and the one made right before the last restore. A backup holds the network and time settings, MQTT and the Home Assistant link, the rooms with their week programs, the Bluetooth sensors, the water temperature settings and the boiler model, with the MQTT password and Bluetooth keys encrypted. The Wi-Fi password and the E32 password are never in it.',
 restore_choose: 'Choose the backup to put back. The E32 checks it first and shows what changes; nothing changes before you confirm.',
 restore_replace: 'Replacing a broken E32: flash the firmware over USB, connect the new E32 to your network (Wi-Fi setup or Ethernet), then enter its address and password here.',
 backup: 'Backup',
 backup_help: 'When the backup was made. Daily backups are made by Home Assistant; manual ones with the Back up E32 settings now button.',
 address: 'E32 web address',
 address_help: 'The address of the E32 to restore, for example http://192.168.1.50. Keep it for this E32; enter the new address for a replacement E32.',
 password: 'E32 password',
 password_help: 'The password you sign in with on that E32\'s web page (user admin). Leave empty to use the saved one; needed when the address is another one.',
 checking: 'The E32 checks the backup and compares it with its own settings. This takes a few seconds; nothing is changed yet.',
 confirm_title: 'Restore these settings?',
 confirm_of: 'Backup of {created}, as the E32 checked it:',
 confirm_rest: 'The rooms keep the mode of the backup. The takeover of the boiler is not part of a backup: a new or reset E32 sends nothing to the boiler until you confirm the takeover on its page (Rooms → Active control). Before the restore Home Assistant also saves a backup of the E32 as it is now.',
 confirm_button: 'Restore these settings on this E32',
 adopt_title: 'Use this E32 from now on?',
 adopt_button: 'Use this E32 from now on',
 applying: 'Home Assistant backs up the E32 as it is now and restores the chosen backup. When the network or Bluetooth settings change, the E32 restarts and Home Assistant waits until it answers again; this can take up to three minutes.',
 tidy: 'Tidy entity IDs',
 tidy_text: 'Optional. The new IDs are the ones Home Assistant itself would give these entities today. History and statistics move along with them. {count} entities can get a shorter ID; {used} of them are used in your automations, scripts or dashboards.',
 tidy_warning: 'Warning: an automation, script or dashboard that uses an old ID stops working until you change it. OpenThermostat\'s own dashboard follows by itself. You can undo this for {days} days. Other places, such as templates in YAML and other integrations, are not searched.',
 scope: 'Which entities',
 scope_help: 'The unused ones are the safe choice: nothing refers to them. All also renames the used ones listed above; update those places yourself afterwards.',
 scope_unused: 'Only entities that are not used anywhere',
 scope_all: 'All, I will update the places where they are used',
 tidy_confirm: 'I have read the list and want to rename these entities',
 undo: 'Undo the entity ID tidy',
 undo_text: '{count} entities get their previous ID back (where it is still free). History moves along with them.',
 undo_confirm: 'Put the old IDs back',
 legacy: 'Remove old Home Assistant rooms',
 legacy_text: 'These older Home Assistant rooms were only needed to connect the E32 and are no longer used: {rooms}.',
 what_happens: 'What happens:',
 legacy_remove_text: 'Removing them deletes their room devices and entities from this integration. Your sensors, thermostats and radiator valves of other integrations stay as they are. The E32 stays connected; it may restart once (about 30 seconds).',
 finish: 'Finish removing the old room',
 finish_text: 'An older Home Assistant room was removed, but the E32 still has its old connection settings. Submit to connect the E32 again without it. The rooms on the E32 stay as they are; the E32 may restart once (about 30 seconds).',
 removing: 'Removing the old rooms and reconnecting the E32. This can take up to two minutes.',
 dashboard_and_name: 'Dashboard and name',
 name: 'Installation name',
 dashboard: 'Show the OpenThermostat dashboard',
 dashboard_help: 'The OpenThermostat dashboard: your rooms at a glance, the week planner and the boiler. Your own dashboards are preserved.',
 kind_daily: 'daily',
 kind_manual: 'manual',
 kind_pre_restore: 'before a restore',
 kind_secrets: 'with passwords and keys',
 name_help: 'A recognisable name in Home Assistant. Your devices and their history stay as they are.',
 hide_title: 'Hide the OpenThermostat dashboard?',
 hide_text: 'This tab goes with it. You can show the dashboard again in Configure → Dashboard and name.',
 hide_button: 'Hide the dashboard',
 admin_only: 'Only an administrator of Home Assistant can change this.',
 undo_button: 'Undo',
 off: 'Off',
 installation: 'Installation',
 maintenance: 'Maintenance',
 backup_file: 'Backup file',
 passphrase: 'Passphrase of this backup',
 passphrase_help: 'Leave empty to restore without passwords and keys.',
 check: 'Check backup',
 no_backup: 'No backup yet',
 room_one: '1 old Home Assistant room',
 rooms_n: '{n} old Home Assistant rooms',
 choose_file: 'Choose a file…',
 file_help: 'A backup file you saved on the E32 page.',
 other_e32: 'Another E32 (replacing a broken one)',
 restore_button: 'Restore',
 both_title: 'Restore these settings and use this E32 from now on?',
 both_text: 'This is not the E32 this installation uses now: the settings of the backup go onto it, and Home Assistant uses it from now on.',
 both_button: 'Restore and use this E32',
 adopt_text: 'This E32 already has the settings of the backup of {created}: there is nothing to restore. Home Assistant still uses the previous E32 for this installation.',
 another: 'Choose another backup',
 close: 'Close',
 last_backup: 'Last backup: {moment}',
 kept_n: '{n} kept',
 optional: 'Optional',
 undo_n: 'Undo possible for {n} IDs',
 more_n: 'and {n} more',
 used_in: 'Used in: {places}',
 tidy_button: 'Tidy',
 rename_title: 'Rename {count} entities?',
 legacy_question: 'Remove the old Home Assistant rooms?',
 read_again: 'Read the list again',
 sends_to: 'Sends to {server}',
 other_e32_text: 'In use for this restore: {address}'
};
// The sentence of each code and closing state (Configure's options.error / options.abort, word for word).
const ERRORS = {
 e32_restore_boiler_owned: 'The E32 refuses a restore while it controls the boiler or a boiler test or boiler settings write is running. Hand back control on the E32 page (Rooms → Active control) or wait until the test has finished, then try again.',
 e32_restore_busy: 'The E32 is busy (a firmware update, or it is short of memory). Wait a minute and try again.',
 e32_restore_settings_changed: 'The settings on the E32 changed after the check. Choose the backup again so that the E32 checks it once more.',
 e32_restore_wrong_passphrase: 'The E32 could not open the passwords and keys in this backup. Choose another backup.',
 e32_restore_newer_backup: 'This backup was made by newer E32 firmware. Update this E32 first (the Firmware update entity, or System → Firmware update on its page), then restore.',
 e32_restore_save_failed: 'The E32 could not save the restored settings and kept its previous settings. Try again; if it keeps failing, restart the E32.',
 e32_restore_save_partial: 'Saving failed on the E32 and not every previous setting could be put back. Check the settings pages of the E32, or restore again.',
 e32_restore_invalid: 'The E32 refused this backup: it does not fit this E32 or its firmware. Choose another backup.',
 e32_restore_failed: 'The restore could not be completed. Check that the E32 is on and its web page opens, then try again.',
 e32_restore_other_installation: 'This E32 belongs to another OpenThermostat installation in Home Assistant, so nothing was restored. Enter the address of this installation\'s E32, or remove the other installation first.',
 e32_restore_adopt_confirm_required: 'Tick the box to use this E32 from now on.',
 e32_restore_adopt_failed: 'Home Assistant could not switch to this E32. Try again, or connect it under Configure → E32 connection.',
 e32_restore_unconfirmed: 'The E32 did not answer after the restore, so it is not known whether the settings arrived. Check that the E32 is on and its web page opens, then choose the backup again: the E32 checks what is still different.',
 e32_restore_not_applied: 'The E32 did not confirm the restore, and its check shows that not all settings arrived. Choose the backup again to restore it once more.',
 controller_address_invalid: 'Enter the local E32 web address: a local IP address or a home-network name, for example http://192.168.1.50, http://e32.local or http://e32.fritz.box. Paths and login details do not belong in the address.',
 controller_password_required: 'Enter the E32 administrator password. A saved password can only be reused for the same address.',
 controller_auth_failed: 'The E32 did not accept this password. Use the password of the E32 web page (user admin).',
 controller_unreachable: 'The E32 could not be reached. Check its address and network connection.',
 controller_update_required: 'The firmware on this E32 is too old for this version of the integration. Update the E32 first: on its web page open System → Firmware update and install the latest release, then connect again.',
 controller_session_capacity: 'The E32 has too many open sign-ins. Sign out on the E32 web page (or sign in there with “End previous web sessions and sign in”) or restart the E32, then try again.',
 controller_try_again_later: 'Too many sign-in attempts on the E32. Wait 30 seconds, then try again.',
 controller_response_invalid: 'The E32 returned an unexpected response. Check its firmware and connection.',
 legacy_rooms_plan_changed: 'The E32 room plan changed since this list was made (on the E32 page or elsewhere). Nothing has been removed. Check the updated list and submit again.',
 legacy_rooms_plan_failed: 'The E32 did not save the updated room plan, so nothing has been removed. Check that the E32 is ready and try again.',
 legacy_rooms_plan_unreadable: 'The E32 room plan could not be read, so nothing has been removed. Check that the E32 is on and connected, then try again.',
 controller_room_plan_update_required: 'This needs newer E32 firmware. Update the E32 first (Settings → Updates → OpenThermostat E32 Firmware), then try again. Nothing has been changed.',
 controller_partial_connection: 'Connecting stopped halfway: some settings may already be saved on the E32. Submit again to finish the connection; Home Assistant checks what is already there.',
 controller_connection_failed: 'The connection could not be completed. Check that the E32 is on and its web page opens, wait a minute and submit again. If it keeps failing, the E32 web page shows the reason under System → Diagnostics and system log.',
 e32_restore_unavailable: 'Restoring needs a connected E32. Connect it under Configure → E32 connection first.',
 e32_restore_nothing: 'Nothing to restore: this E32 already has exactly these settings.',
 e32_restore_cancelled: 'The restore was cancelled; nothing was changed.',
 e32_restore_done_online: 'Settings restored. The E32 restarted and answers again. The rooms keep the mode of the backup; a new or reset E32 controls the boiler only after you confirm the takeover on its Rooms page.\n\nEnter these again on the E32 page:\n{reenter}',
 e32_restore_done_waiting: 'Settings restored. The E32 is restarting and did not answer yet; Home Assistant reconnects by itself as soon as it is back. The rooms keep the mode of the backup; a new or reset E32 controls the boiler only after you confirm the takeover on its Rooms page.\n\nEnter these again on the E32 page:\n{reenter}',
 e32_restore_done_restart: 'Settings restored. Restart the E32 (System → Restart device on its page) to use all of them. The rooms keep the mode of the backup; a new or reset E32 controls the boiler only after you confirm the takeover on its Rooms page.\n\nEnter these again on the E32 page:\n{reenter}',
 e32_restore_done: 'Settings restored. The rooms keep the mode of the backup; a new or reset E32 controls the boiler only after you confirm the takeover on its Rooms page.\n\nEnter these again on the E32 page:\n{reenter}',
 e32_restore_adopted: 'Done: Home Assistant uses this E32 from now on. Nothing was restored; it already had these settings.',
 e32_restore_no_backups: 'Home Assistant has no E32 backup yet. Make one with the Back up E32 settings now button on the E32 device.',
 entity_ids_nothing: 'All OpenThermostat entity IDs already match what Home Assistant would give them.',
 entity_ids_done: '{count} entity IDs renamed. Update these places yourself:\n\n{todo}',
 entity_ids_undone: '{count} entity IDs are back to their old names.',
 legacy_rooms_removed: 'The old Home Assistant rooms have been removed. The E32 stays connected with {rooms} room(s) in its plan.',
 legacy_rooms_none: 'There are no old Home Assistant rooms to remove.',
 legacy_rooms_cancelled: 'Cancelled. Choose Configure → E32 connection to check the connection; some settings may already be saved on the E32.',
 e32_restore_file_invalid: 'This file is not an OpenThermostat E32 backup.',
 e32_restore_file_missing: 'The file did not arrive. Choose the backup file again.',
 e32_restore_passphrase_invalid: 'Use a passphrase of 8 to 64 characters.',
 e32_restore_passphrase_wrong: 'The passphrase is not correct.',
 e32_restore_check_first: 'Check the backup again before you restore it.',
 legacy_rooms_changed: 'The old rooms changed since this list was made. Nothing has been removed. Check the list again.',
 e32_restore_other_e32: 'This installation still uses an older Home Assistant room profile, which belongs to the previous E32. Remove the old Home Assistant rooms first (below, under Maintenance), then restore.',
 invalid_name: 'Give a name of 1 to 80 characters.',
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
 tester_share_not_written: 'Home Assistant could not write the files to its www/open_thermostat folder. Check that the configuration folder has free space, then try again.'
};
// The screens of the E32's own settings (1.4's Advanced, Configure's words).
const TITLES = {logging: 'E32 system log', 'time-zone': 'E32 time zone', tester: 'Tester program', status: 'Status of the room setup'};
const SUBTITLES = {logging: 'Send the E32\'s log to a syslog server on your network, for example to look into a problem.',
 'time-zone': 'The E32 runs the week programs in its own time zone.', tester: 'Help test OpenThermostat with your boiler.',
 status: 'The checks of the old Home Assistant rooms, read only.'};
// The log levels (Configure's selector e32_log_level).
const LEVELS = {0: 'Off', 1: 'Error', 2: 'Warning', 3: 'Info', 4: 'Debug', 5: 'Trace'};
// The bus recording in one line (Configure's tester_text).
const RECORDING = {
 idle: 'No bus recording yet.', recording: 'Recording: {minutes} of 30 minutes, {frames} messages.',
 ready: 'A bus recording is ready: {minutes} minutes, {frames} messages.',
 unavailable: 'This E32 cannot make a bus recording (no room in its memory). You can still share the result.',
 not_supported: 'This E32 firmware cannot make a bus recording yet. Update the E32 first, or share the result without one.',
 unreachable: 'The E32 could not be reached just now.'};
// What the last tester action did (Configure's own result lines).
const DONE = {
 switched_on: 'The tester program is on.',
 tester_recording_started: 'Recording: the E32 keeps the newest {minutes} minutes of your boiler\'s messages until you stop it or choose Share result.',
 tester_recording_stopped: 'The bus recording is stopped. Choose Share result to write the files.',
 tester_shared: 'Ready: open the notification. It lists what is in the files, has the links to download them and the GitHub form. Nothing was sent.',
 tester_switched_off: 'The tester program is off. Files you already wrote stay in www/open_thermostat until you delete them.'};
// A kept backup's kind (e32_backup: daily, manual, pre_restore), and the closing states of a restore that went well.
const KINDS = {daily: 'kind_daily', manual: 'kind_manual', pre_restore: 'kind_pre_restore'};
const CLOSING = ['e32_restore_done_online', 'e32_restore_done_waiting', 'e32_restore_done_restart', 'e32_restore_done', 'e32_restore_adopted'];
// Material Design Icons (Apache-2.0), inline: the rows and parts the kit has no icon for.
const ICONS = {
 log: 'M5,3C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H5M5,5H19V19H5V5M7,7V9H17V7H7M7,11V13H17V11H7M7,15V17H14V15H7Z',
 earth: 'M17.9,17.39C17.64,16.59 16.89,16 16,16H15V13A1,1 0 0,0 14,12H8V10H10A1,1 0 0,0 11,9V7H13A2,2 0 0,0 15,5V4.59C17.93,5.77 20,8.64 20,12C20,14.08 19.2,15.97 17.9,17.39M11,19.93C7.05,19.44 4,16.08 4,12C4,11.38 4.08,10.78 4.21,10.21L9,15V16A2,2 0 0,0 11,18M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z',
 flask: 'M5,19A1,1 0 0,0 6,20H18A1,1 0 0,0 19,19C19,18.79 18.93,18.59 18.82,18.43L13,8.35V4H11V8.35L5.18,18.43C5.07,18.59 5,18.79 5,19M6,22A3,3 0 0,1 3,19C3,18.4 3.18,17.84 3.5,17.37L9,7.81V6A1,1 0 0,1 8,5V4A2,2 0 0,1 10,2H14A2,2 0 0,1 16,4V5A1,1 0 0,1 15,6V7.81L20.5,17.37C20.82,17.84 21,18.4 21,19A3,3 0 0,1 18,22H6M13,16L14.34,14.66L16.27,18H7.73L10.39,13.39L13,16Z',
 checklist: 'M19,3H14.82C14.4,1.84 13.3,1 12,1C10.7,1 9.6,1.84 9.18,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M12,3A1,1 0 0,1 13,4A1,1 0 0,1 12,5A1,1 0 0,1 11,4A1,1 0 0,1 12,3M7,7H17V5H19V19H5V5H7V7M7.5,13.5L9,12L11,14L15.5,9.5L17,11L11,17L7.5,13.5Z',
 restore: 'M12,3A9,9 0 0,0 3,12H0L4,16L8,12H5A7,7 0 0,1 12,5A7,7 0 0,1 19,12A7,7 0 0,1 12,19C10.5,19 9.09,18.5 7.94,17.7L6.5,19.14C8.04,20.3 9.94,21 12,21A9,9 0 0,0 21,12A9,9 0 0,0 12,3M14,12A2,2 0 0,0 12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12Z',
 tag: 'M21.41 11.58L12.41 2.58A2 2 0 0 0 11 2H4A2 2 0 0 0 2 4V11A2 2 0 0 0 2.59 12.42L11.59 21.42A2 2 0 0 0 13 22A2 2 0 0 0 14.41 21.41L21.41 14.41A2 2 0 0 0 22 13A2 2 0 0 0 21.41 11.58M13 20L4 11V4H11L20 13M6.5 5A1.5 1.5 0 1 1 5 6.5A1.5 1.5 0 0 1 6.5 5Z',
 bin: 'M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19M8,9H16V19H8V9M15.5,4L14.5,3H9.5L8.5,4H5V6H19V4H15.5Z',
 upload: 'M9,16V10H5L12,3L19,10H15V16H9M5,20V18H19V20H5Z'};
const POLL_MS = 2000;  // restore_progress and legacy_rooms_progress, as Configure's progress step

/* ---- small helpers (the kit is full: they live here) ---- */
const w = (ctx, id, values) => ctx.t(WORDS[id], values);
const glyph = (name, size = 24) => {
 const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
 for (const [k, v] of Object.entries({viewBox: '0 0 24 24', width: size, height: size, class: 'ot-icon', 'data-icon': name, 'aria-hidden': 'true', focusable: 'false'})) svg.setAttribute(k, v);
 const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
 path.setAttribute('d', ICONS[name]); path.setAttribute('fill', 'currentColor');
 svg.append(path);
 return svg;
};
// The icon tile of a row, card or part with one of this module's icons.
const paint = (el, name, size) => { el.querySelector('.row-icon, .ot-card-icon, .ot-fold-icon')?.replaceChildren(glyph(name, size)); return el; };
const withGlyph = (button, name) => { button.querySelector('svg')?.replaceWith(glyph(name, 20)); return button; };
const errorText = (ctx, e) => e?.text || ctx.errorText(e?.code || 'save_uncertain', e?.placeholders);
// A date and time in Home Assistant's language and clock ("Tue 10 Nov, 03:00").
const when = (ctx, iso) => ctx.kit.time.moment(ctx.hass, iso, 0) || '';
const kilobytes = size => `${Math.max(1, Math.round((Number(size) || 0) / 1024))} kB`;
const notice = (ctx, text, tone, ...more) => { const el = ctx.kit.notice(text, tone, ...more); el.classList.add('iv-pre'); return el; };
const actions = (ctx, ...buttons) => ctx.kit.h('div', {class: 'iv-actions'}, ...buttons.filter(Boolean));
const bar = ctx => ctx.kit.h('div', {class: 'iv-progress', 'aria-hidden': 'true'});

// What the maintenance parts hold between redraws of the page (a save, a wider screen): per installation.
const memos = new Map();
function memoOf(ctx) {
 if (!memos.has(ctx.entry_id)) {
  const keep = ctx.kit.memory('installation-parts');
  memos.set(ctx.entry_id, {open: keep.get() || {}, keep, redraw: {}, restore: {phase: 'choose'}, tidy: {only: true}, legacy: {}});
 }
 const m = memos.get(ctx.entry_id);
 m.action = ctx.action; m.lang = ctx.lang;
 return m;
}
// The progress of a restore or a removal: asked every two seconds while this screen is open (never a second loop).
function poll(m, kind) {
 const part = m[kind];
 if (part.timer) return;
 const name = kind === 'restore' ? 'restore_progress' : 'legacy_rooms_progress';
 const step = async () => {
  if (!m.view?.isConnected) { part.timer = null; return; }
  let answer = null;
  try { answer = await m.action(name, {language: m.lang}); } catch (e) { answer = null; }
  if (answer?.done) {
   part.timer = null;
   if (answer.state === 'idle') { part.phase = kind === 'restore' ? 'choose' : null; part.result = null; }
   else { part.phase = 'done'; part.result = answer; }
   m.redraw[kind]?.();
   return;
  }
  part.timer = setTimeout(step, POLL_MS);
 };
 part.timer = setTimeout(step, 0);
}
// Home Assistant's file upload (the same as its own backup upload): the file's id for restore_check.
async function upload(hass, file) {
 const form = new FormData();
 form.append('file', file);
 const response = await hass.fetchWithAuth('/api/file_upload', {method: 'POST', body: form});
 if (!response.ok) throw new Error('upload ' + response.status);
 const id = (await response.json())?.file_id;
 if (typeof id !== 'string' || !id) throw new Error('upload without an id');
 return id;
}

/* ---- the list: Dashboard and name, the E32's own settings, Maintenance ---- */
function list(ctx) {
 const {kit, t, model} = ctx, {h} = kit, live = model.live || {}, m = memoOf(ctx);
 const general = kit.card({title: w(ctx, 'dashboard_and_name'), icon: 'home', cls: 'form', data: {group: 'general'}},
  h('div', {class: 'fields'},
   ctx.field('text', 'name', {label: w(ctx, 'name'), maxlength: 80, required: true, help: w(ctx, 'name_help')}),
   ctx.field('toggle', 'create_dashboard', {label: w(ctx, 'dashboard'), help: w(ctx, 'dashboard_help')})));
 const needs = live.e32 ? null : t('Connect the E32 first: Configure → E32 connection.');
 const log = live.logging ? (live.logging.on ? w(ctx, 'sends_to', {server: live.logging.server || '–'}) : t('Off')) : t(SUBTITLES.logging);
 const row = (item, icon, summary) => paint(ctx.row({label: t(TITLES[item]), icon: 'info', route: '#installation/' + item, data: {item}, summary: [needs || summary]}), icon);
 const rows = h('div', {class: 'card list iv-rows', 'data-group': 'e32'},
  row('logging', 'log', log), row('time-zone', 'earth', live.time_zone || t(SUBTITLES['time-zone'])),
  row('tester', 'flask', t(live.tester ? 'On' : 'Off')), live.status ? row('status', 'checklist', t(SUBTITLES.status)) : null);
 const maintenance = live.maintenance || {};
 const parts = [part(ctx, m, 'restore', w(ctx, 'restore'), 'restore', () => restoreSummary(ctx), restorePart, maintenance.restoring),
  part(ctx, m, 'tidy', w(ctx, 'tidy'), 'tag', () => tidySummary(ctx, m), tidyPart)];
 if (maintenance.legacy_rooms || maintenance.legacy_pending || maintenance.legacy_removing || m.legacy.phase)
  parts.push(part(ctx, m, 'legacy', w(ctx, 'legacy'), 'bin', () => legacySummary(ctx), legacyPart, maintenance.legacy_removing));
 const page = h('div', {class: 'iv-page'}, general, rows,
  h('h2', {class: 'iv-heading', text: w(ctx, 'maintenance')}), h('div', {class: 'iv-parts'}, ...parts));
 m.view = page;
 return page;
}
// A maintenance part: a collapsible section with its summary line; its body is drawn when it opens, and again after
// each step (m.redraw[key]); a running restore or removal opens it.
function part(ctx, m, key, title, icon, summary, build, running) {
 const body = ctx.kit.h('div', {class: 'iv-part', 'data-part': key});
 if (running) m.open[key] = true;
 let el;
 const draw = () => {
  body.replaceChildren(...[].concat(build(ctx, m, el)).filter(Boolean));
  el.setSummary(summary());
 };
 el = ctx.kit.fold({key, title, icon: 'info', summary: summary(), open: !!m.open[key], data: {section: key},
  onToggle: on => { m.open[key] = on; m.keep.set(m.open); if (on) draw(); }}, body);
 paint(el, icon);
 m.redraw[key] = () => { if (el.isConnected) draw(); };
 if (m.open[key]) draw();
 return el;
}

/* ---- Restore a backup on this E32 (e32_backup_flow's steps: choose, check, confirm, apply, done) ---- */
function restoreSummary(ctx) {
 const b = ctx.model.live?.maintenance?.backup;
 if (!b) return ctx.t(ERRORS.e32_restore_unavailable);
 return [b.last ? w(ctx, 'last_backup', {moment: when(ctx, b.last)}) : w(ctx, 'no_backup'), w(ctx, 'kept_n', {n: b.count ?? (b.kept || []).length})].join(' · ');
}
function restorePart(ctx, m, el) {
 const {kit} = ctx, r = m.restore, b = ctx.model.live?.maintenance?.backup;
 if (ctx.readOnly) return kit.h('p', {class: 'help', text: w(ctx, 'admin_only')});
 // A restore that runs when this model was read is followed (once per model read: a closed result stays closed).
 if (ctx.model.live?.maintenance?.restoring && r.model !== ctx.model) { r.model = ctx.model; if (r.phase !== 'done') r.phase = 'applying'; }
 if (r.phase === 'checking') return [kit.statusLine(w(ctx, 'checking'), 'accent'), bar(ctx)];
 if (r.phase === 'applying') { poll(m, 'restore'); return [kit.statusLine(w(ctx, 'applying'), 'accent'), bar(ctx)]; }
 if (r.phase === 'done') return restoreDone(ctx, m);
 if (!b) return notice(ctx, ctx.t(ERRORS.e32_restore_unavailable), 'info');
 if (r.phase === 'checked' && r.check) return restoreChecked(ctx, m, el);
 return restoreChoose(ctx, m);
}
function restoreChoose(ctx, m) {
 const {kit} = ctx, {h} = kit, r = m.restore, kept = ctx.model.live.maintenance.backup.kept || [];
 const redraw = () => m.redraw.restore?.();
 const options = kept.map(k => ({value: 'kept:' + k.id, label: when(ctx, k.created),
  help: [KINDS[k.kind] ? w(ctx, KINDS[k.kind]) : k.kind, kilobytes(k.size), k.keys ? w(ctx, 'kind_secrets') : ''].filter(Boolean).join(' · ')}));
 options.push({value: 'file', label: w(ctx, 'backup_file'), help: w(ctx, 'file_help')});
 if (!options.some(o => o.value === r.source)) r.source = options[0].value;
 const error = r.error || {}, shown = [];
 const fieldError = (api, field) => { if (error.field === field) { api.setError(error.text); shown.push(field); } return api.el; };
 const parts = [h('p', {class: 'help', text: w(ctx, 'restore_choose')}), kit.more(w(ctx, 'restore_kept', {count: kept.length}), ctx.lang)];
 if (!kept.length) parts.push(notice(ctx, ctx.t(ERRORS.e32_restore_no_backups), 'info'));
 parts.push(kit.fields.radio({key: 'iv-source', hass: ctx.hass, label: w(ctx, 'backup'), value: r.source, options, help: w(ctx, 'backup_help'),
  onChange: v => { r.source = v; r.error = null; redraw(); }}).el);
 if (r.source === 'file') {
  const input = h('input', {type: 'file', accept: '.json,application/json', hidden: true, 'data-file': ''});
  input.addEventListener('change', async () => {
   const file = input.files?.[0];
   if (!file) return;
   r.uploading = true; r.error = null; redraw();
   try { r.file = {upload_id: await upload(ctx.hass, file), name: file.name}; }
   catch (e) { r.file = null; r.error = {field: 'upload_id', text: ctx.t(ERRORS.e32_restore_file_missing)}; }
   r.uploading = false; redraw();
  });
  const chooser = h('div', {class: 'field iv-file', 'data-field': 'upload_id'}, h('span', {class: 'label', text: w(ctx, 'backup_file')}),
   h('div', {class: 'iv-file-row'}, withGlyph(kit.button(w(ctx, 'choose_file'), () => input.click(), 'outlined', {icon: 'plus', 'data-action': 'choose-file', disabled: r.uploading}), 'upload'),
    h('span', {class: 'iv-file-name', text: r.uploading ? '…' : r.file?.name || ''})), input);
  if (error.field === 'upload_id') { chooser.append(h('p', {class: 'error', role: 'alert', text: error.text})); chooser.classList.add('invalid'); shown.push('upload_id'); }
  const phrase = kit.fields.text({key: 'iv-passphrase', hass: ctx.hass, label: w(ctx, 'passphrase'), help: w(ctx, 'passphrase_help'), value: r.passphrase || '',
   maxlength: 64, onChange: v => { r.passphrase = v; }});
  phrase.input.type = 'password'; phrase.input.autocomplete = 'off';
  parts.push(chooser, fieldError(phrase, 'passphrase'));
 }
 // A replacement E32: its address and password, as Configure's form (the stored password never goes to another address).
 const other = kit.button(w(ctx, 'other_e32'), () => { r.other = !r.other; redraw(); }, 'text small', {'aria-expanded': String(!!r.other), 'data-action': 'other-e32'});
 parts.push(h('div', {class: 'iv-other'}, other));
 if (r.other) {
  const address = kit.fields.text({key: 'iv-address', hass: ctx.hass, label: w(ctx, 'address'), help: w(ctx, 'address_help'), value: r.address || '', placeholder: 'http://e32.local',
   onChange: v => { r.address = v; }});
  const password = kit.fields.text({key: 'iv-password', hass: ctx.hass, label: w(ctx, 'password'), help: w(ctx, 'password_help'), value: '', onChange: v => { r.password = v; }});
  password.input.type = 'password'; password.input.autocomplete = 'off';
  parts.push(h('p', {class: 'help', text: w(ctx, 'restore_replace')}), fieldError(address, 'address'), fieldError(password, 'password'));
 }
 if (error.text && !shown.includes(error.field)) parts.push(kit.inlineError(error.text));
 const check = async () => {
  const values = {language: ctx.lang}, source = {};
  if (r.source === 'file') {
   if (!r.file) { r.error = {field: 'upload_id', text: ctx.t(ERRORS.e32_restore_file_missing)}; redraw(); return; }
   source.upload_id = r.file.upload_id;
   if (r.passphrase) values.passphrase = r.passphrase;
  } else source.backup = r.source.slice(5);
  if (r.other && (r.address || '').trim()) { values.address = r.address.trim(); if (r.password) values.password = r.password; }
  r.phase = 'checking'; r.error = null; redraw();
  try {
   r.check = await m.action('restore_check', {...values, ...source});
   r.source_values = source; r.address_used = values.address || null; r.phase = 'checked';
  } catch (e) { r.phase = 'choose'; r.error = {field: e?.field || 'base', text: errorText(ctx, e)}; }
  r.password = '';
  redraw();
 };
 parts.push(actions(ctx, kit.button(w(ctx, 'check'), check, 'outlined', {'data-action': 'check', disabled: r.uploading || (r.source === 'file' && !r.file)})));
 return parts;
}
function restoreChecked(ctx, m, el) {
 const {kit} = ctx, {h} = kit, r = m.restore, c = r.check, redraw = () => m.redraw.restore?.();
 const created = c.created ? when(ctx, c.created) : r.file?.name || '–';
 const back = () => { r.phase = 'choose'; r.check = null; r.error = null; redraw(); };
 const parts = [h('div', {class: 'iv-check', 'data-check': ''}, h('p', {class: 'iv-check-of', text: w(ctx, 'confirm_of', {created})}),
  h('p', {class: 'iv-summary', text: c.summary || ''}))];
 if (r.address_used) parts.push(h('p', {class: 'help', text: w(ctx, 'other_e32_text', {address: r.address_used})}));
 if (c.nothing && !c.adopt) {
  parts.push(notice(ctx, ctx.t(ERRORS.e32_restore_nothing), 'info'), actions(ctx, kit.button(w(ctx, 'another'), back, 'text', {'data-action': 'another'})));
  return parts;
 }
 // One question that states every fact: a restore, and (another E32) that Home Assistant uses this E32 from now on.
 const question = c.adopt && c.nothing ? {title: w(ctx, 'adopt_title'), text: w(ctx, 'adopt_text', {created}), confirm: w(ctx, 'adopt_button')}
  : c.adopt ? {title: w(ctx, 'both_title'), text: `${w(ctx, 'both_text')} ${w(ctx, 'confirm_rest')}`, confirm: w(ctx, 'both_button')}
   : {title: w(ctx, 'confirm_title'), text: w(ctx, 'confirm_rest'), confirm: w(ctx, 'confirm_button')};
 const label = c.adopt && c.nothing ? w(ctx, 'adopt_button') : c.adopt ? w(ctx, 'both_button') : w(ctx, 'restore_button');
 if (!(c.adopt && c.nothing)) parts.push(h('p', {class: 'help', text: w(ctx, 'confirm_rest')}));
 if (r.error?.text) parts.push(kit.inlineError(r.error.text));
 const apply = async () => {
  if (!(await kit.confirm(el.getRootNode(), {...question, lang: ctx.lang}))) return;
  r.phase = 'applying'; r.error = null; redraw();
  try { await m.action('restore_apply', {...r.source_values, ...(c.adopt ? {adopt: true} : {})}); poll(m, 'restore'); }
  catch (e) { r.phase = 'checked'; r.error = {field: 'base', text: errorText(ctx, e)}; }
  redraw();
 };
 parts.push(actions(ctx, kit.button(label, apply, 'filled', {'data-action': 'restore'}), kit.button(w(ctx, 'another'), back, 'text', {'data-action': 'another'})));
 return parts;
}
function restoreDone(ctx, m) {
 const {kit} = ctx, r = m.restore, a = r.result || {};
 const text = a.state === 'failed' ? ctx.errorText(a.error || 'e32_restore_failed')
  : ctx.t(ERRORS[a.state] || ERRORS.e32_restore_failed, {reenter: a.reenter || '-'});
 const tone = a.state === 'failed' ? 'error' : CLOSING.includes(a.state) ? 'success' : 'info';
 const close = () => { m.restore = {phase: 'choose', source: r.source, model: r.model}; m.redraw.restore?.(); };
 return [ctx.kit.h('div', {'data-done': a.state || ''}, notice(ctx, text, tone)), actions(ctx, kit.button(w(ctx, 'close'), close, 'text', {'data-action': 'close'}))];
}

/* ---- Tidy entity IDs and undo it (entity_id_tidy: the steps entity_ids and entity_ids_undo) ---- */
function undoCount(ctx, m) { return m.tidy.undo ?? ctx.model.live?.maintenance?.tidy_undo ?? 0; }
function tidySummary(ctx, m) { const n = undoCount(ctx, m); return n ? w(ctx, 'undo_n', {n}) : w(ctx, 'optional'); }
function tidyPart(ctx, m, el) {
 const {kit} = ctx, {h} = kit, s = m.tidy, redraw = () => m.redraw.tidy?.();
 if (ctx.readOnly) return h('p', {class: 'help', text: w(ctx, 'admin_only')});
 const close = () => { s.done = s.undone = null; s.preview = null; redraw(); };
 if (s.done) return [h('div', {'data-done': 'entity_ids_done'}, notice(ctx, ctx.t(ERRORS.entity_ids_done, {count: s.done.count, todo: s.done.todo || '-'}), 'success')),
  actions(ctx, kit.button(w(ctx, 'close'), close, 'text', {'data-action': 'close'}))];
 if (s.undone) return [h('div', {'data-done': 'entity_ids_undone'}, notice(ctx, ctx.t(ERRORS.entity_ids_undone, {count: s.undone.count}), 'success')),
  actions(ctx, kit.button(w(ctx, 'close'), close, 'text', {'data-action': 'close'}))];
 const load = () => {
  s.loading = true; s.error = null;
  m.action('tidy_ids_preview', {only_unused: s.only, language: ctx.lang}).then(a => { s.preview = a; }, e => { s.error = errorText(ctx, e); })
   .finally(() => { s.loading = false; redraw(); });
 };
 if (s.error && !s.preview) return [kit.inlineError(s.error), actions(ctx, kit.button(w(ctx, 'read_again'), () => { s.error = null; redraw(); }, 'text', {'data-action': 'again'}))];
 if (!s.preview) { if (!s.loading) load(); return kit.skeleton('rows', 2); }
 const p = s.preview, parts = [];
 if (p.nothing) parts.push(h('p', {class: 'iv-line', 'data-nothing': '', text: ctx.t(ERRORS.entity_ids_nothing)}));
 else {
  const n = (p.rows || []).length + (p.more || 0);
  parts.push(h('p', {class: 'help', text: w(ctx, 'tidy_text', {count: p.count, used: p.used})}), kit.more(w(ctx, 'tidy_warning', {days: p.days}), ctx.lang),
   kit.fields.radio({key: 'iv-scope', hass: ctx.hass, label: w(ctx, 'scope'), value: s.only ? 'unused' : 'all', help: w(ctx, 'scope_help'),
    options: [{value: 'unused', label: w(ctx, 'scope_unused')}, {value: 'all', label: w(ctx, 'scope_all')}],
    onChange: v => { s.only = v === 'unused'; s.preview = null; redraw(); }}).el,
   h('div', {class: 'iv-ids', 'data-ids': ''}, ...(p.rows || []).map(r => h('div', {class: 'iv-id', 'data-old': r.old},
    r.name ? h('span', {class: 'iv-id-name', text: r.name}) : null,
    h('span', {class: 'iv-id-ids'}, h('span', {class: 'iv-id-old', text: r.old}), h('span', {class: 'iv-arrow', 'aria-hidden': 'true', text: ' → '}), h('span', {class: 'iv-id-new', text: r.new})),
    r.used_in?.length ? h('span', {class: 'iv-id-used', text: w(ctx, 'used_in', {places: r.used_in.join(', ')})}) : null))),
   p.more ? h('p', {class: 'help', text: w(ctx, 'more_n', {n: p.more})}) : null);
  if (s.error) parts.push(kit.inlineError(s.error));
  const tidy = async () => {
   if (!(await kit.confirm(el.getRootNode(), {title: w(ctx, 'rename_title', {count: n}), text: w(ctx, 'tidy_warning', {days: p.days}),
    confirm: w(ctx, 'tidy_confirm'), lang: ctx.lang}))) return;
   try { const a = await m.action('tidy_ids_apply', {only_unused: s.only, language: ctx.lang}); s.done = a; s.undo = a.count; s.preview = null; }
   catch (e) { s.error = errorText(ctx, e); }
   redraw();
  };
  if (n) parts.push(actions(ctx, kit.button(w(ctx, 'tidy_button'), tidy, 'outlined', {'data-action': 'tidy'})));
 }
 const count = undoCount(ctx, m);
 if (count) {
  const undo = async () => {
   if (!(await kit.confirm(el.getRootNode(), {title: w(ctx, 'undo'), text: w(ctx, 'undo_text', {count}), confirm: w(ctx, 'undo_confirm'), lang: ctx.lang}))) return;
   try { s.undone = await m.action('tidy_ids_undo', {language: ctx.lang}); s.undo = 0; s.preview = null; }
   catch (e) { s.error = errorText(ctx, e); }
   redraw();
  };
  parts.push(h('div', {class: 'iv-undo', 'data-undo': ''}, h('h3', {class: 'iv-sub', text: w(ctx, 'undo')}), h('p', {class: 'help', text: w(ctx, 'undo_text', {count})}),
   actions(ctx, kit.button(w(ctx, 'undo_button'), undo, 'outlined', {'data-action': 'undo'}))));
 }
 return parts;
}

/* ---- Remove the old Home Assistant rooms (legacy_rooms_flow: the steps legacy_rooms*, Repairs' too) ---- */
function legacySummary(ctx) {
 const n = ctx.model.live?.maintenance?.legacy_rooms || 0;
 return n === 1 ? w(ctx, 'room_one') : n ? w(ctx, 'rooms_n', {n}) : w(ctx, 'finish');
}
function legacyPart(ctx, m, el) {
 const {kit} = ctx, {h} = kit, l = m.legacy, redraw = () => m.redraw.legacy?.();
 if (ctx.readOnly) return h('p', {class: 'help', text: w(ctx, 'admin_only')});
 if (ctx.model.live?.maintenance?.legacy_removing && l.model !== ctx.model) { l.model = ctx.model; if (!l.phase) l.phase = 'removing'; }
 if (l.phase === 'removing') { poll(m, 'legacy'); return [kit.statusLine(w(ctx, 'removing'), 'accent'), bar(ctx)]; }
 const reload = () => { l.phase = null; l.list = null; l.result = null; l.error = l.failed = null; redraw(); };
 if (l.phase === 'done') {
  const a = l.result || {};
  const text = a.state === 'failed' ? ctx.errorText(a.error || 'legacy_rooms_plan_failed') : ctx.t(ERRORS[a.state] || ERRORS.legacy_rooms_plan_failed, {rooms: a.rooms ?? 0});
  return [h('div', {'data-done': a.state || ''}, notice(ctx, text, a.state === 'failed' ? 'error' : a.state === 'legacy_rooms_removed' ? 'success' : 'info')),
   actions(ctx, kit.button(w(ctx, 'close'), reload, 'text', {'data-action': 'close'}))];
 }
 if (!l.list) {
  // A list that could not be read says why; a refused removal says why above the list read again.
  if (l.failed) return [kit.inlineError(l.failed), actions(ctx, kit.button(w(ctx, 'read_again'), reload, 'text', {'data-action': 'again'}))];
  if (!l.loading) {
   l.loading = true;
   m.action('legacy_rooms', {language: ctx.lang}).then(a => { l.list = a; }, e => { l.failed = errorText(ctx, e); }).finally(() => { l.loading = false; redraw(); });
  }
  return [l.error ? kit.inlineError(l.error) : null, kit.skeleton('rows', 2)];
 }
 const a = l.list, parts = [];
 const remove = async (ids, question) => {
  if (question && !(await kit.confirm(el.getRootNode(), {...question, lang: ctx.lang}))) return;
  l.phase = 'removing'; l.error = null; redraw();
  try { await m.action('legacy_rooms_remove', {ids, language: ctx.lang}); poll(m, 'legacy'); }
  catch (e) { l.phase = null; l.error = errorText(ctx, e); if (e?.code === 'legacy_rooms_changed') l.list = null; }
  redraw();
 };
 if (a.state === 'legacy_rooms_none') return h('p', {class: 'iv-line', text: ctx.t(ERRORS.legacy_rooms_none)});
 if (a.problem) parts.push(notice(ctx, ctx.errorText(a.problem), 'error'));
 if (l.error) parts.push(kit.inlineError(l.error));
 if (a.finish) {
  parts.push(h('p', {class: 'help', text: w(ctx, 'finish_text')}));
  if (!a.problem) parts.push(actions(ctx, kit.button(w(ctx, 'finish'), () => remove([]), 'outlined', {'data-action': 'finish'})));
  return parts;
 }
 parts.push(h('p', {class: 'help', text: w(ctx, 'legacy_text', {rooms: a.rooms.map(r => r.name).join(', ')})}),
  h('div', {class: 'iv-ids', 'data-rooms': ''}, ...a.rooms.map(r => h('div', {class: 'iv-id', 'data-room': r.id}, h('span', {class: 'iv-id-name', text: r.name}),
   r.entities?.length ? h('span', {class: 'iv-id-used', text: r.entities.join(', ')}) : null))),
  h('h3', {class: 'iv-sub', text: w(ctx, 'what_happens')}), h('p', {class: 'iv-summary', 'data-changes': '', text: a.changes || ''}));
 if (!a.problem && a.readable !== false) {
  parts.push(actions(ctx, kit.button(w(ctx, 'legacy'), () => remove(a.rooms.map(r => r.id), {title: w(ctx, 'legacy_question'), text: w(ctx, 'legacy_remove_text'),
   confirm: w(ctx, 'legacy'), danger: true}), 'danger', {'data-action': 'remove'})));
 } else if (a.readable === false) parts.push(actions(ctx, kit.button(w(ctx, 'read_again'), reload, 'text', {'data-action': 'again'})));
 return parts;
}

/* ---- the E32's own screens (#installation/logging, /time-zone, /tester, /status) ---- */
// The system log's fields (field names, not texts).
const LOGGING = Object.freeze(['syslog_enabled', 'server', 'port', 'syslog_level', 'syslog_esp', 'syslog_ems', 'web_level', 'mark_interval_s']);
function logging(ctx) {
 const {kit, t, model: m, values: v} = ctx, {h} = kit;
 const levels = Object.entries(LEVELS).map(([value, label]) => ({value, label: t(label)}));
 const sending = h('div', {class: 'fields iv-sending', 'data-part': 'sending'},
  ctx.field('text', 'server', {label: t('Syslog server'), maxlength: 15, placeholder: '192.168.1.10',
   help: t('The IPv4 address of the syslog server, for example 192.168.1.10. Needed when sending is on.')}),
  ctx.field('number', 'port', {label: t('UDP port'), min: 1, max: 65535, step: 1, help: t('Usually 514.')}),
  ctx.field('select', 'syslog_level', {label: t('Send up to level'), options: levels, help: t('Error is enough for normal use; Debug and Trace send a lot.')}),
  'syslog_esp' in m ? ctx.field('toggle', 'syslog_esp', {label: t('Send the E32\'s own messages'), help: t('Messages of the E32 itself: network, heating, updates.')}) : null,
  'syslog_ems' in m ? ctx.field('toggle', 'syslog_ems', {label: t('Send the boiler bus messages'),
   help: t('The messages the E32 hears on the boiler bus; useful to look into a boiler problem.')}) : null);
 const toggle = ctx.field('toggle', 'syslog_enabled', {label: t('Send to a syslog server'), help: t('Off: the E32 keeps its log only on its own page.'), onChange: () => show()});
 // The help follows the switch: the "Off: …" line only while it is off.
 const show = () => { sending.hidden = !v.syslog_enabled; const help = toggle.querySelector('.help'); if (help) help.hidden = !!v.syslog_enabled; };
 show();
 return [kit.card({cls: 'form', data: {group: 'sending'}}, h('div', {class: 'fields'}, toggle, sending)),
  kit.card({cls: 'form', data: {group: 'keep'}}, h('div', {class: 'fields'},
   ctx.field('select', 'web_level', {label: t('Keep on the E32 up to level'), options: levels, help: t('The most detailed level the E32 keeps for its own log page.'),
    more: t('The E32 keeps its own log as well (Diagnostics and system log on its web page).')}),
   ctx.field('number', 'mark_interval_s', {label: t('Still-running message every'), unit: 's', min: 0, max: 86400, step: 1,
    help: t('Seconds between short “still running” messages; 0 is off.')})))];
}
function timeZone(ctx) {
 const {kit, t, model: m, values: v} = ctx, {h} = kit, live = m.live || {};
 const options = m.zones.map(z => ({value: z, label: z}));
 if (!m.time_zone) options.unshift({value: '', label: t('{zone} (not in the list)', {zone: live.e32 || '–'})});
 const field = ctx.field('select', 'time_zone', {label: t('Time zone'), options,
  help: t('After saving, the E32 restarts once to use the new time zone; the heating continues after about a minute.'),
  onChange: () => { use.hidden = !live.home_zone || v.time_zone === live.home_zone; }});
 const use = h('div', {class: 'iv-zone'}, ctx.readOnly ? null : kit.button(t('Use the time zone of Home Assistant'), () => {
  const s = field.querySelector('select'); s.value = live.home_zone; s.dispatchEvent(new Event('change'));
 }, 'outlined', {'data-action': 'home-zone'}));
 use.hidden = ctx.readOnly || !live.home_zone || v.time_zone === live.home_zone;
 return [h('div', {class: 'iv-status'}, kit.statusLine(t('Now on the E32: {e32}. Home Assistant: {home}.', {e32: live.e32 || '–', home: live.home || '–'}), 'rest')),
  live.restarting ? h('div', {class: 'iv-done', 'data-done': 'time-zone'}, notice(ctx, t('The E32 now uses {zone}. It restarts once; the heating continues after about a minute.', {zone: m.time_zone}), 'info')) : null,
  kit.card({cls: 'form'}, h('div', {class: 'fields'}, field, use))];
}
function tester(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit, live = m.live || {}, rec = live.recording, parts = [];
 if (live.done && DONE[live.done]) parts.push(h('div', {class: 'iv-done', 'data-done': live.done}, notice(ctx, t(DONE[live.done], {minutes: 30}), 'info')));
 const card = kit.card({cls: 'form'}, h('div', {class: 'fields'}, ctx.field('toggle', 'tester_enabled', {label: t('Take part in the tester program'),
  help: t('You can switch it off here at any time.'),
  more: `${t('While this is on, you can make a 30-minute recording of the messages on your boiler\'s cable and share the result with the OpenThermostat project on GitHub, so your boiler model can be tested and verified.')} ${t('Home Assistant never sends anything itself: it writes the files and shows you a link to the GitHub form. You see everything before you post it. Off: nothing is recorded and nothing is read for it.')}`})));
 parts.push(card);
 if (m.tester_enabled) {
  const state = rec?.state in RECORDING ? rec.state : 'unreachable';
  const minutes = Math.floor((rec?.seconds > 0 ? rec.seconds : 0) / 60), frames = (rec?.frames > 0 ? rec.frames : 0).toLocaleString(ctx.lang);
  const box = kit.card({cls: 'iv-recording', data: {recording: state}}, kit.statusLine(t(RECORDING[state], {minutes, frames}), state === 'recording' ? 'heat' : state === 'ready' ? 'ok' : 'rest'),
   h('p', {class: 'help', text: t('Start a recording, then let the boiler rest, heat (set the thermostat higher) and make hot water (open a hot tap for a few minutes). After 30 minutes choose Share result. Keep your thermostat connected.')}));
  if (!ctx.readOnly) {
   const act = action => () => ctx.act({action});
   box.append(actions(ctx, state === 'recording' ? kit.button(t('Stop the bus recording'), act('stop'), 'outlined', {'data-action': 'stop'})
    : !['unavailable', 'not_supported'].includes(state) ? kit.button(t('Start a bus recording (30 minutes)'), act('start'), 'outlined', {'data-action': 'start'}) : null,
    kit.button(t('Share result'), act('share'), 'filled', {'data-action': 'share'})));
  }
  parts.push(box);
 }
 return parts;
}
function status(ctx) {
 const {kit, t, model: m} = ctx, {h} = kit;
 if (!m.blocks?.length) return kit.card({}, kit.empty({icon: 'check', text: t('There is nothing to check.')}));
 return m.blocks.map(b => kit.card({title: b.title, cls: 'iv-block'}, ...String(b.text).split(/\n{2,}/).map(p => h('p', {text: p}))));
}

// The editable values of a screen (its model names it); the status edits nothing.
function values(m) {
 if (m.screen === 'list') return {name: m.name, create_dashboard: m.create_dashboard === true};
 if (m.screen === 'logging') {
  const v = Object.fromEntries(LOGGING.filter(k => k in m).map(k => [k, m[k]]));
  v.syslog_level = String(m.syslog_level); v.web_level = String(m.web_level);
  return v;
 }
 if (m.screen === 'time-zone') return {time_zone: m.time_zone};
 if (m.screen === 'tester') return {tester_enabled: m.tester_enabled};
 return {};
}

const STYLE = `.iv-page{display:grid}.iv-rows{margin-top:var(--ot-s3)}
.iv-heading{font-size:var(--ot-text-l);line-height:var(--ot-line-l);font-weight:500;margin:var(--ot-s5) 0 var(--ot-s3) 2px}
.iv-part{display:grid;gap:var(--ot-s3);padding:var(--ot-s4) 0 var(--ot-s3)}.iv-part .field{border:0;margin:0;padding:0}
.iv-part .notice{margin:0}.iv-actions{display:flex;flex-wrap:wrap;gap:var(--ot-s2);align-items:center}
.iv-pre p,.iv-summary{white-space:pre-line;overflow-wrap:anywhere}
.iv-check{display:grid;gap:var(--ot-s2);padding:var(--ot-s3) var(--ot-s4);border-radius:var(--ot-radius-s);background:var(--ot-raised);border:1px solid var(--ot-divider)}
.iv-check-of{font-weight:500}.iv-sub{font-size:var(--ot-text-m);font-weight:500}.iv-line{color:var(--ot-text)}
.iv-file-row{display:flex;flex-wrap:wrap;align-items:center;gap:var(--ot-s3)}.iv-file-name{color:var(--ot-muted);overflow-wrap:anywhere}
.iv-file .error{color:var(--ot-error);font-size:var(--ot-text-s);font-weight:500}.iv-other{margin:-4px 0 0 -12px}
.iv-ids{display:grid;border:1px solid var(--ot-divider);border-radius:var(--ot-radius-s);max-height:360px;overflow:auto;background:var(--ot-surface)}
.iv-id{display:grid;gap:2px;padding:var(--ot-s2) var(--ot-s3);border-top:1px solid var(--ot-divider)}.iv-id:first-child{border-top:0}
.iv-id-name{font-weight:500}.iv-id-ids,.iv-id-used{font-size:var(--ot-text-s);line-height:var(--ot-line-s);color:var(--ot-muted);overflow-wrap:anywhere}
.iv-id-new{color:var(--ot-text)}.iv-undo{display:grid;gap:var(--ot-s1);padding-top:var(--ot-s3);border-top:1px solid var(--ot-divider)}
.iv-progress{height:4px;border-radius:2px;overflow:hidden;background:color-mix(in srgb,var(--ot-accent) 18%,var(--ot-surface));position:relative}
.iv-progress::after{content:"";position:absolute;inset:0 auto 0 0;width:30%;border-radius:2px;background:var(--ot-fill);animation:iv-run 1.4s ease-in-out infinite}
@keyframes iv-run{from{transform:translateX(-100%)}to{transform:translateX(340%)}}
.iv-status{margin:-8px 0 var(--ot-s3)}.iv-done{margin-bottom:var(--ot-s3)}.iv-zone{padding:0 0 var(--ot-s2)}
.iv .ot-card.form>.fields>.field:first-child,.iv .ot-card.form>.ot-card-head+.fields>.field:first-child{padding-top:var(--ot-s2)}
.iv-recording{display:grid;gap:var(--ot-s2)}.iv-block p+p{margin-top:var(--ot-s2)}.iv-block p{white-space:pre-line;overflow-wrap:anywhere}
.iv-sending:empty{display:none}
@media(max-width:420px){.iv-check{padding:var(--ot-s3)}.iv-actions .btn{flex:1 1 auto}}`;

(window.OpenThermostatSettingsSections ||= []).push(['installation', {
 title: (model, item) => TITLES[item] || WORDS.installation,
 subtitle: (model, item) => SUBTITLES[item] || null,
 texts: TEXTS,
 errors: ERRORS,
 cards: true,
 values,
 toSave: (v, m) => (m.screen === 'time-zone' ? {time_zone: v.time_zone, posix: m.posix} : v),
 confirm: (v, m, ctx) => {
  if (m.screen === 'list' && m.create_dashboard && v.create_dashboard === false)
   return {title: w(ctx, 'hide_title'), text: w(ctx, 'hide_text'), confirm: w(ctx, 'hide_button'), danger: true};
  if (m.screen === 'time-zone' && v.time_zone !== m.time_zone)
   return {title: ctx.t('Restart the E32 to use the new time zone?'), text: ctx.t('The heating continues after about a minute.'), confirm: ctx.t('Save and restart')};
  return null;
 },
 shown: (key, value, t) => (key.endsWith('_level') ? t(LEVELS[value] || String(value)) : null),
 render: ctx => {
  const {kit} = ctx, screen = ctx.model.screen || 'list';
  const body = {logging, 'time-zone': timeZone, tester, status}[screen] || list;
  return kit.h('div', {class: 'iv', 'data-screen': screen}, kit.h('style', {text: STYLE}), body(ctx));
 }
}]);
