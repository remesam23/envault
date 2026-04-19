import pytest
from click.testing import CliRunner
from envault.cli_env_group import group_cmd
from envault.env_group import create_group


@pytest.fixture
def vault(tmp_path):
    return str(tmp_path)


def run(vault_dir, *args):
    runner = CliRunner()
    return runner.invoke(group_cmd, list(args), obj={"vault_dir": vault_dir})


def test_cli_create_group(vault):
    result = run(vault, "create", "staging", "dev", "qa")
    assert result.exit_code == 0
    assert "staging" in result.output
    assert "dev" in result.output


def test_cli_list_no_groups(vault):
    result = run(vault, "list")
    assert result.exit_code == 0
    assert "No groups" in result.output


def test_cli_list_shows_groups(vault):
    create_group(vault, "mygroup", ["a", "b"])
    result = run(vault, "list")
    assert "mygroup" in result.output
    assert "a" in result.output


def test_cli_show_group(vault):
    create_group(vault, "g", ["alpha", "beta"])
    result = run(vault, "show", "g")
    assert "alpha" in result.output
    assert "beta" in result.output


def test_cli_show_missing_group_error(vault):
    result = run(vault, "show", "ghost")
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_cli_add_to_group(vault):
    create_group(vault, "g", ["a"])
    result = run(vault, "add", "g", "b")
    assert result.exit_code == 0
    assert "b" in result.output


def test_cli_delete_group(vault):
    create_group(vault, "g", ["a"])
    result = run(vault, "delete", "g")
    assert result.exit_code == 0
    assert "Deleted" in result.output
