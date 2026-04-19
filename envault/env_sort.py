"""Sort keys in a profile alphabetically or by custom order."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


class SortError(Exception):
    pass


@dataclass
class SortResult:
    profile: str
    original_order: list[str]
    sorted_order: list[str]
    changed: bool

    @staticmethod
    def ok(profile: str, original: list[str], sorted_keys: list[str]) -> "SortResult":
        return SortResult(
            profile=profile,
            original_order=original,
            sorted_order=sorted_keys,
            changed=original != sorted_keys,
        )


def sort_profile(
    data: dict[str, str],
    profile: str,
    reverse: bool = False,
    group_prefix: Optional[str] = None,
) -> tuple[dict[str, str], SortResult]:
    """Return a new dict with keys sorted. Optionally group keys sharing a prefix first."""
    original_order = list(data.keys())

    if group_prefix:
        primary = sorted(
            [k for k in data if k.startswith(group_prefix)], reverse=reverse
        )
        secondary = sorted(
            [k for k in data if not k.startswith(group_prefix)], reverse=reverse
        )
        sorted_keys = primary + secondary
    else:
        sorted_keys = sorted(data.keys(), reverse=reverse)

    sorted_data = {k: data[k] for k in sorted_keys}
    result = SortResult.ok(profile, original_order, sorted_keys)
    return sorted_data, result


def format_sort_result(result: SortResult) -> str:
    lines = [f"Profile: {result.profile}"]
    if not result.changed:
        lines.append("  Already sorted — no changes made.")
    else:
        lines.append(f"  Sorted {len(result.sorted_order)} keys.")
        for key in result.sorted_order:
            lines.append(f"    {key}")
    return "\n".join(lines)
