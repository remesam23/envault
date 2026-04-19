"""Tests for envault.patch module."""

import pytest
from pathlib import Path
from envault.vault import save_profile, load_profile
from envault.patch import patch_profile, patch_summary, PatchError

PASSWORD = "patchpass"


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def _save(vault, profile, data):
    save_profile(vault, profile, PASSWORD, data)


def test_patch_updates_existing_key(tmp_vault):
    _save(tmp_vault, "dev", {"HOST": "localhost", "PORT": "5432"})
    result = patch_profile(tmp_vault, "dev", PASSWORD, {"PORT": "9999"})
    assert result["PORT"] == "9999"
    assert result["HOST"] == "localhost"


def test_patch_adds_new_key(tmp_vault):
    _save(tmp_vault, "dev", {"HOST": "localhost"})
    result = patch_profile(tmp_vault, "dev", PASSWORD, {"DEBUG": "true"})
    assert result["DEBUG"] == "true"
    assert result["HOST"] == "localhost"


def test_patch_deletes_key(tmp_vault):
    _save(tmp_vault, "dev", {"HOST": "localhost", "SECRET": "abc"})
    result = patch_profile(tmp_vault, "dev", PASSWORD, {}, delete_keys=["SECRET"])
    assert "SECRET" not in result
    assert result["HOST"] == "localhost"


def test_patch_delete_missing_key_raises(tmp_vault):
    _save(tmp_vault, "dev", {"HOST": "localhost"})
    with pytest.raises(PatchError, match="MISSING"):
        patch_profile(tmp_vault, "dev", PASSWORD, {}, delete_keys=["MISSING"])


def test_patch_persists_to_vault(tmp_vault):
    _save(tmp_vault, "dev", {"A": "1"})
    patch_profile(tmp_vault, "dev", PASSWORD, {"B": "2"}, delete_keys=["A"])
    reloaded = load_profile(tmp_vault, "dev", PASSWORD)
    assert reloaded == {"B": "2"}


def test_patch_summary_set_and_delete():
    summary = patch_summary({"HOST": "prod"}, ["OLD_KEY"])
    assert "set   HOST=prod" in summary
    assert "del   OLD_KEY" in summary


def test_patch_summary_empty():
    summary = patch_summary({}, [])
    assert summary == "No changes applied."
