"""CLI commands for batch import/export of profiles."""
import click
from envault.env_import_export_batch import batch_import, batch_export, format_batch_result, BatchError


@click.group("batch")
def batch_cmd():
    """Batch import/export multiple profiles."""


@batch_cmd.command("import")
@click.argument("vault")
@click.argument("directory")
@click.password_option("--password", "-p", prompt=True, help="Vault password")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing profiles")
@click.option("--pattern", default="*.env", show_default=True, help="Glob pattern for files")
def batch_import_cmd(vault, directory, password, overwrite, pattern):
    """Import all .env files from DIRECTORY into VAULT."""
    try:
        result = batch_import(vault, directory, password, overwrite=overwrite, pattern=pattern)
        click.echo(f"Batch import from '{directory}':")
        click.echo(format_batch_result(result, action="imported"))
        if not result.ok:
            raise SystemExit(1)
    except BatchError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@batch_cmd.command("export")
@click.argument("vault")
@click.argument("directory")
@click.password_option("--password", "-p", prompt=True, help="Vault password")
@click.option("--profile", "-n", multiple=True, help="Profiles to export (default: all)")
def batch_export_cmd(vault, directory, password, profile):
    """Export profiles from VAULT to .env files in DIRECTORY."""
    try:
        profiles = list(profile) if profile else None
        result = batch_export(vault, directory, password, profiles=profiles)
        click.echo(f"Batch export to '{directory}':")
        click.echo(format_batch_result(result, action="exported"))
        if not result.ok:
            raise SystemExit(1)
    except BatchError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
