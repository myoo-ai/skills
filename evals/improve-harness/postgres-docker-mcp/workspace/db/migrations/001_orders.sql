CREATE TABLE orders (
    id          bigserial PRIMARY KEY,
    customer_id bigint      NOT NULL,
    status      text        NOT NULL DEFAULT 'new',
    total_cents bigint      NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE refunds (
    id          bigserial PRIMARY KEY,
    order_id    bigint      NOT NULL REFERENCES orders (id),
    amount_cents bigint     NOT NULL,
    reason      text,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX orders_status_updated ON orders (status, updated_at);
