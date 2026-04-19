"""CLI commands for watch feature."""
import click
from envault.watch import watch_file, watch_summary, WatchError


@click.group("watch")
def watch_cmd():
    """Watch a .env file and auto-sync changes into a profile."""


@watch_cmd.command("start")
@click.argument("profile")
@click.argument("dotenv_path")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--interval", default=1.0, show_default=True, help="Poll interval in seconds.")
def watch_start(profile, dotenv_path, vault, password, interval):
    """Watch DOTENV_PATH and sync into PROFILE on every change."""
    click.echo(f"Watching '{dotenv_path}' -> profile '{profile}'. Press Ctrl+C to stop.")

    def on_sync(prof, count):
        click.echo(f"  [sync #{count}] '{prof}' updated.")

    try:
        syncs = watch_file(
            vault_dir=vault,
            dotenv_path=dotenv_path,
            profile=profile,
            password=password,
            interval=interval,
            on_sync=on_sync,
        )
    except WatchError as e:
        raise click.ClickException(str(e))

    click.echo(watch_summary(profile, syncs))
