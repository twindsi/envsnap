"""Search and filter snapshots by key, value, or tag."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envsnap.snapshot import load, list_snapshots
from envsnap.tags import get_tags


@dataclass
class SearchResult:
    snapshot_name: str
    matches: dict = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.matches)


def search_snapshots(
    snapshot_dir: Path,
    key_pattern: Optional[str] = None,
    value_pattern: Optional[str] = None,
    tag: Optional[str] = None,
) -> List[SearchResult]:
    """Search all snapshots for keys/values matching the given patterns."""
    results = []
    names = list_snapshots(snapshot_dir)

    for name in names:
        if tag is not None:
            tags = get_tags(snapshot_dir, name)
            if tag not in tags:
                continue

        data = load(snapshot_dir, name)
        env = data.get("vars", {})
        matches = {}

        for k, v in env.items():
            key_ok = key_pattern is None or fnmatch.fnmatch(k, key_pattern)
            val_ok = value_pattern is None or fnmatch.fnmatch(v, value_pattern)
            if key_ok and val_ok:
                matches[k] = v

        results.append(SearchResult(snapshot_name=name, matches=matches))

    return [r for r in results if r]


def search_by_key(snapshot_dir: Path, key: str) -> List[SearchResult]:
    return search_snapshots(snapshot_dir, key_pattern=key)


def search_by_value(snapshot_dir: Path, value: str) -> List[SearchResult]:
    return search_snapshots(snapshot_dir, value_pattern=value)
