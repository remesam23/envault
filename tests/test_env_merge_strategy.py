"""Tests for envault.env_merge_strategy."""

import pytest

from envault.env_merge_strategy import (
    STRATEGY_INTERSECT,
    STRATEGY_OURS,
    STRATEGY_THEIRS,
    STRATEGY_UNION,
    MergeStrategyError,
    apply_strategy,
    format_strategy_result,
)

BASE = {"A": "1", "B": "2", "C": "3"}
INCOMING = {"B": "99", "C": "3", "D": "4"}


# --- ours ---

def test_ours_keeps_base_on_conflict():
    r = apply_strategy(BASE, INCOMING, STRATEGY_OURS)
    assert r.merged["B"] == "2"


def test_ours_adds_new_keys_from_incoming():
    r = apply_strategy(BASE, INCOMING, STRATEGY_OURS)
    assert r.merged["D"] == "4"
    assert "D" in r.added


def test_ours_preserves_all_base_keys():
    r = apply_strategy(BASE, INCOMING, STRATEGY_OURS)
    assert "A" in r.merged and "B" in r.merged and "C" in r.merged


# --- theirs ---

def test_theirs_overwrites_on_conflict():
    r = apply_strategy(BASE, INCOMING, STRATEGY_THEIRS)
    assert r.merged["B"] == "99"
    assert "B" in r.overwritten


def test_theirs_adds_new_incoming_keys():
    r = apply_strategy(BASE, INCOMING, STRATEGY_THEIRS)
    assert r.merged["D"] == "4"
    assert "D" in r.added


def test_theirs_no_overwrite_when_value_same():
    r = apply_strategy(BASE, INCOMING, STRATEGY_THEIRS)
    assert "C" not in r.overwritten


# --- union ---

def test_union_contains_all_keys():
    r = apply_strategy(BASE, INCOMING, STRATEGY_UNION)
    assert set(r.merged.keys()) == {"A", "B", "C", "D"}


def test_union_base_wins_on_conflict():
    r = apply_strategy(BASE, INCOMING, STRATEGY_UNION)
    assert r.merged["B"] == "2"


def test_union_adds_new_key():
    r = apply_strategy(BASE, INCOMING, STRATEGY_UNION)
    assert "D" in r.added


# --- intersect ---

def test_intersect_only_common_keys():
    r = apply_strategy(BASE, INCOMING, STRATEGY_INTERSECT)
    assert set(r.merged.keys()) == {"B", "C"}


def test_intersect_keeps_base_values():
    r = apply_strategy(BASE, INCOMING, STRATEGY_INTERSECT)
    assert r.merged["B"] == "2"


def test_intersect_removed_lists_dropped_keys():
    r = apply_strategy(BASE, INCOMING, STRATEGY_INTERSECT)
    assert "A" in r.removed


# --- error ---

def test_invalid_strategy_raises():
    with pytest.raises(MergeStrategyError, match="Unknown strategy"):
        apply_strategy(BASE, INCOMING, "magic")


# --- format ---

def test_format_includes_strategy_name():
    r = apply_strategy(BASE, INCOMING, STRATEGY_THEIRS)
    out = format_strategy_result(r)
    assert "theirs" in out


def test_format_includes_total_keys():
    r = apply_strategy(BASE, INCOMING, STRATEGY_OURS)
    out = format_strategy_result(r)
    assert str(len(r.merged)) in out


def test_format_shows_added_when_present():
    r = apply_strategy(BASE, INCOMING, STRATEGY_OURS)
    out = format_strategy_result(r)
    assert "Added" in out and "D" in out


def test_format_no_added_section_when_empty():
    r = apply_strategy({"X": "1"}, {"X": "2"}, STRATEGY_OURS)
    out = format_strategy_result(r)
    assert "Added" not in out
