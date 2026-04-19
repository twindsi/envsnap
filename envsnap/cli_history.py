"""CLI subcommands for snapshot history."""

import argparse
from pathlib import Path
from envsnap.history import get_history, clear_history, recent


def cmd_history(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.dir)

    if args.clear:
        removed = clear_history(snapshot_dir, snapshot_name=args.snapshot or None)
        target = f"'{args.snapshot}'" if args.snapshot else "all snapshots"
        print(f"Cleared {removed} history entries for {target}.")
        return

    if args.snapshot:
        entries = get_history(snapshot_dir, snapshot_name=args.snapshot)
        print(f"History for '{args.snapshot}':")
    else:
        entries = recent(snapshot_dir, limit=args.limit)
        print(f"Recent history (last {args.limit}):")

    if not entries:
        print("  (no entries)")
        return

    for entry in entries:
        print(f"  [{entry['timestamp']}] {entry['action']:10s}  {entry['snapshot']}")


def add_history_subparser(subparsers) -> None:
    parser = subparsers.add_parser(
        "history",
        help="Show or clear snapshot action history",
    )
    parser.add_argument(
        "--dir",
        default=".envsnap",
        help="Snapshot storage directory (default: .envsnap)",
    )
    parser.add_argument(
        "--snapshot",
        metavar="NAME",
        help="Filter history to a specific snapshot name",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of recent entries to show (default: 10)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear history entries (use --snapshot to target one)",
    )
    parser.set_defaults(func=cmd_history)
