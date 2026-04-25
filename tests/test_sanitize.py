"""Tests for envsnap.sanitize module."""

import json
import pytest
from pathlib import Path

from envsnap.sanitize import (
    sanitize_snapshot,
    REDACT_PLACEHOLDER,
    DEFAULT_SENSITIVE_PATTERNS,
    _matches_any,
)


@pytest.fixture
def snapshot_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write_snapshot(directory: Path, name: str, env: dict) -> None:
    data = {"name": name, "env": env}
    (directory / f"{name}.json").write_text(json.dumps(data))


# ---------------------------------------------------------------------------
# Unit tests for _matches_any
# ---------------------------------------------------------------------------

def test_matches_any_secret_key():
    assert _matches_any("MY_SECRET", DEFAULT_SENSITIVE_PATTERNS) is True


def test_matches_any_password_key():
    assert _matches_any("DB_PASSWORD", DEFAULT_SENSITIVE_PATTERNS) is True


def test_matches_any_non_sensitive_key():
    assert _matches_any("HOME", DEFAULT_SENSITIVE_PATTERNS) is False


def test_matches_any_custom_pattern():
    assert _matches_any("INTERNAL_KEY", [r".*INTERNAL.*"]) is True


# ---------------------------------------------------------------------------
# Integration tests for sanitize_snapshot
# ---------------------------------------------------------------------------

def test_sanitize_redacts_sensitive_keys(snapshot_dir):
    _write_snapshot(snapshot_dir, "dev", {"HOME": "/home/user", "API_KEY": "abc123", "PATH": "/usr/bin"})
    result = sanitize_snapshot(snapshot_dir, "dev")

    assert result.ok is True
    assert "API_KEY" in result.redacted_keys
    assert result.removed_keys == []

    saved = json.loads((snapshot_dir / "dev.json").read_text())
    assert saved["env"]["API_KEY"] == REDACT_PLACEHOLDER
    assert saved["env"]["HOME"] == "/home/user"


def test_sanitize_removes_sensitive_keys_when_remove_flag_set(snapshot_dir):
    _write_snapshot(snapshot_dir, "prod", {"DB_PASSWORD": "s3cr3t", "PORT": "5432"})
    result = sanitize_snapshot(snapshot_dir, "prod", remove=True)

    assert result.ok is True
    assert "DB_PASSWORD" in result.removed_keys
    assert result.redacted_keys == []

    saved = json.loads((snapshot_dir / "prod.json").read_text())
    assert "DB_PASSWORD" not in saved["env"]
    assert saved["env"]["PORT"] == "5432"


def test_sanitize_custom_placeholder(snapshot_dir):
    _write_snapshot(snapshot_dir, "ci", {"MY_TOKEN": "tok_live_xyz"})
    result = sanitize_snapshot(snapshot_dir, "ci", placeholder="<hidden>")

    assert result.ok is True
    saved = json.loads((snapshot_dir / "ci.json").read_text())
    assert saved["env"]["MY_TOKEN"] == "<hidden>"


def test_sanitize_missing_snapshot_returns_error(snapshot_dir):
    result = sanitize_snapshot(snapshot_dir, "nonexistent")

    assert result.ok is False
    assert "nonexistent" in result.error


def test_sanitize_no_sensitive_keys_leaves_snapshot_unchanged(snapshot_dir):
    env = {"HOME": "/home/user", "SHELL": "/bin/bash"}
    _write_snapshot(snapshot_dir, "clean", env)
    result = sanitize_snapshot(snapshot_dir, "clean")

    assert result.ok is True
    assert result.redacted_keys == []
    assert result.removed_keys == []

    saved = json.loads((snapshot_dir / "clean.json").read_text())
    assert saved["env"] == env


def test_sanitize_custom_patterns(snapshot_dir):
    _write_snapshot(snapshot_dir, "custom", {"INTERNAL_HOST": "10.0.0.1", "PUBLIC_URL": "https://example.com"})
    result = sanitize_snapshot(snapshot_dir, "custom", patterns=[r".*INTERNAL.*"])

    assert result.ok is True
    assert "INTERNAL_HOST" in result.redacted_keys
    saved = json.loads((snapshot_dir / "custom.json").read_text())
    assert saved["env"]["PUBLIC_URL"] == "https://example.com"
