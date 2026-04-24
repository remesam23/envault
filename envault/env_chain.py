"""env_chain.py — resolve a profile by layering multiple profiles in order.

Later profiles in the chain override earlier ones (last-wins semantics).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class ChainError(Exception):
    """Raised when a chain operation cannot be completed."""


@dataclass
class ChainResult:
    merged: Dict[str, str]
    sources: Dict[str, str]  # key -> profile name that provided the final value
    chain: List[str]         # ordered list of profile names used
    ok: bool = True
    error: Optional[str] = None


def ok(merged: Dict[str, str], sources: Dict[str, str], chain: List[str]) -> ChainResult:
    return ChainResult(merged=merged, sources=sources, chain=chain, ok=True)


def resolve_chain(
    profiles: Dict[str, Dict[str, str]],
    chain: List[str],
) -> ChainResult:
    """Merge profiles in *chain* order; later entries override earlier ones.

    Args:
        profiles: mapping of profile_name -> {key: value} dicts (already decrypted).
        chain:    ordered list of profile names to layer.

    Returns:
        ChainResult with the merged env dict and per-key provenance.
    """
    if not chain:
        raise ChainError("Chain must contain at least one profile name.")

    missing = [name for name in chain if name not in profiles]
    if missing:
        raise ChainError(f"Profiles not found: {', '.join(missing)}")

    merged: Dict[str, str] = {}
    sources: Dict[str, str] = {}

    for profile_name in chain:
        for key, value in profiles[profile_name].items():
            merged[key] = value
            sources[key] = profile_name

    return ok(merged, sources, list(chain))


def format_chain_result(result: ChainResult) -> str:
    """Return a human-readable summary of the chain resolution."""
    lines: List[str] = [
        f"Chain: {' -> '.join(result.chain)}",
        f"Total keys: {len(result.merged)}",
        "",
    ]
    for key in sorted(result.merged):
        lines.append(f"  {key}={result.merged[key]}  (from: {result.sources[key]})")
    return "\n".join(lines)
