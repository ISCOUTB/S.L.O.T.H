from typing import Dict

from proto_utils.messaging import dtypes
from proto_utils.generated.messaging import schemas_pb2


class SchemasSerde:
    @staticmethod
    def serialize_schemas_tasks(task: dtypes.SchemasTasks) -> schemas_pb2.SchemasTasks:
        values: Dict[dtypes.SchemasTasks, schemas_pb2.SchemasTasks] = {
            "upload_schema": schemas_pb2.SchemasTasks.UPLOAD_SCHEMA,
            "remove_schema": schemas_pb2.SchemasTasks.REMOVE_SCHEMA,
            "unknown": schemas_pb2.SchemasTasks.UNKNOWN,
        }

        return values.get(task, schemas_pb2.SchemasTasks.UNKNOWN)

    @staticmethod
    def deserialize_schemas_tasks(
        task: schemas_pb2.SchemasTasks,
    ) -> dtypes.SchemasTasks:
        values: Dict[schemas_pb2.SchemasTasks, dtypes.SchemasTasks] = {
            schemas_pb2.SchemasTasks.UPLOAD_SCHEMA: "upload_schema",
            schemas_pb2.SchemasTasks.REMOVE_SCHEMA: "remove_schema",
            schemas_pb2.SchemasTasks.UNKNOWN: "unknown",
        }

        return values.get(task, "unknown")
