"""Tests for envsnap/profile.py"""

import json
import pytest
from pathlib import Path

from envsnap.profile import (
    add_to_profile,
    remove_from_profile,
    get_profile,
    list_profiles,
)


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, env: dict) -> None:
    data = {"name": name, "env": env}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(data))


def test_add_to_profile_creates_entry(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {"APP_ENV": "development"})
    result = add_to_profile(snapshot_dir, "myproject", "dev")
    assert result.ok
    assert "dev" in result.snapshots
    assert result.profile == "myproject"


def test_add_to_profile_missing_snapshot_returns_error(snapshot_dir):
    result = add_to_profile(snapshot_dir, "myproject", "ghost")
    assert not result.ok
    assert "not found" in result.message


def test_add_to_profile_deduplicates(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {})
    add_to_profile(snapshot_dir, "myproject", "dev")
    result = add_to_profile(snapshot_dir, "myproject", "dev")
    assert not result.ok
    assert "already in profile" in result.message


def test_add_multiple_snapshots_to_profile(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {})
    _write_snapshot(snapshot_dir, "staging", {})
    add_to_profile(snapshot_dir, "web", "dev")
    add_to_profile(snapshot_dir, "web", "staging")
    result = get_profile(snapshot_dir, "web")
    assert result.ok
    assert set(result.snapshots) == {"dev", "staging"}


def test_remove_from_profile_existing(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {})
    add_to_profile(snapshot_dir, "web", "dev")
    result = remove_from_profile(snapshot_dir, "web", "dev")
    assert result.ok
    assert "dev" not in result.snapshots


def test_remove_last_member_deletes_profile(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {})
    add_to_profile(snapshot_dir, "solo", "dev")
    remove_from_profile(snapshot_dir, "solo", "dev")
    profiles = list_profiles(snapshot_dir)
    assert "solo" not in profiles


def test_remove_from_missing_profile_returns_error(snapshot_dir):
    result = remove_from_profile(snapshot_dir, "nonexistent", "dev")
    assert not result.ok
    assert "not found" in result.message


def test_get_profile_missing_returns_error(snapshot_dir):
    result = get_profile(snapshot_dir, "missing")
    assert not result.ok


def test_list_profiles_empty(snapshot_dir):
    assert list_profiles(snapshot_dir) == {}


def test_list_profiles_returns_all(snapshot_dir):
    _write_snapshot(snapshot_dir, "a", {})
    _write_snapshot(snapshot_dir, "b", {})
    add_to_profile(snapshot_dir, "p1", "a")
    add_to_profile(snapshot_dir, "p2", "b")
    profiles = list_profiles(snapshot_dir)
    assert "p1" in profiles
    assert "p2" in profiles
