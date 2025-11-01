from typing import Any, Callable, Dict, Optional, cast

import httpx
from docker.models.services import Service

from src.config import Constants, env
from src.models import ServiceConfig, ServiceMetric
from src.utils import logger


class DockerService(object):
    @staticmethod
    def get_service_config(service: Service) -> Optional[ServiceConfig]:
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
        metric_queries: Dict[ServiceMetric, Callable[[ServiceConfig], str]] = {
            "cpu": lambda c: (
                f"avg(rate(container_cpu_usage_seconds_total{{"
                f'job="cadvisor",'
                f'container_label_com_docker_swarm_service_name="{c.service_name}"'
                f"}}[2m])) * 100"
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
