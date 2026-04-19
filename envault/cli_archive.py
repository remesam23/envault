"""CLI commands for vault-wide archiving."""

import click
from envault.archive import (
    ArchiveError, create_archive, list_archives, get_archive,
    delete_archive, archive_summary,
)
from envault.vault import _load_raw, _save_raw


@click.group("archive")
def archive_cmd():
    """Manage full-vault archives."""


@archive_cmd.command("create")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--label", default="", help="Optional label for this archive.")
def arch_create(vault, label):
    """Archive all profiles in the vault."""
    try:
        raw = _load_raw(vault)
        entry = create_archive(vault, raw, label=label)
        click.echo(f"Created: {archive_summary(entry)}")
    except Exception as e:
        raise click.ClickException(str(e))


@archive_cmd.command("list")
@click.option("--vault", default=".envault", show_default=True)
def arch_list(vault):
    """List all archives."""
    entries = list_archives(vault)
    if not entries:
        click.echo("No archives found.")
        return
    for e in entries:
        click.echo(archive_summary(e))


@archive_cmd.command("restore")
@click.argument("archive_id")
@click.option("--vault", default=".envault", show_default=True)
def arch_restore(archive_id, vault):
    """Restore vault from an archive (overwrites all profiles)."""
    try:
        entry = get_archive(vault, archive_id)
        _save_raw(vault, entry["data"])
        click.echo(f"Restored archive {archive_id} ({len(entry['profiles'])} profiles).")
    except ArchiveError as e:
        raise click.ClickException(str(e))


@archive_cmd.command("delete")
@click.argument("archive_id")
@click.option("--vault", default=".envault", show_default=True)
def arch_delete(archive_id, vault):
    """Delete an archive entry."""
    try:
        delete_archive(vault, archive_id)
        click.echo(f"Deleted archive {archive_id}.")
    except ArchiveError as e:
        raise click.ClickException(str(e))
