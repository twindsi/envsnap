"""Tests for envsnap/cli_schedule.py"""

import argparse
import pytest
from envsnap.cli_schedule import cmd_schedule
from envsnap.schedule import add_schedule, Schedule, get_schedule


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"schedule_cmd": None, "name": None, "interval": None, "prefix": None}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_schedule_add(snapshot_dir, capsys):
    args = _make_args(schedule_cmd="add", name="ci", interval="daily", prefix="CI_")
    cmd_schedule(args, snapshot_dir)
    out = capsys.readouterr().out
    assert "added" in out
    s = get_schedule(snapshot_dir, "ci")
    assert s is not None
    assert s.prefix == "CI_"


def test_cmd_schedule_add_invalid_interval(snapshot_dir, capsys):
    args = _make_args(schedule_cmd="add", name="bad", interval="monthly")
    cmd_schedule(args, snapshot_dir)
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_schedule_list_empty(snapshot_dir, capsys):
    args = _make_args(schedule_cmd="list")
    cmd_schedule(args, snapshot_dir)
    out = capsys.readouterr().out
    assert "No schedules" in out


def test_cmd_schedule_list_shows_entries(snapshot_dir, capsys):
    add_schedule(snapshot_dir, Schedule(name="s1", interval="hourly"))
    args = _make_args(schedule_cmd="list")
    cmd_schedule(args, snapshot_dir)
    out = capsys.readouterr().out
    assert "s1" in out
    assert "hourly" in out


def test_cmd_schedule_remove_existing(snapshot_dir, capsys):
    add_schedule(snapshot_dir, Schedule(name="rm_me", interval="weekly"))
    args = _make_args(schedule_cmd="remove", name="rm_me")
    cmd_schedule(args, snapshot_dir)
    out = capsys.readouterr().out
    assert "removed" in out


def test_cmd_schedule_remove_missing(snapshot_dir, capsys):
    args = _make_args(schedule_cmd="remove", name="ghost")
    cmd_schedule(args, snapshot_dir)
    out = capsys.readouterr().out
    assert "No schedule" in out


def test_cmd_schedule_disable_and_enable(snapshot_dir, capsys):
    add_schedule(snapshot_dir, Schedule(name="tog", interval="daily"))
    cmd_schedule(_make_args(schedule_cmd="disable", name="tog"), snapshot_dir)
    assert get_schedule(snapshot_dir, "tog").enabled is False
    cmd_schedule(_make_args(schedule_cmd="enable", name="tog"), snapshot_dir)
    assert get_schedule(snapshot_dir, "tog").enabled is True
