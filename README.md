<p align="center">
  <img src="https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/brand/logo.svg" alt="OpenThermostat" width="420">
</p>

# OpenThermostat for Home Assistant

OpenThermostat is a thermostat for your central heating. It runs on a small box
next to your boiler, the BBQKees Gateway E32 V2. Every room gets its own week
program, and the thermostat learns how fast each room warms up, so it is warm
when you want it. Everything stays in your own home, without a cloud account.

This integration brings OpenThermostat into Home Assistant: a thermostat per
room, a week planner card, your boiler's values, energy figures, daily backups
and firmware updates with one click.

## What you need

This integration does not work on its own. You need:

- A **[BBQKees Gateway E32 V2](https://bbqkees-electronics.nl/product/gateway-e32-v2-ethernet-wifi-edition-v2/)**,
  connected to your boiler.
- The **OpenThermostat firmware** on that gateway. You install it once over USB;
  HACS does not do that for you. See
  [installing the firmware](https://github.com/dielessen/open_thermostat/blob/main/docs/INSTALL.md#2-install-the-firmware-on-the-e32-first-time-over-usb).
  The gateway usually comes with EMS-ESP, which the firmware replaces, so
  [make a backup first](https://github.com/dielessen/open_thermostat/blob/main/docs/FLASHING.md#make-a-full-backup-first).
- A boiler that speaks **EMS Classic (EMS 1.0)**: most Nefit, Buderus, Bosch,
  Junkers and Worcester boilers. Newer EMS+ boilers are planned for version 1.1.
- An **MQTT broker** (for example the Mosquitto add-on) and the MQTT integration.
- **Home Assistant 2026.10.0 or newer.**

## What you get

- A thermostat per room, with Comfort, Eco, Night and Boost.
- A week planner card: drag a time to change it, copy a day to another.
- Away and holiday modes, and automatically lower when everyone has left. Warm again when you come back.
- Window and door contacts that pause a room while a window is open.
- Radiator valves set per room.
- "What the thermostat has learned": per room how fast it warms up and cools
  down, and what it changed by itself, in plain words.
- Your boiler's water temperatures, pressure, burner starts, hot water use and
  display code in words. Problems show up under Repairs.
- Gas use for heating and hot water, if you have a gas meter in Home Assistant.
- A daily backup of all E32 settings, which you can put back on a new E32.
- Firmware updates for the E32 under Settings → Updates.
- A ready-made dashboard, if you want one.
- English, Dutch and Polish.

The E32 is the thermostat itself. It keeps heating your rooms on its own
program when Home Assistant is offline.

## Screenshots

These use made-up example data, not a real home.

![The OpenThermostat dashboard in Home Assistant: the house card, the rooms, today and the house](https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/ha-dashboard-rc5.png)

![The week planner card in Home Assistant](https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/ha-week-card-rc2.png)

![What the thermostat has learned, per room](https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/e32-home-learned-rc2.png)

<details>
<summary>More screenshots</summary>

![The Boiler tab: what the boiler does now, then what you need first](https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/ha-dashboard-boiler-rc5.png)

![The Learning tab: what the E32 knows, the heating curve and yesterday in figures](https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/ha-dashboard-learning-rc5.png)

![The E32 Overview with rooms and the boiler](https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/e32-overview-rc2.png)

![A room with its week program on the E32](https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/e32-rooms-rc2.png)

![The E32 Boiler page](https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/e32-boiler-rc2.png)

<img src="https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/ha-dashboard-phone-dark-rc5.png" alt="The dashboard on a phone in the dark theme" width="320">
<img src="https://raw.githubusercontent.com/dielessen/open_thermostat/main/docs/img/screenshots/e32-overview-phone-dark-rc2.png" alt="The E32 Overview on a phone in the dark theme" width="320">

</details>

## Install

1. Put the OpenThermostat firmware on the E32 and connect it to your Wi-Fi and
   your MQTT broker. The
   [installation guide](https://github.com/dielessen/open_thermostat/blob/main/docs/INSTALL.md#2-install-the-firmware-on-the-e32-first-time-over-usb)
   explains how.
2. In Home Assistant, open **HACS**, the three dots at the top right, then
   **Custom repositories**. Add `https://github.com/dielessen/openthermostat-ha`
   with type **Integration**.
3. Search for **OpenThermostat** in HACS, choose **Download** and restart Home
   Assistant.
4. Go to **Settings → Devices & services → Add integration → OpenThermostat**
   and follow the steps.

The E32 then guides you further. If your old thermostat is still connected, it
first runs beside it for a while without touching the boiler. Otherwise it
starts with a short boiler test. It only controls your boiler after you confirm.

**Test versions** (such as `1.0.0rc6`) are not shown by default. To install one,
open OpenThermostat in HACS, choose **Download** and pick the version under
**Need a different version?**.

## Help and more information

- [Installation guide](https://github.com/dielessen/open_thermostat/blob/main/docs/INSTALL.md)
- [User guide](https://github.com/dielessen/open_thermostat/blob/main/docs/USER-GUIDE.md)
- [Switching over from your old thermostat](https://github.com/dielessen/open_thermostat/blob/main/docs/SWITCHOVER.md)
- [Release notes](https://github.com/dielessen/open_thermostat/blob/main/docs/modern-thermostat/HA-RELEASE-NOTES.md)
- [The main project](https://github.com/dielessen/open_thermostat): the firmware, all documentation and the source code

Questions or problems? [Open an issue](https://github.com/dielessen/open_thermostat/issues) in the main project. It
helps to add the integration's diagnostics (Settings → Devices & services →
OpenThermostat → ⋮ → Download diagnostics) and the E32's firmware version.

OpenThermostat is an independent project. It is not made or supported by
BBQKees Electronics.

## Versions and licence

Each version here is exactly the released package `ha-v<version>` of the main
project, checked against its SHA-256 list.

MIT licence (see [LICENSE](LICENSE)). OpenThermostat started as
[OpenThermostat by Pawel Filipczak / intuibase](https://github.com/intuibase/open_thermostat).
Further development and releases are by Mark Dielessen.
