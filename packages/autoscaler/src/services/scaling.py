import datetime
from typing import Dict, cast

from docker.client import DockerClient
from docker.models.services import Service

from src.config import env
from src.services.client import DockerClientService
from src.utils import logger


class ScalingService:
    scale_records: Dict[str, datetime.datetime] = {}

    @staticmethod
    def can_scale(service_name: str) -> bool:
        if service_name not in ScalingService.scale_records:
            return True

        elapsed = (
            datetime.datetime.now() - ScalingService.scale_records[service_name]
        ).total_seconds()
        return elapsed >= env.COOLDOWN_PERIOD

    @staticmethod
    def scale(
        client: DockerClient, service_name: str, target_replicas: int, reason: str
    ) -> bool:
        try:
            service = cast(Service, client.services.get(service_name))  # type: ignore
            current = DockerClientService.get_current_replicas(
                client=client, service_name=service_name
            )

            if not current:
                logger.error(
                    f"could not scale {service_name}, failed to get current replicas"
                )
                return False

            service.update(mode={"Replicated": {"Replicas": target_replicas}})  # type: ignore

            direction = "UP" if target_replicas > current else "DOWN"
            logger.info(
                f"{direction} {service_name}: {current} -> {target_replicas} (reason: {reason})"
            )

            ScalingService.scale_records[service_name] = datetime.datetime.now()

            return True
        except Exception as exception:
            logger.error(f"error scaling {service_name}: {exception}")
            return False
