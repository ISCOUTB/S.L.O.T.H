#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/production/.env"
STACK_FILE="$PROJECT_ROOT/production/docker-stack.yml"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}[ ERROR ] file does not exists: $ENV_FILE${NC}"
    exit 1
fi

if [ ! -f "$STACK_FILE" ]; then
    echo -e "${RED}[ ERROR ] file does not exists: $STACK_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}[ INFO ] loading .env vars from $ENV_FILE...${NC}"
set -a
source "$ENV_FILE"
set +a

if [ -z "$GLOBAL_STACK_NAME" ]; then
    echo -e "${RED}[ ERROR] 'GLOBAL_STACK_NAME' is required $ENV_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}[ INFO ] deploying stack: $GLOBAL_STACK_NAME${NC}"
docker stack deploy -c "$STACK_FILE" "$GLOBAL_STACK_NAME" --detach=true

echo -e "${GREEN}[ SUCCESS ] done${NC}"


