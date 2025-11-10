"""Unit tests for minimal FastAPI server.

This module contains comprehensive tests for the minimal HTTP server endpoints,
including root and health check endpoints using FastAPI's TestClient.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.minimal_server import app

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_db_client():
    """Create a mock DatabaseClient."""
    mock_client = MagicMock()
    mock_client.redis_ping = MagicMock(return_value={"pong": True})
    mock_client.mongo_ping = MagicMock(return_value={"pong": True})
    mock_client.close = MagicMock()
    return mock_client


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI app."""
    return TestClient(app)


# ============================================================================
# TEST CLASSES
# ============================================================================


class TestRootEndpoint:
    """Test suite for root endpoint."""

    def test_root_returns_message(self, client):
        """Test that root endpoint returns correct message."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.json() == {"message": "Minimal Typechecking Server is running."}

    def test_root_content_type(self, client):
        """Test that root endpoint returns JSON."""
        response = client.get("/")

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_root_multiple_requests(self, client):
        """Test that root endpoint is idempotent."""
        response1 = client.get("/")
        response2 = client.get("/")
        response3 = client.get("/")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        assert response1.json() == response2.json() == response3.json()


class TestHealthEndpoint:
    """Test suite for health check endpoint."""

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_check_all_healthy(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test health check when all services are healthy."""
        # Setup mocks
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "healthy",
            "database": {
                "status": "healthy",
                "mongodb": True,
                "redis": True,
            },
            "rabbitmq": {
                "status": "healthy",
                "response_time_ms": "< 5000",
            },
        }

        # Execute
        response = client.get("/health")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"]["status"] == "healthy"
        assert data["rabbitmq"]["status"] == "healthy"

        # Verify database client was used
        mock_check_databases.assert_called_once()

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_check_database_unhealthy(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test health check when database is unhealthy."""
        # Setup mocks
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "unhealthy",
            "database": {
                "status": "unhealthy",
                "mongodb": False,
                "redis": True,
            },
            "rabbitmq": {
                "status": "healthy",
                "response_time_ms": "< 5000",
            },
        }

        # Execute
        response = client.get("/health")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"]["status"] == "unhealthy"
        assert data["database"]["mongodb"] is False

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_check_rabbitmq_unhealthy(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test health check when RabbitMQ is unhealthy."""
        # Setup mocks
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "unhealthy",
            "database": {
                "status": "healthy",
                "mongodb": True,
                "redis": True,
            },
            "rabbitmq": {
                "status": "unhealthy",
                "error": "Connection timeout",
            },
        }

        # Execute
        response = client.get("/health")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["rabbitmq"]["status"] == "unhealthy"
        assert "error" in data["rabbitmq"]

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_check_all_unhealthy(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test health check when all services are unhealthy."""
        # Setup mocks
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "unhealthy",
            "database": {
                "status": "unhealthy",
                "mongodb": False,
                "redis": False,
            },
            "rabbitmq": {
                "status": "unhealthy",
                "error": "Connection refused",
            },
        }

        # Execute
        response = client.get("/health")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"]["status"] == "unhealthy"
        assert data["rabbitmq"]["status"] == "unhealthy"

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_check_returns_json(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test that health endpoint returns JSON."""
        # Setup mocks
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "healthy",
            "database": {"status": "healthy", "mongodb": True, "redis": True},
            "rabbitmq": {"status": "healthy"},
        }

        # Execute
        response = client.get("/health")

        # Verify
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_check_closes_db_client(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test that database client is properly closed after health check."""
        # Setup mocks
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "healthy",
            "database": {"status": "healthy", "mongodb": True, "redis": True},
            "rabbitmq": {"status": "healthy"},
        }

        # Execute
        response = client.get("/health")

        # Verify
        assert response.status_code == 200
        # The client should be closed due to the finally block in the dependency
        mock_db_client.close.assert_called()


class TestEndpointIntegration:
    """Integration tests for server endpoints."""

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_multiple_health_checks(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test multiple consecutive health checks."""
        # Setup mocks
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "healthy",
            "database": {"status": "healthy", "mongodb": True, "redis": True},
            "rabbitmq": {"status": "healthy"},
        }

        # Execute multiple requests
        response1 = client.get("/health")
        response2 = client.get("/health")
        response3 = client.get("/health")

        # Verify all succeeded
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # Verify check was called multiple times
        assert mock_check_databases.call_count == 3

    def test_root_and_health_endpoints_work(self, client):
        """Test that both endpoints are accessible."""
        root_response = client.get("/")

        # For health, we need to mock since it has dependencies
        with (
            patch("src.minimal_server.get_database_client") as mock_get_db,
            patch("src.minimal_server.check_databases_connection") as mock_check,
        ):
            mock_db = MagicMock()
            mock_db.close = MagicMock()
            mock_get_db.return_value = mock_db
            mock_check.return_value = {
                "status": "healthy",
                "database": {
                    "status": "healthy",
                    "mongodb": True,
                    "redis": True,
                },
                "rabbitmq": {"status": "healthy"},
            }

            health_response = client.get("/health")

        assert root_response.status_code == 200
        assert health_response.status_code == 200

    def test_nonexistent_endpoint_returns_404(self, client):
        """Test that nonexistent endpoints return 404."""
        response = client.get("/nonexistent")

        assert response.status_code == 404

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_endpoint_structure(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test that health endpoint returns expected structure."""
        # Setup mocks
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "healthy",
            "database": {
                "status": "healthy",
                "mongodb": True,
                "redis": True,
            },
            "rabbitmq": {
                "status": "healthy",
                "response_time_ms": "< 5000",
            },
        }

        # Execute
        response = client.get("/health")
        data = response.json()

        # Verify structure
        assert "status" in data
        assert "database" in data
        assert "rabbitmq" in data
        assert "status" in data["database"]
        assert "mongodb" in data["database"]
        assert "redis" in data["database"]
        assert "status" in data["rabbitmq"]


class TestErrorHandling:
    """Test error handling in server endpoints."""

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_check_handles_exception(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test that health endpoint handles exceptions gracefully."""
        # Setup mocks to raise an exception
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.side_effect = Exception("Unexpected error")

        # Execute - should raise exception (FastAPI will handle it)
        with pytest.raises(Exception) as exc_info:
            client.get("/health")

        assert "Unexpected error" in str(exc_info.value)

    @patch("src.minimal_server.get_database_client")
    @patch("src.minimal_server.check_databases_connection")
    def test_health_check_with_partial_data(
        self,
        mock_check_databases,
        mock_get_db_client,
        client,
        mock_db_client,
    ):
        """Test health check with partial/incomplete data."""
        # Setup mocks with minimal data
        mock_get_db_client.return_value = mock_db_client
        mock_check_databases.return_value = {
            "status": "unhealthy",
            "database": {"status": "unhealthy"},
            "rabbitmq": {"status": "unhealthy"},
        }

        # Execute
        response = client.get("/health")

        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"


class TestServerConfiguration:
    """Test server configuration and setup."""

    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance."""
        assert isinstance(app, FastAPI)

    def test_client_can_be_created(self):
        """Test that TestClient can be created successfully."""
        test_client = TestClient(app)
        assert test_client is not None

    def test_routes_are_registered(self):
        """Test that expected routes are registered."""
        routes = [route.path for route in app.routes]
        assert "/" in routes
        assert "/health" in routes
