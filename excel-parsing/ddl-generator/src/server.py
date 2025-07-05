import asyncio
import logging

import grpc
from clients import ddl_generator_pb2, ddl_generator_pb2_grpc

from core.config import settings
from handlers.ddl_generator import generate_ddl_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DDLGeneratorServer")


class DDLGeneratorServicer(ddl_generator_pb2_grpc.DDLGeneratorServicer):
    def GenerateDDL(
        self, request: ddl_generator_pb2.DDLRequest, _: grpc.aio.ServicerContext
    ) -> ddl_generator_pb2.DDLResponse:
        logger.info("Received DDL generation request")
        return generate_ddl_handler(request)


async def serve() -> None:
    server = grpc.aio.server()
    ddl_generator_pb2_grpc.add_DDLGeneratorServicer_to_server(
        DDLGeneratorServicer(), server
    )
    server.add_insecure_port(settings.DDL_GENERATOR_CHANNEL)
    await server.start()
    logger.info(
        (
            f"DDL Generator server started on {settings.DDL_GENERATOR_CHANNEL}"
            f" -- DEBUG: {settings.DDL_GENERATOR_DEBUG}"
        )
    )
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
