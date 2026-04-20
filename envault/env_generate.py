"""env_generate.py — Generate random values for environment variable keys.

Supports multiple value types: secret (random hex), uuid, password (alphanumeric+symbols),
numeric, and boolean. Useful for bootstrapping new profiles with secure defaults.
"""

import secrets
import string
import uuid as _uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

VALID_TYPES = ("secret", "uuid", "password", "numeric", "bool")

DEFAULT_SECRET_BYTES = 32
DEFAULT_PASSWORD_LENGTH = 24
DEFAULT_NUMERIC_LENGTH = 8


class GenerateError(Exception):
    """Raised when key generation fails."""


@dataclass
class GeneratedKey:
    key: str
    value: str
    type: str


@dataclass
class GenerateResult:
    generated: List[GeneratedKey] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.generated) > 0 or len(self.skipped) == 0

    def as_dict(self) -> Dict[str, str]:
        return {g.key: g.value for g in self.generated}


def _generate_value(value_type: str, length: Optional[int] = None) -> str:
    """Generate a single random value of the given type."""
    if value_type == "secret":
        byte_count = length if length else DEFAULT_SECRET_BYTES
        return secrets.token_hex(byte_count)

    elif value_type == "uuid":
        return str(_uuid.uuid4())

    elif value_type == "password":
        pw_len = length if length else DEFAULT_PASSWORD_LENGTH
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        return "".join(secrets.choice(alphabet) for _ in range(pw_len))

    elif value_type == "numeric":
        num_len = length if length else DEFAULT_NUMERIC_LENGTH
        return "".join(secrets.choice(string.digits) for _ in range(num_len))

    elif value_type == "bool":
        return secrets.choice(["true", "false"])

    else:
        raise GenerateError(
            f"Unknown value type '{value_type}'. "
            f"Valid types: {', '.join(VALID_TYPES)}"
        )


def generate_keys(
    keys: List[str],
    value_type: str = "secret",
    length: Optional[int] = None,
    existing: Optional[Dict[str, str]] = None,
    overwrite: bool = False,
) -> GenerateResult:
    """Generate random values for the given list of keys.

    Args:
        keys: List of environment variable names to generate values for.
        value_type: Type of value to generate (secret, uuid, password, numeric, bool).
        length: Optional length hint for types that support it (secret bytes, password/numeric chars).
        existing: Existing profile dict to check for conflicts.
        overwrite: If True, overwrite existing keys; otherwise skip them.

    Returns:
        GenerateResult containing generated entries and skipped key names.
    """
    if value_type not in VALID_TYPES:
        raise GenerateError(
            f"Unknown value type '{value_type}'. "
            f"Valid types: {', '.join(VALID_TYPES)}"
        )

    result = GenerateResult()
    existing = existing or {}

    for key in keys:
        if not key:
            continue
        if key in existing and not overwrite:
            result.skipped.append(key)
            continue
        value = _generate_value(value_type, length)
        result.generated.append(GeneratedKey(key=key, value=value, type=value_type))

    return result


def format_generate_result(result: GenerateResult) -> str:
    """Return a human-readable summary of a GenerateResult."""
    lines = []
    if result.generated:
        lines.append(f"Generated {len(result.generated)} key(s):")
        for g in result.generated:
            lines.append(f"  {g.key} [{g.type}] = {g.value}")
    if result.skipped:
        lines.append(f"Skipped {len(result.skipped)} existing key(s): {', '.join(result.skipped)}")
    if not lines:
        lines.append("No keys generated.")
    return "\n".join(lines)
