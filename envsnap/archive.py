"""Archive and restore snapshots to/from compressed zip bundles."""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class ArchiveResult:
    ok: bool
    message: str
    names: List[str] = field(default_factory=list)

    def __repr__(self) -> str:  # pragma: no cover
        status = "OK" if self.ok else "ERROR"
        return f"<ArchiveResult [{status}] {self.message}>"


def archive_snapshots(
    snapshot_dir: Path,
    names: List[str],
    dest: Path,
) -> ArchiveResult:
    """Write named snapshots into a zip archive at *dest*."""
    if not names:
        return ArchiveResult(ok=False, message="No snapshot names provided", names=[])

    archived: List[str] = []
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in names:
            snap_path = snapshot_dir / f"{name}.json"
            if not snap_path.exists():
                return ArchiveResult(
                    ok=False,
                    message=f"Snapshot not found: {name}",
                    names=archived,
                )
            zf.write(snap_path, arcname=f"{name}.json")
            archived.append(name)

    return ArchiveResult(ok=True, message=f"Archived {len(archived)} snapshot(s)", names=archived)


def restore_archive(
    archive_path: Path,
    snapshot_dir: Path,
    overwrite: bool = False,
) -> ArchiveResult:
    """Extract snapshots from a zip archive into *snapshot_dir*."""
    if not archive_path.exists():
        return ArchiveResult(ok=False, message=f"Archive not found: {archive_path}", names=[])

    snapshot_dir.mkdir(parents=True, exist_ok=True)
    restored: List[str] = []

    with zipfile.ZipFile(archive_path, "r") as zf:
        for member in zf.namelist():
            if not member.endswith(".json"):
                continue
            dest = snapshot_dir / member
            if dest.exists() and not overwrite:
                return ArchiveResult(
                    ok=False,
                    message=f"Snapshot already exists: {member}. Use overwrite=True to replace.",
                    names=restored,
                )
            zf.extract(member, path=snapshot_dir)
            restored.append(member.removesuffix(".json"))

    return ArchiveResult(ok=True, message=f"Restored {len(restored)} snapshot(s)", names=restored)


def list_archive(archive_path: Path) -> Optional[List[str]]:
    """Return the list of snapshot names inside an archive, or None if missing."""
    if not archive_path.exists():
        return None
    with zipfile.ZipFile(archive_path, "r") as zf:
        return [m.removesuffix(".json") for m in zf.namelist() if m.endswith(".json")]
