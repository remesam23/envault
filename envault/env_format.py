"""env_format.py — Format profile values using named formatters."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class FormatError(Exception):
    pass


@dataclass
class FormatResult:
    updated: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


_FORMATTERS = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
    "strip": str.strip,
    "lstrip": str.lstrip,
    "rstrip": str.rstrip,
    "reverse": lambda v: v[::-1],
    "quote": lambda v: f'"{v}"',
    "unquote": lambda v: v.strip('"\"'),
    "base64": lambda v: __import__("base64").b64encode(v.encode()).decode(),
}


def list_formatters() -> List[str]:
    """Return names of all available formatters."""
    return sorted(_FORMATTERS.keys())


def format_profile(
    data: Dict[str, str],
    formatter: str,
    keys: Optional[List[str]] = None,
) -> FormatResult:
    """Apply *formatter* to *keys* in *data* (all keys if *keys* is None)."""
    if formatter not in _FORMATTERS:
        raise FormatError(
            f"Unknown formatter '{formatter}'. "
            f"Available: {', '.join(list_formatters())}"
        )
    fn = _FORMATTERS[formatter]
    targets = keys if keys is not None else list(data.keys())
    result = FormatResult()
    updated = dict(data)
    for k in targets:
        if k not in data:
            result.skipped.append(k)
            continue
        try:
            updated[k] = fn(data[k])
            result.updated[k] = updated[k]
        except Exception as exc:  # pragma: no cover
            result.errors.append(f"{k}: {exc}")
    return result


def format_format_result(result: FormatResult, formatter: str) -> str:
    lines = [f"Formatter : {formatter}"]
    if result.updated:
        lines.append(f"Updated   : {', '.join(sorted(result.updated))}")
    if result.skipped:
        lines.append(f"Skipped   : {', '.join(sorted(result.skipped))}")
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  {e}")
    return "\n".join(lines)
