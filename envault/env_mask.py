"""Mask/redact sensitive values when displaying profiles."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

DEFAULT_PATTERNS = [
    r"(?i)(password|secret|token|key|api_key|private|auth|credential)",
]

MASK_CHAR = "*"
MASK_LEN = 8


class MaskError(Exception):
    pass


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return True


def _is_sensitive(key: str, patterns: List[str]) -> bool:
    return any(re.search(p, key) for p in patterns)


def mask_profile(
    data: Dict[str, str],
    patterns: Optional[List[str]] = None,
    extra_keys: Optional[List[str]] = None,
    reveal: bool = False,
) -> MaskResult:
    """Return a copy of data with sensitive values masked."""
    if patterns is None:
        patterns = DEFAULT_PATTERNS
    extra_keys = set(extra_keys or [])
    masked: Dict[str, str] = {}
    redacted: List[str] = []
    for k, v in data.items():
        if not reveal and (k in extra_keys or _is_sensitive(k, patterns)):
            masked[k] = MASK_CHAR * MASK_LEN
            redacted.append(k)
        else:
            masked[k] = v
    return MaskResult(original=data, masked=masked, redacted_keys=redacted)


def format_mask_result(result: MaskResult) -> str:
    lines = []
    for k, v in result.masked.items():
        lines.append(f"{k}={v}")
    return "\n".join(lines)
