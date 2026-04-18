"""Tests for envault.crypto module."""

import pytest
from envault.crypto import encrypt, decrypt, SALT_LENGTH


def test_encrypt_returns_bytes():
    result = encrypt("KEY=value", "password")
    assert isinstance(result, bytes)


def test_encrypt_includes_salt():
    result = encrypt("KEY=value", "password")
    assert len(result) > SALT_LENGTH


def test_decrypt_roundtrip():
    plaintext = "DB_HOST=localhost\nDB_PORT=5432\n"
    password = "supersecret"
    encrypted = encrypt(plaintext, password)
    assert decrypt(encrypted, password) == plaintext


def test_different_salts_each_call():
    data1 = encrypt("X=1", "pw")
    data2 = encrypt("X=1", "pw")
    assert data1 != data2


def test_wrong_password_raises():
    encrypted = encrypt("SECRET=abc", "correct")
    with pytest.raises(Exception):
        decrypt(encrypted, "wrong")


def test_empty_string_roundtrip():
    encrypted = encrypt("", "pw")
    assert decrypt(encrypted, "pw") == ""
