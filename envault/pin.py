"""Pin/unpin profiles to mark them as active or default."""

from __future__ import annotations

import json
from pathlib import Path


class PinError(Exception):
    pass


def _pins_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".pins.json"


def _load_pins(vault_dir: str) -> dict:
    p = _pins_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(vault_dir: str, pins: dict) -> None:
    _pins_path(vault_dir).write_text(json.dumps(pins, indent=2))


def pin_profile(vault_dir: str, profile: str) -> None:
    """Mark a profile as pinned."""
    vault_path = Path(vault_dir)
    if not (vault_path / f"{profile}.env.enc").exists():
        raise PinError(f"Profile '{profile}' does not exist.")
    pins = _load_pins(vault_dir)
    pins[profile] = True
    _save_pins(vault_dir, pins)


def unpin_profile(vault_dir: str, profile: str) -> None:
    """Remove pin from a profile."""
    pins = _load_pins(vault_dir)
    if profile not in pins:
        raise PinError(f"Profile '{profile}' is not pinned.")
    del pins[profile]
    _save_pins(vault_dir, pins)


def is_pinned(vault_dir: str, profile: str) -> bool:
    return _load_pins(vault_dir).get(profile, False)


def list_pinned(vault_dir: str) -> list[str]:
    return [p for p, v in _load_pins(vault_dir).items() if v]


def pin_summary(pinned: list[str]) -> str:
    if not pinned:
        return "No pinned profiles."
    return "Pinned profiles: " + ", ".join(sorted(pinned))
