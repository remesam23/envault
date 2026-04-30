"""env_ref.py — cross-profile key reference resolution.

Allows a profile to reference a value from another profile using
the syntax: ${ref:other_profile:KEY}
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

REF_PATTERN = re.compile(r"\$\{ref:([^:}]+):([^}]+)\}")


class RefError(Exception):
    pass


@dataclass
class RefResult:
    resolved: Dict[str, str]
    substitutions: List[Tuple[str, str, str, str]]  # (key, src_profile, src_key, value)
    unresolved: List[Tuple[str, str, str]]           # (key, src_profile, src_key)
    ok: bool


def ok(result: RefResult) -> bool:
    return result.ok


Loader = Callable[[str], Dict[str, str]]


def resolve_refs(
    profile: Dict[str, str],
    loader: Loader,
    strict: bool = False,
) -> RefResult:
    """Resolve ${ref:profile:KEY} placeholders in *profile* values.

    Args:
        profile: The env dict whose values may contain ref placeholders.
        loader:  Callable that accepts a profile name and returns its env dict.
        strict:  If True, raise RefError on any unresolved reference.

    Returns:
        RefResult with the resolved copy of the profile and metadata.
    """
    resolved: Dict[str, str] = {}
    substitutions: List[Tuple[str, str, str, str]] = []
    unresolved: List[Tuple[str, str, str]] = []

    for key, value in profile.items():
        match = REF_PATTERN.search(value)
        if match is None:
            resolved[key] = value
            continue

        src_profile_name = match.group(1)
        src_key = match.group(2)

        try:
            src_data = loader(src_profile_name)
        except Exception as exc:
            if strict:
                raise RefError(
                    f"Cannot load profile '{src_profile_name}' for key '{key}': {exc}"
                ) from exc
            unresolved.append((key, src_profile_name, src_key))
            resolved[key] = value
            continue

        if src_key not in src_data:
            if strict:
                raise RefError(
                    f"Key '{src_key}' not found in profile '{src_profile_name}' "
                    f"(referenced by '{key}')"
                )
            unresolved.append((key, src_profile_name, src_key))
            resolved[key] = value
            continue

        replacement = src_data[src_key]
        new_value = REF_PATTERN.sub(replacement, value, count=1)
        resolved[key] = new_value
        substitutions.append((key, src_profile_name, src_key, replacement))

    return RefResult(
        resolved=resolved,
        substitutions=substitutions,
        unresolved=unresolved,
        ok=len(unresolved) == 0,
    )


def format_ref_result(result: RefResult) -> str:
    lines: List[str] = []
    if result.substitutions:
        lines.append("Resolved references:")
        for key, src_prof, src_key, val in result.substitutions:
            lines.append(f"  {key} <- {src_prof}:{src_key} = {val}")
    if result.unresolved:
        lines.append("Unresolved references:")
        for key, src_prof, src_key in result.unresolved:
            lines.append(f"  {key} -> {src_prof}:{src_key} (not found)")
    if not lines:
        lines.append("No references found.")
    return "\n".join(lines)
