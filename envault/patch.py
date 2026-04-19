"""Apply partial updates (patches) to an existing profile."""

from typing import Optional
from envault.vault import load_profile, save_profile


class PatchError(Exception):
    pass


def patch_profile(
    vault_path: str,
    profile: str,
    password: str,
    updates: dict,
    delete_keys: Optional[list] = None,
) -> dict:
    """Apply key updates and optional deletions to a profile.

    Args:
        vault_path: Path to the vault directory.
        profile: Profile name to patch.
        password: Encryption password.
        updates: Dict of key/value pairs to set or overwrite.
        delete_keys: List of keys to remove from the profile.

    Returns:
        The updated profile dict.

    Raises:
        PatchError: If a key to delete does not exist in the profile.
    """
    data = load_profile(vault_path, profile, password)

    delete_keys = delete_keys or []
    missing = [k for k in delete_keys if k not in data]
    if missing:
        raise PatchError(f"Keys not found in profile '{profile}': {missing}")

    for key in delete_keys:
        del data[key]

    data.update(updates)
    save_profile(vault_path, profile, password, data)
    return data


def patch_summary(updates: dict, deleted: list) -> str:
    """Return a human-readable summary of a patch operation."""
    lines = []
    for k, v in updates.items():
        lines.append(f"  set   {k}={v}")
    for k in deleted:
        lines.append(f"  del   {k}")
    if not lines:
        return "No changes applied."
    return "Patch applied:\n" + "\n".join(lines)
