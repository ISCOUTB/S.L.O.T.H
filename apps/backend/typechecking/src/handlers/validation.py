import jsonschema
import multiprocessing as mp

from datetime import datetime
from typing import Dict, List, Tuple, Any
from fastapi import UploadFile

from src.core.config import settings
from src.handlers.schemas import get_active_schema
from src.services.file_processor import FileProcessor
from src.schemas.handlers import (
    ValidationResult,
    ValidationSummary,
    ValidationResults,
)


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
        return {"success": False, "error": error_message, "validation_results": None}

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

    return {"success": True, "error": None, "validation_results": validation_results}


def get_validation_summary(validation_results: ValidationResult) -> ValidationSummary:
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
    chunks = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    chunk_size = max(1, len(data) // n_workers)
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        chunks.append((chunk, schema, i))

    with mp.Pool(processes=n_workers) as pool:
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

    total_items = len(data)
    invalid_items = total_items - total_valid_items

    # Limit errors to first 50 to avoid overwhelming response
    return {
        "is_valid": len(all_errors) == 0,
        "total_items": total_items,
        "valid_items": total_valid_items,
        "invalid_items": invalid_items,
        "errors": all_errors[:50],
    }
