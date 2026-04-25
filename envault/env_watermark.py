"""env_watermark.py — embed and verify a hidden watermark in a profile."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional

WATERMARK_KEY = "__ENVAULT_WM__"


class WatermarkError(Exception):
    pass


@dataclass
class WatermarkResult:
    profile: str
    token: str
    applied: bool = True
    message: str = ""


@dataclass
class VerifyResult:
    profile: str
    valid: bool
    token: Optional[str] = None
    expected: Optional[str] = None
    message: str = ""


def _make_token(profile: str, secret: str, ts: Optional[str] = None) -> str:
    ts = ts or str(int(time.time()))
    raw = f"{profile}:{secret}:{ts}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{ts}.{digest}"


def apply_watermark(data: dict, profile: str, secret: str) -> tuple[dict, WatermarkResult]:
    """Embed a watermark token into *data* under WATERMARK_KEY."""
    if not secret:
        raise WatermarkError("secret must not be empty")
    token = _make_token(profile, secret)
    updated = {**data, WATERMARK_KEY: token}
    return updated, WatermarkResult(profile=profile, token=token, applied=True,
                                    message=f"Watermark applied to '{profile}'")


def verify_watermark(data: dict, profile: str, secret: str) -> VerifyResult:
    """Verify the watermark token stored in *data*."""
    if not secret:
        raise WatermarkError("secret must not be empty")
    token = data.get(WATERMARK_KEY)
    if token is None:
        return VerifyResult(profile=profile, valid=False,
                            message="No watermark found in profile")
    try:
        ts, _ = token.split(".", 1)
    except ValueError:
        return VerifyResult(profile=profile, valid=False, token=token,
                            message="Malformed watermark token")
    expected = _make_token(profile, secret, ts)
    valid = token == expected
    msg = "Watermark valid" if valid else "Watermark mismatch"
    return VerifyResult(profile=profile, valid=valid, token=token,
                        expected=expected, message=msg)


def strip_watermark(data: dict) -> dict:
    """Return a copy of *data* without the watermark key."""
    return {k: v for k, v in data.items() if k != WATERMARK_KEY}
