"""env_quota.py — per-profile key count and value size quotas."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class QuotaError(Exception):
    pass


@dataclass
class QuotaConfig:
    max_keys: Optional[int] = None
    max_value_bytes: Optional[int] = None


@dataclass
class QuotaViolation:
    key: str
    reason: str


@dataclass
class QuotaResult:
    passed: bool
    violations: list[QuotaViolation] = field(default_factory=list)

    @classmethod
    def ok(cls) -> "QuotaResult":
        return cls(passed=True)


def _quota_path(vault_dir: Path) -> Path:
    return vault_dir / ".quotas.json"


def _load_quotas(vault_dir: Path) -> dict:
    p = _quota_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_quotas(vault_dir: Path, data: dict) -> None:
    _quota_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_quota(vault_dir: Path, profile: str, config: QuotaConfig) -> None:
    data = _load_quotas(vault_dir)
    data[profile] = {
        "max_keys": config.max_keys,
        "max_value_bytes": config.max_value_bytes,
    }
    _save_quotas(vault_dir, data)


def get_quota(vault_dir: Path, profile: str) -> Optional[QuotaConfig]:
    data = _load_quotas(vault_dir)
    if profile not in data:
        return None
    entry = data[profile]
    return QuotaConfig(
        max_keys=entry.get("max_keys"),
        max_value_bytes=entry.get("max_value_bytes"),
    )


def clear_quota(vault_dir: Path, profile: str) -> None:
    data = _load_quotas(vault_dir)
    if profile not in data:
        raise QuotaError(f"No quota set for profile '{profile}'.")
    del data[profile]
    _save_quotas(vault_dir, data)


def check_quota(vault_dir: Path, profile: str, env: dict[str, str]) -> QuotaResult:
    config = get_quota(vault_dir, profile)
    if config is None:
        return QuotaResult.ok()

    violations: list[QuotaViolation] = []

    if config.max_keys is not None and len(env) > config.max_keys:
        violations.append(
            QuotaViolation(
                key="__profile__",
                reason=f"Key count {len(env)} exceeds max_keys={config.max_keys}.",
            )
        )

    if config.max_value_bytes is not None:
        for k, v in env.items():
            size = len(v.encode())
            if size > config.max_value_bytes:
                violations.append(
                    QuotaViolation(
                        key=k,
                        reason=f"Value size {size}B exceeds max_value_bytes={config.max_value_bytes}.",
                    )
                )

    return QuotaResult(passed=len(violations) == 0, violations=violations)


def format_quota_result(result: QuotaResult, profile: str) -> str:
    if result.passed:
        return f"[OK] Profile '{profile}' is within quota limits."
    lines = [f"[FAIL] Profile '{profile}' quota violations:"]
    for v in result.violations:
        lines.append(f"  - {v.key}: {v.reason}")
    return "\n".join(lines)
