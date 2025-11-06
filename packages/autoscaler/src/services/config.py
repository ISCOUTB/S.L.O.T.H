from typing import Any, Dict, Optional, cast

from docker.models.services import Service

from src.config import Constants, env
from src.models import ServiceConfig
from src.utils import logger


class ServiceConfigExtractor(object):
    @staticmethod
    def extract(service: Service) -> Optional[ServiceConfig]:
        logger.debug(f"checking service {service.name}")  # type: ignore

        specs: Dict[str, Any] = service.attrs.get("Spec", {})
        labels: Dict[str, Any] = specs.get("Labels", {})

        if not ServiceConfigExtractor._is_enabled(labels=labels):
            return None

        if not ServiceConfigExtractor._matches_stack(labels=labels):
            return None

        return ServiceConfigExtractor._build(service_name=service.name, labels=labels)  # type: ignore

    @staticmethod
    def _is_enabled(labels: Dict[str, Any]) -> bool:
        return cast(str, labels.get(Constants.LABEL_ENABLED, "false")).lower() == "true"

    @staticmethod
    def _matches_stack(labels: Dict[str, Any]) -> bool:
        if not env.STACK_NAME:
            return True

        service_stack = cast(str, labels.get("com.docker.stack.namespace", ""))

        return service_stack == env.STACK_NAME

    @staticmethod
    def _build(service_name: str, labels: Dict[str, Any]) -> ServiceConfig:
        max_str = cast(
            str, labels.get(Constants.LABEL_MAX, str(env.DEFAULT_MAX_REPLICAS))
        )

        max_replicas = -1
        if max_str.lower() not in ["on-demand", "unlimited", "-1"]:
            max_replicas = int(max_str)

        return ServiceConfig(
            service_name=str(service_name),
            enabled=True,
            priority=labels.get(Constants.LABEL_PRIORITY, "medium"),
            min_replicas=int(labels.get(Constants.LABEL_MIN, env.DEFAULT_MIN_REPLICAS)),
            max_replicas=max_replicas,
            metric=labels.get(Constants.LABEL_METRIC, "cpu"),
            threshold_up=float(labels.get(Constants.LABEL_UP, "75")),
            threshold_down=float(labels.get(Constants.LABEL_DOWN, "25")),
        )
