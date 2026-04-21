"""Tests for envsnap/cli_lock.py"""

import json
import argparse
import pytest
from pathlib import Path
from envsnap.cli_lock import cmd_lock


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str):
    (snapshot_dir / f"{name}.json").write_text(json.dumps({"name": name, "vars": {}}))


def _make_args(snapshot_dir, lock_action, name=None):
    return argparse.Namespace(
        snapshot_dir=str(snapshot_dir),
        lock_action=lock_action,
        name=name,
    )


def test_cmd_lock_locks_snapshot(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "prod")
    cmd_lock(_make_args(snapshot_dir, "lock", "prod"))
    out = capsys.readouterr().out
    assert "locked" in out


def test_cmd_lock_missing_snapshot_exits(snapshot_dir):
    with pytest.raises(SystemExit):
        cmd_lock(_make_args(snapshot_dir, "lock", "missing"))


def test_cmd_unlock_unlocks_snapshot(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "prod")
    cmd_lock(_make_args(snapshot_dir, "lock", "prod"))
    cmd_lock(_make_args(snapshot_dir, "unlock", "prod"))
    out = capsys.readouterr().out
    assert "unlocked" in out


def test_cmd_status_locked(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "staging")
    cmd_lock(_make_args(snapshot_dir, "lock", "staging"))
    capsys.readouterr()
    cmd_lock(_make_args(snapshot_dir, "status", "staging"))
    out = capsys.readouterr().out
    assert "locked" in out


def test_cmd_status_unlocked(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "dev")
    cmd_lock(_make_args(snapshot_dir, "status", "dev"))
    out = capsys.readouterr().out
    assert "unlocked" in out


def test_cmd_list_shows_locked(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "alpha")
    _write_snapshot(snapshot_dir, "beta")
    cmd_lock(_make_args(snapshot_dir, "lock", "alpha"))
    capsys.readouterr()
    cmd_lock(_make_args(snapshot_dir, "list"))
    out = capsys.readouterr().out
    assert "alpha" in out
    assert "beta" not in out


def test_cmd_list_empty(snapshot_dir, capsys):
    cmd_lock(_make_args(snapshot_dir, "list"))
    out = capsys.readouterr().out
    assert "No locked" in out
