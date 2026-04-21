"""Template support: create snapshots from key-name templates with defaults."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TemplateResult:
    name: str
    applied: Dict[str, str] = field(default_factory=dict)
    missing: List[str] = field(default_factory=list)
    used_defaults: Dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return len(self.missing) == 0

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"TemplateResult(name={self.name!r}, ok={self.ok}, "
            f"applied={len(self.applied)}, missing={self.missing})"
        )


def _templates_path(snapshot_dir: Path) -> Path:
    return snapshot_dir / "_templates.json"


def _load_templates(snapshot_dir: Path) -> Dict[str, Dict]:
    p = _templates_path(snapshot_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_templates(snapshot_dir: Path, data: Dict[str, Dict]) -> None:
    _templates_path(snapshot_dir).write_text(json.dumps(data, indent=2))


def save_template(
    snapshot_dir: Path,
    template_name: str,
    keys: List[str],
    defaults: Optional[Dict[str, str]] = None,
) -> None:
    """Persist a named template (list of keys + optional defaults)."""
    data = _load_templates(snapshot_dir)
    data[template_name] = {"keys": keys, "defaults": defaults or {}}
    _save_templates(snapshot_dir, data)


def list_templates(snapshot_dir: Path) -> List[str]:
    return list(_load_templates(snapshot_dir).keys())


def delete_template(snapshot_dir: Path, template_name: str) -> bool:
    data = _load_templates(snapshot_dir)
    if template_name not in data:
        return False
    del data[template_name]
    _save_templates(snapshot_dir, data)
    return True


def apply_template(
    snapshot_dir: Path,
    template_name: str,
    snapshot_name: str,
    env: Optional[Dict[str, str]] = None,
) -> TemplateResult:
    """Build a snapshot dict from a template, reading from env (or os.environ)."""
    data = _load_templates(snapshot_dir)
    if template_name not in data:
        raise KeyError(f"Template {template_name!r} not found")

    tpl = data[template_name]
    keys: List[str] = tpl["keys"]
    defaults: Dict[str, str] = tpl.get("defaults", {})
    source = env if env is not None else dict(os.environ)

    result = TemplateResult(name=snapshot_name)
    for key in keys:
        if key in source:
            result.applied[key] = source[key]
        elif key in defaults:
            result.applied[key] = defaults[key]
            result.used_defaults[key] = defaults[key]
        else:
            result.missing.append(key)

    return result
