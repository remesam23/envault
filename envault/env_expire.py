"""env_expire.py – per-key expiry tracking for profiles."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ExpireError(Exception):
    pass


def _expire_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault_key_expiry.json"


def _load_expiry(vault_dir: str) -> dict:
    p = _expire_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_expiry(vault_dir: str, data: dict) -> None:
    _expire_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_key_expiry(vault_dir: str, profile: str, key: str, expires_at: datetime) -> str:
    """Set an expiry datetime for a specific key in a profile."""
    data = _load_expiry(vault_dir)
    data.setdefault(profile, {})[key] = expires_at.isoformat()
    _save_expiry(vault_dir, data)
    return expires_at.isoformat()


def get_key_expiry(vault_dir: str, profile: str, key: str) -> Optional[str]:
    """Return ISO expiry string for a key, or None if not set."""
    return _load_expiry(vault_dir).get(profile, {}).get(key)


def is_key_expired(vault_dir: str, profile: str, key: str) -> bool:
    """Return True if the key's expiry has passed."""
    raw = get_key_expiry(vault_dir, profile, key)
    if raw is None:
        return False
    expiry = datetime.fromisoformat(raw)
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= expiry


def clear_key_expiry(vault_dir: str, profile: str, key: str) -> None:
    """Remove expiry for a specific key."""
    data = _load_expiry(vault_dir)
    if profile not in data or key not in data[profile]:
        raise ExpireError(f"No expiry set for '{key}' in profile '{profile}'")
    del data[profile][key]
    if not data[profile]:
        del data[profile]
    _save_expiry(vault_dir, data)


def list_expired_keys(vault_dir: str, profile: str) -> list[str]:
    """Return all keys in a profile whose expiry has passed."""
    data = _load_expiry(vault_dir).get(profile, {})
    now = datetime.now(timezone.utc)
    expired = []
    for key, raw in data.items():
        expiry = datetime.fromisoformat(raw)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if now >= expiry:
            expired.append(key)
    return expired


def list_all_expiries(vault_dir: str, profile: str) -> dict[str, str]:
    """Return all key→expiry mappings for a profile."""
    return dict(_load_expiry(vault_dir).get(profile, {}))
