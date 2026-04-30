"""Tests for envault.env_resolve."""
from __future__ import annotations

import pytest

from envault.env_resolve import (
    ResolveError,
    ResolveResult,
    resolve_profile,
    format_resolve_result,
    ok,
)


# ---------------------------------------------------------------------------
# resolve_profile
# ---------------------------------------------------------------------------

def test_no_placeholders_returns_unchanged():
    profile = {"HOST": "localhost", "PORT": "5432"}
    result = resolve_profile(profile)
    assert result.resolved == profile
    assert result.substitutions == {}
    assert result.unresolved == {}
    assert result.ok is True


def test_self_reference_substituted():
    profile = {"BASE": "http://example.com", "URL": "${BASE}/api"}
    result = resolve_profile(profile)
    assert result.resolved["URL"] == "http://example.com/api"
    assert "URL" in result.substitutions


def test_defaults_used_as_fallback():
    profile = {"URL": "${BASE}/api"}
    defaults = {"BASE": "http://fallback.com"}
    result = resolve_profile(profile, defaults=defaults)
    assert result.resolved["URL"] == "http://fallback.com/api"
    assert result.ok is True


def test_profile_overrides_defaults():
    profile = {"BASE": "http://profile.com", "URL": "${BASE}/v1"}
    defaults = {"BASE": "http://default.com"}
    result = resolve_profile(profile, defaults=defaults)
    assert result.resolved["URL"] == "http://profile.com/v1"


def test_missing_ref_reported_in_unresolved():
    profile = {"URL": "${MISSING}/path"}
    result = resolve_profile(profile)
    assert "URL" in result.unresolved
    assert "MISSING" in result.unresolved["URL"]
    assert result.ok is False


def test_partial_resolution_leaves_unresolved_placeholder():
    profile = {"BASE": "http://x.com", "URL": "${BASE}/${MISSING}"}
    result = resolve_profile(profile)
    assert "BASE" in result.resolved["URL"]
    assert "${MISSING}" in result.resolved["URL"]
    assert "URL" in result.unresolved


def test_strict_mode_raises_on_missing_ref():
    profile = {"URL": "${GHOST}/path"}
    with pytest.raises(ResolveError, match="GHOST"):
        resolve_profile(profile, strict=True)


def test_strict_mode_passes_when_all_resolved():
    profile = {"A": "hello", "B": "${A} world"}
    result = resolve_profile(profile, strict=True)
    assert result.resolved["B"] == "hello world"


def test_multiple_refs_in_one_value():
    profile = {"SCHEME": "https", "HOST": "example.com", "URL": "${SCHEME}://${HOST}"}
    result = resolve_profile(profile)
    assert result.resolved["URL"] == "https://example.com"
    assert len(result.substitutions["URL"]) == 2


def test_ok_helper_returns_true_when_no_unresolved():
    profile = {"KEY": "value"}
    result = resolve_profile(profile)
    assert ok(result) is True


# ---------------------------------------------------------------------------
# format_resolve_result
# ---------------------------------------------------------------------------

def test_format_shows_substitutions():
    profile = {"BASE": "http://x.com", "URL": "${BASE}/api"}
    result = resolve_profile(profile)
    text = format_resolve_result(result)
    assert "Substitutions" in text
    assert "URL" in text


def test_format_shows_unresolved():
    profile = {"URL": "${GHOST}"}
    result = resolve_profile(profile)
    text = format_resolve_result(result)
    assert "Unresolved" in text
    assert "GHOST" in text


def test_format_no_placeholders_shows_all_resolved_message():
    profile = {"KEY": "value"}
    result = resolve_profile(profile)
    text = format_resolve_result(result)
    assert "no placeholders" in text.lower()
