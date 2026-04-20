"""Tests for envsnap.cli_validate module."""

import argparse
import json
import os
import sys
import pytest

from envsnap.cli_validate import cmd_validate, add_validate_subparser


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(directory: str, name: str, vars_: dict) -> None:
    path = os.path.join(directory, f"{name}.json")
    with open(path, "w") as fh:
        json.dump({"name": name, "vars": vars_}, fh)


def _make_args(snapshot_dir, name, require="", key_pattern="", value_pattern=""):
    return argparse.Namespace(
        snapshot_dir=snapshot_dir,
        name=name,
        require=require,
        key_pattern=key_pattern,
        value_pattern=value_pattern,
    )


def test_cmd_validate_pass(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "mysnap", {"FOO": "bar"})
    args = _make_args(snapshot_dir, "mysnap", require="FOO")
    with pytest.raises(SystemExit) as exc:
        cmd_validate(args)
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "PASS" in captured.out


def test_cmd_validate_fail_missing_key(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "mysnap2", {"FOO": "bar"})
    args = _make_args(snapshot_dir, "mysnap2", require="FOO,MISSING")
    with pytest.raises(SystemExit) as exc:
        cmd_validate(args)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "FAIL" in captured.out
    assert "MISSING" in captured.out


def test_cmd_validate_fail_invalid_key_pattern(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "mysnap3", {"lowercase": "val"})
    args = _make_args(snapshot_dir, "mysnap3", key_pattern=r"[A-Z_]+")
    with pytest.raises(SystemExit) as exc:
        cmd_validate(args)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "lowercase" in captured.out


def test_cmd_validate_nonexistent_snapshot(snapshot_dir, capsys):
    args = _make_args(snapshot_dir, "ghost")
    with pytest.raises(SystemExit) as exc:
        cmd_validate(args)
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_add_validate_subparser_registers_command():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    add_validate_subparser(subparsers)
    args = parser.parse_args(["validate", "mysnap", "--require", "FOO,BAR"])
    assert args.name == "mysnap"
    assert args.require == "FOO,BAR"
    assert callable(args.func)
