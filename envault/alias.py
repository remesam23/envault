"""Profile alias management for envault."""
from __future__ import annotations
import json
from pathlib import Path


class AliasError(Exception):
    pass


def _alias_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".aliases.json"


def _load_aliases(vault_dir: str) -> dict[str, str]:
    p = _alias_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(vault_dir: str, aliases: dict[str, str]) -> None:
    _alias_path(vault_dir).write_text(json.dumps(aliases, indent=2))


def set_alias(vault_dir: str, alias: str, profile: str) -> None:
    """Map alias -> profile. Raises AliasError if alias == profile."""
    if alias == profile:
        raise AliasError(f"Alias '{alias}' cannot be the same as the profile name.")
    aliases = _load_aliases(vault_dir)
    aliases[alias] = profile
    _save_aliases(vault_dir, aliases)


def remove_alias(vault_dir: str, alias: str) -> None:
    """Remove an alias. Raises AliasError if not found."""
    aliases = _load_aliases(vault_dir)
    if alias not in aliases:
        raise AliasError(f"Alias '{alias}' not found.")
    del aliases[alias]
    _save_aliases(vault_dir, aliases)


def resolve_alias(vault_dir: str, name: str) -> str:
    """Return the profile name for a given alias or name (passthrough if not an alias)."""
    aliases = _load_aliases(vault_dir)
    return aliases.get(name, name)


def list_aliases(vault_dir: str) -> dict[str, str]:
    """Return all alias -> profile mappings."""
    return _load_aliases(vault_dir)


def get_aliases_for_profile(vault_dir: str, profile: str) -> list[str]:
    """Return all aliases pointing to a given profile."""
    return [a for a, p in _load_aliases(vault_dir).items() if p == profile]
