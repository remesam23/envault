"""Tests for envault.env_lint_fix."""
import pytest

from envault.env_lint_fix import fix_profile, format_fix_result, LintFixError


def test_fix_case_uppercases_keys():
    data = {"db_host": "localhost", "db_port": "5432"}
    result = fix_profile(data, fix_case=True)
    assert "DB_HOST" in result.fixed
    assert "DB_PORT" in result.fixed
    assert "db_host" not in result.fixed


def test_fix_case_preserves_values():
    data = {"db_host": "localhost"}
    result = fix_profile(data, fix_case=True)
    assert result.fixed["DB_HOST"] == "localhost"


def test_no_fix_case_leaves_keys_unchanged():
    data = {"db_host": "localhost"}
    result = fix_profile(data, fix_case=False)
    assert "db_host" in result.fixed
    assert "DB_HOST" not in result.fixed


def test_strip_values_removes_whitespace():
    data = {"KEY": "  value  "}
    result = fix_profile(data, strip_values=True)
    assert result.fixed["KEY"] == "value"


def test_no_strip_values_leaves_whitespace():
    data = {"KEY": "  value  "}
    result = fix_profile(data, strip_values=False)
    assert result.fixed["KEY"] == "  value  "


def test_remove_empty_drops_empty_keys():
    data = {"KEY": "value", "EMPTY": ""}
    result = fix_profile(data, remove_empty=True)
    assert "EMPTY" not in result.fixed
    assert "KEY" in result.fixed


def test_remove_empty_false_keeps_empty_keys():
    data = {"KEY": "value", "EMPTY": ""}
    result = fix_profile(data, remove_empty=False)
    assert "EMPTY" in result.fixed


def test_applied_fixes_recorded_for_case():
    data = {"lower": "val"}
    result = fix_profile(data, fix_case=True)
    assert any("lower" in f for f in result.applied_fixes)


def test_applied_fixes_recorded_for_strip():
    data = {"KEY": " val "}
    result = fix_profile(data, strip_values=True)
    assert any("KEY" in f for f in result.applied_fixes)


def test_clean_profile_no_fixes():
    data = {"KEY": "value", "OTHER": "thing"}
    result = fix_profile(data)
    assert result.applied_fixes == []


def test_ok_true_when_no_remaining_issues():
    data = {"KEY": "value"}
    result = fix_profile(data)
    assert result.ok is True


def test_format_fix_result_shows_applied():
    data = {"lower_key": "val"}
    result = fix_profile(data, fix_case=True)
    output = format_fix_result(result)
    assert "Applied fixes" in output
    assert "lower_key" in output


def test_format_fix_result_no_fixes_message():
    data = {"KEY": "val"}
    result = fix_profile(data)
    output = format_fix_result(result)
    assert "No fixes applied" in output


def test_empty_profile_returns_empty_fixed():
    result = fix_profile({})
    assert result.fixed == {}
    assert result.applied_fixes == []
