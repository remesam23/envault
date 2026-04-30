"""CLI commands for classifying profile keys."""
import click

from envault.env_classify import ClassifyError, classify_profile, format_classify
from envault.vault import load_profile


@click.group("classify")
def classify_cmd():
    """Classify keys in a profile by category."""


@classify_cmd.command("show")
@click.argument("profile")
@click.argument("vault_path")
@click.password_option("--password", "-p", prompt="Vault password", help="Vault password.")
@click.option(
    "--category",
    "-c",
    default=None,
    help="Filter output to a single category.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Output as JSON.",
)
def classify_show(profile: str, vault_path: str, password: str, category: str, as_json: bool):
    """Show classified keys for PROFILE in VAULT_PATH."""
    import json

    try:
        data = load_profile(vault_path, profile, password)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    try:
        result = classify_profile(profile, data)
    except ClassifyError as exc:
        raise click.ClickException(str(exc)) from exc

    if category:
        filtered = result.categories.get(category, [])
        if as_json:
            click.echo(json.dumps({category: filtered}, indent=2))
        else:
            if filtered:
                click.echo(f"[{category}]")
                for k in filtered:
                    click.echo(f"  {k}")
            else:
                click.echo(f"No keys in category '{category}'.")
        return

    if as_json:
        click.echo(json.dumps(result.categories, indent=2))
    else:
        click.echo(format_classify(result))
