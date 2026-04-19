"""Tests for envault.promote."""
import os
import pytest
from envault.vault import save_profile
from envault.promote import promote_profile, promote_summary, PromoteError

PASSWORD = "testpass"


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault")


def _save(vault, profile, data):
    save_profile(vault, profile, PASSWORD, data)


def test_promote_all_keys(tmp_vault):
    _save(tmp_vault, "staging", {"A": "1", "B": "2"})
    result = promote_profile(tmp_vault, "staging", "prod", PASSWORD)
    assert set(result["promoted"]) == {"A", "B"}
    assert result["skipped"] == []


def test_promote_specific_keys(tmp_vault):
    _save(tmp_vault, "staging", {"A": "1", "B": "2", "C": "3"})
    result = promote_profile(tmp_vault, "staging", "prod", PASSWORD, keys=["A", "C"])
    assert set(result["promoted"]) == {"A", "C"}


def test_promote_skips_existing_without_overwrite(tmp_vault):
    _save(tmp_vault, "staging", {"A": "new"})
    _save(tmp_vault, "prod", {"A": "old"})
    result = promote_profile(tmp_vault, "staging", "prod", PASSWORD)
    assert "A" in result["skipped"]
    assert "A" not in result["promoted"]


def test_promote_overwrites_with_flag(tmp_vault):
    _save(tmp_vault, "staging", {"A": "new"})
    _save(tmp_vault, "prod", {"A": "old"})
    result = promote_profile(tmp_vault, "staging", "prod", PASSWORD, overwrite=True)
    assert "A" in result["promoted"]
    assert result["skipped"] == []


def test_promote_creates_dst_if_missing(tmp_vault):
    _save(tmp_vault, "staging", {"X": "1"})
    result = promote_profile(tmp_vault, "staging", "newenv", PASSWORD)
    assert result["promoted"] == ["X"]


def test_promote_missing_key_raises(tmp_vault):
    _save(tmp_vault, "staging", {"A": "1"})
    with pytest.raises(PromoteError, match="Keys not found"):
        promote_profile(tmp_vault, "staging", "prod", PASSWORD, keys=["MISSING"])


def test_promote_summary_contains_names(tmp_vault):
    _save(tmp_vault, "staging", {"A": "1"})
    result = promote_profile(tmp_vault, "staging", "prod", PASSWORD)
    summary = promote_summary(result)
    assert "staging" in summary
    assert "prod" in summary
    assert "A" in summary


def test_promote_summary_skipped_hint(tmp_vault):
    _save(tmp_vault, "staging", {"A": "1"})
    _save(tmp_vault, "prod", {"A": "old"})
    result = promote_profile(tmp_vault, "staging", "prod", PASSWORD)
    summary = promote_summary(result)
    assert "overwrite" in summary
