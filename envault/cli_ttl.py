"""CLI commands for profile TTL management."""
import click
from envault.ttl import set_ttl, get_ttl, clear_ttl, list_ttl, is_expired, TTLError


@click.group("ttl")
def ttl_cmd():
    """Manage profile expiry (TTL)."""


@ttl_cmd.command("set")
@click.argument("profile")
@click.argument("seconds", type=int)
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def ttl_set(profile, seconds, vault):
    """Set TTL for PROFILE to SECONDS seconds."""
    try:
        expires_at = set_ttl(vault, profile, seconds)
        click.echo(f"TTL set for '{profile}': expires at {expires_at}")
    except TTLError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ttl_cmd.command("get")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True)
def ttl_get(profile, vault):
    """Show TTL expiry for PROFILE."""
    expiry = get_ttl(vault, profile)
    if expiry is None:
        click.echo(f"No TTL set for '{profile}'.")
    else:
        expired = is_expired(vault, profile)
        status = " [EXPIRED]" if expired else ""
        click.echo(f"{profile}: {expiry}{status}")


@ttl_cmd.command("clear")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True)
def ttl_clear(profile, vault):
    """Remove TTL for PROFILE."""
    try:
        clear_ttl(vault, profile)
        click.echo(f"TTL cleared for '{profile}'.")
    except TTLError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ttl_cmd.command("list")
@click.option("--vault", default=".", show_default=True)
def ttl_list(vault):
    """List all profiles with TTL set."""
    entries = list_ttl(vault)
    if not entries:
        click.echo("No TTL entries.")
        return
    for profile, expiry in entries.items():
        expired = is_expired(vault, profile)
        status = " [EXPIRED]" if expired else ""
        click.echo(f"{profile}: {expiry}{status}")
