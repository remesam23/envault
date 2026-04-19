"""Tests for envault.alias."""
import pytest
from envault.alias import (
    AliasError,
    set_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    get_aliases_for_profile,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_resolve_alias(tmp_vault):
    set_alias(tmp_vault, "prod", "production")
    assert resolve_alias(tmp_vault, "prod") == "production"


def test_resolve_unknown_name_returns_itself(tmp_vault):
    assert resolve_alias(tmp_vault, "staging") == "staging"


def test_set_alias_same_as_profile_raises(tmp_vault):
    with pytest.raises(AliasError, match="same as the profile"):
        set_alias(tmp_vault, "dev", "dev")


def test_remove_alias(tmp_vault):
    set_alias(tmp_vault, "prod", "production")
    remove_alias(tmp_vault, "prod")
    assert resolve_alias(tmp_vault, "prod") == "prod"


def test_remove_missing_alias_raises(tmp_vault):
    with pytest.raises(AliasError, match="not found"):
        remove_alias(tmp_vault, "ghost")


def test_list_aliases_empty(tmp_vault):
    assert list_aliases(tmp_vault) == {}


def test_list_aliases_multiple(tmp_vault):
    set_alias(tmp_vault, "p", "production")
    set_alias(tmp_vault, "d", "development")
    result = list_aliases(tmp_vault)
    assert result == {"p": "production", "d": "development"}


def test_overwrite_alias(tmp_vault):
    set_alias(tmp_vault, "p", "production")
    set_alias(tmp_vault, "p", "preview")
    assert resolve_alias(tmp_vault, "p") == "preview"


def test_get_aliases_for_profile(tmp_vault):
    set_alias(tmp_vault, "p", "production")
    set_alias(tmp_vault, "live", "production")
    set_alias(tmp_vault, "d", "development")
    aliases = get_aliases_for_profile(tmp_vault, "production")
    assert sorted(aliases) == ["live", "p"]


def test_get_aliases_for_profile_none(tmp_vault):
    set_alias(tmp_vault, "p", "production")
    assert get_aliases_for_profile(tmp_vault, "development") == []
