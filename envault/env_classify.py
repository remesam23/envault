"""Classify profile keys into categories based on naming conventions and value patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


class ClassifyError(Exception):
    pass


@dataclass
class ClassifyResult:
    profile: str
    categories: Dict[str, List[str]] = field(default_factory=dict)
    ok: bool = True
    message: str = ""


_CATEGORY_PATTERNS: Dict[str, re.Pattern] = {
    "secret": re.compile(
        r"(SECRET|PASSWORD|PASSWD|TOKEN|API_KEY|PRIVATE|CREDENTIAL|AUTH)",
        re.IGNORECASE,
    ),
    "url": re.compile(r"(URL|URI|ENDPOINT|HOST|HOSTNAME|DOMAIN)", re.IGNORECASE),
    "port": re.compile(r"(PORT)", re.IGNORECASE),
    "path": re.compile(r"(PATH|DIR|DIRECTORY|FOLDER|FILE)", re.IGNORECASE),
    "flag": re.compile(r"(ENABLE|DISABLE|FLAG|TOGGLE|DEBUG|VERBOSE)", re.IGNORECASE),
    "numeric": re.compile(r"(SIZE|LIMIT|MAX|MIN|COUNT|TIMEOUT|RETRY|TTL)", re.IGNORECASE),
}

_VALUE_URL_RE = re.compile(r"^https?://", re.IGNORECASE)
_VALUE_NUMERIC_RE = re.compile(r"^-?\d+(\.\d+)?$")
_VALUE_BOOL_RE = re.compile(r"^(true|false|yes|no|1|0)$", re.IGNORECASE)


def _classify_key(key: str, value: str) -> str:
    for category, pattern in _CATEGORY_PATTERNS.items():
        if pattern.search(key):
            return category
    if _VALUE_URL_RE.match(value):
        return "url"
    if _VALUE_BOOL_RE.match(value):
        return "flag"
    if _VALUE_NUMERIC_RE.match(value):
        return "numeric"
    return "general"


def classify_profile(profile: str, data: Dict[str, str]) -> ClassifyResult:
    if not isinstance(data, dict):
        raise ClassifyError(f"Profile data for '{profile}' must be a dict.")

    categories: Dict[str, List[str]] = {}
    for key, value in data.items():
        cat = _classify_key(key, value)
        categories.setdefault(cat, []).append(key)

    for cat in categories:
        categories[cat].sort()

    return ClassifyResult(profile=profile, categories=categories)


def format_classify(result: ClassifyResult) -> str:
    if not result.ok:
        return f"Error: {result.message}"
    lines = [f"Profile: {result.profile}"]
    if not result.categories:
        lines.append("  (no keys)")
    else:
        for cat, keys in sorted(result.categories.items()):
            lines.append(f"  [{cat}]")
            for k in keys:
                lines.append(f"    {k}")
    return "\n".join(lines)
