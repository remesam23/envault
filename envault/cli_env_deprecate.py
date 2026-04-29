"""CLI commands for managing key deprecation in profiles."""
import click
from pathlib import Path

from envault.env_deprecate import (
    mark_deprecated,
    get_deprecated,
    unmark_deprecated,
    is_deprecated,
    format_deprecate_result,
    DeprecateError,
)


@click.group(name="deprecate")
def deprecate_cmd():
    """Mark, inspect, or clear deprecated keys in a profile."""


@deprecate_cmd.command("mark")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=True)
@click.option("--reason", default=None, help="Why this key is deprecated.")
@click.option("--replacement", default=None, help="Suggested replacement key name.")
@click.option("--vault-dir", default=".", show_default=True)
def deprecate_mark(profile, keys, reason, replacement, vault_dir):
    """Mark one or more keys as deprecated."""
    result = mark_deprecated(
        Path(vault_dir), profile, list(keys), reason=reason, replacement=replacement
    )
    click.echo(format_deprecate_result(result))


@deprecate_cmd.command("list")
@click.argument("profile")
@click.option("--vault-dir", default=".", show_default=True)
def deprecate_list(profile, vault_dir):
    """List all deprecated keys in a profile."""
    entries = get_deprecated(Path(vault_dir), profile)
    if not entries:
        click.echo(f"No deprecated keys in '{profile}'.")
        return
    for key, entry in entries.items():
        hint = f" -> '{entry.replacement}'" if entry.replacement else ""
        note = f" ({entry.reason})" if entry.reason else ""
        click.echo(f"  {key}{note}{hint}")


@deprecate_cmd.command("unmark")
@click.argument("profile")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def deprecate_unmark(profile, key, vault_dir):
    """Remove deprecation mark from a key."""
    try:
        unmark_deprecated(Path(vault_dir), profile, key)
        click.echo(f"Key '{key}' is no longer marked as deprecated in '{profile}'.")
    except DeprecateError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@deprecate_cmd.command("check")
@click.argument("profile")
@click.argument("key")
@click.option("--vault-dir", default=".", show_default=True)
def deprecate_check(profile, key, vault_dir):
    """Check whether a specific key is deprecated."""
    if is_deprecated(Path(vault_dir), profile, key):
        click.echo(f"'{key}' is deprecated in '{profile}'.")
        raise SystemExit(1)
    else:
        click.echo(f"'{key}' is not deprecated in '{profile}'.")
