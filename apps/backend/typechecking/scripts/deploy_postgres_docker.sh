# !/bin/bash
source .env
docker run -d --name typechecking-postgres \
  -p "${POSTGRES_PORT}:5432" \
  -e POSTGRES_USER=${POSTGRES_USER} \
  -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -e POSTGRES_DB=${POSTGRES_DB} \
  -v typechecking_postgres_data:/var/lib/postgresql/data/pgdata \
  postgres:17
