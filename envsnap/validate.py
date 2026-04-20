"""Validate snapshots against a schema or set of required keys."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envsnap.snapshot import load


@dataclass
class ValidationResult:
    snapshot_name: str
    missing_keys: List[str] = field(default_factory=list)
    invalid_keys: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.missing_keys and not self.invalid_keys and not self.errors

    def __repr__(self) -> str:
        status = "PASS" if self.valid else "FAIL"
        return (
            f"ValidationResult({self.snapshot_name!r}, status={status}, "
            f"missing={self.missing_keys}, invalid={self.invalid_keys})"
        )


def validate_snapshot(
    snapshot_dir: str,
    name: str,
    required_keys: Optional[List[str]] = None,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
) -> ValidationResult:
    """Validate a snapshot against optional constraints.

    Args:
        snapshot_dir: Directory where snapshots are stored.
        name: Snapshot name to validate.
        required_keys: Keys that must be present in the snapshot.
        key_pattern: Regex pattern every key must match.
        value_pattern: Regex pattern every value must match.

    Returns:
        ValidationResult with details of any failures.
    """
    result = ValidationResult(snapshot_name=name)

    try:
        data = load(snapshot_dir, name)
    except FileNotFoundError:
        result.errors.append(f"Snapshot '{name}' not found in '{snapshot_dir}'.")
        return result

    env: Dict[str, str] = data.get("vars", {})

    if required_keys:
        for key in required_keys:
            if key not in env:
                result.missing_keys.append(key)

    if key_pattern:
        compiled_key = re.compile(key_pattern)
        for key in env:
            if not compiled_key.fullmatch(key):
                result.invalid_keys.append(key)

    if value_pattern:
        compiled_val = re.compile(value_pattern)
        for key, value in env.items():
            if not compiled_val.fullmatch(value):
                result.errors.append(
                    f"Key '{key}' value does not match pattern '{value_pattern}'."
                )

    return result
