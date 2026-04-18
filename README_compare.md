# envault compare

The `compare` feature lets you diff two encrypted profiles side-by-side.

## Usage

```bash
# Full diff output
envault compare run dev prod --vault .envault

# Summary only
envault compare run dev prod --vault .envault --summary
```

The command exits with code **0** if profiles are identical, **1** if they differ.

## Output example

```
Comparing 'dev' vs 'prod'
----------------------------------------
+ EXTRA = only_prod
~ KEY: dev_val -> prod_val

1 key(s) only in 'prod'
1 key(s) differ
```

## Symbols

| Symbol | Meaning |
|--------|---------|
| `+`    | Key present only in second profile |
| `-`    | Key present only in first profile  |
| `~`    | Key exists in both but value differs |
