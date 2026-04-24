"""CLI integration tests for lint-fix commands."""
import os
import pytest
from click.testing import CliRunner

from envault.cli_env_lint_fix import lint_fix_cmd
from envault.vault import save_profile, load_profile


@pytest.fixture()
def vault(tmp_path):
    return str(tmp_path)


def run(vault_dir, *args):
    runner = CliRunner()
    return runner.invoke(lint_fix_cmd, ["run"] + list(args) + ["--vault-dir", vault_dir])


def test_cli_fix_uppercases_keys(vault):
    save_profile(vault, "dev", "pass", {"db_host": "localhost"})
    result = run(vault, "dev", "pass")
    assert result.exit_code == 0
    data = load_profile(vault, "dev", "pass")
    assert "DB_HOST" in data
    assert "db_host" not in data


def test_cli_fix_strips_values(vault):
    save_profile(vault, "dev", "pass", {"KEY": "  value  "})
    result = run(vault, "dev", "pass")
    assert result.exit_code == 0
    data = load_profile(vault, "dev", "pass")
    assert data["KEY"] == "value"


def test_cli_dry_run_does_not_write(vault):
    save_profile(vault, "dev", "pass", {"lower": "val"})
    result = run(vault, "dev", "pass", "--dry-run")
    assert result.exit_code == 0
    assert "dry-run" in result.output
    data = load_profile(vault, "dev", "pass")
    # original data unchanged
    assert "lower" in data


def test_cli_remove_empty_drops_key(vault):
    save_profile(vault, "dev", "pass", {"KEY": "val", "EMPTY": ""})
    result = run(vault, "dev", "pass", "--remove-empty")
    assert result.exit_code == 0
    data = load_profile(vault, "dev", "pass")
    assert "EMPTY" not in data
    assert "KEY" in data


def test_cli_no_fix_case_leaves_lowercase(vault):
    save_profile(vault, "dev", "pass", {"lower": "val"})
    result = run(vault, "dev", "pass", "--no-fix-case")
    assert result.exit_code == 0
    data = load_profile(vault, "dev", "pass")
    assert "lower" in data


def test_cli_shows_applied_fixes_in_output(vault):
    save_profile(vault, "dev", "pass", {"lower_key": "val"})
    result = run(vault, "dev", "pass")
    assert "lower_key" in result.output or "Applied" in result.output
