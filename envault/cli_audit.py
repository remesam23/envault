"""CLI commands for audit log."""

import click
from envault.audit import get_events, clear_events


@click.command("audit")
@click.option("--profile", "-p", default=None, help="Filter by profile name.")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
def audit_cmd(profile, vault_dir):
    """Show audit log of vault operations."""
    events = get_events(vault_dir, profile=profile)
    if not events:
        click.echo("No audit events found.")
        return
    for e in events:
        line = f"[{e['timestamp']}] {e['action']:10s} profile={e['profile']}"
        if e.get("details"):
            line += f" ({e['details']})"
        line += f" user={e['user']}"
        click.echo(line)


@click.command("audit-clear")
@click.option("--vault-dir", default=".", show_default=True, help="Vault directory.")
@click.confirmation_option(prompt="Clear all audit events?")
def audit_clear_cmd(vault_dir):
    """Clear the audit log."""
    clear_events(vault_dir)
    click.echo("Audit log cleared.")
