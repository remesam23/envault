"""Tests for envault.env_redact."""
import pytest

from envault.env_redact import (
    REDACTED_PLACEHOLDER,
    RedactError,
    RedactResult,
    format_redact_result,
    ok,
    redact_profile,
)


DEFAULT_DATA = {
    "API_KEY": "secret123",
    "DB_PASSWORD": "hunter2",
    "APP_ENV": "production",
    "PORT": "8080",
}


def test_redact_replaces_value_with_placeholder():
    result = redact_profile(DEFAULT_DATA, ["API_KEY"])
    assert result.redacted["API_KEY"] == REDACTED_PLACEHOLDER


def test_redact_keeps_non_targeted_keys_unchanged():
    result = redact_profile(DEFAULT_DATA, ["API_KEY"])
    assert result.redacted["APP_ENV"] == "production"
    assert result.redacted["PORT"] == "8080"


def test_redact_multiple_keys():
    result = redact_profile(DEFAULT_DATA, ["API_KEY", "DB_PASSWORD"])
    assert result.redacted["API_KEY"] == REDACTED_PLACEHOLDER
    assert result.redacted["DB_PASSWORD"] == REDACTED_PLACEHOLDER
    assert len(result.keys_redacted) == 2


def test_redact_keys_redacted_list_sorted():
    result = redact_profile(DEFAULT_DATA, ["PORT", "API_KEY"])
    assert result.keys_redacted == sorted(["PORT", "API_KEY"])


def test_redact_keys_kept_list_sorted():
    result = redact_profile(DEFAULT_DATA, ["API_KEY"])
    expected_kept = sorted([k for k in DEFAULT_DATA if k != "API_KEY"])
    assert result.keys_kept == expected_kept


def test_redact_custom_placeholder():
    result = redact_profile(DEFAULT_DATA, ["API_KEY"], placeholder="<hidden>")
    assert result.redacted["API_KEY"] == "<hidden>"


def test_redact_remove_drops_key():
    result = redact_profile(DEFAULT_DATA, ["API_KEY"], remove=True)
    assert "API_KEY" not in result.redacted
    assert "API_KEY" in result.keys_redacted


def test_redact_remove_keeps_other_keys():
    result = redact_profile(DEFAULT_DATA, ["API_KEY"], remove=True)
    assert "APP_ENV" in result.redacted


def test_redact_empty_keys_list_changes_nothing():
    result = redact_profile(DEFAULT_DATA, [])
    assert result.redacted == DEFAULT_DATA
    assert result.keys_redacted == []


def test_redact_nonexistent_key_is_ignored():
    result = redact_profile(DEFAULT_DATA, ["DOES_NOT_EXIST"])
    assert result.redacted == DEFAULT_DATA
    assert result.keys_redacted == []


def test_redact_invalid_data_raises():
    with pytest.raises(RedactError):
        redact_profile("not-a-dict", ["KEY"])  # type: ignore


def test_ok_returns_true_on_success():
    result = redact_profile(DEFAULT_DATA, ["API_KEY"])
    assert ok(result) is True


def test_format_shows_redacted_keys():
    result = redact_profile(DEFAULT_DATA, ["API_KEY"])
    output = format_redact_result(result)
    assert "API_KEY" in output
    assert REDACTED_PLACEHOLDER in output


def test_format_no_keys_redacted_message():
    result = redact_profile(DEFAULT_DATA, [])
    output = format_redact_result(result)
    assert "No keys redacted" in output
