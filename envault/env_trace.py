"""Trace key access across profiles — record when a key was read and from which profile."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


class TraceError(Exception):
    pass


@dataclass
class TraceEntry:
    profile: str
    key: str
    timestamp: str
    context: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "profile": self.profile,
            "key": self.key,
            "timestamp": self.timestamp,
            "context": self.context,
        }

    @staticmethod
    def from_dict(d: dict) -> "TraceEntry":
        return TraceEntry(
            profile=d["profile"],
            key=d["key"],
            timestamp=d["timestamp"],
            context=d.get("context"),
        )


@dataclass
class TraceResult:
    entries: List[TraceEntry] = field(default_factory=list)
    ok: bool = True
    message: str = ""


def _trace_path(vault_path: Path) -> Path:
    return vault_path / ".trace.json"


def _load_trace(vault_path: Path) -> List[dict]:
    p = _trace_path(vault_path)
    if not p.exists():
        return []
    return json.loads(p.read_text())


def _save_trace(vault_path: Path, entries: List[dict]) -> None:
    _trace_path(vault_path).write_text(json.dumps(entries, indent=2))


def record_access(
    vault_path: Path,
    profile: str,
    key: str,
    context: Optional[str] = None,
) -> TraceEntry:
    """Record a key access event."""
    entries = _load_trace(vault_path)
    entry = TraceEntry(
        profile=profile,
        key=key,
        timestamp=datetime.now(timezone.utc).isoformat(),
        context=context,
    )
    entries.append(entry.to_dict())
    _save_trace(vault_path, entries)
    return entry


def get_trace(
    vault_path: Path,
    profile: Optional[str] = None,
    key: Optional[str] = None,
) -> List[TraceEntry]:
    """Return trace entries, optionally filtered by profile and/or key."""
    raw = _load_trace(vault_path)
    entries = [TraceEntry.from_dict(r) for r in raw]
    if profile is not None:
        entries = [e for e in entries if e.profile == profile]
    if key is not None:
        entries = [e for e in entries if e.key == key]
    return entries


def clear_trace(vault_path: Path, profile: Optional[str] = None) -> int:
    """Clear trace entries. Returns number of entries removed."""
    raw = _load_trace(vault_path)
    if profile is None:
        count = len(raw)
        _save_trace(vault_path, [])
        return count
    before = len(raw)
    remaining = [r for r in raw if r.get("profile") != profile]
    _save_trace(vault_path, remaining)
    return before - len(remaining)


def format_trace(entries: List[TraceEntry]) -> str:
    if not entries:
        return "No trace entries found."
    lines = []
    for e in entries:
        ctx = f" [{e.context}]" if e.context else ""
        lines.append(f"{e.timestamp}  {e.profile}::{e.key}{ctx}")
    return "\n".join(lines)
