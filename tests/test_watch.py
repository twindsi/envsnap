"""Tests for envsnap.watch module."""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from envsnap.watch import WatchConfig, WatchSession, start_watch, _snapshot_env


@pytest.fixture
def snapshot_dir(tmp_path):
    d = tmp_path / ".envsnap"
    d.mkdir()
    return str(d)


def test_watch_config_defaults():
    cfg = WatchConfig()
    assert cfg.interval == 5.0
    assert cfg.prefix is None
    assert cfg.on_change is None
    assert cfg.max_events == 0


def test_watch_session_stop():
    session = WatchSession(name="test", config=WatchConfig())
    session._running = True
    session.stop()
    assert session._running is False


def test_snapshot_env_returns_dict():
    with patch("envsnap.watch.capture") as mock_capture:
        mock_capture.return_value = {"name": "_watch_internal", "vars": {"FOO": "bar"}}
        result = _snapshot_env(prefix=None)
    assert result == {"FOO": "bar"}


def test_snapshot_env_with_prefix():
    with patch("envsnap.watch.capture") as mock_capture:
        mock_capture.return_value = {"name": "_watch_internal", "vars": {"MY_KEY": "val"}}
        result = _snapshot_env(prefix="MY_")
    mock_capture.assert_called_once_with(name="_watch_internal", prefix="MY_")
    assert "MY_KEY" in result


def test_start_watch_detects_change(snapshot_dir):
    call_count = {"n": 0}
    envs = [
        {"FOO": "1"},
        {"FOO": "2"},  # change detected
    ]

    def fake_snapshot(prefix):
        idx = min(call_count["n"], len(envs) - 1)
        call_count["n"] += 1
        return envs[idx]

    changes = []
    cfg = WatchConfig(interval=0, max_events=1, on_change=lambda d: changes.append(d))

    with patch("envsnap.watch._snapshot_env", side_effect=fake_snapshot), \
         patch("envsnap.watch.time.sleep"), \
         patch("envsnap.watch.record_event"):
        session = start_watch("proj", config=cfg, snapshot_dir=snapshot_dir)

    assert len(session.events) == 1
    assert session.events[0]["changed"].get("FOO") == ("1", "2")
    assert len(changes) == 1


def test_start_watch_no_change(snapshot_dir):
    call_count = {"n": 0}
    static_env = {"FOO": "1"}

    def fake_snapshot(prefix):
        call_count["n"] += 1
        if call_count["n"] > 2:
            # force stop via side-effect by exhausting
            raise StopIteration
        return static_env

    cfg = WatchConfig(interval=0, max_events=0)
    session = WatchSession(name="proj", config=cfg)
    session._running = True

    poll_count = {"n": 0}

    def fake_sleep(_):
        poll_count["n"] += 1
        if poll_count["n"] >= 3:
            session.stop()

    with patch("envsnap.watch._snapshot_env", return_value=static_env), \
         patch("envsnap.watch.time.sleep", side_effect=fake_sleep), \
         patch("envsnap.watch.record_event") as mock_record, \
         patch("envsnap.watch.WatchSession", return_value=session):
        result = start_watch("proj", config=cfg, snapshot_dir=snapshot_dir)

    assert len(result.events) == 0
    mock_record.assert_not_called()
