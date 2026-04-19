"""Group multiple profiles under a named group."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict


class GroupError(Exception):
    pass


def _groups_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".groups.json"


def _load_groups(vault_dir: str) -> Dict[str, List[str]]:
    p = _groups_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_groups(vault_dir: str, data: Dict[str, List[str]]) -> None:
    _groups_path(vault_dir).write_text(json.dumps(data, indent=2))


def create_group(vault_dir: str, group: str, profiles: List[str]) -> List[str]:
    data = _load_groups(vault_dir)
    data[group] = list(dict.fromkeys(profiles))  # deduplicate, preserve order
    _save_groups(vault_dir, data)
    return data[group]


def add_to_group(vault_dir: str, group: str, profile: str) -> List[str]:
    data = _load_groups(vault_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    if profile not in data[group]:
        data[group].append(profile)
    _save_groups(vault_dir, data)
    return data[group]


def remove_from_group(vault_dir: str, group: str, profile: str) -> List[str]:
    data = _load_groups(vault_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    if profile not in data[group]:
        raise GroupError(f"Profile '{profile}' is not in group '{group}'.")
    data[group].remove(profile)
    _save_groups(vault_dir, data)
    return data[group]


def get_group(vault_dir: str, group: str) -> List[str]:
    data = _load_groups(vault_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    return data[group]


def list_groups(vault_dir: str) -> Dict[str, List[str]]:
    return _load_groups(vault_dir)


def delete_group(vault_dir: str, group: str) -> None:
    data = _load_groups(vault_dir)
    if group not in data:
        raise GroupError(f"Group '{group}' does not exist.")
    del data[group]
    _save_groups(vault_dir, data)
