"""Lock/unlock snapshots to prevent accidental modification or deletion."""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional


def _locks_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / ".locks.json"


def _load_locks(snapshot_dir: Path) -> dict:
    p = _locks_path(snapshot_dir)
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def _save_locks(snapshot_dir: Path, data: dict) -> None:
    with _locks_path(snapshot_dir).open("w") as f:
        json.dump(data, f, indent=2)


@dataclass
class LockResult:
    ok: bool
    name: str
    locked: bool
    message: str = ""

    def __repr__(self) -> str:
        state = "locked" if self.locked else "unlocked"
        return f"LockResult(name={self.name!r}, state={state}, ok={self.ok})"


def lock_snapshot(snapshot_dir: Path, name: str) -> LockResult:
    """Mark a snapshot as locked."""
    snap_file = snapshot_dir / f"{name}.json"
    if not snap_file.exists():
        return LockResult(ok=False, name=name, locked=False, message=f"Snapshot '{name}' not found.")

    locks = _load_locks(snapshot_dir)
    if locks.get(name):
        return LockResult(ok=True, name=name, locked=True, message=f"Snapshot '{name}' is already locked.")

    locks[name] = True
    _save_locks(snapshot_dir, locks)
    return LockResult(ok=True, name=name, locked=True, message=f"Snapshot '{name}' locked.")


def unlock_snapshot(snapshot_dir: Path, name: str) -> LockResult:
    """Remove lock from a snapshot."""
    locks = _load_locks(snapshot_dir)
    if not locks.get(name):
        return LockResult(ok=True, name=name, locked=False, message=f"Snapshot '{name}' is not locked.")

    del locks[name]
    _save_locks(snapshot_dir, locks)
    return LockResult(ok=True, name=name, locked=False, message=f"Snapshot '{name}' unlocked.")


def is_locked(snapshot_dir: Path, name: str) -> bool:
    """Return True if the snapshot is locked."""
    return _load_locks(snapshot_dir).get(name, False)


def list_locked(snapshot_dir: Path) -> List[str]:
    """Return names of all locked snapshots."""
    return [name for name, locked in _load_locks(snapshot_dir).items() if locked]
