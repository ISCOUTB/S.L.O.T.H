import datetime
import functools
import time
from typing import Any, Callable, Dict, List, Optional, cast

import httpx
from docker.client import DockerClient
from docker.models.services import Service

from src.config import Constants, env
from src.models import ServiceConfig, ServiceMetric
from src.utils import logger


class DockerService(object):
    scale_records: Dict[str, datetime.datetime] = {}

    @staticmethod
    @functools.lru_cache(maxsize=1)
    def get_services(client: DockerClient) -> List[Service]:
        return cast(List[Service], client.services.list())  # type: ignore

    @staticmethod
    def get_service_config(service: Service) -> Optional[ServiceConfig]:
        logger.debug(f"checking service {service.name}")  # type: ignore

        specs: Dict[str, Any] = service.attrs.get("Spec", {})
        labels: Dict[str, Any] = specs.get("Labels", {})

        if cast(str, labels.get(Constants.LABEL_ENABLED, "false")).lower() != "true":
            return None

        if env.STACK_NAME:
            service_stack = cast(str, labels.get("com.docker.stack.namespace", ""))
            if service_stack != env.STACK_NAME:
                return None

        max_str = cast(
            str, labels.get(Constants.LABEL_MAX, str(env.DEFAULT_MAX_REPLICAS))
        )

        max_replicas = -1
        if max_str.lower() not in ["on-demand", "unlimited", "-1"]:
            max_replicas = int(max_str)

        return ServiceConfig(
            service_name=str(service.name),  # type: ignore
            enabled=True,
            min_replicas=int(labels.get(Constants.LABEL_MIN, env.DEFAULT_MIN_REPLICAS)),
            max_replicas=max_replicas,
            metric=labels.get(Constants.LABEL_METRIC, "cpu"),
            threshold_up=float(labels.get(Constants.LABEL_UP, "75")),
            threshold_down=float(labels.get(Constants.LABEL_DOWN, "25")),
        )

    @staticmethod
    def get_metric_value(config: ServiceConfig) -> Optional[float]:
        metric_window = f"{env.metric_window_seconds}s"

        metric_queries: Dict[ServiceMetric, Callable[[ServiceConfig], str]] = {
            "cpu": lambda c: (
                f"avg(rate(container_cpu_usage_seconds_total{{"
                f'job="cadvisor",'
                f'container_label_com_docker_swarm_service_name="{c.service_name}",'
                f'cpu="total"'
                f"}}[{metric_window}])) * 100"
            ),
            "memory": lambda c: (
                f"avg(container_memory_usage_bytes{{"
                f'job="cadvisor",'
                f'container_label_com_docker_swarm_service_name="{c.service_name}"'
                f"}} / container_spec_memory_limit_bytes * 100)"
            ),
        }

        query_fn = metric_queries.get(config.metric, None)
        query = (
            config.custom_query or query_fn(config) if query_fn is not None else None
        )

        if not query:
            logger.warning(f"unknown metric: {config.metric}")
            return None

        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{env.PROMETHEUS_URL}/api/v1/query",
                    params=dict(query=query),
                    timeout=5,
                )

                response.raise_for_status()
                result = response.json()

                if result["data"]["result"]:
                    return float(result["data"]["result"][0]["value"][1])

                return None
        except httpx.HTTPError as exception:
            logger.warning(
                f"(prometheus) service name: {config.service_name} | http exception: {exception}"
            )

            return None
        except Exception as exception:
            logger.warning(f"service name: {config.service_name} | Error: {exception}")

            return None

    @staticmethod
    def get_current_replicas(client: DockerClient, service_name: str) -> Optional[int]:
        try:
            service = cast(Service, client.services.get(service_name))  # type: ignore
            return service.attrs["Spec"]["Mode"]["Replicated"]["Replicas"]
        except Exception as exception:
            logger.error(
                f"error getting current replicas for {service_name}: {exception}"
            )
            return None

    @staticmethod
    def scale_service(
        client: DockerClient, service_name: str, target_replicas: int, reason: str
    ) -> bool:
        try:
            service = cast(Service, client.services.get(service_name))  # type: ignore
            current = DockerService.get_current_replicas(
                client=client, service_name=service_name
            )

            if not current:
                logger.error(
                    f"could not escale {service_name}, failed to get current replicas"
                )
                return False

            service.update(mode={"Replicated": {"Replicas": target_replicas}})  # type: ignore

            direction = "UP" if target_replicas > current else "DOWN"
            logger.info(
                f"{direction} {service_name}: {current} -> {target_replicas} (reason: {reason})"
            )

            DockerService.scale_records[service_name] = datetime.datetime.now()

            return True
        except Exception as exception:
            logger.error(f"error scaling {service_name}: {exception}")
            return False

    @staticmethod
    def can_scale(service_name: str) -> bool:
        if service_name not in DockerService.scale_records:
            return True

        elapsed = (
            datetime.datetime.now() - DockerService.scale_records[service_name]
        ).total_seconds()
        return elapsed >= env.COOLDOWN_PERIOD

    @staticmethod
    def evaluate_service(client: DockerClient, service: Service):
        config = DockerService.get_service_config(service=service)
        if not config:
            return

        metric_value = DockerService.get_metric_value(config=config)
        if metric_value is None:
            logger.debug(f"no valid metrics for {service.name} (value: {metric_value})")  # type: ignore
            return

        current_replicas = DockerService.get_current_replicas(
            client=client, service_name=config.service_name
        )
        if current_replicas is None:
            return

        if not DockerService.can_scale(service_name=config.service_name):
            cooldown_remaining = (
                env.COOLDOWN_PERIOD
                - (
                    datetime.datetime.now()
                    - DockerService.scale_records[config.service_name]
                ).total_seconds()
            )
            logger.debug(
                f"{config.service_name} in cooldown ({cooldown_remaining:0f}s)"
            )
            return

        should_scale_up = metric_value > config.threshold_up
        should_scale_down = metric_value < config.threshold_down

        if should_scale_up:
            if config.is_on_demand or current_replicas < config.max_replicas:
                reason = f"{config.metric}={metric_value:.1f}% > {config.threshold_up}%"
                DockerService.scale_service(
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
            DockerService.scale_service(
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

                services = DockerService.get_services(client=client)  # type: ignore
                logger.debug(f"found {len(services)} services")

                for service in services:
                    logger.debug(f"processing service {service.name}")  # type: ignore
                    try:
                        config = DockerService.get_service_config(service=service)

                        if config:
                            logger.debug(f"config found for {config.service_name}")

                            DockerService.evaluate_service(
                                client=client, service=service
                            )
                    except Exception as exception:
                        logger.error(f"error procesing {service.name}: {exception}")  # type: ignore

                time.sleep(env.CHECK_INTERVAL)
            except KeyboardInterrupt:
                logger.info("autoscaler stopped by user")
                break
            except Exception as exception:
                logger.error(f"error in main loop: {exception}")
                time.sleep(env.CHECK_INTERVAL)
