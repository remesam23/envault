"""Tests for envault.env_version."""
import pytest
from envault.env_version import (
    VersionError,
    VersionEntry,
    set_version,
    get_version,
    clear_version,
    list_versions,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_get_version(tmp_vault):
    entry = set_version(tmp_vault, "production", "1.0.0")
    assert entry.version == "1.0.0"
    result = get_version(tmp_vault, "production")
    assert result is not None
    assert result.version == "1.0.0"


def test_set_version_with_note(tmp_vault):
    set_version(tmp_vault, "staging", "2.3.1", note="initial staging release")
    result = get_version(tmp_vault, "staging")
    assert result.note == "initial staging release"


def test_set_version_no_note_returns_none(tmp_vault):
    set_version(tmp_vault, "dev", "0.1.0")
    result = get_version(tmp_vault, "dev")
    assert result.note is None


def test_get_version_missing_profile_returns_none(tmp_vault):
    assert get_version(tmp_vault, "nonexistent") is None


def test_invalid_version_format_raises(tmp_vault):
    with pytest.raises(VersionError, match="Invalid version format"):
        set_version(tmp_vault, "production", "v1.0")


def test_invalid_version_missing_patch_raises(tmp_vault):
    with pytest.raises(VersionError):
        set_version(tmp_vault, "production", "1.0")


def test_overwrite_version(tmp_vault):
    set_version(tmp_vault, "production", "1.0.0")
    set_version(tmp_vault, "production", "1.1.0", note="bump minor")
    result = get_version(tmp_vault, "production")
    assert result.version == "1.1.0"
    assert result.note == "bump minor"


def test_clear_version_removes_entry(tmp_vault):
    set_version(tmp_vault, "production", "1.0.0")
    clear_version(tmp_vault, "production")
    assert get_version(tmp_vault, "production") is None


def test_clear_version_missing_profile_raises(tmp_vault):
    with pytest.raises(VersionError, match="no version set"):
        clear_version(tmp_vault, "ghost")


def test_list_versions_returns_all(tmp_vault):
    set_version(tmp_vault, "production", "3.0.0")
    set_version(tmp_vault, "staging", "2.1.4")
    result = list_versions(tmp_vault)
    assert set(result.keys()) == {"production", "staging"}
    assert result["production"].version == "3.0.0"
    assert result["staging"].version == "2.1.4"


def test_list_versions_empty_vault(tmp_vault):
    assert list_versions(tmp_vault) == {}


def test_list_versions_returns_version_entries(tmp_vault):
    set_version(tmp_vault, "dev", "0.0.1", note="dev build")
    result = list_versions(tmp_vault)
    assert isinstance(result["dev"], VersionEntry)
    assert result["dev"].note == "dev build"
