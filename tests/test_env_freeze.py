"""Tests for envault.env_freeze."""
import pytest

from envault.env_freeze import (
    FreezeError,
    assert_not_frozen,
    freeze_profile,
    get_freeze_reason,
    is_frozen,
    list_frozen,
    unfreeze_profile,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_freeze_profile(tmp_vault):
    freeze_profile(tmp_vault, "production")
    assert is_frozen(tmp_vault, "production") is True


def test_frozen_profile_not_in_other(tmp_vault):
    freeze_profile(tmp_vault, "production")
    assert is_frozen(tmp_vault, "staging") is False


def test_freeze_with_reason(tmp_vault):
    freeze_profile(tmp_vault, "prod", reason="release lock")
    assert get_freeze_reason(tmp_vault, "prod") == "release lock"


def test_freeze_without_reason_returns_none(tmp_vault):
    freeze_profile(tmp_vault, "prod")
    assert get_freeze_reason(tmp_vault, "prod") is None


def test_freeze_already_frozen_raises(tmp_vault):
    freeze_profile(tmp_vault, "prod")
    with pytest.raises(FreezeError, match="already frozen"):
        freeze_profile(tmp_vault, "prod")


def test_unfreeze_profile(tmp_vault):
    freeze_profile(tmp_vault, "staging")
    unfreeze_profile(tmp_vault, "staging")
    assert is_frozen(tmp_vault, "staging") is False


def test_unfreeze_not_frozen_raises(tmp_vault):
    with pytest.raises(FreezeError, match="not frozen"):
        unfreeze_profile(tmp_vault, "staging")


def test_list_frozen_returns_sorted(tmp_vault):
    freeze_profile(tmp_vault, "prod")
    freeze_profile(tmp_vault, "alpha")
    freeze_profile(tmp_vault, "staging")
    assert list_frozen(tmp_vault) == ["alpha", "prod", "staging"]


def test_list_frozen_empty(tmp_vault):
    assert list_frozen(tmp_vault) == []


def test_list_frozen_excludes_unfrozen(tmp_vault):
    freeze_profile(tmp_vault, "prod")
    freeze_profile(tmp_vault, "staging")
    unfreeze_profile(tmp_vault, "staging")
    assert list_frozen(tmp_vault) == ["prod"]


def test_assert_not_frozen_passes_when_not_frozen(tmp_vault):
    # Should not raise
    assert_not_frozen(tmp_vault, "dev")


def test_assert_not_frozen_raises_when_frozen(tmp_vault):
    freeze_profile(tmp_vault, "prod", reason="locked for deploy")
    with pytest.raises(FreezeError, match="frozen and cannot be modified"):
        assert_not_frozen(tmp_vault, "prod")


def test_assert_not_frozen_includes_reason(tmp_vault):
    freeze_profile(tmp_vault, "prod", reason="deploy window")
    with pytest.raises(FreezeError, match="deploy window"):
        assert_not_frozen(tmp_vault, "prod")
