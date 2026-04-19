"""Export diffs between profiles to various formats (json, csv, text)."""
from __future__ import annotations
import csv
import io
import json
from typing import Literal

from envault.diff import diff_profiles, DiffResult

ExportFormat = Literal["json", "csv", "text"]


def export_diff(
    base: dict[str, str],
    other: dict[str, str],
    fmt: ExportFormat = "text",
    profile_a: str = "a",
    profile_b: str = "b",
) -> str:
    """Return a string representation of the diff in the requested format."""
    result = diff_profiles(base, other)
    if fmt == "json":
        return _to_json(result, profile_a, profile_b)
    if fmt == "csv":
        return _to_csv(result, profile_a, profile_b)
    return _to_text(result, profile_a, profile_b)


def _to_json(result: DiffResult, profile_a: str, profile_b: str) -> str:
    rows = []
    for key, val in result.added.items():
        rows.append({"key": key, "status": "added", profile_b: val})
    for key, val in result.removed.items():
        rows.append({"key": key, "status": "removed", profile_a: val})
    for key, (old, new) in result.changed.items():
        rows.append({"key": key, "status": "changed", profile_a: old, profile_b: new})
    return json.dumps({"profile_a": profile_a, "profile_b": profile_b, "diff": rows}, indent=2)


def _to_csv(result: DiffResult, profile_a: str, profile_b: str) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", profile_a, profile_b])
    for key, val in result.added.items():
        writer.writerow([key, "added", "", val])
    for key, val in result.removed.items():
        writer.writerow([key, "removed", val, ""])
    for key, (old, new) in result.changed.items():
        writer.writerow([key, "changed", old, new])
    return buf.getvalue()


def _to_text(result: DiffResult, profile_a: str, profile_b: str) -> str:
    lines = [f"Diff: {profile_a} → {profile_b}"]
    for key, val in result.added.items():
        lines.append(f"  + {key}={val}")
    for key, val in result.removed.items():
        lines.append(f"  - {key}={val}")
    for key, (old, new) in result.changed.items():
        lines.append(f"  ~ {key}: {old!r} → {new!r}")
    if not (result.added or result.removed or result.changed):
        lines.append("  (no differences)")
    return "\n".join(lines)
