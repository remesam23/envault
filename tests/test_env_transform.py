"""Tests for envault.env_transform."""
import pytest
from envault.env_transform import (
    apply_transform,
    format_transform_result,
    transform_keys_upper,
    transform_keys_lower,
    transform_values_strip,
    transform_add_prefix,
    transform_remove_prefix,
    TransformError,
)

DATA = {"db_host": "localhost", "db_port": "5432", "api_key": " secret "}


def test_keys_upper():
    out, changes = transform_keys_upper({"db_host": "val", "DB_PORT": "5432"})
    assert "DB_HOST" in out
    assert "DB_PORT" in out
    assert len(changes) == 1  # only db_host changed


def test_keys_lower():
    out, changes = transform_keys_lower({"DB_HOST": "val", "db_port": "5432"})
    assert "db_host" in out
    assert "db_port" in out
    assert len(changes) == 1


def test_values_strip():
    out, changes = transform_values_strip({"key": "  value  ", "other": "clean"})
    assert out["key"] == "value"
    assert out["other"] == "clean"
    assert len(changes) == 1


def test_add_prefix():
    out, changes = transform_add_prefix({"HOST": "localhost"}, "APP_")
    assert "APP_HOST" in out
    assert len(changes) == 1


def test_remove_prefix():
    out, changes = transform_remove_prefix({"APP_HOST": "localhost", "OTHER": "val"}, "APP_")
    assert "HOST" in out
    assert "OTHER" in out
    assert len(changes) == 1


def test_remove_prefix_no_match():
    out, changes = transform_remove_prefix({"HOST": "localhost"}, "APP_")
    assert "HOST" in out
    assert changes == []


def test_apply_transform_upper():
    result = apply_transform("dev", {"db_host": "localhost"}, "upper")
    assert "DB_HOST" in result.transformed
    assert result.profile == "dev"
    assert result.ok


def test_apply_transform_strip():
    result = apply_transform("dev", {"KEY": "  val  "}, "strip")
    assert result.transformed["KEY"] == "val"


def test_apply_transform_add_prefix():
    result = apply_transform("dev", {"HOST": "x"}, "add_prefix", prefix="MY_")
    assert "MY_HOST" in result.transformed


def test_apply_transform_unknown_raises():
    with pytest.raises(TransformError):
        apply_transform("dev", {}, "explode")


def test_format_no_changes():
    result = apply_transform("dev", {"KEY": "val"}, "upper")
    msg = format_transform_result(result)
    assert "no changes" in msg


def test_format_with_changes():
    result = apply_transform("dev", {"key": "val"}, "upper")
    msg = format_transform_result(result)
    assert "1 change" in msg
    assert "KEY" in msg
