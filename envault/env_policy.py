"""Policy enforcement: define and check rules across profiles."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import json


class PolicyError(Exception):
    pass


@dataclass
class PolicyRule:
    name: str
    required_keys: List[str] = field(default_factory=list)
    forbidden_keys: List[str] = field(default_factory=list)
    key_pattern: Optional[str] = None  # all keys must match if set
    max_keys: Optional[int] = None


@dataclass
class PolicyViolation:
    rule: str
    message: str


@dataclass
class PolicyResult:
    profile: str
    violations: List[PolicyViolation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.violations) == 0


def _policy_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".policies.json"


def _load_policies(vault_dir: str) -> Dict[str, dict]:
    p = _policy_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_policies(vault_dir: str, data: Dict[str, dict]) -> None:
    _policy_path(vault_dir).write_text(json.dumps(data, indent=2))


def set_policy(vault_dir: str, rule: PolicyRule) -> PolicyRule:
    data = _load_policies(vault_dir)
    data[rule.name] = {
        "required_keys": rule.required_keys,
        "forbidden_keys": rule.forbidden_keys,
        "key_pattern": rule.key_pattern,
        "max_keys": rule.max_keys,
    }
    _save_policies(vault_dir, data)
    return rule


def get_policy(vault_dir: str, name: str) -> Optional[PolicyRule]:
    data = _load_policies(vault_dir)
    if name not in data:
        return None
    d = data[name]
    return PolicyRule(
        name=name,
        required_keys=d.get("required_keys", []),
        forbidden_keys=d.get("forbidden_keys", []),
        key_pattern=d.get("key_pattern"),
        max_keys=d.get("max_keys"),
    )


def list_policies(vault_dir: str) -> List[str]:
    return list(_load_policies(vault_dir).keys())


def remove_policy(vault_dir: str, name: str) -> None:
    data = _load_policies(vault_dir)
    if name not in data:
        raise PolicyError(f"Policy '{name}' not found.")
    del data[name]
    _save_policies(vault_dir, data)


def check_policy(profile_data: Dict[str, str], rule: PolicyRule, profile: str) -> PolicyResult:
    result = PolicyResult(profile=profile)
    keys = set(profile_data.keys())

    for req in rule.required_keys:
        if req not in keys:
            result.violations.append(PolicyViolation(rule=rule.name, message=f"Required key missing: {req}"))

    for forb in rule.forbidden_keys:
        if forb in keys:
            result.violations.append(PolicyViolation(rule=rule.name, message=f"Forbidden key present: {forb}"))

    if rule.key_pattern:
        pat = re.compile(rule.key_pattern)
        for k in keys:
            if not pat.match(k):
                result.violations.append(PolicyViolation(rule=rule.name, message=f"Key '{k}' does not match pattern '{rule.key_pattern}'"))

    if rule.max_keys is not None and len(keys) > rule.max_keys:
        result.violations.append(PolicyViolation(rule=rule.name, message=f"Too many keys: {len(keys)} > {rule.max_keys}"))

    return result


def format_policy_result(result: PolicyResult) -> str:
    if result.ok:
        return f"[OK] Profile '{result.profile}' passes all policy checks."
    lines = [f"[FAIL] Profile '{result.profile}' has {len(result.violations)} violation(s):"]
    for v in result.violations:
        lines.append(f"  [{v.rule}] {v.message}")
    return "\n".join(lines)
