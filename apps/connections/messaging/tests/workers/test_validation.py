import json
import threading
import time
from unittest.mock import MagicMock, patch
from uuid import uuid4

from messaging_utils.messaging.publishers import Publisher
from proto_utils.messaging import dtypes

from src.core.config import settings
from src.workers.validation import ValidationWorker


def test_validation_worker_yielding_success(
    validation_worker: ValidationWorker, publisher: Publisher
) -> None:
    """Test successful message processing - happy path."""
    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    # Time for initialization
    time.sleep(1.0)

    # Publish message
    publisher.publish_validation_request(
        routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
        file_data=bytes.fromhex(
            "48656c6c6f20576f726c6421"
        ),  # "Hello World!" in hex
        import_name="test_import",
        metadata=dtypes.Metadata(
            filename="test_file.txt",
            content_type="text/plain",
            size=24,
        ),
        task="sample_validation",
    )

    processed_messages = validation_worker.get_message_stream(
        timeout_secs=5.0, yield_none_on_timeout=True
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == "test_import"
    assert processed_message["task"] == "sample_validation"
    assert processed_message["metadata"]["filename"] == "test_file.txt"
    assert processed_message["metadata"]["content_type"] == "text/plain"
    assert processed_message["metadata"]["size"] == 24

    worker_thread.join(timeout=2.0)


def test_validation_worker_no_messages_timeout(
    validation_worker: ValidationWorker,
) -> None:
    """Test behavior when no messages are available - yields None on timeout."""
    # Don't start consuming, so no messages will be processed
    processed_messages = validation_worker.get_message_stream(
        timeout_secs=0.5,  # Short timeout
        yield_none_on_timeout=True,
    )

    # Should get None due to timeout
    result = next(processed_messages)
    assert result is None


def test_validation_worker_multiple_messages(
    validation_worker: ValidationWorker, publisher: Publisher
) -> None:
    """Test processing multiple messages in sequence."""
    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Publish multiple messages
    messages_to_send = 3
    for i in range(messages_to_send):
        publisher.publish_validation_request(
            routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
            file_data=bytes.fromhex("48656c6c6f20576f726c6421"),
            import_name=f"test_import_{i}",
            metadata=dtypes.Metadata(
                filename=f"test_file_{i}.txt",
                content_type="text/plain",
                size=24,
            ),
            task=f"validation_task_{i}",
        )

    processed_messages = validation_worker.get_message_stream(
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
    expected_names = [f"test_import_{i}" for i in range(messages_to_send)]

    for expected in expected_names:
        assert expected in import_names

    worker_thread.join(timeout=2.0)


def test_validation_worker_malformed_message_handling(
    validation_worker: ValidationWorker,
) -> None:
    """Test worker behavior with malformed JSON messages."""
    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
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
    validation_worker.process_validation_request(
        mock_ch, mock_method, mock_properties, invalid_body
    )

    # Verify that nack was called due to JSON error
    mock_ch.basic_nack.assert_called_once_with(
        delivery_tag="test_tag", requeue=False
    )

    worker_thread.join(timeout=2.0)


def test_validation_worker_missing_required_fields(
    validation_worker: ValidationWorker,
) -> None:
    """Test worker behavior with messages missing required fields."""
    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    mock_ch = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = "test_tag"
    mock_properties = MagicMock()

    # Message missing required 'id' field
    incomplete_message = {
        "import_name": "test_import",
        "task": "validation",
        # missing 'id' field
    }
    invalid_body = json.dumps(incomplete_message).encode()

    validation_worker.process_validation_request(
        mock_ch, mock_method, mock_properties, invalid_body
    )

    # Should nack the message due to missing required field
    mock_ch.basic_nack.assert_called_once_with(
        delivery_tag="test_tag", requeue=False
    )

    worker_thread.join(timeout=2.0)


def test_validation_worker_connection_failure():
    """Test worker behavior when RabbitMQ connection fails."""
    # Mock a connection failure scenario
    with patch(
        "messaging_utils.messaging.connection_factory.RabbitMQConnectionFactory.get_thread_connection"
    ) as mock_conn:
        mock_conn.side_effect = Exception("Connection failed")

        worker = ValidationWorker()

        # Should handle connection failure gracefully
        worker.start_consuming()

        # Verify worker stopped consuming
        assert not worker._is_consuming


def test_validation_worker_stop_consuming(
    validation_worker: ValidationWorker,
) -> None:
    """Test that worker stops consuming messages when stop_consuming is called."""
    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Verify worker is running
    assert validation_worker._is_consuming

    # Stop the worker
    validation_worker.stop_consuming()

    # Give time for stop to process
    time.sleep(0.5)

    # Verify worker stopped
    assert not validation_worker._is_consuming
    assert validation_worker._stop_event.is_set()

    worker_thread.join(timeout=2.0)


def test_validation_worker_large_message(
    validation_worker: ValidationWorker, publisher: Publisher
) -> None:
    """Test processing of large messages."""
    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Create a large file data (1MB of 'A' characters in hex)
    large_data = "41" * (1024 * 1024)  # 1MB of 'A' in hex

    publisher.publish_validation_request(
        routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
        file_data=bytes.fromhex(large_data),
        import_name="large_file_test",
        metadata=dtypes.Metadata(
            filename="large_test_file.txt",
            content_type="text/plain",
            size=len(large_data) // 2,  # Hex is 2 chars per byte
        ),
        task="large_validation",
    )

    processed_messages = validation_worker.get_message_stream(
        timeout_secs=10.0,  # Longer timeout for large message
        yield_none_on_timeout=True,
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == "large_file_test"
    assert processed_message["metadata"]["size"] == len(large_data) // 2

    worker_thread.join(timeout=2.0)


def test_validation_worker_empty_file_data(
    validation_worker: ValidationWorker, publisher: Publisher
) -> None:
    """Test processing of messages with empty file data."""
    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    publisher.publish_validation_request(
        routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
        file_data=b"",  # Empty file data
        import_name="empty_file_test",
        metadata=dtypes.Metadata(
            filename="empty_file.txt",
            content_type="text/plain",
            size=0,
        ),
        task="empty_validation",
    )

    processed_messages = validation_worker.get_message_stream(
        timeout_secs=5.0, yield_none_on_timeout=True
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == "empty_file_test"
    assert processed_message["metadata"]["size"] == 0

    worker_thread.join(timeout=2.0)


def test_validation_worker_special_characters_in_import_name(
    validation_worker: ValidationWorker, publisher: Publisher
) -> None:
    """Test processing of messages with special characters in import name."""
    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    special_import_name = f"test-import_with.special+chars@{uuid4()}"

    publisher.publish_validation_request(
        routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
        file_data=bytes.fromhex("48656c6c6f"),
        import_name=special_import_name,
        metadata=dtypes.Metadata(
            filename="test_file_special.txt",
            content_type="text/plain",
            size=5,
        ),
        task="special_char_validation",
    )

    processed_messages = validation_worker.get_message_stream(
        timeout_secs=5.0, yield_none_on_timeout=True
    )

    processed_message = next(processed_messages)
    assert processed_message is not None
    assert processed_message["import_name"] == special_import_name

    worker_thread.join(timeout=2.0)


def test_validation_worker_queue_metrics(
    validation_worker: ValidationWorker, publisher: Publisher
) -> None:
    """Test queue size and message tracking metrics."""
    # Initially empty
    assert validation_worker.get_queue_size() == 0
    assert not validation_worker.has_messages()

    worker_thread = threading.Thread(
        target=validation_worker.start_consuming, daemon=True
    )
    worker_thread.start()

    time.sleep(1.0)

    # Send multiple messages quickly
    num_messages = 5
    for i in range(num_messages):
        publisher.publish_validation_request(
            routing_key=settings.RABBITMQ_ROUTING_KEY_VALIDATIONS,
            file_data=bytes.fromhex("48656c6c6f"),
            import_name=f"metrics_test_{i}",
            metadata=dtypes.Metadata(
                filename=f"metrics_file_{i}.txt",
                content_type="text/plain",
                size=5,
            ),
            task=f"metrics_validation_{i}",
        )

    # Give time for messages to be processed into queue
    time.sleep(2.0)

    # Check that we have messages
    assert validation_worker.has_messages()
    initial_queue_size = validation_worker.get_queue_size()

    # Process one message
    processed_messages = validation_worker.get_message_stream(
        timeout_secs=2.0, yield_none_on_timeout=True
    )

    message = next(processed_messages)
    assert message is not None

    # Queue size should have decreased
    assert validation_worker.get_queue_size() < initial_queue_size

    worker_thread.join(timeout=2.0)
