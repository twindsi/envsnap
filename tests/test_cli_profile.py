"""Tests for envsnap/cli_profile.py"""

import json
import argparse
import pytest
from pathlib import Path

from envsnap.cli_profile import cmd_profile


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, env: dict = None) -> None:
    data = {"name": name, "env": env or {}}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(data))


def _make_args(snapshot_dir: Path, profile_action: str, profile: str = None,
               snapshot: str = None) -> argparse.Namespace:
    return argparse.Namespace(
        snapshot_dir=str(snapshot_dir),
        profile_action=profile_action,
        profile=profile,
        snapshot=snapshot,
    )


def test_cmd_profile_add_prints_ok(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "dev")
    args = _make_args(snapshot_dir, "add", profile="web", snapshot="dev")
    cmd_profile(args)
    out = capsys.readouterr().out
    assert "[ok]" in out
    assert "dev" in out


def test_cmd_profile_add_missing_snapshot_prints_error(snapshot_dir, capsys):
    args = _make_args(snapshot_dir, "add", profile="web", snapshot="ghost")
    cmd_profile(args)
    out = capsys.readouterr().out
    assert "[error]" in out


def test_cmd_profile_remove_prints_ok(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "dev")
    add_args = _make_args(snapshot_dir, "add", profile="web", snapshot="dev")
    cmd_profile(add_args)
    rm_args = _make_args(snapshot_dir, "remove", profile="web", snapshot="dev")
    cmd_profile(rm_args)
    out = capsys.readouterr().out
    assert "[ok]" in out


def test_cmd_profile_show_lists_members(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "staging")
    cmd_profile(_make_args(snapshot_dir, "add", profile="proj", snapshot="staging"))
    capsys.readouterr()  # clear
    cmd_profile(_make_args(snapshot_dir, "show", profile="proj"))
    out = capsys.readouterr().out
    assert "staging" in out


def test_cmd_profile_show_missing_profile_prints_error(snapshot_dir, capsys):
    cmd_profile(_make_args(snapshot_dir, "show", profile="nope"))
    out = capsys.readouterr().out
    assert "[error]" in out


def test_cmd_profile_list_empty(snapshot_dir, capsys):
    cmd_profile(_make_args(snapshot_dir, "list"))
    out = capsys.readouterr().out
    assert "No profiles" in out


def test_cmd_profile_list_shows_all(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "alpha")
    _write_snapshot(snapshot_dir, "beta")
    cmd_profile(_make_args(snapshot_dir, "add", profile="g1", snapshot="alpha"))
    cmd_profile(_make_args(snapshot_dir, "add", profile="g2", snapshot="beta"))
    capsys.readouterr()
    cmd_profile(_make_args(snapshot_dir, "list"))
    out = capsys.readouterr().out
    assert "g1" in out
    assert "g2" in out
