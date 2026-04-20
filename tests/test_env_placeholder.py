"""Tests for envault.env_placeholder."""
from __future__ import annotations

import pytest

from envault.env_placeholder import (
    PlaceholderError,
    find_placeholders,
    format_resolution,
    resolve_profile,
)


def test_find_placeholders_simple():
    assert find_placeholders("${HOST}:${PORT}") == ["HOST", "PORT"]


def test_find_placeholders_none():
    assert find_placeholders("plain_value") == []


def test_find_placeholders_repeated():
    result = find_placeholders("${A}/${A}")
    assert result == ["A", "A"]


def test_resolve_substitutes_within_profile():
    profile = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = resolve_profile(profile)
    assert result.resolved["URL"] == "http://localhost/api"
    assert result.ok


def test_resolve_unresolved_left_as_is():
    profile = {"URL": "http://${MISSING}/api"}
    result = resolve_profile(profile)
    assert "${MISSING}" in result.resolved["URL"]
    assert "MISSING" in result.unresolved
    assert not result.ok


def test_resolve_strict_raises_on_missing():
    profile = {"URL": "http://${MISSING}/api"}
    with pytest.raises(PlaceholderError, match="MISSING"):
        resolve_profile(profile, strict=True)


def test_resolve_uses_extra_mapping():
    profile = {"URL": "http://${HOST}/api"}
    result = resolve_profile(profile, extra={"HOST": "example.com"})
    assert result.resolved["URL"] == "http://example.com/api"
    assert result.ok


def test_resolve_profile_key_overrides_extra():
    """Profile values take precedence over extra."""
    profile = {"HOST": "internal", "URL": "http://${HOST}"}
    result = resolve_profile(profile, extra={"HOST": "external"})
    assert result.resolved["URL"] == "http://internal"


def test_resolve_no_placeholders_unchanged():
    profile = {"KEY": "value", "OTHER": "123"}
    result = resolve_profile(profile)
    assert result.resolved == profile
    assert result.substitutions == 0


def test_resolve_deduplicates_unresolved():
    profile = {"A": "${X}/${X}"}
    result = resolve_profile(profile)
    assert result.unresolved.count("X") == 1


def test_format_resolution_ok():
    profile = {"HOST": "localhost", "URL": "http://${HOST}"}
    result = resolve_profile(profile)
    text = format_resolution(result)
    assert "All placeholders resolved" in text


def test_format_resolution_unresolved():
    profile = {"URL": "http://${MISSING}"}
    result = resolve_profile(profile)
    text = format_resolution(result)
    assert "MISSING" in text
    assert "Unresolved" in text
