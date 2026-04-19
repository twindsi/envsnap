"""Tests for envsnap.diff module."""

import json
import os
import pytest

from envsnap.diff import diff_envs, diff_snapshots, DiffResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(directory: str, name: str, env: dict) -> None:
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as fh:
        json.dump({"name": name, "env": env}, fh)


# ---------------------------------------------------------------------------
# diff_envs tests
# ---------------------------------------------------------------------------

def test_diff_envs_no_changes():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = diff_envs(env, env.copy())
    assert not result.has_changes


def test_diff_envs_added():
    result = diff_envs({"A": "1"}, {"A": "1", "B": "2"})
    assert result.added == {"B": "2"}
    assert not result.removed
    assert not result.changed


def test_diff_envs_removed():
    result = diff_envs({"A": "1", "B": "2"}, {"A": "1"})
    assert result.removed == {"B": "2"}
    assert not result.added
    assert not result.changed


def test_diff_envs_changed():
    result = diff_envs({"A": "old"}, {"A": "new"})
    assert result.changed == {"A": ("old", "new")}
    assert not result.added
    assert not result.removed


def test_diff_envs_mixed():
    env_a = {"KEEP": "same", "REMOVE": "gone", "CHANGE": "v1"}
    env_b = {"KEEP": "same", "ADD": "here", "CHANGE": "v2"}
    result = diff_envs(env_a, env_b)
    assert result.added == {"ADD": "here"}
    assert result.removed == {"REMOVE": "gone"}
    assert result.changed == {"CHANGE": ("v1", "v2")}
    assert result.has_changes


# ---------------------------------------------------------------------------
# DiffResult.summary tests
# ---------------------------------------------------------------------------

def test_summary_no_changes():
    result = DiffResult()
    assert result.summary() == "No differences found."


def test_summary_contains_symbols():
    result = diff_envs({"OLD": "x"}, {"NEW": "y"})
    summary = result.summary()
    assert "+ NEW=y" in summary
    assert "- OLD=x" in summary


# ---------------------------------------------------------------------------
# diff_snapshots tests
# ---------------------------------------------------------------------------

def test_diff_snapshots(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"X": "1"})
    _write_snapshot(snapshot_dir, "snap2", {"X": "2", "Y": "3"})
    result = diff_snapshots("snap1", "snap2", snapshot_dir=snapshot_dir)
    assert result.changed == {"X": ("1", "2")}
    assert result.added == {"Y": "3"}
