"""Compare two profiles and produce a human-readable report."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envault.diff import diff_profiles, format_diff, DiffResult


@dataclass
class CompareReport:
    profile_a: str
    profile_b: str
    diff: DiffResult
    summary: List[str] = field(default_factory=list)

    @property
    def identical(self) -> bool:
        return (
            not self.diff.added
            and not self.diff.removed
            and not self.diff.changed
        )


def compare_profiles(
    vault_path: str,
    profile_a: str,
    profile_b: str,
    password: str,
) -> CompareReport:
    """Load two profiles and diff them."""
    from envault.vault import load_profile

    data_a = load_profile(vault_path, profile_a, password)
    data_b = load_profile(vault_path, profile_b, password)
    diff = diff_profiles(data_a, data_b)

    summary: List[str] = []
    if diff.added:
        summary.append(f"{len(diff.added)} key(s) only in '{profile_b}'")
    if diff.removed:
        summary.append(f"{len(diff.removed)} key(s) only in '{profile_a}'")
    if diff.changed:
        summary.append(f"{len(diff.changed)} key(s) differ")
    if not summary:
        summary.append("Profiles are identical")

    return CompareReport(
        profile_a=profile_a,
        profile_b=profile_b,
        diff=diff,
        summary=summary,
    )


def format_compare(report: CompareReport) -> str:
    lines = [
        f"Comparing '{report.profile_a}' vs '{report.profile_b}'",
        "-" * 40,
    ]
    lines.append(format_diff(report.diff))
    lines.append("")
    lines.extend(report.summary)
    return "\n".join(lines)
