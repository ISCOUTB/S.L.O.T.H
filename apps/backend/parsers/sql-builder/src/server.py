import asyncio
import logging

import grpc
from clients import sql_builder_pb2, sql_builder_pb2_grpc

from core.config import settings
from handlers.sql_builder import sql_builder_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SQLBuilderServer")


class SQLBuilderServicer(sql_builder_pb2_grpc.SQLBuilderServicer):
    def BuildSQL(
        self,
        request: sql_builder_pb2.BuildSQLRequest,
        _: grpc.aio.ServicerContext,
    ) -> sql_builder_pb2.BuildSQLResponse:
        logger.info("Received SQL building request")
        return sql_builder_handler(request)


async def serve() -> None:
    server = grpc.aio.server()
    sql_builder_pb2_grpc.add_SQLBuilderServicer_to_server(SQLBuilderServicer(), server)
    server.add_insecure_port(settings.SQL_BUILDER_CHANNEL)
    await server.start()
    logger.info(
        (
            f"SQL Builder server started on {settings.SQL_BUILDER_CHANNEL}"
            f" -- DEBUG: {settings.SQL_BUILDER_DEBUG}"
        )
    )
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
