import asyncio
import signal

import grpc
from grpc._typing import Any  # type: ignore
from proto_utils.generated.parsers import sql_builder_pb2, sql_builder_pb2_grpc

from src.core.config import settings
from src.handlers.sql_builder import sql_builder_handler
from src.utils.logger import logger


class SQLBuilderServicer(sql_builder_pb2_grpc.SQLBuilderServicer):
    """gRPC Servicer for SQL builder operations."""

    def __init__(self):
        """Initialize the SQL builder servicer."""
        logger.info(
            "[INIT] Initializing SQLBuilderServicer - "
            f"SQL Channel: {settings.SQL_BUILDER_CHANNEL}, "
            f"Debug Mode: {settings.SQL_BUILDER_DEBUG}"
        )

    def BuildSQL(
        self,
        request: sql_builder_pb2.BuildSQLRequest,
        context: grpc.aio.ServicerContext[Any, Any],
    ) -> sql_builder_pb2.BuildSQLResponse:
        table_name = request.table_name
        column_count = len(request.cols)

        logger.info(
            f"[SQL_BUILD] Request from client {context.peer()} - "
            f"Table: {table_name}, Columns: {column_count}"
        )

        try:
            response = sql_builder_handler(request)
            content_levels = len(response.content)

            logger.info(
                f"[SQL_BUILD] SQL building completed - "
                f"Content Levels: {content_levels}, Error: {bool(response.error)}"
            )

            return response
        except Exception as e:
            logger.error(f"[SQL_BUILD] Operation failed: {e}")
            raise


async def serve() -> None:
    """Start the gRPC SQL builder server."""
    # Create servicer instance
    servicer = SQLBuilderServicer()

    # Create and configure server
    server = grpc.aio.server()
    sql_builder_pb2_grpc.add_SQLBuilderServicer_to_server(servicer, server)
    server.add_insecure_port(settings.SQL_BUILDER_CHANNEL)

    # Start server
    logger.info("[SERVER] Starting gRPC SQL Builder server...")
    await server.start()

    logger.info(
        f"[SERVER] SQL Builder server ready on {settings.SQL_BUILDER_CHANNEL}"
    )
    logger.info(f"[SERVER] Debug mode: {settings.SQL_BUILDER_DEBUG}")

    # Set up graceful shutdown
    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("[SERVER] Shutdown signal received")
        stop_event.set()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, _signal_handler)
    loop.add_signal_handler(signal.SIGTERM, _signal_handler)

    try:
        await stop_event.wait()
    finally:
        logger.info("[SERVER] Stopping server...")
        await server.stop(grace=5)
        logger.info("[SERVER] Server stopped")


if __name__ == "__main__":
    """Main entry point for the SQL builder server."""
    try:
        logger.info("[MAIN] Initializing SQL Builder Server...")
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("[MAIN] Application terminated by user")
    except Exception as e:
        logger.error(f"[MAIN] Fatal error: {e}")
        raise
