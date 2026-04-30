"""Tests for envault/env_ref.py"""
from __future__ import annotations

import pytest

from envault.env_ref import (
    RefError,
    RefResult,
    format_ref_result,
    ok,
    resolve_refs,
)


def _loader(data: dict):
    """Return a loader that serves profiles from *data*."""
    def _load(name: str):
        if name not in data:
            raise KeyError(name)
        return data[name]
    return _load


# ---------------------------------------------------------------------------
# resolve_refs — happy path
# ---------------------------------------------------------------------------

def test_resolve_substitutes_value_from_other_profile():
    profile = {"DB_URL": "${ref:base:DB_URL}"}
    loader = _loader({"base": {"DB_URL": "postgres://localhost/db"}})
    result = resolve_refs(profile, loader)
    assert result.resolved["DB_URL"] == "postgres://localhost/db"


def test_resolve_non_ref_values_are_unchanged():
    profile = {"APP": "myapp", "PORT": "8080"}
    loader = _loader({})
    result = resolve_refs(profile, loader)
    assert result.resolved == profile


def test_resolve_records_substitution_metadata():
    profile = {"SECRET": "${ref:prod:SECRET_KEY}"}
    loader = _loader({"prod": {"SECRET_KEY": "s3cr3t"}})
    result = resolve_refs(profile, loader)
    assert len(result.substitutions) == 1
    key, src_prof, src_key, val = result.substitutions[0]
    assert key == "SECRET"
    assert src_prof == "prod"
    assert src_key == "SECRET_KEY"
    assert val == "s3cr3t"


def test_resolve_ok_true_when_all_resolved():
    profile = {"X": "${ref:other:X}"}
    loader = _loader({"other": {"X": "42"}})
    result = resolve_refs(profile, loader)
    assert ok(result) is True


# ---------------------------------------------------------------------------
# resolve_refs — missing profile / key (non-strict)
# ---------------------------------------------------------------------------

def test_resolve_missing_profile_leaves_placeholder():
    profile = {"K": "${ref:ghost:K}"}
    loader = _loader({})
    result = resolve_refs(profile, loader)
    assert result.resolved["K"] == "${ref:ghost:K}"
    assert ("K", "ghost", "K") in result.unresolved


def test_resolve_missing_key_in_profile_leaves_placeholder():
    profile = {"K": "${ref:base:MISSING}"}
    loader = _loader({"base": {"OTHER": "val"}})
    result = resolve_refs(profile, loader)
    assert result.resolved["K"] == "${ref:base:MISSING}"
    assert ("K", "base", "MISSING") in result.unresolved


def test_resolve_ok_false_when_unresolved():
    profile = {"K": "${ref:nowhere:K}"}
    loader = _loader({})
    result = resolve_refs(profile, loader)
    assert ok(result) is False


# ---------------------------------------------------------------------------
# resolve_refs — strict mode
# ---------------------------------------------------------------------------

def test_strict_raises_on_missing_profile():
    profile = {"K": "${ref:ghost:K}"}
    loader = _loader({})
    with pytest.raises(RefError, match="ghost"):
        resolve_refs(profile, loader, strict=True)


def test_strict_raises_on_missing_key():
    profile = {"K": "${ref:base:NOPE}"}
    loader = _loader({"base": {}})
    with pytest.raises(RefError, match="NOPE"):
        resolve_refs(profile, loader, strict=True)


# ---------------------------------------------------------------------------
# format_ref_result
# ---------------------------------------------------------------------------

def test_format_shows_resolved_entry():
    profile = {"DB": "${ref:prod:DB}"}
    loader = _loader({"prod": {"DB": "pg://"}})
    result = resolve_refs(profile, loader)
    output = format_ref_result(result)
    assert "DB" in output
    assert "prod" in output
    assert "pg://" in output


def test_format_shows_unresolved_entry():
    profile = {"X": "${ref:missing:X}"}
    loader = _loader({})
    result = resolve_refs(profile, loader)
    output = format_ref_result(result)
    assert "Unresolved" in output
    assert "missing" in output


def test_format_no_refs_shows_default_message():
    profile = {"A": "1", "B": "2"}
    loader = _loader({})
    result = resolve_refs(profile, loader)
    output = format_ref_result(result)
    assert "No references found" in output
