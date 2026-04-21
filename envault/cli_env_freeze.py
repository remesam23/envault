"""CLI commands for freezing / unfreezing profiles."""
import click

from envault.env_freeze import (
    FreezeError,
    freeze_profile,
    unfreeze_profile,
    is_frozen,
    list_frozen,
    get_freeze_reason,
)


@click.group("freeze", help="Freeze or unfreeze profiles to prevent accidental edits.")
def freeze_cmd() -> None:  # pragma: no cover
    pass


@freeze_cmd.command("add")
@click.argument("profile")
@click.option("--reason", default=None, help="Optional reason for freezing.")
@click.option("--vault", default=".envault", show_default=True)
def freeze_add(profile: str, reason: str, vault: str) -> None:
    """Freeze PROFILE so it cannot be modified."""
    try:
        freeze_profile(vault, profile, reason=reason)
        click.echo(f"Profile '{profile}' is now frozen.")
        if reason:
            click.echo(f"Reason: {reason}")
    except FreezeError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@freeze_cmd.command("remove")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def freeze_remove(profile: str, vault: str) -> None:
    """Unfreeze PROFILE."""
    try:
        unfreeze_profile(vault, profile)
        click.echo(f"Profile '{profile}' has been unfrozen.")
    except FreezeError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@freeze_cmd.command("status")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def freeze_status(profile: str, vault: str) -> None:
    """Show freeze status of PROFILE."""
    frozen = is_frozen(vault, profile)
    if frozen:
        reason = get_freeze_reason(vault, profile)
        msg = f"Profile '{profile}' is FROZEN."
        if reason:
            msg += f" Reason: {reason}"
        click.echo(msg)
    else:
        click.echo(f"Profile '{profile}' is not frozen.")


@freeze_cmd.command("list")
@click.option("--vault", default=".envault", show_default=True)
def freeze_list(vault: str) -> None:
    """List all frozen profiles."""
    profiles = list_frozen(vault)
    if not profiles:
        click.echo("No frozen profiles.")
        return
    for name in profiles:
        reason = get_freeze_reason(vault, name)
        line = f"  {name}"
        if reason:
            line += f"  ({reason})"
        click.echo(line)
