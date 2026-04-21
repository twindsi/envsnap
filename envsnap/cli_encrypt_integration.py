"""Integration shim — registers encrypt/decrypt subcommands with the main CLI."""

from __future__ import annotations

import argparse

from envsnap.cli_encrypt import add_encrypt_subparser


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Called by the main CLI builder to attach encrypt/decrypt commands."""
    add_encrypt_subparser(subparsers)
