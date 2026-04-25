"""Read-only mode management for profiles.

Allows marking profiles as read-only to prevent accidental modifications.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class ReadOnlyError(Exception):
    pass


def _readonly_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".readonly.json"


def _load_readonly(vault_dir: str) -> dict:
    p = _readonly_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_readonly(vault_dir: str, data: dict) -> None:
    _readonly_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_readonly(vault_dir: str, profile: str, reason: Optional[str] = None) -> dict:
    """Mark a profile as read-only."""
    data = _load_readonly(vault_dir)
    data[profile] = {"reason": reason or ""}
    _save_readonly(vault_dir, data)
    return data[profile]


def unset_readonly(vault_dir: str, profile: str) -> None:
    """Remove read-only status from a profile."""
    data = _load_readonly(vault_dir)
    if profile not in data:
        raise ReadOnlyError(f"Profile '{profile}' is not marked as read-only.")
    del data[profile]
    _save_readonly(vault_dir, data)


def is_readonly(vault_dir: str, profile: str) -> bool:
    """Return True if the profile is marked as read-only."""
    return profile in _load_readonly(vault_dir)


def get_readonly_reason(vault_dir: str, profile: str) -> Optional[str]:
    """Return the reason a profile is read-only, or None if not read-only."""
    data = _load_readonly(vault_dir)
    entry = data.get(profile)
    if entry is None:
        return None
    return entry.get("reason") or None


def list_readonly(vault_dir: str) -> dict[str, Optional[str]]:
    """Return all read-only profiles mapped to their reasons."""
    data = _load_readonly(vault_dir)
    return {k: (v.get("reason") or None) for k, v in data.items()}


def guard_readonly(vault_dir: str, profile: str) -> None:
    """Raise ReadOnlyError if the profile is read-only."""
    if is_readonly(vault_dir, profile):
        reason = get_readonly_reason(vault_dir, profile)
        msg = f"Profile '{profile}' is read-only."
        if reason:
            msg += f" Reason: {reason}"
        raise ReadOnlyError(msg)
