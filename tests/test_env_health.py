"""Tests for envault.env_health."""
import pytest
from envault.env_health import check_health, format_health, HealthIssue


def _data(**kwargs):
    return dict(kwargs)


def test_empty_profile_returns_h001():
    result = check_health("dev", {})
    codes = [i.code for i in result.issues]
    assert "H001" in codes


def test_empty_profile_total_keys_is_zero():
    result = check_health("dev", {})
    assert result.total_keys == 0


def test_empty_value_returns_h002():
    result = check_health("dev", {"DB_HOST": ""})
    codes = [i.code for i in result.issues]
    assert "H002" in codes


def test_blank_value_returns_h002():
    result = check_health("dev", {"DB_HOST": "   "})
    codes = [i.code for i in result.issues]
    assert "H002" in codes


def test_lowercase_key_returns_h003():
    result = check_health("dev", {"db_host": "localhost"})
    codes = [i.code for i in result.issues]
    assert "H003" in codes


def test_uppercase_key_no_h003():
    result = check_health("dev", {"DB_HOST": "localhost"})
    codes = [i.code for i in result.issues]
    assert "H003" not in codes


def test_duplicate_values_returns_h004():
    result = check_health("dev", {"KEY_A": "same", "KEY_B": "same"})
    codes = [i.code for i in result.issues]
    assert "H004" in codes


def test_unique_values_no_h004():
    result = check_health("dev", {"KEY_A": "val1", "KEY_B": "val2"})
    codes = [i.code for i in result.issues]
    assert "H004" not in codes


def test_clean_profile_is_healthy():
    result = check_health("prod", {"DB_HOST": "localhost", "API_KEY": "secret"})
    assert result.healthy is True


def test_error_severity_marks_unhealthy():
    result = check_health("dev", {"DB_HOST": "localhost"})
    result.issues.append(HealthIssue("X001", "Synthetic error", "error"))
    assert result.healthy is False


def test_score_is_100_for_clean_profile():
    result = check_health("prod", {"DB_HOST": "localhost", "API_KEY": "abc"})
    assert result.score == 100


def test_score_decreases_with_warnings():
    result = check_health("dev", {"DB_HOST": ""})
    assert result.score < 100


def test_format_health_contains_profile_name():
    result = check_health("staging", {"KEY": "val"})
    output = format_health(result)
    assert "staging" in output


def test_format_health_shows_no_issues_when_clean():
    result = check_health("prod", {"KEY": "val"})
    output = format_health(result)
    assert "No issues found" in output


def test_format_health_shows_issue_code():
    result = check_health("dev", {"bad_key": "val"})
    output = format_health(result)
    assert "H003" in output
