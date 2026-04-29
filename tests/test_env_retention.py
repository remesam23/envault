"""Tests for envault.env_retention."""
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from envault.env_retention import (
    RetentionError,
    RetentionPolicy,
    set_policy,
    get_policy,
    clear_policy,
    list_policies,
    apply_retention,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return tmp_path


def test_set_and_get_policy(tmp_vault):
    policy = set_policy(tmp_vault, "prod", max_snapshots=5)
    assert policy.profile == "prod"
    assert policy.max_snapshots == 5
    assert policy.max_days is None

    fetched = get_policy(tmp_vault, "prod")
    assert fetched is not None
    assert fetched.max_snapshots == 5


def test_set_policy_with_max_days(tmp_vault):
    policy = set_policy(tmp_vault, "staging", max_days=30)
    assert policy.max_days == 30
    assert policy.max_snapshots is None


def test_set_policy_with_reason(tmp_vault):
    policy = set_policy(tmp_vault, "dev", max_snapshots=3, reason="cost control")
    assert policy.reason == "cost control"
    fetched = get_policy(tmp_vault, "dev")
    assert fetched.reason == "cost control"


def test_set_policy_invalid_max_snapshots_raises(tmp_vault):
    with pytest.raises(RetentionError, match="max_snapshots"):
        set_policy(tmp_vault, "prod", max_snapshots=0)


def test_set_policy_invalid_max_days_raises(tmp_vault):
    with pytest.raises(RetentionError, match="max_days"):
        set_policy(tmp_vault, "prod", max_days=-1)


def test_set_policy_no_constraints_raises(tmp_vault):
    with pytest.raises(RetentionError, match="At least one"):
        set_policy(tmp_vault, "prod")


def test_get_policy_missing_profile_returns_none(tmp_vault):
    assert get_policy(tmp_vault, "ghost") is None


def test_clear_policy_removes_entry(tmp_vault):
    set_policy(tmp_vault, "prod", max_snapshots=10)
    clear_policy(tmp_vault, "prod")
    assert get_policy(tmp_vault, "prod") is None


def test_clear_policy_missing_raises(tmp_vault):
    with pytest.raises(RetentionError, match="No retention policy"):
        clear_policy(tmp_vault, "ghost")


def test_list_policies_returns_all(tmp_vault):
    set_policy(tmp_vault, "prod", max_snapshots=5)
    set_policy(tmp_vault, "dev", max_days=7)
    policies = list_policies(tmp_vault)
    names = [p.profile for p in policies]
    assert "prod" in names
    assert "dev" in names


def test_list_policies_empty_vault(tmp_vault):
    assert list_policies(tmp_vault) == []


def _snap(snap_id, days_ago):
    ts = datetime.utcnow() - timedelta(days=days_ago)
    return {"id": snap_id, "timestamp": ts.isoformat()}


def test_apply_retention_no_policy_keeps_all(tmp_vault):
    snaps = [_snap("s1", 1), _snap("s2", 5), _snap("s3", 10)]
    result = apply_retention(tmp_vault, "prod", snaps)
    assert result.pruned == []
    assert result.kept == 3


def test_apply_retention_max_snapshots_prunes_oldest(tmp_vault):
    set_policy(tmp_vault, "prod", max_snapshots=2)
    snaps = [_snap("s1", 1), _snap("s2", 5), _snap("s3", 10)]
    result = apply_retention(tmp_vault, "prod", snaps)
    assert result.kept == 2
    assert "s3" in result.pruned
    assert len(result.pruned) == 1


def test_apply_retention_max_days_prunes_old_entries(tmp_vault):
    set_policy(tmp_vault, "prod", max_days=3)
    snaps = [_snap("s1", 1), _snap("s2", 2), _snap("s3", 10)]
    result = apply_retention(tmp_vault, "prod", snaps)
    assert "s3" in result.pruned
    assert result.kept == 2


def test_apply_retention_result_message(tmp_vault):
    set_policy(tmp_vault, "prod", max_snapshots=1)
    snaps = [_snap("s1", 1), _snap("s2", 5)]
    result = apply_retention(tmp_vault, "prod", snaps)
    assert "Pruned" in result.message
    assert result.ok is True
