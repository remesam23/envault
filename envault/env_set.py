"""Bulk set/unset keys in a profile with optional dry-run support."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class EnvSetError(Exception):
    pass


@dataclass
class SetResult:
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return True


def set_keys(
    data: Dict[str, str],
    updates: Dict[str, Optional[str]],
    *,
    overwrite: bool = True,
    delete_none: bool = True,
) -> tuple[Dict[str, str], SetResult]:
    """Apply updates to data dict. None values delete the key."""
    result = SetResult()
    out = dict(data)

    for key, value in updates.items():
        if value is None:
            if delete_none:
                if key in out:
                    del out[key]
                    result.deleted.append(key)
                else:
                    result.skipped.append(key)
            else:
                result.skipped.append(key)
        elif key in out:
            if overwrite:
                out[key] = value
                result.updated.append(key)
            else:
                result.skipped.append(key)
        else:
            out[key] = value
            result.added.append(key)

    return out, result


def format_set_result(result: SetResult) -> str:
    lines = []
    for k in result.added:
        lines.append(f"  + {k} (added)")
    for k in result.updated:
        lines.append(f"  ~ {k} (updated)")
    for k in result.deleted:
        lines.append(f"  - {k} (deleted)")
    for k in result.skipped:
        lines.append(f"  . {k} (skipped)")
    return "\n".join(lines) if lines else "  (no changes)"
