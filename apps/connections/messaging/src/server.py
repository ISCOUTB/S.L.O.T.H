"""gRPC Messaging Server.

This module implements a lightweight proxy server that provides gRPC streaming
interfaces for RabbitMQ message consumption. It maintains persistent connections
to RabbitMQ and streams messages to connected clients in real-time.

The server provides the following services:
    - Parameter retrieval for messaging configuration
    - Routing key management for different message types
    - Continuous streaming of schema and validation messages

Architecture:
    Producer -> RabbitMQ -> Messaging Server (this) -> gRPC Client

The streaming approach uses background threads for RabbitMQ consumption and
asyncio queues for communication between sync/async contexts.

Logging Enhancements:
    - Structured logging with contextual tags for filtering and debugging
    - Unique stream IDs for tracking individual client connections
    - Detailed message processing information including counts and IDs
    - Connection lifecycle logging with error handling and cleanup details
    - Performance metrics including queue sizes and processing times
"""

import asyncio
import json
import threading
import uuid
from typing import AsyncGenerator

import grpc
from messaging_utils.messaging.connection_factory import (
    RabbitMQConnectionFactory,
)
from proto_utils.generated.messaging import messaging_pb2, messaging_pb2_grpc
from proto_utils.messaging import MessagingSerde, dtypes

from src.core.config import settings
from src.core.connection_params import messaging_params
from src.handlers.services import MessagingHandler
from src.utils.logger import logger


class MessagingServicer(messaging_pb2_grpc.MessagingServiceServicer):
    """gRPC Servicer for messaging operations.

    This class implements the MessagingService gRPC interface, providing
    methods for parameter retrieval, routing key management, and continuous
    message streaming from RabbitMQ queues.

    The servicer acts as a lightweight proxy between RabbitMQ and gRPC clients,
    maintaining persistent connections and streaming messages in real-time as
    they arrive in the queues.

    Attributes:
        None. The servicer is stateless and uses RabbitMQ as the source of truth.

    Note:
        This implementation uses background threads for RabbitMQ consumption
        to avoid blocking the async gRPC event loop.
    """

    def __init__(self):
        """Initialize the messaging servicer.

        Configures the RabbitMQ connection factory with the messaging parameters
        defined in the application configuration. The servicer itself is stateless
        and does not maintain any internal state.

        Raises:
            ConnectionError: If RabbitMQ connection configuration fails.
        """
        logger.info(
            f"[INIT] Initializing MessagingServicer - "
            f"RabbitMQ Host: {messaging_params.get('host', 'Unknown')}, "
            f"Exchange: {messaging_params.get('exchange', {}).get('exchange', 'Unknown')}"
        )

        try:
            RabbitMQConnectionFactory.configure(messaging_params)
            logger.info(
                "[INIT] RabbitMQ connection factory configured successfully"
            )
        except Exception as e:
            logger.error(
                f"[INIT] Failed to configure RabbitMQ connection factory: {e}"
            )
            raise

    def GetMessagingParams(
        self,
        request: messaging_pb2.GetMessagingParamsRequest,
        context: grpc.aio.ServicerContext,
    ) -> messaging_pb2.GetMessagingParamsResponse:
        """Retrieve messaging connection parameters.

        Returns the RabbitMQ connection configuration including host, port,
        virtual host, credentials, and exchange information.

        Args:
            request: The gRPC request message (currently unused).
            context: The gRPC service context for the request.

        Returns:
            GetMessagingParamsResponse containing:
                - host: RabbitMQ server hostname
                - port: RabbitMQ server port
                - virtual_host: RabbitMQ virtual host
                - username: Authentication username
                - password: Authentication password
                - exchange: Exchange configuration details

        Raises:
            grpc.RpcError: If configuration retrieval fails.
        """
        logger.info(
            "[GET_PARAMS] Request from client - Connection info requested"
        )

        try:
            response = MessagingHandler.get_messaging_params(request)
            logger.info(
                f"[GET_PARAMS] Successfully returned connection parameters - "
                f"Host: {response.host}:{response.port}, VHost: {response.virtual_host}, "
                f"Exchange: {response.exchange.exchange} ({response.exchange.type})"
            )
            return response
        except Exception as e:
            logger.error(
                f"[GET_PARAMS] Failed to get messaging parameters: {e}"
            )
            raise

    def GetRoutingKeySchemas(
        self,
        request: messaging_pb2.GetRoutingKeySchemasRequest,
        context: grpc.aio.ServicerContext,
    ) -> messaging_pb2.RoutingKey:
        """Retrieve routing key for schema message queues.

        Returns the appropriate routing key for schema messages based on
        the request type (results vs updates).

        Args:
            request: Request containing routing key preferences.
                - results: If True, returns routing key for schema results,
                          if False, returns routing key for schema updates.
            context: The gRPC service context for the request.

        Returns:
            RoutingKey message containing the routing key string for
            schema message operations.

        Raises:
            grpc.RpcError: If routing key retrieval fails.
        """
        logger.info(
            f"[ROUTING_SCHEMAS] Request for schema routing key - Results mode: {request.results}"
        )

        try:
            response = MessagingHandler.get_routing_key_schemas(request)
            logger.info(
                f"[ROUTING_SCHEMAS] Returned routing key: '{response.routing_key}'"
            )
            return response
        except Exception as e:
            logger.error(
                f"[ROUTING_SCHEMAS] Failed to get schema routing key: {e}"
            )
            raise

    def GetRoutingKeyValidations(
        self,
        request: messaging_pb2.GetRoutingKeyValidationsRequest,
        context: grpc.aio.ServicerContext,
    ) -> messaging_pb2.RoutingKey:
        """Retrieve routing key for validation message queues.

        Returns the appropriate routing key for validation messages based on
        the request type (results vs requests).

        Args:
            request: Request containing routing key preferences.
                - results: If True, returns routing key for validation results,
                          if False, returns routing key for validation requests.
            context: The gRPC service context for the request.

        Returns:
            RoutingKey message containing the routing key string for
            validation message operations.

        Raises:
            grpc.RpcError: If routing key retrieval fails.
        """
        logger.info(
            f"[ROUTING_VALIDATIONS] Request for validation routing key - Results mode: {request.results}"
        )

        try:
            response = MessagingHandler.get_routing_key_validations(request)
            logger.info(
                f"[ROUTING_VALIDATIONS] Returned routing key: '{response.routing_key}'"
            )
            return response
        except Exception as e:
            logger.error(
                f"[ROUTING_VALIDATIONS] Failed to get validation routing key: {e}"
            )
            raise

    async def StreamSchemaMessages(
        self,
        request: messaging_pb2.SchemaMessageRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncGenerator[messaging_pb2.SchemaMessageResponse, None]:
        """Stream schema messages continuously from RabbitMQ.

        Establishes a persistent connection to RabbitMQ and streams schema
        messages to the client as they arrive. This method maintains the
        connection until the client disconnects or an error occurs.

        The streaming implementation uses a background thread for RabbitMQ
        consumption to avoid blocking the async gRPC event loop. Messages
        are passed between the sync consumer and async generator using
        an asyncio.Queue.

        Args:
            request: The streaming request (currently unused but required
                    by the gRPC interface).
            context: gRPC service context used to detect client disconnection.

        Yields:
            SchemaMessageResponse: Individual schema messages as they arrive
            from RabbitMQ, serialized for gRPC transport.

        Raises:
            grpc.RpcError: If RabbitMQ connection fails or message processing
                          encounters unrecoverable errors.

        Note:
            This method will run indefinitely until the client disconnects
            or the server is shut down. It maintains a persistent RabbitMQ
            connection in a background thread.
        """
        stream_id = str(uuid.uuid4())[:8]

        logger.info(
            f"[SCHEMA_STREAM:{stream_id}] Client connected for continuous schema streaming - "
            f"Client: {context.peer()}"
        )

        # Queue for communication between RabbitMQ thread and async generator
        message_queue = asyncio.Queue()
        stop_event = threading.Event()

        # Get current event loop to pass to the thread
        current_loop = asyncio.get_running_loop()

        def continuous_consume():
            """Background thread for continuous RabbitMQ consumption.

            This function runs in a separate thread to handle the blocking
            RabbitMQ operations. It establishes a connection, sets up message
            callbacks, and processes events until stopped.

            The function communicates with the main async generator through
            the message_queue and stop_event shared variables.

            Note:
                This function runs in a daemon thread and will be terminated
                when the main process exits.
            """
            connection = None
            channel = None
            messages_consumed = 0

            try:
                logger.debug(
                    f"[SCHEMA_STREAM:{stream_id}] Initializing RabbitMQ consumer thread"
                )

                connection = RabbitMQConnectionFactory.get_thread_connection()
                channel = RabbitMQConnectionFactory.get_thread_channel()
                RabbitMQConnectionFactory.setup_infrastructure(channel)

                schema_queue = settings.RABBITMQ_QUEUE_SCHEMAS

                logger.debug(f"[SCHEMA_STREAM:{stream_id}] Consumer setup")

                def message_callback(ch, method, properties, body):
                    """Process individual RabbitMQ messages.

                    This callback is invoked for each message received from
                    RabbitMQ. It deserializes the message, converts it to
                    gRPC format, and queues it for the async generator.

                    Args:
                        ch: RabbitMQ channel object.
                        method: Message method information including delivery tag.
                        properties: Message properties (currently unused).
                        body: Raw message body as bytes.
                    """
                    nonlocal messages_consumed

                    if stop_event.is_set():
                        logger.debug(
                            f"[SCHEMA_STREAM:{stream_id}] Stop event set, ignoring message"
                        )
                        return

                    try:
                        messages_consumed += 1

                        raw_message: dtypes.SchemaMessageResponse = json.loads(
                            body.decode()
                        )
                        grpc_message = (
                            MessagingSerde.serialize_schema_message_response(
                                raw_message
                            )
                        )

                        logger.debug(
                            f"[SCHEMA_STREAM:{stream_id}] Message #{messages_consumed} processed - "
                            f"SchemaID: {grpc_message.id}, "
                            f"RoutingKey: {method.routing_key}, "
                            f"MessageID: {properties.message_id if properties.message_id else 'N/A'}"
                        )

                        # Send message to async generator using thread-safe method
                        asyncio.run_coroutine_threadsafe(
                            message_queue.put(grpc_message), current_loop
                        )

                        # Acknowledge message immediately
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                        logger.info(
                            f"[SCHEMA_STREAM:{stream_id}] Streamed schema message: {grpc_message.id} "
                            f"(#{messages_consumed})"
                        )

                    except Exception as e:
                        logger.error(
                            f"[SCHEMA_STREAM:{stream_id}] Error processing message #{messages_consumed}: "
                            f"Error: {e}, RoutingKey: {method.routing_key}"
                        )
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag, requeue=False
                        )

                channel.basic_consume(
                    queue=schema_queue, on_message_callback=message_callback
                )

                logger.info(
                    f"[SCHEMA_STREAM:{stream_id}] Consumer ready - Starting CONTINUOUS schema consumption..."
                )

                # Event processing loop - runs indefinitely until stopped
                while not stop_event.is_set():
                    try:
                        connection.process_data_events(
                            time_limit=1
                        )  # Process events for 1 second
                    except Exception as e:
                        logger.error(
                            f"[SCHEMA_STREAM:{stream_id}] Event processing error: {e}"
                        )
                        break

                logger.info(
                    f"[SCHEMA_STREAM:{stream_id}] Consumer stopping - Total messages processed: {messages_consumed}"
                )

            except Exception as e:
                logger.error(
                    f"[SCHEMA_STREAM:{stream_id}] Fatal consumer error: {e}"
                )
                # Signal error to main thread using thread-safe method
                try:
                    # Use run_coroutine_threadsafe to schedule from thread
                    asyncio.run_coroutine_threadsafe(
                        message_queue.put(e), current_loop
                    )
                except Exception as queue_error:
                    logger.error(
                        f"[SCHEMA_STREAM:{stream_id}] Error queuing exception: {queue_error}"
                    )

            finally:
                # Cleanup resources
                try:
                    if (
                        channel
                        and hasattr(channel, "is_open")
                        and channel.is_open
                    ):
                        channel.close()
                        logger.debug(
                            f"[SCHEMA_STREAM:{stream_id}] RabbitMQ channel closed"
                        )
                    if (
                        connection
                        and hasattr(connection, "is_open")
                        and connection.is_open
                    ):
                        connection.close()
                        logger.debug(
                            f"[SCHEMA_STREAM:{stream_id}] RabbitMQ connection closed"
                        )
                except Exception as cleanup_error:
                    logger.warning(
                        f"[SCHEMA_STREAM:{stream_id}] Cleanup error: {cleanup_error}"
                    )
                RabbitMQConnectionFactory.close_thread_connections()
                logger.info(
                    f"[SCHEMA_STREAM:{stream_id}] Continuous schema consumption stopped"
                )

        # Start background consumption thread
        consume_thread = threading.Thread(
            target=continuous_consume, daemon=True
        )
        consume_thread.start()

        logger.debug(
            f"[SCHEMA_STREAM:{stream_id}] Background consumer thread started"
        )

        try:
            # Main async generator loop
            while True:
                try:
                    # Wait for message with timeout to allow periodic client checks
                    message = await asyncio.wait_for(
                        message_queue.get(), timeout=5.0
                    )

                    # Check if it's an exception from the consumer thread
                    if isinstance(message, Exception):
                        logger.error(
                            f"[SCHEMA_STREAM:{stream_id}] Consumer thread error: {message}"
                        )
                        break

                    logger.debug(
                        f"[SCHEMA_STREAM:{stream_id}] Yielding message to client - "
                        f"SchemaID: {message.id}, "
                        f"QueueSize: {message_queue.qsize()}"
                    )

                    yield message

                except asyncio.TimeoutError:
                    # Timeout allows us to check if client is still connected
                    logger.debug(
                        f"[SCHEMA_STREAM:{stream_id}] No messages in 5s, checking client connection..."
                    )
                    if context.cancelled():
                        logger.info(
                            f"[SCHEMA_STREAM:{stream_id}] Client cancelled connection"
                        )
                        break
                    continue

        except asyncio.CancelledError:
            logger.info(
                f"[SCHEMA_STREAM:{stream_id}] Stream cancelled by client"
            )
        except Exception as e:
            logger.error(f"[SCHEMA_STREAM:{stream_id}] Streaming error: {e}")
        finally:
            # Signal thread to stop and wait for cleanup
            logger.info(
                f"[SCHEMA_STREAM:{stream_id}] Stopping consumer thread..."
            )
            stop_event.set()

            # Give consumer thread time to cleanup gracefully
            if consume_thread.is_alive():
                consume_thread.join(timeout=5.0)
                if consume_thread.is_alive():
                    logger.warning(
                        f"[SCHEMA_STREAM:{stream_id}] Consumer thread did not stop gracefully"
                    )
                else:
                    logger.debug(
                        f"[SCHEMA_STREAM:{stream_id}] Consumer thread stopped successfully"
                    )

            logger.info(
                f"[SCHEMA_STREAM:{stream_id}] Schema streaming completed"
            )

    async def StreamValidationMessages(
        self,
        request: messaging_pb2.ValidationMessageRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncGenerator[messaging_pb2.ValidationMessageResponse, None]:
        """Stream validation messages continuously from RabbitMQ.

        Establishes a persistent connection to RabbitMQ and streams validation
        messages to the client as they arrive. This method maintains the
        connection until the client disconnects or an error occurs.

        The streaming implementation uses a background thread for RabbitMQ
        consumption to avoid blocking the async gRPC event loop. Messages
        are passed between the sync consumer and async generator using
        an asyncio.Queue.

        Args:
            request: The streaming request (currently unused but required
                    by the gRPC interface).
            context: gRPC service context used to detect client disconnection.

        Yields:
            ValidationMessageResponse: Individual validation messages as they
            arrive from RabbitMQ, serialized for gRPC transport.

        Raises:
            grpc.RpcError: If RabbitMQ connection fails or message processing
                          encounters unrecoverable errors.

        Note:
            This method will run indefinitely until the client disconnects
            or the server is shut down. It maintains a persistent RabbitMQ
            connection in a background thread.
        """
        stream_id = str(uuid.uuid4())[:8]

        logger.info(
            f"[VALIDATION_STREAM:{stream_id}] Client connected for continuous validation streaming - "
            f"Client: {context.peer()}"
        )

        # Queue for communication between RabbitMQ thread and async generator
        message_queue = asyncio.Queue()
        stop_event = threading.Event()

        # Get current event loop to pass to the thread
        current_loop = asyncio.get_running_loop()

        def continuous_consume():
            """Background thread for continuous RabbitMQ consumption.

            This function runs in a separate thread to handle the blocking
            RabbitMQ operations. It establishes a connection, sets up message
            callbacks, and processes events until stopped.

            The function communicates with the main async generator through
            the message_queue and stop_event shared variables.

            Note:
                This function runs in a daemon thread and will be terminated
                when the main process exits.
            """
            connection = None
            channel = None
            messages_consumed = 0

            try:
                logger.debug(
                    f"[VALIDATION_STREAM:{stream_id}] Initializing RabbitMQ consumer thread"
                )

                connection = RabbitMQConnectionFactory.get_thread_connection()
                channel = RabbitMQConnectionFactory.get_thread_channel()
                RabbitMQConnectionFactory.setup_infrastructure(channel)

                validation_queue = settings.RABBITMQ_QUEUE_VALIDATIONS

                logger.debug(f"[VALIDATION_STREAM:{stream_id}] Consumer setup")

                def message_callback(ch, method, properties, body):
                    """Process individual RabbitMQ messages.

                    This callback is invoked for each message received from
                    RabbitMQ. It deserializes the message, converts it to
                    gRPC format, and queues it for the async generator.

                    Args:
                        ch: RabbitMQ channel object.
                        method: Message method information including delivery tag.
                        properties: Message properties (currently unused).
                        body: Raw message body as bytes.
                    """
                    nonlocal messages_consumed

                    if stop_event.is_set():
                        logger.debug(
                            f"[VALIDATION_STREAM:{stream_id}] Stop event set, ignoring message"
                        )
                        return

                    try:
                        messages_consumed += 1

                        raw_message: dtypes.ValidationMessageResponse = (
                            json.loads(body.decode())
                        )
                        grpc_message = MessagingSerde.serialize_validation_message_response(
                            raw_message
                        )

                        logger.debug(
                            f"[VALIDATION_STREAM:{stream_id}] Message #{messages_consumed} processed - "
                            f"ValidationID: {grpc_message.id}, "
                            f"RoutingKey: {method.routing_key}, "
                            f"MessageID: {properties.message_id if properties.message_id else 'N/A'}"
                        )

                        # Send message to async generator using thread-safe method
                        asyncio.run_coroutine_threadsafe(
                            message_queue.put(grpc_message), current_loop
                        )

                        # Acknowledge message immediately
                        ch.basic_ack(delivery_tag=method.delivery_tag)

                        logger.info(
                            f"[VALIDATION_STREAM:{stream_id}] Streamed validation message: {grpc_message.id} "
                            f"(#{messages_consumed})"
                        )

                    except Exception as e:
                        logger.error(
                            f"[VALIDATION_STREAM:{stream_id}] Error processing message #{messages_consumed}: "
                            f"Error: {e}, RoutingKey: {method.routing_key}"
                        )
                        ch.basic_nack(
                            delivery_tag=method.delivery_tag, requeue=False
                        )

                channel.basic_consume(
                    queue=validation_queue, on_message_callback=message_callback
                )

                logger.info(
                    f"[VALIDATION_STREAM:{stream_id}] Consumer ready - Starting CONTINUOUS validation consumption..."
                )

                # Event processing loop - runs indefinitely until stopped
                while not stop_event.is_set():
                    try:
                        connection.process_data_events(
                            time_limit=1
                        )  # Process events for 1 second
                    except Exception as e:
                        logger.error(
                            f"[VALIDATION_STREAM:{stream_id}] Event processing error: {e}"
                        )
                        break

                logger.info(
                    f"[VALIDATION_STREAM:{stream_id}] Consumer stopping - Total messages processed: {messages_consumed}"
                )

            except Exception as e:
                logger.error(
                    f"[VALIDATION_STREAM:{stream_id}] Fatal consumer error: {e}"
                )
                # Signal error to main thread using thread-safe method
                try:
                    # Use run_coroutine_threadsafe to schedule from thread
                    asyncio.run_coroutine_threadsafe(
                        message_queue.put(e), current_loop
                    )
                except Exception as queue_error:
                    logger.error(
                        f"[VALIDATION_STREAM:{stream_id}] Error queuing exception: {queue_error}"
                    )

            finally:
                # Cleanup resources
                try:
                    if (
                        channel
                        and hasattr(channel, "is_open")
                        and channel.is_open
                    ):
                        channel.close()
                        logger.debug(
                            f"[VALIDATION_STREAM:{stream_id}] RabbitMQ channel closed"
                        )
                    if (
                        connection
                        and hasattr(connection, "is_open")
                        and connection.is_open
                    ):
                        connection.close()
                        logger.debug(
                            f"[VALIDATION_STREAM:{stream_id}] RabbitMQ connection closed"
                        )
                except Exception as cleanup_error:
                    logger.warning(
                        f"[VALIDATION_STREAM:{stream_id}] Cleanup error: {cleanup_error}"
                    )
                RabbitMQConnectionFactory.close_thread_connections()
                logger.info(
                    f"[VALIDATION_STREAM:{stream_id}] Continuous validation consumption stopped"
                )

        # Start background consumption thread
        consume_thread = threading.Thread(
            target=continuous_consume, daemon=True
        )
        consume_thread.start()

        logger.debug(
            f"[VALIDATION_STREAM:{stream_id}] Background consumer thread started"
        )

        try:
            # Main async generator loop
            while True:
                try:
                    # Wait for message with timeout to allow periodic client checks
                    message = await asyncio.wait_for(
                        message_queue.get(), timeout=5.0
                    )

                    # Check if it's an exception from the consumer thread
                    if isinstance(message, Exception):
                        logger.error(
                            f"[VALIDATION_STREAM:{stream_id}] Consumer thread error: {message}"
                        )
                        break

                    logger.debug(
                        f"[VALIDATION_STREAM:{stream_id}] Yielding message to client - "
                        f"ValidationID: {message.id}, "
                        f"QueueSize: {message_queue.qsize()}"
                    )

                    yield message

                except asyncio.TimeoutError:
                    # Timeout allows us to check if client is still connected
                    logger.debug(
                        f"[VALIDATION_STREAM:{stream_id}] No messages in 5s, checking client connection..."
                    )
                    if context.cancelled():
                        logger.info(
                            f"[VALIDATION_STREAM:{stream_id}] Client cancelled connection"
                        )
                        break
                    continue

        except asyncio.CancelledError:
            logger.info(
                f"[VALIDATION_STREAM:{stream_id}] Stream cancelled by client"
            )
        except Exception as e:
            logger.error(
                f"[VALIDATION_STREAM:{stream_id}] Streaming error: {e}"
            )
        finally:
            # Signal thread to stop and wait for cleanup
            logger.info(
                f"[VALIDATION_STREAM:{stream_id}] Stopping consumer thread..."
            )
            stop_event.set()

            # Give consumer thread time to cleanup gracefully
            if consume_thread.is_alive():
                consume_thread.join(timeout=5.0)
                if consume_thread.is_alive():
                    logger.warning(
                        f"[VALIDATION_STREAM:{stream_id}] Consumer thread did not stop gracefully"
                    )
                else:
                    logger.debug(
                        f"[VALIDATION_STREAM:{stream_id}] Consumer thread stopped successfully"
                    )

            logger.info(
                f"[VALIDATION_STREAM:{stream_id}] Validation streaming completed"
            )


async def serve() -> None:
    """Start the gRPC messaging server.

    Creates and configures the gRPC server with the messaging servicer,
    then starts listening for incoming client connections on the configured
    address and port.

    The server runs indefinitely until terminated by a signal or an
    unrecoverable error occurs. It uses the async gRPC server implementation
    to handle multiple concurrent client connections efficiently.

    Raises:
        RuntimeError: If server startup fails due to port conflicts or
                     configuration issues.
        ConnectionError: If RabbitMQ connection cannot be established.

    Note:
        This function will block until the server is terminated.
        Use Ctrl+C or send SIGTERM to gracefully shut down the server.
    """
    # Create servicer instance
    servicer = MessagingServicer()

    # Create and configure server
    server = grpc.aio.server()
    messaging_pb2_grpc.add_MessagingServiceServicer_to_server(servicer, server)
    server.add_insecure_port(settings.MESSAGING_CONNECTION_CHANNEL)

    # Start server
    logger.info("[SERVER] Starting gRPC Messaging server...")
    logger.debug(
        f"[SERVER] Configuration - Channel: {settings.MESSAGING_CONNECTION_CHANNEL}"
    )
    logger.debug(
        f"[SERVER] RabbitMQ Host: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}"
    )
    logger.debug(f"[SERVER] Debug Mode: {settings.MESSAGING_CONNECTION_DEBUG}")

    await server.start()
    logger.info(
        f"[SERVER] Messaging server ready and listening on {settings.MESSAGING_CONNECTION_CHANNEL}"
    )

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("[SERVER] Shutdown signal received, stopping server...")
    finally:
        logger.info("[SERVER] Messaging server stopped")


if __name__ == "__main__":
    """Main entry point for the messaging server.
    
    When run as a script, this starts the gRPC server and runs it until
    terminated. The server will handle KeyboardInterrupt gracefully.
    
    Example:
        $ python -m src.server
        $ python src/server.py
    """
    try:
        logger.info("[MAIN] Initializing gRPC Messaging Server...")
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("[MAIN] Application terminated by user")
    except Exception as e:
        logger.error(f"[MAIN] Fatal error: {e}")
        raise
