"""CLI commands for managing read-only profile protection."""
import click

from envault.env_readonly import (
    ReadOnlyError,
    get_readonly_reason,
    is_readonly,
    list_readonly,
    set_readonly,
    unset_readonly,
)


@click.group("readonly")
def readonly_cmd():
    """Manage read-only protection for profiles."""


@readonly_cmd.command("set")
@click.argument("profile")
@click.option("--reason", default=None, help="Reason for marking as read-only.")
@click.option("--vault", default=".envault", show_default=True)
def readonly_set(profile, reason, vault):
    """Mark PROFILE as read-only."""
    set_readonly(vault, profile, reason)
    msg = f"Profile '{profile}' marked as read-only."
    if reason:
        msg += f" Reason: {reason}"
    click.echo(msg)


@readonly_cmd.command("unset")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def readonly_unset(profile, vault):
    """Remove read-only protection from PROFILE."""
    try:
        unset_readonly(vault, profile)
        click.echo(f"Profile '{profile}' is no longer read-only.")
    except ReadOnlyError as e:
        raise click.ClickException(str(e))


@readonly_cmd.command("status")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def readonly_status(profile, vault):
    """Show read-only status for PROFILE."""
    if is_readonly(vault, profile):
        reason = get_readonly_reason(vault, profile)
        line = f"read-only: yes"
        if reason:
            line += f"  reason: {reason}"
        click.echo(line)
    else:
        click.echo("read-only: no")


@readonly_cmd.command("list")
@click.option("--vault", default=".envault", show_default=True)
def readonly_list(vault):
    """List all read-only profiles."""
    entries = list_readonly(vault)
    if not entries:
        click.echo("No read-only profiles.")
        return
    for profile, reason in sorted(entries.items()):
        suffix = f"  ({reason})" if reason else ""
        click.echo(f"  {profile}{suffix}")
