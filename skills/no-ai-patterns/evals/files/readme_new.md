# Tidewatch

Tidewatch tells you when a cron job fails or runs late. It wraps the command in your crontab, records how the run went and sends an alert by email, Slack or webhook when the command exits with an error or takes longer than you allowed.

Cron itself only mails the output to the local user (if mail is set up at all), so a failed backup usually goes unnoticed until someone needs the backup.

## Installation

Tidewatch is a single static binary without dependencies.

```bash
curl -fsSL https://example.com/tidewatch/install.sh | sh
```

## Usage

Put `tidewatch run` in front of the command in your crontab:

```bash
0 3 * * * tidewatch run --name nightly-backup -- /usr/local/bin/backup.sh
```

Tidewatch records the exit code, the duration and the last 200 lines of output of every run. If the command exits with a non-zero status, or runs longer than the `--timeout` you set, Tidewatch sends an alert to the channels in `~/.config/tidewatch/config.toml`.

## Contributing

Found a bug, or is something in these docs wrong? Please open an issue or a pull request.

## License

MIT
