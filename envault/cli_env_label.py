"""cli_env_label.py — CLI commands for profile label management."""
import click

from envault.env_label import (
    LabelError,
    find_by_label,
    get_label,
    list_labels,
    remove_label,
    set_label,
)


@click.group("label")
def label_cmd():
    """Manage human-readable labels for profiles."""


@label_cmd.command("set")
@click.argument("profile")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def label_set(profile, label, vault):
    """Attach LABEL to PROFILE."""
    try:
        result = set_label(vault, profile, label)
        click.echo(f"Label set: {profile!r} -> {result!r}")
    except LabelError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@label_cmd.command("get")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def label_get(profile, vault):
    """Show the label for PROFILE."""
    lbl = get_label(vault, profile)
    if lbl is None:
        click.echo(f"No label set for '{profile}'.")
    else:
        click.echo(lbl)


@label_cmd.command("remove")
@click.argument("profile")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def label_remove(profile, vault):
    """Remove the label from PROFILE."""
    try:
        remove_label(vault, profile)
        click.echo(f"Label removed from '{profile}'.")
    except LabelError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@label_cmd.command("list")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def label_list(vault):
    """List all profile labels."""
    mapping = list_labels(vault)
    if not mapping:
        click.echo("No labels defined.")
        return
    for profile, lbl in sorted(mapping.items()):
        click.echo(f"  {profile}: {lbl}")


@label_cmd.command("find")
@click.argument("label")
@click.option("--vault", default=".", show_default=True, help="Vault directory.")
def label_find(label, vault):
    """Find profiles whose label matches LABEL (case-insensitive)."""
    profiles = find_by_label(vault, label)
    if not profiles:
        click.echo(f"No profiles labelled '{label}'.")
    else:
        for p in sorted(profiles):
            click.echo(p)
