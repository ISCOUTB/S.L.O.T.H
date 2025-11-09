"""Unit tests for healthcheck service.

This module contains comprehensive tests for the healthcheck functionality,
including RabbitMQ and database connection checks.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.healthcheck import (
    check_database_client_connection,
    check_databases_connection,
    check_rabbitmq_connection,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_db_client():
    """Create a mock DatabaseClient."""
    mock_client = MagicMock()
    mock_client.redis_ping = MagicMock(return_value={"pong": True})
    mock_client.mongo_ping = MagicMock(return_value={"pong": True})
    return mock_client


# ============================================================================
# TEST CLASSES
# ============================================================================


class TestCheckRabbitMQConnection:
    """Test suite for RabbitMQ connection health checks."""

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.aio_pika.connect_robust")
    async def test_rabbitmq_connection_healthy(self, mock_connect):
        """Test successful RabbitMQ connection."""
        # Mock connection and channel
        mock_channel = AsyncMock()
        mock_connection = AsyncMock()
        mock_connection.channel.return_value = mock_channel
        mock_connect.return_value = mock_connection

        # Execute
        result = await check_rabbitmq_connection()

        # Verify
        assert result["status"] == "healthy"
        assert "response_time_ms" in result
        assert result["response_time_ms"] == "< 5000"

        # Verify connections were closed
        mock_channel.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.aio_pika.connect_robust")
    async def test_rabbitmq_connection_timeout(self, mock_connect):
        """Test RabbitMQ connection timeout."""
        # Mock timeout
        mock_connect.side_effect = asyncio.TimeoutError()

        # Execute
        result = await check_rabbitmq_connection()

        # Verify
        assert result["status"] == "unhealthy"
        assert result["error"] == "Connection timeout"
        assert result["response_time_ms"] == "> 5000"

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.aio_pika.connect_robust")
    async def test_rabbitmq_connection_error(self, mock_connect):
        """Test RabbitMQ connection error."""
        # Mock connection error
        mock_connect.side_effect = Exception("Connection refused")

        # Execute
        result = await check_rabbitmq_connection()

        # Verify
        assert result["status"] == "unhealthy"
        assert "error" in result
        assert "Connection refused" in result["error"]

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.aio_pika.connect_robust")
    async def test_rabbitmq_connection_channel_error(self, mock_connect):
        """Test RabbitMQ channel creation error."""
        # Mock connection succeeds but channel fails
        mock_connection = AsyncMock()
        mock_connection.channel.side_effect = Exception("Channel error")
        mock_connect.return_value = mock_connection

        # Execute
        result = await check_rabbitmq_connection()

        # Verify
        assert result["status"] == "unhealthy"
        assert "Channel error" in result["error"]


class TestCheckDatabaseClientConnection:
    """Test suite for database client connection health checks."""

    def test_database_connection_all_healthy(self, mock_db_client):
        """Test when all database connections are healthy."""
        # Execute
        result = check_database_client_connection(mock_db_client)

        # Verify
        assert result["status"] == "healthy"
        assert result["mongodb"] is True
        assert result["redis"] is True

        # Verify methods were called
        mock_db_client.redis_ping.assert_called_once()
        mock_db_client.mongo_ping.assert_called_once()

    def test_database_connection_redis_unhealthy(self, mock_db_client):
        """Test when Redis connection is unhealthy."""
        # Mock Redis failing
        mock_db_client.redis_ping.side_effect = Exception(
            "Redis connection error"
        )

        # Execute
        result = check_database_client_connection(mock_db_client)

        # Verify
        assert result["status"] == "unhealthy"
        assert result["mongodb"] is True
        assert result["redis"] is False

    def test_database_connection_mongodb_unhealthy(self, mock_db_client):
        """Test when MongoDB connection is unhealthy."""
        # Mock MongoDB failing
        mock_db_client.mongo_ping.side_effect = Exception(
            "MongoDB connection error"
        )

        # Execute
        result = check_database_client_connection(mock_db_client)

        # Verify
        assert result["status"] == "unhealthy"
        assert result["mongodb"] is False
        assert result["redis"] is True

    def test_database_connection_all_unhealthy(self, mock_db_client):
        """Test when all database connections are unhealthy."""
        # Mock both failing
        mock_db_client.redis_ping.side_effect = Exception("Redis error")
        mock_db_client.mongo_ping.side_effect = Exception("MongoDB error")

        # Execute
        result = check_database_client_connection(mock_db_client)

        # Verify
        assert result["status"] == "unhealthy"
        assert result["mongodb"] is False
        assert result["redis"] is False

    def test_database_connection_redis_returns_false(self, mock_db_client):
        """Test when Redis ping returns False instead of raising exception."""
        # Mock Redis returning False in pong
        mock_db_client.redis_ping.return_value = {"pong": False}

        # Execute
        result = check_database_client_connection(mock_db_client)

        # Verify
        assert result["status"] == "unhealthy"
        assert result["redis"] is False


class TestCheckDatabasesConnection:
    """Test suite for overall database and RabbitMQ health checks."""

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.check_rabbitmq_connection")
    @patch("src.services.healthcheck.check_database_client_connection")
    async def test_all_services_healthy(
        self,
        mock_db_check,
        mock_rabbitmq_check,
        mock_db_client,
    ):
        """Test when all services are healthy."""
        # Mock all services as healthy
        mock_db_check.return_value = {
            "status": "healthy",
            "mongodb": True,
            "redis": True,
        }
        mock_rabbitmq_check.return_value = {
            "status": "healthy",
            "response_time_ms": "< 5000",
        }

        # Execute
        result = await check_databases_connection(mock_db_client)

        # Verify
        assert result["status"] == "healthy"
        assert result["database"]["status"] == "healthy"
        assert result["rabbitmq"]["status"] == "healthy"

        # Verify functions were called
        mock_db_check.assert_called_once_with(mock_db_client)
        mock_rabbitmq_check.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.check_rabbitmq_connection")
    @patch("src.services.healthcheck.check_database_client_connection")
    async def test_database_unhealthy(
        self,
        mock_db_check,
        mock_rabbitmq_check,
        mock_db_client,
    ):
        """Test when database is unhealthy but RabbitMQ is healthy."""
        # Mock database as unhealthy
        mock_db_check.return_value = {
            "status": "unhealthy",
            "mongodb": False,
            "redis": True,
        }
        mock_rabbitmq_check.return_value = {
            "status": "healthy",
            "response_time_ms": "< 5000",
        }

        # Execute
        result = await check_databases_connection(mock_db_client)

        # Verify
        assert result["status"] == "unhealthy"
        assert result["database"]["status"] == "unhealthy"
        assert result["rabbitmq"]["status"] == "healthy"

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.check_rabbitmq_connection")
    @patch("src.services.healthcheck.check_database_client_connection")
    async def test_rabbitmq_unhealthy(
        self,
        mock_db_check,
        mock_rabbitmq_check,
        mock_db_client,
    ):
        """Test when RabbitMQ is unhealthy but database is healthy."""
        # Mock RabbitMQ as unhealthy
        mock_db_check.return_value = {
            "status": "healthy",
            "mongodb": True,
            "redis": True,
        }
        mock_rabbitmq_check.return_value = {
            "status": "unhealthy",
            "error": "Connection timeout",
        }

        # Execute
        result = await check_databases_connection(mock_db_client)

        # Verify
        assert result["status"] == "unhealthy"
        assert result["database"]["status"] == "healthy"
        assert result["rabbitmq"]["status"] == "unhealthy"

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.check_rabbitmq_connection")
    @patch("src.services.healthcheck.check_database_client_connection")
    async def test_all_services_unhealthy(
        self,
        mock_db_check,
        mock_rabbitmq_check,
        mock_db_client,
    ):
        """Test when all services are unhealthy."""
        # Mock all services as unhealthy
        mock_db_check.return_value = {
            "status": "unhealthy",
            "mongodb": False,
            "redis": False,
        }
        mock_rabbitmq_check.return_value = {
            "status": "unhealthy",
            "error": "Connection refused",
        }

        # Execute
        result = await check_databases_connection(mock_db_client)

        # Verify
        assert result["status"] == "unhealthy"
        assert result["database"]["status"] == "unhealthy"
        assert result["rabbitmq"]["status"] == "unhealthy"

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.check_rabbitmq_connection")
    @patch("src.services.healthcheck.check_database_client_connection")
    async def test_check_includes_detailed_info(
        self,
        mock_db_check,
        mock_rabbitmq_check,
        mock_db_client,
    ):
        """Test that detailed information is included in the response."""
        # Mock with detailed information
        mock_db_check.return_value = {
            "status": "healthy",
            "mongodb": True,
            "redis": True,
        }
        mock_rabbitmq_check.return_value = {
            "status": "healthy",
            "response_time_ms": "< 5000",
        }

        # Execute
        result = await check_databases_connection(mock_db_client)

        # Verify detailed structure
        assert "database" in result
        assert "rabbitmq" in result
        assert "mongodb" in result["database"]
        assert "redis" in result["database"]
        assert "response_time_ms" in result["rabbitmq"]


class TestHealthcheckIntegration:
    """Integration tests for healthcheck workflows."""

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.aio_pika.connect_robust")
    async def test_full_healthcheck_workflow(
        self,
        mock_connect,
        mock_db_client,
    ):
        """Test a complete healthcheck workflow."""
        # Setup mocks
        mock_channel = AsyncMock()
        mock_connection = AsyncMock()
        mock_connection.channel.return_value = mock_channel
        mock_connect.return_value = mock_connection

        # Execute
        result = await check_databases_connection(mock_db_client)

        # Verify complete structure
        assert "status" in result
        assert "database" in result
        assert "rabbitmq" in result
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    @patch("src.services.healthcheck.aio_pika.connect_robust")
    async def test_partial_failure_workflow(
        self,
        mock_connect,
        mock_db_client,
    ):
        """Test healthcheck with partial service failures."""
        # Setup: RabbitMQ fails, databases succeed
        mock_connect.side_effect = Exception("RabbitMQ down")

        # Execute
        result = await check_databases_connection(mock_db_client)

        # Verify
        assert result["status"] == "unhealthy"
        assert result["database"]["status"] == "healthy"
        assert result["rabbitmq"]["status"] == "unhealthy"
        assert "error" in result["rabbitmq"]
