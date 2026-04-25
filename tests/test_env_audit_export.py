"""Tests for env_audit_export.py."""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from envault.audit import record_event
from envault.env_audit_export import AuditExportError, export_audit


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def _populate(vault_path: str) -> None:
    record_event(vault_path, "lock", profile="prod", detail="locked")
    record_event(vault_path, "unlock", profile="prod", detail="unlocked")
    record_event(vault_path, "lock", profile="dev", detail="locked")


def test_text_format_contains_event(tmp_vault):
    _populate(tmp_vault)
    result = export_audit(tmp_vault, fmt="text")
    assert "lock" in result
    assert "unlock" in result


def test_text_format_contains_profile(tmp_vault):
    _populate(tmp_vault)
    result = export_audit(tmp_vault, fmt="text")
    assert "profile=prod" in result
    assert "profile=dev" in result


def test_text_empty_vault_returns_placeholder(tmp_vault):
    result = export_audit(tmp_vault, fmt="text")
    assert result == "(no audit events)"


def test_json_format_is_valid_json(tmp_vault):
    _populate(tmp_vault)
    result = export_audit(tmp_vault, fmt="json")
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) == 3


def test_json_format_contains_expected_keys(tmp_vault):
    _populate(tmp_vault)
    result = export_audit(tmp_vault, fmt="json")
    data = json.loads(result)
    for entry in data:
        assert "event" in entry
        assert "profile" in entry
        assert "timestamp" in entry


def test_csv_format_has_header(tmp_vault):
    _populate(tmp_vault)
    result = export_audit(tmp_vault, fmt="csv")
    first_line = result.splitlines()[0]
    assert "timestamp" in first_line
    assert "event" in first_line
    assert "profile" in first_line


def test_csv_format_row_count(tmp_vault):
    _populate(tmp_vault)
    result = export_audit(tmp_vault, fmt="csv")
    # 1 header + 3 data rows
    assert len(result.strip().splitlines()) == 4


def test_csv_empty_vault_returns_empty_string(tmp_vault):
    result = export_audit(tmp_vault, fmt="csv")
    assert result == ""


def test_filter_by_profile(tmp_vault):
    _populate(tmp_vault)
    result = export_audit(tmp_vault, fmt="text", profile="dev")
    assert "profile=dev" in result
    assert "profile=prod" not in result


def test_unsupported_format_raises(tmp_vault):
    with pytest.raises(AuditExportError, match="Unsupported format"):
        export_audit(tmp_vault, fmt="xml")


def test_text_detail_included(tmp_vault):
    record_event(tmp_vault, "rotate", profile="staging", detail="password changed")
    result = export_audit(tmp_vault, fmt="text")
    assert "password changed" in result
