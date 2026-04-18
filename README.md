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

---

## How It Works

`envault` encrypts your `.env` files using AES-256 and stores them locally in a `.vault/` directory. Each profile maps to an isolated set of environment variables, making it easy to switch between `development`, `staging`, and `production` configurations without exposing secrets.

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

[MIT](LICENSE)