"""Tests for envault.ttl module."""
import pytest
import time
from envault.ttl import set_ttl, get_ttl, clear_ttl, list_ttl, is_expired, TTLError


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_ttl_returns_expiry_string(tmp_vault):
    expiry = set_ttl(tmp_vault, "prod", 60)
    assert "T" in expiry  # ISO format


def test_get_ttl_after_set(tmp_vault):
    set_ttl(tmp_vault, "prod", 60)
    expiry = get_ttl(tmp_vault, "prod")
    assert expiry is not None


def test_get_ttl_missing_profile_returns_none(tmp_vault):
    assert get_ttl(tmp_vault, "ghost") is None


def test_not_expired_for_future_ttl(tmp_vault):
    set_ttl(tmp_vault, "prod", 3600)
    assert not is_expired(tmp_vault, "prod")


def test_expired_for_past_ttl(tmp_vault):
    set_ttl(tmp_vault, "prod", 1)
    time.sleep(1.1)
    assert is_expired(tmp_vault, "prod")


def test_no_ttl_is_not_expired(tmp_vault):
    assert not is_expired(tmp_vault, "prod")


def test_clear_ttl_removes_entry(tmp_vault):
    set_ttl(tmp_vault, "prod", 60)
    clear_ttl(tmp_vault, "prod")
    assert get_ttl(tmp_vault, "prod") is None


def test_clear_ttl_missing_raises(tmp_vault):
    with pytest.raises(TTLError):
        clear_ttl(tmp_vault, "ghost")


def test_list_ttl_empty(tmp_vault):
    assert list_ttl(tmp_vault) == {}


def test_list_ttl_multiple(tmp_vault):
    set_ttl(tmp_vault, "dev", 60)
    set_ttl(tmp_vault, "prod", 120)
    entries = list_ttl(tmp_vault)
    assert set(entries.keys()) == {"dev", "prod"}


def test_set_ttl_zero_raises(tmp_vault):
    with pytest.raises(TTLError):
        set_ttl(tmp_vault, "prod", 0)


def test_set_ttl_negative_raises(tmp_vault):
    with pytest.raises(TTLError):
        set_ttl(tmp_vault, "prod", -10)
