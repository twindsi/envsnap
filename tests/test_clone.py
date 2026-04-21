"""Tests for envsnap.clone."""

import json
import os
import pytest

from envsnap.clone import clone_snapshot


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(directory: str, name: str, vars_: dict) -> None:
    data = {"name": name, "vars": vars_}
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as fh:
        json.dump(data, fh)


def test_clone_creates_destination(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"FOO": "1", "BAR": "2"})
    result = clone_snapshot(snapshot_dir, "base", "base_copy")
    assert result.ok
    dest_path = os.path.join(snapshot_dir, "base_copy.json")
    assert os.path.isfile(dest_path)


def test_clone_copies_all_keys_by_default(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"FOO": "1", "BAR": "2"})
    result = clone_snapshot(snapshot_dir, "base", "base_copy")
    assert sorted(result.cloned_keys) == ["BAR", "FOO"]
    assert result.skipped_keys == []


def test_clone_with_prefix_filter(snapshot_dir):
    _write_snapshot(
        snapshot_dir,
        "base",
        {"APP_HOST": "localhost", "APP_PORT": "8080", "DB_URL": "sqlite://"},
    )
    result = clone_snapshot(snapshot_dir, "base", "app_only", prefix_filter="APP_")
    assert result.ok
    assert sorted(result.cloned_keys) == ["APP_HOST", "APP_PORT"]
    assert result.skipped_keys == ["DB_URL"]

    dest_path = os.path.join(snapshot_dir, "app_only.json")
    with open(dest_path) as fh:
        data = json.load(fh)
    assert "DB_URL" not in data["vars"]
    assert data["vars"]["APP_HOST"] == "localhost"


def test_clone_missing_source_returns_error(snapshot_dir):
    result = clone_snapshot(snapshot_dir, "nonexistent", "copy")
    assert not result.ok
    assert "nonexistent" in result.error


def test_clone_destination_exists_no_overwrite(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"X": "1"})
    _write_snapshot(snapshot_dir, "copy", {"Y": "2"})
    result = clone_snapshot(snapshot_dir, "base", "copy", overwrite=False)
    assert not result.ok
    assert "already exists" in result.error


def test_clone_destination_exists_with_overwrite(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"X": "1"})
    _write_snapshot(snapshot_dir, "copy", {"Y": "2"})
    result = clone_snapshot(snapshot_dir, "base", "copy", overwrite=True)
    assert result.ok
    dest_path = os.path.join(snapshot_dir, "copy.json")
    with open(dest_path) as fh:
        data = json.load(fh)
    assert data["vars"] == {"X": "1"}


def test_clone_preserves_values(snapshot_dir):
    original = {"SECRET": "abc123", "MODE": "production"}
    _write_snapshot(snapshot_dir, "prod", original)
    clone_snapshot(snapshot_dir, "prod", "prod_backup")
    dest_path = os.path.join(snapshot_dir, "prod_backup.json")
    with open(dest_path) as fh:
        data = json.load(fh)
    assert data["vars"] == original
    assert data["name"] == "prod_backup"
