"""CLI integration tests for envault resolve commands."""
from __future__ import annotations

import json
import os
import tempfile

import pytest
from click.testing import CliRunner

from envault.vault import save_profile
from envault.cli_env_resolve import resolve_cmd

PASSWORD = "testpass"


@pytest.fixture()
def vault(tmp_path):
    return str(tmp_path / "vault")


def run(vault_path, *args, password=PASSWORD):
    runner = CliRunner()
    return runner.invoke(
        resolve_cmd,
        ["run", *args, "--vault", vault_path, "--password", password],
        catch_exceptions=False,
    )


def test_cli_resolve_no_placeholders(vault):
    save_profile(vault, "prod", {"HOST": "localhost"}, PASSWORD)
    result = run(vault, "prod")
    assert result.exit_code == 0
    assert "no placeholders" in result.output.lower()


def test_cli_resolve_substitutes_self_ref(vault):
    save_profile(vault, "prod", {"BASE": "http://x.com", "URL": "${BASE}/api"}, PASSWORD)
    result = run(vault, "prod", "--json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["URL"] == "http://x.com/api"


def test_cli_resolve_uses_defaults_profile(vault):
    save_profile(vault, "defaults", {"BASE": "http://default.com"}, PASSWORD)
    save_profile(vault, "prod", {"URL": "${BASE}/v1"}, PASSWORD)
    result = run(vault, "prod", "--defaults-profile", "defaults", "--json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["URL"] == "http://default.com/v1"


def test_cli_resolve_strict_exits_1_on_missing(vault):
    save_profile(vault, "prod", {"URL": "${MISSING}/path"}, PASSWORD)
    runner = CliRunner()
    result = runner.invoke(
        resolve_cmd,
        ["run", "prod", "--vault", vault, "--password", PASSWORD, "--strict"],
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_cli_resolve_json_output_contains_all_keys(vault):
    save_profile(vault, "dev", {"A": "1", "B": "2"}, PASSWORD)
    result = run(vault, "dev", "--json")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert set(data.keys()) == {"A", "B"}
