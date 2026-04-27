"""Priority ordering for profiles — assign numeric priorities and resolve ordered lists."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class PriorityError(Exception):
    pass


def _priority_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".priority.json"


def _load_priorities(vault_dir: str) -> Dict[str, int]:
    p = _priority_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_priorities(vault_dir: str, data: Dict[str, int]) -> None:
    _priority_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_priority(vault_dir: str, profile: str, priority: int) -> int:
    """Assign a numeric priority to a profile. Higher = more important."""
    if not isinstance(priority, int):
        raise PriorityError("Priority must be an integer.")
    data = _load_priorities(vault_dir)
    data[profile] = priority
    _save_priorities(vault_dir, data)
    return priority


def get_priority(vault_dir: str, profile: str) -> Optional[int]:
    """Return the priority for a profile, or None if unset."""
    return _load_priorities(vault_dir).get(profile)


def clear_priority(vault_dir: str, profile: str) -> None:
    """Remove the priority entry for a profile."""
    data = _load_priorities(vault_dir)
    if profile not in data:
        raise PriorityError(f"No priority set for profile '{profile}'.")
    del data[profile]
    _save_priorities(vault_dir, data)


def list_priorities(vault_dir: str) -> List[Dict]:
    """Return all profiles sorted by priority descending."""
    data = _load_priorities(vault_dir)
    return [
        {"profile": k, "priority": v}
        for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)
    ]


def ranked_profiles(vault_dir: str, profiles: List[str]) -> List[str]:
    """Sort a list of profile names by their assigned priority (desc). Unset = 0."""
    data = _load_priorities(vault_dir)
    return sorted(profiles, key=lambda p: data.get(p, 0), reverse=True)
