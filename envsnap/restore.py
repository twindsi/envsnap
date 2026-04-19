"""Restore environment variables from a snapshot."""

import os
from typing import Optional

from envsnap.snapshot import load


class RestoreResult:
    def __init__(self, applied: dict, skipped: dict, snapshot_name: str):
        self.applied = applied
        self.skipped = skipped
        self.snapshot_name = snapshot_name

    def __repr__(self):
        return (
            f"RestoreResult(snapshot={self.snapshot_name!r}, "
            f"applied={len(self.applied)}, skipped={len(self.skipped)})"
        )


def restore_snapshot(
    snapshot_name: str,
    snapshot_dir: str,
    overwrite: bool = False,
    prefix: Optional[str] = None,
) -> RestoreResult:
    """Load a snapshot and apply its variables to the current process environment.

    Args:
        snapshot_name: Name of the snapshot to restore.
        snapshot_dir: Directory where snapshots are stored.
        overwrite: If True, overwrite existing env vars. Default is False.
        prefix: Only restore variables that start with this prefix.

    Returns:
        RestoreResult with applied and skipped variable mappings.
    """
    snapshot = load(snapshot_name, snapshot_dir)
    env_vars: dict = snapshot.get("vars", {})

    if prefix:
        env_vars = {k: v for k, v in env_vars.items() if k.startswith(prefix)}

    applied = {}
    skipped = {}

    for key, value in env_vars.items():
        if key in os.environ and not overwrite:
            skipped[key] = value
        else:
            os.environ[key] = value
            applied[key] = value

    return RestoreResult(applied=applied, skipped=skipped, snapshot_name=snapshot_name)


def export_shell_script(snapshot_name: str, snapshot_dir: str, prefix: Optional[str] = None) -> str:
    """Generate a shell export script from a snapshot.

    Args:
        snapshot_name: Name of the snapshot.
        snapshot_dir: Directory where snapshots are stored.
        prefix: Only include variables that start with this prefix.

    Returns:
        A string of shell export statements.
    """
    snapshot = load(snapshot_name, snapshot_dir)
    env_vars: dict = snapshot.get("vars", {})

    if prefix:
        env_vars = {k: v for k, v in env_vars.items() if k.startswith(prefix)}

    lines = [f"export {k}={v!r}" for k, v in sorted(env_vars.items())]
    return "\n".join(lines)
