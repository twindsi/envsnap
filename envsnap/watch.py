"""Watch for environment variable changes and record diffs automatically."""

import os
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from envsnap.diff import diff_envs, DiffResult
from envsnap.history import record_event
from envsnap.snapshot import capture


@dataclass
class WatchConfig:
    interval: float = 5.0
    prefix: Optional[str] = None
    on_change: Optional[Callable[[DiffResult], None]] = None
    max_events: int = 0  # 0 = unlimited


@dataclass
class WatchSession:
    name: str
    config: WatchConfig
    events: list = field(default_factory=list)
    _running: bool = field(default=False, repr=False)

    def stop(self) -> None:
        self._running = False


def _snapshot_env(prefix: Optional[str]) -> Dict[str, str]:
    snap = capture(name="_watch_internal", prefix=prefix)
    return snap["vars"]


def start_watch(name: str, config: Optional[WatchConfig] = None, snapshot_dir: str = ".envsnap") -> WatchSession:
    """Start watching environment variables for changes.

    Polls at config.interval seconds, records a history event on each diff.
    Returns a WatchSession; call session.stop() to halt.
    """
    if config is None:
        config = WatchConfig()

    session = WatchSession(name=name, config=config)
    session._running = True

    previous = _snapshot_env(config.prefix)

    event_count = 0
    while session._running:
        time.sleep(config.interval)
        current = _snapshot_env(config.prefix)
        result = diff_envs(previous, current)

        if result.has_changes():
            event = {
                "added": result.added,
                "removed": result.removed,
                "changed": result.changed,
            }
            session.events.append(event)
            record_event(snapshot_dir, name, "watch_diff", detail=result.summary())

            if config.on_change:
                config.on_change(result)

            previous = current
            event_count += 1

            if config.max_events and event_count >= config.max_events:
                session.stop()

    return session
