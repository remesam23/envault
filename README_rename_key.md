# envault rename-key

Rename a key within an existing profile without changing its value.

## Usage

```bash
envault rename-key run <profile> <old_key> <new_key> [OPTIONS]
```

### Options

| Option | Description |
|---|---|
| `--vault PATH` | Path to vault directory (default: `.envault`) |
| `--password TEXT` | Vault password (prompted if omitted) |
| `--overwrite` | Overwrite `new_key` if it already exists in the profile |

## Examples

```bash
# Rename DB_HOST to DATABASE_HOST in the prod profile
envault rename-key run prod DB_HOST DATABASE_HOST

# Force overwrite if DATABASE_HOST already exists
envault rename-key run prod DB_HOST DATABASE_HOST --overwrite
```

## Behaviour

- If `old_key` does not exist, the command exits with code `2` and prints an error.
- If `new_key` already exists and `--overwrite` is **not** set, the operation is skipped (exit code `1`).
- With `--overwrite`, the existing `new_key` is replaced by the value of `old_key`, and `old_key` is removed.
- All other keys in the profile are preserved unchanged.
