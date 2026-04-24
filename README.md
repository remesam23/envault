# envault

> CLI tool for managing and encrypting local `.env` files with profile switching

---

## Installation

```bash
pip install envault
```

---

## Usage

Initialize a vault in your project directory:

```bash
envault init
```

Add and encrypt a `.env` file:

```bash
envault add .env --profile production
```

Switch between profiles:

```bash
envault use staging
```

Decrypt and load variables into your shell:

```bash
eval $(envault load)
```

List available profiles:

```bash
envault list
```

Remove a profile:

```bash
envault remove staging
```

Show the current active profile:

```bash
envault status
```

---

## How It Works

`envault` encrypts your `.env` files using AES-256 and stores them locally in a `.vault/` directory. Each profile maps to an isolated set of environment variables, making it easy to switch between `development`, `staging`, and `production` configurations without exposing secrets.

> **Note:** Add `.vault/` to your `.gitignore` to avoid accidentally committing encrypted secrets to version control.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)
