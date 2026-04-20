"""CLI commands for managing snapshot schedules."""

import argparse
from envsnap.schedule import (
    Schedule,
    add_schedule,
    remove_schedule,
    list_schedules,
    toggle_schedule,
    VALID_INTERVALS,
)


def cmd_schedule(args: argparse.Namespace, snapshot_dir: str) -> None:
    sub = args.schedule_cmd

    if sub == "add":
        s = Schedule(
            name=args.name,
            interval=args.interval,
            prefix=args.prefix or None,
            enabled=True,
        )
        try:
            add_schedule(snapshot_dir, s)
            print(f"Schedule '{args.name}' added ({args.interval}).")
        except ValueError as e:
            print(f"Error: {e}")

    elif sub == "remove":
        removed = remove_schedule(snapshot_dir, args.name)
        if removed:
            print(f"Schedule '{args.name}' removed.")
        else:
            print(f"No schedule named '{args.name}'.")

    elif sub == "list":
        schedules = list_schedules(snapshot_dir)
        if not schedules:
            print("No schedules defined.")
            return
        for s in schedules:
            status = "enabled" if s.enabled else "disabled"
            prefix_info = f"  prefix={s.prefix}" if s.prefix else ""
            print(f"  {s.name}: {s.interval} [{status}]{prefix_info}")

    elif sub == "enable":
        ok = toggle_schedule(snapshot_dir, args.name, enabled=True)
        print(f"Schedule '{args.name}' enabled." if ok else f"Schedule '{args.name}' not found.")

    elif sub == "disable":
        ok = toggle_schedule(snapshot_dir, args.name, enabled=False)
        print(f"Schedule '{args.name}' disabled." if ok else f"Schedule '{args.name}' not found.")

    else:
        print("Unknown schedule subcommand.")


def add_schedule_subparser(subparsers) -> None:
    p = subparsers.add_parser("schedule", help="Manage auto-capture schedules")
    sp = p.add_subparsers(dest="schedule_cmd")

    add_p = sp.add_parser("add", help="Add a schedule")
    add_p.add_argument("name", help="Schedule name")
    add_p.add_argument("interval", choices=list(VALID_INTERVALS), help="Capture interval")
    add_p.add_argument("--prefix", help="Env var prefix filter")

    rm_p = sp.add_parser("remove", help="Remove a schedule")
    rm_p.add_argument("name", help="Schedule name")

    sp.add_parser("list", help="List all schedules")

    en_p = sp.add_parser("enable", help="Enable a schedule")
    en_p.add_argument("name")

    dis_p = sp.add_parser("disable", help="Disable a schedule")
    dis_p.add_argument("name")
