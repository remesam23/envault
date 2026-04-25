"""CLI commands for watermarking profiles."""
from __future__ import annotations

import click

from envault.env_watermark import (
    WatermarkError,
    apply_watermark,
    verify_watermark,
    strip_watermark,
)


@click.group("watermark")
def watermark_cmd():
    """Embed or verify a hidden watermark in a profile."""


@watermark_cmd.command("apply")
@click.argument("profile")
@click.option("--secret", required=True, envvar="ENVAULT_WM_SECRET",
              help="Shared secret used to generate the watermark token")
@click.pass_context
def wm_apply(ctx, profile: str, secret: str):
    """Embed a watermark into PROFILE."""
    from envault.vault import load_profile, save_profile
    vault_path = ctx.obj["vault"]
    password = ctx.obj["password"]
    try:
        data = load_profile(vault_path, profile, password)
        updated, result = apply_watermark(data, profile, secret)
        save_profile(vault_path, profile, updated, password)
        click.echo(result.message)
        click.echo(f"Token: {result.token}")
    except WatermarkError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@watermark_cmd.command("verify")
@click.argument("profile")
@click.option("--secret", required=True, envvar="ENVAULT_WM_SECRET",
              help="Shared secret to verify against")
@click.pass_context
def wm_verify(ctx, profile: str, secret: str):
    """Verify the watermark in PROFILE."""
    from envault.vault import load_profile
    vault_path = ctx.obj["vault"]
    password = ctx.obj["password"]
    try:
        data = load_profile(vault_path, profile, password)
        result = verify_watermark(data, profile, secret)
        status = "✓" if result.valid else "✗"
        click.echo(f"{status} {result.message}")
        raise SystemExit(0 if result.valid else 1)
    except WatermarkError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@watermark_cmd.command("strip")
@click.argument("profile")
@click.pass_context
def wm_strip(ctx, profile: str):
    """Remove the watermark key from PROFILE."""
    from envault.vault import load_profile, save_profile
    vault_path = ctx.obj["vault"]
    password = ctx.obj["password"]
    data = load_profile(vault_path, profile, password)
    cleaned = strip_watermark(data)
    save_profile(vault_path, profile, cleaned, password)
    click.echo(f"Watermark stripped from '{profile}'")
