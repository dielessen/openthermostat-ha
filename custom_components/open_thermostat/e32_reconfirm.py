"""Repairs: "Confirm the takeover again" (beta.23, review S3; reasons since E32 1.4.6).

The E32 controlled the boiler, but its stored confirmation no longer holds, so it
does not take over again until the owner confirms once more that the E32 may
control the boiler (``active.reconfirm_required`` in the heating status). Until
then it keeps only frost protection. This is a fault that needs the owner (the
house is not heated), so it is a Repair; it clears by itself once confirmed.
This issue offers that one confirmation (``POST /config/heating/handover``); the
E32 checks it again (its firmware gate, the plan active) and answers with its
active-control status. The E32 Boiler page (Boiler test and takeover) confirms
too; handing back stays on the E32 Rooms page (Active control).

Up to E32 1.4.5 every firmware update asked again. Since 1.4.6 the confirmation
is kept over an update while the boiler, its protocol and the route are the same
(FW-TAKEOVER-KEEP), and the E32 says why it asks (``active.reconfirm_reason``):
``boiler_changed`` -> ``reconfirm_takeover_boiler``, ``route_changed`` ->
``reconfirm_takeover_route``, ``boiler_not_identified`` and
``record_unreadable`` -> ``reconfirm_takeover_unchecked``. ``firmware`` (other
takeover rules, or older firmware asked), no reason (E32 1.4.5 and older) or an
unknown one keep the update words below.

No existing thermostat is assumed (E32 rc.3): the update words mention an old
thermostat only when the E32 ever heard another controller ask the boiler for
heat (``active.thermostat_seen``, kept by the E32), with the translation key
``reconfirm_takeover_thermostat``; otherwise ``reconfirm_takeover`` says
"confirm again that the E32 may control the boiler". The reason words never
assume one.
"""
from __future__ import annotations

from homeassistant.components.repairs import RepairsFlow
from homeassistant.core import callback
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

RECONFIRM_ISSUE = "reconfirm_takeover"
# The same issue in the words of a home whose E32 once heard another thermostat on the boiler bus.
RECONFIRM_THERMOSTAT_KEY = "reconfirm_takeover_thermostat"
# E32 1.4.6: why it asks again -> the issue's words (any other reason: the update words).
REASON_KEYS = {"boiler_changed": "reconfirm_takeover_boiler", "route_changed": "reconfirm_takeover_route",
               "boiler_not_identified": "reconfirm_takeover_unchecked", "record_unreadable": "reconfirm_takeover_unchecked"}
# The E32's refusals -> this flow's errors (plan_not_active ends it); anything else: not reachable.
REFUSALS = {"active_mode_not_released": "reconfirm_not_released"}


def issue_id(entry):
    return f"{RECONFIRM_ISSUE}_{entry.entry_id}"


def _active(hub):
    active = getattr(hub, "active", None)
    if type(active) is not dict:
        status = getattr(hub, "status", None) or {}
        active = status.get("active") if type(status) is dict else None
    return active if type(active) is dict else None


def reconfirm_required(hub):
    """Whether the E32 waits for the owner to confirm the takeover again after an update."""
    active = _active(hub)
    return active is not None and active.get("reconfirm_required") is True


def thermostat_seen(hub):
    """Whether the E32 ever heard another controller ask the boiler for heat (E32 rc.3; older firmware: no)."""
    active = _active(hub)
    return active is not None and active.get("thermostat_seen") is True


def reconfirm_reason(hub):
    """Why the E32 asks again (E32 1.4.6); None from older firmware or while it does not ask."""
    active = _active(hub)
    reason = active.get("reconfirm_reason") if active is not None else None
    return reason if type(reason) is str else None


def translation_key(hub):
    """The issue's words: the E32's reason, else the update words, with the old thermostat only when it heard one."""
    reason_key = REASON_KEYS.get(reconfirm_reason(hub))
    if reason_key:
        return reason_key
    return RECONFIRM_THERMOSTAT_KEY if thermostat_seen(hub) else RECONFIRM_ISSUE


@callback
def update_reconfirm_issue(hass, entry, hub):
    """Raise the issue while the E32 asks for it, remove it once answered (kept during an outage)."""
    if not hub.fresh:
        return
    registry, key = ir.async_get(hass), issue_id(entry)
    if not reconfirm_required(hub):
        if registry.async_get_issue(DOMAIN, key) is not None:
            ir.async_delete_issue(hass, DOMAIN, key)
        return
    words, existing = translation_key(hub), registry.async_get_issue(DOMAIN, key)
    if existing is None or existing.translation_key != words:  # new, another reason, or a thermostat heard since
        ir.async_create_issue(hass, DOMAIN, key, is_fixable=True, is_persistent=False,
                              severity=ir.IssueSeverity.WARNING, translation_key=words,
                              data={"entry_id": entry.entry_id})


async def async_handover(link, disconnected):
    """POST the handover over the room-plan link's stored connection; waits for a free E32 web session."""
    return await link.async_call(lambda client: client.async_handover(disconnected), write=True)


class ReconfirmTakeoverRepairFlow(RepairsFlow):
    """One confirmation: the E32 may control the boiler again (no other thermostat connected)."""

    def __init__(self, issue, data):
        self._issue, self._data = issue, data

    async def async_step_init(self, user_input=None):
        # Home Assistant opens a repair with data={"issue_id": ...} as this step's input: never a submitted form.
        return await self.async_step_reconfirm_takeover()

    async def async_step_reconfirm_takeover(self, user_input=None):
        from .controller_link import ControllerLinkError, HeatingPlanRejected
        entry = self.hass.config_entries.async_get_entry(self._data.get("entry_id"))
        hub = self.hass.data.get(DOMAIN, {}).get(entry.entry_id, {}).get("heating_hub") if entry else None
        if hub is None or hub.plan is None:
            return self.async_abort(reason="e32_rooms_unavailable")
        if hub.fresh and not reconfirm_required(hub):
            ir.async_delete_issue(self.hass, DOMAIN, self._issue)
            return self.async_abort(reason="reconfirm_done")
        if user_input is None:
            return self.async_show_form(step_id="reconfirm_takeover")
        try:
            answer = await async_handover(hub.plan, True)
        except HeatingPlanRejected as err:
            if err.error == "plan_not_active":
                ir.async_delete_issue(self.hass, DOMAIN, self._issue)
                return self.async_abort(reason="reconfirm_plan_not_active")
            return self.async_show_form(step_id="reconfirm_takeover",
                                        errors={"base": REFUSALS.get(err.error, "e32_unreachable")})
        except ControllerLinkError as err:
            refused = str(err) == "controller_password_change_required"  # Repairs: choose a new E32 password first
            return self.async_show_form(step_id="reconfirm_takeover",
                                        errors={"base": "e32_password_change_required" if refused else "e32_unreachable"})
        if type(answer) is not dict or type(answer.get("confirmation")) is not dict or answer.get("reconfirm_required"):
            return self.async_show_form(step_id="reconfirm_takeover", errors={"base": "reconfirm_unconfirmed"})
        ir.async_delete_issue(self.hass, DOMAIN, self._issue)
        return self.async_create_entry(data={})
