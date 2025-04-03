#!/bin/bash
set -e

# Get the schema name from environment variable or use default
SCHEMA=${APP_DATABASE_SCHEMA}

# Connect to the PostgreSQL server and create the schema
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE SCHEMA IF NOT EXISTS "$SCHEMA";
    GRANT ALL ON SCHEMA "$SCHEMA" TO "$POSTGRES_USER";
    ALTER ROLE "$POSTGRES_USER" SET search_path TO "$SCHEMA";
EOSQL

echo "Schema '$SCHEMA' created successfully"
