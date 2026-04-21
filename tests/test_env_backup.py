"""Tests for envault.env_backup."""

from __future__ import annotations

import json
import os
import pytest

from envault.vault import save_profile
from envault.env_backup import (
    BackupError,
    backup_profiles,
    restore_profiles,
)

PASSWORD = "test-pass"


@pytest.fixture()
def tmp_vault(tmp_path):
    vault = str(tmp_path / "vault")
    os.makedirs(vault)
    return vault


def _save(vault, name, data):
    save_profile(vault, name, data, PASSWORD)


# ---------------------------------------------------------------------------
# backup_profiles
# ---------------------------------------------------------------------------

def test_backup_creates_file(tmp_vault, tmp_path):
    _save(tmp_vault, "dev", {"A": "1"})
    dest = str(tmp_path / "backup.json")
    result = backup_profiles(tmp_vault, PASSWORD, dest)
    assert os.path.exists(dest)
    assert result.profiles == ["dev"]


def test_backup_bundle_contains_data(tmp_vault, tmp_path):
    _save(tmp_vault, "dev", {"A": "1", "B": "2"})
    dest = str(tmp_path / "backup.json")
    backup_profiles(tmp_vault, PASSWORD, dest)
    payload = json.loads(open(dest).read())
    assert payload["profiles"]["dev"] == {"A": "1", "B": "2"}


def test_backup_multiple_profiles(tmp_vault, tmp_path):
    _save(tmp_vault, "dev", {"X": "1"})
    _save(tmp_vault, "prod", {"X": "2"})
    dest = str(tmp_path / "backup.json")
    result = backup_profiles(tmp_vault, PASSWORD, dest)
    assert set(result.profiles) == {"dev", "prod"}


def test_backup_selected_profiles_only(tmp_vault, tmp_path):
    _save(tmp_vault, "dev", {"X": "1"})
    _save(tmp_vault, "prod", {"X": "2"})
    dest = str(tmp_path / "backup.json")
    result = backup_profiles(tmp_vault, PASSWORD, dest, profiles=["dev"])
    assert result.profiles == ["dev"]
    payload = json.loads(open(dest).read())
    assert "prod" not in payload["profiles"]


def test_backup_unknown_profile_raises(tmp_vault, tmp_path):
    dest = str(tmp_path / "backup.json")
    with pytest.raises(BackupError, match="Unknown profile"):
        backup_profiles(tmp_vault, PASSWORD, dest, profiles=["ghost"])


# ---------------------------------------------------------------------------
# restore_profiles
# ---------------------------------------------------------------------------

def test_restore_loads_profiles(tmp_vault, tmp_path):
    _save(tmp_vault, "dev", {"A": "1"})
    dest = str(tmp_path / "backup.json")
    backup_profiles(tmp_vault, PASSWORD, dest)

    vault2 = str(tmp_path / "vault2")
    os.makedirs(vault2)
    result = restore_profiles(vault2, PASSWORD, dest)
    assert "dev" in result.restored


def test_restore_skips_existing_without_overwrite(tmp_vault, tmp_path):
    _save(tmp_vault, "dev", {"A": "1"})
    dest = str(tmp_path / "backup.json")
    backup_profiles(tmp_vault, PASSWORD, dest)
    result = restore_profiles(tmp_vault, PASSWORD, dest, overwrite=False)
    assert "dev" in result.skipped
    assert "dev" not in result.restored


def test_restore_overwrite_replaces_profile(tmp_vault, tmp_path):
    _save(tmp_vault, "dev", {"A": "old"})
    dest = str(tmp_path / "backup.json")
    # create backup with new value
    _save(tmp_vault, "dev", {"A": "new"})
    backup_profiles(tmp_vault, PASSWORD, dest)
    _save(tmp_vault, "dev", {"A": "old"})
    restore_profiles(tmp_vault, PASSWORD, dest, overwrite=True)
    from envault.vault import load_profile
    data = load_profile(tmp_vault, "dev", PASSWORD)
    assert data["A"] == "new"


def test_restore_bad_file_raises(tmp_vault, tmp_path):
    bad = str(tmp_path / "bad.json")
    with open(bad, "w") as f:
        f.write("not json")
    with pytest.raises(BackupError, match="Cannot read backup file"):
        restore_profiles(tmp_vault, PASSWORD, bad)
