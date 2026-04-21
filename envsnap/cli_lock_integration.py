"""Integration registration for the lock subcommand."""

from envsnap.cli_lock import add_lock_subparser


def register(subparsers, parent_parser) -> None:
    """Register the lock subcommand with the main CLI parser."""
    add_lock_subparser(subparsers, parent_parser)
