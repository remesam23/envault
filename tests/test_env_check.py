import pytest
from envault.env_check import check_env, format_check, EnvCheckResult


PROFILE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
REFERENCE = {"HOST": "localhost", "PORT": "5432", "SECRET": "abc"}


def test_missing_in_profile():
    result = check_env(PROFILE, REFERENCE)
    assert "SECRET" in result.missing_in_profile


def test_extra_in_profile():
    result = check_env(PROFILE, REFERENCE)
    assert "DEBUG" in result.extra_in_profile


def test_common_keys():
    result = check_env(PROFILE, REFERENCE)
    assert "HOST" in result.common
    assert "PORT" in result.common


def test_ok_when_identical():
    data = {"A": "1", "B": "2"}
    result = check_env(data, data.copy())
    assert result.ok


def test_not_ok_when_mismatch():
    result = check_env(PROFILE, REFERENCE)
    assert not result.ok


def test_empty_profile_all_missing():
    result = check_env({}, REFERENCE)
    assert set(result.missing_in_profile) == set(REFERENCE.keys())
    assert result.extra_in_profile == []


def test_empty_reference_all_extra():
    result = check_env(PROFILE, {})
    assert set(result.extra_in_profile) == set(PROFILE.keys())
    assert result.missing_in_profile == []


def test_format_ok():
    data = {"X": "1"}
    result = check_env(data, data.copy())
    output = format_check(result)
    assert "✓" in output


def test_format_shows_missing():
    result = check_env(PROFILE, REFERENCE)
    output = format_check(result)
    assert "SECRET" in output


def test_format_shows_extra():
    result = check_env(PROFILE, REFERENCE)
    output = format_check(result)
    assert "DEBUG" in output
