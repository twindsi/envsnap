"""Diff two environment snapshots."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.snapshot import load


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines: List[str] = []
        for key, val in sorted(self.added.items()):
            lines.append(f"+ {key}={val}")
        for key, val in sorted(self.removed.items()):
            lines.append(f"- {key}={val}")
        for key, (old, new) in sorted(self.changed.items()):
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "No differences found."


def diff_snapshots(
    name_a: str,
    name_b: str,
    snapshot_dir: Optional[str] = None,
) -> DiffResult:
    """Compare two named snapshots and return a DiffResult."""
    snap_a = load(name_a, snapshot_dir=snapshot_dir)
    snap_b = load(name_b, snapshot_dir=snapshot_dir)

    env_a: Dict[str, str] = snap_a.get("env", {})
    env_b: Dict[str, str] = snap_b.get("env", {})

    return diff_envs(env_a, env_b)


def diff_envs(env_a: Dict[str, str], env_b: Dict[str, str]) -> DiffResult:
    """Compare two env dicts directly and return a DiffResult."""
    result = DiffResult()

    keys_a = set(env_a)
    keys_b = set(env_b)

    for key in keys_b - keys_a:
        result.added[key] = env_b[key]

    for key in keys_a - keys_b:
        result.removed[key] = env_a[key]

    for key in keys_a & keys_b:
        if env_a[key] != env_b[key]:
            result.changed[key] = (env_a[key], env_b[key])

    return result
