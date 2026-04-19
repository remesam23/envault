"""Archive and restore entire vault snapshots (all profiles at once)."""

import json
import time
from pathlib import Path
from typing import Any


class ArchiveError(Exception):
    pass


def _archive_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "archives.json"


def _load_archives(vault_dir: str) -> list[dict]:
    p = _archive_path(vault_dir)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_archives(vault_dir: str, archives: list[dict]) -> None:
    _archive_path(vault_dir).write_text(json.dumps(archives, indent=2))


def create_archive(vault_dir: str, raw_data: dict[str, Any], label: str = "") -> dict:
    """Store a full snapshot of raw vault data."""
    archives = _load_archives(vault_dir)
    entry = {
        "id": str(int(time.time() * 1000)),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "label": label,
        "profiles": list(raw_data.keys()),
        "data": raw_data,
    }
    archives.append(entry)
    _save_archives(vault_dir, archives)
    return entry


def list_archives(vault_dir: str) -> list[dict]:
    return [{k: v for k, v in e.items() if k != "data"} for e in _load_archives(vault_dir)]


def get_archive(vault_dir: str, archive_id: str) -> dict:
    for entry in _load_archives(vault_dir):
        if entry["id"] == archive_id:
            return entry
    raise ArchiveError(f"Archive '{archive_id}' not found.")


def delete_archive(vault_dir: str, archive_id: str) -> None:
    archives = _load_archives(vault_dir)
    new = [e for e in archives if e["id"] != archive_id]
    if len(new) == len(archives):
        raise ArchiveError(f"Archive '{archive_id}' not found.")
    _save_archives(vault_dir, new)


def archive_summary(entry: dict) -> str:
    profiles = ", ".join(entry["profiles"]) or "(none)"
    label = f" [{entry['label']}]" if entry.get("label") else ""
    return f"Archive {entry['id']}{label} @ {entry['timestamp']} — profiles: {profiles}"
