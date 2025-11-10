"""Unit tests for worker utilities.

This module contains comprehensive tests for worker utility functions,
specifically the update_task_status function with mocked DatabaseClient connections.
"""

from unittest.mock import MagicMock

from src.workers.utils import update_task_status


class TestUpdateTaskStatus:
    """Test suite for update_task_status function."""

    def test_update_task_status_basic(self):
        """Test updating task status with basic parameters."""
        mock_db_client = MagicMock()

        update_task_status(
            task_id="task_123",
            field="status",
            value="processing",
            task="schema_validation",
            database_client=mock_db_client,
        )

        mock_db_client.update_task_id.assert_called_once()
        call_args = mock_db_client.update_task_id.call_args[0][0]

        assert call_args["task_id"] == "task_123"
        assert call_args["field"] == "status"
        assert call_args["value"] == "processing"
        assert call_args["task"] == "schema_validation"
        assert call_args["message"] == ""
        assert call_args["data"] is None
        assert call_args["reset_data"] is False

    def test_update_task_status_with_message(self):
        """Test updating task status with a message."""
        mock_db_client = MagicMock()

        update_task_status(
            task_id="task_456",
            field="status",
            value="completed",
            task="validation",
            database_client=mock_db_client,
            message="Validation completed successfully",
        )

        mock_db_client.update_task_id.assert_called_once()
        call_args = mock_db_client.update_task_id.call_args[0][0]

        assert call_args["message"] == "Validation completed successfully"

    def test_update_task_status_with_data(self):
        """Test updating task status with additional data."""
        mock_db_client = MagicMock()
        additional_data = {
            "total_rows": "1000",
            "valid_rows": "950",
            "invalid_rows": "50",
        }

        update_task_status(
            task_id="task_789",
            field="progress",
            value="100",
            task="data_validation",
            database_client=mock_db_client,
            data=additional_data,
        )

        mock_db_client.update_task_id.assert_called_once()
        call_args = mock_db_client.update_task_id.call_args[0][0]

        assert call_args["data"] == additional_data
        assert call_args["data"]["total_rows"] == "1000"

    def test_update_task_status_with_reset_data(self):
        """Test updating task status with data reset flag."""
        mock_db_client = MagicMock()

        update_task_status(
            task_id="task_reset",
            field="status",
            value="restarted",
            task="validation",
            database_client=mock_db_client,
            reset_data=True,
        )

        mock_db_client.update_task_id.assert_called_once()
        call_args = mock_db_client.update_task_id.call_args[0][0]

        assert call_args["reset_data"] is True

    def test_update_task_status_progress_update(self):
        """Test updating task progress field."""
        mock_db_client = MagicMock()

        update_task_status(
            task_id="task_progress",
            field="progress",
            value="75",
            task="file_processing",
            database_client=mock_db_client,
            message="Processing 750/1000 rows",
        )

        mock_db_client.update_task_id.assert_called_once()
        call_args = mock_db_client.update_task_id.call_args[0][0]

        assert call_args["field"] == "progress"
        assert call_args["value"] == "75"

    def test_update_task_status_error_scenario(self):
        """Test updating task status for error scenario."""
        mock_db_client = MagicMock()
        error_data = {
            "error_type": "ValidationError",
            "error_message": "Invalid schema format",
        }

        update_task_status(
            task_id="task_error",
            field="status",
            value="failed",
            task="schema_validation",
            database_client=mock_db_client,
            message="Validation failed due to schema error",
            data=error_data,
        )

        mock_db_client.update_task_id.assert_called_once()
        call_args = mock_db_client.update_task_id.call_args[0][0]

        assert call_args["value"] == "failed"
        assert call_args["data"]["error_type"] == "ValidationError"

    def test_update_task_status_multiple_calls(self):
        """Test multiple sequential task status updates."""
        mock_db_client = MagicMock()

        # First update: start processing
        update_task_status(
            task_id="task_multi",
            field="status",
            value="started",
            task="validation",
            database_client=mock_db_client,
        )

        # Second update: progress
        update_task_status(
            task_id="task_multi",
            field="progress",
            value="50",
            task="validation",
            database_client=mock_db_client,
        )

        # Third update: complete
        update_task_status(
            task_id="task_multi",
            field="status",
            value="completed",
            task="validation",
            database_client=mock_db_client,
        )

        assert mock_db_client.update_task_id.call_count == 3

    def test_update_task_status_with_all_parameters(self):
        """Test updating task status with all optional parameters."""
        mock_db_client = MagicMock()
        data = {"rows_processed": "500", "time_elapsed": "30s"}

        update_task_status(
            task_id="task_complete",
            field="status",
            value="completed",
            task="full_validation",
            database_client=mock_db_client,
            message="All validations passed",
            data=data,
            reset_data=False,
        )

        mock_db_client.update_task_id.assert_called_once()
        call_args = mock_db_client.update_task_id.call_args[0][0]

        assert call_args["task_id"] == "task_complete"
        assert call_args["field"] == "status"
        assert call_args["value"] == "completed"
        assert call_args["task"] == "full_validation"
        assert call_args["message"] == "All validations passed"
        assert call_args["data"] == data
        assert call_args["reset_data"] is False

    def test_update_task_status_empty_message(self):
        """Test that empty message is handled correctly."""
        mock_db_client = MagicMock()

        update_task_status(
            task_id="task_empty_msg",
            field="status",
            value="processing",
            task="validation",
            database_client=mock_db_client,
            message="",
        )

        call_args = mock_db_client.update_task_id.call_args[0][0]
        assert call_args["message"] == ""

    def test_update_task_status_none_data(self):
        """Test that None data is handled correctly."""
        mock_db_client = MagicMock()

        update_task_status(
            task_id="task_none_data",
            field="status",
            value="processing",
            task="validation",
            database_client=mock_db_client,
            data=None,
        )

        call_args = mock_db_client.update_task_id.call_args[0][0]
        assert call_args["data"] is None

    def test_update_task_status_different_field_types(self):
        """Test updating different types of fields."""
        mock_db_client = MagicMock()

        # Test with integer value
        update_task_status(
            task_id="task_int",
            field="retry_count",
            value=3,
            task="validation",
            database_client=mock_db_client,
        )

        # Test with boolean value
        update_task_status(
            task_id="task_bool",
            field="is_completed",
            value=True,
            task="validation",
            database_client=mock_db_client,
        )

        # Test with list value
        update_task_status(
            task_id="task_list",
            field="errors",
            value=["error1", "error2"],
            task="validation",
            database_client=mock_db_client,
        )

        assert mock_db_client.update_task_id.call_count == 3


class TestUpdateTaskStatusIntegration:
    """Integration tests for update_task_status in realistic scenarios."""

    def test_validation_workflow(self):
        """Test a complete validation workflow with status updates."""
        mock_db_client = MagicMock()

        # Step 1: Mark as started
        update_task_status(
            task_id="workflow_123",
            field="status",
            value="started",
            task="validation",
            database_client=mock_db_client,
            message="Starting validation process",
            reset_data=True,
        )

        # Step 2: Update progress
        update_task_status(
            task_id="workflow_123",
            field="progress",
            value="30",
            task="validation",
            database_client=mock_db_client,
            data={"rows_validated": "300"},
        )

        # Step 3: Update progress again
        update_task_status(
            task_id="workflow_123",
            field="progress",
            value="70",
            task="validation",
            database_client=mock_db_client,
            data={"rows_validated": "700"},
        )

        # Step 4: Mark as completed
        update_task_status(
            task_id="workflow_123",
            field="status",
            value="completed",
            task="validation",
            database_client=mock_db_client,
            message="Validation completed successfully",
            data={
                "total_rows": "1000",
                "valid_rows": "950",
                "invalid_rows": "50",
            },
        )

        assert mock_db_client.update_task_id.call_count == 4

        # Verify the last call (completion)
        last_call_args = mock_db_client.update_task_id.call_args[0][0]
        assert last_call_args["value"] == "completed"
        assert last_call_args["data"]["total_rows"] == "1000"

    def test_error_recovery_workflow(self):
        """Test a workflow with error and recovery."""
        mock_db_client = MagicMock()

        # Start processing
        update_task_status(
            task_id="error_task",
            field="status",
            value="processing",
            task="validation",
            database_client=mock_db_client,
        )

        # Encounter error
        update_task_status(
            task_id="error_task",
            field="status",
            value="error",
            task="validation",
            database_client=mock_db_client,
            message="Temporary connection error",
            data={"retry_count": "1"},
        )

        # Retry
        update_task_status(
            task_id="error_task",
            field="status",
            value="retrying",
            task="validation",
            database_client=mock_db_client,
            message="Retrying validation",
        )

        # Success on retry
        update_task_status(
            task_id="error_task",
            field="status",
            value="completed",
            task="validation",
            database_client=mock_db_client,
            message="Validation completed after retry",
        )

        assert mock_db_client.update_task_id.call_count == 4
