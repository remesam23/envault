"""Profile statistics and summary reporting."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProfileStats:
    profile: str
    total_keys: int
    empty_values: int
    unique_values: int
    duplicate_values: int
    longest_key: str
    shortest_key: str
    avg_value_length: float


@dataclass
class StatsResult:
    profiles: Dict[str, ProfileStats] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return bool(self.profiles)


def compute_stats(profile_name: str, data: Dict[str, str]) -> ProfileStats:
    if not data:
        return ProfileStats(
            profile=profile_name,
            total_keys=0,
            empty_values=0,
            unique_values=0,
            duplicate_values=0,
            longest_key="",
            shortest_key="",
            avg_value_length=0.0,
        )

    keys = list(data.keys())
    values = list(data.values())
    value_counts: Dict[str, int] = {}
    for v in values:
        value_counts[v] = value_counts.get(v, 0) + 1

    unique_values = sum(1 for c in value_counts.values() if c == 1)
    duplicate_values = len(values) - unique_values
    avg_value_length = sum(len(v) for v in values) / len(values)

    return ProfileStats(
        profile=profile_name,
        total_keys=len(keys),
        empty_values=sum(1 for v in values if not v.strip()),
        unique_values=unique_values,
        duplicate_values=duplicate_values,
        longest_key=max(keys, key=len),
        shortest_key=min(keys, key=len),
        avg_value_length=round(avg_value_length, 2),
    )


def format_stats(stats: ProfileStats) -> str:
    lines = [
        f"Profile : {stats.profile}",
        f"Total keys       : {stats.total_keys}",
        f"Empty values     : {stats.empty_values}",
        f"Unique values    : {stats.unique_values}",
        f"Duplicate values : {stats.duplicate_values}",
        f"Longest key      : {stats.longest_key}",
        f"Shortest key     : {stats.shortest_key}",
        f"Avg value length : {stats.avg_value_length}",
    ]
    return "\n".join(lines)
