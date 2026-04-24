"""Namespace support: prefix-based logical grouping of keys within a profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class NamespaceError(Exception):
    pass


@dataclass
class NamespaceResult:
    namespace: str
    keys: Dict[str, str] = field(default_factory=dict)
    stripped_keys: Dict[str, str] = field(default_factory=dict)
    is_ok: bool = True
    message: str = ""


def ok(result: NamespaceResult) -> bool:
    return result.is_ok


def extract_namespace(
    profile: Dict[str, str],
    namespace: str,
    strip_prefix: bool = True,
) -> NamespaceResult:
    """Extract all keys belonging to a namespace (prefix match).

    Args:
        profile: flat key/value dict.
        namespace: prefix string, e.g. "DB" matches "DB_HOST", "DB_PORT".
        strip_prefix: if True, returned stripped_keys omit the prefix.
    """
    prefix = namespace.rstrip("_") + "_"
    matched: Dict[str, str] = {}
    stripped: Dict[str, str] = {}

    for k, v in profile.items():
        if k.startswith(prefix):
            matched[k] = v
            if strip_prefix:
                stripped[k[len(prefix):]] = v

    return NamespaceResult(
        namespace=namespace,
        keys=matched,
        stripped_keys=stripped if strip_prefix else {},
        is_ok=True,
    )


def list_namespaces(profile: Dict[str, str]) -> List[str]:
    """Return sorted list of unique namespace prefixes found in the profile."""
    namespaces: set = set()
    for k in profile:
        if "_" in k:
            namespaces.add(k.split("_")[0])
    return sorted(namespaces)


def inject_namespace(
    profile: Dict[str, str],
    namespace: str,
    keys: Dict[str, str],
    overwrite: bool = False,
) -> Dict[str, str]:
    """Add keys under a namespace prefix into an existing profile dict."""
    prefix = namespace.rstrip("_") + "_"
    result = dict(profile)
    for k, v in keys.items():
        full_key = prefix + k
        if full_key in result and not overwrite:
            continue
        result[full_key] = v
    return result


def format_namespace_result(result: NamespaceResult, strip: bool = True) -> str:
    lines = [f"Namespace: {result.namespace}", ""]
    src = result.stripped_keys if strip and result.stripped_keys else result.keys
    if not src:
        lines.append("  (no keys found)")
    else:
        for k, v in sorted(src.items()):
            lines.append(f"  {k}={v}")
    return "\n".join(lines)
