"""Tests for envault.env_sort."""
import pytest
from envault.env_sort import sort_profile, format_sort_result, SortResult


SAMPLE = {"ZEBRA": "1", "APPLE": "2", "MANGO": "3"}


def test_sort_ascending():
    sorted_data, result = sort_profile(SAMPLE, "dev")
    assert list(sorted_data.keys()) == ["APPLE", "MANGO", "ZEBRA"]
    assert result.changed is True


def test_sort_descending():
    sorted_data, result = sort_profile(SAMPLE, "dev", reverse=True)
    assert list(sorted_data.keys()) == ["ZEBRA", "MANGO", "APPLE"]


def test_sort_already_sorted():
    data = {"ALPHA": "a", "BETA": "b", "GAMMA": "c"}
    _, result = sort_profile(data, "dev")
    assert result.changed is False


def test_sort_preserves_values():
    sorted_data, _ = sort_profile(SAMPLE, "dev")
    assert sorted_data["APPLE"] == "2"
    assert sorted_data["ZEBRA"] == "1"


def test_sort_group_prefix_brings_keys_first():
    data = {"DB_HOST": "h", "APP_NAME": "n", "DB_PORT": "5432", "LOG_LEVEL": "info"}
    sorted_data, result = sort_profile(data, "prod", group_prefix="DB_")
    keys = list(sorted_data.keys())
    assert keys.index("DB_HOST") < keys.index("APP_NAME")
    assert keys.index("DB_PORT") < keys.index("LOG_LEVEL")


def test_sort_group_prefix_secondary_sorted():
    data = {"DB_Z": "1", "ZEBRA": "2", "APPLE": "3", "DB_A": "4"}
    sorted_data, _ = sort_profile(data, "prod", group_prefix="DB_")
    keys = list(sorted_data.keys())
    assert keys[:2] == ["DB_A", "DB_Z"]
    assert keys[2:] == ["APPLE", "ZEBRA"]


def test_format_sort_result_changed():
    _, result = sort_profile(SAMPLE, "dev")
    output = format_sort_result(result)
    assert "dev" in output
    assert "APPLE" in output


def test_format_sort_result_unchanged():
    data = {"A": "1", "B": "2"}
    _, result = sort_profile(data, "dev")
    output = format_sort_result(result)
    assert "Already sorted" in output


def test_sort_empty_profile():
    sorted_data, result = sort_profile({}, "empty")
    assert sorted_data == {}
    assert result.changed is False
