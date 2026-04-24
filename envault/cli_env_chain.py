"""CLI commands for profile chaining."""
from __future__ import annotations

import click

from envault.vault import load_profile
from envault.env_chain import ChainError, resolve_chain, format_chain_result


@click.group("chain")
def chain_cmd() -> None:
    """Layer multiple profiles into a single resolved environment."""


@chain_cmd.command("resolve")
@click.argument("profiles", nargs=-1, required=True)
@click.option("--vault", "vault_path", required=True, envvar="ENVAULT_VAULT", help="Path to vault directory.")
@click.option("--password", prompt=True, hide_input=True, envvar="ENVAULT_PASSWORD", help="Vault password.")
@click.option("--show-sources", is_flag=True, default=False, help="Show which profile each key came from.")
@click.option("--keys-only", is_flag=True, default=False, help="Print only key names.")
def chain_resolve(
    profiles: tuple,
    vault_path: str,
    password: str,
    show_sources: bool,
    keys_only: bool,
) -> None:
    """Resolve PROFILES in order (last wins) and print the merged environment."""
    try:
        loaded = {name: load_profile(vault_path, name, password) for name in profiles}
        result = resolve_chain(loaded, list(profiles))
    except ChainError as exc:
        raise click.ClickException(str(exc)) from exc

    if keys_only:
        for key in sorted(result.merged):
            click.echo(key)
        return

    if show_sources:
        click.echo(format_chain_result(result))
        return

    for key in sorted(result.merged):
        click.echo(f"{key}={result.merged[key]}")
