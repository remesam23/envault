"""Compare a snapshot to the current profile state and report differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envault.snapshot import get_snapshot, SnapshotError
from envault.diff import diff_profiles, format_diff


@dataclass
class SnapshotDiffResult:
    profile: str
    snapshot_id: str
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_diff(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def ok(result: SnapshotDiffResult) -> bool:
    return not result.has_diff


def diff_snapshot(
    vault_path: str,
    profile: str,
    snapshot_id: str,
    current_data: Dict[str, str],
) -> SnapshotDiffResult:
    """Diff a named snapshot against the current profile data."""
    entry = get_snapshot(vault_path, profile, snapshot_id)
    if entry is None:
        raise SnapshotError(f"Snapshot '{snapshot_id}' not found for profile '{profile}'")

    snapshot_data: Dict[str, str] = entry.get("data", {})
    diff = diff_profiles(snapshot_data, current_data)

    return SnapshotDiffResult(
        profile=profile,
        snapshot_id=snapshot_id,
        added=diff.added,
        removed=diff.removed,
        changed=diff.changed,
        unchanged=diff.unchanged,
    )


def format_snapshot_diff(result: SnapshotDiffResult) -> str:
    """Return a human-readable string describing the snapshot diff."""
    lines = [
        f"Snapshot diff: '{result.snapshot_id}' -> current  [{result.profile}]",
        "-" * 50,
    ]
    if not result.has_diff:
        lines.append("No differences found.")
        return "\n".join(lines)

    for key, val in sorted(result.added.items()):
        lines.append(f"  + {key}={val}")
    for key, val in sorted(result.removed.items()):
        lines.append(f"  - {key}={val}")
    for key, (old, new) in sorted(result.changed.items()):
        lines.append(f"  ~ {key}: {old!r} -> {new!r}")

    return "\n".join(lines)
