"""CLI command for exporting snapshots."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envsnap.export import export_snapshot, write_export, SUPPORTED_FORMATS


DEFAULT_SNAPSHOT_DIR = Path.home() / ".envsnap"


def cmd_export(args: argparse.Namespace) -> None:
    """Handle the 'export' CLI subcommand."""
    snapshot_dir = Path(args.snapshot_dir) if args.snapshot_dir else DEFAULT_SNAPSHOT_DIR

    if not snapshot_dir.exists():
        print(f"Snapshot directory not found: {snapshot_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        if args.output:
            output_path = Path(args.output)
            write_export(args.name, args.format, snapshot_dir, output_path)
            print(f"Exported '{args.name}' as {args.format} to {output_path}")
        else:
            content = export_snapshot(args.name, args.format, snapshot_dir)
            print(content)
    except FileNotFoundError:
        print(f"Snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


def add_export_subparser(subparsers) -> None:
    """Register the export subcommand on an existing subparsers action."""
    parser: argparse.ArgumentParser = subparsers.add_parser(
        "export",
        help="Export a snapshot to dotenv, shell, or JSON format",
    )
    parser.add_argument("name", help="Name of the snapshot to export")
    parser.add_argument(
        "--format", "-f",
        choices=SUPPORTED_FORMATS,
        default="dotenv",
        help="Output format (default: dotenv)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Write output to FILE instead of stdout",
    )
    parser.add_argument(
        "--snapshot-dir",
        metavar="DIR",
        help="Directory where snapshots are stored",
    )
    parser.set_defaults(func=cmd_export)
