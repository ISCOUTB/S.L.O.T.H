"""gRPC DDL Generator Server.

This module implements a gRPC server that provides DDL (Data Definition Language)
generation services for the ETL design system. It processes AST (Abstract Syntax Tree)
structures and column information to generate SQL DDL statements.

The server provides the following services:
    - DDL generation: converts AST and column data to SQL DDL statements

Architecture:
    Client -> gRPC DDL Generator Server (this) -> DDL Generator Handler -> Core Logic

Logging Enhancements:
    - Structured logging with operation tags for filtering and debugging
    - Client information tracking for connection monitoring
    - Detailed request/response logging with sanitized data
    - Error handling with contextual information
    - Performance tracking and operation success/failure metrics
"""

import asyncio
import signal

import grpc
from grpc._typing import Any  # type: ignore
from proto_utils.generated.parsers import (
    ddl_generator_pb2,
    ddl_generator_pb2_grpc,
)

from src.core.config import settings
from src.handlers.ddl_generator import generate_ddl_handler
from src.utils.logger import logger


class DDLGeneratorServicer(ddl_generator_pb2_grpc.DDLGeneratorServicer):
    """gRPC Servicer for DDL generation operations.

    This class implements the DDLGeneratorService gRPC interface, providing
    methods for converting AST structures and column information into SQL DDL.
    It acts as the entry point for all DDL generation requests in the ETL system.

    The servicer delegates actual DDL generation to specialized handlers
    while providing comprehensive logging, error handling, and client tracking.

    Attributes:
        None. The servicer is stateless and delegates to handler functions.

    Note:
        All operations are logged with structured tags for easy filtering
        and debugging. Client information is tracked for monitoring purposes.
    """

    def __init__(self):
        """Initialize the DDL generator servicer.

        Sets up the servicer with configuration logging. The servicer itself
        is stateless and relies on handler functions for actual DDL generation.
        """
        logger.info(
            "[INIT] Initializing DDLGeneratorServicer - "
            f"DDL Channel: {settings.DDL_GENERATOR_CHANNEL}, "
            f"Debug Mode: {settings.DDL_GENERATOR_DEBUG}"
        )

    def GenerateDDL(
        self,
        request: ddl_generator_pb2.DDLRequest,
        context: grpc.aio.ServicerContext[Any, Any],
    ) -> ddl_generator_pb2.DDLResponse:
        column_count = len(request.columns)
        ast_type = request.ast.type if request.HasField("ast") else "NO_AST"

        logger.info(
            f"[DDL_GENERATE] Request from client {context.peer()} - "
            f"AST Type: {ast_type}, Column Count: {column_count}"
        )

        try:
            response = generate_ddl_handler(request)
            sql_length = len(response.sql) if response.sql else 0

            logger.info(
                f"[DDL_GENERATE] DDL generation completed - "
                f"Response Type: {response.type}, SQL Length: {sql_length} chars"
            )

            return response
        except Exception as e:
            logger.error(f"[DDL_GENERATE] Operation failed: {e}")
            raise


async def serve() -> None:
    """Start the gRPC DDL generator server."""
    # Create servicer instance
    servicer = DDLGeneratorServicer()

    # Create and configure server
    server = grpc.aio.server()
    ddl_generator_pb2_grpc.add_DDLGeneratorServicer_to_server(servicer, server)
    server.add_insecure_port(settings.DDL_GENERATOR_CHANNEL)

    # Start server
    logger.info("[SERVER] Starting gRPC DDL Generator server...")
    await server.start()

    logger.info(
        f"[SERVER] DDL Generator server ready on {settings.DDL_GENERATOR_CHANNEL}"
    )
    logger.info(f"[SERVER] Debug mode: {settings.DDL_GENERATOR_DEBUG}")

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
    """Main entry point for the DDL generator server."""
    try:
        logger.info("[MAIN] Initializing DDL Generator Server...")
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("[MAIN] Application terminated by user")
    except Exception as e:
        logger.error(f"[MAIN] Fatal error: {e}")
        raise
