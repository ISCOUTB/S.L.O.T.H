from typing import Dict

from proto_utils.messaging import dtypes
from proto_utils.generated.messaging import validation_pb2


class ValidationSerde:
    @staticmethod
    def serialize_validation_tasks(
        task: dtypes.ValidationTasks,
    ) -> validation_pb2.ValidationTasks:
        values: Dict[dtypes.ValidationTasks, validation_pb2.ValidationTasks] = {
            "sample_validation": validation_pb2.ValidationTasks.SAMPLE_VALIDATION,
            "unknown": validation_pb2.ValidationTasks.UNKNOWN,
        }

        return values.get(task, validation_pb2.ValidationTasks.UNKNOWN)

    @staticmethod
    def deserialize_validation_tasks(
        task: validation_pb2.ValidationTasks,
    ) -> dtypes.ValidationTasks:
        values: Dict[validation_pb2.ValidationTasks, dtypes.ValidationTasks] = {
            validation_pb2.ValidationTasks.SAMPLE_VALIDATION: "sample_validation",
            validation_pb2.ValidationTasks.UNKNOWN: "unknown",
        }

        return values.get(task, "unknown")

    @staticmethod
    def serialize_metadata(metadata: dtypes.Metadata) -> validation_pb2.Metadata:
        return validation_pb2.Metadata(
            filename=metadata["filename"],
            content_type=metadata["content_type"],
            size=metadata["size"],
        )

    @staticmethod
    def deserialize_metadata(metadata: validation_pb2.Metadata) -> dtypes.Metadata:
        return dtypes.Metadata(
            filename=metadata.filename,
            content_type=metadata.content_type,
            size=metadata.size,
        )
