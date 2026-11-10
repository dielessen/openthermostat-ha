"""Configure → Advanced and diagnostics → Tester program (track E5, boiler_share.py).

Off by default. "Tester program" first shows the switch with what it is in plain words. While it is on, the
same item opens a menu with the bus recording's state in one line ("Recording: 12 of 30 minutes, 1,234 messages")
and:

- "Start a bus recording (30 minutes)" (POST /ems/recording/start), or "Stop the bus recording" while it runs;
- "Share result": stops a running recording, reads what the E32 serves, writes the files under
  <config>/www/open_thermostat/ and shows the notification with the download links and the prefilled GitHub form
  (Home Assistant sends nothing itself);
- "Switch the tester program off".

The texts the menu builds itself are selector.tester_text (EN/NL); every request is one sign-in.
"""
from __future__ import annotations

from .boiler_share import STATE_KEY, async_share, async_status, save_tester, tester_on
from .const import DOMAIN

TEXTS = "tester_text"


class TesterSteps:
    """Mixin for the product options flow."""

    def _tester_monitor(self):
        return (self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id) or {}).get(STATE_KEY)

    def _tester_link(self):
        from .e32_system import link_for
        return link_for(self.hass, self.config_entry)

    async def async_step_tester(self, user_input=None):
        """The switch while off; the tester's menu while on."""
        import probatio as vol
        from homeassistant.helpers import selector
        if self._tester_link() is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        if tester_on(self.config_entry):
            return await self.async_step_tester_menu()
        if user_input is not None:
            if user_input.get("tester_enabled") is not True:
                return self.async_abort(reason="tester_unchanged")
            save_tester(self.hass, self.config_entry, True)
            texts = await self._tester_texts()
            self._menu_note = texts["switched_on"]
            return await self.async_step_tester_menu()
        return self.async_show_form(step_id="tester", data_schema=vol.Schema({
            vol.Required("tester_enabled", default=False): selector.BooleanSelector()}))

    async def _tester_texts(self):
        from .options_navigation import async_flow_texts
        return await async_flow_texts(self.hass, TEXTS)

    async def async_step_tester_menu(self, user_input=None):
        from .controller_link import ControllerLinkError
        from .e32_system import async_e32_call
        link = self._tester_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        if not tester_on(self.config_entry):
            return await self.async_step_tester()
        texts = await self._tester_texts()
        try:
            status = await async_e32_call(link, async_status, write=False)
        except ControllerLinkError:
            status = None
        monitor = self._tester_monitor()
        if monitor is not None:
            monitor.observe(status)
        state = (status or {}).get("state")
        options = (["tester_stop"] if state == "recording" else
                   [] if state in ("unavailable", "not_supported") else ["tester_start"]) + ["tester_share", "tester_off"]
        return self.async_show_menu(step_id="tester_menu", menu_options=options,
                                    description_placeholders={"recording": status_line(status, texts)})

    async def async_step_tester_start(self, user_input=None):
        return await self._tester_recording(True)

    async def async_step_tester_stop(self, user_input=None):
        return await self._tester_recording(False)

    async def _tester_recording(self, start):
        from .controller_link import ControllerLinkError
        from .e32_system import async_e32_call, failure
        link = self._tester_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        try:
            status = await async_e32_call(link, lambda c: c.async_recording(start), write=True)
        except ControllerLinkError as err:
            if str(err) == "controller_recording_unavailable":
                return self.async_abort(reason="tester_recording_unavailable")
            key, values = failure(err)
            return self.async_abort(reason=key, description_placeholders=values)
        monitor = self._tester_monitor()
        if monitor is not None:
            monitor.observe(status if type(status) is dict else None)
            if start:
                monitor.recording_started()
        return self.async_abort(reason="tester_recording_started" if start else "tester_recording_stopped",
                                description_placeholders={"minutes": "30"})

    async def async_step_tester_share(self, user_input=None):
        from .controller_link import ControllerLinkError
        from .e32_system import failure
        link = self._tester_link()
        if link is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        try:
            share, links = await async_share(self.hass, self.config_entry, link)
        except ControllerLinkError as err:
            key, values = failure(err)
            return self.async_abort(reason=key, description_placeholders=values)
        except OSError:
            return self.async_abort(reason="tester_share_not_written")
        return self.async_abort(reason="tester_shared", description_placeholders={"files": str(len(links))})

    async def async_step_tester_off(self, user_input=None):
        save_tester(self.hass, self.config_entry, False)
        trail = self._trail()
        if trail and trail[-1] == "tester_menu":
            trail.pop()  # the note goes on the menu above it: the tester's own menu is gone
        return self.async_abort(reason="tester_switched_off", description_placeholders={"name": self.config_entry.title})


def status_line(status, texts):
    """The bus recording in one line for the tester's menu."""
    if status is None:
        return texts["unreachable"]
    state = status.get("state")
    seconds, frames = status.get("seconds"), status.get("frames")
    minutes = seconds // 60 if type(seconds) is int and seconds >= 0 else 0
    count = frames if type(frames) is int and frames >= 0 else 0
    key = state if state in ("idle", "recording", "ready", "unavailable", "not_supported") else "unreachable"
    return texts[key].format(minutes=minutes, frames=count)
