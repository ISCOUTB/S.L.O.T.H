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
from src.utils import logger


class DDLGeneratorServicer(ddl_generator_pb2_grpc.DDLGeneratorServicer):
    def GenerateDDL(
        self,
        request: ddl_generator_pb2.DDLRequest,
        context: grpc.aio.ServicerContext[Any, Any],
    ) -> ddl_generator_pb2.DDLResponse:
        logger.info("Received DDL generation request")
        return generate_ddl_handler(request)


async def serve() -> None:
    server = grpc.aio.server()

    ddl_generator_pb2_grpc.add_DDLGeneratorServicer_to_server(  # type: ignore
        DDLGeneratorServicer(), server
    )

    server.add_insecure_port(settings.DDL_GENERATOR_CHANNEL)

    await server.start()

    logger.info(f"running on {settings.DDL_GENERATOR_CHANNEL}")
    logger.info(f"debug: {settings.DDL_GENERATOR_DEBUG}")

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
