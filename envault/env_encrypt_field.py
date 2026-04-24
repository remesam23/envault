"""Field-level encryption: encrypt/decrypt individual keys within a profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.crypto import encrypt, decrypt

FIELD_CIPHER_PREFIX = "enc:"


class FieldEncryptError(Exception):
    pass


@dataclass
class FieldEncryptResult:
    encrypted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    already_encrypted: List[str] = field(default_factory=list)


@dataclass
class FieldDecryptResult:
    decrypted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    not_encrypted: List[str] = field(default_factory=list)


def ok(result: FieldEncryptResult) -> bool:
    return len(result.skipped) == 0


def is_field_encrypted(value: str) -> bool:
    """Return True if the value looks like a field-encrypted blob."""
    return value.startswith(FIELD_CIPHER_PREFIX)


def encrypt_fields(
    profile: Dict[str, str],
    keys: List[str],
    password: str,
    overwrite: bool = False,
) -> tuple[Dict[str, str], FieldEncryptResult]:
    """Encrypt specific keys in a profile dict. Returns updated profile and result."""
    result = FieldEncryptResult()
    updated = dict(profile)

    for key in keys:
        if key not in profile:
            result.skipped.append(key)
            continue
        value = profile[key]
        if is_field_encrypted(value):
            if not overwrite:
                result.already_encrypted.append(key)
                continue
        ciphertext = encrypt(value.encode(), password).decode()
        updated[key] = FIELD_CIPHER_PREFIX + ciphertext
        result.encrypted.append(key)

    return updated, result


def decrypt_fields(
    profile: Dict[str, str],
    keys: Optional[List[str]],
    password: str,
) -> tuple[Dict[str, str], FieldDecryptResult]:
    """Decrypt specific keys (or all encrypted keys) in a profile dict."""
    result = FieldDecryptResult()
    updated = dict(profile)
    targets = keys if keys is not None else list(profile.keys())

    for key in targets:
        if key not in profile:
            result.skipped.append(key)
            continue
        value = profile[key]
        if not is_field_encrypted(value):
            result.not_encrypted.append(key)
            continue
        blob = value[len(FIELD_CIPHER_PREFIX):].encode()
        try:
            plaintext = decrypt(blob, password).decode()
        except Exception as exc:
            raise FieldEncryptError(f"Failed to decrypt field '{key}': {exc}") from exc
        updated[key] = plaintext
        result.decrypted.append(key)

    return updated, result
