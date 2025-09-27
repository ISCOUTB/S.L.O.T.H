import json
import threading
import time
from unittest.mock import MagicMock, patch
from uuid import uuid4

from messaging_utils.messaging.publishers import Publisher

from src.core.config import settings
from src.workers.schemas import SchemasWorker


def test_schemas_worker_yielding_success(
    schemas_worker: SchemasWorker, publisher: Publisher
) -> None:
    """Test successful message processing - happy path."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    # Time for initialization
    time.sleep(1.0)

    # Publish schema message
    test_schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name"],
    }

    publisher.publish_schema_update(
        routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
        schema=test_schema,
        import_name="test_schema",
        raw=False,
        task="upload_schema",
    )

    processed_messages = schemas_worker.get_message_stream(
        timeout_secs=5.0, yield_none_on_timeout=True
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == "test_schema"
    assert processed_message["tasks"] == "upload_schema"
    assert processed_message["raw"] is False
    assert processed_message["schema"] == test_schema

    worker_thread.join(timeout=2.0)


def test_schemas_worker_no_messages_timeout(
    schemas_worker: SchemasWorker,
) -> None:
    """Test behavior when no messages are available - yields None on timeout."""
    # Don't start consuming, so no messages will be processed
    processed_messages = schemas_worker.get_message_stream(
        timeout_secs=0.5,  # Short timeout
        yield_none_on_timeout=True,
    )

    # Should get None due to timeout
    result = next(processed_messages)
    assert result is None


def test_schemas_worker_multiple_messages(
    schemas_worker: SchemasWorker, publisher: Publisher
) -> None:
    """Test processing multiple messages in sequence."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Publish multiple messages
    messages_to_send = 3
    for i in range(messages_to_send):
        test_schema = {
            "type": "object",
            "properties": {"field": {"type": "string"}},
        }
        publisher.publish_schema_update(
            routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
            schema=test_schema,
            import_name=f"test_schema_{i}",
            raw=False,
            task="upload_schema",
        )

    processed_messages = schemas_worker.get_message_stream(
        timeout_secs=2.0, yield_none_on_timeout=True
    )

    received_messages = []
    for _ in range(messages_to_send):
        message = next(processed_messages)
        if message is not None:
            received_messages.append(message)

    assert len(received_messages) == messages_to_send

    # Verify all messages were processed correctly
    import_names = [msg["import_name"] for msg in received_messages]
    expected_names = [f"test_schema_{i}" for i in range(messages_to_send)]

    for expected in expected_names:
        assert expected in import_names

    worker_thread.join(timeout=2.0)


def test_schemas_worker_malformed_message_handling(
    schemas_worker: SchemasWorker,
) -> None:
    """Test worker behavior with malformed JSON messages."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Simulate a malformed message by directly putting invalid JSON in the queue
    # Mock the channel and method objects
    mock_ch = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = "test_tag"
    mock_properties = MagicMock()

    # Invalid JSON body
    invalid_body = b'{"invalid": json, missing quotes}'

    # Call the method directly with invalid data
    schemas_worker.process_schema_update(
        mock_ch, mock_method, mock_properties, invalid_body
    )

    # Verify that nack was called due to JSON error
    mock_ch.basic_nack.assert_called_once_with(
        delivery_tag="test_tag", requeue=False
    )

    worker_thread.join(timeout=2.0)


def test_schemas_worker_missing_required_fields(
    schemas_worker: SchemasWorker,
) -> None:
    """Test worker behavior with messages missing required fields."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    mock_ch = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = "test_tag"
    mock_properties = MagicMock()

    # Message missing required 'id' field
    incomplete_message = {
        "import_name": "test_schema",
        "tasks": "upload_schema",
        "schema": {"type": "object"},
    }
    invalid_body = json.dumps(incomplete_message).encode()

    schemas_worker.process_schema_update(
        mock_ch, mock_method, mock_properties, invalid_body
    )

    # Should nack the message due to missing required field
    mock_ch.basic_nack.assert_called_once_with(
        delivery_tag="test_tag", requeue=False
    )

    worker_thread.join(timeout=2.0)


def test_schemas_worker_connection_failure():
    """Test worker behavior when RabbitMQ connection fails."""
    # Mock a connection failure scenario
    with patch(
        "messaging_utils.messaging.connection_factory.RabbitMQConnectionFactory.get_thread_connection"
    ) as mock_conn:
        mock_conn.side_effect = Exception("Connection failed")

        worker = SchemasWorker()

        # start_consuming should handle the exception gracefully
        worker.start_consuming()

        # Worker should not be consuming after connection failure
        assert not worker._is_consuming


def test_schemas_worker_stop_consuming(
    schemas_worker: SchemasWorker,
) -> None:
    """Test that worker stops consuming messages when stop_consuming is called."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Verify worker is running
    assert schemas_worker._is_consuming

    # Stop the worker
    schemas_worker.stop_consuming()

    # Give time for stop to process
    time.sleep(0.5)

    # Verify worker stopped
    assert not schemas_worker._is_consuming
    assert schemas_worker._stop_event.is_set()

    worker_thread.join(timeout=2.0)


def test_schemas_worker_large_schema(
    schemas_worker: SchemasWorker, publisher: Publisher
) -> None:
    """Test processing of large schema messages."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Create a large schema with many properties
    large_schema = {"type": "object", "properties": {}}

    # Add 1000 properties to make it large
    for i in range(1000):
        large_schema["properties"][f"field_{i}"] = {
            "type": "string",
            "description": f"Field number {i} with a long description to make the schema larger",
        }

    publisher.publish_schema_update(
        routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
        schema=large_schema,
        import_name="large_schema_test",
        raw=False,
        task="upload_schema",
    )

    processed_messages = schemas_worker.get_message_stream(
        timeout_secs=10.0,  # Longer timeout for large message
        yield_none_on_timeout=True,
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == "large_schema_test"
    assert processed_message["tasks"] == "upload_schema"
    assert len(processed_message["schema"]["properties"]) == 1000

    worker_thread.join(timeout=2.0)


def test_schemas_worker_empty_schema(
    schemas_worker: SchemasWorker, publisher: Publisher
) -> None:
    """Test processing of empty schema."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Empty schema
    empty_schema = {}

    publisher.publish_schema_update(
        routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
        schema=empty_schema,
        import_name="empty_schema_test",
        raw=True,
        task="upload_schema",
    )

    processed_messages = schemas_worker.get_message_stream(
        timeout_secs=2.0, yield_none_on_timeout=True
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == "empty_schema_test"
    assert processed_message["raw"] is True
    assert processed_message["schema"] == empty_schema

    worker_thread.join(timeout=2.0)


def test_schemas_worker_special_characters_in_import_name(
    schemas_worker: SchemasWorker, publisher: Publisher
) -> None:
    """Test processing schema with special characters in import name."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    test_schema = {"type": "object", "properties": {"test": {"type": "string"}}}

    # Import name with special characters
    special_import_name = f"test-import_with.special@chars-{uuid4().hex[:12]}"

    publisher.publish_schema_update(
        routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
        schema=test_schema,
        import_name=special_import_name,
        raw=False,
        task="upload_schema",
    )

    processed_messages = schemas_worker.get_message_stream(
        timeout_secs=2.0, yield_none_on_timeout=True
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == special_import_name
    assert processed_message["schema"] == test_schema

    worker_thread.join(timeout=2.0)


def test_schemas_worker_queue_metrics(
    schemas_worker: SchemasWorker, publisher: Publisher
) -> None:
    """Test queue metrics functionality."""
    # Initially, queue should be empty
    assert schemas_worker.get_queue_size() == 0
    assert not schemas_worker.has_messages()

    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Publish multiple messages to test metrics
    test_schema = {"type": "object", "properties": {"name": {"type": "string"}}}

    messages_count = 4
    for i in range(messages_count):
        publisher.publish_schema_update(
            routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
            schema=test_schema,
            import_name=f"metrics_test_{i}",
            raw=False,
            task="upload_schema",
        )

    # Give time for messages to be received
    time.sleep(2.0)

    # Check that messages are queued
    assert schemas_worker.has_messages()
    queue_size = schemas_worker.get_queue_size()
    assert queue_size > 0
    assert queue_size <= messages_count

    # Process one message
    processed_messages = schemas_worker.get_message_stream(
        timeout_secs=1.0, yield_none_on_timeout=True
    )

    first_message = next(processed_messages)
    assert first_message is not None

    # Queue size should decrease
    new_queue_size = schemas_worker.get_queue_size()
    assert new_queue_size == queue_size - 1

    worker_thread.join(timeout=2.0)


def test_schemas_worker_remove_schema_task(
    schemas_worker: SchemasWorker, publisher: Publisher
) -> None:
    """Test processing of remove_schema task."""
    worker_thread = threading.Thread(
        target=schemas_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Empty schema for removal
    empty_schema = {}

    publisher.publish_schema_update(
        routing_key=settings.RABBITMQ_ROUTING_KEY_SCHEMAS,
        schema=empty_schema,
        import_name="schema_to_remove",
        raw=True,
        task="remove_schema",
    )

    processed_messages = schemas_worker.get_message_stream(
        timeout_secs=2.0, yield_none_on_timeout=True
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == "schema_to_remove"
    assert processed_message["tasks"] == "remove_schema"
    assert processed_message["raw"] is True

    worker_thread.join(timeout=2.0)
