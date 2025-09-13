from uuid import uuid4
from datetime import datetime, timedelta
from proto_utils.database import dtypes
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


def test_count_all_documents() -> None:
    response = MongoSchemasService.count_all_documents()
    assert isinstance(response["amount"], int)
    assert response["amount"] >= 0


def test_insert_one_schema() -> None:
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

    schema = json_schema.pop("schema")
    json_schema["$schema"] = schema

    response = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=f"import_name_test-{uuid4()}",
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        )
    )

    assert response["result"]["status"] == "inserted"


def test_find_one_jsonschema() -> None:
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

    schema = json_schema.pop("schema")
    json_schema["$schema"] = schema

    import_name = f"import_name_test-{uuid4()}"

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        )
    )

    response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name)
    )

    assert response["status"] == "found"
    assert response["schema"]["import_name"] == import_name
    assert (
        MongoSchemasService.compare_schemas(
            response["schema"]["active_schema"], json_schema
        )
        is True
    )


def test_find_one_jsonschema_not_found() -> None:
    response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=f"non_existent-{uuid4()}")
    )

    assert response["status"] == "not_found"
    assert response["schema"] is None


def test_insert_one_schema_duplicate() -> None:
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

    schema = json_schema.pop("schema")
    json_schema["$schema"] = schema

    import_name = f"import_name_test-{uuid4()}"

    response1 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        )
    )

    response2 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        )
    )

    assert response1["result"]["status"] == "inserted"
    assert response2["result"]["status"] == "no_change"


def test_insert_one_schema_update() -> None:
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

    schema_v1 = json_schema_v1.pop("schema")
    json_schema_v1["$schema"] = schema_v1

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

    schema_v2 = json_schema_v2.pop("schema")
    json_schema_v2["$schema"] = schema_v2

    import_name = f"import_name_test-{uuid4()}"

    response1 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema_v1,
            schemas_releases=[],
        )
    )

    response2 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema_v2,
            schemas_releases=[],
        )
    )

    assert response1["result"]["status"] == "inserted"
    assert response2["result"]["status"] == "updated"

    # Verify schema releases
    find_response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name)
    )

    assert find_response["status"] == "found"
    assert len(find_response["schema"]["schemas_releases"]) == 1
    assert (
        MongoSchemasService.compare_schemas(
            find_response["schema"]["schemas_releases"][0]["schema"], json_schema_v1
        )
        is True
    )


def test_update_one_schema() -> None:
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

    schema_v1 = json_schema_v1.pop("schema")
    json_schema_v1["$schema"] = schema_v1

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

    schema_v2 = json_schema_v2.pop("schema")
    json_schema_v2["$schema"] = schema_v2

    import_name = f"import_name_test-{uuid4()}"

    response1 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema_v1,
            schemas_releases=[],
        )
    )

    response2 = MongoSchemasService.update_one_schema(
        request=dtypes.MongoUpdateOneJsonSchemaRequest(
            import_name=import_name,
            schema=json_schema_v2,
            created_at=datetime.now(),
        )
    )

    assert response1["result"]["status"] == "inserted"
    assert response2["result"]["status"] == "updated"


def test_update_one_schema_not_found() -> None:
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

    schema = json_schema.pop("schema")
    json_schema["$schema"] = schema

    response = MongoSchemasService.update_one_schema(
        request=dtypes.MongoUpdateOneJsonSchemaRequest(
            import_name=f"non_existent-{uuid4()}",
            schema=json_schema,
            created_at=datetime.now(),
        )
    )

    assert response["result"]["status"] == "error"


def test_update_one_schema_no_change() -> None:
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

    schema = json_schema.pop("schema")
    json_schema["$schema"] = schema

    import_name = f"import_name_test-{uuid4()}"

    response1 = MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        )
    )

    response2 = MongoSchemasService.update_one_schema(
        request=dtypes.MongoUpdateOneJsonSchemaRequest(
            import_name=import_name,
            schema=json_schema,
            created_at=datetime.now(),
        )
    )

    assert response1["result"]["status"] == "inserted"
    assert response2["result"]["status"] == "no_change"


def test_delete_one_schema_with_no_releases() -> None:
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

    schema = json_schema.pop("schema")
    json_schema["$schema"] = schema

    import_name = f"import_name_test-{uuid4()}"

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        )
    )

    response = MongoSchemasService.delete_one_schema(
        request=dtypes.MongoDeleteOneJsonSchemaRequest(import_name=import_name)
    )

    assert response["result"]["status"] == "deleted"

    # Verify deletion
    find_response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name)
    )

    assert find_response["status"] == "not_found"


def test_delete_one_schema_with_releases() -> None:
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

    schema_v1 = json_schema_v1.pop("schema")
    json_schema_v1["$schema"] = schema_v1

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

    schema_v2 = json_schema_v2.pop("schema")
    json_schema_v2["$schema"] = schema_v2

    import_name = f"import_name_test-{uuid4()}"

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema_v1,
            schemas_releases=[],
        )
    )

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now() + timedelta(minutes=10),
            active_schema=json_schema_v2,
            schemas_releases=[],
        )
    )

    response = MongoSchemasService.delete_one_schema(
        request=dtypes.MongoDeleteOneJsonSchemaRequest(import_name=import_name)
    )

    assert response["result"]["status"] == "reverted"

    # Verify reversion
    find_response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name)
    )

    assert find_response["status"] == "found"
    assert (
        MongoSchemasService.compare_schemas(
            find_response["schema"]["active_schema"], json_schema_v1
        )
        is True
    )


def test_delete_one_schema_not_found() -> None:
    response = MongoSchemasService.delete_one_schema(
        request=dtypes.MongoDeleteOneJsonSchemaRequest(
            import_name=f"non_existent-{uuid4()}"
        )
    )

    assert response["result"]["status"] == "error"


def test_delete_import_name() -> None:
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

    schema = json_schema.pop("schema")
    json_schema["$schema"] = schema

    import_name = f"import_name_test-{uuid4()}"

    MongoSchemasService.insert_one_schema(
        request=dtypes.MongoInsertOneSchemaRequest(
            import_name=import_name,
            created_at=datetime.now(),
            active_schema=json_schema,
            schemas_releases=[],
        )
    )

    response = MongoSchemasService.delete_import_name(
        request=dtypes.MongoDeleteImportNameRequest(import_name=import_name)
    )

    assert response["result"]["status"] == "deleted"

    # Verify deletion
    find_response = MongoSchemasService.find_one_jsonschema(
        dtypes.MongoFindJsonSchemaRequest(import_name=import_name)
    )

    assert find_response["status"] == "not_found"


def test_delete_import_name_not_found() -> None:
    response = MongoSchemasService.delete_import_name(
        request=dtypes.MongoDeleteImportNameRequest(
            import_name=f"non_existent-{uuid4()}"
        )
    )

    assert response["result"]["status"] == "not_found"
