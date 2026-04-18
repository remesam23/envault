"""CLI commands for template rendering."""
import click
from envault.vault import load_profile
from envault.template import render_file, list_placeholders, TemplateError


@click.group("template")
def template_cmd():
    """Render .env templates from a vault profile."""


@template_cmd.command("render")
@click.argument("profile")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory")
@click.option("--strict/--no-strict", default=True, show_default=True)
@click.password_option(prompt="Password", confirmation_prompt=False)
def render_cmd(profile, template_file, output, vault, strict, password):
    """Render TEMPLATE_FILE using secrets from PROFILE."""
    try:
        env = load_profile(vault, profile, password)
        rendered = render_file(template_file, env, output_path=output, strict=strict)
        if output:
            click.echo(f"Rendered '{template_file}' -> '{output}'")
        else:
            click.echo(rendered, nl=False)
    except TemplateError as exc:
        raise click.ClickException(str(exc))
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@template_cmd.command("inspect")
@click.argument("template_file", type=click.Path(exists=True))
def inspect_cmd(template_file):
    """List all placeholder variables in TEMPLATE_FILE."""
    with open(template_file, "r", encoding="utf-8") as fh:
        content = fh.read()
    placeholders = list_placeholders(content)
    if not placeholders:
        click.echo("No placeholders found.")
    else:
        click.echo(f"{len(placeholders)} placeholder(s):")
        for name in placeholders:
            click.echo(f"  ${{{{ {name} }}}}")
