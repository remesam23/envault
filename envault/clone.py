"""Clone a profile to a new name, optionally filtering keys."""
from __future__ import annotations
from typing import Optional
from envault.vault import load_profile, save_profile, list_profiles


class CloneError(Exception):
    pass


def clone_profile(
    vault_path: str,
    password: str,
    src: str,
    dst: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
) -> dict:
    """Clone *src* profile into *dst*.

    Args:
        vault_path: Path to the vault directory.
        password: Master password.
        src: Source profile name.
        dst: Destination profile name.
        keys: If given, only these keys are copied. Missing keys are ignored.
        overwrite: Allow overwriting an existing destination profile.

    Returns:
        The dict that was saved to *dst*.

    Raises:
        CloneError: If the source profile does not exist, the destination
            profile already exists and *overwrite* is False, or *src* and
            *dst* refer to the same profile name.
    """
    if src == dst:
        raise CloneError("Source and destination profile names must be different.")

    profiles = list_profiles(vault_path)

    if src not in profiles:
        raise CloneError(f"Source profile '{src}' does not exist.")

    if dst in profiles and not overwrite:
        raise CloneError(
            f"Destination profile '{dst}' already exists. Use overwrite=True to replace it."
        )

    data = load_profile(vault_path, src, password)

    if keys is not None:
        data = {k: v for k, v in data.items() if k in keys}

    save_profile(vault_path, dst, data, password)
    return data


def clone_summary(src: str, dst: str, data: dict) -> str:
    n = len(data)
    return f"Cloned profile '{src}' -> '{dst}' ({n} key{'s' if n != 1 else ''})"
