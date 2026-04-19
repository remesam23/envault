import pytest
import json
from pathlib import Path
from envault.archive import (
    ArchiveError, create_archive, list_archives, get_archive,
    delete_archive, archive_summary,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


RAW = {
    "dev": {"KEY": "val1"},
    "prod": {"KEY": "val2", "SECRET": "s"},
}


def test_create_archive_returns_entry(tmp_vault):
    entry = create_archive(tmp_vault, RAW, label="initial")
    assert entry["label"] == "initial"
    assert set(entry["profiles"]) == {"dev", "prod"}
    assert entry["data"] == RAW
    assert "timestamp" in entry
    assert "id" in entry


def test_list_archives_hides_data(tmp_vault):
    create_archive(tmp_vault, RAW)
    listing = list_archives(tmp_vault)
    assert len(listing) == 1
    assert "data" not in listing[0]
    assert "profiles" in listing[0]


def test_multiple_archives_accumulate(tmp_vault):
    create_archive(tmp_vault, RAW, label="a")
    create_archive(tmp_vault, RAW, label="b")
    assert len(list_archives(tmp_vault)) == 2


def test_get_archive_by_id(tmp_vault):
    entry = create_archive(tmp_vault, RAW)
    fetched = get_archive(tmp_vault, entry["id"])
    assert fetched["data"] == RAW


def test_get_archive_missing_raises(tmp_vault):
    with pytest.raises(ArchiveError, match="not found"):
        get_archive(tmp_vault, "nonexistent")


def test_delete_archive(tmp_vault):
    entry = create_archive(tmp_vault, RAW)
    delete_archive(tmp_vault, entry["id"])
    assert list_archives(tmp_vault) == []


def test_delete_missing_raises(tmp_vault):
    with pytest.raises(ArchiveError):
        delete_archive(tmp_vault, "bad-id")


def test_archive_summary_with_label(tmp_vault):
    entry = create_archive(tmp_vault, RAW, label="release")
    s = archive_summary(entry)
    assert "release" in s
    assert entry["id"] in s
    assert "dev" in s or "prod" in s


def test_list_empty_vault(tmp_vault):
    assert list_archives(tmp_vault) == []
