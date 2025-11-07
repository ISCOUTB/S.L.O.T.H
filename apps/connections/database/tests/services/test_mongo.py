from datetime import datetime, timedelta
from uuid import uuid4

from proto_utils.database import dtypes

from src.core.database_mongo import MongoConnection
from src.services.mongo import MongoSchemasService


def test_compare_different_schemas() -> None:
    json_schema_1: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    json_schema_2: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
            "address": {"type": "string"},
        },
        "required": ["name", "email", "address"],
    }

    response = MongoSchemasService.compare_schemas(
        schema1=json_schema_1, schema2=json_schema_2
    )

    assert response is False


def test_compare_identical_schemas() -> None:
    json_schema: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    response = MongoSchemasService.compare_schemas(
        schema1=json_schema, schema2=json_schema.copy()
    )

    assert response is True


def test_count_all_documents(mongo_schemas_connection: MongoConnection) -> None:
    response = MongoSchemasService.count_all_documents(
        mongo_schemas_connection=mongo_schemas_connection
    )
    assert isinstance(response["amount"], int)
    assert response["amount"] >= 0


def test_insert_one_schema(mongo_schemas_connection: MongoConnection) -> None:
    json_schema: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    response = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=f"import_name_test-{uuid4()}",
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "inserted"


def test_find_one_jsonschema(mongo_schemas_connection: MongoConnection) -> None:
    json_schema: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    import_name = f"import_name_test-{uuid4()}"

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "found"
    assert response["schema"]["import_name"] == import_name
    assert (
        MongoSchemasService.compare_schemas(
            response["schema"]["active_schema"], json_schema
        )
        is True
    )


def test_find_one_jsonschema_not_found(
    mongo_schemas_connection: MongoConnection,
) -> None:
    response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=f"non_existent-{uuid4()}"),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "not_found"
    assert response["schema"] is None


def test_insert_one_schema_duplicate(mongo_schemas_connection: MongoConnection) -> None:
    json_schema: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    import_name = f"import_name_test-{uuid4()}"

    response1 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    response2 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response1["status"] == "inserted"
    assert response2["status"] == "no_change"


def test_insert_one_schema_update(mongo_schemas_connection: MongoConnection) -> None:
    json_schema_v1: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    json_schema_v2: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
            "address": {"type": "string"},
        },
        "required": ["name", "email", "address"],
    }

    import_name = f"import_name_test-{uuid4()}"

    response1 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema_v1,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    response2 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema_v2,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response1["status"] == "inserted"
    assert response2["status"] == "updated"

    # Verify schema releases
    find_response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert find_response["status"] == "found"
    assert len(find_response["schema"]["schemas_releases"]) == 1
    assert (
        MongoSchemasService.compare_schemas(
            find_response["schema"]["schemas_releases"][0]["schema"], json_schema_v1
        )
        is True
    )


def test_update_one_schema(mongo_schemas_connection: MongoConnection) -> None:
    json_schema_v1: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    json_schema_v2: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
            "address": {"type": "string"},
        },
        "required": ["name", "email", "address"],
    }

    import_name = f"import_name_test-{uuid4()}"

    response1 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema_v1,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    response2 = MongoSchemasService.update_one_schema(
        request=dtypes.MongoUpdateOneJsonSchemaRequest(
            import_name=import_name,
            schema=json_schema_v2,
            created_at=datetime.now(),
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response1["status"] == "inserted"
    assert response2["status"] == "updated"


def test_update_one_schema_not_found(mongo_schemas_connection: MongoConnection) -> None:
    json_schema: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    response = MongoSchemasService.update_one_schema(
        request=dtypes.MongoUpdateOneJsonSchemaRequest(
            import_name=f"non_existent-{uuid4()}",
            schema=json_schema,
            created_at=datetime.now(),
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "error"


def test_update_one_schema_no_change(mongo_schemas_connection: MongoConnection) -> None:
    json_schema: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    import_name = f"import_name_test-{uuid4()}"

    response1 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    response2 = MongoSchemasService.update_one_schema(
        request=dtypes.MongoUpdateOneJsonSchemaRequest(
            import_name=import_name,
            schema=json_schema,
            created_at=datetime.now(),
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response1["status"] == "inserted"
    assert response2["status"] == "no_change"


def test_delete_one_schema_with_no_releases(
    mongo_schemas_connection: MongoConnection,
) -> None:
    json_schema: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    import_name = f"import_name_test-{uuid4()}"

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    response = MongoSchemasService.delete_one_schema(
        request=dtypes.MongoDeleteOneJsonSchemaRequest(import_name=import_name),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "deleted"

    # Verify deletion
    find_response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert find_response["status"] == "not_found"


def test_delete_one_schema_with_releases(
    mongo_schemas_connection: MongoConnection,
) -> None:
    json_schema_v1: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    json_schema_v2: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
            "address": {"type": "string"},
        },
        "required": ["name", "email", "address"],
    }

    import_name = f"import_name_test-{uuid4()}"

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema_v1,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now() + timedelta(minutes=10),
            active_schema=json_schema_v2,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    response = MongoSchemasService.delete_one_schema(
        request=dtypes.MongoDeleteOneJsonSchemaRequest(import_name=import_name),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "reverted"

    # Verify reversion
    find_response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert find_response["status"] == "found"
    assert (
        MongoSchemasService.compare_schemas(
            find_response["schema"]["active_schema"], json_schema_v1
        )
        is True
    )


def test_delete_one_schema_not_found(mongo_schemas_connection: MongoConnection) -> None:
    response = MongoSchemasService.delete_one_schema(
        request=dtypes.MongoDeleteOneJsonSchemaRequest(
            import_name=f"non_existent-{uuid4()}"
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "error"


def test_delete_import_name(mongo_schemas_connection: MongoConnection) -> None:
    json_schema: dtypes.JsonSchema = {
        "schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string", "format": "email"},
        },
        "required": ["name", "email"],
    }

    import_name = f"import_name_test-{uuid4()}"

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    response = MongoSchemasService.delete_import_name(
        request=dtypes.MongoDeleteImportNameRequest(import_name=import_name),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "deleted"

    # Verify deletion
    find_response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert find_response["status"] == "not_found"


def test_delete_import_name_not_found(
    mongo_schemas_connection: MongoConnection,
) -> None:
    response = MongoSchemasService.delete_import_name(
        request=dtypes.MongoDeleteImportNameRequest(
            import_name=f"non_existent-{uuid4()}"
        ),
        mongo_schemas_connection=mongo_schemas_connection,
    )

    assert response["status"] == "error"
