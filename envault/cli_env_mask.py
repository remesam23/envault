"""CLI commands for masked profile display."""
import click
from envault.vault import load_profile
from envault.env_mask import mask_profile, format_mask_result


@click.group("mask")
def mask_cmd():
    """Display profiles with sensitive values masked."""


@mask_cmd.command("show")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--reveal", is_flag=True, default=False, help="Show all values unmasked.")
@click.option("--extra", multiple=True, help="Additional keys to mask.")
@click.option("--pattern", multiple=True, help="Extra regex patterns for sensitive keys.")
def mask_show(profile, vault, password, reveal, extra, pattern):
    """Show a profile with sensitive values masked."""
    try:
        data = load_profile(vault, profile, password)
    except Exception as e:
        raise click.ClickException(str(e))

    from envault.env_mask import DEFAULT_PATTERNS
    patterns = list(DEFAULT_PATTERNS) + list(pattern)
    result = mask_profile(data, patterns=patterns, extra_keys=list(extra), reveal=reveal)

    if result.redacted_keys:
        click.echo(f"# Redacted keys: {', '.join(sorted(result.redacted_keys))}")
    click.echo(format_mask_result(result))


@mask_cmd.command("list-sensitive")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--pattern", multiple=True)
def list_sensitive(profile, vault, password, pattern):
    """List which keys would be masked in a profile."""
    try:
        data = load_profile(vault, profile, password)
    except Exception as e:
        raise click.ClickException(str(e))

    from envault.env_mask import DEFAULT_PATTERNS
    patterns = list(DEFAULT_PATTERNS) + list(pattern)
    result = mask_profile(data, patterns=patterns)
    if result.redacted_keys:
        for k in sorted(result.redacted_keys):
            click.echo(k)
    else:
        click.echo("No sensitive keys detected.")
