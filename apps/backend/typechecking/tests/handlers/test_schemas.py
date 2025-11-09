"""Unit tests for schema handlers.

This module contains comprehensive tests for schema-related handler functions,
including schema retrieval, creation, saving, and removal operations
with mocked DatabaseClient connections.
"""

from unittest.mock import MagicMock, patch

import pytest
from jsonschema import SchemaError

from src.handlers.schemas import (
    create_schema,
    get_active_schema,
    remove_schema,
    save_schema,
)


class TestGetActiveSchema:
    """Test suite for get_active_schema function."""

    def test_get_active_schema_found(self):
        """Test retrieving an active schema that exists."""
        mock_db_client = MagicMock()
        mock_schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }
        mock_db_client.mongo_find_jsonschema.return_value = {
            "status": "found",
            "schema": mock_schema,
        }

        result = get_active_schema("test_import", mock_db_client)

        assert result == mock_schema
        mock_db_client.mongo_find_jsonschema.assert_called_once()
        # Verify the request was made with correct import_name
        # Note: TypedDict is a dict, not an object with attributes
        request = mock_db_client.mongo_find_jsonschema.call_args.args[0]
        assert request["import_name"] == "test_import"

    def test_get_active_schema_not_found(self):
        """Test retrieving a schema that doesn't exist."""
        mock_db_client = MagicMock()
        mock_db_client.mongo_find_jsonschema.return_value = {
            "status": "not_found",
            "schema": None,
        }

        result = get_active_schema("non_existent_import", mock_db_client)

        assert result is None
        mock_db_client.mongo_find_jsonschema.assert_called_once()

    def test_get_active_schema_with_complex_schema(self):
        """Test retrieving a complex schema with multiple properties."""
        mock_db_client = MagicMock()
        complex_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1, "maxLength": 100},
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
                "email": {"type": "string", "format": "email"},
                "active": {"type": "boolean"},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"},
                    },
                },
            },
            "required": ["name", "email"],
        }
        mock_db_client.mongo_find_jsonschema.return_value = {
            "status": "found",
            "schema": complex_schema,
        }

        result = get_active_schema("complex_import", mock_db_client)

        assert result == complex_schema
        assert "properties" in result
        assert "name" in result["properties"]


class TestCreateSchema:
    """Test suite for create_schema function."""

    def test_create_schema_non_raw(self):
        """Test creating a non-raw schema from keyword arguments."""
        properties = {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string"},
        }

        result = create_schema(raw=False, kwargs=properties)

        assert result["type"] == "object"
        assert result["properties"] == properties
        assert result["required"] == ["name", "age", "email"]
        assert result["additionalProperties"] is False

    def test_create_schema_raw_valid(self):
        """Test creating a raw schema with valid JSON schema."""
        raw_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
            },
            "required": ["name"],
        }

        result = create_schema(raw=True, kwargs=raw_schema)

        assert result == raw_schema

    def test_create_schema_raw_invalid(self):
        """Test creating a raw schema with invalid JSON schema raises error."""
        invalid_schema = {
            "type": "invalid_type",  # Invalid type
            "properties": {"name": {"type": "string"}},
        }

        with pytest.raises(SchemaError):
            create_schema(raw=True, kwargs=invalid_schema)

    def test_create_schema_non_raw_empty_properties(self):
        """Test creating a non-raw schema with empty properties."""
        result = create_schema(raw=False, kwargs={})

        assert result["type"] == "object"
        assert result["properties"] == {}
        assert result["required"] == []
        assert result["additionalProperties"] is False

    def test_create_schema_raw_with_complex_validation(self):
        """Test creating a raw schema with complex validation rules."""
        complex_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 18, "maximum": 100},
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
            },
            "required": ["email"],
            "additionalProperties": False,
        }

        result = create_schema(raw=True, kwargs=complex_schema)

        assert result == complex_schema


class TestSaveSchema:
    """Test suite for save_schema function."""

    @patch("src.handlers.schemas.get_datetime_now")
    def test_save_schema_success(self, mock_datetime):
        """Test successfully saving a schema."""
        mock_datetime.return_value = "2024-01-01T12:00:00"
        mock_db_client = MagicMock()
        mock_response = {"status": "success", "inserted_id": "schema_123"}
        mock_db_client.mongo_insert_one_schema.return_value = mock_response

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "age": {"type": "integer", "minimum": 0},
            },
        }

        result = save_schema(schema.copy(), "test_import", mock_db_client)

        assert result == mock_response
        mock_db_client.mongo_insert_one_schema.assert_called_once()

        # Verify the request structure (TypedDict = dict)
        request = mock_db_client.mongo_insert_one_schema.call_args.args[0]
        assert request["import_name"] == "test_import"
        assert request["created_at"] == "2024-01-01T12:00:00"
        assert request["schemas_releases"] == []

    @patch("src.handlers.schemas.get_datetime_now")
    def test_save_schema_transforms_properties(self, mock_datetime):
        """Test that save_schema properly transforms property structures."""
        mock_datetime.return_value = "2024-01-01T12:00:00"
        mock_db_client = MagicMock()
        mock_db_client.mongo_insert_one_schema.return_value = {"status": "success"}

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1, "maxLength": 100},
                "age": {"type": "integer", "minimum": 0, "maximum": 120},
            },
        }

        save_schema(schema.copy(), "test_import", mock_db_client)

        request = mock_db_client.mongo_insert_one_schema.call_args.args[0]
        active_schema = request["active_schema"]

        # Verify properties transformation
        assert "name" in active_schema["properties"]
        assert active_schema["properties"]["name"]["type"] == "string"
        assert "extra" in active_schema["properties"]["name"]
        assert active_schema["properties"]["name"]["extra"]["minLength"] == "1"
        assert active_schema["properties"]["name"]["extra"]["maxLength"] == "100"

    @patch("src.handlers.schemas.get_datetime_now")
    def test_save_schema_removes_schema_key(self, mock_datetime):
        """Test that $schema key is removed and stored separately."""
        mock_datetime.return_value = "2024-01-01T12:00:00"
        mock_db_client = MagicMock()
        mock_db_client.mongo_insert_one_schema.return_value = {"status": "success"}

        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }

        save_schema(schema.copy(), "test_import", mock_db_client)

        request = mock_db_client.mongo_insert_one_schema.call_args.args[0]
        active_schema = request["active_schema"]

        assert "$schema" not in active_schema
        assert active_schema["schema"] == "http://json-schema.org/draft-07/schema#"

    @patch("src.handlers.schemas.get_datetime_now")
    def test_save_schema_with_custom_schema_version(self, mock_datetime):
        """Test saving schema with custom $schema version."""
        mock_datetime.return_value = "2024-01-01T12:00:00"
        mock_db_client = MagicMock()
        mock_db_client.mongo_insert_one_schema.return_value = {"status": "success"}

        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }

        save_schema(schema.copy(), "test_import", mock_db_client)

        request = mock_db_client.mongo_insert_one_schema.call_args.args[0]
        active_schema = request["active_schema"]

        assert active_schema["schema"] == "http://json-schema.org/draft-04/schema#"


class TestRemoveSchema:
    """Test suite for remove_schema function."""

    def test_remove_schema_success(self):
        """Test successfully removing a schema."""
        mock_db_client = MagicMock()
        mock_response = {"status": "deleted", "deleted_count": 1}
        mock_db_client.mongo_delete_one_jsonschema.return_value = mock_response

        result = remove_schema("test_import", mock_db_client)

        assert result == mock_response
        mock_db_client.mongo_delete_one_jsonschema.assert_called_once()

        request = mock_db_client.mongo_delete_one_jsonschema.call_args.args[0]
        assert request["import_name"] == "test_import"

    def test_remove_schema_not_found(self):
        """Test removing a schema that doesn't exist."""
        mock_db_client = MagicMock()
        mock_response = {"status": "not_found", "deleted_count": 0}
        mock_db_client.mongo_delete_one_jsonschema.return_value = mock_response

        result = remove_schema("non_existent_import", mock_db_client)

        assert result == mock_response
        assert result["deleted_count"] == 0

    def test_remove_schema_with_releases(self):
        """Test removing a schema that has releases (should revert)."""
        mock_db_client = MagicMock()
        mock_response = {
            "status": "reverted",
            "message": "Reverted to previous schema",
            "modified_count": 1,
        }
        mock_db_client.mongo_delete_one_jsonschema.return_value = mock_response

        result = remove_schema("test_import", mock_db_client)

        assert result == mock_response
        mock_db_client.mongo_delete_one_jsonschema.assert_called_once()


class TestIntegrationSchemas:
    """Integration tests for schema operations."""

    @patch("src.handlers.schemas.get_datetime_now")
    def test_full_schema_lifecycle(self, mock_datetime):
        """Test complete schema lifecycle: create, save, get, remove."""
        mock_datetime.return_value = "2024-01-01T12:00:00"
        mock_db_client = MagicMock()

        # 1. Create schema
        properties = {
            "name": {"type": "string"},
            "age": {"type": "integer"},
        }
        created_schema = create_schema(raw=False, kwargs=properties)

        assert created_schema["type"] == "object"
        assert "properties" in created_schema

        # 2. Save schema
        mock_db_client.mongo_insert_one_schema.return_value = {
            "status": "success",
            "inserted_id": "schema_123",
        }

        save_result = save_schema(created_schema.copy(), "test_import", mock_db_client)
        assert save_result["status"] == "success"

        # 3. Get active schema
        mock_db_client.mongo_find_jsonschema.return_value = {
            "status": "found",
            "schema": created_schema,
        }

        retrieved_schema = get_active_schema("test_import", mock_db_client)
        assert created_schema == retrieved_schema

        # 4. Remove schema
        mock_db_client.mongo_delete_one_jsonschema.return_value = {
            "status": "deleted",
            "deleted_count": 1,
        }

        remove_result = remove_schema("test_import", mock_db_client)
        assert remove_result["status"] == "deleted"

    def test_compare_created_schemas(self):
        """Test that two schemas created the same way are equal."""
        properties = {"name": {"type": "string"}, "age": {"type": "integer"}}

        schema1 = create_schema(raw=False, kwargs=properties)
        schema2 = create_schema(raw=False, kwargs=properties)

        assert schema1 == schema2
