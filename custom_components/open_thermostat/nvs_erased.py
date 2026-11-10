"""The Repairs item "The E32 lost its stored settings" (1.4.2, plan 3.15; FW-SMALL detects it, F3).

At start the Arduino core may wipe the whole settings memory (NVS) without a word; the E32 then starts with the
factory password, without rooms, learned data and Bluetooth pairings. E32 1.4.2 notices it (no plan and no password
while its marker says the previous boot had them) and says ``"nvs_erased": true`` in that one boot's ``fw/state/boot``
record (last_restart.decode). That is a fault, so a Repairs item that says what to do: restore the last backup and
choose a new password. Persistent, because the firmware says it once; it goes when the user ignores it, or by itself
once the E32 is online with rooms in a plan other than the one it had when the item was raised (a restored backup)
and Home Assistant does not see the factory password (e32_access's ``e32_default_password`` item). Never because a
later boot record lacks the key.

Mixed versions: E32 1.4.1 never sends the key (no item); Home Assistant 1.4.1 ignores it.
"""
from __future__ import annotations

from homeassistant.core import callback
from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN

NVS_ERASED_ISSUE = "nvs_erased"


def nvs_issue_id(entry):
    return f"{NVS_ERASED_ISSUE}_{entry.entry_id}"


@callback
def sync_nvs_erased(hass, entry, hub, report=None):
    """The Repairs item ``nvs_erased``: raised by a boot report that says so, kept until dismissed or repaired.

    Persistent, because the E32 says it in one boot's record only. Another boot that says it again shows it again
    (also after a dismissal); the same boot again (a Home Assistant restart, the retained record) keeps a dismissal.
    It goes by itself once the E32 is online with rooms in a plan other than the one it had when the item was
    raised (a restored backup) and Home Assistant does not see the factory password.
    """
    issue_id = nvs_issue_id(entry)
    registry = ir.async_get(hass)
    existing = registry.async_get_issue(DOMAIN, issue_id)
    config = getattr(hub, "config", None)
    revision = config.get("revision") if type(config) is dict else None
    if report is not None and report.get("nvs_erased"):
        if existing is not None and (existing.data or {}).get("boot") == report["boot"]:
            return
        if existing is not None:
            ir.async_delete_issue(hass, DOMAIN, issue_id)  # another boot: shown again, also after a dismissal
        ir.async_create_issue(hass, DOMAIN, issue_id, is_fixable=False, is_persistent=True,
                              severity=ir.IssueSeverity.ERROR, translation_key=NVS_ERASED_ISSUE,
                              translation_placeholders={"name": entry.title},
                              data={"boot": report["boot"], "revision": revision})
        return
    if existing is None or not getattr(hub, "fresh", False) or type(config) is not dict or not config.get("rooms"):
        return
    from .e32_access import default_password_issue_id
    if revision != (existing.data or {}).get("revision") and registry.async_get_issue(
            DOMAIN, default_password_issue_id(entry)) is None:
        ir.async_delete_issue(hass, DOMAIN, issue_id)
