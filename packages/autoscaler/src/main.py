import time

import docker

from src.config import env
from src.services.monitor import ServiceMonitor
from src.utils import logger

if __name__ == "__main__":
    import logging

    docker_client = docker.from_env()

    if env.DEBUG:
        logger.info(f"Debug Mode: {env.DEBUG}")

    logger.info(f"waiting {env.metric_window_seconds}s before starting monitoring")
    time.sleep(env.metric_window_seconds)

    if env.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    ServiceMonitor.loop(client=docker_client)
