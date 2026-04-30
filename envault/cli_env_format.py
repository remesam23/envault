"""cli_env_format.py — CLI commands for env-format feature."""
import click

from envault.env_format import (
    FormatError,
    format_profile,
    format_format_result,
    list_formatters,
)
from envault.vault import load_profile, save_profile


@click.group("format")
def format_cmd() -> None:
    """Format profile values using built-in formatters."""


@format_cmd.command("run")
@click.argument("profile")
@click.argument("formatter")
@click.option("--key", "-k", "keys", multiple=True, help="Limit to specific keys.")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--dry-run", is_flag=True, default=False)
def format_run(
    profile: str,
    formatter: str,
    keys: tuple,
    vault: str,
    password: str,
    dry_run: bool,
) -> None:
    """Apply FORMATTER to values in PROFILE."""
    try:
        data = load_profile(vault, profile, password)
        result = format_profile(data, formatter, list(keys) or None)
    except FormatError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(format_format_result(result, formatter))

    if not dry_run and result.updated:
        merged = {**data, **{k: result.updated[k] for k in result.updated}}
        save_profile(vault, profile, password, merged)
        click.echo("Profile updated.")
    elif dry_run:
        click.echo("(dry-run — no changes written)")


@format_cmd.command("list")
def format_list() -> None:
    """List available formatters."""
    for name in list_formatters():
        click.echo(name)
