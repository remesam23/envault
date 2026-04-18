"""Tests for envault.audit module."""

import pytest
from envault.audit import record_event, get_events, clear_events


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_record_and_get_events(tmp_vault):
    record_event(tmp_vault, "lock", "prod")
    events = get_events(tmp_vault)
    assert len(events) == 1
    assert events[0]["action"] == "lock"
    assert events[0]["profile"] == "prod"


def test_multiple_events(tmp_vault):
    record_event(tmp_vault, "lock", "prod")
    record_event(tmp_vault, "unlock", "dev")
    record_event(tmp_vault, "lock", "dev")
    events = get_events(tmp_vault)
    assert len(events) == 3


def test_filter_by_profile(tmp_vault):
    record_event(tmp_vault, "lock", "prod")
    record_event(tmp_vault, "unlock", "dev")
    events = get_events(tmp_vault, profile="dev")
    assert len(events) == 1
    assert events[0]["profile"] == "dev"


def test_event_has_timestamp(tmp_vault):
    record_event(tmp_vault, "lock", "prod")
    events = get_events(tmp_vault)
    assert "timestamp" in events[0]
    assert events[0]["timestamp"].endswith("+00:00")


def test_event_details(tmp_vault):
    record_event(tmp_vault, "delete", "staging", details="profile removed")
    events = get_events(tmp_vault)
    assert events[0]["details"] == "profile removed"


def test_clear_events(tmp_vault):
    record_event(tmp_vault, "lock", "prod")
    clear_events(tmp_vault)
    assert get_events(tmp_vault) == []


def test_empty_vault_returns_empty(tmp_vault):
    assert get_events(tmp_vault) == []


def test_filter_no_match(tmp_vault):
    record_event(tmp_vault, "lock", "prod")
    assert get_events(tmp_vault, profile="nonexistent") == []
