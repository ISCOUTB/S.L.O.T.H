import io
from typing import Dict, List, Tuple

import polars as pl
from fastapi import UploadFile

from src.schemas.services import FileInfo


class FileProcessor:
    """Service class for processing uploaded files."""

    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

    @classmethod
    async def process_file(
        cls, file: UploadFile
    ) -> Tuple[bool, List[Dict], str]:
        """
        Process an uploaded file and convert it to a list of dictionaries.

        Args:
            file (UploadFile): The uploaded file to process.

        Returns:
            Tuple[bool, List[Dict], str]: A tuple containing:
                - success (bool): Whether the processing was successful
                - data (List[Dict]): The processed data as a list of dictionaries
                - error_message (str): Error message if processing failed
        """
        try:
            # Validate file type
            if not cls._is_supported_file(file.filename):
                return (
                    False,
                    [],
                    f"Unsupported file type. Supported types: {', '.join(cls.SUPPORTED_EXTENSIONS)}",
                )

            # Read file content
            content = await file.read()

            # Process based on file type
            filename_lower = file.filename.lower()

            if filename_lower.endswith(".csv"):
                return cls._process_csv_content(content)
            if filename_lower.endswith((".xlsx", ".xls")):
                return cls._process_excel_content(content)

        except Exception as e:
            return False, [], f"Error processing file: {str(e)}"

        return False, [], "Unknown error occurred during file processing"

    @classmethod
    def _is_supported_file(cls, filename: str) -> bool:
        """Check if the file type is supported."""
        if not filename:
            return False

        filename_lower = filename.lower()
        return any(
            filename_lower.endswith(ext) for ext in cls.SUPPORTED_EXTENSIONS
        )

    @classmethod
    def _process_csv_content(
        cls, content: bytes
    ) -> Tuple[bool, List[Dict], str]:
        """
        Process CSV file content.

        Args:
            content (bytes): The CSV file content as bytes.

        Returns:
            Tuple[bool, List[Dict], str]: Processing result.
        """
        try:
            # Try different encodings
            for encoding in ["utf-8", "latin-1", "cp1252"]:
                try:
                    csv_string = content.decode(encoding)
                    df = pl.read_csv(io.StringIO(csv_string))
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return (
                    False,
                    [],
                    "Unable to decode CSV file with supported encodings",
                )

            # Handle empty file
            if df.height == 0:
                return True, [], ""

            data = df.to_dicts()
            return True, data, ""

        except Exception as e:
            return False, [], f"Error processing CSV file: {str(e)}"

    @classmethod
    def _process_excel_content(
        cls, content: bytes
    ) -> Tuple[bool, List[Dict], str]:
        """
        Process Excel file content.

        Args:
            content (bytes): The Excel file content as bytes.

        Returns:
            Tuple[bool, List[Dict], str]: Processing result.
        """
        try:
            # Read Excel file from bytes
            df = pl.read_excel(io.BytesIO(content), engine="openpyxl")

            if df.height == 0:
                return True, [], ""

            data = df.to_dicts()
            return True, data, ""

        except Exception as e:
            return False, [], f"Error processing Excel file: {str(e)}"

    @classmethod
    def get_file_info(cls, file: UploadFile) -> FileInfo:
        """
        Get basic information about the uploaded file.

        Args:
            file (UploadFile): The uploaded file.

        Returns:
            FileInfo: File information.
        """
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file.size,
            "is_supported": cls._is_supported_file(file.filename),
        }
