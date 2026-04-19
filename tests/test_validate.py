import pytest
from envault.validate import validate_profile, format_validation


PROFILE = "dev"


def test_valid_profile_passes():
    data = {"APP_KEY": "secret", "DB_URL": "postgres://localhost/db"}
    result = validate_profile(PROFILE, data)
    assert result.ok
    assert result.errors == []


def test_missing_required_key():
    data = {"APP_KEY": "secret"}
    result = validate_profile(PROFILE, data, required_keys=["APP_KEY", "DB_URL"])
    assert not result.ok
    keys = [e.key for e in result.errors]
    assert "DB_URL" in keys


def test_all_required_keys_present():
    data = {"A": "1", "B": "2"}
    result = validate_profile(PROFILE, data, required_keys=["A", "B"])
    assert result.ok


def test_key_pattern_mismatch():
    data = {"VALID_KEY": "val", "invalid-key": "val"}
    result = validate_profile(PROFILE, data, key_pattern=r"[A-Z][A-Z0-9_]*")
    assert not result.ok
    keys = [e.key for e in result.errors]
    assert "invalid-key" in keys
    assert "VALID_KEY" not in keys


def test_key_pattern_all_match():
    data = {"FOO": "bar", "BAZ_QUX": "val"}
    result = validate_profile(PROFILE, data, key_pattern=r"[A-Z][A-Z0-9_]*")
    assert result.ok


def test_value_min_length_violation():
    data = {"SECRET": "x"}
    result = validate_profile(PROFILE, data, value_min_length=8)
    assert not result.ok
    assert result.errors[0].key == "SECRET"


def test_value_min_length_passes():
    data = {"SECRET": "longenoughvalue"}
    result = validate_profile(PROFILE, data, value_min_length=8)
    assert result.ok


def test_format_ok():
    data = {"KEY": "value"}
    result = validate_profile(PROFILE, data)
    out = format_validation(result)
    assert "OK" in out
    assert PROFILE in out


def test_format_errors():
    data = {"KEY": "v"}
    result = validate_profile(PROFILE, data, required_keys=["MISSING"], value_min_length=5)
    out = format_validation(result)
    assert "error" in out
    assert "MISSING" in out
    assert "KEY" in out
