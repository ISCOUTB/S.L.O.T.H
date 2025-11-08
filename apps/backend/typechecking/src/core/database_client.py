import logging
from typing import Optional

from proto_utils.database.base_client import DatabaseClient

from src.core.config import settings


def get_database_client(
    logger: Optional[logging.Logger] = None,
) -> DatabaseClient:
    """Create a new DatabaseClient instance with retry configuration.

    Returns a configured DatabaseClient with automatic retry on failures,
    exponential backoff, and channel health checking. Each call creates
    a new independent client instance suitable for worker threads.

    Returns:
        DatabaseClient: Configured client with retry logic.

    Configuration:
        - max_retries: 3 attempts before failing
        - retry_delay: 1 second initial delay
        - backoff: 2.0 (exponential: 1s, 2s, 4s)

    Example:
        >>> client = get_database_client()
        >>> response = client.get_task_id(request)
        >>> client.close()  # Clean up when done

    Note:
        For worker threads, create one client per worker to avoid
        sharing gRPC channels across threads. The client is thread-safe
        for its own operations but should not be shared between threads.
    """
    return DatabaseClient(
        settings.DATABASE_CONNECTION_CHANNEL,
        max_retries=settings.DATABASE_MAX_RETRIES,
        retry_delay=settings.DATABASE_RETRY_DELAY_SECONDS,
        backoff=settings.DATABASE_BACKOFF_MULTIPLIER,
        logger=logger,
    )
