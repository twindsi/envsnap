"""Integration hook — registers the 'archive' subcommand with the main CLI."""

from __future__ import annotations

from envsnap.cli_archive import add_archive_subparser


def register(subparsers, snapshot_dir_arg=None) -> None:
    """Called by the main CLI builder to attach the archive subcommand."""
    add_archive_subparser(subparsers, snapshot_dir_arg)
