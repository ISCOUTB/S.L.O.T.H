from dataclasses import dataclass
from typing import Literal, Optional

type ServiceMetric = Literal["cpu", "memory"]
type ServicePriority = Literal["low", "medium", "high"]


@dataclass
class ServiceConfig:
    service_name: str
    enabled: bool
    min_replicas: int
    max_replicas: int
    metric: ServiceMetric
    threshold_up: float
    threshold_down: float
    priority: ServicePriority = "medium"
    custom_query: Optional[str] = None

    @property
    def is_on_demand(self) -> bool:
        return self.max_replicas == -1


if __name__ == "__main__":
    pass
