"""CLI commands for generating random env var values."""

import click
from envault.vault import load_profile, save_profile
from envault.env_generate import generate_for_profile, format_generate_result, GenerateError, CHARSETS


@click.group("generate")
def generate_cmd():
    """Generate random values for environment variable keys."""


@generate_cmd.command("run")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=True)
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--length", default=32, show_default=True, help="Length of generated value.")
@click.option(
    "--charset",
    default="alphanum",
    show_default=True,
    type=click.Choice(list(CHARSETS.keys())),
    help="Character set to use.",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--reveal", is_flag=True, default=False, help="Show generated values in output.")
@click.option("--vault", "vault_path", default=".envault", show_default=True, help="Vault directory.")
def generate_run(profile, keys, password, length, charset, overwrite, reveal, vault_path):
    """Generate random values for KEYS in PROFILE."""
    try:
        data = load_profile(vault_path, profile, password)
        result = generate_for_profile(
            data,
            list(keys),
            length=length,
            charset=charset,
            overwrite=overwrite,
        )
        save_profile(vault_path, profile, data, password)
        click.echo(f"Profile '{profile}' updated:")
        click.echo(format_generate_result(result, reveal=reveal))
    except GenerateError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(2)
