"""env_pivot.py — Pivot profile keys into a structured view grouped by prefix."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class PivotError(Exception):
    pass


@dataclass
class PivotResult:
    groups: Dict[str, Dict[str, str]]
    ungrouped: Dict[str, str]
    ok: bool = True
    error: Optional[str] = None


def ok(groups: Dict[str, Dict[str, str]], ungrouped: Dict[str, str]) -> PivotResult:
    return PivotResult(groups=groups, ungrouped=ungrouped)


def pivot_by_prefix(
    profile: Dict[str, str],
    delimiter: str = "_",
    min_group_size: int = 1,
) -> PivotResult:
    """Group keys by their prefix (part before the first delimiter).

    Keys with a unique prefix (below min_group_size) end up in 'ungrouped'.

    Args:
        profile: A flat dictionary of environment variable key-value pairs.
        delimiter: The character used to split keys into prefix and remainder.
            Defaults to ``"_"``.
        min_group_size: Minimum number of keys required for a prefix to form
            its own group.  Prefixes with fewer keys are placed in
            ``ungrouped``.  Defaults to ``1``.

    Returns:
        A :class:`PivotResult` containing grouped and ungrouped keys.
    """
    if not profile:
        return ok(groups={}, ungrouped={})

    buckets: Dict[str, Dict[str, str]] = {}
    for key, value in profile.items():
        if delimiter in key:
            prefix, _ = key.split(delimiter, 1)
        else:
            prefix = ""
        buckets.setdefault(prefix, {})[key] = value

    groups: Dict[str, Dict[str, str]] = {}
    ungrouped: Dict[str, str] = {}

    for prefix, keys in buckets.items():
        if prefix == "" or len(keys) < min_group_size:
            ungrouped.update(keys)
        else:
            groups[prefix] = keys

    return ok(groups=groups, ungrouped=ungrouped)


def format_pivot(result: PivotResult) -> str:
    """Return a human-readable representation of a PivotResult."""
    lines: List[str] = []
    for prefix in sorted(result.groups):
        lines.append(f"[{prefix}]")
        for key in sorted(result.groups[prefix]):
            lines.append(f"  {key} = {result.groups[prefix][key]}")
    if result.ungrouped:
        lines.append("[ungrouped]")
        for key in sorted(result.ungrouped):
            lines.append(f"  {key} = {result.ungrouped[key]}")
    return "\n".join(lines)
