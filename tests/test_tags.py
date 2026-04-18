"""Tests for envault.tags module."""
import pytest
from envault.tags import add_tag, remove_tag, get_tags, profiles_by_tag, remove_profile_tags, TagError


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_add_and_get_tag(tmp_vault):
    add_tag(tmp_vault, "dev", "staging")
    assert "staging" in get_tags(tmp_vault, "dev")


def test_add_duplicate_tag_is_idempotent(tmp_vault):
    add_tag(tmp_vault, "dev", "staging")
    add_tag(tmp_vault, "dev", "staging")
    assert get_tags(tmp_vault, "dev").count("staging") == 1


def test_get_tags_missing_profile_returns_empty(tmp_vault):
    assert get_tags(tmp_vault, "nonexistent") == []


def test_remove_tag(tmp_vault):
    add_tag(tmp_vault, "dev", "active")
    remove_tag(tmp_vault, "dev", "active")
    assert "active" not in get_tags(tmp_vault, "dev")


def test_remove_missing_tag_raises(tmp_vault):
    with pytest.raises(TagError):
        remove_tag(tmp_vault, "dev", "ghost")


def test_profiles_by_tag(tmp_vault):
    add_tag(tmp_vault, "dev", "env:local")
    add_tag(tmp_vault, "staging", "env:local")
    add_tag(tmp_vault, "prod", "env:prod")
    result = profiles_by_tag(tmp_vault, "env:local")
    assert set(result) == {"dev", "staging"}


def test_profiles_by_tag_none_match(tmp_vault):
    assert profiles_by_tag(tmp_vault, "unknown") == []


def test_remove_profile_tags(tmp_vault):
    add_tag(tmp_vault, "dev", "t1")
    add_tag(tmp_vault, "dev", "t2")
    remove_profile_tags(tmp_vault, "dev")
    assert get_tags(tmp_vault, "dev") == []


def test_multiple_profiles_independent(tmp_vault):
    add_tag(tmp_vault, "dev", "alpha")
    add_tag(tmp_vault, "prod", "beta")
    assert get_tags(tmp_vault, "dev") == ["alpha"]
    assert get_tags(tmp_vault, "prod") == ["beta"]
