"""CLI commands for managing per-key annotations."""
from __future__ import annotations

import click

from envault.env_annotate import (
    AnnotateError,
    format_annotations,
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)


@click.group("annotate")
def annotate_cmd() -> None:
    """Manage human-readable notes attached to individual keys."""


@annotate_cmd.command("set")
@click.argument("profile")
@click.argument("key")
@click.argument("note")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def annotate_set(profile: str, key: str, note: str, vault: str) -> None:
    """Attach NOTE to KEY in PROFILE."""
    stored = set_annotation(vault, profile, key, note)
    click.echo(f"Annotated {key}: {stored}")


@annotate_cmd.command("get")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def annotate_get(profile: str, key: str, vault: str) -> None:
    """Show the note for KEY in PROFILE."""
    note = get_annotation(vault, profile, key)
    if note is None:
        click.echo(f"(no annotation for '{key}')")
    else:
        click.echo(note)


@annotate_cmd.command("remove")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def annotate_remove(profile: str, key: str, vault: str) -> None:
    """Remove the note for KEY in PROFILE."""
    try:
        remove_annotation(vault, profile, key)
        click.echo(f"Removed annotation for '{key}'.")
    except AnnotateError as exc:
        raise click.ClickException(str(exc)) from exc


@annotate_cmd.command("list")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def annotate_list(profile: str, vault: str) -> None:
    """List all annotations for PROFILE."""
    annotations = list_annotations(vault, profile)
    click.echo(format_annotations(annotations))
