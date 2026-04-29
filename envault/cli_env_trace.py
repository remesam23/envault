"""CLI commands for env-trace: record and inspect key access traces."""

from __future__ import annotations

from pathlib import Path

import click

from .env_trace import clear_trace, format_trace, get_trace, record_access


@click.group("trace")
def trace_cmd() -> None:
    """Track and inspect key access events."""


@trace_cmd.command("record")
@click.argument("profile")
@click.argument("key")
@click.option("--context", default=None, help="Optional context label.")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def trace_record(profile: str, key: str, context: str | None, vault: str) -> None:
    """Record a key access event."""
    entry = record_access(Path(vault), profile, key, context=context)
    ctx_str = f" [{entry.context}]" if entry.context else ""
    click.echo(f"Recorded: {entry.profile}::{entry.key}{ctx_str} at {entry.timestamp}")


@trace_cmd.command("list")
@click.option("--profile", default=None, help="Filter by profile.")
@click.option("--key", default=None, help="Filter by key name.")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def trace_list(profile: str | None, key: str | None, vault: str) -> None:
    """List recorded key access events."""
    entries = get_trace(Path(vault), profile=profile, key=key)
    click.echo(format_trace(entries))


@trace_cmd.command("clear")
@click.option("--profile", default=None, help="Clear only entries for this profile.")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def trace_clear(profile: str | None, vault: str) -> None:
    """Clear trace entries."""
    removed = clear_trace(Path(vault), profile=profile)
    scope = f"profile '{profile}'" if profile else "all profiles"
    click.echo(f"Cleared {removed} trace entries for {scope}.")
