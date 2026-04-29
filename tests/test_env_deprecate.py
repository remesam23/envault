"""Tests for envault.env_deprecate."""
import pytest
from pathlib import Path

from envault.env_deprecate import (
    mark_deprecated,
    get_deprecated,
    unmark_deprecated,
    is_deprecated,
    format_deprecate_result,
    DeprecateError,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return tmp_path


def test_mark_returns_result(tmp_vault):
    result = mark_deprecated(tmp_vault, "prod", ["OLD_KEY"])
    assert result.profile == "prod"
    assert len(result.deprecated) == 1
    assert result.deprecated[0].key == "OLD_KEY"


def test_mark_stores_reason_and_replacement(tmp_vault):
    mark_deprecated(tmp_vault, "prod", ["DB_URL"], reason="Use DSN instead", replacement="DB_DSN")
    entries = get_deprecated(tmp_vault, "prod")
    assert "DB_URL" in entries
    assert entries["DB_URL"].reason == "Use DSN instead"
    assert entries["DB_URL"].replacement == "DB_DSN"


def test_get_deprecated_missing_profile_returns_empty(tmp_vault):
    result = get_deprecated(tmp_vault, "nonexistent")
    assert result == {}


def test_mark_multiple_keys(tmp_vault):
    mark_deprecated(tmp_vault, "staging", ["KEY_A", "KEY_B", "KEY_C"])
    entries = get_deprecated(tmp_vault, "staging")
    assert set(entries.keys()) == {"KEY_A", "KEY_B", "KEY_C"}


def test_is_deprecated_returns_true_after_mark(tmp_vault):
    mark_deprecated(tmp_vault, "dev", ["LEGACY"])
    assert is_deprecated(tmp_vault, "dev", "LEGACY") is True


def test_is_deprecated_returns_false_for_unknown_key(tmp_vault):
    assert is_deprecated(tmp_vault, "dev", "UNKNOWN") is False


def test_unmark_removes_key(tmp_vault):
    mark_deprecated(tmp_vault, "prod", ["OLD"])
    unmark_deprecated(tmp_vault, "prod", "OLD")
    assert is_deprecated(tmp_vault, "prod", "OLD") is False


def test_unmark_not_marked_raises(tmp_vault):
    with pytest.raises(DeprecateError, match="not marked as deprecated"):
        unmark_deprecated(tmp_vault, "prod", "MISSING_KEY")


def test_mark_persists_across_calls(tmp_vault):
    mark_deprecated(tmp_vault, "prod", ["KEY_1"])
    mark_deprecated(tmp_vault, "prod", ["KEY_2"])
    entries = get_deprecated(tmp_vault, "prod")
    assert "KEY_1" in entries
    assert "KEY_2" in entries


def test_deprecations_isolated_per_profile(tmp_vault):
    mark_deprecated(tmp_vault, "prod", ["KEY_X"])
    assert is_deprecated(tmp_vault, "staging", "KEY_X") is False


def test_format_result_includes_key_and_reason(tmp_vault):
    result = mark_deprecated(tmp_vault, "prod", ["OLD_API"], reason="Deprecated API", replacement="NEW_API")
    output = format_deprecate_result(result)
    assert "OLD_API" in output
    assert "Deprecated API" in output
    assert "NEW_API" in output


def test_format_result_no_reason_no_replacement(tmp_vault):
    result = mark_deprecated(tmp_vault, "prod", ["BARE_KEY"])
    output = format_deprecate_result(result)
    assert "BARE_KEY" in output
    assert "[DEPRECATED]" in output
