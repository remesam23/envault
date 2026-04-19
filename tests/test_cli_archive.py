import pytest
from click.testing import CliRunner
from pathlib import Path
from envault.cli_archive import archive_cmd
from envault.vault import _save_raw


@pytest.fixture
def vault(tmp_path):
    v = str(tmp_path)
    _save_raw(v, {"dev": {"A": "1"}, "prod": {"A": "2"}})
    return v


def run(vault_dir, *args):
    runner = CliRunner()
    return runner.invoke(archive_cmd, [*args, "--vault", vault_dir])


def test_create_archive(vault):
    result = run(vault, "create", "--label", "v1")
    assert result.exit_code == 0
    assert "Created" in result.output
    assert "v1" in result.output


def test_list_no_archives(vault):
    result = run(vault, "list")
    assert result.exit_code == 0
    assert "No archives" in result.output


def test_list_shows_archives(vault):
    run(vault, "create", "--label", "snap1")
    result = run(vault, "list")
    assert "snap1" in result.output


def test_restore_archive(vault):
    run(vault, "create")
    result = run(vault, "list")
    archive_id = result.output.split()[1]
    r = run(vault, "restore", archive_id)
    assert r.exit_code == 0
    assert "Restored" in r.output


def test_delete_archive(vault):
    run(vault, "create")
    listing = run(vault, "list")
    archive_id = listing.output.split()[1]
    r = run(vault, "delete", archive_id)
    assert r.exit_code == 0
    assert "Deleted" in r.output


def test_restore_missing_raises(vault):
    r = run(vault, "restore", "bad-id")
    assert r.exit_code != 0
