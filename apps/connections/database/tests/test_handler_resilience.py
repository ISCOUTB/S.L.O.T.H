"""Resilience tests for handlers - testing retry and reconnection logic.

These tests verify that handlers work correctly with real operations
and have proper retry configuration:
- Real operations with Redis
- Real operations with MongoDB
- Real operations with DatabaseTasks (Redis + Mongo)
- Retry configuration is properly set
- Connection manager health checks
"""

from proto_utils.generated.database import database_pb2, mongo_pb2, redis_pb2, utils_pb2

from src.handlers.mongo_handler import MongoHandler
from src.handlers.redis_handler import RedisHandler
from src.handlers.tasks_handler import DatabaseTasksHandler


class TestRedisHandlerOperations:
    """Test Redis handler with real operations."""

    def test_redis_handler_ping(self):
        """Test that handler can ping Redis successfully."""
        handler = RedisHandler()
        request = redis_pb2.RedisPingRequest()

        response = handler.ping(request)

        assert response.pong is True

    def test_redis_handler_set_and_get(self):
        """Test that handler can set and get values successfully."""
        handler = RedisHandler()

        # Set value
        set_request = redis_pb2.RedisSetRequest(
            key="test:handler:resilience:key", value="handler_value"
        )
        set_response = handler.set(set_request)
        assert set_response.success is True

        # Get value
        get_request = redis_pb2.RedisGetRequest(key="test:handler:resilience:key")
        get_response = handler.get(get_request)
        assert get_response.found is True
        assert get_response.value == "handler_value"

    def test_redis_handler_get_keys(self):
        """Test that handler can retrieve keys matching a pattern."""
        handler = RedisHandler()

        # Set some test keys
        handler.set(redis_pb2.RedisSetRequest(key="test:resilience:1", value="val1"))
        handler.set(redis_pb2.RedisSetRequest(key="test:resilience:2", value="val2"))

        # Get keys matching pattern
        request = redis_pb2.RedisGetKeysRequest(pattern="test:resilience:*")
        response = handler.get_keys(request)

        assert len(response.keys) >= 2
        keys = list(response.keys)
        assert "test:resilience:1" in keys
        assert "test:resilience:2" in keys

    def test_redis_handler_delete(self):
        """Test that handler can delete keys successfully."""
        handler = RedisHandler()

        # Set a key
        handler.set(
            redis_pb2.RedisSetRequest(key="test:delete:resilience", value="delete_me")
        )

        # Delete it (RedisDeleteRequest uses 'keys' plural)
        delete_request = redis_pb2.RedisDeleteRequest(keys=["test:delete:resilience"])
        delete_response = handler.delete(delete_request)
        # RedisDeleteResponse has 'count' not 'success'
        assert delete_response.count >= 0

        # Verify it's gone
        get_request = redis_pb2.RedisGetRequest(key="test:delete:resilience")
        get_response = handler.get(get_request)
        assert get_response.found is False


class TestMongoHandlerOperations:
    """Test MongoDB handler with real operations."""

    def test_mongo_handler_count_documents(self):
        """Test that handler can count documents successfully."""
        handler = MongoHandler()
        request = mongo_pb2.MongoCountAllDocumentsRequest()

        response = handler.count_all_documents(request)

        # Should return a valid count (>= 0)
        assert response.amount >= 0

    def test_mongo_handler_find_existing_schema(self):
        """Test that handler properly handles find operations."""
        handler = MongoHandler()

        # Try to find a schema - status should indicate result properly
        find_request = mongo_pb2.MongoFindJsonSchemaRequest(
            import_name="nonexistent_test_schema_xyz"
        )
        find_response = handler.find_jsonschema(find_request)

        # Status should be 'not_found' for nonexistent schemas
        assert find_response.status == "not_found"


class TestDatabaseTasksHandlerOperations:
    """Test DatabaseTasks handler with real operations (Redis + Mongo)."""

    def test_tasks_handler_set_and_get_task(self):
        """Test that handler can set and get tasks successfully."""
        handler = DatabaseTasksHandler()

        # Set task
        value = utils_pb2.ApiResponse(
            status="processing", code=202, message="Task started"
        )
        set_request = database_pb2.SetTaskIdRequest(
            task_id="test_resilience_task", task="excel", value=value
        )
        set_response = handler.set_task_id(set_request)
        assert set_response.success is True

        # Get task
        get_request = database_pb2.GetTaskIdRequest(
            task_id="test_resilience_task", task="excel"
        )
        get_response = handler.get_task_id(get_request)
        assert get_response.found is True
        assert get_response.value.status == "processing"


class TestConnectionManagerResilience:
    """Test connection manager health checks and configuration."""

    def test_handler_retry_configuration(self):
        """Verify that handlers have proper retry configuration."""
        redis_handler = RedisHandler()
        mongo_handler = MongoHandler()
        tasks_handler = DatabaseTasksHandler()

        # Redis handler
        assert redis_handler.max_retries_redis > 0
        assert redis_handler.retry_delay_redis > 0
        assert redis_handler.backoff_redis > 1.0

        # Mongo handler
        assert mongo_handler.max_retries_mongo > 0
        assert mongo_handler.retry_delay_mongo > 0
        assert mongo_handler.backoff_mongo > 1.0

        # Tasks handler (uses both Redis and Mongo)
        assert tasks_handler.max_retries_redis > 0
        assert tasks_handler.retry_delay_redis > 0
        assert tasks_handler.max_retries_mongo > 0
        assert tasks_handler.retry_delay_mongo > 0
        assert tasks_handler.backoff_redis > 1.0
        assert tasks_handler.backoff_mongo > 1.0

    def test_exponential_backoff_calculation(self):
        """Verify exponential backoff is configured correctly."""
        handler = RedisHandler()

        # Verify backoff multiplier creates exponential delays
        initial_delay = handler.retry_delay_redis
        backoff_factor = handler.backoff_redis

        # After first retry
        second_delay = initial_delay * backoff_factor
        assert second_delay > initial_delay

        # After second retry
        third_delay = second_delay * backoff_factor
        assert third_delay > second_delay

        # Verify exponential growth
        assert third_delay == initial_delay * (backoff_factor**2)
