# envault mask

The `mask` command group lets you display profiles with sensitive values automatically redacted.

## Commands

### `envault mask show <profile>`

Display a profile's keys and values, masking anything that looks sensitive.

```bash
envault mask show prod --vault .envault
# Redacted keys: API_KEY, DB_PASSWORD
APP_NAME=myapp
DB_PASSWORD=********
API_KEY=********
DEBUG=false
```

Options:
- `--reveal` — show all values unmasked
- `--extra KEY` — additional key names to mask (repeatable)
- `--pattern REGEX` — extra regex patterns for detecting sensitive keys (repeatable)
- `--vault PATH` — path to vault directory (default: `.envault`)
- `--password TEXT` — vault password

### `envault mask list-sensitive <profile>`

List which keys would be masked without displaying values.

```bash
envault mask list-sensitive prod
API_KEY
DB_PASSWORD
AUTH_TOKEN
```

## Sensitivity Detection

By default, keys matching any of these patterns are masked:

- `password`, `secret`, `token`, `key`, `api_key`, `private`, `auth`, `credential` (case-insensitive)

You can extend detection with `--pattern` or force masking of specific keys with `--extra`.

## Notes

- The original encrypted data is never modified.
- `--reveal` overrides all masking for debugging purposes — use with care.
