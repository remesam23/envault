"""Lint profiles for common .env issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
import re


@dataclass
class LintIssue:
    key: str
    code: str
    message: str


@dataclass
class LintResult:
    profile: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0


_UPPER_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_EMPTY_RE = re.compile(r'^\s*$')


def lint_profile(profile: str, env: Dict[str, str]) -> LintResult:
    result = LintResult(profile=profile)
    for key, value in env.items():
        if not _UPPER_RE.match(key):
            result.issues.append(LintIssue(
                key=key,
                code='E001',
                message=f"Key '{key}' should be UPPER_SNAKE_CASE"
            ))
        if _EMPTY_RE.match(value):
            result.issues.append(LintIssue(
                key=key,
                code='W001',
                message=f"Key '{key}' has an empty or blank value"
            ))
        if value.startswith(' ') or value.endswith(' '):
            result.issues.append(LintIssue(
                key=key,
                code='W002',
                message=f"Key '{key}' value has leading/trailing whitespace"
            ))
    return result


def format_lint(result: LintResult) -> str:
    if result.ok:
        return f"[{result.profile}] No issues found."
    lines = [f"[{result.profile}] {len(result.issues)} issue(s):"]
    for issue in result.issues:
        lines.append(f"  {issue.code}  {issue.message}")
    return "\n".join(lines)
