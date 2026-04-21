"""CLI subcommands for snapshot encryption and decryption."""

import argparse
import json
import sys
from pathlib import Path

from envsnap.encrypt import decrypt_snapshot, encrypt_snapshot, is_encrypted
from envsnap.snapshot import load, save


def cmd_encrypt(args: argparse.Namespace) -> None:
    """Encrypt an existing snapshot in-place."""
    snap_dir = Path(args.dir)
    try:
        snapshot = load(args.name, snap_dir)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    if is_encrypted(snapshot):
        print(f"Snapshot '{args.name}' is already encrypted.")
        return

    encrypted = encrypt_snapshot(snapshot, key=args.key or None)
    save(encrypted, snap_dir)
    print(f"Snapshot '{args.name}' encrypted successfully.")


def cmd_decrypt(args: argparse.Namespace) -> None:
    """Decrypt an existing snapshot in-place."""
    snap_dir = Path(args.dir)
    try:
        snapshot = load(args.name, snap_dir)
    except FileNotFoundError:
        print(f"Error: snapshot '{args.name}' not found.", file=sys.stderr)
        sys.exit(1)

    if not is_encrypted(snapshot):
        print(f"Snapshot '{args.name}' is not encrypted.")
        return

    try:
        decrypted = decrypt_snapshot(snapshot, key=args.key or None)
    except Exception as exc:  # noqa: BLE001
        print(f"Decryption failed: {exc}", file=sys.stderr)
        sys.exit(1)

    save(decrypted, snap_dir)
    print(f"Snapshot '{args.name}' decrypted successfully.")


def add_encrypt_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register 'encrypt' and 'decrypt' sub-commands."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("name", help="Snapshot name")
    common.add_argument("--dir", default=".envsnap", help="Snapshot directory")
    common.add_argument("--key", default="", help="Encryption key (overrides env var)")

    enc_p = subparsers.add_parser("encrypt", parents=[common], help="Encrypt a snapshot")
    enc_p.set_defaults(func=cmd_encrypt)

    dec_p = subparsers.add_parser("decrypt", parents=[common], help="Decrypt a snapshot")
    dec_p.set_defaults(func=cmd_decrypt)
