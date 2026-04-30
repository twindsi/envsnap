"""CLI subcommand for scoring snapshots."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsnap.score import score_snapshot


def cmd_score(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    result = score_snapshot(args.name, snapshot_dir)

    if result is None:
        print(f"[error] Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Snapshot : {result.name}")
    print(f"Score    : {result.score}/{result.max_score}  (Grade: {result.grade})")
    print()
    print("Breakdown:")
    for criterion, pts in result.breakdown.items():
        label = criterion.replace("_", " ").capitalize()
        bar = "#" * pts + "-" * (20 - pts)
        print(f"  {label:<22} {pts:>3}/20  [{bar}]")

    if result.notes and not getattr(args, "quiet", False):
        print()
        print("Notes:")
        for note in result.notes:
            print(f"  - {note}")


def add_score_subparser(subparsers: argparse._SubParsersAction, snapshot_dir: str) -> None:
    parser = subparsers.add_parser(
        "score",
        help="Score a snapshot on quality heuristics (0-100).",
    )
    parser.add_argument("name", help="Name of the snapshot to score.")
    parser.add_argument(
        "--snapshot-dir",
        default=snapshot_dir,
        help="Directory where snapshots are stored.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress improvement notes.",
    )
    parser.set_defaults(func=cmd_score)
