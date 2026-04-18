import pytest
from pathlib import Path
from envault.vault import save_profile, load_profile
from envault.clone import CloneError, clone_profile, clone_summary


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault")


PASSWORD = "secret"


def _save(vault, name, data):
    save_profile(vault, name, data, PASSWORD)


def test_clone_full_profile(tmp_vault):
    _save(tmp_vault, "prod", {"A": "1", "B": "2"})
    result = clone_profile(tmp_vault, PASSWORD, "prod", "staging")
    assert result == {"A": "1", "B": "2"}
    loaded = load_profile(tmp_vault, "staging", PASSWORD)
    assert loaded == {"A": "1", "B": "2"}


def test_clone_subset_of_keys(tmp_vault):
    _save(tmp_vault, "prod", {"A": "1", "B": "2", "C": "3"})
    result = clone_profile(tmp_vault, PASSWORD, "prod", "staging", keys=["A", "C"])
    assert result == {"A": "1", "C": "3"}
    loaded = load_profile(tmp_vault, "staging", PASSWORD)
    assert loaded == {"A": "1", "C": "3"}


def test_clone_missing_key_in_filter_ignored(tmp_vault):
    _save(tmp_vault, "prod", {"A": "1"})
    result = clone_profile(tmp_vault, PASSWORD, "prod", "staging", keys=["A", "Z"])
    assert result == {"A": "1"}


def test_clone_missing_source_raises(tmp_vault):
    with pytest.raises(CloneError, match="Source profile"):
        clone_profile(tmp_vault, PASSWORD, "ghost", "new")


def test_clone_existing_dst_raises_without_overwrite(tmp_vault):
    _save(tmp_vault, "prod", {"A": "1"})
    _save(tmp_vault, "staging", {"B": "2"})
    with pytest.raises(CloneError, match="already exists"):
        clone_profile(tmp_vault, PASSWORD, "prod", "staging")


def test_clone_existing_dst_allowed_with_overwrite(tmp_vault):
    _save(tmp_vault, "prod", {"A": "1"})
    _save(tmp_vault, "staging", {"B": "2"})
    result = clone_profile(tmp_vault, PASSWORD, "prod", "staging", overwrite=True)
    assert result == {"A": "1"}


def test_clone_summary_plural(tmp_vault):
    _save(tmp_vault, "prod", {"A": "1", "B": "2"})
    data = clone_profile(tmp_vault, PASSWORD, "prod", "staging")
    msg = clone_summary("prod", "staging", data)
    assert "prod" in msg and "staging" in msg and "2 keys" in msg


def test_clone_summary_singular(tmp_vault):
    _save(tmp_vault, "prod", {"A": "1"})
    data = clone_profile(tmp_vault, PASSWORD, "prod", "staging")
    msg = clone_summary("prod", "staging", data)
    assert "1 key" in msg and "1 keys" not in msg
