"""Auto-fix common lint issues in a profile."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.lint import lint_profile, LintIssue


class LintFixError(Exception):
    pass


@dataclass
class FixResult:
    fixed: Dict[str, str]
    applied_fixes: List[str]
    skipped_issues: List[LintIssue]
    ok: bool


def ok(result: FixResult) -> bool:
    return result.ok


def fix_profile(
    data: Dict[str, str],
    *,
    fix_case: bool = True,
    strip_values: bool = True,
    remove_empty: bool = False,
) -> FixResult:
    """Apply automatic fixes to a profile dict."""
    result: Dict[str, str] = {}
    applied: List[str] = []
    lint = lint_profile(data)
    skipped: List[LintIssue] = []

    for raw_key, raw_val in data.items():
        key = raw_key
        val = raw_val

        if fix_case and not key.isupper():
            key = key.upper()
            applied.append(f"E001: renamed '{raw_key}' -> '{key}'")

        if strip_values and val != val.strip():
            val = val.strip()
            applied.append(f"W002: stripped whitespace from '{key}'")

        if remove_empty and val == "":
            applied.append(f"W001: removed empty key '{key}'")
            continue

        result[key] = val

    for issue in lint.issues:
        if issue.code not in ("E001", "W001", "W002"):
            skipped.append(issue)

    success = len(skipped) == 0
    return FixResult(fixed=result, applied_fixes=applied, skipped_issues=skipped, ok=success)


def format_fix_result(result: FixResult) -> str:
    lines: List[str] = []
    if result.applied_fixes:
        lines.append("Applied fixes:")
        for f in result.applied_fixes:
            lines.append(f"  [fixed] {f}")
    else:
        lines.append("No fixes applied.")
    if result.skipped_issues:
        lines.append("Remaining issues (manual fix required):")
        for issue in result.skipped_issues:
            lines.append(f"  [{issue.code}] {issue.key}: {issue.message}")
    return "\n".join(lines)
