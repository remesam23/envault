"""Integration tests for copy CLI command."""

from click.testing import CliRunner
from envault.cli_copy import copy_cmd
from envault.vault import save_profile, load_profile


PASSWORD = "cli-pass"


def test_cli_copy_all_keys(tmp_path):
    vault = str(tmp_path / "vault")
    save_profile(vault, "dev", {"FOO": "bar", "BAZ": "qux"}, PASSWORD)
    runner = CliRunner()
    result = runner.invoke(
        copy_cmd,
        ["dev", "prod", "--vault", vault, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    assert "Copied" in result.output
    loaded = load_profile(vault, "prod", PASSWORD)
    assert loaded["FOO"] == "bar"


def test_cli_copy_specific_key(tmp_path):
    vault = str(tmp_path / "vault")
    save_profile(vault, "dev", {"A": "1", "B": "2"}, PASSWORD)
    runner = CliRunner()
    result = runner.invoke(
        copy_cmd,
        ["dev", "prod", "--key", "A", "--vault", vault, "--password", PASSWORD],
    )
    assert result.exit_code == 0
    loaded = load_profile(vault, "prod", PASSWORD)
    assert "A" in loaded
    assert "B" not in loaded


def test_cli_copy_missing_key_error(tmp_path):
    vault = str(tmp_path / "vault")
    save_profile(vault, "dev", {"A": "1"}, PASSWORD)
    runner = CliRunner()
    result = runner.invoke(
        copy_cmd,
        ["dev", "prod", "--key", "NOPE", "--vault", vault, "--password", PASSWORD],
    )
    assert result.exit_code != 0
    assert "Keys not found" in result.output
