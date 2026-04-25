"""Export audit logs to various formats (json, csv, text)."""
from __future__ import annotations

import csv
import io
import json
from typing import List, Optional

from envault.audit import get_events


class AuditExportError(Exception):
    pass


SUPPORTED_FORMATS = ("json", "csv", "text")


def export_audit(
    vault_path: str,
    fmt: str = "text",
    profile: Optional[str] = None,
) -> str:
    """Return audit log as a formatted string.

    Args:
        vault_path: Path to the vault directory.
        fmt: Output format — 'json', 'csv', or 'text'.
        profile: Optional profile name to filter events.

    Returns:
        Formatted string representation of the audit log.
    """
    if fmt not in SUPPORTED_FORMATS:
        raise AuditExportError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )

    events: List[dict] = get_events(vault_path, profile=profile)

    if fmt == "json":
        return _to_json(events)
    if fmt == "csv":
        return _to_csv(events)
    return _to_text(events)


def _to_json(events: List[dict]) -> str:
    return json.dumps(events, indent=2)


def _to_csv(events: List[dict]) -> str:
    if not events:
        return ""
    output = io.StringIO()
    fieldnames = ["timestamp", "event", "profile", "detail"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for event in events:
        writer.writerow(
            {
                "timestamp": event.get("timestamp", ""),
                "event": event.get("event", ""),
                "profile": event.get("profile", ""),
                "detail": event.get("detail", ""),
            }
        )
    return output.getvalue()


def _to_text(events: List[dict]) -> str:
    if not events:
        return "(no audit events)"
    lines = []
    for e in events:
        ts = e.get("timestamp", "?")
        ev = e.get("event", "?")
        pr = e.get("profile", "?")
        detail = e.get("detail", "")
        line = f"[{ts}] {ev} | profile={pr}"
        if detail:
            line += f" | {detail}"
        lines.append(line)
    return "\n".join(lines)
