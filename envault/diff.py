"""Diff utilities for comparing vault profiles or .env files."""

from typing import Dict, List, Tuple


AddedKey = Tuple[str, str]
RemovedKey = Tuple[str, str]
ChangedKey = Tuple[str, str, str]


def diff_profiles(
    old: Dict[str, str], new: Dict[str, str]
) -> Dict[str, list]:
    """Compare two profiles and return added, removed, and changed keys.

    Returns a dict with keys:
      - 'added':   list of (key, new_value)
      - 'removed': list of (key, old_value)
      - 'changed': list of (key, old_value, new_value)
    """
    old_keys = set(old.keys())
    new_keys = set(new.keys())

    added: List[AddedKey] = [
        (k, new[k]) for k in sorted(new_keys - old_keys)
    ]
    removed: List[RemovedKey] = [
        (k, old[k]) for k in sorted(old_keys - new_keys)
    ]
    changed: List[ChangedKey] = [
        (k, old[k], new[k])
        for k in sorted(old_keys & new_keys)
        if old[k] != new[k]
    ]

    return {"added": added, "removed": removed, "changed": changed}


def format_diff(diff: Dict[str, list], mask_values: bool = True) -> str:
    """Format a diff dict into a human-readable string.

    If mask_values is True, actual values are hidden.
    """
    lines: List[str] = []

    def _val(v: str) -> str:
        return "***" if mask_values else v

    for key, val in diff["added"]:
        lines.append(f"  + {key}={_val(val)}")

    for key, val in diff["removed"]:
        lines.append(f"  - {key}={_val(val)}")

    for key, old_val, new_val in diff["changed"]:
        lines.append(f"  ~ {key}: {_val(old_val)} -> {_val(new_val)}")

    if not lines:
        return "  (no differences)"

    return "\n".join(lines)
