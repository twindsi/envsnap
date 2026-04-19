import json
import os
import pytest
from envsnap.compare import compare_snapshots, format_compare_table


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(snapshot_dir, name, vars_):
    path = os.path.join(snapshot_dir, f"{name}.json")
    with open(path, "w") as f:
        json.dump({"name": name, "vars": vars_}, f)


def test_compare_all_same(snapshot_dir):
    _write_snapshot(snapshot_dir, "a", {"X": "1"})
    _write_snapshot(snapshot_dir, "b", {"X": "1"})
    result = compare_snapshots(snapshot_dir, ["a", "b"])
    assert result.divergent_keys() == []
    assert "X" in result.common_keys()


def test_compare_divergent(snapshot_dir):
    _write_snapshot(snapshot_dir, "a", {"X": "1"})
    _write_snapshot(snapshot_dir, "b", {"X": "2"})
    result = compare_snapshots(snapshot_dir, ["a", "b"])
    assert "X" in result.divergent_keys()


def test_compare_missing_key(snapshot_dir):
    _write_snapshot(snapshot_dir, "a", {"X": "1", "Y": "2"})
    _write_snapshot(snapshot_dir, "b", {"X": "1"})
    result = compare_snapshots(snapshot_dir, ["a", "b"])
    assert "Y" in result.divergent_keys()
    assert result.table["Y"]["b"] is None


def test_compare_three_snapshots(snapshot_dir):
    _write_snapshot(snapshot_dir, "a", {"X": "1"})
    _write_snapshot(snapshot_dir, "b", {"X": "1"})
    _write_snapshot(snapshot_dir, "c", {"X": "3"})
    result = compare_snapshots(snapshot_dir, ["a", "b", "c"])
    assert "X" in result.divergent_keys()


def test_format_table_contains_names(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"FOO": "bar"})
    _write_snapshot(snapshot_dir, "snap2", {"FOO": "baz"})
    result = compare_snapshots(snapshot_dir, ["snap1", "snap2"])
    table_str = format_compare_table(result)
    assert "snap1" in table_str
    assert "snap2" in table_str
    assert "FOO" in table_str
