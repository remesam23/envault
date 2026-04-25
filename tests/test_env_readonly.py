"""Tests for envault.env_readonly."""
import pytest

from envault.env_readonly import (
    ReadOnlyError,
    get_readonly_reason,
    guard_readonly,
    is_readonly,
    list_readonly,
    set_readonly,
    unset_readonly,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_readonly_marks_profile(tmp_vault):
    set_readonly(tmp_vault, "production")
    assert is_readonly(tmp_vault, "production")


def test_is_readonly_returns_false_for_unknown(tmp_vault):
    assert not is_readonly(tmp_vault, "staging")


def test_set_readonly_with_reason(tmp_vault):
    set_readonly(tmp_vault, "prod", reason="stable release")
    assert get_readonly_reason(tmp_vault, "prod") == "stable release"


def test_set_readonly_no_reason_returns_none(tmp_vault):
    set_readonly(tmp_vault, "prod")
    assert get_readonly_reason(tmp_vault, "prod") is None


def test_unset_readonly_removes_profile(tmp_vault):
    set_readonly(tmp_vault, "prod")
    unset_readonly(tmp_vault, "prod")
    assert not is_readonly(tmp_vault, "prod")


def test_unset_readonly_not_set_raises(tmp_vault):
    with pytest.raises(ReadOnlyError, match="not marked as read-only"):
        unset_readonly(tmp_vault, "staging")


def test_list_readonly_returns_all(tmp_vault):
    set_readonly(tmp_vault, "prod", reason="live")
    set_readonly(tmp_vault, "staging")
    result = list_readonly(tmp_vault)
    assert "prod" in result
    assert "staging" in result
    assert result["prod"] == "live"
    assert result["staging"] is None


def test_list_readonly_empty_vault(tmp_vault):
    assert list_readonly(tmp_vault) == {}


def test_guard_readonly_raises_for_readonly_profile(tmp_vault):
    set_readonly(tmp_vault, "prod", reason="do not touch")
    with pytest.raises(ReadOnlyError, match="read-only"):
        guard_readonly(tmp_vault, "prod")


def test_guard_readonly_passes_for_normal_profile(tmp_vault):
    guard_readonly(tmp_vault, "dev")  # should not raise


def test_guard_readonly_message_includes_reason(tmp_vault):
    set_readonly(tmp_vault, "prod", reason="freeze period")
    with pytest.raises(ReadOnlyError, match="freeze period"):
        guard_readonly(tmp_vault, "prod")


def test_multiple_profiles_independent(tmp_vault):
    set_readonly(tmp_vault, "prod")
    assert not is_readonly(tmp_vault, "dev")
    assert is_readonly(tmp_vault, "prod")
