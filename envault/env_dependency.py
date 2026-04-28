"""Dependency checking between env keys.

Allows defining rules like:
  - key A requires key B to also be present
  - key A conflicts with key B (both cannot be set)
  - key A requires key B to have a specific value
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


class DependencyError(Exception):
    """Raised for invalid dependency rule definitions."""


@dataclass
class DependencyViolation:
    rule_type: str  # 'requires', 'conflicts', 'requires_value'
    key: str
    dependency: str
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass
class DependencyResult:
    violations: List[DependencyViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        if self.ok:
            return "All dependency rules satisfied."
        lines = [f"{len(self.violations)} violation(s) found:"]
        for v in self.violations:
            lines.append(f"  [{v.rule_type}] {v.message}")
        return "\n".join(lines)


@dataclass
class DependencyRules:
    """Container for all dependency rules for a profile."""

    # key -> list of keys that must also be present
    requires: Dict[str, List[str]] = field(default_factory=dict)

    # key -> list of keys that must NOT also be present
    conflicts: Dict[str, List[str]] = field(default_factory=dict)

    # (key, dependency_key) -> required value for dependency_key
    requires_value: List[Tuple[str, str, str]] = field(default_factory=list)


def check_dependencies(
    profile: Dict[str, str],
    rules: DependencyRules,
) -> DependencyResult:
    """Check a profile dict against a set of dependency rules.

    Args:
        profile: Mapping of env key -> value.
        rules: DependencyRules instance describing constraints.

    Returns:
        DependencyResult with any violations found.
    """
    violations: List[DependencyViolation] = []

    # Check 'requires' rules
    for key, deps in rules.requires.items():
        if key not in profile:
            continue
        for dep in deps:
            if dep not in profile:
                violations.append(
                    DependencyViolation(
                        rule_type="requires",
                        key=key,
                        dependency=dep,
                        message=f"'{key}' requires '{dep}' to be present, but it is missing.",
                    )
                )

    # Check 'conflicts' rules (only report once per pair)
    seen_conflicts: set = set()
    for key, conflicting in rules.conflicts.items():
        if key not in profile:
            continue
        for other in conflicting:
            if other not in profile:
                continue
            pair = tuple(sorted([key, other]))
            if pair in seen_conflicts:
                continue
            seen_conflicts.add(pair)
            violations.append(
                DependencyViolation(
                    rule_type="conflicts",
                    key=key,
                    dependency=other,
                    message=f"'{key}' conflicts with '{other}': both are set.",
                )
            )

    # Check 'requires_value' rules
    for key, dep_key, required_val in rules.requires_value:
        if key not in profile:
            continue
        if dep_key not in profile:
            violations.append(
                DependencyViolation(
                    rule_type="requires_value",
                    key=key,
                    dependency=dep_key,
                    message=(
                        f"'{key}' requires '{dep_key}' to be present "
                        f"with value '{required_val}', but '{dep_key}' is missing."
                    ),
                )
            )
        elif profile[dep_key] != required_val:
            violations.append(
                DependencyViolation(
                    rule_type="requires_value",
                    key=key,
                    dependency=dep_key,
                    message=(
                        f"'{key}' requires '{dep_key}' = '{required_val}', "
                        f"but got '{profile[dep_key]}'."
                    ),
                )
            )

    return DependencyResult(violations=violations)


def rules_from_dict(raw: dict) -> DependencyRules:
    """Build a DependencyRules object from a plain dict (e.g. loaded from JSON/YAML).

    Expected format::

        {
          "requires": {"DATABASE_URL": ["DATABASE_NAME"]},
          "conflicts": {"DEBUG": ["PRODUCTION"]},
          "requires_value": [["USE_SSL", "SSL_MODE", "verify-full"]]
        }
    """
    requires = raw.get("requires", {})
    conflicts = raw.get("conflicts", {})
    requires_value_raw = raw.get("requires_value", [])

    if not isinstance(requires, dict):
        raise DependencyError("'requires' must be a dict mapping key -> list of keys")
    if not isinstance(conflicts, dict):
        raise DependencyError("'conflicts' must be a dict mapping key -> list of keys")
    if not isinstance(requires_value_raw, list):
        raise DependencyError("'requires_value' must be a list of [key, dep_key, value] triples")

    requires_value: List[Tuple[str, str, str]] = []
    for item in requires_value_raw:
        if not (isinstance(item, (list, tuple)) and len(item) == 3):
            raise DependencyError(
                f"Each 'requires_value' entry must be [key, dep_key, value], got: {item!r}"
            )
        requires_value.append((str(item[0]), str(item[1]), str(item[2])))

    return DependencyRules(
        requires={k: list(v) for k, v in requires.items()},
        conflicts={k: list(v) for k, v in conflicts.items()},
        requires_value=requires_value,
    )
