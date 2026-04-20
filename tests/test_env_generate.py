"""Tests for envault.env_generate."""

import pytest
from envault.env_generate import (
    generate_for_profile,
    format_generate_result,
    as_dict,
    GenerateError,
    CHARSETS,
)


def test_generates_value_for_new_key():
    profile = {}
    result = generate_for_profile(profile, ["SECRET_KEY"])
    assert len(result.generated) == 1
    assert result.generated[0].key == "SECRET_KEY"
    assert len(result.generated[0].value) == 32


def test_generated_value_stored_in_profile():
    profile = {}
    generate_for_profile(profile, ["API_TOKEN"])
    assert "API_TOKEN" in profile
    assert len(profile["API_TOKEN"]) == 32


def test_skips_existing_key_without_overwrite():
    profile = {"DB_PASS": "original"}
    result = generate_for_profile(profile, ["DB_PASS"])
    assert result.skipped == ["DB_PASS"]
    assert profile["DB_PASS"] == "original"


def test_overwrite_flag_replaces_existing():
    profile = {"DB_PASS": "original"}
    result = generate_for_profile(profile, ["DB_PASS"], overwrite=True)
    assert len(result.generated) == 1
    assert profile["DB_PASS"] != "original"


def test_custom_length():
    profile = {}
    result = generate_for_profile(profile, ["TOKEN"], length=64)
    assert len(result.generated[0].value) == 64


def test_hex_charset_only_hex_chars():
    profile = {}
    result = generate_for_profile(profile, ["HEX_VAL"], length=40, charset="hex")
    val = result.generated[0].value
    assert all(c in "0123456789abcdef" for c in val)


def test_numeric_charset():
    profile = {}
    result = generate_for_profile(profile, ["OTP"], length=6, charset="numeric")
    assert result.generated[0].value.isdigit()


def test_invalid_charset_raises():
    with pytest.raises(GenerateError, match="Unknown charset"):
        generate_for_profile({}, ["KEY"], charset="emoji")


def test_invalid_length_raises():
    with pytest.raises(GenerateError, match="Length"):
        generate_for_profile({}, ["KEY"], length=0)


def test_invalid_key_name_raises():
    with pytest.raises(GenerateError, match="valid env var"):
        generate_for_profile({}, ["bad-key"])


def test_multiple_keys_generated():
    profile = {}
    result = generate_for_profile(profile, ["KEY_A", "KEY_B", "KEY_C"])
    assert len(result.generated) == 3
    assert len(result.skipped) == 0


def test_as_dict_returns_key_value_map():
    profile = {}
    result = generate_for_profile(profile, ["SECRET"])
    d = as_dict(result)
    assert "SECRET" in d
    assert d["SECRET"] == profile["SECRET"]


def test_format_masks_values_by_default():
    profile = {}
    result = generate_for_profile(profile, ["HIDDEN"])
    output = format_generate_result(result, reveal=False)
    assert "HIDDEN" in output
    assert "*" in output


def test_format_reveals_values_when_flag_set():
    profile = {}
    result = generate_for_profile(profile, ["VISIBLE"])
    output = format_generate_result(result, reveal=True)
    assert result.generated[0].value in output


def test_format_shows_skipped():
    profile = {"EXISTING": "val"}
    result = generate_for_profile(profile, ["EXISTING"])
    output = format_generate_result(result)
    assert "skipped" in output
    assert "EXISTING" in output
