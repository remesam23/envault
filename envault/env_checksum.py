"""Checksum tracking for profiles — detect unexpected external changes."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional


class ChecksumError(Exception):
    pass


class ChecksumResult:
    def __init__(self, profile: str, checksum: str, matched: bool, previous: Optional[str]):
        self.profile = profile
        self.checksum = checksum
        self.matched = matched
        self.previous = previous

    def ok(self) -> bool:
        return self.matched or self.previous is None


def _checksum_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".checksums.json"


def _load_checksums(vault_dir: str) -> dict:
    p = _checksum_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_checksums(vault_dir: str, data: dict) -> None:
    _checksum_path(vault_dir).write_text(json.dumps(data, indent=2))


def _compute(profile_data: dict) -> str:
    serialized = json.dumps(profile_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def record_checksum(vault_dir: str, profile: str, profile_data: dict) -> str:
    """Compute and store checksum for a profile. Returns the checksum string."""
    checksum = _compute(profile_data)
    data = _load_checksums(vault_dir)
    data[profile] = checksum
    _save_checksums(vault_dir, data)
    return checksum


def verify_checksum(vault_dir: str, profile: str, profile_data: dict) -> ChecksumResult:
    """Verify current profile data against stored checksum."""
    data = _load_checksums(vault_dir)
    previous = data.get(profile)
    current = _compute(profile_data)
    matched = previous == current
    return ChecksumResult(profile=profile, checksum=current, matched=matched, previous=previous)


def get_checksum(vault_dir: str, profile: str) -> Optional[str]:
    """Return stored checksum for a profile, or None if not recorded."""
    return _load_checksums(vault_dir).get(profile)


def clear_checksum(vault_dir: str, profile: str) -> None:
    """Remove stored checksum for a profile."""
    data = _load_checksums(vault_dir)
    if profile not in data:
        raise ChecksumError(f"No checksum recorded for profile '{profile}'")
    del data[profile]
    _save_checksums(vault_dir, data)


def list_checksums(vault_dir: str) -> dict:
    """Return all stored checksums as {profile: checksum}."""
    return dict(_load_checksums(vault_dir))
