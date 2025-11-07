import time
from typing import cast

from docker.client import DockerClient
from docker.models.services import Service

from src.config import env
from src.models import ServiceConfig
from src.services.client import DockerClientService
from src.services.config import ServiceConfigExtractor
from src.services.metrics import MetricsService
from src.services.scaling import ScalingService
from src.utils import logger


class ServiceMonitor:
    @staticmethod
    def evaluate(client: DockerClient, config: ServiceConfig):
        metric_value = MetricsService.get_metric_value(config)
        if metric_value is None:
            logger.debug(
                f"no valid metrics for {config.service_name} (value: {metric_value})"
            )  # type: ignore
            return

        replicas = DockerClientService.get_replicas(
            client=client, service_name=config.service_name
        )

        if replicas is None:
            return

        running, current = replicas

        ServiceMonitor._check_and_scale(
            client=client,
            config=config,
            running_replicas=running,
            current_replicas=current,
            metric_value=metric_value,
        )

    @staticmethod
    def _check_and_scale(
        client: DockerClient,
        config: ServiceConfig,
        running_replicas: int,
        current_replicas: int,
        metric_value: float,
    ):
        services_down = current_replicas - running_replicas

        if (
            config.priority == "high"
            and services_down > 0
            and metric_value > config.threshold_up
        ):
            logger.warning(
                f"{config.service_name}: {services_down} replicas down, bypassing cooldown due to high priority and high load"
            )

            scale_to = current_replicas + min(
                services_down, config.max_replicas - current_replicas
            )

            ScalingService.scale(
                client=client,
                service_name=config.service_name,
                target_replicas=scale_to,
                reason=f"high priority emergency scale-up ({services_down} down, load={metric_value:.1f}%)",
            )

        if config.priority == "medium" and services_down > 0:
            logger.info(
                f"{config.service_name}: {services_down} replicas down, terminating for swarm to recover"
            )

            service = cast(Service, client.services.get(config.service_name))  # type: ignore
            tasks = service.tasks()  # type: ignore

            for task in tasks:  # type: ignore
                state = task.get("Status", {}).get("State")  # type: ignore

                if state not in ("running", "starting"):
                    task_id = task.get("ID")  # type: ignore

                    logger.info(
                        f"terminating failed task ({task_id}) (state: {state}) (service: {config.service_name})"
                    )

                    try:
                        client.api.kill(task_id)  # type: ignore
                    except Exception as exception:
                        logger.error(
                            f"failed to terminate task ({task_id}) (state: {state}) (service: {config.service_name}): {exception}"
                        )

        if config.priority == "low" and services_down > 0:
            logger.info(
                f"{config.service_name}: {services_down} replicas down, low priority, no action taken (waiting for swarm)"
            )

        ServiceMonitor._scale(
            client=client,
            config=config,
            current_replicas=current_replicas,
            metric_value=metric_value,
        )

    @staticmethod
    def _scale(
        client: DockerClient,
        config: ServiceConfig,
        current_replicas: int,
        metric_value: float,
    ):
        ignore_cooldown = (
            config.priority == "high" and metric_value > config.threshold_up
        )

        if not (
            ScalingService.can_scale(service_name=config.service_name)
            or ignore_cooldown
        ):
            return

        should_scale_up = metric_value > config.threshold_up
        should_scale_down = metric_value < config.threshold_down

        if should_scale_up:
            if config.is_on_demand or current_replicas < config.max_replicas:
                reason = f"{config.metric}={metric_value:.1f}% > {config.threshold_up}%"

                if ignore_cooldown:
                    reason = f'{reason} | priority: {config.priority} [ignored]'

                ScalingService.scale(
                    client=client,
                    service_name=config.service_name,
                    target_replicas=current_replicas + 1,
                    reason=reason,
                )
                return

            # TODO: Should send and email when reaching this point
            logger.warning(
                f"{config.service_name} in max replicas ({config.max_replicas})"
            )

            return

        if should_scale_down and current_replicas > config.min_replicas:
            reason = f"{config.metric}={metric_value:.1f}% < {config.threshold_down}%"
            ScalingService.scale(
                client=client,
                service_name=config.service_name,
                target_replicas=current_replicas - 1,
                reason=reason,
            )

            return

        logger.info(f"no actions required for {config.service_name}")

    @staticmethod
    def loop(client: DockerClient):
        logger.info("autoscaler init")

        while True:
            try:
                logger.debug("checking...")

                services = DockerClientService.get_services(client)
                logger.debug(f"found {len(services)} services")

                for service in services:
                    logger.debug(f"processing service {service.name}")  # type: ignore
                    try:
                        config = ServiceConfigExtractor.extract(service)

                        if config:
                            logger.debug(f"config found for {config.service_name}")

                            ServiceMonitor.evaluate(client=client, config=config)
                    except Exception as exception:
                        logger.error(f"error processing {service.name}: {exception}")  # type: ignore

                time.sleep(env.CHECK_INTERVAL)
            except KeyboardInterrupt:
                logger.info("autoscaler stopped by user")
                break
            except Exception as exception:
                logger.error(f"error in main loop: {exception}")
                time.sleep(env.CHECK_INTERVAL)
