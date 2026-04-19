"""Core snapshot functionality for envsnap."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_SNAPSHOT_DIR = Path.home() / ".envsnap" / "snapshots"


def capture(name: Optional[str] = None, prefix: Optional[str] = None) -> dict:
    """Capture current environment variables into a snapshot dict."""
    env = dict(os.environ)
    if prefix:
        env = {k: v for k, v in env.items() if k.startswith(prefix)}

    return {
        "name": name or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
        "created_at": datetime.utcnow().isoformat(),
        "prefix_filter": prefix,
        "variables": env,
    }


def save(snapshot: dict, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> Path:
    """Persist a snapshot to disk as a JSON file."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    file_path = snapshot_dir / f"{snapshot['name']}.json"
    with open(file_path, "w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2)
    return file_path


def load(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> dict:
    """Load a snapshot by name from disk."""
    file_path = snapshot_dir / f"{name}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {file_path}")
    with open(file_path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def list_snapshots(snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> list[str]:
    """Return names of all stored snapshots, sorted by modification time."""
    if not snapshot_dir.exists():
        return []
    files = sorted(snapshot_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    return [p.stem for p in files]


def delete(name: str, snapshot_dir: Path = DEFAULT_SNAPSHOT_DIR) -> None:
    """Remove a snapshot file from disk."""
    file_path = snapshot_dir / f"{name}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Snapshot '{name}' not found at {file_path}")
    file_path.unlink()
