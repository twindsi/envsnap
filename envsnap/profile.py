"""Profile management: group multiple snapshots under a named profile."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _profiles_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_profiles.json"


def _load_profiles(snapshot_dir: Path) -> Dict[str, List[str]]:
    path = _profiles_path(snapshot_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_profiles(snapshot_dir: Path, data: Dict[str, List[str]]) -> None:
    _profiles_path(snapshot_dir).write_text(json.dumps(data, indent=2))


@dataclass
class ProfileResult:
    ok: bool
    message: str
    profile: Optional[str] = None
    snapshots: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"ProfileResult(ok={self.ok}, message={self.message!r})"


def add_to_profile(snapshot_dir: Path, profile: str, snapshot_name: str) -> ProfileResult:
    """Add a snapshot to a named profile, creating the profile if needed."""
    snap_file = snapshot_dir / f"{snapshot_name}.json"
    if not snap_file.exists():
        return ProfileResult(ok=False, message=f"Snapshot '{snapshot_name}' not found.")

    profiles = _load_profiles(snapshot_dir)
    members = profiles.setdefault(profile, [])
    if snapshot_name in members:
        return ProfileResult(ok=False, message=f"'{snapshot_name}' already in profile '{profile}'.",
                             profile=profile, snapshots=list(members))
    members.append(snapshot_name)
    _save_profiles(snapshot_dir, profiles)
    return ProfileResult(ok=True, message=f"Added '{snapshot_name}' to profile '{profile}'.",
                         profile=profile, snapshots=list(members))


def remove_from_profile(snapshot_dir: Path, profile: str, snapshot_name: str) -> ProfileResult:
    """Remove a snapshot from a profile."""
    profiles = _load_profiles(snapshot_dir)
    if profile not in profiles:
        return ProfileResult(ok=False, message=f"Profile '{profile}' not found.")
    members = profiles[profile]
    if snapshot_name not in members:
        return ProfileResult(ok=False, message=f"'{snapshot_name}' not in profile '{profile}'.")
    members.remove(snapshot_name)
    if not members:
        del profiles[profile]
    _save_profiles(snapshot_dir, profiles)
    return ProfileResult(ok=True, message=f"Removed '{snapshot_name}' from profile '{profile}'.",
                         profile=profile, snapshots=list(members))


def get_profile(snapshot_dir: Path, profile: str) -> ProfileResult:
    """Return all snapshot names belonging to a profile."""
    profiles = _load_profiles(snapshot_dir)
    if profile not in profiles:
        return ProfileResult(ok=False, message=f"Profile '{profile}' not found.")
    return ProfileResult(ok=True, message="ok", profile=profile, snapshots=list(profiles[profile]))


def list_profiles(snapshot_dir: Path) -> Dict[str, List[str]]:
    """Return all profiles and their snapshot members."""
    return _load_profiles(snapshot_dir)
