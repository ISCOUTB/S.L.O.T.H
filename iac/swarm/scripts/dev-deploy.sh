#!/bin/bash

set -e -a

source swarm/development/.env
set +a

docker stack deploy -c swarm/development/docker-stack.yml "$GLOBAL_STACK_NAME" --detach=true