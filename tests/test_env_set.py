import pytest
from envault.env_set import set_keys, format_set_result, SetResult


BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_add_new_key():
    data, result = set_keys(BASE, {"NEW_KEY": "value"})
    assert data["NEW_KEY"] == "value"
    assert "NEW_KEY" in result.added


def test_update_existing_key():
    data, result = set_keys(BASE, {"HOST": "remotehost"})
    assert data["HOST"] == "remotehost"
    assert "HOST" in result.updated


def test_no_overwrite_skips_existing():
    data, result = set_keys(BASE, {"HOST": "other"}, overwrite=False)
    assert data["HOST"] == "localhost"
    assert "HOST" in result.skipped


def test_no_overwrite_still_adds_new():
    data, result = set_keys(BASE, {"BRAND_NEW": "yes"}, overwrite=False)
    assert data["BRAND_NEW"] == "yes"
    assert "BRAND_NEW" in result.added


def test_delete_existing_key():
    data, result = set_keys(BASE, {"DEBUG": None})
    assert "DEBUG" not in data
    assert "DEBUG" in result.deleted


def test_delete_missing_key_skips():
    data, result = set_keys(BASE, {"MISSING": None})
    assert result.skipped == ["MISSING"]


def test_delete_none_false_skips_none_values():
    data, result = set_keys(BASE, {"DEBUG": None}, delete_none=False)
    assert "DEBUG" in data
    assert "DEBUG" in result.skipped


def test_original_data_not_mutated():
    original = dict(BASE)
    set_keys(BASE, {"HOST": "changed", "NEW": "val"})
    assert BASE == original


def test_format_result_shows_all_actions():
    result = SetResult(added=["A"], updated=["B"], deleted=["C"], skipped=["D"])
    text = format_set_result(result)
    assert "+ A" in text
    assert "~ B" in text
    assert "- C" in text
    assert ". D" in text


def test_format_result_empty():
    result = SetResult()
    assert format_set_result(result) == "  (no changes)"


def test_multiple_updates_in_one_call():
    data, result = set_keys(BASE, {"HOST": "new", "EXTRA": "x", "PORT": None})
    assert data["HOST"] == "new"
    assert data["EXTRA"] == "x"
    assert "PORT" not in data
    assert len(result.updated) == 1
    assert len(result.added) == 1
    assert len(result.deleted) == 1
