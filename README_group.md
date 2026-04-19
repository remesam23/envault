# envault — Profile Groups

Group multiple profiles under a named label for easier management.

## Commands

### Create a group
```bash
envault group create <group> <profile1> [profile2 ...]
```

### Add a profile to a group
```bash
envault group add <group> <profile>
```

### Remove a profile from a group
```bash
envault group remove <group> <profile>
```

### List all groups
```bash
envault group list
```

### Show profiles in a group
```bash
envault group show <group>
```

### Delete a group
```bash
envault group delete <group>
```

## Storage

Groups are stored in `.groups.json` inside the vault directory. Only metadata
(group names and profile names) is stored — no secrets.

## Example

```bash
# Create a group for all non-production profiles
envault group create non-prod dev staging qa

# Add a new profile later
envault group add non-prod uat

# See what's in the group
envault group show non-prod
# dev
# staging
# qa
# uat
```
