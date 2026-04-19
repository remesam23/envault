"""Rollback a profile to a previous history snapshot."""
from __future__ import annotations
from typing import Optional
from envault.history import get_history, HistoryError
from envault.vault import save_profile, load_profile


class RollbackError(Exception):
    pass


def rollback_profile(
    vault_path: str,
    profile: str,
    password: str,
    entry_id: str,
) -> dict:
    """Restore a profile to the state recorded in a history entry.

    Returns the restored env dict.
    """
    entries = get_history(vault_path, profile)
    match = next((e for e in entries if e["id"] == entry_id), None)
    if match is None:
        raise RollbackError(
            f"History entry '{entry_id}' not found for profile '{profile}'."
        )

    env = match["data"]
    save_profile(vault_path, profile, env, password)
    return env


def rollback_summary(profile: str, entry_id: str, env: dict) -> str:
    lines = [
        f"Rolled back profile '{profile}' to snapshot {entry_id}.",
        f"  {len(env)} key(s) restored.",
    ]
    return "\n".join(lines)
