import json
import os
import argparse
import pytest
from envsnap.cli_compare import cmd_compare


@pytest.fixture
def snapshot_dir(tmp_path):
    return str(tmp_path)


def _write_snapshot(snapshot_dir, name, vars_):
    path = os.path.join(snapshot_dir, f"{name}.json")
    with open(path, "w") as f:
        json.dump({"name": name, "vars": vars_}, f)


def _make_args(snapshot_dir, names, divergent=False):
    ns = argparse.Namespace()
    ns.snapshot_dir = snapshot_dir
    ns.names = names
    ns.divergent = divergent
    return ns


def test_cmd_compare_prints_table(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "a", {"X": "1"})
    _write_snapshot(snapshot_dir, "b", {"X": "2"})
    cmd_compare(_make_args(snapshot_dir, ["a", "b"]))
    out = capsys.readouterr().out
    assert "X" in out
    assert "a" in out


def test_cmd_compare_too_few_names(snapshot_dir, capsys):
    cmd_compare(_make_args(snapshot_dir, ["a"]))
    out = capsys.readouterr().out
    assert "Error" in out


def test_cmd_compare_divergent_flag(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "a", {"X": "1", "Y": "same"})
    _write_snapshot(snapshot_dir, "b", {"X": "2", "Y": "same"})
    cmd_compare(_make_args(snapshot_dir, ["a", "b"], divergent=True))
    out = capsys.readouterr().out
    assert "X" in out


def test_cmd_compare_missing_snapshot(snapshot_dir, capsys):
    _write_snapshot(snapshot_dir, "a", {"X": "1"})
    cmd_compare(_make_args(snapshot_dir, ["a", "missing"]))
    out = capsys.readouterr().out
    assert "Error" in out
