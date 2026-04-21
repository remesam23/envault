"""Tests for envault.env_dedupe."""
import pytest
from envault.env_dedupe import (
    DedupeError,
    DedupeResult,
    dedupe_profile,
    find_duplicates,
    format_dedupe,
    ok,
)


def test_find_duplicates_detects_shared_values():
    profile = {"A": "x", "B": "x", "C": "y"}
    dupes = find_duplicates(profile)
    assert "x" in dupes
    assert set(dupes["x"]) == {"A", "B"}
    assert "y" not in dupes


def test_find_duplicates_no_dupes_returns_empty():
    profile = {"A": "1", "B": "2", "C": "3"}
    assert find_duplicates(profile) == {}


def test_find_duplicates_empty_profile():
    assert find_duplicates({}) == {}


def test_dedupe_keep_first_removes_later_keys():
    profile = {"A": "val", "B": "val", "C": "val"}
    result = dedupe_profile(profile, keep="first")
    assert "A" in result.profile
    assert "B" not in result.profile
    assert "C" not in result.profile
    assert set(result.removed) == {"B", "C"}


def test_dedupe_keep_last_removes_earlier_keys():
    profile = {"A": "val", "B": "val", "C": "val"}
    result = dedupe_profile(profile, keep="last")
    assert "C" in result.profile
    assert "A" not in result.profile
    assert "B" not in result.profile


def test_dedupe_no_duplicates_returns_unchanged_profile():
    profile = {"A": "1", "B": "2"}
    result = dedupe_profile(profile)
    assert result.profile == profile
    assert result.removed == []
    assert result.duplicates == {}


def test_dedupe_result_ok_flag_is_true():
    result = dedupe_profile({"X": "v", "Y": "v"})
    assert ok(result) is True


def test_dedupe_ignores_empty_values_by_default():
    profile = {"A": "", "B": "", "C": "real"}
    result = dedupe_profile(profile, ignore_empty=True)
    # empty values not treated as duplicates
    assert "A" in result.profile
    assert "B" in result.profile
    assert result.removed == []


def test_dedupe_includes_empty_values_when_flag_false():
    profile = {"A": "", "B": "", "C": "real"}
    result = dedupe_profile(profile, ignore_empty=False)
    assert len(result.removed) == 1


def test_dedupe_invalid_keep_raises():
    with pytest.raises(DedupeError, match="Invalid keep strategy"):
        dedupe_profile({"A": "v"}, keep="middle")


def test_dedupe_preserves_non_duplicate_keys():
    profile = {"A": "dup", "B": "dup", "C": "unique"}
    result = dedupe_profile(profile)
    assert "C" in result.profile
    assert result.profile["C"] == "unique"


def test_format_dedupe_no_duplicates():
    result = dedupe_profile({"A": "1", "B": "2"})
    output = format_dedupe(result)
    assert "No duplicate" in output


def test_format_dedupe_shows_duplicate_info():
    result = dedupe_profile({"A": "same", "B": "same"})
    output = format_dedupe(result)
    " in output
    assert "Removed" in output
