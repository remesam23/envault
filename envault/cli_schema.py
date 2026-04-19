"""CLI commands for schema validation."""
import json
import click
from pathlib import Path
from envault.schema import FieldSpec, validate_profile, format_validation
from envault.vault import load_profile


@click.group("schema")
def schema_cmd():
    """Validate profiles against a schema."""


@schema_cmd.command("check")
@click.argument("profile")
@click.argument("schema_file", type=click.Path(exists=True))
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def schema_check(profile, schema_file, vault_path, password):
    """Validate PROFILE against SCHEMA_FILE (JSON)."""
    raw = json.loads(Path(schema_file).read_text())
    schema = {
        k: FieldSpec(
            required=v.get("required", True),
            pattern=v.get("pattern"),
            allowed=v.get("allowed"),
            description=v.get("description", ""),
        )
        for k, v in raw.items()
    }
    env = load_profile(vault_path, profile, password)
    result = validate_profile(env, schema)
    click.echo(format_validation(result))
    if not result.ok:
        raise SystemExit(1)
