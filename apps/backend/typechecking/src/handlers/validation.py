import multiprocessing as mp
from datetime import datetime
from typing import Any, Dict, List, Tuple

import jsonschema
from fastapi import UploadFile
from proto_utils.database import dtypes

from src.core.config import settings
from src.handlers.schemas import get_active_schema
from src.schemas.handlers import (
    ValidationResult,
    ValidationResults,
    ValidationSummary,
)
from src.services.file_processor import FileProcessor


async def validate_file_against_schema(
    file: UploadFile,
    import_name: str,
    n_workers: int = settings.MAX_WORKERS,
) -> ValidationResult:
    """
    Validate an uploaded file against its corresponding JSON schema.

    Args:
        file (UploadFile): The file to validate.
        import_name (str): The name of the import to get the schema for.
        n_workers (int): Number of worker threads for parallel validation.

    Returns:
        Dict: Validation results containing success status, statistics, and errors.
    """
    n_workers = min(n_workers, settings.MAX_WORKERS)

    # Get the active schema for the import
    schema = get_active_schema(import_name)
    if not schema:
        return {
            "success": False,
            "error": f"No active schema found for import name: {import_name}",
            "validation_results": None,
        }

    # Process the uploaded file using FileProcessor service
    file_processed, data, error_message = await FileProcessor.process_file(file)
    if not file_processed:
        return {
            "success": False,
            "error": error_message,
            "validation_results": None,
        }

    if not data:
        return {
            "success": False,
            "error": None,
            "validation_results": {
                "is_valid": False,
                "total_items": 0,
                "valid_items": 0,
                "invalid_items": 0,
                "errors": [],
                "message": "File is empty but valid",
            },
        }

    # Verify that the columns in data match the schema properties
    schema_properties = set(schema.get("properties", {}).keys())
    df_columns = set(data[0].keys())

    if df_columns != schema_properties:
        return {
            "success": False,
            "error": (
                "Columns do not match schema properties. "
                f"File columns: {sorted(df_columns)}. "
                f"Schema properties: {sorted(schema_properties)}."
            ),
            "validation_results": None,
        }

    # Try to parse the data types according to schema
    data = _convert_data_types(data, schema)

    # Validate data against schema
    validation_results = validate_data_parallel(data, schema, n_workers)

    # Add file metadata to results
    file_info = FileProcessor.get_file_info(file)
    validation_results.update(
        {
            "file_name": file_info["filename"],
            "file_size": file_info["size"],
            "content_type": file_info["content_type"],
            "import_name": import_name,
            "validated_at": datetime.now().isoformat(),
        }
    )

    return {
        "success": True,
        "error": None,
        "validation_results": validation_results,
    }


def get_validation_summary(
    validation_results: ValidationResult,
) -> ValidationSummary:
    """
    Generate a summary of validation results.

    Args:
        validation_results (Dict): The validation results from validate_file_against_schema.

    Returns:
        Dict: A summary of the validation results.
    """
    if not validation_results.get("validation_results"):
        return {"status": "error", "summary": "No validation results available"}

    results = validation_results["validation_results"]

    if results["is_valid"]:
        status = "success"
        summary = f"All {results['total_items']} items passed validation"
    else:
        status = "warning"
        summary = f"{results['invalid_items']} out of {results['total_items']} items failed validation"

    return {
        "status": status,
        "summary": summary,
        "details": {
            "total_items": results["total_items"],
            "valid_items": results["valid_items"],
            "invalid_items": results["invalid_items"],
            "error_count": len(results.get("errors", [])),
            "file_name": results.get("file_name"),
            "validated_at": results.get("validated_at"),
        },
    }


def validate_chunks(
    args: Tuple[List[Dict], Dict[str, Any], int],
) -> Tuple[int, bool, list[str]]:
    data, schema, index = args
    errors = []

    for i, item in enumerate(data):
        try:
            jsonschema.validate(instance=item, schema=schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Item {i}: {str(e)}")

    return index, len(errors) == 0, errors


def validate_data_parallel(
    data: List[Dict[str, Any]],
    schema: Dict,
    n_workers: int = settings.MAX_WORKERS,
) -> ValidationResults:
    """
    Validate data against a JSON schema using parallel processing.

    Args:
        data (List[Dict]): The data to validate.
        schema (Dict): The JSON schema to validate against.
        n_workers (int): Number of worker threads to use.

    Returns:
        Dict: A dictionary containing validation results with success status,
              total items, valid items, and error details.
    """
    if not data:
        return {
            "is_valid": True,
            "total_items": 0,
            "valid_items": 0,
            "invalid_items": 0,
            "errors": [],
        }

    # Split data into chunks for parallel processing
    chunk_size = max(1, len(data) // n_workers)
    chunks = list(
        map(
            lambda idx: (
                data[idx : idx + chunk_size],
                schema,
                idx // chunk_size,
            ),
            range(0, len(data), chunk_size),
        )
    )

    actual_processes = min(n_workers, len(chunks))
    with mp.Pool(processes=actual_processes) as pool:
        results = pool.map(validate_chunks, chunks)

    # Process results
    all_errors = []
    total_valid_items = 0

    for index, is_valid, errors in results:
        chunk_size_actual = len(chunks[index])
        if is_valid:
            total_valid_items += chunk_size_actual
            continue

        # Adjust error indices to reflect their position in the original data
        chunk_start = sum(len(chunks[j]) for j in range(index))
        adjusted_errors = []
        for error in errors:
            # Extract the item number and adjust it
            if error.startswith("Item "):
                try:
                    item_num = int(error.split(":")[0].replace("Item ", ""))
                    adjusted_error = error.replace(
                        f"Item {item_num}:", f"Item {chunk_start + item_num}:"
                    )
                    adjusted_errors.append(adjusted_error)
                except Exception:
                    adjusted_errors.append(error)
            else:
                adjusted_errors.append(error)
        all_errors.extend(adjusted_errors)
        total_valid_items += chunk_size_actual - len(errors)

    # Assuming all rows the same number of fields (should be always true for CSV/Excel at least)
    total_items = len(data) * len(data[0])
    invalid_items = total_items - total_valid_items

    # Limit errors to first 50 to avoid overwhelming response
    return {
        "is_valid": len(all_errors) == 0,
        "total_items": total_items,
        "valid_items": total_valid_items,
        "invalid_items": invalid_items,
        "errors": all_errors[:50],
    }


def _convert_data_types(
    data: List[Dict[str, Any]], schema: dtypes.JsonSchema
) -> List[Dict[str, Any]]:
    """
    Convert data types according to JSON schema definitions.

    Args:
        data: List of dictionaries representing rows
        schema: JSON schema with type definitions

    Returns:
        List of dictionaries with converted types
    """
    if not data or not schema.get("properties"):
        return data

    properties = schema["properties"]
    converted_data = []

    for row in data:
        converted_row = {}
        for key, value in row.items():
            if key not in properties:
                converted_row[key] = value
                continue

            prop_type = properties[key].get("type")

            try:
                if prop_type == "boolean":
                    # Handle boolean conversion from string representations
                    if isinstance(value, str):
                        if value.lower() in ("true", "1", "yes", "y"):
                            converted_row[key] = True
                        elif value.lower() in ("false", "0", "no", "n"):
                            converted_row[key] = False
                        else:
                            # Keep original value if can't convert
                            converted_row[key] = value
                    else:
                        converted_row[key] = bool(value)

                elif prop_type == "integer":
                    if value is None or value == "":
                        converted_row[key] = None
                    else:
                        converted_row[key] = int(float(str(value)))

                elif prop_type == "number":
                    if value is None or value == "":
                        converted_row[key] = None
                    else:
                        converted_row[key] = float(value)

                elif prop_type == "string":
                    converted_row[key] = (
                        str(value) if value is not None else None
                    )

                else:
                    # For other types (array, object, etc.), keep as is
                    converted_row[key] = value

            except (ValueError, TypeError):
                # If conversion fails, keep original value for validation to catch error
                converted_row[key] = value

        converted_data.append(converted_row)

    return converted_data
