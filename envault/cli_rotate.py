"""CLI commands for password rotation."""

import click
from envault.rotate import rotate_password, rotate_summary, RotationError


@click.command("rotate")
@click.argument("vault_path")
@click.option("--old-password", prompt=True, hide_input=True, help="Current vault password.")
@click.option(
    "--new-password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="New vault password.",
)
def rotate_cmd(vault_path: str, old_password: str, new_password: str) -> None:
    """Re-encrypt all profiles in VAULT_PATH with a new password."""
    if old_password == new_password:
        click.echo("New password is the same as the old password. Nothing to do.")
        return
    try:
        rotated = rotate_password(vault_path, old_password, new_password)
        click.echo(rotate_summary(rotated))
    except RotationError as e:
        click.echo(f"Rotation failed: {e}", err=True)
        raise SystemExit(1)
