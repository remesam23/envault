"""CLI commands for profile tag management."""
import click
from envault.tags import add_tag, remove_tag, get_tags, profiles_by_tag, TagError


@click.group("tags")
def tags_cmd():
    """Manage tags on profiles."""
    pass


@tags_cmd.command("add")
@click.argument("profile")
@click.argument("tag")
@click.option("--vault-dir", default=".envault", show_default=True)
def tag_add(profile: str, tag: str, vault_dir: str):
    """Add a tag to a profile."""
    add_tag(vault_dir, profile, tag)
    click.echo(f"Tagged '{profile}' with '{tag}'.")


@tags_cmd.command("remove")
@click.argument("profile")
@click.argument("tag")
@click.option("--vault-dir", default=".envault", show_default=True)
def tag_remove(profile: str, tag: str, vault_dir: str):
    """Remove a tag from a profile."""
    try:
        remove_tag(vault_dir, profile, tag)
        click.echo(f"Removed tag '{tag}' from '{profile}'.")
    except TagError as e:
        raise click.ClickException(str(e))


@tags_cmd.command("list")
@click.argument("profile")
@click.option("--vault-dir", default=".envault", show_default=True)
def tag_list(profile: str, vault_dir: str):
    """List tags on a profile."""
    tags = get_tags(vault_dir, profile)
    if tags:
        for t in tags:
            click.echo(t)
    else:
        click.echo(f"No tags on '{profile}'.")


@tags_cmd.command("find")
@click.argument("tag")
@click.option("--vault-dir", default=".envault", show_default=True)
def tag_find(tag: str, vault_dir: str):
    """Find all profiles with a given tag."""
    profiles = profiles_by_tag(vault_dir, tag)
    if profiles:
        for p in profiles:
            click.echo(p)
    else:
        click.echo(f"No profiles tagged '{tag}'.")
