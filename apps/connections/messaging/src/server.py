import asyncio
from typing import AsyncGenerator

import grpc
from proto_utils.generated.messaging import messaging_pb2, messaging_pb2_grpc

from src.core.config import settings
from src.handlers.services import MessagingHandler
from src.handlers.workers import WorkersHandler
from src.utils.logger import logger
from src.workers.main import WorkerManager


class MessagingServicer(messaging_pb2_grpc.MessagingServiceServicer):
    """gRPC Servicer for messaging operations.

    Handles messaging service requests including parameter retrieval,
    routing key management, and streaming message processing.
    """

    def __init__(self):
        """Initialize the servicer with a worker manager."""
        self.worker_manager = WorkerManager()
        self.workers_handler = WorkersHandler(self.worker_manager)
        self._workers_ready = asyncio.Event()

    async def initialize_workers(self):
        """Initialize workers when the server starts."""
        logger.info("Initializing message workers...")
        try:
            # Start workers in background task
            asyncio.create_task(self.worker_manager.start_workers())
            # Give workers time to initialize and connect to RabbitMQ
            await asyncio.sleep(2.0)
            self._workers_ready.set()
            logger.info("Message workers initialized and ready")
        except Exception as e:
            logger.error(f"Failed to initialize workers: {e}")
            raise

    def GetMessagingParams(
        self,
        request: messaging_pb2.GetMessagingParamsRequest,
        context: grpc.aio.ServicerContext,
    ) -> messaging_pb2.GetMessagingParamsResponse:
        """Get messaging connection parameters."""
        logger.info(f"Received GetMessagingParams request: {request}")
        return MessagingHandler.get_messaging_params(request)

    def GetRoutingKeySchemas(
        self,
        request: messaging_pb2.GetRoutingKeySchemasRequest,
        context: grpc.aio.ServicerContext,
    ) -> messaging_pb2.RoutingKey:
        """Get routing key for schemas queue."""
        logger.info(f"Received GetRoutingKeySchemas request: {request}")
        return MessagingHandler.get_routing_key_schemas(request)

    def GetRoutingKeyValidations(
        self,
        request: messaging_pb2.GetRoutingKeyValidationsRequest,
        context: grpc.aio.ServicerContext,
    ) -> messaging_pb2.RoutingKey:
        """Get routing key for validations queue."""
        logger.info(f"Received GetRoutingKeyValidations request: {request}")
        return MessagingHandler.get_routing_key_validations(request)

    async def StreamSchemaMessages(
        self,
        request: messaging_pb2.SchemaMessageRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncGenerator[messaging_pb2.SchemaMessageResponse, None]:
        """Stream schema messages from the schemas worker.

        Yields schema messages as they are processed by the schemas worker.
        This is a streaming RPC that continues until the connection is closed
        or an error occurs.
        """
        logger.info(f"Starting StreamSchemaMessages for request: {request}")

        try:
            # Ensure workers are ready before streaming
            await self._workers_ready.wait()

            # Stream messages from the schemas worker
            for message in self.workers_handler.stream_schemas_messages(
                request
            ):
                if message is not None:
                    logger.debug(f"Streaming schema message: {message.id}")
                    yield message

                # Check if client disconnected
                if context.cancelled():
                    logger.info("Client cancelled StreamSchemaMessages")
                    break

        except Exception as e:
            logger.error(f"Error in StreamSchemaMessages: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Streaming error: {e}"
            )

    async def StreamValidationMessages(
        self,
        request: messaging_pb2.ValidationMessageRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncGenerator[messaging_pb2.ValidationMessageResponse, None]:
        """Stream validation messages from the validation worker.

        Yields validation messages as they are processed by the validation worker.
        This is a streaming RPC that continues until the connection is closed
        or an error occurs.
        """
        logger.info(f"Starting StreamValidationMessages for request: {request}")

        try:
            # Ensure workers are ready before streaming
            await self._workers_ready.wait()
            logger.info("Workers are ready, starting schema streaming")

            # Stream messages from the validation worker
            for message in self.workers_handler.stream_validation_messages(
                request
            ):
                if message is not None:
                    logger.debug(f"Streaming validation message: {message.id}")
                    yield message

                # Check if client disconnected
                if context.cancelled():
                    logger.info("Client cancelled StreamValidationMessages")
                    break

        except Exception as e:
            logger.error(f"Error in StreamValidationMessages: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Streaming error: {e}"
            )


async def serve() -> None:
    """Start the gRPC messaging server.

    Creates and starts the gRPC server with the messaging servicer,
    listening on the configured port for incoming requests.
    """
    # Create servicer instance
    servicer = MessagingServicer()

    # Initialize workers before starting the server
    await servicer.initialize_workers()

    # Create and configure server
    server = grpc.aio.server()
    messaging_pb2_grpc.add_MessagingServiceServicer_to_server(servicer, server)
    server.add_insecure_port(settings.MESSAGING_CONNECTION_CHANNEL)

    # Start server
    await server.start()
    logger.info(
        f"Messaging server started on {settings.MESSAGING_CONNECTION_CHANNEL}"
        f" -- DEBUG: {settings.MESSAGING_CONNECTION_DEBUG}"
    )
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
