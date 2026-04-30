"""Tests for envault/env_format.py."""
import pytest

from envault.env_format import (
    FormatError,
    FormatResult,
    format_profile,
    format_format_result,
    list_formatters,
)


SAMPLE = {
    "APP_NAME": "hello world",
    "DB_URL": "  postgres://localhost  ",
    "SECRET": "abc123",
}


def test_list_formatters_returns_sorted_names():
    names = list_formatters()
    assert "upper" in names
    assert "lower" in names
    assert names == sorted(names)


def test_format_upper_all_keys():
    result = format_profile(SAMPLE, "upper")
    assert result.updated["APP_NAME"] == "HELLO WORLD"
    assert result.updated["DB_URL"] == "  POSTGRES://LOCALHOST  "
    assert result.updated["SECRET"] == "ABC123"
    assert result.ok


def test_format_lower_specific_keys():
    data = {"KEY_A": "HELLO", "KEY_B": "WORLD"}
    result = format_profile(data, "lower", keys=["KEY_A"])
    assert result.updated["KEY_A"] == "hello"
    assert "KEY_B" not in result.updated


def test_format_strip_removes_whitespace():
    result = format_profile(SAMPLE, "strip", keys=["DB_URL"])
    assert result.updated["DB_URL"] == "postgres://localhost"


def test_format_skips_missing_keys():
    result = format_profile(SAMPLE, "upper", keys=["MISSING_KEY"])
    assert "MISSING_KEY" in result.skipped
    assert result.updated == {}


def test_format_unknown_formatter_raises():
    with pytest.raises(FormatError, match="Unknown formatter"):
        format_profile(SAMPLE, "nonexistent")


def test_format_quote_wraps_value():
    data = {"VAR": "value"}
    result = format_profile(data, "quote")
    assert result.updated["VAR"] == '"value"'


def test_format_reverse_reverses_value():
    data = {"K": "abcde"}
    result = format_profile(data, "reverse")
    assert result.updated["K"] == "edcba"


def test_format_base64_encodes_value():
    import base64
    data = {"K": "hello"}
    result = format_profile(data, "base64")
    assert result.updated["K"] == base64.b64encode(b"hello").decode()


def test_format_result_ok_when_no_errors():
    result = FormatResult(updated={"A": "x"}, skipped=[], errors=[])
    assert result.ok


def test_format_result_not_ok_when_errors():
    result = FormatResult(updated={}, skipped=[], errors=["A: boom"])
    assert not result.ok


def test_format_format_result_output_contains_formatter_name():
    result = FormatResult(updated={"A": "X"}, skipped=["B"], errors=[])
    output = format_format_result(result, "upper")
    assert "upper" in output
    assert "A" in output
    assert "B" in output
