import asyncio
import signal

import grpc
from grpc._typing import Any  # type: ignore

from clients import sql_builder_pb2, sql_builder_pb2_grpc
from core.config import settings
from handlers.sql_builder import sql_builder_handler
from utils import logger


class SQLBuilderServicer(sql_builder_pb2_grpc.SQLBuilderServicer):
    def BuildSQL(
        self,
        request: sql_builder_pb2.BuildSQLRequest,
        context: grpc.aio.ServicerContext[Any, Any],
    ) -> sql_builder_pb2.BuildSQLResponse:
        logger.info("Received SQL building request")
        return sql_builder_handler(request)


async def serve() -> None:
    server = grpc.aio.server()

    sql_builder_pb2_grpc.add_SQLBuilderServicer_to_server(  # type: ignore
        SQLBuilderServicer(), server
    )

    server.add_insecure_port(settings.SQL_BUILDER_CHANNEL)

    await server.start()

    logger.info(f"running on {settings.SQL_BUILDER_CHANNEL}")
    logger.info(f"debug: {settings.SQL_BUILDER_DEBUG}")

    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("stop requested")
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, _signal_handler)
    loop.add_signal_handler(signal.SIGTERM, _signal_handler)

    await stop_event.wait()
    await server.stop(grace=5)

    logger.info("stopped")


if __name__ == "__main__":
    asyncio.run(serve())
