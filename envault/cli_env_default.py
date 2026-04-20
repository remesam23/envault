"""CLI commands for applying default values to a profile."""
from __future__ import annotations

import json
import sys

import click

from envault.env_default import apply_defaults, merge_into, format_default_result, DefaultError
from envault.vault import load_profile, save_profile


@click.group("default")
def default_cmd() -> None:
    """Apply or inspect default values for a profile."""


@default_cmd.command("apply")
@click.argument("profile")
@click.argument("defaults_file", type=click.Path(exists=True))
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--dry-run", is_flag=True, default=False, help="Show changes without saving.")
def apply_cmd(
    profile: str,
    defaults_file: str,
    vault_path: str,
    password: str,
    overwrite: bool,
    dry_run: bool,
) -> None:
    """Apply defaults from a JSON file to PROFILE."""
    try:
        with open(defaults_file) as fh:
            defaults = json.load(fh)
        if not isinstance(defaults, dict):
            click.echo("Error: defaults file must contain a JSON object.", err=True)
            sys.exit(2)

        data = load_profile(vault_path, profile, password)
        result = apply_defaults(data, defaults, overwrite=overwrite)
        merged = merge_into(data, defaults, overwrite=overwrite)

        click.echo(format_default_result(result))

        if not dry_run:
            save_profile(vault_path, profile, merged, password)
            click.echo(f"Profile '{profile}' updated.")
        else:
            click.echo("(dry-run: no changes written)")
    except DefaultError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Unexpected error: {exc}", err=True)
        sys.exit(1)
