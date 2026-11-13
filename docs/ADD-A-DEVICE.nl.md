# Een apparaat aanmelden: stuur een opname

> **De firmware en de hoofdrepository van het project zijn op dit moment niet openbaar.** Wat deze
> handleidingen zeggen over het downloaden van de firmware of een release-ZIP van GitHub, het bijwerken van
> de firmware van de E32 vanuit Home Assistant of met **Check for updates**, en het GitHub-formulier van het
> testerprogramma werkt voorlopig niet. De Home Assistant-integratie installeer en werk je bij via de
> Marketplace, zoals beschreven. Een paar verwijzingen naar pagina's die niet openbaar zijn hebben hier
> geen link. Vragen of problemen: [open een issue](https://github.com/dielessen/openthermostat-ha/issues).

[English](ADD-A-DEVICE.md)

Staat je radiatorkraan, thermostaat of sensor niet in de [apparatentabel](DEVICES.nl.md), of leest OpenThermostat hem
niet goed (geen batterij, geen "staat op", een kraan die "onbekend" blijft)? Stuur ons wat het apparaat echt stuurt:
een **opname**. Het kost een paar minuten. Wij maken er een test van, en vanaf dan wordt elke build tegen jouw apparaat
gecontroleerd, zodat het blijft werken.

Een opname is tekst, nooit een schermafbeelding. Er staan geen wachtwoorden in. Wel misschien de namen die je je
apparaten en ruimtes gaf: verander die voordat je plakt als je ze liever niet deelt.

## 1. De status in Zigbee2MQTT (Zigbee2MQTT-apparaten)

Beide manieren geven dezelfde tekst; één is genoeg.

**In de Zigbee2MQTT-frontend:** open **Devices**, kies het apparaat, open het tabblad **State** en kopieer alles wat
erin staat.

**Met `mosquitto_sub`** (op een computer die je MQTT-broker bereikt; de Mosquitto broker-add-on van Home Assistant
heeft het in zijn terminal):

```sh
mosquitto_sub -h <adres van de broker> -u <gebruiker> -P <wachtwoord> -t 'zigbee2mqtt/<naam van het apparaat>' -C 1 -W 900
```

Het wacht op het volgende bericht van het apparaat (hooguit 15 minuten) en drukt het af. Draai aan de knop van de kraan
of verander zijn gewenste temperatuur, dan stuurt hij er meteen een. `<naam van het apparaat>` is de friendly name in
Zigbee2MQTT, met spaties (laat de aanhalingstekens staan).

Noteer ook de **versie van Zigbee2MQTT** (Zigbee2MQTT → **Settings** → **About**) en de **firmwareversie** van het
apparaat zelf (het tabblad **About** van het apparaat).

## 2. De entiteit in Home Assistant (elk apparaat in Home Assistant)

Open in Home Assistant **Ontwikkelaarshulpmiddelen** → **Statussen**, typ de naam van het apparaat in het filter en
kies zijn entiteit: voor een thermostaat of radiatorkraan de `climate.`-entiteit, voor een sensor de `sensor.`-entiteit.
Kopieer:

- de **entiteits-ID** (bijvoorbeeld `climate.kraan_woonkamer`),
- de **status** (bijvoorbeeld `heat`),
- de **attributen** (de tekst in het vak met attributen, zoals hij is).

## 3. De regel op Diagnose van de E32

Sinds E32 1.4.4 telt de E32 elk apparaatbericht dat hij ontving en niet kon lezen. Kijk op de E32-pagina **Systeem →
Diagnose en systeemlog**, of in Home Assistant op het tabblad **Diagnose** van het OpenThermostat-dashboard onder
**Verbinding met de E32**, naar een regel zoals:

> Berichten die de E32 niet kon lezen sinds hij startte: 3, laatste: zigbee2mqtt/Kraan woonkamer, te groot (7,1 KB)

Kopieer hem als hij er staat; schrijf "geen" als hij er niet staat.

## 4. Versturen

Open een nieuwe melding met het formulier **Add or fix a device**:
[github.com/dielessen/openthermostat-ha/issues/new?template=new-device.yml](https://github.com/dielessen/openthermostat-ha/issues/new?template=new-device.yml).
Plak elk deel in zijn eigen veld en zeg hoe het apparaat is aangesloten (bijvoorbeeld "Zigbee2MQTT op dezelfde broker
als de E32" of "ZHA in Home Assistant"). Het formulier is in het Engels; Nederlands schrijven mag. Alles wat je daar
plaatst is openbaar.

## Wat we ermee doen

Wij draaien één opdracht (`tools/dev/device_fixture.py`) die je melding omzet in een map van de apparatenverzameling
van het project (`test/fixtures/devices/`). De tests lezen de status van je apparaat dan met de eigen code van de E32
en met die van Home Assistant, en de [apparatentabel](DEVICES.nl.md) toont het als **bevestigd met een echte opname**.
Leest de E32 het nog niet, dan wordt de oplossing tegen jouw opname gecontroleerd voordat hij uitkomt.
