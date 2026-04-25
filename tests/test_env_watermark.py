"""Tests for envault.env_watermark."""
from __future__ import annotations

import pytest

from envault.env_watermark import (
    WATERMARK_KEY,
    WatermarkError,
    apply_watermark,
    verify_watermark,
    strip_watermark,
    _make_token,
)


PROFILE = "production"
SECRET = "s3cr3t"
DATA = {"DB_HOST": "localhost", "DB_PORT": "5432"}


# --- apply_watermark ---

def test_apply_adds_watermark_key():
    updated, result = apply_watermark(DATA, PROFILE, SECRET)
    assert WATERMARK_KEY in updated


def test_apply_preserves_existing_keys():
    updated, _ = apply_watermark(DATA, PROFILE, SECRET)
    for k, v in DATA.items():
        assert updated[k] == v


def test_apply_result_has_token():
    _, result = apply_watermark(DATA, PROFILE, SECRET)
    assert result.token and "." in result.token


def test_apply_empty_secret_raises():
    with pytest.raises(WatermarkError):
        apply_watermark(DATA, PROFILE, "")


def test_apply_token_stored_in_data():
    updated, result = apply_watermark(DATA, PROFILE, SECRET)
    assert updated[WATERMARK_KEY] == result.token


# --- verify_watermark ---

def test_verify_valid_watermark():
    updated, _ = apply_watermark(DATA, PROFILE, SECRET)
    result = verify_watermark(updated, PROFILE, SECRET)
    assert result.valid is True


def test_verify_wrong_secret_fails():
    updated, _ = apply_watermark(DATA, PROFILE, SECRET)
    result = verify_watermark(updated, PROFILE, "wrong")
    assert result.valid is False


def test_verify_missing_watermark_fails():
    result = verify_watermark(DATA, PROFILE, SECRET)
    assert result.valid is False
    assert "No watermark" in result.message


def test_verify_malformed_token_fails():
    bad = {**DATA, WATERMARK_KEY: "notavalidtoken"}
    result = verify_watermark(bad, PROFILE, SECRET)
    assert result.valid is False
    assert "Malformed" in result.message


def test_verify_wrong_profile_fails():
    updated, _ = apply_watermark(DATA, PROFILE, SECRET)
    result = verify_watermark(updated, "staging", SECRET)
    assert result.valid is False


def test_verify_empty_secret_raises():
    updated, _ = apply_watermark(DATA, PROFILE, SECRET)
    with pytest.raises(WatermarkError):
        verify_watermark(updated, PROFILE, "")


# --- strip_watermark ---

def test_strip_removes_watermark_key():
    updated, _ = apply_watermark(DATA, PROFILE, SECRET)
    stripped = strip_watermark(updated)
    assert WATERMARK_KEY not in stripped


def test_strip_preserves_other_keys():
    updated, _ = apply_watermark(DATA, PROFILE, SECRET)
    stripped = strip_watermark(updated)
    for k, v in DATA.items():
        assert stripped[k] == v


def test_strip_no_watermark_is_noop():
    stripped = strip_watermark(DATA)
    assert stripped == DATA
