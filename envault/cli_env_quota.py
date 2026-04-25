"""cli_env_quota.py — CLI commands for profile quota management."""
import click
from pathlib import Path

from envault.env_quota import (
    QuotaConfig,
    QuotaError,
    set_quota,
    get_quota,
    clear_quota,
    check_quota,
    format_quota_result,
)
from envault.vault import load_profile


@click.group("quota")
def quota_cmd():
    """Manage per-profile key/value quotas."""


@quota_cmd.command("set")
@click.argument("profile")
@click.option("--max-keys", type=int, default=None, help="Maximum number of keys allowed.")
@click.option("--max-value-bytes", type=int, default=None, help="Maximum value size in bytes.")
@click.option("--vault-dir", default=".", show_default=True)
def quota_set(profile, max_keys, max_value_bytes, vault_dir):
    """Set quota limits for a profile."""
    if max_keys is None and max_value_bytes is None:
        raise click.UsageError("Provide at least --max-keys or --max-value-bytes.")
    config = QuotaConfig(max_keys=max_keys, max_value_bytes=max_value_bytes)
    set_quota(Path(vault_dir), profile, config)
    click.echo(f"Quota set for profile '{profile}'.")


@quota_cmd.command("get")
@click.argument("profile")
@click.option("--vault-dir", default=".", show_default=True)
def quota_get(profile, vault_dir):
    """Show quota limits for a profile."""
    config = get_quota(Path(vault_dir), profile)
    if config is None:
        click.echo(f"No quota configured for profile '{profile}'.")
        return
    click.echo(f"Profile: {profile}")
    click.echo(f"  max_keys:        {config.max_keys}")
    click.echo(f"  max_value_bytes: {config.max_value_bytes}")


@quota_cmd.command("clear")
@click.argument("profile")
@click.option("--vault-dir", default=".", show_default=True)
def quota_clear(profile, vault_dir):
    """Remove quota limits for a profile."""
    try:
        clear_quota(Path(vault_dir), profile)
        click.echo(f"Quota cleared for profile '{profile}'.")
    except QuotaError as exc:
        raise click.ClickException(str(exc))


@quota_cmd.command("check")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault-dir", default=".", show_default=True)
def quota_check(profile, password, vault_dir):
    """Check whether a profile's current data satisfies its quota."""
    env = load_profile(Path(vault_dir), profile, password)
    result = check_quota(Path(vault_dir), profile, env)
    click.echo(format_quota_result(result, profile))
    if not result.passed:
        raise SystemExit(1)
