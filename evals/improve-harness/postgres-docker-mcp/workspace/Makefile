.PHONY: up down logs psql stuck test

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs --tail=200 -f api worker

psql:
	docker compose exec db psql -U orders orders

# orders that have been "processing" for more than 15 minutes
stuck:
	docker compose exec -T db psql -U orders orders < scripts/stuck-orders.sql

test:
	go test ./...
