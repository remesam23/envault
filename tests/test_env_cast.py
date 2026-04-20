"""Tests for envault.env_cast."""
import pytest

from envault.env_cast import (
    CastError,
    CastResult,
    cast_profile,
    format_cast_result,
    _cast_value,
)


# --- _cast_value unit tests ---

def test_cast_int_valid():
    assert _cast_value("42", "int") == 42


def test_cast_int_invalid():
    with pytest.raises(CastError, match="Cannot cast"):
        _cast_value("abc", "int")


def test_cast_float_valid():
    assert _cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_float_invalid():
    with pytest.raises(CastError):
        _cast_value("nope", "float")


@pytest.mark.parametrize("val,expected", [
    ("true", True), ("1", True), ("yes", True), ("on", True),
    ("false", False), ("0", False), ("no", False), ("off", False),
    ("TRUE", True), ("FALSE", False),
])
def test_cast_bool_valid(val, expected):
    assert _cast_value(val, "bool") is expected


def test_cast_bool_invalid():
    with pytest.raises(CastError):
        _cast_value("maybe", "bool")


def test_cast_str_passthrough():
    assert _cast_value("hello", "str") == "hello"


def test_cast_unknown_type_raises():
    with pytest.raises(CastError, match="Unknown type"):
        _cast_value("x", "list")


# --- cast_profile tests ---

def test_cast_profile_basic():
    data = {"PORT": "8080", "DEBUG": "true", "NAME": "myapp"}
    schema = {"PORT": "int", "DEBUG": "bool"}
    result = cast_profile(data, schema, profile="dev")
    assert result.ok
    assert result.casted["PORT"] == 8080
    assert result.casted["DEBUG"] is True
    assert result.casted["NAME"] == "myapp"


def test_cast_profile_skips_unschema_keys():
    data = {"X": "1", "Y": "hello"}
    result = cast_profile(data, {}, profile="p")
    assert "X" in result.skipped
    assert "Y" in result.skipped
    assert result.casted["X"] == "1"


def test_cast_profile_non_strict_keeps_bad_value():
    data = {"PORT": "notanint"}
    result = cast_profile(data, {"PORT": "int"}, strict=False)
    assert result.ok
    assert result.casted["PORT"] == "notanint"
    assert "PORT" in result.skipped


def test_cast_profile_strict_records_error():
    data = {"PORT": "notanint"}
    result = cast_profile(data, {"PORT": "int"}, strict=True)
    assert not result.ok
    assert len(result.errors) == 1


def test_format_cast_result_contains_profile():
    data = {"PORT": "9000"}
    result = cast_profile(data, {"PORT": "int"}, profile="staging")
    text = format_cast_result(result)
    assert "staging" in text
    assert "PORT" in text
    assert "int" in text


def test_format_cast_result_shows_skipped():
    data = {"UNKNOWN": "val"}
    result = cast_profile(data, {}, profile="p")
    text = format_cast_result(result)
    assert "UNKNOWN" in text
