"""Tests for envault.snapshot."""

import pytest

from envault.snapshot import SnapshotError, delete_snapshot, list_snapshots, restore_snapshot, take_snapshot
from envault.vault import load_profile, save_profile


@pytest.fixture
def tmp_vault(tmp_path):
    vault = str(tmp_path)
    save_profile(vault, "dev", {"KEY": "val1", "OTHER": "x"}, "pass")
    return vault


def test_take_snapshot_returns_entry(tmp_vault):
    entry = take_snapshot(tmp_vault, "dev", "pass", label="v1")
    assert entry["label"] == "v1"
    assert entry["env"] == {"KEY": "val1", "OTHER": "x"}
    assert entry["ts"] > 0


def test_list_snapshots_shows_metadata(tmp_vault):
    take_snapshot(tmp_vault, "dev", "pass", label="first")
    take_snapshot(tmp_vault, "dev", "pass", label="second")
    snaps = list_snapshots(tmp_vault, "dev")
    assert len(snaps) == 2
    assert snaps[0]["index"] == 0
    assert snaps[0]["label"] == "first"
    assert snaps[1]["label"] == "second"
    # env data should not be exposed
    assert "env" not in snaps[0]


def test_list_snapshots_empty(tmp_vault):
    assert list_snapshots(tmp_vault, "dev") == []


def test_restore_snapshot_rewrites_profile(tmp_vault):
    take_snapshot(tmp_vault, "dev", "pass")  # snapshot index 0: KEY=val1
    save_profile(tmp_vault, "dev", {"KEY": "val2"}, "pass")  # modify profile
    restore_snapshot(tmp_vault, "dev", 0, "pass")
    env = load_profile(tmp_vault, "dev", "pass")
    assert env == {"KEY": "val1", "OTHER": "x"}


def test_restore_invalid_index_raises(tmp_vault):
    take_snapshot(tmp_vault, "dev", "pass")
    with pytest.raises(SnapshotError):
        restore_snapshot(tmp_vault, "dev", 99, "pass")


def test_restore_no_snapshots_raises(tmp_vault):
    with pytest.raises(SnapshotError):
        restore_snapshot(tmp_vault, "dev", 0, "pass")


def test_delete_snapshot(tmp_vault):
    take_snapshot(tmp_vault, "dev", "pass", label="a")
    take_snapshot(tmp_vault, "dev", "pass", label="b")
    delete_snapshot(tmp_vault, "dev", 0)
    snaps = list_snapshots(tmp_vault, "dev")
    assert len(snaps) == 1
    assert snaps[0]["label"] == "b"


def test_delete_invalid_index_raises(tmp_vault):
    take_snapshot(tmp_vault, "dev", "pass")
    with pytest.raises(SnapshotError):
        delete_snapshot(tmp_vault, "dev", 5)
