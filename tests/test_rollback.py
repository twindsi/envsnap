"""Tests for envsnap.rollback."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envsnap.rollback import rollback_snapshot


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, env: dict) -> None:
    data = {"name": name, "env": env}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(data))


def _write_history(snapshot_dir: Path, events: list) -> None:
    history_file = snapshot_dir / "history.json"
    history_file.write_text(json.dumps(events))


def test_rollback_success(snapshot_dir: Path) -> None:
    env_v1 = {"FOO": "bar", "BAZ": "1"}
    env_v2 = {"FOO": "baz", "BAZ": "2"}
    _write_snapshot(snapshot_dir, "mysnap", env_v2)
    _write_history(snapshot_dir, [
        {"name": "mysnap", "event": "capture", "timestamp": "2024-01-01T00:00:00", "env": env_v1},
        {"name": "mysnap", "event": "capture", "timestamp": "2024-01-02T00:00:00", "env": env_v2},
    ])

    result = rollback_snapshot("mysnap", snapshot_dir, steps=1)

    assert result.ok is True
    assert result.restored_vars == env_v1
    assert result.rolled_back_to == "2024-01-01T00:00:00"


def test_rollback_updates_snapshot_file(snapshot_dir: Path) -> None:
    env_v1 = {"KEY": "old"}
    env_v2 = {"KEY": "new"}
    _write_snapshot(snapshot_dir, "snap", env_v2)
    _write_history(snapshot_dir, [
        {"name": "snap", "event": "capture", "timestamp": "t1", "env": env_v1},
        {"name": "snap", "event": "capture", "timestamp": "t2", "env": env_v2},
    ])

    rollback_snapshot("snap", snapshot_dir, steps=1)

    saved = json.loads((snapshot_dir / "snap.json").read_text())
    assert saved["env"] == env_v1


def test_rollback_no_history(snapshot_dir: Path) -> None:
    _write_snapshot(snapshot_dir, "snap", {"A": "1"})
    _write_history(snapshot_dir, [])

    result = rollback_snapshot("snap", snapshot_dir, steps=1)

    assert result.ok is False
    assert "no capture events" in result.message


def test_rollback_not_enough_steps(snapshot_dir: Path) -> None:
    env_v1 = {"X": "1"}
    _write_snapshot(snapshot_dir, "snap", env_v1)
    _write_history(snapshot_dir, [
        {"name": "snap", "event": "capture", "timestamp": "t1", "env": env_v1},
    ])

    result = rollback_snapshot("snap", snapshot_dir, steps=2)

    assert result.ok is False
    assert "not enough history" in result.message


def test_rollback_invalid_steps(snapshot_dir: Path) -> None:
    result = rollback_snapshot("snap", snapshot_dir, steps=0)
    assert result.ok is False
    assert "steps must be" in result.message


def test_rollback_skips_events_without_env(snapshot_dir: Path) -> None:
    env_v1 = {"ONLY": "this"}
    _write_snapshot(snapshot_dir, "snap", env_v1)
    _write_history(snapshot_dir, [
        {"name": "snap", "event": "capture", "timestamp": "t1", "env": env_v1},
        {"name": "snap", "event": "delete", "timestamp": "t2"},
    ])

    # Only 1 capture event with env, steps=1 should fail (no prior state)
    result = rollback_snapshot("snap", snapshot_dir, steps=1)
    assert result.ok is False
