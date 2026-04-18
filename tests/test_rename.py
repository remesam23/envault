"""Tests for envault.rename module."""

import pytest
from envault.vault import save_profile, load_profile, list_profiles
from envault.rename import rename_profile, rename_summary, RenameError


PASSWORD = "test-secret"


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


def test_rename_profile_success(tmp_vault):
    save_profile(tmp_vault, "dev", {"KEY": "val"}, PASSWORD)
    rename_profile(tmp_vault, "dev", "development", PASSWORD)
    profiles = list_profiles(tmp_vault)
    assert "development" in profiles
    assert "dev" not in profiles


def test_rename_preserves_data(tmp_vault):
    save_profile(tmp_vault, "dev", {"KEY": "val", "OTHER": "123"}, PASSWORD)
    rename_profile(tmp_vault, "dev", "production", PASSWORD)
    data = load_profile(tmp_vault, "production", PASSWORD)
    assert data == {"KEY": "val", "OTHER": "123"}


def test_rename_missing_profile_raises(tmp_vault):
    with pytest.raises(RenameError, match="does not exist"):
        rename_profile(tmp_vault, "ghost", "new", PASSWORD)


def test_rename_to_existing_profile_raises(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1"}, PASSWORD)
    save_profile(tmp_vault, "prod", {"B": "2"}, PASSWORD)
    with pytest.raises(RenameError, match="already exists"):
        rename_profile(tmp_vault, "dev", "prod", PASSWORD)


def test_rename_old_name_no_longer_accessible(tmp_vault):
    from envault.vault import load_profile
    save_profile(tmp_vault, "dev", {"X": "y"}, PASSWORD)
    rename_profile(tmp_vault, "dev", "staging", PASSWORD)
    with pytest.raises(KeyError):
        load_profile(tmp_vault, "dev", PASSWORD)


def test_rename_summary():
    result = rename_summary("dev", "development")
    assert "dev" in result
    assert "development" in result
