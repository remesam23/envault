"""Tests for field-level encryption module."""

import pytest

from envault.env_encrypt_field import (
    encrypt_fields,
    decrypt_fields,
    is_field_encrypted,
    FieldEncryptError,
    FIELD_CIPHER_PREFIX,
)

PASSWORD = "test-secret"


def _make_profile():
    return {"DB_HOST": "localhost", "DB_PASS": "hunter2", "API_KEY": "abc123"}


def test_encrypt_fields_marks_with_prefix():
    profile = _make_profile()
    updated, result = encrypt_fields(profile, ["DB_PASS"], PASSWORD)
    assert updated["DB_PASS"].startswith(FIELD_CIPHER_PREFIX)
    assert "DB_PASS" in result.encrypted


def test_encrypt_fields_does_not_touch_other_keys():
    profile = _make_profile()
    updated, _ = encrypt_fields(profile, ["DB_PASS"], PASSWORD)
    assert updated["DB_HOST"] == "localhost"
    assert updated["API_KEY"] == "abc123"


def test_encrypt_multiple_keys():
    profile = _make_profile()
    updated, result = encrypt_fields(profile, ["DB_PASS", "API_KEY"], PASSWORD)
    assert is_field_encrypted(updated["DB_PASS"])
    assert is_field_encrypted(updated["API_KEY"])
    assert len(result.encrypted) == 2


def test_encrypt_missing_key_goes_to_skipped():
    profile = _make_profile()
    _, result = encrypt_fields(profile, ["MISSING_KEY"], PASSWORD)
    assert "MISSING_KEY" in result.skipped


def test_already_encrypted_key_skipped_without_overwrite():
    profile = _make_profile()
    updated, _ = encrypt_fields(profile, ["DB_PASS"], PASSWORD)
    _, result2 = encrypt_fields(updated, ["DB_PASS"], PASSWORD, overwrite=False)
    assert "DB_PASS" in result2.already_encrypted
    assert "DB_PASS" not in result2.encrypted


def test_already_encrypted_key_re_encrypted_with_overwrite():
    profile = _make_profile()
    updated, _ = encrypt_fields(profile, ["DB_PASS"], PASSWORD)
    _, result2 = encrypt_fields(updated, ["DB_PASS"], PASSWORD, overwrite=True)
    assert "DB_PASS" in result2.encrypted


def test_decrypt_roundtrip():
    profile = _make_profile()
    encrypted, _ = encrypt_fields(profile, ["DB_PASS", "API_KEY"], PASSWORD)
    decrypted, result = decrypt_fields(encrypted, ["DB_PASS", "API_KEY"], PASSWORD)
    assert decrypted["DB_PASS"] == "hunter2"
    assert decrypted["API_KEY"] == "abc123"
    assert set(result.decrypted) == {"DB_PASS", "API_KEY"}


def test_decrypt_all_when_no_keys_specified():
    profile = _make_profile()
    encrypted, _ = encrypt_fields(profile, ["DB_PASS", "API_KEY"], PASSWORD)
    decrypted, result = decrypt_fields(encrypted, None, PASSWORD)
    assert decrypted["DB_PASS"] == "hunter2"
    assert decrypted["API_KEY"] == "abc123"
    assert "DB_HOST" in result.not_encrypted


def test_decrypt_plain_key_goes_to_not_encrypted():
    profile = _make_profile()
    _, result = decrypt_fields(profile, ["DB_HOST"], PASSWORD)
    assert "DB_HOST" in result.not_encrypted


def test_decrypt_wrong_password_raises():
    profile = _make_profile()
    encrypted, _ = encrypt_fields(profile, ["DB_PASS"], PASSWORD)
    with pytest.raises(FieldEncryptError):
        decrypt_fields(encrypted, ["DB_PASS"], "wrong-password")


def test_is_field_encrypted_true_for_prefixed():
    assert is_field_encrypted(FIELD_CIPHER_PREFIX + "someblob") is True


def test_is_field_encrypted_false_for_plain():
    assert is_field_encrypted("plaintext") is False
