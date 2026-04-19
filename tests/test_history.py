"""Tests for envault.history module."""
import time
import pytest
from envault.history import (
    record_snapshot,
    get_history,
    clear_history,
    format_history,
)


@pytest.fixture
def tmp_vault(tmp_path):
    vault = str(tmp_path / ".envault")
    import os
    os.makedirs(vault, exist_ok=True)
    return vault


def test_record_returns_entry(tmp_vault):
    env = {"KEY": "value"}
    entry = record_snapshot(tmp_vault, "dev", env)
    assert entry["env"] == env
    assert "timestamp" in entry


def test_get_history_returns_all_entries(tmp_vault):
    record_snapshot(tmp_vault, "dev", {"A": "1"})
    record_snapshot(tmp_vault, "dev", {"A": "2"})
    entries = get_history(tmp_vault, "dev")
    assert len(entries) == 2
    assert entries[0]["env"] == {"A": "1"}
    assert entries[1]["env"] == {"A": "2"}


def test_get_history_missing_profile_returns_empty(tmp_vault):
    assert get_history(tmp_vault, "nonexistent") == []


def test_history_isolated_per_profile(tmp_vault):
    record_snapshot(tmp_vault, "dev", {"X": "1"})
    record_snapshot(tmp_vault, "prod", {"Y": "2"})
    assert len(get_history(tmp_vault, "dev")) == 1
    assert len(get_history(tmp_vault, "prod")) == 1


def test_clear_history_returns_count(tmp_vault):
    record_snapshot(tmp_vault, "dev", {"A": "1"})
    record_snapshot(tmp_vault, "dev", {"B": "2"})
    removed = clear_history(tmp_vault, "dev")
    assert removed == 2
    assert get_history(tmp_vault, "dev") == []


def test_clear_missing_profile_returns_zero(tmp_vault):
    assert clear_history(tmp_vault, "ghost") == 0


def test_format_history_empty():
    assert format_history([]) == "No history found."


def test_format_history_shows_keys(tmp_vault):
    record_snapshot(tmp_vault, "dev", {"FOO": "bar", "BAZ": "qux"})
    entries = get_history(tmp_vault, "dev")
    output = format_history(entries)
    assert "FOO" in output
    assert "BAZ" in output


def test_format_history_with_values(tmp_vault):
    record_snapshot(tmp_vault, "dev", {"SECRET": "abc"})
    entries = get_history(tmp_vault, "dev")
    output = format_history(entries, show_values=True)
    assert "SECRET=abc" in output
