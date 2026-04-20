"""Tests for envault.env_default."""
from __future__ import annotations

import pytest

from envault.env_default import (
    DefaultError,
    DefaultResult,
    apply_defaults,
    format_default_result,
    merge_into,
    ok,
)


# ---------------------------------------------------------------------------
# apply_defaults
# ---------------------------------------------------------------------------

def test_apply_adds_missing_keys():
    profile = {"A": "1"}
    defaults = {"A": "99", "B": "2", "C": "3"}
    result = apply_defaults(profile, defaults)
    assert "B" in result.applied
    assert "C" in result.applied
    assert result.ok is True


def test_apply_skips_existing_by_default():
    profile = {"A": "1"}
    defaults = {"A": "99"}
    result = apply_defaults(profile, defaults)
    assert "A" not in result.applied
    assert "A" in result.skipped


def test_apply_overwrite_replaces_existing():
    profile = {"A": "1"}
    defaults = {"A": "99"}
    result = apply_defaults(profile, defaults, overwrite=True)
    assert "A" in result.applied
    assert result.applied["A"] == "99"


def test_apply_empty_defaults_returns_empty_applied():
    profile = {"A": "1"}
    result = apply_defaults(profile, {})
    assert result.applied == {}
    assert result.skipped == []


def test_apply_empty_profile_fills_all_defaults():
    defaults = {"X": "10", "Y": "20"}
    result = apply_defaults({}, defaults)
    assert set(result.applied.keys()) == {"X", "Y"}


def test_apply_none_defaults_raises():
    with pytest.raises(DefaultError):
        apply_defaults({}, None)  # type: ignore[arg-type]


def test_ok_helper_returns_true_on_success():
    result = apply_defaults({}, {"K": "v"})
    assert ok(result) is True


# ---------------------------------------------------------------------------
# merge_into
# ---------------------------------------------------------------------------

def test_merge_into_does_not_overwrite_by_default():
    merged = merge_into({"A": "orig"}, {"A": "new", "B": "b"})
    assert merged["A"] == "orig"
    assert merged["B"] == "b"


def test_merge_into_overwrite_flag():
    merged = merge_into({"A": "orig"}, {"A": "new"}, overwrite=True)
    assert merged["A"] == "new"


def test_merge_into_does_not_mutate_original():
    profile = {"A": "1"}
    merge_into(profile, {"B": "2"})
    assert "B" not in profile


# ---------------------------------------------------------------------------
# format_default_result
# ---------------------------------------------------------------------------

def test_format_shows_applied_keys():
    result = DefaultResult(applied={"B": "2"}, skipped=[])
    text = format_default_result(result)
    assert "B=2" in text
    assert "Applied 1" in text


def test_format_shows_skipped_count():
    result = DefaultResult(applied={}, skipped=["A", "C"])
    text = format_default_result(result)
    assert "Skipped 2" in text


def test_format_empty_result_shows_no_defaults():
    result = DefaultResult(applied={}, skipped=[])
    text = format_default_result(result)
    assert "No defaults" in text
