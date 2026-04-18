"""Tests for envault.diff module."""

import pytest
from envault.diff import diff_profiles, format_diff


OLD = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "old_secret"}
NEW = {"DB_HOST": "remotehost", "DB_PORT": "5432", "API_KEY": "abc123"}


def test_diff_added():
    result = diff_profiles(OLD, NEW)
    assert ("API_KEY", "abc123") in result["added"]


def test_diff_removed():
    result = diff_profiles(OLD, NEW)
    assert ("SECRET", "old_secret") in result["removed"]


def test_diff_changed():
    result = diff_profiles(OLD, NEW)
    assert ("DB_HOST", "localhost", "remotehost") in result["changed"]


def test_diff_unchanged_key_not_in_changed():
    result = diff_profiles(OLD, NEW)
    changed_keys = [k for k, _, _ in result["changed"]]
    assert "DB_PORT" not in changed_keys


def test_diff_identical_profiles():
    result = diff_profiles(OLD, OLD)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["changed"] == []


def test_diff_empty_old():
    result = diff_profiles({}, {"FOO": "bar"})
    assert result["added"] == [("FOO", "bar")]
    assert result["removed"] == []
    assert result["changed"] == []


def test_format_diff_masks_values():
    diff = diff_profiles(OLD, NEW)
    output = format_diff(diff, mask_values=True)
    assert "old_secret" not in output
    assert "abc123" not in output
    assert "***" in output


def test_format_diff_shows_values():
    diff = diff_profiles(OLD, NEW)
    output = format_diff(diff, mask_values=False)
    assert "abc123" in output
    assert "old_secret" in output


def test_format_diff_no_differences():
    diff = diff_profiles(OLD, OLD)
    output = format_diff(diff)
    assert "no differences" in output


def test_format_diff_prefixes():
    diff = diff_profiles(OLD, NEW)
    output = format_diff(diff, mask_values=False)
    assert any(line.strip().startswith("+") for line in output.splitlines())
    assert any(line.strip().startswith("-") for line in output.splitlines())
    assert any(line.strip().startswith("~") for line in output.splitlines())
