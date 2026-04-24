"""Profile inheritance: resolve a profile by layering parent profiles."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class InheritError(Exception):
    pass


@dataclass
class InheritResult:
    resolved: Dict[str, str]
    chain: List[str]          # ordered list of profiles used, base-first
    sources: Dict[str, str]   # key -> profile that provided the final value
    ok: bool = True
    error: str = ""


def ok(resolved: Dict[str, str], chain: List[str], sources: Dict[str, str]) -> InheritResult:
    return InheritResult(resolved=resolved, chain=chain, sources=sources)


def resolve_inheritance(
    profile: str,
    parents: List[str],
    loader,  # callable(profile_name) -> Dict[str, str]
    *,
    max_depth: int = 10,
) -> InheritResult:
    """Resolve *profile* by merging parent profiles in order then overlaying
    the child.  Earlier parents act as base; later parents override them;
    the child profile overrides everything.

    Args:
        profile:   Name of the child profile.
        parents:   Ordered list of parent profile names (base first).
        loader:    Callable that accepts a profile name and returns its key/value dict.
        max_depth: Guard against excessively deep chains.
    """
    if len(parents) >= max_depth:
        raise InheritError(
            f"Inheritance chain too deep (limit {max_depth}): {parents}"
        )

    merged: Dict[str, str] = {}
    sources: Dict[str, str] = {}
    chain: List[str] = []

    for parent in parents:
        try:
            data = loader(parent)
        except Exception as exc:
            raise InheritError(f"Failed to load parent profile '{parent}': {exc}") from exc
        chain.append(parent)
        for k, v in data.items():
            merged[k] = v
            sources[k] = parent

    # overlay child
    try:
        child_data = loader(profile)
    except Exception as exc:
        raise InheritError(f"Failed to load profile '{profile}': {exc}") from exc

    chain.append(profile)
    for k, v in child_data.items():
        merged[k] = v
        sources[k] = profile

    return ok(merged, chain, sources)


def format_inherit_result(result: InheritResult) -> str:
    lines = [f"Chain: {' -> '.join(result.chain)}", ""]
    for k, v in sorted(result.resolved.items()):
        lines.append(f"  {k}={v}  (from: {result.sources[k]})")
    return "\n".join(lines)
