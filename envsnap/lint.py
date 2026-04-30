"""Lint snapshots for common issues: empty values, duplicate-ish keys, naming conventions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envsnap.snapshot import load


@dataclass
class LintWarning:
    key: str
    message: str

    def __str__(self) -> str:
        return f"  [{self.key}] {self.message}"


@dataclass
class LintResult:
    snapshot_name: str
    warnings: List[LintWarning] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.warnings) == 0

    def __repr__(self) -> str:
        if self.ok:
            return f"LintResult({self.snapshot_name!r}: OK)"
        return (
            f"LintResult({self.snapshot_name!r}: {len(self.warnings)} warning(s))"
        )


_UPPER_SNAKE_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_SENSITIVE_PATTERNS = re.compile(
    r'(SECRET|PASSWORD|TOKEN|KEY|PRIVATE|CREDENTIAL)', re.IGNORECASE
)


def lint_snapshot(
    name: str,
    snapshot_dir: Path,
    *,
    check_empty: bool = True,
    check_naming: bool = True,
    check_sensitive_exposure: bool = True,
) -> Optional[LintResult]:
    """Run lint checks on a snapshot. Returns None if snapshot not found."""
    data = load(name, snapshot_dir)
    if data is None:
        return None

    result = LintResult(snapshot_name=name)
    env: dict = data.get("env", {})

    seen_normalised: dict[str, str] = {}

    for key, value in env.items():
        if check_empty and value == "":
            result.warnings.append(
                LintWarning(key, "value is empty")
            )

        if check_naming and not _UPPER_SNAKE_RE.match(key):
            result.warnings.append(
                LintWarning(key, "key does not follow UPPER_SNAKE_CASE convention")
            )

        if check_sensitive_exposure and _SENSITIVE_PATTERNS.search(key):
            if value and not value.startswith("enc:"):
                result.warnings.append(
                    LintWarning(key, "sensitive key has a plaintext value (consider encrypting)")
                )

        norm = key.upper().replace("-", "_").replace(" ", "_")
        if norm in seen_normalised and seen_normalised[norm] != key:
            result.warnings.append(
                LintWarning(key, f"key is a near-duplicate of '{seen_normalised[norm]}'")
            )
        else:
            seen_normalised[norm] = key

    return result
