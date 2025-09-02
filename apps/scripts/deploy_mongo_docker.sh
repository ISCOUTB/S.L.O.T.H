# !/bin/bash
source .env
docker run -d --name typechecking-mongo \
  -p "${MONGO_PORT}:27017" \
  -e MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME} \
  -e MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD} \
  -e MONGO_INITDB_DATABASE=${MONGO_INITDB_DATABASE} \
  -v typechecking_mongo_data:/data/db \
  mongo:latest
