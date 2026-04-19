"""Tag management for envsnap snapshots."""

import json
from pathlib import Path
from typing import List, Optional

TAGS_FILE = "tags.json"


def _tags_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / TAGS_FILE


def _load_tags(snapshot_dir: Path) -> dict:
    path = _tags_path(snapshot_dir)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _save_tags(snapshot_dir: Path, tags: dict) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    with open(_tags_path(snapshot_dir), "w") as f:
        json.dump(tags, f, indent=2)


def add_tag(snapshot_dir: Path, snapshot_name: str, tag: str) -> None:
    """Add a tag to a snapshot."""
    tags = _load_tags(snapshot_dir)
    tags.setdefault(snapshot_name, []).append(tag)
    tags[snapshot_name] = list(dict.fromkeys(tags[snapshot_name]))  # dedupe
    _save_tags(snapshot_dir, tags)


def remove_tag(snapshot_dir: Path, snapshot_name: str, tag: str) -> bool:
    """Remove a tag from a snapshot. Returns True if tag was present."""
    tags = _load_tags(snapshot_dir)
    if snapshot_name in tags and tag in tags[snapshot_name]:
        tags[snapshot_name].remove(tag)
        if not tags[snapshot_name]:
            del tags[snapshot_name]
        _save_tags(snapshot_dir, tags)
        return True
    return False


def get_tags(snapshot_dir: Path, snapshot_name: str) -> List[str]:
    """Return all tags for a given snapshot."""
    return _load_tags(snapshot_dir).get(snapshot_name, [])


def find_by_tag(snapshot_dir: Path, tag: str) -> List[str]:
    """Return all snapshot names that have the given tag."""
    tags = _load_tags(snapshot_dir)
    return [name for name, t_list in tags.items() if tag in t_list]


def clear_tags(snapshot_dir: Path, snapshot_name: str) -> None:
    """Remove all tags for a snapshot."""
    tags = _load_tags(snapshot_dir)
    if snapshot_name in tags:
        del tags[snapshot_name]
        _save_tags(snapshot_dir, tags)
