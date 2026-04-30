"""Tests for envsnap.score"""

import json
from pathlib import Path

import pytest

from envsnap.score import score_snapshot, ScoreResult


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, env: dict, extra: dict | None = None) -> None:
    data = {"name": name, "env": env}
    if extra:
        data.update(extra)
    (snapshot_dir / f"{name}.json").write_text(json.dumps(data))


def test_score_missing_snapshot_returns_none(snapshot_dir):
    result = score_snapshot("ghost", snapshot_dir)
    assert result is None


def test_score_returns_score_result(snapshot_dir):
    _write_snapshot(snapshot_dir, "mysnap", {"FOO": "bar", "BAZ": "qux", "APP_ENV": "prod"})
    result = score_snapshot("mysnap", snapshot_dir)
    assert isinstance(result, ScoreResult)
    assert result.name == "mysnap"
    assert 0 <= result.score <= result.max_score


def test_score_empty_snapshot_penalised(snapshot_dir):
    _write_snapshot(snapshot_dir, "empty", {})
    result = score_snapshot("empty", snapshot_dir)
    assert result.breakdown["non_empty"] == 0
    assert any("no environment" in n.lower() for n in result.notes)


def test_score_few_vars_partial_credit(snapshot_dir):
    _write_snapshot(snapshot_dir, "tiny", {"A": "1", "B": "2"})
    result = score_snapshot("tiny", snapshot_dir)
    assert result.breakdown["non_empty"] == 10


def test_score_empty_values_penalised(snapshot_dir):
    _write_snapshot(snapshot_dir, "empvals", {"FOO": "", "BAR": "", "BAZ": "ok"})
    result = score_snapshot("empvals", snapshot_dir)
    assert result.breakdown["no_empty_values"] < 20
    assert any("empty values" in n for n in result.notes)


def test_score_bad_naming_penalised(snapshot_dir):
    _write_snapshot(snapshot_dir, "badnames", {"foo_bar": "1", "CamelCase": "2", "OK_KEY": "3"})
    result = score_snapshot("badnames", snapshot_dir)
    assert result.breakdown["naming_convention"] < 20


def test_score_description_adds_points(snapshot_dir):
    _write_snapshot(snapshot_dir, "described", {"A": "1", "B": "2", "C": "3"},
                    extra={"description": "My snapshot"})
    result = score_snapshot("described", snapshot_dir)
    assert result.breakdown["has_description"] == 20


def test_score_no_description_zero_points(snapshot_dir):
    _write_snapshot(snapshot_dir, "nodesc", {"A": "1"})
    result = score_snapshot("nodesc", snapshot_dir)
    assert result.breakdown["has_description"] == 0
    assert any("description" in n.lower() for n in result.notes)


def test_score_tags_add_points(snapshot_dir):
    _write_snapshot(snapshot_dir, "tagged", {"X": "1", "Y": "2", "Z": "3"})
    tags_file = snapshot_dir / "tags.json"
    tags_file.write_text(json.dumps({"tagged": ["production"]}))
    result = score_snapshot("tagged", snapshot_dir)
    assert result.breakdown["has_tags"] == 20


def test_score_grade_a_for_perfect(snapshot_dir):
    _write_snapshot(snapshot_dir, "perfect",
                    {"APP_ENV": "prod", "DB_HOST": "localhost", "DB_PORT": "5432"},
                    extra={"description": "Production snapshot"})
    tags_file = snapshot_dir / "tags.json"
    tags_file.write_text(json.dumps({"perfect": ["prod"]}))
    result = score_snapshot("perfect", snapshot_dir)
    assert result.score == 100
    assert result.grade == "A"


def test_score_repr_contains_grade(snapshot_dir):
    _write_snapshot(snapshot_dir, "repr_test", {"A": "1", "B": "2", "C": "3"})
    result = score_snapshot("repr_test", snapshot_dir)
    assert "grade=" in repr(result)
