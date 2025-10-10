# !#bin/bash
source .env
docker run -d \
  --name typechecking-redis \
  -p "${REDIS_PORT}:6379" \
  -v typechecking_redis_data:/data \
  -e REDIS_PASSWORD=${REDIS_PASSWORD} \
  redis:7.4.1 redis-server --requirepass "${REDIS_PASSWORD}"
