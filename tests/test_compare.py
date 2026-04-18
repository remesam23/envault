"""Tests for envault.compare."""
import pytest
from pathlib import Path
from envault.vault import save_profile
from envault.compare import compare_profiles, format_compare


PASSWORD = "testpass"


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault")


def _save(vault, profile, data):
    save_profile(vault, profile, data, PASSWORD)


def test_compare_identical_profiles(tmp_vault):
    data = {"KEY": "value", "FOO": "bar"}
    _save(tmp_vault, "a", data)
    _save(tmp_vault, "b", data)
    report = compare_profiles(tmp_vault, "a", "b", PASSWORD)
    assert report.identical
    assert report.diff.added == {}
    assert report.diff.removed == {}
    assert report.diff.changed == {}


def test_compare_added_keys(tmp_vault):
    _save(tmp_vault, "a", {"KEY": "val"})
    _save(tmp_vault, "b", {"KEY": "val", "EXTRA": "new"})
    report = compare_profiles(tmp_vault, "a", "b", PASSWORD)
    assert not report.identical
    assert "EXTRA" in report.diff.added


def test_compare_removed_keys(tmp_vault):
    _save(tmp_vault, "a", {"KEY": "val", "OLD": "gone"})
    _save(tmp_vault, "b", {"KEY": "val"})
    report = compare_profiles(tmp_vault, "a", "b", PASSWORD)
    assert "OLD" in report.diff.removed


def test_compare_changed_keys(tmp_vault):
    _save(tmp_vault, "a", {"KEY": "old"})
    _save(tmp_vault, "b", {"KEY": "new"})
    report = compare_profiles(tmp_vault, "a", "b", PASSWORD)
    assert "KEY" in report.diff.changed
    assert report.diff.changed["KEY"] == ("old", "new")


def test_compare_summary_identical(tmp_vault):
    data = {"K": "v"}
    _save(tmp_vault, "a", data)
    _save(tmp_vault, "b", data)
    report = compare_profiles(tmp_vault, "a", "b", PASSWORD)
    assert any("identical" in s.lower() for s in report.summary)


def test_compare_summary_counts(tmp_vault):
    _save(tmp_vault, "a", {"A": "1", "B": "2"})
    _save(tmp_vault, "b", {"B": "changed", "C": "3"})
    report = compare_profiles(tmp_vault, "a", "b", PASSWORD)
    text = " ".join(report.summary)
    assert "1 key(s) only in 'a'" in text
    assert "1 key(s) only in 'b'" in text
    assert "1 key(s) differ" in text


def test_format_compare_contains_profiles(tmp_vault):
    _save(tmp_vault, "dev", {"X": "1"})
    _save(tmp_vault, "prod", {"X": "2"})
    report = compare_profiles(tmp_vault, "dev", "prod", PASSWORD)
    out = format_compare(report)
    assert "dev" in out
    assert "prod" in out


def test_compare_missing_profile_raises(tmp_vault):
    _save(tmp_vault, "a", {"K": "v"})
    with pytest.raises(Exception):
        compare_profiles(tmp_vault, "a", "missing", PASSWORD)
