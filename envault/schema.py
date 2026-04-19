"""Schema validation for env profiles."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


class SchemaError(Exception):
    pass


@dataclass
class FieldSpec:
    required: bool = True
    pattern: Optional[str] = None
    allowed: Optional[List[str]] = None
    description: str = ""


@dataclass
class ValidationIssue:
    key: str
    message: str
    level: str = "error"  # error | warning


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.level == "error" for i in self.issues)


def validate_profile(env: Dict[str, str], schema: Dict[str, FieldSpec]) -> ValidationResult:
    issues = []
    for key, spec in schema.items():
        if key not in env:
            if spec.required:
                issues.append(ValidationIssue(key, f"Required key '{key}' is missing.", "error"))
            continue
        val = env[key]
        if spec.pattern and not re.fullmatch(spec.pattern, val):
            issues.append(ValidationIssue(key, f"Value '{val}' does not match pattern '{spec.pattern}'.", "error"))
        if spec.allowed and val not in spec.allowed:
            issues.append(ValidationIssue(key, f"Value '{val}' not in allowed values: {spec.allowed}.", "error"))
    return ValidationResult(issues=issues)


def format_validation(result: ValidationResult) -> str:
    if result.ok and not result.issues:
        return "Schema validation passed."
    lines = []
    for issue in result.issues:
        tag = "[ERROR]" if issue.level == "error" else "[WARN]"
        lines.append(f"  {tag} {issue.key}: {issue.message}")
    status = "PASSED (with warnings)" if result.ok else "FAILED"
    lines.insert(0, f"Schema validation {status}:")
    return "\n".join(lines)
