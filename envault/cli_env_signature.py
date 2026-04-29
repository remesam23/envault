"""CLI commands for profile HMAC signing and verification."""
from __future__ import annotations

import click

from envault.env_signature import (
    SignatureError,
    list_signatures,
    remove_signature,
    sign_profile,
    verify_profile,
)
from envault.vault import load_profile


@click.group("signature")
def signature_cmd():
    """Sign and verify profile integrity."""


@signature_cmd.command("sign")
@click.argument("profile")
@click.option("--secret", required=True, envvar="ENVAULT_SIG_SECRET", help="HMAC secret")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD", help="Vault password")
@click.option("--vault", "vault_dir", default=".", show_default=True)
def sig_sign(profile: str, secret: str, password: str, vault_dir: str):
    """Sign a profile with an HMAC signature."""
    try:
        data = load_profile(vault_dir, profile, password)
        result = sign_profile(vault_dir, profile, data, secret)
        click.echo(f"Signed profile '{profile}'.")
        click.echo(f"Signature : {result.signature}")
    except SignatureError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@signature_cmd.command("verify")
@click.argument("profile")
@click.option("--secret", required=True, envvar="ENVAULT_SIG_SECRET")
@click.option("--password", required=True, envvar="ENVAULT_PASSWORD")
@click.option("--vault", "vault_dir", default=".", show_default=True)
def sig_verify(profile: str, secret: str, password: str, vault_dir: str):
    """Verify a profile's HMAC signature."""
    try:
        data = load_profile(vault_dir, profile, password)
        result = verify_profile(vault_dir, profile, data, secret)
        status = "VALID" if result.valid else "INVALID"
        click.echo(f"[{status}] {result.message}")
        raise SystemExit(0 if result.valid else 2)
    except SignatureError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@signature_cmd.command("remove")
@click.argument("profile")
@click.option("--vault", "vault_dir", default=".", show_default=True)
def sig_remove(profile: str, vault_dir: str):
    """Remove the stored signature for a profile."""
    try:
        remove_signature(vault_dir, profile)
        click.echo(f"Signature removed for profile '{profile}'.")
    except SignatureError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@signature_cmd.command("list")
@click.option("--vault", "vault_dir", default=".", show_default=True)
def sig_list(vault_dir: str):
    """List all signed profiles."""
    import datetime
    sigs = list_signatures(vault_dir)
    if not sigs:
        click.echo("No signatures recorded.")
        return
    for profile, ts in sorted(sigs.items()):
        dt = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        click.echo(f"  {profile:<20} signed at {dt}")
