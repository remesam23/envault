"""Tests for envault.env_filter."""
import pytest
from envault.env_filter import (
    filter_by_prefix, filter_by_pattern, filter_by_predicate,
    format_filter_result, FilterResult,
)

SAMPLE = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "myapp",
    "APP_ENV": "prod",
    "SECRET_KEY": "abc123",
}


def test_filter_by_prefix_returns_matching_keys():
    result = filter_by_prefix(SAMPLE, "DB_")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PORT"}


def test_filter_by_prefix_skips_others():
    result = filter_by_prefix(SAMPLE, "DB_")
    assert "APP_NAME" in result.skipped
    assert "SECRET_KEY" in result.skipped


def test_filter_by_prefix_no_match_returns_empty():
    result = filter_by_prefix(SAMPLE, "MISSING_")
    assert result.matched == {}
    assert len(result.skipped) == len(SAMPLE)


def test_filter_by_pattern_glob():
    result = filter_by_pattern(SAMPLE, "APP_*")
    assert set(result.matched.keys()) == {"APP_NAME", "APP_ENV"}


def test_filter_by_pattern_exact():
    result = filter_by_pattern(SAMPLE, "SECRET_KEY")
    assert list(result.matched.keys()) == ["SECRET_KEY"]


def test_filter_by_pattern_no_match():
    result = filter_by_pattern(SAMPLE, "NOPE_*")
    assert result.matched == {}


def test_filter_by_predicate_on_value():
    result = filter_by_predicate(SAMPLE, lambda k, v: v.isdigit())
    assert result.matched == {"DB_PORT": "5432"}


def test_filter_by_predicate_all_match():
    result = filter_by_predicate(SAMPLE, lambda k, v: True)
    assert len(result.matched) == len(SAMPLE)
    assert result.skipped == []


def test_filter_result_ok_when_matched():
    result = FilterResult(matched={"A": "1"}, skipped=[])
    assert result.ok is True


def test_filter_result_not_ok_when_empty():
    result = FilterResult(matched={}, skipped=["A"])
    assert result.ok is False


def test_format_filter_result_contains_profile_name():
    result = filter_by_prefix(SAMPLE, "DB_")
    output = format_filter_result(result, "production")
    assert "production" in output
    assert "Matched" in output
    assert "Skipped" in output
