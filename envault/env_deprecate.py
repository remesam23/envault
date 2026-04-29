"""Mark profile keys as deprecated with optional replacement hints."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class DeprecateError(Exception):
    pass


@dataclass
class DeprecateEntry:
    key: str
    reason: Optional[str] = None
    replacement: Optional[str] = None


@dataclass
class DeprecateResult:
    profile: str
    deprecated: list[DeprecateEntry] = field(default_factory=list)
    message: str = ""

    @staticmethod
    def ok(profile: str, entries: list[DeprecateEntry]) -> "DeprecateResult":
        return DeprecateResult(
            profile=profile,
            deprecated=entries,
            message=f"{len(entries)} key(s) marked as deprecated in '{profile}'.",
        )


def _deprecate_path(vault_dir: Path) -> Path:
    return vault_dir / ".deprecations.json"


def _load_deprecations(vault_dir: Path) -> dict:
    p = _deprecate_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deprecations(vault_dir: Path, data: dict) -> None:
    _deprecate_path(vault_dir).write_text(json.dumps(data, indent=2))


def mark_deprecated(
    vault_dir: Path,
    profile: str,
    keys: list[str],
    reason: Optional[str] = None,
    replacement: Optional[str] = None,
) -> DeprecateResult:
    data = _load_deprecations(vault_dir)
    profile_data = data.get(profile, {})
    entries: list[DeprecateEntry] = []
    for key in keys:
        profile_data[key] = {"reason": reason, "replacement": replacement}
        entries.append(DeprecateEntry(key=key, reason=reason, replacement=replacement))
    data[profile] = profile_data
    _save_deprecations(vault_dir, data)
    return DeprecateResult.ok(profile, entries)


def get_deprecated(vault_dir: Path, profile: str) -> dict[str, DeprecateEntry]:
    data = _load_deprecations(vault_dir)
    raw = data.get(profile, {})
    return {
        k: DeprecateEntry(key=k, reason=v.get("reason"), replacement=v.get("replacement"))
        for k, v in raw.items()
    }


def unmark_deprecated(vault_dir: Path, profile: str, key: str) -> None:
    data = _load_deprecations(vault_dir)
    profile_data = data.get(profile, {})
    if key not in profile_data:
        raise DeprecateError(f"Key '{key}' is not marked as deprecated in '{profile}'.")
    del profile_data[key]
    data[profile] = profile_data
    _save_deprecations(vault_dir, data)


def is_deprecated(vault_dir: Path, profile: str, key: str) -> bool:
    return key in _load_deprecations(vault_dir).get(profile, {})


def format_deprecate_result(result: DeprecateResult) -> str:
    lines = [result.message]
    for entry in result.deprecated:
        hint = f" -> replace with '{entry.replacement}'" if entry.replacement else ""
        note = f" ({entry.reason})" if entry.reason else ""
        lines.append(f"  [DEPRECATED] {entry.key}{note}{hint}")
    return "\n".join(lines)
