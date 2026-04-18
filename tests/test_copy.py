"""Tests for envault.copy module."""

import pytest
from envault.vault import save_profile
from envault.copy import copy_keys, copy_summary, CopyError


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault")


PASSWORD = "test-pass"


def test_copy_all_keys(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1", "B": "2"}, PASSWORD)
    result = copy_keys(tmp_vault, "dev", "staging", PASSWORD)
    assert set(result["copied"]) == {"A", "B"}
    assert result["skipped"] == []


def test_copy_specific_keys(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1", "B": "2", "C": "3"}, PASSWORD)
    result = copy_keys(tmp_vault, "dev", "staging", PASSWORD, keys=["A", "C"])
    assert set(result["copied"]) == {"A", "C"}


def test_copy_skips_existing_without_overwrite(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1", "B": "2"}, PASSWORD)
    save_profile(tmp_vault, "staging", {"A": "old"}, PASSWORD)
    result = copy_keys(tmp_vault, "dev", "staging", PASSWORD)
    assert "A" in result["skipped"]
    assert "B" in result["copied"]


def test_copy_overwrite_flag(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "new"}, PASSWORD)
    save_profile(tmp_vault, "staging", {"A": "old"}, PASSWORD)
    result = copy_keys(tmp_vault, "dev", "staging", PASSWORD, overwrite=True)
    assert "A" in result["copied"]
    assert result["skipped"] == []


def test_copy_creates_dst_if_missing(tmp_vault):
    save_profile(tmp_vault, "dev", {"X": "42"}, PASSWORD)
    result = copy_keys(tmp_vault, "dev", "newenv", PASSWORD)
    assert result["copied"] == ["X"]


def test_copy_missing_key_raises(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1"}, PASSWORD)
    with pytest.raises(CopyError, match="Keys not found"):
        copy_keys(tmp_vault, "dev", "staging", PASSWORD, keys=["MISSING"])


def test_copy_summary_copied(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1"}, PASSWORD)
    result = copy_keys(tmp_vault, "dev", "staging", PASSWORD)
    summary = copy_summary(result)
    assert "Copied" in summary


def test_copy_summary_skipped(tmp_vault):
    save_profile(tmp_vault, "dev", {"A": "1"}, PASSWORD)
    save_profile(tmp_vault, "staging", {"A": "old"}, PASSWORD)
    result = copy_keys(tmp_vault, "dev", "staging", PASSWORD)
    summary = copy_summary(result)
    assert "Skipped" in summary


def test_copy_summary_nothing(tmp_vault):
    result = {"copied": [], "skipped": []}
    assert copy_summary(result) == "Nothing to copy."
