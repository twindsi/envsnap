"""Tests for envsnap.history module."""

import pytest
from pathlib import Path
from envsnap.history import record_event, get_history, clear_history, recent


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def test_record_event_creates_entry(snapshot_dir):
    record_event(snapshot_dir, "mysnap", "capture")
    history = get_history(snapshot_dir)
    assert len(history) == 1
    assert history[0]["snapshot"] == "mysnap"
    assert history[0]["action"] == "capture"
    assert "timestamp" in history[0]


def test_multiple_events_appended(snapshot_dir):
    record_event(snapshot_dir, "snap1", "capture")
    record_event(snapshot_dir, "snap1", "restore")
    record_event(snapshot_dir, "snap2", "export")
    assert len(get_history(snapshot_dir)) == 3


def test_get_history_filtered_by_name(snapshot_dir):
    record_event(snapshot_dir, "snap1", "capture")
    record_event(snapshot_dir, "snap2", "restore")
    result = get_history(snapshot_dir, snapshot_name="snap1")
    assert len(result) == 1
    assert result[0]["snapshot"] == "snap1"


def test_get_history_empty(snapshot_dir):
    assert get_history(snapshot_dir) == []


def test_clear_history_all(snapshot_dir):
    record_event(snapshot_dir, "snap1", "capture")
    record_event(snapshot_dir, "snap2", "capture")
    removed = clear_history(snapshot_dir)
    assert removed == 2
    assert get_history(snapshot_dir) == []


def test_clear_history_by_name(snapshot_dir):
    record_event(snapshot_dir, "snap1", "capture")
    record_event(snapshot_dir, "snap2", "capture")
    removed = clear_history(snapshot_dir, snapshot_name="snap1")
    assert removed == 1
    remaining = get_history(snapshot_dir)
    assert len(remaining) == 1
    assert remaining[0]["snapshot"] == "snap2"


def test_recent_returns_last_n(snapshot_dir):
    for i in range(15):
        record_event(snapshot_dir, f"snap{i}", "capture")
    result = recent(snapshot_dir, limit=5)
    assert len(result) == 5
    assert result[-1]["snapshot"] == "snap14"


def test_recent_default_limit(snapshot_dir):
    for i in range(12):
        record_event(snapshot_dir, f"snap{i}", "capture")
    result = recent(snapshot_dir)
    assert len(result) == 10
