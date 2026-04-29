"""CLI commands for retention policy management."""
import click
from pathlib import Path

from envault.env_retention import (
    RetentionError,
    set_policy,
    get_policy,
    clear_policy,
    list_policies,
)


@click.group(name="retention")
def retention_cmd():
    """Manage retention policies for vault profiles."""


@retention_cmd.command("set")
@click.argument("profile")
@click.option("--max-snapshots", type=int, default=None, help="Maximum number of snapshots to retain")
@click.option("--max-days", type=int, default=None, help="Maximum age in days for snapshots")
@click.option("--reason", default=None, help="Optional reason for this policy")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory")
def retention_set(profile, max_snapshots, max_days, reason, vault):
    """Set a retention policy for a profile."""
    try:
        policy = set_policy(Path(vault), profile, max_snapshots=max_snapshots, max_days=max_days, reason=reason)
        parts = []
        if policy.max_snapshots is not None:
            parts.append(f"max_snapshots={policy.max_snapshots}")
        if policy.max_days is not None:
            parts.append(f"max_days={policy.max_days}")
        click.echo(f"Retention policy set for '{profile}': {', '.join(parts)}")
        if policy.reason:
            click.echo(f"Reason: {policy.reason}")
    except RetentionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@retention_cmd.command("get")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory")
def retention_get(profile, vault):
    """Show the retention policy for a profile."""
    policy = get_policy(Path(vault), profile)
    if policy is None:
        click.echo(f"No retention policy set for '{profile}'")
        return
    click.echo(f"Profile: {policy.profile}")
    if policy.max_snapshots is not None:
        click.echo(f"  max_snapshots: {policy.max_snapshots}")
    if policy.max_days is not None:
        click.echo(f"  max_days:      {policy.max_days}")
    if policy.reason:
        click.echo(f"  reason:        {policy.reason}")


@retention_cmd.command("clear")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory")
def retention_clear(profile, vault):
    """Remove the retention policy for a profile."""
    try:
        clear_policy(Path(vault), profile)
        click.echo(f"Retention policy cleared for '{profile}'")
    except RetentionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@retention_cmd.command("list")
@click.option("--vault", default=".", show_default=True, help="Path to vault directory")
def retention_list(vault):
    """List all retention policies."""
    policies = list_policies(Path(vault))
    if not policies:
        click.echo("No retention policies defined.")
        return
    for p in policies:
        parts = []
        if p.max_snapshots is not None:
            parts.append(f"max_snapshots={p.max_snapshots}")
        if p.max_days is not None:
            parts.append(f"max_days={p.max_days}")
        suffix = f" [{p.reason}]" if p.reason else ""
        click.echo(f"  {p.profile}: {', '.join(parts)}{suffix}")
