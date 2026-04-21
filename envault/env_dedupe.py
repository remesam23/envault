"""Detect and remove duplicate values across keys in a profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DedupeError(Exception):
    pass


@dataclass
class DedupeResult:
    duplicates: Dict[str, List[str]]  # value -> list of keys sharing it
    removed: List[str]                # keys that were dropped
    profile: Dict[str, str]           # resulting profile after deduplication
    ok: bool = True


def ok(result: DedupeResult) -> bool:
    return result.ok


def find_duplicates(profile: Dict[str, str]) -> Dict[str, List[str]]:
    """Return a mapping of value -> [keys] for values that appear more than once."""
    value_map: Dict[str, List[str]] = {}
    for key, val in profile.items():
        value_map.setdefault(val, []).append(key)
    return {val: keys for val, keys in value_map.items() if len(keys) > 1}


def dedupe_profile(
    profile: Dict[str, str],
    keep: str = "first",
    ignore_empty: bool = True,
) -> DedupeResult:
    """Remove keys with duplicate values, keeping one representative per value.

    Args:
        profile: The env key/value mapping.
        keep: Which key to keep when duplicates found — 'first' or 'last'.
        ignore_empty: If True, empty-string values are not considered duplicates.
    """
    if keep not in ("first", "last"):
        raise DedupeError(f"Invalid keep strategy '{keep}': must be 'first' or 'last'.")

    duplicates = find_duplicates(profile)
    if ignore_empty:
        duplicates = {v: ks for v, ks in duplicates.items() if v != ""}

    removed: List[str] = []
    keys_to_remove: set = set()

    for val, keys in duplicates.items():
        ordered = list(keys)  # dict preserves insertion order (Python 3.7+)
        if keep == "first":
            keys_to_remove.update(ordered[1:])
            removed.extend(ordered[1:])
        else:
            keys_to_remove.update(ordered[:-1])
            removed.extend(ordered[:-1])

    new_profile = {k: v for k, v in profile.items() if k not in keys_to_remove}
    return DedupeResult(duplicates=duplicates, removed=removed, profile=new_profile)


def format_dedupe(result: DedupeResult) -> str:
    lines: List[str] = []
    if not result.duplicates:
        lines.append("No duplicate values found.")
        return "\n".join(lines)
    lines.append(f"Found {len(result.duplicates)} duplicate value(s):")
    for val, keys in result.duplicates.items():
        display_val = repr(val) if val else "(empty)"
        lines.append(f"  {display_val}: {', '.join(keys)}")
    if result.removed:
        lines.append(f"Removed {len(result.removed)} key(s): {', '.join(result.removed)}")
    return "\n".join(lines)
