"""CLI integration tests for the 'default apply' command."""
from __future__ import annotations

import json
import os

import pytest
from click.testing import CliRunner

from envault.cli_env_default import default_cmd
from envault.vault import save_profile, load_profile


PASSWORD = "testpass"


@pytest.fixture()
def vault(tmp_path):
    return str(tmp_path / "vault")


@pytest.fixture()
def defaults_file(tmp_path):
    path = tmp_path / "defaults.json"
    path.write_text(json.dumps({"HOST": "localhost", "PORT": "5432"}))
    return str(path)


def run(vault_path, *args):
    runner = CliRunner(mix_stderr=False)
    return runner.invoke(
        default_cmd,
        ["apply", "--vault", vault_path, "--password", PASSWORD, *args],
    )


def test_cli_apply_adds_missing_keys(vault, defaults_file):
    save_profile(vault, "dev", {"APP": "myapp"}, PASSWORD)
    result = run(vault, "dev", defaults_file)
    assert result.exit_code == 0
    data = load_profile(vault, "dev", PASSWORD)
    assert data["HOST"] == "localhost"
    assert data["PORT"] == "5432"
    assert data["APP"] == "myapp"   # untouched


def test_cli_apply_skips_existing_without_overwrite(vault, defaults_file):
    save_profile(vault, "dev", {"HOST": "remotehost"}, PASSWORD)
    result = run(vault, "dev", defaults_file)
    assert result.exit_code == 0
    data = load_profile(vault, "dev", PASSWORD)
    assert data["HOST"] == "remotehost"   # not overwritten
    assert data["PORT"] == "5432"         # filled in


def test_cli_apply_overwrite_flag_replaces_value(vault, defaults_file):
    save_profile(vault, "dev", {"HOST": "remotehost"}, PASSWORD)
    result = run(vault, "dev", defaults_file, "--overwrite")
    assert result.exit_code == 0
    data = load_profile(vault, "dev", PASSWORD)
    assert data["HOST"] == "localhost"


def test_cli_apply_dry_run_does_not_save(vault, defaults_file):
    save_profile(vault, "dev", {}, PASSWORD)
    result = run(vault, "dev", defaults_file, "--dry-run")
    assert result.exit_code == 0
    assert "dry-run" in result.output
    data = load_profile(vault, "dev", PASSWORD)
    assert "HOST" not in data   # nothing written


def test_cli_apply_shows_applied_in_output(vault, defaults_file):
    save_profile(vault, "dev", {}, PASSWORD)
    result = run(vault, "dev", defaults_file)
    assert "HOST" in result.output or "Applied" in result.output
