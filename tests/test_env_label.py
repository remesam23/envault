"""Tests for envault.env_label."""
import pytest

from envault.env_label import (
    LabelError,
    find_by_label,
    get_label,
    list_labels,
    remove_label,
    set_label,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_get_label(tmp_vault):
    set_label(tmp_vault, "production", "Production Env")
    assert get_label(tmp_vault, "production") == "Production Env"


def test_get_label_missing_profile_returns_none(tmp_vault):
    assert get_label(tmp_vault, "ghost") is None


def test_set_label_strips_whitespace(tmp_vault):
    set_label(tmp_vault, "staging", "  Staging  ")
    assert get_label(tmp_vault, "staging") == "Staging"


def test_set_blank_label_raises(tmp_vault):
    with pytest.raises(LabelError, match="blank"):
        set_label(tmp_vault, "dev", "   ")


def test_overwrite_label(tmp_vault):
    set_label(tmp_vault, "dev", "Development")
    set_label(tmp_vault, "dev", "Dev Env")
    assert get_label(tmp_vault, "dev") == "Dev Env"


def test_remove_label(tmp_vault):
    set_label(tmp_vault, "dev", "Development")
    remove_label(tmp_vault, "dev")
    assert get_label(tmp_vault, "dev") is None


def test_remove_missing_label_raises(tmp_vault):
    with pytest.raises(LabelError, match="No label"):
        remove_label(tmp_vault, "nonexistent")


def test_list_labels_returns_all(tmp_vault):
    set_label(tmp_vault, "prod", "Production")
    set_label(tmp_vault, "dev", "Development")
    mapping = list_labels(tmp_vault)
    assert mapping == {"prod": "Production", "dev": "Development"}


def test_list_labels_empty_vault(tmp_vault):
    assert list_labels(tmp_vault) == {}


def test_find_by_label_case_insensitive(tmp_vault):
    set_label(tmp_vault, "prod", "Production")
    set_label(tmp_vault, "prod2", "production")
    results = find_by_label(tmp_vault, "PRODUCTION")
    assert set(results) == {"prod", "prod2"}


def test_find_by_label_no_match(tmp_vault):
    set_label(tmp_vault, "dev", "Development")
    assert find_by_label(tmp_vault, "Staging") == []


def test_labels_isolated_per_vault(tmp_path):
    vault_a = str(tmp_path / "a")
    vault_b = str(tmp_path / "b")
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    set_label(vault_a, "dev", "Dev A")
    assert get_label(vault_b, "dev") is None
