"""Tests for envsnap.promote."""

import json
import os
import pytest

from envsnap.promote import promote_snapshot, STAGES, _next_stage


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir, name: str, env: dict):
    data = {"name": name, "env": env, "timestamp": "2024-01-01T00:00:00"}
    path = snapshot_dir / f"{name}.json"
    path.write_text(json.dumps(data))
    return data


# --- _next_stage ---

def test_next_stage_dev_to_staging():
    assert _next_stage("dev") == "staging"


def test_next_stage_staging_to_prod():
    assert _next_stage("staging") == "prod"


def test_next_stage_prod_returns_none():
    assert _next_stage("prod") is None


def test_next_stage_unknown_returns_none():
    assert _next_stage("unknown") is None


# --- promote_snapshot ---

def test_promote_missing_snapshot_returns_error(snapshot_dir):
    result = promote_snapshot(snapshot_dir, "ghost-dev", target_stage="staging")
    assert not result.ok
    assert "not found" in result.error


def test_promote_creates_destination_snapshot(snapshot_dir):
    _write_snapshot(snapshot_dir, "myapp-dev", {"DB_HOST": "localhost", "PORT": "5432"})
    result = promote_snapshot(snapshot_dir, "myapp-dev", target_stage="staging")
    assert result.ok
    assert result.new_name == "myapp-staging"
    assert (snapshot_dir / "myapp-staging.json").exists()


def test_promote_auto_detects_next_stage(snapshot_dir):
    _write_snapshot(snapshot_dir, "svc-dev", {"KEY": "val"})
    result = promote_snapshot(snapshot_dir, "svc-dev")
    assert result.ok
    assert result.destination == "staging"


def test_promote_copies_all_keys_by_default(snapshot_dir):
    env = {"A": "1", "B": "2", "C": "3"}
    _write_snapshot(snapshot_dir, "app-dev", env)
    result = promote_snapshot(snapshot_dir, "app-dev", target_stage="staging")
    assert result.ok
    dest = json.loads((snapshot_dir / "app-staging.json").read_text())
    assert dest["env"] == env


def test_promote_excludes_specified_keys(snapshot_dir):
    env = {"DB_PASS": "secret", "HOST": "db"}
    _write_snapshot(snapshot_dir, "app-dev", env)
    result = promote_snapshot(snapshot_dir, "app-dev", target_stage="staging", exclude_keys=["DB_PASS"])
    assert result.ok
    assert "DB_PASS" in result.skipped_keys
    dest = json.loads((snapshot_dir / "app-staging.json").read_text())
    assert "DB_PASS" not in dest["env"]
    assert dest["env"]["HOST"] == "db"


def test_promote_blocks_overwrite_by_default(snapshot_dir):
    _write_snapshot(snapshot_dir, "app-dev", {"X": "1"})
    _write_snapshot(snapshot_dir, "app-staging", {"X": "old"})
    result = promote_snapshot(snapshot_dir, "app-dev", target_stage="staging")
    assert not result.ok
    assert "already exists" in result.error


def test_promote_allows_overwrite_when_flag_set(snapshot_dir):
    _write_snapshot(snapshot_dir, "app-dev", {"X": "new"})
    _write_snapshot(snapshot_dir, "app-staging", {"X": "old"})
    result = promote_snapshot(snapshot_dir, "app-dev", target_stage="staging", overwrite=True)
    assert result.ok
    dest = json.loads((snapshot_dir / "app-staging.json").read_text())
    assert dest["env"]["X"] == "new"


def test_promote_unknown_stage_returns_error(snapshot_dir):
    _write_snapshot(snapshot_dir, "app-dev", {"K": "v"})
    result = promote_snapshot(snapshot_dir, "app-dev", target_stage="canary")
    assert not result.ok
    assert "Unknown stage" in result.error


def test_promote_at_final_stage_without_target_returns_error(snapshot_dir):
    _write_snapshot(snapshot_dir, "app-prod", {"K": "v"})
    result = promote_snapshot(snapshot_dir, "app-prod")
    assert not result.ok
    assert "Cannot determine" in result.error
