"""env_immutable.py — mark profile keys as immutable (cannot be overwritten)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class ImmutableError(Exception):
    pass


def _immutable_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".immutable.json"


def _load_immutable(vault_dir: str) -> dict:
    p = _immutable_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_immutable(vault_dir: str, data: dict) -> None:
    _immutable_path(vault_dir).write_text(json.dumps(data, indent=2))


def lock_keys(vault_dir: str, profile: str, keys: List[str]) -> List[str]:
    """Mark *keys* in *profile* as immutable. Returns the list of newly locked keys."""
    data = _load_immutable(vault_dir)
    existing: List[str] = data.get(profile, [])
    added = [k for k in keys if k not in existing]
    data[profile] = sorted(set(existing) | set(keys))
    _save_immutable(vault_dir, data)
    return added


def unlock_keys(vault_dir: str, profile: str, keys: List[str]) -> List[str]:
    """Remove immutability from *keys* in *profile*. Returns keys that were actually unlocked."""
    data = _load_immutable(vault_dir)
    existing: List[str] = data.get(profile, [])
    removed = [k for k in keys if k in existing]
    if not removed:
        raise ImmutableError(f"None of the specified keys are immutable in profile '{profile}'.")
    data[profile] = sorted(set(existing) - set(keys))
    _save_immutable(vault_dir, data)
    return removed


def get_immutable_keys(vault_dir: str, profile: str) -> List[str]:
    """Return the list of immutable keys for *profile*."""
    data = _load_immutable(vault_dir)
    return data.get(profile, [])


def is_immutable(vault_dir: str, profile: str, key: str) -> bool:
    """Return True if *key* is immutable in *profile*."""
    return key in get_immutable_keys(vault_dir, profile)


def check_immutable(vault_dir: str, profile: str, keys: List[str]) -> List[str]:
    """Return the subset of *keys* that are immutable (i.e. must not be overwritten)."""
    locked = set(get_immutable_keys(vault_dir, profile))
    return [k for k in keys if k in locked]


def clear_immutable(vault_dir: str, profile: str) -> None:
    """Remove all immutability rules for *profile*."""
    data = _load_immutable(vault_dir)
    if profile not in data:
        raise ImmutableError(f"No immutability rules found for profile '{profile}'.")
    del data[profile]
    _save_immutable(vault_dir, data)
