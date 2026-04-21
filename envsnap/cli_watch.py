"""CLI subcommand for watch feature."""

import argparse
import sys
from typing import Optional

from envsnap.diff import DiffResult
from envsnap.watch import WatchConfig, start_watch


def _print_diff(diff: DiffResult) -> None:
    print("[watch] Environment change detected:")
    for key, value in diff.added.items():
        print(f"  + {key}={value}")
    for key in diff.removed:
        print(f"  - {key}")
    for key, (old, new) in diff.changed.items():
        print(f"  ~ {key}: {old!r} -> {new!r}")


def cmd_watch(args: argparse.Namespace, snapshot_dir: str = ".envsnap") -> int:
    """Run the watch command: poll env vars and report changes."""
    if not hasattr(args, "name") or not args.name:
        print("error: --name is required for watch", file=sys.stderr)
        return 1

    interval = getattr(args, "interval", 5.0)
    prefix = getattr(args, "prefix", None)
    max_events = getattr(args, "max_events", 0)
    quiet = getattr(args, "quiet", False)

    on_change = None if quiet else _print_diff

    config = WatchConfig(
        interval=interval,
        prefix=prefix,
        on_change=on_change,
        max_events=max_events,
    )

    print(f"[watch] Watching environment for '{args.name}' (interval={interval}s). Ctrl-C to stop.")
    try:
        session = start_watch(args.name, config=config, snapshot_dir=snapshot_dir)
    except KeyboardInterrupt:
        print("\n[watch] Stopped.")
        return 0

    print(f"[watch] Session ended. Total change events: {len(session.events)}")
    return 0


def add_watch_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("watch", help="Watch for environment variable changes")
    parser.add_argument("--name", required=True, help="Snapshot/project name to associate events with")
    parser.add_argument("--interval", type=float, default=5.0, help="Poll interval in seconds (default: 5.0)")
    parser.add_argument("--prefix", default=None, help="Only watch variables with this prefix")
    parser.add_argument("--max-events", type=int, default=0, dest="max_events",
                        help="Stop after this many change events (0=unlimited)")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-change output")
    parser.set_defaults(func=cmd_watch)
