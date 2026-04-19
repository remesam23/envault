"""CLI commands for env-check feature."""
import click
from pathlib import Path
from envault.vault import load_profile
from envault.export import parse_dotenv
from envault.env_check import check_env, format_check


@click.group("check")
def check_cmd():
    """Check profile keys against a reference .env file."""


@check_cmd.command("run")
@click.argument("profile")
@click.argument("reference", type=click.Path(exists=True))
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--strict", is_flag=True, default=False, help="Exit 1 if any mismatch found.")
def check_run(profile, reference, vault_path, password, strict):
    """Compare PROFILE keys against REFERENCE .env file."""
    try:
        profile_data = load_profile(vault_path, profile, password)
    except Exception as e:
        raise click.ClickException(str(e))

    ref_text = Path(reference).read_text()
    reference_data = parse_dotenv(ref_text)

    result = check_env(profile_data, reference_data)
    click.echo(format_check(result))

    if strict and not result.ok:
        raise SystemExit(1)
