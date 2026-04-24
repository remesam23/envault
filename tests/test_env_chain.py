"""Tests for envault.env_chain."""
from __future__ import annotations

import pytest

from envault.env_chain import ChainError, resolve_chain, format_chain_result


BASE = {"APP_ENV": "development", "DB_HOST": "localhost", "LOG_LEVEL": "debug"}
OVERRIDE = {"APP_ENV": "staging", "DB_HOST": "db.staging.example.com"}
EXTRA = {"NEW_KEY": "extra_value", "APP_ENV": "production"}

PROFILES = {"base": BASE, "override": OVERRIDE, "extra": EXTRA}


def test_single_profile_returns_its_keys():
    result = resolve_chain({"base": BASE}, ["base"])
    assert result.merged == BASE
    assert result.ok is True


def test_later_profile_overrides_earlier():
    result = resolve_chain(PROFILES, ["base", "override"])
    assert result.merged["APP_ENV"] == "staging"
    assert result.merged["DB_HOST"] == "db.staging.example.com"


def test_earlier_keys_not_in_override_are_kept():
    result = resolve_chain(PROFILES, ["base", "override"])
    assert result.merged["LOG_LEVEL"] == "debug"


def test_three_layer_chain_last_wins():
    result = resolve_chain(PROFILES, ["base", "override", "extra"])
    assert result.merged["APP_ENV"] == "production"
    assert result.merged["NEW_KEY"] == "extra_value"


def test_sources_track_provenance():
    result = resolve_chain(PROFILES, ["base", "override"])
    assert result.sources["APP_ENV"] == "override"
    assert result.sources["LOG_LEVEL"] == "base"


def test_sources_three_layers():
    result = resolve_chain(PROFILES, ["base", "override", "extra"])
    assert result.sources["APP_ENV"] == "extra"
    assert result.sources["DB_HOST"] == "override"
    assert result.sources["LOG_LEVEL"] == "base"


def test_chain_order_preserved_in_result():
    result = resolve_chain(PROFILES, ["base", "override", "extra"])
    assert result.chain == ["base", "override", "extra"]


def test_empty_chain_raises():
    with pytest.raises(ChainError, match="at least one"):
        resolve_chain(PROFILES, [])


def test_missing_profile_raises():
    with pytest.raises(ChainError, match="nonexistent"):
        resolve_chain(PROFILES, ["base", "nonexistent"])


def test_multiple_missing_profiles_listed():
    with pytest.raises(ChainError, match="ghost"):
        resolve_chain(PROFILES, ["ghost", "phantom"])


def test_format_chain_result_contains_chain_header():
    result = resolve_chain(PROFILES, ["base", "override"])
    output = format_chain_result(result)
    assert "base -> override" in output


def test_format_chain_result_contains_source_annotation():
    result = resolve_chain(PROFILES, ["base", "override"])
    output = format_chain_result(result)
    assert "(from: override)" in output or "(from: base)" in output


def test_format_chain_result_shows_total_keys():
    result = resolve_chain(PROFILES, ["base", "override"])
    output = format_chain_result(result)
    assert f"Total keys: {len(result.merged)}" in output
