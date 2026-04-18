"""CLI commands for snapshot management."""

import click

from envault.snapshot import SnapshotError, delete_snapshot, list_snapshots, restore_snapshot, take_snapshot


@click.group("snapshot")
def snapshot_cmd():
    """Manage profile snapshots."""


@snapshot_cmd.command("take")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--label", default="", help="Optional label for this snapshot")
def snap_take(profile, vault, password, label):
    """Take a snapshot of PROFILE."""
    try:
        entry = take_snapshot(vault, profile, password, label)
        ts = entry["ts"]
        click.echo(f"Snapshot taken for '{profile}' at {ts:.0f}" + (f" [{label}]" if label else ""))
    except Exception as e:
        raise click.ClickException(str(e))


@snapshot_cmd.command("list")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
def snap_list(profile, vault):
    """List snapshots for PROFILE."""
    snaps = list_snapshots(vault, profile)
    if not snaps:
        click.echo(f"No snapshots for '{profile}'.")
        return
    for s in snaps:
        label = f" [{s['label']}]" if s["label"] else ""
        click.echo(f"  [{s['index']}] ts={s['ts']:.0f}{label}")


@snapshot_cmd.command("restore")
@click.argument("profile")
@click.argument("index", type=int)
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def snap_restore(profile, index, vault, password):
    """Restore PROFILE from snapshot INDEX."""
    try:
        restore_snapshot(vault, profile, index, password)
        click.echo(f"Profile '{profile}' restored from snapshot {index}.")
    except SnapshotError as e:
        raise click.ClickException(str(e))


@snapshot_cmd.command("delete")
@click.argument("profile")
@click.argument("index", type=int)
@click.option("--vault", default=".envault", show_default=True)
def snap_delete(profile, index, vault):
    """Delete snapshot INDEX for PROFILE."""
    try:
        delete_snapshot(vault, profile, index)
        click.echo(f"Snapshot {index} deleted for '{profile}'.")
    except SnapshotError as e:
        raise click.ClickException(str(e))
