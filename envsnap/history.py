"""Track access and usage history for snapshots."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


def _history_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".history.json"


def _load_history(snapshot_dir: Path) -> List[Dict]:
    path = _history_path(snapshot_dir)
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _save_history(snapshot_dir: Path, history: List[Dict]) -> None:
    path = _history_path(snapshot_dir)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def record_event(snapshot_dir: Path, snapshot_name: str, action: str) -> None:
    """Record an action (capture, restore, export, delete) for a snapshot."""
    history = _load_history(snapshot_dir)
    history.append({
        "snapshot": snapshot_name,
        "action": action,
        "timestamp": datetime.utcnow().isoformat(),
    })
    _save_history(snapshot_dir, history)


def get_history(snapshot_dir: Path, snapshot_name: Optional[str] = None) -> List[Dict]:
    """Return history entries, optionally filtered by snapshot name."""
    history = _load_history(snapshot_dir)
    if snapshot_name:
        return [e for e in history if e["snapshot"] == snapshot_name]
    return history


def clear_history(snapshot_dir: Path, snapshot_name: Optional[str] = None) -> int:
    """Clear history entries. Returns number of entries removed."""
    history = _load_history(snapshot_dir)
    if snapshot_name:
        kept = [e for e in history if e["snapshot"] != snapshot_name]
    else:
        kept = []
    removed = len(history) - len(kept)
    _save_history(snapshot_dir, kept)
    return removed


def recent(snapshot_dir: Path, limit: int = 10) -> List[Dict]:
    """Return the most recent history entries."""
    history = _load_history(snapshot_dir)
    return history[-limit:]
