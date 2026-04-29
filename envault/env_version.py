"""Profile versioning: assign semantic version strings to profiles."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


class VersionError(Exception):
    pass


@dataclass
class VersionEntry:
    version: str
    note: Optional[str] = None


def _version_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".envault_versions.json"


def _load_versions(vault_dir: str) -> dict:
    p = _version_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_versions(vault_dir: str, data: dict) -> None:
    _version_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_version(vault_dir: str, profile: str, version: str, note: Optional[str] = None) -> VersionEntry:
    """Assign a semver string to a profile."""
    if not VERSION_RE.match(version):
        raise VersionError(f"Invalid version format '{version}'. Expected MAJOR.MINOR.PATCH.")
    data = _load_versions(vault_dir)
    data[profile] = {"version": version, "note": note}
    _save_versions(vault_dir, data)
    return VersionEntry(version=version, note=note)


def get_version(vault_dir: str, profile: str) -> Optional[VersionEntry]:
    """Return the version entry for a profile, or None if unset."""
    data = _load_versions(vault_dir)
    if profile not in data:
        return None
    entry = data[profile]
    return VersionEntry(version=entry["version"], note=entry.get("note"))


def clear_version(vault_dir: str, profile: str) -> None:
    """Remove the version tag from a profile."""
    data = _load_versions(vault_dir)
    if profile not in data:
        raise VersionError(f"Profile '{profile}' has no version set.")
    del data[profile]
    _save_versions(vault_dir, data)


def list_versions(vault_dir: str) -> dict[str, VersionEntry]:
    """Return all versioned profiles."""
    data = _load_versions(vault_dir)
    return {p: VersionEntry(version=e["version"], note=e.get("note")) for p, e in data.items()}
