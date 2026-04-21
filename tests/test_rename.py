"""Tests for envsnap.rename module."""

import json
import pytest
from pathlib import Path

from envsnap.rename import rename_snapshot
from envsnap import tags as tags_mod
from envsnap import pin as pin_mod
from envsnap import history as history_mod


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, env: dict) -> Path:
    path = snapshot_dir / f"{name}.json"
    path.write_text(json.dumps({"name": name, "env": env}, indent=2))
    return path


def test_rename_success(snapshot_dir):
    _write_snapshot(snapshot_dir, "old", {"FOO": "bar"})
    result = rename_snapshot(snapshot_dir, "old", "new")
    assert result.success is True
    assert result.old_name == "old"
    assert result.new_name == "new"
    assert (snapshot_dir / "new.json").exists()
    assert not (snapshot_dir / "old.json").exists()


def test_rename_updates_name_field(snapshot_dir):
    _write_snapshot(snapshot_dir, "alpha", {"X": "1"})
    rename_snapshot(snapshot_dir, "alpha", "beta")
    data = json.loads((snapshot_dir / "beta.json").read_text())
    assert data["name"] == "beta"


def test_rename_missing_snapshot_returns_error(snapshot_dir):
    result = rename_snapshot(snapshot_dir, "ghost", "phantom")
    assert result.success is False
    assert "not found" in result.error


def test_rename_target_exists_returns_error(snapshot_dir):
    _write_snapshot(snapshot_dir, "a", {"K": "v"})
    _write_snapshot(snapshot_dir, "b", {"K": "v"})
    result = rename_snapshot(snapshot_dir, "a", "b")
    assert result.success is False
    assert "already exists" in result.error


def test_rename_migrates_tags(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"ENV": "prod"})
    tags_mod.add_tag(snapshot_dir, "snap1", "production")
    tags_mod.add_tag(snapshot_dir, "snap1", "stable")
    result = rename_snapshot(snapshot_dir, "snap1", "snap2")
    assert result.success is True
    assert result.tags_updated is True
    new_tags = tags_mod.get_tags(snapshot_dir, "snap2")
    assert "production" in new_tags
    assert "stable" in new_tags


def test_rename_migrates_pins(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"A": "1"})
    pin_mod.pin_snapshot(snapshot_dir, "mysnap", "latest")
    result = rename_snapshot(snapshot_dir, "mysnap", "mysnap_v2")
    assert result.success is True
    assert "latest" in result.pins_updated
    pins = pin_mod._load_pins(snapshot_dir)
    assert pins["latest"] == "mysnap_v2"


def test_rename_records_history(snapshot_dir):
    _write_snapshot(snapshot_dir, "orig", {"Z": "9"})
    rename_snapshot(snapshot_dir, "orig", "renamed")
    events = history_mod.get_history(snapshot_dir, name="renamed")
    assert any(e["event"] == "rename" for e in events)


def test_rename_repr_success(snapshot_dir):
    _write_snapshot(snapshot_dir, "x", {"P": "q"})
    result = rename_snapshot(snapshot_dir, "x", "y")
    assert "->" in repr(result)


def test_rename_repr_failure(snapshot_dir):
    result = rename_snapshot(snapshot_dir, "missing", "target")
    assert "error=" in repr(result)
