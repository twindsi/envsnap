"""Tests for envsnap.snapshot module."""

import json
import os
from pathlib import Path

import pytest

from envsnap.snapshot import capture, delete, list_snapshots, load, save


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path / "snapshots"


def test_capture_returns_all_env_vars():
    snap = capture()
    assert "variables" in snap
    assert snap["variables"] == dict(os.environ)


def test_capture_with_prefix(monkeypatch):
    monkeypatch.setenv("MY_APP_FOO", "bar")
    monkeypatch.setenv("OTHER_VAR", "baz")
    snap = capture(prefix="MY_APP_")
    assert all(k.startswith("MY_APP_") for k in snap["variables"])
    assert "OTHER_VAR" not in snap["variables"]


def test_capture_uses_provided_name():
    snap = capture(name="my-snapshot")
    assert snap["name"] == "my-snapshot"


def test_save_creates_json_file(snapshot_dir):
    snap = capture(name="test-save")
    path = save(snap, snapshot_dir=snapshot_dir)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["name"] == "test-save"


def test_load_returns_saved_snapshot(snapshot_dir):
    snap = capture(name="roundtrip")
    save(snap, snapshot_dir=snapshot_dir)
    loaded = load("roundtrip", snapshot_dir=snapshot_dir)
    assert loaded["name"] == "roundtrip"
    assert loaded["variables"] == snap["variables"]


def test_load_raises_for_missing_snapshot(snapshot_dir):
    with pytest.raises(FileNotFoundError, match="missing-snap"):
        load("missing-snap", snapshot_dir=snapshot_dir)


def test_list_snapshots_empty(snapshot_dir):
    assert list_snapshots(snapshot_dir=snapshot_dir) == []


def test_list_snapshots_returns_names(snapshot_dir):
    for name in ("alpha", "beta", "gamma"):
        save(capture(name=name), snapshot_dir=snapshot_dir)
    names = list_snapshots(snapshot_dir=snapshot_dir)
    assert set(names) == {"alpha", "beta", "gamma"}


def test_delete_removes_snapshot(snapshot_dir):
    save(capture(name="to-delete"), snapshot_dir=snapshot_dir)
    delete("to-delete", snapshot_dir=snapshot_dir)
    assert "to-delete" not in list_snapshots(snapshot_dir=snapshot_dir)


def test_delete_raises_for_missing(snapshot_dir):
    with pytest.raises(FileNotFoundError):
        delete("ghost", snapshot_dir=snapshot_dir)
