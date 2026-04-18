"""CLI commands for importing/exporting .env profiles in envault."""
from __future__ import annotations

import click
from pathlib import Path

from envault.export import read_dotenv_file, write_dotenv_file
from envault.vault import save_profile, load_profile


@click.command("import")
@click.argument("profile")
@click.argument("env_file", default=".env", type=click.Path(exists=True))
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.password_option(prompt="Vault password")
def import_cmd(profile: str, env_file: str, vault: str, password: str) -> None:
    """Import ENV_FILE into PROFILE inside the vault."""
    env = read_dotenv_file(env_file)
    save_profile(vault, profile, env, password)
    click.echo(f"Imported '{env_file}' into profile '{profile}'.")


@click.command("export")
@click.argument("profile")
@click.argument("env_file", default=".env")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.option(
    "--overwrite", is_flag=True, default=False, help="Overwrite existing file."
)
@click.password_option(prompt="Vault password", confirmation_prompt=False)
def export_cmd(profile: str, env_file: str, vault: str, overwrite: bool, password: str) -> None:
    """Export PROFILE from the vault to ENV_FILE."""
    dest = Path(env_file)
    if dest.exists() and not overwrite:
        raise click.ClickException(
            f"'{env_file}' already exists. Use --overwrite to replace it."
        )
    try:
        env = load_profile(vault, profile, password)
    except KeyError:
        raise click.ClickException(f"Profile '{profile}' not found in vault.")
    except Exception as exc:
        raise click.ClickException(f"Failed to decrypt profile: {exc}")
    write_dotenv_file(dest, env)
    click.echo(f"Exported profile '{profile}' to '{env_file}'.")
