"""Tests for envault.merge module."""

import pytest
from envault.merge import merge_profiles, merge_summary, MergeConflictError


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
INCOMING = {"HOST": "remotehost", "PORT": "5432", "NEW_KEY": "hello"}


def test_merge_ours_keeps_base_on_conflict():
    result = merge_profiles(BASE, INCOMING, strategy="ours")
    assert result["HOST"] == "localhost"


def test_merge_ours_adds_new_keys():
    result = merge_profiles(BASE, INCOMING, strategy="ours")
    assert result["NEW_KEY"] == "hello"


def test_merge_ours_keeps_unchanged_keys():
    result = merge_profiles(BASE, INCOMING, strategy="ours")
    assert result["PORT"] == "5432"
    assert result["DEBUG"] == "true"


def test_merge_theirs_overwrites_on_conflict():
    result = merge_profiles(BASE, INCOMING, strategy="theirs")
    assert result["HOST"] == "remotehost"


def test_merge_theirs_adds_new_keys():
    result = merge_profiles(BASE, INCOMING, strategy="theirs")
    assert result["NEW_KEY"] == "hello"


def test_merge_error_raises_on_conflict():
    with pytest.raises(MergeConflictError) as exc_info:
        merge_profiles(BASE, INCOMING, strategy="error")
    assert "HOST" in exc_info.value.conflicts


def test_merge_error_no_conflict_succeeds():
    incoming_no_conflict = {"NEW_KEY": "hello"}
    result = merge_profiles(BASE, incoming_no_conflict, strategy="error")
    assert result["NEW_KEY"] == "hello"


def test_merge_identical_values_not_conflict():
    incoming_same = {"PORT": "5432"}
    result = merge_profiles(BASE, incoming_same, strategy="error")
    assert result["PORT"] == "5432"


def test_merge_empty_incoming():
    result = merge_profiles(BASE, {}, strategy="ours")
    assert result == BASE


def test_merge_empty_base():
    result = merge_profiles({}, INCOMING, strategy="ours")
    assert result == INCOMING


def test_merge_summary_added():
    merged = merge_profiles(BASE, INCOMING, strategy="ours")
    summary = merge_summary(BASE, INCOMING, merged)
    assert "NEW_KEY" in summary["added"]


def test_merge_summary_skipped_ours():
    merged = merge_profiles(BASE, INCOMING, strategy="ours")
    summary = merge_summary(BASE, INCOMING, merged)
    assert "HOST" in summary["skipped"]


def test_merge_summary_overwritten_theirs():
    merged = merge_profiles(BASE, INCOMING, strategy="theirs")
    summary = merge_summary(BASE, INCOMING, merged)
    assert "HOST" in summary["overwritten"]
