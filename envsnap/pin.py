"""Pin a snapshot as a named alias (e.g. 'production', 'staging')."""

import json
from pathlib import Path

_PINS_FILE = "pins.json"


def _pins_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / _PINS_FILE


def _load_pins(snapshot_dir: Path) -> dict:
    p = _pins_path(snapshot_dir)
    if not p.exists():
        return {}
    with open(p) as f:
        return json.load(f)


def _save_pins(snapshot_dir: Path, pins: dict) -> None:
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    with open(_pins_path(snapshot_dir), "w") as f:
        json.dump(pins, f, indent=2)


def pin_snapshot(snapshot_dir: Path, alias: str, snapshot_name: str) -> None:
    """Associate an alias with a snapshot name."""
    snapshot_file = snapshot_dir / f"{snapshot_name}.json"
    if not snapshot_file.exists():
        raise FileNotFoundError(f"Snapshot '{snapshot_name}' not found.")
    pins = _load_pins(snapshot_dir)
    pins[alias] = snapshot_name
    _save_pins(snapshot_dir, pins)


def unpin(snapshot_dir: Path, alias: str) -> bool:
    """Remove a pin alias. Returns True if it existed."""
    pins = _load_pins(snapshot_dir)
    if alias not in pins:
        return False
    del pins[alias]
    _save_pins(snapshot_dir, pins)
    return True


def resolve_pin(snapshot_dir: Path, alias: str) -> str | None:
    """Return the snapshot name for an alias, or None."""
    return _load_pins(snapshot_dir).get(alias)


def list_pins(snapshot_dir: Path) -> dict:
    """Return all alias -> snapshot_name mappings."""
    return _load_pins(snapshot_dir)
