"""Tests for envsnap.cli_archive."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from envsnap.cli_archive import cmd_archive
from envsnap.archive import archive_snapshots


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write_snapshot(directory: Path, name: str, env: dict) -> Path:
    p = directory / f"{name}.json"
    p.write_text(json.dumps({"name": name, "env": env}))
    return p


def _make_args(snapshot_dir, archive_cmd, **kwargs):
    return SimpleNamespace(snapshot_dir=str(snapshot_dir), archive_cmd=archive_cmd, **kwargs)


def test_cmd_archive_create_prints_ok(snapshot_dir, tmp_path, capsys):
    _write_snapshot(snapshot_dir, "snap1", {"X": "1"})
    dest = str(tmp_path / "out.zip")
    args = _make_args(snapshot_dir, "create", dest=dest, names=["snap1"])
    cmd_archive(args)
    out = capsys.readouterr().out
    assert "[ok]" in out
    assert "snap1" in out


def test_cmd_archive_create_missing_snapshot_exits(snapshot_dir, tmp_path):
    dest = str(tmp_path / "out.zip")
    args = _make_args(snapshot_dir, "create", dest=dest, names=["ghost"])
    with pytest.raises(SystemExit):
        cmd_archive(args)


def test_cmd_archive_restore_prints_ok(snapshot_dir, tmp_path, capsys):
    _write_snapshot(snapshot_dir, "snap1", {"X": "1"})
    archive_path = tmp_path / "bundle.zip"
    archive_snapshots(snapshot_dir, ["snap1"], archive_path)

    restore_dir = tmp_path / "restored"
    args = _make_args(restore_dir, "restore", archive=str(archive_path), overwrite=False)
    cmd_archive(args)
    out = capsys.readouterr().out
    assert "[ok]" in out
    assert "snap1" in out


def test_cmd_archive_restore_missing_archive_exits(snapshot_dir, tmp_path):
    args = _make_args(snapshot_dir, "restore", archive=str(tmp_path / "nope.zip"), overwrite=False)
    with pytest.raises(SystemExit):
        cmd_archive(args)


def test_cmd_archive_list_prints_names(snapshot_dir, tmp_path, capsys):
    _write_snapshot(snapshot_dir, "snap1", {"X": "1"})
    _write_snapshot(snapshot_dir, "snap2", {"Y": "2"})
    archive_path = tmp_path / "bundle.zip"
    archive_snapshots(snapshot_dir, ["snap1", "snap2"], archive_path)

    args = _make_args(snapshot_dir, "list", archive=str(archive_path))
    cmd_archive(args)
    out = capsys.readouterr().out
    assert "snap1" in out
    assert "snap2" in out


def test_cmd_archive_list_missing_archive_exits(snapshot_dir, tmp_path):
    args = _make_args(snapshot_dir, "list", archive=str(tmp_path / "nope.zip"))
    with pytest.raises(SystemExit):
        cmd_archive(args)
