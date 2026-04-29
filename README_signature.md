# envault — Profile Signatures

Profile signatures provide HMAC-SHA256-based integrity verification for vault profiles. Once a profile is signed, any modification to its data will cause verification to fail.

## Commands

### Sign a profile

```bash
envault signature sign <profile> --secret <secret> --password <password>
```

Computes an HMAC-SHA256 digest over the canonically serialised profile data and stores it in `.signatures.json` inside the vault directory.

### Verify a profile

```bash
envault signature verify <profile> --secret <secret> --password <password>
```

Exits `0` when the signature is valid, `2` when the signature does not match, and `1` on an error.

### Remove a signature

```bash
envault signature remove <profile>
```

Deletes the stored signature entry for the given profile.

### List signed profiles

```bash
envault signature list
```

Prints all profiles that have a recorded signature together with the timestamp at which they were signed.

## Environment variables

| Variable | Description |
|---|---|
| `ENVAULT_SIG_SECRET` | HMAC secret (replaces `--secret`) |
| `ENVAULT_PASSWORD` | Vault password (replaces `--password`) |

## Storage

Signatures are stored in `<vault_dir>/.signatures.json`:

```json
{
  "prod": {
    "signature": "a3f1...",
    "signed_at": 1718000000.0
  }
}
```

## Notes

- The canonical payload is produced by `json.dumps(data, sort_keys=True)`, so key ordering in the original `.env` file does not affect the signature.
- The secret is **not** stored anywhere in the vault; you must supply it on every `sign` and `verify` call.
- Signatures are independent of vault encryption — they operate on the decrypted data.
