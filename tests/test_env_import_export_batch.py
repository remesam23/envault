"""Tests for batch import/export feature."""
import pytest
from pathlib import Path
from envault.env_import_export_batch import batch_import, batch_export, BatchError
from envault.vault import save_profile, load_profile, list_profiles

PASSWORD = "batchpass"


@pytest.fixture
def tmp_vault(tmp_path):
    return str(tmp_path / "vault.db")


@pytest.fixture
def env_dir(tmp_path):
    d = tmp_path / "envs"
    d.mkdir()
    (d / "prod.env").write_text("DB_HOST=prod-db\nDB_PORT=5432\n")
    (d / "staging.env").write_text("DB_HOST=staging-db\nDB_PORT=5433\n")
    return str(d)


def test_batch_import_loads_all_files(tmp_vault, env_dir):
    result = batch_import(tmp_vault, env_dir, PASSWORD)
    assert "prod" in result.processed
    assert "staging" in result.processed
    assert result.ok


def test_batch_import_data_is_correct(tmp_vault, env_dir):
    batch_import(tmp_vault, env_dir, PASSWORD)
    data = load_profile(tmp_vault, "prod", PASSWORD)
    assert data["DB_HOST"] == "prod-db"
    assert data["DB_PORT"] == "5432"


def test_batch_import_skips_existing_without_overwrite(tmp_vault, env_dir):
    save_profile(tmp_vault, "prod", {"DB_HOST": "old"}, PASSWORD)
    result = batch_import(tmp_vault, env_dir, PASSWORD, overwrite=False)
    assert "prod" in result.skipped
    assert load_profile(tmp_vault, "prod", PASSWORD)["DB_HOST"] == "old"


def test_batch_import_overwrites_when_flag_set(tmp_vault, env_dir):
    save_profile(tmp_vault, "prod", {"DB_HOST": "old"}, PASSWORD)
    result = batch_import(tmp_vault, env_dir, PASSWORD, overwrite=True)
    assert "prod" in result.processed
    assert load_profile(tmp_vault, "prod", PASSWORD)["DB_HOST"] == "prod-db"


def test_batch_import_missing_directory_raises(tmp_vault, tmp_path):
    with pytest.raises(BatchError):
        batch_import(tmp_vault, str(tmp_path / "nonexistent"), PASSWORD)


def test_batch_export_creates_files(tmp_vault, tmp_path):
    save_profile(tmp_vault, "prod", {"KEY": "val1"}, PASSWORD)
    save_profile(tmp_vault, "dev", {"KEY": "val2"}, PASSWORD)
    out_dir = str(tmp_path / "out")
    result = batch_export(tmp_vault, out_dir, PASSWORD)
    assert "prod" in result.processed
    assert "dev" in result.processed
    assert (Path(out_dir) / "prod.env").exists()
    assert (Path(out_dir) / "dev.env").exists()


def test_batch_export_file_content(tmp_vault, tmp_path):
    save_profile(tmp_vault, "prod", {"API_KEY": "secret"}, PASSWORD)
    out_dir = str(tmp_path / "out")
    batch_export(tmp_vault, out_dir, PASSWORD)
    content = (Path(out_dir) / "prod.env").read_text()
    assert "API_KEY" in content
    assert "secret" in content


def test_batch_export_specific_profiles(tmp_vault, tmp_path):
    save_profile(tmp_vault, "prod", {"X": "1"}, PASSWORD)
    save_profile(tmp_vault, "dev", {"X": "2"}, PASSWORD)
    out_dir = str(tmp_path / "out")
    result = batch_export(tmp_vault, out_dir, PASSWORD, profiles=["prod"])
    assert result.processed == ["prod"]
    assert not (Path(out_dir) / "dev.env").exists()
