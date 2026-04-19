"""Filter profile keys by pattern, prefix, or custom predicate."""
from __future__ import annotations
import fnmatch
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


class FilterError(Exception):
    pass


@dataclass
class FilterResult:
    matched: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.matched) > 0


def filter_by_prefix(data: Dict[str, str], prefix: str) -> FilterResult:
    """Return keys that start with the given prefix."""
    matched = {k: v for k, v in data.items() if k.startswith(prefix)}
    skipped = [k for k in data if k not in matched]
    return FilterResult(matched=matched, skipped=skipped)


def filter_by_pattern(data: Dict[str, str], pattern: str) -> FilterResult:
    """Return keys matching a glob pattern (e.g. 'DB_*')."""
    matched = {k: v for k, v in data.items() if fnmatch.fnmatch(k, pattern)}
    skipped = [k for k in data if k not in matched]
    return FilterResult(matched=matched, skipped=skipped)


def filter_by_predicate(
    data: Dict[str, str],
    predicate: Callable[[str, str], bool],
) -> FilterResult:
    """Return keys/values for which predicate(key, value) is True."""
    matched = {k: v for k, v in data.items() if predicate(k, v)}
    skipped = [k for k in data if k not in matched]
    return FilterResult(matched=matched, skipped=skipped)


def format_filter_result(result: FilterResult, profile: str) -> str:
    lines = [f"Filter results for profile '{profile}':",
             f"  Matched : {len(result.matched)}",
             f"  Skipped : {len(result.skipped)}"]
    if result.matched:
        lines.append("  Keys    : " + ", ".join(sorted(result.matched)))
    return "\n".join(lines)
