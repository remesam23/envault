"""Tests for envault.env_diff_export."""
import json
import csv
import io
import pytest

from envault.env_diff_export import export_diff

BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
OTHER = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "xyz"}


def test_text_shows_added():
    out = export_diff(BASE, OTHER, fmt="text")
    assert "+ SECRET=xyz" in out


def test_text_shows_removed():
    out = export_diff(BASE, OTHER, fmt="text")
    assert "- DEBUG=true" in out


def test_text_shows_changed():
    out = export_diff(BASE, OTHER, fmt="text")
    assert "~ HOST" in out
    assert "localhost" in out
    assert "prod.example.com" in out


def test_text_no_diff():
    out = export_diff(BASE, BASE, fmt="text")
    assert "(no differences)" in out


def test_text_header_contains_profile_names():
    out = export_diff(BASE, OTHER, fmt="text", profile_a="dev", profile_b="prod")
    assert "dev" in out
    assert "prod" in out


def test_json_structure():
    raw = export_diff(BASE, OTHER, fmt="json", profile_a="dev", profile_b="prod")
    data = json.loads(raw)
    assert data["profile_a"] == "dev"
    assert data["profile_b"] == "prod"
    statuses = {row["status"] for row in data["diff"]}
    assert "added" in statuses
    assert "removed" in statuses
    assert "changed" in statuses


def test_json_added_entry():
    raw = export_diff(BASE, OTHER, fmt="json")
    data = json.loads(raw)
    added = [r for r in data["diff"] if r["status"] == "added"]
    keys = {r["key"] for r in added}
    assert "SECRET" in keys


def test_csv_has_header():
    raw = export_diff(BASE, OTHER, fmt="csv", profile_a="dev", profile_b="prod")
    reader = csv.reader(io.StringIO(raw))
    header = next(reader)
    assert header == ["key", "status", "dev", "prod"]


def test_csv_rows_count():
    raw = export_diff(BASE, OTHER, fmt="csv")
    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)
    # header + added(1) + removed(1) + changed(1)
    assert len(rows) == 4


def test_csv_no_diff_only_header():
    raw = export_diff(BASE, BASE, fmt="csv")
    reader = csv.reader(io.StringIO(raw))
    rows = list(reader)
    assert len(rows) == 1  # header only
