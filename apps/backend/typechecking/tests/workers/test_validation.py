"""Unit tests for ValidationWorker.

This module contains comprehensive tests for the ValidationWorker class,
which processes file validation messages from RabbitMQ.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile

from src.workers.validation import ValidationWorker

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
def validation_worker(mock_db_client):
    """Create a ValidationWorker instance with mocked dependencies."""
    with patch(
        "src.workers.validation.get_database_client",
        return_value=mock_db_client,
    ):
        worker = ValidationWorker(
            max_retries=5,
            retry_delay=2.0,
            backoff=2.0,
            threshold=60.0,
        )
    return worker


@pytest.fixture
def sample_validation_message():
    """Create a sample validation message."""
    file_data = b"col1,col2,col3\nvalue1,value2,value3\n"
    return {
        "id": "task_123",
        "task": "sample_validation",
        "date": "2024-01-01T00:00:00",
        "import_name": "test_schema",
        "file_data": file_data.hex(),
        "metadata": {"filename": "test_file.csv"},
    }


# ============================================================================
# TEST CLASSES
# ============================================================================


class TestValidationWorkerInitialization:
    """Test ValidationWorker initialization."""

    def test_worker_initialization(self, validation_worker):
        """Test that worker is initialized correctly."""
        assert validation_worker.TASK == "validation"
        assert validation_worker.max_retries == 5
        assert validation_worker.retry_delay == 2.0
        assert validation_worker.backoff == 2.0
        assert validation_worker.threshold == 60.0
        assert validation_worker.connection is None
        assert validation_worker.channel is None
        assert validation_worker.db_client is not None

    def test_worker_initialization_custom_params(self, mock_db_client):
        """Test worker initialization with custom parameters."""
        with patch(
            "src.workers.validation.get_database_client",
            return_value=mock_db_client,
        ):
            worker = ValidationWorker(
                max_retries=10,
                retry_delay=5.0,
                backoff=1.5,
                threshold=120.0,
            )

        assert worker.max_retries == 10
        assert worker.retry_delay == 5.0
        assert worker.backoff == 1.5
        assert worker.threshold == 120.0


class TestProcessValidationRequest:
    """Test process_validation_request method."""

    @patch("src.workers.validation.asyncio.run")
    def test_process_validation_request_success(
        self, mock_asyncio_run, validation_worker, sample_validation_message
    ):
        """Test successful validation request processing."""
        # Mock channel and method
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_123"
        mock_properties = MagicMock()

        # Mock validation result
        mock_validation_result = {
            "task_id": "task_123",
            "status": "valid",
            "results": {
                "status": "valid",
                "total_rows": 1,
                "error_count": 0,
            },
        }
        mock_asyncio_run.return_value = mock_validation_result

        # Mock _publish_result
        validation_worker._publish_result = MagicMock()

        # Execute
        body = json.dumps(sample_validation_message).encode()
        validation_worker.process_validation_request(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify
        mock_asyncio_run.assert_called_once()
        validation_worker._publish_result.assert_called_once_with(
            "task_123",
            mock_validation_result,
            db_client=validation_worker.db_client,
        )
        mock_channel.basic_ack.assert_called_once_with(
            delivery_tag="delivery_123"
        )

    def test_process_validation_request_invalid_json(self, validation_worker):
        """Test handling of invalid JSON in message."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_456"
        mock_properties = MagicMock()

        # Invalid JSON body
        body = b"invalid json {{"

        # Execute
        validation_worker.process_validation_request(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify nack was called
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag="delivery_456", requeue=False
        )

    @patch("src.workers.validation.asyncio.run")
    def test_process_validation_request_validation_error(
        self, mock_asyncio_run, validation_worker, sample_validation_message
    ):
        """Test handling of validation errors."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_789"
        mock_properties = MagicMock()

        # Mock validation raising an exception
        mock_asyncio_run.side_effect = Exception("Validation failed")

        # Execute
        body = json.dumps(sample_validation_message).encode()
        validation_worker.process_validation_request(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify nack was called
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag="delivery_789", requeue=False
        )

    @patch("src.workers.validation.asyncio.run")
    def test_process_validation_request_updates_task_status(
        self, mock_asyncio_run, validation_worker, sample_validation_message
    ):
        """Test that task status is updated during processing."""
        mock_channel = MagicMock()
        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_status"
        mock_properties = MagicMock()

        mock_validation_result = {
            "task_id": "task_123",
            "status": "valid",
            "results": {},
        }
        mock_asyncio_run.return_value = mock_validation_result
        validation_worker._publish_result = MagicMock()

        # Execute
        body = json.dumps(sample_validation_message).encode()
        validation_worker.process_validation_request(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify update_task_id was called
        assert validation_worker.db_client.update_task_id.called


class TestValidateData:
    """Test _validate_data method."""

    @pytest.mark.asyncio
    @patch("src.workers.validation.validate_file_against_schema")
    @patch("src.workers.validation.get_validation_summary")
    async def test_validate_data_success(
        self,
        mock_get_summary,
        mock_validate_file,
        validation_worker,
        sample_validation_message,
    ):
        """Test successful data validation."""
        # Mock validation results
        mock_validation_results = {
            "total_rows": 1,
            "validated_items": [{"row": 1, "errors": []}],
        }
        mock_validate_file.return_value = mock_validation_results

        mock_summary = {
            "status": "valid",
            "total_rows": 1,
            "error_count": 0,
        }
        mock_get_summary.return_value = mock_summary

        # Execute
        result = await validation_worker._validate_data(
            sample_validation_message, db_client=validation_worker.db_client
        )

        # Verify
        assert result["task_id"] == "task_123"
        assert result["status"] == "valid"
        assert result["results"] == mock_summary

        # Verify file was created correctly
        mock_validate_file.assert_called_once()
        call_args = mock_validate_file.call_args
        uploaded_file = call_args[1]["file"]
        assert isinstance(uploaded_file, UploadFile)
        assert uploaded_file.filename == "test_file.csv"

    @pytest.mark.asyncio
    @patch("src.workers.validation.validate_file_against_schema")
    @patch("src.workers.validation.get_validation_summary")
    async def test_validate_data_with_errors(
        self,
        mock_get_summary,
        mock_validate_file,
        validation_worker,
        sample_validation_message,
    ):
        """Test validation with errors in data."""
        # Mock validation results with errors
        mock_validation_results = {
            "total_rows": 2,
            "validated_items": [
                {"row": 1, "errors": []},
                {"row": 2, "errors": ["Type mismatch"]},
            ],
        }
        mock_validate_file.return_value = mock_validation_results

        mock_summary = {
            "status": "invalid",
            "total_rows": 2,
            "error_count": 1,
        }
        mock_get_summary.return_value = mock_summary

        # Execute
        result = await validation_worker._validate_data(
            sample_validation_message, db_client=validation_worker.db_client
        )

        # Verify
        assert result["status"] == "invalid"
        assert result["results"]["error_count"] == 1

    @pytest.mark.asyncio
    @patch("src.workers.validation.validate_file_against_schema")
    async def test_validate_data_file_processing_error(
        self,
        mock_validate_file,
        validation_worker,
        sample_validation_message,
    ):
        """Test handling of file processing errors."""
        # Mock validation raising an exception
        mock_validate_file.side_effect = Exception("File processing error")

        # Execute and verify exception is propagated
        with pytest.raises(Exception) as exc_info:
            await validation_worker._validate_data(
                sample_validation_message,
                db_client=validation_worker.db_client,
            )

        assert "File processing error" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch("src.workers.validation.validate_file_against_schema")
    @patch("src.workers.validation.get_validation_summary")
    async def test_validate_data_updates_status(
        self,
        mock_get_summary,
        mock_validate_file,
        validation_worker,
        sample_validation_message,
    ):
        """Test that task status is updated during validation."""
        mock_validate_file.return_value = {"total_rows": 1}
        mock_get_summary.return_value = {"status": "valid"}

        # Execute
        await validation_worker._validate_data(
            sample_validation_message, db_client=validation_worker.db_client
        )

        # Verify multiple status updates were made
        assert validation_worker.db_client.update_task_id.call_count >= 3

        # Check that processing-file and validating-file statuses were set
        call_args_list = [
            call[0][0]
            for call in validation_worker.db_client.update_task_id.call_args_list
        ]
        statuses = [
            args["value"]
            for args in call_args_list
            if args["field"] == "status"
        ]
        assert "processing-file" in statuses
        assert "validating-file" in statuses

    @pytest.mark.asyncio
    @patch("src.workers.validation.validate_file_against_schema")
    @patch("src.workers.validation.get_validation_summary")
    async def test_validate_data_converts_hex_correctly(
        self,
        mock_get_summary,
        mock_validate_file,
        validation_worker,
    ):
        """Test that hexadecimal file data is converted correctly."""
        # Create message with specific content
        original_content = b"Name,Age,City\nAlice,30,NYC\nBob,25,LA\n"
        message = {
            "id": "task_hex",
            "task": "sample_validation",
            "date": "2024-01-01T00:00:00",
            "import_name": "test_schema",
            "file_data": original_content.hex(),
            "metadata": {"filename": "data.csv"},
        }

        mock_validate_file.return_value = {"total_rows": 2}
        mock_get_summary.return_value = {"status": "valid"}

        # Execute
        await validation_worker._validate_data(
            message, db_client=validation_worker.db_client
        )

        # Verify the file content
        call_args = mock_validate_file.call_args
        uploaded_file = call_args[1]["file"]
        file_content = uploaded_file.file.read()
        assert file_content == original_content


class TestPublishResult:
    """Test _publish_result method."""

    def test_publish_result_success(self, validation_worker):
        """Test successful result publishing."""
        mock_channel = MagicMock()
        validation_worker.channel = mock_channel

        result = {
            "task_id": "task_pub",
            "status": "valid",
            "results": {"total_rows": 100},
        }

        # Execute
        validation_worker._publish_result(
            "task_pub", result, db_client=validation_worker.db_client
        )

        # Verify
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args

        # Check the published message
        published_body = call_args[1]["body"]
        published_data = json.loads(published_body)
        assert published_data["task_id"] == "task_pub"
        assert published_data["status"] == "valid"

        # Verify task status was updated
        validation_worker.db_client.update_task_id.assert_called()

    def test_publish_result_with_error_status(self, validation_worker):
        """Test publishing result when validation had errors."""
        mock_channel = MagicMock()
        validation_worker.channel = mock_channel

        result = {
            "task_id": "task_error",
            "status": "error",
            "results": {"error": "Schema not found"},
        }

        # Execute
        validation_worker._publish_result(
            "task_error", result, db_client=validation_worker.db_client
        )

        # Verify that publish was NOT called for error status
        mock_channel.basic_publish.assert_not_called()

        # Verify status was updated to failed-publishing-result
        update_calls = [
            call[0][0]
            for call in validation_worker.db_client.update_task_id.call_args_list
        ]
        statuses = [c["value"] for c in update_calls if c["field"] == "status"]
        assert "failed-publishing-result" in statuses

    def test_publish_result_uses_correct_routing(self, validation_worker):
        """Test that correct exchange and routing key are used."""
        mock_channel = MagicMock()
        validation_worker.channel = mock_channel

        result = {
            "task_id": "task_routing",
            "status": "valid",
            "results": {},
        }

        # Execute
        validation_worker._publish_result(
            "task_routing", result, db_client=validation_worker.db_client
        )

        # Verify routing
        call_args = mock_channel.basic_publish.call_args
        assert "exchange" in call_args[1]
        assert "routing_key" in call_args[1]


class TestStopConsuming:
    """Test stop_consuming method."""

    def test_stop_consuming_closes_connections(self, validation_worker):
        """Test that stop_consuming closes all connections properly."""
        mock_channel = MagicMock()
        mock_channel.is_open = True
        validation_worker.channel = mock_channel

        # Execute
        with patch(
            "src.workers.validation.RabbitMQConnectionFactory.close_thread_connections"
        ) as mock_close:
            validation_worker.stop_consuming()

            # Verify
            mock_channel.stop_consuming.assert_called_once()
            mock_close.assert_called_once()
            validation_worker.db_client.close.assert_called_once()

    def test_stop_consuming_handles_closed_channel(self, validation_worker):
        """Test stop_consuming when channel is already closed."""
        mock_channel = MagicMock()
        mock_channel.is_open = False
        validation_worker.channel = mock_channel

        # Execute (should not raise exception)
        validation_worker.stop_consuming()

        # Verify db_client was still closed
        validation_worker.db_client.close.assert_called_once()

    def test_stop_consuming_handles_exceptions(self, validation_worker):
        """Test that stop_consuming handles exceptions gracefully."""
        mock_channel = MagicMock()
        mock_channel.is_open = True
        mock_channel.stop_consuming.side_effect = Exception("Channel error")
        validation_worker.channel = mock_channel

        # Execute (should not raise exception)
        validation_worker.stop_consuming()

        # Should complete without raising


class TestValidationWorkerIntegration:
    """Integration tests for complete validation workflows."""

    @patch("src.workers.validation.asyncio.run")
    @patch("src.workers.validation.validate_file_against_schema")
    @patch("src.workers.validation.get_validation_summary")
    def test_complete_validation_workflow(
        self,
        mock_get_summary,
        mock_validate_file,
        mock_asyncio_run,
        validation_worker,
        sample_validation_message,
    ):
        """Test a complete validation workflow from message to result."""
        # Setup mocks
        mock_validation_results = {
            "total_rows": 10,
            "validated_items": [{"row": i, "errors": []} for i in range(10)],
        }
        mock_summary = {
            "status": "valid",
            "total_rows": 10,
            "error_count": 0,
            "valid_rows": 10,
        }

        async def mock_validate_data(message, db_client):
            mock_validate_file.return_value = mock_validation_results
            mock_get_summary.return_value = mock_summary
            return await validation_worker._validate_data(message, db_client)

        mock_asyncio_run.side_effect = lambda coro: coro

        # Mock channel
        mock_channel = MagicMock()
        validation_worker.channel = mock_channel
        validation_worker._publish_result = MagicMock()

        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_complete"
        mock_properties = MagicMock()

        # Execute
        body = json.dumps(sample_validation_message).encode()
        validation_worker.process_validation_request(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify complete workflow
        mock_asyncio_run.assert_called_once()
        validation_worker._publish_result.assert_called_once()
        mock_channel.basic_ack.assert_called_once()

    @patch("src.workers.validation.asyncio.run")
    def test_workflow_with_mixed_results(
        self,
        mock_asyncio_run,
        validation_worker,
        sample_validation_message,
    ):
        """Test workflow with mixed valid/invalid results."""
        # Mock result with some errors
        mock_result = {
            "task_id": "task_123",
            "status": "invalid",
            "results": {
                "status": "invalid",
                "total_rows": 10,
                "error_count": 3,
                "valid_rows": 7,
            },
        }
        mock_asyncio_run.return_value = mock_result

        mock_channel = MagicMock()
        validation_worker.channel = mock_channel
        validation_worker._publish_result = MagicMock()

        mock_method = MagicMock()
        mock_method.delivery_tag = "delivery_mixed"
        mock_properties = MagicMock()

        # Execute
        body = json.dumps(sample_validation_message).encode()
        validation_worker.process_validation_request(
            mock_channel, mock_method, mock_properties, body
        )

        # Verify result was published with invalid status
        published_result = validation_worker._publish_result.call_args[0][1]
        assert published_result["status"] == "invalid"
        assert published_result["results"]["error_count"] == 3
