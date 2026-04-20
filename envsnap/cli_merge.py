"""CLI subcommand for merging two snapshots into a new one."""

import argparse
from envsnap.merge import merge_snapshots, MergeResult
from envsnap.snapshot import save


def cmd_merge(args: argparse.Namespace) -> None:
    """Merge two snapshots into a new snapshot file."""
    result: MergeResult = merge_snapshots(
        args.snapshot_dir,
        args.base,
        args.other,
        overwrite=args.overwrite,
    )

    if result.conflicts and not args.overwrite:
        print(f"Merge conflict — {len(result.conflicts)} key(s) differ:")
        for key in sorted(result.conflicts):
            base_val = result.base_vars.get(key, "<missing>")
            other_val = result.other_vars.get(key, "<missing>")
            print(f"  {key}")
            print(f"    base : {base_val}")
            print(f"    other: {other_val}")
        print()
        print(
            "Use --overwrite to let the 'other' snapshot win on conflicts, "
            "or resolve manually."
        )
        return

    # Persist the merged environment as a new snapshot.
    save(args.snapshot_dir, args.output, result.merged)

    print(f"Merged '{args.base}' + '{args.other}' → '{args.output}'")
    if result.conflicts:
        print(
            f"  {len(result.conflicts)} conflict(s) resolved by taking "
            "'other' values (--overwrite)."
        )
    print(f"  Total keys: {len(result.merged)}")


def add_merge_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'merge' subcommand."""
    parser = subparsers.add_parser(
        "merge",
        help="Merge two snapshots into a new one.",
        description=(
            "Combine environment variables from BASE and OTHER snapshots. "
            "Keys present in both snapshots are treated as conflicts unless "
            "--overwrite is supplied."
        ),
    )
    parser.add_argument("base", help="Name of the base snapshot.")
    parser.add_argument("other", help="Name of the snapshot to merge in.")
    parser.add_argument(
        "output",
        help="Name for the resulting merged snapshot.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="When keys conflict, take the value from OTHER.",
    )
    parser.add_argument(
        "--snapshot-dir",
        dest="snapshot_dir",
        default=".envsnap",
        help="Directory where snapshots are stored (default: .envsnap).",
    )
    parser.set_defaults(func=cmd_merge)
