"""Key/value transformation utilities for envault profiles."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


class TransformError(Exception):
    pass


@dataclass
class TransformResult:
    profile: str
    original: Dict[str, str]
    transformed: Dict[str, str]
    changes: List[str] = field(default_factory=list)
    ok: bool = True


def ok(result: TransformResult) -> bool:
    return result.ok


def _apply(data: Dict[str, str], fn: Callable[[str, str], tuple]) -> tuple[Dict[str, str], List[str]]:
    out: Dict[str, str] = {}
    changes: List[str] = []
    for k, v in data.items():
        new_k, new_v = fn(k, v)
        out[new_k] = new_v
        if new_k != k or new_v != v:
            changes.append(f"{k}={v!r} -> {new_k}={new_v!r}")
    return out, changes


def transform_keys_upper(data: Dict[str, str]) -> tuple[Dict[str, str], List[str]]:
    return _apply(data, lambda k, v: (k.upper(), v))


def transform_keys_lower(data: Dict[str, str]) -> tuple[Dict[str, str], List[str]]:
    return _apply(data, lambda k, v: (k.lower(), v))


def transform_values_strip(data: Dict[str, str]) -> tuple[Dict[str, str], List[str]]:
    return _apply(data, lambda k, v: (k, v.strip()))


def transform_add_prefix(data: Dict[str, str], prefix: str) -> tuple[Dict[str, str], List[str]]:
    return _apply(data, lambda k, v: (f"{prefix}{k}", v))


def transform_remove_prefix(data: Dict[str, str], prefix: str) -> tuple[Dict[str, str], List[str]]:
    def fn(k, v):
        return (k[len(prefix):] if k.startswith(prefix) else k, v)
    return _apply(data, fn)


def apply_transform(
    profile: str,
    data: Dict[str, str],
    transform: str,
    prefix: Optional[str] = None,
) -> TransformResult:
    transforms = {
        "upper": lambda d: transform_keys_upper(d),
        "lower": lambda d: transform_keys_lower(d),
        "strip": lambda d: transform_values_strip(d),
        "add_prefix": lambda d: transform_add_prefix(d, prefix or ""),
        "remove_prefix": lambda d: transform_remove_prefix(d, prefix or ""),
    }
    if transform not in transforms:
        raise TransformError(f"Unknown transform: {transform!r}. Choose from: {', '.join(transforms)}")
    transformed, changes = transforms[transform](data)
    return TransformResult(profile=profile, original=data, transformed=transformed, changes=changes)


def format_transform_result(result: TransformResult) -> str:
    if not result.changes:
        return f"Profile '{result.profile}': no changes."
    lines = [f"Profile '{result.profile}': {len(result.changes)} change(s):"]
    for c in result.changes:
        lines.append(f"  {c}")
    return "\n".join(lines)
