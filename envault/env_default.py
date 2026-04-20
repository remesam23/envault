"""Apply default values to profiles — fill in missing keys from a defaults map."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DefaultError(Exception):
    """Raised when applying defaults fails."""


@dataclass
class DefaultResult:
    applied: Dict[str, str] = field(default_factory=dict)   # key -> value filled in
    skipped: List[str] = field(default_factory=list)         # keys already present
    ok: bool = True
    message: str = ""


def ok(result: DefaultResult) -> bool:
    return result.ok


def apply_defaults(
    profile: Dict[str, str],
    defaults: Dict[str, str],
    overwrite: bool = False,
) -> DefaultResult:
    """Return a new profile dict with defaults applied.

    Args:
        profile:   Existing key/value pairs.
        defaults:  Mapping of key -> default value.
        overwrite: If True, overwrite existing keys with default values.

    Returns:
        DefaultResult with the merged profile stored in .applied (new keys only)
        and the full merged dict accessible via merge_into().
    """
    if defaults is None:
        raise DefaultError("defaults map must not be None")

    applied: Dict[str, str] = {}
    skipped: List[str] = []

    merged = dict(profile)
    for key, value in defaults.items():
        if key in profile and not overwrite:
            skipped.append(key)
        else:
            if key not in profile or overwrite:
                if key in profile:
                    skipped_flag = False
                else:
                    skipped_flag = False
                merged[key] = value
                applied[key] = value

    return DefaultResult(applied=applied, skipped=skipped, ok=True)


def merge_into(
    profile: Dict[str, str],
    defaults: Dict[str, str],
    overwrite: bool = False,
) -> Dict[str, str]:
    """Return the fully merged profile dict."""
    merged = dict(profile)
    for key, value in defaults.items():
        if key not in merged or overwrite:
            merged[key] = value
    return merged


def format_default_result(result: DefaultResult) -> str:
    lines: List[str] = []
    if result.applied:
        lines.append(f"Applied {len(result.applied)} default(s):")
        for k, v in sorted(result.applied.items()):
            lines.append(f"  + {k}={v}")
    if result.skipped:
        lines.append(f"Skipped {len(result.skipped)} existing key(s): {', '.join(sorted(result.skipped))}")
    if not result.applied and not result.skipped:
        lines.append("No defaults to apply.")
    return "\n".join(lines)
