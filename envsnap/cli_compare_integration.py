"""Integration helper: register compare subparser into main CLI."""
from envsnap.cli_compare import add_compare_subparser  # noqa: F401


def register(subparsers) -> None:
    """Register the compare subcommand with the provided subparsers object."""
    add_compare_subparser(subparsers)
