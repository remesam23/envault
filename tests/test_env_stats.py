"""Tests for envault.env_stats."""
import pytest
from envault.env_stats import compute_stats, format_stats


SAMPLE = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "supersecret",
    "DEBUG": "true",
    "EMPTY_VAL": "",
    "ALSO_TRUE": "true",  # duplicate of DEBUG
}


def test_total_keys():
    stats = compute_stats("dev", SAMPLE)
    assert stats.total_keys == 5


def test_empty_values():
    stats = compute_stats("dev", SAMPLE)
    assert stats.empty_values == 1


def test_duplicate_values():
    # "true" appears twice -> both are duplicates
    stats = compute_stats("dev", SAMPLE)
    assert stats.duplicate_values == 2


def test_unique_values():
    stats = compute_stats("dev", SAMPLE)
    # total 5 values, 2 duplicates => 3 unique
    assert stats.unique_values == 3


def test_longest_key():
    stats = compute_stats("dev", SAMPLE)
    assert stats.longest_key == "DATABASE_URL"


def test_shortest_key():
    stats = compute_stats("dev", SAMPLE)
    assert stats.shortest_key == "DEBUG"


def test_avg_value_length():
    stats = compute_stats("dev", SAMPLE)
    expected = round(sum(len(v) for v in SAMPLE.values()) / len(SAMPLE), 2)
    assert stats.avg_value_length == expected


def test_empty_profile():
    stats = compute_stats("empty", {})
    assert stats.total_keys == 0
    assert stats.empty_values == 0
    assert stats.longest_key == ""
    assert stats.avg_value_length == 0.0


def test_format_stats_contains_profile_name():
    stats = compute_stats("staging", SAMPLE)
    output = format_stats(stats)
    assert "staging" in output


def test_format_stats_contains_key_counts():
    stats = compute_stats("dev", SAMPLE)
    output = format_stats(stats)
    assert "5" in output
    assert "DATABASE_URL" in output
