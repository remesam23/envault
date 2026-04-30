"""Tests for envault.env_policy."""
import pytest
from envault.env_policy import (
    PolicyRule, PolicyError,
    set_policy, get_policy, list_policies, remove_policy,
    check_policy, format_policy_result,
)


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_get_policy(tmp_vault):
    rule = PolicyRule(name="strict", required_keys=["DB_URL"], forbidden_keys=["DEBUG"])
    set_policy(tmp_vault, rule)
    loaded = get_policy(tmp_vault, "strict")
    assert loaded is not None
    assert loaded.name == "strict"
    assert "DB_URL" in loaded.required_keys
    assert "DEBUG" in loaded.forbidden_keys


def test_get_missing_policy_returns_none(tmp_vault):
    assert get_policy(tmp_vault, "nonexistent") is None


def test_list_policies_empty(tmp_vault):
    assert list_policies(tmp_vault) == []


def test_list_policies_returns_names(tmp_vault):
    set_policy(tmp_vault, PolicyRule(name="p1"))
    set_policy(tmp_vault, PolicyRule(name="p2"))
    names = list_policies(tmp_vault)
    assert "p1" in names
    assert "p2" in names


def test_remove_policy(tmp_vault):
    set_policy(tmp_vault, PolicyRule(name="temp"))
    remove_policy(tmp_vault, "temp")
    assert get_policy(tmp_vault, "temp") is None


def test_remove_missing_policy_raises(tmp_vault):
    with pytest.raises(PolicyError, match="not found"):
        remove_policy(tmp_vault, "ghost")


def test_check_required_key_missing(tmp_vault):
    rule = PolicyRule(name="r", required_keys=["API_KEY"])
    result = check_policy({"HOST": "localhost"}, rule, "dev")
    assert not result.ok
    assert any("API_KEY" in v.message for v in result.violations)


def test_check_forbidden_key_present(tmp_vault):
    rule = PolicyRule(name="r", forbidden_keys=["DEBUG"])
    result = check_policy({"DEBUG": "true", "HOST": "x"}, rule, "dev")
    assert not result.ok
    assert any("DEBUG" in v.message for v in result.violations)


def test_check_key_pattern_violation(tmp_vault):
    rule = PolicyRule(name="r", key_pattern="^[A-Z_]+$")
    result = check_policy({"good_KEY": "v", "ALSO_GOOD": "v"}, rule, "dev")
    assert not result.ok
    assert any("good_KEY" in v.message for v in result.violations)


def test_check_max_keys_violation(tmp_vault):
    rule = PolicyRule(name="r", max_keys=2)
    result = check_policy({"A": "1", "B": "2", "C": "3"}, rule, "dev")
    assert not result.ok
    assert any("Too many keys" in v.message for v in result.violations)


def test_check_clean_profile_passes(tmp_vault):
    rule = PolicyRule(name="r", required_keys=["HOST"], forbidden_keys=["DEBUG"], max_keys=5)
    result = check_policy({"HOST": "localhost", "PORT": "5432"}, rule, "dev")
    assert result.ok
    assert result.violations == []


def test_format_ok_result(tmp_vault):
    rule = PolicyRule(name="r")
    result = check_policy({"A": "1"}, rule, "prod")
    text = format_policy_result(result)
    assert "OK" in text
    assert "prod" in text


def test_format_fail_result(tmp_vault):
    rule = PolicyRule(name="strict", required_keys=["MISSING"])
    result = check_policy({}, rule, "dev")
    text = format_policy_result(result)
    assert "FAIL" in text
    assert "MISSING" in text
