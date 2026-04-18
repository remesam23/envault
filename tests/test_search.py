"""Tests for envault.search."""
import pytest
from envault.vault import save_profile
from envault.search import search_profiles, format_search, SearchMatch

PASSWORD = "test-pass"


@pytest.fixture
def tmp_vault(tmp_path):
    save_profile(str(tmp_path), "dev", {"DB_HOST": "localhost", "DB_PORT": "5432"}, PASSWORD)
    save_profile(str(tmp_path), "prod", {"DB_HOST": "prod.db", "API_KEY": "secret123"}, PASSWORD)
    return str(tmp_path)


def test_search_finds_key_substring(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "DB")
    keys = {m.key for m in result.matches}
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_search_finds_value_substring(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "localhost")
    assert any(m.value == "localhost" for m in result.matches)


def test_search_keys_only_skips_value_match(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "localhost", keys_only=True)
    assert result.empty


def test_search_values_only_skips_key_match(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "DB_HOST", values_only=True)
    assert result.empty


def test_search_limited_to_profile(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "DB_HOST", profile="dev")
    assert all(m.profile == "dev" for m in result.matches)
    assert len(result.matches) == 1


def test_search_case_insensitive_default(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "db_host")
    assert not result.empty


def test_search_case_sensitive_no_match(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "db_host", case_sensitive=True)
    assert result.empty


def test_search_no_matches_returns_empty(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "NONEXISTENT_XYZ")
    assert result.empty


def test_format_search_empty():
    from envault.search import SearchResult
    assert format_search(SearchResult()) == "No matches found."


def test_format_search_shows_values(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "DB_PORT")
    output = format_search(result, show_values=True)
    assert "5432" in output


def test_format_search_hides_values_by_default(tmp_vault):
    result = search_profiles(tmp_vault, PASSWORD, "DB_PORT")
    output = format_search(result, show_values=False)
    assert "5432" not in output
    assert "DB_PORT" in output
