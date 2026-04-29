"""CLI-level tests for envault signature commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_env_signature import signature_cmd
from envault.env_signature import sign_profile
from envault.vault import save_profile

SECRET = "test-secret"
PASSWORD = "vault-pass"
DATA = {"API_KEY": "abc123", "DEBUG": "false"}


@pytest.fixture()
def vault(tmp_path):
    save_profile(str(tmp_path), "prod", DATA, PASSWORD)
    return str(tmp_path)


def run(vault_dir, *args):
    runner = CliRunner()
    return runner.invoke(signature_cmd, list(args) + ["--vault", vault_dir])


def test_cli_sign_outputs_signature(vault):
    result = run(vault, "sign", "prod", "--secret", SECRET, "--password", PASSWORD)
    assert result.exit_code == 0
    assert "Signed profile 'prod'" in result.output
    assert "Signature" in result.output


def test_cli_verify_valid_exits_0(vault):
    sign_profile(vault, "prod", DATA, SECRET)
    result = run(vault, "verify", "prod", "--secret", SECRET, "--password", PASSWORD)
    assert result.exit_code == 0
    assert "VALID" in result.output


def test_cli_verify_no_signature_exits_nonzero(vault):
    result = run(vault, "verify", "prod", "--secret", SECRET, "--password", PASSWORD)
    assert result.exit_code != 0
    assert "INVALID" in result.output


def test_cli_remove_signature(vault):
    sign_profile(vault, "prod", DATA, SECRET)
    result = run(vault, "remove", "prod")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_cli_remove_missing_signature_exits_1(vault):
    result = run(vault, "remove", "prod")
    assert result.exit_code == 1
    assert "Error" in result.output


def test_cli_list_shows_signed_profiles(vault):
    sign_profile(vault, "prod", DATA, SECRET)
    result = run(vault, "list")
    assert result.exit_code == 0
    assert "prod" in result.output


def test_cli_list_empty_vault(vault):
    result = run(vault, "list")
    assert result.exit_code == 0
    assert "No signatures" in result.output
