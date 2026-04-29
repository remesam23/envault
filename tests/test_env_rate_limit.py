"""Tests for envault.env_rate_limit."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.env_rate_limit import (
    RateLimitConfig,
    RateLimitError,
    check_and_record,
    clear_rate_limit,
    get_rate_limit,
    set_rate_limit,
)


@pytest.fixture
def tmp_vault(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_set_and_get_rate_limit(tmp_vault):
    cfg = set_rate_limit(tmp_vault, "prod", max_accesses=10, window_seconds=60)
    assert isinstance(cfg, RateLimitConfig)
    assert cfg.max_accesses == 10
    assert cfg.window_seconds == 60
    fetched = get_rate_limit(tmp_vault, "prod")
    assert fetched is not None
    assert fetched.max_accesses == 10
    assert fetched.window_seconds == 60


def test_get_rate_limit_missing_profile_returns_none(tmp_vault):
    result = get_rate_limit(tmp_vault, "nonexistent")
    assert result is None


def test_set_invalid_max_accesses_raises(tmp_vault):
    with pytest.raises(RateLimitError, match="max_accesses"):
        set_rate_limit(tmp_vault, "prod", max_accesses=0, window_seconds=60)


def test_set_invalid_window_raises(tmp_vault):
    with pytest.raises(RateLimitError, match="window_seconds"):
        set_rate_limit(tmp_vault, "prod", max_accesses=5, window_seconds=0)


def test_clear_rate_limit_removes_entry(tmp_vault):
    set_rate_limit(tmp_vault, "staging", max_accesses=5, window_seconds=30)
    clear_rate_limit(tmp_vault, "staging")
    assert get_rate_limit(tmp_vault, "staging") is None


def test_clear_missing_profile_raises(tmp_vault):
    with pytest.raises(RateLimitError, match="No rate limit configured"):
        clear_rate_limit(tmp_vault, "ghost")


def test_check_and_record_no_config_always_allowed(tmp_vault):
    result = check_and_record(tmp_vault, "unconfigured")
    assert result.allowed is True
    assert "No rate limit" in result.message


def test_check_and_record_within_limit_allowed(tmp_vault):
    set_rate_limit(tmp_vault, "dev", max_accesses=3, window_seconds=60)
    for _ in range(3):
        result = check_and_record(tmp_vault, "dev")
    assert result.allowed is True
    assert result.accesses_in_window == 3


def test_check_and_record_exceeds_limit_denied(tmp_vault):
    set_rate_limit(tmp_vault, "dev", max_accesses=2, window_seconds=60)
    check_and_record(tmp_vault, "dev")
    check_and_record(tmp_vault, "dev")
    result = check_and_record(tmp_vault, "dev")  # 3rd access
    assert result.allowed is False
    assert "exceeded" in result.message
    assert result.accesses_in_window == 3
    assert result.limit == 2


def test_check_and_record_profiles_are_isolated(tmp_vault):
    set_rate_limit(tmp_vault, "a", max_accesses=1, window_seconds=60)
    set_rate_limit(tmp_vault, "b", max_accesses=1, window_seconds=60)
    check_and_record(tmp_vault, "a")
    result_a = check_and_record(tmp_vault, "a")
    result_b = check_and_record(tmp_vault, "b")
    assert result_a.allowed is False
    assert result_b.allowed is True


def test_result_message_contains_counts(tmp_vault):
    set_rate_limit(tmp_vault, "prod", max_accesses=5, window_seconds=60)
    result = check_and_record(tmp_vault, "prod")
    assert "1/5" in result.message
