import datetime
import time

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
    def evaluate(client: DockerClient, service: Service):
        config = ServiceConfigExtractor.extract(service)
        if not config:
            return

        metric_value = MetricsService.get_metric_value(config)
        if metric_value is None:
            logger.debug(f"no valid metrics for {service.name} (value: {metric_value})")  # type: ignore
            return

        current_replicas = DockerClientService.get_current_replicas(
            client=client, service_name=config.service_name
        )
        if current_replicas is None:
            return

        ServiceMonitor._check_and_scale(
            client=client,
            config=config,
            current_replicas=current_replicas,
            metric_value=metric_value,
        )

    @staticmethod
    def _check_and_scale(
        client: DockerClient,
        config: ServiceConfig,
        current_replicas: int,
        metric_value: float,
    ):
        if not ScalingService.can_scale(service_name=config.service_name):
            cooldown_remaining = (
                env.COOLDOWN_PERIOD
                - (
                    datetime.datetime.now()
                    - ScalingService.scale_records[config.service_name]
                ).total_seconds()
            )

            logger.debug(
                f"{config.service_name} in cooldown ({cooldown_remaining:.0f}s)"
            )
            return

        should_scale_up = metric_value > config.threshold_up
        should_scale_down = metric_value < config.threshold_down

        if should_scale_up:
            if config.is_on_demand or current_replicas < config.max_replicas:
                reason = f"{config.metric}={metric_value:.1f}% > {config.threshold_up}%"
                ScalingService.scale(
                    client=client,
                    service_name=config.service_name,
                    target_replicas=current_replicas + 1,
                    reason=reason,
                )
                return

            logger.info(
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

                            ServiceMonitor.evaluate(client=client, service=service)
                    except Exception as exception:
                        logger.error(f"error processing {service.name}: {exception}")  # type: ignore

                time.sleep(env.CHECK_INTERVAL)
            except KeyboardInterrupt:
                logger.info("autoscaler stopped by user")
                break
            except Exception as exception:
                logger.error(f"error in main loop: {exception}")
                time.sleep(env.CHECK_INTERVAL)
