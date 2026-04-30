"""CLI tests for policy commands."""
import pytest
from click.testing import CliRunner
from envault.cli_env_policy import policy_cmd
from envault.vault import save_profile
from envault.env_policy import set_policy, PolicyRule


@pytest.fixture
def vault(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


def run(runner, vault, *args):
    return runner.invoke(policy_cmd, list(args), obj={"vault_dir": vault})


def test_cli_set_and_list(runner, vault):
    result = run(runner, vault, "set", "mypolicy", "--require", "DB_URL")
    assert result.exit_code == 0
    assert "saved" in result.output

    result = run(runner, vault, "list")
    assert "mypolicy" in result.output


def test_cli_get_policy(runner, vault):
    set_policy(vault, PolicyRule(name="p1", required_keys=["HOST"], max_keys=10))
    result = run(runner, vault, "get", "p1")
    assert result.exit_code == 0
    assert "HOST" in result.output
    assert "10" in result.output


def test_cli_get_missing_policy_exits_1(runner, vault):
    result = run(runner, vault, "get", "ghost")
    assert result.exit_code == 1


def test_cli_remove_policy(runner, vault):
    set_policy(vault, PolicyRule(name="temp"))
    result = run(runner, vault, "remove", "temp")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_remove_missing_exits_1(runner, vault):
    result = run(runner, vault, "remove", "ghost")
    assert result.exit_code == 1


def test_cli_check_passes(runner, vault):
    password = "secret"
    save_profile(vault, "dev", {"HOST": "localhost", "PORT": "5432"}, password)
    set_policy(vault, PolicyRule(name="base", required_keys=["HOST"]))
    result = run(runner, vault, "check", "dev", "base", f"--password={password}")
    assert result.exit_code == 0
    assert "OK" in result.output


def test_cli_check_fails_missing_key(runner, vault):
    password = "secret"
    save_profile(vault, "dev", {"HOST": "localhost"}, password)
    set_policy(vault, PolicyRule(name="strict", required_keys=["API_KEY"]))
    result = run(runner, vault, "check", "dev", "strict", f"--password={password}")
    assert result.exit_code == 1
    assert "FAIL" in result.output
