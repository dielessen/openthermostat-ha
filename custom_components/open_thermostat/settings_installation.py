"""The settings panel's section Installation (1.4.1; settings.py registers it after Advanced; its screen is built in
golf B of docs/engineering/HA-INSTELPANEEL-FASE2.nl.md, chapter 3.7).

"Dashboard and name" and "Advanced" in one section, with under a heading Maintenance what Configure → Advanced and
diagnostics still did alone: restoring an E32 settings backup, tidying entity IDs (and undoing it) and removing the
older Home Assistant rooms. One back end: every part calls the function Configure's step calls.

Items (the part after ``#installation/``):

- ``None``, the list: ``name`` and ``create_dashboard`` (settings.read_general; the save is general's check and
  commit_general), and under ``live`` what the list only shows (outside the token, so a backup made meanwhile never
  makes a save of the name "changed elsewhere"): ``e32`` (connected), ``logging`` (the E32 system log as last read
  through this section, else None: the list never signs in to the E32), ``time_zone``, ``tester``, ``status``
  (settings_advanced's list), and ``maintenance``: the last backup and the backups Home Assistant keeps (no document),
  whether a restore runs, how many entities an undo would rename back, the older Home Assistant rooms.
- ``logging``, ``time-zone``, ``tester``, ``status``: the screens of Advanced (settings_advanced.read_advanced and
  save_advanced), the same models, saves and refusals.

Actions (CONTRACT-1.4.1 §3; ``values`` may carry ``language``, the viewer's, for texts):

- ``restore_check {upload_id | backup, address?, password?, passphrase?}`` → ``{summary, adopt, nothing, restart,
  created, changes, reenter}``: the backup is an uploaded file (Home Assistant's file upload; ``passphrase`` opens its
  passwords and keys, without one they are skipped) or one Home Assistant keeps (``backup``: its id, as Configure's
  list). The E32 checks it (e32_backup.async_check: the step e32_restore_checking), then the confirm step's rules
  (e32_backup_flow.check_outcome). ``address``/``password``: another E32 (a replacement), as the form.
- ``restore_apply {upload_id | backup, adopt?}`` → ``{started}``: the restore of exactly what was checked, as the
  confirm step's task (one at a time); a restore onto another E32 than this installation uses (or the adopt case:
  it holds the settings already) needs ``adopt: true``.
- ``restore_progress`` → ``{state, done, error?, reenter?}``: ``applying``, then the key of Configure's closing
  sentence (``e32_restore_done_online`` …, ``e32_restore_adopted``, ``e32_restore_cancelled``) or ``failed`` with the
  form's error key; ``idle`` when nothing ran.
- ``tidy_ids_preview {only_unused}`` → ``{rows, more, text, count, used, days, nothing}``; ``tidy_ids_apply
  {only_unused}`` → ``{state: "entity_ids_done", count, todo}``; ``tidy_ids_undo`` → ``{state:
  "entity_ids_undone", count}`` (the steps entity_ids and entity_ids_undo).
- ``legacy_rooms`` → ``{rooms: [{id, name, entities}], count, changes, finish, readable, problem, state}``;
  ``legacy_rooms_remove {ids}`` → ``{started}``; ``legacy_rooms_progress`` → ``{state, done, error?, rooms?}`` (the
  steps legacy_rooms*, with their task and their codes).

The panel asks its question (the step's tick) before it calls an action that writes. No password, passphrase or
secret is ever in an answer or a log; a checked backup (it holds the E32 password the user typed) is kept in memory
for CHECK_KEPT seconds, for its restore_apply only.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
import logging
import time
from typing import Any

from homeassistant.util import dt as dt_util

from .const import CONF_CREATE_DASHBOARD
from .settings import (LIVE, SettingsError, commit_general, general_unchanged, general_values, language, read_general,
                       register_section)

_LOGGER = logging.getLogger(__name__)

STATE = "open_thermostat_settings_installation"  # hass.data: entry_id -> _State (survives a reload of the entry)
ITEMS = ("logging", "time-zone", "tester", "status")  # the screens of Advanced, also under #installation/
CHECK_KEPT = 1800  # seconds a checked backup waits for its restore_apply
# The form's sign-in refusals belong to a field of the panel.
LOGIN_FIELDS = {"controller_address_invalid": "address", "controller_password_required": "password",
                "controller_auth_failed": "password"}


@dataclass
class _State:
    """What an action leaves for the next one (Configure keeps it on its flow object)."""
    restore_source: str | None = None
    restore_record: dict | None = field(default=None, repr=False)  # an uploaded file's record (holds its passphrase)
    restore_check: Any = field(default=None, repr=False)  # the RestoreCheck (holds the E32 password)
    restore_outcome: str | None = None
    restore_at: float = 0.0
    restore_task: asyncio.Task | None = field(default=None, repr=False)
    restore_result: dict | None = None
    upload: tuple | None = field(default=None, repr=False)  # (upload id, document, when): the last file, re-checkable
    tidy_plan: Any = field(default=None, repr=False)
    legacy_listed: bool = False
    legacy_shown: Any = field(default=None, repr=False)
    legacy_task: asyncio.Task | None = field(default=None, repr=False)
    legacy_result: dict | None = None
    logging: dict | None = None

    def forget_check(self):
        self.restore_source = self.restore_record = self.restore_check = self.restore_outcome = None
        self.restore_at = 0.0


def _state(hass, entry):
    states = hass.data.setdefault(STATE, {})
    state = states.get(entry.entry_id)
    if state is None:
        state = states[entry.entry_id] = _State()
    return state


def _running(task):
    return task is not None and not task.done()


def _language(hass, values):
    wanted = values.get("language") if isinstance(values, dict) else None
    return language(hass, wanted if type(wanted) is str else None)


# -- the list ------------------------------------------------------------------------------------------------------

async def _maintenance(hass, entry, state):
    from .e32_backup import backups, last_backup
    from .e32_link import legacy_rooms_pending, legacy_zones
    from .entity_id_tidy import async_undo_available
    manager = backups(hass, entry)
    backup = None
    if manager is not None:
        last, info = last_backup(manager)
        backup = {"last": last.isoformat() if last else None, "count": info["count"], "size": info["size"],
                  "error": manager.last_error,
                  # Configure's list of the backups (record_label); "keys": with the passwords and keys, sealed.
                  "kept": [{"id": r["id"], "kind": r["kind"], "created": r["created"], "size": r["size"],
                            "keys": bool(r.get("secrets"))} for r in manager.records()]}
    return {"backup": backup, "restoring": _running(state.restore_task),
            "tidy_undo": len(await async_undo_available(hass, entry)),
            "legacy_rooms": len(legacy_zones(entry)), "legacy_pending": legacy_rooms_pending(entry),
            "legacy_removing": _running(state.legacy_task)}


async def _read_list(hass, entry, state):
    from .settings_advanced import _read_list as advanced_list
    advanced = await advanced_list(hass, entry)
    return {"screen": "list", **read_general(hass, entry),
            LIVE: {"e32": advanced["e32"], "logging": state.logging, "time_zone": advanced["time_zone"],
                   "tester": advanced["tester"], "status": advanced["status"],
                   "maintenance": await _maintenance(hass, entry, state)}}


def _save_list(hass, entry, values):
    """Dashboard and name, as the section general saves them; a key the panel leaves out keeps its value."""
    from .product import configuration_snapshot
    current = read_general(hass, entry)
    name, dashboard = general_values({**current, **{k: values[k] for k in ("name", CONF_CREATE_DASHBOARD) if k in values}})
    if not general_unchanged(entry, name, dashboard):
        commit_general(hass, entry, configuration_snapshot(entry), name, dashboard)


def _remember_logging(state, model):
    """The system log's sending state as last read or saved here (the list shows it without signing in)."""
    if type(model) is dict and model.get("screen") == "logging" and type(model.get("syslog_enabled")) is bool:
        state.logging = {"on": model["syslog_enabled"], "server": model.get("server") or ""}


async def read_installation(hass, entry, item=None):
    state = _state(hass, entry)
    if item is None:
        return await _read_list(hass, entry, state)
    if item in ITEMS:
        from .settings_advanced import read_advanced
        model = await read_advanced(hass, entry, item)
        _remember_logging(state, model)
        return model
    raise SettingsError("unknown_section")


async def save_installation(hass, entry, item, values):
    state = _state(hass, entry)
    if item is None:
        _save_list(hass, entry, values)
        return await _read_list(hass, entry, state)
    if item in ITEMS:
        from .settings_advanced import save_advanced
        model = await save_advanced(hass, entry, item, values)
        _remember_logging(state, model)
        return model
    raise SettingsError("unknown_section")


# -- the overview line ---------------------------------------------------------------------------------------------

TEXT = {
    "en": {"today": "Backup from today", "yesterday": "Backup from yesterday", "days": "Backup from {n} days ago",
           "none": "No backup yet", "room_one": "1 old Home Assistant room", "rooms": "{n} old Home Assistant rooms"},
    "nl": {"today": "Back-up van vandaag", "yesterday": "Back-up van gisteren", "days": "Back-up van {n} dagen geleden",
           "none": "Nog geen back-up", "room_one": "1 oude Home Assistant-ruimte", "rooms": "{n} oude Home Assistant-ruimtes"},
    "pl": {"today": "Kopia z dzisiaj", "yesterday": "Kopia z wczoraj", "days": "Kopia sprzed {n} dni",
           "none": "Brak jeszcze kopii", "room_one": "1 stare pomieszczenie Home Assistant",
           "rooms": "Stare pomieszczenia Home Assistant: {n}"},
}


def summary_installation(hass, entry, hub, lang):
    """"Thuis · Back-up van gisteren · 1 oude Home Assistant-ruimte": the name, how old the last E32 backup is (with
    an E32 connection) and the older Home Assistant rooms that are left. From memory only."""
    from .e32_backup import backups
    from .e32_link import legacy_zones
    t, parts = TEXT[lang], [entry.title]
    manager = backups(hass, entry)
    if manager is not None:
        last = manager.last_success
        if last is None:
            parts.append(t["none"])
        else:
            days = (dt_util.now().date() - dt_util.as_local(last).date()).days
            parts.append(t["today"] if days <= 0 else t["yesterday"] if days == 1 else t["days"].format(n=days))
    rooms = len(legacy_zones(entry))
    if rooms:
        parts.append(t["room_one"] if rooms == 1 else t["rooms"].format(n=rooms))
    return [" · ".join(parts)]


# -- restore a backup ----------------------------------------------------------------------------------------------

def _read_upload(hass, upload_id):
    """The uploaded file's bytes (at most one byte more than a backup may have), or None when there is no such
    upload. Runs in the executor; Home Assistant removes the file afterwards."""
    from homeassistant.components.file_upload import process_uploaded_file
    from .e32_backup import UPLOAD_MAX
    try:
        with process_uploaded_file(hass, upload_id) as path, path.open("rb") as file:
            return file.read(UPLOAD_MAX + 1)
    except (ValueError, OSError):
        return None


def _source_key(values):
    """"upload:<id>" or "backup:<id>": which backup the panel means (exactly one of the two), else None."""
    upload, backup = values.get("upload_id"), values.get("backup")
    if (upload is None) == (backup is None):
        return None
    value = upload if backup is None else backup
    if type(value) is not str or not value:
        return None
    return ("upload:" if backup is None else "backup:") + value


async def _source(hass, entry, manager, values):
    """(source key, record, the uploaded record or None) of the backup to check; SettingsError on a refusal."""
    from .e32_backup import document_from_file, uploaded_record, valid_passphrase
    source = _source_key(values)
    if source is None:
        raise SettingsError("setup_invalid")
    kind, _, value = source.partition(":")
    if kind == "backup":
        record = manager.record(value)
        if record is None:
            raise SettingsError("e32_restore_failed")  # as the form: a backup that is gone meanwhile
        return source, record, None
    passphrase = values.get("passphrase") or None
    if passphrase is not None and not valid_passphrase(passphrase):
        raise SettingsError("e32_restore_passphrase_invalid", "passphrase")
    state = _state(hass, entry)
    if state.upload is not None and state.upload[0] == value and time.monotonic() - state.upload[2] <= CHECK_KEPT:
        document = state.upload[1]  # Home Assistant hands a file over once: a second check (another passphrase) reuses it
    else:
        data = await hass.async_add_executor_job(_read_upload, hass, value)
        if data is None:
            raise SettingsError("e32_restore_file_missing", "upload_id")
        document = document_from_file(data)
        if document is None:
            raise SettingsError("e32_restore_file_invalid", "upload_id")
        state.upload = (value, document, time.monotonic())
    record = uploaded_record(document, passphrase)
    return source, record, record


def _refusal(err, uploaded):
    """A failed check as the form's error (restore_error), on the panel's field."""
    from .controller_link import BackupRejected
    from .e32_backup_flow import restore_error
    if uploaded and isinstance(err, BackupRejected) and err.error in ("wrong_passphrase", "invalid_passphrase"):
        return SettingsError("e32_restore_passphrase_wrong", "passphrase")
    code = restore_error(err)
    return SettingsError(code, LOGIN_FIELDS.get(code, "base"))


async def restore_check(hass, entry, item, values):
    from .controller_link import ControllerLinkError
    from .controller_setup_flow import CONTROLLER_ADDRESS
    from .e32_backup import backups, other_e32, summary_text
    from .e32_backup_flow import check_outcome, restore_login
    state = _state(hass, entry)
    if _running(state.restore_task):
        raise SettingsError("e32_restore_busy")  # one restore at a time
    manager = backups(hass, entry)
    if manager is None:
        raise SettingsError("e32_restore_unavailable")
    state.forget_check()
    try:
        # Before the file is taken from Home Assistant's upload: a refused sign-in never costs the upload.
        address, password = restore_login(entry, values.get("address") or entry.data.get(CONTROLLER_ADDRESS, ""),
                                          values.get("password") or "")
    except ControllerLinkError as err:
        raise _refusal(err, False) from None
    source, record, uploaded = await _source(hass, entry, manager, values)
    try:
        check = await manager.async_check(address, password, record["id"], record=uploaded)
    except Exception as err:  # noqa: BLE001 - every failure becomes a named error, as in the form
        raise _refusal(err, uploaded is not None) from None
    outcome = check_outcome(hass, entry, check)
    if outcome not in ("adopt", "nothing", "confirm"):
        raise SettingsError(outcome)
    state.restore_source, state.restore_record, state.restore_check = source, uploaded, check
    state.restore_outcome, state.restore_at, state.restore_result = outcome, time.monotonic(), None
    return {"summary": summary_text(check.summary, _language(hass, values)),
            "adopt": outcome == "adopt" or (outcome == "confirm" and other_e32(entry, check)),
            "nothing": outcome in ("adopt", "nothing"), "restart": check.summary["restart"],
            "created": record.get("created"), "changes": len(check.summary["changes"]),
            "reenter": len(check.summary["reenter"])}


def _restore_finished(state, task):
    """The restore task's outcome, kept for restore_progress (also when nobody asks)."""
    from .e32_backup_flow import done_reason, restore_error
    if state.restore_task is task:
        state.restore_task = None
    try:
        result = task.result()
    except asyncio.CancelledError:
        state.restore_result = {"state": "e32_restore_cancelled"}
        return
    except Exception as err:  # noqa: BLE001 - every failure becomes the form's named error
        state.restore_result = {"state": "failed", "error": restore_error(err)}
        return
    state.restore_result = {"state": done_reason(result), "reenter": list(result["reenter"])}


async def restore_apply(hass, entry, item, values):
    from .e32_backup import backups, other_e32
    from .e32_backup_flow import check_outcome
    state = _state(hass, entry)
    if _running(state.restore_task):
        raise SettingsError("e32_restore_busy")
    source = _source_key(values)
    if (source is None or source != state.restore_source or state.restore_check is None
            or time.monotonic() - state.restore_at > CHECK_KEPT):
        raise SettingsError("e32_restore_check_first")
    manager = backups(hass, entry)
    check, uploaded = state.restore_check, state.restore_record
    if manager is None or (uploaded is None and manager.record(check.record_id) is None):
        state.forget_check()
        raise SettingsError("e32_restore_unavailable")
    # As the confirm step on its submit: the rules again (another installation may have this E32 now).
    outcome = check_outcome(hass, entry, check)
    if outcome not in ("adopt", "nothing", "confirm"):
        state.forget_check()
        raise SettingsError(outcome)
    if outcome == "nothing":
        raise SettingsError("e32_restore_nothing")
    if (outcome == "adopt" or other_e32(entry, check)) and values.get("adopt") is not True:
        raise SettingsError("e32_restore_adopt_confirm_required", "adopt")
    if outcome == "adopt":
        if not manager.adopt(check):
            raise SettingsError("e32_restore_adopt_failed")
        state.forget_check()
        state.restore_result = {"state": "e32_restore_adopted"}
        return {"started": True}
    task = hass.async_create_task(manager.async_restore(check, record=uploaded), "OpenThermostat restore E32 backup")
    state.forget_check()
    state.upload = None
    state.restore_task, state.restore_result = task, None
    task.add_done_callback(lambda done: _restore_finished(state, done))
    return {"started": True}


def restore_progress(hass, entry, item, values):
    from .e32_backup import reenter_text
    state = _state(hass, entry)
    if _running(state.restore_task):
        return {"state": "applying", "done": False}
    if state.restore_task is not None:  # finished, its done callback not run yet
        _restore_finished(state, state.restore_task)
    result = state.restore_result
    if result is None:
        return {"state": "idle", "done": True}
    answer = {"state": result["state"], "done": True}
    if "error" in result:
        answer["error"] = result["error"]
    if "reenter" in result:
        answer["reenter"] = reenter_text(result["reenter"], _language(hass, values))
    return answer


# -- tidy entity IDs -----------------------------------------------------------------------------------------------

def _only_unused(values):
    value = values.get("only_unused", True)  # the form's default scope: only entities used nowhere
    if type(value) is not bool:
        raise SettingsError("setup_invalid", "only_unused")
    return value


async def tidy_ids_preview(hass, entry, item, values):
    from . import entity_id_tidy as tidy
    only_unused = _only_unused(values)
    state = _state(hass, entry)
    plan = state.tidy_plan = await tidy.async_plan(hass, entry)
    rows = tidy.chosen(plan, only_unused)
    return {"rows": [{"old": r.old, "new": r.new, "name": r.name, "used_in": list(r.used_in)}
                     for r in rows[:tidy.PREVIEW_LINES]],
            "more": max(0, len(rows) - tidy.PREVIEW_LINES),
            "text": tidy.preview_text(plan, only_unused, _language(hass, values)),
            "count": len(plan.renames), "used": len(plan.renames) - len(plan.unused), "days": tidy.UNDO_DAYS,
            "nothing": not plan.renames}


async def tidy_ids_apply(hass, entry, item, values):
    """The step's confirmed submit: the plan the preview showed (else a fresh one), the chosen scope."""
    from . import entity_id_tidy as tidy
    only_unused = _only_unused(values)
    state = _state(hass, entry)
    plan = state.tidy_plan or await tidy.async_plan(hass, entry)
    state.tidy_plan = None
    if not plan.renames:
        raise SettingsError("entity_ids_nothing")
    done, todo = await tidy.async_apply_plan(hass, entry, plan, only_unused)
    return {"state": "entity_ids_done", "count": len(done), "todo": todo}


async def tidy_ids_undo(hass, entry, item, values):
    from . import entity_id_tidy as tidy
    if not await tidy.async_undo_available(hass, entry):
        raise SettingsError("entity_ids_nothing")
    undone = await tidy.async_undo(hass, entry)
    return {"state": "entity_ids_undone", "count": len(undone)}


# -- the older Home Assistant rooms ----------------------------------------------------------------------------------

def _legacy_retry(state):
    """After a failed removal the step offers to try again, also when no old room is left (the E32 link)."""
    return state.legacy_result is not None and state.legacy_result.get("state") == "failed"


async def legacy_rooms(hass, entry, item, values):
    from .e32_link import async_room_plan_firmware_problem, legacy_rooms_pending, legacy_zones
    from .legacy_room_migration import describe, zone_entities
    from .legacy_rooms_flow import async_read_migration
    state = _state(hass, entry)
    if not legacy_rooms_pending(entry) and not _legacy_retry(state):
        state.legacy_listed, state.legacy_shown = False, None
        return {"rooms": [], "count": 0, "changes": "", "finish": False, "readable": True, "problem": None,
                "state": "legacy_rooms_none"}
    zones = sorted(legacy_zones(entry), key=lambda z: z.title)
    # As the step's first form: firmware before beta.19 is said before the user confirms.
    problem = await async_room_plan_firmware_problem(hass, entry)
    migration = await async_read_migration(hass, entry, zones) if zones else None
    state.legacy_listed, state.legacy_shown = True, migration.signature() if migration is not None else None
    owned = zone_entities(hass, entry, zones)
    rooms = [{"id": zone.subentry_id, "name": zone.title,
              "entities": sorted(e for e, z in owned.items() if z.subentry_id == zone.subentry_id)} for zone in zones]
    return {"rooms": rooms, "count": len(zones),
            "changes": describe(hass, migration, _language(hass, values)) if zones else "",
            "finish": not zones, "readable": migration is not None or not zones, "problem": problem,
            "state": "legacy_rooms" if zones else "legacy_rooms_finish"}


def _legacy_finished(hass, entry, state, task):
    from .legacy_rooms_flow import removal_done, removal_failure
    if state.legacy_task is task:
        state.legacy_task = None
    try:
        result = task.result()
    except asyncio.CancelledError:
        state.legacy_result = {"state": "legacy_rooms_cancelled"}
        return
    except Exception as err:  # noqa: BLE001 - every failure becomes the step's named error
        state.legacy_result = {"state": "failed", "error": removal_failure(err)}
        return
    removal_done(hass, entry)
    rooms = result.get("room_ids", []) if isinstance(result, dict) else []
    state.legacy_result = {"state": "legacy_rooms_removed", "rooms": len(rooms)}


async def legacy_rooms_remove(hass, entry, item, values):
    from .e32_link import legacy_rooms_pending, legacy_zones
    from .legacy_rooms_flow import start_removal
    state = _state(hass, entry)
    if _running(state.legacy_task):
        return {"started": True}  # the removal that runs (never a second one)
    if not legacy_rooms_pending(entry) and not _legacy_retry(state):
        raise SettingsError("legacy_rooms_none")
    zones = legacy_zones(entry)
    ids = values.get("ids", [])
    if (not state.legacy_listed or type(ids) is not list or not all(type(i) is str for i in ids)
            or sorted(ids) != sorted(z.subentry_id for z in zones)):
        raise SettingsError("legacy_rooms_changed", "ids")
    if zones and state.legacy_shown is None:
        raise SettingsError("legacy_rooms_plan_unreadable")
    task = start_removal(hass, entry, state.legacy_shown)
    # A new list after this reads the plan again (the step's rule).
    state.legacy_listed, state.legacy_shown, state.legacy_task, state.legacy_result = False, None, task, None
    task.add_done_callback(lambda done: _legacy_finished(hass, entry, state, done))
    return {"started": True}


def legacy_rooms_progress(hass, entry, item, values):
    state = _state(hass, entry)
    if _running(state.legacy_task):
        return {"state": "removing", "done": False}
    if state.legacy_task is not None:  # finished, its done callback not run yet
        _legacy_finished(hass, entry, state, state.legacy_task)
    result = state.legacy_result
    if result is None:
        return {"state": "idle", "done": True}
    return {**result, "done": True}


ACTIONS = {"restore_check": restore_check, "restore_apply": restore_apply, "restore_progress": restore_progress,
           "tidy_ids_preview": tidy_ids_preview, "tidy_ids_apply": tidy_ids_apply, "tidy_ids_undo": tidy_ids_undo,
           "legacy_rooms": legacy_rooms, "legacy_rooms_remove": legacy_rooms_remove,
           "legacy_rooms_progress": legacy_rooms_progress}

register_section("installation", read_installation, save_installation, summary=summary_installation, order=8,
                 actions=ACTIONS)
