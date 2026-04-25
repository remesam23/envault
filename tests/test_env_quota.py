"""Tests for envault.env_quota."""
import pytest
from pathlib import Path

from envault.env_quota import (
    QuotaConfig,
    QuotaError,
    set_quota,
    get_quota,
    clear_quota,
    check_quota,
    format_quota_result,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return tmp_path


def test_set_and_get_quota(tmp_vault):
    config = QuotaConfig(max_keys=10, max_value_bytes=256)
    set_quota(tmp_vault, "prod", config)
    result = get_quota(tmp_vault, "prod")
    assert result is not None
    assert result.max_keys == 10
    assert result.max_value_bytes == 256


def test_get_quota_missing_profile_returns_none(tmp_vault):
    assert get_quota(tmp_vault, "ghost") is None


def test_clear_quota_removes_entry(tmp_vault):
    set_quota(tmp_vault, "staging", QuotaConfig(max_keys=5))
    clear_quota(tmp_vault, "staging")
    assert get_quota(tmp_vault, "staging") is None


def test_clear_quota_missing_raises(tmp_vault):
    with pytest.raises(QuotaError, match="No quota set"):
        clear_quota(tmp_vault, "nonexistent")


def test_check_quota_no_config_passes(tmp_vault):
    env = {"KEY": "value"}
    result = check_quota(tmp_vault, "dev", env)
    assert result.passed
    assert result.violations == []


def test_check_quota_within_limits_passes(tmp_vault):
    set_quota(tmp_vault, "dev", QuotaConfig(max_keys=5, max_value_bytes=100))
    env = {"A": "hello", "B": "world"}
    result = check_quota(tmp_vault, "dev", env)
    assert result.passed


def test_check_quota_exceeds_max_keys_fails(tmp_vault):
    set_quota(tmp_vault, "prod", QuotaConfig(max_keys=2))
    env = {"A": "1", "B": "2", "C": "3"}
    result = check_quota(tmp_vault, "prod", env)
    assert not result.passed
    assert any(v.key == "__profile__" for v in result.violations)


def test_check_quota_exceeds_value_bytes_fails(tmp_vault):
    set_quota(tmp_vault, "prod", QuotaConfig(max_value_bytes=4))
    env = {"KEY": "toolongvalue"}
    result = check_quota(tmp_vault, "prod", env)
    assert not result.passed
    assert any(v.key == "KEY" for v in result.violations)


def test_check_quota_multiple_violations(tmp_vault):
    set_quota(tmp_vault, "prod", QuotaConfig(max_value_bytes=3))
    env = {"A": "toolong", "B": "alsotoolong"}
    result = check_quota(tmp_vault, "prod", env)
    assert not result.passed
    assert len(result.violations) == 2


def test_format_quota_result_ok(tmp_vault):
    set_quota(tmp_vault, "dev", QuotaConfig(max_keys=10))
    env = {"X": "1"}
    result = check_quota(tmp_vault, "dev", env)
    output = format_quota_result(result, "dev")
    assert "OK" in output
    assert "dev" in output


def test_format_quota_result_fail(tmp_vault):
    set_quota(tmp_vault, "dev", QuotaConfig(max_keys=1))
    env = {"A": "1", "B": "2"}
    result = check_quota(tmp_vault, "dev", env)
    output = format_quota_result(result, "dev")
    assert "FAIL" in output
    assert "__profile__" in output


def test_overwrite_quota_updates_values(tmp_vault):
    set_quota(tmp_vault, "prod", QuotaConfig(max_keys=5))
    set_quota(tmp_vault, "prod", QuotaConfig(max_keys=20, max_value_bytes=512))
    config = get_quota(tmp_vault, "prod")
    assert config.max_keys == 20
    assert config.max_value_bytes == 512
