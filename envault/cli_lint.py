"""CLI commands for linting profiles."""
import click
from envault.vault import load_profile, list_profiles
from envault.lint import lint_profile, format_lint


@click.group('lint')
def lint_cmd():
    """Lint .env profiles for common issues."""


@lint_cmd.command('check')
@click.argument('profile')
@click.option('--vault', default='.envault', show_default=True)
@click.option('--password', prompt=True, hide_input=True)
def lint_check(profile, vault, password):
    """Lint a single profile."""
    try:
        env = load_profile(vault, profile, password)
    except Exception as e:
        raise click.ClickException(str(e))
    result = lint_profile(profile, env)
    click.echo(format_lint(result))
    if not result.ok:
        raise SystemExit(1)


@lint_cmd.command('check-all')
@click.option('--vault', default='.envault', show_default=True)
@click.option('--password', prompt=True, hide_input=True)
def lint_check_all(vault, password):
    """Lint all profiles in the vault."""
    profiles = list_profiles(vault)
    if not profiles:
        click.echo('No profiles found.')
        return
    any_issues = False
    for profile in profiles:
        try:
            env = load_profile(vault, profile, password)
        except Exception as e:
            click.echo(f"[{profile}] ERROR: {e}")
            any_issues = True
            continue
        result = lint_profile(profile, env)
        click.echo(format_lint(result))
        if not result.ok:
            any_issues = True
    if any_issues:
        raise SystemExit(1)
