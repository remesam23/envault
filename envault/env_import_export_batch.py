"""Batch import/export multiple profiles to/from a directory of .env files."""
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
from envault.export import parse_dotenv, serialize_dotenv
from envault.vault import save_profile, load_profile, list_profiles


class BatchError(Exception):
    pass


@dataclass
class BatchResult:
    processed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def batch_import(vault_path: str, directory: str, password: str,
                 overwrite: bool = False, pattern: str = "*.env") -> BatchResult:
    """Import all matching .env files from a directory as profiles."""
    result = BatchResult()
    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise BatchError(f"Directory not found: {directory}")
    existing = list_profiles(vault_path)
    for env_file in sorted(dir_path.glob(pattern)):
        profile = env_file.stem
        if profile in existing and not overwrite:
            result.skipped.append(profile)
            continue
        try:
            data = parse_dotenv(env_file.read_text())
            save_profile(vault_path, profile, data, password)
            result.processed.append(profile)
        except Exception as e:
            result.errors.append(f"{profile}: {e}")
    return result


def batch_export(vault_path: str, directory: str, password: str,
                 profiles: Optional[List[str]] = None) -> BatchResult:
    """Export profiles from vault to .env files in a directory."""
    result = BatchResult()
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    targets = profiles if profiles is not None else list_profiles(vault_path)
    for profile in targets:
        try:
            data = load_profile(vault_path, profile, password)
            out = dir_path / f"{profile}.env"
            out.write_text(serialize_dotenv(data))
            result.processed.append(profile)
        except Exception as e:
            result.errors.append(f"{profile}: {e}")
    return result


def format_batch_result(result: BatchResult, action: str = "processed") -> str:
    lines = []
    for p in result.processed:
        lines.append(f"  {action}: {p}")
    for p in result.skipped:
        lines.append(f"  skipped (exists): {p}")
    for e in result.errors:
        lines.append(f"  error: {e}")
    if not lines:
        lines.append("  (nothing to do)")
    return "\n".join(lines)
