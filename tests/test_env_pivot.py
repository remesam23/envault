"""Tests for envault.env_pivot."""

import pytest
from envault.env_pivot import pivot_by_prefix, format_pivot, PivotResult


SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "mydb",
    "REDIS_HOST": "127.0.0.1",
    "REDIS_PORT": "6379",
    "DEBUG": "true",
}


def test_groups_by_prefix():
    result = pivot_by_prefix(SAMPLE)
    assert "DB" in result.groups
    assert "REDIS" in result.groups


def test_group_contains_correct_keys():
    result = pivot_by_prefix(SAMPLE)
    assert set(result.groups["DB"]) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_ungrouped_contains_no_delimiter_keys():
    result = pivot_by_prefix(SAMPLE)
    assert "DEBUG" in result.ungrouped


def test_ungrouped_keys_not_in_groups():
    result = pivot_by_prefix(SAMPLE)
    for key in result.ungrouped:
        for group_keys in result.groups.values():
            assert key not in group_keys


def test_empty_profile_returns_empty():
    result = pivot_by_prefix({})
    assert result.groups == {}
    assert result.ungrouped == {}
    assert result.ok is True


def test_all_ungrouped_when_no_delimiters():
    profile = {"FOO": "1", "BAR": "2", "BAZ": "3"}
    result = pivot_by_prefix(profile)
    assert result.groups == {}
    assert set(result.ungrouped) == {"FOO", "BAR", "BAZ"}


def test_min_group_size_filters_small_groups():
    profile = {"DB_HOST": "h", "DB_PORT": "p", "SOLO_KEY": "v"}
    result = pivot_by_prefix(profile, min_group_size=2)
    assert "DB" in result.groups
    assert "SOLO" not in result.groups
    assert "SOLO_KEY" in result.ungrouped


def test_custom_delimiter():
    profile = {"APP.HOST": "h", "APP.PORT": "p", "OTHER": "x"}
    result = pivot_by_prefix(profile, delimiter=".")
    assert "APP" in result.groups
    assert set(result.groups["APP"]) == {"APP.HOST", "APP.PORT"}


def test_format_pivot_contains_group_headers():
    result = pivot_by_prefix(SAMPLE)
    output = format_pivot(result)
    assert "[DB]" in output
    assert "[REDIS]" in output


def test_format_pivot_contains_ungrouped_section():
    result = pivot_by_prefix(SAMPLE)
    output = format_pivot(result)
    assert "[ungrouped]" in output
    assert "DEBUG" in output


def test_format_pivot_empty_produces_empty_string():
    result = pivot_by_prefix({})
    assert format_pivot(result) == ""


def test_values_preserved_in_groups():
    result = pivot_by_prefix(SAMPLE)
    assert result.groups["DB"]["DB_HOST"] == "localhost"
    assert result.groups["REDIS"]["REDIS_PORT"] == "6379"
