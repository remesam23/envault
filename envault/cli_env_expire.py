"""CLI commands for per-key expiry management."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import click

from .env_expire import (
    set_key_expiry,
    get_key_expiry,
    is_key_expired,
    clear_key_expiry,
    list_expired_keys,
    list_all_expiries,
    ExpireError,
)


@click.group("expire")
def expire_cmd():
    """Manage per-key expiry for profiles."""


@expire_cmd.command("set")
@click.argument("profile")
@click.argument("key")
@click.option("--days", type=int, default=None, help="Expire after N days from now.")
@click.option("--at", "at_str", default=None, help="Exact ISO datetime to expire at.")
@click.pass_context
def expire_set(ctx, profile, key, days, at_str):
    """Set expiry for KEY in PROFILE."""
    vault_dir = ctx.obj["vault_dir"]
    if days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    elif at_str:
        expires_at = datetime.fromisoformat(at_str)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
    else:
        raise click.UsageError("Provide --days or --at.")
    result = set_key_expiry(vault_dir, profile, key, expires_at)
    click.echo(f"Expiry set for '{key}' in '{profile}': {result}")


@expire_cmd.command("get")
@click.argument("profile")
@click.argument("key")
@click.pass_context
def expire_get(ctx, profile, key):
    """Show expiry for KEY in PROFILE."""
    vault_dir = ctx.obj["vault_dir"]
    raw = get_key_expiry(vault_dir, profile, key)
    if raw is None:
        click.echo(f"No expiry set for '{key}' in '{profile}'.")
        return
    expired = is_key_expired(vault_dir, profile, key)
    status = " [EXPIRED]" if expired else ""
    click.echo(f"{key}: {raw}{status}")


@expire_cmd.command("clear")
@click.argument("profile")
@click.argument("key")
@click.pass_context
def expire_clear(ctx, profile, key):
    """Remove expiry for KEY in PROFILE."""
    vault_dir = ctx.obj["vault_dir"]
    try:
        clear_key_expiry(vault_dir, profile, key)
        click.echo(f"Expiry cleared for '{key}' in '{profile}'.")
    except ExpireError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@expire_cmd.command("list")
@click.argument("profile")
@click.option("--expired-only", is_flag=True, help="Show only expired keys.")
@click.pass_context
def expire_list(ctx, profile, expired_only):
    """List expiry info for all keys in PROFILE."""
    vault_dir = ctx.obj["vault_dir"]
    if expired_only:
        keys = list_expired_keys(vault_dir, profile)
        if not keys:
            click.echo("No expired keys.")
        for k in keys:
            click.echo(k)
    else:
        expiries = list_all_expiries(vault_dir, profile)
        if not expiries:
            click.echo("No expiries set.")
        for k, v in expiries.items():
            click.echo(f"{k}: {v}")
