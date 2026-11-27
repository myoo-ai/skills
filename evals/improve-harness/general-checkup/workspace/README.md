# billing-service

FastAPI service that issues invoices and sends dunning reminders. Data lives
in Postgres and errors go to Sentry. Issues and pull requests are on GitHub.

```sh
uv sync
uv run pytest
```
