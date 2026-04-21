"""CLI subcommand for renaming snapshots."""

import argparse
from pathlib import Path

from envsnap.rename import rename_snapshot


def cmd_rename(args: argparse.Namespace) -> None:
    """Handle the 'rename' subcommand."""
    snapshot_dir = Path(args.snapshot_dir)

    result = rename_snapshot(snapshot_dir, args.old_name, args.new_name)

    if not result.success:
        print(f"Error: {result.error}")
        raise SystemExit(1)

    print(f"Renamed '{result.old_name}' -> '{result.new_name}'")

    if result.tags_updated:
        print("  Tags migrated to new name.")

    if result.pins_updated:
        aliases = ", ".join(result.pins_updated)
        print(f"  Updated pin(s): {aliases}")


def add_rename_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'rename' subcommand with the given subparsers."""
    parser = subparsers.add_parser(
        "rename",
        help="Rename an existing snapshot, migrating tags and pins.",
    )
    parser.add_argument(
        "old_name",
        help="Current name of the snapshot.",
    )
    parser.add_argument(
        "new_name",
        help="New name for the snapshot.",
    )
    parser.add_argument(
        "--snapshot-dir",
        default=".envsnap",
        help="Directory where snapshots are stored (default: .envsnap).",
    )
    parser.set_defaults(func=cmd_rename)
