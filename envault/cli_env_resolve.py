"""CLI commands for env-resolve: resolve ${REF} placeholders inside a profile."""
from __future__ import annotations

import json
import sys

import click

from envault.vault import load_profile
from envault.env_resolve import resolve_profile, format_resolve_result


@click.group("resolve")
def resolve_cmd() -> None:
    """Resolve ${REF} placeholders within a profile."""


@resolve_cmd.command("run")
@click.argument("profile")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--defaults-profile", default=None, help="Profile to use as fallback defaults.")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero if any refs unresolved.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output resolved values as JSON.")
def resolve_run(
    profile: str,
    vault_path: str,
    password: str,
    defaults_profile: str | None,
    strict: bool,
    as_json: bool,
) -> None:
    """Resolve placeholders in PROFILE and print results."""
    try:
        data = load_profile(vault_path, profile, password)
        defaults = {}
        if defaults_profile:
            defaults = load_profile(vault_path, defaults_profile, password)

        result = resolve_profile(data, defaults=defaults, strict=strict)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    if as_json:
        click.echo(json.dumps(result.resolved, indent=2))
    else:
        click.echo(format_resolve_result(result))

    if not result.ok and strict:
        sys.exit(1)
