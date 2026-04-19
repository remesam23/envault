"""CLI commands for filtering profile keys."""
import click
from envault.vault import load_profile, save_profile
from envault.env_filter import (
    filter_by_prefix, filter_by_pattern, format_filter_result
)


@click.group("filter")
def filter_cmd():
    """Filter keys in a profile by prefix or pattern."""


@filter_cmd.command("prefix")
@click.argument("profile")
@click.argument("prefix")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--save-as", default=None, help="Save filtered keys into a new profile.")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def filter_prefix(profile, prefix, password, save_as, vault_path):
    """Show (or save) keys from PROFILE that start with PREFIX."""
    data = load_profile(vault_path, profile, password)
    result = filter_by_prefix(data, prefix)
    click.echo(format_filter_result(result, profile))
    if save_as:
        save_profile(vault_path, save_as, result.matched, password)
        click.echo(f"Saved {len(result.matched)} keys to profile '{save_as}'.")


@filter_cmd.command("pattern")
@click.argument("profile")
@click.argument("pattern")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--save-as", default=None, help="Save filtered keys into a new profile.")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def filter_pattern(profile, pattern, password, save_as, vault_path):
    """Show (or save) keys from PROFILE matching glob PATTERN (e.g. 'DB_*')."""
    data = load_profile(vault_path, profile, password)
    result = filter_by_pattern(data, pattern)
    click.echo(format_filter_result(result, profile))
    if save_as:
        save_profile(vault_path, save_as, result.matched, password)
        click.echo(f"Saved {len(result.matched)} keys to profile '{save_as}'.")
