#!/bin/sh
set -e

# Esperar a PostgreSQL
while ! nc -z db 5432; do
  echo "Esperando a PostgreSQL..."
  sleep 1
done

# Ejecutar migraciones
cd /app && alembic upgrade head

# Iniciar aplicación (ajusta según tu estructura real)
exec gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000