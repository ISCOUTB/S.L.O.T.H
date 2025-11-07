from typing import Callable, Dict, Optional

import httpx

from src.config import env
from src.models import ServiceConfig, ServiceMetric
from src.utils import logger


class MetricsService:
    @staticmethod
    def get_metric_value(config: ServiceConfig) -> Optional[float]:
        query = MetricsService._build_query(config)
        
        if not query:
            logger.warning(f"unknown metric: {config.metric}")
            return None

        return MetricsService._query_prometheus(config.service_name, query)

    @staticmethod
    def _build_query(config: ServiceConfig) -> Optional[str]:
        if config.custom_query:
            return config.custom_query

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

        query_fn = metric_queries.get(config.metric)
        return query_fn(config) if query_fn else None

    @staticmethod
    def _query_prometheus(service_name: str, query: str) -> Optional[float]:
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
                f"(prometheus) service name: {service_name} | http exception: {exception}"
            )
            return None
        except Exception as exception:
            logger.warning(f"service name: {service_name} | Error: {exception}")
            return None