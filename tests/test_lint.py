"""Tests for envault.lint module."""
import pytest
from envault.lint import lint_profile, format_lint, LintIssue


def test_clean_profile_has_no_issues():
    env = {'DATABASE_URL': 'postgres://localhost/db', 'SECRET_KEY': 'abc123'}
    result = lint_profile('prod', env)
    assert result.ok
    assert result.issues == []


def test_lowercase_key_raises_e001():
    env = {'database_url': 'value'}
    result = lint_profile('dev', env)
    codes = [i.code for i in result.issues]
    assert 'E001' in codes


def test_mixed_case_key_raises_e001():
    env = {'MyKey': 'value'}
    result = lint_profile('dev', env)
    codes = [i.code for i in result.issues]
    assert 'E001' in codes


def test_empty_value_raises_w001():
    env = {'API_KEY': ''}
    result = lint_profile('dev', env)
    codes = [i.code for i in result.issues]
    assert 'W001' in codes


def test_blank_value_raises_w001():
    env = {'API_KEY': '   '}
    result = lint_profile('dev', env)
    codes = [i.code for i in result.issues]
    assert 'W001' in codes


def test_leading_whitespace_raises_w002():
    env = {'API_KEY': ' value'}
    result = lint_profile('dev', env)
    codes = [i.code for i in result.issues]
    assert 'W002' in codes


def test_trailing_whitespace_raises_w002():
    env = {'API_KEY': 'value '}
    result = lint_profile('dev', env)
    codes = [i.code for i in result.issues]
    assert 'W002' in codes


def test_multiple_issues_collected():
    env = {'bad_key': ' ', 'GOOD_KEY': 'ok'}
    result = lint_profile('dev', env)
    assert not result.ok
    assert len(result.issues) >= 2


def test_format_lint_ok():
    env = {'VALID': 'value'}
    result = lint_profile('prod', env)
    output = format_lint(result)
    assert 'No issues' in output
    assert 'prod' in output


def test_format_lint_with_issues():
    env = {'bad': ''}
    result = lint_profile('dev', env)
    output = format_lint(result)
    assert 'issue' in output
    assert 'E001' in output or 'W001' in output
