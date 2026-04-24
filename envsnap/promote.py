"""Promote a snapshot from one environment stage to another (e.g. dev -> staging -> prod)."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import List, Optional

from envsnap.snapshot import load, save

STAGES: List[str] = ["dev", "staging", "prod"]


@dataclass
class PromoteResult:
    ok: bool
    source: str
    destination: str
    new_name: str = ""
    error: str = ""
    skipped_keys: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        if self.ok:
            return f"<PromoteResult ok source={self.source!r} dest={self.destination!r} new={self.new_name!r}>"
        return f"<PromoteResult FAILED error={self.error!r}>"


def _next_stage(current: str) -> Optional[str]:
    """Return the next stage after *current*, or None if already at the last stage."""
    try:
        idx = STAGES.index(current)
    except ValueError:
        return None
    if idx + 1 >= len(STAGES):
        return None
    return STAGES[idx + 1]


def promote_snapshot(
    snapshot_dir,
    name: str,
    target_stage: Optional[str] = None,
    exclude_keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> PromoteResult:
    """Promote *name* to *target_stage* (or the next stage automatically).

    The promoted snapshot is saved as ``<base>-<stage>`` where *base* is the
    original name stripped of any known stage suffix.
    """
    exclude_keys = exclude_keys or []

    data = load(snapshot_dir, name)
    if data is None:
        return PromoteResult(ok=False, source=name, destination="", error=f"Snapshot {name!r} not found.")

    # Determine current stage from name suffix
    current_stage = None
    base_name = name
    for stage in STAGES:
        if name.endswith(f"-{stage}"):
            current_stage = stage
            base_name = name[: -(len(stage) + 1)]
            break

    if target_stage is None:
        target_stage = _next_stage(current_stage or "")
        if target_stage is None:
            return PromoteResult(
                ok=False,
                source=name,
                destination="",
                error="Cannot determine next stage; specify target_stage explicitly.",
            )

    if target_stage not in STAGES:
        return PromoteResult(ok=False, source=name, destination=target_stage, error=f"Unknown stage {target_stage!r}.")

    new_name = f"{base_name}-{target_stage}"

    existing = load(snapshot_dir, new_name)
    if existing is not None and not overwrite:
        return PromoteResult(
            ok=False,
            source=name,
            destination=target_stage,
            new_name=new_name,
            error=f"Snapshot {new_name!r} already exists. Use overwrite=True to replace.",
        )

    promoted_env = {k: v for k, v in data["env"].items() if k not in exclude_keys}
    skipped = [k for k in data["env"] if k in exclude_keys]

    promoted = copy.deepcopy(data)
    promoted["env"] = promoted_env
    promoted["name"] = new_name

    save(snapshot_dir, promoted)
    return PromoteResult(ok=True, source=name, destination=target_stage, new_name=new_name, skipped_keys=skipped)
