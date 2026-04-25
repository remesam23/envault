"""Health check module: assess overall vault profile health."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HealthIssue:
    code: str
    message: str
    severity: str  # "error" | "warning" | "info"


@dataclass
class HealthResult:
    profile: str
    issues: list[HealthIssue] = field(default_factory=list)
    total_keys: int = 0

    @property
    def healthy(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def score(self) -> int:
        """0-100 score; deduct points per issue severity."""
        deductions = {"error": 30, "warning": 10, "info": 2}
        total = sum(deductions.get(i.severity, 0) for i in self.issues)
        return max(0, 100 - total)


def ok(profile: str, total_keys: int) -> HealthResult:
    return HealthResult(profile=profile, total_keys=total_keys)


def check_health(profile: str, data: dict[str, str]) -> HealthResult:
    """Run all health checks on a profile's key-value data."""
    result = HealthResult(profile=profile, total_keys=len(data))

    if not data:
        result.issues.append(HealthIssue("H001", "Profile is empty.", "warning"))
        return result

    empty_keys = [k for k, v in data.items() if v.strip() == ""]
    for k in empty_keys:
        result.issues.append(HealthIssue("H002", f"Empty value for key '{k}'.", "warning"))

    lowercase_keys = [k for k in data if k != k.upper()]
    for k in lowercase_keys:
        result.issues.append(HealthIssue("H003", f"Non-uppercase key '{k}'.", "info"))

    values = list(data.values())
    seen: dict[str, list[str]] = {}
    for k, v in data.items():
        seen.setdefault(v, []).append(k)
    for v, keys in seen.items():
        if len(keys) > 1 and v.strip():
            result.issues.append(
                HealthIssue("H004", f"Duplicate value shared by: {', '.join(keys)}.", "info")
            )

    return result


def format_health(result: HealthResult) -> str:
    lines = [f"Health report for profile '{result.profile}':"]
    lines.append(f"  Total keys : {result.total_keys}")
    lines.append(f"  Score      : {result.score}/100")
    lines.append(f"  Status     : {'OK' if result.healthy else 'UNHEALTHY'}")
    if result.issues:
        lines.append("  Issues:")
        for issue in result.issues:
            lines.append(f"    [{issue.severity.upper()}] {issue.code}: {issue.message}")
    else:
        lines.append("  No issues found.")
    return "\n".join(lines)
