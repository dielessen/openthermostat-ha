# Add a device: send a capture

> **The firmware and the project's main repository are not public at the moment.** What these guides say
> about downloading the firmware or a release ZIP from GitHub, updating the E32's firmware from Home
> Assistant or with **Check for updates**, and the tester program's GitHub form does not work for now. The
> Home Assistant integration is installed and updated through the Marketplace as described. A few
> references to pages that are not public have no link here. Questions or problems:
> [open an issue](https://github.com/dielessen/openthermostat-ha/issues).

[Nederlands](ADD-A-DEVICE.nl.md)

Your radiator valve, thermostat or sensor is not in the [device matrix](DEVICES.md), or OpenThermostat does not read
it well (no battery, no "set to", a valve that stays "unknown")? Send us what the device really sends: a **capture**.
It takes a few minutes. We turn it into a test, and from then on every build is checked against your device, so it
keeps working.

A capture is text, never a screenshot. It holds no passwords. It may hold the names you gave your devices and rooms:
rename them before you paste if you would rather not share them.

## 1. The Zigbee2MQTT state (Zigbee2MQTT devices)

Either way gives the same text; one is enough.

**In the Zigbee2MQTT frontend:** open **Devices**, choose the device, open its **State** tab and copy everything in
it.

**With `mosquitto_sub`** (on a computer that reaches your MQTT broker; the Mosquitto broker add-on of Home Assistant
has it in its terminal):

```sh
mosquitto_sub -h <broker address> -u <user> -P <password> -t 'zigbee2mqtt/<device name>' -C 1 -W 900
```

It waits for the device's next message (at most 15 minutes) and prints it. Turn the valve's knob or change its
target temperature to make it send one at once. `<device name>` is the device's friendly name in Zigbee2MQTT,
spaces included (keep the quotes).

Also note the **Zigbee2MQTT version** (Zigbee2MQTT → **Settings** → **About**) and the device's own **firmware
version** (the device's **About** tab).

## 2. The Home Assistant entity (every device in Home Assistant)

In Home Assistant open **Developer tools** → **States**, type the device's name in the filter and choose its entity:
for a thermostat or a radiator valve the `climate.` one, for a sensor its `sensor.` one. Copy:

- the **entity ID** (for example `climate.living_room_valve`),
- its **state** (for example `heat`),
- the **attributes** (the text in the attributes box, as it is).

## 3. The E32 Diagnostics line

Since E32 1.4.4 the E32 counts every device message it received and could not read. Look on the E32's page
**System → Diagnostics and system log**, or in Home Assistant on the OpenThermostat dashboard's **Diagnostics** tab
under **Connection with the E32**, for a line like:

> Messages the E32 could not read since it started: 3, last: zigbee2mqtt/Living room valve, too large (7.1 KB)

Copy it if it is there; write "none" when it is not.

## 4. Send it

Open a new issue with the form **Add or fix a device**:
[github.com/dielessen/openthermostat-ha/issues/new?template=new-device.yml](https://github.com/dielessen/openthermostat-ha/issues/new?template=new-device.yml).
Paste each part into its own field and say how the device is connected (for example "Zigbee2MQTT on the same broker
as the E32" or "ZHA in Home Assistant"). Everything you post there is public.

## What happens with it

We run one command (`tools/dev/device_fixture.py`) that turns your issue into a folder of the project's device
collection (`test/fixtures/devices/`). The tests then read your device's state with the E32's own code and with Home
Assistant's, and the [device matrix](DEVICES.md) shows it as **verified with a real capture**. If the E32 does not
read it yet, the fix is checked against your capture before it is released.
