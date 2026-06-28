#!/bin/sh
set -e

# Wait for PostgreSQL
echo "Waiting for PostgreSQL at ${DB_HOST:-db}:${DB_PORT:-5432}..."
until pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}"; do
  echo "PostgreSQL is unavailable - sleeping 2s"
  sleep 2
done
echo "PostgreSQL is up!"

# Wait for Redis
echo "Waiting for Redis at ${REDIS_HOST:-redis}:${REDIS_PORT:-6379}..."
until redis-cli -h "${REDIS_HOST:-redis}" -p "${REDIS_PORT:-6379}" ping | grep -q PONG; do
  echo "Redis is unavailable - sleeping 2s"
  sleep 2
done
echo "Redis is up!"

# Execute the provided command
exec "$@"
