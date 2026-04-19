"""CLI subcommand for searching snapshots."""

from __future__ import annotations

import argparse
from pathlib import Path

from envsnap.search import search_snapshots


def cmd_search(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)

    if not args.key and not args.value and not args.tag:
        print("Error: at least one of --key, --value, or --tag is required.")
        raise SystemExit(1)

    results = search_snapshots(
        snapshot_dir,
        key_pattern=args.key,
        value_pattern=args.value,
        tag=args.tag,
    )

    if not results:
        print("No matches found.")
        return

    for result in results:
        print(f"[{result.snapshot_name}]")
        for k, v in result.matches.items():
            print(f"  {k}={v}")


def add_search_subparser(subparsers: argparse._SubParsersAction, snapshot_dir: str) -> None:
    parser = subparsers.add_parser(
        "search",
        help="Search snapshots by key, value, or tag",
    )
    parser.add_argument(
        "--key",
        metavar="PATTERN",
        help="Glob pattern to match environment variable names",
    )
    parser.add_argument(
        "--value",
        metavar="PATTERN",
        help="Glob pattern to match environment variable values",
    )
    parser.add_argument(
        "--tag",
        metavar="TAG",
        help="Filter snapshots by tag",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=snapshot_dir,
        help="Directory where snapshots are stored",
    )
    parser.set_defaults(func=cmd_search)
