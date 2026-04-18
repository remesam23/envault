"""Tests for envault.vault module."""

import pytest
from pathlib import Path
from envault.vault import save_profile, load_profile, list_profiles, delete_profile


@pytest.fixture
def tmp_vault(tmp_path):
    return tmp_path / ".envault"


def test_save_and_load_profile(tmp_vault):
    content = "API_KEY=secret\nDEBUG=true\n"
    save_profile("dev", content, "pass123", vault_path=tmp_vault)
    result = load_profile("dev", "pass123", vault_path=tmp_vault)
    assert result == content


def test_load_missing_profile_raises(tmp_vault):
    with pytest.raises(KeyError, match="not found"):
        load_profile("ghost", "pw", vault_path=tmp_vault)


def test_list_profiles(tmp_vault):
    save_profile("dev", "A=1", "pw", vault_path=tmp_vault)
    save_profile("prod", "A=2", "pw", vault_path=tmp_vault)
    profiles = list_profiles(vault_path=tmp_vault)
    assert set(profiles) == {"dev", "prod"}


def test_list_empty_vault(tmp_vault):
    assert list_profiles(vault_path=tmp_vault) == []


def test_delete_profile(tmp_vault):
    save_profile("staging", "X=1", "pw", vault_path=tmp_vault)
    assert delete_profile("staging", vault_path=tmp_vault) is True
    assert "staging" not in list_profiles(vault_path=tmp_vault)


def test_delete_missing_profile(tmp_vault):
    assert delete_profile("nope", vault_path=tmp_vault) is False


def test_overwrite_profile(tmp_vault):
    save_profile("dev", "OLD=1", "pw", vault_path=tmp_vault)
    save_profile("dev", "NEW=2", "pw", vault_path=tmp_vault)
    assert load_profile("dev", "pw", vault_path=tmp_vault) == "NEW=2"
