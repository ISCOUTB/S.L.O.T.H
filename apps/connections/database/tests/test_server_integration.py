"""Integration tests for the gRPC Database Server.

These tests verify that the server components are properly initialized
and that handlers are correctly wired up. For full end-to-end testing
of database operations, see tests/services/.

Note: Full gRPC server testing requires async setup which is handled
by the actual server runtime. These tests focus on component integration.
"""

from src.handlers.mongo_handler import MongoHandler
from src.handlers.redis_handler import RedisHandler
from src.handlers.tasks_handler import DatabaseTasksHandler
from src.server import DatabaseServicer


class TestServerComponentIntegration:
    """Test that server components are properly integrated."""

    def test_database_servicer_initialization(self):
        """Test that DatabaseServicer initializes with all handlers."""
        servicer = DatabaseServicer()

        # Verify all handlers are initialized
        assert hasattr(servicer, "redis_handler")
        assert hasattr(servicer, "mongo_handler")
        assert hasattr(servicer, "database_tasks_handler")

        # Verify handlers are the correct type
        assert isinstance(servicer.redis_handler, RedisHandler)
        assert isinstance(servicer.mongo_handler, MongoHandler)
        assert isinstance(servicer.database_tasks_handler, DatabaseTasksHandler)

    def test_redis_handler_has_connection_manager(self):
        """Test that Redis handler has access to connection manager."""
        servicer = DatabaseServicer()
        handler = servicer.redis_handler

        assert hasattr(handler, "manager")
        assert handler.manager is not None
        assert hasattr(handler, "max_retries_redis")
        assert hasattr(handler, "retry_delay_redis")

    def test_mongo_handler_has_connection_manager(self):
        """Test that Mongo handler has access to connection manager."""
        servicer = DatabaseServicer()
        handler = servicer.mongo_handler

        assert hasattr(handler, "manager")
        assert handler.manager is not None
        assert hasattr(handler, "max_retries_mongo")
        assert hasattr(handler, "retry_delay_mongo")

    def test_tasks_handler_has_both_connection_configs(self):
        """Test that Tasks handler has both Redis and Mongo configurations."""
        servicer = DatabaseServicer()
        handler = servicer.database_tasks_handler

        assert hasattr(handler, "manager")
        assert handler.manager is not None

        # Verify both Redis and Mongo retry configurations
        assert hasattr(handler, "max_retries_redis")
        assert hasattr(handler, "retry_delay_redis")
        assert hasattr(handler, "max_retries_mongo")
        assert hasattr(handler, "retry_delay_mongo")

    def test_servicer_has_all_grpc_methods(self):
        """Test that servicer implements all required gRPC methods."""
        servicer = DatabaseServicer()

        # Redis operations
        assert hasattr(servicer, "RedisGetKeys")
        assert hasattr(servicer, "RedisSet")
        assert hasattr(servicer, "RedisGet")
        assert hasattr(servicer, "RedisDelete")
        assert hasattr(servicer, "RedisPing")
        assert hasattr(servicer, "RedisGetCache")
        assert hasattr(servicer, "RedisClearCache")

        # MongoDB operations
        assert hasattr(servicer, "MongoInsertOneSchema")
        assert hasattr(servicer, "MongoCountAllDocuments")
        assert hasattr(servicer, "MongoFindJsonSchema")
        assert hasattr(servicer, "MongoUpdateOneJsonSchema")
        assert hasattr(servicer, "MongoDeleteOneJsonSchema")
        assert hasattr(servicer, "MongoDeleteImportName")

        # Task operations
        assert hasattr(servicer, "UpdateTaskId")
        assert hasattr(servicer, "GetTaskId")
        assert hasattr(servicer, "GetTasksByImportName")
        assert hasattr(servicer, "SetTaskId")

    def test_handlers_use_correct_retry_configurations(self):
        """Test that handlers have reasonable retry configurations."""
        servicer = DatabaseServicer()

        # Redis handler
        redis_handler = servicer.redis_handler
        assert redis_handler.max_retries_redis > 0
        assert redis_handler.retry_delay_redis > 0
        assert redis_handler.backoff_redis >= 1.0

        # Mongo handler
        mongo_handler = servicer.mongo_handler
        assert mongo_handler.max_retries_mongo > 0
        assert mongo_handler.retry_delay_mongo > 0
        assert mongo_handler.backoff_mongo >= 1.0

        # Tasks handler (has both)
        tasks_handler = servicer.database_tasks_handler
        assert tasks_handler.max_retries_redis > 0
        assert tasks_handler.max_retries_mongo > 0


class TestHandlerInitialization:
    """Test individual handler initialization."""

    def test_redis_handler_initialization(self):
        """Test that RedisHandler initializes correctly."""
        handler = RedisHandler()

        assert handler.manager is not None
        assert handler.max_retries_redis > 0
        assert handler.retry_delay_redis > 0
        assert handler.backoff_redis >= 1.0

    def test_mongo_handler_initialization(self):
        """Test that MongoHandler initializes correctly."""
        handler = MongoHandler()

        assert handler.manager is not None
        assert handler.max_retries_mongo > 0
        assert handler.retry_delay_mongo > 0
        assert handler.backoff_mongo >= 1.0

    def test_tasks_handler_initialization(self):
        """Test that DatabaseTasksHandler initializes correctly."""
        handler = DatabaseTasksHandler()

        assert handler.manager is not None
        # Has both Redis and Mongo configs
        assert handler.max_retries_redis > 0
        assert handler.retry_delay_redis > 0
        assert handler.backoff_redis >= 1.0
        assert handler.max_retries_mongo > 0
        assert handler.retry_delay_mongo > 0
        assert handler.backoff_mongo >= 1.0


class TestHandlerOperationMethods:
    """Test that handlers expose the correct operation methods."""

    def test_redis_handler_has_all_operations(self):
        """Test that RedisHandler has all required methods."""
        handler = RedisHandler()

        assert hasattr(handler, "get_keys")
        assert hasattr(handler, "set")
        assert hasattr(handler, "get")
        assert hasattr(handler, "delete")
        assert hasattr(handler, "ping")
        assert hasattr(handler, "get_cache")
        assert hasattr(handler, "clear_cache")
        assert hasattr(handler, "_execute_with_retry")

    def test_mongo_handler_has_all_operations(self):
        """Test that MongoHandler has all required methods."""
        handler = MongoHandler()

        assert hasattr(handler, "insert_one_schema")
        assert hasattr(handler, "count_all_documents")
        assert hasattr(handler, "find_jsonschema")
        assert hasattr(handler, "update_one_jsonschema")
        assert hasattr(handler, "delete_one_jsonschema")
        assert hasattr(handler, "delete_import_name")
        assert hasattr(handler, "_execute_with_retry")

    def test_tasks_handler_has_all_operations(self):
        """Test that DatabaseTasksHandler has all required methods."""
        handler = DatabaseTasksHandler()

        assert hasattr(handler, "update_task_id")
        assert hasattr(handler, "get_task_id")
        assert hasattr(handler, "get_tasks_by_import_name")
        assert hasattr(handler, "set_task_id")
        assert hasattr(handler, "_execute_with_retry")
