"""CLI commands for comparing two profiles."""
import click
from envault.compare import compare_profiles, format_compare


@click.group("compare")
def compare_cmd():
    """Compare two vault profiles."""


@compare_cmd.command("run")
@click.argument("profile_a")
@click.argument("profile_b")
@click.option("--vault", default=".envault", show_default=True, help="Vault directory")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
@click.option("--summary", is_flag=True, default=False, help="Show summary only")
def compare_run(profile_a: str, profile_b: str, vault: str, password: str, summary: bool):
    """Compare PROFILE_A and PROFILE_B."""
    try:
        report = compare_profiles(vault, profile_a, profile_b, password)
        if summary:
            for line in report.summary:
                click.echo(line)
        else:
            click.echo(format_compare(report))
        if report.identical:
            raise SystemExit(0)
        raise SystemExit(1)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
