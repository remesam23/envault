"""Search keys/values across vault profiles."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from envault.vault import list_profiles, load_profile


@dataclass
class SearchMatch:
    profile: str
    key: str
    value: str


@dataclass
class SearchResult:
    matches: list[SearchMatch] = field(default_factory=list)

    @property
    def empty(self) -> bool:
        return len(self.matches) == 0


def search_profiles(
    vault_dir: str,
    password: str,
    query: str,
    *,
    keys_only: bool = False,
    values_only: bool = False,
    profile: Optional[str] = None,
    case_sensitive: bool = False,
) -> SearchResult:
    """Search for query across all (or a specific) profile(s)."""
    profiles = [profile] if profile else list_profiles(vault_dir)
    needle = query if case_sensitive else query.lower()
    result = SearchResult()

    for prof in profiles:
        try:
            env = load_profile(vault_dir, prof, password)
        except Exception:
            continue
        for k, v in env.items():
            k_cmp = k if case_sensitive else k.lower()
            v_cmp = v if case_sensitive else v.lower()
            key_hit = not values_only and needle in k_cmp
            val_hit = not keys_only and needle in v_cmp
            if key_hit or val_hit:
                result.matches.append(SearchMatch(profile=prof, key=k, value=v))

    return result


def format_search(result: SearchResult, *, show_values: bool = False) -> str:
    if result.empty:
        return "No matches found."
    lines = []
    for m in result.matches:
        val_part = f" = {m.value}" if show_values else ""
        lines.append(f"[{m.profile}] {m.key}{val_part}")
    return "\n".join(lines)
