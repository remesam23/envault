"""CLI commands for copying keys between profiles."""

import click
from envault.copy import copy_keys, copy_summary, CopyError
from envault.audit import record_event


@click.command("copy")
@click.argument("src_profile")
@click.argument("dst_profile")
@click.option("--key", "keys", multiple=True, help="Specific key(s) to copy (repeatable).")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in destination.")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory path.")
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def copy_cmd(src_profile, dst_profile, keys, overwrite, vault, password):
    """Copy keys from SRC_PROFILE to DST_PROFILE."""
    try:
        result = copy_keys(
            vault_path=vault,
            src_profile=src_profile,
            dst_profile=dst_profile,
            password=password,
            keys=list(keys) if keys else None,
            overwrite=overwrite,
        )
        record_event(vault, "copy", src_profile, detail=f"-> {dst_profile}")
        click.echo(copy_summary(result))
    except CopyError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Copy failed: {e}")
