"""Command-line interface for envsnap."""

import argparse
import sys

from envsnap.snapshot import capture, save, load, list_snapshots, delete
from envsnap.diff import diff_snapshots


def cmd_capture(args: argparse.Namespace) -> None:
    env = capture(prefix=args.prefix, name=args.name)
    save(env, snapshot_dir=args.dir)
    print(f"Snapshot '{env['name']}' saved ({len(env['env'])} variables).")


def cmd_show(args: argparse.Namespace) -> None:
    """Print all variables stored in a snapshot."""
    try:
        env = load(args.name, snapshot_dir=args.dir)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    for key, value in sorted(env["env"].items()):
        print(f"{key}={value}")


def cmd_list(args: argparse.Namespace) -> None:
    snapshots = list_snapshots(snapshot_dir=args.dir)
    if not snapshots:
        print("No snapshots found.")
    else:
        for name in snapshots:
            print(name)


def cmd_diff(args: argparse.Namespace) -> None:
    try:
        result = diff_snapshots(args.snapshot_a, args.snapshot_b, snapshot_dir=args.dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(result.summary())


def cmd_delete(args: argparse.Namespace) -> None:
    try:
        delete(args.name, snapshot_dir=args.dir)
        print(f"Snapshot '{args.name}' deleted.")
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envsnap",
        description="Snapshot, diff, and restore environment variable sets.",
    )
    parser.add_argument("--dir", default=None, help="Snapshot storage directory.")

    sub = parser.add_subparsers(dest="command", required=True)

    # capture
    p_capture = sub.add_parser("capture", help="Capture current environment.")
    p_capture.add_argument("--prefix", default=None, help="Filter vars by prefix.")
    p_capture.add_argument("--name", default=None, help="Snapshot name.")
    p_capture.set_defaults(func=cmd_capture)

    # list
    p_list = sub.add_parser("list", help="List saved snapshots.")
    p_list.set_defaults(func=cmd_list)

    # show
    p_show = sub.add_parser("show", help="Show variables in a snapshot.")
    p_show.add_argument("name", help="Snapshot name to display.")
    p_show.set_defaults(func=cmd_show)

    # diff
    p_diff = sub.add_parser("diff", help="Diff two snapshots.")
    p_diff.add_argument("snapshot_a", help="First snapshot name.")
    p_diff.add_argument("snapshot_b", help="Second snapshot name.")
    p_diff.set_defaults(func=cmd_diff)

    # delete
    p_delete = sub.add_parser("delete", help="Delete a snapshot.")
    p_delete.add_argument("name", help="Snapshot name to delete.")
    p_delete.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
