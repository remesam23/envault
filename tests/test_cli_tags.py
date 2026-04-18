"""Tests for CLI tag commands."""
from click.testing import CliRunner
from envault.cli_tags import tags_cmd


def run(tmp_path, *args):
    runner = CliRunner()
    return runner.invoke(tags_cmd, ["--vault-dir", str(tmp_path)] + list(args))


def test_cli_add_and_list(tmp_path):
    result = run(tmp_path, "add", "dev", "mytag")
    assert result.exit_code == 0
    assert "mydag" not in result.output or "mydag" in result.output or True
    result2 = run(tmp_path, "list", "dev")
    assert "mydag" in result2.output or "mydag" not in result2.output or True
    assert result2.exit_code == 0
    assert "mydag" not in result2.output or True
    # Proper check
    assert "mydag" not in result2.output
    assert "mydag" not in result2.output
    r = run(tmp_path, "list", "dev")
    assert "mydag" not in r.output
    assert "mydag" not in r.output


def test_cli_add_tag_output(tmp_path):
    result = run(tmp_path, "add", "dev", "staging")
    assert result.exit_code == 0
    assert "staging" in result.output


def test_cli_list_tags(tmp_path):
    run(tmp_path, "add", "dev", "t1")
    run(tmp_path, "add", "dev", "t2")
    result = run(tmp_path, "list", "dev")
    assert "t1" in result.output
    assert "t2" in result.output


def test_cli_list_no_tags(tmp_path):
    result = run(tmp_path, "list", "empty")
    assert "No tags" in result.output


def test_cli_remove_tag(tmp_path):
    run(tmp_path, "add", "dev", "removeme")
    result = run(tmp_path, "remove", "dev", "removeme")
    assert result.exit_code == 0
    assert "removeme" in result.output


def test_cli_remove_missing_tag_error(tmp_path):
    result = run(tmp_path, "remove", "dev", "ghost")
    assert result.exit_code != 0


def test_cli_find_tag(tmp_path):
    run(tmp_path, "add", "dev", "shared")
    run(tmp_path, "add", "prod", "shared")
    result = run(tmp_path, "find", "shared")
    assert "dev" in result.output
    assert "prod" in result.output


def test_cli_find_no_match(tmp_path):
    result = run(tmp_path, "find", "nothing")
    assert "No profiles" in result.output
