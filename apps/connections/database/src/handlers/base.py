from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

from src.core.config import settings
from src.core.connection_manager import get_connection_manager

T = TypeVar("T")
Request = TypeVar("Request")


class BaseHandler(ABC):
    def __init__(self):
        super().__init__()
        self.manager = get_connection_manager()
        self.max_retries_redis: int = settings.REDIS_MAX_RETRIES
        self.retry_delay_redis: float = settings.REDIS_RETRY_DELAY_SECONDS
        self.backoff_redis: float = settings.REDIS_RETRY_BACKOFF_FACTOR

        self.max_retries_mongo: int = settings.MONGO_MAX_RETRIES
        self.retry_delay_mongo: float = settings.MONGO_RETRY_DELAY_SECONDS
        self.backoff_mongo: float = settings.MONGO_RETRY_BACKOFF_FACTOR

    @abstractmethod
    def _execute_with_retry(
        self, operation: Callable[[Request, Any], T], request: Request
    ) -> T:
        """Execute a database operation with automatic retry on connection failure.

        Args:
            operation (Callable[[Request, Any], T]): The database operation to execute.
            request (Request): The request data for the operation.

        Returns:
            T: The result of the database operation.
        """
        pass
