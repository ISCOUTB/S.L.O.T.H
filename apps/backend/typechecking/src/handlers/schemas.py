from typing import Any, Dict

from jsonschema import Draft7Validator
from proto_utils.database import dtypes

from src.core.database_client import database_client
from src.utils import get_datetime_now


def compare_schemas(schema1: Dict[str, Any], schema2: Dict[str, Any]) -> bool:
    """
    Compare two JSON schemas for equality.
    Returns True if they are equal, False otherwise.
    """
    return schema1 == schema2


def get_active_schema(import_name: str) -> dtypes.JsonSchema | None:
    """
    Get the active schema for a given import name.

    Args:
        import_name (str): The name of the import.

    Returns:
        Dict | None: The active schema if found, None otherwise.
    """
    schema_doc = database_client.mongo_find_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name)
    )

    return schema_doc["schema"] if schema_doc["status"] == "found" else None


def create_schema(raw: bool, kwargs) -> Dict:
    """
    Create a JSON schema from the provided keyword arguments.

    Args:
        raw (bool): Indicates if the schema is raw or not.
        kwargs: Key-value pairs representing the schema properties.

    Returns:
        Dict: The created JSON schema.

    Raises:
        SchemaError: If the raw schema is invalid.
    """
    if not raw:
        # TODO: Implement proper schema creation logic for non-raw schemas.
        # Any way, this is not to be intended to be used in production. Just for testing purposes.
        return {
            "type": "object",
            "properties": kwargs,
            "required": list(kwargs.keys()),
            "additionalProperties": False,
        }

    Draft7Validator.check_schema(kwargs)
    return kwargs


def save_schema(
    schema: dict, import_name: str
) -> dtypes.MongoInsertOneSchemaResponse:
    """
    Save the schema to the MongoDB collection.
    If the schema is the same as the active schema, no update is needed.
    Otherwise, update the active schema and add it to the schemas_releases.

    Args:
        schema (dict): The JSON schema to save.
        import_name (str): The name of the import, used as a unique identifier.
    Returns:
        proto_utils.database.dtypes.MongoInsertOneSchemaResponse:
        The result of the insert or update operation.
    """
    schema_key_value = schema.pop(
        "$schema", "http://json-schema.org/draft-07/schema#"
    )
    schema["schema"] = schema_key_value

    schema["properties"] = dict(
        map(
            lambda item: (
                item[0],
                {
                    "type": item[1]["type"],
                    "extra": {k: str(v) for k, v in item[1].items() if k != "type"},
                },
            ),
            schema["properties"].items(),
        )
    )

    return database_client.mongo_insert_one_schema(
        dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=get_datetime_now(),
            active_schema=schema,
            schemas_releases=[],
        )
    )


def remove_schema(import_name: str) -> dtypes.MongoDeleteOneJsonSchemaResponse:
    """
    Remove or revert a schema based on its import name.

    This function handles schema removal by either deleting the entire schema
    document if no releases exist, or reverting to the previous schema release
    by removing the most recent release and setting the active schema to the
    last available release.

    Args:
        import_name (str): The unique identifier for the schema to be removed.

    Returns:
        proto_utils.database.dtypes.MongoDeleteOneJsonSchemaResponse: Returns
            None if the schema doesn't exist.
            If no releases exist, returns the MongoDB delete result.
            If releases exist, returns a dictionary containing
            status information and the MongoDB update result.

    Note:
        - If the schema document doesn't exist, returns None
        - If no releases exist, the entire document is deleted
        - If releases exist, reverts to the previous schema by:
            * Setting active_schema to the last release's schema
            * Updating the created_at timestamp
            * Removing the most recent release from schemas_releases array
    """
    return database_client.mongo_delete_one_jsonschema(
        dtypes.MongoDeleteOneJsonSchemaRequest(import_name=import_name)
    )
