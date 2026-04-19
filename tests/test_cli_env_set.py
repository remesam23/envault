import pytest
from click.testing import CliRunner
from envault.cli_env_set import set_cmd
from envault.vault import save_profile, load_profile


@pytest.fixture
def vault(tmp_path):
    vp = str(tmp_path / "vault")
    save_profile(vp, "dev", {"HOST": "localhost", "PORT": "5432"}, "pass")
    return vp


def run(vault_path, *args):
    runner = CliRunner()
    return runner.invoke(set_cmd, [*args, "--vault", vault_path], catch_exceptions=False)


def test_cli_set_adds_key(vault):
    result = run(vault, "key", "dev", "NEW=value", "--password", "pass")
    assert result.exit_code == 0
    assert "added" in result.output
    data = load_profile(vault, "dev", "pass")
    assert data["NEW"] == "value"


def test_cli_set_updates_key(vault):
    result = run(vault, "key", "dev", "HOST=remotehost", "--password", "pass")
    assert result.exit_code == 0
    assert "updated" in result.output
    data = load_profile(vault, "dev", "pass")
    assert data["HOST"] == "remotehost"


def test_cli_set_no_overwrite_skips(vault):
    result = run(vault, "key", "dev", "HOST=other", "--no-overwrite", "--password", "pass")
    assert result.exit_code == 0
    assert "skipped" in result.output
    data = load_profile(vault, "dev", "pass")
    assert data["HOST"] == "localhost"


def test_cli_unset_removes_key(vault):
    result = run(vault, "unset", "dev", "PORT", "--password", "pass")
    assert result.exit_code == 0
    assert "deleted" in result.output
    data = load_profile(vault, "dev", "pass")
    assert "PORT" not in data


def test_cli_unset_missing_key_skips(vault):
    result = run(vault, "unset", "dev", "NONEXISTENT", "--password", "pass")
    assert result.exit_code == 0
    assert "skipped" in result.output


def test_cli_set_invalid_pair_format(vault):
    runner = CliRunner()
    result = runner.invoke(
        set_cmd,
        ["key", "dev", "BADFORMAT", "--password", "pass", "--vault", vault],
    )
    assert result.exit_code != 0
