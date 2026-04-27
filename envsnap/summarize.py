"""Summarize a snapshot into a human-readable report."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envsnap.snapshot import load


@dataclass
class SummaryReport:
    name: str
    total_keys: int
    prefixes: Dict[str, int]  # prefix -> count
    longest_key: str
    longest_value_key: str
    empty_value_keys: List[str]
    tags: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        lines = [
            f"Snapshot : {self.name}",
            f"Total keys: {self.total_keys}",
            f"Empty values: {len(self.empty_value_keys)}",
            f"Longest key: {self.longest_key}",
            f"Longest value key: {self.longest_value_key}",
        ]
        if self.prefixes:
            lines.append("Prefixes:")
            for prefix, count in sorted(self.prefixes.items()):
                lines.append(f"  {prefix}_*  ({count})")
        if self.tags:
            lines.append(f"Tags: {', '.join(self.tags)}")
        return "\n".join(lines)


def _extract_prefixes(keys: List[str]) -> Dict[str, int]:
    """Group keys by their first underscore-delimited segment."""
    counts: Dict[str, int] = {}
    for key in keys:
        if "_" in key:
            prefix = key.split("_", 1)[0]
            counts[prefix] = counts.get(prefix, 0) + 1
    return counts


def summarize_snapshot(
    snapshot_dir: Path,
    name: str,
    tags: Optional[List[str]] = None,
) -> Optional[SummaryReport]:
    """Load a snapshot and return a SummaryReport, or None if not found."""
    data = load(snapshot_dir, name)
    if data is None:
        return None

    env: Dict[str, str] = data.get("env", {})
    keys = list(env.keys())

    if not keys:
        longest_key = ""
        longest_value_key = ""
    else:
        longest_key = max(keys, key=len)
        longest_value_key = max(keys, key=lambda k: len(env.get(k, "")))

    empty_value_keys = [k for k, v in env.items() if v == ""]
    prefixes = _extract_prefixes(keys)

    return SummaryReport(
        name=name,
        total_keys=len(keys),
        prefixes=prefixes,
        longest_key=longest_key,
        longest_value_key=longest_value_key,
        empty_value_keys=empty_value_keys,
        tags=tags or [],
    )
