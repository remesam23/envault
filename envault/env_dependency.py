"""env_dependency.py — Track and resolve key dependencies within a profile.

Allows declaring that a key 'depends on' other keys being present,
and validates or resolves those dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


class DependencyError(Exception):
    """Raised when a dependency operation fails."""


@dataclass
class DependencyViolation:
    key: str
    missing_deps: List[str]

    def __str__(self) -> str:
        deps = ", ".join(self.missing_deps)
        return f"'{self.key}' requires missing keys: {deps}"


@dataclass
class DependencyResult:
    satisfied: List[str]  # keys whose dependencies are all present
    violations: List[DependencyViolation]  # keys with unmet dependencies
    skipped: List[str]  # keys not covered by any rule

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0


def ok(satisfied: List[str], skipped: List[str]) -> DependencyResult:
    """Convenience constructor for a passing result."""
    return DependencyResult(satisfied=satisfied, violations=[], skipped=skipped)


def check_dependencies(
    profile: Dict[str, str],
    rules: Dict[str, List[str]],
) -> DependencyResult:
    """Check that each key's declared dependencies exist in the profile.

    Args:
        profile: The env key/value mapping to validate.
        rules: A dict mapping key -> list of keys it depends on.
               Example: {"DB_URL": ["DB_HOST", "DB_PORT"]}

    Returns:
        DependencyResult with satisfied keys, violations, and uncovered keys.
    """
    present: Set[str] = set(profile.keys())
    covered: Set[str] = set(rules.keys())

    satisfied: List[str] = []
    violations: List[DependencyViolation] = []

    for key, deps in rules.items():
        missing = [d for d in deps if d not in present]
        if missing:
            violations.append(DependencyViolation(key=key, missing_deps=missing))
        else:
            satisfied.append(key)

    skipped = sorted(present - covered)
    return DependencyResult(satisfied=sorted(satisfied), violations=violations, skipped=skipped)


def resolve_order(
    rules: Dict[str, List[str]],
) -> List[str]:
    """Return a topological sort of keys based on dependency rules.

    Raises DependencyError if a cycle is detected.

    Args:
        rules: A dict mapping key -> list of keys it depends on.

    Returns:
        Ordered list of keys from least dependent to most dependent.
    """
    # Build full node set
    all_keys: Set[str] = set(rules.keys())
    for deps in rules.values():
        all_keys.update(deps)

    # Kahn's algorithm
    in_degree: Dict[str, int] = {k: 0 for k in all_keys}
    graph: Dict[str, List[str]] = {k: [] for k in all_keys}

    for key, deps in rules.items():
        for dep in deps:
            graph[dep].append(key)
            in_degree[key] += 1

    queue = sorted(k for k, deg in in_degree.items() if deg == 0)
    order: List[str] = []

    while queue:
        node = queue.pop(0)
        order.append(node)
        for neighbor in sorted(graph[node]):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(all_keys):
        raise DependencyError(
            "Cycle detected in dependency rules; cannot determine resolution order."
        )

    return order


def format_dependency_result(result: DependencyResult) -> str:
    """Render a DependencyResult as a human-readable string."""
    lines: List[str] = []

    if result.satisfied:
        lines.append("Satisfied:")
        for k in result.satisfied:
            lines.append(f"  ✓ {k}")

    if result.violations:
        lines.append("Violations:")
        for v in result.violations:
            lines.append(f"  ✗ {v}")

    if result.skipped:
        lines.append(f"Skipped (no rules): {', '.join(result.skipped)}")

    if not lines:
        return "No dependency rules defined."

    status = "OK" if result.ok else "FAILED"
    lines.insert(0, f"Dependency check: {status}")
    return "\n".join(lines)
