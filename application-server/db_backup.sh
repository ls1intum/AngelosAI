#!/bin/bash
set -euo pipefail

# Load .env.postgres if present
ENV_FILE="$(dirname "$0")/.env.postgres"
[ -f "$ENV_FILE" ] && set -a && . "$ENV_FILE" && set +a

CONTAINER="angelos-db"
DB="${POSTGRES_DB:-kbdatabase}"
USER="${POSTGRES_USER:-postgres}"

# Timestamp
DATE=$(date +%F)

echo "Creating backup inside container: /backups/backup_${DATE}.dump.gz"

docker exec "$CONTAINER" \
  sh -c "pg_dump -U \"$USER\" -F c \"$DB\" | gzip > /backups/backup_${DATE}.dump.gz"

echo "Deleting previous backups inside container"

docker exec "$CONTAINER" \
  sh -c "find /backups -type f -name 'backup_*.dump.gz' ! -name 'backup_${DATE}.dump.gz' -delete"

echo "Weekly backup complete."