#!/bin/bash

set -euo pipefail

BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
DATA_DIR="${WEAVIATE_VOLUME_MOUNT:-$BASE_DIR/.docker-data/weaviate-data}"
BACKUP_DIR="$BASE_DIR/.docker-data/weaviate-backups"

mkdir -p "$BACKUP_DIR"

DATE=$(date +%F)
FILE="$BACKUP_DIR/weaviate_backup_${DATE}.tar.gz"

echo "Creating $FILE"
tar -C "$DATA_DIR" -czf "$FILE" .

echo "Deleting previous backups"
find "$BACKUP_DIR" -type f -name 'weaviate_backup_*.tar.gz' ! -name "$(basename "$FILE")" -delete

echo "Weekly Weaviate backup complete."