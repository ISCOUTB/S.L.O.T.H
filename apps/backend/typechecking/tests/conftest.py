"""Pytest configuration and fixtures for typechecking tests.

This module provides shared fixtures and configuration for the typechecking
test suite. Fixtures include sample files, schemas, and test data that are
reused across multiple test modules.
"""

import io
from typing import Any, Dict, List

import polars as pl
import pytest
from fastapi import UploadFile


@pytest.fixture
def sample_csv_content() -> bytes:
    """Sample CSV content for testing."""
    csv_data = """name,age,email,active
John Doe,30,john@example.com,true
Jane Smith,25,jane@example.com,false
Bob Johnson,35,bob@example.com,true
"""
    return csv_data.encode("utf-8")


@pytest.fixture
def sample_csv_latin1_content() -> bytes:
    """Sample CSV with latin-1 encoding (with special characters)."""
    csv_data = """name,age,email,active
José García,30,jose@example.com,true
María López,25,maria@example.com,false
"""
    return csv_data.encode("latin-1")


@pytest.fixture
def empty_csv_content() -> bytes:
    """Empty CSV with only headers."""
    return b"name,age,email,active\n"


@pytest.fixture
def sample_excel_content() -> bytes:
    """Sample Excel content for testing."""
    df = pl.DataFrame(
        {
            "name": ["John Doe", "Jane Smith", "Bob Johnson"],
            "age": [30, 25, 35],
            "email": [
                "john@example.com",
                "jane@example.com",
                "bob@example.com",
            ],
            "active": [True, False, True],
        }
    )
    buffer = io.BytesIO()
    df.write_excel(buffer)
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def invalid_csv_content() -> bytes:
    """Corrupted CSV content."""
    return b"\x00\x01\x02\xff\xfe invalid data"


@pytest.fixture
def sample_upload_file_csv(sample_csv_content: bytes) -> UploadFile:
    """Create a mock UploadFile for CSV testing."""
    file = UploadFile(
        filename="test.csv",
        file=io.BytesIO(sample_csv_content),
    )
    file.size = len(sample_csv_content)
    return file


@pytest.fixture
def sample_upload_file_excel(sample_excel_content: bytes) -> UploadFile:
    """Create a mock UploadFile for Excel testing."""
    file = UploadFile(
        filename="test.xlsx",
        file=io.BytesIO(sample_excel_content),
    )
    file.size = len(sample_excel_content)
    return file


@pytest.fixture
def sample_json_schema() -> Dict[str, Any]:
    """Sample JSON schema for validation testing."""
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0, "maximum": 120},
            "email": {"type": "string", "format": "email"},
            "active": {"type": "boolean"},
        },
        "required": ["name", "age", "email", "active"],
    }


@pytest.fixture
def sample_valid_data() -> List[Dict[str, Any]]:
    """Sample valid data matching the schema."""
    return [
        {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "active": True,
        },
        {
            "name": "Jane Smith",
            "age": 25,
            "email": "jane@example.com",
            "active": False,
        },
        {
            "name": "Bob Johnson",
            "age": 35,
            "email": "bob@example.com",
            "active": True,
        },
    ]


@pytest.fixture
def sample_invalid_data() -> List[Dict[str, Any]]:
    """Sample invalid data (violates schema)."""
    return [
        {
            "name": "John Doe",
            "age": -5,  # Invalid: negative age
            "email": "john@example.com",
            "active": True,
        },
        {
            "name": "Jane Smith",
            "age": 150,  # Invalid: age > 120
            "email": "not-an-email",  # Invalid: not an email format
            "active": False,
        },
    ]


@pytest.fixture
def sample_mixed_data() -> List[Dict[str, Any]]:
    """Sample data with both valid and invalid items."""
    return [
        {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com",
            "active": True,
        },
        {
            "name": "Jane Smith",
            "age": -10,  # Invalid
            "email": "jane@example.com",
            "active": False,
        },
        {
            "name": "Bob Johnson",
            "age": 35,
            "email": "invalid-email",  # Invalid
            "active": True,
        },
    ]


@pytest.fixture
def sample_data_for_type_conversion() -> List[Dict[str, Any]]:
    """Sample data with string values that need type conversion."""
    return [
        {
            "name": "John Doe",
            "age": "30",  # String that should convert to int
            "email": "john@example.com",
            "active": "true",  # String that should convert to boolean
        },
        {
            "name": "Jane Smith",
            "age": "25.0",  # String with decimal that should convert to int
            "email": "jane@example.com",
            "active": "false",
        },
    ]
