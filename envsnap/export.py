"""Export snapshots to various formats (dotenv, shell, JSON)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from envsnap.snapshot import load


SUPPORTED_FORMATS = ("dotenv", "shell", "json")


def export_snapshot(name: str, fmt: str, snapshot_dir: Path) -> str:
    """Load a snapshot and return its contents as a formatted string.

    Args:
        name: The name of the snapshot to export.
        fmt: The output format; one of 'dotenv', 'shell', or 'json'.
        snapshot_dir: Directory where snapshots are stored.

    Returns:
        A string containing the snapshot variables in the requested format.

    Raises:
        ValueError: If ``fmt`` is not a supported format.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")

    snapshot = load(name, snapshot_dir)
    env_vars: Dict[str, str] = snapshot.get("vars", {})

    if fmt == "dotenv":
        return _to_dotenv(env_vars)
    elif fmt == "shell":
        return _to_shell(env_vars)
    elif fmt == "json":
        return json.dumps(env_vars, indent=2)


def _to_dotenv(env_vars: Dict[str, str]) -> str:
    """Render variables in .env file format.

    Values are double-quoted with internal double-quotes escaped.
    """
    lines = []
    for key, value in sorted(env_vars.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def _to_shell(env_vars: Dict[str, str]) -> str:
    """Render variables as export statements for shell sourcing.

    Values are single-quoted with internal single quotes safely escaped
    using the '"'"' idiom, making the output safe for POSIX sh.
    """
    lines = ["#!/usr/bin/env sh"]
    for key, value in sorted(env_vars.items()):
        escaped = value.replace("'", "'\"'\"'")
        lines.append(f"export {key}='{escaped}'")
    return "\n".join(lines)


def write_export(name: str, fmt: str, snapshot_dir: Path, output_path: Path) -> None:
    """Export a snapshot to a file.

    Args:
        name: The name of the snapshot to export.
        fmt: The output format; one of 'dotenv', 'shell', or 'json'.
        snapshot_dir: Directory where snapshots are stored.
        output_path: Destination file path for the exported content.
    """
    content = export_snapshot(name, fmt, snapshot_dir)
    output_path.write_text(content, encoding="utf-8")
