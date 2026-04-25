"""CLI tests for envault/cli_env_expire.py"""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from datetime import datetime, timezone, timedelta

from envault.cli_env_expire import expire_cmd
from envault.env_expire import set_key_expiry


@pytest.fixture
def vault(tmp_path):
    return str(tmp_path)


@pytest.fixture
def run(vault):
    runner = CliRunner()

    def _run(*args):
        return runner.invoke(expire_cmd, args, obj={"vault_dir": vault})

    return _run, vault


def test_cli_set_expiry_by_days(run):
    invoke, _ = run
    result = invoke("set", "prod", "API_KEY", "--days", "30")
    assert result.exit_code == 0
    assert "Expiry set" in result.output
    assert "API_KEY" in result.output


def test_cli_set_expiry_by_at(run):
    invoke, _ = run
    future = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    result = invoke("set", "prod", "TOKEN", "--at", future)
    assert result.exit_code == 0
    assert "TOKEN" in result.output


def test_cli_get_expiry_shows_value(run):
    invoke, vault = run
    future = datetime.now(timezone.utc) + timedelta(days=7)
    set_key_expiry(vault, "prod", "DB_PASS", future)
    result = invoke("get", "prod", "DB_PASS")
    assert result.exit_code == 0
    assert "DB_PASS" in result.output


def test_cli_get_expiry_expired_shows_label(run):
    invoke, vault = run
    past = datetime.now(timezone.utc) - timedelta(days=1)
    set_key_expiry(vault, "prod", "OLD", past)
    result = invoke("get", "prod", "OLD")
    assert "EXPIRED" in result.output


def test_cli_get_no_expiry_set(run):
    invoke, _ = run
    result = invoke("get", "prod", "MISSING")
    assert result.exit_code == 0
    assert "No expiry" in result.output


def test_cli_clear_expiry(run):
    invoke, vault = run
    future = datetime.now(timezone.utc) + timedelta(days=3)
    set_key_expiry(vault, "prod", "TEMP", future)
    result = invoke("clear", "prod", "TEMP")
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_cli_clear_missing_key_exits_1(run):
    invoke, _ = run
    result = invoke("clear", "prod", "GHOST")
    assert result.exit_code == 1


def test_cli_list_all_expiries(run):
    invoke, vault = run
    set_key_expiry(vault, "staging", "A", datetime.now(timezone.utc) + timedelta(days=1))
    set_key_expiry(vault, "staging", "B", datetime.now(timezone.utc) + timedelta(days=2))
    result = invoke("list", "staging")
    assert "A" in result.output
    assert "B" in result.output


def test_cli_list_expired_only(run):
    invoke, vault = run
    set_key_expiry(vault, "prod", "STALE", datetime.now(timezone.utc) - timedelta(days=1))
    set_key_expiry(vault, "prod", "FRESH", datetime.now(timezone.utc) + timedelta(days=5))
    result = invoke("list", "prod", "--expired-only")
    assert "STALE" in result.output
    assert "FRESH" not in result.output
