"""Merge two snapshots into a new combined snapshot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.snapshot import load, save


@dataclass
class MergeResult:
    name: str
    base: str
    overlay: str
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"MergeResult(name={self.name!r}, base={self.base!r}, "
            f"overlay={self.overlay!r}, conflicts={len(self.conflicts)}, "
            f"overwritten={len(self.overwritten)})"
        )


def merge_snapshots(
    snapshot_dir: str,
    base_name: str,
    overlay_name: str,
    result_name: str,
    overwrite: bool = False,
) -> MergeResult:
    """Merge overlay snapshot onto base snapshot and save as result_name.

    Keys present in both snapshots are considered conflicts.
    If overwrite=True the overlay value wins; otherwise the base value is kept.
    """
    base_data = load(snapshot_dir, base_name)
    overlay_data = load(snapshot_dir, overlay_name)

    base_env: Dict[str, str] = base_data.get("env", {})
    overlay_env: Dict[str, str] = overlay_data.get("env", {})

    conflicts: List[str] = []
    overwritten: List[str] = []
    merged: Dict[str, str] = dict(base_env)

    for key, value in overlay_env.items():
        if key in merged:
            conflicts.append(key)
            if overwrite:
                merged[key] = value
                overwritten.append(key)
        else:
            merged[key] = value

    result = MergeResult(
        name=result_name,
        base=base_name,
        overlay=overlay_name,
        merged=merged,
        conflicts=conflicts,
        overwritten=overwritten,
    )

    save(snapshot_dir, result_name, merged)
    return result
