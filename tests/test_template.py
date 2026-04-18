"""Tests for envault.template."""
import pytest
from envault.template import render_template, list_placeholders, TemplateError


ENV = {"HOST": "localhost", "PORT": "5432", "DB": "mydb"}


def test_render_simple_substitution():
    tmpl = "DATABASE_URL=postgres://${HOST}:${PORT}/${DB}"
    result = render_template(tmpl, ENV)
    assert result == "DATABASE_URL=postgres://localhost:5432/mydb"


def test_render_no_placeholders():
    tmpl = "STATIC=value"
    assert render_template(tmpl, ENV) == "STATIC=value"


def test_render_strict_raises_on_missing():
    tmpl = "FOO=${MISSING_KEY}"
    with pytest.raises(TemplateError, match="MISSING_KEY"):
        render_template(tmpl, ENV, strict=True)


def test_render_non_strict_leaves_placeholder():
    tmpl = "FOO=${MISSING_KEY}"
    result = render_template(tmpl, ENV, strict=False)
    assert result == "FOO=${MISSING_KEY}"


def test_render_multiple_missing_reported():
    tmpl = "A=${X} B=${Y}"
    with pytest.raises(TemplateError) as exc_info:
        render_template(tmpl, {}, strict=True)
    msg = str(exc_info.value)
    assert "X" in msg and "Y" in msg


def test_list_placeholders_returns_sorted_unique():
    tmpl = "${B} ${A} ${B} ${C}"
    assert list_placeholders(tmpl) == ["A", "B", "C"]


def test_list_placeholders_empty():
    assert list_placeholders("NO_VARS=true") == []


def test_render_multiline_template():
    tmpl = "HOST=${HOST}\nPORT=${PORT}\n"
    result = render_template(tmpl, ENV)
    assert result == "HOST=localhost\nPORT=5432\n"


def test_render_file_writes_output(tmp_path):
    from envault.template import render_file
    tmpl_path = tmp_path / "app.env.template"
    out_path = tmp_path / "app.env"
    tmpl_path.write_text("URL=http://${HOST}:${PORT}")
    rendered = render_file(str(tmpl_path), ENV, output_path=str(out_path))
    assert rendered == "URL=http://localhost:5432"
    assert out_path.read_text() == rendered


def test_render_file_no_output(tmp_path):
    from envault.template import render_file
    tmpl_path = tmp_path / "t.template"
    tmpl_path.write_text("KEY=${DB}")
    rendered = render_file(str(tmpl_path), ENV)
    assert rendered == "KEY=mydb"
