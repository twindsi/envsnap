"""Tests for envsnap.merge."""

import json
import os
import pytest

from envsnap.merge import merge_snapshots, MergeResult


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(snapshot_dir: str, name: str, env: dict) -> None:
    path = os.path.join(snapshot_dir, f"{name}.json")
    with open(path, "w") as fh:
        json.dump({"name": name, "env": env}, fh)


def test_merge_combines_disjoint_keys(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"A": "1", "B": "2"})
    _write_snapshot(snapshot_dir, "overlay", {"C": "3", "D": "4"})

    result = merge_snapshots(snapshot_dir, "base", "overlay", "merged")

    assert result.merged == {"A": "1", "B": "2", "C": "3", "D": "4"}
    assert result.conflicts == []
    assert result.overwritten == []


def test_merge_detects_conflicts(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"A": "base_val"})
    _write_snapshot(snapshot_dir, "overlay", {"A": "overlay_val"})

    result = merge_snapshots(snapshot_dir, "base", "overlay", "merged", overwrite=False)

    assert "A" in result.conflicts
    assert result.merged["A"] == "base_val"  # base wins
    assert result.overwritten == []


def test_merge_overwrite_flag(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"A": "base_val"})
    _write_snapshot(snapshot_dir, "overlay", {"A": "overlay_val"})

    result = merge_snapshots(snapshot_dir, "base", "overlay", "merged", overwrite=True)

    assert result.merged["A"] == "overlay_val"
    assert "A" in result.overwritten


def test_merge_saves_result_file(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"X": "1"})
    _write_snapshot(snapshot_dir, "overlay", {"Y": "2"})

    merge_snapshots(snapshot_dir, "base", "overlay", "out")

    out_path = os.path.join(snapshot_dir, "out.json")
    assert os.path.exists(out_path)
    with open(out_path) as fh:
        data = json.load(fh)
    assert data["env"]["X"] == "1"
    assert data["env"]["Y"] == "2"


def test_merge_result_repr(snapshot_dir):
    _write_snapshot(snapshot_dir, "b", {"K": "v"})
    _write_snapshot(snapshot_dir, "o", {})
    result = merge_snapshots(snapshot_dir, "b", "o", "r")
    assert isinstance(repr(result), str)


def test_merge_missing_snapshot_raises(snapshot_dir):
    _write_snapshot(snapshot_dir, "base", {"A": "1"})
    with pytest.raises(Exception):
        merge_snapshots(snapshot_dir, "base", "nonexistent", "out")
