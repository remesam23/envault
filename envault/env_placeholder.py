"""Placeholder detection and resolution for env profiles."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

PLACEHOLDER_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


class PlaceholderError(Exception):
    pass


@dataclass
class ResolutionResult:
    resolved: Dict[str, str]
    unresolved: List[str]
    substitutions: int

    @property
    def ok(self) -> bool:
        return len(self.unresolved) == 0


def find_placeholders(value: str) -> List[str]:
    """Return all placeholder names referenced in *value*."""
    return PLACEHOLDER_RE.findall(value)


def resolve_profile(
    profile: Dict[str, str],
    *,
    strict: bool = False,
    extra: Optional[Dict[str, str]] = None,
) -> ResolutionResult:
    """Resolve ${VAR} placeholders within a profile using its own keys.

    Parameters
    ----------
    profile:  The env key/value mapping to resolve.
    strict:   If True, raise PlaceholderError on any unresolved placeholder.
    extra:    Additional key/value pairs used for resolution (e.g. OS env).
    """
    lookup: Dict[str, str] = {}
    if extra:
        lookup.update(extra)
    lookup.update(profile)

    resolved: Dict[str, str] = {}
    unresolved: List[str] = []
    substitutions = 0

    for key, value in profile.items():
        placeholders = find_placeholders(value)
        if not placeholders:
            resolved[key] = value
            continue

        def _replace(m: re.Match) -> str:  # noqa: E306
            name = m.group(1)
            if name in lookup:
                return lookup[name]
            unresolved.append(name)
            return m.group(0)

        new_value = PLACEHOLDER_RE.sub(_replace, value)
        substitutions += len(placeholders) - new_value.count("${")  # rough count
        resolved[key] = new_value

    # deduplicate unresolved list
    seen = set()
    unique_unresolved = [x for x in unresolved if not (x in seen or seen.add(x))]

    if strict and unique_unresolved:
        raise PlaceholderError(
            f"Unresolved placeholders: {', '.join(unique_unresolved)}"
        )

    return ResolutionResult(
        resolved=resolved,
        unresolved=unique_unresolved,
        substitutions=substitutions,
    )


def format_resolution(result: ResolutionResult) -> str:
    lines: List[str] = []
    lines.append(f"Substitutions made : {result.substitutions}")
    if result.unresolved:
        lines.append("Unresolved placeholders:")
        for name in result.unresolved:
            lines.append(f"  - ${{{name}}}")
    else:
        lines.append("All placeholders resolved.")
    return "\n".join(lines)
