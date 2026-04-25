# envault – Per-Key Expiry

The **expire** feature lets you attach expiry timestamps to individual keys
within a profile. This is useful for rotating secrets, short-lived tokens,
or any credential that must be refreshed on a schedule.

## CLI Usage

### Set expiry

```bash
# Expire in 30 days from now
envault expire set prod API_KEY --days 30

# Expire at a specific datetime (ISO 8601)
envault expire set prod TOKEN --at 2025-12-31T00:00:00+00:00
```

### Get expiry

```bash
envault expire get prod API_KEY
# API_KEY: 2025-09-01T12:00:00+00:00
# API_KEY: 2024-01-01T00:00:00+00:00 [EXPIRED]
```

### Clear expiry

```bash
envault expire clear prod API_KEY
```

### List expiries

```bash
# All keys with expiry in a profile
envault expire list prod

# Only expired keys
envault expire list prod --expired-only
```

## Python API

```python
from envault.env_expire import (
    set_key_expiry,
    get_key_expiry,
    is_key_expired,
    clear_key_expiry,
    list_expired_keys,
    list_all_expiries,
)
from datetime import datetime, timezone, timedelta

vault = "/path/to/vault"
expiry = datetime.now(timezone.utc) + timedelta(days=7)

set_key_expiry(vault, "prod", "DB_PASSWORD", expiry)
print(is_key_expired(vault, "prod", "DB_PASSWORD"))  # False

expired = list_expired_keys(vault, "prod")
print(expired)  # keys whose expiry has passed
```

## Storage

Expiry data is stored in `.envault_key_expiry.json` inside the vault directory.
The format is:

```json
{
  "prod": {
    "API_KEY": "2025-09-01T12:00:00+00:00",
    "DB_PASSWORD": "2025-06-15T08:30:00+00:00"
  }
}
```

Expiry datetimes are stored as ISO 8601 strings with timezone information.
