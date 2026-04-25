"""Tests for envault.env_crossref module."""
import pytest
from envault.env_crossref import (
    crossref_profiles,
    format_crossref,
    empty_result,
    CrossRefResult,
)


P1 = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}
P2 = {"DB_HOST": "prod.db",   "DB_PORT": "5432", "API_KEY": "xyz"}
P3 = {"DB_HOST": "staging",   "DB_PORT": "5432", "SECRET": "abc"}


def test_common_keys_present_in_all_profiles():
    result = crossref_profiles({"p1": P1, "p2": P2})
    assert "DB_PORT" in result.common_keys


def test_common_keys_excludes_partial_keys():
    result = crossref_profiles({"p1": P1, "p2": P2})
    assert "SECRET" not in result.common_keys
    assert "API_KEY" not in result.common_keys


def test_partial_keys_lists_correct_owners():
    result = crossref_profiles({"p1": P1, "p2": P2})
    assert "SECRET" in result.partial_keys
    assert result.partial_keys["SECRET"] == ["p1"]
    assert "API_KEY" in result.partial_keys
    assert result.partial_keys["API_KEY"] == ["p2"]


def test_value_conflict_detected():
    result = crossref_profiles({"p1": P1, "p2": P2})
    # DB_HOST is in both but differs
    assert "DB_HOST" in result.value_conflicts
    assert result.value_conflicts["DB_HOST"]["p1"] == "localhost"
    assert result.value_conflicts["DB_HOST"]["p2"] == "prod.db"


def test_no_conflict_when_values_identical():
    result = crossref_profiles({"p1": P1, "p2": P2})
    # DB_PORT is 5432 in both — no conflict
    assert "DB_PORT" not in result.value_conflicts


def test_three_profiles_common_key():
    result = crossref_profiles({"p1": P1, "p2": P2, "p3": P3})
    assert "DB_PORT" in result.common_keys


def test_three_profiles_partial_key():
    result = crossref_profiles({"p1": P1, "p2": P2, "p3": P3})
    # SECRET is in p1 and p3 but not p2
    assert "SECRET" in result.partial_keys
    owners = result.partial_keys["SECRET"]
    assert "p1" in owners and "p3" in owners
    assert "p2" not in owners


def test_empty_profiles_returns_empty_result():
    result = crossref_profiles({})
    assert result.common_keys == set()
    assert result.partial_keys == {}
    assert result.value_conflicts == {}
    assert result.profiles_checked == []


def test_single_profile_all_keys_are_common():
    result = crossref_profiles({"only": {"A": "1", "B": "2"}})
    assert "A" in result.common_keys
    assert "B" in result.common_keys
    assert result.partial_keys == {}
    assert result.value_conflicts == {}


def test_format_crossref_contains_profile_names():
    result = crossref_profiles({"dev": P1, "prod": P2})
    output = format_crossref(result)
    assert "dev" in output
    assert "prod" in output


def test_format_crossref_shows_conflicts():
    result = crossref_profiles({"dev": P1, "prod": P2})
    output = format_crossref(result)
    assert "DB_HOST" in output
    assert "localhost" in output
    assert "prod.db" in output


def test_format_crossref_no_conflicts_message():
    profiles = {"a": {"X": "1"}, "b": {"X": "1"}}
    result = crossref_profiles(profiles)
    output = format_crossref(result)
    assert "No value conflicts" in output
