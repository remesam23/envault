"""CLI commands for applying merge strategies between profiles."""

import click

from envault.env_merge_strategy import (
    VALID_STRATEGIES,
    MergeStrategyError,
    apply_strategy,
    format_strategy_result,
)
from envault.vault import load_profile, save_profile


@click.group("merge-strategy")
def merge_strategy_cmd():
    """Apply a merge strategy between two profiles."""


@merge_strategy_cmd.command("apply")
@click.argument("base_profile")
@click.argument("incoming_profile")
@click.option(
    "--strategy",
    "-s",
    default="ours",
    show_default=True,
    type=click.Choice(sorted(VALID_STRATEGIES), case_sensitive=False),
    help="Merge strategy to apply.",
)
@click.option(
    "--into",
    "dest_profile",
    default=None,
    help="Save result into this profile (defaults to base_profile).",
)
@click.option("--dry-run", is_flag=True, help="Print result without saving.")
@click.option("--vault", "vault_path", default=".envault", show_default=True)
@click.password_option("--password", prompt="Vault password")
def merge_apply(base_profile, incoming_profile, strategy, dest_profile, dry_run, vault_path, password):
    """Merge INCOMING_PROFILE into BASE_PROFILE using STRATEGY."""
    try:
        base = load_profile(vault_path, base_profile, password)
        incoming = load_profile(vault_path, incoming_profile, password)
        result = apply_strategy(base, incoming, strategy=strategy.lower())
    except MergeStrategyError as exc:
        raise click.ClickException(str(exc))

    click.echo(format_strategy_result(result))

    if not dry_run:
        target = dest_profile or base_profile
        save_profile(vault_path, target, result.merged, password)
        click.echo(f"Saved merged profile → '{target}'")
    else:
        click.echo("(dry-run: nothing saved)")
