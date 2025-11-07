"""gRPC Database Server.

This module implements a gRPC server that provides database operations
for Redis, MongoDB, and task management. It acts as a unified interface
for database operations across the ETL design system.

The server provides the following services:
    - Redis operations: get, set, delete, ping, cache management
    - MongoDB operations: schema management, document operations
    - Task management: task ID tracking and import name associations

Architecture:
    Client -> gRPC Database Server (this) -> Database Handlers -> Redis/MongoDB

Logging Enhancements:
    - Structured logging with operation tags for filtering and debugging
    - Client information tracking for connection monitoring
    - Detailed request/response logging with sanitized data
    - Error handling with contextual information
    - Performance tracking and operation success/failure metrics
"""

import asyncio

import grpc
from proto_utils.generated.database import (
    database_pb2,
    database_pb2_grpc,
    mongo_pb2,
    redis_pb2,
)

from src.core.config import settings
from src.core.connection_manager import get_connection_manager
from src.handlers.mongo_handler import MongoHandler
from src.handlers.redis_handler import RedisHandler
from src.handlers.tasks_handler import DatabaseTasksHandler
from src.utils.logger import logger


class DatabaseServicer(database_pb2_grpc.DatabaseServiceServicer):
    """gRPC Servicer for database operations.

    This class implements the DatabaseService gRPC interface, providing
    methods for Redis operations, MongoDB schema management, and task tracking.
    It acts as a unified gateway for all database operations in the ETL system.

    The servicer delegates actual database operations to specialized handlers
    while providing comprehensive logging, error handling, and client tracking.

    Attributes:
        None. The servicer is stateless and delegates to handler classes.

    Note:
        All operations are logged with structured tags for easy filtering
        and debugging. Client information is tracked for monitoring purposes.
    """

    def __init__(self):
        """Initialize the database servicer.

        Sets up the servicer with configuration logging. The servicer itself
        is stateless and relies on handler classes for actual database operations.
        """
        logger.info(
            "[INIT] Initializing DatabaseServicer - "
            f"Database Channel: {settings.DATABASE_CONNECTION_CHANNEL}, "
            f"Debug Mode: {settings.DATABASE_CONNECTION_DEBUG}"
        )

        self.redis_handler = RedisHandler()
        self.mongo_handler = MongoHandler()
        self.database_tasks_handler = DatabaseTasksHandler()

    def RedisGetKeys(
        self,
        request: redis_pb2.RedisGetKeysRequest,
        context: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisGetKeysResponse:
        """Retrieve Redis keys based on pattern.

        Args:
            request: Request containing the key pattern to search for.
            context: gRPC service context for the request.

        Returns:
            RedisGetKeysResponse containing the matching keys.

        Raises:
            grpc.RpcError: If Redis operation fails.
        """
        logger.info(
            f"[REDIS_GET_KEYS] Request from client {context.peer()} - "
            f"Pattern: '{request.pattern}'"
        )

        try:
            response = self.redis_handler.get_keys(request)
            key_count = len(response.keys)
            logger.info(f"[REDIS_GET_KEYS] Successfully retrieved {key_count} keys")
            return response
        except Exception as e:
            logger.error(f"[REDIS_GET_KEYS] Operation failed: {e}")
            raise

    def RedisSet(
        self,
        request: redis_pb2.RedisSetRequest,
        context: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisSetResponse:
        """Set a Redis key-value pair.

        Args:
            request: Request containing the key and value to set.
            context: gRPC service context for the request.

        Returns:
            RedisSetResponse indicating operation success.

        Raises:
            grpc.RpcError: If Redis operation fails.
        """
        expiration_info = (
            f", TTL: {request.expiration}s" if request.HasField("expiration") else ""
        )
        logger.info(
            f"[REDIS_SET] Request from client {context.peer()} - "
            f"Key: '{request.key}'{expiration_info}"
        )

        try:
            response = self.redis_handler.set(request)
            logger.info(
                f"[REDIS_SET] Key operation completed - "
                f"Key: '{request.key}', Success: {response.success}"
            )
            return response
        except Exception as e:
            logger.error(f"[REDIS_SET] Operation failed: {e}")
            raise

    def RedisGet(
        self,
        request: redis_pb2.RedisGetRequest,
        context: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisGetResponse:
        """Retrieve a value from Redis by key.

        Args:
            request: Request containing the key to retrieve.
            context: gRPC service context for the request.

        Returns:
            RedisGetResponse containing the value or indicating key not found.

        Raises:
            grpc.RpcError: If Redis operation fails.
        """
        logger.info(
            f"[REDIS_GET] Request from client {context.peer()} - Key: '{request.key}'"
        )

        try:
            response = self.redis_handler.get(request)
            logger.info(
                f"[REDIS_GET] Key lookup completed - "
                f"Key: '{request.key}', Found: {response.found}"
            )
            return response
        except Exception as e:
            logger.error(f"[REDIS_GET] Operation failed: {e}")
            raise

    def RedisDelete(
        self,
        request: redis_pb2.RedisDeleteRequest,
        context: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisDeleteResponse:
        """Delete Redis keys.

        Args:
            request: Request containing the keys to delete.
            context: gRPC service context for the request.

        Returns:
            RedisDeleteResponse indicating deletion count.

        Raises:
            grpc.RpcError: If Redis operation fails.
        """
        key_count = len(request.keys)
        logger.info(
            f"[REDIS_DELETE] Request from client {context.peer()} - "
            f"KeyCount: {key_count}"
        )

        try:
            response = self.redis_handler.delete(request)
            logger.info(
                f"[REDIS_DELETE] Key deletion completed - "
                f"RequestedKeys: {key_count}, DeletedKeys: {response.count}"
            )
            return response
        except Exception as e:
            logger.error(f"[REDIS_DELETE] Operation failed: {e}")
            raise

    def RedisPing(
        self,
        request: redis_pb2.RedisPingRequest,
        context: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisPingResponse:
        """Ping Redis to check connection status.

        Args:
            request: Ping request (typically empty).
            context: gRPC service context for the request.

        Returns:
            RedisPingResponse indicating connection status.

        Raises:
            grpc.RpcError: If Redis connection fails.
        """
        logger.info(f"[REDIS_PING] Health check request from client {context.peer()}")

        try:
            response = self.redis_handler.ping(request)
            logger.info(
                f"[REDIS_PING] Health check completed - "
                f"Connection: {'OK' if response.pong else 'FAILED'}"
            )
            return response
        except Exception as e:
            logger.error(f"[REDIS_PING] Health check failed: {e}")
            raise

    def RedisGetCache(
        self,
        request: redis_pb2.RedisGetCacheRequest,
        context: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisGetCacheResponse:
        """Retrieve entire Redis cache.

        Args:
            request: Request for cache retrieval.
            context: gRPC service context for the request.

        Returns:
            RedisGetCacheResponse containing all cache entries.

        Raises:
            grpc.RpcError: If Redis operation fails.
        """
        logger.info(f"[REDIS_GET_CACHE] Request from client {context.peer()}")

        try:
            response = self.redis_handler.get_cache(request)
            cache_size = len(response.cache)
            logger.info(
                f"[REDIS_GET_CACHE] Cache retrieval completed - "
                f"CacheEntries: {cache_size}"
            )
            return response
        except Exception as e:
            logger.error(f"[REDIS_GET_CACHE] Operation failed: {e}")
            raise

    def RedisClearCache(
        self,
        request: redis_pb2.RedisClearCacheRequest,
        context: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisClearCacheResponse:
        """Clear entire Redis cache.

        Args:
            request: Request for cache clearing.
            context: gRPC service context for the request.

        Returns:
            RedisClearCacheResponse indicating clearing operation result.

        Raises:
            grpc.RpcError: If Redis operation fails.
        """
        logger.info(f"[REDIS_CLEAR_CACHE] Request from client {context.peer()}")

        try:
            response = self.redis_handler.clear_cache(request)
            logger.info(
                f"[REDIS_CLEAR_CACHE] Cache clear completed - "
                f"Success: {response.success}"
            )
            return response
        except Exception as e:
            logger.error(f"[REDIS_CLEAR_CACHE] Operation failed: {e}")
            raise

    def MongoInsertOneSchema(
        self,
        request: mongo_pb2.MongoInsertOneSchemaRequest,
        context: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoInsertOneSchemaResponse:
        """Insert a schema document into MongoDB.

        Args:
            request: Request containing the schema document to insert.
            context: gRPC service context for the request.

        Returns:
            MongoInsertOneSchemaResponse with insertion result and status.

        Raises:
            grpc.RpcError: If MongoDB operation fails.
        """
        schema_count = len(request.schemas_releases)
        logger.info(
            f"[MONGO_INSERT_SCHEMA] Request from client {context.peer()} - "
            f"ImportName: '{request.import_name}', SchemaReleases: {schema_count}"
        )

        try:
            response = self.mongo_handler.insert_one_schema(request)
            logger.info(
                f"[MONGO_INSERT_SCHEMA] Schema insertion completed - "
                f"ImportName: '{request.import_name}', Status: '{response.status}'"
            )
            return response
        except Exception as e:
            logger.error(f"[MONGO_INSERT_SCHEMA] Operation failed: {e}")
            raise

    def MongoCountAllDocuments(
        self,
        request: mongo_pb2.MongoCountAllDocumentsRequest,
        context: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoCountAllDocumentsResponse:
        """Count all documents in MongoDB collection.

        Args:
            request: Request for document count.
            context: gRPC service context for the request.

        Returns:
            MongoCountAllDocumentsResponse with document count.

        Raises:
            grpc.RpcError: If MongoDB operation fails.
        """
        logger.info(f"[MONGO_COUNT_DOCS] Request from client {context.peer()}")

        try:
            response = self.mongo_handler.count_all_documents(request)
            logger.info(
                f"[MONGO_COUNT_DOCS] Document count completed - "
                f"Count: {response.amount}"
            )
            return response
        except Exception as e:
            logger.error(f"[MONGO_COUNT_DOCS] Operation failed: {e}")
            raise

    def MongoFindJsonSchema(
        self,
        request: mongo_pb2.MongoFindJsonSchemaRequest,
        context: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoFindJsonSchemaResponse:
        """Find a JSON schema document in MongoDB.

        Args:
            request: Request containing search criteria for the schema.
            context: gRPC service context for the request.

        Returns:
            MongoFindJsonSchemaResponse containing the found schema or status.

        Raises:
            grpc.RpcError: If MongoDB operation fails.
        """
        logger.info(
            f"[MONGO_FIND_SCHEMA] Request from client {context.peer()} - "
            f"ImportName: '{request.import_name}'"
        )

        try:
            response = self.mongo_handler.find_jsonschema(request)
            has_schema = response.HasField("schema")
            logger.info(
                f"[MONGO_FIND_SCHEMA] Schema search completed - "
                f"ImportName: '{request.import_name}', Status: '{response.status}', "
                f"HasSchema: {has_schema}"
            )
            return response
        except Exception as e:
            logger.error(f"[MONGO_FIND_SCHEMA] Operation failed: {e}")
            raise

    def MongoUpdateOneJsonSchema(
        self,
        request: mongo_pb2.MongoUpdateOneJsonSchemaRequest,
        context: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoUpdateOneJsonSchemaResponse:
        """Update a JSON schema document in MongoDB.

        Args:
            request: Request containing schema ID and update data.
            context: gRPC service context for the request.

        Returns:
            MongoUpdateOneJsonSchemaResponse indicating update result.

        Raises:
            grpc.RpcError: If MongoDB operation fails.
        """
        logger.info(
            f"[MONGO_UPDATE_SCHEMA] Request from client {context.peer()} - "
            f"ImportName: '{request.import_name}'"
        )

        try:
            response = self.mongo_handler.update_one_jsonschema(request)
            logger.info(
                f"[MONGO_UPDATE_SCHEMA] Schema update completed - "
                f"ImportName: '{request.import_name}', Status: '{response.status}'"
            )
            return response
        except Exception as e:
            logger.error(f"[MONGO_UPDATE_SCHEMA] Operation failed: {e}")
            raise

    def MongoDeleteOneJsonSchema(
        self,
        request: mongo_pb2.MongoDeleteOneJsonSchemaRequest,
        context: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoDeleteOneJsonSchemaResponse:
        """Delete a JSON schema document from MongoDB.

        Args:
            request: Request containing the schema import name to delete.
            context: gRPC service context for the request.

        Returns:
            MongoDeleteOneJsonSchemaResponse indicating deletion result.

        Raises:
            grpc.RpcError: If MongoDB operation fails.
        """
        logger.info(
            f"[MONGO_DELETE_SCHEMA] Request from client {context.peer()} - "
            f"ImportName: '{request.import_name}'"
        )

        try:
            response = self.mongo_handler.delete_one_jsonschema(request)
            logger.info(
                f"[MONGO_DELETE_SCHEMA] Schema deletion completed - "
                f"ImportName: '{request.import_name}', Success: {response.success}, "
                f"Status: '{response.status}'"
            )
            return response
        except Exception as e:
            logger.error(f"[MONGO_DELETE_SCHEMA] Operation failed: {e}")
            raise

    def MongoDeleteImportName(
        self,
        request: mongo_pb2.MongoDeleteImportNameRequest,
        context: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoDeleteImportNameResponse:
        """Delete documents by import name from MongoDB.

        Args:
            request: Request containing the import name to delete.
            context: gRPC service context for the request.

        Returns:
            MongoDeleteImportNameResponse indicating deletion result.

        Raises:
            grpc.RpcError: If MongoDB operation fails.
        """
        logger.info(
            f"[MONGO_DELETE_IMPORT] Request from client {context.peer()} - "
            f"ImportName: '{request.import_name}'"
        )

        try:
            response = self.mongo_handler.delete_import_name(request)
            logger.info(
                f"[MONGO_DELETE_IMPORT] Import deletion completed - "
                f"ImportName: '{request.import_name}', Success: {response.success}, "
                f"Status: '{response.status}'"
            )
            return response
        except Exception as e:
            logger.error(f"[MONGO_DELETE_IMPORT] Operation failed: {e}")
            raise

    def UpdateTaskId(
        self,
        request: database_pb2.UpdateTaskIdRequest,
        context: grpc.aio.ServicerContext,
    ) -> database_pb2.UpdateTaskIdResponse:
        """Update a task ID in the database.

        Args:
            request: Request containing task update information.
            context: gRPC service context for the request.

        Returns:
            UpdateTaskIdResponse indicating update result.

        Raises:
            grpc.RpcError: If database operation fails.
        """
        logger.info(
            f"[TASKS_UPDATE] Request from client {context.peer()} - "
            f"TaskID: '{request.task_id}', Task: '{request.task}', "
            f"Field: '{request.field}'"
        )

        try:
            response = self.database_tasks_handler.update_task_id(request)
            logger.info(
                f"[TASKS_UPDATE] Task update completed - "
                f"TaskID: '{request.task_id}', Success: {response.success}"
            )
            return response
        except Exception as e:
            logger.error(f"[TASKS_UPDATE] Operation failed: {e}")
            raise

    def GetTaskId(
        self,
        request: database_pb2.GetTaskIdRequest,
        context: grpc.aio.ServicerContext,
    ) -> database_pb2.GetTaskIdResponse:
        """Retrieve a task ID from the database.

        Args:
            request: Request containing task identification parameters.
            context: gRPC service context for the request.

        Returns:
            GetTaskIdResponse containing the task data or not found indicator.

        Raises:
            grpc.RpcError: If database operation fails.
        """
        logger.info(
            f"[TASKS_GET] Request from client {context.peer()} - "
            f"TaskID: '{request.task_id}', Task: '{request.task}'"
        )

        try:
            response = self.database_tasks_handler.get_task_id(request)
            has_value = response.HasField("value")
            logger.info(
                f"[TASKS_GET] Task lookup completed - "
                f"TaskID: '{request.task_id}', Found: {response.found}, "
                f"HasValue: {has_value}"
            )
            return response
        except Exception as e:
            logger.error(f"[TASKS_GET] Operation failed: {e}")
            raise

    def GetTasksByImportName(
        self,
        request: database_pb2.GetTasksByImportNameRequest,
        context: grpc.aio.ServicerContext,
    ) -> database_pb2.GetTasksByImportNameResponse:
        """Retrieve tasks associated with an import name.

        Args:
            request: Request containing the import name to search for.
            context: gRPC service context for the request.

        Returns:
            GetTasksByImportNameResponse containing matching tasks.

        Raises:
            grpc.RpcError: If database operation fails.
        """
        logger.info(
            f"[TASKS_GET_BY_IMPORT] Request from client {context.peer()} - "
            f"ImportName: '{request.import_name}', Task: '{request.task}'"
        )

        try:
            response = self.database_tasks_handler.get_tasks_by_import_name(request)
            task_count = len(response.tasks)
            logger.info(
                f"[TASKS_GET_BY_IMPORT] Task lookup completed - "
                f"ImportName: '{request.import_name}', TaskCount: {task_count}"
            )
            return response
        except Exception as e:
            logger.error(f"[TASKS_GET_BY_IMPORT] Operation failed: {e}")
            raise

    def SetTaskId(
        self,
        request: database_pb2.SetTaskIdRequest,
        context: grpc.aio.ServicerContext,
    ) -> database_pb2.SetTaskIdResponse:
        """Set a task ID in the database.

        Args:
            request: Request containing task information to set.
            context: gRPC service context for the request.

        Returns:
            SetTaskIdResponse indicating set operation result.

        Raises:
            grpc.RpcError: If database operation fails.
        """
        logger.info(
            f"[TASKS_SET] Request from client {context.peer()} - "
            f"TaskID: '{request.task_id}', Task: '{request.task}'"
        )

        try:
            response = self.database_tasks_handler.set_task_id(request)
            logger.info(
                f"[TASKS_SET] Task set completed - "
                f"TaskID: '{request.task_id}', Success: {response.success}"
            )
            return response
        except Exception as e:
            logger.error(f"[TASKS_SET] Operation failed: {e}")
            raise


async def serve() -> None:
    """Start the gRPC database server.

    Creates and configures the gRPC server with the database servicer,
    then starts listening for incoming client connections on the configured
    address and port.

    The server runs indefinitely until terminated by a signal or an
    unrecoverable error occurs. It provides unified database access
    for Redis, MongoDB, and task management operations.

    Raises:
        RuntimeError: If server startup fails due to port conflicts or
                     configuration issues.
        ConnectionError: If database connections cannot be established.

    Note:
        This function will block until the server is terminated.
        Use Ctrl+C or send SIGTERM to gracefully shut down the server.
    """
    # Create servicer instance
    servicer = DatabaseServicer()

    # Create and configure server
    server = grpc.aio.server()
    database_pb2_grpc.add_DatabaseServiceServicer_to_server(servicer, server)
    server.add_insecure_port(settings.DATABASE_CONNECTION_CHANNEL)

    # Start server
    logger.info("[SERVER] Starting gRPC Database server...")
    logger.debug(
        f"[SERVER] Configuration - Channel: {settings.DATABASE_CONNECTION_CHANNEL}"
    )
    logger.debug(f"[SERVER] Debug Mode: {settings.DATABASE_CONNECTION_DEBUG}")

    await server.start()
    logger.info(
        f"[SERVER] Database server ready and listening on {settings.DATABASE_CONNECTION_CHANNEL}"
    )

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("[SERVER] Shutdown signal received, stopping server...")
    finally:
        logger.info("[SERVER] Database server stopped")


if __name__ == "__main__":
    """Main entry point for the database server.
    
    When run as a script, this starts the gRPC server and runs it until
    terminated. The server will handle KeyboardInterrupt gracefully.
    
    Example:
        $ python -m src.server
    """
    try:
        logger.info("[MAIN] Initializing gRPC Database Server...")
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("[MAIN] Application terminated by user")
        get_connection_manager().close_all()
    except Exception as e:
        logger.error(f"[MAIN] Fatal error: {e}")
        raise
