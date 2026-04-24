"""Tests for envault.env_scope."""
import pytest

from envault.env_scope import (
    ScopeError,
    apply_scope,
    clear_scope,
    get_scope,
    list_scopes,
    set_scope,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_get_scope(tmp_vault):
    keys = set_scope(tmp_vault, "prod", ["DB_URL", "SECRET_KEY"])
    assert sorted(keys) == ["DB_URL", "SECRET_KEY"]
    assert get_scope(tmp_vault, "prod") == ["DB_URL", "SECRET_KEY"]


def test_set_scope_deduplicates(tmp_vault):
    keys = set_scope(tmp_vault, "prod", ["A", "A", "B"])
    assert keys == ["A", "B"]


def test_get_scope_missing_profile_returns_none(tmp_vault):
    assert get_scope(tmp_vault, "nonexistent") is None


def test_clear_scope_removes_entry(tmp_vault):
    set_scope(tmp_vault, "staging", ["KEY1"])
    clear_scope(tmp_vault, "staging")
    assert get_scope(tmp_vault, "staging") is None


def test_clear_scope_missing_profile_raises(tmp_vault):
    with pytest.raises(ScopeError, match="No scope defined"):
        clear_scope(tmp_vault, "ghost")


def test_apply_scope_filters_keys(tmp_vault):
    set_scope(tmp_vault, "prod", ["ALLOWED"])
    env = {"ALLOWED": "yes", "BLOCKED": "no"}
    result = apply_scope(tmp_vault, "prod", env)
    assert result == {"ALLOWED": "yes"}


def test_apply_scope_no_scope_returns_full_env(tmp_vault):
    env = {"A": "1", "B": "2"}
    result = apply_scope(tmp_vault, "dev", env)
    assert result == env


def test_apply_scope_empty_scope_returns_empty(tmp_vault):
    set_scope(tmp_vault, "empty", [])
    env = {"A": "1"}
    result = apply_scope(tmp_vault, "empty", env)
    assert result == {}


def test_list_scopes_returns_all(tmp_vault):
    set_scope(tmp_vault, "prod", ["X"])
    set_scope(tmp_vault, "dev", ["Y", "Z"])
    scopes = list_scopes(tmp_vault)
    assert set(scopes.keys()) == {"prod", "dev"}


def test_list_scopes_empty_vault(tmp_vault):
    assert list_scopes(tmp_vault) == {}


def test_set_scope_overwrites_existing(tmp_vault):
    set_scope(tmp_vault, "prod", ["OLD"])
    set_scope(tmp_vault, "prod", ["NEW"])
    assert get_scope(tmp_vault, "prod") == ["NEW"]
