"""Tests for envsnap/audit.py"""

import pytest
import json
from pathlib import Path
from envsnap.audit import record_audit, get_audit_log, clear_audit_log, _audit_path


@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / "snapshots"
    d.mkdir()
    return str(d)


def test_record_audit_creates_entry(snapshot_dir):
    entry = record_audit(snapshot_dir, "capture", "mysnap")
    assert entry["action"] == "capture"
    assert entry["snapshot"] == "mysnap"
    assert "timestamp" in entry
    assert "user" in entry


def test_record_audit_persists_to_file(snapshot_dir):
    record_audit(snapshot_dir, "delete", "oldsnap", details="manual cleanup")
    path = _audit_path(snapshot_dir)
    assert path.exists()
    with open(path) as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["details"] == "manual cleanup"


def test_multiple_events_appended(snapshot_dir):
    record_audit(snapshot_dir, "capture", "snap1")
    record_audit(snapshot_dir, "restore", "snap1")
    record_audit(snapshot_dir, "export", "snap2")
    log = get_audit_log(snapshot_dir)
    assert len(log) == 3


def test_get_audit_log_filtered_by_snapshot(snapshot_dir):
    record_audit(snapshot_dir, "capture", "alpha")
    record_audit(snapshot_dir, "capture", "beta")
    record_audit(snapshot_dir, "delete", "alpha")
    results = get_audit_log(snapshot_dir, snapshot_name="alpha")
    assert len(results) == 2
    assert all(e["snapshot"] == "alpha" for e in results)


def test_get_audit_log_filtered_by_action(snapshot_dir):
    record_audit(snapshot_dir, "capture", "snap1")
    record_audit(snapshot_dir, "restore", "snap1")
    record_audit(snapshot_dir, "capture", "snap2")
    results = get_audit_log(snapshot_dir, action="capture")
    assert len(results) == 2
    assert all(e["action"] == "capture" for e in results)


def test_get_audit_log_empty(snapshot_dir):
    results = get_audit_log(snapshot_dir)
    assert results == []


def test_clear_audit_log_returns_count(snapshot_dir):
    record_audit(snapshot_dir, "capture", "snap1")
    record_audit(snapshot_dir, "capture", "snap2")
    count = clear_audit_log(snapshot_dir)
    assert count == 2


def test_clear_audit_log_empties_file(snapshot_dir):
    record_audit(snapshot_dir, "capture", "snap1")
    clear_audit_log(snapshot_dir)
    log = get_audit_log(snapshot_dir)
    assert log == []


def test_audit_entry_has_all_fields(snapshot_dir):
    entry = record_audit(snapshot_dir, "rename", "mysnap", details="renamed to newsnap")
    for field in ("timestamp", "user", "action", "snapshot", "details"):
        assert field in entry
