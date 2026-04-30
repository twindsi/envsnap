"""Snapshot quality scoring — assigns a numeric score to a snapshot based on
heuristics like completeness, naming conventions, and documentation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envsnap.snapshot import load


@dataclass
class ScoreResult:
    name: str
    score: int  # 0-100
    max_score: int
    breakdown: dict[str, int] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    @property
    def grade(self) -> str:
        pct = self.score / self.max_score if self.max_score else 0
        if pct >= 0.9:
            return "A"
        if pct >= 0.75:
            return "B"
        if pct >= 0.6:
            return "C"
        if pct >= 0.4:
            return "D"
        return "F"

    def __repr__(self) -> str:
        return (
            f"ScoreResult(name={self.name!r}, score={self.score}/{self.max_score},"
            f" grade={self.grade!r})"
        )


def score_snapshot(name: str, snapshot_dir: Path) -> Optional[ScoreResult]:
    """Score a snapshot and return a ScoreResult, or None if not found."""
    data = load(name, snapshot_dir)
    if data is None:
        return None

    breakdown: dict[str, int] = {}
    notes: list[str] = []
    env = data.get("env", {})

    # 1. Non-empty snapshot (up to 20 pts)
    key_count = len(env)
    if key_count == 0:
        notes.append("Snapshot has no environment variables.")
        breakdown["non_empty"] = 0
    elif key_count < 3:
        breakdown["non_empty"] = 10
        notes.append("Snapshot has very few variables.")
    else:
        breakdown["non_empty"] = 20

    # 2. No empty values (up to 20 pts)
    empty_vals = [k for k, v in env.items() if v == ""]
    if empty_vals:
        breakdown["no_empty_values"] = max(0, 20 - len(empty_vals) * 4)
        notes.append(f"{len(empty_vals)} key(s) have empty values: {empty_vals[:3]}")
    else:
        breakdown["no_empty_values"] = 20

    # 3. Consistent key naming (UPPER_SNAKE_CASE) (up to 20 pts)
    bad_keys = [k for k in env if not k.replace("_", "").isupper() or " " in k]
    if bad_keys:
        breakdown["naming_convention"] = max(0, 20 - len(bad_keys) * 5)
        notes.append(f"{len(bad_keys)} key(s) violate UPPER_SNAKE_CASE convention.")
    else:
        breakdown["naming_convention"] = 20

    # 4. Has a description/metadata field (up to 20 pts)
    if data.get("description"):
        breakdown["has_description"] = 20
    else:
        breakdown["has_description"] = 0
        notes.append("No description field found.")

    # 5. Has tags (up to 20 pts)
    tags_file = snapshot_dir / "tags.json"
    has_tags = False
    if tags_file.exists():
        import json
        tags_data = json.loads(tags_file.read_text())
        has_tags = bool(tags_data.get(name))
    breakdown["has_tags"] = 20 if has_tags else 0
    if not has_tags:
        notes.append("No tags associated with this snapshot.")

    total = sum(breakdown.values())
    return ScoreResult(
        name=name,
        score=total,
        max_score=100,
        breakdown=breakdown,
        notes=notes,
    )
