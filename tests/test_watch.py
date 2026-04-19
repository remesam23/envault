"""Tests for envault.watch."""
import os
import time
import pytest
from pathlib import Path

from envault.watch import watch_file, watch_summary, WatchError
from envault.vault import load_profile


@pytest.fixture
def tmp_vault(tmp_path):
    vault = str(tmp_path / "vault")
    os.makedirs(vault)
    return vault


def _write(path, content):
    Path(path).write_text(content)
    # Bump mtime explicitly to avoid sub-second resolution issues
    t = Path(path).stat().st_mtime + 1
    os.utime(path, (t, t))


def test_watch_syncs_on_change(tmp_vault, tmp_path):
    env_file = str(tmp_path / ".env")
    Path(env_file).write_text("KEY=initial\n")

    synced = []

    def on_sync(profile, count):
        synced.append(count)
        # Mutate mtime again to stop after first sync via max_cycles

    # Seed with initial write then let one cycle detect the change
    _write(env_file, "KEY=updated\n")

    watch_file(
        vault_dir=tmp_vault,
        dotenv_path=env_file,
        profile="dev",
        password="secret",
        interval=0,
        max_cycles=1,
        on_sync=on_sync,
    )

    assert len(synced) == 1
    data = load_profile(tmp_vault, "dev", "secret")
    assert data["KEY"] == "updated"


def test_watch_no_change_no_sync(tmp_vault, tmp_path):
    env_file = str(tmp_path / ".env")
    Path(env_file).write_text("KEY=value\n")

    syncs = watch_file(
        vault_dir=tmp_vault,
        dotenv_path=env_file,
        profile="dev",
        password="secret",
        interval=0,
        max_cycles=3,
    )
    assert syncs == 0


def test_watch_missing_file_raises(tmp_vault):
    with pytest.raises(WatchError, match="File not found"):
        watch_file(
            vault_dir=tmp_vault,
            dotenv_path="/nonexistent/.env",
            profile="dev",
            password="secret",
            interval=0,
            max_cycles=1,
        )


def test_watch_summary():
    assert watch_summary("prod", 5) == "Watched profile 'prod': 5 sync(s) recorded."
    assert watch_summary("dev", 0) == "Watched profile 'dev': 0 sync(s) recorded."
