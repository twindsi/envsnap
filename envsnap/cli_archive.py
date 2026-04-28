"""CLI subcommands for archiving and restoring snapshot bundles."""

from __future__ import annotations

import sys
from pathlib import Path

from envsnap.archive import archive_snapshots, restore_archive, list_archive


def cmd_archive(args) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    sub = args.archive_cmd

    if sub == "create":
        dest = Path(args.dest)
        result = archive_snapshots(snapshot_dir, args.names, dest)
        if result.ok:
            print(f"[ok] {result.message} -> {dest}")
            for n in result.names:
                print(f"  + {n}")
        else:
            print(f"[error] {result.message}", file=sys.stderr)
            sys.exit(1)

    elif sub == "restore":
        archive_path = Path(args.archive)
        result = restore_archive(archive_path, snapshot_dir, overwrite=args.overwrite)
        if result.ok:
            print(f"[ok] {result.message}")
            for n in result.names:
                print(f"  + {n}")
        else:
            print(f"[error] {result.message}", file=sys.stderr)
            sys.exit(1)

    elif sub == "list":
        archive_path = Path(args.archive)
        names = list_archive(archive_path)
        if names is None:
            print(f"[error] Archive not found: {archive_path}", file=sys.stderr)
            sys.exit(1)
        if not names:
            print("(empty archive)")
        else:
            for n in sorted(names):
                print(n)


def add_archive_subparser(subparsers, parent_snapshot_dir_arg) -> None:
    p = subparsers.add_parser("archive", help="Bundle or restore snapshot archives")
    p.add_argument("--snapshot-dir", default=".envsnap", dest="snapshot_dir")
    sub = p.add_subparsers(dest="archive_cmd", required=True)

    # create
    pc = sub.add_parser("create", help="Pack snapshots into a zip archive")
    pc.add_argument("dest", help="Destination zip file path")
    pc.add_argument("names", nargs="+", help="Snapshot names to include")

    # restore
    pr = sub.add_parser("restore", help="Unpack snapshots from a zip archive")
    pr.add_argument("archive", help="Path to zip archive")
    pr.add_argument("--overwrite", action="store_true", help="Overwrite existing snapshots")

    # list
    pl = sub.add_parser("list", help="List snapshots inside a zip archive")
    pl.add_argument("archive", help="Path to zip archive")

    p.set_defaults(func=cmd_archive)
