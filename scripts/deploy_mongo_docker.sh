#!/bin/bash
source scripts/.env

CONTAINER_NAME=typechecking-mongo

if [ "$(docker ps -a -q -f name=^/${CONTAINER_NAME}$)" ]; then
  docker start $CONTAINER_NAME
  exit 0
fi

docker run -d --name $CONTAINER_NAME \
  -p "${MONGO_PORT}:27017" \
  --restart on-failure \
  -e MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME} \
  -e MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD} \
  -e MONGO_INITDB_DATABASE=${MONGO_INITDB_DATABASE} \
  -v typechecking_mongo_data:/data/db \
  mongo:7.0
