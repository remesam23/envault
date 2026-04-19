"""CLI commands for profile history."""
import click
from envault.history import get_history, clear_history, format_history


@click.group("history")
def history_cmd():
    """View and manage profile value history."""


@history_cmd.command("list")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--show-values", is_flag=True, default=False, help="Show key=value pairs.")
def history_list(profile: str, vault: str, show_values: bool):
    """List history entries for a profile."""
    entries = get_history(vault, profile)
    click.echo(format_history(entries, show_values=show_values))


@history_cmd.command("show")
@click.argument("profile")
@click.argument("index", type=int)
@click.option("--vault", default=".envault", show_default=True)
def history_show(profile: str, index: int, vault: str):
    """Show a specific history entry by index."""
    entries = get_history(vault, profile)
    if not entries:
        click.echo("No history found.")
        raise SystemExit(1)
    if index < 0 or index >= len(entries):
        click.echo(f"Index {index} out of range (0-{len(entries)-1}).")
        raise SystemExit(1)
    entry = entries[index]
    import time
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry["timestamp"]))
    click.echo(f"Snapshot [{index}] at {ts}:")
    for k, v in entry["env"].items():
        click.echo(f"  {k}={v}")


@history_cmd.command("clear")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
@click.confirmation_option(prompt="Clear all history for this profile?")
def history_clear(profile: str, vault: str):
    """Clear all history entries for a profile."""
    removed = clear_history(vault, profile)
    click.echo(f"Cleared {removed} history entry(s) for '{profile}'.")
