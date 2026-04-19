# Schema Validation

envault supports validating profiles against a JSON schema to enforce required keys, value patterns, and allowed values.

## Schema Format

Create a JSON file describing expected keys:

```json
{
  "DATABASE_URL": {
    "required": true,
    "pattern": "postgres://.+",
    "description": "PostgreSQL connection string"
  },
  "ENV": {
    "required": true,
    "allowed": ["dev", "staging", "prod"]
  },
  "PORT": {
    "required": false,
    "pattern": "\\d+"
  }
}
```

### Field options

| Option | Type | Description |
|---|---|---|
| `required` | bool | Whether the key must be present (default: true) |
| `pattern` | string | Regex pattern the value must fully match |
| `allowed` | list | Explicit list of permitted values |
| `description` | string | Human-readable description |

## Usage

```bash
envault schema check <profile> <schema.json>
```

Exits with code `1` if validation fails.

## Example

```bash
$ envault schema check production schema.json
Schema validation FAILED:
  [ERROR] DATABASE_URL: Required key 'DATABASE_URL' is missing.
```
