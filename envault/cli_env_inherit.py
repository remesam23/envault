"""CLI commands for profile inheritance resolution."""
import click

from envault.env_inherit import InheritError, format_inherit_result, resolve_inheritance
from envault.vault import load_profile


@click.group("inherit")
def inherit_cmd():
    """Resolve a profile by inheriting from parent profiles."""


@inherit_cmd.command("resolve")
@click.argument("profile")
@click.option(
    "--parent",
    "parents",
    multiple=True,
    required=True,
    help="Parent profile(s) to inherit from, in order (base first).",
)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--show-source", is_flag=True, default=False, help="Show which profile each key comes from.")
def resolve_cmd(profile, parents, vault_path, password, show_source):
    """Resolve PROFILE by layering PARENT profiles beneath it."""

    def _loader(name: str):
        return load_profile(vault_path, name, password)

    try:
        result = resolve_inheritance(profile, list(parents), _loader)
    except InheritError as exc:
        raise click.ClickException(str(exc))

    if show_source:
        click.echo(format_inherit_result(result))
    else:
        click.echo(f"Chain: {' -> '.join(result.chain)}")
        click.echo()
        for k, v in sorted(result.resolved.items()):
            click.echo(f"  {k}={v}")
