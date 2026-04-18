"""Merge two vault profiles with configurable conflict resolution."""

from typing import Dict, Literal

ConflictStrategy = Literal["ours", "theirs", "error"]


class MergeConflictError(Exception):
    """Raised when conflicting keys exist and strategy is 'error'."""

    def __init__(self, conflicts: list[str]):
        self.conflicts = conflicts
        super().__init__(f"Merge conflicts on keys: {', '.join(conflicts)}")


def merge_profiles(
    base: Dict[str, str],
    incoming: Dict[str, str],
    strategy: ConflictStrategy = "ours",
) -> Dict[str, str]:
    """Merge *incoming* into *base* and return the merged dict.

    Parameters
    ----------
    base:     The existing profile variables ("ours").
    incoming: The profile being merged in ("theirs").
    strategy: How to resolve key conflicts:
              - 'ours'   – keep base value (default)
              - 'theirs' – use incoming value
              - 'error'  – raise MergeConflictError listing conflicting keys
    """
    conflicts = [
        key
        for key in incoming
        if key in base and base[key] != incoming[key]
    ]

    if strategy == "error" and conflicts:
        raise MergeConflictError(conflicts)

    merged = dict(base)
    for key, value in incoming.items():
        if key not in merged:
            merged[key] = value
        elif strategy == "theirs":
            merged[key] = value
        # strategy == 'ours': keep existing value (no-op)

    return merged


def merge_summary(
    base: Dict[str, str],
    incoming: Dict[str, str],
    merged: Dict[str, str],
) -> Dict[str, list[str]]:
    """Return a summary dict with keys 'added', 'overwritten', 'skipped'."""
    added = [k for k in incoming if k not in base]
    overwritten = [
        k for k in incoming if k in base and merged[k] == incoming[k] and base[k] != incoming[k]
    ]
    skipped = [
        k for k in incoming if k in base and merged[k] == base[k] and base[k] != incoming[k]
    ]
    return {"added": added, "overwritten": overwritten, "skipped": skipped}
