"""CLI entry point for envault."""

import sys
import getpass
from pathlib import Path

import click

from envault.vault import save_profile, load_profile, list_profiles, delete_profile


@click.group()
def cli():
    """envault — encrypt and manage local .env profiles."""


@cli.command()
@click.argument("profile")
@click.option("--file", "env_file", default=".env", show_default=True,
              help="Path to the .env file to encrypt.")
def lock(profile, env_file):
    """Encrypt a .env file and store it as PROFILE."""
    path = Path(env_file)
    if not path.exists():
        click.echo(f"Error: '{env_file}' not found.", err=True)
        sys.exit(1)
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        click.echo("Error: passwords do not match.", err=True)
        sys.exit(1)
    content = path.read_text()
    save_profile(profile, content, password)
    click.echo(f"Profile '{profile}' saved to vault.")


@cli.command()
@click.argument("profile")
@click.option("--output", "-o", default=".env", show_default=True,
              help="Destination file for decrypted content.")
def unlock(profile, output):
    """Decrypt PROFILE from vault and write to file."""
    password = getpass.getpass("Password: ")
    try:
        content = load_profile(profile, password)
    except KeyError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except Exception:
        click.echo("Error: decryption failed. Wrong password?", err=True)
        sys.exit(1)
    Path(output).write_text(content)
    click.echo(f"Profile '{profile}' written to '{output}'.")


@cli.command(name="list")
def list_cmd():
    """List available profiles in the vault."""
    profiles = list_profiles()
    if not profiles:
        click.echo("No profiles found.")
    for p in profiles:
        click.echo(p)


@cli.command()
@click.argument("profile")
def delete(profile):
    """Delete PROFILE from the vault."""
    if delete_profile(profile):
        click.echo(f"Profile '{profile}' deleted.")
    else:
        click.echo(f"Profile '{profile}' not found.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
