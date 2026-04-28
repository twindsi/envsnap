"""Tests for envsnap.archive."""

import json
import zipfile
from pathlib import Path

import pytest

from envsnap.archive import archive_snapshots, restore_archive, list_archive


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / "snapshots"
    d.mkdir()
    return d


def _write_snapshot(directory: Path, name: str, env: dict) -> Path:
    p = directory / f"{name}.json"
    p.write_text(json.dumps({"name": name, "env": env}))
    return p


def test_archive_creates_zip(snapshot_dir, tmp_path):
    _write_snapshot(snapshot_dir, "alpha", {"A": "1"})
    _write_snapshot(snapshot_dir, "beta", {"B": "2"})
    dest = tmp_path / "bundle.zip"
    result = archive_snapshots(snapshot_dir, ["alpha", "beta"], dest)
    assert result.ok
    assert dest.exists()
    assert set(result.names) == {"alpha", "beta"}


def test_archive_no_names_returns_error(snapshot_dir, tmp_path):
    dest = tmp_path / "bundle.zip"
    result = archive_snapshots(snapshot_dir, [], dest)
    assert not result.ok
    assert "No snapshot names" in result.message


def test_archive_missing_snapshot_returns_error(snapshot_dir, tmp_path):
    _write_snapshot(snapshot_dir, "alpha", {"A": "1"})
    dest = tmp_path / "bundle.zip"
    result = archive_snapshots(snapshot_dir, ["alpha", "ghost"], dest)
    assert not result.ok
    assert "ghost" in result.message


def test_restore_archive_extracts_snapshots(snapshot_dir, tmp_path):
    _write_snapshot(snapshot_dir, "alpha", {"A": "1"})
    dest = tmp_path / "bundle.zip"
    archive_snapshots(snapshot_dir, ["alpha"], dest)

    restore_dir = tmp_path / "restored"
    result = restore_archive(dest, restore_dir)
    assert result.ok
    assert "alpha" in result.names
    assert (restore_dir / "alpha.json").exists()


def test_restore_archive_refuses_overwrite_by_default(snapshot_dir, tmp_path):
    _write_snapshot(snapshot_dir, "alpha", {"A": "1"})
    dest = tmp_path / "bundle.zip"
    archive_snapshots(snapshot_dir, ["alpha"], dest)

    restore_dir = tmp_path / "restored"
    restore_dir.mkdir()
    (restore_dir / "alpha.json").write_text("{}")

    result = restore_archive(dest, restore_dir, overwrite=False)
    assert not result.ok
    assert "already exists" in result.message


def test_restore_archive_overwrite_flag(snapshot_dir, tmp_path):
    _write_snapshot(snapshot_dir, "alpha", {"A": "1"})
    dest = tmp_path / "bundle.zip"
    archive_snapshots(snapshot_dir, ["alpha"], dest)

    restore_dir = tmp_path / "restored"
    restore_dir.mkdir()
    (restore_dir / "alpha.json").write_text("{}")

    result = restore_archive(dest, restore_dir, overwrite=True)
    assert result.ok


def test_restore_archive_missing_file(tmp_path):
    result = restore_archive(tmp_path / "nope.zip", tmp_path / "out")
    assert not result.ok
    assert "not found" in result.message


def test_list_archive_returns_names(snapshot_dir, tmp_path):
    _write_snapshot(snapshot_dir, "alpha", {"A": "1"})
    _write_snapshot(snapshot_dir, "beta", {"B": "2"})
    dest = tmp_path / "bundle.zip"
    archive_snapshots(snapshot_dir, ["alpha", "beta"], dest)
    names = list_archive(dest)
    assert set(names) == {"alpha", "beta"}


def test_list_archive_missing_returns_none(tmp_path):
    assert list_archive(tmp_path / "nope.zip") is None
