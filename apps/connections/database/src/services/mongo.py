"""MongoDB schemas service operations module.

This module provides high-level MongoDB service operations for managing
JSON schemas in the database. It implements the service layer pattern
to handle schema CRUD operations with proper versioning and comparison
functionality.

The module includes operations for schema insertion, updates, deletion,
and retrieval with built-in schema comparison and version management
through releases tracking.
"""

import pymongo
from proto_utils.database import dtypes
from core.database_mongo import mongo_schemas_connection


class MongoSchemasService:
    """MongoDB schemas service layer class.

    Provides high-level MongoDB operations for JSON schema management
    including versioning, comparison, and CRUD operations. This class
    acts as a service layer between API endpoints and the MongoDB
    database operations.
    """

    @staticmethod
    def compare_schemas(schema1: dtypes.JsonSchema, schema2: dtypes.JsonSchema) -> bool:
        """Compare two JSON schemas for equality.

        Args:
            schema1 (dtypes.JsonSchema): First schema to compare.
            schema2 (dtypes.JsonSchema): Second schema to compare.

        Returns:
            bool: True if schemas are equal, False otherwise.
        """
        return schema1 == schema2

    @staticmethod
    def insert_one_schema(
        request: dtypes.MongoInsertOneSchemaRequest,
    ) -> dtypes.MongoInsertOneSchemaResponse:
        """Insert or update a JSON schema in the database.

        This method handles schema insertion with intelligent version management.
        If no schema exists, it inserts a new one. If a schema exists and is
        identical, it returns no-change status. If different, it updates the
        schema and moves the old one to releases.

        Args:
            request (dtypes.MongoInsertOneSchemaRequest): Request containing
                                                         the schema data to insert.

        Returns:
            dtypes.MongoInsertOneSchemaResponse: Response indicating the operation
                                               result (inserted, updated, no_change, or error).
        """
        total_documents = MongoSchemasService.count_all_documents()["amount"]
        schemas_releases = MongoSchemasService.find_one_jsonschema(
            dtypes.MongoInsertOneSchemaRequest(import_name=request["import_name"])
        )

        # Try to fetch the existing schema document, and if it's not, then insert a new one.
        if total_documents <= 0 or schemas_releases["schema"] is None:
            try:
                result: pymongo.results.InsertOneResult = (
                    mongo_schemas_connection.insert_one(request)
                )
                return dtypes.MongoInsertOneSchemaResponse(
                    status="inserted",
                    result={
                        "acknowledged": result.acknowledged,
                        "inserted_id": str(result.inserted_id),
                    },
                )
            except Exception as e:
                return dtypes.MongoInsertOneSchemaResponse(
                    status="error",
                    result={"message": str(e)},
                )

        # If the schema already exists, compare it with the new one,
        # and if they are identical, return a no-change response.
        new_active_schema = request["active_schema"]
        if MongoSchemasService.compare_schemas(
            schemas_releases["schema"]["active_schema"], new_active_schema
        ):
            return dtypes.MongoInsertOneSchemaResponse(
                status="no_change",
                result={"message": "Schema is identical to the existing one."},
            )

        # If the schema is different, update the existing document.
        try:
            result: pymongo.results.UpdateResult = mongo_schemas_connection.update_one(
                {"import_name": request["import_name"]},
                {
                    "$set": {
                        "active_schema": new_active_schema.copy(),
                        "created_at": request["created_at"],
                    },
                    "$push": {
                        "schemas_releases": {
                            "schema": (
                                schemas_releases["schema"]["active_schema"]
                            ).copy(),
                            "created_at": schemas_releases["schema"]["created_at"],
                        }
                    },
                },
            )
        except Exception as e:
            return dtypes.MongoInsertOneSchemaResponse(
                status="error",
                result={"message": str(e)},
            )

        return dtypes.MongoInsertOneSchemaResponse(
            status="updated",
            result={
                "message": "Schema successfully updated",
                "modified_count": str(result.modified_count),
                "matched_count": str(result.matched_count),
            },
        )

    @staticmethod
    def count_all_documents(
        _: dtypes.MongoCountAllDocumentsRequest = None,
    ) -> dtypes.MongoCountAllDocumentsResponse:
        """Count all documents in the schemas collection.

        Args:
            _ (dtypes.MongoCountAllDocumentsRequest, optional): Unused request parameter.

        Returns:
            dtypes.MongoCountAllDocumentsResponse: Response containing the document count.
                                                 Returns -1 if an error occurs.
        """
        try:
            amount = mongo_schemas_connection.count_documents()
        except Exception:
            amount = -1

        return dtypes.MongoCountAllDocumentsResponse(amount=amount)

    @staticmethod
    def find_one_jsonschema(
        request: dtypes.MongoFindJsonSchemaRequest,
    ) -> dtypes.MongoFindJsonSchemaResponse:
        """Find a JSON schema by import name.

        Args:
            request (dtypes.MongoFindJsonSchemaRequest): Request containing the
                                                       import name to search for.

        Returns:
            dtypes.MongoFindJsonSchemaResponse: Response containing the found schema
                                              or appropriate status (not_found, error).
        """
        try:
            schema_doc = mongo_schemas_connection.find_one(
                {"import_name": request["import_name"]}
            )
            if not (schema_doc and "active_schema" in schema_doc):
                return dtypes.MongoFindJsonSchemaResponse(
                    status="not_found", extra={}, schema=None
                )
        except Exception as e:
            extra = {"error": str(e)}

            return dtypes.MongoFindJsonSchemaResponse(
                status="error", extra=extra, schema=None
            )

        return dtypes.MongoFindJsonSchemaResponse(
            status="found", extra={}, schema=schema_doc
        )

    @staticmethod
    def update_one_schema(
        request: dtypes.MongoUpdateOneJsonSchemaRequest,
    ) -> dtypes.MongoUpdateOneJsonSchemaResponse:
        """Update an existing JSON schema.

        This method updates an existing schema with a new version, preserving
        the old version in the releases history. It includes schema comparison
        to avoid unnecessary updates when schemas are identical.

        Args:
            request (dtypes.MongoUpdateOneJsonSchemaRequest): Request containing
                                                            the import name and new schema.

        Returns:
            dtypes.MongoUpdateOneJsonSchemaResponse: Response indicating the operation
                                                   result (updated, no_change, or error).
        """
        # First, check if the schema document exists
        existing_schema = MongoSchemasService.find_one_jsonschema(
            dtypes.MongoFindJsonSchemaRequest(import_name=request["import_name"])
        )

        # If schema doesn't exist, return error
        if existing_schema["status"] != "found" or existing_schema["schema"] is None:
            return dtypes.MongoUpdateOneJsonSchemaResponse(
                status="error",
                result={
                    "message": f"Schema with import_name '{request['import_name']}' not found",
                },
            )

        current_schema_doc = existing_schema["schema"]
        current_active_schema = current_schema_doc["active_schema"]

        # Compare the new schema with the current active schema
        if MongoSchemasService.compare_schemas(
            current_active_schema, request["schema"]
        ):
            return dtypes.MongoUpdateOneJsonSchemaResponse(
                status="no_change",
                result={
                    "message": "New schema is identical to the current active schema",
                },
            )

        # Update the document with the new schema
        try:
            result: pymongo.results.UpdateResult = mongo_schemas_connection.update_one(
                {"import_name": request["import_name"]},
                {
                    "$set": {
                        "active_schema": request["schema"],
                        "created_at": request["created_at"],
                    },
                    "$push": {"schemas_releases": current_active_schema},
                },
            )

            if result.modified_count > 0:
                return dtypes.MongoUpdateOneJsonSchemaResponse(
                    status="updated",
                    result={
                        "message": "Schema successfully updated",
                        "modified_count": str(result.modified_count),
                        "matched_count": str(result.matched_count),
                    },
                )
            else:
                return dtypes.MongoUpdateOneJsonSchemaResponse(
                    status="error",
                    result={
                        "message": "No documents were modified during update operation",
                    },
                )

        except Exception as e:
            return dtypes.MongoUpdateOneJsonSchemaResponse(
                status="error",
                result={
                    "message": f"Failed to update schema: {str(e)}",
                },
            )

    @staticmethod
    def delete_one_schema(
        request: dtypes.MongoDeleteOneJsonSchemaRequest,
    ) -> dtypes.MongoDeleteOneJsonSchemaResponse:
        """Delete the current active schema or revert to previous version.

        This method implements intelligent schema deletion. If there are previous
        versions in releases, it reverts to the most recent one. If no releases
        exist, it deletes the entire schema document.

        Args:
            request (dtypes.MongoDeleteOneJsonSchemaRequest): Request containing
                                                            the import name to delete.

        Returns:
            dtypes.MongoDeleteOneJsonSchemaResponse: Response indicating the operation
                                                   result (deleted, reverted, or error).
        """
        schema_doc = MongoSchemasService.find_one_jsonschema(
            dtypes.MongoFindJsonSchemaRequest(import_name=request["import_name"])
        )

        if schema_doc["status"] != "found" or schema_doc["schema"] is None:
            return dtypes.MongoDeleteOneJsonSchemaResponse(
                success=False,
                message=f"Schema with import_name '{request['import_name']}' not found",
                status="error",
                extra={},
            )

        releases = schema_doc["schema"].get("schemas_releases", [])

        if not releases:
            result: pymongo.results.DeleteResult = mongo_schemas_connection.delete_one(
                {"import_name": request["import_name"]}
            )
            return dtypes.MongoDeleteOneJsonSchemaResponse(
                success=True,
                message=f"Schema with import_name '{request['import_name']}' deleted",
                status="deleted",
                extra={**result.raw_result},
            )

        result: pymongo.results.UpdateResult = mongo_schemas_connection.update_one(
            {"import_name": request["import_name"]},
            {
                "$set": {
                    "active_schema": releases[-1]["schema"].copy(),
                    "created_at": releases[-1].get(
                        "created_at", schema_doc["schema"]["created_at"]
                    ),
                },
                "$pop": {"schemas_releases": 1},
            },
        )

        return dtypes.MongoDeleteOneJsonSchemaResponse(
            success=True,
            message=f"Schema with import_name '{request['import_name']}' reverted to previous release",
            status="reverted",
            extra={**result.raw_result},
        )

    @staticmethod
    def delete_import_name(
        request: dtypes.MongoDeleteImportNameRequest,
    ) -> dtypes.MongoDeleteImportNameResponse:
        """Delete all schemas associated with an import name.

        This method completely removes all schema data (including releases)
        for a given import name from the database.

        Args:
            request (dtypes.MongoDeleteImportNameRequest): Request containing
                                                         the import name to delete.

        Returns:
            dtypes.MongoDeleteImportNameResponse: Response indicating the operation
                                                result (deleted or error).
        """
        try:
            result: pymongo.results.DeleteResult = mongo_schemas_connection.delete_one(
                {"import_name": request["import_name"]}
            )
            if result.deleted_count > 0:
                return dtypes.MongoDeleteImportNameResponse(
                    success=True,
                    message=f"All schemas with import_name '{request['import_name']}' deleted",
                    status="deleted",
                    extra={**result.raw_result},
                )
            else:
                return dtypes.MongoDeleteImportNameResponse(
                    success=False,
                    message=f"No schemas found with import_name '{request['import_name']}'",
                    status="error",
                    extra={},
                )
        except Exception as e:
            return dtypes.MongoDeleteImportNameResponse(
                success=False,
                message=f"Failed to delete schemas: {str(e)}",
                status="error",
                extra={},
            )
