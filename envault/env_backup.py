"""Backup and restore profiles to/from a portable JSON bundle."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envault.vault import list_profiles, load_profile, save_profile


class BackupError(Exception):
    pass


@dataclass
class BackupResult:
    profiles: List[str]
    path: str
    timestamp: float

    def ok(self) -> bool:
        return len(self.profiles) > 0

    def summary(self) -> str:
        names = ", ".join(self.profiles)
        return f"Backed up {len(self.profiles)} profile(s) to {self.path}: {names}"


@dataclass
class RestoreResult:
    restored: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = []
        if self.restored:
            parts.append(f"Restored: {', '.join(self.restored)}")
        if self.skipped:
            parts.append(f"Skipped (already exist): {', '.join(self.skipped)}")
        return "  ".join(parts) if parts else "Nothing to restore."


def backup_profiles(
    vault_path: str,
    password: str,
    dest: str,
    profiles: Optional[List[str]] = None,
) -> BackupResult:
    """Encrypt-decrypt all (or selected) profiles and write a JSON bundle."""
    available = list_profiles(vault_path)
    targets = profiles if profiles is not None else available
    unknown = set(targets) - set(available)
    if unknown:
        raise BackupError(f"Unknown profile(s): {', '.join(sorted(unknown))}")

    bundle: Dict[str, Dict[str, str]] = {}
    for name in targets:
        bundle[name] = load_profile(vault_path, name, password)

    ts = time.time()
    payload = {"timestamp": ts, "profiles": bundle}
    Path(dest).write_text(json.dumps(payload, indent=2))
    return BackupResult(profiles=list(targets), path=dest, timestamp=ts)


def restore_profiles(
    vault_path: str,
    password: str,
    src: str,
    overwrite: bool = False,
) -> RestoreResult:
    """Load a JSON bundle and re-encrypt profiles into the vault."""
    try:
        payload = json.loads(Path(src).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise BackupError(f"Cannot read backup file: {exc}") from exc

    bundle: Dict[str, Dict[str, str]] = payload.get("profiles", {})
    existing = set(list_profiles(vault_path))
    result = RestoreResult()

    for name, data in bundle.items():
        if name in existing and not overwrite:
            result.skipped.append(name)
            continue
        save_profile(vault_path, name, data, password)
        result.restored.append(name)

    return result
