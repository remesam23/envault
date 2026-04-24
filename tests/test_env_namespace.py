"""Tests for envault.env_namespace."""

from __future__ import annotations

import pytest

from envault.env_namespace import (
    extract_namespace,
    inject_namespace,
    list_namespaces,
    format_namespace_result,
    ok,
)


SAMPLE: dict = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "myapp",
    "APP_ENV": "production",
    "SECRET_KEY": "abc123",
    "PLAIN": "value",
}


def test_extract_returns_matching_keys():
    result = extract_namespace(SAMPLE, "DB")
    assert "DB_HOST" in result.keys
    assert "DB_PORT" in result.keys


def test_extract_excludes_non_matching_keys():
    result = extract_namespace(SAMPLE, "DB")
    assert "APP_NAME" not in result.keys
    assert "SECRET_KEY" not in result.keys


def test_extract_strip_prefix_true():
    result = extract_namespace(SAMPLE, "DB", strip_prefix=True)
    assert "HOST" in result.stripped_keys
    assert "PORT" in result.stripped_keys


def test_extract_strip_prefix_false():
    result = extract_namespace(SAMPLE, "DB", strip_prefix=False)
    assert result.stripped_keys == {}
    assert "DB_HOST" in result.keys


def test_extract_empty_profile():
    result = extract_namespace({}, "DB")
    assert result.keys == {}
    assert ok(result)


def test_extract_no_match_returns_empty():
    result = extract_namespace(SAMPLE, "REDIS")
    assert result.keys == {}
    assert result.is_ok


def test_list_namespaces_detects_all_prefixes():
    namespaces = list_namespaces(SAMPLE)
    assert "DB" in namespaces
    assert "APP" in namespaces
    assert "SECRET" in namespaces


def test_list_namespaces_sorted():
    namespaces = list_namespaces(SAMPLE)
    assert namespaces == sorted(namespaces)


def test_list_namespaces_excludes_no_underscore_keys():
    namespaces = list_namespaces({"PLAIN": "val"})
    assert namespaces == []


def test_inject_adds_prefixed_keys():
    result = inject_namespace({}, "DB", {"HOST": "localhost", "PORT": "5432"})
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_inject_skips_existing_without_overwrite():
    base = {"DB_HOST": "oldhost"}
    result = inject_namespace(base, "DB", {"HOST": "newhost"}, overwrite=False)
    assert result["DB_HOST"] == "oldhost"


def test_inject_overwrites_when_flag_set():
    base = {"DB_HOST": "oldhost"}
    result = inject_namespace(base, "DB", {"HOST": "newhost"}, overwrite=True)
    assert result["DB_HOST"] == "newhost"


def test_inject_preserves_unrelated_keys():
    base = {"APP_NAME": "myapp"}
    result = inject_namespace(base, "DB", {"HOST": "localhost"})
    assert result["APP_NAME"] == "myapp"
    assert result["DB_HOST"] == "localhost"


def test_format_namespace_result_shows_stripped_keys():
    result = extract_namespace(SAMPLE, "DB", strip_prefix=True)
    output = format_namespace_result(result, strip=True)
    assert "HOST" in output
    assert "PORT" in output
    assert "Namespace: DB" in output


def test_format_namespace_result_empty():
    result = extract_namespace({}, "DB")
    output = format_namespace_result(result)
    assert "(no keys found)" in output
