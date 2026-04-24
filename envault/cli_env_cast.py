"""CLI commands for env-cast type casting."""
from __future__ import annotations

import json
import sys

import click

from envault.env_cast import cast_profile, format_cast_result
from envault.vault import load_profile


@click.group("cast")
def cast_cmd():
    """Cast env var values to typed Python values."""


@cast_cmd.command("run")
@click.argument("profile")
@click.argument("vault_path", type=click.Path())
@click.argument("password")
@click.option(
    "--schema",
    "schema_json",
    required=True,
    help='JSON mapping of KEY to type, e.g. \'{"PORT":"int","DEBUG":"bool"}\'',
)
@click.option("--strict", is_flag=True, default=False, help="Fail on cast errors.")
@click.option("--json-out", is_flag=True, default=False, help="Output JSON.")
def cast_run(profile, vault_path, password, schema_json, strict, json_out):
    """Cast values in PROFILE using a JSON type schema."""
    try:
        schema = json.loads(schema_json)
    except json.JSONDecodeError as exc:
        click.echo(f"Invalid schema JSON: {exc}", err=True)
        sys.exit(2)

    if not isinstance(schema, dict):
        click.echo("Invalid schema: expected a JSON object mapping keys to types.", err=True)
        sys.exit(2)

    try:
        data = load_profile(vault_path, profile, password)
    except Exception as exc:
        click.echo(f"Error loading profile: {exc}", err=True)
        sys.exit(1)

    result = cast_profile(data, schema, profile=profile, strict=strict)

    if not result.ok:
        for err in result.errors:
            click.echo(f"Cast error: {err}", err=True)
        sys.exit(1)

    if json_out:
        click.echo(json.dumps(result.casted, indent=2))
    else:
        click.echo(format_cast_result(result))
