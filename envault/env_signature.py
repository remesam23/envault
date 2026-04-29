"""Profile signature — HMAC-based signing and verification of profile data."""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class SignatureError(Exception):
    """Raised on signature-related failures."""


@dataclass
class SignResult:
    profile: str
    signature: str
    signed_at: float
    ok: bool = True
    message: str = ""


@dataclass
class VerifyResult:
    profile: str
    valid: bool
    signed_at: Optional[float] = None
    message: str = ""


def _sig_path(vault_dir: str) -> Path:
    return Path(vault_dir) / ".signatures.json"


def _load_sigs(vault_dir: str) -> dict:
    p = _sig_path(vault_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_sigs(vault_dir: str, data: dict) -> None:
    _sig_path(vault_dir).write_text(json.dumps(data, indent=2))


def _compute_hmac(secret: str, payload: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def _canonical(profile_data: dict) -> str:
    return json.dumps(profile_data, sort_keys=True, separators=(",", ":"))


def sign_profile(vault_dir: str, profile: str, profile_data: dict, secret: str) -> SignResult:
    if not secret:
        raise SignatureError("secret must not be empty")
    payload = _canonical(profile_data)
    sig = _compute_hmac(secret, payload)
    ts = time.time()
    sigs = _load_sigs(vault_dir)
    sigs[profile] = {"signature": sig, "signed_at": ts}
    _save_sigs(vault_dir, sigs)
    return SignResult(profile=profile, signature=sig, signed_at=ts)


def verify_profile(vault_dir: str, profile: str, profile_data: dict, secret: str) -> VerifyResult:
    if not secret:
        raise SignatureError("secret must not be empty")
    sigs = _load_sigs(vault_dir)
    if profile not in sigs:
        return VerifyResult(profile=profile, valid=False, message="no signature found")
    entry = sigs[profile]
    expected = _compute_hmac(secret, _canonical(profile_data))
    valid = hmac.compare_digest(expected, entry["signature"])
    msg = "signature valid" if valid else "signature mismatch"
    return VerifyResult(profile=profile, valid=valid, signed_at=entry["signed_at"], message=msg)


def remove_signature(vault_dir: str, profile: str) -> None:
    sigs = _load_sigs(vault_dir)
    if profile not in sigs:
        raise SignatureError(f"no signature for profile '{profile}'")
    del sigs[profile]
    _save_sigs(vault_dir, sigs)


def list_signatures(vault_dir: str) -> dict:
    """Return {profile: signed_at} mapping."""
    return {p: v["signed_at"] for p, v in _load_sigs(vault_dir).items()}
