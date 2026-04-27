"""Tests for envault.env_priority."""

from __future__ import annotations

import pytest

from envault.env_priority import (
    PriorityError,
    clear_priority,
    get_priority,
    list_priorities,
    ranked_profiles,
    set_priority,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_get_priority(tmp_vault):
    set_priority(tmp_vault, "production", 10)
    assert get_priority(tmp_vault, "production") == 10


def test_get_priority_missing_profile_returns_none(tmp_vault):
    assert get_priority(tmp_vault, "ghost") is None


def test_set_priority_overwrites_existing(tmp_vault):
    set_priority(tmp_vault, "staging", 5)
    set_priority(tmp_vault, "staging", 99)
    assert get_priority(tmp_vault, "staging") == 99


def test_clear_priority_removes_entry(tmp_vault):
    set_priority(tmp_vault, "dev", 1)
    clear_priority(tmp_vault, "dev")
    assert get_priority(tmp_vault, "dev") is None


def test_clear_priority_missing_raises(tmp_vault):
    with pytest.raises(PriorityError, match="No priority set"):
        clear_priority(tmp_vault, "nonexistent")


def test_list_priorities_sorted_descending(tmp_vault):
    set_priority(tmp_vault, "dev", 1)
    set_priority(tmp_vault, "production", 100)
    set_priority(tmp_vault, "staging", 50)
    entries = list_priorities(tmp_vault)
    priorities = [e["priority"] for e in entries]
    assert priorities == sorted(priorities, reverse=True)


def test_list_priorities_empty_vault(tmp_vault):
    assert list_priorities(tmp_vault) == []


def test_list_priorities_contains_all_entries(tmp_vault):
    set_priority(tmp_vault, "a", 10)
    set_priority(tmp_vault, "b", 20)
    profiles = {e["profile"] for e in list_priorities(tmp_vault)}
    assert profiles == {"a", "b"}


def test_ranked_profiles_orders_by_priority(tmp_vault):
    set_priority(tmp_vault, "dev", 1)
    set_priority(tmp_vault, "production", 100)
    set_priority(tmp_vault, "staging", 50)
    ranked = ranked_profiles(tmp_vault, ["dev", "staging", "production"])
    assert ranked == ["production", "staging", "dev"]


def test_ranked_profiles_unset_treated_as_zero(tmp_vault):
    set_priority(tmp_vault, "production", 5)
    ranked = ranked_profiles(tmp_vault, ["production", "unknown"])
    assert ranked[0] == "production"
    assert ranked[1] == "unknown"


def test_set_priority_returns_the_value(tmp_vault):
    result = set_priority(tmp_vault, "prod", 42)
    assert result == 42
