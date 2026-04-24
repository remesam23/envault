"""Annotation support: attach human-readable notes to individual keys in a profile."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class AnnotateError(Exception):
    pass


def _annotations_path(vault_dir: str, profile: str) -> Path:
    return Path(vault_dir) / f".annotations_{profile}.json"


def _load_annotations(vault_dir: str, profile: str) -> Dict[str, str]:
    path = _annotations_path(vault_dir, profile)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_annotations(vault_dir: str, profile: str, data: Dict[str, str]) -> None:
    path = _annotations_path(vault_dir, profile)
    path.write_text(json.dumps(data, indent=2))


def set_annotation(vault_dir: str, profile: str, key: str, note: str) -> str:
    """Attach a note to *key* in *profile*. Returns the stored note."""
    annotations = _load_annotations(vault_dir, profile)
    annotations[key] = note
    _save_annotations(vault_dir, profile, annotations)
    return note


def get_annotation(vault_dir: str, profile: str, key: str) -> Optional[str]:
    """Return the note for *key*, or None if not set."""
    return _load_annotations(vault_dir, profile).get(key)


def remove_annotation(vault_dir: str, profile: str, key: str) -> None:
    """Remove the note for *key*. Raises AnnotateError if not found."""
    annotations = _load_annotations(vault_dir, profile)
    if key not in annotations:
        raise AnnotateError(f"No annotation for key '{key}' in profile '{profile}'")
    del annotations[key]
    _save_annotations(vault_dir, profile, annotations)


def list_annotations(vault_dir: str, profile: str) -> Dict[str, str]:
    """Return all key→note mappings for *profile*."""
    return dict(_load_annotations(vault_dir, profile))


def format_annotations(annotations: Dict[str, str]) -> str:
    if not annotations:
        return "(no annotations)"
    lines = [f"  {k}: {v}" for k, v in sorted(annotations.items())]
    return "\n".join(lines)
