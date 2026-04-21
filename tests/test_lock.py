"""Tests for envsnap/lock.py"""

import json
import pytest
from pathlib import Path
from envsnap.lock import lock_snapshot, unlock_snapshot, is_locked, list_locked


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, data: dict = None):
    payload = data or {"name": name, "vars": {"FOO": "bar"}}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(payload))


def test_lock_missing_snapshot_returns_error(snapshot_dir):
    result = lock_snapshot(snapshot_dir, "ghost")
    assert result.ok is False
    assert "not found" in result.message
    assert result.locked is False


def test_lock_creates_lock_entry(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev")
    result = lock_snapshot(snapshot_dir, "dev")
    assert result.ok is True
    assert result.locked is True
    assert is_locked(snapshot_dir, "dev") is True


def test_lock_already_locked_is_idempotent(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev")
    lock_snapshot(snapshot_dir, "dev")
    result = lock_snapshot(snapshot_dir, "dev")
    assert result.ok is True
    assert result.locked is True
    assert "already locked" in result.message


def test_unlock_removes_lock(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev")
    lock_snapshot(snapshot_dir, "dev")
    result = unlock_snapshot(snapshot_dir, "dev")
    assert result.ok is True
    assert result.locked is False
    assert is_locked(snapshot_dir, "dev") is False


def test_unlock_not_locked_is_safe(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev")
    result = unlock_snapshot(snapshot_dir, "dev")
    assert result.ok is True
    assert result.locked is False
    assert "not locked" in result.message


def test_is_locked_returns_false_for_unknown(snapshot_dir):
    assert is_locked(snapshot_dir, "nonexistent") is False


def test_list_locked_returns_only_locked(snapshot_dir):
    _write_snapshot(snapshot_dir, "alpha")
    _write_snapshot(snapshot_dir, "beta")
    _write_snapshot(snapshot_dir, "gamma")
    lock_snapshot(snapshot_dir, "alpha")
    lock_snapshot(snapshot_dir, "gamma")
    locked = list_locked(snapshot_dir)
    assert set(locked) == {"alpha", "gamma"}
    assert "beta" not in locked


def test_list_locked_empty_when_none_locked(snapshot_dir):
    _write_snapshot(snapshot_dir, "solo")
    assert list_locked(snapshot_dir) == []
