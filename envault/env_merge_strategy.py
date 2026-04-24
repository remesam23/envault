"""Merge strategy module: apply configurable merge strategies across profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class MergeStrategyError(Exception):
    pass


STRATEGY_OURS = "ours"
STRATEGY_THEIRS = "theirs"
STRATEGY_UNION = "union"
STRATEGY_INTERSECT = "intersect"

VALID_STRATEGIES = {STRATEGY_OURS, STRATEGY_THEIRS, STRATEGY_UNION, STRATEGY_INTERSECT}


@dataclass
class MergeStrategyResult:
    merged: Dict[str, str]
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)
    strategy: str = STRATEGY_OURS


def ok(result: MergeStrategyResult) -> bool:
    return isinstance(result, MergeStrategyResult)


def apply_strategy(
    base: Dict[str, str],
    incoming: Dict[str, str],
    strategy: str = STRATEGY_OURS,
) -> MergeStrategyResult:
    """Merge *incoming* into *base* using the given strategy.

    Strategies:
      ours      – keep base value on conflict (default)
      theirs    – incoming value wins on conflict
      union     – all keys from both; base wins on conflict
      intersect – only keys present in both; base value kept
    """
    if strategy not in VALID_STRATEGIES:
        raise MergeStrategyError(
            f"Unknown strategy '{strategy}'. Choose from: {', '.join(sorted(VALID_STRATEGIES))}"
        )

    base_keys = set(base)
    incoming_keys = set(incoming)

    added: List[str] = []
    removed: List[str] = []
    overwritten: List[str] = []
    merged: Dict[str, str] = {}

    if strategy == STRATEGY_OURS:
        merged = dict(base)
        for k, v in incoming.items():
            if k not in merged:
                merged[k] = v
                added.append(k)

    elif strategy == STRATEGY_THEIRS:
        merged = dict(base)
        for k, v in incoming.items():
            if k in merged and merged[k] != v:
                overwritten.append(k)
            elif k not in merged:
                added.append(k)
            merged[k] = v

    elif strategy == STRATEGY_UNION:
        merged = dict(base)
        for k, v in incoming.items():
            if k not in merged:
                merged[k] = v
                added.append(k)

    elif strategy == STRATEGY_INTERSECT:
        common = base_keys & incoming_keys
        merged = {k: base[k] for k in common}
        removed = sorted(base_keys - common)

    return MergeStrategyResult(
        merged=merged,
        added=sorted(added),
        removed=sorted(removed),
        overwritten=sorted(overwritten),
        strategy=strategy,
    )


def format_strategy_result(result: MergeStrategyResult) -> str:
    lines = [f"Strategy : {result.strategy}", f"Total keys: {len(result.merged)}"]
    if result.added:
        lines.append(f"Added     : {', '.join(result.added)}")
    if result.overwritten:
        lines.append(f"Overwritten: {', '.join(result.overwritten)}")
    if result.removed:
        lines.append(f"Removed   : {', '.join(result.removed)}")
    return "\n".join(lines)
