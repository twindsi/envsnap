"""Tests for envsnap.search module."""

import json
import pytest
from pathlib import Path

from envsnap.search import search_snapshots, search_by_key, search_by_value


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, vars: dict):
    data = {"name": name, "vars": vars}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(data))


def test_search_by_key_exact(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"FOO": "bar", "BAZ": "qux"})
    results = search_by_key(snapshot_dir, "FOO")
    assert len(results) == 1
    assert results[0].snapshot_name == "snap1"
    assert results[0].matches == {"FOO": "bar"}


def test_search_by_key_wildcard(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"DB_HOST": "localhost", "DB_PORT": "5432", "APP": "x"})
    results = search_by_key(snapshot_dir, "DB_*")
    assert len(results) == 1
    assert set(results[0].matches.keys()) == {"DB_HOST", "DB_PORT"}


def test_search_by_value(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"HOST": "localhost", "OTHER": "remote"})
    _write_snapshot(snapshot_dir, "snap2", {"HOST": "remote"})
    results = search_by_value(snapshot_dir, "localhost")
    assert len(results) == 1
    assert results[0].snapshot_name == "snap1"


def test_search_no_match_returns_empty(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"FOO": "bar"})
    results = search_by_key(snapshot_dir, "MISSING")
    assert results == []


def test_search_multiple_snapshots(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"SECRET": "abc"})
    _write_snapshot(snapshot_dir, "snap2", {"SECRET": "xyz", "OTHER": "val"})
    results = search_by_key(snapshot_dir, "SECRET")
    names = {r.snapshot_name for r in results}
    assert names == {"snap1", "snap2"}


def test_search_with_tag_filter(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"FOO": "bar"})
    _write_snapshot(snapshot_dir, "snap2", {"FOO": "bar"})
    tags_data = {"snap1": ["production"]}
    (snapshot_dir / ".tags.json").write_text(json.dumps(tags_data))
    results = search_snapshots(snapshot_dir, key_pattern="FOO", tag="production")
    assert len(results) == 1
    assert results[0].snapshot_name == "snap1"


def test_search_key_and_value_combined(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1", {"URL": "http://prod", "URL_BACKUP": "http://backup"})
    results = search_snapshots(snapshot_dir, key_pattern="URL", value_pattern="http://prod")
    assert len(results) == 1
    assert list(results[0].matches.keys()) == ["URL"]
