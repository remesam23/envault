"""CLI commands for field-level encryption within a profile."""

import click

from envault.env_encrypt_field import encrypt_fields, decrypt_fields, FieldEncryptError
from envault.vault import load_profile, save_profile


@click.group("field")
def field_cmd():
    """Field-level encryption for individual keys."""


@field_cmd.command("encrypt")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=True)
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory")
@click.option("--overwrite", is_flag=True, default=False, help="Re-encrypt already-encrypted fields")
def field_encrypt(profile, keys, password, vault, overwrite):
    """Encrypt specific KEYS inside PROFILE."""
    try:
        data = load_profile(vault, profile, password)
    except Exception as exc:
        raise click.ClickException(str(exc))

    updated, result = encrypt_fields(data, list(keys), password, overwrite=overwrite)

    try:
        save_profile(vault, profile, updated, password)
    except Exception as exc:
        raise click.ClickException(str(exc))

    if result.encrypted:
        click.echo(f"Encrypted: {', '.join(result.encrypted)}")
    if result.already_encrypted:
        click.echo(f"Already encrypted (skipped): {', '.join(result.already_encrypted)}")
    if result.skipped:
        click.echo(f"Key not found (skipped): {', '.join(result.skipped)}")


@field_cmd.command("decrypt")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=False)
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory")
def field_decrypt(profile, keys, password, vault):
    """Decrypt specific KEYS (or all encrypted keys) inside PROFILE."""
    try:
        data = load_profile(vault, profile, password)
    except Exception as exc:
        raise click.ClickException(str(exc))

    key_list = list(keys) if keys else None
    try:
        updated, result = decrypt_fields(data, key_list, password)
    except FieldEncryptError as exc:
        raise click.ClickException(str(exc))

    try:
        save_profile(vault, profile, updated, password)
    except Exception as exc:
        raise click.ClickException(str(exc))

    if result.decrypted:
        click.echo(f"Decrypted: {', '.join(result.decrypted)}")
    if result.not_encrypted:
        click.echo(f"Not encrypted (skipped): {', '.join(result.not_encrypted)}")
    if result.skipped:
        click.echo(f"Key not found (skipped): {', '.join(result.skipped)}")
