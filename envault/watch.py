"""Watch a .env file and auto-lock it into a profile on changes."""
import time
import os
from pathlib import Path
from typing import Optional

from envault.export import read_dotenv_file
from envault.vault import save_profile
from envault.audit import record_event


class WatchError(Exception):
    pass


def watch_file(
    vault_dir: str,
    dotenv_path: str,
    profile: str,
    password: str,
    interval: float = 1.0,
    max_cycles: Optional[int] = None,
    on_sync=None,
) -> int:
    """Poll dotenv_path and sync into profile whenever mtime changes.

    Returns number of sync events performed.
    """
    path = Path(dotenv_path)
    if not path.exists():
        raise WatchError(f"File not found: {dotenv_path}")

    last_mtime = path.stat().st_mtime
    syncs = 0
    cycles = 0

    try:
        while True:
            if max_cycles is not None and cycles >= max_cycles:
                break
            time.sleep(interval)
            cycles += 1

            if not path.exists():
                continue

            mtime = path.stat().st_mtime
            if mtime != last_mtime:
                last_mtime = mtime
                data = read_dotenv_file(str(path))
                save_profile(vault_dir, profile, data, password)
                record_event(vault_dir, "watch_sync", profile)
                syncs += 1
                if on_sync:
                    on_sync(profile, syncs)
    except KeyboardInterrupt:
        pass

    return syncs


def watch_summary(profile: str, syncs: int) -> str:
    return f"Watched profile '{profile}': {syncs} sync(s) recorded."
