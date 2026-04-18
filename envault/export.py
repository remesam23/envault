"""Export and import .env file utilities for envault."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict


def parse_dotenv(text: str) -> Dict[str, str]:
    """Parse a .env file string into a key/value dict."""
    env: Dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]
        if key:
            env[key] = value
    return env


def serialize_dotenv(env: Dict[str, str]) -> str:
    """Serialize a key/value dict to .env file format."""
    lines = []
    for key, value in env.items():
        # Quote values that contain spaces or special chars
        if any(c in value for c in (" ", "#", "'", '"', "\n")):
            value = '"' + value.replace('"', '\\"') + '"'
        lines.append(f"{key}={value}")
    return os.linesep.join(lines) + os.linesep


def read_dotenv_file(path: str | Path) -> Dict[str, str]:
    """Read and parse a .env file from disk."""
    content = Path(path).read_text(encoding="utf-8")
    return parse_dotenv(content)


def write_dotenv_file(path: str | Path, env: Dict[str, str]) -> None:
    """Write a key/value dict as a .env file to disk."""
    Path(path).write_text(serialize_dotenv(env), encoding="utf-8")
