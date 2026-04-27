"""Tests for envault/env_visibility.py"""
import pytest
from envault.env_visibility import (
    hide_keys,
    show_keys,
    get_hidden_keys,
    filter_visible,
    clear_hidden,
    VisibilityError,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_hide_keys_returns_hidden_list(tmp_vault):
    result = hide_keys(tmp_vault, "prod", ["SECRET", "TOKEN"])
    assert "SECRET" in result
    assert "TOKEN" in result


def test_hide_keys_deduplicates(tmp_vault):
    hide_keys(tmp_vault, "prod", ["SECRET"])
    result = hide_keys(tmp_vault, "prod", ["SECRET", "TOKEN"])
    assert result.count("SECRET") == 1


def test_get_hidden_keys_missing_profile_returns_empty(tmp_vault):
    assert get_hidden_keys(tmp_vault, "nonexistent") == []


def test_get_hidden_keys_after_hide(tmp_vault):
    hide_keys(tmp_vault, "dev", ["DB_PASS"])
    assert "DB_PASS" in get_hidden_keys(tmp_vault, "dev")


def test_show_keys_removes_from_hidden(tmp_vault):
    hide_keys(tmp_vault, "prod", ["A", "B", "C"])
    result = show_keys(tmp_vault, "prod", ["B"])
    assert "B" not in result
    assert "A" in result
    assert "C" in result


def test_show_keys_not_hidden_raises(tmp_vault):
    hide_keys(tmp_vault, "prod", ["A"])
    with pytest.raises(VisibilityError, match="not hidden"):
        show_keys(tmp_vault, "prod", ["MISSING_KEY"])


def test_filter_visible_removes_hidden_keys(tmp_vault):
    hide_keys(tmp_vault, "prod", ["SECRET"])
    env = {"APP_NAME": "myapp", "SECRET": "s3cr3t", "PORT": "8080"}
    visible = filter_visible(tmp_vault, "prod", env)
    assert "SECRET" not in visible
    assert "APP_NAME" in visible
    assert "PORT" in visible


def test_filter_visible_no_hidden_returns_all(tmp_vault):
    env = {"A": "1", "B": "2"}
    visible = filter_visible(tmp_vault, "dev", env)
    assert visible == env


def test_clear_hidden_removes_profile_rules(tmp_vault):
    hide_keys(tmp_vault, "staging", ["KEY1", "KEY2"])
    clear_hidden(tmp_vault, "staging")
    assert get_hidden_keys(tmp_vault, "staging") == []


def test_clear_hidden_missing_profile_raises(tmp_vault):
    with pytest.raises(VisibilityError, match="No visibility rules"):
        clear_hidden(tmp_vault, "ghost")


def test_hidden_keys_isolated_per_profile(tmp_vault):
    hide_keys(tmp_vault, "prod", ["PROD_SECRET"])
    hide_keys(tmp_vault, "dev", ["DEV_SECRET"])
    assert "PROD_SECRET" not in get_hidden_keys(tmp_vault, "dev")
    assert "DEV_SECRET" not in get_hidden_keys(tmp_vault, "prod")
