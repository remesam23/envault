import pytest
from envault.schema import FieldSpec, ValidationIssue, validate_profile, format_validation


SCHEMA = {
    "DATABASE_URL": FieldSpec(required=True, pattern=r"postgres://.+"),
    "ENV": FieldSpec(required=True, allowed=["dev", "staging", "prod"]),
    "PORT": FieldSpec(required=False, pattern=r"\d+"),
}


def test_valid_profile_passes():
    env = {"DATABASE_URL": "postgres://localhost/db", "ENV": "dev", "PORT": "5432"}
    result = validate_profile(env, SCHEMA)
    assert result.ok
    assert result.issues == []


def test_missing_required_key():
    env = {"ENV": "dev"}
    result = validate_profile(env, SCHEMA)
    assert not result.ok
    keys = [i.key for i in result.issues]
    assert "DATABASE_URL" in keys


def test_pattern_mismatch():
    env = {"DATABASE_URL": "mysql://localhost/db", "ENV": "dev"}
    result = validate_profile(env, SCHEMA)
    assert not result.ok
    assert any(i.key == "DATABASE_URL" for i in result.issues)


def test_allowed_values_violation():
    env = {"DATABASE_URL": "postgres://localhost/db", "ENV": "production"}
    result = validate_profile(env, SCHEMA)
    assert not result.ok
    assert any(i.key == "ENV" for i in result.issues)


def test_optional_key_missing_is_ok():
    env = {"DATABASE_URL": "postgres://localhost/db", "ENV": "prod"}
    result = validate_profile(env, SCHEMA)
    assert result.ok


def test_optional_key_with_bad_pattern():
    env = {"DATABASE_URL": "postgres://localhost/db", "ENV": "dev", "PORT": "abc"}
    result = validate_profile(env, SCHEMA)
    assert not result.ok
    assert any(i.key == "PORT" for i in result.issues)


def test_format_validation_pass():
    env = {"DATABASE_URL": "postgres://localhost/db", "ENV": "dev"}
    result = validate_profile(env, SCHEMA)
    out = format_validation(result)
    assert "passed" in out.lower()


def test_format_validation_fail():
    env = {}
    result = validate_profile(env, SCHEMA)
    out = format_validation(result)
    assert "FAILED" in out
    assert "DATABASE_URL" in out
