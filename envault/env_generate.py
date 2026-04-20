"""Generate random values for environment variable keys."""

import secrets
import string
import re
from dataclasses import dataclass, field
from typing import Optional


class GenerateError(Exception):
    pass


@dataclass
class GeneratedKey:
    key: str
    value: str
    length: int
    charset: str


@dataclass
class GenerateResult:
    generated: list[GeneratedKey] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    is_ok: bool = True
    error: Optional[str] = None


def ok(generated: list[GeneratedKey], skipped: list[str]) -> GenerateResult:
    return GenerateResult(generated=generated, skipped=skipped)


def as_dict(result: GenerateResult) -> dict[str, str]:
    return {g.key: g.value for g in result.generated}


CHARSETS = {
    "alpha": string.ascii_letters,
    "alphanum": string.ascii_letters + string.digits,
    "hex": string.hexdigits[:16],
    "numeric": string.digits,
    "base64url": string.ascii_letters + string.digits + "-_",
    "printable": string.ascii_letters + string.digits + string.punctuation,
}


def _generate_value(length: int, charset: str) -> str:
    chars = CHARSET_CHARS(charset)
    return "".join(secrets.choice(chars) for _ in range(length))


def CHARSET_CHARS(charset: str) -> str:
    if charset in CHARSETS:
        return CHARSETS[charset]
    raise GenerateError(f"Unknown charset '{charset}'. Choose from: {', '.join(CHARSETS)}.")


def generate_for_profile(
    profile: dict[str, str],
    keys: list[str],
    length: int = 32,
    charset: str = "alphanum",
    overwrite: bool = False,
) -> GenerateResult:
    """Generate random values for the given keys in a profile."""
    if length < 1 or length > 512:
        raise GenerateError("Length must be between 1 and 512.")

    chars = CHARSET_CHARS(charset)  # validate early

    generated: list[GeneratedKey] = []
    skipped: list[str] = []

    for key in keys:
        if not re.match(r"^[A-Z_][A-Z0-9_]*$", key):
            raise GenerateError(f"Key '{key}' is not a valid env var name.")
        if key in profile and not overwrite:
            skipped.append(key)
            continue
        value = "".join(secrets.choice(chars) for _ in range(length))
        profile[key] = value
        generated.append(GeneratedKey(key=key, value=value, length=length, charset=charset))

    return ok(generated, skipped)


def format_generate_result(result: GenerateResult, reveal: bool = False) -> str:
    lines = []
    for g in result.generated:
        display = g.value if reveal else "*" * min(g.length, 12)
        lines.append(f"  [generated] {g.key}={display}")
    for key in result.skipped:
        lines.append(f"  [skipped]   {key} (already set)")
    if not lines:
        lines.append("  (nothing generated)")
    return "\n".join(lines)
