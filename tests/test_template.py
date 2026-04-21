"""Tests for envsnap/template.py"""

import pytest
from pathlib import Path

from envsnap.template import (
    apply_template,
    delete_template,
    list_templates,
    save_template,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    snapshot_dir = tmp_path / "snapshots"
    snapshot_dir.mkdir()
    return snapshot_dir


def test_save_and_list_templates(snapshot_dir):
    save_template(snapshot_dir, "web", ["HOST", "PORT", "DEBUG"])
    names = list_templates(snapshot_dir)
    assert "web" in names


def test_list_templates_empty(snapshot_dir):
    assert list_templates(snapshot_dir) == []


def test_save_multiple_templates(snapshot_dir):
    save_template(snapshot_dir, "alpha", ["A"])
    save_template(snapshot_dir, "beta", ["B"])
    names = list_templates(snapshot_dir)
    assert set(names) == {"alpha", "beta"}


def test_delete_existing_template(snapshot_dir):
    save_template(snapshot_dir, "tmp", ["X"])
    removed = delete_template(snapshot_dir, "tmp")
    assert removed is True
    assert "tmp" not in list_templates(snapshot_dir)


def test_delete_missing_template_returns_false(snapshot_dir):
    assert delete_template(snapshot_dir, "nope") is False


def test_apply_template_all_present(snapshot_dir):
    save_template(snapshot_dir, "db", ["DB_HOST", "DB_PORT"])
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = apply_template(snapshot_dir, "db", "snap1", env=env)
    assert result.ok
    assert result.applied == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert result.missing == []
    assert result.used_defaults == {}


def test_apply_template_uses_default(snapshot_dir):
    save_template(snapshot_dir, "svc", ["HOST", "PORT"], defaults={"PORT": "8080"})
    env = {"HOST": "example.com"}
    result = apply_template(snapshot_dir, "svc", "snap2", env=env)
    assert result.ok
    assert result.applied["PORT"] == "8080"
    assert "PORT" in result.used_defaults


def test_apply_template_missing_key(snapshot_dir):
    save_template(snapshot_dir, "strict", ["REQUIRED_KEY"])
    result = apply_template(snapshot_dir, "strict", "snap3", env={})
    assert not result.ok
    assert "REQUIRED_KEY" in result.missing


def test_apply_template_unknown_template_raises(snapshot_dir):
    with pytest.raises(KeyError, match="ghost"):
        apply_template(snapshot_dir, "ghost", "snap4", env={})


def test_apply_template_partial_defaults(snapshot_dir):
    save_template(
        snapshot_dir, "mixed", ["A", "B", "C"], defaults={"B": "default_b"}
    )
    env = {"A": "val_a"}
    result = apply_template(snapshot_dir, "mixed", "snap5", env=env)
    assert result.applied["A"] == "val_a"
    assert result.applied["B"] == "default_b"
    assert "C" in result.missing
    assert not result.ok
