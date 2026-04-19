"""Tests for envault CLI history commands."""
import os
import pytest
from click.testing import CliRunner
from envault.cli_history import history_cmd
from envault.history import record_snapshot


@pytest.fixture
def vault(tmp_path):
    v = str(tmp_path / ".envault")
    os.makedirs(v, exist_ok=True)
    return v


def run(vault_dir, *args):
    runner = CliRunner()
    return runner.invoke(history_cmd, ["--vault", vault_dir, *args])


def test_list_no_history(vault):
    result = run(vault, "list", "dev")
    assert result.exit_code == 0
    assert "No history found" in result.output


def test_list_shows_entries(vault):
    record_snapshot(vault, "dev", {"FOO": "bar"})
    result = run(vault, "list", "dev")
    assert result.exit_code == 0
    assert "FOO" in result.output


def test_list_show_values(vault):
    record_snapshot(vault, "dev", {"TOKEN": "secret"})
    result = run(vault, "list", "dev", "--show-values")
    assert result.exit_code == 0
    assert "TOKEN=secret" in result.output


def test_show_specific_entry(vault):
    record_snapshot(vault, "dev", {"A": "1"})
    result = run(vault, "show", "dev", "0")
    assert result.exit_code == 0
    assert "A=1" in result.output


def test_show_out_of_range(vault):
    record_snapshot(vault, "dev", {"A": "1"})
    result = run(vault, "show", "dev", "5")
    assert result.exit_code == 1
    assert "out of range" in result.output


def test_show_no_history(vault):
    result = run(vault, "show", "dev", "0")
    assert result.exit_code == 1
    assert "No history" in result.output


def test_clear_history(vault):
    record_snapshot(vault, "dev", {"X": "1"})
    runner = CliRunner()
    result = runner.invoke(
        history_cmd, ["--vault", vault, "clear", "dev"], input="y\n"
    )
    assert result.exit_code == 0
    assert "Cleared 1" in result.output
