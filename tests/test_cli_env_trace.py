"""CLI integration tests for env-trace."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_env_trace import trace_cmd
from envault.env_trace import record_access


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    return tmp_path


def run(vault: Path, *args):
    runner = CliRunner()
    return runner.invoke(trace_cmd, [*args, "--vault", str(vault)])


def test_cli_record_outputs_entry(vault):
    result = run(vault, "record", "prod", "DB_URL")
    assert result.exit_code == 0
    assert "prod::DB_URL" in result.output


def test_cli_record_with_context(vault):
    result = run(vault, "record", "dev", "SECRET", "--context", "deploy")
    assert result.exit_code == 0
    assert "[deploy]" in result.output


def test_cli_list_shows_entries(vault):
    record_access(vault, "prod", "DB_URL")
    record_access(vault, "prod", "API_KEY")
    result = run(vault, "list")
    assert result.exit_code == 0
    assert "prod::DB_URL" in result.output
    assert "prod::API_KEY" in result.output


def test_cli_list_empty(vault):
    result = run(vault, "list")
    assert result.exit_code == 0
    assert "No trace" in result.output


def test_cli_list_filter_by_profile(vault):
    record_access(vault, "prod", "DB_URL")
    record_access(vault, "dev", "SECRET")
    result = run(vault, "list", "--profile", "dev")
    assert result.exit_code == 0
    assert "dev::SECRET" in result.output
    assert "prod" not in result.output


def test_cli_clear_all(vault):
    record_access(vault, "prod", "DB_URL")
    record_access(vault, "dev", "API_KEY")
    result = run(vault, "clear")
    assert result.exit_code == 0
    assert "2" in result.output
    list_result = run(vault, "list")
    assert "No trace" in list_result.output


def test_cli_clear_by_profile(vault):
    record_access(vault, "prod", "DB_URL")
    record_access(vault, "dev", "API_KEY")
    result = run(vault, "clear", "--profile", "prod")
    assert result.exit_code == 0
    assert "1" in result.output
    list_result = run(vault, "list")
    assert "dev::API_KEY" in list_result.output
    assert "prod" not in list_result.output
