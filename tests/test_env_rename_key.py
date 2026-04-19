"""Tests for envault.env_rename_key."""
import pytest
from pathlib import Path
from envault.vault import save_profile, load_profile
from envault.env_rename_key import rename_key, RenameKeyError, ok

PASSWORD = "testpass"


@pytest.fixture
def tmp_vault(tmp_path):
    return tmp_path / "vault"


def _save(vault, profile, data):
    save_profile(vault, profile, PASSWORD, data)


def test_rename_key_success(tmp_vault):
    _save(tmp_vault, "dev", {"OLD_KEY": "value", "OTHER": "x"})
    result = rename_key(tmp_vault, "dev", PASSWORD, "OLD_KEY", "NEW_KEY")
    assert ok(result)
    data = load_profile(tmp_vault, "dev", PASSWORD)
    assert "NEW_KEY" in data
    assert "OLD_KEY" not in data
    assert data["NEW_KEY"] == "value"


def test_rename_key_preserves_other_keys(tmp_vault):
    _save(tmp_vault, "dev", {"A": "1", "B": "2"})
    rename_key(tmp_vault, "dev", PASSWORD, "A", "Z")
    data = load_profile(tmp_vault, "dev", PASSWORD)
    assert data["B"] == "2"
    assert data["Z"] == "1"


def test_rename_key_missing_key_raises(tmp_vault):
    _save(tmp_vault, "dev", {"A": "1"})
    with pytest.raises(RenameKeyError, match="not found"):
        rename_key(tmp_vault, "dev", PASSWORD, "MISSING", "NEW")


def test_rename_key_existing_target_skips_without_overwrite(tmp_vault):
    _save(tmp_vault, "dev", {"A": "1", "B": "existing"})
    result = rename_key(tmp_vault, "dev", PASSWORD, "A", "B", overwrite=False)
    assert result.skipped
    assert "already exists" in result.reason
    data = load_profile(tmp_vault, "dev", PASSWORD)
    assert data["A"] == "1"
    assert data["B"] == "existing"


def test_rename_key_existing_target_overwrite(tmp_vault):
    _save(tmp_vault, "dev", {"A": "new_val", "B": "old_val"})
    result = rename_key(tmp_vault, "dev", PASSWORD, "A", "B", overwrite=True)
    assert ok(result)
    data = load_profile(tmp_vault, "dev", PASSWORD)
    assert data["B"] == "new_val"
    assert "A" not in data


def test_rename_key_result_fields(tmp_vault):
    _save(tmp_vault, "prod", {"FOO": "bar"})
    result = rename_key(tmp_vault, "prod", PASSWORD, "FOO", "BAZ")
    assert result.old_key == "FOO"
    assert result.new_key == "BAZ"
    assert result.profile == "prod"
