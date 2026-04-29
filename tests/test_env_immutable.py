"""Tests for envault.env_immutable."""
import pytest

from envault.env_immutable import (
    ImmutableError,
    check_immutable,
    clear_immutable,
    get_immutable_keys,
    is_immutable,
    lock_keys,
    unlock_keys,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_lock_keys_returns_added(tmp_vault):
    added = lock_keys(tmp_vault, "prod", ["SECRET", "API_KEY"])
    assert sorted(added) == ["API_KEY", "SECRET"]


def test_lock_keys_stores_keys(tmp_vault):
    lock_keys(tmp_vault, "prod", ["SECRET", "API_KEY"])
    assert sorted(get_immutable_keys(tmp_vault, "prod")) == ["API_KEY", "SECRET"]


def test_lock_keys_deduplicates(tmp_vault):
    lock_keys(tmp_vault, "prod", ["SECRET"])
    added = lock_keys(tmp_vault, "prod", ["SECRET", "DB_PASS"])
    # SECRET is already locked, only DB_PASS is new
    assert added == ["DB_PASS"]
    assert sorted(get_immutable_keys(tmp_vault, "prod")) == ["DB_PASS", "SECRET"]


def test_get_immutable_keys_missing_profile_returns_empty(tmp_vault):
    assert get_immutable_keys(tmp_vault, "nonexistent") == []


def test_is_immutable_true(tmp_vault):
    lock_keys(tmp_vault, "prod", ["TOKEN"])
    assert is_immutable(tmp_vault, "prod", "TOKEN") is True


def test_is_immutable_false_for_unlocked_key(tmp_vault):
    lock_keys(tmp_vault, "prod", ["TOKEN"])
    assert is_immutable(tmp_vault, "prod", "OTHER") is False


def test_unlock_keys_removes_entry(tmp_vault):
    lock_keys(tmp_vault, "prod", ["SECRET", "API_KEY"])
    removed = unlock_keys(tmp_vault, "prod", ["SECRET"])
    assert removed == ["SECRET"]
    assert get_immutable_keys(tmp_vault, "prod") == ["API_KEY"]


def test_unlock_keys_raises_when_none_locked(tmp_vault):
    lock_keys(tmp_vault, "prod", ["TOKEN"])
    with pytest.raises(ImmutableError):
        unlock_keys(tmp_vault, "prod", ["NOT_LOCKED"])


def test_check_immutable_returns_locked_subset(tmp_vault):
    lock_keys(tmp_vault, "prod", ["SECRET", "API_KEY"])
    violations = check_immutable(tmp_vault, "prod", ["SECRET", "SAFE_KEY"])
    assert violations == ["SECRET"]


def test_check_immutable_empty_when_no_rules(tmp_vault):
    violations = check_immutable(tmp_vault, "prod", ["ANY_KEY"])
    assert violations == []


def test_clear_immutable_removes_profile(tmp_vault):
    lock_keys(tmp_vault, "prod", ["SECRET"])
    clear_immutable(tmp_vault, "prod")
    assert get_immutable_keys(tmp_vault, "prod") == []


def test_clear_immutable_missing_profile_raises(tmp_vault):
    with pytest.raises(ImmutableError):
        clear_immutable(tmp_vault, "ghost")


def test_profiles_are_isolated(tmp_vault):
    lock_keys(tmp_vault, "prod", ["SECRET"])
    lock_keys(tmp_vault, "staging", ["OTHER"])
    assert get_immutable_keys(tmp_vault, "prod") == ["SECRET"]
    assert get_immutable_keys(tmp_vault, "staging") == ["OTHER"]
