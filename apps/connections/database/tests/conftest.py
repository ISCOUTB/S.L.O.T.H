import concurrent.futures
from typing import Generator

import grpc
import pytest
from proto_utils.generated.database import database_pb2_grpc

from src.core.connection_manager import get_connection_manager
from src.core.database_mongo import MongoConnection
from src.core.database_redis import RedisConnection
from src.server import DatabaseServicer


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


# gRPC Server Fixtures
@pytest.fixture(scope="module")
def grpc_server():
    """Start a real gRPC server for testing."""
    # Create thread pool executor
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    # Create server
    server = grpc.server(
        thread_pool,
        options=[
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
        ],
    )

    # Add servicer
    servicer = DatabaseServicer()
    database_pb2_grpc.add_DatabaseServiceServicer_to_server(servicer, server)

    # Use a test port
    test_port = "[::]:50052"
    server.add_insecure_port(test_port)

    # Start server
    server.start()

    yield test_port

    # Cleanup
    server.stop(grace=2)


@pytest.fixture
def grpc_channel(grpc_server):
    """Create a gRPC channel to the test server."""
    channel = grpc.insecure_channel(grpc_server)
    yield channel
    channel.close()


@pytest.fixture
def grpc_stub(grpc_channel):
    """Create a DatabaseService stub for gRPC testing."""
    return database_pb2_grpc.DatabaseServiceStub(grpc_channel)
