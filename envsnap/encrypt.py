"""Encryption support for snapshots — encrypt/decrypt snapshot values at rest."""

import base64
import json
import os
from pathlib import Path
from typing import Dict, Optional

ENV_KEY_VAR = "ENVSNAP_SECRET_KEY"
_MARKER = "enc:v1:"


def _get_key(key: Optional[str] = None) -> bytes:
    """Return a 32-byte key derived from the provided string or env variable."""
    raw = key or os.environ.get(ENV_KEY_VAR, "")
    if not raw:
        raise ValueError(
            f"No encryption key provided. Set {ENV_KEY_VAR} or pass --key."
        )
    # Pad / truncate to 32 bytes for a simple symmetric key.
    encoded = raw.encode("utf-8")
    return (encoded * ((32 // len(encoded)) + 1))[:32]


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """Simple repeating-XOR cipher (demo-grade; swap for AES in production)."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def encrypt_value(plaintext: str, key: Optional[str] = None) -> str:
    """Return an encrypted, base64-encoded representation of *plaintext*."""
    k = _get_key(key)
    cipher = _xor_bytes(plaintext.encode("utf-8"), k)
    return _MARKER + base64.b64encode(cipher).decode("ascii")


def decrypt_value(ciphertext: str, key: Optional[str] = None) -> str:
    """Decrypt a value previously produced by :func:`encrypt_value`."""
    if not ciphertext.startswith(_MARKER):
        raise ValueError("Value does not appear to be encrypted by envsnap.")
    k = _get_key(key)
    raw = base64.b64decode(ciphertext[len(_MARKER):])
    return _xor_bytes(raw, k).decode("utf-8")


def encrypt_snapshot(snapshot: Dict, key: Optional[str] = None) -> Dict:
    """Return a copy of *snapshot* with all env values encrypted."""
    result = dict(snapshot)
    result["vars"] = {
        k: encrypt_value(v, key) for k, v in snapshot.get("vars", {}).items()
    }
    result["encrypted"] = True
    return result


def decrypt_snapshot(snapshot: Dict, key: Optional[str] = None) -> Dict:
    """Return a copy of *snapshot* with all env values decrypted."""
    result = dict(snapshot)
    result["vars"] = {
        k: decrypt_value(v, key) for k, v in snapshot.get("vars", {}).items()
    }
    result["encrypted"] = False
    return result


def is_encrypted(snapshot: Dict) -> bool:
    """Return True when the snapshot was saved in encrypted form."""
    return bool(snapshot.get("encrypted", False))
