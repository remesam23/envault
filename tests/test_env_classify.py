"""Tests for envault.env_classify."""
import pytest

from envault.env_classify import (
    ClassifyError,
    ClassifyResult,
    classify_profile,
    format_classify,
)


def test_secret_key_classified_correctly():
    data = {"DB_PASSWORD": "hunter2", "APP_NAME": "myapp"}
    result = classify_profile("dev", data)
    assert "DB_PASSWORD" in result.categories.get("secret", [])


def test_url_key_classified_correctly():
    data = {"DATABASE_URL": "postgres://localhost/db"}
    result = classify_profile("dev", data)
    assert "DATABASE_URL" in result.categories.get("url", [])


def test_port_key_classified_correctly():
    data = {"APP_PORT": "8080"}
    result = classify_profile("dev", data)
    assert "APP_PORT" in result.categories.get("port", [])


def test_path_key_classified_correctly():
    data = {"LOG_PATH": "/var/log/app.log"}
    result = classify_profile("dev", data)
    assert "LOG_PATH" in result.categories.get("path", [])


def test_flag_key_classified_correctly():
    data = {"ENABLE_CACHE": "true"}
    result = classify_profile("dev", data)
    assert "ENABLE_CACHE" in result.categories.get("flag", [])


def test_numeric_key_classified_correctly():
    data = {"MAX_RETRIES": "5"}
    result = classify_profile("dev", data)
    assert "MAX_RETRIES" in result.categories.get("numeric", [])


def test_value_url_fallback():
    data = {"SOME_VAR": "https://example.com/api"}
    result = classify_profile("dev", data)
    assert "SOME_VAR" in result.categories.get("url", [])


def test_value_bool_fallback():
    data = {"SOME_FLAG": "true"}
    result = classify_profile("dev", data)
    assert "SOME_FLAG" in result.categories.get("flag", [])


def test_value_numeric_fallback():
    data = {"SOME_NUM": "42"}
    result = classify_profile("dev", data)
    assert "SOME_NUM" in result.categories.get("numeric", [])


def test_general_fallback():
    data = {"APP_NAME": "myapp"}
    result = classify_profile("dev", data)
    assert "APP_NAME" in result.categories.get("general", [])


def test_empty_profile_returns_empty_categories():
    result = classify_profile("dev", {})
    assert result.categories == {}


def test_invalid_data_raises():
    with pytest.raises(ClassifyError):
        classify_profile("dev", "not-a-dict")  # type: ignore


def test_result_profile_name():
    result = classify_profile("staging", {"KEY": "val"})
    assert result.profile == "staging"


def test_categories_are_sorted():
    data = {"Z_TOKEN": "abc", "A_TOKEN": "xyz"}
    result = classify_profile("dev", data)
    keys = result.categories.get("secret", [])
    assert keys == sorted(keys)


def test_format_classify_contains_profile():
    result = classify_profile("prod", {"DB_PASSWORD": "s3cr3t"})
    output = format_classify(result)
    assert "prod" in output


def test_format_classify_contains_category():
    result = classify_profile("prod", {"DB_PASSWORD": "s3cr3t"})
    output = format_classify(result)
    assert "[secret]" in output
    assert "DB_PASSWORD" in output


def test_format_classify_empty_profile():
    result = classify_profile("dev", {})
    output = format_classify(result)
    assert "(no keys)" in output
