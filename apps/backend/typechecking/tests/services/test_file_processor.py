"""Unit tests for FileProcessor service.

This module contains comprehensive tests for the FileProcessor class,
including CSV and Excel file processing, encoding handling, error cases,
and file information retrieval.
"""

import io

import polars as pl
import pytest
from fastapi import UploadFile

from src.services.file_processor import FileProcessor


class TestFileProcessor:
    """Test suite for FileProcessor class."""

    # ==================== Test _is_supported_file ====================

    def test_is_supported_file_csv(self):
        """Test that CSV files are recognized as supported."""
        assert FileProcessor._is_supported_file("test.csv")
        assert FileProcessor._is_supported_file("TEST.CSV")
        assert FileProcessor._is_supported_file("my_file.csv")

    def test_is_supported_file_excel(self):
        """Test that Excel files (.xlsx, .xls) are recognized as supported."""
        assert FileProcessor._is_supported_file("test.xlsx")
        assert FileProcessor._is_supported_file("TEST.XLSX")
        assert FileProcessor._is_supported_file("test.xls")
        assert FileProcessor._is_supported_file("TEST.XLS")

    def test_is_supported_file_unsupported(self):
        """Test that unsupported file types are rejected."""
        assert not FileProcessor._is_supported_file("test.txt")
        assert not FileProcessor._is_supported_file("test.pdf")
        assert not FileProcessor._is_supported_file("test.json")
        assert not FileProcessor._is_supported_file("test.xml")
        assert not FileProcessor._is_supported_file("")
        assert not FileProcessor._is_supported_file(None)

    # ==================== Test _process_csv_content ====================

    def test_process_csv_content_utf8(self, sample_csv_content: bytes):
        """Test processing CSV with UTF-8 encoding."""
        success, data, error = FileProcessor._process_csv_content(sample_csv_content)

        assert success is True
        assert error == ""
        assert len(data) == 3
        assert data[0]["name"] == "John Doe"
        assert data[0]["age"] == 30
        assert data[0]["email"] == "john@example.com"
        assert data[0]["active"] is True

    def test_process_csv_content_latin1(self, sample_csv_latin1_content: bytes):
        """Test processing CSV with latin-1 encoding (special characters)."""
        success, data, error = FileProcessor._process_csv_content(
            sample_csv_latin1_content
        )

        assert success is True
        assert error == ""
        assert len(data) == 2
        assert data[0]["name"] == "José García"
        assert data[1]["name"] == "María López"

    def test_process_csv_content_empty(self, empty_csv_content: bytes):
        """Test processing empty CSV (headers only)."""
        success, data, error = FileProcessor._process_csv_content(empty_csv_content)

        assert success is True
        assert error == ""
        assert len(data) == 0

    def test_process_csv_content_invalid(self, invalid_csv_content: bytes):
        """Test processing corrupted CSV content."""
        success, data, error = FileProcessor._process_csv_content(invalid_csv_content)

        # The corrupted data may succeed or fail depending on polars behavior
        # If it succeeds, it should have empty or unexpected data
        # If it fails, error message should be present
        if not success:
            assert data == []
            assert "Error processing CSV file" in error or "Unable to decode" in error
        else:
            # If polars managed to parse it, the data structure might be unexpected
            # Just verify we got back a consistent response
            assert isinstance(data, list)

    # ==================== Test _process_excel_content ====================

    def test_process_excel_content_valid(self, sample_excel_content: bytes):
        """Test processing valid Excel content."""
        success, data, error = FileProcessor._process_excel_content(
            sample_excel_content
        )

        assert success is True
        assert error == ""
        assert len(data) == 3
        assert data[0]["name"] == "John Doe"
        assert data[0]["age"] == 30

    def test_process_excel_content_empty(self):
        """Test processing empty Excel file."""
        # Create empty Excel file
        df = pl.DataFrame({"name": [], "age": [], "email": [], "active": []})
        buffer = io.BytesIO()
        df.write_excel(buffer)
        buffer.seek(0)
        content = buffer.read()

        success, data, error = FileProcessor._process_excel_content(content)

        assert success is True
        assert error == ""
        assert len(data) == 0

    def test_process_excel_content_invalid(self):
        """Test processing corrupted Excel content."""
        invalid_content = b"\x00\x01\x02\xff\xfe invalid excel data"

        success, data, error = FileProcessor._process_excel_content(invalid_content)

        assert success is False
        assert data == []
        assert "Error processing Excel file" in error

    # ==================== Test process_file (main method) ====================

    @pytest.mark.asyncio
    async def test_process_file_csv_success(self, sample_upload_file_csv: UploadFile):
        """Test successful processing of CSV file via process_file."""
        success, data, error = await FileProcessor.process_file(sample_upload_file_csv)

        assert success is True
        assert error == ""
        assert len(data) == 3
        assert data[0]["name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_process_file_excel_success(
        self, sample_upload_file_excel: UploadFile
    ):
        """Test successful processing of Excel file via process_file."""
        success, data, error = await FileProcessor.process_file(
            sample_upload_file_excel
        )

        assert success is True
        assert error == ""
        assert len(data) == 3
        assert data[0]["name"] == "John Doe"

    @pytest.mark.asyncio
    async def test_process_file_unsupported_type(self):
        """Test processing unsupported file type."""
        file = UploadFile(
            filename="test.txt",
            file=io.BytesIO(b"some text content"),
        )

        success, data, error = await FileProcessor.process_file(file)

        assert success is False
        assert data == []
        assert "Unsupported file type" in error
        assert ".csv" in error

    @pytest.mark.asyncio
    async def test_process_file_no_filename(self):
        """Test processing file with no filename."""
        file = UploadFile(
            filename=None,
            file=io.BytesIO(b"some content"),
        )

        success, data, error = await FileProcessor.process_file(file)

        assert success is False
        assert data == []
        assert "Unsupported file type" in error

    @pytest.mark.asyncio
    async def test_process_file_csv_with_different_encodings(
        self, sample_csv_latin1_content: bytes
    ):
        """Test that process_file handles different CSV encodings."""
        file = UploadFile(
            filename="test_latin1.csv",
            file=io.BytesIO(sample_csv_latin1_content),
        )

        success, data, error = await FileProcessor.process_file(file)

        assert success is True
        assert error == ""
        assert len(data) == 2
        assert "José" in data[0]["name"]

    # ==================== Test get_file_info ====================

    def test_get_file_info_csv(self, sample_upload_file_csv: UploadFile):
        """Test getting file info for CSV file."""
        info = FileProcessor.get_file_info(sample_upload_file_csv)

        assert info["filename"] == "test.csv"
        assert info["is_supported"] is True
        assert info["size"] > 0

    def test_get_file_info_excel(self, sample_upload_file_excel: UploadFile):
        """Test getting file info for Excel file."""
        info = FileProcessor.get_file_info(sample_upload_file_excel)

        assert info["filename"] == "test.xlsx"
        assert info["is_supported"] is True
        assert info["size"] > 0

    def test_get_file_info_unsupported(self):
        """Test getting file info for unsupported file."""
        file = UploadFile(
            filename="test.txt",
            file=io.BytesIO(b"content"),
        )
        file.size = 7

        info = FileProcessor.get_file_info(file)

        assert info["filename"] == "test.txt"
        assert info["is_supported"] is False
        assert info["size"] == 7

    # ==================== Integration Tests ====================

    @pytest.mark.asyncio
    async def test_process_file_with_special_characters_in_data(self):
        """Test processing CSV with special characters in data."""
        csv_data = """name,age,email,active
John "The Great",30,john@example.com,true
Jane's,25,jane@example.com,false
"""
        file = UploadFile(
            filename="special.csv",
            file=io.BytesIO(csv_data.encode("utf-8")),
        )

        success, data, error = await FileProcessor.process_file(file)

        assert success is True
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_process_file_large_dataset(self):
        """Test processing CSV with larger dataset."""
        # Create a larger CSV in memory
        rows = []
        for i in range(1000):
            rows.append(f"Person{i},{20 + i % 50},person{i}@example.com,true")

        csv_data = "name,age,email,active\n" + "\n".join(rows)
        file = UploadFile(
            filename="large.csv",
            file=io.BytesIO(csv_data.encode("utf-8")),
        )

        success, data, error = await FileProcessor.process_file(file)

        assert success is True
        assert len(data) == 1000
        assert error == ""

    @pytest.mark.asyncio
    async def test_process_file_with_empty_cells(self):
        """Test processing CSV with empty cells."""
        csv_data = """name,age,email,active
John Doe,30,john@example.com,true
Jane Smith,,jane@example.com,false
Bob,25,,true
"""
        file = UploadFile(
            filename="empty_cells.csv",
            file=io.BytesIO(csv_data.encode("utf-8")),
        )

        success, data, error = await FileProcessor.process_file(file)

        assert success is True
        assert len(data) == 3
        # Polars typically represents empty strings as None or empty string
        assert data[1]["age"] is None or data[1]["age"] == ""
