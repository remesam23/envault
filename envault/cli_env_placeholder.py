"""CLI commands for placeholder resolution."""
from __future__ import annotations

import click

from envault.env_placeholder import PlaceholderError, format_resolution, resolve_profile
from envault.vault import load_profile, save_profile


@click.group("placeholder")
def placeholder_cmd() -> None:
    """Resolve ${VAR} placeholders inside a profile."""


@placeholder_cmd.command("resolve")
@click.argument("profile")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with error if any placeholder cannot be resolved.",
)
@click.option(
    "--apply",
    is_flag=True,
    default=False,
    help="Write resolved values back to the vault.",
)
def resolve_cmd(
    profile: str, vault_path: str, password: str, strict: bool, apply: bool
) -> None:
    """Resolve placeholders in PROFILE and optionally write back."""
    try:
        data = load_profile(vault_path, profile, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    try:
        result = resolve_profile(data, strict=strict)
    except PlaceholderError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(format_resolution(result))

    if apply:
        try:
            save_profile(vault_path, profile, password, result.resolved)
            click.echo("Resolved values written back to vault.")
        except Exception as exc:  # noqa: BLE001
            raise click.ClickException(str(exc)) from exc


@placeholder_cmd.command("list")
@click.argument("profile")
@click.option("--vault", "vault_path", required=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True)
def list_cmd(profile: str, vault_path: str, password: str) -> None:
    """List all placeholders found in PROFILE."""
    try:
        data = load_profile(vault_path, profile, password)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc

    from envault.env_placeholder import find_placeholders

    found: dict[str, list[str]] = {}
    for key, value in data.items():
        ph = find_placeholders(value)
        if ph:
            found[key] = ph

    if not found:
        click.echo("No placeholders found.")
        return

    for key, names in found.items():
        click.echo(f"  {key}: {', '.join(f'${{{n}}}' for n in names)}")
