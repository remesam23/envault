"""CLI commands for renaming keys within a profile."""
import click
from envault.env_rename_key import rename_key, format_rename_key_result, RenameKeyError


@click.group("rename-key")
def rename_key_cmd():
    """Rename a key inside a profile."""


@rename_key_cmd.command("run")
@click.argument("profile")
@click.argument("old_key")
@click.argument("new_key")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite new_key if it exists.")
def rename_key_run(profile, old_key, new_key, vault, password, overwrite):
    """Rename OLD_KEY to NEW_KEY in PROFILE."""
    try:
        result = rename_key(vault, profile, password, old_key, new_key, overwrite=overwrite)
        click.echo(format_rename_key_result(result))
        if result.skipped:
            raise SystemExit(1)
    except RenameKeyError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(2)
