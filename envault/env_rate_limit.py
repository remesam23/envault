"""Rate limiting for vault operations — tracks access frequency per profile."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class RateLimitError(Exception):
    pass


@dataclass
class RateLimitConfig:
    max_accesses: int
    window_seconds: int


@dataclass
class RateLimitResult:
    allowed: bool
    profile: str
    accesses_in_window: int
    limit: int
    window_seconds: int
    message: str = ""

    @classmethod
    def ok(cls, profile: str, count: int, limit: int, window: int) -> "RateLimitResult":
        return cls(True, profile, count, limit, window, f"Access allowed ({count}/{limit})")

    @classmethod
    def denied(cls, profile: str, count: int, limit: int, window: int) -> "RateLimitResult":
        return cls(False, profile, count, limit, window, f"Rate limit exceeded ({count}/{limit} in {window}s)")


def _rate_limit_path(vault_path: Path) -> Path:
    return vault_path / ".rate_limits.json"


def _load_data(vault_path: Path) -> dict:
    p = _rate_limit_path(vault_path)
    if not p.exists():
        return {"configs": {}, "log": {}}
    return json.loads(p.read_text())


def _save_data(vault_path: Path, data: dict) -> None:
    _rate_limit_path(vault_path).write_text(json.dumps(data, indent=2))


def set_rate_limit(vault_path: Path, profile: str, max_accesses: int, window_seconds: int) -> RateLimitConfig:
    if max_accesses < 1:
        raise RateLimitError("max_accesses must be >= 1")
    if window_seconds < 1:
        raise RateLimitError("window_seconds must be >= 1")
    data = _load_data(vault_path)
    data["configs"][profile] = {"max_accesses": max_accesses, "window_seconds": window_seconds}
    _save_data(vault_path, data)
    return RateLimitConfig(max_accesses=max_accesses, window_seconds=window_seconds)


def get_rate_limit(vault_path: Path, profile: str) -> Optional[RateLimitConfig]:
    data = _load_data(vault_path)
    cfg = data["configs"].get(profile)
    if cfg is None:
        return None
    return RateLimitConfig(**cfg)


def clear_rate_limit(vault_path: Path, profile: str) -> None:
    data = _load_data(vault_path)
    if profile not in data["configs"]:
        raise RateLimitError(f"No rate limit configured for profile '{profile}'")
    data["configs"].pop(profile, None)
    data["log"].pop(profile, None)
    _save_data(vault_path, data)


def check_and_record(vault_path: Path, profile: str) -> RateLimitResult:
    """Record an access attempt and check whether it is within the rate limit."""
    data = _load_data(vault_path)
    cfg = data["configs"].get(profile)
    if cfg is None:
        return RateLimitResult(True, profile, 0, 0, 0, "No rate limit configured")
    max_accesses = cfg["max_accesses"]
    window_seconds = cfg["window_seconds"]
    now = time.time()
    cutoff = now - window_seconds
    log: list = data["log"].get(profile, [])
    log = [ts for ts in log if ts > cutoff]
    log.append(now)
    data["log"][profile] = log
    _save_data(vault_path, data)
    count = len(log)
    if count > max_accesses:
        return RateLimitResult.denied(profile, count, max_accesses, window_seconds)
    return RateLimitResult.ok(profile, count, max_accesses, window_seconds)
