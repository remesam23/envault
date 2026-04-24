"""Access control for profiles: restrict which keys a caller may read."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class AccessError(Exception):
    pass


def _access_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".access.json"


def _load_access(vault_dir: str) -> Dict[str, List[str]]:
    p = _access_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_access(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _access_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_allowed_keys(vault_dir: str, profile: str, keys: List[str]) -> List[str]:
    """Set the allow-list of keys readable for *profile*."""
    data = _load_access(vault_dir)
    data[profile] = sorted(set(keys))
    _save_access(vault_dir, data)
    return data[profile]


def get_allowed_keys(vault_dir: str, profile: str) -> Optional[List[str]]:
    """Return the allow-list for *profile*, or None if unrestricted."""
    data = _load_access(vault_dir)
    return data.get(profile)


def clear_allowed_keys(vault_dir: str, profile: str) -> None:
    """Remove access restrictions for *profile* (unrestricted again)."""
    data = _load_access(vault_dir)
    if profile not in data:
        raise AccessError(f"No access rules found for profile '{profile}'")
    del data[profile]
    _save_access(vault_dir, data)


def apply_access(vault_dir: str, profile: str, env: Dict[str, str]) -> Dict[str, str]:
    """Filter *env* to only allowed keys; returns full dict if unrestricted."""
    allowed = get_allowed_keys(vault_dir, profile)
    if allowed is None:
        return dict(env)
    return {k: v for k, v in env.items() if k in allowed}


def list_restricted_profiles(vault_dir: str) -> List[str]:
    """Return profiles that have access restrictions defined."""
    return sorted(_load_access(vault_dir).keys())
