"""Tag management for envault profiles."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List


class TagError(Exception):
    pass


def _tags_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "tags.json"


def _load_tags(vault_dir: str) -> Dict[str, List[str]]:
    path = _tags_path(vault_dir)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _save_tags(vault_dir: str, data: Dict[str, List[str]]) -> None:
    path = _tags_path(vault_dir)
    Path(vault_dir).mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def add_tag(vault_dir: str, profile: str, tag: str) -> None:
    data = _load_tags(vault_dir)
    tags = data.get(profile, [])
    if tag not in tags:
        tags.append(tag)
    data[profile] = tags
    _save_tags(vault_dir, data)


def remove_tag(vault_dir: str, profile: str, tag: str) -> None:
    data = _load_tags(vault_dir)
    tags = data.get(profile, [])
    if tag not in tags:
        raise TagError(f"Tag '{tag}' not found on profile '{profile}'.")
    tags.remove(tag)
    data[profile] = tags
    _save_tags(vault_dir, data)


def get_tags(vault_dir: str, profile: str) -> List[str]:
    return _load_tags(vault_dir).get(profile, [])


def profiles_by_tag(vault_dir: str, tag: str) -> List[str]:
    data = _load_tags(vault_dir)
    return [profile for profile, tags in data.items() if tag in tags]


def remove_profile_tags(vault_dir: str, profile: str) -> None:
    data = _load_tags(vault_dir)
    data.pop(profile, None)
    _save_tags(vault_dir, data)
