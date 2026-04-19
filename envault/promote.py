"""Promote a profile's values into another profile (e.g. staging -> production)."""
from typing import Optional
from envault.vault import load_profile, save_profile


class PromoteError(Exception):
    pass


def promote_profile(
    vault_path: str,
    src: str,
    dst: str,
    password: str,
    keys: Optional[list] = None,
    overwrite: bool = False,
) -> dict:
    """Copy keys from src profile into dst profile.

    Returns a summary dict with promoted/skipped key lists.
    """
    src_data = load_profile(vault_path, src, password)
    try:
        dst_data = load_profile(vault_path, dst, password)
    except KeyError:
        dst_data = {}

    if keys:
        missing = [k for k in keys if k not in src_data]
        if missing:
            raise PromoteError(f"Keys not found in source profile '{src}': {missing}")
        candidates = {k: src_data[k] for k in keys}
    else:
        candidates = dict(src_data)

    promoted = []
    skipped = []
    for k, v in candidates.items():
        if k in dst_data and not overwrite:
            skipped.append(k)
        else:
            dst_data[k] = v
            promoted.append(k)

    save_profile(vault_path, dst, password, dst_data)
    return {"promoted": promoted, "skipped": skipped, "src": src, "dst": dst}


def promote_summary(result: dict) -> str:
    lines = [f"Promoted '{result['src']}' -> '{result['dst']}':"]
    if result["promoted"]:
        lines.append(f"  Promoted : {', '.join(result['promoted'])}")
    if result["skipped"]:
        lines.append(f"  Skipped  : {', '.join(result['skipped'])} (use --overwrite to replace)")
    if not result["promoted"] and not result["skipped"]:
        lines.append("  No keys to promote.")
    return "\n".join(lines)
