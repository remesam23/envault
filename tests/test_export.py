"""Tests for envault.export module."""
import pytest
from pathlib import Path

from envault.export import (
    parse_dotenv,
    serialize_dotenv,
    read_dotenv_file,
    write_dotenv_file,
)


def test_parse_simple():
    text = "KEY=value\nSECRET=abc123\n"
    result = parse_dotenv(text)
    assert result == {"KEY": "value", "SECRET": "abc123"}


def test_parse_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=bar\n"
    result = parse_dotenv(text)
    assert result == {"FOO": "bar"}


def test_parse_strips_quotes():
    text = 'DB_URL="postgres://localhost/db"\nTOKEN=\'secret\'\n'
    result = parse_dotenv(text)
    assert result["DB_URL"] == "postgres://localhost/db"
    assert result["TOKEN"] == "secret"


def test_parse_value_with_equals():
    text = "ENCODED=abc=def=ghi\n"
    result = parse_dotenv(text)
    assert result["ENCODED"] == "abc=def=ghi"


def test_serialize_roundtrip():
    env = {"KEY": "value", "SECRET": "abc123"}
    text = serialize_dotenv(env)
    assert parse_dotenv(text) == env


def test_serialize_quotes_spaces():
    env = {"MSG": "hello world"}
    text = serialize_dotenv(env)
    assert '"hello world"' in text
    assert parse_dotenv(text) == env


def test_read_write_dotenv_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    original = {"APP_ENV": "production", "PORT": "8080"}
    write_dotenv_file(env_file, original)
    assert env_file.exists()
    loaded = read_dotenv_file(env_file)
    assert loaded == original


def test_read_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        read_dotenv_file(tmp_path / "nonexistent.env")
