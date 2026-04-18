"""Tests for envault.pin module."""

import pytest
from pathlib import Path

from envault.pin import (
    pin_profile,
    unpin_profile,
    is_pinned,
    list_pinned,
    pin_summary,
    PinError,
)


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a vault dir with a couple of fake encrypted profile files."""
    for name in ("dev", "prod", "staging"):
        (tmp_path / f"{name}.env.enc").write_bytes(b"fake")
    return str(tmp_path)


def test_pin_profile(tmp_vault):
    pin_profile(tmp_vault, "dev")
    assert is_pinned(tmp_vault, "dev")


def test_pin_missing_profile_raises(tmp_vault):
    with pytest.raises(PinError, match="does not exist"):
        pin_profile(tmp_vault, "ghost")


def test_unpin_profile(tmp_vault):
    pin_profile(tmp_vault, "dev")
    unpin_profile(tmp_vault, "dev")
    assert not is_pinned(tmp_vault, "dev")


def test_unpin_not_pinned_raises(tmp_vault):
    with pytest.raises(PinError, match="not pinned"):
        unpin_profile(tmp_vault, "dev")


def test_is_pinned_false_by_default(tmp_vault):
    assert not is_pinned(tmp_vault, "prod")


def test_list_pinned_multiple(tmp_vault):
    pin_profile(tmp_vault, "dev")
    pin_profile(tmp_vault, "prod")
    pinned = list_pinned(tmp_vault)
    assert set(pinned) == {"dev", "prod"}


def test_list_pinned_empty(tmp_vault):
    assert list_pinned(tmp_vault) == []


def test_pin_summary_with_profiles(tmp_vault):
    pin_profile(tmp_vault, "staging")
    summary = pin_summary(list_pinned(tmp_vault))
    assert "staging" in summary


def test_pin_summary_empty():
    assert pin_summary([]) == "No pinned profiles."


def test_pin_idempotent(tmp_vault):
    pin_profile(tmp_vault, "dev")
    pin_profile(tmp_vault, "dev")
    assert list_pinned(tmp_vault).count("dev") == 1
