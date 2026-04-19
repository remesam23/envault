import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_schema import schema_cmd
from envault.vault import save_profile


@pytest.fixture
def vault(tmp_path):
    return str(tmp_path / "vault")


@pytest.fixture
def schema_file(tmp_path):
    spec = {
        "API_KEY": {"required": True},
        "ENV": {"required": True, "allowed": ["dev", "prod"]},
    }
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(spec))
    return str(p)


def run(vault, args, password="secret"):
    runner = CliRunner()
    return runner.invoke(schema_cmd, args, input=password + "\n")


def test_cli_schema_check_passes(vault, schema_file):
    save_profile(vault, "dev", {"API_KEY": "abc123", "ENV": "dev"}, "secret")
    result = run(vault, ["check", "dev", schema_file, "--vault", vault])
    assert result.exit_code == 0
    assert "passed" in result.output.lower()


def test_cli_schema_check_fails_missing_key(vault, schema_file):
    save_profile(vault, "dev", {"API_KEY": "abc123"}, "secret")
    result = run(vault, ["check", "dev", schema_file, "--vault", vault])
    assert result.exit_code == 1
    assert "ENV" in result.output


def test_cli_schema_check_fails_bad_allowed(vault, schema_file):
    save_profile(vault, "dev", {"API_KEY": "abc", "ENV": "staging"}, "secret")
    result = run(vault, ["check", "dev", schema_file, "--vault", vault])
    assert result.exit_code == 1
    assert "ENV" in result.output
