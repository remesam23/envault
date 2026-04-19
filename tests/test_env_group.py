import pytest
from envault.env_group import (
    create_group, add_to_group, remove_from_group,
    get_group, list_groups, delete_group, GroupError
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_create_group(tmp_vault):
    members = create_group(tmp_vault, "staging", ["dev", "qa"])
    assert members == ["dev", "qa"]


def test_create_group_deduplicates(tmp_vault):
    members = create_group(tmp_vault, "g", ["a", "b", "a"])
    assert members == ["a", "b"]


def test_get_group_returns_members(tmp_vault):
    create_group(tmp_vault, "g", ["x", "y"])
    assert get_group(tmp_vault, "g") == ["x", "y"]


def test_get_missing_group_raises(tmp_vault):
    with pytest.raises(GroupError, match="does not exist"):
        get_group(tmp_vault, "nope")


def test_add_to_group(tmp_vault):
    create_group(tmp_vault, "g", ["a"])
    members = add_to_group(tmp_vault, "g", "b")
    assert "b" in members


def test_add_duplicate_is_idempotent(tmp_vault):
    create_group(tmp_vault, "g", ["a"])
    add_to_group(tmp_vault, "g", "a")
    assert get_group(tmp_vault, "g").count("a") == 1


def test_add_to_missing_group_raises(tmp_vault):
    with pytest.raises(GroupError):
        add_to_group(tmp_vault, "missing", "profile")


def test_remove_from_group(tmp_vault):
    create_group(tmp_vault, "g", ["a", "b"])
    members = remove_from_group(tmp_vault, "g", "a")
    assert "a" not in members


def test_remove_not_in_group_raises(tmp_vault):
    create_group(tmp_vault, "g", ["a"])
    with pytest.raises(GroupError, match="not in group"):
        remove_from_group(tmp_vault, "g", "z")


def test_list_groups_returns_all(tmp_vault):
    create_group(tmp_vault, "g1", ["a"])
    create_group(tmp_vault, "g2", ["b", "c"])
    groups = list_groups(tmp_vault)
    assert set(groups.keys()) == {"g1", "g2"}


def test_list_groups_empty(tmp_vault):
    assert list_groups(tmp_vault) == {}


def test_delete_group(tmp_vault):
    create_group(tmp_vault, "g", ["a"])
    delete_group(tmp_vault, "g")
    assert "g" not in list_groups(tmp_vault)


def test_delete_missing_group_raises(tmp_vault):
    with pytest.raises(GroupError):
        delete_group(tmp_vault, "ghost")
