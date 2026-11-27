# orders-api

Order service with an HTTP API (`cmd/orders-api`) and a background worker
(`cmd/orders-worker`) that share one Postgres database.

Local development runs everything in Docker:

```sh
make up      # postgres on localhost:5433, api on :8080, worker
make logs    # follow api and worker logs
make psql    # psql shell on the local database
make stuck   # orders stuck in 'processing' for more than 15 minutes
```

Copy `.env.example` to `.env` to run the binaries outside Docker.
