"""Audit log for envsnap: track who accessed or modified snapshots."""

import json
import os
import getpass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


def _audit_path(snapshot_dir: str) -> Path:
    return Path(snapshot_dir) / ".audit_log.json"


def _load_audit(snapshot_dir: str) -> List[dict]:
    path = _audit_path(snapshot_dir)
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_audit(snapshot_dir: str, entries: List[dict]) -> None:
    path = _audit_path(snapshot_dir)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def record_audit(snapshot_dir: str, action: str, snapshot_name: str, details: Optional[str] = None) -> dict:
    """Record an audit event for a snapshot action."""
    entries = _load_audit(snapshot_dir)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": _get_user(),
        "action": action,
        "snapshot": snapshot_name,
        "details": details or "",
    }
    entries.append(entry)
    _save_audit(snapshot_dir, entries)
    return entry


def _get_user() -> str:
    try:
        return getpass.getuser()
    except Exception:
        return os.environ.get("USER", "unknown")


def get_audit_log(snapshot_dir: str, snapshot_name: Optional[str] = None, action: Optional[str] = None) -> List[dict]:
    """Retrieve audit entries, optionally filtered by snapshot name or action."""
    entries = _load_audit(snapshot_dir)
    if snapshot_name:
        entries = [e for e in entries if e.get("snapshot") == snapshot_name]
    if action:
        entries = [e for e in entries if e.get("action") == action]
    return entries


def clear_audit_log(snapshot_dir: str) -> int:
    """Clear all audit entries. Returns number of entries removed."""
    entries = _load_audit(snapshot_dir)
    count = len(entries)
    _save_audit(snapshot_dir, [])
    return count
