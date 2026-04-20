"""Tests for envsnap/schedule.py"""

import pytest
from envsnap.schedule import (
    Schedule,
    add_schedule,
    remove_schedule,
    get_schedule,
    list_schedules,
    toggle_schedule,
)


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def test_add_schedule_creates_entry(snapshot_dir):
    s = Schedule(name="nightly", interval="daily", prefix="APP_")
    add_schedule(snapshot_dir, s)
    result = get_schedule(snapshot_dir, "nightly")
    assert result is not None
    assert result.interval == "daily"
    assert result.prefix == "APP_"
    assert result.enabled is True


def test_add_schedule_invalid_interval(snapshot_dir):
    s = Schedule(name="bad", interval="monthly")
    with pytest.raises(ValueError, match="Invalid interval"):
        add_schedule(snapshot_dir, s)


def test_remove_schedule_existing(snapshot_dir):
    s = Schedule(name="weekly_snap", interval="weekly")
    add_schedule(snapshot_dir, s)
    removed = remove_schedule(snapshot_dir, "weekly_snap")
    assert removed is True
    assert get_schedule(snapshot_dir, "weekly_snap") is None


def test_remove_schedule_missing(snapshot_dir):
    removed = remove_schedule(snapshot_dir, "nonexistent")
    assert removed is False


def test_list_schedules_empty(snapshot_dir):
    assert list_schedules(snapshot_dir) == []


def test_list_schedules_multiple(snapshot_dir):
    add_schedule(snapshot_dir, Schedule(name="a", interval="hourly"))
    add_schedule(snapshot_dir, Schedule(name="b", interval="daily"))
    results = list_schedules(snapshot_dir)
    names = {s.name for s in results}
    assert names == {"a", "b"}


def test_toggle_schedule_disable(snapshot_dir):
    add_schedule(snapshot_dir, Schedule(name="tog", interval="daily"))
    ok = toggle_schedule(snapshot_dir, "tog", enabled=False)
    assert ok is True
    assert get_schedule(snapshot_dir, "tog").enabled is False


def test_toggle_schedule_missing(snapshot_dir):
    ok = toggle_schedule(snapshot_dir, "ghost", enabled=True)
    assert ok is False


def test_add_schedule_overwrites_existing(snapshot_dir):
    add_schedule(snapshot_dir, Schedule(name="snap", interval="daily"))
    add_schedule(snapshot_dir, Schedule(name="snap", interval="weekly"))
    result = get_schedule(snapshot_dir, "snap")
    assert result.interval == "weekly"
