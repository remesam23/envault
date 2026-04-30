# envault resolve

Resolve `${REF}` placeholders within a profile's values.

## Overview

The `resolve` command expands `${KEY}` references inside a profile's values,
looking up each referenced key within the same profile first, then optionally
falling back to a *defaults profile*.

## Usage

```bash
envault resolve run <profile> [OPTIONS]
```

### Options

| Flag | Description |
|------|-------------|
| `--vault PATH` | Path to vault directory (default: `.envault`) |
| `--password TEXT` | Vault password (prompted if omitted) |
| `--defaults-profile NAME` | Profile to use as fallback for missing refs |
| `--strict` | Exit with code 1 if any placeholder cannot be resolved |
| `--json` | Output the fully-resolved profile as JSON |

## Examples

### Resolve within a single profile

```bash
# Profile "prod" contains:
#   BASE=http://api.example.com
#   URL=${BASE}/v2

envault resolve run prod --vault .envault
# Substitutions:
#   URL: resolved ['BASE']
```

### Use a defaults profile as fallback

```bash
envault resolve run prod --defaults-profile base-defaults
```

### Output resolved values as JSON

```bash
envault resolve run prod --json
# {
#   "BASE": "http://api.example.com",
#   "URL": "http://api.example.com/v2"
# }
```

### Strict mode

```bash
envault resolve run prod --strict
# Exits with code 1 if any ${REF} cannot be resolved.
```

## Python API

```python
from envault.env_resolve import resolve_profile

data = {"BASE": "http://x.com", "URL": "${BASE}/api"}
result = resolve_profile(data)
print(result.resolved)       # {'BASE': 'http://x.com', 'URL': 'http://x.com/api'}
print(result.substitutions)  # {'URL': ['BASE']}
print(result.unresolved)     # {}
print(result.ok)             # True
```
