"""CLI integration tests for compare command."""
import pytest
from click.testing import CliRunner
from envault.cli_compare import compare_cmd
from envault.vault import save_profile


PASSWORD = "secret"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault(tmp_path):
    v = str(tmp_path / "vault")
    save_profile(v, "dev", {"KEY": "dev_val", "SHARED": "same"}, PASSWORD)
    save_profile(v, "prod", {"KEY": "prod_val", "SHARED": "same", "EXTRA": "only_prod"}, PASSWORD)
    return v


def run(runner, vault, *args):
    return runner.invoke(
        compare_cmd,
        ["run", *args, "--vault", vault, "--password", PASSWORD],
        catch_exceptions=False,
    )


def test_cli_compare_different_exits_1(runner, vault):
    result = run(runner, vault, "dev", "prod")
    assert result.exit_code == 1


def test_cli_compare_identical_exits_0(runner, vault):
    save_profile(vault, "copy", {"KEY": "dev_val", "SHARED": "same"}, PASSWORD)
    result = run(runner, vault, "dev", "copy")
    assert result.exit_code == 0


def test_cli_compare_output_contains_profiles(runner, vault):
    result = run(runner, vault, "dev", "prod")
    assert "dev" in result.output
    assert "prod" in result.output


def test_cli_compare_summary_flag(runner, vault):
    result = run(runner, vault, "dev", "prod", "--summary")
    assert "key(s)" in result.output
    assert "Comparing" not in result.output
