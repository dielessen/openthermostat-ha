# Install OpenThermostat

> **The firmware and the project's main repository are not public at the moment.** What these guides say
> about downloading the firmware or a release ZIP from GitHub, updating the E32's firmware from Home
> Assistant or with **Check for updates**, and the tester program's GitHub form does not work for now. The
> Home Assistant integration is installed and updated through the Marketplace as described. A few
> references to pages that are not public have no link here. Questions or problems:
> [open an issue](https://github.com/dielessen/openthermostat-ha/issues).

This guide takes you from a new BBQKees E32 V2 gateway to a working
OpenThermostat with Home Assistant: firmware installed, connected to your
network and boiler, linked to Home Assistant, and your rooms set up with a
week program. You do not need to be a developer. You do need to be
comfortable adding a custom integration to Home Assistant (with the Marketplace, or by
copying files) and, once, connecting the E32 to your boiler.

It matches the E32 firmware of the release you download and the Home
Assistant integration that the same release notes pair with it. Always install the
firmware and the integration versions that the release notes pair together: a
firmware and an integration from different releases may not understand each
other.

> **The E32 sends nothing to the boiler until you confirm the takeover.** The
> default path is: connect the E32, run the **boiler test**, take over. When the
> E32 hears that your old thermostat still asks the boiler for heat, it first
> runs a **trial run** (shadow mode) beside it: it measures your rooms, follows
> your week programs and calculates what it *would* ask of the boiler, and your
> thermostat keeps controlling the boiler. The trial run is optional: you can
> always go straight to the boiler test. The one thing that acts on your home
> before the takeover is an optional *setting device* (a valve or thermostat
> that Home Assistant sets to your week program); see
> [The route to the takeover](#12-the-route-to-the-takeover-boiler-test-or-a-trial-run-first).

Want someone to check the guide as they go? Give them the
[installation checklist](INSTALL-CHECK.md): each step, its expected result
and where to look.

Installing as a field tester? Start with the
field tester pack: what to prepare, the install order, how
to hand back to your thermostat, and what to report.

**Time needed:** about one hour for the E32, plus about half an hour for Home
Assistant.

## Contents

1. [What you need](#1-what-you-need)
2. [Install the firmware on the E32 (first time, over USB)](#2-install-the-firmware-on-the-e32-first-time-over-usb)
3. [First start: connect the E32 to your Wi-Fi](#3-first-start-connect-the-e32-to-your-wi-fi)
4. [Sign in and change the admin password](#4-sign-in-and-change-the-admin-password)
5. [Basic settings: time zone and boiler reception](#5-basic-settings-time-zone-and-boiler-reception)
6. [Connect the E32 to the boiler](#6-connect-the-e32-to-the-boiler)
7. [Pair Bluetooth thermometers (optional)](#7-pair-bluetooth-thermometers-optional)
8. [MQTT: let the E32 talk to Home Assistant](#8-mqtt-let-the-e32-talk-to-home-assistant)
9. [Install the Home Assistant integration](#9-install-the-home-assistant-integration)
10. [Add the integration and connect the E32](#10-add-the-integration-and-connect-the-e32)
11. [Add your rooms](#11-add-your-rooms)
12. [The route to the takeover: boiler test, or a trial run first](#12-the-route-to-the-takeover-boiler-test-or-a-trial-run-first)
13. [Updates](#13-updates)
14. [Backup and restore](#14-backup-and-restore)
15. [Secure your setup](#15-secure-your-setup)
16. [Forgotten password and Wi-Fi recovery over USB](#16-forgotten-password-and-wi-fi-recovery-over-usb)
17. [Troubleshooting](#17-troubleshooting)

## 1. What you need

**Hardware**

- A **BBQKees E32 V2** gateway (ESP32 with 16 MB flash). The release files
  are built for this board only; the original E32 and the ESP32-S3 gateways
  are different boards.
- A boiler that speaks **EMS Classic (EMS 1.0)**, connected directly or
  through an adapter such as the Bosch EasyControl Adapter. Boilers that only
  speak **EMS+ (EMS 2.0) are supported read-only until their model is
  verified**: the E32 reads them and runs a trial run beside the thermostat,
  but does not control them. Today no EMS+ model is verified (see
  [an EMS+ boiler](#an-ems-boiler-the-attended-test-with-the-thermostat-disconnected)).
- A **USB-C cable that carries data** (not a charge-only cable) and a
  computer. A new E32 gets its first firmware over USB; later updates go over
  the network.
- At least one **temperature source per room**: a supported Bluetooth
  thermometer, or a temperature sensor or thermostat that is already in Home
  Assistant.

**Network**

- A **2.4 GHz Wi-Fi** network (the E32 cannot use 5 GHz), or an Ethernet
  cable to your router.

**Home Assistant**

- **Home Assistant 2026.10.0 or newer** (the automatic tests run against 2026.10.0, 2026.10.4, 2026.11.0 and 2026.11.1; it is in use on 2026.11.x).
- An **MQTT broker**, for example the Mosquitto broker add-on, and Home
  Assistant's **MQTT integration**. All live values travel between the E32 and
  Home Assistant over MQTT. Section 8 explains how to set it up.
- Internet access for Home Assistant, so it can fetch firmware updates from
  GitHub.
- The **Marketplace** (**Settings → Marketplace**, built into Home Assistant
  2026.11 and newer) is the easiest way to install and update the integration
  (section 9). Without it you copy the release ZIP into Home Assistant by
  hand. On Home Assistant 2026.10 and older the same job is done by HACS; see
  the note in section 9.1.

**Optional**

- **Zigbee2MQTT**, only if you want the E32 to drive Zigbee2MQTT radiator
  valves (Bosch BTH-RA, Sonoff TRVZB, Sonoff TRV Gen2, Tuya TV02 or another
  Zigbee2MQTT thermostat) on the same MQTT broker. Valves of other
  integrations (ZHA, Z-Wave, Shelly and so on) work through Home Assistant
  without it. See [Radiator valves](USER-GUIDE-REFERENCE.md#radiator-valves).

**Not needed:** a cloud account or the ESPHome integration. Without
Home Assistant, sections 8 to 11 do not apply: you then set up the rooms on
the E32 itself (see the [user guide](USER-GUIDE.md#6-add-your-first-room-on-the-e32)).

<a id="2-install-the-firmware-on-a-new-e32-usb"></a>

## 2. Install the firmware on the E32 (first time, over USB)

You do this only once. Later updates go over your network and keep your
settings (see [Updates](#13-updates)).

> **This erases the E32.** A BBQKees gateway usually comes with EMS-ESP
> installed. Installing OpenThermostat replaces it and deletes its settings.
> If you might want to go back, first export your EMS-ESP settings and make a
> full backup as described in [USB backup and recovery](FLASHING.md#make-a-full-backup-first).

### 2.1 Download the release

1. Open the releases page
   and choose the newest **E32 V2** release. Its tag starts with `v` and
   contains `e32v2`, for example `v1.4.6-e32v2`.
2. Under **Assets**, download `open-thermostat-e32v2-<version>.zip`. Do not
   use the "Source code" downloads that GitHub adds automatically.
3. Extract the ZIP into a new folder. You need two files from it:
   - `e32v2-factory.bin`: the complete installation image, written at address
     `0x0`;
   - `FACTORY-CHECK.txt`: the image length and the checksum (MD5) you use to
     check that the image was written correctly.

   The `firmware.bin` in the same release is for updates only. The factory
   image is only for a first installation or a clean reinstall.

### 2.2 Connect the E32 to your computer

1. Disconnect the E32 from the boiler (the EMS cable) and from any other power
   supply.
2. Connect the E32's USB-C port to your computer. USB powers the E32 while you
   install.
3. If your computer shows no new serial port (a COM port on Windows), install
   the USB driver that BBQKees recommends; see the
   [BBQKees firmware update guide](https://bbqkees-electronics.nl/wiki/gateway/firmware-update-and-downgrade.html#gateway-s3-s3-lr-and-e32-v2).

Then choose one of the two routes below. Route A needs no installation on
your computer.

### 2.3 Route A: in the browser with ESPConnect

[ESPConnect](https://thelastoutpostworkshop.github.io/ESPConnect/) is a free,
open-source flashing tool that runs in **Chrome or Edge** (not Safari or
Firefox). It is made by an independent developer, not by this project.

1. Open ESPConnect, choose **115200** baud if it asks, click **Connect** and
   pick the E32's serial port.
2. Check **Device Info**: it must show an **ESP32** (not ESP32-S3) with
   **16 MB** flash. If it does not, stop: this is not an E32 V2.
3. Go to **Flash Tools → Flash Firmware** and select `e32v2-factory.bin`.
4. Set the **flash offset** to exactly `0x0` and tick **Erase entire flash
   before writing**.
5. Click **Flash Firmware**, check the file name and `0x0` in the
   confirmation, and wait until it reports success. Keep the cable connected.
6. Before the first restart, check the result under **Flash Tools → Flash
   Integrity**: start offset `0x0`, length = the `Length` from
   `FACTORY-CHECK.txt` (a number of bytes). Click **Compute MD5**. The result
   must equal the "MD5 before first boot" in `FACTORY-CHECK.txt`. If it
   differs, flash again.
   *Why now:* at its first start the E32 writes its own settings, after which
   the checksum no longer matches.
7. Click **Disconnect**, unplug the USB cable and plug it in again. The E32
   starts OpenThermostat.

### 2.4 Route B: on the command line with esptool

For people who prefer a terminal. Install Python, then run these commands in
the folder with the extracted files. Replace `PORT` with the E32's port, for
example `COM5` on Windows or `/dev/ttyUSB0` on Linux.

```sh
python -m pip install esptool==4.5.1
python -m esptool --chip esp32 --port PORT flash_id
# Continue only if this reports an ESP32 with 16MB flash.
python -m esptool --chip esp32 --port PORT --after no_reset erase_flash
python -m esptool --chip esp32 --port PORT --baud 115200 --after no_reset write_flash \
  --flash_mode dio --flash_freq 80m --flash_size 16MB 0x0 e32v2-factory.bin
python -m esptool --chip esp32 --port PORT --after no_reset verify_flash 0x0 e32v2-factory.bin
```

`--after no_reset` keeps the E32 from starting before the check. When
`verify_flash` succeeds, unplug the USB cable and plug it in again.

**If neither tool can connect:** try another data cable, plug directly into
the computer (not through a hub), close other programs that use the same
port, and follow BBQKees' instructions for starting the board in download
mode. Do not bridge pins on the board.

## 3. First start: connect the E32 to your Wi-Fi

A new E32 has no Wi-Fi settings yet, so it opens its own temporary setup
network for you to connect to.

1. Power the E32 (USB is fine for now). After a few seconds a Wi-Fi network
   called **`OpenThermostat-xxxxxx`** appears, where `xxxxxx` is the end of the
   E32's hardware address. Its password is **`openthermostat`**.
2. Join that network with your phone or laptop. The page **Connect to your
   WiFi** usually opens by itself; if not, open `http://10.10.10.1/` in a
   browser. If your phone asks whether to stay on a network without internet,
   choose to stay.
3. Choose **Find networks**, pick your home network under **Networks found**
   (only 2.4 GHz networks are listed), or type its name under **WiFi name**.
   Enter the **WiFi password** and choose **Connect**.
4. The E32 tests the connection; this takes up to 30 seconds. Your settings
   are saved only after a successful connection. If it fails, the page says
   so, the setup network stays available, and you can try again.
5. When it succeeds, the page shows **WiFi connected** and the E32's address
   on your home network, then closes the setup network after a few seconds.
   Reconnect your phone or laptop to your home network and open that address.
   **Save it as a bookmark**: you will need it again for Home Assistant.

A new E32 is also reachable by its name, for example
`http://openthermostat-a1b2c3.local/`, if your network supports `.local`
names. Your router's list of connected devices shows it too (its name starts
with `openthermostat-`).

The setup network stays open for about 15 minutes. If it closes before you
are done, unplug the E32 and plug it in again: it opens again as long as no
Wi-Fi network has been saved.

**Ethernet instead of Wi-Fi (optional):** after signing in, open **System → Settings**,
section **Network**, set **E32 network (active after restart)** to
**Ethernet only**, choose **Save settings**, let the E32 restart and plug in
the network cable. Your router then gives the E32 a new address; look it up in
the router.

## 4. Sign in and change the admin password

1. Open the E32's address. Sign in with user **`admin`** and password
   **`admin`**.
2. The page asks you straight away to **Choose your own password**. Enter
   **Your new password** (8 to 64 characters) and **Repeat your new
   password**, then choose **Save password**. The user name stays `admin`.
   Until you do, the E32 shows its pages but accepts no change, from the
   browser or from Home Assistant, with one exception: giving control back to
   your old thermostat always works (a button on this step while the E32
   controls the boiler).

*Why it matters:* with the default password, anyone on your network could
change your heating. Write the new password down: Home Assistant asks for it in
section 10. If you ever forget it, you can reset it over USB
([section 16](#16-forgotten-password-and-wi-fi-recovery-over-usb)).

*An E32 that was set up with an older firmware and still uses `admin`:* after the
update it keeps heating as before and Home Assistant keeps reading it, but
changes wait. Home Assistant shows the repair **E32 still uses the default
password**; choose **Fix**, enter a new password twice and submit. Home
Assistant changes it on the E32 and stores it, in one step. You can also sign
in on the E32 page, which asks for the new password at once; Home Assistant
then asks you for it once (Settings → Devices & services).

The E32 menu reads **Overview, Rooms, Home, Boiler** and **System**. System
holds Settings, Password, Backup and restore, Devices
(Bluetooth sensors and Shelly devices), Firmware update, Diagnostics and system log, About, Restart device
and, once you are signed in, **Sign out**. In Dutch: Overzicht, Ruimtes, Huis,
Ketel and Systeem (Sign out is Afmelden). The language follows your browser;
change it at the bottom of any page.

**System → Settings** opens the page with the sections Password, Network,
Home Assistant (the link and its MQTT broker), Time, Backup and restore and
Advanced; Password and Backup and restore also have their own menu rows. The
tools for developers are under **System → Diagnostics and system log → For
developers**. Messages of an older Home Assistant integration may still name the earlier
menu path *System → Network and Home Assistant → MQTT*; it is now **System →
Settings → Home Assistant**.

## 5. Basic settings: time zone and boiler reception

Both are on the **System → Settings** page. When you are done, choose **Save settings**
at the bottom. The E32 then offers a restart so the changes take
effect; choose **Restart now**.

1. **Time zone** (section **Time**). Week programs follow the E32's own clock,
   so it must know your time zone. Pick yours under **Time zone**, or choose
   **Use this time zone** when the page suggests your browser's time zone.
   Keep the time server (`pool.ntp.org`) unless your network needs another.
   For a time zone that is not listed, choose "Other (enter POSIX text under
   Advanced)" and enter it under **Advanced**, for example
   `EST5EDT,M3.2.0,M11.1.0` for US Eastern.
2. **Boiler reception** (fold **Advanced**, near the bottom):
   tick **Boiler bus (EMS) on**. A newly installed E32 starts with this off, so it
   receives no boiler data until you turn it on. Turning it on only lets the
   E32 *listen* to the boiler; it does not let it send heat requests.

Leave the other settings as they are for now. MQTT follows in section 8.

## 6. Connect the E32 to the boiler

> **Safety first.** Switch the boiler off (and disconnect its power) before
> you connect or disconnect anything on the EMS bus. Follow BBQKees'
> instructions for your gateway and boiler: see the
> [BBQKees wiki](https://bbqkees-electronics.nl/wiki/) and the
> [gateway hardware details](https://bbqkees-electronics.nl/wiki/gateway/hardware-details.html).
> If you are not sure how your boiler is wired, ask an installer.

1. Connect the E32 to the boiler's EMS bus and power it the way BBQKees
   describes for your setup.
2. **Leave your existing thermostat connected and in control for now.** The
   E32 only listens; it hears whether a thermostat still asks the boiler for
   heat and picks its route from that (section 12). The boiler test tells you
   when to disconnect it.
3. Switch the boiler on again.
4. On the E32, open **Boiler**. Within a few minutes it shows live values such
   as flow and return temperature, the burner status and the boiler's
   **Display code** in words. "Listening to the boiler bus (EMS) is off."
   means the **Boiler bus (EMS) on** setting from section 5 is still off.
5. Open **Boiler model**, choose your boiler and choose **Save boiler
   selection**. This only changes the name and picture shown; it does not
   change how the E32 talks to the boiler.
6. After about 10 minutes, the block **My boiler** names the boiler the E32
   recognised on the bus, and whether it may control it
   ([boiler recognition](USER-GUIDE-REFERENCE.md#boiler-recognition-my-boiler)).

Not every boiler reports every value; water pressure, for example, is missing
on many models. The E32 never makes up a value that the boiler does not
report. See [Boiler values are missing](#boiler-values-are-missing).

## 7. Pair Bluetooth thermometers (optional)

Skip this section if all your room temperatures come from Home Assistant.
Bluetooth thermometers have one advantage: the E32 receives them itself, so
they keep working when Home Assistant is offline.

Supported: **Shelly BLU H&T Display**, **Xiaomi Monitor 3 (MJWSD05MMC)** with
its bindkey, and thermometers with **pvvx firmware** (BTHome v2, plain or with
a bindkey, or the older PVVX Custom format).

1. Place the sensor in the room, away from radiators, windows and direct sun,
   and within Bluetooth range of the E32.
2. On the E32, open **System → Devices** and, under **Bluetooth sensors**, choose **Search nearby**. The list shows
   up to 32 of the strongest nearby devices.
3. Click your sensor. Give it a clear name (for example "Living room
   thermometer") and check its profile. Enter the encryption key only if the
   sensor uses one; Xiaomi Monitor 3 always needs its bindkey. Keys are stored
   on the E32 and never shown again.
4. Choose **Save Bluetooth settings**. The E32 restarts by itself about 30
   seconds later to apply them.
5. After the restart the sensor shows a temperature under **Your sensors**.
   "Waiting" means nothing has been received yet.

With Home Assistant and OpenThermostat already set up, the dashboard tab
**Settings → Devices → Bluetooth sensors → Pair a sensor** does steps 2 to 4:
the E32 searches, you choose your sensor, check its name and **Sensor type**,
fill in the key only if it encrypts, and choose **Pair**.

Up to eight sensors can be paired. A reading stays valid for 15 minutes. The
[user guide](USER-GUIDE.md#5-pair-a-bluetooth-thermometer) has a worked
example for a pvvx thermometer.

## 8. MQTT: let the E32 talk to Home Assistant

MQTT is the messenger between the E32 and Home Assistant: the E32 sends its
room temperatures, boiler values and calculations through an MQTT *broker*,
and Home Assistant reads them there. Home Assistant's own setup step
([section 10](#10-add-the-integration-and-connect-the-e32)) refuses to
continue until MQTT is on, so do this first.

### 8.1 A broker and Home Assistant's MQTT integration

Skip this if Home Assistant already uses an MQTT broker.

1. In Home Assistant, go to **Settings → Add-ons → Add-on store**, install
   the **Mosquitto broker** add-on and start it. (Add-ons exist on Home
   Assistant OS and Supervised installations. On other installation types, run
   an MQTT broker yourself.)
2. Home Assistant then offers the **MQTT** integration under **Settings →
   Devices & services**. Add it. If you use another broker, add the MQTT
   integration and enter that broker.

### 8.2 A login for the E32 on the broker

The E32 needs its own user name and password on the broker; it does not
connect to Home Assistant through a broker without a login.

With the Mosquitto add-on, the simplest way is a separate Home Assistant user,
for example `e32`: **Settings → People → Users → Add user**. (The **Users** tab
appears when **Advanced mode** is on in your Home Assistant user profile.) The
user does not need to be an administrator.

### 8.3 MQTT settings on the E32

On the E32, open **System → Settings**, section **Home Assistant**, part
**MQTT broker**:

1. Tick **Connect to the MQTT broker**.
2. **Broker address**: the IP address or name of the broker. With the
   Mosquitto add-on, this is the address of your Home Assistant, for example
   `192.168.1.10`.
3. **Broker port**: `1883`, unless your broker uses another port.
4. **User name** and **Password**: the login from section 8.2.
5. Leave everything under **Advanced** as it is. The **Base** is
   `openthermostat` on a new E32 (an E32 set up before beta.19 keeps
   `ib-therm`); Home Assistant fills in what it needs when it connects.
6. Leave **Home Assistant link** and **HA adapter ID** at the top of the same
   section alone. Home Assistant fills them in itself in section 10.
7. Choose **Save settings** and let the E32 restart. Under the broker switch
   the page says (E32 1.4.5) that the E32 sends nothing over MQTT without the
   Home Assistant link: that is right at this point. **Connect E32** in Home
   Assistant (section 10) switches the link on.

After the restart, the log on **System → Diagnostics and system log** shows
whether the E32 reached the broker; the console command `mqtt` on the same
page shows the connection and its counters.

## 9. Install the Home Assistant integration

Install the integration with the Marketplace (9.1), or copy the release ZIP by
hand (9.2). Both put the same files in the same place:
`<config>/custom_components/open_thermostat`, where `<config>` is your Home
Assistant configuration folder (the folder that contains
`configuration.yaml`). Use one route, not both. Already installed by hand?
See 9.3 to move to the Marketplace.

Always install the integration version that the release notes pair with your
E32 firmware.

### 9.1 With the Marketplace (recommended)

OpenThermostat is a *custom repository* in the Marketplace: you add it once.

1. In Home Assistant, open **Settings → Marketplace**. The first time, tick
   **I understand the risks** to continue.
2. Choose **Add from link** at the top right. Under **GitHub link** enter
   `https://github.com/dielessen/openthermostat-ha` and choose **Add**. If the
   Marketplace does not recognise the type by itself, choose **Integration**
   under **Type** and add it again.
3. Search the Marketplace for **OpenThermostat**, open it and choose
   **Install**. The newest stable version is selected.
4. Restart Home Assistant (**Settings → System → Restart**). *Why:* Home
   Assistant only loads new integrations at start-up.

**Updates.** A new version appears under **Settings → Updates**. Select it,
choose **Install** and restart Home Assistant: updates of an integration
still need a restart.

**Home Assistant 2026.10 and older.** There the Marketplace does not exist
and the same steps are done with **HACS**: open **HACS**, the three dots at
the top right, **Custom repositories**, add the repository above (type
**Integration**), then search HACS for **OpenThermostat** and choose
**Download**. HACS checks a repository added by URL only every 48 hours of
Home Assistant uptime; to see a new version at once, open the three dots of
the **OpenThermostat** entry and choose **Update information**. HACS offers
release candidates (versions such as `1.0.0rc7`) only through **Need a
different version?** or the **Pre-release** switch of its OpenThermostat
device. When you upgrade to Home Assistant 2026.11, your HACS custom
repositories move to the Marketplace by themselves.

### 9.2 Without the Marketplace: the release ZIP

1. On the releases page,
   choose the **Home Assistant** release that the release notes pair with your
   E32 firmware. Its tag starts with `ha-v`, for example `ha-v1.4.6`.
   Download `OpenThermostat-HA-<version>.zip`.
2. Extract the ZIP on your computer. It contains a folder
   `custom_components/open_thermostat`.
3. Copy that `open_thermostat` folder into the `custom_components` folder of
   your Home Assistant configuration folder. Create `custom_components` if it
   does not exist yet. When you are done, this file must exist:
   `<config>/custom_components/open_thermostat/manifest.json`.
   Any way of copying files to Home Assistant works, for example the
   **Samba share** or **File editor** add-on.
4. Restart Home Assistant (**Settings → System → Restart**). *Why:* Home
   Assistant only loads new integrations at start-up.

The other files in the ZIP (licence, checksums, release notes, `SOURCE.json`)
do not need to be copied. The optional Zigbee2MQTT companion in the same
release is not needed.

### 9.3 Move a manual install to the Marketplace

The Marketplace writes to the same `custom_components/open_thermostat` folder as the
manual install, so your OpenThermostat entry, rooms, programs and entities
stay as they are. Nothing needs to be removed first.

1. Make a Home Assistant backup: **Settings → System → Backups → Back up
   now**.
2. Keep the OpenThermostat entry under **Settings → Devices & services**. Do
   not delete it and do not add the integration a second time.
3. Follow 9.1: add the custom repository and install the version that
   matches your E32 firmware (the version you have, or the newer one the
   release notes pair with it). The Marketplace replaces the files in
   `custom_components/open_thermostat`.
4. Restart Home Assistant.
5. Check: **Settings → Devices & services** shows **one** OpenThermostat entry
   with your rooms, and the Marketplace lists OpenThermostat as installed.

Keep no second copy of the integration inside `custom_components` (for
example a renamed `open_thermostat_old` folder): Home Assistant would see two
integrations with the same name. Store a copy outside the configuration
folder if you want one.

## 10. Add the integration and connect the E32

### 10.1 Add OpenThermostat

1. Go to **Settings → Devices & services → Add integration** and choose
   **OpenThermostat**.
2. The form **Set up your heating installation** opens:
   - **Installation name**: any name you recognise, for example "Home".
   - **Show the OpenThermostat dashboard**: tick it. The dashboard holds the
     visual week planner, so it makes the next steps easier. Your own
     dashboards are kept.
   - **Advanced → Controller MQTT prefix**: keep `openthermostat`. Change it
     only if the **Base** on your E32's MQTT settings is different (for
     example `ib-therm` on an older E32). The two must match.
3. Choose **Add installation**.

Home Assistant then tells you the next step: **Configure → E32 connection**.
You do not need to add a room yet; that comes right after connecting.

### 10.2 Connect the E32

Before you start, check that MQTT on the E32 is on with a broker user name and
password (section 8.3). Without it, this step stops with a message.

1. Go to **Settings → Devices & services → OpenThermostat** and choose
   **Configure** (the gear icon). Before the E32 is connected, Configure starts
   with **E32 connection**. Once it is connected and the OpenThermostat
   dashboard is shown, Configure has two items: **Open the settings page** (the
   way to the dashboard's **Settings** tab, where every setting is) and **E32
   connection**. Without the dashboard it has
   nine: **Rooms**, **House**, **Heating and boiler**, **Energy and outdoor
   temperature**, **Notifications**, **E32 connection**, **E32 devices**,
   **Dashboard and name** and **Advanced and diagnostics**. Every submenu has
   **← Back**. After you save you are back in the menu, and **Done** closes
   Configure.
2. Choose **E32 connection**.
3. **E32 web address**: the address you use in your browser, including
   `http://`, for example `http://192.168.1.50` or
   `http://openthermostat-a1b2c3.local`. An IP address or a home-network name
   ending in `.local`, `.lan`, `.home`, `.internal`, `.localdomain`,
   `.fritz.box` or `.home.arpa` works.
4. **E32 password**: the password you chose in section 4.
5. Choose **Submit**. Home Assistant checks the E32, points its MQTT link to
   Home Assistant and waits for the E32's first report over MQTT. This can
   take up to two minutes, and the E32 may restart once.
6. When **E32 connected** appears, continue with **Add the first room**
   (section 11).

Home Assistant stores the E32 password. If you change it on the E32 later,
Home Assistant asks for the new one (a **Re-authenticate** prompt on the
integration).

The E32's **Overview** now shows **Home Assistant: connected**.

## 11. Add your rooms

Every room has:

- **one to four temperature sources**: Home Assistant sensors or thermostats,
  and/or Bluetooth sensors paired on the E32. The first one with a fresh value
  is used; the others are a backup;
- **a week program**: the temperatures the room should have through the week.
  The E32 stores it and runs it, also when Home Assistant is offline;
- **optionally a setting device**: a thermostat, radiator valve or number in
  Home Assistant that shows the program's temperature and lets you turn it up
  or down by hand.

### 11.1 Add a room

Right after connecting, choose **Add the first room**. Later, use **Add room** on
the dashboard's **Settings → Rooms** (the same fields, the temperature sources in
one list; without the dashboard: Configure's room form, **Configure → Rooms → Add
a room**). Fill in the **E32 room** form:

1. **Room name**, for example "Living room" (up to 40 letters).
2. **Heating**: **On**. (**Off (no heat demand)** keeps the room in the plan
   but it never asks for heat.)
3. **Heating type**: **Radiators** or **Floor heating**. Each type gets its own
   flow temperature.
4. **Temperature sources from Home Assistant**: choose one or more sensors or
   thermostats that measure this room. Drag them to change the order.
5. **Bluetooth sensors on the E32**: choose the sensors from section 7, if
   any. Tick **Use the Bluetooth sensors first** to make them lead and keep the
   Home Assistant sources as backup.
6. **Setting device (optional)**: see [11.3](#113-the-setting-device).
7. **Temperature without a week program**: a safe fixed temperature, for
   example 19 °C. The room keeps it when it has no week program, and until the
   E32 has a valid clock.
8. **Week program on the E32**: the form fills in the **Workdays and weekend**
   template. You can keep it and fine-tune it later in the visual planner
   (11.2), or type your own: one line per group of days, for example

   ```text
   mon-fri: 06:30 20.5; 22:30 18
   sat-sun: 08:00 20.5; 23:00 18
   ```

   Each temperature holds until the next switch time; a line without days
   applies to every day; up to six switch times per day.
9. **Windows and doors** (folded section, optional): the room's window and
   door contacts (up to 8: after you choose one, an empty field appears below
   it for the next) and **Pause after** (2 minutes by default). See 11.5.
10. **Temperature limits** (folded section): the lowest and highest target this
    room may get. The program and any manual change stay within them.
11. **Persons** (folded section, optional): **Persons of this room**, for
    example the people who sleep in a bedroom. See 11.5.
12. Choose **Submit**. The room is saved on the E32 right away. Choose **Add a
    room** for the next one, or close the window.

The "Workdays and weekend" template is: on workdays 20 °C from 06:30, 18 °C
from 08:30, 20 °C from 17:00 and 16 °C from 22:30; at the weekend 20 °C from
08:00 and 16 °C from 23:00.

To change or remove a room later: the dashboard's **Settings → Rooms**, then the
room (**Remove room** is at the bottom); its radiator valves, persons and
temperature limits are on the same screen (see
[Radiator valves](USER-GUIDE-REFERENCE.md#radiator-valves)). Without the dashboard:
**Configure → Rooms → Edit or remove a room**, pick the room and choose **Edit
room**.

On the E32 **Rooms** page each room is a card that opens with a click. Inside
it, the blocks **Temperature**, **Week program**, **Windows and doors**,
**Persons** and, since 1.4.4, **Learning** (with **Learn again**) fold open too; a
closed block shows a one-line summary.

### 11.2 Edit the week program in the visual planner

The easiest way to change a program is the week planner on the room's own
screen: the **OpenThermostat** dashboard in the Home Assistant sidebar,
**Settings → Rooms** → the room → **Week program**. Every room has
three levels, **Comfort**, **Eco** and **Night**, each with its own
temperature; changing a level changes every block that uses it. Paint a block
with a level, drag the edges of the blocks, use **Copy…** to copy a day to
other days, **Undo** a step, or **Start from a template**. On a phone the
planner also lists each day's blocks. The same planner is on the E32's
**Rooms** page.
Both edit the same program on the E32, and neither overwrites a change the
other made in the meantime.

### 11.3 The setting device

The setting device is how you turn a room up or down by hand. Choose what fits
the room:

| Your room has | Choose as setting device | What happens |
| --- | --- | --- |
| A radiator valve (TRV) in Home Assistant | The valve's thermostat entity | The valve shows the room's temperature; turning it changes the room. |
| A smart thermostat such as tado | Its thermostat entity | The same, on the tado. |
| A number or input number with a target (for example a sensor with a settable temperature) | That number | The number shows the room's temperature; changing it changes the room. |
| None of these | Leave the field empty | You use the room's own **thermostat in Home Assistant** (one per room, created by the integration) or the E32 Overview as a virtual thermostat. |

A setting device shows the room's temperature, and what you turn on it is a
manual change of the room. Valves that the E32 should drive itself after the switch-over (with the room's measured
temperature, and the boiler flow kept as low as the valves allow) go under
the room's **Radiator valves** instead; see the
[reference](USER-GUIDE-REFERENCE.md#radiator-valves).

How it works:

- Home Assistant keeps the setting device at the room's temperature: at every
  switch time of the week program, when the room changes and when the E32 or
  Home Assistant comes back. It works both ways, with and without a week program.
- **Turning the device yourself is a manual change of the room.** With a week
  program it lasts until the next switch time, then the program takes over
  again. Example: the program says 18 °C from 08:30; you turn the tado to 21 °C
  at 10:00; the room aims for 21 °C until the next switch time at 17:00, and
  then follows the program again. Without a week program the turn becomes the
  room's temperature without a week program, for good. The state of the room
  never changes: an Off room stays Off.
- **A device is the room's setting device or a radiator valve the E32 drives,
  not both.** Home Assistant refuses the second role when you save the room.
  After the update to 1.4.2 a valve that had both lost its Valve control once,
  with a Repairs item that goes when you save the room.
- **Turn off the device's own schedule** (put it in manual mode, for example
  in the tado or valve app). Otherwise the device changes its temperature by
  itself and every change counts as a manual change. Home Assistant sets the
  device to manual itself (at most once an hour) and shows a repair message when
  it still notices that a device runs its own schedule.
- Home Assistant writes only to the device you chose, at most once a minute,
  and never while the room is off or paused for an open window. A manual change
  and away go to the device too: it shows what the room aims for now.
- The room's thermostat in Home Assistant shows under **Attributes** what the
  setting device last got and gave, and the last error (`setting_device_...`).
  If setting it fails three times in a row, a repair message says what to
  check.
- The setting device is never filled in for you. If a temperature source of
  the room is a thermostat or valve, the form mentions it as a suggestion;
  choose it yourself only if Home Assistant may write the program's
  temperature to it.

The setting device is a convenience, not a requirement. It needs Home
Assistant: without Home Assistant the E32 keeps running the program, but
changes on the device are not seen until Home Assistant is back.

### 11.4 Water temperature limits

These limits are the lowest and highest water temperature to the heating
(flow temperature) that the E32 may ask of the boiler, for all rooms
together. Check them on the dashboard's **Settings → Heating and boiler → Water
temperature limits** in Home Assistant (without the dashboard: **Configure →
Heating and boiler → Water temperature limits**; without Home Assistant: the E32
**Home** page, section **Water temperature limits**, then **Save limits**). The default is 30–60 °C. Floor
heating fed without a mixing valve usually needs at most 45–50 °C; radiators
often need 60–75 °C on cold days. The E32 never asks for more than the maximum heating temperature
set on the boiler itself.

### 11.5 More options (optional)

On the dashboard's **Settings** tab (without the dashboard: the same items under
**Configure**):

- **Window and door contacts**: sensors that pause a room while a window or
  door is open (it drops to frost protection and asks for no heat). Choose
  them per room under **Settings → Rooms → the room → Windows and doors** (in
  Configure's room form: section **Windows and doors**).
- **Settings → House → Presence and away temperature**: the people of the
  house, how long everyone must be away, and the temperature for an empty
  house. In the house mode Automatic the rooms go to the away temperature once
  everyone has been away for that time (15 minutes by default). A room can
  also have **persons of its own** (Configure's room form, section **Persons**):
  it goes to the away temperature when they are all away, also while others are
  home.
- **Settings → House → House mode and holiday**: the **House mode**
  **Automatic**, **At home**, **Away** or **Holiday** (for a holiday that starts
  now you also choose when it ends); the same control is on the E32 device, on
  the dashboard and on the E32's **Home** page. Under it the holiday planner,
  next.
- **Holiday planner** (**Planned holidays** with **Plan a holiday**, and
  **Temperature on holiday**; in Configure without the dashboard: **House →
  House mode and holiday**; on the E32: the **Home** page, block **Holidays**):
  plan up to 8 holidays ahead,
  each with a start and an end (back home, at most a year ahead). A holiday
  starts and ends by itself. During it every room stays at most **Temperature
  on holiday** (5–25 °C; until you set one it is the away temperature; frost
  protection stays on), the rooms warm up before the end, and afterwards the
  house mode is as before. While a holiday runs, removing it from **Planned
  holidays** ends it at once (Configure without the dashboard: **House → Stop
  holiday**; on the E32 in the **Holidays** block). A holiday
  needs the E32's clock. Home Assistant and the E32 page edit the same list,
  and the **Overview** tab of the dashboard shows the next holiday.
- **Settings → House → Room defaults**: the Comfort and Night temperatures of a
  room without a week program and the pause after a window or door opens.
- **Settings → Heating and boiler → Smart warm-up and weather compensation**:
  both are on by default. Smart warm-up starts heating early,
  so a room is warm at the time in its week program. Weather compensation
  makes the water warmer when it is colder outside. The E32 learns both for
  your house.
  *In the first days:* Smart warm-up starts early at once, as an **estimate**
  (the pages say "starts at 07:40 (estimate; it learns from every morning)"),
  and every morning it checks whether the room was warm on time. A morning
  within 10 minutes teaches it nothing; after a later or earlier one the next
  start moves by 30 per cent of the part beyond 10 minutes, at most 15 minutes
  a morning. See
  [Warm on time](USER-GUIDE-REFERENCE.md#warm-on-time-smart-warm-up).
- **Settings → Energy and outdoor temperature**: a gas meter, gas price,
  outdoor temperature and your boiler's power. All optional; they make the gas
  and cost estimates and the heating advice more accurate.
- The **Daily summary**, the warnings and the notification blueprints: see
  the [reference](USER-GUIDE-REFERENCE.md#daily-summary-and-warnings).

### 11.6 Check it

- The **OpenThermostat** dashboard in the sidebar opens on the **Overview**
  tab. It starts with the **house card**: what the boiler does now, the boiler
  request while rooms want heat, today's gas and burner starts and the day so
  far. Under it is a status card for each room with its temperature and target
  and, in one line, why the room heats or not (the rooms that are on come
  first; the house card shows the room that is on as a figure too). Next to the room cards
  stand **Today** (when each room warms up next) and **House** (home or away,
  holiday, outdoor temperature). The **Rooms** tab has the 24-hour graph of
  each room. The E32's own **Overview** shows the same line on
  each room's card, in the same words, also without Home Assistant.
- Each room has its own group on the integration page, with a thermostat
  (climate entity).
- The **Heating problem** sensor is off when all is well, and **Settings →
  System → Repairs** shows no **Heating needs attention** message.
- On the E32, the **Rooms** page shows the rooms read-only with "Managed in
  Home Assistant". **Edit here anyway** unlocks editing on the E32 for when
  Home Assistant is not reachable.
- Once the E32 has measured a day, **Yesterday** shows how it went: heating
  hours, burner starts per heating hour, short burner runs, gas for heating
  (an estimate), degree-days and, per room, how many minutes late or early it
  was warm and how far it overshot. In Home Assistant it is the section
  **Yesterday** of the **Learning** tab (each figure is
  also a sensor); on the E32 it is on the **Home** page, under **What the E32 has learned**.

**Without Home Assistant**, rooms are set up on the E32 **Rooms** page
instead; see [Add your first room on the E32](USER-GUIDE.md#6-add-your-first-room-on-the-e32).

<a id="12-what-the-trial-run-does-and-does-not-do"></a>

## 12. The route to the takeover: boiler test, or a trial run first

The route to the takeover follows what the E32 hears on the boiler bus
during its first two minutes, as long as it has no room plan stored yet:

- **Another thermostat still asks the boiler for heat** (an EMS thermostat
  such as a tado on the bus): the E32 starts with a **trial run** beside it.
  It calculates and compares, sends nothing, and the Rooms page shows
  **Ready for the E32 to control the boiler?**; its last step is the boiler
  test below.
- **No other thermostat is heard** (none, already removed, or one that is not
  an EMS thermostat): the plan starts in **active control**, and the Rooms page
  leads you through the **Boiler test and takeover**. Active control still
  sends nothing to the boiler until you confirm the takeover.
- **Still listening:** the page says "Checking the boiler bus…" and the E32
  stays in the trial run until it knows.

The Rooms page says which route it chose and why, and you can always choose
the other one: **Trial run first (compare with your thermostat)** or **Go
straight to the boiler test**. An installation that already has a room plan
keeps its mode.

**Boiler test and takeover** (E32 **Boiler** page, right under **Now**). With someone at the boiler,
about 30 minutes; **Start the boiler test** first asks you to stay near the
boiler, so you can switch it off if something looks wrong. The E32 checks each
step itself from what the boiler reports and shows it as passed, waiting or
failed, with what to do. No existing thermostat is required: the page speaks
of an old thermostat only when the E32 has heard another controller ask the
boiler for heat (it remembers that).

1. **No other thermostat on the boiler** (**Disconnect your old thermostat**
   when the E32 heard one): with an old thermostat, switch the boiler off,
   disconnect the thermostat from the boiler and switch the boiler on again.
   Passes when no other thermostat is heard for 2 minutes while boiler
   messages arrive.
2. **Confirm the takeover:** **Confirm the takeover** opens the usual
   confirmation ("Let the E32 control the boiler?"; after an old thermostat:
   "Confirm that your current thermostat is disconnected…"). Passes once the
   E32 controls the boiler.
3. **Start heating:** the E32 sets the first active room with a working sensor
   about 1 °C above its temperature, as a temporary change with an end time
   (the week program is not changed). Passes when the burner starts for
   heating within 10 minutes and the water to heating gets at least 3 °C
   warmer within 15 minutes.
4. **Hot water while heating:** open a hot tap for 3 minutes. Passes when hot
   water goes first and heating resumes within 5 minutes after it, without a
   warning. A boiler without hot water can skip this step.
5. **Stop heating:** the room is set 0.5 °C below its temperature. Passes when
   the burner switches off within about 45 seconds of the E32's request for no
   heat (after its shortest run) and stays off for 5 minutes.
6. **Done:** "The E32 now controls your boiler." The temporary change ends and
   the week program continues.

Each step has a time limit. The E32 stops the test with "Stop and give control
back to your thermostat" (without a thermostat it ever heard: "Stop E32
control") and the steps to do so when another thermostat asks the boiler for
heat, control is given back, room measurements are lost, a warning of active
control appears, the water to heating goes above the highest water
temperature, the boiler is silent for 3 minutes, or a boiler settings change
or the installer check (Diagnostics, **For the installer**) uses the connection to the boiler
(a start is refused while one runs). **Stop the test** ends it at any step.

**The E32 remembers the test** over restarts and firmware updates. The Boiler
page says for example "Last test: passed on 1 Nov 2026, 21:12." with the
highest water temperature the E32 asked during it; a test that was still
running when the E32 restarted shows as ended by the restart. **I have already
done this test** marks it as done without running it: the page then says
"Marked as done by you on 3 Nov 2026. This is your own mark, not a test the
E32 measured." **Undo my mark** takes it back, and running the test replaces
it. An E32 that has controlled this boiler before (for example since an
earlier release) shows "Not needed: the E32 has controlled this boiler
before." When the test passed, is marked or is not needed, its steps fold away
and **Run the test anyway** stays available. While the test needs you (running,
before the takeover, after a safety stop), **Active control** on the Rooms page
says so in one line with a link to it. Home
Assistant shows it as attributes of the sensor *Ready for E32 control*
(`boiler_test`, `boiler_test_summary`, `boiler_test_at`, `boiler_test_flow_c`,
`boiler_test_marked_at`, `boiler_test_steps`, `boiler_test_step`,
`boiler_test_reason`). The test is optional: **Skip the test and confirm the
takeover now** does the same takeover without it. Starting the test during a trial
run asks first, because it ends the trial run; a start the E32 refuses leaves the
trial run as it was.

This is the only boiler test: the attended heating test of the
Boiler page is retired. What stays, since 1.2.0 under **System → Diagnostics and
system log → For the installer**, never asks the boiler for heat: the zero-only
check, reading the heating settings and a device identity, and the measurement
report.

### What the trial run does and does not do

The trial run is optional. **The E32 does:**

- measure every room and follow each room's week program, manual changes,
  the house mode (away, holiday) and open-window pauses;
- calculate whether the house needs heat and at what water temperature, and
  show that as the **calculated boiler request**;
- learn how fast each room warms up (shown as advice only);
- compare its decisions with your current thermostat where that thermostat
  talks to the boiler over EMS (on the E32 **Rooms** page and in Home
  Assistant);
- set your setting devices (valves, tado) to the room's temperature
  through Home Assistant.

**The E32 does not, until you confirm the takeover:**

- send any heat request to the boiler. Your existing thermostat keeps
  controlling the boiler. The Overview says **Your thermostat controls the
  boiler** and, under **How this works**, that this is a trial run;
- change any boiler setting;
- learn from how your boiler answers its requests (its ceiling and rest, see
  [Listening to the boiler](USER-GUIDE-REFERENCE.md#listening-to-the-boiler)); the
  boiler's response says **E32 not controlling the boiler** until the takeover;
- drive radiator valves. A room's **Radiator valve control** switch is off by default,
  and even when it is on, valves are only driven while the E32 controls the
  boiler itself.

**Watch out: setting devices are real devices.** Home Assistant really sets
them, also during the trial run:

- A **radiator valve** chosen as setting device opens and closes by its own
  logic towards the room's temperature, so that radiator follows the week
  program. On a room that is **On** such a valve often closes before the room
  is warm, because it regulates on its own sensor; consider valve control with
  a separate thermometer instead.
- A **thermostat that controls your boiler** (for example a tado) chosen as
  setting device gets the room's temperature, so the week program now
  decides, through that thermostat, when the boiler heats.

That is usually what you want, but it means your heating can change on the
day you set it up. If you only want to watch during the trial run first, leave the
setting device empty and add it later.

The firmware can control the boiler, but it never starts on its own. The E32
takes over only after you confirm it (with an existing thermostat on the
boiler: after you disconnected it): in the boiler test (step 2), or with **Let
the E32 control the boiler** (after an old thermostat: **My thermostat is
disconnected from the boiler — let the E32 take over**) in the **Active
control** section of the **Rooms** page. Do that with someone at the boiler;
the switch-over procedure has the details and the hand-back.
Until then, an existing thermostat stays connected and in control.

### An EMS+ boiler: the attended test with the thermostat disconnected

An EMS+ boiler is read, and the E32 runs a trial run beside your thermostat,
but it does not control the boiler. The boiler test above does not run on an
EMS+ boiler, and there is no takeover for it until its model is verified. Keep
your thermostat connected and in control.

Testers who want to help can run one **attended test** instead. It is the only
moment the thermostat is disconnected from an EMS+ boiler. The steps are in the
[user guide](USER-GUIDE.md#b-the-attended-test-only-if-you-want-to-help); the
details in the
[reference](USER-GUIDE-REFERENCE.md#the-attended-test). In short:

> **Warning.** During the test the E32 asks your boiler for heat, at a low
> water temperature, for at most 10 minutes. Stay at the boiler for the whole
> test, about 20 minutes. If anything looks wrong, switch the boiler off with
> its main switch: heating stops at once.

1. Photograph and label the thermostat's wires at the boiler.
2. Switch the boiler off, disconnect the thermostat, switch the boiler on.
3. Wait 10 minutes: the E32 starts the test only after 10 minutes without
   another thermostat on the bus.
4. On the E32, open **Boiler**, block **Test your EMS+ boiler** (under **My
   boiler**). Tick **The thermostat is disconnected** and choose **Start the
   test**. Choose **I am at the boiler** within 60 seconds.
5. Watch the boiler, with the E32 page open and signed in: the block shows each
   step, its countdown and what the boiler shows. **Stop the test** ends it at
   any moment. The E32 ends the test by itself, always with three requests for
   no heat; at any doubt it does so at once, and also when your sign-in ends.

**Put the thermostat back** as soon as the test has ended, also when it
stopped early:

1. Switch the boiler off.
2. Reconnect the thermostat's two labelled wires, as in the photo.
3. Switch the boiler on. Within a few minutes the thermostat asks for heat
   again. Check hot water, the water pressure and the boiler display.

The E32 goes back to its trial run by itself. The block says **Last test** and the result. A passed test makes **My
boiler** say **Tested by you: the result waits for review** until the E32
restarts; the E32 still does not control the boiler. Share the result as the
[user guide](USER-GUIDE.md#c-share-your-result) describes.

<a id="9-updates"></a>

## 13. Updates

Updates keep your network settings, rooms, programs and paired sensors.
**Never use the factory image (`e32v2-factory.bin`) for an update**; it
erases everything.

### 13.1 Update order

When a new release pair comes out, read its release notes first. They say
which integration goes with which firmware. Usually: **update the integration
first, then the firmware.**

**The usual order,** for every release:

1. Update OpenThermostat in the Marketplace (**Settings → Updates**) and restart
   Home Assistant ([13.2](#132-update-the-integration)). The integration comes
   first.
2. Install the E32 firmware from the **Firmware** update entity
   ([13.3](#133-update-the-e32-firmware-from-home-assistant-recommended)), while
   someone is home.
3. The takeover stays. Since E32 1.4.6 a firmware update keeps it while the
   boiler and the way the E32 talks to it are unchanged; the E32 resumes about
   two minutes after its restart, as after any restart. Only when something
   changed (another boiler, another way to talk to it, a boiler it could not
   check, or a firmware with new takeover rules) does the E32 ask again, and
   until you confirm it keeps only frost protection. Home Assistant then shows a
   repair that says why (Settings → System → Repairs): choose **Fix**, or confirm
   on the E32 **Boiler** page under **Boiler test and takeover**. Up to 1.4.5
   every firmware update asked again.

Every release has one block below, newest first. **Two or more releases behind?**
Updating straight from an older version works: read every block from your
version up to the new one and do the [install check](INSTALL-CHECK.md)
afterwards. The changes add up, and the order is the same each time. Releases
are tested one step at a time, from one version to the next.

| You have | Next release | Read |
| --- | --- | --- |
| 1.4.5 | 1.4.6 | From 1.4.5 to 1.4.6 |
| 1.4.4 | 1.4.5 | From 1.4.4 to 1.4.5 |
| 1.4.3 | 1.4.4 | From 1.4.3 to 1.4.4 |
| 1.4.2 | 1.4.3 | From 1.4.2 to 1.4.3 |
| 1.4.1 | 1.4.2 | From 1.4.1 to 1.4.2 |
| 1.4.0 | 1.4.1 | From 1.4.0 to 1.4.1 |
| 1.3.0 | 1.4.0 | From 1.3.0 to 1.4.0 |
| 1.2.0 | 1.3.0 | From 1.2.0 to 1.3.0 |
| 1.1.0 | 1.2.0 | From 1.1.0 to 1.2.0 |
| 1.0.0 | 1.1.0 | From 1.0.0 to 1.1.0 |

**From 1.4.5 to 1.4.6** (Home Assistant integration 1.4.6). Update in the usual
order (above): the integration first, then the firmware. You do not confirm the
takeover again.

What the update changes in an existing installation:

- **The takeover is kept.** E32 1.4.6 keeps the confirmation that 1.4.5 stored,
  checks that the boiler is the one 1.4.5 knew, and stores it from then on with
  the boiler and the way the E32 talks to it. The E32 controls the boiler again
  about two minutes after the update, as after any restart; nothing is asked.
  It asks again only when the boiler is another one, the E32 cannot identify it
  within 15 minutes, the boiler talks EMS+, or the stored confirmation cannot be
  read; Home Assistant then shows a repair that says why.
- **Smart warm-up moves more slowly.** After an early or late morning the next
  start moves by at most 15 minutes. If an earlier release had moved a room's
  start more than an hour away from the E32's own estimate, the first judged
  morning brings it back inside that hour at once. What it learned is kept.
- **"Learned" means more.** A room's warm-up timing counts as learned only when
  four of its last five usable mornings were within a quarter of an hour. After
  the update every room collects usable mornings again, which takes about a
  week, and "Known about your home" can be lower until then. Until a room has
  learned how fast it warms, its start estimate stays capped (floor 3 hours,
  radiators 90 minutes). The correction factor stays between 0.7 and 1.5.
- **The Heating plan sensor** shows a few words (for example "Not planning
  (still learning)") instead of Unknown or Unavailable while nothing is to
  start; an automation that uses its time should check that the state is a
  time.
- **Home Assistant 1.4.6 with E32 1.4.5:** everything works; after an update of
  the firmware the E32 asks again as before, with the usual repair.
- **Home Assistant 1.4.5 with E32 1.4.6:** everything works; when the E32 asks
  again, the repair says "before its firmware was updated" whatever the reason.
- **Back to E32 1.4.5 (a firmware downgrade):** 1.4.5 asks for the takeover
  again, as every firmware change did up to 1.4.5. Confirm it there; updating to
  1.4.6 again then keeps that confirmation.

**From 1.4.4 to 1.4.5** (Home Assistant integration 1.4.5), while someone is
home. Both the integration and the E32 firmware change. Update in the usual
order (above): the integration first, then the firmware, then confirm the
takeover again. No reload is needed.

What the update changes in an existing installation:

- **Settings, rooms, programs, sensors, valves and what the E32 learned are
  kept.** Nothing of the integration is removed or renamed.
- **While a boost runs,** the E32 Overview says "Set replaces the boost, until
  22:30": choosing **Set** ends the boost and takes your temperature.
- **The E32's Home page shows House and boiler in the words and figures of the
  Learning tab in Home Assistant:** the learned water line, the highest water,
  and where the boiler burns steadily and starts heating.
- **A room with many valves no longer drops out of Home Assistant.** When its
  valve details are too big to send, the E32 leaves the least important ones
  out, and **Diagnostics** says "shortened" beside the room. A valve whose
  message becomes too large to read says so within minutes, not after two hours.
- **The scoreboard and the hot-water days survive a restart in houses with seven
  or eight rooms,** and the room plan takes less settings memory.
- **The hot water flow is on the Boiler tab** when your boiler measures it:
  **Tapping now** with the flow, or **No tapping**, under **Hot water**. The
  *Hot water flow* sensor is no longer under Diagnostic.
- **Connect E32** (a step of the Home Assistant integration, not of the
  firmware) removes the old "OpenThermostat 1.0.0" MQTT entities that the
  previous firmware left under the E32's former MQTT base. A house linked
  before 1.4.5 keeps them until you delete that MQTT device by hand
  (**Settings → Devices & services → MQTT**).
- **E32 Settings** explains that the MQTT broker alone sends nothing until you
  use **Connect E32** in Home Assistant. The E32 V2 firmware no longer carries
  the old room scheduler from before the E32 room plan.
- **Home Assistant:** the room card keeps all five presets on a narrow phone
  (two rows), and "The E32 cannot be reached" says how things are now.
- **Home Assistant 1.4.4 with E32 1.4.5:** everything works; a room that lost
  details can show a blank battery or no "set to" line for a valve. The hot
  water flow tile and the "shortened" note need the integration 1.4.5.
- **Home Assistant 1.4.5 with E32 1.4.4:** everything works; no "shortened"
  note, and a very crowded room can still be missing.
- **Back to E32 1.4.4 (a firmware downgrade):** nothing stored changes. On a
  seven- or eight-room E32 the scoreboard and the hot-water days are refused
  again, and the copies 1.4.5 wrote go stale.

**From 1.4.3 to 1.4.4** (Home Assistant integration 1.4.4), while someone is
home. Both the integration and the E32 firmware change this time.

Update in the usual order (above). Home Assistant sees the new abilities of the firmware at once. No reload is needed.

What the update changes in an existing installation:

- **Settings, rooms, programs, sensors, valves and what the E32 learned are
  kept.** No entity is removed or renamed.
- **Radiator valves with a large Zigbee2MQTT message are read again.** A Sonoff
  TRV-ZBT sends about 2.3 KB; the E32 now reads messages up to 6 KB, so its
  battery, set temperature and mode show, and the valve watch works on it. A
  valve whose message is still too large (or cut off) says **Message too large
  to read** with its size instead of waiting for a report. Report it with the
  valve model.
- **What the E32 learned is kept in houses with seven or eight rooms.** Before,
  a full settings memory could keep the learned record from being saved, and a
  restart lost it. The Repair "could not store what it learned" should not come
  back. If it does, its figures are honest: the places that are free, the places
  the E32 keeps for its own settings (usually 155 now) and the places what it
  learned needs; what it learned needs more than the free places beyond those
  it keeps, and the E32 tries again at the next save.
- **Learn again:** one button per room and one for the house, on the E32 pages
  and in Home Assistant (the room's screen, **Heating and boiler**, and the
  **Learning** tab).
- **Dashboard:** **Diagnostics** fills the screen and lists every radiator valve;
  **Heat along only** rooms show how often they reached their temperature; a
  setting device that reports only a range shows its temperature on the room
  card (issue #16). See the [user guide](USER-GUIDE.md#13-let-the-e32-learn).
- **Stop boost** on the E32 Overview, also for a room without a week program.
  The Rooms page now says "temperature without a week program" in its help.

Mixed versions:

- **Home Assistant 1.4.4 with E32 1.4.3:** everything works as before; the
  Learn again buttons are missing (the E32 does not offer it), and a TRV-ZBT
  stays unknown, as in 1.4.3.
- **Home Assistant 1.4.3 with E32 1.4.4:** the valves are read and show their
  battery and set temperature; the Learn again buttons are missing in Home
  Assistant (the E32's own pages have them), and a valve with a message that is
  too large looks like an unknown one on the room card.
- **Back to E32 1.4.3 (a firmware downgrade):** nothing stored changes; the
  TRV-ZBT valves go back to unknown, and the learned record stays readable.

**From 1.4.2 to 1.4.3** (Home Assistant integration 1.4.3), while someone is
home. The update is small: the dashboard changes most; the E32 firmware only gets
one fix.

Update in the usual order (above). No reload is needed.

What the update changes in an existing installation:

- **Settings, rooms, programs, sensors, valves and what the E32 learned are
  kept.** No entity is removed or renamed.
- **Every tab of the dashboard uses the whole width of your screen,** like the
  Overview.
- **Rooms:** one card per room with the program of today, the last 24 hours and
  the devices of the room, and the presets and the room's state on the card.
- **Learning:** the tab was called "Learning and settings"; it is now **Learning**
  and holds everything the E32 learns, per room in figures. A fact the E32 does
  not know yet says what it still needs.
- **Radiator valves:** what the E32 found on each valve (put back, own program,
  switched off by you, not responding) shows on the room card. With E32 1.4.2
  this appears as soon as the E32 reports it.
- **With E32 1.4.2 still installed,** Home Assistant 1.4.3 works as before; only
  the House page fix needs the 1.4.3 firmware.

**From 1.4.1 to 1.4.2** (Home Assistant integration 1.4.2), while someone is
home.

Update in the usual order (above). Home Assistant sees the new abilities of the firmware at once. No reload is needed.

What the update changes in an existing installation:

- **Settings, rooms, programs, sensors, valves and what the E32 learned are
  kept.**
- **A temperature never changes the state of a room.** A change on a thermostat
  or setting device lasts until the next switch time with a week program (no
  24-hour limit) and becomes the room's temperature without a week program
  without one. The setting **Length of a manual change** is gone. An override set
  by 1.4.1 during Away ends at the first step after the update.
- **A setting device works both ways,** also without a week program. A radiator
  valve that was also a room's setting device lost its Valve control once, with
  a Repairs item per room; save the room to clear it.
- **Each room has its own Recipients,** and every room keeps the people it had.
  A battery that is already low sends one new message naming the device.
- **The old MQTT route.** An E32 that uses MQTT without the
  Home Assistant integration now sends nothing over MQTT and no longer announces
  the old "OpenThermostat 1.0.0" device. If Home Assistant still lists that old
  device, delete it by hand (Settings → Devices & services → MQTT → the device →
  Delete). From 1.4.5 the integration's **Connect E32** clears it for you when it
  links an E32 that still had that older MQTT base (Home Assistant does this,
  not the firmware).
- **Length of a manual change is gone.** The option disappears from Configure
  and the panel by itself; no reload is needed.
- **Hot water with a tank:** once the E32 has reported a tank for a full day,
  the sensors Keeping warm today, Tapping gas and Keeping-warm gas are removed
  and Charges today is added.
- **Fewer Repairs items:** only faults remain. "Ready to plan the heating" is
  a house message and a button under Today's plan on the Learning tab; a room
  that stays cold and a burner that keeps cycling are advice there. "Boiler status bits (raw)" was switched off
  once; switch it on again under the entity's settings if you use it.
- **Nothing stays "Unavailable" after an update,** also when Home Assistant
  restarts while the E32 is off.
- **With E32 1.4.1 again** (a firmware downgrade): a change "until the next
  switch time" lasts at most 24 hours, a hot water tank's taps are not
  counted, and what the 1.4.2 firmware stored for its hot water day is ignored.

**From 1.4.0 to 1.4.1** (Home Assistant integration 1.4.1), while someone is
home.

Update in the usual order (above). The integration must come first: the new Settings screens need it.

What the update changes in an existing installation:

- **Settings, rooms, programs, sensors, valves and what the E32 learned are
  kept.** Nothing changes in how the heating runs until you choose Summer.
- **The Settings tab looks calmer and holds everything.** Every room has one
  screen with all its settings, including the week program with its reset times
  drawn on the day bars; boiler settings, pairing a Bluetooth sensor, the search
  for valves at a BLU Gateway, the two notification questions and Maintenance
  (restore a backup, tidy entity IDs, old rooms) are there too. **Configure** has
  two items: **Open the settings page** and **E32 connection**.
- **The Week program tab is gone** from the dashboard: the program is on the
  room's screen (**Settings → Rooms**, the room); every link that led to the tab
  now opens that screen.
- **Summer mode** is a fifth house mode (needs E32 firmware 1.4.1): the heating
  stays off until you switch it off; hot water and frost protection stay. A
  banner on every dashboard tab says so, and once a week the E32 exercises the
  floor valves and pumps for a minute. After five warm days Home Assistant asks
  once whether to switch it on. Switch summer mode off before you go back to an
  older firmware.
- **The dashboard cards look like the Settings tab:** each room shows its state
  as a coloured label and one line for what it does now, and the house card
  shows the house mode large.
- **Nothing stays "Unavailable" after an update:** yesterday's figures,
  Bluetooth readings and other sensors that exist stay and say Unknown when the
  E32 has nothing to report; after a restart of the E32 yesterday's burner
  starts per heating hour, heating hours, short burner runs and each room's
  "above target" are kept.
- **To go back to 1.4.0,** switch summer mode off first. The integration 1.4.0
  has the earlier Settings tab; Configure has three items again.

**From 1.3.0 to 1.4.0** (Home Assistant integration 1.4.0), while someone is
home.

Update in the usual order (above). The integration must come first: the Settings tab, reset times and Smart warm-up per room need it.

What the update changes in an existing installation:

- **Settings, rooms, programs, sensors, valves and what the E32 learned are
  kept.** Every room starts with Smart warm-up **As the house** and without reset
  times, so the heating does what it did on 1.3.0 until you change that.
- **The dashboard has a last tab, Settings,** with every setting of the
  installation. While the dashboard is shown, **Configure** has three items:
  **Open the settings page**, **E32 connection** and **Advanced and
  diagnostics**. Without the dashboard, Configure stays as it was.
- **Fewer Repairs.** Notices that named no fault go by themselves at the first
  start: a room with one temperature source, a room group that came back, the
  renewed boiler counters and room estimates, and "Give your rooms a week
  program".
- **The E32 device gets the sensor Errors** once E32 1.4.0 runs: the error
  lines in the E32's system log since the last restart, with the last one.
- **A room that is Off shows its temperature** on the E32 and in Home
  Assistant.
- **A weather forecast you chose** under **Energy and outdoor temperature** now
  reaches the E32.
- **Going back to 1.3.0 is safe.** The E32 1.3.0 ignores reset times and a room's
  own Smart warm-up: every room follows the house's Smart warm-up again, and the
  reset times are lost. The integration 1.3.0 has no Settings tab; Configure has
  all its items again.

**From 1.2.0 to 1.3.0** (Home Assistant integration 1.3.0), while someone is
home.

Update in the usual order (above). The integration must come first: the E32 devices menu, Heat along only and the automatic lowest water temperature need it.

What the update changes in an existing installation:

- **Settings, rooms, programs, sensors, valves and what the E32 learned are
  kept.** The E32 starts to learn the steady water temperature downwards: once a
  day it tries one step lower water for half an hour. **Home → What the E32 has
  learned** tells what was tried.
- **The lowest water temperature is automatic only if it was 30 °C.** A value
  you set yourself stays set by you. To let the E32 decide, tick **Lowest water
  temperature: automatic** under **Home → Water temperature limits** (or in Home
  Assistant on the dashboard's **Settings → Heating and boiler → Water temperature
  limits**).
- **Every heating setting stays adjustable on the E32** while Home Assistant is
  linked; a change on either side reaches the other.
- **The status light stays off** until you choose the name printed on your board
  under **System → Settings → Advanced**.
- **The devices have one page:** Bluetooth sensors, Shelly devices and the
  devices heard on the boiler bus are under **System → Devices** on the E32 and
  on the dashboard's **Settings → Devices** in Home Assistant (without the
  dashboard: **Configure → E32 devices**). Nothing has to be added
  again.
- **Going back to 1.2.0 is safe.** It learns the steady water temperature again
  from the start, and a room set to **Heat along only** is Off there.

**From 1.1.0 to 1.2.0** (Home Assistant integration 1.2.0), while someone is
home.

Update in the usual order (above). The integration must come first: the new devices, the notifications and the room models need it.

What the update changes in an existing installation:

- **What the E32 learned is kept**, and so are settings, rooms, programs,
  sensors and valves. The first start after the update shows no earlier details
  under **Last restart**. The E32 starts to learn the steady water temperature of
  your boiler as soon as it sees the boiler switch itself on and off inside one
  request, and the room models start collecting readings and say how far they
  are (for example "2 of 3 days good"). Until the models have predicted well for
  days, nothing in the heating changes because of them.
- **Home Assistant gets new devices.** The boiler's values move to a device named
  after the model you chose (for example "Nefit EcomLine HRC 22", otherwise
  "Boiler"); a thermostat the E32 hears on the bus is "Thermostat on the boiler
  bus"; the rest stays on "OpenThermostat E32". Entity IDs and history stay. The
  seven "Old: ..." energy counters are gone; their history stays. A name you gave
  a device yourself stays.
- **Notifications are off** until you switch them on under the dashboard's
  **Settings → Notifications** (without the dashboard: **Configure →
  Notifications**).
- **The E32 plans the heating only after you confirm once.** It watches first
  (the Home page shows "If the E32 planned the heating: ..."). After at least a week of good
  predictions it asks (Settings → Repairs, the button on the E32 device, or the
  Home page). Nothing changes until you confirm.
- **Going back to 1.1.0 is safe.** It skips the new learned data. A backup made
  on 1.2.0 and restored on 1.1.0 leaves out only the learned part.

**From 1.0.0 to 1.1.0** (Home Assistant integration 1.1.0): update in the
usual order (above). Every window or door contact you chose before is a window: move a door to **Door
contacts** in the room form, section **Windows and doors**. The options that came
with 1.1.0 (boiler settings, the EMS+ tester, Shelly devices) stay off until you
choose them. Settings, rooms, programs and paired sensors are kept.

### 13.2 Update the integration

**With the Marketplace:** **Settings → Updates** shows the new OpenThermostat
version. Select it, **Install**, then restart Home Assistant. A stable release
shows up there by itself. On Home Assistant 2026.10 and older, HACS does this;
if it has not shown a new version yet, choose **Update information** in the
**OpenThermostat** menu of the HACS list (section 9.1 explains why).

**Without the Marketplace:**

1. Download the new `OpenThermostat-HA-<version>.zip` from the releases page.
2. Delete the old `custom_components/open_thermostat` folder in your Home
   Assistant configuration folder and copy the new one in its place.
3. Restart Home Assistant.

Keep your existing OpenThermostat entry; there is no need to remove and add
it again. If you copied blueprints, copy them again.

### 13.3 Update the E32 firmware from Home Assistant (recommended)

1. The OpenThermostat device has an update entity called **Firmware**. Home
   Assistant checks GitHub for a new version every 6 hours.
2. A new version appears under **Settings → Updates**.
   Choose it and choose **Install**.
3. Home Assistant downloads `firmware.bin`, checks its checksum, size and
   version, uploads it to the E32 and waits until the E32 reports the new
   version. Keep the E32 powered.

### 13.4 Update the E32 firmware without Home Assistant

On the E32, open **System → Firmware update**:

- **Check for updates** lets the E32 look for a new release itself; then
  choose **Download and install**.
- **Recovery (advanced)**: download `firmware.bin` from the release
  (**Look up latest release on GitHub** helps you find it and check it),
  choose it with **Choose firmware file...** and choose **Upload firmware**.

### 13.5 Automatic rollback

A new firmware confirms itself after it has run normally for about a minute
and the network has worked. If it fails to start, or gets no working network
connection within 10 minutes (router, MQTT broker or the web page answering),
the E32 goes back to the previous version by itself.

## 14. Backup and restore

Make a backup once your setup works, and again after big changes. It saves
your network and time settings, MQTT and the Home Assistant link, rooms and
week programs, planned holidays, Bluetooth sensors, flow settings, boiler model
and language.

### 14.1 Make a backup

1. On the E32, open **System → Backup and restore**.
2. Optionally tick **Include passwords and Bluetooth keys, encrypted with a
   passphrase** and enter a **Passphrase** (12 to 64 characters) twice. Without
   it the file holds no secrets, and the page lists what you would need to
   enter again after a restore (the MQTT password and the Bluetooth sensor
   keys).
3. Choose **Download backup** and keep the file somewhere safe. Keep the
   passphrase too: nobody can recover it.

The Wi-Fi password and the E32 web password are never in a backup. The
encrypted passwords are tied to the network settings in the same file: a
backup whose broker address was edited does not open them. (Backups made
by older firmware still restore; the E32 says they are older. Make a new one
afterwards.)

### 14.2 Restore a backup

Use this on a new or reset E32, or to undo a change.

1. First connect the E32 to your network (section 3) and sign in.
2. Open **System → Backup and restore**, section **Restore a backup**.
   Choose the **Backup file**, enter the **Passphrase of this backup** if it
   has one, and choose **Check backup**.
3. The E32 shows what will change, what it skips and what you need to enter
   again. Nothing is saved yet.
4. Choose **Restore these settings**. If network or Bluetooth settings change,
   the E32 restarts about 10 seconds later; sign in again afterwards.
5. If the backup had no passphrase, enter the MQTT password again under
   **System → Settings → Home Assistant**. *Why:* MQTT stays off until you do, so Home Assistant
   receives nothing.

A restore never changes the Wi-Fi network or the web page port. The rooms keep
the mode of the backup (active control stays active), but the takeover is not
part of a backup: a new or reset E32 sends nothing to the boiler until you
confirm the takeover on its Rooms page again. It is refused while a boiler test
runs.

Home Assistant's own backup (Settings → System → Backups) covers the
integration's settings in Home Assistant, including the copied
`custom_components` folder.

## 15. Secure your setup

The E32 sits on your home network, so its protection is your network's. A few
steps make a big difference.

1. **Your own E32 password.** Choose it at the first sign-in (section 4); the
   E32 accepts no change until you do. Use one you do not use elsewhere.
2. **One MQTT user per client, and a broker ACL.** Give Home Assistant, the
   E32 and Zigbee2MQTT each their own broker login (section 8.2), and let each
   write only its own topics: the E32 publishes under `<base>/fw/`, Home
   Assistant under `<base>/ha/`, and only Zigbee2MQTT publishes the states
   under `zigbee2mqtt/` (the others only send commands to
   `zigbee2mqtt/<device>/set`). `<base>` is the **Base** of section 8.3
   (`openthermostat` on a new E32). With the Mosquitto add-on, turn on
   **customize** in its configuration (`active: true`, `folder: mosquitto`),
   and put two files in Home Assistant's `/share/mosquitto/`. First
   `accesscontrollist`, the rules:

   ```text
   # Home Assistant: reads everything; writes its own E32 topics, discovery
   # and Zigbee2MQTT commands.
   user homeassistant
   topic read #
   topic write openthermostat/ha/#
   topic readwrite homeassistant/#
   topic write zigbee2mqtt/+/set

   # The E32: reads Home Assistant's messages, writes its own topics,
   # its discovery and the radiator valve commands.
   user e32
   topic read openthermostat/#
   topic write openthermostat/fw/#
   topic readwrite homeassistant/#
   topic read zigbee2mqtt/#
   topic write zigbee2mqtt/+/set

   # Zigbee2MQTT: its own tree and its discovery.
   user zigbee2mqtt
   topic readwrite zigbee2mqtt/#
   topic readwrite homeassistant/#
   ```

   Then `acl.conf`, which turns them on:

   ```text
   acl_file /share/mosquitto/accesscontrollist
   ```

   Use the user names you created, restart the add-on and check that Home
   Assistant, the E32 (System → Diagnostics, console command `mqtt`) and
   Zigbee2MQTT still connect. Replace `openthermostat` if your Base differs.
3. **Broker TLS (optional).** Home Assistant and Zigbee2MQTT can reach the
   broker over TLS (usually port 8883). The E32 itself connects without TLS on
   port 1883 for now; keep that port reachable only from your home network,
   never from the internet.
4. **The setup network.** The setup Wi-Fi `OpenThermostat-xxxxxx` uses the
   password `openthermostat` for every E32. It only opens on a new E32 without
   Wi-Fi settings, or after the `setup` command over USB, and closes itself
   after about 15 minutes. Finish the setup in one go, and do not leave a
   new E32 powered and unconfigured where others can reach it.

Not yet available, planned for a later release: a setup Wi-Fi password of
its own per E32, encrypted settings storage on the E32 and secure boot.

<a id="10-forgotten-password-and-wi-fi-recovery-over-usb"></a>
<a id="15-forgotten-password-and-wi-fi-recovery-over-usb"></a>

## 16. Forgotten password and Wi-Fi recovery over USB

Two commands work over the USB cable. They need physical access to the E32,
so nobody can use them over the network.

1. Connect the E32 to a computer with a USB-C data cable.
2. Open a serial terminal at **115200 baud** that sends a line ending when you
   press Enter, for example the Arduino IDE Serial Monitor, PuTTY, or
   `python -m serial.tools.miniterm PORT 115200` (from the `pyserial`
   package).
3. Type one of these commands and press Enter:
   - **`password-reset`** sets the web password back to `admin`. Sign in with
     `admin` / `admin`; the page asks for a new password at once. Home
     Assistant then asks for the new password.
   - **`setup`** restarts the E32 into the setup network
     `OpenThermostat-xxxxxx` for 15 minutes, also when a Wi-Fi network is
     saved or the E32 uses Ethernet. Use it after a router or Wi-Fi password
     change. The old network settings stay until a new connection works.

While the E32 still works on your network, you can also change Wi-Fi from
**System → Settings → Network → Start WiFi setup (restart)**.

<a id="16-troubleshooting"></a>

## 17. Troubleshooting

### The E32 is not reachable

- Make sure your phone or computer is on the same home network as the E32.
- Look up the E32's address in your router (its name starts with
  `openthermostat-`), or try `http://openthermostat-xxxxxx.local/`.
- Wi-Fi must be 2.4 GHz. If the Wi-Fi name or password changed, use the USB
  `setup` command ([section 16](#16-forgotten-password-and-wi-fi-recovery-over-usb)).
- In Ethernet mode, check the cable and the router; the setup network does not
  open by itself.
- Never set up yet? Look for the `OpenThermostat-xxxxxx` network and open
  `http://10.10.10.1/`.

### I cannot sign in on the E32

- The user name is always `admin`. Forgot the password? Use `password-reset`
  over USB (section 16).
- "Four saved web sessions occupy all sign-in slots": the E32 remembers up to
  four signed-in browsers. Tick **End previous web sessions and sign in** and
  enter your password again. A sign-in ends by itself after 30 minutes
  without use, after seven days, or when the E32 restarts.

### Connect E32 does not work

The form says what is wrong. The most common messages:

- *Enter the local E32 web address*: include `http://` and use an IP address
  or a home-network name; no paths or login details.
- *The E32 did not accept this password*: use the E32 web password (user
  `admin`), not your Home Assistant or MQTT password.
- *The E32 could not be reached*: check the address in a browser on the same
  network as Home Assistant.
- *The E32 needs its own MQTT login first*: MQTT is off on the E32, or has no
  user name or password. Complete [section 8.3](#83-mqtt-settings-on-the-e32)
  and let the E32 restart.
- *Home Assistant received nothing from it over MQTT within 90 seconds*: the
  E32 and Home Assistant do not use the same broker, or the broker refused
  the E32's login. Compare **System → Settings → Home Assistant** on the E32 with Home
  Assistant's MQTT integration, check the E32's **System → Diagnostics and system log**, and
  try again.
- *This integration needs Home Assistant 2026.10.0 or newer*: update Home
  Assistant.
- *The E32 is updating or restarting, or it waits for a restart*: wait a
  minute until its web page opens normally and try again.
- *This E32 is already linked to another OpenThermostat installation*: the E32
  is still linked to another OpenThermostat entry in Home Assistant (for
  example an old one). Remove the old entry, or connect from the entry it is
  linked to.
- *The E32 has too many open sign-ins*: sign out on the E32 web page, or sign
  in there with **End previous web sessions and sign in**, then try again.
- *The firmware on this E32 is too old for this version of the integration*:
  update the E32 first (**System → Firmware update**), then connect.

### No values in Home Assistant

All live values come over MQTT.

1. In Home Assistant, check that the MQTT integration is set up and connected.
2. On the E32, check **System → Settings → Home Assistant**: **Connect to the MQTT broker** ticked, the right
   broker address and port, and a user name and password the broker accepts.
   Save and restart after a change. **System → Diagnostics and system log** shows connection
   errors.
3. The **Base** on the E32 (System → Settings → Home Assistant → Advanced) and the controller
   MQTT prefix of the integration must match. Connect E32 sets this up; if you
   changed either by hand, run **Configure → E32 connection** again.
4. Check that the firmware and integration versions are a pair from the same
   release notes. An older integration does not understand newer firmware, and
   the other way round.

Values become unavailable only when the E32 reports itself offline or about 3
minutes pass without its heartbeat. The **Heating problem** sensor turns on
when the E32 has sent nothing for 10 minutes.

### The link between Home Assistant and the E32 does not come back

The E32 and Home Assistant keep a running session over MQTT. It restarts by
itself after a restart of Home Assistant, the broker or the E32, or after a
Wi-Fi outage. The E32 **Overview** shows its state: **Home Assistant:
connected**, or "last connected ... ago".

If it stays disconnected for more than a few minutes:

1. Check MQTT as in [No values in Home Assistant](#no-values-in-home-assistant).
2. If the E32 changed its password, Home Assistant shows a **Re-authenticate**
   prompt on the integration. Enter the new E32 password there.
3. If Home Assistant's clock jumped, a repair message "Room measurements
   paused: the clock of Home Assistant jumped" appears. Check the time of the
   Home Assistant host, then reload the integration (**Settings → Devices &
   services → OpenThermostat → ⋮ → Reload**).
4. Otherwise reload the integration, or run **Configure → E32 connection** again
   with the same address and password. Your rooms on the E32 stay as they
   are.

The E32 keeps running its rooms and week programs while the link is down.

### Boiler values are missing

The E32 learns which values your boiler really reports and Home Assistant only
creates entities for those. This keeps Home Assistant free of empty sensors,
but it can look as if something is missing.

- On the E32, open **Boiler → What your boiler reports**. It lists:
  - **Values available**: what your boiler reports;
  - **Not fitted on this boiler**: the boiler always answers "no sensor" for
    these, for example a water pressure sensor it does not have;
  - **Not reported (yet)**: messages that only come in certain situations, or
    only when another controller asks for them.
- A value that appears later is added automatically.
- If you know your boiler has a value that is listed as not fitted, choose
  **Show anyway** next to it.
- In Home Assistant, values the boiler never reported are created disabled.
  You can enable them on the device page.
- No boiler values at all? Check that **Boiler bus (EMS) on** is ticked
  (section 5) and that the Boiler page does not say "Listening to the boiler bus (EMS) is off.".

### A room shows no measurement

- **"Backup sensor in use"**: the room's first source stopped reporting and
  its second source (backup sensor) measures the room. Nothing is wrong with
  the heating; check the first sensor.
- **"Sensor silent: last reading used"**: none of the room's sources delivered
  a fresh reading. The room keeps its last value for 30 minutes.
- **"No reading: this room does not ask for heat"**: still no reading after
  30 minutes; the room stops asking for heat.

A Bluetooth reading is valid for 15 minutes, so the sensor must be heard at
least that often. A Home Assistant source needs Home Assistant and MQTT
running and must report a temperature in °C or °F. Adding a second source
keeps the room measured when one drops out.

### A Bluetooth sensor is not found or stays "Waiting"

- Bring it closer to the E32 and check its battery. **Search nearby** lists
  only the 32 strongest devices.
- Check the profile and the key: an encrypted sensor needs its key; a pvvx
  thermometer must advertise in BTHome v2 or PVVX Custom format.
- After saving, wait for the automatic restart (about 30 seconds).
- At most eight sensors can be paired.

### Heating needs attention

**Settings → System → Repairs** shows **Heating needs attention** and the
**Heating problem** sensor is on. The message says what is wrong, for example
a room without a usable measurement for 30 minutes, no report from the E32
for 10 minutes, a room that asks for heat but stays more than 0.5 °C below its
target for 3 hours, or no working link with the E32 for 15 minutes while the
E32 is online. The message clears itself once the cause is gone.

### The setting device changes the temperature by itself

The device runs its own schedule. Put it in manual mode (in its own app or
on the device). Home Assistant shows a repair message "{device} seems to run
its own schedule" when it notices this.

### Remove an old Home Assistant room

Installations set up with integration 0.4.0b10 or older had to create a room
in Home Assistant before the E32 could connect. That room is no longer used:
your rooms live on the E32 now. Home Assistant offers to remove it:

1. Go to **Settings → System → Repairs**.
2. Open **Old Home Assistant room no longer used** and follow the steps. The
   same is available on the dashboard's **Settings → Installation → Remove old
   Home Assistant rooms** (without the dashboard: **Configure → Advanced and
   diagnostics → Remove old Home Assistant rooms**).
3. Home Assistant updates the E32 room plan first and then removes the old
   room's devices and entities. Your own sensors, thermostats and valves stay
   as they are, and so do the rooms on the E32. The E32 may restart once
   (about 30 seconds).

If an E32 room used the old room's thermostat as its only temperature source,
a repair **Choose a temperature source for ...** asks you to pick a new one.

### An update was rolled back

The E32 shows the previous version after an update when the new firmware did
not start properly or did not reach the network within 10 minutes. Check
that the router and the MQTT broker were available, then try again.
**System → Firmware update → Recovery (advanced) → Update diagnostics** and the system log show
what happened. If Home Assistant says the E32 did not report the new version
in time, check the version on the E32 itself before trying again. A failed
installation from Home Assistant now says in words where it stopped
(downloading, checking the file, sending it to the E32, or the E32 not
confirming the new version).

### Something else

The [user guide](USER-GUIDE.md) takes you through the setup, and its
[reference](USER-GUIDE-REFERENCE.md) explains every setting. For a return to the
original firmware, see [USB backup and recovery](FLASHING.md). When you
report a problem on GitHub, include the firmware and integration versions,
the relevant part of the E32 system log and, if you can, Home Assistant's
**Download diagnostics** file of the integration (it leaves out passwords,
keys, addresses and Wi-Fi names). Remove any passwords from logs before you
share them.
