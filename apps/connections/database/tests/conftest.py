from typing import Generator

import pytest

from src.core.connection_manager import get_connection_manager
from src.core.database_mongo import MongoConnection
from src.core.database_redis import RedisConnection


@pytest.fixture(scope="session")
def redis_db() -> Generator[RedisConnection, None, None]:
    manager = get_connection_manager()
    try:
        redis_conn = manager.get_redis_connection()
        yield redis_conn
    finally:
        redis_conn.redis_client.close()


@pytest.fixture(scope="session")
def mongo_tasks_connection() -> Generator[MongoConnection, None, None]:
    manager = get_connection_manager()
    try:
        mongo_conn = manager.get_mongo_tasks_connection()
        yield mongo_conn
    finally:
        mongo_conn.client.close()


@pytest.fixture(scope="session")
def mongo_schemas_connection() -> Generator[MongoConnection, None, None]:
    manager = get_connection_manager()
    try:
        mongo_conn = manager.get_mongo_schemas_connection()
        yield mongo_conn
    finally:
        mongo_conn.client.close()
