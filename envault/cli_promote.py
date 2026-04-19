"""CLI commands for profile promotion."""
import click
from envault.promote import promote_profile, promote_summary, PromoteError


@click.group("promote")
def promote_cmd():
    """Promote keys from one profile to another."""


@promote_cmd.command("run")
@click.argument("src")
@click.argument("dst")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--key", "keys", multiple=True, help="Specific keys to promote (repeatable).")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in dst.")
def promote_run(src, dst, vault, password, keys, overwrite):
    """Promote keys from SRC profile into DST profile."""
    try:
        result = promote_profile(
            vault,
            src,
            dst,
            password,
            keys=list(keys) if keys else None,
            overwrite=overwrite,
        )
        click.echo(promote_summary(result))
    except PromoteError as e:
        raise click.ClickException(str(e))
