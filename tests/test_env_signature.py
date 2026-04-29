"""Tests for envault.env_signature."""
from __future__ import annotations

import json
import time

import pytest

from envault.env_signature import (
    SignatureError,
    list_signatures,
    remove_signature,
    sign_profile,
    verify_profile,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


DATA = {"DB_HOST": "localhost", "DB_PORT": "5432"}
SECRET = "supersecret"


def test_sign_returns_result(tmp_vault):
    result = sign_profile(tmp_vault, "prod", DATA, SECRET)
    assert result.profile == "prod"
    assert isinstance(result.signature, str) and len(result.signature) == 64
    assert result.ok is True


def test_sign_stores_signature_on_disk(tmp_vault):
    sign_profile(tmp_vault, "prod", DATA, SECRET)
    sig_file = __import__("pathlib").Path(tmp_vault) / ".signatures.json"
    assert sig_file.exists()
    stored = json.loads(sig_file.read_text())
    assert "prod" in stored


def test_verify_valid_signature(tmp_vault):
    sign_profile(tmp_vault, "prod", DATA, SECRET)
    result = verify_profile(tmp_vault, "prod", DATA, SECRET)
    assert result.valid is True
    assert "valid" in result.message


def test_verify_tampered_data_fails(tmp_vault):
    sign_profile(tmp_vault, "prod", DATA, SECRET)
    tampered = {**DATA, "DB_HOST": "evil.host"}
    result = verify_profile(tmp_vault, "prod", tampered, SECRET)
    assert result.valid is False
    assert "mismatch" in result.message


def test_verify_wrong_secret_fails(tmp_vault):
    sign_profile(tmp_vault, "prod", DATA, SECRET)
    result = verify_profile(tmp_vault, "prod", DATA, "wrongsecret")
    assert result.valid is False


def test_verify_unsigned_profile_returns_no_signature(tmp_vault):
    result = verify_profile(tmp_vault, "staging", DATA, SECRET)
    assert result.valid is False
    assert "no signature" in result.message


def test_sign_empty_secret_raises(tmp_vault):
    with pytest.raises(SignatureError):
        sign_profile(tmp_vault, "prod", DATA, "")


def test_verify_empty_secret_raises(tmp_vault):
    with pytest.raises(SignatureError):
        verify_profile(tmp_vault, "prod", DATA, "")


def test_remove_signature(tmp_vault):
    sign_profile(tmp_vault, "prod", DATA, SECRET)
    remove_signature(tmp_vault, "prod")
    result = verify_profile(tmp_vault, "prod", DATA, SECRET)
    assert result.valid is False


def test_remove_missing_signature_raises(tmp_vault):
    with pytest.raises(SignatureError, match="no signature"):
        remove_signature(tmp_vault, "ghost")


def test_list_signatures_returns_profiles(tmp_vault):
    sign_profile(tmp_vault, "prod", DATA, SECRET)
    sign_profile(tmp_vault, "staging", {"X": "1"}, SECRET)
    sigs = list_signatures(tmp_vault)
    assert set(sigs.keys()) == {"prod", "staging"}


def test_list_signatures_empty_vault(tmp_vault):
    assert list_signatures(tmp_vault) == {}


def test_sign_records_timestamp(tmp_vault):
    before = time.time()
    result = sign_profile(tmp_vault, "prod", DATA, SECRET)
    after = time.time()
    assert before <= result.signed_at <= after


def test_different_secrets_produce_different_signatures(tmp_vault):
    r1 = sign_profile(tmp_vault, "prod", DATA, "secret-a")
    r2 = sign_profile(tmp_vault, "prod", DATA, "secret-b")
    assert r1.signature != r2.signature
