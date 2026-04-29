"""Tests for envault.env_checksum."""
import pytest
from envault.env_checksum import (
    record_checksum,
    verify_checksum,
    get_checksum,
    clear_checksum,
    list_checksums,
    ChecksumError,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_record_returns_hex_string(tmp_vault):
    cs = record_checksum(tmp_vault, "prod", {"KEY": "val"})
    assert isinstance(cs, str)
    assert len(cs) == 64  # SHA-256 hex


def test_get_checksum_after_record(tmp_vault):
    record_checksum(tmp_vault, "prod", {"KEY": "val"})
    cs = get_checksum(tmp_vault, "prod")
    assert cs is not None and len(cs) == 64


def test_get_checksum_missing_profile_returns_none(tmp_vault):
    assert get_checksum(tmp_vault, "ghost") is None


def test_verify_matches_when_data_unchanged(tmp_vault):
    data = {"A": "1", "B": "2"}
    record_checksum(tmp_vault, "dev", data)
    result = verify_checksum(tmp_vault, "dev", data)
    assert result.matched is True
    assert result.ok() is True


def test_verify_fails_when_data_changed(tmp_vault):
    record_checksum(tmp_vault, "dev", {"A": "1"})
    result = verify_checksum(tmp_vault, "dev", {"A": "TAMPERED"})
    assert result.matched is False
    assert result.ok() is False


def test_verify_ok_when_no_previous_checksum(tmp_vault):
    result = verify_checksum(tmp_vault, "new", {"X": "y"})
    assert result.previous is None
    assert result.ok() is True


def test_checksum_is_deterministic(tmp_vault):
    data = {"Z": "end", "A": "start"}
    cs1 = record_checksum(tmp_vault, "p", data)
    cs2 = record_checksum(tmp_vault, "p", data)
    assert cs1 == cs2


def test_different_data_different_checksum(tmp_vault):
    cs1 = record_checksum(tmp_vault, "p", {"K": "v1"})
    cs2 = record_checksum(tmp_vault, "p", {"K": "v2"})
    assert cs1 != cs2


def test_list_checksums_returns_all(tmp_vault):
    record_checksum(tmp_vault, "prod", {"A": "1"})
    record_checksum(tmp_vault, "dev", {"B": "2"})
    cs = list_checksums(tmp_vault)
    assert set(cs.keys()) == {"prod", "dev"}


def test_list_checksums_empty_vault(tmp_vault):
    assert list_checksums(tmp_vault) == {}


def test_clear_removes_checksum(tmp_vault):
    record_checksum(tmp_vault, "staging", {"K": "v"})
    clear_checksum(tmp_vault, "staging")
    assert get_checksum(tmp_vault, "staging") is None


def test_clear_missing_profile_raises(tmp_vault):
    with pytest.raises(ChecksumError, match="staging"):
        clear_checksum(tmp_vault, "staging")


def test_result_stores_previous_checksum(tmp_vault):
    record_checksum(tmp_vault, "prod", {"K": "v"})
    result = verify_checksum(tmp_vault, "prod", {"K": "changed"})
    assert result.previous is not None
    assert result.checksum != result.previous
