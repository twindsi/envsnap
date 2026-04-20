"""Tests for envsnap.validate module."""

import json
import os
import pytest

from envsnap.validate import validate_snapshot, ValidationResult


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(directory: str, name: str, vars_: dict) -> None:
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as fh:
        json.dump({"name": name, "vars": vars_}, fh)


def test_validate_all_required_keys_present(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"FOO": "bar", "BAZ": "qux"})
    result = validate_snapshot(snapshot_dir, "snap1", required_keys=["FOO", "BAZ"])
    assert result.valid
    assert result.missing_keys == []


def test_validate_missing_required_key(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap2", {"FOO": "bar"})
    result = validate_snapshot(snapshot_dir, "snap2", required_keys=["FOO", "MISSING"])
    assert not result.valid
    assert "MISSING" in result.missing_keys


def test_validate_key_pattern_all_match(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap3", {"APP_HOST": "localhost", "APP_PORT": "8080"})
    result = validate_snapshot(snapshot_dir, "snap3", key_pattern=r"APP_[A-Z]+")
    assert result.valid
    assert result.invalid_keys == []


def test_validate_key_pattern_some_invalid(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap4", {"APP_HOST": "localhost", "debug": "true"})
    result = validate_snapshot(snapshot_dir, "snap4", key_pattern=r"[A-Z_]+")
    assert not result.valid
    assert "debug" in result.invalid_keys


def test_validate_value_pattern_match(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap5", {"PORT": "8080", "TIMEOUT": "30"})
    result = validate_snapshot(snapshot_dir, "snap5", value_pattern=r"\d+")
    assert result.valid
    assert result.errors == []


def test_validate_value_pattern_mismatch(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap6", {"PORT": "8080", "HOST": "localhost"})
    result = validate_snapshot(snapshot_dir, "snap6", value_pattern=r"\d+")
    assert not result.valid
    assert any("HOST" in e for e in result.errors)


def test_validate_missing_snapshot(snapshot_dir):
    result = validate_snapshot(snapshot_dir, "nonexistent")
    assert not result.valid
    assert any("not found" in e for e in result.errors)


def test_validate_combined_constraints(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap7", {"DB_HOST": "db.local", "DB_PORT": "5432"})
    result = validate_snapshot(
        snapshot_dir,
        "snap7",
        required_keys=["DB_HOST", "DB_PORT"],
        key_pattern=r"DB_[A-Z]+",
    )
    assert result.valid


def test_validation_result_repr_pass(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap8", {"KEY": "val"})
    result = validate_snapshot(snapshot_dir, "snap8", required_keys=["KEY"])
    assert "PASS" in repr(result)


def test_validation_result_repr_fail(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap9", {})
    result = validate_snapshot(snapshot_dir, "snap9", required_keys=["REQUIRED"])
    assert "FAIL" in repr(result)
