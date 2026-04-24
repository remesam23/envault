"""Reorder keys in a profile according to a specified key order list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ReorderError(Exception):
    pass


@dataclass
class ReorderResult:
    reordered: Dict[str, str]
    moved: List[str]
    unchanged: List[str]
    appended: List[str]  # keys not in order list, appended at end
    ok: bool = True
    error: Optional[str] = None


def ok(result: ReorderResult) -> bool:
    return result.ok


def reorder_profile(
    profile: Dict[str, str],
    key_order: List[str],
    append_remaining: bool = True,
) -> ReorderResult:
    """Reorder profile keys according to key_order.

    Keys in key_order appear first (in that order), remaining keys are
    appended alphabetically if append_remaining is True, else dropped.
    """
    if not isinstance(profile, dict):
        raise ReorderError("profile must be a dict")
    if not isinstance(key_order, list):
        raise ReorderError("key_order must be a list")

    reordered: Dict[str, str] = {}
    moved: List[str] = []
    unchanged: List[str] = []
    appended: List[str] = []

    original_keys = list(profile.keys())

    for key in key_order:
        if key in profile:
            reordered[key] = profile[key]
            if original_keys.index(key) != len(reordered) - 1:
                moved.append(key)
            else:
                unchanged.append(key)

    remaining = [k for k in original_keys if k not in reordered]

    if append_remaining:
        for key in sorted(remaining):
            reordered[key] = profile[key]
            appended.append(key)

    return ReorderResult(
        reordered=reordered,
        moved=moved,
        unchanged=unchanged,
        appended=appended,
    )


def format_reorder_result(result: ReorderResult) -> str:
    lines = []
    if result.moved:
        lines.append(f"Moved:     {', '.join(result.moved)}")
    if result.appended:
        lines.append(f"Appended:  {', '.join(result.appended)}")
    if not result.moved and not result.appended:
        lines.append("No changes to key order.")
    return "\n".join(lines)
