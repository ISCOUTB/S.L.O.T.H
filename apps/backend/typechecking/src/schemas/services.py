"""Service Schemas Module.

This module defines TypedDict schemas used by service layer components
for file information and metadata handling. These schemas provide type
safety and structure for file-related operations throughout the application.

The schemas are used primarily for file upload validation, content type
detection, and file metadata processing in the service layer.
"""

from typing import TypedDict, Optional


class FileInfo(TypedDict):
    """File information schema for uploaded files.

    TypedDict containing metadata about uploaded files including
    basic file properties and support status. Used by file services
    to validate and process uploaded files before further processing.

    Attributes:
        filename (Optional[str]): Original name of the uploaded file, may be None if not provided.
        size (Optional[int]): Size of the file in bytes, None if size cannot be determined.
        content_type (Optional[str]): MIME type of the file content, None if not detectable.
        is_supported (bool): Boolean indicating if the file type is supported
            by the application for processing.

    Example:
        >>> file_info: FileInfo = {
        ...     "filename": "data.csv",
        ...     "size": 1024,
        ...     "content_type": "text/csv",
        ...     "is_supported": True
        ... }
    """

    filename: Optional[str]
    size: Optional[int]
    content_type: Optional[str]
    is_supported: bool
