"""Copy keys between profiles in the vault."""

from typing import Optional
from envault.vault import load_profile, save_profile


class CopyError(Exception):
    pass


def copy_keys(
    vault_path: str,
    src_profile: str,
    dst_profile: str,
    password: str,
    keys: Optional[list] = None,
    overwrite: bool = False,
) -> dict:
    """
    Copy keys from src_profile to dst_profile.

    If keys is None, all keys are copied.
    Returns a summary dict with copied/skipped counts.
    """
    src = load_profile(vault_path, src_profile, password)

    try:
        dst = load_profile(vault_path, dst_profile, password)
    except KeyError:
        dst = {}

    keys_to_copy = keys if keys is not None else list(src.keys())

    missing = [k for k in keys_to_copy if k not in src]
    if missing:
        raise CopyError(f"Keys not found in source profile: {missing}")

    copied, skipped = [], []
    for key in keys_to_copy:
        if key in dst and not overwrite:
            skipped.append(key)
        else:
            dst[key] = src[key]
            copied.append(key)

    save_profile(vault_path, dst_profile, dst, password)

    return {"copied": copied, "skipped": skipped}


def copy_summary(result: dict) -> str:
    lines = []
    if result["copied"]:
        lines.append(f"Copied: {', '.join(result['copied'])}")
    if result["skipped"]:
        lines.append(f"Skipped (already exist): {', '.join(result['skipped'])}")
    if not result["copied"] and not result["skipped"]:
        lines.append("Nothing to copy.")
    return "\n".join(lines)
