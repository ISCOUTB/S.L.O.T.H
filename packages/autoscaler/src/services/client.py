import functools
from typing import List, Optional, Tuple, cast

from docker.client import DockerClient
from docker.models.services import Service

from src.utils import logger


class DockerClientService(object):
    @staticmethod
    @functools.lru_cache(maxsize=1)
    def get_services(client: DockerClient) -> List[Service]:
        return cast(List[Service], client.services.list())  # type: ignore

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
    def get_running_replicas(client: DockerClient, service_name: str) -> Optional[int]:
        try:
            service = cast(Service, client.services.get(service_name))  # type: ignore
            tasks = service.tasks(filters={"desired-state": "running"})  # type: ignore

            running: List[Service] = [
                t
                for t in tasks  # type: ignore
                if t.get("Status", {}).get("State") == "running"  # type: ignore
            ]

            return len(running)
        except Exception as exception:
            logger.error(
                f"error getting running replicas for {service_name}: {exception}"
            )
            return None

    @staticmethod
    def get_replicas(
        client: DockerClient, service_name: str
    ) -> Optional[Tuple[int, int]]:
        try:
            running = DockerClientService.get_running_replicas(
                client=client, service_name=service_name
            )

            if running is None:
                raise Exception(f"could not get running replicas for {service_name}")

            current = DockerClientService.get_current_replicas(
                client=client, service_name=service_name
            )

            if current is None:
                raise Exception(f"could not get current replicas for {service_name}")

            return running, current
        except Exception as exception:
            logger.error(f"error getting replicas for {service_name}: {exception}")
            return None
