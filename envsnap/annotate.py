"""Annotation support: attach free-text notes to snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


def _annotations_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_annotations.json"


def _load_annotations(snapshot_dir: Path) -> Dict[str, List[str]]:
    path = _annotations_path(snapshot_dir)
    if not path.exists():
        return {}
    with path.open() as f:
        return json.load(f)


def _save_annotations(snapshot_dir: Path, data: Dict[str, List[str]]) -> None:
    path = _annotations_path(snapshot_dir)
    with path.open("w") as f:
        json.dump(data, f, indent=2)


def add_annotation(snapshot_dir: Path, snapshot_name: str, note: str) -> bool:
    """Append a note to the snapshot's annotation list.

    Returns False if the snapshot file does not exist.
    """
    snap_file = snapshot_dir / f"{snapshot_name}.json"
    if not snap_file.exists():
        return False

    data = _load_annotations(snapshot_dir)
    data.setdefault(snapshot_name, []).append(note)
    _save_annotations(snapshot_dir, data)
    return True


def get_annotations(snapshot_dir: Path, snapshot_name: str) -> List[str]:
    """Return all notes attached to a snapshot (empty list if none)."""
    data = _load_annotations(snapshot_dir)
    return data.get(snapshot_name, [])


def remove_annotation(snapshot_dir: Path, snapshot_name: str, index: int) -> bool:
    """Remove the note at *index* from a snapshot's annotation list.

    Returns False if the snapshot has no annotations or the index is out of range.
    """
    data = _load_annotations(snapshot_dir)
    notes = data.get(snapshot_name, [])
    if index < 0 or index >= len(notes):
        return False
    notes.pop(index)
    if notes:
        data[snapshot_name] = notes
    else:
        data.pop(snapshot_name, None)
    _save_annotations(snapshot_dir, data)
    return True


def clear_annotations(snapshot_dir: Path, snapshot_name: str) -> int:
    """Remove all annotations for a snapshot. Returns the count removed."""
    data = _load_annotations(snapshot_dir)
    notes = data.pop(snapshot_name, [])
    if notes:
        _save_annotations(snapshot_dir, data)
    return len(notes)
