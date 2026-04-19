import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_env_check import check_cmd
from envault.vault import save_profile


@pytest.fixture
def vault(tmp_path):
    return str(tmp_path / "vault")


@pytest.fixture
def ref_file(tmp_path):
    f = tmp_path / ".env.reference"
    f.write_text("HOST=localhost\nPORT=5432\nSECRET=abc\n")
    return str(f)


def run(args):
    return CliRunner().invoke(check_cmd, args, catch_exceptions=False)


def test_cli_check_shows_missing(vault, ref_file):
    save_profile(vault, "dev", {"HOST": "localhost", "PORT": "5432"}, "pass")
    result = CliRunner().invoke(
        check_cmd, ["run", "dev", ref_file, "--vault", vault, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "SECRET" in result.output


def test_cli_check_ok_when_matching(vault, ref_file):
    save_profile(vault, "dev", {"HOST": "localhost", "PORT": "5432", "SECRET": "abc"}, "pass")
    result = CliRunner().invoke(
        check_cmd, ["run", "dev", ref_file, "--vault", vault, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "✓" in result.output


def test_cli_check_strict_exits_1_on_mismatch(vault, ref_file):
    save_profile(vault, "dev", {"HOST": "localhost"}, "pass")
    result = CliRunner().invoke(
        check_cmd,
        ["run", "dev", ref_file, "--vault", vault, "--password", "pass", "--strict"],
    )
    assert result.exit_code == 1
