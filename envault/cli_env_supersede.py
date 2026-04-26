"""CLI commands for env_supersede: mark/clear/list superseded profiles."""
import click

from envault.env_supersede import (
    SupersedeError,
    clear_supersede,
    get_supersede,
    list_superseded,
    mark_superseded,
)


@click.group("supersede")
def supersede_cmd():
    """Manage superseded profile relationships."""


@supersede_cmd.command("mark")
@click.argument("profile")
@click.argument("superseded_by")
@click.option("--reason", default=None, help="Optional reason for supersession.")
@click.option("--vault", default=".", show_default=True)
def supersede_mark(profile, superseded_by, reason, vault):
    """Mark PROFILE as superseded by SUPERSEDED_BY."""
    try:
        result = mark_superseded(vault, profile, superseded_by, reason=reason)
        click.echo(result.message)
        if reason:
            click.echo(f"  Reason: {reason}")
    except SupersedeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@supersede_cmd.command("get")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True)
def supersede_get(profile, vault):
    """Show supersede info for PROFILE."""
    entry = get_supersede(vault, profile)
    if entry is None:
        click.echo(f"Profile '{profile}' is not marked as superseded.")
        return
    click.echo(f"Profile : {entry.profile}")
    click.echo(f"Replaced by: {entry.superseded_by}")
    if entry.reason:
        click.echo(f"Reason  : {entry.reason}")


@supersede_cmd.command("clear")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True)
def supersede_clear(profile, vault):
    """Remove supersede entry for PROFILE."""
    try:
        clear_supersede(vault, profile)
        click.echo(f"Supersede entry for '{profile}' removed.")
    except SupersedeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@supersede_cmd.command("list")
@click.option("--vault", default=".", show_default=True)
def supersede_list(vault):
    """List all superseded profiles."""
    entries = list_superseded(vault)
    if not entries:
        click.echo("No superseded profiles.")
        return
    for e in entries:
        line = f"{e.profile}  ->  {e.superseded_by}"
        if e.reason:
            line += f"  ({e.reason})"
        click.echo(line)
