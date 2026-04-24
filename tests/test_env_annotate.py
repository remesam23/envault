"""Tests for envault.env_annotate."""
from __future__ import annotations

import pytest

from envault.env_annotate import (
    AnnotateError,
    format_annotations,
    get_annotation,
    list_annotations,
    remove_annotation,
    set_annotation,
)


@pytest.fixture()
def tmp_vault(tmp_path):
    return str(tmp_path)


def test_set_and_get_annotation(tmp_vault):
    set_annotation(tmp_vault, "dev", "DB_URL", "Primary database connection string")
    note = get_annotation(tmp_vault, "dev", "DB_URL")
    assert note == "Primary database connection string"


def test_get_missing_annotation_returns_none(tmp_vault):
    result = get_annotation(tmp_vault, "dev", "NONEXISTENT")
    assert result is None


def test_overwrite_annotation(tmp_vault):
    set_annotation(tmp_vault, "dev", "API_KEY", "old note")
    set_annotation(tmp_vault, "dev", "API_KEY", "new note")
    assert get_annotation(tmp_vault, "dev", "API_KEY") == "new note"


def test_remove_annotation(tmp_vault):
    set_annotation(tmp_vault, "dev", "SECRET", "some note")
    remove_annotation(tmp_vault, "dev", "SECRET")
    assert get_annotation(tmp_vault, "dev", "SECRET") is None


def test_remove_missing_annotation_raises(tmp_vault):
    with pytest.raises(AnnotateError, match="No annotation"):
        remove_annotation(tmp_vault, "dev", "MISSING_KEY")


def test_list_annotations_returns_all(tmp_vault):
    set_annotation(tmp_vault, "dev", "A", "note A")
    set_annotation(tmp_vault, "dev", "B", "note B")
    result = list_annotations(tmp_vault, "dev")
    assert result == {"A": "note A", "B": "note B"}


def test_list_annotations_empty_profile(tmp_vault):
    result = list_annotations(tmp_vault, "empty_profile")
    assert result == {}


def test_annotations_are_isolated_per_profile(tmp_vault):
    set_annotation(tmp_vault, "dev", "KEY", "dev note")
    set_annotation(tmp_vault, "prod", "KEY", "prod note")
    assert get_annotation(tmp_vault, "dev", "KEY") == "dev note"
    assert get_annotation(tmp_vault, "prod", "KEY") == "prod note"


def test_format_annotations_sorted(tmp_vault):
    annotations = {"Z_KEY": "last", "A_KEY": "first"}
    output = format_annotations(annotations)
    assert output.index("A_KEY") < output.index("Z_KEY")


def test_format_annotations_empty():
    output = format_annotations({})
    assert "no annotations" in output
