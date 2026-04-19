import json
import pytest
from pathlib import Path
from envsnap.pin import pin_snapshot, unpin, resolve_pin, list_pins


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, data: dict = None):
    if data is None:
        data = {"name": name, "vars": {"FOO": "bar"}}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(data))


def test_pin_creates_alias(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap")
    pin_snapshot(snapshot_dir, "production", "mysnap")
    pins = list_pins(snapshot_dir)
    assert pins["production"] == "mysnap"


def test_pin_missing_snapshot_raises(snapshot_dir):
    with pytest.raises(FileNotFoundError, match="mysnap"):
        pin_snapshot(snapshot_dir, "production", "mysnap")


def test_pin_overwrites_existing_alias(snapshot_dir):
    _write_snapshot(snapshot_dir, "snap1")
    _write_snapshot(snapshot_dir, "snap2")
    pin_snapshot(snapshot_dir, "staging", "snap1")
    pin_snapshot(snapshot_dir, "staging", "snap2")
    assert resolve_pin(snapshot_dir, "staging") == "snap2"


def test_unpin_removes_alias(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap")
    pin_snapshot(snapshot_dir, "production", "mysnap")
    result = unpin(snapshot_dir, "production")
    assert result is True
    assert resolve_pin(snapshot_dir, "production") is None


def test_unpin_nonexistent_returns_false(snapshot_dir):
    result = unpin(snapshot_dir, "ghost")
    assert result is False


def test_resolve_pin_missing_returns_none(snapshot_dir):
    assert resolve_pin(snapshot_dir, "nope") is None


def test_list_pins_empty(snapshot_dir):
    assert list_pins(snapshot_dir) == {}


def test_list_pins_multiple(snapshot_dir):
    _write_snapshot(snapshot_dir, "a")
    _write_snapshot(snapshot_dir, "b")
    pin_snapshot(snapshot_dir, "prod", "a")
    pin_snapshot(snapshot_dir, "dev", "b")
    pins = list_pins(snapshot_dir)
    assert pins == {"prod": "a", "dev": "b"}
