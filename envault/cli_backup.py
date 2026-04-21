"""CLI commands for backup and restore."""

from __future__ import annotations

import click

from envault.env_backup import BackupError, backup_profiles, restore_profiles


@click.group("backup")
def backup_cmd() -> None:
    """Backup and restore profile bundles."""


@backup_cmd.command("create")
@click.argument("dest")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--profile",
    "profiles",
    multiple=True,
    help="Profile(s) to include (default: all).",
)
def backup_create(dest: str, vault: str, password: str, profiles: tuple) -> None:
    """Create a backup bundle at DEST."""
    try:
        result = backup_profiles(
            vault,
            password,
            dest,
            list(profiles) if profiles else None,
        )
        click.echo(result.summary())
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@backup_cmd.command("restore")
@click.argument("src")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing profiles.",
)
def backup_restore(src: str, vault: str, password: str, overwrite: bool) -> None:
    """Restore profiles from a backup bundle at SRC."""
    try:
        result = restore_profiles(vault, password, src, overwrite=overwrite)
        click.echo(result.summary())
    except BackupError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
