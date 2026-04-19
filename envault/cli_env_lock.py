"""CLI commands for profile locking."""
import click
from envault.env_lock import (
    lock_profile,
    unlock_profile,
    is_locked,
    list_locked,
    EnvLockError,
)


@click.group("lock")
def lock_cmd():
    """Manage write-locks on profiles."""


@lock_cmd.command("add")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def lock_add(profile, vault):
    """Lock a profile to prevent writes."""
    lock_profile(vault, profile)
    click.echo(f"Profile '{profile}' is now locked.")


@lock_cmd.command("remove")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def lock_remove(profile, vault):
    """Unlock a previously locked profile."""
    try:
        unlock_profile(vault, profile)
        click.echo(f"Profile '{profile}' has been unlocked.")
    except EnvLockError as e:
        raise click.ClickException(str(e))


@lock_cmd.command("status")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def lock_status(profile, vault):
    """Show lock status for a profile."""
    locked = is_locked(vault, profile)
    state = "locked" if locked else "unlocked"
    click.echo(f"Profile '{profile}' is {state}.")


@lock_cmd.command("list")
@click.option("--vault", default=".envault", show_default=True)
def lock_list(vault):
    """List all locked profiles."""
    locked = list_locked(vault)
    if not locked:
        click.echo("No profiles are locked.")
    else:
        for p in locked:
            click.echo(f"  🔒 {p}")
