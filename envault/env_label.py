"""env_label.py — attach human-readable labels (display names) to profiles."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class LabelError(Exception):
    pass


def _label_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".labels.json"


def _load_labels(vault_dir: str) -> dict:
    p = _label_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_labels(vault_dir: str, data: dict) -> None:
    _label_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_label(vault_dir: str, profile: str, label: str) -> str:
    """Attach a label to *profile*. Returns the label."""
    if not label.strip():
        raise LabelError("Label must not be blank.")
    data = _load_labels(vault_dir)
    data[profile] = label.strip()
    _save_labels(vault_dir, data)
    return label.strip()


def get_label(vault_dir: str, profile: str) -> Optional[str]:
    """Return the label for *profile*, or None if unset."""
    return _load_labels(vault_dir).get(profile)


def remove_label(vault_dir: str, profile: str) -> None:
    """Remove the label for *profile*. Raises LabelError if not set."""
    data = _load_labels(vault_dir)
    if profile not in data:
        raise LabelError(f"No label set for profile '{profile}'.")
    del data[profile]
    _save_labels(vault_dir, data)


def list_labels(vault_dir: str) -> dict:
    """Return a mapping of profile -> label for all labelled profiles."""
    return dict(_load_labels(vault_dir))


def find_by_label(vault_dir: str, label: str) -> list:
    """Return profile names whose label matches *label* (case-insensitive)."""
    needle = label.strip().lower()
    return [
        profile
        for profile, lbl in _load_labels(vault_dir).items()
        if lbl.lower() == needle
    ]
