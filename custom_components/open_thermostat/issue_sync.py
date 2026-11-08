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
