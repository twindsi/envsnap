"""Rename snapshots and update related metadata (tags, pins, history)."""

import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from envsnap import tags as tags_mod
from envsnap import history as history_mod
from envsnap import pin as pin_mod


@dataclass
class RenameResult:
    old_name: str
    new_name: str
    tags_updated: bool
    pins_updated: list
    success: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        if self.success:
            return (
                f"RenameResult('{self.old_name}' -> '{self.new_name}', "
                f"tags_updated={self.tags_updated}, pins_updated={self.pins_updated})"
            )
        return f"RenameResult(error='{self.error}')"


def rename_snapshot(snapshot_dir: Path, old_name: str, new_name: str) -> RenameResult:
    """Rename a snapshot file and update tags, pins, and history metadata."""
    old_path = snapshot_dir / f"{old_name}.json"
    new_path = snapshot_dir / f"{new_name}.json"

    if not old_path.exists():
        return RenameResult(
            old_name=old_name,
            new_name=new_name,
            tags_updated=False,
            pins_updated=[],
            success=False,
            error=f"Snapshot '{old_name}' not found.",
        )

    if new_path.exists():
        return RenameResult(
            old_name=old_name,
            new_name=new_name,
            tags_updated=False,
            pins_updated=[],
            success=False,
            error=f"Snapshot '{new_name}' already exists.",
        )

    # Rename the file
    old_path.rename(new_path)

    # Update the 'name' field inside the JSON
    data = json.loads(new_path.read_text())
    data["name"] = new_name
    new_path.write_text(json.dumps(data, indent=2))

    # Migrate tags
    tags_updated = False
    existing_tags = tags_mod.get_tags(snapshot_dir, old_name)
    if existing_tags:
        for tag in existing_tags:
            tags_mod.add_tag(snapshot_dir, new_name, tag)
        tags_mod.remove_tag(snapshot_dir, old_name, existing_tags[0])
        # Remove all old tags
        for tag in existing_tags[1:]:
            tags_mod.remove_tag(snapshot_dir, old_name, tag)
        tags_updated = True

    # Migrate pins
    updated_pins = []
    pins = pin_mod._load_pins(snapshot_dir)
    for alias, target in list(pins.items()):
        if target == old_name:
            pins[alias] = new_name
            updated_pins.append(alias)
    if updated_pins:
        pin_mod._save_pins(snapshot_dir, pins)

    # Record history
    history_mod.record_event(snapshot_dir, new_name, "rename", {"from": old_name})

    return RenameResult(
        old_name=old_name,
        new_name=new_name,
        tags_updated=tags_updated,
        pins_updated=updated_pins,
        success=True,
    )
