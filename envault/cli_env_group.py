"""CLI commands for profile groups."""
import click
from envault.env_group import (
    create_group, add_to_group, remove_from_group,
    get_group, list_groups, delete_group, GroupError
)


@click.group("group")
def group_cmd():
    """Manage profile groups."""


@group_cmd.command("create")
@click.argument("group")
@click.argument("profiles", nargs=-1, required=True)
@click.pass_context
def group_create(ctx, group, profiles):
    """Create a group with the given profiles."""
    vault_dir = ctx.obj["vault_dir"]
    members = create_group(vault_dir, group, list(profiles))
    click.echo(f"Created group '{group}' with: {', '.join(members)}")


@group_cmd.command("add")
@click.argument("group")
@click.argument("profile")
@click.pass_context
def group_add(ctx, group, profile):
    """Add a profile to an existing group."""
    vault_dir = ctx.obj["vault_dir"]
    try:
        members = add_to_group(vault_dir, group, profile)
        click.echo(f"Group '{group}': {', '.join(members)}")
    except GroupError as e:
        raise click.ClickException(str(e))


@group_cmd.command("remove")
@click.argument("group")
@click.argument("profile")
@click.pass_context
def group_remove(ctx, group, profile):
    """Remove a profile from a group."""
    vault_dir = ctx.obj["vault_dir"]
    try:
        members = remove_from_group(vault_dir, group, profile)
        click.echo(f"Group '{group}': {', '.join(members) or '(empty)'}")
    except GroupError as e:
        raise click.ClickException(str(e))


@group_cmd.command("list")
@click.pass_context
def group_list(ctx, ):
    """List all groups."""
    vault_dir = ctx.obj["vault_dir"]
    groups = list_groups(vault_dir)
    if not groups:
        click.echo("No groups defined.")
        return
    for name, members in groups.items():
        click.echo(f"{name}: {', '.join(members)}")


@group_cmd.command("show")
@click.argument("group")
@click.pass_context
def group_show(ctx, group):
    """Show profiles in a group."""
    vault_dir = ctx.obj["vault_dir"]
    try:
        members = get_group(vault_dir, group)
        click.echo("\n".join(members) if members else "(empty)")
    except GroupError as e:
        raise click.ClickException(str(e))


@group_cmd.command("delete")
@click.argument("group")
@click.pass_context
def group_delete(ctx, group):
    """Delete a group."""
    vault_dir = ctx.obj["vault_dir"]
    try:
        delete_group(vault_dir, group)
        click.echo(f"Deleted group '{group}'.")
    except GroupError as e:
        raise click.ClickException(str(e))
