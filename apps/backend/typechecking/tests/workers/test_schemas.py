"""Unit tests for SchemaWorker.

This module contains comprehensive tests for the SchemaWorker class,
which processes schema update messages from RabbitMQ.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from jsonschema import SchemaError

from src.workers.schemas import SchemaWorker

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_db_client():
    """Create a mock DatabaseClient."""
    mock_client = MagicMock()
    mock_client.update_task_id = MagicMock()
    mock_client.get_task_id = MagicMock(
        return_value={"value": {"data": {"upload_date": "2024-01-01T00:00:00"}}}
    )
    mock_client.close = MagicMock()
    return mock_client


@pytest.fixture
def schema_worker(mock_db_client):
    """Create a SchemaWorker instance with mocked dependencies."""
    with patch(
        "src.workers.schemas.get_database_client",
        return_value=mock_db_client,
    ):
        worker = SchemaWorker(
            max_retries=5,
            retry_delay=2.0,
            backoff=2.0,
            threshold=60.0,
        )
    return worker


@pytest.fixture
def sample_upload_schema_message():
    """Create a sample upload schema message."""
    return {
        "id": "task_123",
        "task": "upload_schema",
        "date": "2024-01-01T00:00:00",
        "import_name": "test_schema",
        "raw": False,
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        },
    }


@pytest.fixture
def sample_remove_schema_message():
    """Create a sample remove schema message."""
    return {
        "id": "task_456",
        "task": "remove_schema",
        "date": "2024-01-01T00:00:00",
        "import_name": "test_schema",
    }


# ============================================================================
# TEST CLASSES
# ============================================================================


class TestSchemaWorkerInitialization:
    """Test SchemaWorker initialization."""

    def test_worker_initialization(self, schema_worker):
        """Test that worker is initialized correctly."""
        assert schema_worker.TASK == "schemas"
        assert schema_worker.max_retries == 5
        assert schema_worker.retry_delay == 2.0
        assert schema_worker.backoff == 2.0
        assert schema_worker.threshold == 60.0
        assert schema_worker.connection is None
        assert schema_worker.channel is None
        assert schema_worker.db_client is not None

    def test_worker_initialization_custom_params(self, mock_db_client):
        """Test worker initialization with custom parameters."""
        with patch(
            "src.workers.schemas.get_database_client",
            return_value=mock_db_client,
        ):
            worker = SchemaWorker(
                max_retries=10,
                retry_delay=5.0,
                backoff=1.5,
                threshold=120.0,
            )

        assert worker.max_retries == 10
        assert worker.retry_delay == 5.0
        assert worker.backoff == 1.5
        assert worker.threshold == 120.0


class TestProcessSchemaUpdate:
    """Test process_schema_update method."""

    def test_process_upload_schema_success(
        self, schema_worker, sample_upload_schema_message
    ):
        """Test successful schema upload processing."""
        # Mock channel and method
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_123"
        mock_properties = MagicMock()

        # Mock _update_schema and _publish_result
        mock_result = {
            "task_id": "task_123",
            "status": "completed",
            "import_name": "test_schema",
            "schema": {},
            "result": True,
        }
        schema_worker._update_schema = MagicMock(return_value=mock_result)
        schema_worker._publish_result = MagicMock()

        # Execute
        body = json.dumps(sample_upload_schema_message).encode()
        schema_worker.process_schema_update(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify
        schema_worker._update_schema.assert_called_once()
        schema_worker._publish_result.assert_called_once_with(
            "task_123", mock_result, db_client=schema_worker.db_client
        )
        mock_channel.basic_ack.assert_called_once_with(
            delivery_tag="delivery_123"
        )

    def test_process_remove_schema_success(
        self, schema_worker, sample_remove_schema_message
    ):
        """Test successful schema removal processing."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_456"
        mock_properties = MagicMock()

        # Mock _remove_schema and _publish_result
        mock_result = {
            "task_id": "task_456",
            "status": "completed",
            "import_name": "test_schema",
            "schema": None,
            "result": True,
        }
        schema_worker._remove_schema = MagicMock(return_value=mock_result)
        schema_worker._publish_result = MagicMock()

        # Execute
        body = json.dumps(sample_remove_schema_message).encode()
        schema_worker.process_schema_update(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify
        schema_worker._remove_schema.assert_called_once()
        schema_worker._publish_result.assert_called_once()
        mock_channel.basic_ack.assert_called_once()

    def test_process_schema_update_invalid_json(self, schema_worker):
        """Test handling of invalid JSON in message."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_error"
        mock_properties = MagicMock()

        # Invalid JSON body
        body = b"invalid json {{"

        # Execute
        schema_worker.process_schema_update(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify nack was called
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag="delivery_error", requeue=False
        )

    def test_process_schema_update_exception_during_processing(
        self, schema_worker, sample_upload_schema_message
    ):
        """Test handling of exceptions during schema processing."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_exc"
        mock_properties = MagicMock()

        # Mock _update_schema raising an exception
        schema_worker._update_schema = MagicMock(
            side_effect=Exception("Processing error")
        )

        # Execute
        body = json.dumps(sample_upload_schema_message).encode()
        schema_worker.process_schema_update(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify nack was called
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag="delivery_exc", requeue=False
        )


class TestUpdateSchema:
    """Test _update_schema method."""

    @patch("src.workers.schemas.create_schema")
    @patch("src.workers.schemas.save_schema")
    def test_update_schema_success(
        self,
        mock_save_schema,
        mock_create_schema,
        schema_worker,
        sample_upload_schema_message,
    ):
        """Test successful schema update."""
        # Mock schema creation and save
        mock_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        mock_create_schema.return_value = mock_schema
        mock_save_schema.return_value = True

        # Execute
        result = schema_worker._update_schema(
            sample_upload_schema_message, db_client=schema_worker.db_client
        )

        # Verify
        mock_create_schema.assert_called_once_with(
            False, sample_upload_schema_message["schema"]
        )
        mock_save_schema.assert_called_once()

        assert result["task_id"] == "task_123"
        assert result["status"] == "completed"
        assert result["import_name"] == "test_schema"
        assert result["schema"] == mock_schema
        assert result["result"] is True

    @patch("src.workers.schemas.create_schema")
    @patch("src.workers.schemas.save_schema")
    def test_update_schema_with_raw_flag(
        self,
        mock_save_schema,
        mock_create_schema,
        schema_worker,
    ):
        """Test schema update with raw flag set to True."""
        message = {
            "id": "task_raw",
            "task": "upload_schema",
            "date": "2024-01-01T00:00:00",
            "import_name": "raw_schema",
            "raw": True,
            "schema": {"type": "string"},
        }

        mock_schema = {"type": "string"}
        mock_create_schema.return_value = mock_schema
        mock_save_schema.return_value = True

        # Execute
        result = schema_worker._update_schema(
            message, db_client=schema_worker.db_client
        )

        # Verify create_schema was called with raw=True
        mock_create_schema.assert_called_once_with(True, message["schema"])
        assert result["status"] == "completed"

    @patch("src.workers.schemas.create_schema")
    def test_update_schema_creation_failure(
        self,
        mock_create_schema,
        schema_worker,
        sample_upload_schema_message,
    ):
        """Test handling of schema creation failure."""
        # Mock schema creation raising SchemaError
        mock_create_schema.side_effect = SchemaError("Invalid schema format")

        # Execute
        result = schema_worker._update_schema(
            sample_upload_schema_message, db_client=schema_worker.db_client
        )

        # Verify
        assert result["status"] == "failed-creating-schema"
        assert result["result"] is False
        assert result["schema"] is None

    @patch("src.workers.schemas.create_schema")
    @patch("src.workers.schemas.save_schema")
    def test_update_schema_save_failure(
        self,
        mock_save_schema,
        mock_create_schema,
        schema_worker,
        sample_upload_schema_message,
    ):
        """Test handling of schema save failure."""
        mock_schema = {"type": "object"}
        mock_create_schema.return_value = mock_schema

        # Mock save_schema raising an exception
        mock_save_schema.side_effect = Exception("Database error")

        # Execute
        result = schema_worker._update_schema(
            sample_upload_schema_message, db_client=schema_worker.db_client
        )

        # Verify
        assert result["status"] == "failed-saving-schema"
        assert "Exception" in str(result["result"])

    @patch("src.workers.schemas.create_schema")
    @patch("src.workers.schemas.save_schema")
    def test_update_schema_updates_task_status(
        self,
        mock_save_schema,
        mock_create_schema,
        schema_worker,
        sample_upload_schema_message,
    ):
        """Test that task status is updated during schema update."""
        mock_create_schema.return_value = {"type": "object"}
        mock_save_schema.return_value = True

        # Execute
        schema_worker._update_schema(
            sample_upload_schema_message, db_client=schema_worker.db_client
        )

        # Verify multiple status updates
        assert schema_worker.db_client.update_task_id.call_count >= 3

        # Check specific status values
        call_args_list = [
            call[0][0]
            for call in schema_worker.db_client.update_task_id.call_args_list
        ]
        statuses = [
            args["value"]
            for args in call_args_list
            if args["field"] == "status"
        ]

        assert "creating-schema" in statuses
        assert "schema-created" in statuses or "completed" in statuses


class TestRemoveSchema:
    """Test _remove_schema method."""

    @patch("src.workers.schemas.remove_schema")
    def test_remove_schema_success(
        self,
        mock_remove_schema,
        schema_worker,
        sample_remove_schema_message,
    ):
        """Test successful schema removal."""
        mock_remove_schema.return_value = True

        # Execute
        result = schema_worker._remove_schema(
            sample_remove_schema_message, db_client=schema_worker.db_client
        )

        # Verify
        mock_remove_schema.assert_called_once_with(
            "test_schema", database_client=schema_worker.db_client
        )

        assert result["task_id"] == "task_456"
        assert result["status"] == "completed"
        assert result["import_name"] == "test_schema"
        assert result["schema"] is None
        assert result["result"] is True

    @patch("src.workers.schemas.remove_schema")
    def test_remove_schema_failure(
        self,
        mock_remove_schema,
        schema_worker,
        sample_remove_schema_message,
    ):
        """Test handling of schema removal failure."""
        # Mock remove_schema raising an exception
        mock_remove_schema.side_effect = Exception("Schema not found")

        # Execute
        result = schema_worker._remove_schema(
            sample_remove_schema_message, db_client=schema_worker.db_client
        )

        # Verify
        assert result["status"] == "failed-removing-schema"
        assert "Exception" in str(result["result"])

    @patch("src.workers.schemas.remove_schema")
    def test_remove_schema_updates_task_status(
        self,
        mock_remove_schema,
        schema_worker,
        sample_remove_schema_message,
    ):
        """Test that task status is updated during schema removal."""
        mock_remove_schema.return_value = True

        # Execute
        schema_worker._remove_schema(
            sample_remove_schema_message, db_client=schema_worker.db_client
        )

        # Verify status updates
        assert schema_worker.db_client.update_task_id.call_count >= 2

        call_args_list = [
            call[0][0]
            for call in schema_worker.db_client.update_task_id.call_args_list
        ]
        statuses = [
            args["value"]
            for args in call_args_list
            if args["field"] == "status"
        ]

        assert "removing-schema" in statuses
        assert "completed" in statuses


class TestPublishResult:
    """Test _publish_result method."""

    def test_publish_result_success(self, schema_worker):
        """Test successful result publishing."""
        mock_channel = MagicMock()
        schema_worker.channel = mock_channel

        result = {
            "task_id": "task_pub",
            "status": "completed",
            "import_name": "test_schema",
            "schema": {},
            "result": True,
        }

        # Execute
        schema_worker._publish_result(
            "task_pub", result, db_client=schema_worker.db_client
        )

        # Verify
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args

        # Check the published message
        published_body = call_args[1]["body"]
        published_data = json.loads(published_body)
        assert published_data["task_id"] == "task_pub"
        assert published_data["status"] == "completed"

    def test_publish_result_with_failed_status(self, schema_worker):
        """Test publishing when schema operation failed."""
        mock_channel = MagicMock()
        schema_worker.channel = mock_channel

        result = {
            "task_id": "task_failed",
            "status": "failed-creating-schema",
            "import_name": "test_schema",
            "schema": None,
            "result": False,
        }

        # Execute
        schema_worker._publish_result(
            "task_failed", result, db_client=schema_worker.db_client
        )

        # Verify that publish was NOT called
        mock_channel.basic_publish.assert_not_called()

        # Verify status was updated to failed-publishing-result
        update_calls = [
            call[0][0]
            for call in schema_worker.db_client.update_task_id.call_args_list
        ]
        statuses = [c["value"] for c in update_calls if c["field"] == "status"]
        assert "failed-publishing-result" in statuses

    def test_publish_result_uses_correct_routing(self, schema_worker):
        """Test that correct exchange and routing key are used."""
        mock_channel = MagicMock()
        schema_worker.channel = mock_channel

        result = {
            "task_id": "task_routing",
            "status": "completed",
            "import_name": "test_schema",
            "schema": {},
            "result": True,
        }

        # Execute
        schema_worker._publish_result(
            "task_routing", result, db_client=schema_worker.db_client
        )

        # Verify routing
        call_args = mock_channel.basic_publish.call_args
        assert "exchange" in call_args[1]
        assert "routing_key" in call_args[1]


class TestStopConsuming:
    """Test stop_consuming method."""

    def test_stop_consuming_closes_connections(self, schema_worker):
        """Test that stop_consuming closes all connections properly."""
        mock_channel = MagicMock()
        mock_channel.is_open = True
        schema_worker.channel = mock_channel

        # Execute
        with patch(
            "src.workers.schemas.RabbitMQConnectionFactory.close_thread_connections"
        ) as mock_close:
            schema_worker.stop_consuming()

            # Verify
            mock_channel.stop_consuming.assert_called_once()
            mock_close.assert_called_once()
            schema_worker.db_client.close.assert_called_once()

    def test_stop_consuming_handles_closed_channel(self, schema_worker):
        """Test stop_consuming when channel is already closed."""
        mock_channel = MagicMock()
        mock_channel.is_open = False
        schema_worker.channel = mock_channel

        # Execute (should not raise exception)
        schema_worker.stop_consuming()

        # Verify db_client was still closed
        schema_worker.db_client.close.assert_called_once()

    def test_stop_consuming_handles_exceptions(self, schema_worker):
        """Test that stop_consuming handles exceptions gracefully."""
        mock_channel = MagicMock()
        mock_channel.is_open = True
        mock_channel.stop_consuming.side_effect = Exception("Channel error")
        schema_worker.channel = mock_channel

        # Execute (should not raise exception)
        schema_worker.stop_consuming()

        # Should complete without raising


class TestSchemaWorkerIntegration:
    """Integration tests for complete schema workflows."""

    @patch("src.workers.schemas.create_schema")
    @patch("src.workers.schemas.save_schema")
    def test_complete_upload_workflow(
        self,
        mock_save_schema,
        mock_create_schema,
        schema_worker,
        sample_upload_schema_message,
    ):
        """Test a complete schema upload workflow."""
        # Setup mocks
        mock_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        mock_create_schema.return_value = mock_schema
        mock_save_schema.return_value = True

        # Mock channel
        mock_channel = MagicMock()
        schema_worker.channel = mock_channel
        schema_worker._publish_result = MagicMock()

        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_complete"
        mock_properties = MagicMock()

        # Execute
        body = json.dumps(sample_upload_schema_message).encode()
        schema_worker.process_schema_update(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify complete workflow
        mock_create_schema.assert_called_once()
        mock_save_schema.assert_called_once()
        schema_worker._publish_result.assert_called_once()
        mock_channel.basic_ack.assert_called_once()

    @patch("src.workers.schemas.remove_schema")
    def test_complete_removal_workflow(
        self,
        mock_remove_schema,
        schema_worker,
        sample_remove_schema_message,
    ):
        """Test a complete schema removal workflow."""
        mock_remove_schema.return_value = True

        # Mock channel
        mock_channel = MagicMock()
        schema_worker.channel = mock_channel
        schema_worker._publish_result = MagicMock()

        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_removal"
        mock_properties = MagicMock()

        # Execute
        body = json.dumps(sample_remove_schema_message).encode()
        schema_worker.process_schema_update(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify
        mock_remove_schema.assert_called_once()
        schema_worker._publish_result.assert_called_once()
        mock_channel.basic_ack.assert_called_once()

    @patch("src.workers.schemas.create_schema")
    @patch("src.workers.schemas.save_schema")
    def test_workflow_with_save_failure_recovery(
        self,
        mock_save_schema,
        mock_create_schema,
        schema_worker,
        sample_upload_schema_message,
    ):
        """Test workflow when save fails but is handled gracefully."""
        mock_schema = {"type": "object"}
        mock_create_schema.return_value = mock_schema
        mock_save_schema.side_effect = Exception("Database connection lost")

        mock_channel = MagicMock()
        schema_worker.channel = mock_channel
        schema_worker._publish_result = MagicMock()

        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_save_fail"
        mock_properties = MagicMock()

        # Execute
        body = json.dumps(sample_upload_schema_message).encode()
        schema_worker.process_schema_update(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify workflow completed (with failed status)
        result = schema_worker._publish_result.call_args[0][1]
        assert result["status"] == "failed-saving-schema"
        mock_channel.basic_ack.assert_called_once()
