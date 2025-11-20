#!/bin/bash
set -e

echo "⏳ Aguardando PostgreSQL ficar pronto..."

until pg_isready -h db -p 5432 -U clinic_admin > /dev/null 2>&1; do
  echo "Postgres ainda iniciando..."
  sleep 2
done

echo "✅ Postgres pronto! Iniciando FastAPI..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
