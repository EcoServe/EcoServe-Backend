# EcoServe Starter (Flask + Postgres + Redis/RQ)

## Quick start
1. Copy `.env.example` to `.env` and adjust values if needed.
2. `docker compose up --build`
3. Visit `http://localhost:8000/healthz`.

## Migrations
Initialize DB inside the `web` container:
```
docker compose exec web flask db init
docker compose exec web flask db migrate -m "initial"
docker compose exec web flask db upgrade
```

## Test deposit flow
- Create an ItemType, DropBox, and ThresholdRule using POSTs to the admin endpoints.
- Open `http://localhost:8000/d/<qr_token>` to submit a deposit.
