import asyncio
from utils.logger import logger

import grpc
from proto_utils.generated.database import (
    redis_pb2,
    mongo_pb2,
    database_pb2,
    database_pb2_grpc,
)

from core.config import settings
from handlers.redis import RedisHandler
from handlers.mongo import MongoHandler
from handlers.tasks import DatabaseTasksHandler


class DatabaseServicer(database_pb2_grpc.DatabaseServiceServicer):
    def RedisGetKeys(
        self,
        request: redis_pb2.RedisGetKeysRequest,
        _: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisGetKeysResponse:
        logger.info(f"Received RedisGetKeys request: {request}")
        return RedisHandler.get_keys(request)

    def RedisSet(
        self,
        request: redis_pb2.RedisSetRequest,
        _: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisSetResponse:
        logger.info(f"Received RedisSet request: {request}")
        return RedisHandler.set(request)

    def RedisGet(
        self,
        request: redis_pb2.RedisGetRequest,
        _: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisGetResponse:
        logger.info(f"Received RedisGet request: {request}")
        return RedisHandler.get(request)

    def RedisDelete(
        self,
        request: redis_pb2.RedisDeleteRequest,
        _: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisDeleteResponse:
        logger.info(f"Received RedisDelete request: {request}")
        return RedisHandler.delete(request)

    def RedisPing(
        self,
        request: redis_pb2.RedisPingRequest,
        _: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisPingResponse:
        logger.info(f"Received RedisPing request: {request}")
        return RedisHandler.ping(request)

    def RedisGetCache(
        self,
        request: redis_pb2.RedisGetCacheRequest,
        _: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisGetCacheResponse:
        logger.info(f"Received RedisGetCache request: {request}")
        return RedisHandler.get_cache(request)

    def RedisClearCache(
        self,
        request: redis_pb2.RedisClearCacheRequest,
        _: grpc.aio.ServicerContext,
    ) -> redis_pb2.RedisClearCacheResponse:
        logger.info(f"Received RedisClearCache request: {request}")
        return RedisHandler.clear_cache(request)

    def MongoInsertOneSchema(
        self,
        request: mongo_pb2.MongoInsertOneSchemaRequest,
        _: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoInsertOneSchemaResponse:
        logger.info(f"Received MongoInsertOneSchema request: {request}")
        return MongoHandler.insert_one_schema(request)

    def MongoCountAllDocuments(
        self,
        request: mongo_pb2.MongoCountAllDocumentsRequest,
        _: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoCountAllDocumentsResponse:
        logger.info(f"Received MongoCountAllDocuments request: {request}")
        return MongoHandler.count_all_documents(request)

    def MongoFindJsonSchema(
        self,
        request: mongo_pb2.MongoFindJsonSchemaRequest,
        _: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoFindJsonSchemaResponse:
        logger.info(f"Received MongoFindJsonSchema request: {request}")
        return MongoHandler.find_jsonschema(request)

    def MongoUpdateOneJsonSchema(
        self,
        request: mongo_pb2.MongoUpdateOneJsonSchemaRequest,
        _: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoUpdateOneJsonSchemaResponse:
        logger.info(f"Received MongoUpdateOneJsonSchema request: {request}")
        return MongoHandler.update_one_jsonschema(request)

    def MongoDeleteOneJsonSchema(
        self,
        request: mongo_pb2.MongoDeleteOneJsonSchemaRequest,
        _: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoDeleteOneJsonSchemaResponse:
        logger.info(f"Received MongoDeleteOneJsonSchema request: {request}")
        return MongoHandler.delete_one_jsonschema(request)

    def MongoDeleteImportName(
        self,
        request: mongo_pb2.MongoDeleteImportNameRequest,
        _: grpc.aio.ServicerContext,
    ) -> mongo_pb2.MongoDeleteImportNameResponse:
        logger.info(f"Received MongoDeleteImportName request: {request}")
        return MongoHandler.delete_import_name(request)

    def UpdateTaskId(
        self,
        request: database_pb2.UpdateTaskIdRequest,
        _: grpc.aio.ServicerContext,
    ) -> database_pb2.UpdateTaskIdResponse:
        logger.info(f"Received UpdateTaskId request: {request}")
        return DatabaseTasksHandler.update_task_id(request)

    def GetTaskId(
        self,
        request: database_pb2.GetTaskIdRequest,
        _: grpc.aio.ServicerContext,
    ) -> database_pb2.GetTaskIdResponse:
        logger.info(f"Received GetTaskId request: {request}")
        return DatabaseTasksHandler.get_task_id(request)

    def GetTasksByImportName(
        self,
        request: database_pb2.GetTasksByImportNameRequest,
        _: grpc.aio.ServicerContext,
    ) -> database_pb2.GetTasksByImportNameResponse:
        logger.info(f"Received GetTasksByImportName request: {request}")
        return DatabaseTasksHandler.get_tasks_by_import_name(request)

    def SetTaskId(
        self,
        request: database_pb2.SetTaskIdRequest,
        _: grpc.aio.ServicerContext,
    ) -> database_pb2.SetTaskIdResponse:
        logger.info(f"Received SetTaskId request: {request}")
        return DatabaseTasksHandler.set_task_id(request)


async def serve() -> None:
    server = grpc.aio.server()
    database_pb2_grpc.add_DatabaseServiceServicer_to_server(DatabaseServicer(), server)
    server.add_insecure_port(settings.DATABASE_CONNECTION_CHANNEL)
    await server.start()
    logger.info(
        (
            f"Database server started on {settings.DATABASE_CONNECTION_CHANNEL}"
            f" -- DEBUG: {settings.DATABASE_CONNECTION_DEBUG}"
        )
    )
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
