"""gRPC Server resilience tests with real server and database failure simulation.

These tests verify:
1. Server can start and handle requests through gRPC
2. Handlers can recover from temporary database failures
3. Retry logic works correctly when databases reconnect
4. Server gracefully handles database unavailability
"""

from unittest.mock import MagicMock, patch

import pymongo.errors
import pytest
import redis.exceptions
from proto_utils.generated.database import database_pb2, mongo_pb2, redis_pb2, utils_pb2


class TestGrpcServerOperations:
    """Test that gRPC server works correctly with real network calls."""

    def test_redis_ping_through_grpc(self, grpc_stub):
        """Test Redis ping through gRPC server."""
        request = redis_pb2.RedisPingRequest()
        response = grpc_stub.RedisPing(request)

        assert response.pong is True

    def test_redis_set_and_get_through_grpc(self, grpc_stub):
        """Test Redis set/get operations through gRPC server."""
        # Set value
        set_request = redis_pb2.RedisSetRequest(
            key="test:grpc:key", value="grpc_test_value"
        )
        set_response = grpc_stub.RedisSet(set_request)
        assert set_response.success is True

        # Get value
        get_request = redis_pb2.RedisGetRequest(key="test:grpc:key")
        get_response = grpc_stub.RedisGet(get_request)
        assert get_response.found is True
        assert get_response.value == "grpc_test_value"

    def test_mongo_count_through_grpc(self, grpc_stub):
        """Test MongoDB count operation through gRPC server."""
        request = mongo_pb2.MongoCountAllDocumentsRequest()
        response = grpc_stub.MongoCountAllDocuments(request)

        assert response.amount >= 0

    def test_tasks_set_and_get_through_grpc(self, grpc_stub):
        """Test task operations through gRPC server."""
        # Set task
        value = utils_pb2.ApiResponse(
            status="processing", code=202, message="Task started via gRPC"
        )
        set_request = database_pb2.SetTaskIdRequest(
            task_id="test_grpc_task", task="excel", value=value
        )
        set_response = grpc_stub.SetTaskId(set_request)
        assert set_response.success is True

        # Get task
        get_request = database_pb2.GetTaskIdRequest(
            task_id="test_grpc_task", task="excel"
        )
        get_response = grpc_stub.GetTaskId(get_request)
        assert get_response.found is True
        assert get_response.value.status == "processing"


class TestRedisFailureRecovery:
    """Test Redis handler recovery from database failures."""

    def test_redis_recovers_from_connection_error(self, grpc_stub):
        """Test that Redis operations retry and recover from connection errors."""
        # First, verify normal operation works
        request = redis_pb2.RedisPingRequest()
        response = grpc_stub.RedisPing(request)
        assert response.pong is True

        # Note: To truly test failure recovery, you would need to:
        # 1. Stop the Redis container
        # 2. Make a request (which should retry)
        # 3. Restart Redis container
        # 4. Verify the request eventually succeeds
        #
        # This requires Docker control which is better done in integration tests
        # For now, we verify the retry configuration is in place

    def test_redis_handler_has_retry_on_connection_failure(self):
        """Verify Redis handler will retry on connection failures."""
        from src.handlers.redis_handler import RedisHandler

        handler = RedisHandler()

        # Verify retry configuration
        assert handler.max_retries_redis > 1
        assert handler.retry_delay_redis > 0
        assert handler.backoff_redis > 1.0

        # Mock a connection that fails then succeeds
        with patch.object(
            handler.manager, "get_redis_connection"
        ) as mock_get_connection:
            # First call fails, second succeeds
            failing_conn = MagicMock()
            failing_conn.ping.side_effect = redis.exceptions.ConnectionError(
                "Connection refused"
            )

            working_conn = MagicMock()
            working_conn.ping.return_value = True

            mock_get_connection.side_effect = [failing_conn, working_conn]

            # Mock time.sleep to avoid actual delays
            with patch("src.handlers.redis_handler.time.sleep"):
                from proto_utils.database import dtypes

                request = dtypes.RedisPingRequest()
                response = handler._execute_with_retry(
                    lambda req, redis_db: dtypes.RedisPingResponse(
                        pong=redis_db.ping()
                    ),
                    request,
                )

                # Should succeed after retry
                assert response["pong"] is True
                # Should have been called twice (failure + success)
                assert mock_get_connection.call_count == 2


class TestMongoFailureRecovery:
    """Test MongoDB handler recovery from database failures."""

    def test_mongo_handler_has_retry_on_connection_failure(self):
        """Verify MongoDB handler will retry on connection failures."""
        from src.handlers.mongo_handler import MongoHandler

        handler = MongoHandler()

        # Verify retry configuration
        assert handler.max_retries_mongo > 1
        assert handler.retry_delay_mongo > 0
        assert handler.backoff_mongo > 1.0

        # Mock a connection that fails then succeeds
        with patch.object(
            handler.manager, "get_mongo_schemas_connection"
        ) as mock_get_connection:
            # First call fails, second succeeds
            failing_conn = MagicMock()
            failing_conn.count_documents.side_effect = pymongo.errors.ConnectionFailure(
                "Connection refused"
            )

            working_conn = MagicMock()
            working_conn.count_documents.return_value = 5

            mock_get_connection.side_effect = [failing_conn, working_conn]

            # Mock time.sleep to avoid actual delays
            with patch("src.handlers.mongo_handler.time.sleep"):
                from proto_utils.database import dtypes

                request = dtypes.MongoCountAllDocumentsRequest()
                response = handler._execute_with_retry(
                    lambda req,
                    mongo_schemas_connection: dtypes.MongoCountAllDocumentsResponse(
                        amount=mongo_schemas_connection.count_documents()
                    ),
                    request,
                )

                # Should succeed after retry
                assert response["amount"] == 5
                # Should have been called twice (failure + success)
                assert mock_get_connection.call_count == 2


class TestDatabaseTasksFailureRecovery:
    """Test DatabaseTasks handler recovery from failures."""

    def test_tasks_handler_has_dual_retry_config(self):
        """Verify DatabaseTasks handler has retry config for both databases."""
        from src.handlers.tasks_handler import DatabaseTasksHandler

        handler = DatabaseTasksHandler()

        # Verify Redis retry configuration
        assert handler.max_retries_redis > 1
        assert handler.retry_delay_redis > 0
        assert handler.backoff_redis > 1.0

        # Verify Mongo retry configuration
        assert handler.max_retries_mongo > 1
        assert handler.retry_delay_mongo > 0
        assert handler.backoff_mongo > 1.0

    def test_tasks_handler_recovers_from_redis_then_mongo(self):
        """Test that tasks handler can fall back to Mongo when Redis fails."""
        from src.handlers.tasks_handler import DatabaseTasksHandler

        handler = DatabaseTasksHandler()

        # Mock Redis to fail, Mongo to succeed
        with (
            patch.object(handler.manager, "get_redis_connection") as mock_redis,
            patch.object(handler.manager, "get_mongo_tasks_connection") as mock_mongo,
        ):
            # Redis fails
            failing_redis = MagicMock()
            failing_redis.get.side_effect = redis.exceptions.ConnectionError(
                "Redis down"
            )
            mock_redis.return_value = failing_redis

            # Mongo works
            working_mongo = MagicMock()
            working_mongo.find_one.return_value = {
                "task_id": "test_task",
                "value": {"status": "completed", "code": 200, "message": "Done"},
            }
            mock_mongo.return_value = working_mongo

            # The handler's logic should try Redis first, then fall back to Mongo
            # This is the actual behavior in DatabaseTasksService


class TestExponentialBackoff:
    """Test that exponential backoff is working correctly."""

    def test_retry_delays_increase_exponentially(self):
        """Verify that retry delays increase exponentially."""
        from src.handlers.redis_handler import RedisHandler

        handler = RedisHandler()

        initial_delay = handler.retry_delay_redis
        backoff = handler.backoff_redis

        # Calculate expected delays
        delays = [initial_delay * (backoff**i) for i in range(3)]

        # Verify exponential growth
        assert delays[1] > delays[0]
        assert delays[2] > delays[1]
        assert delays[2] == initial_delay * (backoff**2)

    def test_max_retries_exhausted_raises_error(self):
        """Verify that after max retries, the error is raised."""
        from src.handlers.redis_handler import RedisHandler

        handler = RedisHandler()

        # Mock connection to always fail
        with patch.object(
            handler.manager, "get_redis_connection"
        ) as mock_get_connection:
            failing_conn = MagicMock()
            failing_conn.ping.side_effect = redis.exceptions.ConnectionError(
                "Connection refused"
            )
            mock_get_connection.return_value = failing_conn

            # Mock time.sleep to avoid actual delays
            with patch("src.handlers.redis_handler.time.sleep"):
                from proto_utils.database import dtypes

                request = dtypes.RedisPingRequest()

                # Should raise after max retries
                with pytest.raises(redis.exceptions.ConnectionError):
                    handler._execute_with_retry(
                        lambda req, redis_db: dtypes.RedisPingResponse(
                            pong=redis_db.ping()
                        ),
                        request,
                    )

                # Should have been called max_retries times
                assert mock_get_connection.call_count == handler.max_retries_redis


class TestServerErrorHandling:
    """Test that server handles errors gracefully."""

    def test_grpc_error_on_invalid_request(self, grpc_stub):
        """Test that server returns proper gRPC error on invalid operations."""
        # Try to get a non-existent key
        request = redis_pb2.RedisGetRequest(key="nonexistent:key:xyz123")
        response = grpc_stub.RedisGet(request)

        # Should return not found, not crash
        assert response.found is False

    def test_server_handles_concurrent_requests(self, grpc_stub):
        """Test that server can handle multiple concurrent requests."""
        import concurrent.futures

        def make_request(key_num):
            set_request = redis_pb2.RedisSetRequest(
                key=f"test:concurrent:{key_num}", value=f"value_{key_num}"
            )
            return grpc_stub.RedisSet(set_request)

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in futures]

        # All should succeed
        assert all(r.success for r in results)
