"""CLI commands for managing profile priorities."""

from __future__ import annotations

import click

from envault.env_priority import (
    PriorityError,
    clear_priority,
    get_priority,
    list_priorities,
    set_priority,
)


@click.group("priority")
def priority_cmd():
    """Manage numeric priorities for profiles."""


@priority_cmd.command("set")
@click.argument("profile")
@click.argument("priority", type=int)
@click.option("--vault", default=".envault", show_default=True)
def priority_set(profile: str, priority: int, vault: str):
    """Set the priority for PROFILE."""
    val = set_priority(vault, profile, priority)
    click.echo(f"Priority for '{profile}' set to {val}.")


@priority_cmd.command("get")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def priority_get(profile: str, vault: str):
    """Get the priority for PROFILE."""
    val = get_priority(vault, profile)
    if val is None:
        click.echo(f"No priority set for '{profile}'.")
    else:
        click.echo(f"{profile}: {val}")


@priority_cmd.command("clear")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def priority_clear(profile: str, vault: str):
    """Remove the priority entry for PROFILE."""
    try:
        clear_priority(vault, profile)
        click.echo(f"Priority cleared for '{profile}'.")
    except PriorityError as exc:
        raise click.ClickException(str(exc))


@priority_cmd.command("list")
@click.option("--vault", default=".envault", show_default=True)
def priority_list(vault: str):
    """List all profiles ordered by priority (highest first)."""
    entries = list_priorities(vault)
    if not entries:
        click.echo("No priorities set.")
        return
    for entry in entries:
        click.echo(f"{entry['profile']:30s}  {entry['priority']}")
