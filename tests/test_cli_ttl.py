"""CLI tests for TTL commands."""
import pytest
from click.testing import CliRunner
from envault.cli_ttl import ttl_cmd


@pytest.fixture
def vault(tmp_path):
    return str(tmp_path)


def run(vault_dir, *args):
    runner = CliRunner()
    return runner.invoke(ttl_cmd, ["--vault", vault_dir] + list(args))


def test_cli_set_ttl(vault):
    result = run(vault, "set", "prod", "60")
    assert result.exit_code == 0
    assert "expires at" in result.output


def test_cli_get_ttl_shows_expiry(vault):
    run(vault, "set", "prod", "3600")
    result = run(vault, "get", "prod")
    assert result.exit_code == 0
    assert "prod" in result.output


def test_cli_get_ttl_no_entry(vault):
    result = run(vault, "get", "ghost")
    assert "No TTL" in result.output


def test_cli_clear_ttl(vault):
    run(vault, "set", "prod", "60")
    result = run(vault, "clear", "prod")
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_cli_clear_missing_exits_1(vault):
    result = run(vault, "clear", "ghost")
    assert result.exit_code == 1


def test_cli_list_empty(vault):
    result = run(vault, "list")
    assert "No TTL" in result.output


def test_cli_list_shows_profiles(vault):
    run(vault, "set", "dev", "60")
    run(vault, "set", "prod", "120")
    result = run(vault, "list")
    assert "dev" in result.output
    assert "prod" in result.output
