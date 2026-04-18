"""Audit log for vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_AUDIT_FILE = ".envault_audit.json"


def _audit_path(vault_dir: str) -> Path:
    return Path(vault_dir) / DEFAULT_AUDIT_FILE


def record_event(vault_dir: str, action: str, profile: str, details: str = "") -> None:
    """Append an audit event to the log file."""
    path = _audit_path(vault_dir)
    events = _load_events(vault_dir)
    events.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "profile": profile,
        "details": details,
        "user": os.environ.get("USER", "unknown"),
    })
    path.write_text(json.dumps(events, indent=2))


def _load_events(vault_dir: str) -> list:
    path = _audit_path(vault_dir)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def get_events(vault_dir: str, profile: str = None) -> list:
    """Return audit events, optionally filtered by profile."""
    events = _load_events(vault_dir)
    if profile:
        events = [e for e in events if e.get("profile") == profile]
    return events


def clear_events(vault_dir: str) -> None:
    """Clear all audit events."""
    path = _audit_path(vault_dir)
    if path.exists():
        path.unlink()
