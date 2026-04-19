"""CLI tests for rename-key command."""
import pytest
from click.testing import CliRunner
from envault.cli_env_rename_key import rename_key_cmd
from envault.vault import save_profile, load_profile

PASSWORD = "secret"


@pytest.fixture
def vault(tmp_path):
    v = tmp_path / "vault"
    save_profile(v, "dev", PASSWORD, {"OLD": "val", "KEEP": "yes"})
    return v


def run(vault, *args):
    runner = CliRunner()
    return runner.invoke(rename_key_cmd, ["run", "--vault", str(vault), "--password", PASSWORD, *args])


def test_cli_rename_key_success(vault):
    result = run(vault, "dev", "OLD", "NEW")
    assert result.exit_code == 0
    assert "OLD" in result.output
    assert "NEW" in result.output
    data = load_profile(vault, "dev", PASSWORD)
    assert "NEW" in data
    assert "OLD" not in data


def test_cli_rename_key_missing_key_exits_2(vault):
    result = run(vault, "dev", "MISSING", "NEW")
    assert result.exit_code == 2
    assert "Error" in result.output


def test_cli_rename_key_conflict_exits_1(vault):
    result = run(vault, "dev", "OLD", "KEEP")
    assert result.exit_code == 1
    assert "Skipped" in result.output


def test_cli_rename_key_overwrite_flag(vault):
    result = run(vault, "dev", "OLD", "KEEP", "--overwrite")
    assert result.exit_code == 0
    data = load_profile(vault, "dev", PASSWORD)
    assert data["KEEP"] == "val"
