"""Database serialization and deserialization module.

This module provides serialization and deserialization utilities for database
operations including task management functionality for tracking asynchronous
operations across database systems. Contains the DatabaseSerde class with
methods for converting between Python dictionaries and Protocol Buffer messages
for task-related database operations.
"""

from proto_utils.database import dtypes
from proto_utils.database.utils_serde import DatabaseUtilsSerde
from proto_utils.generated.database import database_pb2


class DatabaseSerde:
    """Serialization and deserialization utilities for database task operations.
    
    This class provides static methods for converting between Python TypedDict
    objects and their corresponding Protocol Buffer message representations for
    task management operations. These operations work with both Redis and MongoDB
    for task state management and tracking asynchronous processes.
    """

    @staticmethod
    def serialize_update_task_id_request(
        request: dtypes.UpdateTaskIdRequest,
    ) -> database_pb2.UpdateTaskIdRequest:
        """Serialize an UpdateTaskIdRequest dictionary to Protocol Buffer format.
        
        Args:
            request: The update task ID request dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer UpdateTaskIdRequest message.
        """
        return database_pb2.UpdateTaskIdRequest(
            task_id=request["task_id"],
            field=request["field"],
            value=request["value"],
            task=request["task"],
            message=request["message"],
            data=request["data"],
            reset_data=request["reset_data"],
        )

    @staticmethod
    def deserialize_update_task_id_request(
        proto: database_pb2.UpdateTaskIdRequest,
    ) -> dtypes.UpdateTaskIdRequest:
        """Deserialize a Protocol Buffer UpdateTaskIdRequest to dictionary format.
        
        Args:
            proto: The Protocol Buffer UpdateTaskIdRequest message to deserialize.
            
        Returns:
            The deserialized update task ID request dictionary.
        """
        return {
            "task_id": proto.task_id,
            "field": proto.field,
            "value": proto.value,
            "task": proto.task,
            "message": proto.message,
            "data": dict(proto.data),
            "reset_data": proto.reset_data,
        }

    @staticmethod
    def serialize_update_task_id_response(
        response: dtypes.UpdateTaskIdResponse,
    ) -> database_pb2.UpdateTaskIdResponse:
        """Serialize an UpdateTaskIdResponse dictionary to Protocol Buffer format.
        
        Args:
            response: The update task ID response dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer UpdateTaskIdResponse message.
        """
        return database_pb2.UpdateTaskIdResponse(
            success=response["success"],
            message=response["message"],
        )

    @staticmethod
    def deserialize_update_task_id_response(
        proto: database_pb2.UpdateTaskIdResponse,
    ) -> dtypes.UpdateTaskIdResponse:
        """Deserialize a Protocol Buffer UpdateTaskIdResponse to dictionary format.
        
        Args:
            proto: The Protocol Buffer UpdateTaskIdResponse message to deserialize.
            
        Returns:
            The deserialized update task ID response dictionary.
        """
        return {
            "success": proto.success,
            "message": proto.message,
        }

    @staticmethod
    def serialize_set_task_id_request(
        request: dtypes.SetTaskIdRequest,
    ) -> database_pb2.SetTaskIdRequest:
        """Serialize a SetTaskIdRequest dictionary to Protocol Buffer format.
        
        Args:
            request: The set task ID request dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer SetTaskIdRequest message.
        """
        return database_pb2.SetTaskIdRequest(
            task_id=request["task_id"],
            value=DatabaseUtilsSerde.serialize_api_response(request["value"]),
            task=request["task"],
        )

    @staticmethod
    def deserialize_set_task_id_request(
        proto: database_pb2.SetTaskIdRequest,
    ) -> dtypes.SetTaskIdRequest:
        """Deserialize a Protocol Buffer SetTaskIdRequest to dictionary format.
        
        Args:
            proto: The Protocol Buffer SetTaskIdRequest message to deserialize.
            
        Returns:
            The deserialized set task ID request dictionary.
        """
        return {
            "task_id": proto.task_id,
            "value": DatabaseUtilsSerde.deserialize_api_response(proto.value),
            "task": proto.task,
        }

    @staticmethod
    def serialize_set_task_id_response(
        response: dtypes.SetTaskIdResponse,
    ) -> database_pb2.SetTaskIdResponse:
        """Serialize a SetTaskIdResponse dictionary to Protocol Buffer format.
        
        Args:
            response: The set task ID response dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer SetTaskIdResponse message.
        """
        return database_pb2.SetTaskIdResponse(
            success=response["success"],
            message=response["message"],
        )

    @staticmethod
    def deserialize_set_task_id_response(
        proto: database_pb2.SetTaskIdResponse,
    ) -> dtypes.SetTaskIdResponse:
        """Deserialize a Protocol Buffer SetTaskIdResponse to dictionary format.
        
        Args:
            proto: The Protocol Buffer SetTaskIdResponse message to deserialize.
            
        Returns:
            The deserialized set task ID response dictionary.
        """
        return {
            "success": proto.success,
            "message": proto.message,
        }

    @staticmethod
    def serialize_get_task_id_request(
        request: dtypes.GetTaskIdRequest,
    ) -> database_pb2.GetTaskIdRequest:
        """Serialize a GetTaskIdRequest dictionary to Protocol Buffer format.
        
        Args:
            request: The get task ID request dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer GetTaskIdRequest message.
        """
        return database_pb2.GetTaskIdRequest(
            task_id=request["task_id"],
            task=request["task"],
        )

    @staticmethod
    def deserialize_get_task_id_request(
        proto: database_pb2.GetTaskIdRequest,
    ) -> dtypes.GetTaskIdRequest:
        """Deserialize a Protocol Buffer GetTaskIdRequest to dictionary format.
        
        Args:
            proto: The Protocol Buffer GetTaskIdRequest message to deserialize.
            
        Returns:
            The deserialized get task ID request dictionary.
        """
        return {
            "task_id": proto.task_id,
            "task": proto.task,
        }

    @staticmethod
    def serialize_get_task_id_response(
        response: dtypes.GetTaskIdResponse,
    ) -> database_pb2.GetTaskIdResponse:
        """Serialize a GetTaskIdResponse dictionary to Protocol Buffer format.
        
        Args:
            response: The get task ID response dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer GetTaskIdResponse message.
        """
        return database_pb2.GetTaskIdResponse(
            value=(
                DatabaseUtilsSerde.serialize_api_response(response["value"])
                if response["value"] is not None
                else None
            ),
            found=response["found"],
        )

    @staticmethod
    def deserialize_get_task_id_response(
        proto: database_pb2.GetTaskIdResponse,
    ) -> dtypes.GetTaskIdResponse:
        """Deserialize a Protocol Buffer GetTaskIdResponse to dictionary format.
        
        Args:
            proto: The Protocol Buffer GetTaskIdResponse message to deserialize.
            
        Returns:
            The deserialized get task ID response dictionary.
        """
        return {
            "value": (
                DatabaseUtilsSerde.deserialize_api_response(proto.value)
                if proto.HasField("value")
                else None
            ),
            "found": proto.found,
        }

    @staticmethod
    def serialize_get_tasks_by_import_name_request(
        request: dtypes.GetTasksByImportNameRequest,
    ) -> database_pb2.GetTasksByImportNameRequest:
        """Serialize a GetTasksByImportNameRequest dictionary to Protocol Buffer format.
        
        Args:
            request: The get tasks by import name request dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer GetTasksByImportNameRequest message.
        """
        return database_pb2.GetTasksByImportNameRequest(
            import_name=request["import_name"],
            task=request["task"],
        )

    @staticmethod
    def deserialize_get_tasks_by_import_name_request(
        proto: database_pb2.GetTasksByImportNameRequest,
    ) -> dtypes.GetTasksByImportNameRequest:
        """Deserialize a Protocol Buffer GetTasksByImportNameRequest to dictionary format.
        
        Args:
            proto: The Protocol Buffer GetTasksByImportNameRequest message to deserialize.
            
        Returns:
            The deserialized get tasks by import name request dictionary.
        """
        return {
            "import_name": proto.import_name,
            "task": proto.task,
        }

    @staticmethod
    def serialize_get_tasks_by_import_name_response(
        response: dtypes.GetTasksByImportNameResponse,
    ) -> database_pb2.GetTasksByImportNameResponse:
        """Serialize a GetTasksByImportNameResponse dictionary to Protocol Buffer format.
        
        Args:
            response: The get tasks by import name response dictionary to serialize.
            
        Returns:
            The serialized Protocol Buffer GetTasksByImportNameResponse message.
        """
        return database_pb2.GetTasksByImportNameResponse(
            tasks=[
                DatabaseUtilsSerde.serialize_api_response(task)
                for task in response["tasks"]
            ]
        )

    @staticmethod
    def deserialize_get_tasks_by_import_name_response(
        proto: database_pb2.GetTasksByImportNameResponse,
    ) -> dtypes.GetTasksByImportNameResponse:
        """Deserialize a Protocol Buffer GetTasksByImportNameResponse to dictionary format.
        
        Args:
            proto: The Protocol Buffer GetTasksByImportNameResponse message to deserialize.
            
        Returns:
            The deserialized get tasks by import name response dictionary.
        """
        return {
            "tasks": [
                DatabaseUtilsSerde.deserialize_api_response(task)
                for task in proto.tasks
            ]
        }
