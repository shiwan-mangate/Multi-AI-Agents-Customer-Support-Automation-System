#!/bin/bash

set -e

echo "======================================================"
echo "Restoring faq_vector_db database..."
echo "======================================================"

BACKUP_FILE="/backup/faq_vector_db.backup"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found:"
    echo "$BACKUP_FILE"
    exit 1
fi

echo "Backup file found."

echo "Creating pgvector extension..."

psql \
    --username="$POSTGRES_USER" \
    --dbname="$POSTGRES_DB" \
    -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "pgvector extension ready."

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
echo "faq_vector_db restored successfully."
echo "======================================================"