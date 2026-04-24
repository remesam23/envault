"""Scope management: restrict which keys are visible per profile context."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class ScopeError(Exception):
    pass


def _scope_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".scopes.json"


def _load_scopes(vault_dir: str) -> Dict[str, List[str]]:
    p = _scope_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_scopes(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _scope_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_scope(vault_dir: str, profile: str, keys: List[str]) -> List[str]:
    """Define the allowed key list for a profile scope."""
    scopes = _load_scopes(vault_dir)
    scopes[profile] = sorted(set(keys))
    _save_scopes(vault_dir, scopes)
    return scopes[profile]


def get_scope(vault_dir: str, profile: str) -> Optional[List[str]]:
    """Return the scope key list for a profile, or None if no scope is set."""
    return _load_scopes(vault_dir).get(profile)


def clear_scope(vault_dir: str, profile: str) -> None:
    """Remove the scope restriction for a profile."""
    scopes = _load_scopes(vault_dir)
    if profile not in scopes:
        raise ScopeError(f"No scope defined for profile '{profile}'")
    del scopes[profile]
    _save_scopes(vault_dir, scopes)


def apply_scope(vault_dir: str, profile: str, env: Dict[str, str]) -> Dict[str, str]:
    """Filter an env dict to only keys allowed by the profile scope.

    If no scope is defined the full dict is returned unchanged.
    """
    scope = get_scope(vault_dir, profile)
    if scope is None:
        return dict(env)
    return {k: v for k, v in env.items() if k in scope}


def list_scopes(vault_dir: str) -> Dict[str, List[str]]:
    """Return all defined scopes."""
    return _load_scopes(vault_dir)
