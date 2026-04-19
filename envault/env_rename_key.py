"""Rename a key within a profile."""
from dataclasses import dataclass, field
from typing import Optional


class RenameKeyError(Exception):
    pass


@dataclass
class RenameKeyResult:
    old_key: str
    new_key: str
    profile: str
    skipped: bool = False
    reason: Optional[str] = None


def ok(r: RenameKeyResult) -> bool:
    return not r.skipped


def rename_key(vault_path, profile: str, password: str, old_key: str, new_key: str, overwrite: bool = False) -> RenameKeyResult:
    from envault.vault import load_profile, save_profile

    data = load_profile(vault_path, profile, password)

    if old_key not in data:
        raise RenameKeyError(f"Key '{old_key}' not found in profile '{profile}'.")

    if new_key in data and not overwrite:
        return RenameKeyResult(old_key=old_key, new_key=new_key, profile=profile,
                               skipped=True, reason=f"Key '{new_key}' already exists (use --overwrite).")

    value = data.pop(old_key)
    data[new_key] = value
    save_profile(vault_path, profile, password, data)

    return RenameKeyResult(old_key=old_key, new_key=new_key, profile=profile)


def format_rename_key_result(result: RenameKeyResult) -> str:
    if result.skipped:
        return f"Skipped: {result.reason}"
    return f"Renamed '{result.old_key}' -> '{result.new_key}' in profile '{result.profile}'."
