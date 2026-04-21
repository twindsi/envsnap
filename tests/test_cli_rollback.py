"""Tests for envsnap.cli_rollback."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

from envsnap.cli_rollback import cmd_rollback, add_rollback_subparser


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, env: dict) -> None:
    data = {"name": name, "env": env}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(data))


def _write_history(snapshot_dir: Path, events: list) -> None:
    (snapshot_dir / "history.json").write_text(json.dumps(events))


def _make_args(snapshot_dir: Path, name: str, steps: int = 1, verbose: bool = False) -> argparse.Namespace:
    return argparse.Namespace(
        name=name,
        steps=steps,
        snapshot_dir=str(snapshot_dir),
        verbose=verbose,
    )


def test_cmd_rollback_prints_success(snapshot_dir: Path, capsys) -> None:
    env_v1 = {"A": "1"}
    env_v2 = {"A": "2"}
    _write_snapshot(snapshot_dir, "snap", env_v2)
    _write_history(snapshot_dir, [
        {"name": "snap", "event": "capture", "timestamp": "2024-01-01T00:00:00", "env": env_v1},
        {"name": "snap", "event": "capture", "timestamp": "2024-01-02T00:00:00", "env": env_v2},
    ])

    cmd_rollback(_make_args(snapshot_dir, "snap", steps=1))

    out = capsys.readouterr().out
    assert "snap" in out
    assert "2024-01-01T00:00:00" in out


def test_cmd_rollback_verbose_prints_vars(snapshot_dir: Path, capsys) -> None:
    env_v1 = {"MYVAR": "hello"}
    env_v2 = {"MYVAR": "world"}
    _write_snapshot(snapshot_dir, "snap", env_v2)
    _write_history(snapshot_dir, [
        {"name": "snap", "event": "capture", "timestamp": "t1", "env": env_v1},
        {"name": "snap", "event": "capture", "timestamp": "t2", "env": env_v2},
    ])

    cmd_rollback(_make_args(snapshot_dir, "snap", steps=1, verbose=True))

    out = capsys.readouterr().out
    assert "MYVAR=hello" in out


def test_cmd_rollback_failure_exits(snapshot_dir: Path) -> None:
    _write_snapshot(snapshot_dir, "snap", {})
    _write_history(snapshot_dir, [])

    with pytest.raises(SystemExit) as exc_info:
        cmd_rollback(_make_args(snapshot_dir, "snap", steps=1))

    assert exc_info.value.code == 1


def test_add_rollback_subparser_registers_command() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_rollback_subparser(subparsers)

    args = parser.parse_args(["rollback", "mysnap", "--steps", "2"])
    assert args.name == "mysnap"
    assert args.steps == 2
    assert args.func is not None
