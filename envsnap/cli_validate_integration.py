"""Integration hook to register the validate subcommand with the main CLI."""

from __future__ import annotations

import argparse

from envsnap.cli_validate import add_validate_subparser


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the validate subcommand into the provided subparsers group.

    This follows the same integration pattern used by cli_compare_integration
    and cli_schedule_integration so the main CLI entry point can discover
    and mount all subcommands uniformly.

    Args:
        subparsers: The subparsers action from the root ArgumentParser.
    """
    add_validate_subparser(subparsers)
