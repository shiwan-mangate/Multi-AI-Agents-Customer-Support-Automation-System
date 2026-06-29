#!/bin/bash

set -e

echo "======================================================"
echo "Restoring customer_support_ai database..."
echo "======================================================"

BACKUP_FILE="/backup/customer_support_ai.backup"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found:"
    echo "$BACKUP_FILE"
    exit 1
fi

echo "Backup file found."

echo "Starting pg_restore..."

pg_restore \
    --username="$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    --verbose \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges \
    "$BACKUP_FILE"

echo
echo "======================================================"
echo "customer_support_ai restored successfully."
echo "======================================================"