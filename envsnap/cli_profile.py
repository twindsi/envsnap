"""CLI commands for profile management."""

from __future__ import annotations

import argparse
from pathlib import Path

from envsnap.profile import add_to_profile, remove_from_profile, get_profile, list_profiles


def cmd_profile(args: argparse.Namespace) -> None:
    """Dispatch profile subcommands based on parsed arguments."""
    snapshot_dir = Path(args.snapshot_dir)

    if args.profile_action == "add":
        result = add_to_profile(snapshot_dir, args.profile, args.snapshot)
        if result.ok:
            print(f"[ok] {result.message}")
            print(f"Members: {', '.join(result.snapshots)}")
        else:
            print(f"[error] {result.message}")

    elif args.profile_action == "remove":
        result = remove_from_profile(snapshot_dir, args.profile, args.snapshot)
        if result.ok:
            print(f"[ok] {result.message}")
        else:
            print(f"[error] {result.message}")

    elif args.profile_action == "show":
        result = get_profile(snapshot_dir, args.profile)
        if result.ok:
            if result.snapshots:
                print(f"Profile '{result.profile}':")
                for snap in result.snapshots:
                    print(f"  - {snap}")
            else:
                print(f"Profile '{result.profile}' is empty.")
        else:
            print(f"[error] {result.message}")

    elif args.profile_action == "list":
        _cmd_profile_list(snapshot_dir)

    else:
        print(f"[error] Unknown profile action: {args.profile_action}")


def _cmd_profile_list(snapshot_dir: Path) -> None:
    """Print all profiles and their members to stdout."""
    profiles = list_profiles(snapshot_dir)
    if not profiles:
        print("No profiles defined.")
    else:
        for name, members in profiles.items():
            member_str = ', '.join(members) if members else "(empty)"
            print(f"{name}: {member_str}")


def add_profile_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'profile' command and its subcommands with the argument parser."""
    parser = subparsers.add_parser("profile", help="Manage snapshot profiles")
    parser.add_argument("--snapshot-dir", default=".envsnap", help="Snapshot storage directory")

    sub = parser.add_subparsers(dest="profile_action", required=True)

    p_add = sub.add_parser("add", help="Add a snapshot to a profile")
    p_add.add_argument("profile", help="Profile name")
    p_add.add_argument("snapshot", help="Snapshot name")

    p_rm = sub.add_parser("remove", help="Remove a snapshot from a profile")
    p_rm.add_argument("profile", help="Profile name")
    p_rm.add_argument("snapshot", help="Snapshot name")

    p_show = sub.add_parser("show", help="Show snapshots in a profile")
    p_show.add_argument("profile", help="Profile name")

    sub.add_parser("list", help="List all profiles")

    parser.set_defaults(func=cmd_profile)
