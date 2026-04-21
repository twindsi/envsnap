"""Clone an existing snapshot under a new name, optionally filtering keys."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import List, Optional

from envsnap.snapshot import load, save


@dataclass
class CloneResult:
    source: str
    destination: str
    cloned_keys: List[str] = field(default_factory=list)
    skipped_keys: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None

    def __repr__(self) -> str:  # pragma: no cover
        if not self.ok:
            return f"CloneResult(error={self.error!r})"
        return (
            f"CloneResult({self.source!r} -> {self.destination!r}, "
            f"keys={len(self.cloned_keys)}, skipped={len(self.skipped_keys)})"
        )


def clone_snapshot(
    snapshot_dir: str,
    source_name: str,
    dest_name: str,
    prefix_filter: Optional[str] = None,
    overwrite: bool = False,
) -> CloneResult:
    """Clone *source_name* to *dest_name* inside *snapshot_dir*.

    Args:
        snapshot_dir: Directory that holds all snapshots.
        source_name: Name of the snapshot to clone.
        dest_name: Name for the new cloned snapshot.
        prefix_filter: If given, only keys starting with this prefix are copied.
        overwrite: Allow overwriting an existing snapshot with *dest_name*.

    Returns:
        A :class:`CloneResult` describing what happened.
    """
    result = CloneResult(source=source_name, destination=dest_name)

    try:
        source_data = load(snapshot_dir, source_name)
    except FileNotFoundError:
        result.error = f"Source snapshot '{source_name}' not found."
        return result

    # Check destination collision
    try:
        load(snapshot_dir, dest_name)
        if not overwrite:
            result.error = (
                f"Destination snapshot '{dest_name}' already exists. "
                "Use overwrite=True to replace it."
            )
            return result
    except FileNotFoundError:
        pass  # destination does not exist — that's fine

    env_vars: dict = copy.deepcopy(source_data.get("vars", {}))

    if prefix_filter:
        for key in list(env_vars.keys()):
            if key.startswith(prefix_filter):
                result.cloned_keys.append(key)
            else:
                result.skipped_keys.append(key)
                del env_vars[key]
    else:
        result.cloned_keys = list(env_vars.keys())

    new_snapshot = {"name": dest_name, "vars": env_vars}
    save(snapshot_dir, dest_name, new_snapshot)
    return result
