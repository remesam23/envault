"""env_notify.py — notification hooks for envault events.

Allows users to register webhook URLs or shell commands that are triggered
when specific vault events occur (e.g. profile unlocked, TTL expired,
profile rotated). Notifications are stored per-vault and fired on demand.
"""

from __future__ import annotations

import json
import subprocess
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any


EVENT_TYPES = {
    "unlock",
    "lock",
    "rotate",
    "ttl_expired",
    "profile_deleted",
    "snapshot_taken",
    "any",
}


class NotifyError(Exception):
    """Raised when a notification operation fails."""


@dataclass
class NotifyHook:
    """A single notification hook entry."""
    event: str          # event type or "any"
    kind: str           # "webhook" or "command"
    target: str         # URL or shell command template
    label: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "NotifyHook":
        return NotifyHook(
            event=d["event"],
            kind=d["kind"],
            target=d["target"],
            label=d.get("label"),
        )


@dataclass
class NotifyResult:
    """Result of firing notifications for an event."""
    event: str
    profile: str
    fired: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0


def _notify_path(vault_dir: Path) -> Path:
    return vault_dir / ".notify_hooks.json"


def _load_hooks(vault_dir: Path) -> List[NotifyHook]:
    p = _notify_path(vault_dir)
    if not p.exists():
        return []
    raw = json.loads(p.read_text())
    return [NotifyHook.from_dict(h) for h in raw]


def _save_hooks(vault_dir: Path, hooks: List[NotifyHook]) -> None:
    _notify_path(vault_dir).write_text(
        json.dumps([h.to_dict() for h in hooks], indent=2)
    )


def add_hook(
    vault_dir: Path,
    event: str,
    kind: str,
    target: str,
    label: Optional[str] = None,
) -> NotifyHook:
    """Register a new notification hook.

    Args:
        vault_dir: Path to the vault directory.
        event: One of EVENT_TYPES.
        kind: "webhook" or "command".
        target: The webhook URL or shell command (may include {profile}, {event}).
        label: Optional human-readable label.

    Returns:
        The created NotifyHook.

    Raises:
        NotifyError: If event or kind is invalid.
    """
    if event not in EVENT_TYPES:
        raise NotifyError(f"Unknown event type '{event}'. Valid: {sorted(EVENT_TYPES)}")
    if kind not in ("webhook", "command"):
        raise NotifyError(f"Unknown kind '{kind}'. Use 'webhook' or 'command'.")
    hooks = _load_hooks(vault_dir)
    hook = NotifyHook(event=event, kind=kind, target=target, label=label)
    hooks.append(hook)
    _save_hooks(vault_dir, hooks)
    return hook


def remove_hook(vault_dir: Path, index: int) -> NotifyHook:
    """Remove a hook by its zero-based index.

    Raises:
        NotifyError: If the index is out of range.
    """
    hooks = _load_hooks(vault_dir)
    if index < 0 or index >= len(hooks):
        raise NotifyError(f"Hook index {index} out of range (0–{len(hooks) - 1}).")
    removed = hooks.pop(index)
    _save_hooks(vault_dir, hooks)
    return removed


def list_hooks(vault_dir: Path) -> List[NotifyHook]:
    """Return all registered hooks."""
    return _load_hooks(vault_dir)


def fire_event(
    vault_dir: Path,
    event: str,
    profile: str,
    extra: Optional[Dict[str, str]] = None,
) -> NotifyResult:
    """Fire all hooks matching the given event.

    Webhook hooks receive a JSON POST body with event metadata.
    Command hooks are executed as a shell command with {profile} and {event}
    substituted in the target string.

    Args:
        vault_dir: Path to the vault directory.
        event: The event that occurred.
        profile: The profile name involved.
        extra: Optional additional context passed in the payload.

    Returns:
        A NotifyResult summarising which hooks fired or failed.
    """
    hooks = _load_hooks(vault_dir)
    result = NotifyResult(event=event, profile=profile)
    payload: Dict[str, Any] = {"event": event, "profile": profile}
    if extra:
        payload.update(extra)

    for hook in hooks:
        if hook.event not in (event, "any"):
            continue
        label = hook.label or hook.target
        try:
            if hook.kind == "webhook":
                _fire_webhook(hook.target, payload)
            else:
                _fire_command(hook.target, event, profile)
            result.fired.append(label)
        except Exception as exc:  # noqa: BLE001
            result.failed.append(f"{label}: {exc}")

    return result


def _fire_webhook(url: str, payload: Dict[str, Any]) -> None:
    """POST JSON payload to a webhook URL."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        if resp.status >= 400:
            raise NotifyError(f"Webhook returned HTTP {resp.status}")


def _fire_command(template: str, event: str, profile: str) -> None:
    """Execute a shell command, substituting {event} and {profile}."""
    cmd = template.format(event=event, profile=profile)
    result = subprocess.run(cmd, shell=True, capture_output=True)  # noqa: S602
    if result.returncode != 0:
        stderr = result.stderr.decode(errors="replace").strip()
        raise NotifyError(f"Command exited {result.returncode}: {stderr}")


def format_notify_result(result: NotifyResult) -> str:
    """Return a human-readable summary of a fire_event call."""
    lines = [f"Event '{result.event}' on profile '{result.profile}':"]
    if result.fired:
        lines.append(f"  Fired ({len(result.fired)}):")
        for f in result.fired:
            lines.append(f"    ✓ {f}")
    if result.failed:
        lines.append(f"  Failed ({len(result.failed)}):")
        for f in result.failed:
            lines.append(f"    ✗ {f}")
    if not result.fired and not result.failed:
        lines.append("  No matching hooks.")
    return "\n".join(lines)
