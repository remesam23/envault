"""Tests for envault/env_expire.py"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from envault.env_expire import (
    set_key_expiry,
    get_key_expiry,
    is_key_expired,
    clear_key_expiry,
    list_expired_keys,
    list_all_expiries,
    ExpireError,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def _future(days=10):
    return datetime.now(timezone.utc) + timedelta(days=days)


def _past(days=1):
    return datetime.now(timezone.utc) - timedelta(days=days)


def test_set_and_get_expiry(tmp_vault):
    expiry = _future()
    result = set_key_expiry(tmp_vault, "prod", "API_KEY", expiry)
    assert result == expiry.isoformat()
    raw = get_key_expiry(tmp_vault, "prod", "API_KEY")
    assert raw == expiry.isoformat()


def test_get_expiry_missing_key_returns_none(tmp_vault):
    assert get_key_expiry(tmp_vault, "prod", "MISSING") is None


def test_get_expiry_missing_profile_returns_none(tmp_vault):
    assert get_key_expiry(tmp_vault, "ghost", "KEY") is None


def test_is_key_expired_future_returns_false(tmp_vault):
    set_key_expiry(tmp_vault, "prod", "TOKEN", _future())
    assert is_key_expired(tmp_vault, "prod", "TOKEN") is False


def test_is_key_expired_past_returns_true(tmp_vault):
    set_key_expiry(tmp_vault, "prod", "OLD_TOKEN", _past())
    assert is_key_expired(tmp_vault, "prod", "OLD_TOKEN") is True


def test_is_key_expired_no_entry_returns_false(tmp_vault):
    assert is_key_expired(tmp_vault, "prod", "NEVER_SET") is False


def test_clear_expiry_removes_key(tmp_vault):
    set_key_expiry(tmp_vault, "prod", "DB_PASS", _future())
    clear_key_expiry(tmp_vault, "prod", "DB_PASS")
    assert get_key_expiry(tmp_vault, "prod", "DB_PASS") is None


def test_clear_expiry_missing_raises(tmp_vault):
    with pytest.raises(ExpireError):
        clear_key_expiry(tmp_vault, "prod", "NONEXISTENT")


def test_list_expired_keys_returns_only_expired(tmp_vault):
    set_key_expiry(tmp_vault, "prod", "STALE", _past())
    set_key_expiry(tmp_vault, "prod", "FRESH", _future())
    expired = list_expired_keys(tmp_vault, "prod")
    assert "STALE" in expired
    assert "FRESH" not in expired


def test_list_expired_keys_empty_profile(tmp_vault):
    assert list_expired_keys(tmp_vault, "empty") == []


def test_list_all_expiries_returns_all_keys(tmp_vault):
    set_key_expiry(tmp_vault, "staging", "A", _future(5))
    set_key_expiry(tmp_vault, "staging", "B", _future(10))
    expiries = list_all_expiries(tmp_vault, "staging")
    assert set(expiries.keys()) == {"A", "B"}


def test_multiple_profiles_isolated(tmp_vault):
    set_key_expiry(tmp_vault, "prod", "KEY", _past())
    set_key_expiry(tmp_vault, "dev", "KEY", _future())
    assert is_key_expired(tmp_vault, "prod", "KEY") is True
    assert is_key_expired(tmp_vault, "dev", "KEY") is False


def test_overwrite_expiry(tmp_vault):
    set_key_expiry(tmp_vault, "prod", "API", _past())
    assert is_key_expired(tmp_vault, "prod", "API") is True
    set_key_expiry(tmp_vault, "prod", "API", _future())
    assert is_key_expired(tmp_vault, "prod", "API") is False
