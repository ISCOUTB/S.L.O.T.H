import time

import docker

from src.config import env
from src.services import DockerService
from src.utils import logger

if __name__ == "__main__":
    import logging

    docker_client = docker.from_env()

    logger.info(f"waiting {env.metric_window_seconds}s before starting monitoring")
    time.sleep(env.metric_window_seconds)

    if env.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    DockerService.loop(client=docker_client)
