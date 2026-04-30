"""env_redact.py — redact specific keys from a profile before output or export."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

REDACTED_PLACEHOLDER = "***REDACTED***"


class RedactError(Exception):
    pass


@dataclass
class RedactResult:
    redacted: Dict[str, str] = field(default_factory=dict)
    keys_redacted: List[str] = field(default_factory=list)
    keys_kept: List[str] = field(default_factory=list)
    ok: bool = True
    message: str = ""


def ok(result: RedactResult) -> bool:
    return result.ok


def redact_profile(
    data: Dict[str, str],
    keys: List[str],
    *,
    placeholder: str = REDACTED_PLACEHOLDER,
    remove: bool = False,
) -> RedactResult:
    """Return a copy of *data* with *keys* redacted or removed.

    Args:
        data: Original key/value mapping.
        keys: Keys to redact.
        placeholder: Replacement value when remove=False.
        remove: If True, drop the key entirely instead of replacing its value.
    """
    if not isinstance(data, dict):
        raise RedactError("data must be a dict")

    key_set = set(keys)
    redacted: Dict[str, str] = {}
    keys_redacted: List[str] = []
    keys_kept: List[str] = []

    for k, v in data.items():
        if k in key_set:
            if not remove:
                redacted[k] = placeholder
            keys_redacted.append(k)
        else:
            redacted[k] = v
            keys_kept.append(k)

    return RedactResult(
        redacted=redacted,
        keys_redacted=sorted(keys_redacted),
        keys_kept=sorted(keys_kept),
    )


def format_redact_result(result: RedactResult, *, show_placeholder: bool = True) -> str:
    """Return a human-readable summary of a RedactResult."""
    lines: List[str] = []
    if result.keys_redacted:
        lines.append(f"Redacted ({len(result.keys_redacted)}):")
        for k in result.keys_redacted:
            if show_placeholder and k in result.redacted:
                lines.append(f"  {k} = {result.redacted[k]}")
            else:
                lines.append(f"  {k}")
    else:
        lines.append("No keys redacted.")
    return "\n".join(lines)
