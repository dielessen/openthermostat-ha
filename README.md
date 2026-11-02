# OpenThermostat for Home Assistant

The Home Assistant integration of [OpenThermostat](https://github.com/dielessen/open_thermostat): a self-learning room
thermostat on an E32 V2 board that controls an EMS boiler (Nefit, Buderus, Bosch,
Junkers, Worcester) and radiator valves.

This repository only carries the integration for HACS. The firmware, the documentation
and the issue tracker live in the main repository: <https://github.com/dielessen/open_thermostat>.

## Install with HACS

1. In Home Assistant open **HACS**, the three dots at the top right, **Custom repositories**.
2. Repository: `https://github.com/dielessen/openthermostat-ha`, type **Integration**, **Add**.
3. Find **OpenThermostat** in HACS, **Download**, and restart Home Assistant.
   Release candidates (for example 1.0.0rc1) are pre-releases: switch on
   **Show beta versions** for this repository to see them.
4. **Settings → Devices and services → Add integration → OpenThermostat**, and follow
   the steps. The installation guide explains everything: <https://github.com/dielessen/open_thermostat/blob/main/docs/INSTALL.md>.

Requirements: Home Assistant 2026.10.0 or newer, an MQTT broker (the MQTT integration), and an
E32 V2 with the OpenThermostat firmware (see the main repository for the firmware and
how to install it).

## Versions

Each version here is exactly the released package `ha-v<version>` of the main repository
(the same files, checked against its SHA-256 list). Release notes: see each release, or
https://github.com/dielessen/open_thermostat/blob/main/docs/modern-thermostat/HA-RELEASE-NOTES.md.
