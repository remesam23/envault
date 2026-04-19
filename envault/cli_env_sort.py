"""CLI commands for sorting profile keys."""
import click
from envault.vault import load_profile, save_profile
from envault.env_sort import sort_profile, format_sort_result


@click.group("sort")
def sort_cmd():
    """Sort keys in a profile."""


@sort_cmd.command("run")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--reverse", is_flag=True, default=False, help="Sort descending.")
@click.option("--group-prefix", default=None, help="Bring keys with this prefix to the top.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without saving.")
def sort_run(profile, password, vault_path, reverse, group_prefix, dry_run):
    """Sort keys in PROFILE alphabetically."""
    data = load_profile(vault_path, profile, password)
    sorted_data, result = sort_profile(data, profile, reverse=reverse, group_prefix=group_prefix)
    click.echo(format_sort_result(result))
    if not dry_run:
        save_profile(vault_path, profile, sorted_data, password)
        if result.changed:
            click.echo("  Saved.")
    else:
        click.echo("  Dry-run: no changes saved.")
