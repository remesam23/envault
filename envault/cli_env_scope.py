"""CLI commands for profile scope management."""
import click

from envault.env_scope import (
    ScopeError,
    apply_scope,
    clear_scope,
    get_scope,
    list_scopes,
    set_scope,
)


@click.group("scope")
def scope_cmd() -> None:
    """Restrict which keys are visible for a profile."""


@scope_cmd.command("set")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=True)
@click.option("--vault", default=".", show_default=True, help="Vault directory")
def scope_set(profile: str, keys: tuple, vault: str) -> None:
    """Set allowed keys for PROFILE scope."""
    result = set_scope(vault, profile, list(keys))
    click.echo(f"Scope set for '{profile}': {', '.join(result)}")


@scope_cmd.command("get")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True, help="Vault directory")
def scope_get(profile: str, vault: str) -> None:
    """Show the scope for PROFILE."""
    keys = get_scope(vault, profile)
    if keys is None:
        click.echo(f"No scope defined for '{profile}' (all keys visible)")
    else:
        click.echo(f"Scope for '{profile}': {', '.join(keys)}")


@scope_cmd.command("clear")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True, help="Vault directory")
def scope_clear(profile: str, vault: str) -> None:
    """Remove scope restriction for PROFILE."""
    try:
        clear_scope(vault, profile)
        click.echo(f"Scope cleared for '{profile}'")
    except ScopeError as exc:
        raise click.ClickException(str(exc))


@scope_cmd.command("list")
@click.option("--vault", default=".", show_default=True, help="Vault directory")
def scope_list(vault: str) -> None:
    """List all defined scopes."""
    scopes = list_scopes(vault)
    if not scopes:
        click.echo("No scopes defined.")
        return
    for profile, keys in sorted(scopes.items()):
        click.echo(f"{profile}: {', '.join(keys)}")
