"""Freeze a profile: mark it as read-only so no keys can be modified."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class FreezeError(Exception):
    pass


def _freeze_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".freeze.json"


def _load_frozen(vault_dir: str) -> dict:
    p = _freeze_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_frozen(vault_dir: str, data: dict) -> None:
    _freeze_path(vault_dir).write_text(json.dumps(data, indent=2))


def freeze_profile(vault_dir: str, profile: str, reason: Optional[str] = None) -> None:
    """Mark *profile* as frozen.  Raises FreezeError if already frozen."""
    data = _load_frozen(vault_dir)
    if data.get(profile, {}).get("frozen"):
        raise FreezeError(f"Profile '{profile}' is already frozen.")
    data[profile] = {"frozen": True, "reason": reason or ""}
    _save_frozen(vault_dir, data)


def unfreeze_profile(vault_dir: str, profile: str) -> None:
    """Remove the frozen flag from *profile*.  Raises FreezeError if not frozen."""
    data = _load_frozen(vault_dir)
    if not data.get(profile, {}).get("frozen"):
        raise FreezeError(f"Profile '{profile}' is not frozen.")
    del data[profile]
    _save_frozen(vault_dir, data)


def is_frozen(vault_dir: str, profile: str) -> bool:
    """Return True if *profile* is currently frozen."""
    return _load_frozen(vault_dir).get(profile, {}).get("frozen", False)


def get_freeze_reason(vault_dir: str, profile: str) -> Optional[str]:
    """Return the freeze reason for *profile*, or None if not frozen."""
    entry = _load_frozen(vault_dir).get(profile)
    if entry and entry.get("frozen"):
        return entry.get("reason") or None
    return None


def list_frozen(vault_dir: str) -> list[str]:
    """Return a sorted list of all currently frozen profile names."""
    data = _load_frozen(vault_dir)
    return sorted(k for k, v in data.items() if v.get("frozen"))


def assert_not_frozen(vault_dir: str, profile: str) -> None:
    """Raise FreezeError if *profile* is frozen (call before any mutating op)."""
    if is_frozen(vault_dir, profile):
        reason = get_freeze_reason(vault_dir, profile)
        msg = f"Profile '{profile}' is frozen and cannot be modified."
        if reason:
            msg += f" Reason: {reason}"
        raise FreezeError(msg)
