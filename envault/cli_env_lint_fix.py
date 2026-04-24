"""CLI commands for auto-fixing lint issues in a profile."""
import click

from envault.vault import load_profile, save_profile
from envault.env_lint_fix import fix_profile, format_fix_result


@click.group("lint-fix")
def lint_fix_cmd() -> None:
    """Auto-fix lint issues in a profile."""


@lint_fix_cmd.command("run")
@click.argument("profile")
@click.argument("password")
@click.option("--vault-dir", default=".envault", show_default=True)
@click.option("--no-fix-case", is_flag=True, default=False, help="Skip key case fixes.")
@click.option("--no-strip-values", is_flag=True, default=False, help="Skip value stripping.")
@click.option("--remove-empty", is_flag=True, default=False, help="Remove keys with empty values.")
@click.option("--dry-run", is_flag=True, default=False, help="Show fixes without applying them.")
def fix_run(
    profile: str,
    password: str,
    vault_dir: str,
    no_fix_case: bool,
    no_strip_values: bool,
    remove_empty: bool,
    dry_run: bool,
) -> None:
    """Auto-fix lint issues in PROFILE."""
    try:
        data = load_profile(vault_dir, profile, password)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    result = fix_profile(
        data,
        fix_case=not no_fix_case,
        strip_values=not no_strip_values,
        remove_empty=remove_empty,
    )

    click.echo(format_fix_result(result))

    if dry_run:
        click.echo("(dry-run) No changes written.")
        return

    try:
        save_profile(vault_dir, profile, password, result.fixed)
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Profile '{profile}' updated.")
    if not result.ok:
        raise SystemExit(1)
