"""Profile locking — prevent accidental writes to specific profiles."""
from __future__ import annotations
import json
from pathlib import Path


class EnvLockError(Exception):
    pass


def _lock_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".locks.json"


def _load_locks(vault_dir: str) -> dict:
    p = _lock_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_locks(vault_dir: str, data: dict) -> None:
    _lock_path(vault_dir).write_text(json.dumps(data, indent=2))


def lock_profile(vault_dir: str, profile: str) -> None:
    """Mark a profile as locked."""
    locks = _load_locks(vault_dir)
    locks[profile] = True
    _save_locks(vault_dir, locks)


def unlock_profile(vault_dir: str, profile: str) -> None:
    """Remove lock from a profile."""
    locks = _load_locks(vault_dir)
    if profile not in locks:
        raise EnvLockError(f"Profile '{profile}' is not locked.")
    del locks[profile]
    _save_locks(vault_dir, locks)


def is_locked(vault_dir: str, profile: str) -> bool:
    return _load_locks(vault_dir).get(profile, False)


def assert_unlocked(vault_dir: str, profile: str) -> None:
    """Raise EnvLockError if profile is locked."""
    if is_locked(vault_dir, profile):
        raise EnvLockError(
            f"Profile '{profile}' is locked. Use 'envault lock remove {profile}' to unlock."
        )


def list_locked(vault_dir: str) -> list[str]:
    return [p for p, v in _load_locks(vault_dir).items() if v]
