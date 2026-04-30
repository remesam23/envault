"""env_resolve.py – resolve a profile's values through a chain of lookups.

Supports resolving ${KEY} references within the same profile, falling back
to a provided defaults dict, and reporting which keys remain unresolved.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_REF_RE = re.compile(r"\$\{([^}]+)\}")


class ResolveError(Exception):
    pass


@dataclass
class ResolveResult:
    resolved: Dict[str, str]
    substitutions: Dict[str, List[str]]  # key -> list of ref-names substituted
    unresolved: Dict[str, List[str]]     # key -> list of ref-names still missing
    ok: bool


def ok(result: ResolveResult) -> bool:
    return result.ok


def resolve_profile(
    profile: Dict[str, str],
    defaults: Optional[Dict[str, str]] = None,
    strict: bool = False,
) -> ResolveResult:
    """Resolve ${REF} placeholders inside *profile* values.

    Resolution order: profile itself, then *defaults*.
    If *strict* is True and any placeholder remains unresolved, raise ResolveError.
    """
    defaults = defaults or {}
    resolved: Dict[str, str] = {}
    substitutions: Dict[str, List[str]] = {}
    unresolved: Dict[str, List[str]] = {}

    lookup = {**defaults, **profile}  # profile wins over defaults

    for key, value in profile.items():
        refs = _REF_RE.findall(value)
        if not refs:
            resolved[key] = value
            continue

        new_value = value
        subs: List[str] = []
        missing: List[str] = []

        for ref in refs:
            if ref in lookup:
                new_value = new_value.replace(f"${{{ref}}}", lookup[ref])
                subs.append(ref)
            else:
                missing.append(ref)

        resolved[key] = new_value
        if subs:
            substitutions[key] = subs
        if missing:
            unresolved[key] = missing

    if strict and unresolved:
        flat = ", ".join(f"{k}: {v}" for k, v in unresolved.items())
        raise ResolveError(f"Unresolved references: {flat}")

    return ResolveResult(
        resolved=resolved,
        substitutions=substitutions,
        unresolved=unresolved,
        ok=not bool(unresolved),
    )


def format_resolve_result(result: ResolveResult) -> str:
    lines: List[str] = []
    if result.substitutions:
        lines.append("Substitutions:")
        for k, refs in sorted(result.substitutions.items()):
            lines.append(f"  {k}: resolved {refs}")
    if result.unresolved:
        lines.append("Unresolved:")
        for k, refs in sorted(result.unresolved.items()):
            lines.append(f"  {k}: missing {refs}")
    if not lines:
        lines.append("All values resolved (no placeholders found).")
    return "\n".join(lines)
