"""Type-casting utilities for env var values."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class CastError(Exception):
    pass


@dataclass
class CastResult:
    profile: str
    casted: Dict[str, Any]
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}


def _cast_value(value: str, typ: str) -> Any:
    if typ == "int":
        try:
            return int(value)
        except ValueError:
            raise CastError(f"Cannot cast {value!r} to int")
    if typ == "float":
        try:
            return float(value)
        except ValueError:
            raise CastError(f"Cannot cast {value!r} to float")
    if typ == "bool":
        low = value.strip().lower()
        if low in _TRUTHY:
            return True
        if low in _FALSY:
            return False
        raise CastError(f"Cannot cast {value!r} to bool")
    if typ == "str":
        return value
    raise CastError(f"Unknown type {typ!r}")


def cast_profile(
    data: Dict[str, str],
    schema: Dict[str, str],
    profile: str = "",
    strict: bool = False,
) -> CastResult:
    """Cast env values according to a type schema {KEY: type_name}."""
    casted: Dict[str, Any] = {}
    skipped: List[str] = []
    errors: List[str] = []

    for key, value in data.items():
        typ = schema.get(key)
        if typ is None:
            casted[key] = value
            skipped.append(key)
            continue
        try:
            casted[key] = _cast_value(value, typ)
        except CastError as exc:
            if strict:
                errors.append(str(exc))
            else:
                casted[key] = value
                skipped.append(key)

    return CastResult(profile=profile, casted=casted, skipped=skipped, errors=errors)


def format_cast_result(result: CastResult) -> str:
    lines = [f"Cast result for profile '{result.profile}':"]
    for key, val in result.casted.items():
        lines.append(f"  {key} = {val!r} ({type(val).__name__})")
    if result.skipped:
        lines.append(f"Skipped (no schema): {', '.join(result.skipped)}")
    if result.errors:
        lines.append("Errors:")
        for e in result.errors:
            lines.append(f"  - {e}")
    return "\n".join(lines)
