"""Password rotation: re-encrypt all profiles with a new password."""

from typing import Optional
from envault.vault import _load_raw, _save_raw, save_profile, load_profile, list_profiles
from envault.audit import record_event


class RotationError(Exception):
    pass


def rotate_password(vault_path: str, old_password: str, new_password: str) -> list[str]:
    """
    Re-encrypt every profile in the vault with new_password.
    Returns list of rotated profile names.
    Raises RotationError if any profile fails to decrypt with old_password.
    """
    profiles = list_profiles(vault_path)
    if not profiles:
        return []

    decrypted = {}
    for name in profiles:
        try:
            decrypted[name] = load_profile(vault_path, name, old_password)
        except Exception as e:
            raise RotationError(f"Failed to decrypt profile '{name}' with old password: {e}") from e

    for name, env_vars in decrypted.items():
        save_profile(vault_path, name, env_vars, new_password)

    record_event(vault_path, "rotate", "__all__", {"profiles": profiles})
    return profiles


def rotate_summary(rotated: list[str]) -> str:
    if not rotated:
        return "No profiles found; nothing to rotate."
    lines = [f"Rotated {len(rotated)} profile(s):"] + [f"  - {n}" for n in rotated]
    return "\n".join(lines)
