"""Tests for envault.env_reorder."""
import pytest
from envault.env_reorder import (
    ReorderError,
    ReorderResult,
    ok,
    reorder_profile,
    format_reorder_result,
)


PROFILE = {"DB_HOST": "localhost", "API_KEY": "abc", "APP_ENV": "dev", "PORT": "8080"}


def test_reorder_puts_keys_in_specified_order():
    result = reorder_profile(PROFILE, ["APP_ENV", "DB_HOST", "PORT", "API_KEY"])
    assert list(result.reordered.keys()) == ["APP_ENV", "DB_HOST", "PORT", "API_KEY"]


def test_reorder_preserves_values():
    result = reorder_profile(PROFILE, ["PORT", "API_KEY"])
    assert result.reordered["PORT"] == "8080"
    assert result.reordered["API_KEY"] == "abc"


def test_reorder_appends_remaining_sorted():
    result = reorder_profile(PROFILE, ["PORT"])
    keys = list(result.reordered.keys())
    assert keys[0] == "PORT"
    # remaining should be sorted alphabetically
    assert keys[1:] == sorted(["API_KEY", "APP_ENV", "DB_HOST"])


def test_reorder_appended_list_contains_remaining_keys():
    result = reorder_profile(PROFILE, ["PORT"])
    assert set(result.appended) == {"API_KEY", "APP_ENV", "DB_HOST"}


def test_reorder_no_append_remaining_drops_unlisted():
    result = reorder_profile(PROFILE, ["PORT", "API_KEY"], append_remaining=False)
    assert list(result.reordered.keys()) == ["PORT", "API_KEY"]
    assert result.appended == []


def test_reorder_key_not_in_profile_is_skipped():
    result = reorder_profile(PROFILE, ["MISSING_KEY", "PORT"])
    assert "MISSING_KEY" not in result.reordered
    assert "PORT" in result.reordered


def test_reorder_empty_order_appends_all_sorted():
    result = reorder_profile(PROFILE, [])
    assert list(result.reordered.keys()) == sorted(PROFILE.keys())
    assert result.moved == []


def test_reorder_empty_profile_returns_empty():
    result = reorder_profile({}, ["A", "B"])
    assert result.reordered == {}
    assert result.moved == []
    assert result.appended == []


def test_ok_returns_true_on_success():
    result = reorder_profile(PROFILE, ["PORT"])
    assert ok(result) is True


def test_invalid_profile_raises():
    with pytest.raises(ReorderError):
        reorder_profile("not-a-dict", [])


def test_invalid_key_order_raises():
    with pytest.raises(ReorderError):
        reorder_profile(PROFILE, "not-a-list")


def test_format_shows_moved_keys():
    result = reorder_profile(PROFILE, ["PORT", "API_KEY", "APP_ENV", "DB_HOST"])
    output = format_reorder_result(result)
    assert "Moved" in output or "No changes" in output


def test_format_no_changes_message():
    # Profile already in the given order
    ordered = {"A": "1", "B": "2"}
    result = reorder_profile(ordered, ["A", "B"], append_remaining=False)
    output = format_reorder_result(result)
    assert "No changes" in output


def test_format_shows_appended_keys():
    result = reorder_profile(PROFILE, ["PORT"], append_remaining=True)
    output = format_reorder_result(result)
    assert "Appended" in output
