from services.tasks import DatabaseTasksService
from proto_utils.generated.database import database_pb2
from proto_utils.database.database_serde import DatabaseSerde


class DatabaseTasksHandler:
    @staticmethod
    def update_task_id(
        request: database_pb2.UpdateTaskIdRequest,
    ) -> database_pb2.UpdateTaskIdResponse:
        deserialized_request = DatabaseSerde.deserialize_update_task_id_request(request)
        service_response = DatabaseTasksService.update_task_id(deserialized_request)
        return DatabaseSerde.serialize_update_task_id_response(service_response)

    @staticmethod
    def get_task_id(
        request: database_pb2.GetTaskIdRequest,
    ) -> database_pb2.GetTaskIdResponse:
        deserialized_request = DatabaseSerde.deserialize_get_task_id_request(request)
        service_response = DatabaseTasksService.get_task_id(deserialized_request)
        return DatabaseSerde.serialize_get_task_id_response(service_response)

    @staticmethod
    def get_tasks_by_import_name(
        request: database_pb2.GetTasksByImportNameRequest,
    ) -> database_pb2.GetTasksByImportNameResponse:
        deserialized_request = (
            DatabaseSerde.deserialize_get_tasks_by_import_name_request(request)
        )
        service_response = DatabaseTasksService.get_tasks_by_import_name(
            deserialized_request
        )

        return DatabaseSerde.serialize_get_tasks_by_import_name_response(
            service_response
        )

    @staticmethod
    def set_task_id(
        request: database_pb2.SetTaskIdRequest,
    ) -> database_pb2.SetTaskIdResponse:
        deserialized_request = DatabaseSerde.deserialize_set_task_id_request(request)
        service_response = DatabaseTasksService.set_task_id(deserialized_request)
        return DatabaseSerde.serialize_set_task_id_response(service_response)
