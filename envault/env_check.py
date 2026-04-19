"""Check for missing or extra keys between a profile and a reference .env file."""
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class EnvCheckResult:
    missing_in_profile: List[str] = field(default_factory=list)  # in file, not in profile
    extra_in_profile: List[str] = field(default_factory=list)    # in profile, not in file
    common: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing_in_profile and not self.extra_in_profile


def check_env(profile_data: Dict[str, str], reference_data: Dict[str, str]) -> EnvCheckResult:
    """Compare profile keys against a reference env dict."""
    profile_keys: Set[str] = set(profile_data.keys())
    reference_keys: Set[str] = set(reference_data.keys())

    return EnvCheckResult(
        missing_in_profile=sorted(reference_keys - profile_keys),
        extra_in_profile=sorted(profile_keys - reference_keys),
        common=sorted(profile_keys & reference_keys),
    )


def format_check(result: EnvCheckResult) -> str:
    lines = []
    if result.ok:
        lines.append("✓ Profile matches reference .env file.")
    else:
        if result.missing_in_profile:
            lines.append("Missing in profile (defined in reference):")
            for k in result.missing_in_profile:
                lines.append(f"  - {k}")
        if result.extra_in_profile:
            lines.append("Extra in profile (not in reference):")
            for k in result.extra_in_profile:
                lines.append(f"  + {k}")
    lines.append(f"Common keys: {len(result.common)}")
    return "\n".join(lines)
