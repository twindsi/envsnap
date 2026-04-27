"""Tests for envsnap.summarize."""

import json
import pytest
from pathlib import Path

from envsnap.summarize import summarize_snapshot, _extract_prefixes, SummaryReport


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, env: dict) -> None:
    path = snapshot_dir / f"{name}.json"
    path.write_text(json.dumps({"name": name, "env": env}))


def test_summarize_missing_snapshot_returns_none(snapshot_dir):
    result = summarize_snapshot(snapshot_dir, "ghost")
    assert result is None


def test_summarize_total_keys(snapshot_dir):
    _write_snapshot(snapshot_dir, "s1", {"FOO": "bar", "BAZ": "qux"})
    report = summarize_snapshot(snapshot_dir, "s1")
    assert report is not None
    assert report.total_keys == 2


def test_summarize_empty_values(snapshot_dir):
    _write_snapshot(snapshot_dir, "s2", {"FOO": "", "BAR": "hello", "BAZ": ""})
    report = summarize_snapshot(snapshot_dir, "s2")
    assert report.empty_value_keys == ["FOO", "BAZ"]


def test_summarize_longest_key(snapshot_dir):
    _write_snapshot(snapshot_dir, "s3", {"A": "1", "LONG_KEY_NAME": "2", "MID": "3"})
    report = summarize_snapshot(snapshot_dir, "s3")
    assert report.longest_key == "LONG_KEY_NAME"


def test_summarize_longest_value_key(snapshot_dir):
    _write_snapshot(snapshot_dir, "s4", {"X": "short", "Y": "a_much_longer_value_here"})
    report = summarize_snapshot(snapshot_dir, "s4")
    assert report.longest_value_key == "Y"


def test_summarize_prefixes(snapshot_dir):
    env = {
        "AWS_KEY": "k",
        "AWS_SECRET": "s",
        "DB_HOST": "localhost",
        "PLAIN": "x",
    }
    _write_snapshot(snapshot_dir, "s5", env)
    report = summarize_snapshot(snapshot_dir, "s5")
    assert report.prefixes["AWS"] == 2
    assert report.prefixes["DB"] == 1
    assert "PLAIN" not in report.prefixes


def test_summarize_tags_passed_through(snapshot_dir):
    _write_snapshot(snapshot_dir, "s6", {"K": "v"})
    report = summarize_snapshot(snapshot_dir, "s6", tags=["production", "stable"])
    assert report.tags == ["production", "stable"]


def test_summarize_empty_snapshot(snapshot_dir):
    _write_snapshot(snapshot_dir, "empty", {})
    report = summarize_snapshot(snapshot_dir, "empty")
    assert report.total_keys == 0
    assert report.longest_key == ""
    assert report.longest_value_key == ""
    assert report.empty_value_keys == []


def test_extract_prefixes_no_underscores():
    result = _extract_prefixes(["FOO", "BAR", "BAZ"])
    assert result == {}


def test_extract_prefixes_mixed():
    result = _extract_prefixes(["APP_NAME", "APP_ENV", "DB_HOST"])
    assert result == {"APP": 2, "DB": 1}


def test_repr_contains_name(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"FOO": "bar"})
    report = summarize_snapshot(snapshot_dir, "mysnap")
    assert "mysnap" in repr(report)
