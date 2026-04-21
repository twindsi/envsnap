"""Rollback support: revert a snapshot directory to a previous history state."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envsnap.history import get_history
from envsnap.snapshot import load, save


@dataclass
class RollbackResult:
    ok: bool
    snapshot_name: str
    rolled_back_to: Optional[str] = None  # event timestamp
    message: str = ""
    restored_vars: dict = field(default_factory=dict)

    def __repr__(self) -> str:  # pragma: no cover
        status = "OK" if self.ok else "ERROR"
        return f"<RollbackResult [{status}] {self.snapshot_name}: {self.message}>"


def rollback_snapshot(
    snapshot_name: str,
    snapshot_dir: Path,
    steps: int = 1,
) -> RollbackResult:
    """Revert *snapshot_name* by *steps* capture events recorded in history.

    The function inspects the history log for ``capture`` events that stored
    a ``vars_count`` payload, then walks back *steps* events and restores the
    snapshot file to the state recorded at that point.  Because the full env
    dict is embedded in the history payload we can reconstruct it without
    keeping separate backup files.
    """
    if steps < 1:
        return RollbackResult(
            ok=False,
            snapshot_name=snapshot_name,
            message="steps must be >= 1",
        )

    events = get_history(snapshot_dir, name=snapshot_name)
    capture_events = [
        e for e in events if e.get("event") == "capture" and "env" in e
    ]

    if not capture_events:
        return RollbackResult(
            ok=False,
            snapshot_name=snapshot_name,
            message="no capture events with env payload found in history",
        )

    target_index = len(capture_events) - 1 - steps
    if target_index < 0:
        return RollbackResult(
            ok=False,
            snapshot_name=snapshot_name,
            message=f"not enough history: only {len(capture_events)} capture event(s) available",
        )

    target_event = capture_events[target_index]
    env_snapshot = target_event["env"]
    timestamp = target_event.get("timestamp", "unknown")

    # Overwrite the current snapshot file with the historical env dict.
    save(
        env=env_snapshot,
        name=snapshot_name,
        snapshot_dir=snapshot_dir,
    )

    return RollbackResult(
        ok=True,
        snapshot_name=snapshot_name,
        rolled_back_to=timestamp,
        message=f"rolled back to state at {timestamp}",
        restored_vars=env_snapshot,
    )
