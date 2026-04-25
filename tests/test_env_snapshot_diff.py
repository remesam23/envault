"""Tests for env_snapshot_diff module."""

import pytest
from unittest.mock import patch

from envault.env_snapshot_diff import diff_snapshot, format_snapshot_diff, ok, SnapshotDiffResult
from envault.snapshot import SnapshotError


SNAP_ENTRY = {
    "id": "snap-001",
    "data": {"DB_HOST": "localhost", "DB_PORT": "5432", "OLD_KEY": "old_val"},
}


def _mock_get_snapshot(vault_path, profile, snapshot_id):
    if snapshot_id == "snap-001":
        return SNAP_ENTRY
    return None


@pytest.fixture
def current_data():
    return {"DB_HOST": "prod-host", "DB_PORT": "5432", "NEW_KEY": "new_val"}


def test_diff_detects_added_key(current_data):
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", current_data)
    assert "NEW_KEY" in result.added


def test_diff_detects_removed_key(current_data):
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", current_data)
    assert "OLD_KEY" in result.removed


def test_diff_detects_changed_key(current_data):
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", current_data)
    assert "DB_HOST" in result.changed
    assert result.changed["DB_HOST"] == ("localhost", "prod-host")


def test_diff_unchanged_key_not_in_changed(current_data):
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", current_data)
    assert "DB_PORT" not in result.changed
    assert "DB_PORT" in result.unchanged


def test_has_diff_true_when_differences(current_data):
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", current_data)
    assert result.has_diff is True


def test_ok_false_when_differences(current_data):
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", current_data)
    assert ok(result) is False


def test_no_diff_when_identical():
    identical = {"DB_HOST": "localhost", "DB_PORT": "5432", "OLD_KEY": "old_val"}
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", identical)
    assert not result.has_diff
    assert ok(result) is True


def test_missing_snapshot_raises():
    with patch("envault.env_snapshot_diff.get_snapshot", return_value=None):
        with pytest.raises(SnapshotError, match="not found"):
            diff_snapshot(".envault", "prod", "missing-id", {})


def test_format_shows_added(current_data):
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", current_data)
    output = format_snapshot_diff(result)
    assert "+ NEW_KEY" in output


def test_format_shows_removed(current_data):
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", current_data)
    output = format_snapshot_diff(result)
    assert "- OLD_KEY" in output


def test_format_no_diff_message():
    identical = {"DB_HOST": "localhost", "DB_PORT": "5432", "OLD_KEY": "old_val"}
    with patch("envault.env_snapshot_diff.get_snapshot", side_effect=_mock_get_snapshot):
        result = diff_snapshot(".envault", "prod", "snap-001", identical)
    output = format_snapshot_diff(result)
    assert "No differences" in output
