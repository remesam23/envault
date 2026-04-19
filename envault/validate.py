"""Validate profile keys/values against simple rules."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class ValidationError:
    key: str
    message: str


@dataclass
class ProfileValidationResult:
    profile: str
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def validate_profile(
    profile: str,
    data: Dict[str, str],
    required_keys: Optional[List[str]] = None,
    key_pattern: Optional[str] = None,
    value_min_length: int = 0,
) -> ProfileValidationResult:
    """Run validation rules against a profile's key/value pairs."""
    result = ProfileValidationResult(profile=profile)

    required_keys = required_keys or []
    for rk in required_keys:
        if rk not in data:
            result.errors.append(ValidationError(key=rk, message=f"Required key '{rk}' is missing"))

    compiled = re.compile(key_pattern) if key_pattern else None
    for k, v in data.items():
        if compiled and not compiled.fullmatch(k):
            result.errors.append(ValidationError(key=k, message=f"Key '{k}' does not match pattern '{key_pattern}'"))
        if len(v) < value_min_length:
            result.errors.append(
                ValidationError(key=k, message=f"Value for '{k}' is shorter than minimum length {value_min_length}")
            )

    return result


def format_validation(result: ProfileValidationResult) -> str:
    if result.ok:
        return f"[{result.profile}] OK — no validation errors."
    lines = [f"[{result.profile}] {len(result.errors)} error(s):"]
    for e in result.errors:
        lines.append(f"  - {e.key}: {e.message}")
    return "\n".join(lines)
