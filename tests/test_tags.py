"""Tests for envsnap.tags module."""

import pytest
from pathlib import Path
from envsnap.tags import add_tag, remove_tag, get_tags, find_by_tag, clear_tags


@pytest.fixture
def snapshot_dir(tmp_path):
    return tmp_path / "snapshots"


def test_add_tag_creates_entry(snapshot_dir):
    add_tag(snapshot_dir, "snap1", "production")
    assert "production" in get_tags(snapshot_dir, "snap1")


def test_add_tag_deduplicates(snapshot_dir):
    add_tag(snapshot_dir, "snap1", "production")
    add_tag(snapshot_dir, "snap1", "production")
    assert get_tags(snapshot_dir, "snap1").count("production") == 1


def test_add_multiple_tags(snapshot_dir):
    add_tag(snapshot_dir, "snap1", "production")
    add_tag(snapshot_dir, "snap1", "backend")
    tags = get_tags(snapshot_dir, "snap1")
    assert "production" in tags
    assert "backend" in tags


def test_get_tags_missing_snapshot(snapshot_dir):
    assert get_tags(snapshot_dir, "nonexistent") == []


def test_remove_tag_returns_true_when_present(snapshot_dir):
    add_tag(snapshot_dir, "snap1", "staging")
    result = remove_tag(snapshot_dir, "snap1", "staging")
    assert result is True
    assert "staging" not in get_tags(snapshot_dir, "snap1")


def test_remove_tag_returns_false_when_absent(snapshot_dir):
    result = remove_tag(snapshot_dir, "snap1", "ghost")
    assert result is False


def test_remove_last_tag_cleans_up_entry(snapshot_dir):
    add_tag(snapshot_dir, "snap1", "only")
    remove_tag(snapshot_dir, "snap1", "only")
    assert get_tags(snapshot_dir, "snap1") == []


def test_find_by_tag_returns_matching_snapshots(snapshot_dir):
    add_tag(snapshot_dir, "snap1", "production")
    add_tag(snapshot_dir, "snap2", "production")
    add_tag(snapshot_dir, "snap3", "staging")
    result = find_by_tag(snapshot_dir, "production")
    assert set(result) == {"snap1", "snap2"}


def test_find_by_tag_no_matches(snapshot_dir):
    assert find_by_tag(snapshot_dir, "unknown") == []


def test_clear_tags(snapshot_dir):
    add_tag(snapshot_dir, "snap1", "a")
    add_tag(snapshot_dir, "snap1", "b")
    clear_tags(snapshot_dir, "snap1")
    assert get_tags(snapshot_dir, "snap1") == []


def test_clear_tags_does_not_affect_others(snapshot_dir):
    add_tag(snapshot_dir, "snap1", "keep")
    add_tag(snapshot_dir, "snap2", "also-keep")
    clear_tags(snapshot_dir, "snap1")
    assert "also-keep" in get_tags(snapshot_dir, "snap2")
