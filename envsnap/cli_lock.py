"""CLI subcommands for snapshot lock/unlock management."""

import argparse
from pathlib import Path
from envsnap.lock import lock_snapshot, unlock_snapshot, is_locked, list_locked


def cmd_lock(args: argparse.Namespace) -> None:
    snapshot_dir = Path(args.snapshot_dir)
    action = args.lock_action

    if action == "lock":
        result = lock_snapshot(snapshot_dir, args.name)
        print(result.message)
        if not result.ok:
            raise SystemExit(1)

    elif action == "unlock":
        result = unlock_snapshot(snapshot_dir, args.name)
        print(result.message)
        if not result.ok:
            raise SystemExit(1)

    elif action == "status":
        state = is_locked(snapshot_dir, args.name)
        status = "locked" if state else "unlocked"
        print(f"{args.name}: {status}")

    elif action == "list":
        locked = list_locked(snapshot_dir)
        if not locked:
            print("No locked snapshots.")
        else:
            for name in sorted(locked):
                print(f"  [locked] {name}")

    else:
        print(f"Unknown lock action: {action}")
        raise SystemExit(1)


def add_lock_subparser(subparsers, parent_parser) -> None:
    parser = subparsers.add_parser("lock", help="Lock or unlock snapshots", parents=[parent_parser])
    lock_sub = parser.add_subparsers(dest="lock_action", required=True)

    lock_cmd = lock_sub.add_parser("lock", help="Lock a snapshot")
    lock_cmd.add_argument("name", help="Snapshot name to lock")

    unlock_cmd = lock_sub.add_parser("unlock", help="Unlock a snapshot")
    unlock_cmd.add_argument("name", help="Snapshot name to unlock")

    status_cmd = lock_sub.add_parser("status", help="Check lock status of a snapshot")
    status_cmd.add_argument("name", help="Snapshot name")

    lock_sub.add_parser("list", help="List all locked snapshots")

    parser.set_defaults(func=cmd_lock)
