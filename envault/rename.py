"""Rename a profile within the vault."""

from envault.vault import _load_raw, _save_raw


class RenameError(Exception):
    pass


def rename_profile(vault_path: str, old_name: str, new_name: str, password: str) -> None:
    """Rename a profile from old_name to new_name.

    Raises RenameError if old_name doesn't exist or new_name already exists.
    Re-encrypts data under the same password.
    """
    from envault.vault import load_profile, save_profile, list_profiles

    profiles = list_profiles(vault_path)

    if old_name not in profiles:
        raise RenameError(f"Profile '{old_name}' does not exist.")

    if new_name in profiles:
        raise RenameError(f"Profile '{new_name}' already exists.")

    data = load_profile(vault_path, old_name, password)
    save_profile(vault_path, new_name, data, password)

    raw = _load_raw(vault_path)
    del raw[old_name]
    _save_raw(vault_path, raw)


def rename_summary(old_name: str, new_name: str) -> str:
    """Return a human-readable summary of a rename operation."""
    return f"Profile '{old_name}' renamed to '{new_name}'."
