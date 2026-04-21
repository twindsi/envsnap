"""Tests for envsnap.cli_encrypt."""

import json
import argparse
from pathlib import Path

import pytest

from envsnap.cli_encrypt import cmd_decrypt, cmd_encrypt
from envsnap.encrypt import _MARKER, encrypt_snapshot

SECRET = "testkey123"


@pytest.fixture()
def snapshot_dir(tmp_path: Path) -> Path:
    d = tmp_path / ".envsnap"
    d.mkdir()
    return d


def _write_snapshot(snap_dir: Path, data: dict) -> None:
    path = snap_dir / f"{data['name']}.json"
    path.write_text(json.dumps(data))


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {"name": "mysnap", "dir": "", "key": SECRET}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_cmd_encrypt_encrypts_snapshot(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, {"name": "mysnap", "vars": {"A": "1"}, "encrypted": False})
    args = _make_args(dir=str(snapshot_dir))
    cmd_encrypt(args)
    out = capsys.readouterr().out
    assert "encrypted successfully" in out
    data = json.loads((snapshot_dir / "mysnap.json").read_text())
    assert data["encrypted"] is True
    assert data["vars"]["A"].startswith(_MARKER)


def test_cmd_encrypt_already_encrypted(snapshot_dir, capsys):
    snap = {"name": "mysnap", "vars": {"A": "1"}, "encrypted": False}
    encrypted = encrypt_snapshot(snap, key=SECRET)
    _write_snapshot(snapshot_dir, encrypted)
    args = _make_args(dir=str(snapshot_dir))
    cmd_encrypt(args)
    out = capsys.readouterr().out
    assert "already encrypted" in out


def test_cmd_decrypt_decrypts_snapshot(snapshot_dir, capsys):
    snap = {"name": "mysnap", "vars": {"X": "hello"}, "encrypted": False}
    encrypted = encrypt_snapshot(snap, key=SECRET)
    _write_snapshot(snapshot_dir, encrypted)
    args = _make_args(dir=str(snapshot_dir))
    cmd_decrypt(args)
    out = capsys.readouterr().out
    assert "decrypted successfully" in out
    data = json.loads((snapshot_dir / "mysnap.json").read_text())
    assert data["vars"]["X"] == "hello"


def test_cmd_decrypt_not_encrypted(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, {"name": "mysnap", "vars": {"A": "1"}, "encrypted": False})
    args = _make_args(dir=str(snapshot_dir))
    cmd_decrypt(args)
    out = capsys.readouterr().out
    assert "not encrypted" in out


def test_cmd_encrypt_missing_snapshot(snapshot_dir):
    args = _make_args(name="ghost", dir=str(snapshot_dir))
    with pytest.raises(SystemExit):
        cmd_encrypt(args)
