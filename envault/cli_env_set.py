"""CLI commands for bulk set/unset of profile keys."""
import click
from envault.vault import load_profile, save_profile
from envault.env_set import set_keys, format_set_result
from envault.audit import record_event


@click.group("set")
def set_cmd():
    """Set or unset keys in a profile."""


@set_cmd.command("key")
@click.argument("profile")
@click.argument("pairs", nargs=-1, required=True, metavar="KEY=VALUE...")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--no-overwrite", is_flag=True, default=False)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def set_key(profile, pairs, password, no_overwrite, vault_path):
    """Set KEY=VALUE pairs in a profile."""
    updates = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Invalid format (expected KEY=VALUE): {pair}")
        k, v = pair.split("=", 1)
        updates[k.strip()] = v

    data = load_profile(vault_path, profile, password)
    new_data, result = set_keys(data, updates, overwrite=not no_overwrite)
    save_profile(vault_path, profile, new_data, password)
    record_event(vault_path, "set_keys", profile, {"keys": list(updates.keys())})
    click.echo(f"Profile '{profile}' updated:")
    click.echo(format_set_result(result))


@set_cmd.command("unset")
@click.argument("profile")
@click.argument("keys", nargs=-1, required=True)
@click.option("--password", prompt=True, hide_input=True)
@click.option("--vault", "vault_path", default=".envault", show_default=True)
def unset_key(profile, keys, password, vault_path):
    """Remove keys from a profile."""
    updates = {k: None for k in keys}
    data = load_profile(vault_path, profile, password)
    new_data, result = set_keys(data, updates)
    save_profile(vault_path, profile, new_data, password)
    record_event(vault_path, "unset_keys", profile, {"keys": list(keys)})
    click.echo(f"Profile '{profile}' updated:")
    click.echo(format_set_result(result))
