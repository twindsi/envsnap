"""CLI commands for managing snapshot templates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsnap.template import (
    apply_template,
    delete_template,
    list_templates,
    save_template,
)
from envsnap.snapshot import save as save_snapshot


def cmd_template(args: argparse.Namespace, snapshot_dir: Path) -> int:
    action = args.template_action

    if action == "add":
        keys = [k.strip() for k in args.keys.split(",") if k.strip()]
        if not keys:
            print("Error: --keys must be a non-empty comma-separated list.", file=sys.stderr)
            return 1
        defaults: dict[str, str] = {}
        for pair in (args.defaults or []):
            if "=" not in pair:
                print(f"Error: invalid default {pair!r}, expected KEY=VALUE", file=sys.stderr)
                return 1
            k, v = pair.split("=", 1)
            defaults[k.strip()] = v
        save_template(snapshot_dir, args.template_name, keys, defaults or None)
        print(f"Template {args.template_name!r} saved with {len(keys)} key(s).")
        return 0

    if action == "list":
        names = list_templates(snapshot_dir)
        if not names:
            print("No templates defined.")
        else:
            for n in names:
                print(n)
        return 0

    if action == "delete":
        removed = delete_template(snapshot_dir, args.template_name)
        if removed:
            print(f"Template {args.template_name!r} deleted.")
            return 0
        print(f"Template {args.template_name!r} not found.", file=sys.stderr)
        return 1

    if action == "apply":
        try:
            result = apply_template(snapshot_dir, args.template_name, args.snapshot_name)
        except KeyError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        if not result.ok:
            print(f"Missing required keys: {result.missing}", file=sys.stderr)
            return 1
        save_snapshot(snapshot_dir, result.snapshot_name, result.applied)
        if result.used_defaults:
            print(f"Used defaults for: {list(result.used_defaults.keys())}")
        print(f"Snapshot {result.name!r} created from template {args.template_name!r}.")
        return 0

    print(f"Unknown action: {action}", file=sys.stderr)
    return 1


def add_template_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("template", help="Manage snapshot templates")
    sub = p.add_subparsers(dest="template_action")

    add_p = sub.add_parser("add", help="Define a new template")
    add_p.add_argument("template_name", help="Template name")
    add_p.add_argument("--keys", required=True, help="Comma-separated env key names")
    add_p.add_argument("--default", dest="defaults", action="append", metavar="KEY=VALUE")

    sub.add_parser("list", help="List all templates")

    del_p = sub.add_parser("delete", help="Remove a template")
    del_p.add_argument("template_name")

    apply_p = sub.add_parser("apply", help="Create a snapshot from a template")
    apply_p.add_argument("template_name")
    apply_p.add_argument("snapshot_name")

    p.set_defaults(func=cmd_template)
