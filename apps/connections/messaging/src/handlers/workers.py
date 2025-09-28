from typing import Generator

from proto_utils.generated.messaging import messaging_pb2
from proto_utils.messaging.messaging_serde import MessagingSerde

from src.utils.logger import logger
from src.workers.main import WorkerManager


class WorkersHandler:
    def __init__(self, worker_manager: WorkerManager) -> None:
        self.worker_manager = worker_manager

    def stream_schemas_messages(
        self, request: messaging_pb2.SchemaMessageRequest
    ) -> Generator[messaging_pb2.SchemaMessageResponse, None, None]:
        """Stream schema messages from the schemas worker."""
        try:
            logger.debug("Starting schema messages streaming")
            for (
                message
            ) in self.worker_manager.schemas_worker.get_message_stream(
                timeout_secs=1.0,
                yield_none_on_timeout=False,  # Don't yield None for streaming
            ):
                # Serialize the message response for gRPC
                serialized_message = (
                    MessagingSerde.serialize_schema_message_response(message)
                )
                logger.debug(
                    f"Successfully serialized schema message: {serialized_message.id}"
                )
                yield serialized_message
        except Exception as e:
            logger.error(f"Error streaming schema messages: {e}")
            logger.error(f"Message content: {message}")
            raise

    def stream_validation_messages(
        self, request: messaging_pb2.ValidationMessageRequest
    ) -> Generator[messaging_pb2.ValidationMessageResponse, None, None]:
        """Stream validation messages from the validation worker."""
        try:
            logger.debug("Starting validation messages streaming")
            for (
                message
            ) in self.worker_manager.validation_worker.get_message_stream(
                timeout_secs=1.0,
                yield_none_on_timeout=False,  # Don't yield None for streaming
            ):
                # Serialize the message response for gRPC
                serialized_message = (
                    MessagingSerde.serialize_validation_message_response(
                        message
                    )
                )
                logger.debug(
                    f"Successfully serialized validation message: {serialized_message.id}"
                )
                yield serialized_message
        except Exception as e:
            logger.error(f"Error streaming validation messages: {e}")
            logger.error(f"Message content: {message}")
            raise
