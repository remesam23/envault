"""CLI commands for env-transform feature."""
import click
from envault.env_transform import apply_transform, format_transform_result, TransformError
from envault.vault import load_profile, save_profile


@click.group("transform")
def transform_cmd():
    """Transform keys or values in a profile."""


@transform_cmd.command("run")
@click.argument("profile")
@click.argument("transform", type=click.Choice(["upper", "lower", "strip", "add_prefix", "remove_prefix"]))
@click.option("--vault", "vault_path", required=True, envvar="ENVAULT_VAULT", help="Path to vault.")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", hide_input=True)
@click.option("--prefix", default=None, help="Prefix for add_prefix/remove_prefix transforms.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without saving.")
def transform_run(profile, transform, vault_path, password, prefix, dry_run):
    """Apply a transformation to a profile's keys or values."""
    try:
        data = load_profile(vault_path, profile, password)
        result = apply_transform(profile, data, transform, prefix=prefix)
        click.echo(format_transform_result(result))
        if not dry_run:
            save_profile(vault_path, profile, result.transformed, password)
            click.echo("Saved.")
        else:
            click.echo("(dry-run: not saved)")
    except TransformError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(2)
