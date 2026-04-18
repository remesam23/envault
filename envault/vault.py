"""Vault file read/write operations for encrypted .env profiles."""

import json
import os
from pathlib import Path
from typing import Dict, Optional

from envault.crypto import encrypt, decrypt

DEFAULT_VAULT_PATH = Path(".envault")


def _load_raw(vault_path: Path) -> dict:
    if not vault_path.exists():
        return {}
    with vault_path.open("rb") as f:
        content = f.read()
    if not content.strip():
        return {}
    return json.loads(content)


def _save_raw(vault_path: Path, data: dict) -> None:
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    with vault_path.open("wb") as f:
        f.write(json.dumps(data).encode())


def save_profile(profile: str, env_content: str, password: str,
                 vault_path: Path = DEFAULT_VAULT_PATH) -> None:
    """Encrypt and save an env profile to the vault."""
    data = _load_raw(vault_path)
    encrypted = encrypt(env_content, password)
    data[profile] = encrypted.hex()
    _save_raw(vault_path, data)


def load_profile(profile: str, password: str,
                 vault_path: Path = DEFAULT_VAULT_PATH) -> str:
    """Load and decrypt an env profile from the vault."""
    data = _load_raw(vault_path)
    if profile not in data:
        raise KeyError(f"Profile '{profile}' not found in vault.")
    encrypted = bytes.fromhex(data[profile])
    return decrypt(encrypted, password)


def list_profiles(vault_path: Path = DEFAULT_VAULT_PATH):
    """Return list of stored profile names."""
    return list(_load_raw(vault_path).keys())


def delete_profile(profile: str, vault_path: Path = DEFAULT_VAULT_PATH) -> bool:
    """Remove a profile from the vault. Returns True if removed."""
    data = _load_raw(vault_path)
    if profile not in data:
        return False
    del data[profile]
    _save_raw(vault_path, data)
    return True
