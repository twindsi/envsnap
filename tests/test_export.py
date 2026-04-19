"""Tests for envsnap.export module."""

import json
import pytest
from pathlib import Path

from envsnap.export import export_snapshot, write_export, SUPPORTED_FORMATS


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, vars: dict):
    snap = {"name": name, "vars": vars}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(snap))


def test_export_dotenv_format(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"FOO": "bar", "BAZ": "qux"})
    result = export_snapshot("mysnap", "dotenv", snapshot_dir)
    assert 'BAZ="qux"' in result
    assert 'FOO="bar"' in result


def test_export_dotenv_escapes_quotes(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"MSG": 'say "hello"'})
    result = export_snapshot("mysnap", "dotenv", snapshot_dir)
    assert 'MSG="say \\"hello\\""' in result


def test_export_shell_format(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"FOO": "bar"})
    result = export_snapshot("mysnap", "shell", snapshot_dir)
    assert "export FOO='bar'" in result
    assert result.startswith("#!/usr/bin/env sh")


def test_export_shell_escapes_single_quotes(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"VAR": "it's alive"})
    result = export_snapshot("mysnap", "shell", snapshot_dir)
    assert "VAR=" in result
    assert "it" in result


def test_export_json_format(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"KEY": "value"})
    result = export_snapshot("mysnap", "json", snapshot_dir)
    parsed = json.loads(result)
    assert parsed == {"KEY": "value"}


def test_export_unsupported_format(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"A": "1"})
    with pytest.raises(ValueError, match="Unsupported format"):
        export_snapshot("mysnap", "toml", snapshot_dir)


def test_write_export_creates_file(snapshot_dir, tmp_path):
    _write_snapshot(snapshot_dir, "mysnap", {"X": "1"})
    out = tmp_path / "output.env"
    write_export("mysnap", "dotenv", snapshot_dir, out)
    assert out.exists()
    assert 'X="1"' in out.read_text()
