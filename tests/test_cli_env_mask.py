"""CLI tests for mask show and list-sensitive commands."""
import pytest
from click.testing import CliRunner
from envault.cli_env_mask import mask_cmd
from envault.vault import save_profile
import tempfile, os


@pytest.fixture
def vault(tmp_path):
    vdir = str(tmp_path / "vault")
    data = {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "hunter2",
        "API_KEY": "key123",
        "DEBUG": "false",
    }
    save_profile(vdir, "prod", data, "pass")
    return vdir


def run(vault, *args):
    runner = CliRunner()
    return runner.invoke(mask_cmd, [*args, "--vault", vault, "--password", "pass"])


def test_mask_show_hides_password(vault):
    result = run(vault, "show", "prod")
    assert result.exit_code == 0
    assert "DB_PASSWORD=" + "*" * 8 in result.output


def test_mask_show_reveals_non_sensitive(vault):
    result = run(vault, "show", "prod")
    assert "APP_NAME=myapp" in result.output
    assert "DEBUG=false" in result.output


def test_mask_show_reveal_flag(vault):
    runner = CliRunner()
    result = runner.invoke(
        mask_cmd,
        ["show", "prod", "--vault", vault, "--password", "pass", "--reveal"]
    )
    assert result.exit_code == 0
    assert "DB_PASSWORD=hunter2" in result.output


def test_list_sensitive_shows_keys(vault):
    result = run(vault, "list-sensitive", "prod")
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "DB_PASSWORD" in result.output


def test_list_sensitive_no_sensitive_keys(vault):
    from envault.vault import save_profile
    save_profile(vault, "clean", {"HOST": "localhost", "PORT": "5432"}, "pass")
    result = run(vault, "list-sensitive", "clean")
    assert "No sensitive keys detected" in result.output


def test_mask_show_missing_profile(vault):
    result = run(vault, "show", "nonexistent")
    assert result.exit_code != 0
