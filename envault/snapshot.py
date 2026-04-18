"""Snapshot support: save and restore point-in-time copies of profiles."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from envault.vault import load_profile, save_profile


class SnapshotError(Exception):
    pass


def _snapshots_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "snapshots.json"


def _load_snapshots(vault_dir: str) -> dict[str, list[dict]]:
    p = _snapshots_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_snapshots(vault_dir: str, data: dict[str, list[dict]]) -> None:
    _snapshots_path(vault_dir).write_text(json.dumps(data, indent=2))


def take_snapshot(vault_dir: str, profile: str, password: str, label: str = "") -> dict:
    """Decrypt profile and store a timestamped snapshot."""
    env = load_profile(vault_dir, profile, password)
    snapshots = _load_snapshots(vault_dir)
    entry = {
        "ts": time.time(),
        "label": label,
        "env": env,
    }
    snapshots.setdefault(profile, []).append(entry)
    _save_snapshots(vault_dir, snapshots)
    return entry


def list_snapshots(vault_dir: str, profile: str) -> list[dict]:
    """Return snapshots for a profile (without env data)."""
    snapshots = _load_snapshots(vault_dir)
    return [
        {"index": i, "ts": s["ts"], "label": s["label"]}
        for i, s in enumerate(snapshots.get(profile, []))
    ]


def restore_snapshot(vault_dir: str, profile: str, index: int, password: str) -> dict:
    """Re-encrypt a snapshot back into the vault."""
    snapshots = _load_snapshots(vault_dir)
    entries = snapshots.get(profile, [])
    if not entries:
        raise SnapshotError(f"No snapshots found for profile '{profile}'")
    if index < 0 or index >= len(entries):
        raise SnapshotError(f"Snapshot index {index} out of range (0-{len(entries)-1})")
    env = entries[index]["env"]
    save_profile(vault_dir, profile, env, password)
    return env


def delete_snapshot(vault_dir: str, profile: str, index: int) -> None:
    snapshots = _load_snapshots(vault_dir)
    entries = snapshots.get(profile, [])
    if index < 0 or index >= len(entries):
        raise SnapshotError(f"Snapshot index {index} out of range")
    entries.pop(index)
    snapshots[profile] = entries
    _save_snapshots(vault_dir, snapshots)
