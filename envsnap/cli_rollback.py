"""CLI sub-command: rollback — revert a snapshot to a previous captured state."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsnap.rollback import rollback_snapshot

_DEFAULT_DIR = Path.home() / ".envsnap"


def cmd_rollback(args: argparse.Namespace) -> None:
    """Handle the ``rollback`` sub-command."""
    snapshot_dir = Path(getattr(args, "snapshot_dir", _DEFAULT_DIR))

    result = rollback_snapshot(
        snapshot_name=args.name,
        snapshot_dir=snapshot_dir,
        steps=args.steps,
    )

    if not result.ok:
        print(f"error: {result.message}", file=sys.stderr)
        sys.exit(1)

    print(f"Rolled back '{args.name}' to state at {result.rolled_back_to}")
    if args.verbose:
        for key, value in sorted(result.restored_vars.items()):
            print(f"  {key}={value}")


def add_rollback_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the ``rollback`` sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "rollback",
        help="revert a snapshot to a previous captured state",
    )
    parser.add_argument("name", help="snapshot name to roll back")
    parser.add_argument(
        "--steps",
        type=int,
        default=1,
        metavar="N",
        help="number of capture events to roll back (default: 1)",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=str(_DEFAULT_DIR),
        help="directory where snapshots are stored",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="print restored variable values",
    )
    parser.set_defaults(func=cmd_rollback)
