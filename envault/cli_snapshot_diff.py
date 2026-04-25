"""CLI commands for diffing snapshots against current profile state."""

import click
from envault.vault import load_profile
from envault.env_snapshot_diff import diff_snapshot, format_snapshot_diff, ok
from envault.snapshot import SnapshotError


@click.group("snapshot-diff")
def snapshot_diff_cmd():
    """Compare snapshots to current profile state."""


@snapshot_diff_cmd.command("show")
@click.argument("profile")
@click.argument("snapshot_id")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--exit-code", is_flag=True, default=False,
              help="Exit with code 1 if differences exist.")
def snap_diff_show(profile: str, snapshot_id: str, vault_path: str, password: str, exit_code: bool):
    """Show diff between SNAPSHOT_ID and current state of PROFILE."""
    try:
        current = load_profile(vault_path, profile, password)
        result = diff_snapshot(vault_path, profile, snapshot_id, current)
        click.echo(format_snapshot_diff(result))
        if exit_code and result.has_diff:
            raise SystemExit(1)
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(2)
