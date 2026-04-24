"""Tests for envault.env_inherit."""
import pytest

from envault.env_inherit import InheritError, format_inherit_result, resolve_inheritance


def _make_loader(profiles):
    """Return a simple loader backed by a dict of dicts."""
    def loader(name):
        if name not in profiles:
            raise KeyError(f"profile '{name}' not found")
        return dict(profiles[name])
    return loader


def test_child_overrides_parent():
    loader = _make_loader({
        "base": {"A": "1", "B": "2"},
        "child": {"B": "99", "C": "3"},
    })
    result = resolve_inheritance("child", ["base"], loader)
    assert result.resolved == {"A": "1", "B": "99", "C": "3"}


def test_chain_order_is_base_first():
    loader = _make_loader({
        "base": {"X": "0"},
        "child": {"Y": "1"},
    })
    result = resolve_inheritance("child", ["base"], loader)
    assert result.chain == ["base", "child"]


def test_sources_track_provenance():
    loader = _make_loader({
        "base": {"A": "1", "B": "2"},
        "child": {"B": "override"},
    })
    result = resolve_inheritance("child", ["base"], loader)
    assert result.sources["A"] == "base"
    assert result.sources["B"] == "child"


def test_multiple_parents_later_wins():
    loader = _make_loader({
        "p1": {"K": "from_p1"},
        "p2": {"K": "from_p2"},
        "child": {},
    })
    result = resolve_inheritance("child", ["p1", "p2"], loader)
    assert result.resolved["K"] == "from_p2"
    assert result.sources["K"] == "p2"


def test_no_parents_returns_child_only():
    loader = _make_loader({"child": {"A": "1"}})
    result = resolve_inheritance("child", [], loader)
    assert result.resolved == {"A": "1"}
    assert result.chain == ["child"]


def test_missing_parent_raises():
    loader = _make_loader({"child": {"A": "1"}})
    with pytest.raises(InheritError, match="missing_parent"):
        resolve_inheritance("child", ["missing_parent"], loader)


def test_missing_child_raises():
    loader = _make_loader({"base": {"A": "1"}})
    with pytest.raises(InheritError, match="no_such_child"):
        resolve_inheritance("no_such_child", ["base"], loader)


def test_max_depth_guard():
    loader = _make_loader({"child": {}})
    parents = [f"p{i}" for i in range(10)]
    with pytest.raises(InheritError, match="too deep"):
        resolve_inheritance("child", parents, loader, max_depth=10)


def test_format_inherit_result_contains_chain():
    loader = _make_loader({
        "base": {"A": "hello"},
        "child": {"B": "world"},
    })
    result = resolve_inheritance("child", ["base"], loader)
    text = format_inherit_result(result)
    assert "base -> child" in text
    assert "A=hello" in text
    assert "B=world" in text
    assert "(from: base)" in text
    assert "(from: child)" in text
