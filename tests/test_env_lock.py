import pytest
from envault.env_lock import (
    lock_profile,
    unlock_profile,
    is_locked,
    assert_unlocked,
    list_locked,
    EnvLockError,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_lock_profile(tmp_vault):
    lock_profile(tmp_vault, "production")
    assert is_locked(tmp_vault, "production") is True


def test_unlock_profile(tmp_vault):
    lock_profile(tmp_vault, "production")
    unlock_profile(tmp_vault, "production")
    assert is_locked(tmp_vault, "production") is False


def test_unlock_not_locked_raises(tmp_vault):
    with pytest.raises(EnvLockError, match="not locked"):
        unlock_profile(tmp_vault, "staging")


def test_is_locked_missing_profile_returns_false(tmp_vault):
    assert is_locked(tmp_vault, "nonexistent") is False


def test_assert_unlocked_passes_when_not_locked(tmp_vault):
    assert_unlocked(tmp_vault, "dev")  # should not raise


def test_assert_unlocked_raises_when_locked(tmp_vault):
    lock_profile(tmp_vault, "production")
    with pytest.raises(EnvLockError, match="locked"):
        assert_unlocked(tmp_vault, "production")


def test_list_locked_empty(tmp_vault):
    assert list_locked(tmp_vault) == []


def test_list_locked_multiple(tmp_vault):
    lock_profile(tmp_vault, "prod")
    lock_profile(tmp_vault, "staging")
    locked = list_locked(tmp_vault)
    assert set(locked) == {"prod", "staging"}


def test_lock_idempotent(tmp_vault):
    lock_profile(tmp_vault, "prod")
    lock_profile(tmp_vault, "prod")
    assert list_locked(tmp_vault).count("prod") == 1
