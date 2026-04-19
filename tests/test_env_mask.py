"""Tests for envault.env_mask."""
import pytest
from envault.env_mask import mask_profile, format_mask_result, MASK_CHAR, MASK_LEN, MaskResult


SAMPLE = {
    "APP_NAME": "myapp",
    "DB_PASSWORD": "s3cr3t",
    "API_KEY": "abc123",
    "DEBUG": "true",
    "AUTH_TOKEN": "tok_xyz",
}


def test_sensitive_keys_are_masked():
    result = mask_profile(SAMPLE)
    assert result.masked["DB_PASSWORD"] == MASK_CHAR * MASK_LEN
    assert result.masked["API_KEY"] == MASK_CHAR * MASK_LEN
    assert result.masked["AUTH_TOKEN"] == MASK_CHAR * MASK_LEN


def test_non_sensitive_keys_are_unchanged():
    result = mask_profile(SAMPLE)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["DEBUG"] == "true"


def test_redacted_keys_listed():
    result = mask_profile(SAMPLE)
    assert "DB_PASSWORD" in result.redacted_keys
    assert "API_KEY" in result.redacted_keys
    assert "APP_NAME" not in result.redacted_keys


def test_reveal_flag_shows_all():
    result = mask_profile(SAMPLE, reveal=True)
    assert result.masked["DB_PASSWORD"] == "s3cr3t"
    assert result.redacted_keys == []


def test_extra_keys_are_masked():
    result = mask_profile(SAMPLE, extra_keys=["APP_NAME"])
    assert result.masked["APP_NAME"] == MASK_CHAR * MASK_LEN
    assert "APP_NAME" in result.redacted_keys


def test_custom_pattern():
    data = {"MY_CUSTOM_SAUCE": "val", "NORMAL": "ok"}
    result = mask_profile(data, patterns=[r"(?i)sauce"])
    assert result.masked["MY_CUSTOM_SAUCE"] == MASK_CHAR * MASK_LEN
    assert result.masked["NORMAL"] == "ok"


def test_original_data_unchanged():
    result = mask_profile(SAMPLE)
    assert result.original["DB_PASSWORD"] == "s3cr3t"


def test_format_output_contains_all_keys():
    result = mask_profile(SAMPLE)
    output = format_mask_result(result)
    for k in SAMPLE:
        assert k in output


def test_empty_profile():
    result = mask_profile({})
    assert result.masked == {}
    assert result.redacted_keys == []


def test_ok_property():
    result = mask_profile(SAMPLE)
    assert result.ok is True
