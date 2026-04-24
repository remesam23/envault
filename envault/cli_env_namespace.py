"""CLI commands for namespace operations."""

from __future__ import annotations

import click

from envault.env_namespace import (
    extract_namespace,
    inject_namespace,
    list_namespaces,
    format_namespace_result,
)
from envault.vault import load_profile, save_profile


@click.group("namespace")
def namespace_cmd() -> None:
    """Manage key namespaces within a profile."""


@namespace_cmd.command("extract")
@click.argument("profile")
@click.argument("namespace")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--no-strip", is_flag=True, default=False, help="Keep full key names.")
def namespace_extract(
    profile: str,
    namespace: str,
    password: str,
    vault_path: str,
    no_strip: bool,
) -> None:
    """Show all keys under NAMESPACE prefix in PROFILE."""
    data = load_profile(vault_path, profile, password)
    result = extract_namespace(data, namespace, strip_prefix=not no_strip)
    click.echo(format_namespace_result(result, strip=not no_strip))


@namespace_cmd.command("list")
@click.argument("profile")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def namespace_list(profile: str, password: str, vault_path: str) -> None:
    """List all namespace prefixes detected in PROFILE."""
    data = load_profile(vault_path, profile, password)
    namespaces = list_namespaces(data)
    if not namespaces:
        click.echo("No namespaces found.")
    else:
        for ns in namespaces:
            click.echo(ns)


@namespace_cmd.command("inject")
@click.argument("profile")
@click.argument("namespace")
@click.argument("pairs", nargs=-1, required=True, metavar="KEY=VALUE...")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--overwrite", is_flag=True, default=False)
def namespace_inject(
    profile: str,
    namespace: str,
    pairs: tuple,
    password: str,
    vault_path: str,
    overwrite: bool,
) -> None:
    """Inject KEY=VALUE pairs under NAMESPACE prefix into PROFILE."""
    data = load_profile(vault_path, profile, password)
    keys: dict = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {pair}")
        k, v = pair.split("=", 1)
        keys[k] = v
    updated = inject_namespace(data, namespace, keys, overwrite=overwrite)
    added = len(updated) - len(data)
    save_profile(vault_path, profile, updated, password)
    click.echo(f"Injected {len(keys)} key(s) under '{namespace}_' ({added} new).")
