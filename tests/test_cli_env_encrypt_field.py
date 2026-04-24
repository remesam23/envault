"""CLI integration tests for field-level encryption commands."""

import os
import pytest
from click.testing import CliRunner

from envault.cli_env_encrypt_field import field_cmd
from envault.vault import save_profile, load_profile
from envault.env_encrypt_field import is_field_encrypted, FIELD_CIPHER_PREFIX

PASSWORD = "cli-test-pass"


@pytest.fixture
def vault(tmp_path):
    vault_dir = str(tmp_path / ".envault")
    os.makedirs(vault_dir)
    data = {"SECRET": "topsecret", "HOST": "localhost"}
    save_profile(vault_dir, "prod", data, PASSWORD)
    return vault_dir


def run(vault_dir, *args):
    runner = CliRunner()
    return runner.invoke(
        field_cmd,
        ["--vault", vault_dir] + list(args),
        catch_exceptions=False,
    )


def test_cli_encrypt_field_marks_key(vault):
    result = run(vault, "encrypt", "prod", "SECRET", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "Encrypted" in result.output
    data = load_profile(vault, "prod", PASSWORD)
    assert is_field_encrypted(data["SECRET"])


def test_cli_encrypt_does_not_touch_other_keys(vault):
    run(vault, "encrypt", "prod", "SECRET", "--password", PASSWORD)
    data = load_profile(vault, "prod", PASSWORD)
    assert data["HOST"] == "localhost"


def test_cli_encrypt_already_encrypted_shows_skipped(vault):
    run(vault, "encrypt", "prod", "SECRET", "--password", PASSWORD)
    result = run(vault, "encrypt", "prod", "SECRET", "--password", PASSWORD)
    assert "Already encrypted" in result.output


def test_cli_decrypt_field_restores_value(vault):
    run(vault, "encrypt", "prod", "SECRET", "--password", PASSWORD)
    result = run(vault, "decrypt", "prod", "SECRET", "--password", PASSWORD)
    assert result.exit_code == 0
    assert "Decrypted" in result.output
    data = load_profile(vault, "prod", PASSWORD)
    assert data["SECRET"] == "topsecret"


def test_cli_decrypt_plain_key_shows_not_encrypted(vault):
    result = run(vault, "decrypt", "prod", "HOST", "--password", PASSWORD)
    assert "Not encrypted" in result.output


def test_cli_encrypt_missing_key_shows_skipped(vault):
    result = run(vault, "encrypt", "prod", "DOES_NOT_EXIST", "--password", PASSWORD)
    assert "Key not found" in result.output
