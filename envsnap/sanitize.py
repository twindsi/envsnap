"""Sanitize snapshots by redacting or removing sensitive environment variable values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsnap.snapshot import load, save

DEFAULT_SENSITIVE_PATTERNS = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
]

REDACT_PLACEHOLDER = "**REDACTED**"


@dataclass
class SanitizeResult:
    snapshot_name: str
    redacted_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)
    ok: bool = True
    error: Optional[str] = None

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"SanitizeResult(name={self.snapshot_name!r}, "
            f"redacted={len(self.redacted_keys)}, removed={len(self.removed_keys)}, "
            f"ok={self.ok})"
        )


def _matches_any(key: str, patterns: List[str]) -> bool:
    upper = key.upper()
    return any(re.fullmatch(p, upper) for p in patterns)


def sanitize_snapshot(
    snapshot_dir: Path,
    name: str,
    patterns: Optional[List[str]] = None,
    remove: bool = False,
    placeholder: str = REDACT_PLACEHOLDER,
) -> SanitizeResult:
    """Redact or remove keys matching sensitive patterns in a snapshot.

    Args:
        snapshot_dir: Directory where snapshots are stored.
        name: Name of the snapshot to sanitize.
        patterns: List of regex patterns to match sensitive keys (case-insensitive).
                  Defaults to DEFAULT_SENSITIVE_PATTERNS.
        remove: If True, matching keys are deleted entirely; otherwise they are
                replaced with *placeholder*.
        placeholder: Replacement value when *remove* is False.

    Returns:
        A SanitizeResult describing what was changed.
    """
    if patterns is None:
        patterns = DEFAULT_SENSITIVE_PATTERNS

    try:
        data: Dict = load(snapshot_dir, name)
    except FileNotFoundError:
        return SanitizeResult(snapshot_name=name, ok=False, error=f"Snapshot '{name}' not found.")

    env: Dict[str, str] = data.get("env", {})
    redacted: List[str] = []
    removed: List[str] = []

    sanitized_env: Dict[str, str] = {}
    for key, value in env.items():
        if _matches_any(key, patterns):
            if remove:
                removed.append(key)
            else:
                sanitized_env[key] = placeholder
                redacted.append(key)
        else:
            sanitized_env[key] = value

    data["env"] = sanitized_env
    save(snapshot_dir, data)

    return SanitizeResult(snapshot_name=name, redacted_keys=redacted, removed_keys=removed, ok=True)
