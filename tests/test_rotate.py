"""Tests for envault.rotate."""

import os
import pytest
from envault.vault import save_profile, load_profile, list_profiles
from envault.rotate import rotate_password, rotate_summary, RotationError


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.json")


OLD_PW = "old-secret"
NEW_PW = "new-secret"


def test_rotate_re_encrypts_all_profiles(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1"}, OLD_PW)
    save_profile(tmp_vault, "prod", {"B": "2"}, OLD_PW)

    rotated = rotate_password(tmp_vault, OLD_PW, NEW_PW)
    assert set(rotated) == {"dev", "prod"}

    assert load_profile(tmp_vault, "dev", NEW_PW) == {"A": "1"}
    assert load_profile(tmp_vault, "prod", NEW_PW) == {"B": "2"}


def test_rotate_old_password_no_longer_works(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1"}, OLD_PW)
    rotate_password(tmp_vault, OLD_PW, NEW_PW)

    with pytest.raises(Exception):
        load_profile(tmp_vault, "dev", OLD_PW)


def test_rotate_wrong_old_password_raises(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1"}, OLD_PW)

    with pytest.raises(RotationError):
        rotate_password(tmp_vault, "wrong-password", NEW_PW)


def test_rotate_empty_vault_returns_empty(tmp_vault):
    rotated = rotate_password(tmp_vault, OLD_PW, NEW_PW)
    assert rotated == []


def test_rotate_preserves_profile_list(tmp_vault):
    save_profile(tmp_vault, "staging", {"X": "y"}, OLD_PW)
    rotate_password(tmp_vault, OLD_PW, NEW_PW)
    assert list_profiles(tmp_vault) == ["staging"]


def test_rotate_summary_multiple():
    summary = rotate_summary(["dev", "prod"])
    assert "2 profile(s)" in summary
    assert "dev" in summary
    assert "prod" in summary


def test_rotate_summary_empty():
    summary = rotate_summary([])
    assert "nothing" in summary.lower()
