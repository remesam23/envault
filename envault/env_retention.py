"""Retention policy management for vault profiles."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class RetentionError(Exception):
    pass


@dataclass
class RetentionPolicy:
    profile: str
    max_snapshots: Optional[int] = None
    max_days: Optional[int] = None
    reason: Optional[str] = None


@dataclass
class RetentionResult:
    profile: str
    pruned: list[str]
    kept: int
    ok: bool
    message: str


def _retention_path(vault_dir: Path) -> Path:
    return vault_dir / ".retention.json"


def _load_retention(vault_dir: Path) -> dict:
    p = _retention_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_retention(vault_dir: Path, data: dict) -> None:
    _retention_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_policy(
    vault_dir: Path,
    profile: str,
    max_snapshots: Optional[int] = None,
    max_days: Optional[int] = None,
    reason: Optional[str] = None,
) -> RetentionPolicy:
    if max_snapshots is not None and max_snapshots < 1:
        raise RetentionError("max_snapshots must be >= 1")
    if max_days is not None and max_days < 1:
        raise RetentionError("max_days must be >= 1")
    if max_snapshots is None and max_days is None:
        raise RetentionError("At least one of max_snapshots or max_days must be set")
    data = _load_retention(vault_dir)
    data[profile] = {
        "max_snapshots": max_snapshots,
        "max_days": max_days,
        "reason": reason,
    }
    _save_retention(vault_dir, data)
    return RetentionPolicy(profile=profile, max_snapshots=max_snapshots, max_days=max_days, reason=reason)


def get_policy(vault_dir: Path, profile: str) -> Optional[RetentionPolicy]:
    data = _load_retention(vault_dir)
    if profile not in data:
        return None
    entry = data[profile]
    return RetentionPolicy(
        profile=profile,
        max_snapshots=entry.get("max_snapshots"),
        max_days=entry.get("max_days"),
        reason=entry.get("reason"),
    )


def clear_policy(vault_dir: Path, profile: str) -> None:
    data = _load_retention(vault_dir)
    if profile not in data:
        raise RetentionError(f"No retention policy found for profile '{profile}'")
    del data[profile]
    _save_retention(vault_dir, data)


def list_policies(vault_dir: Path) -> list[RetentionPolicy]:
    data = _load_retention(vault_dir)
    return [
        RetentionPolicy(
            profile=p,
            max_snapshots=v.get("max_snapshots"),
            max_days=v.get("max_days"),
            reason=v.get("reason"),
        )
        for p, v in data.items()
    ]


def apply_retention(
    vault_dir: Path,
    profile: str,
    snapshots: list[dict],
) -> RetentionResult:
    """Given a list of snapshot dicts with 'id' and 'timestamp', return which to prune."""
    policy = get_policy(vault_dir, profile)
    if policy is None:
        return RetentionResult(profile=profile, pruned=[], kept=len(snapshots), ok=True, message="No policy set")

    sorted_snaps = sorted(snapshots, key=lambda s: s["timestamp"], reverse=True)
    to_keep = list(sorted_snaps)

    if policy.max_snapshots is not None:
        to_keep = to_keep[: policy.max_snapshots]

    if policy.max_days is not None:
        cutoff = datetime.utcnow() - timedelta(days=policy.max_days)
        to_keep = [s for s in to_keep if datetime.fromisoformat(s["timestamp"]) >= cutoff]

    kept_ids = {s["id"] for s in to_keep}
    pruned = [s["id"] for s in sorted_snaps if s["id"] not in kept_ids]

    return RetentionResult(
        profile=profile,
        pruned=pruned,
        kept=len(to_keep),
        ok=True,
        message=f"Pruned {len(pruned)} snapshot(s), kept {len(to_keep)}",
    )
