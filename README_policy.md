# envault — Policy Enforcement

Policies let you define reusable rule sets that can be checked against any profile.

## Concepts

A **policy** is a named rule set that can specify:

| Option | Description |
|---|---|
| `--require KEY` | Key must be present in the profile |
| `--forbid KEY` | Key must **not** be present in the profile |
| `--key-pattern REGEX` | Every key must match the regular expression |
| `--max-keys N` | Profile may not have more than N keys |

Policies are stored in `.policies.json` inside the vault directory.

## Commands

### Define a policy

```bash
envault policy set production \
  --require DB_URL \
  --require SECRET_KEY \
  --forbid DEBUG \
  --key-pattern '^[A-Z_]+$' \
  --max-keys 50
```

### Inspect a policy

```bash
envault policy get production
```

### List all policies

```bash
envault policy list
```

### Remove a policy

```bash
envault policy remove production
```

### Check a profile against a policy

```bash
envault policy check prod production
# Password: ****
# [OK] Profile 'prod' passes all policy checks.
```

If violations are found the command exits with code **1**:

```
[FAIL] Profile 'prod' has 2 violation(s):
  [production] Required key missing: SECRET_KEY
  [production] Key 'debug_mode' does not match pattern '^[A-Z_]+$'
```

## Python API

```python
from envault.env_policy import PolicyRule, set_policy, check_policy

rule = PolicyRule(
    name="ci",
    required_keys=["CI_TOKEN"],
    key_pattern=r"^[A-Z_]+$",
)
set_policy("/path/to/vault", rule)

result = check_policy(profile_data, rule, profile_name="ci")
if not result.ok:
    for v in result.violations:
        print(v.message)
```
