"""CLI commands for searching across vault profiles."""
import click
from envault.search import search_profiles, format_search


@click.group("search")
def search_cmd():
    """Search keys and values across profiles."""


@search_cmd.command("run")
@click.argument("query")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--profile", default=None, help="Limit search to one profile.")
@click.option("--keys-only", is_flag=True, help="Search only key names.")
@click.option("--values-only", is_flag=True, help="Search only values.")
@click.option("--show-values", is_flag=True, help="Print matched values.")
@click.option("--case-sensitive", is_flag=True, help="Case-sensitive matching.")
def search_run(
    query, vault, password, profile, keys_only, values_only, show_values, case_sensitive
):
    """Search for QUERY across vault profiles."""
    if keys_only and values_only:
        raise click.UsageError("--keys-only and --values-only are mutually exclusive.")
    result = search_profiles(
        vault,
        password,
        query,
        keys_only=keys_only,
        values_only=values_only,
        profile=profile,
        case_sensitive=case_sensitive,
    )
    click.echo(format_search(result, show_values=show_values))
