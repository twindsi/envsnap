"""CLI subcommand for validating snapshots."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from envsnap.validate import validate_snapshot


def cmd_validate(args: argparse.Namespace) -> None:
    """Handle the 'validate' subcommand."""
    required_keys: Optional[List[str]] = (
        [k.strip() for k in args.require.split(",") if k.strip()]
        if args.require
        else None
    )

    result = validate_snapshot(
        snapshot_dir=args.snapshot_dir,
        name=args.name,
        required_keys=required_keys,
        key_pattern=args.key_pattern or None,
        value_pattern=args.value_pattern or None,
    )

    if result.valid:
        print(f"[PASS] Snapshot '{args.name}' is valid.")
        sys.exit(0)
    else:
        print(f"[FAIL] Snapshot '{args.name}' failed validation.")
        if result.missing_keys:
            print(f"  Missing keys : {', '.join(result.missing_keys)}")
        if result.invalid_keys:
            print(f"  Invalid keys : {', '.join(result.invalid_keys)}")
        if result.errors:
            for err in result.errors:
                print(f"  Error        : {err}")
        sys.exit(1)


def add_validate_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'validate' subcommand."""
    parser = subparsers.add_parser(
        "validate",
        help="Validate a snapshot against required keys or patterns.",
    )
    parser.add_argument("name", help="Name of the snapshot to validate.")
    parser.add_argument(
        "--require",
        default="",
        metavar="KEYS",
        help="Comma-separated list of required keys.",
    )
    parser.add_argument(
        "--key-pattern",
        default="",
        metavar="REGEX",
        help="Regex pattern that every key must fully match.",
    )
    parser.add_argument(
        "--value-pattern",
        default="",
        metavar="REGEX",
        help="Regex pattern that every value must fully match.",
    )
    parser.set_defaults(func=cmd_validate)
