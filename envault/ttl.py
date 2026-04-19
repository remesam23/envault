"""TTL (time-to-live) expiry for vault profiles."""
from __future__ import annotations
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


class TTLError(Exception):
    pass


def _ttl_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".ttl.json"


def _load_ttl(vault_dir: str) -> dict:
    p = _ttl_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(vault_dir: str, data: dict) -> None:
    _ttl_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_ttl(vault_dir: str, profile: str, seconds: int) -> str:
    """Set an expiry for a profile. Returns ISO expiry timestamp."""
    if seconds <= 0:
        raise TTLError("TTL must be a positive number of seconds.")
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()
    data = _load_ttl(vault_dir)
    data[profile] = expires_at
    _save_ttl(vault_dir, data)
    return expires_at


def get_ttl(vault_dir: str, profile: str) -> Optional[str]:
    """Return ISO expiry string or None if no TTL set."""
    return _load_ttl(vault_dir).get(profile)


def is_expired(vault_dir: str, profile: str) -> bool:
    """Return True if the profile TTL has passed."""
    expiry = get_ttl(vault_dir, profile)
    if expiry is None:
        return False
    return datetime.now(timezone.utc) >= datetime.fromisoformat(expiry)


def clear_ttl(vault_dir: str, profile: str) -> None:
    """Remove TTL for a profile."""
    data = _load_ttl(vault_dir)
    if profile not in data:
        raise TTLError(f"No TTL set for profile '{profile}'.")
    del data[profile]
    _save_ttl(vault_dir, data)


def list_ttl(vault_dir: str) -> dict:
    """Return all profile TTL entries."""
    return _load_ttl(vault_dir)
