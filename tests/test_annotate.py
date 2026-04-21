"""Tests for envsnap.annotate."""

import json
import pytest
from pathlib import Path

from envsnap.annotate import (
    add_annotation,
    get_annotations,
    remove_annotation,
    clear_annotations,
    _annotations_path,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_snapshot(directory: Path, name: str, env: dict) -> None:
    snap = {"name": name, "env": env}
    (directory / f"{name}.json").write_text(json.dumps(snap))


def test_add_annotation_creates_entry(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {"FOO": "bar"})
    result = add_annotation(snapshot_dir, "dev", "initial setup")
    assert result is True
    notes = get_annotations(snapshot_dir, "dev")
    assert notes == ["initial setup"]


def test_add_multiple_annotations_appends(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {"FOO": "bar"})
    add_annotation(snapshot_dir, "dev", "first note")
    add_annotation(snapshot_dir, "dev", "second note")
    notes = get_annotations(snapshot_dir, "dev")
    assert notes == ["first note", "second note"]


def test_add_annotation_missing_snapshot_returns_false(snapshot_dir):
    result = add_annotation(snapshot_dir, "ghost", "hello")
    assert result is False


def test_get_annotations_missing_snapshot_returns_empty(snapshot_dir):
    notes = get_annotations(snapshot_dir, "nonexistent")
    assert notes == []


def test_remove_annotation_by_index(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {})
    add_annotation(snapshot_dir, "dev", "keep")
    add_annotation(snapshot_dir, "dev", "remove me")
    result = remove_annotation(snapshot_dir, "dev", 1)
    assert result is True
    assert get_annotations(snapshot_dir, "dev") == ["keep"]


def test_remove_annotation_out_of_range_returns_false(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {})
    add_annotation(snapshot_dir, "dev", "only note")
    result = remove_annotation(snapshot_dir, "dev", 5)
    assert result is False


def test_remove_last_annotation_cleans_up_entry(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {})
    add_annotation(snapshot_dir, "dev", "sole note")
    remove_annotation(snapshot_dir, "dev", 0)
    data = json.loads(_annotations_path(snapshot_dir).read_text())
    assert "dev" not in data


def test_clear_annotations_returns_count(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {})
    add_annotation(snapshot_dir, "dev", "a")
    add_annotation(snapshot_dir, "dev", "b")
    count = clear_annotations(snapshot_dir, "dev")
    assert count == 2
    assert get_annotations(snapshot_dir, "dev") == []


def test_clear_annotations_no_existing_returns_zero(snapshot_dir):
    count = clear_annotations(snapshot_dir, "nobody")
    assert count == 0


def test_annotations_persisted_to_file(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod", {"ENV": "production"})
    add_annotation(snapshot_dir, "prod", "live snapshot")
    raw = json.loads(_annotations_path(snapshot_dir).read_text())
    assert raw["prod"] == ["live snapshot"]
