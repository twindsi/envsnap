"""Tests for envsnap.lint module."""

import json
import pytest
from pathlib import Path

from envsnap.lint import lint_snapshot, LintResult, LintWarning


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_snapshot(snapshot_dir: Path, name: str, env: dict) -> None:
    data = {"name": name, "env": env}
    (snapshot_dir / f"{name}.json").write_text(json.dumps(data))


def test_lint_missing_snapshot_returns_none(snapshot_dir):
    result = lint_snapshot("ghost", snapshot_dir)
    assert result is None


def test_lint_clean_snapshot_returns_ok(snapshot_dir):
    _write_snapshot(snapshot_dir, "clean", {"APP_ENV": "production", "PORT": "8080"})
    result = lint_snapshot("clean", snapshot_dir)
    assert result is not None
    assert result.ok
    assert result.warnings == []


def test_lint_detects_empty_value(snapshot_dir):
    _write_snapshot(snapshot_dir, "empty_val", {"APP_NAME": ""})
    result = lint_snapshot("empty_val", snapshot_dir)
    assert not result.ok
    messages = [w.message for w in result.warnings]
    assert any("empty" in m for m in messages)


def test_lint_detects_non_upper_snake_key(snapshot_dir):
    _write_snapshot(snapshot_dir, "badkey", {"appName": "myapp"})
    result = lint_snapshot("badkey", snapshot_dir)
    assert not result.ok
    assert any("UPPER_SNAKE_CASE" in w.message for w in result.warnings)


def test_lint_detects_plaintext_sensitive_key(snapshot_dir):
    _write_snapshot(snapshot_dir, "sensitive", {"DB_PASSWORD": "hunter2"})
    result = lint_snapshot("sensitive", snapshot_dir)
    assert not result.ok
    assert any("plaintext" in w.message for w in result.warnings)


def test_lint_encrypted_sensitive_key_is_ok(snapshot_dir):
    _write_snapshot(snapshot_dir, "encrypted", {"DB_PASSWORD": "enc:abc123"})
    result = lint_snapshot("encrypted", snapshot_dir)
    # Only possible remaining warning would be naming; no plaintext warning
    assert all("plaintext" not in w.message for w in result.warnings)


def test_lint_detects_near_duplicate_keys(snapshot_dir):
    _write_snapshot(snapshot_dir, "dupes", {"APP_URL": "http://a", "app_url": "http://b"})
    result = lint_snapshot("dupes", snapshot_dir)
    assert not result.ok
    assert any("near-duplicate" in w.message for w in result.warnings)


def test_lint_check_flags_can_be_disabled(snapshot_dir):
    _write_snapshot(snapshot_dir, "nocheck", {"appName": "", "DB_SECRET": "pass"})
    result = lint_snapshot(
        "nocheck",
        snapshot_dir,
        check_empty=False,
        check_naming=False,
        check_sensitive_exposure=False,
    )
    assert result is not None
    assert result.ok


def test_lint_result_repr_ok(snapshot_dir):
    _write_snapshot(snapshot_dir, "repr_ok", {"GOOD_KEY": "val"})
    result = lint_snapshot("repr_ok", snapshot_dir)
    assert "OK" in repr(result)


def test_lint_result_repr_warnings(snapshot_dir):
    _write_snapshot(snapshot_dir, "repr_warn", {"bad-key": ""})
    result = lint_snapshot("repr_warn", snapshot_dir)
    assert "warning" in repr(result)
