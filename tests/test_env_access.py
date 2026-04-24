"""Tests for envault.env_access."""
import pytest
from envault.env_access import (
    AccessError,
    apply_access,
    clear_allowed_keys,
    get_allowed_keys,
    list_restricted_profiles,
    set_allowed_keys,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_get_allowed_keys(tmp_vault):
    result = set_allowed_keys(tmp_vault, "prod", ["DB_URL", "SECRET_KEY"])
    assert result == ["DB_URL", "SECRET_KEY"]
    assert get_allowed_keys(tmp_vault, "prod") == ["DB_URL", "SECRET_KEY"]


def test_set_deduplicates_keys(tmp_vault):
    result = set_allowed_keys(tmp_vault, "prod", ["A", "A", "B"])
    assert result == ["A", "B"]


def test_get_unknown_profile_returns_none(tmp_vault):
    assert get_allowed_keys(tmp_vault, "staging") is None


def test_clear_removes_restriction(tmp_vault):
    set_allowed_keys(tmp_vault, "prod", ["KEY"])
    clear_allowed_keys(tmp_vault, "prod")
    assert get_allowed_keys(tmp_vault, "prod") is None


def test_clear_missing_profile_raises(tmp_vault):
    with pytest.raises(AccessError, match="No access rules"):
        clear_allowed_keys(tmp_vault, "ghost")


def test_apply_access_filters_keys(tmp_vault):
    set_allowed_keys(tmp_vault, "prod", ["DB_URL"])
    env = {"DB_URL": "postgres://", "SECRET": "abc", "PORT": "5432"}
    result = apply_access(tmp_vault, "prod", env)
    assert result == {"DB_URL": "postgres://"}


def test_apply_access_unrestricted_returns_all(tmp_vault):
    env = {"A": "1", "B": "2"}
    result = apply_access(tmp_vault, "dev", env)
    assert result == env


def test_apply_access_key_not_in_env_ignored(tmp_vault):
    set_allowed_keys(tmp_vault, "prod", ["MISSING_KEY", "DB_URL"])
    env = {"DB_URL": "postgres://"}
    result = apply_access(tmp_vault, "prod", env)
    assert result == {"DB_URL": "postgres://"}


def test_list_restricted_profiles(tmp_vault):
    set_allowed_keys(tmp_vault, "prod", ["A"])
    set_allowed_keys(tmp_vault, "staging", ["B"])
    profiles = list_restricted_profiles(tmp_vault)
    assert profiles == ["prod", "staging"]


def test_list_restricted_empty_vault(tmp_vault):
    assert list_restricted_profiles(tmp_vault) == []


def test_overwrite_allowed_keys(tmp_vault):
    set_allowed_keys(tmp_vault, "prod", ["OLD_KEY"])
    set_allowed_keys(tmp_vault, "prod", ["NEW_KEY"])
    assert get_allowed_keys(tmp_vault, "prod") == ["NEW_KEY"]
