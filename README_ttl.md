# envault TTL — Profile Expiry

Assign a time-to-live (TTL) to any profile. Once expired, integrations can check and refuse to unlock stale profiles.

## Commands

### Set a TTL
```bash
envault ttl set <profile> <seconds>
```
Example — expire `prod` in 1 hour:
```bash
envault ttl set prod 3600
# TTL set for 'prod': expires at 2024-06-01T12:00:00+00:00
```

### Get TTL for a profile
```bash
envault ttl get prod
# prod: 2024-06-01T12:00:00+00:00
# prod: 2024-06-01T11:00:00+00:00 [EXPIRED]
```

### List all TTL entries
```bash
envault ttl list
# dev: 2024-06-01T13:00:00+00:00
# prod: 2024-06-01T11:00:00+00:00 [EXPIRED]
```

### Clear a TTL
```bash
envault ttl clear prod
# TTL cleared for 'prod'.
```

## Python API

```python
from envault.ttl import set_ttl, get_ttl, is_expired, clear_ttl

set_ttl(".vault", "prod", seconds=3600)

# Retrieve the raw expiry datetime (or None if no TTL is set)
expiry = get_ttl(".vault", "prod")
if expiry:
    print(f"Profile expires at: {expiry}")

if is_expired(".vault", "prod"):
    raise RuntimeError("Profile has expired — re-lock and unlock to refresh.")

clear_ttl(".vault", "prod")
```

## Notes

- TTL metadata is stored in `.ttl.json` inside the vault directory.
- Expiry is checked against UTC time.
- TTL does **not** automatically delete profiles; it is advisory.
- `get_ttl` returns a `datetime` object (UTC) or `None` if no TTL has been set for the profile.
