SELECT id, customer_id, status, total_cents, updated_at
FROM orders
WHERE status = 'processing'
  AND updated_at < now() - interval '15 minutes'
ORDER BY updated_at
LIMIT 50;
