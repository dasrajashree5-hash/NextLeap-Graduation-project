#!/bin/sh
set -e

PORT="${PORT:-8000}"

echo "Running database migrations..."
python -m alembic upgrade head

echo "Starting uvicorn on 0.0.0.0:${PORT}"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
