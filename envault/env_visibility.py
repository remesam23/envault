"""env_visibility.py — control which keys are visible per profile.

Allows marking keys as hidden so they are excluded from display/export
without being deleted from the vault.
"""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class VisibilityError(Exception):
    pass


def _visibility_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".visibility.json"


def _load_visibility(vault_dir: str) -> Dict[str, List[str]]:
    p = _visibility_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_visibility(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _visibility_path(vault_dir).write_text(json.dumps(data, indent=2))


def hide_keys(vault_dir: str, profile: str, keys: List[str]) -> List[str]:
    """Mark keys as hidden for a profile. Returns the updated hidden list."""
    data = _load_visibility(vault_dir)
    current = set(data.get(profile, []))
    current.update(keys)
    data[profile] = sorted(current)
    _save_visibility(vault_dir, data)
    return data[profile]


def show_keys(vault_dir: str, profile: str, keys: List[str]) -> List[str]:
    """Remove keys from the hidden list. Returns the updated hidden list."""
    data = _load_visibility(vault_dir)
    current = set(data.get(profile, []))
    missing = [k for k in keys if k not in current]
    if missing:
        raise VisibilityError(f"Keys not hidden: {', '.join(missing)}")
    current -= set(keys)
    data[profile] = sorted(current)
    _save_visibility(vault_dir, data)
    return data[profile]


def get_hidden_keys(vault_dir: str, profile: str) -> List[str]:
    """Return list of hidden keys for a profile."""
    return _load_visibility(vault_dir).get(profile, [])


def filter_visible(vault_dir: str, profile: str, env: Dict[str, str]) -> Dict[str, str]:
    """Return env dict with hidden keys removed."""
    hidden = set(get_hidden_keys(vault_dir, profile))
    return {k: v for k, v in env.items() if k not in hidden}


def clear_hidden(vault_dir: str, profile: str) -> None:
    """Remove all hidden-key restrictions for a profile."""
    data = _load_visibility(vault_dir)
    if profile not in data:
        raise VisibilityError(f"No visibility rules for profile '{profile}'")
    del data[profile]
    _save_visibility(vault_dir, data)
