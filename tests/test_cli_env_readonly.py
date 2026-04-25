"""Tests for the readonly CLI commands."""
import pytest
from click.testing import CliRunner

from envault.cli_env_readonly import readonly_cmd
from envault.env_readonly import set_readonly


@pytest.fixture
def vault(tmp_path):
    return str(tmp_path)


def run(vault_dir, *args):
    runner = CliRunner()
    return runner.invoke(readonly_cmd, ["--vault", vault_dir, *args])


def test_cli_set_marks_profile(vault):
    result = run(vault, "set", "production")
    assert result.exit_code == 0
    assert "read-only" in result.output


def test_cli_set_with_reason_shows_reason(vault):
    result = run(vault, "set", "prod", "--reason", "stable")
    assert result.exit_code == 0
    assert "stable" in result.output


def test_cli_unset_removes_profile(vault):
    set_readonly(vault, "prod")
    result = run(vault, "unset", "prod")
    assert result.exit_code == 0
    assert "no longer read-only" in result.output


def test_cli_unset_not_set_shows_error(vault):
    result = run(vault, "unset", "dev")
    assert result.exit_code != 0
    assert "not marked as read-only" in result.output


def test_cli_status_readonly(vault):
    set_readonly(vault, "prod", reason="live")
    result = run(vault, "status", "prod")
    assert result.exit_code == 0
    assert "yes" in result.output
    assert "live" in result.output


def test_cli_status_not_readonly(vault):
    result = run(vault, "status", "dev")
    assert result.exit_code == 0
    assert "no" in result.output


def test_cli_list_no_entries(vault):
    result = run(vault, "list")
    assert result.exit_code == 0
    assert "No read-only" in result.output


def test_cli_list_shows_profiles(vault):
    set_readonly(vault, "prod", reason="freeze")
    set_readonly(vault, "staging")
    result = run(vault, "list")
    assert result.exit_code == 0
    assert "prod" in result.output
    assert "staging" in result.output
    assert "freeze" in result.output
