#!/usr/bin/env bash
set -e

if [ -f ".env" ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found!"
  exit 1
fi

echo "=== Waiting for MySQL ==="
timeout=30
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Waiting for $DB_HOST:$DB_PORT..."
  sleep 1
  timeout=$((timeout - 1))
  if [ "$timeout" -le 0 ]; then
    echo "Timeout waiting for MySQL"
    exit 1
  fi
done

until mysqladmin ping -h"$DB_HOST" -P"$DB_PORT" --silent; do
    echo "Waiting for MySQL..."
    sleep 2
done
echo "MySQL is available!"

echo "=== Waiting for MongoDB ==="
timeout=30
while ! nc -z "$MONGO_HOST" "$MONGO_PORT"; do
  echo "Waiting for $MONGO_HOST:$MONGO_PORT..."
  sleep 1
  timeout=$((timeout - 1))
  if [ "$timeout" -le 0 ]; then
    echo "Timeout waiting for MongoDB port"
    exit 1
  fi
done

until nc -z "$MONGO_HOST" "$MONGO_PORT"; do
    echo "Waiting for MongoDB port..."
    sleep 2
done
echo "MongoDB port is open!"

exec "$@"
