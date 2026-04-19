"""Tests for envsnap.restore module."""

import json
import os
import pytest

from envsnap.restore import restore_snapshot, export_shell_script


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(directory: str, name: str, vars: dict):
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as f:
        json.dump({"name": name, "vars": vars}, f)


def test_restore_applies_variables(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"FOO": "bar", "BAZ": "qux"})
    result = restore_snapshot("mysnap", snapshot_dir, overwrite=True)
    assert os.environ["FOO"] == "bar"
    assert os.environ["BAZ"] == "qux"
    assert result.applied == {"FOO": "bar", "BAZ": "qux"}
    assert result.skipped == {}


def test_restore_skips_existing_without_overwrite(snapshot_dir):
    os.environ["EXISTING_VAR"] = "original"
    _write_snapshot(snapshot_dir, "snap2", {"EXISTING_VAR": "new_value", "NEW_VAR": "hello"})
    result = restore_snapshot("snap2", snapshot_dir, overwrite=False)
    assert os.environ["EXISTING_VAR"] == "original"
    assert os.environ["NEW_VAR"] == "hello"
    assert "EXISTING_VAR" in result.skipped
    assert "NEW_VAR" in result.applied


def test_restore_with_overwrite(snapshot_dir):
    os.environ["OVER_VAR"] = "old"
    _write_snapshot(snapshot_dir, "snap3", {"OVER_VAR": "new"})
    result = restore_snapshot("snap3", snapshot_dir, overwrite=True)
    assert os.environ["OVER_VAR"] == "new"
    assert result.applied == {"OVER_VAR": "new"}


def test_restore_with_prefix(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap4", {"APP_HOST": "localhost", "DB_HOST": "db"})
    result = restore_snapshot("snap4", snapshot_dir, overwrite=True, prefix="APP_")
    assert os.environ["APP_HOST"] == "localhost"
    assert result.applied == {"APP_HOST": "localhost"}
    assert "DB_HOST" not in result.applied


def test_restore_result_repr(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap5", {"X": "1"})
    result = restore_snapshot("snap5", snapshot_dir, overwrite=True)
    assert "snap5" in repr(result)


def test_export_shell_script(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap6", {"HELLO": "world", "NUM": "42"})
    script = export_shell_script("snap6", snapshot_dir)
    assert "export HELLO='world'" in script
    assert "export NUM='42'" in script


def test_export_shell_script_with_prefix(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap7", {"APP_KEY": "abc", "OTHER": "xyz"})
    script = export_shell_script("snap7", snapshot_dir, prefix="APP_")
    assert "APP_KEY" in script
    assert "OTHER" not in script
