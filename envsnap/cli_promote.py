"""CLI sub-command: promote — promote a snapshot to the next (or a specified) stage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsnap.promote import promote_snapshot, STAGES


def cmd_promote(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)

    exclude = [k.strip() for k in args.exclude.split(",") if k.strip()] if args.exclude else []

    result = promote_snapshot(
        snapshot_dir=snapshot_dir,
        name=args.name,
        target_stage=args.stage or None,
        exclude_keys=exclude,
        overwrite=args.overwrite,
    )

    if not result.ok:
        print(f"[error] {result.error}", file=sys.stderr)
        sys.exit(1)

    print(f"[ok] Promoted {result.source!r} -> {result.new_name!r} (stage: {result.destination})")
    if result.skipped_keys:
        print(f"     Excluded keys: {', '.join(result.skipped_keys)}")


def add_promote_subparser(subparsers) -> None:
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "promote",
        help="Promote a snapshot to the next environment stage.",
        description=(
            "Copy a snapshot forward through the pipeline stages: "
            + " -> ".join(STAGES)
            + ". The destination name is derived automatically from the source name."
        ),
    )
    parser.add_argument("name", help="Source snapshot name (e.g. myapp-dev).")
    parser.add_argument(
        "--stage",
        metavar="STAGE",
        choices=STAGES,
        default=None,
        help="Target stage to promote to. Defaults to the next stage in the pipeline.",
    )
    parser.add_argument(
        "--exclude",
        metavar="KEYS",
        default="",
        help="Comma-separated list of environment variable keys to exclude from the promoted snapshot.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite the destination snapshot if it already exists.",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=".envsnap",
        metavar="DIR",
        help="Directory where snapshots are stored (default: .envsnap).",
    )
    parser.set_defaults(func=cmd_promote)
