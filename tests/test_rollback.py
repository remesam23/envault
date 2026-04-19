import pytest
from pathlib import Path
from envault.vault import save_profile, load_profile
from envault.history import record_snapshot
from envault.rollback import rollback_profile, rollback_summary, RollbackError

PASSWORD = "testpass"


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def _save(vault, profile, env):
    save_profile(vault, profile, env, PASSWORD)


def test_rollback_restores_old_state(tmp_vault):
    env_v1 = {"KEY": "v1", "FOO": "bar"}
    _save(tmp_vault, "dev", env_v1)
    entry = record_snapshot(tmp_vault, "dev", env_v1, label="v1")

    env_v2 = {"KEY": "v2", "FOO": "baz", "NEW": "extra"}
    _save(tmp_vault, "dev", env_v2)

    restored = rollback_profile(tmp_vault, "dev", PASSWORD, entry["id"])
    assert restored == env_v1

    live = load_profile(tmp_vault, "dev", PASSWORD)
    assert live == env_v1


def test_rollback_missing_entry_raises(tmp_vault):
    env = {"A": "1"}
    _save(tmp_vault, "dev", env)
    with pytest.raises(RollbackError, match="not found"):
        rollback_profile(tmp_vault, "dev", PASSWORD, "nonexistent-id")


def test_rollback_wrong_profile_raises(tmp_vault):
    env = {"A": "1"}
    _save(tmp_vault, "dev", env)
    entry = record_snapshot(tmp_vault, "dev", env, label="snap")
    # entry belongs to 'dev', not 'prod'
    with pytest.raises(RollbackError):
        rollback_profile(tmp_vault, "prod", PASSWORD, entry["id"])


def test_rollback_summary_format(tmp_vault):
    env = {"X": "1", "Y": "2"}
    _save(tmp_vault, "staging", env)
    entry = record_snapshot(tmp_vault, "staging", env, label="snap")
    restored = rollback_profile(tmp_vault, "staging", PASSWORD, entry["id"])
    summary = rollback_summary("staging", entry["id"], restored)
    assert "staging" in summary
    assert entry["id"] in summary
    assert "2 key(s)" in summary
