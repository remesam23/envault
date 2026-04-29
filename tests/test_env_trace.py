"""Tests for envault.env_trace."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.env_trace import (
    TraceEntry,
    clear_trace,
    format_trace,
    get_trace,
    record_access,
)


@pytest.fixture
def tmp_vault(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_record_returns_entry(tmp_vault):
    entry = record_access(tmp_vault, "prod", "DB_URL")
    assert isinstance(entry, TraceEntry)
    assert entry.profile == "prod"
    assert entry.key == "DB_URL"
    assert entry.timestamp
    assert entry.context is None


def test_record_with_context(tmp_vault):
    entry = record_access(tmp_vault, "dev", "SECRET_KEY", context="cli-unlock")
    assert entry.context == "cli-unlock"


def test_get_trace_returns_all_entries(tmp_vault):
    record_access(tmp_vault, "prod", "DB_URL")
    record_access(tmp_vault, "dev", "API_KEY")
    entries = get_trace(tmp_vault)
    assert len(entries) == 2


def test_get_trace_filter_by_profile(tmp_vault):
    record_access(tmp_vault, "prod", "DB_URL")
    record_access(tmp_vault, "dev", "API_KEY")
    entries = get_trace(tmp_vault, profile="prod")
    assert len(entries) == 1
    assert entries[0].profile == "prod"


def test_get_trace_filter_by_key(tmp_vault):
    record_access(tmp_vault, "prod", "DB_URL")
    record_access(tmp_vault, "prod", "API_KEY")
    entries = get_trace(tmp_vault, key="DB_URL")
    assert len(entries) == 1
    assert entries[0].key == "DB_URL"


def test_get_trace_filter_by_profile_and_key(tmp_vault):
    record_access(tmp_vault, "prod", "DB_URL")
    record_access(tmp_vault, "dev", "DB_URL")
    entries = get_trace(tmp_vault, profile="dev", key="DB_URL")
    assert len(entries) == 1
    assert entries[0].profile == "dev"


def test_get_trace_empty_vault_returns_empty(tmp_vault):
    assert get_trace(tmp_vault) == []


def test_clear_trace_removes_all(tmp_vault):
    record_access(tmp_vault, "prod", "DB_URL")
    record_access(tmp_vault, "dev", "API_KEY")
    removed = clear_trace(tmp_vault)
    assert removed == 2
    assert get_trace(tmp_vault) == []


def test_clear_trace_by_profile(tmp_vault):
    record_access(tmp_vault, "prod", "DB_URL")
    record_access(tmp_vault, "dev", "API_KEY")
    removed = clear_trace(tmp_vault, profile="prod")
    assert removed == 1
    remaining = get_trace(tmp_vault)
    assert len(remaining) == 1
    assert remaining[0].profile == "dev"


def test_entries_have_iso_timestamps(tmp_vault):
    entry = record_access(tmp_vault, "prod", "KEY")
    # Should be parseable ISO format with timezone info
    from datetime import datetime
    dt = datetime.fromisoformat(entry.timestamp)
    assert dt.tzinfo is not None


def test_format_trace_empty():
    result = format_trace([])
    assert "No trace" in result


def test_format_trace_shows_profile_and_key(tmp_vault):
    record_access(tmp_vault, "prod", "DB_URL", context="test")
    entries = get_trace(tmp_vault)
    output = format_trace(entries)
    assert "prod::DB_URL" in output
    assert "[test]" in output


def test_multiple_records_accumulate(tmp_vault):
    for i in range(5):
        record_access(tmp_vault, "prod", f"KEY_{i}")
    assert len(get_trace(tmp_vault)) == 5
