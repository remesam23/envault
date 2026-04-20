"""CLI tests for envault cast commands."""
import json
import os
import tempfile

import pytest
from click.testing import CliRunner

from envault.cli_env_cast import cast_cmd
from envault.vault import save_profile


@pytest.fixture
def vault(tmp_path):
    vpath = str(tmp_path / "vault.db")
    save_profile(vpath, "dev", {"PORT": "8080", "DEBUG": "true", "APP": "myapp"}, "secret")
    return vpath


def run(vault_path, profile, schema_json, password="secret", extra_args=None):
    runner = CliRunner()
    args = ["run", profile, vault_path, password, "--schema", schema_json]
    if extra_args:
        args.extend(extra_args)
    return runner.invoke(cast_cmd, args)


def test_cli_cast_basic(vault):
    result = run(vault, "dev", '{"PORT": "int", "DEBUG": "bool"}')
    assert result.exit_code == 0
    assert "PORT" in result.output
    assert "int" in result.output


def test_cli_cast_json_output(vault):
    result = run(vault, "dev", '{"PORT": "int"}', extra_args=["--json-out"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["PORT"] == 8080


def test_cli_cast_strict_error_exits_1(vault):
    result = run(vault, "dev", '{"APP": "int"}', extra_args=["--strict"])
    assert result.exit_code == 1


def test_cli_cast_invalid_schema_exits_2(vault):
    result = run(vault, "dev", "not-json")
    assert result.exit_code == 2


def test_cli_cast_wrong_password_exits_1(vault):
    result = run(vault, "dev", '{"PORT": "int"}', password="wrong")
    assert result.exit_code == 1


def test_cli_cast_bool_in_json_output(vault):
    result = run(vault, "dev", '{"DEBUG": "bool"}', extra_args=["--json-out"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["DEBUG"] is True
