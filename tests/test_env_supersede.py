"""Tests for envault.env_supersede."""
import pytest

from envault.env_supersede import (
    SupersedeError,
    clear_supersede,
    get_supersede,
    list_superseded,
    mark_superseded,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_mark_superseded_returns_ok(tmp_vault):
    result = mark_superseded(tmp_vault, "staging", "production")
    assert result.ok is True
    assert result.entry.profile == "staging"
    assert result.entry.superseded_by == "production"


def test_mark_superseded_with_reason(tmp_vault):
    result = mark_superseded(tmp_vault, "dev", "staging", reason="promoted")
    assert result.entry.reason == "promoted"


def test_mark_superseded_message_contains_names(tmp_vault):
    result = mark_superseded(tmp_vault, "old", "new")
    assert "old" in result.message
    assert "new" in result.message


def test_mark_self_supersede_raises(tmp_vault):
    with pytest.raises(SupersedeError, match="cannot supersede itself"):
        mark_superseded(tmp_vault, "prod", "prod")


def test_get_supersede_returns_entry(tmp_vault):
    mark_superseded(tmp_vault, "alpha", "beta", reason="upgrade")
    entry = get_supersede(tmp_vault, "alpha")
    assert entry is not None
    assert entry.superseded_by == "beta"
    assert entry.reason == "upgrade"


def test_get_supersede_missing_returns_none(tmp_vault):
    assert get_supersede(tmp_vault, "nonexistent") is None


def test_clear_supersede_removes_entry(tmp_vault):
    mark_superseded(tmp_vault, "v1", "v2")
    clear_supersede(tmp_vault, "v1")
    assert get_supersede(tmp_vault, "v1") is None


def test_clear_supersede_missing_raises(tmp_vault):
    with pytest.raises(SupersedeError):
        clear_supersede(tmp_vault, "ghost")


def test_list_superseded_returns_all(tmp_vault):
    mark_superseded(tmp_vault, "a", "b")
    mark_superseded(tmp_vault, "c", "d", reason="merged")
    entries = list_superseded(tmp_vault)
    profiles = {e.profile for e in entries}
    assert profiles == {"a", "c"}


def test_list_superseded_empty_vault(tmp_vault):
    assert list_superseded(tmp_vault) == []


def test_overwrite_supersede_entry(tmp_vault):
    mark_superseded(tmp_vault, "x", "y")
    mark_superseded(tmp_vault, "x", "z", reason="changed again")
    entry = get_supersede(tmp_vault, "x")
    assert entry.superseded_by == "z"
    assert entry.reason == "changed again"


def test_list_superseded_no_reason_field(tmp_vault):
    mark_superseded(tmp_vault, "p", "q")
    entries = list_superseded(tmp_vault)
    assert entries[0].reason is None
