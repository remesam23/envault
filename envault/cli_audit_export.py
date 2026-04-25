"""CLI commands for exporting audit logs."""
from __future__ import annotations

import click

from envault.env_audit_export import AuditExportError, export_audit


@click.group("audit-export")
def audit_export_cmd() -> None:
    """Export audit logs to a file or stdout."""


@audit_export_cmd.command("run")
@click.argument("vault_path")
@click.option(
    "--format",
    "fmt",
    default="text",
    show_default=True,
    type=click.Choice(["json", "csv", "text"], case_sensitive=False),
    help="Output format.",
)
@click.option(
    "--profile",
    default=None,
    help="Filter events by profile name.",
)
@click.option(
    "--output",
    "output_file",
    default=None,
    type=click.Path(),
    help="Write output to this file instead of stdout.",
)
def export_run(
    vault_path: str,
    fmt: str,
    profile: str | None,
    output_file: str | None,
) -> None:
    """Export audit log for VAULT_PATH."""
    try:
        result = export_audit(vault_path, fmt=fmt, profile=profile)
    except AuditExportError as exc:
        raise click.ClickException(str(exc)) from exc

    if output_file:
        with open(output_file, "w", encoding="utf-8") as fh:
            fh.write(result)
        click.echo(f"Audit log written to {output_file}")
    else:
        click.echo(result)
