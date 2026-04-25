"""Cross-reference analysis: find keys shared across profiles and detect inconsistencies."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


class CrossRefError(Exception):
    pass


@dataclass
class CrossRefResult:
    common_keys: Set[str]          # keys present in ALL profiles
    partial_keys: Dict[str, List[str]]  # key -> list of profiles that have it (not all)
    value_conflicts: Dict[str, Dict[str, str]]  # key -> {profile: value} for differing values
    profiles_checked: List[str]
    ok: bool = True


def empty_result(profiles: List[str]) -> CrossRefResult:
    return CrossRefResult(
        common_keys=set(),
        partial_keys={},
        value_conflicts={},
        profiles_checked=profiles,
    )


def crossref_profiles(profiles: Dict[str, Dict[str, str]]) -> CrossRefResult:
    """Analyse key overlap and value consistency across multiple profiles."""
    if not profiles:
        return empty_result([])

    names = list(profiles.keys())
    all_keys: Set[str] = set()
    for data in profiles.values():
        all_keys.update(data.keys())

    common_keys: Set[str] = set(all_keys)
    partial_keys: Dict[str, List[str]] = {}
    value_conflicts: Dict[str, Dict[str, str]] = {}

    for key in all_keys:
        owners = [name for name, data in profiles.items() if key in data]
        if len(owners) == len(names):
            # Key is in every profile — check value consistency
            values = {name: profiles[name][key] for name in names}
            unique_vals = set(values.values())
            if len(unique_vals) > 1:
                value_conflicts[key] = values
        else:
            common_keys.discard(key)
            partial_keys[key] = owners

    return CrossRefResult(
        common_keys=common_keys,
        partial_keys=partial_keys,
        value_conflicts=value_conflicts,
        profiles_checked=names,
    )


def format_crossref(result: CrossRefResult) -> str:
    lines: List[str] = []
    lines.append(f"Profiles analysed: {', '.join(result.profiles_checked)}")
    lines.append(f"Common keys ({len(result.common_keys)}): "
                 + (', '.join(sorted(result.common_keys)) or "none"))

    if result.partial_keys:
        lines.append(f"\nPartial keys ({len(result.partial_keys)}):")
        for key, owners in sorted(result.partial_keys.items()):
            lines.append(f"  {key}: present in {', '.join(owners)}")

    if result.value_conflicts:
        lines.append(f"\nValue conflicts ({len(result.value_conflicts)}):")
        for key, vals in sorted(result.value_conflicts.items()):
            lines.append(f"  {key}:")
            for profile, val in vals.items():
                lines.append(f"    {profile} = {val}")
    else:
        lines.append("\nNo value conflicts detected.")

    return "\n".join(lines)
