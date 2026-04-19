"""CLI subcommand for comparing multiple snapshots."""
import argparse
from envsnap.compare import compare_snapshots, format_compare_table


def cmd_compare(args: argparse.Namespace) -> None:
    if len(args.names) < 2:
        print("Error: provide at least two snapshot names to compare.")
        return

    try:
        result = compare_snapshots(args.snapshot_dir, args.names)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return

    if args.divergent:
        keys = result.divergent_keys()
        if not keys:
            print("No divergent keys found.")
            return
        from envsnap.compare import CompareResult
        filtered = CompareResult(
            names=result.names,
            keys=keys,
            table={k: result.table[k] for k in keys},
        )
        print(format_compare_table(filtered))
    else:
        print(format_compare_table(result))

    divergent = result.divergent_keys()
    print(f"\n{len(divergent)} divergent key(s) across {len(result.names)} snapshots.")


def add_compare_subparser(subparsers) -> None:
    p = subparsers.add_parser("compare", help="Compare multiple snapshots side-by-side")
    p.add_argument("names", nargs="+", metavar="SNAPSHOT", help="Snapshot names to compare")
    p.add_argument("--divergent", action="store_true", help="Show only divergent keys")
    p.set_defaults(func=cmd_compare)
