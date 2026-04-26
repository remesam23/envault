"""env_supersede: mark a profile as superseded by another, with optional reason."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class SupersedeError(Exception):
    pass


def _supersede_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".supersede.json"


def _load_supersede(vault_dir: str) -> dict:
    p = _supersede_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_supersede(vault_dir: str, data: dict) -> None:
    _supersede_path(vault_dir).write_text(json.dumps(data, indent=2))


@dataclass
class SupersedeEntry:
    profile: str
    superseded_by: str
    reason: Optional[str] = None


@dataclass
class SupersedeResult:
    ok: bool
    entry: Optional[SupersedeEntry] = None
    message: str = ""


def mark_superseded(
    vault_dir: str,
    profile: str,
    superseded_by: str,
    reason: Optional[str] = None,
) -> SupersedeResult:
    if profile == superseded_by:
        raise SupersedeError(f"Profile '{profile}' cannot supersede itself.")
    data = _load_supersede(vault_dir)
    entry = {"superseded_by": superseded_by}
    if reason:
        entry["reason"] = reason
    data[profile] = entry
    _save_supersede(vault_dir, data)
    return SupersedeResult(
        ok=True,
        entry=SupersedeEntry(profile=profile, superseded_by=superseded_by, reason=reason),
        message=f"Profile '{profile}' marked as superseded by '{superseded_by}'.",
    )


def get_supersede(vault_dir: str, profile: str) -> Optional[SupersedeEntry]:
    data = _load_supersede(vault_dir)
    if profile not in data:
        return None
    rec = data[profile]
    return SupersedeEntry(
        profile=profile,
        superseded_by=rec["superseded_by"],
        reason=rec.get("reason"),
    )


def clear_supersede(vault_dir: str, profile: str) -> None:
    data = _load_supersede(vault_dir)
    if profile not in data:
        raise SupersedeError(f"Profile '{profile}' has no supersede entry.")
    del data[profile]
    _save_supersede(vault_dir, data)


def list_superseded(vault_dir: str) -> list[SupersedeEntry]:
    data = _load_supersede(vault_dir)
    return [
        SupersedeEntry(
            profile=p,
            superseded_by=rec["superseded_by"],
            reason=rec.get("reason"),
        )
        for p, rec in data.items()
    ]
