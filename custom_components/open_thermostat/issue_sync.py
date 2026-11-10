"""Keep a set of Repairs issues equal to what is wrong now: create the new ones, delete the ones that cleared.

A shared helper for the heating problems (heating_problem.py) and any other part that raises
issues per item, such as radiator valves: each owner passes its own ``group`` and the full set of
issues it wants now; issues of that group that are no longer wanted are removed, so a warning
clears itself once its cause is gone.
"""
from __future__ import annotations

from homeassistant.helpers import issue_registry as ir

from .const import DOMAIN, SHARED

_KEY = "issue_sync"


def sync_issues(hass, entry_id, group, wanted, *, severity=ir.IssueSeverity.WARNING):
    """``wanted``: {item id: (translation key, placeholders)}. Returns the issue ids that exist now."""
    store = hass.data.setdefault(SHARED, {}).setdefault(_KEY, {})
    key = (entry_id, group)
    current = {f"{group}_{item}_{entry_id}": value for item, value in wanted.items()}
    for issue_id, (translation_key, placeholders) in current.items():
        ir.async_create_issue(hass, DOMAIN, issue_id, is_fixable=False, is_persistent=False, severity=severity,
                              translation_key=translation_key,
                              translation_placeholders={k: str(v) for k, v in (placeholders or {}).items()})
    for issue_id in store.get(key, set()) - set(current):
        ir.async_delete_issue(hass, DOMAIN, issue_id)
    if current:
        store[key] = set(current)
    else:
        store.pop(key, None)  # nothing raised: no key kept for an owner that is gone (R4-31)
    return set(current)


def clear_issues(hass, entry_id, group):
    """Remove every issue of a group (the owner is unloaded)."""
    return sync_issues(hass, entry_id, group, {})


def forget_entry(hass, entry_id):
    """A removed installation: drop its bookkeeping (its issues are deleted by async_remove_entry)."""
    store = hass.data.get(SHARED, {}).get(_KEY, {})
    for key in [k for k in store if k[0] == entry_id]:
        del store[key]


# Repairs items earlier versions raised that are no Repairs items any more (1.4): a Repairs item names something that
# is broken or needs a decision now, never a design fact, an advice or an "it changed" notice. A room with one
# temperature source is explained in the room form, a restored room group is only logged and the "renewed" notes
# are only in the diagnostics.
RETIRED = ("valve_single_source", "room_group_restored", "legacy_metrics_history", "metrics_definition_v2",
           "room_model_v2",
    "room_programs",  # 1.4 (#7): a room without a program is a choice, not a fault
    "valve_battery_low",  # 1.4.2: upcoming maintenance; the Batteries list and the battery message say it
    # 1.4.2 (HA-LIFETIME, HC-05, T-24): an invitation that has its button and its notification ("Let the E32 plan
    # the heating"), information after the fact (the E32 learns it again; a line in the diagnostics), and a
    # firmware fact the tester program's screen says itself ("This E32 firmware cannot make a bus recording yet").
    "plan_ready", "learned_lost_at_restart", "tester_recording_update",
)


def retired_issue(issue_id, entry_id, translation_key=None):
    """True for a retired item of this entry: its id is ``<key>_<entry>`` or ``<key>_<entry>_<item>``, or (an item
    of a group, issue_sync's ``<group>_<item>_<entry>``) its translation key is a retired key."""
    if translation_key in RETIRED and (issue_id.endswith(f"_{entry_id}") or f"_{entry_id}_" in issue_id):
        return True
    return any(issue_id == f"{key}_{entry_id}" or issue_id.startswith(f"{key}_{entry_id}_") for key in RETIRED)


def remove_retired_issues(hass, entry_id):
    """At every setup of the entry: remove the retired items an older version left in the issue registry."""
    registry = ir.async_get(hass)
    for (domain, issue_id), issue in list(registry.issues.items()):
        if domain == DOMAIN and retired_issue(issue_id, entry_id, getattr(issue, "translation_key", None)):
            ir.async_delete_issue(hass, DOMAIN, issue_id)
