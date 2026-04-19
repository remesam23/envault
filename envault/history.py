"""Profile value history tracking for envault."""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Any


class HistoryError(Exception):
    pass


def _history_path(vault_dir: str) -> Path:
    return Path(vault_dir) / "history.json"


def _load_history(vault_dir: str) -> dict:
    p = _history_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_history(vault_dir: str, data: dict) -> None:
    _history_path(vault_dir).write_text(json.dumps(data, indent=2))


def record_snapshot(vault_dir: str, profile: str, env: dict[str, str]) -> dict:
    """Record a history entry for a profile's current state."""
    history = _load_history(vault_dir)
    entries = history.setdefault(profile, [])
    entry = {"timestamp": time.time(), "env": dict(env)}
    entries.append(entry)
    _save_history(vault_dir, history)
    return entry


def get_history(vault_dir: str, profile: str) -> list[dict]:
    """Return all history entries for a profile."""
    history = _load_history(vault_dir)
    return history.get(profile, [])


def clear_history(vault_dir: str, profile: str) -> int:
    """Clear history for a profile. Returns number of entries removed."""
    history = _load_history(vault_dir)
    entries = history.pop(profile, [])
    _save_history(vault_dir, history)
    return len(entries)


def format_history(entries: list[dict], show_values: bool = False) -> str:
    """Format history entries for display."""
    if not entries:
        return "No history found."
    lines = []
    for i, entry in enumerate(entries):
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["timestamp"]))
        keys = list(entry["env"].keys())
        lines.append(f"[{i}] {ts} — {len(keys)} key(s): {', '.join(keys)}")
        if show_values:
            for k, v in entry["env"].items():
                lines.append(f"      {k}={v}")
    return "\n".join(lines)
