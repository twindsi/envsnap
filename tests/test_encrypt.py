"""Tests for envsnap.encrypt."""

import pytest

from envsnap.encrypt import (
    decrypt_snapshot,
    decrypt_value,
    encrypt_snapshot,
    encrypt_value,
    is_encrypted,
    _MARKER,
)

SECRET = "supersecretkey"


def test_encrypt_value_produces_marker():
    result = encrypt_value("hello", key=SECRET)
    assert result.startswith(_MARKER)


def test_roundtrip_value():
    original = "my_secret_value_123"
    enc = encrypt_value(original, key=SECRET)
    dec = decrypt_value(enc, key=SECRET)
    assert dec == original


def test_different_keys_produce_different_ciphertext():
    enc1 = encrypt_value("value", key="key1")
    enc2 = encrypt_value("value", key="key2")
    assert enc1 != enc2


def test_decrypt_wrong_key_gives_garbage():
    enc = encrypt_value("secret", key="rightkey")
    dec = decrypt_value(enc, key="wrongkey")
    assert dec != "secret"


def test_decrypt_non_encrypted_value_raises():
    with pytest.raises(ValueError, match="does not appear to be encrypted"):
        decrypt_value("plain_text", key=SECRET)


def test_no_key_raises(monkeypatch):
    monkeypatch.delenv("ENVSNAP_SECRET_KEY", raising=False)
    with pytest.raises(ValueError, match="No encryption key"):
        encrypt_value("value")


def test_key_from_env(monkeypatch):
    monkeypatch.setenv("ENVSNAP_SECRET_KEY", SECRET)
    enc = encrypt_value("env_key_test")
    dec = decrypt_value(enc)
    assert dec == "env_key_test"


def test_encrypt_snapshot_marks_flag():
    snap = {"name": "test", "vars": {"FOO": "bar", "BAZ": "qux"}}
    result = encrypt_snapshot(snap, key=SECRET)
    assert result["encrypted"] is True
    assert all(v.startswith(_MARKER) for v in result["vars"].values())


def test_decrypt_snapshot_roundtrip():
    snap = {"name": "test", "vars": {"A": "alpha", "B": "beta"}}
    enc = encrypt_snapshot(snap, key=SECRET)
    dec = decrypt_snapshot(enc, key=SECRET)
    assert dec["vars"] == snap["vars"]
    assert dec["encrypted"] is False


def test_is_encrypted_true_and_false():
    assert is_encrypted({"encrypted": True}) is True
    assert is_encrypted({"encrypted": False}) is False
    assert is_encrypted({}) is False
