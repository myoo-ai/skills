# 🚀 Tidewatch

**Tidewatch is a powerful, lightweight, and blazing-fast CLI tool that seamlessly monitors your cron jobs — so you never miss a failed backup again.**

## ✨ Key Features

- **Effortless Setup:** Get up and running in seconds with a single command.
- **Real-Time Alerts:** Instantly receive notifications via email, Slack, or webhooks whenever a job fails or runs late.
- **Robust History:** Every run is logged, providing a complete audit trail of your scheduled tasks.
- **Zero Dependencies:** A single static binary that works anywhere — no runtime required.

## 🤔 Why Tidewatch?

Cron is great at running jobs, but it's terrible at telling you when something goes wrong. Failed jobs fail silently, and you often only find out when it's too late. Tidewatch bridges this gap by wrapping your existing commands and reporting their outcome — it's not just a monitor, it's peace of mind.

## 📦 Installation

Simply download the latest release and you're good to go:

```bash
curl -fsSL https://example.com/tidewatch/install.sh | sh
```

## 🛠️ Usage

Wrap any cron command with `tidewatch run`:

```bash
0 3 * * * tidewatch run --name nightly-backup -- /usr/local/bin/backup.sh
```

Tidewatch records the exit code, duration, and the last 200 lines of output. If the command exits with a non-zero status, or takes longer than the `--timeout` you set, Tidewatch sends an alert to the channels configured in `~/.config/tidewatch/config.toml`.

## 🤝 Contributing

We welcome contributions from the community! Whether it's fixing bugs, improving documentation, or suggesting new features, every contribution makes a difference. Feel free to open an issue or submit a pull request.

## 📄 License

Tidewatch is released under the MIT License. Happy monitoring! 🎉
