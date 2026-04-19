"""CLI commands for profile statistics."""
import click
from envault.vault import load_profile, list_profiles
from envault.env_stats import compute_stats, format_stats


@click.group("stats")
def stats_cmd():
    """Show statistics for vault profiles."""


@stats_cmd.command("show")
@click.argument("profile")
@click.option("--vault", default=".envault", show_default=True)
@click.password_option("--password", prompt="Password", confirmation_prompt=False)
def stats_show(profile: str, vault: str, password: str):
    """Show statistics for a single profile."""
    try:
        data = load_profile(vault, profile, password)
    except KeyError:
        raise click.ClickException(f"Profile '{profile}' not found.")
    except Exception as e:
        raise click.ClickException(str(e))

    stats = compute_stats(profile, data)
    click.echo(format_stats(stats))


@stats_cmd.command("all")
@click.option("--vault", default=".envault", show_default=True)
@click.password_option("--password", prompt="Password", confirmation_prompt=False)
def stats_all(vault: str, password: str):
    """Show statistics for all profiles."""
    profiles = list_profiles(vault)
    if not profiles:
        click.echo("No profiles found.")
        return

    for name in profiles:
        try:
            data = load_profile(vault, name, password)
            stats = compute_stats(name, data)
            click.echo(format_stats(stats))
            click.echo("-" * 36)
        except Exception as e:
            click.echo(f"[{name}] Error: {e}")
