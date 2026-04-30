"""CLI commands for policy management."""
import json
import click
from envault.env_policy import (
    PolicyRule, PolicyError,
    set_policy, get_policy, list_policies, remove_policy,
    check_policy, format_policy_result,
)
from envault.vault import load_profile


@click.group("policy")
def policy_cmd():
    """Manage and enforce profile policies."""


@policy_cmd.command("set")
@click.argument("name")
@click.option("--require", multiple=True, metavar="KEY", help="Required key.")
@click.option("--forbid", multiple=True, metavar="KEY", help="Forbidden key.")
@click.option("--key-pattern", default=None, help="Regex all keys must match.")
@click.option("--max-keys", default=None, type=int, help="Maximum number of keys.")
@click.pass_context
def policy_set(ctx, name, require, forbid, key_pattern, max_keys):
    """Create or update a policy rule."""
    vault_dir = ctx.obj["vault_dir"]
    rule = PolicyRule(
        name=name,
        required_keys=list(require),
        forbidden_keys=list(forbid),
        key_pattern=key_pattern,
        max_keys=max_keys,
    )
    set_policy(vault_dir, rule)
    click.echo(f"Policy '{name}' saved.")


@policy_cmd.command("get")
@click.argument("name")
@click.pass_context
def policy_get(ctx, name):
    """Show a policy rule."""
    vault_dir = ctx.obj["vault_dir"]
    rule = get_policy(vault_dir, name)
    if rule is None:
        click.echo(f"Policy '{name}' not found.", err=True)
        raise SystemExit(1)
    click.echo(f"Policy: {rule.name}")
    click.echo(f"  Required keys : {rule.required_keys or '(none)'}")
    click.echo(f"  Forbidden keys: {rule.forbidden_keys or '(none)'}")
    click.echo(f"  Key pattern   : {rule.key_pattern or '(any)'}")
    click.echo(f"  Max keys      : {rule.max_keys or '(unlimited)'}")


@policy_cmd.command("list")
@click.pass_context
def policy_list(ctx):
    """List all defined policies."""
    vault_dir = ctx.obj["vault_dir"]
    names = list_policies(vault_dir)
    if not names:
        click.echo("No policies defined.")
    else:
        for n in names:
            click.echo(n)


@policy_cmd.command("remove")
@click.argument("name")
@click.pass_context
def policy_remove(ctx, name):
    """Remove a policy rule."""
    vault_dir = ctx.obj["vault_dir"]
    try:
        remove_policy(vault_dir, name)
        click.echo(f"Policy '{name}' removed.")
    except PolicyError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@policy_cmd.command("check")
@click.argument("profile")
@click.argument("policy_name")
@click.option("--password", prompt=True, hide_input=True)
@click.pass_context
def policy_check(ctx, profile, policy_name, password):
    """Check a profile against a policy."""
    vault_dir = ctx.obj["vault_dir"]
    rule = get_policy(vault_dir, policy_name)
    if rule is None:
        click.echo(f"Policy '{policy_name}' not found.", err=True)
        raise SystemExit(1)
    data = load_profile(vault_dir, profile, password)
    result = check_policy(data, rule, profile)
    click.echo(format_policy_result(result))
    if not result.ok:
        raise SystemExit(1)
